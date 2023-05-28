#!/usr/bin/python
# ---   *   ---   *   ---
# MATERIAL
# Wrappers for bpy type
# of the same name
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
from ..guts import N3;

from arcana.Mod import bl_kls_merge;
from arcana.Tools import bl_list2enum;

from bpy.types import (

  ShaderNodeTexCoord,
  ShaderNodeMapping,
  ShaderNodeTexImage,
  ShaderNodeGroup,

  ShaderNodeOutputMaterial,

);

# ---   *   ---   *   ---
# NOTE:
#
#  * DA_Material wraps material slot
#  * DA_Materials wraps object materials

# ---   *   ---   *   ---
# info

class DA_Material(PropertyGroup):

  VERSION = 'v2.00.1';
  AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# F:ROM
#
# consts have been converted
# into static methods just to
# let blender's backward API
# utilize classes correctly
#
# what's the deal?
#
# blender can see the consts
# within the class before/during
# method/attr merging...
#
# ... but they are all destroyed
# after registration!
#
# what a feature! EHIB

# ---   *   ---   *   ---
# switches for texcords

  @staticmethod
  def MAPPING_TYPES():

    return {

      'Generated',
      'Normal',
      'UV',

    };

# ---   *   ---   *   ---
# switches for texture projection

  @staticmethod
  def PROJECTION_TYPES():

    return [
      'BOX',
      'FLAT',

    ];

# ---   *   ---   *   ---
# [key=>node_type] list for
# matbake group, used to
# validate nodetree

  @staticmethod
  def MB_NODES():

    return {

      'TEXCOORDS': ShaderNodeTexCoord,
      'MAPPING'  : ShaderNodeMapping,
      'TEXTURE'  : ShaderNodeTexImage,

      'MATBAKE'  : ShaderNodeGroup,
      'OUTPUT'   : ShaderNodeOutputMaterial,

      'BAKETO_COLOR': ShaderNodeTexImage,
      'BAKETO_ALPHA': ShaderNodeTexImage,

    };

# ---   *   ---   *   ---
# keylist for inputs of
# matbake nodegroup

  @staticmethod
  def MB_INPUTS():

    return [

      "BumpStr",
      "RoughTight","RoughBase",

      "CurvDetail","CurvEdge",
      "EmitColor","EmitTolerance",

      "MetalColor","MetalTolerance",
      "MetalMult",

    ];

# ---   *   ---   *   ---
# attrlist used to save
# and load material config

  @staticmethod
  def STATE_DICT():

    return {

      'self':['mapping','im'],

      'TEXTURE':[
        'projection',
        'projection_blend',

      ],

      'MAPPING':[

        'inputs[1].default_value[:]',
        'inputs[2].default_value[:]',
        'inputs[3].default_value[:]',

      ],

      'MATBAKE':MB_INPUTS(),

    };

# ---   *   ---   *   ---
# creates new

  def nit(self,ob):

    self.ob  = ob;
    self.ref = self.get_ref();

    N3.load_material(self.ref,'non');

# ---   *   ---   *   ---
# checks nodetree is valid

  def validate(self):

    out   = "";
    nodes = self.get_nodes();

    for name,type in DA_Material.MB_NODES().items():

      if not node_type_name_chk(nodes,name,type):

        st=self.save_state();

        try:
          self.nit(self.ob);
          out="Material regenerated";

          self.load_state(st);

        except:
          out="Material regeneration failed";


    return out;

# ---   *   ---   *   ---
# get blender material
# assoc with DA_Material

  def get_ref(self):

    if self.ref == None:

      dama = self.ob.da_materials;
      i    = dama.iof(self);

      self.ref=(
        self.ob.material_slots[i].material

      );

    return self.ref;

# ---   *   ---   *   ---
# get material node tree
# assoc with selected DA_Material

  def get_nodetree(self):

    if self.ref==None:
      return None;

    return self.ref.node_tree;

# ---   *   ---   *   ---
# ^get nodes of nodetree

  def get_nodes(self):

    nt=self.get_nodetree();

    if nt==None:
      return None;

    return nt.nodes;

