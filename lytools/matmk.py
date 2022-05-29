# ---   *   ---   *   ---
# MATMK
# Material-making utils
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,
# ---   *   ---   *   ---

import bpy, os;

from bpy.types import (
  Scene,
  Image,
  PropertyGroup,
  Panel,
  Operator,

  Object as blObject,
  Material as blMaterial

);

from bpy.utils import (
  register_class,
  unregister_class

);

from bpy.props import (

  StringProperty,
  EnumProperty,
  FloatProperty,
  FloatVectorProperty,
  IntProperty,
  PointerProperty

);

from . import(

  walk,
  DROOT

);

# ---   *   ---   *   ---
# getters/shorthands to circumvent API verbosity

def get_tree(ob:blObject,matid:int=0):
  material:BlMaterial=ob.data.materials[matid];
  return material.node_tree;

def get_node(ob:blObject,name:str,matid:int=0):
  material:BlMaterial=ob.data.materials[matid];
  return material.node_tree.nodes[name];

# ---   *   ---   *   ---

def get_bake_canvas():
  return bpy.data.objects["Canvas"];

def get_bake_node(name):
  return get_node(
    get_bake_canvas(),
    name,0

  );

def get_bake_links():
  return get_tree(get_bake_canvas(),0).links;

# ---   *   ---   *   ---

def sel_bake_node(name):
  nodes=get_tree(get_bake_canvas(),0);
  nodes.active=nodes[name];

#   ---     ---     ---     ---     ---

def get_bake_folder(self, context):

#  if not len(DROOT):
#    return [('','','')];

  w=walk(DROOT);

  print(w);

  shit=[

    tuple([s,s.capitalize(),''])
    for s in w

  ];

  print(shit);

  return [

    tuple([s,s.capitalize(),''])
    for s in w

  ];

def get_bake_subfolder(self, context):

  if(not len(context.scene.lytools.bake_folder)):
    return [('','','')];

  w=walk(
    context.scene.lytools.bake_folder,
    '([^t]|t[^e]|te[^x]|tex[^t]|text[^u])'

  );

  return [

    tuple([s,s.capitalize(),''])
    for s in w

  ];

# ---   *   ---   *   ---

def update_image_paths(self,context):

  node=get_bake_node("BAKE_FROM");
  lyt=context.scene.lytools;

  node.image.filepath=(
    lyt.bake_subfolder
    +'albedo.png'

  );

  rtpath=lyt.bake_subfolder[:-1];
  if os.path.exists(rtpath+".lytx"):
    load_lytx(lyt);

  bpy.ops.file.make_paths_relative();

#   ---     ---     ---     ---     ---

def update_normal(self, context):

  node=get_bake_node("NBAKE_SETTINGS");
  lyt=context.scene.lytools;

  for i in range(4):
    node.inputs[1+i].default_value=(
      getattr(lyt, f"bkr_nsng{i}")

    );

  node=get_bake_node("ADDROUGH");
  node.inputs[1].default_value=lyt.roughness_mod;

  node=get_bake_node("RMASK");
  node.color_ramp.elements[1].position=lyt.rmask;

# ---   *   ---   *   ---

def set_bake_size(self, context):

  lyt=context.scene.lytools;
  context.scene.render.resolution_x=(
    lyt.bkr_size*lyt.bkr_res

  );

  context.scene.render.resolution_y=(
    lyt.bkr_size*lyt.bkr_res

  );

#   ---     ---     ---     ---     ---

def update_metallic(self, context):

  lyt=context.scene.lytools;
  node=get_bake_node("METMASK");

  node.inputs[1].default_value=lyt.metallic_color;
  node.inputs[2].default_value=lyt.metallic_base;
  node.inputs[3].default_value=(
    lyt.metallic_tolerance

  );

def update_emit(self, context):

  lyt=context.scene.lytools;
  node=get_bake_node("EMITMASK");

  node.inputs[1].default_value=lyt.emit_color;
  node.inputs[2].default_value=lyt.emit_base;
  node.inputs[3].default_value=lyt.emit_tolerance;

