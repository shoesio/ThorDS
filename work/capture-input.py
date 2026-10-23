#!/usr/bin/env python3
import glob
import os
import select
import struct
import time

event_struct = struct.Struct("llHHi")
devices = {}
for path in glob.glob("/dev/input/event*"):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        devices[fd] = path
    except OSError:
        pass

deadline = time.monotonic() + 20
while time.monotonic() < deadline:
    ready, _, _ = select.select(list(devices), [], [], 1)
    for fd in ready:
        try:
            data = os.read(fd, event_struct.size * 64)
        except OSError:
            continue
        for offset in range(0, len(data) - event_struct.size + 1, event_struct.size):
            _, _, kind, code, value = event_struct.unpack_from(data, offset)
            if kind in (1, 3) and value not in (0, 255):
                print(devices[fd], kind, code, value, flush=True)
