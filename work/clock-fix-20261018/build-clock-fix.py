#!/usr/bin/python3
"""Incrementally rebuild one clock object, preserving the installed build's other changes."""
from pathlib import Path
import hashlib
import json
import os
import shlex
import shutil
import subprocess

root=Path.home()/'azahar-build'
build=root/'build'
work=root/'clock-fix-20261018'
work.mkdir(exist_ok=True)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
original=build/'bin/Release/azahar'
assert sha(original)==sha('/usr/bin/azahar'),'Cached build differs from installed emulator'
baseline=sha(original)
obj='src/core/CMakeFiles/citra_core.dir/hle/kernel/shared_page.cpp.o'
compile_line=subprocess.check_output(['ninja','-t','commands',obj],cwd=build,text=True).splitlines()[-1]
args=shlex.split(compile_line)
for flag in ('-o','-MF'):
    args[args.index(flag)+1]=str(work/('shared_page.cpp.o' if flag=='-o' else 'shared_page.cpp.o.d'))
args[-1]=str(work/'shared_page.cpp')
# A stale precompiled header can belong to a different compiler. Use the same
# headers directly without changing the cached project or other objects.
if '-include' in args:
    i=args.index('-include');del args[i:i+2]
if '-Winvalid-pch' in args:args.remove('-Winvalid-pch')
subprocess.run(args,cwd=build,check=True)
archive=work/'libcitra_core.a'
shutil.copyfile(build/'src/core/libcitra_core.a',archive)
subprocess.run(['ar','rD',str(archive),str(work/'shared_page.cpp.o')],check=True)
line=subprocess.check_output(['ninja','-t','commands','bin/Release/azahar'],cwd=build,text=True).splitlines()[-1]
args=shlex.split(line)
assert args[:2]==[':', '&&'] and args[-2:]==['&&',':']
args=args[2:-2]
# The build cached a Qt patch version. Link to the currently installed Qt6
# SONAME used by the running binary, without altering system libraries.
for i,arg in enumerate(args):
    if arg.startswith('/usr/lib/libQt6') and '.so.6.' in arg and not Path(arg).exists():
        soname=arg.split('.so.6.')[0]+'.so.6'
        assert Path(soname).exists(),soname
        args[i]=soname
args=[str(archive) if a=='src/core/libcitra_core.a' else a for a in args]
args[args.index('-o')+1]=str(work/'azahar')
args=[('-Wl,--dependency-file='+str(work/'link.d')) if a.startswith('-Wl,--dependency-file=') else a for a in args]
subprocess.run(args,cwd=build,check=True)
result=subprocess.check_output(['ldd',str(work/'azahar')],text=True)
assert 'not found' not in result,result
(work/'manifest.json').write_text(json.dumps({'baseline_sha256':baseline,'fixed_sha256':sha(work/'azahar')},indent=2)+'\n')
env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen'
subprocess.run([str(work/'azahar'),'--help'],env=env,check=True,stdout=subprocess.DEVNULL,timeout=20)
print('Clock build and runtime-library checks passed. Manifest:',work/'manifest.json')