#   ---     ---     ---     ---     ---

viewModes = [

  ("normal", "Normal", "Show calculated normal map"),
  ("albedo", "Albedo", "Show base color map"       ),
  ("height", "Height", "Show height map"           ),
  ("rmask",  "RMASK",  "Show rawmask"              ),
  ("rough",  "Rough",  "Show roughness map"        ),
  ("metal",  "Metal",  "Show metalness mask"       ),
  ("emit",   "Emit",   "Show emission mask"        )

];

viewModes_nd = {

  "normal": "NBAKE_SETTINGS",
  "albedo": "BAKE_FROM",
  "height": "NBAKE_SETTINGS",
  "rmask" : "RMASK",
  "rough" : "BKROUGH",
  "metal" : "METMASK",
  "emit"  : "EMITMASK"

}

def update_view(self, context):

  lyt=context.scene.lytools;
  links=get_bake_links();

  node=get_bake_node(viewModes_nd[lyt.bkr_view]);
  out_node=get_bake_node("REOUT");

  out_idex=2 if lyt.bkr_view=="height" else 0;

  links.new(
    node.outputs[out_idex],
    out_node.inputs[0]

  );

# ---   *   ---   *   ---

class LYT_SceneSettings(PropertyGroup):

  bkr_view:EnumProperty (

    items       = viewModes,
    default     = "normal",
    update      = update_view,

    name        = "Cathegory",
    description = "Root folder to pick from"

  );

  bake_folder:EnumProperty (

    items       = get_bake_folder,
    update      = update_image_paths,

    name        = "Cathegory",
    description = "Root folder to pick from"

  );

  bake_subfolder:EnumProperty (

    items       = get_bake_subfolder,
    update      = update_image_paths,

    name        = "Material",
    description = "Material folder to work with"

  );

  rmask:FloatProperty (

    name        = "Rawmask tolerance",

    description = "Adjusts grey levels of the "\
                  "initial rawmask",

    default     = 0.338776,
    min         = 0.000001,
    max         = 1.0,

    update      = update_normal

  );

  height:FloatProperty (

    name        = "Height",

    description = "Middle point for the "\
                  " generated heightmap",

    default     = 0.5,
    min         = 0,
    max         = 1.0,

    update      = update_normal

  );

  roughness:FloatProperty (

    name        = "Treshold",

    description = "Middle point for the "\
                  "roughness factor",

    default     = 0.5,
    min         = 0,
    max         = 1.0,

    update      = update_normal

  );

  softness:FloatProperty (

    name        = "Softness",

    description = "Softens the resulting "\
                  "normal & rough values",

    default     = 0.0,
    min         = 0,
    max         = 2.0,

    update      = update_normal

  );

  normal_mod:FloatProperty (

    name        = "Intensity",
    description = "Makes resulting normal sharper",

    default     = 0.25,
    min         = -2.0,
    max         = 2.0,

    update      = update_normal

  );

  roughness_mod:FloatProperty (

    name        = "Rough modifier",

    description = "Adds to roughness post "\
                  "normal calculations",

    default     = 0.0,
    min         = -1.0,
    max         = 4.0,

    update      = update_normal

  );

  bkr_size:IntProperty (

    name        = "Size",

    description = "Final bake size, after "\
                  "de-scaling",

    default     = 256,
    min         = 2,
    max         = 8192,

    update      = set_bake_size

  );

  bkr_res:IntProperty (

    name        = "Scale",

    description = "Resolution multiplier, "\
                  "renders at larger size "\
                  "then scales down",

    default     = 1,
    min         = 1,
    max         = 16,

    update      = set_bake_size

  );

  metallic_color:FloatVectorProperty (

    name        = "Metal color",
    description = "Color for metallic mask",
    subtype     = 'COLOR',

    size        = 4,
    default     = [1.0,1.0,1.0,1.0],
    update      = update_metallic

  );

  metallic_base:FloatProperty (

    name        = "Metal base",
    description = "Multiplier for metallic",

    default     = 0.0,
    min         = 0.0,
    max         = 2.0,

    update      = update_metallic

  );

  metallic_tolerance:FloatProperty (

    name        = "Metal tolerance",

    description = "Makes non-metallic "\
                  "colors more metallic",

    default     = 0.0,
    min         = 0.0,
    max         = 2.0,

    update      = update_metallic

  );

  emit_color:FloatVectorProperty (

    name        = "Emit color",
    description = "Color for emission mask",
    subtype     = 'COLOR',

    size        = 4,
    default     = [1.0,1.0,1.0,1.0],
    update      = update_emit

  );

  emit_base:FloatProperty (

    name        = "Emit base",
    description = "Multiplier for emission",

    default     = 0.0,
    min         = 0.0,
    max         = 2.0,

    update      = update_emit

  );

  emit_tolerance:FloatProperty (

    name        = "Emit tolerance",
    description = "Makes non-emissive "\
                  "colors more emissive",

    default     = 0.0,
    min         = 0.0,
    max         = 2.0,

    update      = update_emit

  );

  fresnel:FloatProperty (

    name        = "Base Fresnel",
    description = "Base fresnel value",

    default     = 0.050,
    min         = 0.050,
    max         = 1.000

  );

