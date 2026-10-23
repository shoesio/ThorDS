import ctypes as C
E=C.CDLL('libEGL.so.1');G=C.CDLL('libGL.so.1')
def fn(lib,n,r,args):
 f=getattr(lib,n);f.restype=r;f.argtypes=args;return f
p=C.c_void_p;i=C.c_int;u=C.c_uint
get=fn(E,'eglGetPlatformDisplay',p,[u,p,C.POINTER(i)])
d=get(0x31DD,None,None)
major=i();minor=i()
assert fn(E,'eglInitialize',u,[p,C.POINTER(i),C.POINTER(i)])(d,C.byref(major),C.byref(minor))
assert fn(E,'eglBindAPI',u,[u])(0x30A2)
attrs=(i*7)(0x3033,1,0x3040,8,0x3038,0x3038,0x3038)
c=p();n=i()
assert fn(E,'eglChooseConfig',u,[p,C.POINTER(i),C.POINTER(p),i,C.POINTER(i)])(d,attrs,C.byref(c),1,C.byref(n)) and n.value
ctx=fn(E,'eglCreateContext',p,[p,p,p,C.POINTER(i)])(d,c,None,(i*1)(0x3038))
s=fn(E,'eglCreatePbufferSurface',p,[p,p,C.POINTER(i)])(d,c,(i*5)(0x3057,1,0x3056,1,0x3038))
assert ctx and s
assert fn(E,'eglMakeCurrent',u,[p,p,p,p])(d,s,s,ctx)
string=fn(G,'glGetString',C.c_char_p,[u])
for label,key in [('vendor',0x1F00),('renderer',0x1F01),('version',0x1F02)]:print(label,string(key).decode())
