#!/usr/bin/python3
"""Fix ThorDS D-pad SDL hat mapping; preserve all unrelated settings."""
import os
from pathlib import Path
import pwd
import select
import shutil
import signal
import subprocess
import tempfile
import time


def atomic_write(path, text, mode, uid, gid):
    fd, name = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, mode)
        os.chown(name, uid, gid)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def fix_startup(text):
    replacements = {
        'axis:7,direction:-,threshold:-0.5': 'hat:0,direction:up',
        'axis:7,direction:+,threshold:0.5': 'hat:0,direction:down',
        'axis:6,direction:-,threshold:-0.5': 'hat:0,direction:left',
        'axis:6,direction:+,threshold:0.5': 'hat:0,direction:right',
    }
    for old, new in replacements.items():
        if text.count(old) == 1:
            text = text.replace(old, new)
        elif old in text or text.count(new) != 1:
            raise RuntimeError('Unexpected startup mapping; no changes applied')
    return text


def fix_config(text):
    lines = text.splitlines()
    count = 0
    for direction in ('up', 'down', 'left', 'right'):
        key = r'profiles\1\button_' + direction
        matches = [i for i, line in enumerate(lines) if line.startswith(key + '=')]
        if len(matches) != 1:
            raise RuntimeError('Unexpected input profile; no changes applied')
        index = matches[0]
        old = lines[index].split('=', 1)[1].strip('"')
        parts = [p for p in old.split(',') if not p.startswith(('axis:', 'hat:', 'direction:', 'threshold:'))]
        if 'engine:sdl' not in parts:
            raise RuntimeError('Expected SDL controller profile')
        lines[index] = key + '="hat:0,direction:' + direction + ',' + ','.join(parts) + '"'
        count += 1
    assert count == 4
    return '\n'.join(lines) + '\n'


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run this installer with sudo.')
    account = pwd.getpwnam('thords')
    startup = Path('/usr/bin/thords-configure-controls')
    config = Path(account.pw_dir) / '.config/azaharplus-emu/qt-config.ini'
    # Validate both formats before touching the running session.
    new_startup = fix_startup(startup.read_text())
    fix_config(config.read_text())
    backup = Path('/var/lib/thords') / ('dpad-backup-' + time.strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(mode=0o700)
    shutil.copy2(startup, backup / startup.name)
    shutil.copy2(config, backup / config.name)
    pids = subprocess.run(['pgrep', '-u', str(account.pw_uid), '-x', 'azahar'],
                          capture_output=True, text=True).stdout.split()
    if len(pids) > 1:
        raise RuntimeError('Multiple emulators running; no changes applied')
    parent_fd = child_fd = None
    try:
        if pids:
            pid = int(pids[0])
            parent = int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[1])
            if b'/usr/bin/thords-session' not in Path(f'/proc/{parent}/cmdline').read_bytes().split(b'\0'):
                raise RuntimeError('Unexpected emulator supervisor; no changes applied')
            parent_fd = os.pidfd_open(parent)
            child_fd = os.pidfd_open(pid)
            signal.pidfd_send_signal(parent_fd, signal.SIGSTOP)
            subprocess.run(['/usr/bin/setpriv', f'--reuid={account.pw_uid}',
                            f'--regid={account.pw_gid}', '--init-groups',
                            '/usr/local/libexec/thords/thords-restart-azahar'],
                           check=True, timeout=25)
            if not select.select([child_fd], [], [], 1)[0]:
                raise RuntimeError('Emulator is still running; no changes applied')
        # Clean shutdown can save settings: edit the latest file after exit.
        latest = config.read_text()
        shutil.copy2(config, backup / 'qt-config.after-clean-close.ini')
        atomic_write(config, fix_config(latest), 0o600, account.pw_uid, account.pw_gid)
        atomic_write(startup, new_startup, 0o755, 0, 0)
        print('D-pad now uses SDL hat 0 in all four directions.', flush=True)
        print('Startup mapping fixed. Gyro, sticks and buttons preserved.', flush=True)
        print('Backup:', backup, flush=True)
    finally:
        if parent_fd is not None:
            signal.pidfd_send_signal(parent_fd, signal.SIGCONT)
            os.close(parent_fd)
        if child_fd is not None:
            os.close(child_fd)


if __name__ == '__main__':
    main()
