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
from ..guts.CRK import CRK;

# ---   *   ---   *   ---

class DA_OT_CRK_Run(Operator):

  bl_idname      = "darkage.crk_run";
  bl_label       = "Exports mesh";

  bl_description = \
    "Transforms mesh into binary CRK file";

  def execute(self,C):

    ob    = C.active_object;
    crk   = C.scene.da_crk;

    CRK.from_bmesh(ob);
    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_CRK(PropertyGroup):
  pass;

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
    row.operator(
      'darkage.crk_run',
      text='BAKE',
      icon='SPHERE'

    );

# ---   *   ---   *   ---
# generate boilerplate

exec(DA_iface_module("""

$:rclass;>
  DA_CRK
  DA_OT_CRK_Run
  DA_CRK_Panel

$:bind;>
  Scene.da_crk: DA_CRK

"""));

# ---   *   ---   *   ---
