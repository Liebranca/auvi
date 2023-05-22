#!/usr/bin/python
# ---   *   ---   *   ---
# META GUTS
# Blender stuff
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import bmesh,bpy;
import numpy as np;

# ---   *   ---   *   ---
# scene manipulation

def update_scene():
  bpy.context.view_layer.update();

def link_object(ob):
  bpy.context.collection.objects.link(ob);

def get_depsgraph():
  return bpy.context.evaluated_depsgraph_get();

# ---   *   ---   *   ---
# manipulate selection

def select(ob):
  ob.select_set(True);

def make_active(ob):
  bpy.context.view_layer.objects.active=ob;

def get_selected():
  return bpy.context.selected_objects;

def get_active():
  return bpy.context.view_layer.objects.active;

# ---   *   ---   *   ---
# ^bat

def select_all(ob,selection=[]):

  bpy.ops.object.select_all(
    action='DESELECT'

  );

  for child in selection:
    select(child);

  select(ob);
  make_active(ob);

# ---   *   ---   *   ---
# get array of all mesh objects
# sharing a collection with ob

def get_hierarchy(ob):

  out=[];

  for collection in ob.users_collection:

    out.extend([

      child for child
      in collection.objects

      if (

        (isinstance(child.data,bpy.types.Mesh))

        and (not (child.hide_viewport))
        and (not (child.hide_render  ))

        and (not (child in out))
        and (not (child is ob ))

      )

    ]);

  return out;

# ---   *   ---   *   ---
# bakes shapekeys

def apply_keys(ob):

  ob.shape_key_add(
    name='Mix',
    from_mix=True

  );

  for k in ob.data.shape_keys.key_blocks:

    if(k.name == 'Mix'):
      continue;

    ob.shape_key_remove(k);

  ob.shape_key_remove(
    ob.data.shape_keys.key_blocks['Mix']

  );

# ---   *   ---   *   ---
# selfex

def apply_mods(ob):

  for m in ob.modifiers:
    bpy.ops.object.modifier_apply(
      modifier=m.name

    );

# ---   *   ---   *   ---
# make backup of mesh

def bmesh_save(me):

  bm=bmesh.new();
  bm.from_mesh(me);

  out=bm.copy();
  bm.free();

  return out;

# ---   *   ---   *   ---
# ^restore

def bmesh_load(dst,src):
  src.to_mesh(dst);
  src.free();

# ---   *   ---   *   ---
# bakes object mesh

def meshbake(ob,mktris):

  apply_keys(ob);
  apply_mods(ob);

  bm=bmesh.new();

  bm.from_object(
    ob,get_depsgraph(),face_normals=False

  );

  if mktris:
    bmesh.ops.triangulate(bm,faces=bm.faces);

  bm.to_mesh(ob.data);
  bm.free();

# ---   *   ---   *   ---
# duplicates single object
# renames new

def duplicate(ob,xt="CRK"):

  me      = ob.data.copy();
  me.name = me.name+f".{xt}";

  out     = bpy.data.objects.new(me.name,me);

  link_object(out);
  out.matrix_world=ob.matrix_world;

  return out;

# ---   *   ---   *   ---
# duplicates and bakes deforms
# for an entire selection

def duplibake(merge=False,mktris=False):

  out   = None;
  clear = [];

  sel   = get_selected();

  bpy.ops.object.duplicate();
  for dupli in get_selected():
    meshbake(dupli,mktris);
    clear.append(dupli.data);

  if merge:

    if len(sel) > 1:
      bpy.ops.object.join();

    out   = get_active();
    clear = [
      me for me in clear
      if me != out.data

    ];

    for me in clear:
      bpy.data.meshes.remove(me);

  else:
    out=get_selected();

  return out;

# ---   *   ---   *   ---
# ensures object has shapekeys

def force_shapes(ob):

  if not ob.data.shape_keys:
    ob.shape_key_add(name='Basis');

  ob.data.shape_keys.use_relative=True;

# ---   *   ---   *   ---
# fills out shapekey from array
# of vcords

def make_shape(dst,src,pose_name):

  shape=dst.shape_key_add(
    name=pose_name

  );

  if isinstance(src,list):
    shape_from_flat(shape,src);

  else:
    shape_from_verts(shape,src.vertices);

# ---   *   ---   *   ---
# variations on copying
# vcords to shapekey

def shape_from_flat(dst,src):
  verts   = np.array(src[:]);
  indices = [i for i in range(len(verts))];

  vflat_shape_set(verts,indices,dst);

def shape_from_verts(dst,src):
  verts   = np.array(src[:]);
  indices = [i for i in range(len(verts))];

  vvert_shape_set(verts,indices,dst);

# ---   *   ---   *   ---
# ^only difference is access

def flat_shape_set(src,vi,dst):
  dst.data[vi].co[:]=src[:];

def vert_shape_set(src,vi,dst):
  dst.data[vi].co[:]=src.co[:];

# ---   *   ---   *   ---
# ^saves me typing the loops
# *might* also speed it up a bit

vflat_shape_set=np.vectorize(
  flat_shape_set

);

vvert_shape_set=np.vectorize(
  vert_shape_set

);

# ---   *   ---   *   ---
# keyframes display of Nth pose

def make_shape_anim(ob,idex):

  shapes     = ob.data.shape_keys;
  curr_block = shapes.key_blocks[idex];

  # 0th shape is always basis
  # thus, offset by one
  idex+=1;

  # first pose after basis
  if idex==1:
    next_block=shapes.key_blocks[idex+1];
    prev_block=shapes.key_blocks[-1];

  # ^last one
  elif idex == len(shapes.key_blocks)-1:
    next_block=shapes.key_blocks[1];
    prev_block=shapes.key_blocks[idex-1];

  # ^in between
  else:
    next_block=shapes.key_blocks[idex+1];
    prev_block=shapes.key_blocks[idex-1];

  # only curr displays
  # if curr &&! (prev|next)
  curr_block.value=1;
  next_block.value=0;
  prev_block.value=0;

  # undo offset
  idex-=1;

  # assign values
  curr_block.keyframe_insert("value",frame=idex);
  next_block.keyframe_insert("value",frame=idex);
  prev_block.keyframe_insert("value",frame=idex);

# ---   *   ---   *   ---