#   ---     ---     ---     ---     ---

LYT_ATTRS=([

  "rmask",

  "height",
  "roughness",
  "softness",
  "normal_mod",
  "roughness_mod",

  "bkr_size",
  "bkr_res",

  "metallic_color",
  "metallic_base",
  "metallic_tolerance",

  "emit_color",
  "emit_base",
  "emit_tolerance",

  "fresnel"

]);

# ---   *   ---   *   ---

def save_lytx(lyt):

  d={};
  rtpath=lyt.bake_subfolder[:-1];

  for k in LYT_ATTRS:
    if k == "metallic_color":
      d[k]=lyt.metallic_color[:];
    elif k == "emit_color":
      d[k]=lyt.emit_color[:];

    else:
      d[k]=getattr(lyt, k);

  path=rtpath+".lytx"; d=(str(d)).replace(" ", "");
  with open(path, "w+") as file: file.write(d);

# ---   *   ---   *   ---

def load_lytx(lyt):
  s=""; path=lyt.bake_subfolder[:-1]+".lytx";
  with open(path, "r") as file:
    s=file.read();

  d=eval(s);
  for k in LYT_ATTRS:
    if k not in d:
      continue;

    if k == "metallic_color":
      lyt.metallic_color[:]=d[k][:];
    elif k == "emit_color":
      lyt.emit_color[:]=d[k][:];

    else:
      setattr(lyt, k, d[k]);

#   ---     ---     ---     ---     ---

class LYT_OT_SVBUTT(Operator):

  bl_idname      = "lytbkr.svlytx";

  bl_label       = "Saves settings for this "\
                   "material";

  bl_description = "Save current settings to "\
                   "a file associated with this "\
                   "material";

# ---   *   ---   *   ---

  def execute(self, context):

    lyt=context.scene.lytools;
    save_lytx(lyt);

    self.report(

      {'INFO'}, "Material settings saved to "\
      f"<{lyt.bake_subfolder[:-1]+'.lytx'}>"

    );return {'FINISHED'};

# ---   *   ---   *   ---

class LYT_OT_LDBUTT(Operator):

  bl_idname      = "lytbkr.ldlytx";
  bl_label       = "Loads settings for this "\
                   "material";

  bl_description = "Load settings from a file "\
                   "associated with this material";

