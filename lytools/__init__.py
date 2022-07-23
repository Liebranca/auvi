import sys;
import subprocess;

from os import (
  environ as ENV,

  getcwd,
  chdir

);

# ---   *   ---   *   ---

ROOT='/'.join(__file__.split("/")[0:-2]);
DROOT=ROOT+'/data';

# ---   *   ---   *   ---

paths:dict={

  'ARPATH':ENV['ARPATH'],

  'arcana':ROOT+'/arcana',
  'lytools':ROOT+'/lytools',
  'xforms':ROOT+'/xforms',

};

if(not len(paths['ARPATH'])):

  print(

    "ARPATH is not set -- " \
    "something's def wrong with you\n"

  );

  exit();

# ---   *   ---   *   ---

for v in paths.values():
  if v not in sys.path:
    sys.path.append(v);

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

from .PYZJC import *;
from ctypes import cdll;

def wrap_cfunc(lib, funcname, restype, argtypes):

    func          = lib.__getattr__(funcname)
    func.restype  = restype
    func.argtypes = argtypes

    return func

# ---   *   ---   *   ---

pastcwd=getcwd();
im_c=cdll.LoadLibrary(f"{paths['xforms']}/im.so");

chdir(pastcwd);

# ---   *   ---   *   ---

im_c_nit=wrap_cfunc(
  im_c,"nit",None,[size_t],

);

im_c_del=wrap_cfunc(
  im_c,"del",None,[],

);

im_c_take=wrap_cfunc(

  im_c,"take",size_t,[

    size_t,
    size_t,
    size_t,

    star(c_float)

  ],

);

im_c_get_buff=wrap_cfunc(
  im_c,"get_buff",star(c_float),[size_t],

);

# ---   *   ---   *   ---

#import struct; plat=struct.calcsize("P") * 8
#plat='x64' if plat==64 else 'Win32'

# MAKING CTYPES ARRAYS
#
#    pth_l  = [
#      cstr(kvrdir),
#      cstr(root+"\\"),
#      cstr(""),
#      cstr(pecwd)
#
#    ];
#
#    arr=(charstar * len(pth_l))();
#    arr[:]=pth_l;
