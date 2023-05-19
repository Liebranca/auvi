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

BITS=[i for i in range(0,16)];
STEP=[1.0/(1<<i) for i in range(1,17)];
MAXV=[(1<<i)-1 for i in range(1,17)];

ROUND_NVEC=1.25;
ROUND_CORD=0.64;

ROUND_MODE=ROUND_NVEC;

# ---   *   ---   *   ---
# float to linear int

def frac(x,step,nbits,unsig=False):

  mid  = 1<<nbits;
  max  = MAXV[nbits];

  midp = mid if not unsig else 1;

  b    = round(x/step);
  top  = step*(max-mid);

  top -= step*ROUND_MODE;

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

def frac_u8(x):
  return frac(x,STEP[7],BITS[7],True);

def unfrac_u8(b):
  return unfrac(b,STEP[7],BITS[7],True);

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