# ---   *   ---   *   ---

  def execute(self, context):

    lyt=context.scene.lytools;
    path=lyt.bake_subfolder[:-1]+".lytx";

    if os.path.exists(path):
      load_lytx(lyt);

      self.report(
        {'INFO'}, f"Loaded <{path}>"

      );

    else:

      self.report(

        {'WARNING'},f"File <{path}> not found!"

      );

    return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_OT_BKOGL(Operator):

  bl_idname      = "lytbkr.bkogl";
  bl_label       = "Executes OpenGL bake";

  bl_description = "OpenGL renders the canvas "\
                   "with current settings";

#   ---     ---     ---     ---     ---

  def execute(self, context):

    lyt=context.scene.lytools;
    ob=get_bake_canvas();

    ob.select=1;
    context.scene.objects.active=ob;

    usystem=context.user_preferences.system;
    umm_old=usystem.use_mipmaps;

    links=get_bake_links();

    node=get_bake_node("NBAKE_SETTINGS");
    out_node=get_bake_node("REOUT");

    links.new(node.outputs[0], out_node.inputs[0]);

    mix_node=get_bake_node("OUTMIX");
    links.new(node.outputs[2], mix_node.inputs[0]);

    node=get_bake_node("BAKE_FROM");
    rtpath=lyt.bake_subfolder;

    save_lytx(lyt);
    usystem.use_mipmaps=1;

    context.scene.camera=(
      context.scene.objects["CANVAS_CAM"]

    );

    for area in bpy.context.screen.areas:
      if area.type == 'VIEW_3D':

        area.spaces[0].\
        region_3d.\
        view_perspective='CAMERA';

        break;

#   ---     ---     ---     ---     ---
# render normal

    context.scene.render.engine='BLENDER_EEVEE';

    print("Baking normal... ");

    context.scene.render.\
    image_settings.file_format='PNG';

    bpy.ops.render.opengl();

    path=rtpath+"normal.png";
    bpy.data.images["Render Result"].\
      save_render(path);

    for link in mix_node.inputs[0].links:
      links.remove(link);

#   ---     ---     ---     ---     ---
# set ao as out then bake

    node=get_bake_node("NBAKE_FROM");
    node.image.source='FILE';

    node.image.filepath=path;

    context.scene.render.engine='CYCLES';
    context.scene.cycles.bake_type='EMIT';

    print("Baking AO... ");
    bpy.ops.render.opengl();

    path=rtpath+"tmp.png";
    bpy.data.images["Render Result"].\
      save_render(path);

    node=get_bake_node("AO_BAKETO");
    node.image.source='FILE';
    node.image.filepath=path;

#   ---     ---     ---     ---     ---
# combine ao, rough, metalness & emit into orm+e

    node=get_bake_node("BKORM");

    links.new(
      node.outputs[0],
      out_node.inputs[0]

    );

    links.new(
      get_bake_node("EMITMASK").outputs[0],
      mix_node.inputs[0]

    );

    print("Combining ORM map... ");
    path=rtpath+"orm.png";

    bpy.ops.render.opengl();
    bpy.data.images["Render Result"].\
      save_render(path);

    for link in mix_node.inputs[0].links:
      links.remove(link);

#   ---     ---     ---     ---     ---
# set curv as out then bake

    node=get_bake_node("SCURVY");

    links.new(
      node.outputs[0],
      out_node.inputs[0]

    );

    mix_node.inputs[0].default_value=1.0-lyt.fresnel;
    print("Baking curvature... ");

    path=rtpath+"curv.png";

    bpy.ops.render.opengl();
    bpy.data.images["Render Result"].\
      save_render(path);

    mix_node.inputs[0].default_value=1.0;

