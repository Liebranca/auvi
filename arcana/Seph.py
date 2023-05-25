#!/usr/bin/python
# ---   *   ---   *   ---
# SEPH
# Even hotter
# see: bitter/kvrnel/Seph.hpp
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

from mathutils import Vector;

from math import (

  sin,
  cos,
  acos,
  atan2,

  radians,

);

from .Bytes import (

  frac,
  unfrac,

  FRAC_SIGNED,
  FRAC_UNSIGNED,

  ROUND_NVEC,
  ROUND_CORD,
  ROUND_LINE,

);

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.2b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

PI=3.14159265;

# ---   *   ---   *   ---

class Seph:

  # modes
  NORMAL = 0x00;
  POINT  = 0x01;
  QUAT   = 0x02;
  NC     = 0x03;

  # cstruc
  def __init__(

    self,
    mode,

    rad_nbits,
    zen_nbits,
    azi_nbits

  ):

    self.mode      = mode;

    self.rad_nbits = rad_nbits;
    self.zen_nbits = zen_nbits;
    self.azi_nbits = azi_nbits;

    # bmask for unpack
    self.rad_mask  = (1 << rad_nbits)-1;
    self.zen_mask  = (1 << zen_nbits)-1;
    self.azi_mask  = (1 << azi_nbits)-1;

    # get wall
    self.rad_maxp  = (1 << (rad_nbits)
      if   self.mode==Seph.NC
      else 1 << (rad_nbits-2)

    );

    self.zen_maxp  = 1 << (zen_nbits-1);
    self.azi_maxp  = 1 << (azi_nbits-1);

    # get precision
    self.rad_step  = 1.0  / self.rad_maxp;
    self.zen_step  = PI   / self.zen_maxp;
    self.azi_step  = PI   / self.azi_maxp;

# ---   *   ---   *   ---
# encodes normalized vector

  def angle_pack(self,n):

    out=0x00;

    # get coords as angles
    zen=acos(n.y);
    azi=atan2(n.x,n.z);

    # ^pack values
    out|=frac(

      zen,

      self.zen_step,
      self.zen_nbits-1,

      FRAC_SIGNED,
      ROUND_NVEC,

    ) << 0;

    out|=frac(

      azi,

      self.azi_step,
      self.azi_nbits-1,

      FRAC_SIGNED,
      ROUND_NVEC,

    ) << self.zen_nbits;

    return out;

# ---   *   ---   *   ---
# ^undo

  def angle_unpack(self,b):

    # retrieve packed elements
    bzen = b &  self.zen_mask;
    b    = b >> self.zen_nbits;

    bazi = b &  self.azi_mask;

    # float-ify
    zen=unfrac(

      bzen,

      self.zen_step,
      self.zen_nbits-1,

      FRAC_SIGNED

    );

    azi=unfrac(

      bazi,

      self.azi_step,
      self.azi_nbits-1,

      FRAC_SIGNED

    );

    szen = sin(zen);

    x    = szen * sin(azi);
    y    = cos(zen);
    z    = szen * cos(azi);

    return Vector([x,y,z]);

# ---   *   ---   *   ---
# magnitude of vector eq sphere radius

  def radius_pack(p):

    return frac(

      p.length,

      self.rad_step,
      self.rad_nbits-1,

      FRAC_UNSIGNED,
      ROUND_LINE

    );

# ---   *   ---   *   ---
# ^undo

  def radius_unpack(self,b):

    return unfrac(

      b & self.rad_mask,

      self.rad_step,
      self.rad_nbits-1,

      FRAC_UNSIGNED

    );

# ---   *   ---   *   ---
# vector to packed spherical coords

  def pack(self,a):

    if self.mode == Seph.NORMAL:
      return self.angle_pack(a);

    else:

      radius = self.radius_pack(a);
      a      = a.normalized();

      angle  = self.angle_pack(a);

      return radius | (angle << self.rad_nbits);

# ---   *   ---   *   ---
# ^undo

  def unpack(self,b,bug=False):

    if self.mode == Seph.NORMAL:
      return self.angle_unpack(b).normalized();

    else:

      r = self.radius_unpack(b);
      b = b >> self.rad_nbits;

      n = self.angle_unpack(b);

      return n.normalized()*r;

# ---   *   ---   *   ---
