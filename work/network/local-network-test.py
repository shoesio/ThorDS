#!/usr/bin/env python3
"""Bounded network A/B tests; restore settings even on interruption."""
import ctypes
import fcntl
import os
from pathlib import Path
import signal
import socket
import struct
import time

IFACE = b'wlp1s0'
TARGET = ('88.19.187.219', 7777)

def ioctl(data):
    buf = ctypes.create_string_buffer(data)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        fcntl.ioctl(sock, 0x8946, struct.pack('16sP', IFACE, ctypes.addressof(buf)))
    return buf.raw[:len(data)]

def feature_state():
    header = ioctl(struct.pack('II', 0x3a, 0))
    blocks = struct.unpack('II', header)[1]
    if not 0 < blocks < 32:
        raise RuntimeError('Unexpected feature count')
    raw = ioctl(struct.pack('II', 0x3a, blocks) + bytes(16 * blocks))
    states = [struct.unpack_from('IIII', raw, 8 + i * 16) for i in range(blocks)]
    names_raw = ioctl(struct.pack('III', 0x1b, 4, blocks * 32) + bytes(blocks * 32 * 32))
    count = struct.unpack_from('I', names_raw, 8)[0]
    if count > blocks * 32:
        raise RuntimeError('Unexpected feature names length')
    names = [names_raw[12+i*32:12+(i+1)*32].split(b'\0')[0].decode() for i in range(count)]
    return blocks, states, names

def set_features(blocks, masks, values):
    raw = struct.pack('II', 0x3b, blocks)
    for mask, value in zip(masks, values):
        raw += struct.pack('II', mask, value)
    ioctl(raw)

def probe(label):
    start = time.monotonic()
    try:
        with socket.create_connection(TARGET, 4):
            print(label, 'CONNECTED', round(time.monotonic()-start, 3), 'seconds', flush=True)
    except OSError as error:
        print(label, str(error), flush=True)

def interrupted(signum, frame):
    raise KeyboardInterrupt

def main():
    if os.geteuid() != 0:
        raise SystemExit('Run with sudo python3 /home/thords/local-network-test.py')
    signal.signal(signal.SIGTERM, interrupted)
    print('Temporary local tests; original settings restored after each test.', flush=True)
    probe('Baseline')
    try:
        blocks, states, names = feature_state()
        masks = [0] * blocks
        for i, name in enumerate(names):
            available, requested, active, fixed = states[i // 32]
            bit = 1 << (i % 32)
            if name.startswith('tx-checksum'):
                print(name, 'active=', bool(active & bit), 'changeable=', bool(available & bit and not fixed & bit), flush=True)
                if available & bit and not fixed & bit:
                    masks[i // 32] |= bit
        if any(masks):
            original = [state[1] for state in states]
            try:
                set_features(blocks, masks, [0] * blocks)
                _, changed, _ = feature_state()
                if any(state[2] & mask for state, mask in zip(changed, masks)):
                    print('Offload did not fully disable; result inconclusive.', flush=True)
                probe('TX checksum offload OFF')
            finally:
                set_features(blocks, masks, original)
                _, restored, _ = feature_state()
                if any((state[1] ^ old) & mask for state, old, mask in zip(restored, original, masks)):
                    raise RuntimeError('Checksum restoration verification failed')
                print('Checksum settings restored and verified.', flush=True)
        else:
            print('No changeable TX checksum features.', flush=True)
    except OSError as error:
        print('Offload test unavailable:', error, flush=True)
    timestamps = Path('/proc/sys/net/ipv4/tcp_timestamps')
    original = timestamps.read_text()
    try:
        timestamps.write_text('0\n')
        probe('TCP timestamps OFF')
    finally:
        timestamps.write_text(original)
        if timestamps.read_text() != original:
            raise RuntimeError('Timestamp restoration verification failed')
        print('TCP timestamps restored and verified.', flush=True)
    probe('Restored baseline')
    print('Done. No persistent changes.', flush=True)

if __name__ == '__main__':
    main()
