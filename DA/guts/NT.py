#!/usr/bin/python
# ---   *   ---   *   ---
# NT
# Node tree walker
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import bpy;

from bpy.types import (

  bpy_prop_array,

  Mesh,
  ShaderNode,

);

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.1b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

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
# convenience wrapper
# holds data for serialization unit

class DA_Node_Tree:

  def __init__(self,nt):
    self.nt=nt;
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

      if not len(socket.links):

        value=socket.default_value;

        if isinstance(value,bpy_prop_array):
          value=value[:];

        out['inputs'][-1]=value;

    # ^non-input values
    for attr in scan_attrs(nd):
      out['attrs'][attr]=getattr(nd,attr);

    return out;

# ---   *   ---   *   ---
# makes dict for rebuilding node

  def get_node_desc(self,nd):

    return {

      'name'   : nd.name,
      'type'   : nd.type,

      'loc'    : nd.location,
      'width'  : nd.width,

      'links'  : self.get_node_links(nd),
      'values' : self.get_node_values(nd),

    };

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

      DA_Node_Tree(mat.node_tree)
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

  return ar[0].get_node_desc(ar[0].nt.nodes["Bump"]);

# ---   *   ---   *   ---
