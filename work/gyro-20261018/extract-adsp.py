#!/usr/bin/python3
# Read-only extraction of this Thor's Android ADSP firmware for comparison.
import os, shutil
from pathlib import Path
from android_parts import PARTS, mounted, super_partitions
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
dest=Path('/var/lib/thords/gyro/android-adsp')
dest.mkdir(exist_ok=True)
try:
    with mounted(str(image)) as vendor:
        for entry in Path(vendor+'/firmware').glob('adsp*'):
            if entry.is_file():
                shutil.copyfile(entry, dest/entry.name)
        print('Extracted',len(list(dest.iterdir())),'ADSP files',flush=True)
finally:
    image.unlink()
