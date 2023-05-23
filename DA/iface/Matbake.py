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
from ..guts import Matbake as guts;

from arcana import ARPATH;
from arcana.Tools import bl_list2enum;

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.3b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

MAPPING_TYPES=[

  'Generated',
  'Normal',
  'UV',

];

PROJECTION_TYPES=[
  'BOX',
  'FLAT',

];

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
# syncs material to image

def on_set_matim(self,C):

  mat = guts.get_material(self,C.object);
  nt  = mat.node_tree;

  if self.im!=None:
    self.name=mat.name=self.im.name;

  else:
    self.name=mat.name='non';

  nt.nodes['TEXTURE'].image=self.im;

def set_texture_mapping(self,C):

  nt  = guts.get_matnodes(self,C.object);
  src = nt.nodes['TEXCOORDS'];
  dst = nt.nodes['MAPPING'];

  key = 'UV' \
    if self.mapping == 'UV' \
    else self.mapping.capitalize();

  nt.links.new(
    src.outputs[key],
    dst.inputs['Vector']

  );

# ---   *   ---   *   ---
# wrap for material slot

class DA_Material(PropertyGroup):

  name: StringProperty(default='non');

  src: PointerProperty(type=Material);

  im: PointerProperty(

    name        = 'Source',
    description = \
      'Image used to generate texture maps',

    type        = Image,
    update      = on_set_matim,

  );

  mapping: EnumProperty(

    name        = 'Mapping',

    description = \
      "Vector source for mapping node",

    items       = bl_list2enum(MAPPING_TYPES),
    default     = 'UV',

    update      = set_texture_mapping,

  );

  projection: EnumProperty(

    name        = 'Projection',

    description = \
      "Projection method used for image",

    items       = bl_list2enum(PROJECTION_TYPES),
    default     = 'FLAT',

  );

  boxblend: FloatProperty(

    name        = 'Blend',

    description = \
      "Texture blending for box projection",

    default     = 0.65,
    max         = 1.0,
    min         = 0.0,

  );

# ---   *   ---   *   ---
# makes editable prop field
# for a node input

def draw_node_input(nd,name,layout):

  layout.label(text=name+':');
  layout.prop(
    nd.inputs[name],
    'default_value',

    text='',

  );

# ---   *   ---   *   ---

def draw_matbox(self,ob,layout):

  nt=guts.get_matnodes(self,ob);

  if not nt:
    return;

  row=layout.row();
  row.label(text='TEXTURE SETTINGS');

  layout.row();

  nd=nt.nodes['TEXTURE'];

  row=layout.row();
  row.prop(self,'mapping');

  row=layout.row();
  row.prop(nd,'projection');

  if nd.projection == 'BOX':
    row=layout.row();
    row.label(text='Blend:');
    row.prop(nd,'projection_blend',text='');

  nd=nt.nodes['MAPPING'];

  row=layout.row();
  row.label(text='Offset:');
  row.prop(nd.inputs[1],'default_value',text='');

  row=layout.row();
  row.label(text='Rotation:');
  row.prop(nd.inputs[2],'default_value',text='');

  row=layout.row();
  row.label(text='Scale:');
  row.prop(nd.inputs[3],'default_value',text='');

# ---   *   ---   *   ---

  layout.separator();

  row=layout.row();
  row.label(text='MATERIAL SETTINGS');

  layout.row();

  nd=nt.nodes['MATBAKE'];

  row=layout.row();
  draw_node_input(nd,"BumpStr",row);

  layout.row();

  row=layout.row();
  draw_node_input(nd,"RoughTight",row);

  row=layout.row();
  draw_node_input(nd,"RoughBase",row);

  layout.row();

  row=layout.row();
  draw_node_input(nd,"CurvDetail",row);

  row=layout.row();
  draw_node_input(nd,"CurvEdge",row);

  layout.row();

  row=layout.row();
  draw_node_input(nd,"EmitColor",row);

  row=layout.row();
  draw_node_input(nd,"EmitTolerance",row);

  layout.row();

  row=layout.row();
  draw_node_input(nd,"MetalColor",row);

  row=layout.row();
  draw_node_input(nd,"MetalTolerance",row);

  row=layout.row();
  draw_node_input(nd,"MetalMult",row);

# ---   *   ---   *   ---
# wrap multiple materials
# on single object

register_class(DA_Material);
class DA_Material_Bake(PropertyGroup):

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

    items       = bl_list2enum(RENDER_SIZES),
    default     = '128',

  );

  render_scale: EnumProperty(

    name        = 'AA Scale',
    description = (
      "Renders bake at higher resolution "
    + "to achieve smoother result"

    ),

    items       = AA_SCALES,
    default     = 'x2',

  );

  fpath: StringProperty(
    description = "Path to output directory",
    default     = ARPATH+'/.cache/auvi/material/',

  );

  materials: CollectionProperty(
    type=DA_Material

  );

  material_i: IntProperty(default=0);

