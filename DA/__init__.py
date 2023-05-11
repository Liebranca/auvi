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

from .guts import N3;
from .guts import Matbake as Matbake_guts;

from .iface import (

  Apparel,Attach,
  State,Char,Anim,

  Spritebake,Matbake,

  CRK,

);

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.5a';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# used to reload the entire module
# from blender's python console

def update():

  # handle unregister
  if(hasattr(bpy,'da_blocks')):
    for key in bpy.da_blocks:
      bpy.da_blocks[key]();

  # ^re-register
  bpy.da_blocks={};
  for mod in [

    Apparel,Attach,
    State,Char,Anim,

    Spritebake,Matbake,

    CRK,

  ]:

    reload(mod);
    mod.register();

  # ^reload common modules
  for mod in [
    N3,Matbake_guts

  ]:

    reload(mod);

# ---   *   ---   *   ---
