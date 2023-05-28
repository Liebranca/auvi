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

import os;

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

from ..guts.CRK import CACHEPATH as CRKPATH;
from ..guts.ANS import CACHEPATH as ANSPATH;
from ..guts.Matbake import CACHEPATH as JOJPATH;

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.2b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

CACHEPATH = AUVICACHE+'/AL/';
SUFFIXES  = hexstr_range(256);

DAF_MODES = [

  ('PUSH','Push'   ,'Add new entry to DAF'),

  ('REPL','Replace','Update existing entry'),
  ('POP' ,'Remove' ,'Remove existing entry'),

];

ASSET_FCNT=3;

# ---   *   ---   *   ---
# method class

class DA_AL(PropertyGroup):

  def new(self):
    self.ref=None;
    self.get_ref();

# ---   *   ---   *   ---
# locates collection ice
# is a property of

  def get_ref(self):

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

  def get_daf(self):
    fpath = chkdir(CACHEPATH,self.dafname);
    daf   = DAF(fpath);

    return daf;

# ---   *   ---   *   ---
# checks whether self.name is
# already present within archive

  def get_suffixes(self,C):

    daf  = self.get_daf();
    n    = daf.replchk(self.name);

    return bl_list2enum(SUFFIXES[0:n]);

# ---   *   ---   *   ---
# ^sync user pick to actual value

  def sync_suffix(self,C):
    self.suffix=self.suffix_pick;

# ---   *   ---   *   ---
# pre-pends name of asset
# to string

  def tag(self,s):
    return f"{self.name}::{s}";

# ---   *   ---   *   ---
# appends suffix to name of asset

  def fullname(self):
    return f"{self.name}_{self.suffix}";

# ---   *   ---   *   ---
# ensures the suffix in use is
# valid for current mode

  def validate_suffix(self,daf):

    out = True;
    n   = daf.replchk(self.name);

    # push always to new suffix
    if self.mode=='PUSH':
      self.suffix=SUFFIXES[n];

    # should never see this errme
    # unless you bruteforce it
    elif self.suffix==SUFFIXES[n]:

      print(

        f"DAF {self.mode} out of bounds\n"
      + f"for {self.name}_{self.suffix}"

      );

      out=False;

    return out;

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
# writes files generated by
# asset bake tools to archive

  def write(self):

    out   = "";

    daf   = self.get_daf();
    files = self.get_files(daf);

    # input ok
    if len(files) == ASSET_FCNT:

      daf.cpush(files);

      if self.mode=='PUSH':
        self.mode='REPL';

    # ^input error
    else:

      out=(

        "DAF write aborted; "
      + "see console for details"

      );

    return out;

# ---   *   ---   *   ---
# get list of files created by
# this asset layer

  def get_files(self,daf):

    if not self.validate_suffix(daf):
      return [];

    out   = [];
    name  = self.fullname();

    paths = [CRKPATH,ANSPATH,JOJPATH];
    exts  = ['.crk','.ans','.joj'];

    for path,ext in zip(paths,exts):

      f=chkdir(path,name+ext)

      if os.path.exists(f):
        out.append();

    return out;

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

  # the real value used when
  # composing filenames;
  # hidden to the user
  suffix: StringProperty(
    default = '00',

  );

  # ^what we show the user
  # ultimately meaningless if
  # the system decides to
  # overwrite self.suffix
  suffix_pick: EnumProperty(

    name        = 'Suffix',
    description = (
      "Secondary identifier for "
    + "this group. Utilized if other "
    + "assets with it's name exist"

    ),

    items       = DA_AL.get_suffixes,
    update      = DA_AL.sync_suffix,

    default     = 0,

  );

  mode: EnumProperty(
    name        = 'Mode',
    description = "Operation done on archive",

    items       = DAF_MODES,
    default     = 'PUSH',

  );

  ref: PointerProperty(type=Collection);

  exec(bl_kls_merge('DA_AL'));

# ---   *   ---   *   ---
# make ice

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
# button

class DA_OT_AL_Write(Operator):

  bl_idname      = "darkage.al_write";
  bl_label       = "Write asset to DAF";

  bl_description = (
    "Pushes or replaces current asset "
  + "to selected archive file."

  );

  def execute(self,C):

    al=C.collection.da_al;
    me=al.write();

    if len(me):
      self.report({'INFO'},me);

    return {'FINISHED'};

# ---   *   ---   *   ---
# ^actual iface code

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

# ---   *   ---   *   ---
# separated this section
# in case we add others

  def draw_imp_props(self,C):

    layout = self.layout;
    al     = C.collection.da_al;

    row=layout.row();
    row.prop(al,'dafname');

    row=layout.row();
    row.prop(al,'mode');

    layout.separator();

    row=layout.row();
    row.prop(al,'name');

    if al.mode != 'PUSH':
      row=layout.row();
      row.prop(al,'suffix_pick');

    layout.separator();

    row=layout.row();
    row.operator(

      'darkage.al_write',

      text='WRITE',
      icon='MESH_ICOSPHERE'

    );

# ---   *   ---   *   ---
# create register/unregister

exec(DA_iface_module("""

$:rclass;>

  DA_AL

  DA_AL_Panel
  DA_OT_AL_New
  DA_OT_AL_Write

$:bind;>
  Collection.da_al:DA_AL

"""));

# ---   *   ---   *   ---