#!/usr/bin/python
# ---   *   ---   *   ---
# FMAT
# What files come in
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

from Avt.cwrap import *;

# ---   *   ---   *   ---
# typenames added to this space
# so sizeof.[type] == sizeof(type);

class sizeof:
  pass;

# ---   *   ---   *   ---
# info

class Fmat:

  VERSION = 'v0.00.2b';
  AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# cstruc

  def __init__(self,name,table,total=0):

    self.__strucf__ = [];
    self.__strucn__ = name;

    sumof=0;

    for i in range(0,len(table),2):

      key = table[i+0];
      sz  = table[i+1];

      setattr(self,key,None);
      setattr(sizeof,name+f"_{key}",sz);

      self.__strucf__.append(key);

      sumof+=sz;

    if(total>sumof):
      sumof=total;

    setattr(sizeof,name,sumof);

# ---   *   ---   *   ---
# lookup sizes of fields
# and whole struct

  def field_sz(self,key):
    return sizeof.__dict__[
      self.__strucn__+f"_{key}"

    ];

  def struc_sz(self):
    return sizeof.__dict__[
      self.__strucn__

    ];

# ---   *   ---   *   ---
# read sizeof(ice) from file

  def read(self,file):

    out   = {};
    sumof = 0;

    for key in self.__strucf__:
      sz    = self.field_sz(key);
      entry = file.read(sz);

      if(entry==bytes('','ascii')):
        break;

      out[key]=int.from_bytes(entry,'little');
      sumof+=sz;

    left=self.struc_sz()-sumof;

    if(left):
      file.read(left);

    return out;

# ---   *   ---   *   ---
