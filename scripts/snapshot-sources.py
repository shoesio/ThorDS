#!/usr/bin/env python3
"""Refresh pinned checkout references and local sources without build/data payloads."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    'build/thorch-work/packages/thords-kiosk/rootfs/usr/share/thords/boot-splash.png',
    'build/thorch-work/packages/thords-kiosk/rootfs/usr/share/thords/boot-splash.asp',
}
SKIP = {'.git', 'node_modules', '__pycache__', '.venv', 'target'}


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], cwd=ROOT)


def source(path):
    if any(x in path.parts for x in SKIP):
        return False
    if path.is_symlink():
        # Preserve systemd masks and relative links, never copy their targets.
        target = os.readlink(path)
        return target == '/dev/null' or (not os.path.isabs(target) and '..' not in Path(target).parts)
    if not path.is_file():
        return False
    if path.relative_to(ROOT).as_posix() in ASSETS:
        return True
    if path.stat().st_size > 5_000_000:
        return False
    if path.name in ('.env', 'id_rsa', 'id_ed25519') or path.suffix.lower() in ('.pem', '.key', '.cia', '.3ds', '.bin'):
        return False
    try:
        data = path.read_bytes()
        data.decode('utf-8')
        return b'\0' not in data
    except (UnicodeError, OSError):
        return False


def snapshot():
    repos = []
    seen = set()

    def capture(root):
        if root in seen:
            return
        seen.add(root)
        out = ROOT / 'state/checkouts' / root
        out.mkdir(parents=True, exist_ok=True)
        # Remove stale untracked snapshots after files are deleted or become tracked.
        if (out / 'untracked').exists():
            shutil.rmtree(out / 'untracked')
        origin = git(root, 'remote', 'get-url', 'origin').decode().strip()
        if origin == str(ROOT / 'upstream/thorch'):
            origin = 'https://github.com/thorch-os/thorch.git'
        repos.append({'path': root, 'origin': origin,
                      'commit': git(root, 'rev-parse', 'HEAD').decode().strip()})
        (out / 'changes.patch').write_bytes(git(root, 'diff', '--binary', 'HEAD'))
        for raw in git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
            if not raw:
                continue
            rel = os.fsdecode(raw).rstrip('/')
            p = ROOT / root / rel
            if p.is_dir() and (p / '.git').exists():
                capture(f'{root}/{rel}')
            elif source(p):
                dest = out / 'untracked' / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if p.is_symlink():
                    dest.symlink_to(os.readlink(p))
                else:
                    shutil.copy2(p, dest)

    for base in ('upstream', 'build', 'work'):
        for root, dirs, files in os.walk(ROOT / base):
            dirs[:] = [d for d in dirs if d not in SKIP]
            if '.git' in files or (Path(root) / '.git').is_dir():
                capture(Path(root).relative_to(ROOT).as_posix())
                dirs[:] = []
    (ROOT / 'state/checkouts.json').write_text(json.dumps(repos, indent=2) + '\n')
    hashes = {}
    for p in sorted((ROOT / 'state/checkouts').rglob('*')):
        if p.is_symlink():
            hashes[p.relative_to(ROOT).as_posix()] = {'symlink': os.readlink(p)}
        elif p.is_file():
            hashes[p.relative_to(ROOT).as_posix()] = {
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                'executable': bool(p.stat().st_mode & 0o111)}
    (ROOT / 'state/source-hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print(f'Captured {len(repos)} checkouts and {len(hashes)} snapshot file hashes.')


if __name__ == '__main__':
    snapshot()
