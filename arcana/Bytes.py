#!/usr/bin/python
# ---   *   ---   *   ---
# BYTES
# Hot stuff
# see: bitter/kvrnel/Bytes.hpp
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

# ---   *   ---   *   ---
# info

VERSION = 'v0.01.0b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

BITS=[i for i in range(0,16)];
STEP=[1.0/(1<<i) for i in range(1,17)];
MAXV=[(1<<i)-1 for i in range(1,17)];

# ---   *   ---   *   ---

ROUND_NVEC    = 1.25;
ROUND_CORD    = 0.64;
ROUND_LINE    = 1.00;

FRAC_SIGNED   = False;
FRAC_UNSIGNED = True;

# ---   *   ---   *   ---
# float to linear int

def frac(

  x,

  step,
  nbits,

  unsig=False,
  rmode=ROUND_NVEC

):

  mid  = 1<<nbits;
  max  = MAXV[nbits];

  midp = mid if not unsig else 1;

  b    = round(x/step);
  top  = step*(max-mid);

  top -= step*rmode;

  b   += mid*(not unsig);
  b   -= 1*(b==max and x<top);

  over = b>max;
  b    = (max*over)+(b*(not over));

  return b;

# ---   *   ---   *   ---
# ^inverse

def unfrac(b,step,nbits,unsig=False):

  mid = 1<<nbits;
  max = MAXV[nbits];

  b  += 1*(b==max);
  b  -= mid*(not unsig);

  return b*step;

# ---   *   ---   *   ---
# aliasing

def frac_u8(x,rmode=ROUND_NVEC):
  return frac(x,STEP[7],BITS[7],True,rmode);

def unfrac_u8(b):
  return unfrac(b,STEP[7],BITS[7],True);

def frac_i8(x,rmode=ROUND_NVEC):
  return frac(x,STEP[7],BITS[7],False,rmode);

def unfrac_i8(b):
  return unfrac(b,STEP[7],BITS[7],False);

# ---   *   ---   *   ---
# ^bat

def unfrac_vec(b,vsz,nbits,step,unsig):

  out=[];

  for _ in range(0,vsz):

    out.append(unfrac_u8(

      b & 0xFF,

      nbits,
      step,

      unsig

    ));

    b = b >> 8;

  return out;

# ---   *   ---   *   ---
# ^bat aliasing ;>

def unfrac_u8_vec3(b):

  return unfrac_vec(

    b,3,

    STEP[7],
    BITS[7],

    FRAC_UNSIGNED

  );

def unfrac_i8_vec3(b):

  return unfrac_vec(

    b,3,

    STEP[7],
    BITS[7],

    FRAC_SIGNED

  );

# ---   *   ---   *   ---
# TODO
#
#   move this somewhere else
#   where mathstuffs reside
#
# calculate bitangent handedness

def bhand (t,b,n):
  t,b,n=Vector(t),Vector(b),Vector(n);
  return -1 if (n.cross(t)).dot(b) < 0 else 1;

# ---   *   ---   *   ---
