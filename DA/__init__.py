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

import bpy;
from importlib import reload;

from .iface import Anim;
from .iface import Char;

def update():

  if(hasattr(bpy,'da_blocks')):
    for key in bpy.da_blocks:

      try:
        bpy.da_blocks[key]();

      except:
        print("Couldn't unreg: %s"%key);

# ---   *   ---   *   ---

  bpy.da_blocks={};
  for mod in [Anim,Char]:
    reload(mod);
    mod.register();

# ---   *   ---   *   ---