# ---   *   ---   *   ---
# swaps current texture
# for selected image

  def set_image(self,C):

    nodes=self.get_nodes();

    if self.im != None:
      name=self.im.name;

    else:
      name='non';

    self.ref.name = f"{self.ob.name}::{name}";
    self.name     = name;

    nodes['TEXTURE'].image=self.im;

# ---   *   ---   *   ---
# sets which kind of mapping
# a given texture will use

  def set_mapping(self,C):

    nt  = self.get_nodetree();

    src = nt.nodes['TEXCOORDS'];
    dst = nt.nodes['MAPPING'];

    # ensure we have key right
    key=(

      'UV'

      if self.mapping == 'UV'
      else self.mapping.capitalize()

    );

    # ^connect node sockets
    nt.links.new(
      src.outputs[key],
      dst.inputs['Vector']

    );

# ---   *   ---   *   ---
# make backup of settings

  def save_state(self):

    nodes = self.get_nodes();
    out   = [];

    d     = DA_Material.STATE_DICT();

    # TODO: replace eval/exec by
    #       "layered" [get/set]attr

    # own props
    for attr in d['self']:
      out.append(eval(f"self.{attr}"));

    # data from common nodes
    for key in ['TEXTURE','MAPPING']:

      nd=nodes[key];

      for attr in d[key]:
        out.append(eval(f"nd.{attr}"));

    # data from matbake group
    for key in d['MATBAKE']:
      out.append(self.get_mb_input(
        nodes['MATBAKE'],
        key

      ));

    return out;

# ---   *   ---   *   ---
# restore

  def load_state(self,src):

    i     = 0;
    nodes = self.get_nodes();

    # see: TODO on previous F

    # own props
    for attr in d['self']:
      exec(f"self.{attr}=src[i];");
      i+=1;

    # data from common nodes
    for key in ['TEXTURE','MAPPING']:

      nd=nodes[key];

      for attr in d[key]:
        exec(f"nd.{attr}=src[i];");
        i+=1;

    # data from matbake group
    for key in d['MATBAKE']:
      self.set_mb_input(
        nodes['MATBAKE'],
        key,

        src[i]

      );

      i+=1;

# ---   *   ---   *   ---
# gets matbake group node input

  def get_mb_input(nd,key):

    value=nd.inputs[key].default_value;

    if(

       isinstance(value,bpy.types.bpy_prop_array)
    or isinstance(value,Vector)

    ):

      return value[:];

    return value;

# ---   *   ---   *   ---
# ^set

  def set_mb_input(self,nd,key,value):

    if isinstance(value,list):
      nd.inputs[key].default_value[:]=value[:];

    else:
      ndi.inputs[key].default_value=value;

# ---   *   ---   *   ---
# ^attr def

