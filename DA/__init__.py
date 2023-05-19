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

from .guts import (

  Meta    as Meta_guts,
  Matbake as Matbake_guts,
  CRK     as CRK_guts,

  N3,

);

from .iface import (

  Meta,

  Apparel,Attach,
  State,Char,Anim,

  Spritebake,Matbake,

  CRK,

);

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.6a';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# used to reload the entire module
# from blender's python console

def update():

  # handle unregister
  if(hasattr(bpy,'da_blocks')):
    for key in bpy.da_blocks:
      bpy.da_blocks[key]();

  reload(Meta);

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

    Meta_guts,
    Matbake_guts,
    CRK_guts,

    N3,

  ]:

    reload(mod);

# ---   *   ---   *   ---
