#!/usr/bin/python
# ---   *   ---   *   ---
# CRK
# Corruptor of geometry
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
from arcana.Bytes import CRK;

# ---   *   ---   *   ---

class DA_OT_CRK_Run(Operator):

  bl_idname      = "darkage.crk_run";
  bl_label       = "Exports mesh";

  bl_description = \
    "Transforms mesh into binary CRK file";

  def execute(self,C):

    ob    = C.active_object;
    crk   = C.scene.da_crk;

    fpath = crk.outdir + ob.data.name;

    CRK.bl_to_crk(ob,fpath);
    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_CRK(PropertyGroup):

  matid: IntProperty(

    name        = 'Material ID',

    description =
      "ID of DA material to use for mesh",

    default     = 0,
    min         = 0,
    max         = (2**16)-1,

  );

  outdir: StringProperty(
    description = "Path to output directory",
    default     = '/tmp/',

  );

# ---   *   ---   *   ---

class DA_CRK_Panel(Panel):

  bl_label       = 'DarkAge CRK';
  bl_idname      = 'DA_PT_CRK_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'scene';
  bl_category    = 'DA';

# ---   *   ---   *   ---

  @classmethod
  def poll(cls,context):

    ob=context.active_object;

    return (
        ob!=None
    and isinstance(ob.data,Mesh)

    );

# ---   *   ---   *   ---

  def draw(self,context):

    layout = self.layout;

    ob     = context.active_object;
    crk    = context.scene.da_crk;

# ---   *   ---   *   ---

    row=layout.row();
    row.prop(crk,"outdir",text='');

    row=layout.row();
    row.prop(crk,"matid");

    row=layout.row();
    row.operator(
      'darkage.crk_run',
      text='BAKE',
      icon='SPHERE'

    );

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_CRK);
  register_class(DA_OT_CRK_Run);
  register_class(DA_CRK_Panel);

  Scene.da_crk=PointerProperty(
    type=DA_CRK

  );

# ---   *   ---   *   ---

def unregister():

  del Scene.da_crk;

  unregister_class(DA_CRK);
  unregister_class(DA_OT_CRK_Run);
  unregister_class(DA_CRK_Panel);

# ---   *   ---   *   ---
