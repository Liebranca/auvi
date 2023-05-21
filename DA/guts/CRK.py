#!/usr/bin/python
# ---   *   ---   *   ---
# CRK GUTS
# Mesh-baking madness
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import os,bpy,bmesh;

from Avt.cwrap import (
  real,wide,byte,
  pastr8,ftb,

);

from arcana.Fmat import *;
from arcana.Tools import basef,chkdir;
from arcana.Xfer import DOS;
from arcana.Bytes import unfrac_u8,unfrac_u8_vec3;
from arcana.Seph import *;

from .Meta import *;

# ---   *   ---   *   ---
# info

VERSION = 'v1.00.2';
AUTHOR  = 'IBN-3DILA';

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

  # file read modes
  UNPACK_BMESH={
    'use_pseph': 1,

  };

  pseph=Seph(Seph.POINT,8,8,8);

# ---   *   ---   *   ---
# ice of this class used to
# remember original object
# and bake settings

  def __init__(self,ob,hier=False):

    self.pose = None;

    self.ob   = ob;
    self.hier = hier;

  def __del__(self):
    self.clear_pose();

# ---   *   ---   *   ---
# apply all mods/deforms/shapes
# into copy of object

  def bake_pose(self):

    if self.pose:
      self.clear_pose();

    children=[];

    if self.hier:
      children=get_hierarchy(self.ob);

    select_all(self.ob,children);
    self.pose=duplibake(True,True);

    n=self.ob.name+'.CRKP';
    self.pose.name=self.pose.data.name=n;

  def clear_pose(self):

    if not self.pose:
      return;

    bpy.data.meshes.remove(self.pose.data);
    self.pose=None;

# ---   *   ---   *   ---
# converts primitives from crk
# into a python object
#
# mesh can then be iced
# through mesh.from_pydata()

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
          vert[0],-vert[2],vert[1],

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
# gives pydata to recreate
# mesh within blender

  @staticmethod
  def read(fpath,use_pseph=0):

    out    = [];

    xyz_fn = (CRK.pseph.unpack
      if   use_pseph
      else unfrac_u8_vec3

    );

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

          xyz  = (

            (vert['X'] <<  0)
          | (vert['Y'] <<  8)
          | (vert['Z'] << 16)

          );

          uf.extend(xyz_fn(xyz));

          uf.append(unfrac_u8(vert['UVX']));
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
  def from_bmesh(ob,fpath,hier=False):

    self  = CRK(ob,hier);
    fpath = chkdir(fpath,ob.name);

    # generate temp
    files=self.bake(fpath);

    # invoke C-side
    DOS('bmesh2crk',[fpath]);

    # ^clean temp
    for f in files:
      os.remove(f);

    select_all(self.ob,[]);

# ---   *   ---   *   ---
# ^goes through

  def bake(self,fpath):

    # initial bake required for
    # triangulation, else polycount
    # would be wrong
    self.bake_pose();

    # placeholder
    mat   = 0;
    poses = 1;

    # remember files created
    # for later cleanup
    files = [f"{fpath}_meta"];

    # serialize metadata
    with open(files[-1],'wb+') as f:
      f.write(self.bl_write_meta(poses,mat));

    # ^serialize each pose
    for i in range(0,poses):

      files.append(f"{fpath}_pose{i}");

      # TODO: bl_adv_pose for animated meshes
      with open(files[-1],'wb+') as f:
        f.write(self.bl_write_pose());

    return files;

# ---   *   ---   *   ---
# ^takes note of metadata

  def bl_write_meta(self,poses,mat):

    me    = self.pose.data;
    hbuff = bytearray(CRK.DUMP_HED_SZ);

    hbuff[0:2]=ftb(wide,[len(me.vertices)]);
    hbuff[2:4]=ftb(wide,[len(me.polygons)*3]);
    hbuff[4:6]=ftb(wide,[poses]);
    hbuff[6:8]=ftb(wide,[mat]);

    return hbuff;

# ---   *   ---   *   ---
# ^called once per frame or static

  def bl_write_pose(self):

    self.bake_pose();
    me=self.pose.data;

    ibuff=bytearray(len(me.polygons) * 6);
    vbuff=bytearray(
      len(me.vertices) * CRK.DUMP_STRIDE

    );

    # get bounding box size
    bbuff=self.bl_write_box();

    # serialize pose
    self.bl_write_cords(vbuff,ibuff);
    self.bl_write_tangents(vbuff);

    return bbuff + ibuff + vbuff;

# ---   *   ---   *   ---
# ^serialize bounding box

  def bl_write_box(self):

    d     = self.pose.dimensions;
    bbuff = bytearray(3*4);

    bbuff[ 0 :  4]=ftb(real,[d.x / 2]);
    bbuff[ 4 :  8]=ftb(real,[d.z    ]);
    bbuff[ 8 : 12]=ftb(real,[d.y / 2]);

    return bbuff;

# ---   *   ---   *   ---
# ^write vertex cords, normals, uvs
# and indices to pre-allocated buffers

  def bl_write_cords(self,vbuff,ibuff):

    me    = self.pose.data;

    loops = me.uv_layers.active.data;
    idex  = 0;

    vt    = [None for i in range(len(me.vertices))];

    for face in me.polygons:
      for vi,li in zip(
        face.vertices,
        face.loop_indices

      ):

        svi  = vi * CRK.DUMP_STRIDE;
        loop = me.loops[li];
        vert = me.vertices[vi];

        vt[vi]=vert;

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

  def bl_write_tangents(self,vbuff):

    me=self.pose.data;
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
# iv of from_bmesh;
# makes bmesh from crk file

  @staticmethod
  def load(fpath,mode=UNPACK_BMESH,name=""):

    if not len(name):
      name=basef(name);

    if name in bpy.data.meshes:
      bpy.data.meshes.remove(
        bpy.data.meshes[name]

      );

    me   = bpy.data.meshes.new(name);
    ob   = bpy.data.objects.new(name,me);

    src  = CRK.read(fpath,*mode);
    self = CRK(ob);

    self.load_poses(src);
    link_object(ob);

# ---   *   ---   *   ---
# TODO: loading material
#    me.materials.append();

# ---   *   ---   *   ---
# read in single pose data from
# source file (see: CRK.read)

  def load_pose(self,src,i):

    verts = src[i]['co'];
    faces = src[i]['face'];
    uvs   = src[i]['uv'];

    if i==0:
      self.ice_t(verts,faces,uvs);

    else:
      make_shape(self.ob,verts,'pose_'+str(i));

# ---   *   ---   *   ---
# ^bat

  def load_poses(self,src):

    for i in range(len(src)):
      self.load_pose(src,i);

# ---   *   ---   *   ---
# instance default pose

  def ice_t(self,verts,faces,uvs):

    me  = self.ob.data;

    beg = faces[0][0];
    i   = 0;

    me.from_pydata(verts,[],faces);
    me.uv_layers.new();

    for face in me.polygons:
      for vi,loop in zip(
        face.vertices,
        face.loop_indices

      ):

        loop=me.uv_layers.active.data[loop];
        loop.uv[:]=uvs[vi][:];

# ---   *   ---   *   ---
