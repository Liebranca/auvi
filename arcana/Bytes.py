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

from .Fmat import *;

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

class CRK:

  VERTEX=Fmat(

    'CRK_VERTEX',[

      'X',1,'Y',1,'Z',1,
      'N',1,'T',1,'B',1,

      'UVX',1,'UVY',1,

      'ID',   2,
      'BONE', 2,

    ],

    total=16

  );

  HEADER=Fmat(

    'CRK_HEADER',[

      'sig',    4,

      'vcount', 2,
      'icount', 2,

      'cnt',    8,

    ],

  );

  PRIM=Fmat(

    'CRK_PRIM',[

      'vcount',2,
      'icount',2,

    ],

  );

# ---   *   ---   *   ---

  @staticmethod
  def bl_topy(raw):

    out=[];
    for prim in raw:

      verts   = prim[0];
      indices = prim[1];

      bl_prim = {

        'co'   : [],
        'uv'   : [],

        'face' : [],

      };

# ---   *   ---   *   ---

      for vert in verts:

        bl_prim['co'].append((
          vert[0],vert[1],vert[2],

        ));

        bl_prim['uv'].append((
          vert[3],vert[4],

        ));

# ---   *   ---   *   ---

      for i in range(0,len(indices),3):

        bl_prim['face'].append((
          indices[i+0],
          indices[i+1],
          indices[i+2],

        ));

# ---   *   ---   *   ---

      out.append(bl_prim);

    return out;

# ---   *   ---   *   ---

  @staticmethod
  def read(fpath):

    out=[];

    with open(fpath,'rb') as file:

      hed=CRK.HEADER.read(file);

      for i in range(hed['cnt']):

        p       = CRK.PRIM.read(file);

        verts   = [];
        indices = [];

        if('vcount' not in p):
          break;

        for _ in range(p['vcount']):

          vert = CRK.VERTEX.read(file);
          uf   = [];

          for key in ['X','Y','Z','UVX']:
            uf.append(unfrac_u8(vert[key]));

          uf.append(1.0-unfrac_u8(vert['UVY']));

          verts.append(uf);

        for _ in range(p['icount']):
          indices.append(int.from_bytes(
            file.read(2),'little'

          ));

        out.append([verts,indices]);

    return CRK.bl_topy(out);

# ---   *   ---   *   ---
