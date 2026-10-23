#!/usr/bin/env python3
"""Refresh nested checkout provenance, local patches, and untracked text sources."""
import json, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args])
def source(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 5_000_000:
        return False
    if any(x in path.parts for x in ('.git', 'node_modules', '__pycache__', '.venv', 'target')):
        return False
    if path.name in ('.env', 'id_rsa', 'id_ed25519') or path.suffix.lower() in ('.pem', '.key', '.cia', '.3ds', '.bin'):
        return False
    try:
        data = path.read_bytes()
        return b'\0' not in data and bool(data.decode('utf-8') or True)
    except (UnicodeError, OSError):
        return False
repos = []
for base in ('upstream', 'build', 'work'):
    for root, dirs, files in os.walk(base):
        if '.git' not in dirs and '.git' not in files:
            continue
        dirs[:] = []
        out = ROOT / 'state/checkouts' / root
        out.mkdir(parents=True, exist_ok=True)
        origin = git(root, 'remote', 'get-url', 'origin').decode().strip()
        if origin == str(ROOT / 'upstream/thorch'):
            origin = 'https://github.com/thorch-os/thorch.git'
        repos.append({'path': root, 'origin': origin, 'commit': git(root, 'rev-parse', 'HEAD').decode().strip()})
        (out / 'changes.patch').write_bytes(git(root, 'diff', '--binary', 'HEAD'))
        for raw in git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
            if not raw:
                continue
            rel = os.fsdecode(raw)
            p = Path(root) / rel
            if source(p):
                dest = out / 'untracked' / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(p.read_bytes())
                dest.chmod(p.stat().st_mode & 0o777)
Path('state/checkouts.json').write_text(json.dumps(repos, indent=2) + '\n')
print(f'Captured {len(repos)} checkout references and local changes.')
