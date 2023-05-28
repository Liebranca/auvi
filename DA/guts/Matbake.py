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

from arcana import WLog,AUVICACHE;
from arcana.Xfer import DOS;

from arcana.Tools import (
  ns_path,
  chkdir,
  dirof,
  basef,
  nxbasef,

);

from .Meta import *;
from . import N3;

# ---   *   ---   *   ---
# ROM

CACHEPATH = AUVICACHE+'/material/';
EXT       = '.joj';

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
# selfex

def deselect_node(nd):
  nd.select=False;

def deselect_all_nodes(nt):
  for node in nt.nodes:
    deselect_node(node);

def select_node(nd):
  nd.select=True;

def set_active_node(nt,nd):

  deselect_all_nodes(nt);
  select_node(nd);

  nt.nodes.active=nd;

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

  # get output path
  name  = nxbasef(ob.name);
  fpath = chkdir(CACHEPATH,name);
  files = [];

  # swap config
  old=get_render_settings();
  set_render_settings(RENDER_SETTINGS);
  sz=set_output_settings(ob);

  select_all(ob.da_matbake.dst,[ob]);
  update_scene();

  # run baking for each layer
  for t in BAKE_TYPES.keys():
    files.append(bake_image(ob,t,fpath));


  # ^pack images
  errme=DOS(

    'joj',[

      '-sd',dirof(fpath),
      '-o',fpath,

      '-as',str(sz),

      basef(fpath),

    ],

  );

  # remove temp files
  for f in files:
    os.remove(f);

  # ^restore config
  set_render_settings(old);
  setout(ob,'NormalBake',0);
  select_all(ob,[]);

  return "";

# ---   *   ---   *   ---
# loads material from *.joj

def load(ob,fname):

  global Log;

  fpath=CACHEPATH+'/'+ns_path(fname);

  if not joj_unpack(fpath):
    return;

  files=[

    fpath+IMAGE_EXT[t]
    for t in BAKE_TYPES.keys()

  ];

  dst_nit_preview(ob,basef(fpath));
  dst_nit_images(ob,files);

  del Log;

# ---   *   ---   *   ---
# selfex

def joj_unpack(fpath):

  out   = True;
  errme = DOS(

    'unjoj',[

      '-o',fpath+'_u',
      fpath,

    ],

  );

  if len(errme):
    out=False;

  else:

    exts=['n','a','o'];
    for i in range(0,3):

      base=fpath+f"_u{i}.png";

      if not os.path.exists(base):
        out=False;

        break;

      ext=exts[i];
      os.rename(base,fpath+f"_{ext}.png");

  return out;

# ---   *   ---   *   ---
# creates material preview

def dst_nit_preview(ob,name='Material'):

  bl_material_clear(ob);
  bl_material_add(ob,name);

  mat = ob.material_slots[0].material;
  nt  = mat.node_tree;

  mat.name=name;
  N3.load_material(mat,'Bake_Preview');

# ---   *   ---   *   ---
# ^fills out rendered images

def dst_nit_images(ob,files):

  mat = ob.material_slots[0].material;
  nt  = mat.node_tree;

  load_image(nt.nodes['ALBEDO'],files[0]);
  load_image(nt.nodes['NC'],files[1]);
  load_image(nt.nodes['ORME'],files[2]);

  nt.nodes['NC'].image.colorspace_settings.name=(
    'Non-Color'

  );

  nt.nodes['ORME'].image.colorspace_settings.name=(
    'sRGB'

  );

  nt.nodes['ORME'].image.alpha_mode='CHANNEL_PACKED';

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
