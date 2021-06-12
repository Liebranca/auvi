import bpy, os;

from bpy.types import Scene, Image, PropertyGroup, Panel, Operator;
from bpy.utils import register_class, unregister_class;

#   ---     ---     ---     ---     ---

from bpy.props import (

    StringProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty

);

#   ---     ---     ---     ---     ---

DROOT="\\".join(__file__.split("\\")[:-2])+'\\data';

def GTBKR_NODE(name):
    return bpy.data.objects["Canvas"].data.materials[0].node_tree.nodes[name];

def SLBKR_NODE(name):
    nodes=bpy.data.objects["Canvas"].data.materials[0].node_tree.nodes;
    nodes.active=nodes[name];

def GTBKR_LINKS():
    return bpy.data.objects["Canvas"].data.materials[0].node_tree.links;

#   ---     ---     ---     ---     ---

def GTBKR_F0(self, context):
    w=list(os.walk(DROOT));
    return [tuple([w[0][0]+'\\'+s, s.capitalize(), '']) for s in w[0][1]];

def GTBKR_F1(self, context):
    w=list(os.walk(context.scene.lytools.bkr_f0));
    w=[pis for pis in w if "textures" in pis[1] or "textures" in pis[0]]; l=[];

    for pis in w:
        for s in pis[1]:
            if s!="textures":
                l.append( tuple( [pis[0]+'\\'+s+'\\'+s+'_', s.capitalize(), '' ]) );

    return l;

def UPIMPATH(self, context):
    node=GTBKR_NODE("BAKE_FROM"); lyt=context.scene.lytools;
    node.image.filepath=lyt.bkr_f1+'albedo.png';

#   ---     ---     ---     ---     ---

def STNSNG(self, context):
    node=GTBKR_NODE("NBAKE_SETTINGS"); lyt=context.scene.lytools;
    for i in range(4):
        node.inputs[1+i].default_value=getattr(lyt, f"bkr_nsng{i}");

def STBKSIZE(self, context):
    lyt=context.scene.lytools;
    context.scene.render.resolution_x=lyt.bkr_size;
    context.scene.render.resolution_y=lyt.bkr_size;

#   ---     ---     ---     ---     ---

class LYT_SceneSettings(PropertyGroup):

    bkr_f0=EnumProperty (

        items       = GTBKR_F0,
        update      = UPIMPATH,

        name        = "Cathegory",
        description = "Root folder to pick from"

    );

    bkr_f1=EnumProperty (

        items       = GTBKR_F1,
        update      = UPIMPATH,

        name        = "Material",
        description = "Material folder to work with"

    );

    bkr_nsng0=FloatProperty (

        name        = "Height",
        description = "Middle point for the generated heightmap",

        default     = 0.5,
        min         = 0,
        max         = 1.0,

        update      = STNSNG

    );

    bkr_nsng1=FloatProperty (

        name        = "Treshold",
        description = "Middle point for the roughness factor",

        default     = 0.5,
        min         = 0,
        max         = 1.0,

        update      = STNSNG

    );

    bkr_nsng2=FloatProperty (

        name        = "Base",
        description = "Softens the resulting normal & rough values",

        default     = 0.0,
        min         = 0,
        max         = 2.0,

        update      = STNSNG

    );

    bkr_nsng3=FloatProperty (

        name        = "Intensity",
        description = "Makes resulting normal sharper",

        default     = 0.25,
        min         = -2.0,
        max         = 2.0,

        update      = STNSNG

    );

    bkr_size=IntProperty (

        name        = "Resolution",
        description = "Sets bake size",

        default     = 256,
        min         = 2,
        max         = 8192,

        update      = STBKSIZE

    );

#   ---     ---     ---     ---     ---

class LYT_BKOGL(Operator):

    bl_idname      = "lytbkr.bkogl";
    bl_label       = "Executes OpenGL bake";

    bl_description = "OpenGL renders the canvas with current settings";

