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

from arcana import ARPATH;
from arcana.Tools import (
  isro,ns_path,chkdir,moo

);

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.4b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

CACHEPATH=ARPATH+'/.cache/auvi/node_tree/';
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

# ---   *   ---   *   ---
# GBL

Sesh_WT={};

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
    DA_Node_Tree(self.name,g).pack();

# ---   *   ---   *   ---
# ^iv

  def from_cache(self):

    # make ice
    g   = bpy.data.node_groups.new(self.name)

    # retrieve
    key = ns_path(self.name);
    d   = DA_Node_Tree.unpack(CACHEPATH+key);

    load_tree(g,d);

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

# ---   *   ---   *   ---
# ^whole tree

def load_tree(dst,ar):

  # first create all nodes
  nodes=[load_node(dst,d) for d in ar];

  # then remake links
  for i,nd in enumerate(nodes):
    load_node_links(dst,nd,ar[i]);

# ---   *   ---   *   ---
# convenience wrapper
# holds data for serialization unit

class DA_Node_Tree:

  def __init__(self,name,nt):

    self.name = name;
    self.nt   = nt;

    self.mkftab();

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

    return [
      self.get_node_desc(nd)
      for nd in self.nt.nodes

    ];

# ---   *   ---   *   ---
# ^wrapper, saves to file

  def pack(self):

    if not node_tree_updated(self.name):
      return;

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
# selfex entry point

def test():

  ob=bpy.context.object;
  ar=get_node_trees(ob);

  ar[0].pack();
  d=DA_Node_Tree.unpack(ar[0].name);

  load_tree(ar[1].nt,d);

# ---   *   ---   *   ---
