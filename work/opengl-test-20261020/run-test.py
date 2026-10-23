#!/usr/bin/python3
"""Run the alternate renderer once; resume the original kiosk on exit."""
from pathlib import Path
import fcntl,json,os,select,shutil,signal,subprocess,time
w=Path.home()/'opengl-test-20261020'
with (w/'test.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 binary=w/'build/bin/Release/azahar'
 assert binary.is_file()
 pids=subprocess.check_output(['pgrep','-u',str(os.getuid()),'-x','azahar'],text=True).split()
 assert len(pids)==1,pids
 pid=int(pids[0]);proc=Path('/proc')/str(pid)
 assert (proc/'exe').resolve()==Path('/usr/bin/azahar')
 parent=int((proc/'stat').read_text().rsplit(')',1)[1].split()[1])
 assert b'/usr/bin/thords-session' in Path(f'/proc/{parent}/cmdline').read_bytes().split(b'\0')
 env={}
 for item in (proc/'environ').read_bytes().split(b'\0'):
  if b'=' in item:
   k,v=item.split(b'=',1);env[os.fsdecode(k)]=os.fsdecode(v)
 fd=os.pidfd_open(parent);child_fd=os.pidfd_open(pid)
 candidate=None
 def interrupted(*_):raise RuntimeError('Test interrupted')
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 try:
  signal.pidfd_send_signal(fd,signal.SIGSTOP)
  subprocess.run(['/usr/local/libexec/thords/thords-restart-azahar'],check=True,timeout=25)
  assert select.select([child_fd],[],[],1)[0],'Old emulator still running'
  source=Path.home()/'.config/azaharplus-emu'
  config=w/'config/azaharplus-emu'
  shutil.copytree(source,config,dirs_exist_ok=True)
  # Copy after a clean close so the settings match the saved live session.
  for path in [config/'qt-config.ini',*list((config/'custom').glob('*.ini'))]:
   lines=path.read_text().splitlines()
   for idx,line in enumerate(lines):
    if line.startswith('graphics_api='):lines[idx]='graphics_api=1'
    elif line.startswith('graphics_api\\default='):lines[idx]='graphics_api\\default=false'
   path.write_text('\n'.join(lines)+'\n')
  log=Path.home()/'.local/share/azaharplus-emu/log/azahar_log.txt'
  shutil.copy2(log,w/'vulkan-before.log')
  env['XDG_CONFIG_HOME']=str(w/'config');env['QT_QPA_PLATFORM']='xcb'
  for name in list(env):
   if name.startswith(('MAKO_','THORDS_FRAMEGEN_')):env.pop(name)
  with (w/'runtime.log').open('w') as output:
   candidate=subprocess.Popen([str(binary),'--boot-home-menu-europe'],env=env,stdout=output,stderr=subprocess.STDOUT)
   (w/'test-state.json').write_text(json.dumps({'supervisor_pid':parent,'candidate_pid':candidate.pid,'started':time.time()}))
   print('OpenGL test launched',candidate.pid,flush=True)
   while candidate.poll() is None:
    if (w/'stop-test').exists():
     # Ask Qt to close its main window and flush saves/settings.
     def nodes(node):
      yield node
      for c in node.get('nodes',[])+node.get('floating_nodes',[]):yield from nodes(c)
     for sock in Path(f'/run/user/{os.getuid()}').glob('sway-ipc.*.sock'):
      tree=json.loads(subprocess.check_output(['swaymsg','-s',str(sock),'-r','-t','get_tree']))
      windows=[n for n in nodes(tree) if n.get('pid')==candidate.pid and (n.get('name') or '').startswith('Azahar ') and not (n.get('window_properties') or {}).get('transient_for')]
      if windows:
       subprocess.run(['swaymsg','-s',str(sock),f'[con_id={windows[0]["id"]}] kill'],check=True)
       break
     try:candidate.wait(timeout=10)
     except subprocess.TimeoutExpired:
      candidate.terminate();candidate.wait(timeout=10)
    time.sleep(1)
   print('Test exited',candidate.returncode,flush=True)
 finally:
  if candidate is not None and candidate.poll() is None:
   candidate.terminate()
   try:candidate.wait(timeout=10)
   except subprocess.TimeoutExpired:candidate.kill();candidate.wait()
  if candidate is not None and log.exists():
   shutil.copy2(log,w/'opengl-after.log')
  signal.pidfd_send_signal(fd,signal.SIGCONT)
  os.close(fd);os.close(child_fd)
  (w/'test-finished').write_text(str(time.time())+'\n')
  print('Original Vulkan kiosk resumed',flush=True)
