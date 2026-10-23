/*
 * FastRPC reverse tunnel
 *
 * Copyright (C) 2023 The Sensor Shell Contributors
 *
 * This file is part of sensh.
 *
 * Sensh is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <inttypes.h>
#include <libhexagonrpc/fastrpc.h>
#include <libhexagonrpc/interfaces/remotectl.def>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "aee_error.h"
#include "interfaces/adsp_listener.def"
#include "iobuffer.h"
#include "listener.h"

static int adsp_listener_init2(int fd)
{
	return fastrpc2(&adsp_listener_init2_def, fd, ADSP_LISTENER_HANDLE);
}

static int adsp_listener_next2(int fd,
			       uint32_t ret_rctx,
			       uint32_t ret_res,
			       uint32_t ret_outbuf_len, void *ret_outbuf,
			       uint32_t *rctx,
			       uint32_t *handle,
			       uint32_t *sc,
			       uint32_t *inbufs_len,
			       uint32_t inbufs_size, void *inbufs)
{
	return fastrpc2(&adsp_listener_next2_def, fd, ADSP_LISTENER_HANDLE,
			ret_rctx,
			ret_res,
			ret_outbuf_len, ret_outbuf,
			rctx,
			handle,
			sc,
			inbufs_len,
			inbufs_size, inbufs);
}

static int adsp_listener_get_in_bufs2(int fd,
				      uint32_t rctx,
				      uint32_t offset,
				      uint32_t *len_req,
				      uint32_t bufs_size, void *bufs)
{
	return fastrpc2(&adsp_listener_get_in_bufs2_def, fd, ADSP_LISTENER_HANDLE,
			rctx,
			offset,
			len_req,
			bufs_size, bufs);
}

/*
 * A message larger than the part next2 returns (a file write of more than a
 * few hundred bytes, for example): fetch the rest with get_in_bufs2, as
 * Qualcomm's listener does. *out is the whole message, to be freed.
 */
static int fetch_large_inbufs(int fd, uint32_t rctx,
			      const char *first, uint32_t first_len,
			      uint32_t len, char **out)
{
	uint32_t req = 0;
	char *buf;
	int ret;

	if (len > 16 * 1024 * 1024) {
		fprintf(stderr, "Input buffers too large: %" PRIu32 "\n", len);
		return -1;
	}

	buf = malloc(len);
	if (buf == NULL) {
		perror("Could not allocate the input buffers");
		return -1;
	}

	memcpy(buf, first, first_len);

	ret = adsp_listener_get_in_bufs2(fd, rctx, first_len, &req,
					 len - first_len, buf + first_len);
	if (ret || req > len) {
		fprintf(stderr, "Could not fetch the rest of the input buffers: %d (%" PRIu32 " of %" PRIu32 ")\n",
				ret, req, len);
		free(buf);
		return -1;
	}

	*out = buf;

	return 0;
}

static struct fastrpc_io_buffer *allocate_outbufs(const struct fastrpc_function_def_interp2 *def,
						  uint32_t *first_inbuf)
{
	struct fastrpc_io_buffer *out;
	size_t out_count;
	size_t i, j;
	off_t off;
	uint32_t *sizes;

	out_count = def->out_bufs + (def->out_nums && 1);
	/*
	 * POSIX allows malloc to return a non-NULL pointer to a zero-size area
	 * in memory. Since the code below assumes non-zero size if the pointer
	 * is non-NULL, exit early if we do not need to allocate anything.
	 */
	if (out_count == 0)
		return NULL;

	out = malloc(sizeof(struct fastrpc_io_buffer) * out_count);
	if (out == NULL)
		return NULL;

	out[0].s = def->out_nums * 4;
	if (out[0].s) {
		out[0].p = malloc(def->out_nums * 4);
		if (out[0].p == NULL)
			goto err_free_out;
	}

	off = def->out_nums && 1;
	sizes = &first_inbuf[def->in_nums + def->in_bufs];

	for (i = 0; i < def->out_bufs; i++) {
		out[off + i].s = sizes[i];
		out[off + i].p = malloc(sizes[i]);
		if (out[off + i].p == NULL)
			goto err_free_prev;
	}

	return out;

err_free_prev:
	for (j = 0; j < i; j++)
		free(out[off + j].p);

err_free_out:
	free(out);
	return NULL;
}

