#!/usr/bin/python
# ---   *   ---   *   ---
# IFACE APPAREL
# High fashion
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

SLOTS=[

  'Helmet',
  'Chest',
  'Belt',
  'Greaves',

  'Cape',
  'Aura',

  'Boot_L',
  'Boot_R',

  'Glove_L',
  'Glove_R',

  'Pauldron_L',
  'Pauldron_R',

];

# ---   *   ---   *   ---

def bl_list2enum(l):
  return [(x.upper(),x,'') for x in l];

# ---   *   ---   *   ---

class DA_Apparel_BL(PropertyGroup):

  slot: EnumProperty(

    name        = 'Slot',

    description =\
      "Comma-separated list of bodyparts "\
      "hidden by this piece",

    items       = bl_list2enum(SLOTS),
    default     = SLOTS[0].upper(),

  );

  mask: StringProperty(

    name        = 'Mask',

    description =\
      "Comma-separated list of bodyparts "\
      "hidden by this piece",

    default     = '',

  );

# ---   *   ---   *   ---

class DA_Apparel_Panel(Panel):

  bl_label       = 'DarkAge Apparel';
  bl_idname      = 'DA_PT_Apparel_Panel';
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
    and "Apparel::" in ob.name
    and isinstance(ob.data,Mesh)

    );

# ---   *   ---   *   ---

  def draw(self,C):

    layout = self.layout;

    ob     = C.active_object;

    scene  = C.scene;
    piece  = ob.data.da_apparel;

# ---   *   ---   *   ---

    row=layout.row();
    row.prop(piece,'slot');

    row=layout.row();
    row.prop(piece,'mask');

# ---   *   ---   *   ---

def register():
  bpy.da_blocks[__file__]=unregister;

  register_class(DA_Apparel_BL);
  register_class(DA_Apparel_Panel);

  Mesh.da_apparel=PointerProperty(
    type=DA_Apparel_BL

  );

def unregister():

  del Mesh.da_apparel;

  unregister_class(DA_Apparel_Panel);
  unregister_class(DA_Apparel_BL);

# ---   *   ---   *   ---
# generate poll funcs
#
# these are used to filter out pieces
# by which slot they occupy

for slot in SLOTS:

  exec(

    'def match_'+slot+'(self,ob):\n'\
    '  return ob.da_apparel.slot=="'\
    +slot+'".upper();'

  );

# ---   *   ---   *   ---
