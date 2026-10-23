from pathlib import Path
import os, subprocess, tempfile, time, json, sys
base=Path(sys.argv[1]);new=Path(sys.argv[2]);original=Path.home()/'.config/azaharplus-emu/qt-config.ini'
results={}
for label,source in [('before',base),('after',new)]:
 with tempfile.TemporaryDirectory() as d:
  home=Path(d);cfg=home/'.config/azaharplus-emu/qt-config.ini';cfg.parent.mkdir(parents=True);cfg.write_bytes(original.read_bytes())
  binary=home/'bin';binary.mkdir();(binary/'busctl').write_text('#!/bin/sh\nexit 0\n');(binary/'busctl').chmod(0o755)
  env=dict(os.environ,HOME=d,PATH=str(binary)+':'+os.environ['PATH'])
  s=(source/'thords-session').read_text()
  start=s.index("# Use Azahar's separate Vulkan windows")
  end=s.index('\n/usr/bin/thords-diagnostics') if label=='before' else s.index('# Run the GPU/hardware inventory')
  fragment='set -eu\nqt_config="$HOME/.config/azaharplus-emu/qt-config.ini"\nconfig_edits=()\n'+s[start:end]
  t=time.monotonic();subprocess.run(['bash','-c',fragment],env=env,check=True)
  for name in ('controls','performance'):
   subprocess.run(['bash',str(source/f'thords-configure-{name}')],env=env,check=True)
  results[label]={'seconds':round(time.monotonic()-t,3),'config':cfg.read_bytes()}
assert results['before']['config']==results['after']['config'], 'Settings changed'
print(json.dumps({k:v['seconds'] for k,v in results.items()}));print('Settings byte-for-byte identical')
