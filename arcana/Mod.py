#!/usr/bin/python
# ---   *   ---   *   ---
# MOD
# Python module-making utils
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

from . import ARPATH
from . import Xfer;

# ---   *   ---   *   ---
# generic dict fetch

def load_config(dst,fname):
  path=ARPATH+'/.config/'+fname;

  if(os.path.exists(path)):
    d=Xfer.load(path);

    for key,value in d.items():
      dst[key]=value;

# ---   *   ---   *   ---
