#!/usr/bin/python
# ---   *   ---   *   ---
# AL IFACE
# Asset Layer
# as seen by user
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
from ..guts.Meta import *;

from arcana import AUVICACHE;

from arcana.Mod import bl_kls_merge;
from arcana.DAF import *;

from arcana.Tools import (

  chkdir,

  hexstr_range,
  bl_list2enum

);

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.1b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

CACHEPATH = AUVICACHE+'/AL/';
SUFFIXES  = hexstr_range(256);

# ---   *   ---   *   ---
# method class

class DA_AL(PropertyGroup):

  def new(self):
    self.ref=None;
    self.find_ref();

# ---   *   ---   *   ---
# locates collection ice
# is a property of

  def find_ref(self):

    if self.ref:
      return;

    for c in bpy.data.collections:
      if c.da_al == self:
        self.ref=c;
        break;

# ---   *   ---   *   ---
# locates archive file assoc
# with this collection
#
# gives weak handle

  def find_daf(self):
    fpath = chkdir(CACHEPATH,self.name);
    daf   = DAF(fpath);

    return daf;

# ---   *   ---   *   ---
# checks whether self.name is
# already present within archive

  @staticmethod
  def get_suffixes():

    C=bpy.context;
    if not hasattr(C.collection,'da_al'):
      return bl_list2enum(['00']);

    self = C.collection.da_al;

    out  = [];

    daf  = self.find_daf();
    n    = daf.replchk(self.name);

    if n==0:
      out=SUFFIXES[0];

    else:
      out=SUFFIXES[0:n];

    return bl_list2enum(out);

# ---   *   ---   *   ---
# pre-pends name of asset
# to string

  def tag(self,s):
    return f"{self.name}::{s}";

# ---   *   ---   *   ---
# collection has object

  def hasob(self,name):
    return self.tag(name) in self.ref.objects;

# ---   *   ---   *   ---
# ^append

  def setob(self,name,me):

    if isinstance(me,str):
      me=bpy.data.meshes[me];

    ob=self.getob(name);

    if not ob:
      ob=new_object(self.tag(name),me);

    else:
      ob.data=me;

    return ob;

# ---   *   ---   *   ---
# ^fetch

  def getob(self,name):
    if self.hasob(name):
      return self.ref.objects[self.tag(name)];

    return None;

# ---   *   ---   *   ---
# get self is attached
# to scene collection

  def is_scene(self,C):
    return self==C.scene.collection.da_al;

# ---   *   ---   *   ---
# ^attr class

class DA_AL(PropertyGroup):

  name: StringProperty(
    name        = 'Name',
    description = "Identifier for this group",

    default     = 'ASSET',

  );

  dafname: StringProperty(
    name        = 'DAF',
    description = "Archive file assoc with group",

    default     = 'Lib'

  );

  suffix: EnumProperty(

    name        = 'Suffix',
    description = (
      "Secondary identifier for "
    + "this group. Utilized if other "
    + "assets with it's name exist"

    ),

    items       = DA_AL.get_suffixes(),
    default     = '00',

  );

  ref: PointerProperty(type=Collection);

  exec(bl_kls_merge('DA_AL'));

# ---   *   ---   *   ---
# button

class DA_OT_AL_New(Operator):

  bl_idname      = "darkage.al_new";
  bl_label       = "Create asset layer";

  bl_description = (
    "Manual initialization for asset layers "
  + "is required as argless __init__ doesn't "
  + "work for PropertyGroup.\n\nGENIUS design"

  );

  def execute(self,C):

    c    = C.scene.collection;
    name = 'Asset Layer';

    if name not in c.children:
      new_collection(name);

    else:
      c.children[name].da_al.new();

    return {'FINISHED'};

# ---   *   ---   *   ---
# ^panel

class DA_AL_Panel(Panel):

  bl_label       = 'Asset Layer';
  bl_idname      = 'DA_PT_AL_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'scene';
  bl_category    = 'DA';

# ---   *   ---   *   ---
# validate selected

  @classmethod
  def poll(cls,C):

    al=C.collection.da_al;

    return (

       al.is_scene(C)
    or al.ref != None

    );

# ---   *   ---   *   ---
# crux

  def draw(self,C):

    al=C.collection.da_al;

    if al.is_scene(C):
      self.draw_frame_panel(C);

    else:
      self.draw_ice_panel(C);

# ---   *   ---   *   ---
# ^path A

  def draw_frame_panel(self,C):

    layout = self.layout;

    c      = C.collection
    al     = c.da_al;

    s='NEW';
    if 'Asset Layer' in c.children:
      s='REFRESH'

    row=layout.row();
    row.operator(

      'darkage.al_new',

      text=s,
      icon='MESH_ICOSPHERE'

    );

# ---   *   ---   *   ---
# ^path B

  def draw_ice_panel(self,C):

    layout = self.layout;
    al     = C.collection.da_al;

    self.draw_imp_props(C);

  def draw_imp_props(self,C):

    layout = self.layout;
    al     = C.collection.da_al;

    row=layout.row();
    row.prop(al,'dafname');

    layout.separator();

    row=layout.row();
    row.prop(al,'name');

    row=layout.row();
    row.prop(al,'suffix');

# ---   *   ---   *   ---

exec(DA_iface_module("""

$:rclass;>
  DA_AL
  DA_AL_Panel
  DA_OT_AL_New

$:bind;>
  Collection.da_al:DA_AL

"""));

# ---   *   ---   *   ---
