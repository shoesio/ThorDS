from pathlib import Path
import os, subprocess, tempfile
source=Path('build/thorch-work/packages/thords-kiosk/rootfs/usr/bin/thords-azahar').read_text()
with tempfile.TemporaryDirectory() as d:
    home=Path(d)
    launcher=home/'.local/mako/bin/mako-launch'
    launcher.parent.mkdir(parents=True)
    launcher.write_text('''#!/usr/bin/env bash
set -eu
[[ "$QT_QPA_PLATFORM" == xcb ]]
[[ "$MAKO_FRAME_GENERATION_TOP_ONLY" == 1 ]]
[[ "$1" == azahar && "$2" == --boot-home-menu-europe ]]
grep -q '^multiplier = 2$' "$MAKO_CONFIG"
grep -q '^adaptive = false$' "$MAKO_CONFIG"
printf 'cold-boot launcher contract passed\\n'
''')
    launcher.chmod(0o755)
    script=home/'launch'
    script.write_text(source.replace('log_file="/var/log/thords/framegen.log"',f'log_file="{d}/framegen.log"'))
    env=dict(os.environ,HOME=d,QT_QPA_PLATFORM='wayland',DISPLAY=':93')
    subprocess.run(['bash',str(script),'--boot-home-menu-europe'],env=env,check=True)
