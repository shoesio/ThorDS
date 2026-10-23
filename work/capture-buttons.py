import os
import select
import struct
import time

paths = [
    "/dev/input/event0",
    "/dev/input/event9",
    "/dev/input/event10",
    "/dev/input/event11",
]
files = {os.open(path, os.O_RDONLY | os.O_NONBLOCK): path for path in paths}
deadline = time.time() + 45
print("READY", flush=True)
while time.time() < deadline:
    readable, _, _ = select.select(list(files), [], [], 1)
    for descriptor in readable:
        data = os.read(descriptor, 24 * 32)
        for offset in range(0, len(data), 24):
            _, _, event_type, code, value = struct.unpack(
                "llHHi", data[offset : offset + 24]
            )
            if event_type:
                print(
                    files[descriptor],
                    "type",
                    event_type,
                    "code",
                    code,
                    "value",
                    value,
                    flush=True,
                )
