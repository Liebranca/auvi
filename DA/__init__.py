#!/usr/bin/python
# ---   *   ---   *   ---
# DA
# DarkAge to Blender
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import bpy;
from importlib import reload;
from arcana import Mod;

from .iface import Apparel;
from .iface import Attach;
from .iface import State;
from .iface import Char;
from .iface import Anim;
from .iface import Spritebake;

from .iface import CRK;

# ---   *   ---   *   ---
# used to reload the entire module
# from blender's python console

def update():

  if(hasattr(bpy,'da_blocks')):
    for key in bpy.da_blocks:
      bpy.da_blocks[key]();

# ---   *   ---   *   ---

  bpy.da_blocks={};
  for mod in [

    Apparel,Attach,
    State,Char,Anim,
    Spritebake,CRK

  ]:

    reload(mod);
    mod.register();

# ---   *   ---   *   ---
