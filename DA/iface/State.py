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

  print(src.name);

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
# for mixing base skin and attach
# functionality
#
# essentially: lets you use shape
# modifiers on base skin as we do
# for attachments themselves

def skin_as_piece(slot,piece,equip,ob):

  if piece==None:
    return None;

  elif slot == 'skin':

    equip=[
      o.name for o in ob.children
      if o.data and o.data.name == piece.name

    ];

    if not len(equip):
      return None;

    equip=equip[0];

  return equip;

# ---   *   ---   *   ---

def state_nit(self,C):

  ob   = C.object;
  char = ob.data.da_char;

  for slot in Attach.XN_SLOTS:
    piece   = eval('char.'+slot);
    equip   = 'BP_Equip::'+slot;
    mount   = equip+'_mount';

    chnames = [ch.name for ch in ob.children];
    equip   = skin_as_piece(
      slot,piece,equip,ob

    );

    if equip==None:
      continue;

# ---   *   ---   *   ---

    if piece.shape_keys:

      equip= \
        ob.children[chnames.index(equip)] \
        if equip in chnames else equip;

      shape_copy(self.data,equip);

    if mount in chnames:
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

    i    = char.state_i;

    char.states.remove(i);

    return {'FINISHED'};

# ---   *   ---   *   ---

def wap(states,src_i,dst_i):

  dst = states[dst_i];
  src = states[src_i];

  v=dst.ID;
  dst.ID=src.ID;
  src.ID=v;

  for i in range(len(src.data)):
    x=dst.data[i];
    y=src.data[i];

    v=[x.path,x.name,x.value,x.mode];
    (x.path,x.name,x.value,x.mode)=\
      (y.path,y.name,y.value,y.mode);

    (y.path,y.name,y.value,y.mode)=v;

# ---   *   ---   *   ---

class DA_OT_State_Goup(Operator):

  bl_idname      = "darkage.state_goup";
  bl_label       = "Change state priority";
  bl_description = "Change state priority";

  def execute(self,C):

    ob   = C.object;
    char = ob.data.da_char;

    i    = char.state_i;

    if(i>0):
      wap(char.states,i-1,i);
      char.state_i-=1;

    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_State_Godown(Operator):

  bl_idname      = "darkage.state_godown";
  bl_label       = "Change state priority";
  bl_description = "Change state priority";

  def execute(self,C):

    ob   = C.object;
    char = ob.data.da_char;

    i    = char.state_i;

    if(i<len(char.states)-1):
      wap(char.states,i+1,i);
      char.state_i+=1;

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
  register_class(DA_OT_State_Goup);
  register_class(DA_OT_State_Godown);

def unregister():

  unregister_class(DA_OT_State_Godown);
  unregister_class(DA_OT_State_Goup);
  unregister_class(DA_OT_State_Add);
  unregister_class(DA_OT_State_Remove);

  unregister_class(DA_State_BL);
  unregister_class(DA_State_Data);

# ---   *   ---   *   ---
