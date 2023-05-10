#!/usr/bin/python
# ---   *   ---   *   ---
# MATBAKE
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

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.1b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---

class DA_Material(PropertyGroup):

  render_sz: IntProperty(
    name        = 'Bake size',
    description =
      "(pow 2) Resolution used for baking",

    default     = 7,
    min         = 4,
    max         = 12,

  );

  name: StringProperty(
    description = "Name of material",
    default     = 'MT_0000',

  );

  fpath: StringProperty(
    description = "Path to output directory",
    default     = '/tmp/',

  );

# ---   *   ---   *   ---

class DA_Material_Panel(Panel):

  bl_label       = 'DarkAge Material';
  bl_idname      = 'DA_PT_Material_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'material';
  bl_category    = 'DA';

# ---   *   ---   *   ---

  @classmethod
  def poll(cls,context):

    ob=context.active_object;

    return (
        ob!=None

    and isinstance(ob.data,Mesh)
    and ob.active_material!=None

    );

# ---   *   ---   *   ---

  def draw(self,context):

    layout = self.layout;

    ob     = context.active_object;
    mat    = ob.active_material.da_material

# ---   *   ---   *   ---

    row=layout.row();
    row.prop(mat,"fpath");

    row=layout.row();
    row.prop(mat,"render_sz",text='');

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_Material);
  register_class(DA_Material_Panel);

  Material.da_material=PointerProperty(
    type=DA_Material

  );

def unregister():

  del Material.da_material;

  unregister_class(DA_Material);
  unregister_class(DA_Material_Panel);

# ---   *   ---   *   ---
