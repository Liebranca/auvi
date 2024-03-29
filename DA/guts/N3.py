#!/usr/bin/python
# ---   *   ---   *   ---
# N3
# Node tree!
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import bpy,pickle,os;

from bpy.types import (

  bpy_prop_array,

  Mesh,
  Image,

  ShaderNode,
  ShaderNodeTree,

);

from mathutils import Vector,Euler;

from arcana import ARPATH,AUVICACHE;
from arcana.Tools import (
  isro,ns_path,chkdir,moo

);

from arcana.Xfer import DOS;
from arcana.DAF import *;

from .Meta import *;

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.5b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

CACHEPATH = AUVICACHE+'/node_tree/';
DATAPATH  = ARPATH+'/auvi/data/';

EXT='.n3';

SHD_ATTRS=[

  'bl_description','bl_height_default',
  'bl_height_max','bl_height_min', 'bl_icon',
  'bl_idname','bl_label', 'bl_static_type',
  'bl_width_default','bl_width_max',
  'bl_width_min','color','dimensions',
  'draw_buttons','draw_buttons_ext','height',
  'hide','input_template','inputs',
  'internal_links','label','location',
  'mute','name','output_template','outputs',
  'parent','poll_instance','rna_type','select',
  'show_options','show_preview','show_texture',
  'socket_value_update','type','update',
  'use_custom_color','width','width_hidden',

];

SHD_ATTRS.extend(dir(ShaderNode));
SHD_ATTRS={key:None for key in SHD_ATTRS};

ARCHIVE_FLIST=[

  'Bake_Preview.n3',
  'FauxMetal2.n3',
  'non.n3',

  'Bump2Normal.n3',
  'FauxMetal.n3',
  'Normal2AO.n3',

  'ColorMask.n3',
  'FauxMetalShine.n3',
  'Normal2Curv.n3',

  'CompChannel.n3',
  'Matbake.n3',
  'Normal2Rough.n3'

];

# ---   *   ---   *   ---
# GBL

Sesh_WT={};

# ---   *   ---   *   ---
# recreates archive from cache

def save_archive(ar):

  flist=[

    CACHEPATH+f"/{f}"
    for f in ARCHIVE_FLIST

  ];

  ar.cpush(flist);

# ---   *   ---   *   ---
# ^checks that all nodetrees are in
# cache, fetches missing

def load_archive(ar):

  flist=[
    f for f in ARCHIVE_FLIST
    if not os.path.exists(CACHEPATH+f"/{f}")

  ];

  if len(flist):
    ar.extract(flist,CACHEPATH);

# ---   *   ---   *   ---
# routine

def on_reload():

  ar=DAF(DATAPATH+'matbake_nodes');

  if not ar.exists():
    save_archive(ar);

  load_archive(ar);

# ---   *   ---   *   ---
# check if cached node tree needs updating

def node_tree_updated(name):

  key   = ns_path(name);
  fpath = CACHEPATH+key+EXT;

  return (

  not (os.path.exists(fpath))

  or  (name not in Sesh_WT)
  or  (moo(fpath,bpy.data.filepath))

  );

# ---   *   ---   *   ---
# wrapper class to rebuild
# bpy image references

class Image_Bld:

  def __init__(self,im):
    self.name  = im.name;
    self.fpath = im.filepath;

  def regen(self):

    # get existing
    if self.name in bpy.data.images:
      return bpy.data.images[self.name];

    # recreate
    im=bpy.data.images.new(self.name,8,8);

    im.filepath = self.fpath;
    im.source   = 'FILE';

    return im;

# ---   *   ---   *   ---
# wrapper class to rebuild
# bpy node tree references

class ShaderNodeTree_Bld:

  def __init__(self,g):
    self.name=g.name;
    self.to_cache(g);

  def regen(self):

    # get existing
    if self.name in bpy.data.node_groups:
      return bpy.data.node_groups[self.name];

    # recreate
    return self.from_cache();

# ---   *   ---   *   ---
# saves node group to cache

  def to_cache(self,g):

    DA_Node_Tree(
      self.name,g,
      is_group=True

    ).pack();