class DA_Material(PropertyGroup):

  name: StringProperty(default='non');

  ref: PointerProperty(type=Material);
  ob: PointerProperty(type=Object);

  im: PointerProperty(

    name        = 'Source',
    description = \
      'Image used to generate texture maps',

    type        = Image,
    update      = DA_Material.set_image,

  );

  mapping: EnumProperty(

    name        = 'Mapping',

    description = \
      "Vector source for mapping node",

    items       = bl_list2enum(
      DA_Material.MAPPING_TYPES()

    ),

    default     = 'UV',

    update      = DA_Material.set_mapping,

  );

  projection: EnumProperty(

    name        = 'Projection',

    description = \
      "Projection method used for image",

    items       = bl_list2enum(
      DA_Material.PROJECTION_TYPES()

    ),

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

  # join with previous def
  exec(bl_kls_merge("DA_Material"));

# ---   *   ---   *   ---
# prematurely registered so
# the other class can find it

register_class(DA_Material);

# ---   *   ---   *   ---
# ob.material_slots is an array
# that (apparently) lacks a (good)
# method for removing elements
#
# only two ways i could find:
#   * clear ALL materials
#   * use bpy.ops (ughh!)
#
# you see how i bring up
# GENIUS design throughout
# this entire codebase?
#
# this crap is why
#
# no, you can't just have a ref
# to an object and pop from an array!
#
# you have to SELECT the object
# and run an operator, as if this
# was a UI and not a wall of code!
#
# EHIB, just EHIB!

def bl_material_remove(ob,idex):

  sel=get_selection();
  select_all(ob);

  ob.active_material_index=idex;
  bpy.data.materials.remove(ob.active_material);
  bpy.ops.object.material_slot_remove();

  reselect(sel);

# ---   *   ---   *   ---
# ^will add a new material
# AND a new slot if needed!
#
# just whoa, such expertise!
# you can push, but you can't pop!
#
# absolutely revolutionary,
# hats off
#
# EHIB

def bl_material_add(ob,name='Material'):

  out=bpy.data.materials.new(name);
  ob.data.materials.append(out);

  ob.active_material_index=len(
    ob.material_slots

  )-1;

  ob.active_material=out;

  return out;

# ---   *   ---   *   ---
# ^clears all

def bl_materials_clear(ob):
  ob.data.materials.clear();

# ---   *   ---   *   ---
# wrap multiple materials
# on single object
#
# method def

class DA_Materials(PropertyGroup):

# ---   *   ---   *   ---
# finds object holding prop

  def get_ref(self):

    if self.ref == None:

      for ob in bpy.data.objects:
        if ob.da_materials == self:
          self.ref=ob;
          break;

    return self.ref;

# ---   *   ---   *   ---
# swap one material for another

  def wap(self,dst_i,src_i):

    tmp=self.data[dst_i].copy();

    self.data[dst_i]=self.data[src_i];
    self.data[src_i]=tmp;

# ---   *   ---   *   ---
# gets currently selected
# material in data

  def deref(self):
    return self.data[self.ptr];

# ---   *   ---   *   ---
# get index of DA_Material
# within data

  def iof(self,m):

    if m in self.data[:]:
      return self.data[:].index(m);

    return None;

# ---   *   ---   *   ---
# add new item

  def push(self):

    ob=self.get_ref();
    bl_material_add(ob,'non');

    m=self.data.add();
    m.nit(ob);

# ---   *   ---   *   ---
# ^removes

  def pop(self):

    ob=self.get_ref();
    bl_material_remove(ob,self.ptr);

    self.data.remove(self.ptr);

# ---   *   ---   *   ---
# ^attr def

class DA_Materials(PropertyGroup):

  ref: PointerProperty(type=Object);

  data: CollectionProperty(
    type=DA_Material

  );

  ptr: IntProperty(default=0);

  # join with previous def
  exec(bl_kls_merge("DA_Materials"));

# ---   *   ---   *   ---
# draws a list from a collection
# of DA_Material

class DA_UL_Materials(UIList):

  def draw_item(
    self,C,layout,

    ob,slot,icon,

    active_data,
    active_propname

  ):

    layout.prop(slot,'im');

# ---   *   ---   *   ---
# further GENIUS additions

class DA_OT_Materials_Add(Operator):

  bl_idname      = "darkage.materials_add";
  bl_label       = "Add a new material";

  bl_description = \
    "Adds a new DarkAge material to object";

  def execute(self,C):

    ob   = C.object;
    dama = ob.da_materials;

    dama.push();

    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_Materials_Remove(Operator):

  bl_idname      = "darkage.materials_remove";
  bl_label       = "Destroy selected material";

  bl_description = \
    "Remove selected material from object";

  def execute(self,C):

    ob   = C.object;
    dama = ob.da_materials;

    dama.pop();

    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_Materials_Goup(Operator):

  bl_idname      = "darkage.materials_goup";
  bl_label       = "Move material up";
  bl_description = "Move material up";

  def execute(self,C):

    ob   = C.object;
    dama = ob.da_materials;

    i    = dama.ptr;

    if(i > 0):

      ob.active_material_index=i;
      bpy.ops.object.material_slot_move(
        direction='DOWN'

      );

      dama.wap(i,i-1);
      dama.ptr-=1;

    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_OT_Materials_Godown(Operator):

  bl_idname      = "darkage.materials_godown";
  bl_label       = "Move material down";
  bl_description = "Move material down";

  def execute(self,C):

    ob   = C.object;
    dama = ob.da_materials;

    i    = dama.ptr;

    if(i < len(dama.data)-1):

      ob.active_material_index=i;
      bpy.ops.object.material_slot_move(
        direction='UP'

      );

      dama.wap(i,i+1);
      dama.ptr+=1;

    return {'FINISHED'};

# ---   *   ---   *   ---
# adds material baking ctl
# to scene tab

class DA_Materials_Panel(Panel):

  bl_label       = 'Materials';
  bl_idname      = 'DA_PT_Materials_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'object';
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

    ob   = C.active_object;
    dama = ob.da_materials;

    self.draw_matbox_sel(C);

    if len(dama.data):
      self.draw_matbox(C);

# ---   *   ---   *   ---
# shows list/list controls for
# DA_Material in object

  def draw_matbox_sel(self,C):

    layout = self.layout;

    ob   = C.active_object;
    dama = ob.da_materials;

    # list DA_Material in collection
    row=layout.row();
    row.template_list(
      'DA_UL_Materials','',

      dama,'data',
      dama,'ptr',

    );

    # operator/text/icon
    ctl=[

      'darkage.materials_add'   ,'','ADD',
      'darkage.materials_remove','','REMOVE',
      'darkage.materials_goup'  ,'','TRIA_UP',
      'darkage.materials_godown','','TRIA_DOWN',

    ];

    # ^draw each
    col=row.column();
    for i in range(0,len(ctl),3):
      name,text,icon=ctl[i:i+3];
      col.operator(name,text=text,icon=icon);

    layout.separator();

# ---   *   ---   *   ---
# shows material controls

  def draw_matbox(self,C):

    layout = self.layout;

    ob   = C.active_object;
    dama = ob.da_materials;

    box=layout.box();
    box.row();

    nodes=dama.deref().get_nodes();

    if not nodes:
      return;

    self.draw_tex_node(C,box,nodes);
    self.draw_map_node(box,nodes);
    self.draw_mb_node(box,nodes);

# ---   *   ---   *   ---
# shows controls of image texture node

  def draw_tex_node(self,C,layout,nodes):

    ob   = C.active_object;
    dama = ob.da_materials;

    row=layout.row();
    row.label(text='TEXTURE SETTINGS');

    layout.row();

    nd=nodes['TEXTURE'];

    row=layout.row();
    row.prop(dama.deref(),'mapping');

    row=layout.row();
    row.prop(nd,'projection');

    if nd.projection == 'BOX':
      row=layout.row();
      row.label(text='Blend:');
      row.prop(nd,'projection_blend',text='');

# ---   *   ---   *   ---
# shows controls of mapping node

  def draw_map_node(self,layout,nodes):

    nd=nodes['MAPPING'];

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
# shows controls of matbake group

  def draw_mb_node(self,layout,nodes):

    row=layout.row();
    row.label(text='MATERIAL SETTINGS');

    layout.row();

    nd=nodes['MATBAKE'];

    for key in DA_Material.MB_INPUTS():
      row=layout.row();
      self.draw_node_input(nd,key,row);

    self.layout.separator();

# ---   *   ---   *   ---
# ^makes editable prop field
# for a node group input

  def draw_node_input(self,nd,name,layout):

    layout.label(text=name+':');
    layout.prop(
      nd.inputs[name],
      'default_value',

      text='',

    );

# ---   *   ---   *   ---
# create register/unregister

exec(DA_iface_module("""

$:rclass;>

  DA_Materials

  DA_OT_Materials_Add
  DA_OT_Materials_Remove
  DA_OT_Materials_Godown
  DA_OT_Materials_Goup

  DA_UL_Materials
  DA_Materials_Panel

$:uclass;>
  DA_Material

$:bind;>
  Material.da_material  : DA_Material
  Object.da_materials   : DA_Materials

"""));

# ---   *   ---   *   ---
