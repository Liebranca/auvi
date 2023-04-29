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

import os;

from mathutils import Vector;
from Avt.cwrap import real,wide,ftb;

from .Fmat import *;
from .Xfer import DOS;

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

  # size of single raw vert
  DUMP_STRIDE=56;

  # verts + indices + poses + matidex
  DUMP_HED_SZ=2+2+2+2;

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
# write blender mesh data to
# binary float dump
#
# THEN invoke bmesh2crk

  @staticmethod
  def bl_to_crk(ob,fpath):

    me    = ob.data;
    mat   = 0;
    poses = 1;

    files = [f"{fpath}_meta"];

    # serialize metadata
    with open(files[-1],'wb+') as f:
      f.write(CRK.bl_write_meta(me,poses,mat));

    # ^serialize each pose
    for i in range(0,poses):

      files.append(f"{fpath}_pose{i}");

      # TODO: bl_adv_pose for animated meshes
      with open(files[-1],'wb+') as f:
        f.write(CRK.bl_write_pose(ob));

    # invoke C-side
    DOS('bmesh2crk',[fpath]);

    # clean temp files
    for f in files:
      os.remove(f);

# ---   *   ---   *   ---
# ^takes note of metadata

  @staticmethod
  def bl_write_meta(me,poses,mat):

    hbuff=bytearray(CRK.DUMP_HED_SZ);

    hbuff[0:2]=ftb(wide,[len(me.vertices)]);
    hbuff[2:4]=ftb(wide,[len(me.polygons)*3]);
    hbuff[4:6]=ftb(wide,[poses]);
    hbuff[6:8]=ftb(wide,[mat]);

    return hbuff;

# ---   *   ---   *   ---
# ^called once per frame or static

  @staticmethod
  def bl_write_pose(ob):

    me    = ob.data;

    ibuff = bytearray(len(me.polygons) * 6);
    vbuff = bytearray(
      len(me.vertices) * CRK.DUMP_STRIDE

    );

    # get bounding box size
    bbuff=CRK.bl_write_box(ob);

    # serialize pose
    CRK.bl_write_cords(me,vbuff,ibuff);
    CRK.bl_write_tangents(me,vbuff);

    return bbuff + ibuff + vbuff;

# ---   *   ---   *   ---
# ^serialize bounding box

  @staticmethod
  def bl_write_box(ob):

    bbuff=bytearray(3*4);
    bbuff[ 0 :  4]=ftb(real,[ob.dimensions.x/2]);
    bbuff[ 4 :  8]=ftb(real,[ob.dimensions.z]);
    bbuff[ 8 : 12]=ftb(real,[ob.dimensions.y/2]);

    return bbuff;

# ---   *   ---   *   ---
# ^write vertex cords, normals, uvs
# and indices to pre-allocated buffers

  @staticmethod
  def bl_write_cords(me,vbuff,ibuff):

    loops = me.uv_layers.active.data;
    idex  = 0;

    for face in me.polygons:
      for vi,li in zip(
        face.vertices,
        face.loop_indices

      ):

        svi  = vi * CRK.DUMP_STRIDE;
        loop = me.loops[li];
        vert = me.vertices[vi];

        # write coords
        co=vert.co;
        vbuff[svi +  0 : svi +  4]=ftb(real,[ co[0]]);
        vbuff[svi +  4 : svi +  8]=ftb(real,[ co[2]]);
        vbuff[svi +  8 : svi + 12]=ftb(real,[-co[1]]);

        # write normals
        n=vert.normal;
        vbuff[svi + 12 : svi + 16]=ftb(real,[ n[0]]);
        vbuff[svi + 16 : svi + 20]=ftb(real,[ n[2]]);
        vbuff[svi + 20 : svi + 24]=ftb(real,[-n[1]]);

        # write uvs
        uv=loops[li].uv;
        vbuff[svi + 48 : svi + 52]=ftb(real,[uv[0]]);
        vbuff[svi + 52 : svi + 56]=ftb(real,[uv[1]]);

        # write indices
        ibuff[idex+0:idex+2]=vi.to_bytes(2,'little');
        idex+=2;

# ---   *   ---   *   ---
# ^write tangents and bitangents

  @staticmethod
  def bl_write_tangents(me,vbuff):

    me.calc_tangents();

    for face in me.polygons:
      for vi,li in zip(
        face.vertices,
        face.loop_indices

      ):

        svi  = vi * CRK.DUMP_STRIDE;
        loop = me.loops[li];
        vert = me.vertices[vi];

        # write tangent
        t=loop.tangent;
        t=[t[0],t[2],-t[1]];
        vbuff[svi + 24 : svi + 28]=ftb(real,[t[0]]);
        vbuff[svi + 28 : svi + 32]=ftb(real,[t[1]]);
        vbuff[svi + 32 : svi + 36]=ftb(real,[t[2]]);

        # write bitangent
        b=loop.bitangent;
        b=[b[0],b[2],-b[1]];
        vbuff[svi + 36 : svi + 40]=ftb(real,[b[0]]);
        vbuff[svi + 40 : svi + 44]=ftb(real,[b[1]]);
        vbuff[svi + 44 : svi + 48]=ftb(real,[b[2]]);

    me.free_tangents();

# ---   *   ---   *   ---