#   ---     ---     ---     ---     ---

    print("Resizing... ");

    node=get_bake_node("NBAKE_FROM");

    node.image.scale(
      lyt.bkr_size,
      lyt.bkr_size

    );node.image.save();

    node.image.filepath=rtpath+"orm.png";

    node.image.scale(
      lyt.bkr_size,
      lyt.bkr_size

    );node.image.save();

    node.image.filepath=rtpath+"curv.png";

    node.image.scale(
      lyt.bkr_size,
      lyt.bkr_size

    );node.image.save();

    print("Cleaning up temp files... ");

    node=get_bake_node("AO_BAKETO");
    path=node.image.filepath;

    node.image.source='GENERATED';

    os.system("@del %s"%path);

    print("Done!\n");

    usystem.use_mipmaps=umm_old;

    update_view(self, context);
    return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_PT_renderPanel(Panel):

  bl_label       = 'LYT BAKER';
  bl_idname      = 'LYT_PT_renderPanel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'render';
  bl_category    = 'LYT';

#   ---     ---     ---     ---     ---

  @classmethod
  def poll(cls, context):
    return context.scene is not None;

  def draw(self, context):
    layout = self.layout;

    scene  = context.scene;
    lyt    = scene.lytools;

    row    = layout.row(

      align=1

    );

    row.prop_enum(lyt, "bkr_view", "normal");
    row.prop_enum(lyt, "bkr_view", "albedo");
    row.prop_enum(lyt, "bkr_view", "height");
    row.prop_enum(lyt, "bkr_view", "rmask" );
    row.prop_enum(lyt, "bkr_view", "rough" );
    row.prop_enum(lyt, "bkr_view", "metal" );
    row.prop_enum(lyt, "bkr_view", "emit"  );

# ---   *   ---   *   ---

    layout.separator(); row=layout.row();
    row.prop(lyt, "bake_folder"); row=layout.row();

    if lyt.bake_folder:
      row.prop(lyt, "bake_subfolder");

      if lyt.bake_subfolder:

        layout.separator();
        row=layout.row(

          align=1

        );

# ---   *   ---   *   ---

        row.operator(

          "lytbkr.svlytx",

          text = "SAVE",
          icon = "FILE_TICK"

        );

        row.operator(

          "lytbkr.ldlytx",

          text = "LOAD",
          icon = "FILE_REFRESH"

        );

# ---   *   ---   *   ---

        layout.separator();
        row=layout.row();

        row.label(

          text="Normal/Rough settings:"

        );

        layout.separator();
        normal_attrs:list=[

          'rmask',
          'height',
          'roughness',
          'softness',
          'normal_mod',
          'roughness_mod',
          'fresnel'

        ];

        for attr in normal_attrs:
          row=layout.row();
          row.prop(lyt, attr);

# ---   *   ---   *   ---

        layout.separator();
        row=layout.row();

        row.label(

          text="Metalness settings:"

        );

        metallic_attrs:list=[
          'metallic_base',
          'metallic_tolerance',
          'metallic_color',

        ];

        for attr in metallic_attrs:
          row=layout.row();
          row.prop(lyt, attr);

# ---   *   ---   *   ---

        layout.separator();
        row=layout.row();

        row.label(

          text="Emission settings:"

        );

        emit_attrs:list=[
          'emit_base',
          'emit_tolerance',
          'emit_color',

        ];

        for attr in emit_attrs:
          row=layout.row();
          row.prop(lyt, attr);

# ---   *   ---   *   ---

        layout.separator();

        row=layout.row();
        row.prop(lyt, "bkr_size");
        row.prop(lyt, "bkr_res");

        row=layout.row();

        row.operator(

          "lytbkr.bkogl",

          text="BAKE",
          icon="RENDER_STILL"

        );


#   ---     ---     ---     ---     ---

def register():
  register_class(LYT_SceneSettings);
  register_class(LYT_OT_BKOGL);
  register_class(LYT_OT_SVBUTT);
  register_class(LYT_OT_LDBUTT);
  register_class(LYT_PT_renderPanel);

  Scene.lytools=PointerProperty(
    type=LYT_SceneSettings

  );

def unregister():

  del Scene.lytools;

  unregister_class(LYT_PT_renderPanel);
  unregister_class(LYT_OT_LDBUTT);
  unregister_class(LYT_OT_SVBUTT);
  unregister_class(LYT_OT_BKOGL);
  unregister_class(LYT_SceneSettings);
