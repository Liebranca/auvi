#!/usr/bin/python
# ---   *   ---   *   ---
# IFACE CHAR
# For your 3D dollhouse
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

from mathutils import Vector;

from .Meta import *;
from . import Apparel,Attach,State;

from .State import DA_State_BL;

# ---   *   ---   *   ---
# GBL

Cache={};

# ---   *   ---   *   ---
# get bodypart data for skin

def rebuild_bodyparts(self,C):

  if(not self.skin):
    return;

  bp_dict = {};
  flag    = 1;

# ---   *   ---   *   ---
# get array of vertex colors

  attrs        = [

    a for a in self.skin.color_attributes

    if  "BP_Mask::" in a.name
    and "BP_Mask::Combined" not in a.name

  ];

# ---   *   ---   *   ---
# ^partition based on array

  for attr in attrs:

    indices=[

      i for i in range(len(attr.data))
      if attr.data[i].color[0]<=0

    ];

    bp_dict[attr.name]=[flag,indices];
    flag=flag<<1;

# ---   *   ---   *   ---
# shady use of object name for storage
# required to bypass the GENIUS of this API

  ob=C.object;

  if(self.skin.name not in Cache):
    Cache[self.skin.name]=DA_Char();

  Cache[self.skin.name].bp_dict=bp_dict;

# ---   *   ---   *   ---

def rebuild_mask(self,C):

  if(not self.skin):
    return;

  if(self.skin.name not in Cache):
    rebuild_bodyparts(self,C);

# ---   *   ---   *   ---
# unhide all

  bp_dict = Cache[self.skin.name].bp_dict;

  attrs   = self.skin.color_attributes;
  mask    = attrs['BP_Mask::Combined'].data;

  reset   = [1,1,1,1]*len(mask);

  mask.foreach_set('color',reset);

  # you must manually write to array,
  # else scene doesn't update
  mask[0].color=[1,1,1,1];

# ---   *   ---   *   ---
# get bodyparts to hide

  for name,set in bp_dict.items():

    flag,indices=set;

    if(self.skin_mask&flag):
      data=attrs[name].data;

      for i in indices:
        mask[i].color=data[i].color;

# ---   *   ---   *   ---

def unequip(ob,equip,chnames):

  if(equip in chnames):
    bpy.data.objects.remove(
      ob.children[chnames.index(equip)]

    );

# ---   *   ---   *   ---

def equip_spawn(ob,equip,piece):
  new_ob=bpy.data.objects.new(equip,piece);
  ob.users_collection[0].objects.link(new_ob);
  new_ob.parent=ob;

  return new_ob;

# ---   *   ---   *   ---

def equip_apparel(ob,chnames,equip,piece):

  if(equip not in chnames):
    new_ob=equip_spawn(ob,equip,piece);

    mod=new_ob.modifiers.new(
      name='Armature',
      type='ARMATURE',

    );

    mod.object=ob;
    chnames=[ch.name for ch in ob.children];

  ob.children[chnames.index(equip)].data=piece;

# ---   *   ---   *   ---

def equip_attach(

  ob,
  chnames,

  equip,
  piece

):

  if(equip not in chnames):

    new_ob = equip_spawn(ob,equip,piece);
    bone   = ob.data.bones[
      piece.da_attach.attach_bone_name

    ];

    new_ob.matrix_world=bone.matrix.to_4x4();
    new_ob.parent_type='BONE';
    new_ob.parent_bone=bone.name;

# ---   *   ---   *   ---

    if(piece.da_attach.mount not in 'NONE'):
      new_ob = equip_spawn(
        ob,
        equip+'_mount',

        piece.da_attach.mount_mesh

      );

      bone   = ob.data.bones[
        piece.da_attach.mount_bone_name

      ];

      new_ob.matrix_world=bone.matrix.to_4x4();
      new_ob.parent_type='BONE';
      new_ob.parent_bone=bone.name;

# ---   *   ---   *   ---

    chnames=[ch.name for ch in ob.children];

  ob.children[chnames.index(equip)].data=piece;

# ---   *   ---   *   ---

def get_apparel_mask(self,C):

  if(not self.skin):
    return;

  if(self.skin.name not in Cache):
    rebuild_bodyparts(self,C);

# ---   *   ---   *   ---

  ob      = C.object;
  bp_dict = Cache[self.skin.name].bp_dict;
  result  = 0;

  for slot in Apparel.SLOTS:

    piece   = eval('self.'+slot);
    equip   = 'BP_Equip::'+slot;

    chnames = [ch.name for ch in ob.children];

    if piece==None:
      unequip(ob,equip,chnames);
      continue;

    else:
      equip_apparel(ob,chnames,equip,piece);

    mask=piece.da_apparel.mask;

    for key in mask.split(','):
      if(key == None or not len(key)):
        continue;

      result|=bp_dict['BP_Mask::'+key][0];

  self.skin_mask=result;

# ---   *   ---   *   ---

