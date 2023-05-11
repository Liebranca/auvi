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
from arcana.Tools import ns_path,chkdir;

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.1b';
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

  'ORME' : ['AO','Roughness','Metal','Emit'],

};

# ---   *   ---   *   ---
# match node output to
# file extension

LAYER_EXT={

  'Albedo'      : '_a0.png',
  'Alpha'       : '_a1.png',

  'NormalBake'  : '_n0.png',
  'Curv'        : '_n1.png',

  'AO'          : '_o0.png',
  'Roughness'   : '_o1.png',
  'Metal'       : '_o2.png',
  'Emit'        : '_o3.png',

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
# get node holding image being
# baked to
#
# also configs im to match
# output settings

def get_output_node(ob):

  mat = ob.material_slots[0].material;

  nd  = mat.node_tree.nodes["BAKETO"];
  im  = nd.image;

  sz  = 2**ob.da_material.render_sz;

  im.file_format      = 'PNG';

  im.source           = 'GENERATED';
  im.generated_width  = sz;
  im.generated_height = sz;

  RENDER_SETTINGS[
    'render.bake.margin'

  ]=sz>>5;

  return im;

# ---   *   ---   *   ---
# connects matbake output
# to material output surface

def setout(ob,key):

  mats=[slot.material for slot in ob.material_slots];

  for mat in mats:

    nt   = mat.node_tree;

    bake = nt.nodes['Matbake'];
    out  = nt.nodes['Material Output'];

    nt.links.new(
      bake.outputs[key],
      out.inputs['Surface']

    );

# ---   *   ---   *   ---
# render single output
# of matbake node

def bake_layer(ob,key):

  bake_t='';

  if key == 'NormalBake':
    bake_t='NORMAL';

  else:
    bake_t='COMBINED';

  setout(ob,key);
  bpy.ops.object.bake(type=bake_t);

# ---   *   ---   *   ---
# ^multiple layers of
# a packed texture

def bake_image(ob,t,im,fpath):

  # spit step
  print(f"\\-->{t}");

  for key in BAKE_TYPES[t]:

    # spit step
    print(f".  \\-->{key}");

    bake_layer(ob,key);

    im.save(
      filepath = fpath+LAYER_EXT[key],
      quality  = 100

    );

# ---   *   ---   *   ---
# ^bakes all images

def run(ob):

  # get output data
  im    = get_output_node(ob);
  fpath = chkdir(ob.da_material.fpath,ob.name);

  # swap config
  old=get_render_settings();
  set_render_settings(RENDER_SETTINGS);

  # spit beg
  print('MATBAKE');

  # run baking for each layer
  for t in BAKE_TYPES.keys():
    bake_image(ob,t,im,fpath);

  # spit end
  print("\nRET\n");

  # ^restore config
  set_render_settings(old);

# ---   *   ---   *   ---