static int check_inbuf_sizes(const struct fastrpc_function_def_interp2 *def,
			     const struct fastrpc_io_buffer *inbufs)
{
	uint8_t i;
	const uint32_t *sizes = &((const uint32_t *) inbufs[0].p)[def->in_nums];

	if (inbufs[0].s != 4U * (def->in_nums
			      + def->in_bufs
			      + def->out_bufs)) {
		fprintf(stderr, "Invalid number of input numbers: %" PRIu32 " (expected %u)\n",
				inbufs[0].s,
				4 * (def->in_nums
				   + def->in_bufs
				   + def->out_bufs));
		return -1;
	}

	for (i = 0; i < def->in_bufs; i++) {
		if (inbufs[i + 1].s != sizes[i]) {
			fprintf(stderr, "Invalid buffer size\n");
			return -1;
		}
	}

	return 0;
}

static int return_for_next_invoke(int fd,
				  uint32_t result,
				  uint32_t *rctx,
				  uint32_t *handle,
				  uint32_t *sc,
				  const struct fastrpc_io_buffer *returned,
				  struct fastrpc_io_buffer **decoded)
{
	struct fastrpc_decoder_context *ctx;
	char inbufs[256];
	const char *msg = inbufs;
	char *large = NULL;
	char *outbufs = NULL;
	uint32_t inbufs_len;
	uint32_t outbufs_len;
	int ret;

	outbufs_len = outbufs_calculate_size(REMOTE_SCALARS_OUTBUFS(*sc), returned);

	if (outbufs_len) {
		outbufs = malloc(outbufs_len);
		if (outbufs == NULL) {
			perror("Could not allocate encoded output buffer");
			return -1;
		}

		outbufs_encode(REMOTE_SCALARS_OUTBUFS(*sc), returned, outbufs);
	}

	ret = adsp_listener_next2(fd,
				  *rctx, result,
				  outbufs_len, outbufs,
				  rctx, handle, sc,
				  &inbufs_len, 256, inbufs);
	if (ret) {
		if (ret == -1)
			perror("Could not fetch next FastRPC message");
		else
			fprintf(stderr, "Could not fetch next FastRPC message: %d\n", ret);

		goto err_free_outbufs;
	}

	if (inbufs_len > sizeof(inbufs)) {
		ret = fetch_large_inbufs(fd, *rctx, inbufs, sizeof(inbufs),
					 inbufs_len, &large);
		if (ret)
			goto err_free_outbufs;

		msg = large;
	}

	ctx = inbuf_decode_start(*sc);
	if (!ctx) {
		perror("Could not start decoding");
		ret = -1;
		goto err_free_outbufs;
	}

	ret = inbuf_decode(ctx, inbufs_len, msg);
	if (ret) {
		perror("Could not decode");
		goto err_free_outbufs;
	}

	if (!inbuf_decode_is_complete(ctx)) {
		fprintf(stderr, "Expected more input buffers\n");
		ret = -1;
		goto err_free_outbufs;
	}

	*decoded = inbuf_decode_finish(ctx);

err_free_outbufs:
	free(large);
	free(outbufs);
	return ret;
}

static int invoke_requested_procedure(size_t n_ifaces,
				      struct fastrpc_interface **ifaces,
				      uint32_t handle,
				      uint32_t sc,
			              uint32_t *result,
				      const struct fastrpc_io_buffer *decoded,
				      struct fastrpc_io_buffer **returned)
{
	const struct fastrpc_function_impl *impl;
	uint8_t in_count;
	uint8_t out_count;
	uint32_t method = REMOTE_SCALARS_METHOD(sc);
	int ret;

