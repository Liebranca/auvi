#!/usr/bin/python
# ---   *   ---   *   ---
# IFACE ANIM
# Animation data
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

from arcana.Mod import bl_kls_merge;

from .Meta import *;
from . import Attach,Char,State;

# ---   *   ---   *   ---
# declare class twice so it can
# find it's own methods...
#
# GENIUS strikes again

class DA_Anim(PropertyGroup):

# ---   *   ---   *   ---
# cstruc

  def new(self):
    self.ref=None;
    self.find_ref();

# ---   *   ---   *   ---
# get action assoc with DA_Anim

  def find_ref(self):

    if self.ref:
      return;

    for act in bpy.data.actions:
      if act.da_anim == self:
        self.ref=act;
        break;

# ---   *   ---   *   ---
# get adjusted framerange of action

  def get_length(self):

    self.find_action();

    beg,end  = self.ref.frame_range;
    end     -= (self.is_loop==True);

    return beg,end;

# ---   *   ---   *   ---
# bit mask helpers

  def get_state(self):

    l=[];

    for i in range(State.MASK_SZ):
      b=1<<i;
      l.append((self.state_mask&b)==b);

    return l;

  def set_state(self,values):

    for i in range(State.MASK_SZ):
      if(values[i]):
        self.state_mask|=1<<i;

      else:
        self.state_mask&=~ (1<<i);

# ---   *   ---   *   ---
# ^update self accto mask

  def apply_state(self,C):

    ob   = C.object;
    char = ob.data.da_char;

    for i in range(State.MASK_SZ):
      if(self.state_mask&(1<<i)):
        State.apply(char.states[i]);

# ---   *   ---   *   ---
# give list of names
# of all attachments

  def get_attach_equipped(self,C):

    l  = ['None'];
    ob = C.object;

    if hasattr(ob.data.da_char):

      char=ob.data.da_char;

      for slot in Attach.SLOTS:
        piece=eval('char.'+slot);

        if piece:
          l.append(slot);

    return [(x.upper(),x,'') for x in l];

# ---   *   ---   *   ---
# updates self on attr changes

  def set_anim(self,C):
    ob=C.object;
    Char.set_anim(ob.data.da_char,C);

# ---   *   ---   *   ---

class DA_Anim(PropertyGroup):

  is_attack: BoolProperty(

    name        = 'Attack',
    description = "Frame has weapon hitbox",

    default     = False,

  );

  attack_hitbox: EnumProperty(

    name        = 'Attack.hitbox',
    description = \
      "Which attachment will be used "\
      "to calculate the attack's hitbox.",

    items       = DA_Anim.get_attach_equipped,
    default     = 0,

  );

  is_loop: BoolProperty(
    name        = 'Loop',
    description = "Adjust frame range for looping",

    default     = True,
    update      = DA_Anim.set_anim,

  );

  shape_frames: BoolProperty(
    name        = 'Shape',
    description = "Enables attachment shapekeys",

    default     = False,
    update      = DA_Anim.set_anim,

  );

# ---   *   ---   *   ---

  is_trans: BoolProperty(
    name        = 'Transition',
    description =
      "Forces first and last frames of "
      "animation to come from other actions",

    default     = False,
    update      = DA_Anim.set_anim,

  );

  trans_beg: PointerProperty(
    name        = 'Begin',
    description =
      "Animation being transitioned from",

    type        = Action,
    poll        = Char.anim_kls_match,
    update      = DA_Anim.set_anim

  );

  trans_end: PointerProperty(
    name        = 'End',
    description =
      "Animation being transitioned into",

    type        = Action,
    poll        = Char.anim_kls_match,
    update      = DA_Anim.set_anim

  );

  trans_len: IntProperty(
    name        = 'Length',
    description =
      "End pose is pasted at frame_end+length",

    default     = 0,
    min         = 0,

    update      = DA_Anim.set_anim,

  );

