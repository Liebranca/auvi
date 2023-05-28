#!/usr/bin/python
# ---   *   ---   *   ---
# MATBAKE IFACE
# Takes pictures
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
from ..guts import Matbake as guts;

from arcana.Mod import bl_kls_merge;
from arcana.Tools import bl_list2enum;

# ---   *   ---   *   ---
# info

class DA_Matbake(PropertyGroup):

  VERSION = 'v2.00.1';
  AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

  RENDER_SIZES=[

    '64','128','256','512',
    '1024','2048','4096',

  ];

  AA_SCALES=[

    ('x1','1',"No scaling"),
    ('x2','2',"Double scale"),
    ('x4','4',"Four times scale"),
    ('x8','8',"Eight times scale"),

    ('x16','16',"Sixteen times scale"),

  ];

# ---   *   ---   *   ---
# ^attr def

class DA_Matbake(PropertyGroup):

  dst: PointerProperty(

    name        = 'Baketo',
    description = \
      "Low-poly object used for baking",

    type        = Object,

  );

  render_sz: EnumProperty(

    name        = 'Bake size',
    description =
      "Resolution used for baking",

    items       = bl_list2enum(
      DA_Matbake.RENDER_SIZES

    ),

    default     = '128',

  );

  render_scale: EnumProperty(

    name        = 'AA Scale',
    description = (
      "Renders bake at higher resolution "
    + "to achieve smoother result"

    ),

    items       = DA_Matbake.AA_SCALES,
    default     = 'x2',

  );

  # join with previous def
  exec(bl_kls_merge("DA_Matbake"));

# ---   *   ---   *   ---
# runs baking routine for
# objects in this collection

class DA_OT_Matbake_Run(Operator):

  bl_idname      = "darkage.matbake_run";
  bl_label       = "Bake materials to JOJ";

  bl_description = \
    "Packs materials into JOJ file";

  def execute(self,C):

    al=C.collection.da_al;
    me=guts.run(al);

    if len(me):
      self.report({'INFO'},me);

    return {'FINISHED'};

# ---   *   ---   *   ---
# adds material baking ctl
# to scene tab

class DA_Matbake_Panel(Panel):

  bl_label       = 'Matbake';
  bl_idname      = 'DA_PT_Matbake_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'scene';
  bl_category    = 'DA';

# ---   *   ---   *   ---

  @classmethod
  def poll(cls,C):

    ob=C.active_object;

    return (
        ob!=None
    and isinstance(ob.data,Mesh)

    );

# ---   *   ---   *   ---

  def draw(self,C):

    layout = self.layout;

    c  = C.collection;
    mb = c.da_matbake;

    row=layout.row();
    row.label(text='Lowpoly:');
    row.prop(mb,"dst",text='');

    row=layout.row();
    row.label(text='Size:');
    row.prop(mb,"render_sz",text='');

    row=layout.row();
    row.label(text='AA Scale:');
    row.prop(mb,"render_scale",text='');

    row=layout.row();
    row.operator(
      'darkage.matbake_run',

      text='BAKE',
      icon='MATERIAL'

    );

# ---   *   ---   *   ---
# create register/unregister

exec(DA_iface_module("""

$:rclass;>

  DA_Matbake

  DA_OT_Matbake_Run
  DA_Matbake_Panel

$:bind;>
  Collection.da_matbake : DA_Matbake

"""));

# ---   *   ---   *   ---
