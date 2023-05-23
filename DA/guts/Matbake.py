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

import bpy,io,os;
from mathutils import Vector;
from contextlib import redirect_stdout

from bpy.types import (

  ShaderNodeTexCoord,
  ShaderNodeMapping,
  ShaderNodeTexImage,
  ShaderNodeGroup,

  ShaderNodeOutputMaterial,

);

from arcana import WLog;
from arcana.Xfer import DOS;

from arcana.Tools import (
  ns_path,
  chkdir,
  dirof,
  basef,

);

from .Meta import *;
from . import N3;

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
  'render.bake.cage_extrusion',

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

  'render.bake.use_selected_to_active':True,
  'render.bake.cage_extrusion':0.05,

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
# GBL

Log=None;

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
  sz  = int(ob.da_matbake.render_sz);
  aa  = int(
    ob.da_matbake.render_scale.replace('x','')

  );

  for key in ['ALPHA','COLOR']:

    nd=mat.node_tree.nodes["BAKETO_"+key];
    im=nd.image;

    im.file_format      = 'PNG';

    im.source           = 'GENERATED';
    im.generated_width  = sz*aa;
    im.generated_height = sz*aa;

  RENDER_SETTINGS[
    'render.bake.margin'

  ]=sz>>4;

  return sz;

# ---   *   ---   *   ---
# get node holding image being
# baked to

def get_output_node(ob,mode='COLOR'):

  dst  = ob.da_matbake.dst;
  ndst = dst.material_slots[0].material;
  ndst = ndst.node_tree;

  im   = ndst.nodes["BAKETO_"+mode];

  return im;

# ---   *   ---   *   ---
# connects matbake output
# to material output surface

def setout(ob,key,alpha):

  mats=[

    slot.material
    for slot in ob.material_slots

  ];

  mode = 'ALPHA' if alpha else 'COLOR';

  dst  = ob.da_matbake.dst;
  ndst = dst.material_slots[0].material;
  ndst = ndst.node_tree;

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

  # for selected to active
  im=ndst.nodes['BAKETO_'+mode];
  set_active_node(ndst,im);

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

  with redirect_stdout(io.StringIO()):
    bpy.ops.object.bake(type=bake_t);

# ---   *   ---   *   ---
# ^multiple layers of
# a packed texture

def bake_image(ob,t,fpath):

  mode=False;
  Log.beg_scope(t);

  for key in BAKE_TYPES[t]:

    Log.line(key);

    bake_layer(ob,key,mode);
    mode=True;

  return combine_layers(ob,t,fpath);

# ---   *   ---   *   ---
# ^puts the two bakes together

def combine_layers(ob,t,fpath):

  Log.line('^Combining layers');

  out   = fpath+IMAGE_EXT[t];
  sz    = int(ob.da_matbake.render_sz);

  color = get_output_node(ob,'COLOR');
  alpha = get_output_node(ob,'ALPHA');

  # undo scaling
  color.image.scale(sz,sz);
  alpha.image.scale(sz,sz);

  # get color and alpha
  a=list(color.image.pixels);
  b=list(alpha.image.pixels);

  # ^roll together
  a[3::4]=b[0::4];
  color.image.pixels[:]=a[:];

  # save modified
  color.image.save(
    filepath = out,
    quality  = 100

  );

  Log.end_scope("\n");

  return out;

# ---   *   ---   *   ---
# checks for correct structure
# in material node trees
#
# will load base tree if incorrect
# and return false
#
# else ret true

def validate_input(ob):

  out  = True;
  mb   = ob.da_matbake;

  mats = [

    slot.material
    for slot in ob.material_slots

  ];

  st={

    'TEXCOORDS': ShaderNodeTexCoord,
    'MAPPING'  : ShaderNodeMapping,
    'TEXTURE'  : ShaderNodeTexImage,

    'MATBAKE'  : ShaderNodeGroup,
    'OUTPUT'   : ShaderNodeOutputMaterial,

    'BAKETO_COLOR': ShaderNodeTexImage,
    'BAKETO_ALPHA': ShaderNodeTexImage,

  };

  i=0;

  for mat in mats:

    nodes = mat.node_tree.nodes;
    x     = mb.materials[i];

    for name,type in st.items():

      if not node_type_name_chk(nodes,name,type):

        config=get_st(x,ob);

        try:

          N3.load_material(mat,'non');
          out=False;

          set_st(x,ob,config);

        except:

          Log.err(
            "\nMaterial regeneration failed"

          );

        break;

    i+=1;

  return out;

# ---   *   ---   *   ---
# node of given name and type exists
# within node tree

def node_type_name_chk(nodes,name,type):

  return (
      name in nodes
  and isinstance(nodes[name],type)

  );

# ---   *   ---   *   ---
# bakes all images

def run(ob):

  # early exit
  if not validate_input(ob):

    return (

      'Materials were out of whack and '
    + 'had to be regenerated! baking aborted'

    );

  elif not ob.da_matbake.dst:

    return (

      'Bake has no destination; '
    + 'set Lowpoly field of DarkAge Material'

    );

  global Log;
  Log=WLog.beget('MATBAKE');

  # get output path
  fpath = chkdir(ob.da_matbake.fpath,ob.name);
  files = [];

  # swap config
  Log.line('Running config swap');
  old=get_render_settings();
  set_render_settings(RENDER_SETTINGS);
  sz=set_output_settings(ob);

  select_all(ob.da_matbake.dst,[ob]);

  # run baking for each layer
  for t in BAKE_TYPES.keys():
    files.append(bake_image(ob,t,fpath));

  # ^pack images
  Log.line('Getting the JOJ');
  DOS(

    'joj',[

      '-sd',dirof(fpath),
      '-o',fpath,

      '-as',str(sz),

      basef(fpath),

    ],

  );

  dst_nit_preview(ob,files);

