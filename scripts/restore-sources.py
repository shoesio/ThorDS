#!/usr/bin/env python3
"""Restore a pinned checkout and any nested checkout snapshots; never overwrite one."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    subprocess.run(args, check=True)


def restore(checkout, destination):
    entries = json.loads((ROOT / 'state/checkouts.json').read_text())
    chosen = [r for r in entries if r['path'] == checkout or r['path'].startswith(checkout + '/')]
    if not chosen or chosen[0]['path'] != checkout:
        raise SystemExit(f'No snapshot for {checkout}')
    destination = destination.resolve()
    if destination.exists():
        raise SystemExit(f'Refusing to overwrite {destination}; choose a new --destination.')
    hashes = json.loads((ROOT / 'state/source-hashes.json').read_text())
    # Check inputs before creating a destination or contacting upstream.
    for rel, expected in hashes.items():
        if any(rel.startswith('state/checkouts/' + r['path'] + '/') for r in chosen):
            p = ROOT / rel
            if 'symlink' in expected:
                valid = p.is_symlink() and os.readlink(p) == expected['symlink']
            else:
                valid = (p.is_file() and not p.is_symlink()
                         and hashlib.sha256(p.read_bytes()).hexdigest() == expected['sha256']
                         and bool(p.stat().st_mode & 0o111) == expected['executable'])
            if not valid:
                raise SystemExit(f'Snapshot integrity check failed: {rel}')
    for entry in sorted(chosen, key=lambda r: len(Path(r['path']).parts)):
        suffix = Path(entry['path']).relative_to(checkout)
        dest = destination / suffix
        if dest.exists():
            raise SystemExit(f'Refusing to overwrite nested destination {dest}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        run('git', 'clone', '--filter=blob:none', '--no-checkout', entry['origin'], str(dest))
        run('git', '-C', str(dest), 'checkout', '--detach', entry['commit'])
        snap = ROOT / 'state/checkouts' / entry['path']
        patch = snap / 'changes.patch'
        if patch.stat().st_size:
            run('git', '-C', str(dest), 'apply', '--check', str(patch))
            run('git', '-C', str(dest), 'apply', str(patch))
        if (snap / 'untracked').is_dir():
            shutil.copytree(snap / 'untracked', dest, dirs_exist_ok=True, symlinks=True)
        print(f'Restored {entry["path"]} at {entry["commit"]}', flush=True)
    print(f'Source ready at {destination}. No image was built or device modified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', default='build/thorch-work')
    parser.add_argument('--destination', type=Path, default=ROOT / 'build/thorch-work')
    args = parser.parse_args()
    restore(args.checkout, args.destination)


if __name__ == '__main__':
    main()