def attach_swap(self,C):

  ob      = C.object;

  chnames = [ch.name for ch in ob.children];

  for slot in Attach.SLOTS:

    piece   = eval('self.'+slot);
    equip   = 'BP_Equip::'+slot;

    chnames = [ch.name for ch in ob.children];

    if piece==None:
      unequip(ob,equip,chnames);
      chnames=[ch.name for ch in ob.children];

      unequip(ob,equip+'_mount',chnames);
      continue;

    else:

      equip_attach(
        ob,
        chnames,
        equip,
        piece

      );

# ---   *   ---   *   ---

def anim_kls_match(self,ob):
  name=bpy.context.active_object.data.name+'::';
  return ob.name.startswith(name);

# ---   *   ---   *   ---

def get_secondary_anim(act_name,piece):

  name=piece.name+'->'+act_name;

  if(name not in bpy.data.actions):
    bpy.data.actions.new(name);

  if(piece.shape_keys.animation_data==None):
    act=piece.shape_keys.animation_data_create();
    act.use_fake_user=True;

  return bpy.data.actions[name];

# ---   *   ---   *   ---

def fcurves_path(fcurves):

  return [

    fcurve.data_path
    for fcurve in fcurves

  ];

# ---   *   ---   *   ---

def fcurves_map(path):

  out={};

  for idex,key in path.items():
    if(key in out):
      out[key].append(idex);

    else:
      out[key]=[idex];

  return out;

# ---   *   ---   *   ---

def fcurves_imit(dst,src):

  out      = {};

  dst_path = fcurves_path(dst.fcurves);
  src_path = fcurves_path(src.fcurves);

  cpy_path = list(dst_path);
  top      = len(dst_path);

  for key in src_path:

    if(key not in dst_path):
      dst.fcurves.new(key,index=top);
      cpy_path.append(key);
      top+=1;

  dst_path=fcurves_map({
    i:s for i,s in enumerate(cpy_path)

  });

  src_path=fcurves_map({
    i:s for i,s in enumerate(src_path)

  });

  for key in src_path:

    for i in range(len(src_path[key])):

      dst_idex=dst_path[key][i];
      src_idex=src_path[key][i];

      out[dst_idex]=src_idex;

  return out;

# ---   *   ---   *   ---

def copy_pose(dst,dst_f,src,src_f):

  path=fcurves_imit(dst,src);

  for dst_i,src_i in path.items():

    c0=dst.fcurves[dst_i];
    c1=src.fcurves[src_i];

    f0=c0.keyframe_points;
    f1=c1.keyframe_points;

    frame=None;

    for key in f1:
      if(key.co[0]==src_f):
        frame=key;
        break;

    if(frame):
      kf=frame.co[1];

    else:

      idex=None;

      if(src_f==src.frame_range[0]):
        idex=0;

      elif(src_f==src.frame_range[1]):
        idex=-1;

      if(idex!=None):
        kf=f1[idex].co[1];

    if(kf!=None):

      frame=None;
      for key in f0:
        if(key.co[0]==dst_f):
          frame=key;
          break;

      if(frame):
        f0.remove(frame);

      f0.insert(dst_f,kf);

# ---   *   ---   *   ---

def enforce_transition(act):

  if(act.da_anim.trans_beg):

    src=act.da_anim.trans_beg;

    copy_pose(
      act,
      act.frame_range[0],

      src,
      src.frame_range[1]

    );

  if(act.da_anim.trans_end):

    src=act.da_anim.trans_end;

    frame=act.frame_range[1];
    frame+=act.da_anim.trans_len;

    copy_pose(
      act,
      frame,

      src,
      src.frame_range[0]

    );

# ---   *   ---   *   ---

def get_anim_list(self,C):

  out=[];

  for anim in bpy.data.actions:
    if(anim_kls_match(None,anim)):
      out.append(anim);

  return out;

# ---   *   ---   *   ---

def set_anim(self,C):

  ob  = C.active_object;
  act = self.action;

  ob.animation_data.action=act;

  if(act.da_anim.is_trans):
    enforce_transition(act);

# ---   *   ---   *   ---
# set frame range

  beg,end=da_anim.get_length();

  C.scene.frame_start,C.scene.frame_end=\
    int(beg),int(end);

  clear=(act.da_anim.shape_frames==False);

# ---   *   ---   *   ---
# manage secondary actions

  chnames=[ch.name for ch in ob.children];

  for slot in Attach.XN_SLOTS:

    piece=eval('self.'+slot);

    if(

       piece==None
    or piece.shape_keys.animation_data == None

    ):

      continue;

    equip='BP_Equip::'+slot;
    mount=equip+'_mount';

# ---   *   ---   *   ---

    if(clear):
      sec=None;

    else:
      sec=get_secondary_anim(act.name,piece);

    piece.shape_keys.animation_data.action=sec;