# ---   *   ---   *   ---

class DA_UL_Material(UIList):

  def draw_item(
    self,C,layout,

    ob,slot,icon,

    active_data,
    active_propname

  ):

    layout.prop(slot,'im');

# ---   *   ---   *   ---
# further GENIUS additions

class DA_OT_Material_Add(Operator):

  bl_idname      = "darkage.material_add";
  bl_label       = "Add a new material";

  bl_description = \
    "Adds a new DarkAge material to object";

  def execute(self,C):
    guts.material_nit(C.object);
    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_Material_Remove(Operator):

  bl_idname      = "darkage.material_remove";
  bl_label       = "Destroy selected material";

  bl_description = \
    "Remove selected material from object";

  def execute(self,C):
    guts.material_del(C.object);
    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_Material_Goup(Operator):

  bl_idname      = "darkage.material_goup";
  bl_label       = "Move material up";
  bl_description = "Move material up";

  def execute(self,C):

    ob = C.object;
    mb = ob.da_matbake;

    i  = mb.material_i;

    if(i>0):

      ob.active_material_index=i;
      bpy.ops.object.material_slot_move(
        direction='DOWN'

      );

      wap(mb.materials,i,i-1);
      mb.material_i-=1;

    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_Material_Godown(Operator):

  bl_idname      = "darkage.material_godown";
  bl_label       = "Move material down";
  bl_description = "Move material down";

  def execute(self,C):

    ob = C.object;
    mb = ob.da_matbake;

    i  = mb.material_i;

    if(i<len(mb.materials)-1):

      ob.active_material_index=i;
      bpy.ops.object.material_slot_move(
        direction='UP'

      );

      wap(mb.materials,i,i+1);
      mb.material_i+=1;

    return {'FINISHED'};

# ---   *   ---   *   ---
# swap one material for another

def wap(materials,dst_i,src_i):
  pass;

# ---   *   ---   *   ---
# syncs da_matbake.materials
# to material_slots of object

def matsync(ob):

  mats=[slot.mat for slot in ob.material_slots];

  for mat in mats:
    pass;

# ---   *   ---   *   ---

class DA_OT_Matbake_Run(Operator):

  bl_idname      = "darkage.matbake_run";
  bl_label       = "Bake material to JOJ";

  bl_description = \
    "Packs material layers into JOJ file";

  def execute(self,C):

    ob=C.active_object;
    me=guts.run(ob);

    if len(me):
      self.report({'INFO'},me);

    return {'FINISHED'};

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

    );

# ---   *   ---   *   ---

  def draw(self,context):

    layout = self.layout;

    ob = context.active_object;
    mb = ob.da_matbake;

# ---   *   ---   *   ---

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
    row.prop(mb,"fpath");

    row=layout.row();
    row.operator(
      'darkage.matbake_run',

      text='BAKE',
      icon='MATERIAL'

    );

    row=layout.row();
    row.separator();

# ---   *   ---   *   ---

    row=layout.row();

    row.template_list(
      'DA_UL_Material','',

      mb,'materials',
      mb,'material_i',

    );

    col=row.column();

    col.operator(
      'darkage.material_add',
      text='',
      icon='ADD'

    );

    col.operator(
      'darkage.material_remove',
      text='',
      icon='REMOVE'

    );

    col.operator(
      'darkage.material_goup',
      text='',
      icon='TRIA_UP'

    );

    col.operator(
      'darkage.material_godown',
      text='',
      icon='TRIA_DOWN'

    );

    layout.separator();

    if len(mb.materials):

      box=layout.box();
      box.row();

      draw_matbox(
        mb.materials[mb.material_i],
        ob,box

      );

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_Material_Bake);
  register_class(DA_OT_Matbake_Run);

  register_class(DA_UL_Material);

  register_class(DA_OT_Material_Add);
  register_class(DA_OT_Material_Remove);
  register_class(DA_OT_Material_Godown);
  register_class(DA_OT_Material_Goup);

  register_class(DA_Material_Panel);

  Object.da_matbake=PointerProperty(
    type=DA_Material_Bake

  );

def unregister():

  del Object.da_matbake;

  unregister_class(DA_Material_Bake);
  unregister_class(DA_OT_Matbake_Run);
  unregister_class(DA_Material_Panel);

  unregister_class(DA_UL_Material);

  unregister_class(DA_OT_Material_Add);
  unregister_class(DA_OT_Material_Remove);
  unregister_class(DA_OT_Material_Godown);
  unregister_class(DA_OT_Material_Goup);

  unregister_class(DA_Material);

# ---   *   ---   *   ---