# ---   *   ---   *   ---
# ^iv

  def from_cache(self):

    # make ice
    g   = bpy.data.node_groups.new(
      self.name,
      'ShaderNodeTree'

    );

    # retrieve
    key = ns_path(self.name);
    d   = DA_Node_Tree.unpack(key);

    load_tree(g,d,is_group=True);

    return g;

# ---   *   ---   *   ---
# complex type to primitive

def cplex_to_prim(value):

  if isinstance(value,bpy_prop_array) \
  or isinstance(value,Vector) \
  or isinstance(value,Euler):
    value=value[:];

  elif isinstance(value,ShaderNodeTree):
    value=ShaderNodeTree_Bld(value);

  elif isinstance(value,Image):
    value=Image_Bld(value);

  return value;

# ---   *   ---   *   ---
# ^iv

def prim_to_cplex(value):

  if isinstance(value,Image_Bld) \
  or isinstance(value,ShaderNodeTree_Bld):
    value=value.regen();

  return value;

# ---   *   ---   *   ---
# find in/out idex

def scan_lnk(x,sockets):

  out=0;

  for s in sockets:

    if x==s:
      break;

    out+=1;

  return out;

# ---   *   ---   *   ---
# get attributes unique to
# shader node type

def scan_attrs(nd):

  return [

    key for key in dir(nd)
    if key not in SHD_ATTRS

  ];

# ---   *   ---   *   ---
# nodes.new() wants a string, not a type
# however str(type(node)) won't do
#
# AND node.type also doesn't work
#
# you know what this is, right?
# absolutely GENIUS design

def typeof_node(nd):

  t=str(type(nd));
  t=t.replace("<class 'bpy.types.","");
  t=t.replace("'>","");

  return t;

# ---   *   ---   *   ---
# rebuilds node from descriptor

def load_node(dst,d):

  nd          = dst.nodes.new(d['type']);

  nd.name     = d['name'];
  nd.location = d['loc'];
  nd.width    = d['width'];

  # restore attrs
  for attr,value in d['values']['attrs'].items():
    setattr(nd,attr,prim_to_cplex(value));

  # restore unconnected inputs
  for i,input in enumerate(
    d['values']['inputs']

  ):

    if input != None:
      nd.inputs[i].default_value= \
        prim_to_cplex(input);

  return nd;

# ---   *   ---   *   ---
# edge case: node in/out

def load_group_io(port,src):

  for o in src:

    i=port.new(o['type'],o['name']);

    for key in [

      'default_value',

      'min_value',
      'max_value',

    ]:

      if hasattr(i,key):
        setattr(i,key,prim_to_cplex(o[key]));

# ---   *   ---   *   ---
# ^reconnects links

def load_node_links(dst,nd,d):

  sockets=d['links'];

  for i,socket in enumerate(sockets):
    for lnk in socket:

      other = dst.nodes[lnk['node']];
      j     = lnk['slot'];

      dst.links.new(
        nd.outputs[i],
        other.inputs[j]

      );

  update_scene();

# ---   *   ---   *   ---
# ^whole tree

def load_tree(dst,ar,is_group=False):

  gin,gout={},{};

  if is_group:

    gin,gout=ar[0],ar[1];

    ar.remove(ar[0]);
    ar.remove(ar[0]);

  # recreate all nodes
  dst.nodes.clear();
  nodes=[load_node(dst,d) for d in ar];

  if is_group:
    load_group_io(dst.inputs,gin);
    load_group_io(dst.outputs,gout);

  # ^remake links
  for i,nd in enumerate(nodes):
    load_node_links(dst,nd,ar[i]);

# ---   *   ---   *   ---
# convenience wrapper
# holds data for serialization unit

class DA_Node_Tree:

  def __init__(self,name,nt,is_group=False):

    self.name = name;
    self.nt   = nt;

    self.mkftab();

    self.is_group = is_group;

# ---   *   ---   *   ---
# make [name -> idex] fetch table

  def mkftab(self):

    self.ftab = {};
    idex      = 0;

    for nd in self.nt.nodes:
      self.ftab[nd.name]=idex;
      idex+=1;

