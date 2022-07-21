#!/usr/bin/python
# ---   *   ---   *   ---
# SHAPEBAKE
# Turns NLA into shapekeys
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,
# ---   *   ---   *   ---

import bmesh,bpy,struct;
from mathutils import Matrix,Vector;

#   ---     ---     ---     ---     ---

def ftb(num):
  return struct.pack('<f',num);

def ftbarr(arr):
  return struct.pack('%sf'%len(arr), *arr);

# ---   *   ---   *   ---

FRAC_SCALE=64;
FRAC_STEP=1.0/FRAC_SCALE;
FRAC_MAX=16;
FRAC_SHIFT=FRAC_SCALE*FRAC_MAX;

INTERPOLATION_MODE='CONSTANT';

# ---   *   ---   *   ---

def FLTOFRAC(x):
  x=max(-FRAC_MAX,min(x,FRAC_MAX-FRAC_STEP));
  return int(round(x*FRAC_SCALE)+FRAC_SHIFT);

def FRACTOFL(x):
  if(x==(FRAC_SHIFT*2)-1): x = FRAC_SHIFT*2;
  return (x-FRAC_SHIFT)*FRAC_STEP;

# ---   *   ---   *   ---

OLD_VERSION=0;

def update_scene():

  if(OLD_VERSION):
    bpy.context.scene.update();

  else:
    bpy.context.view_layer.update();

def select(ob):

  if(OLD_VERSION):
    ob.select=True;

  else:
    ob.select_set(True);

def set_ob_active(ob):

  if(OLD_VERSION):
    bpy.context.scene.objects.active=ob;

  else:
    bpy.context.view_layer.objects.active=ob;

def link_object(ob):

  if(OLD_VERSION):
    scene.objects.link(ob);

  else:
    bpy.context.collection.objects.link(ob);

# ---   *   ---   *   ---
# blender devs what the fuck

def scene_or_depsgraph():

  out=None;

  if(OLD_VERSION):
    out=bpy.context.scene;

  else:
    out=bpy.context.evaluated_depsgraph_get()

  return out;

# ---   *   ---   *   ---

def bake_deforms(ob,me):

  bm=bmesh.new();

  bm.from_object(
    ob,scene_or_depsgraph(),
    face_normals=True

  );

  bm.to_mesh(me);
  bm.free();

# ---   *   ---   *   ---

def reset_pose(ob):
  for pb in ob.parent.pose.bones:
    pb.matrix_basis=Matrix();

  update_scene();

#   ---     ---     ---     ---     ---

def shapebake(ob,frames):

  scene=bpy.context.scene;

  update_scene();

  original_object=ob;
  duplis=[];

# ---   *   ---   *   ---
# get list of objects to bake together

  if ob.parent:
    merge=(

      [child.children[0] for child
      in ob.parent.children

      if child.name.startswith("BP_")
      and not child.children[0].hide_render]

    );

  else:
    merge=[ob];

# ---   *   ---   *   ---

  bpy.ops.object.select_all(
    action='DESELECT'

  );

  # select objects in bake list
  original_object=ob;
  select(ob);

  for piece in merge:
    select(piece);

  set_ob_active(original_object);

  bpy.ops.object.duplicate();

  for dupli in bpy.context.selected_objects:

    duplis.append(dupli.data);
    shapes=dupli.data.shape_keys;

    nme=dupli.data;

    if shapes:

      nme=dupli.to_mesh(
        scene,1,'RENDER'

      );

# ---   *   ---   *   ---

      ansdata=shapes.animation_data;

      if ansdata:
        if ansdata.action:
          bpy.data.actions.remove(ansdata.action);

      for k in shapes.key_blocks:
        dupli.shape_key_remove(k);

# ---   *   ---   *   ---

    dupli.data=nme;
    duplis.append(nme);

    bpy.ops.object.join();
    update_scene();

    ob=bpy.context.object;
    ob.data.name=ob.name;

# ---   *   ---   *   ---

  tgt_me=ob.data.copy();

  tgt_me.name=(
    original_object.name+".CRK"

  );

  tgt=bpy.data.objects.new(
    tgt_me.name,tgt_me

  );

  me=ob.data;

  link_object(tgt);

  if not tgt.data.shape_keys:
    sk_basis=tgt.shape_key_add(name='Basis');

  tgt.data.shape_keys.use_relative=True;
  ans=me.copy();

  ans.name=(
    me.name+"CRK_shapebake"

  );

#   ---     ---     ---     ---     ---

  scene.frame_set(0);
  for n in range(frames):

    bpy.ops.object.select_all(
      action='DESELECT'

    );

    select(original_object);
    for piece in merge:
      select(piece);

    set_ob_active(original_object);
    bpy.ops.object.duplicate();

# ---   *   ---   *   ---

    for dupli in bpy.context.selected_objects:

      duplis.append(dupli.data);
      shapes=dupli.data.shape_keys;

      if shapes:
        nme=dupli.to_mesh(scene,1,'RENDER');
        ansdata=shapes.animation_data;

        if ansdata:
          if ansdata.action:
            bpy.data.actions.remove(
              ansdata.action

            );

        for k in shapes.key_blocks:
          dupli.shape_key_remove(k);

        dupli.data=nme;
        duplis.append(nme);

# ---   *   ---   *   ---

    bpy.ops.object.join();
    update_scene();

    ob=bpy.context.object;
    ob.data.name=ob.name;

    me=ob.data;

    sk=tgt.shape_key_add(name='frame_'+str(n));
    bake_deforms(ob,ans);

    update_scene();