# ---   *   ---   *   ---

    if(mount not in chnames):
      continue;

    piece=ob.children[chnames.index(mount)].data;

    if(clear):
      sec=None;

    else:
      sec=get_secondary_anim(act.name,piece);

    piece.shape_keys.animation_data.action=sec;

# ---   *   ---   *   ---
# apply anim state

  anim=act.da_anim;

  for i in range(State.MASK_SZ):
    if(anim.state_mask&(1<<i)):
      State.apply(self.states[i]);

# ---   *   ---   *   ---

class DA_Char:

  def __init__(self):

    self.bp_dict={};
    self.apparel={};

# ---   *   ---   *   ---

class DA_Char_BL(PropertyGroup):

  skin: PointerProperty(

    name        = 'Skin',
    description = "Base skin for character",

    type        = Mesh,
    update      = rebuild_bodyparts,

  );

  skin_mask: IntProperty(

    name        = 'Skin mask',
    description = "Controls hiding of bodyparts",

    default     = 0,
    update      = rebuild_mask,

  );

  state_mask: IntProperty(

    name        = 'State mask',
    description = "Enforces vars for current state",

    default     = 0,

  );

  state_i: IntProperty(default=0);
  states: CollectionProperty(
    type=DA_State_BL

  );

  action: PointerProperty(

    name        = 'Action',
    description = "Current action being edited",

    type        = Action,
    poll        = anim_kls_match,
    update      = set_anim,

  );

  for slot in Apparel.SLOTS:
    exec(slot+': PointerProperty('\
      'type=Mesh,'\
      'update=get_apparel_mask,'\
      'poll=Apparel.match_'+slot+','\
    ');');

  for slot in Attach.SLOTS:

    exec(slot+': PointerProperty('\
      'type=Mesh,'\
      'update=attach_swap,'\
      'poll=Attach.match_'+slot+','\
    ');');

# ---   *   ---   *   ---

class DA_UL_States(UIList):

  # the number of args here is a clear
  # testament to your incompetence
  def draw_item(
    self,C,layout,

    ob,slot,icon,

    active_data,
    active_propname

  ):

    layout.prop(slot,'ID');

# ---   *   ---   *   ---

class DA_State_Panel(Panel):

  bl_label       = 'State Editor';
  bl_idname      = 'DA_PT_State_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'data';
  bl_category    = 'DA';

  @classmethod
  def poll(cls,C):

    ob=C.active_object;

    return (

        ob!=None
    and isinstance(ob.data,Armature)

    );

  def draw(self,C):

    layout = self.layout;

    ob     = C.active_object;
    char   = ob.data.da_char;

# ---   *   ---   *   ---

    row=layout.row();

    row.template_list(
      'DA_UL_States','',

      char,'states',
      char,'state_i',

    );

    col=row.column();

    col.operator(
      'darkage.state_add',
      text='',
      icon='ADD'

    );

    col.operator(
      'darkage.state_remove',
      text='',
      icon='REMOVE'

    );

    col.operator(
      'darkage.state_goup',
      text='',
      icon='TRIA_UP'

    );

    col.operator(
      'darkage.state_godown',
      text='',
      icon='TRIA_DOWN'

    );

    layout.separator();
    box=layout.box();
    box.row();

    if char.state_i < len(char.states):
      State.draw(char.states[char.state_i],box);

# ---   *   ---   *   ---

class DA_Char_Panel(Panel):

  bl_label       = 'DarkAge Character';
  bl_idname      = 'DA_PT_Char_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'data';
  bl_category    = 'DA';

#   ---     ---     ---     ---     ---

  @classmethod
  def poll(cls,C):

    ob=C.active_object;

    return (

        ob!=None
    and isinstance(ob.data,Armature)

    );

  def draw(self,C):

    layout = self.layout;

    ob     = C.active_object;

    scene  = C.scene;
    char   = ob.data.da_char;

    row=layout.row();

# ---   *   ---   *   ---

    row.label(text='Base skin');
    row.prop(char,'skin',text='');

# ---   *   ---   *   ---

    layout.separator();
    box=layout.box();
    row=box.row();

    row.label(text='Apparel');
    box.separator();

    for slot in Apparel.SLOTS:

      if('_R' not in slot):
        row=box.row();
        row.label(text='  '+slot.replace('_L',''));

      row.prop(char,slot,text='');

# ---   *   ---   *   ---

    layout.separator();
    box=layout.box();
    row=box.row();

    row.label(text='Attachments');
    layout.separator();

    for slot in Attach.SLOTS:

      row=box.row();
      row.label(text='  '+slot);
      row.prop(char,slot,text='');

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_UL_States);

  register_class(DA_Char_BL);
  register_class(DA_Char_Panel);
  register_class(DA_State_Panel);

  Armature.da_char=PointerProperty(
    type=DA_Char_BL

  );

def unregister():

  del Armature.da_char;

  unregister_class(DA_Char_BL);
  unregister_class(DA_Char_Panel);
  unregister_class(DA_State_Panel);

  unregister_class(DA_UL_States);

# ---   *   ---   *   ---

