import sys;

import subprocess;
from os import environ as ENV;

# ---   *   ---   *   ---

ROOT='/'.join(__file__.split("/")[0:-2]);
DROOT=ROOT+'/data';

# maybe we want to add more paths to this later?
for v in [ROOT]:
  if v not in sys.path:
    sys.path.append(v);

# ---   *   ---   *   ---

paths:dict={

  'ARPATH':ENV['ARPATH'],

  'arcana':ROOT+'/arcana',
  'lytools':ROOT+'/lytools'

};

if(not len(paths['ARPATH'])):

  print(

    "ARPATH is not set -- " \
    "something's def wrong with you\n"

  );

  exit();

# ---   *   ---   *   ---

def cmd(proc:str,args:list=[]):

  l:list=[proc];
  for arg in args:
    l.append(arg);

  out:str=subprocess.run(
    l,stdout=subprocess.PIPE

  ).stdout.decode();

  return out;

# ---   *   ---   *   ---
# i'd overwrite os.walk *just* out of spite
# but that'd be too much

def walk(path:str,lookfor:str=''):

  w:str=cmd(
    paths['arcana']+'/walk',
    [path,lookfor]

  );w=w.split("\n");

  return w;

# ---   *   ---   *   ---
#
#from .PYZJC import *;
#
#def wrap_cfunc(lib, funcname, restype, argtypes):
#
#    func          = lib.__getattr__(funcname)
#    func.restype  = restype
#    func.argtypes = argtypes
#
#    return func
#
#import struct; plat=struct.calcsize("P") * 8
#plat='x64' if plat==64 else 'Win32'
#
## pulla dir switcharoo so we can find dll
#pastcwd=os.getcwd(); os.chdir(f"{root}\\bin\\{plat}");
#
#from ctypes import WinDLL;
#CSIDE=WinDLL(f"{root}\\bin\\{plat}\\blkmgk.dll");
#
## eh, sucks not to have -rpath
#os.chdir(pastcwd);
#
#DLBLKMGK  = wrap_cfunc(CSIDE, "DLBLKMGK", None,       [                          ]);
#_NTBLKMGK = wrap_cfunc(CSIDE, "NTBLKMGK", None,       [star(charstar)            ]);
#_UTJOJ    = wrap_cfunc(CSIDE, "UTJOJ",    None,       [uint, uint, uint, charstar]);
#_INJOJ    = wrap_cfunc(CSIDE, "INJOJ",    None,       [uint                      ]);
#
## ---   *   ---   *   ---
#
#import bpy; from . import blmod;
#
#def UTJOJ(i, dim, level, name): _UTJOJ(i, dim, level, cstr(name));
#def INJOJ(i                  ): _INJOJ(i);
#
#def NTBLKMGK(pecwd):
#
#    kvrdir = root;
#
#    pth_l  = [cstr(kvrdir), cstr(root+"\\"), cstr(""), cstr(pecwd)];
#    arr    = (charstar * len(pth_l))(); arr[:]=pth_l;
#
#    _NTBLKMGK(arr);