	if (sc & 0xff) {
		fprintf(stderr, "Handles are not supported, but got %u in, %u out\n",
				(sc & 0xf0) >> 4, sc & 0xf);
		*result = AEE_EBADPARM;
		return 1;
	}

	if (handle >= n_ifaces) {
		fprintf(stderr, "Unsupported handle: %u\n", handle);
		*result = AEE_EUNSUPPORTED;
		return 1;
	}

	/*
	 * The scalars have five bits for the method: from 31 on, they hold 31
	 * and the method is the first input number (which these methods'
	 * definitions count in their in_nums).
	 */
	if (method == 31) {
		if (REMOTE_SCALARS_INBUFS(sc) == 0 || decoded[0].s < 4) {
			fprintf(stderr, "Method 31 without its number: %08x\n", sc);
			*result = AEE_EBADPARM;
			return 1;
		}

		method = *(const uint32_t *) decoded[0].p;
	}

	if (method >= ifaces[handle]->n_procs) {
		fprintf(stderr, "Unsupported method: %u (%08x)\n", method, sc);
		*result = AEE_EUNSUPPORTED;
		return 1;
	}

	impl = &ifaces[handle]->procs[method];

	if (impl->def == NULL || impl->impl == NULL) {
		fprintf(stderr, "Unsupported method: %u (%08x)\n", method, sc);
		*result = AEE_EUNSUPPORTED;
		return 1;
	}

	in_count = impl->def->in_bufs + ((impl->def->in_nums
				       || impl->def->in_bufs
				       || impl->def->out_bufs) && 1);
	out_count = impl->def->out_bufs + (impl->def->out_nums && 1);

	if (REMOTE_SCALARS_INBUFS(sc) != in_count
	 || REMOTE_SCALARS_OUTBUFS(sc) != out_count) {
		fprintf(stderr, "Unexpected buffer count for method %u: %08x (in: %d vs %d, out: %d vs %d)\n",
			method, sc,
			REMOTE_SCALARS_INBUFS(sc), in_count,
			REMOTE_SCALARS_OUTBUFS(sc), out_count);
		*result = AEE_EBADPARM;
		return 1;
	}

	ret = check_inbuf_sizes(impl->def, decoded);
	if (ret) {
		*result = AEE_EBADPARM;
		return 1;
	}

	*returned = allocate_outbufs(impl->def, decoded[0].p);
	if (*returned == NULL && out_count > 0) {
		perror("Could not allocate output buffers");
		*result = AEE_ENOMEMORY;
		return 1;
	}

	*result = impl->impl(ifaces[handle]->data, decoded, *returned);

	return 0;
}

int run_fastrpc_listener(int fd,
			 size_t n_ifaces,
			 struct fastrpc_interface **ifaces)
{
	struct fastrpc_io_buffer *decoded = NULL,
				 *returned = NULL;
	uint32_t result = 0xffffffff;
	uint32_t handle;
	uint32_t rctx = 0;
	uint32_t sc = REMOTE_SCALARS_MAKE(0, 0, 0);
	uint32_t n_outbufs = 0;
	int ret;

	ret = adsp_listener_init2(fd);
	if (ret) {
		fprintf(stderr, "Could not initialize the listener: %u\n", ret);
		return ret;
	}

	while (!ret) {
		ret = return_for_next_invoke(fd,
					     result, &rctx, &handle, &sc,
					     returned, &decoded);
		if (ret)
			break;

		if (returned != NULL)
			iobuf_free(n_outbufs, returned);

		ret = invoke_requested_procedure(n_ifaces, ifaces,
						 handle, sc, &result,
						 decoded, &returned);
		if (ret)
			break;

		if (decoded != NULL)
			iobuf_free(REMOTE_SCALARS_INBUFS(sc), decoded);

		n_outbufs = REMOTE_SCALARS_OUTBUFS(sc);
	}

	return ret;
}
