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

from .Meta import *;

# ---   *   ---   *   ---
# ROM

ATTACH_LIST=[

  ('HAND_R','Right hand',''),
  ('HIPS_L0','Hip sheath 0',''),

];

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
      "Which attachment will be used"\
      "to calculate the attack's hitbox.",

    items       = ATTACH_LIST,
    default     = 'HAND_R',

  );

  frame_cnt: IntProperty(

    name        = 'Frames',
    description = \
      "How many frames the animation has",

    default     = 6,
    min         = 0,

  );

  attach: PointerProperty(

    name        = 'Attach',
    description = "Test!",

    type        = Object,

  );

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

  def draw(self, context):

    layout = self.layout;

    ob     = context.active_object;

    scene  = context.scene;
    act    = ob.animation_data.action;

    if act==None: return;

    anim=act.da_anim;

    row=layout.row();
    row.prop(anim,'is_attack');
    row.prop(anim,'attack_hitbox');

    row=layout.row();
    row.prop(anim,'frame_cnt');

    row=layout.row();
    row.prop(anim,'attach');

#    row.operator("lytmat.initmat", text="INIT", icon="SMOOTH");
#    layout.separator();
#    row.label("Edges:");

# ---   *   ---   *   ---

def register():

  bpy.da_blocks['Anim']=unregister;

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
