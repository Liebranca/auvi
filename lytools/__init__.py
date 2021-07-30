import sys, os;

s=__file__.split("\\"); i=0;
for sub in s[::-1]:
    if sub=="lytools":
        break;
    
    i+=1;

root="\\".join(s[0:-(i+1)]);
if root not in sys.path:
    sys.path.append(root);

#///////////////////////////////////////////

from .PYZJC import *;

def wrap_cfunc(lib, funcname, restype, argtypes):

    func          = lib.__getattr__(funcname)
    func.restype  = restype
    func.argtypes = argtypes

    return func

import struct; plat=struct.calcsize("P") * 8
plat='x64' if plat==64 else 'Win32'

# pulla dir switcharoo so we can find dll
pastcwd=os.getcwd(); os.chdir(f"{root}\\bin\\{plat}");

from ctypes import WinDLL;
CSIDE=WinDLL(f"{root}\\bin\\{plat}\\blkmgk.dll");

# eh, sucks not to have -rpath
os.chdir(pastcwd);

DLBLKMGK  = wrap_cfunc(CSIDE, "DLBLKMGK", None,       [                          ]);
_NTBLKMGK = wrap_cfunc(CSIDE, "NTBLKMGK", None,       [star(charstar)            ]);
_UTJOJ    = wrap_cfunc(CSIDE, "UTJOJ",    None,       [uint, uint, uint, charstar]);
_INJOJ    = wrap_cfunc(CSIDE, "INJOJ",    None,       [uint                      ]);

#///////////////////////////////////////////

import bpy; from . import blmod;

def UTJOJ(i, dim, level, name): _UTJOJ(i, dim, level, cstr(name));
def INJOJ(i                  ): _INJOJ(i);

def NTBLKMGK(pecwd):

    kvrdir = root;

    pth_l  = [cstr(kvrdir), cstr(root+"\\"), cstr(""), cstr(pecwd)];
    arr    = (charstar * len(pth_l))(); arr[:]=pth_l;

    _NTBLKMGK(arr);