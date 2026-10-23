#!/usr/bin/python3
"""Thor SSC to Cemuhook DSU, on loopback only. Samples only for active clients."""
import json
import math
import os
from pathlib import Path
import selectors
import signal
import socket
import struct
import subprocess
import time
import zlib

VERSION, PORTS, DATA = 0x100000, 0x100001, 0x100002
INFO = bytes((0, 2, 2, 1)) + bytes.fromhex('020000005448') + bytes((5, 1))
SAMPLER = '/usr/local/libexec/thords/ssc-sampler'

def packet(kind, body):
    result = bytearray(struct.pack('<4sHHIII', b'DSUS', 1001, len(body) + 4, 0, 0x54484f52, kind) + body)
    struct.pack_into('<I', result, 8, zlib.crc32(result))
    return result

def request(data):
    if len(data) < 20 or data[:4] != b'DSUC':
        return None
    ver, size, crc = struct.unpack_from('<HHI', data, 4)
    if ver > 1001 or size != len(data) - 16:
        return None
    check = bytearray(data)
    check[8:12] = b'\0' * 4
    if zlib.crc32(check) != crc:
        return None
    return struct.unpack_from('<I', data, 16)[0]

def motion_body(counter, stamp, accel, gyro):
    body = bytearray(80)
    body[:12] = INFO
    struct.pack_into('<I', body, 12, counter)
    body[20:24] = bytes((128, 128, 128, 128))
    struct.pack_into('<Q6f', body, 48, stamp, *accel, *gyro)
    return body

def rotate(values, scale):
    # Thor Sensor Core portrait frame -> landscape, X right, Y top, Z out.
    x, y, z = values
    return (-y * scale, x * scale, z * scale)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 26760))
    sock.setblocking(False)
    selector = selectors.DefaultSelector()
    selector.register(sock, selectors.EVENT_READ, 'udp')
    clients, values, seen, counts = {}, {}, {}, {'A': 0, 'G': 0}
    process = None
    buffer = b''
    counter = 0
    last_start = last_status = 0
    running = True
    def stop(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    def stop_sampler():
        nonlocal process, buffer
        if process:
            selector.unregister(process.stdout)
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            process.stdout.close()
        process = None
        buffer = b''
        seen.clear()
    print('Thor motion DSU listening on 127.0.0.1:26760', flush=True)
    try:
        while running:
            now = time.monotonic()
            clients = {peer: expiry for peer, expiry in clients.items() if expiry > now}
            if clients and process is None and now - last_start > 3:
                process = subprocess.Popen([SAMPLER], stdout=subprocess.PIPE, bufsize=0)
                os.set_blocking(process.stdout.fileno(), False)
                selector.register(process.stdout, selectors.EVENT_READ, 'ssc')
                last_start = now
            if process and (not clients or process.poll() is not None or
                            (now - last_start > 15 and any(now - seen.get(k, 0) > 5 for k in ('A', 'G')))):
                stop_sampler()
            for key, _ in selector.select(timeout=1 / 60):
                if key.data == 'udp':
                    data, peer = sock.recvfrom(1024)
                    kind = request(data)
                    if kind == VERSION:
                        sock.sendto(packet(VERSION, struct.pack('<H', 1001)), peer)
                    elif kind == PORTS and len(data) >= 24:
                        count = struct.unpack_from('<I', data, 20)[0]
                        if count <= 4 and len(data) >= 24 + count and 0 in data[24:24 + count]:
                            sock.sendto(packet(PORTS, INFO[:11] + b'\0'), peer)
                    elif kind == DATA and len(data) == 28:
                        flags, pad = data[20:22]
                        if flags == 0 or (flags == 1 and pad == 0) or (flags == 2 and data[22:28] == INFO[4:10]):
                            if peer in clients or len(clients) < 8:
                                clients[peer] = now + 5
                else:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    buffer += chunk
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        fields = line.split()
                        if len(fields) != 4 or fields[0] not in (b'A', b'G'):
                            continue
                        try:
                            sample = tuple(map(float, fields[1:]))
                        except ValueError:
                            continue
                        if not all(math.isfinite(v) for v in sample):
                            continue
                        sensor = fields[0].decode()
                        values[sensor] = sample
                        seen[sensor] = time.monotonic()
                        counts[sensor] += 1
            now = time.monotonic()
            if clients and all(now - seen.get(k, 0) < .5 for k in ('A', 'G')):
                counter = (counter + 1) & 0xffffffff
                ax, ay, az = rotate(values['A'], 1 / 9.80665)
                # Match Azahar Android's landscape TransformAxes(), accounting
                # for the desktop DSU client's X/Z acceleration sign changes.
                # Flat on a table must become 3DS gravity (0, -1, 0).
                accel = (-ax, -az, ay)
                # DSU pitch/yaw are negated by Azahar; angles are degrees/s.
                gx, gy, gz = rotate(values['G'], 180 / math.pi)
                body = motion_body(counter, int(seen['A'] * 1000000), accel, (gx, -gz, gy))
                for peer in clients:
                    sock.sendto(packet(DATA, body), peer)
            if now - last_status > 1:
                status = {'clients': len(clients), 'samples': counts, 'packets': counter,
                          'raw': values, 'fresh': {k: now - seen.get(k, 0) < .5 for k in ('A', 'G')}}
                Path('/run/thords-motion/status.json').write_text(json.dumps(status) + '\n')
                last_status = now
    finally:
        stop_sampler()
        sock.close()
        selector.close()

if __name__ == '__main__':
    main()
