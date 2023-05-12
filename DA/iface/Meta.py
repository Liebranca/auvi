#!/usr/bin/python
# ---   *   ---   *   ---
# IFACE META
# Massive imports
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
from bpy.types import(

  Scene,

  Object,
  Mesh,
  Material,
  Action,
  Armature,

  Image,

  PropertyGroup,

  Panel,
  Operator,

  UIList

);

from bpy.utils import(
  register_class,
  unregister_class

);

from bpy.props import(
  StringProperty,
  EnumProperty,
  FloatProperty,
  FloatVectorProperty,
  IntProperty,
  BoolProperty,
  BoolVectorProperty,
  PointerProperty,
  CollectionProperty

);

# ---   *   ---   *   ---
