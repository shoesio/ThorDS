#!/usr/bin/python3
"""Copy this Thor's Android sensor data, using read-only block mappings.

Uses android_parts.py from kettlelinux (GPL-3.0-or-later).
Android partitions are never opened for writing.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys

from android_parts import PARTS, mounted, super_partitions

dest = Path('/var/lib/thords/gyro/qcom')
if dest.exists():
    raise SystemExit('Sensor data already exists; preserve it.')
parts = super_partitions(PARTS + '/super')
slot = next(s for s in ('_a', '_b') if parts.get('vendor' + s))
# This kernel omits device-mapper: reconstruct a temporary vendor image instead.
image = Path('/var/lib/thords/gyro/vendor-readonly.img')
image.parent.mkdir(parents=True, exist_ok=True)
with open(PARTS + '/super', 'rb') as source, image.open('xb') as target:
    for offset, size in parts['vendor' + slot]:
        source.seek(offset)
        remaining = size
        while remaining:
            chunk = source.read(min(4 * 1024 * 1024, remaining))
            if not chunk:
                raise RuntimeError('Short read from Android super')
            target.write(chunk)
            remaining -= len(chunk)
new = Path(str(dest) + '.new')
new.mkdir(parents=True, mode=0o700)
try:
    with mounted(str(image)) as vendor:
        shutil.copytree(vendor + '/etc/sensors/config', new / 'sensors/config')
        shutil.copyfile(vendor + '/etc/sensors/sns_reg_config', new / 'sensors/sns_reg.conf')
finally:
    image.unlink()
with mounted(PARTS + '/persist') as persist:
    shutil.copytree(persist + '/sensors', new / 'sensors/persist', symlinks=True)
    shutil.copytree(persist + '/sensors/registry/registry', new / 'sensors/registry')
    shutil.copyfile(persist + '/sensors/registry/sns_reg_version', new / 'sensors/sns_reg_version')
with mounted(PARTS + '/dsp' + slot) as dsp:
    shutil.copytree(dsp + '/adsp', new / 'dsp/adsp')
os.symlink('/sys/devices/soc0', new / 'socinfo')
new.rename(dest)
print('Copied device-specific sensor data to', dest)
