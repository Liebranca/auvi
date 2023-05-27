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

from arcana.Mod import pelist;

import bpy;
from bpy.types import(

  Collection,
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
# generates codestr
# for register func

def DA_register(kls_l,bind={}):

# another example of the
# inherent silliness of
# significant whitespace,
#
# metahacks are even more
# unreadable than usual
# when you can't format them
# however the hell you please
#
# this would only be acceptable
# in an environment where these
# techniques are never needed
#
# but you'd need good design
# for that to be the case

  prol=(

    # lame fwd decl
    "unregister=None;\n"

    # actual code
  + "def register():\n"
  + "  bpy.da_blocks[__file__]=unregister;\n"

  );

  body="";
  for name in kls_l:
    body=body+f"  register_class({name});\n";

  epil="";
  for key,value in bind.items():

    epil=epil+(

      f"  {key}=PointerProperty(\n"
    + f"    type={value}\n"

    +  "  );\n"

    );

  return ''.join([prol,body,epil]);

# ---   *   ---   *   ---
# ^undo

def DA_unregister(kls_l,bind={}):

  prol="def unregister():\n";

  for key in bind.keys():
    prol=prol+f"  del {key};\n";

  body="";
  for name in kls_l:
    body=body+f"  unregister_class({name});\n";

  return ''.join([prol,body]);

# ---   *   ---   *   ---
# ^makes both from string input

def DA_iface_module(s):

  d=pelist(s);

  if 'rclass' not in d:
    d['rclass']=[];

  if 'uclass' not in d:
    d['uclass']=[];

  if 'bind' not in d:
    d['bind']={};

  a=DA_register(
    d['rclass'],
    d['bind']

  );

  b=DA_unregister(

    d['rclass']
  + d['uclass'],

    d['bind']

  );

  return a+"\n"+b+"\n";

# ---   *   ---   *   ---
