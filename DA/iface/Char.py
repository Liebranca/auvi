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

from .Meta import *;
from . import Apparel;

# ---   *   ---   *   ---
# ROM

ATTACH_LIST=[

  ('HAND_R','Right hand',''),
  ('HIPS_L0','Hip sheath 0',''),

];

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
# shady use of unique id for storage
# required to bypass the GENIUS of this API

  ob=C.object;

  if(id(ob) not in Cache):
    Cache[id(ob)]=DA_Char();

  Cache[id(ob)].bp_dict=bp_dict;

# ---   *   ---   *   ---

def rebuild_mask(self,C):

  if(not self.skin):
    return;

# ---   *   ---   *   ---
# unhide all

  bp_dict = Cache[id(C.object)].bp_dict;

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

def get_apparel_mask(self,C):

  ob      = C.object;
  bp_dict = Cache[id(ob)].bp_dict;
  result  = 0;

  chnames = [ch.name for ch in ob.children];

  for slot in Apparel.SLOTS:
    piece = eval('self.'+slot);
    equip = 'BP_Equip::'+slot;

    if piece==None:

      if(equip in chnames):
        bpy.data.objects.remove(
          ob.children[chnames.index(equip)]

        );

      continue;

    if(equip not in chnames):

      new_ob=bpy.data.objects.new(equip,piece);
      C.collection.objects.link(new_ob);

      new_ob.parent=ob;

      mod=new_ob.modifiers.new(
        name='Armature',
        type='ARMATURE',

      );

      mod.object=ob;

    ob.children[
      chnames.index(equip)

    ].data=piece;

    mask=piece.da_apparel.mask;

    for key in mask.split(','):
      if(key == None or not len(key)):
        continue;

      result|=bp_dict['BP_Mask::'+key][0];

  self.skin_mask=result;

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

  for slot in Apparel.SLOTS:
    exec(slot+': PointerProperty('\
      'type=Mesh,'\
      'update=get_apparel_mask,'\
      'poll=Apparel.match_'+slot+','\
    ');');

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

    row.label(text='Base skin');
    row.prop(char,'skin',text='');

# ---   *   ---   *   ---

    layout.separator();
    row=layout.row();

    row.label(text='Equipment');

# ---   *   ---   *   ---

    for slot in Apparel.SLOTS:

      if('_R' not in slot):
        row=layout.row();
        row.label(text='>'+slot.replace('_L',''));

      row.prop(char,slot,text='');

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_Char_BL);
  register_class(DA_Char_Panel);

  Armature.da_char=PointerProperty(
    type=DA_Char_BL

  );

def unregister():

  del Armature.da_char;

  unregister_class(DA_Char_BL);
  unregister_class(DA_Char_Panel);

# ---   *   ---   *   ---

