#!/usr/bin/env python3
"""Verify a saved deployment snapshot, optionally compare a Thor over read-only SSH."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as source:
        value = hashlib.sha256()
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            value.update(chunk)
        return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, default=ROOT / 'state/deployed/thor-20261023')
    parser.add_argument('--host', help='Optional SSH target, e.g. thords@192.168.0.143; reads files only')
    args = parser.parse_args()
    manifest = json.loads((args.snapshot / 'manifest.json').read_text())
    expected = {}
    for name, info in manifest['files'].items():
        path = args.snapshot / 'rootfs' / name.lstrip('/')
        if digest(path) != info['sha256'] or (path.stat().st_mode & 0o777) != int(info['mode'], 8):
            raise SystemExit(f'Saved snapshot file failed verification: {name}')
        expected[name] = info['sha256']
    emulator = manifest['emulator']
    if digest(args.snapshot / 'emulator/changes.patch') != emulator['patch_sha256']:
        raise SystemExit('Saved emulator patch failed verification')
    for info in manifest['sensor_source']['overlay_files'].values():
        if digest(args.snapshot / info['path']) != info['sha256']:
            raise SystemExit(f'Saved sensor source failed verification: {info["path"]}')
    print(f'Local snapshot verified: {len(expected)} deployed text files, emulator patch, sensor overlays.', flush=True)
    if not args.host:
        return 0
    if args.host.startswith('-'):
        parser.error('--host must be an SSH destination, not an option')
    expected.update({p: info['sha256'] for p, info in manifest['binary_fingerprints'].items()})
    payload = '''import hashlib,json,os,subprocess
from pathlib import Path
paths = PATHS
result = {'kernel': os.uname().release, 'files': {}}
for name in paths:
 try:
  value = hashlib.sha256()
  with Path(name).open('rb') as source:
   for chunk in iter(lambda: source.read(1024*1024), b''):
    value.update(chunk)
  result['files'][name] = value.hexdigest()
 except OSError as error:
  result['files'][name] = {'error': str(error)}
p = subprocess.run(['pacman','-Q',*PACKAGES],capture_output=True,text=True)
result['packages'] = dict(line.split(' ',1) for line in p.stdout.splitlines())
print(json.dumps(result))
'''.replace('PATHS', repr(sorted(expected))).replace('PACKAGES', repr(list(manifest['packages'])))
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
                           args.host, 'python3 -'], input=payload, capture_output=True, text=True)
    if proc.returncode:
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    live = json.loads(proc.stdout)
    differences = [p for p, value in expected.items() if live['files'].get(p) != value]
    packages = {p: {'expected': value, 'actual': live['packages'].get(p)}
                for p, value in manifest['packages'].items() if live['packages'].get(p) != value}
    result = {'checked_files': len(expected), 'file_differences': differences,
              'package_differences': packages, 'kernel_matches': live['kernel'] == manifest['kernel'],
              'scope': 'Captured deployment files, not the historical image recipe or all device state. No remote writes.'}
    print(json.dumps(result, indent=2))
    return int(bool(differences or packages or not result['kernel_matches']))


if __name__ == '__main__':
    sys.exit(main())