# ---   *   ---   *   ---
# ^lookup node in ftab

  def idexof(self,nd):
    return self.ftab[nd.name];

# ---   *   ---   *   ---
# we only write output links;
#
# connected inputs are implicitly
# saved as the output of another node

  def get_node_links(self,nd):

    result=[];

    for socket in nd.outputs:
      result.append([]);

      for lnk in socket.links:

        result[-1].append({

          'slot': scan_lnk(
            lnk.to_socket,
            lnk.to_node.inputs

          ),

          'node': self.idexof(
            lnk.to_node

          ),

        });

    return result;

# ---   *   ---   *   ---
# ^all link-less

  def get_node_values(self,nd):

    out={

      'inputs' : [],
      'attrs'  : {},

    };

    # get values of unconnected inputs
    for socket in nd.inputs:
      out['inputs'].append(None);

      if  not len(socket.links) \
      and hasattr(socket,'default_value'):

        out['inputs'][-1]=cplex_to_prim(
          socket.default_value

        );

    # ^non-input values
    for attr in scan_attrs(nd):

      if isro(nd,attr):
        continue;

      out['attrs'][attr]=cplex_to_prim(
        getattr(nd,attr)

      );

    return out;

# ---   *   ---   *   ---
# edge case: node group in/out

  def get_group_io(self,port):

    out=[];

    for i in port:

      t=typeof_node(i);
      t=t.replace('Interface','');

      o={

        'type'  : t,
        'name'  : i.name,

      };

      for key in [
        'default_value',
        'min_value',
        'max_value',

      ]:

        if hasattr(i,key):
          o[key]=cplex_to_prim(
            getattr(i,key)

          );

      out.append(o);

    return out;

# ---   *   ---   *   ---
# makes dict for rebuilding node

  def get_node_desc(self,nd):

    return {

      'name'   : nd.name,
      'type'   : typeof_node(nd),

      'loc'    : cplex_to_prim(nd.location),
      'width'  : nd.width,

      'links'  : self.get_node_links(nd),
      'values' : self.get_node_values(nd),

    };

# ---   *   ---   *   ---
# ^whole tree

  def get_desc(self):

    out=[];

    if self.is_group:

      out.extend([
        self.get_group_io(self.nt.inputs),
        self.get_group_io(self.nt.outputs),

      ]);

    out.extend([
      self.get_node_desc(nd)
      for nd in self.nt.nodes

    ]);

    return out;

# ---   *   ---   *   ---
# ^wrapper, saves to file

  def pack(self):

    fpath=chkdir(CACHEPATH,self.name);
    stout=self.get_desc();

    with open(fpath+EXT,'wb+') as f:
      pickle.dump(stout,f);

# ---   *   ---   *   ---
# ^undo

  @staticmethod
  def unpack(name):

    out   = None;
    fpath = CACHEPATH+ns_path(name);

    with open(fpath+EXT,'rb') as f:
      out=pickle.load(f);

    return out;

# ---   *   ---   *   ---
# return array of nodetree for
# each material in ob

def get_node_trees(ob):

  # validate input
  if not ob_has_matslots(ob):
    return [];

  # scan materials
  else:

    slots = ob.material_slots;
    mats  = [slot.material for slot in slots];

    return [

      DA_Node_Tree(mat.name,mat.node_tree)
      for mat in mats if mat

    ];

# ---   *   ---   *   ---
# ^errchk 0

def ob_has_matslots(ob):

  out = 1;

  me  = ob.data;
  chk = {

    "Object has no data": "not me",
    "Object data is not mesh": \
      "not isinstance(me,Mesh)",

    "Object has no material slots": \
      "not len(ob.material_slots)",

  };

  # ^ensure all false
  for mess,err in chk.items():

    if eval(err):
      print(mess);

      out=0;
      break;

  return out;

# ---   *   ---   *   ---
# saves material node tree to disk

def save_material(mat):
  n3=DA_Node_Tree(mat.name,mat.node_tree);
  n3.pack();

def load_material(dst,src):

  dst.use_nodes=True;
  update_scene();

  ar=DA_Node_Tree.unpack(src);
  load_tree(dst.node_tree,ar);

# ---   *   ---   *   ---
