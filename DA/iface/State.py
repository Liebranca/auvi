#!/usr/bin/python
# ---   *   ---   *   ---
# IFACE STATE
# Ticks on a box
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
from . import Attach,Apparel;

from arcana.Tools import bl_list2enum;

# ---   *   ---   *   ---
# ROM

MASK_SZ=32;

D_MODES={

  'MIX':'=',
  'ADD':'+=',
  'SUB':'-=',
  'MUL':'*=',
  'DIV':'/=',

};

MODES=bl_list2enum(D_MODES.keys());

# ---   *   ---   *   ---

class DA_State_Data(PropertyGroup):

  path: StringProperty(default='');
  name: StringProperty(default='');
  value: StringProperty(default='0');

  mode: EnumProperty(
    items=MODES,
    default='MIX',

    name='Mode',
    description=\
      "Sets the operation to carry out on the "
      "referenced attribute",

  );

# ---   *   ---   *   ---

def apply(self):

  for item in self.data:
    op=D_MODES[item.mode];
    exec(item.path+op+item.value);

# ---   *   ---   *   ---

def shape_copy(data,src):

  path  = 'bpy.data.objects["'+src.name+'"]';
  shape = 'shape_keys.key_blocks';

  me    = src.data;

  for key in me.shape_keys.key_blocks:

    if(key.name == 'Basis'):
      continue;

    item       = data.add();

    item.path  =\
      path  + '.data.'\
    + shape + '["'+key.name+'"].value';

    item.name  =\
      src.name.replace('BP_Equip::','')+'::'+key.name;

    item.value = str(eval(item.path));

# ---   *   ---   *   ---

def state_nit(self,C):

  ob   = C.object;
  char = ob.data.da_char;

  for slot in Attach.SLOTS:
    piece   = eval('char.'+slot);
    equip   = 'BP_Equip::'+slot;
    mount   = equip+'_mount';

    chnames = [ch.name for ch in ob.children];

    if(piece==None):
      continue;

    if(piece.shape_keys):
      shape_copy(
        self.data,
        ob.children[chnames.index(equip)]

      );

    if(mount in chnames):
      shape_copy(
        self.data,
        ob.children[chnames.index(mount)]

      );

# ---   *   ---   *   ---

register_class(DA_State_Data);
class DA_State_BL(PropertyGroup):

  ID: StringProperty(

    name        = 'ID',
    description = "Keyword to identify this state",

    default     = '',

  );

  data: CollectionProperty(
    type=DA_State_Data

  );

# ---   *   ---   *   ---
# See how you need a separate class for each
# individual action, no matter how small?
#
# This is GENIUS """design"""

class DA_OT_State_Add(Operator):

  bl_idname      = "darkage.state_add";
  bl_label       = "Add a new state";

  bl_description = \
    "Adds a new toggable state to object";

  def execute(self,C):

    ob   = C.object;
    char = ob.data.da_char;

    x    = char.states.add();

    state_nit(x,C);

    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_State_Remove(Operator):

  bl_idname      = "darkage.state_remove";
  bl_label       = "Destroy current state";

  bl_description = \
    "Discards selected state from object";

  def execute(self,C):

    ob   = C.object;
    char = ob.data.da_char;

    i=char.state_i;
    char.states.remove(i);

    return {'FINISHED'};

# ---   *   ---   *   ---

def draw(self,layout):

  for item in self.data:

    row=layout.row();

    row.label(text=item.name);
    row.prop(item,'value',text='');
    row.prop(item,'mode',text='');

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_State_BL);

  register_class(DA_OT_State_Add);
  register_class(DA_OT_State_Remove);

def unregister():

  unregister_class(DA_OT_State_Add);
  unregister_class(DA_OT_State_Remove);

  unregister_class(DA_State_BL);
  unregister_class(DA_State_Data);

# ---   *   ---   *   ---
