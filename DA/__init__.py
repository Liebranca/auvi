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

  Meta,AL,

  Apparel,Attach,
  State,Char,Anim,

  Material,
  Spritebake,Matbake,

  CRK,

);

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.7a';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# TODO: load *.n3 from DAF

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

    AL,

    Apparel,Attach,
    State,Char,Anim,

    Material,
    Spritebake,Matbake,

    CRK,

  ]:

    reload(mod);
    mod.register();

    if hasattr(mod,'on_reload'):
      mod.on_reload();

  # ^reload common modules
  for mod in [

    Meta_guts,
    Matbake_guts,
    CRK_guts,

    N3,

  ]:

    reload(mod);

    if hasattr(mod,'on_reload'):
      mod.on_reload();

# ---   *   ---   *   ---