# ---   *   ---   *   ---

    for vert in ans.vertices:

      vi=vert.index;

      sk.data[vi].co=[
        FRACTOFL(FLTOFRAC(ax))
        for ax in vert.co

      ];

    scene.frame_set(
      scene.frame_current+1

    );

# ---   *   ---   *   ---

  scene.frame_set(0);

  for dupli in duplis:

    try:

      if dupli.shape_keys:

        me=tgt.data;
        tgt.data=dupli;

        for k in dupli.shape_keys.key_blocks:
          tgt.shape_key_remove(k);
          tgt.data=me;

    except:
      pass;

# ---   *   ---   *   ---

    try:
      bpy.data.meshes.remove(dupli);

    except:
      pass;

#   ---     ---     ---     ---     ---

  duplis=[];
  tgt.data.shape_keys.name=tgt.name;

  for action in bpy.data.actions:
    if tgt.name in action.name:
      bpy.data.actions.remove(action);

  update_scene();

# ---   *   ---   *   ---

  for n in range(0, frames):

    shapes=tgt.data.shape_keys;
    alpha=1.0;

    for sub in merge:
      if sub.color[3] < alpha:
        alpha=sub.color[3];

    curr_block=shapes.key_blocks[
      'frame_%s'%(str(n))

    ];

# ---   *   ---   *   ---

    if n==0:
      next_block=shapes.key_blocks[
        'frame_%s'%(str(n+1))

      ];

      prev_block=shapes.key_blocks[
        'frame_%s'%(str(frames-1))

      ];

# ---   *   ---   *   ---

    elif n == frames-1:
      next_block=shapes.key_blocks[
        'frame_%s'%(str(0))

      ];

      prev_block=shapes.key_blocks[
        'frame_%s'%(str(n-1))

      ];

# ---   *   ---   *   ---

    else:
      next_block=shapes.key_blocks[
        'frame_%s'%(str(n+1))

      ];

      prev_block=shapes.key_blocks[
        'frame_%s'%(str(n-1))

      ];

#   ---     ---     ---     ---     ---

    curr_block.value=1;
    next_block.value=prev_block.value=0;

    curr_block.keyframe_insert("value",frame=n);
    next_block.keyframe_insert("value",frame=n);
    prev_block.keyframe_insert("value",frame=n);

    tgt.color[3]=alpha;
    tgt.keyframe_insert("color",frame=n);

    scene.frame_set(
      scene.frame_current+1

    );

# ---   *   ---   *   ---

  bpy.data.meshes.remove(ans);
  scene.frame_set(0);

  bpy.data.actions[tgt.name+"Action"].name=(
    tgt.name

  );

  bpy.data.actions[tgt.name+"Action.001"].name=(
    tgt.name+"ALPHA"

  );

  act=bpy.data.actions[tgt.name];
  for fcurve in act.fcurves:
    for kf in fcurve.keyframe_points:
      kf.interpolation=INTERPOLATION_MODE;

  act=bpy.data.actions[tgt.name+"ALPHA"];
  for fcurve in act.fcurves:
    for kf in fcurve.keyframe_points:
      kf.interpolation = 'BEZIER';

  return tgt;

#   ---     ---     ---     ---     ---

def take(ob):

  scene=bpy.context.scene;

  t_name=ob.name;
  original_object=None;

  strips=None;

# ---   *   ---   *   ---

  if ob.parent:

    nla_tracks=ob.parent.animation_data.nla_tracks;

    if len(nla_tracks) > 1:
      strips=nla_tracks["BAKE"].strips;

    else:
      strips=nla_tracks[0].strips;

  else:
    nla_tracks=ob.animation_data.nla_tracks;
    strips=nla_tracks[0].strips;

  animdata=[];
  frames=2;

# ---   *   ---   *   ---

  for anim in strips:

    animdata.append((
      anim.name,

      int(anim.frame_start),
      int(anim.frame_end)

    ));

    frames=anim.frame_end;

# ---   *   ---   *   ---

  frames=int(frames);

  if ob.name+".CRK" in bpy.data.meshes:
    old_tgt=bpy.data.objects[ob.name+".CRK"];
    for k in old_tgt.data.shape_keys.key_blocks:
      old_tgt.shape_key_remove(k);

    bpy.data.meshes.remove(old_tgt.data);

  if ob.parent:
    reset_pose(ob);

  tgt=shapebake(ob,frames+1);

#   ---     ---     ---     ---     ---

  set_ob_active(tgt);
  update_scene();

  if(OLD_VERSION):
    pass; # it'd be a layer swap i guess...

  else:
    collection=bpy.data.collections.new(
      bpy.context.collection.name+'.CRK'

    );

    bpy.context.scene.collection.children.link(
      collection

    );

    bpy.context.collection.objects.unlink(tgt);
    collection.objects.link(tgt);

# ---   *   ---   *   ---

# TODO: handle animdata files
#
#  animfile_path="\\".join(
#    __file__.split("\\")[:-2]
#
#  )+"\\dsm\\animdata\\";
#
## ---   *   ---   *   ---
#
#  with open(animfile_path+tgt.name, "w") as file:
#    s=(",".join(
#
#      f"{name},{start},{end}"
#      for name, start, end in animdata)
#
#    );
#
#    file.write(s);
#
## ---   *   ---   *   ---
#
#  bpy.ops.object.select_all(action='DESELECT');
#  tgt.select=1;
#
#  scene.objects.active=tgt;

# ---   *   ---   *   ---

