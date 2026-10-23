import os, struct
def join_split(mdt, out):
    """A split Qualcomm image (NAME.mdt and NAME.bNN, one per program segment) as the single
    ELF file the kernel loads, each segment at its file offset (as pil-squasher does)."""
    hdr = open(mdt, "rb").read()
    if hdr[:4] != b"\x7fELF":
        raise ValueError(f"{mdt}: not an ELF file")
    if hdr[4] == 1:
        phoff, = struct.unpack_from("<I", hdr, 28)
        phentsize, phnum = struct.unpack_from("<HH", hdr, 42)
        segs = [struct.unpack_from("<8I", hdr, phoff + i * phentsize) for i in range(phnum)]
        segs = [(p[1], p[4]) for p in segs]
    else:
        phoff, = struct.unpack_from("<Q", hdr, 32)
        phentsize, phnum = struct.unpack_from("<HH", hdr, 54)
        segs = [struct.unpack_from("<IIQQQQQQ", hdr, phoff + i * phentsize) for i in range(phnum)]
        segs = [(p[2], p[5]) for p in segs]
    buf = bytearray(max(off + size for off, size in segs))
    for i, (off, size) in enumerate(segs):
        if size == 0:
            continue
        part = f"{mdt[:-4]}.b{i:02d}"
        data = open(part, "rb").read() if os.path.exists(part) else hdr[off:off + size]
        if len(data) < size:
            raise ValueError(f"{part}: {len(data)} bytes, the segment has {size}")
        buf[off:off + size] = data[:size]
    with open(out, "wb") as f:
        f.write(buf)
for name in ("adsp", "adsp_dtb"):
    join_split("/var/lib/thords/gyro/android-adsp/"+name+".mdt", "/var/lib/thords/gyro/android-adsp/"+name+".mbn")