# ---   *   ---   *   ---

  state_mask: IntProperty(default=0);
  v_state_mask: BoolVectorProperty(

    size    = State.MASK_SZ,

    get     = DA_Anim.get_state,
    set     = DA_Anim.set_state,

    update  = DA_Anim.apply_state,

  );

  action: PointerProperty(type=Action);

# ---   *   ---   *   ---
# """fixes""" for GENIUS

  exec(bl_kls_merge('DA_Anim'));

# ---   *   ---   *   ---

class DA_Anim_Panel(Panel):

  bl_label       = 'DarkAge Animation';
  bl_idname      = 'DA_PT_Anim_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'data';
  bl_category    = 'DA';

#   ---     ---     ---     ---     ---

  @classmethod
  def poll(cls, context):

    ob=context.active_object;

    return (
        ob!=None
    and isinstance(ob.data,Armature)

    );

# ---   *   ---   *   ---

  def draw_shapebox(self,me,shapes):

    layout = self.layout;

    box    = layout.box();
    row    = box.row();

    row.label(text=me.name);
    layout.separator();
    row=box.row();

    for shape in shapes[1:]:
      row=box.row();
      row.prop(shape,'value',text=shape.name);

    layout.separator();

# ---   *   ---   *   ---

  def draw(self, context):

    layout = self.layout;

    ob     = context.active_object;
    char   = ob.data.da_char;

# ---   *   ---   *   ---

    row=layout.row();
    row.prop(char,'action');

    if(char.action==None):
      return;

    layout.separator();

# ---   *   ---   *   ---

    act  = ob.animation_data.action;
    anim = act.da_anim;

# ---   *   ---   *   ---

    box=layout.box();

    row=box.row();
    row.label(text='Properties');

    layout.separator();
    box.row();

    row=box.row();

    row.prop(anim,'is_attack');
    row.prop(anim,'attack_hitbox',text='');

    row.prop(anim,'is_loop');
    row.prop(anim,'shape_frames');

    row=box.row();
    row.prop(anim,'is_trans');

# ---   *   ---   *   ---

    if(anim.is_trans):
      layout.separator();
      box=layout.box();
      row=box.row();

      box.use_property_split=False;
      box.use_property_decorate=False;

      row.label(text='Transition');
      box.row();

      row=box.row();
      row.prop(anim,'trans_beg');

      row=box.row();
      row.prop(anim,'trans_end');

      row=box.row();
      row.prop(anim,'trans_len');

# ---   *   ---   *   ---

    layout.separator();
    box=layout.box();
    row=box.row();

    box.use_property_split=False;
    box.use_property_decorate=False;

    row.label(text='States');
    box.row();

    row=box.row();
    for i in range(State.MASK_SZ):

      if(i==len(char.states)):
        break;

      if(i and not i%4):
        row=box.row();

      n=char.states[i].ID;
      row.prop(
        anim,'v_state_mask',
        text=n,
        index=i

      );

# ---   *   ---   *   ---

    if(anim.shape_frames==False):
      return;

    layout.separator();

# ---   *   ---   *   ---
# attachment controls

    char    = ob.data.da_char;
    chnames = [ch.name for ch in ob.children];

    for slot in Attach.XN_SLOTS:
      piece = eval('char.'+slot);
      equip = 'BP_Equip::'+slot+'_mount';

      if piece==None:
        continue;

      shapes=piece.shape_keys.key_blocks;
      self.draw_shapebox(piece,shapes);

# ---   *   ---   *   ---
# ^repeat for mount if present

      if(equip in chnames):

        me     = ob.children[
          chnames.index(equip)

        ].data;

        shapes = me.shape_keys.key_blocks;
        self.draw_shapebox(me,shapes);

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_Anim);
  register_class(DA_Anim_Panel);

  Action.da_anim=PointerProperty(
    type=DA_Anim

  );

def unregister():

  del Action.da_anim;

  unregister_class(DA_Anim_Panel);
  unregister_class(DA_Anim);

# ---   *   ---   *   ---
