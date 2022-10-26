#!/usr/bin/python
# ---   *   ---   *   ---
# IFACE ATTACH
# Swords and sheathes
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
from arcana.Tools import bl_list2enum;

# ---   *   ---   *   ---
# ROM

D_SLOTS={

  'Hand_R': 'Hand.R',

};

SLOTS=D_SLOTS.keys();
D_SLOTS={

  key.upper():value
  for key,value in D_SLOTS.items()

};

I_SLOTS=['None'];
I_SLOTS.extend(SLOTS);

# ---   *   ---   *   ---

MOUNTS=[

  'None',
  'Hips.L',

];

# ---   *   ---   *   ---

def get_bone_name(self,C):
  self.bone_name=D_SLOTS[self.slot];

# ---   *   ---   *   ---

class DA_Attach_BL(PropertyGroup):

  mount: EnumProperty(

    name        = 'Mount',

    description =\
      "Where the attachment goes when put away",

    items       = bl_list2enum(MOUNTS),
    default     = MOUNTS[0].upper(),

  );

  slot: EnumProperty(

    name        = 'Slot',

    description =\
      "Where the attachment goes when active",

    items       = bl_list2enum(I_SLOTS),
    default     = 'NONE',

    update      = get_bone_name,

  );

  bone_name: StringProperty(
    default     = 'NONE',

  );

# ---   *   ---   *   ---

class DA_Attach_Panel(Panel):

  bl_label       = 'DarkAge Attachment';
  bl_idname      = 'DA_PT_Attach_Panel';
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
    and "Attach::" in ob.name
    and isinstance(ob.data,Mesh)

    );

# ---   *   ---   *   ---

  def draw(self,C):

    layout = self.layout;

    ob     = C.active_object;

    scene  = C.scene;
    piece  = ob.data.da_attach;

# ---   *   ---   *   ---

    row=layout.row();
    row.prop(piece,'slot');

    row=layout.row();
    row.prop(piece,'mount');

# ---   *   ---   *   ---

def register():
  bpy.da_blocks[__file__]=unregister;

  register_class(DA_Attach_BL);
  register_class(DA_Attach_Panel);

  Mesh.da_attach=PointerProperty(
    type=DA_Attach_BL

  );

def unregister():

  del Mesh.da_attach;

  unregister_class(DA_Attach_Panel);
  unregister_class(DA_Attach_BL);

# ---   *   ---   *   ---
# generate poll funcs
#
# these are used to filter out pieces
# by which slot they occupy

for slot in SLOTS:

  exec(

    'def match_'+slot+'(self,ob):\n'\
    '  return ob.da_attach.slot=="'\
    +slot+'".upper();'

  );

# ---   *   ---   *   ---
