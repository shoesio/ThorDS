#!/usr/bin/python3
"""Install the verified ThorDS live-clock binary and relaunch its kiosk session."""
from pathlib import Path
import hashlib
import json
import os
import pwd
import select
import shutil
import signal
import subprocess
import tempfile
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if os.geteuid()!=0:
        raise SystemExit('Run this installer with sudo after saving your game.')
    account=pwd.getpwnam('thords')
    work=Path(account.pw_dir)/'azahar-build/clock-fix-20261018'
    manifest=json.loads((work/'manifest.json').read_text())
    candidate=work/'azahar'
    installed=Path('/usr/bin/azahar')
    if sha(candidate)!=manifest['fixed_sha256']:
        raise RuntimeError('Clock build hash mismatch')
    if sha(installed)!=manifest['baseline_sha256']:
        raise RuntimeError('Installed emulator changed; recheck before installation')
    backup=Path('/var/lib/thords')/('clock-backup-'+time.strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(mode=0o700)
    shutil.copy2(installed,backup/'azahar')
    shutil.copy2(work/'manifest.json',backup/'manifest.json')
    config=Path(account.pw_dir)/'.config/azaharplus-emu/qt-config.ini'
    shutil.copy2(config,backup/config.name)
    pids=subprocess.run(['pgrep','-u',str(account.pw_uid),'-x','azahar'],capture_output=True,text=True).stdout.split()
    if len(pids)>1:
        raise RuntimeError('Multiple emulator processes; no change applied')
    parent_fd=child_fd=None
    try:
        if pids:
            pid=int(pids[0])
            parent=int(Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[1])
            if b'/usr/bin/thords-session' not in Path(f'/proc/{parent}/cmdline').read_bytes().split(b'\0'):
                raise RuntimeError('Unexpected supervisor; no change applied')
            parent_fd=os.pidfd_open(parent);child_fd=os.pidfd_open(pid)
            signal.pidfd_send_signal(parent_fd,signal.SIGSTOP)
            subprocess.run(['/usr/bin/setpriv',f'--reuid={account.pw_uid}',f'--regid={account.pw_gid}',
                            '--init-groups','/usr/local/libexec/thords/thords-restart-azahar'],check=True,timeout=25)
            if not select.select([child_fd],[],[],1)[0]:
                raise RuntimeError('Emulator has not exited; no change applied')
        fd,temp=tempfile.mkstemp(prefix='.azahar-clock-',dir=installed.parent)
        try:
            with os.fdopen(fd,'wb') as dst,candidate.open('rb') as src:
                shutil.copyfileobj(src,dst);dst.flush();os.fsync(dst.fileno())
            os.chown(temp,0,0);os.chmod(temp,0o755)
            if sha(temp)!=manifest['fixed_sha256']:
                raise RuntimeError('Copy verification failed')
            os.replace(temp,installed)
            directory=os.open(installed.parent,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(directory)
            finally:os.close(directory)
        finally:
            Path(temp).unlink(missing_ok=True)
        print('Live-clock fix installed. Existing filters, 3x resolution and controls preserved.',flush=True)
        print('Previous emulator and settings:',backup,flush=True)
    finally:
        if parent_fd is not None:
            signal.pidfd_send_signal(parent_fd,signal.SIGCONT);os.close(parent_fd)
        if child_fd is not None:os.close(child_fd)


if __name__=='__main__':main()
