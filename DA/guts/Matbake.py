#!/usr/bin/python
# ---   *   ---   *   ---
# GUTS MATBAKE
# So we don't pollute the
# iface file
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import bpy;

from bpy.types import (

  ShaderNodeTexImage,
  ShaderNodeGroup,

);

from arcana.Tools import ns_path,chkdir;

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.3b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

RENDER_ATTRS=[

  'render.engine',

  'cycles.use_adaptive_sampling',
  'cycles.adaptive_threshold',

  'cycles.samples',
  'cycles.adaptive_min_samples',

  'cycles.time_limit',

  'cycles.max_bounces',
  'cycles.diffuse_bounces',
  'cycles.glossy_bounces',
  'cycles.transmission_bounces',
  'cycles.volume_bounces',
  'cycles.transparent_max_bounces',

  'cycles.blur_glossy',
  'cycles.caustics_reflective',
  'cycles.caustics_refractive',

  'render.bake.target',
  'render.bake.use_clear',
  'render.bake.margin_type',
  'render.bake.margin',

  'render.bake.use_selected_to_active',

  'cycles.bake_type',
  'render.bake.view_from',

];

# ---   *   ---   *   ---
# config used for material baking

RENDER_SETTINGS={

  'render.engine':'CYCLES',

  'cycles.use_adaptive_sampling':True,
  'cycles.adaptive_threshold':0.100,

  'cycles.samples':16,
  'cycles.adaptive_min_samples':1,

  'cycles.time_limit':0,

  'cycles.max_bounces':1,
  'cycles.diffuse_bounces':1,
  'cycles.glossy_bounces':1,
  'cycles.transmission_bounces':1,
  'cycles.volume_bounces':0,
  'cycles.transparent_max_bounces':0,

  'cycles.blur_glossy':1.0,
  'cycles.caustics_reflective':False,
  'cycles.caustics_refractive':False,

  'render.bake.target':'IMAGE_TEXTURES',
  'render.bake.use_clear':True,
  'render.bake.margin_type':'ADJACENT_FACES',
  'render.bake.margin':2,

  'render.bake.use_selected_to_active':False,

  'cycles.bake_type':'COMBINED',
  'render.bake.view_from':'ABOVE_SURFACE',

};

# ---   *   ---   *   ---
# matches bake type to
# matbake node outputs

BAKE_TYPES={

  'A'    : ['Albedo','Alpha'],
  'NC'   : ['NormalBake','Curv'],

  'ORME' : ['ORM','E',],

};

# ---   *   ---   *   ---
# match node output to
# file extension

IMAGE_EXT={

  'A'    : '_a.png',
  'NC'   : '_n.png',

  'ORME' : '_o.png',

};

# ---   *   ---   *   ---
# makes dict of current config

def get_render_settings():

  return {

    key: eval('bpy.context.scene.'+key)
    for key in RENDER_ATTRS

  };

# ---   *   ---   *   ---
# ^sets from dict

def set_render_settings(o):

  for key,value in o.items():
    exec('bpy.context.scene.'+key+'=value');

# ---   *   ---   *   ---
# selfex

def deselect_node(nd):
  nd.select=False;

def select_node(nd):
  nd.select=True;

def set_active_node(nt,nd):
  for node in nt.nodes:
    deselect_node(node);

  select_node(nd);
  nt.nodes.active=nd;

# ---   *   ---   *   ---
# sync output images to
# da_matbake props

def set_output_settings(ob):

  mat = ob.material_slots[0].material;
  sz  = 2**ob.da_matbake.render_sz;

  for key in ['ALPHA','COLOR']:

    nd=mat.node_tree.nodes["BAKETO_"+key];
    im=nd.image;

    im.file_format      = 'PNG';

    im.source           = 'GENERATED';
    im.generated_width  = sz;
    im.generated_height = sz;

  RENDER_SETTINGS[
    'render.bake.margin'

  ]=sz>>5;

# ---   *   ---   *   ---
# get node holding image being
# baked to

def get_output_node(ob,mode='COLOR'):

  mat = ob.material_slots[0].material;
  im  = mat.node_tree.nodes["BAKETO_"+mode];

  return im;

# ---   *   ---   *   ---
# connects matbake output
# to material output surface

def setout(ob,key,alpha):

  mats=[slot.material for slot in ob.material_slots];
  mode='ALPHA' if alpha else 'COLOR';

  for mat in mats:

    nt   = mat.node_tree;

    bake = nt.nodes['MATBAKE'];
    out  = nt.nodes['OUTPUT'];

    im   = nt.nodes['BAKETO_'+mode];

    nt.links.new(
      bake.outputs[key],
      out.inputs['Surface']

    );

    set_active_node(nt,im);

# ---   *   ---   *   ---
# render single output
# of matbake node

def bake_layer(ob,key,alpha):

  bake_t='';

  if key == 'NormalBake':
    bake_t='NORMAL';

  else:
    bake_t='COMBINED';

  setout(ob,key,alpha);
  bpy.ops.object.bake(type=bake_t);

# ---   *   ---   *   ---
# ^multiple layers of
# a packed texture

def bake_image(ob,t,fpath):

  mode=False;

  # spit step
  print(f"\\-->{t}");

  for key in BAKE_TYPES[t]:

    # spit step
    print(f".  \\-->{key}");

    bake_layer(ob,key,mode);
    mode=True;

  combine_layers(ob,t,fpath);

# ---   *   ---   *   ---
# ^puts the two bakes together

def combine_layers(ob,t,fpath):

  color=get_output_node(ob,'COLOR');
  alpha=get_output_node(ob,'ALPHA');

  a=list(color.image.pixels);
  b=list(alpha.image.pixels);

  a[3::4]=b[0::4];

  color.image.pixels[:]=a[:];

  color.image.save(
    filepath = fpath+IMAGE_EXT[t],
    quality  = 100

  );

# ---   *   ---   *   ---
# checks for correct structure
# in material node trees

# TODO: full validation!
#       this is placeholder at best

def validate_input(ob):

  out  = True;
  mats = [

    slot.material
    for slot in ob.material_slots

  ];

#  for mat in mats:
#
#    nt=mat.node_tree;
#    for name,type in {
#      'MATBAKE': NodeShaderGroup,
#      'TEXTURE': NodeShaderTexImage,
#
#    }.items():
#      out=node_type_name_chk(name,type)
#      if not out: break;
#
#    if not out: break;

  return out;

# ---   *   ---   *   ---
# node of given name and type exists
# within node tree

def node_type_name_chk(nodes,name,type):

  return (
      name in nodes
  and isintance(nodes[name],type)

  );

# ---   *   ---   *   ---
# recreates correct node structure

def n3_regen(ob):
  pass;

# ---   *   ---   *   ---
# bakes all images

def run(ob):

  if not validate_input(ob):
    n3_regen(ob);

  # get output path
  fpath = chkdir(ob.da_matbake.fpath,ob.name);

  # swap config
  old=get_render_settings();
  set_render_settings(RENDER_SETTINGS);
  set_output_settings(ob);

  # spit beg
  print('MATBAKE');

  # run baking for each layer
  for t in BAKE_TYPES.keys():
    bake_image(ob,t,fpath);

  # spit end
  print("\nRET\n");

  # ^restore config
  set_render_settings(old);

# ---   *   ---   *   ---
