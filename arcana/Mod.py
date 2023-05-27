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
# """fixes""" for GENIUS design
#
# will import methods from
# one class into another

def bl_kls_merge(name):

# NOTE: lyeb@IBN-3DILA, 05/26/23 00:41
#
# an example of significant
# whitespace being silly,
#
# a throwaway metahack for
# blenders backwards API
# must be correctly indented
# or execution will fail
#
# so: i must un-indent the
# multi-line string, making
# this entire F look wrong,
# as parts of it's body don't
# follow correct indentation
#
# however: skipping newline and
# ident at the end of the codestr?
#
# that's just fine. put a semi ;>
#
# what can i say...
# walrus van rossum strikes again

  SRC="""

methods=[
  attr for attr in dir($:KLS;>)
  if  callable(getattr($:KLS;>,attr))
  and not attr.startswith('__')

];

for m in methods:
  exec(f"{m}=getattr($:KLS;>,'{m}');");

del methods;
del m;

""";return SRC.replace('$:KLS;>',name);

# ^the worse thing about this?
# it works...

# ---   *   ---   *   ---
# reads pelist in perl
#
# could be done in python
# but i value my time

def pelist(s):

  return eval(Xfer.DOS(
    ARPATH+'/auvi/bin/pepy',[s]

  ));

# ---   *   ---   *   ---
