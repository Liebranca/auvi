import sys, os;

s=__file__.split("\\"); i=0;
for sub in s[::-1]:
    if sub=="lytools":
        break;
    
    i+=1;

root="\\".join(s[0:-i]);
if root not in sys.path:
    sys.path.append(root);

#///////////////////////////////////////////

from .PYZJC import *;

def wrap_cfunc(lib, funcname, restype, argtypes):

    func          = lib.__getattr__(funcname)
    func.restype  = restype
    func.argtypes = argtypes

    return func

os.chdir(root);

from ctypes import WinDLL; CSIDE = WinDLL(root + "\\blkmgk.dll");

DLBLKMGK  = wrap_cfunc(CSIDE, "DLBLKMGK", None,       [                          ]);
_NTBLKMGK = wrap_cfunc(CSIDE, "NTBLKMGK", None,       [star(charstar)            ]);
_UTJOJ    = wrap_cfunc(CSIDE, "UTJOJ",    None,       [uint, uint, uint, charstar]);
_INJOJ    = wrap_cfunc(CSIDE, "INJOJ",    None,       [uint                      ]);

#///////////////////////////////////////////

import bpy; from . import blmod;

def UTJOJ(i, dim, level, name): _UTJOJ(i, dim, level, cstr(name));
def INJOJ(i                  ): _INJOJ(i);

def NTBLKMGK(pecwd):

    kvrdir = "\\".join(root.split("\\")[:-2]);
    kvrdir = kvrdir+"\\KVR\\trashcan\\log\\";

    pth_l  = [cstr(kvrdir), cstr(root+"\\"), cstr(""), cstr(pecwd)];
    arr    = (charstar * len(pth_l))(); arr[:]=pth_l;

    _NTBLKMGK(arr);