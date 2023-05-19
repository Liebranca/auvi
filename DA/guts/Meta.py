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

def select_all(ob,merge):

  bpy.ops.object.select_all(
    action='DESELECT'

  );

  select(ob);

  for piece in merge:
    select(piece);

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

def meshbake(ob,make_triangles):

  apply_keys(ob);
  apply_mods(ob);

  bm=bmesh.new();

  bm.from_object(
    ob,get_depsgraph(),face_normals=False

  );

  if make_triangles:
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

def duplibake(merge=False):

  out   = None;
  clear = [];

  bpy.ops.object.duplicate();
  for dupli in get_selected():
    meshbake(dupli,True);
    clear.append(dupli.data);

  if merge:

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
