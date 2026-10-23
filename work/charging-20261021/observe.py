#!/usr/bin/python3
"""Read-only battery/USB samples and copies of completed sleep snapshots."""
import json,time
from pathlib import Path
w=Path.home()/'charging-20261021';w.mkdir(exist_ok=True)
start=time.monotonic()
keys=('status','online','capacity','charge_counter','current_now','voltage_now','voltage_ocv','power_now','usb_type','input_current_limit','current_max','temp','constant_charge_current','constant_charge_current_max','charge_control_start_threshold','charge_control_end_threshold')
with (w/'samples.jsonl').open('a',buffering=1) as log:
 while time.monotonic()-start<600:
  data={'timestamp':time.time(),'boottime':time.clock_gettime(time.CLOCK_BOOTTIME),'supplies':{}}
  for p in Path('/sys/class/power_supply').iterdir():
   row={}
   for key in keys:
    try:row[key]=(p/key).read_text().strip()
    except OSError:pass
   data['supplies'][p.name]=row
  log.write(json.dumps(data)+'\n')
  for kind in ('pre','post'):
   try:
    text=Path(f'/var/log/thords/sleep/latest-{kind}.json').read_text()
    stamp=json.loads(text)['sample']['timestamp']
    dest=w/f'{stamp:.6f}-{kind}.json'
    if not dest.exists():dest.write_text(text)
   except (OSError,ValueError,KeyError):pass
  time.sleep(2)
