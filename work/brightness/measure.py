from pathlib import Path
import subprocess,time,json,signal
paths=[Path('/sys/class/backlight')/n/'brightness' for n in ('ae94000.dsi.0','ae96000.dsi.0')]
old=[p.read_text().strip() for p in paths]
out=Path.home()/'brightness-comparison';out.mkdir(exist_ok=True)
def stop(*_):raise SystemExit(130)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:
 for name,values in [('original',old),('dim',['51','1228']),('original-repeat',old)]:
  for p,v in zip(paths,values):p.write_text(v)
  time.sleep(10)
  with (out/(name+'.jsonl')).open('w') as f:
   subprocess.run(['/usr/bin/thords-power-sample','--seconds','60'],stdout=f,check=True)
  print(name,(out/(name+'.jsonl')).read_text().splitlines()[-1],flush=True)
finally:
 for p,v in zip(paths,old):p.write_text(v)
