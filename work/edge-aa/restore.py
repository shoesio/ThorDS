from pathlib import Path
import os, signal, subprocess, time, shutil
home=Path.home()
config=home/'.config/azaharplus-emu/qt-config.ini'
pids=subprocess.check_output(['pgrep','-x','azahar'],text=True).split()
assert len(pids)==1, 'Expected one emulator'
pid=int(pids[0])
def parent(p):
    return int(Path(f'/proc/{p}/stat').read_text().split(') ')[1].split()[1])
wrapper=parent(pid)
session=wrapper if b'/usr/bin/thords-session' in Path(f'/proc/{wrapper}/cmdline').read_bytes() else parent(wrapper)
assert b'/usr/bin/thords-session' in Path(f'/proc/{session}/cmdline').read_bytes()
backup=home/'edge-aa-update'/('backup-'+str(int(time.time())))
backup.mkdir()
shutil.copy2(config,backup/'qt-config.ini')
shader_dir=home/'.local/share/azaharplus-emu/shaders'
shader_dir.mkdir(exist_ok=True)
shader=shader_dir/'ThorDS Edge AA.glsl'
if shader.exists(): shutil.copy2(shader,backup/shader.name)
shutil.copy2(home/'edge-aa-update'/shader.name,shader)
os.kill(session,signal.SIGSTOP)
try:
    if wrapper != session: os.kill(wrapper,signal.SIGSTOP)
    os.kill(pid,signal.SIGKILL)
    if wrapper != session: os.kill(wrapper,signal.SIGKILL)
    for _ in range(100):
        if not Path(f'/proc/{pid}').exists() or Path(f'/proc/{pid}/stat').read_text().split(') ')[1].split()[0] == 'Z': break
        time.sleep(.1)
    else: raise RuntimeError('Emulator did not exit; settings not changed')
    shutil.copy2(home/'edge-aa-update/backup-1790411085/qt-config.ini',config)
finally:
    os.kill(session,signal.SIGCONT)
print('Previous configuration restored')