#   ---     ---     ---     ---     ---

    def execute(self, context):

        lyt=context.scene.lytools;
        ob=bpy.data.objects["Canvas"]; ob.select=1;
        context.scene.objects.active=ob;

        usystem=context.user_preferences.system;
        umm_old=usystem.use_mipmaps; links=GTBKR_LINKS();

        node=GTBKR_NODE("NBAKE_SETTINGS"); out_node=GTBKR_NODE("EMITOUT");
        links.new(node.outputs[0], out_node.inputs[0]);

        node=GTBKR_NODE("BAKE_FROM");
        rtpath=node.image.filepath;
        rtpath="_".join(rtpath.split("_")[:-1])+"_"

        usystem.use_mipmaps=1;

        context.scene.camera=context.scene.objects["CANVAS_CAM"];
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA';
                break;

#   ---     ---     ---     ---     ---
# render normal

        context.scene.render.image_settings.file_format='PNG';
        bpy.ops.render.opengl();

        path=rtpath+"normal.png";
        bpy.data.images["Render Result"].save_render(path);

#   ---     ---     ---     ---     ---
# set ao as out then bake

        node=GTBKR_NODE("NBAKE_FROM");
        node.image.source='FILE'; node.image.filepath=path;

        node=GTBKR_NODE("AOBAKE");
        links.new(node.outputs[0], out_node.inputs[0]);

        node=GTBKR_NODE("AO_BAKETO");
        node.image.generated_width=lyt.bkr_size;
        node.image.generated_height=lyt.bkr_size;

        context.scene.cycles.bake_type='EMIT'; SLBKR_NODE("AO_BAKETO");

        bpy.ops.object.bake(type='EMIT');

#   ---     ---     ---     ---     ---
# combine ao, rough & metalness into orm

        node=GTBKR_NODE("BKORM");
        links.new(node.outputs[0], out_node.inputs[0]);

        path=rtpath+"orm.png"; bpy.ops.render.opengl();
        bpy.data.images["Render Result"].save_render(path);

#   ---     ---     ---     ---     ---
# set curv as out then bake

        node=GTBKR_NODE("SCURVY");
        links.new(node.outputs[0], out_node.inputs[0]);

        context.scene.cycles.bake_type='EMIT'; SLBKR_NODE("G_BAKETO");

        node=GTBKR_NODE("G_BAKETO");
        node.image.generated_width=lyt.bkr_size;
        node.image.generated_height=lyt.bkr_size

        bpy.ops.object.bake(type='EMIT');

        path=rtpath+"curv.png"; node.image.save_render(path);

#   ---     ---     ---     ---     ---

        usystem.use_mipmaps=umm_old;
        return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_renderPanel(Panel):

    bl_label       = 'LYT BAKER';
    bl_idname      = 'LYT_renderPanel';
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
        row    = layout.row();

        row.prop(lyt, "bkr_f0"); row=layout.row();
        if lyt.bkr_f0:
            row.prop(lyt, "bkr_f1");

            if lyt.bkr_f1:

                layout.separator();

                row=layout.row(); row.prop(lyt, "bkr_nsng0");
                row=layout.row(); row.prop(lyt, "bkr_nsng1");
                row=layout.row(); row.prop(lyt, "bkr_nsng2");
                row=layout.row(); row.prop(lyt, "bkr_nsng3");

                layout.separator();

                row=layout.row(); row.prop(lyt, "bkr_size");
                row.operator("lytbkr.bkogl", text = "BAKE", icon = "SCENE");


#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_SceneSettings);
    register_class(LYT_BKOGL);
    register_class(LYT_renderPanel);
    Scene.lytools=PointerProperty(type=LYT_SceneSettings);

def unregister():
    del Scene.lytools;
    unregister_class(LYT_renderPanel);
    unregister_class(LYT_BKOGL);
    unregister_class(LYT_SceneSettings);