#  # remove temp files
#  Log.line('Running cleanup');
#  for f in files:
#    os.remove(f);

  # ^restore config
  set_render_settings(old);
  setout(ob,'NormalBake',0);
  select_all(ob,[]);

  del Log;

  return "";

# ---   *   ---   *   ---
# creates material preview

def dst_nit_preview(ob,files):

  dst  = ob.da_matbake.dst;
  name = basef(ns_path(ob.name))+'_preview';

  if not len(dst.material_slots):
    bl_material_add(dst,name);

  mat = dst.material_slots[0].material;
  nt  = mat.node_tree;

  mat.name=name;
  N3.load_material(mat,'Bake_Preview');

  load_image(nt.nodes['A'],files[0]);
  load_image(nt.nodes['NC'],files[1]);
  load_image(nt.nodes['ORME'],files[2]);

  nt.nodes['NC'].image.colorspace_settings.name=(
    'Non-Color'

  );

  nt.nodes['ORME'].image.colorspace_settings.name=(
    'Non-Color'

  );

# ---   *   ---   *   ---
# ^create image if missing

def load_image(dst,fpath):

  if dst.image==None:

    if fpath not in bpy.data.images:
      dst.image=bpy.data.images.new(fpath,8,8);

    else:
      dst.image=bpy.data.images[fpath];

  dst.image.filepath = fpath;
  dst.image.source   = 'FILE';

# ---   *   ---   *   ---

def bl_material_add(ob,name='Material'):

  select(ob);
  make_active(ob);

  bpy.ops.object.material_slot_add();
  out=bpy.data.materials.new(name);

  ob.active_material_index=len(
    ob.material_slots

  )-1;

  ob.active_material=out;

  return out;

# ---   *   ---   *   ---
# get blender material
# assoc with DA_Material

def get_material(self,ob):

  mb  = ob.da_matbake;
  i   = mb.materials[:].index(self);

  mat = ob.material_slots[i].material;

  return mat;

# ---   *   ---   *   ---
# get material node tree
# assoc with selected DA_Material

def get_matnodes(self,ob):

  mat = get_material(self,ob);
  nt  = mat.node_tree;

  return nt;

# ---   *   ---   *   ---
# creates new

def material_nit(ob):

  mb  = ob.da_matbake;
  mat = bl_material_add(ob,'non');

  mb.materials.add();
  N3.load_material(mat,'non');

# ---   *   ---   *   ---
# ^removes

def material_del(ob):

  ob = C.object;
  mb = ob.da_matbake;

  i  = mb.material_i;

  ob.active_material_index=i;

  bpy.data.materials.remove(ob.active_material);
  bpy.ops.object.material_slot_remove();

  mb.materials.remove(i);

# ---   *   ---   *   ---
# gets matbake group node input

def get_mbin(nodes,key):

  ndi   = nodes['MATBAKE'].inputs;
  value = ndi[key].default_value;

  if(

     isinstance(value,bpy.types.bpy_prop_array)
  or isinstance(value,Vector)

  ):

    return value[:];

  else:
    return value;

# ---   *   ---   *   ---
# ^set

def set_mbin(nodes,key,value):

  ndi=nodes['MATBAKE'].inputs;

  if isinstance(value,list):
    ndi[key].default_value[:]=value[:];

  else:
    ndi[key].default_value=value;

# ---   *   ---   *   ---
# record DA_material state

def get_st(x,ob):

  mat = get_material(x,ob);
  nd  = mat.node_tree.nodes;

  return [

    x.mapping,

    nd['TEXTURE'].projection,
    nd['TEXTURE'].projection_blend,

    nd['MAPPING'].inputs[1].default_value[:],
    nd['MAPPING'].inputs[2].default_value[:],
    nd['MAPPING'].inputs[3].default_value[:],

    get_mbin(nd,'BumpStr'),

    get_mbin(nd,'RoughTight'),
    get_mbin(nd,'RoughBase'),

    get_mbin(nd,'CurvDetail'),
    get_mbin(nd,'CurvEdge'),

    get_mbin(nd,'EmitColor'),
    get_mbin(nd,'EmitTolerance'),

    get_mbin(nd,'MetalColor'),
    get_mbin(nd,'MetalTolerance'),
    get_mbin(nd,'MetalMult'),

    x.im,

  ];

# ---   *   ---   *   ---
# ^restore

def set_st(x,ob,src):

  mat = get_material(x,ob);
  nd  = mat.node_tree.nodes;

  x.mapping=src[0];

  nd['TEXTURE'].projection=src[1];
  nd['TEXTURE'].projection_blend=src[2];

  nd['MAPPING'].inputs[1].default_value=src[3];
  nd['MAPPING'].inputs[2].default_value=src[4];
  nd['MAPPING'].inputs[3].default_value=src[5];

  set_mbin(nd,'BumpStr',src[6]);

  set_mbin(nd,'RoughTight',src[7]);
  set_mbin(nd,'RoughBase',src[8]);

  set_mbin(nd,'CurvDetail',src[9]);
  set_mbin(nd,'CurvEdge',src[10]);

  set_mbin(nd,'EmitColor',src[11]);
  set_mbin(nd,'EmitTolerance',src[12]);

  set_mbin(nd,'MetalColor',src[13]);
  set_mbin(nd,'MetalTolerance',src[14]);
  get_mbin(nd,'MetalMult',src[15]),

  x.im=src[16];

# ---   *   ---   *   ---
