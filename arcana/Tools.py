#!/usr/bin/python
# ---   *   ---   *   ---
# TOOLS
# Stuff I don't want to
# type twice
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

# ---   *   ---   *   ---

def bl_list2enum(l):
  return [(x.upper(),x,'') for x in l];

# ---   *   ---   *   ---
# generic code emitter

def codice(src,keys):

  for key,value in keys.items():
    src=src.replace(key,value);

  return src;

# ---   *   ---   *   ---
