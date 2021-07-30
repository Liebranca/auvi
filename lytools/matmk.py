import bpy, os;

from bpy.types import Scene, Image, PropertyGroup, Panel, Operator;
from bpy.utils import register_class, unregister_class;

#   ---     ---     ---     ---     ---

from bpy.props import (

    StringProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
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

    rtpath=lyt.bkr_f1[:-1];
    if os.path.exists(rtpath+".lytx"):
        LDLYTX(lyt);

    bpy.ops.file.make_paths_relative();

#   ---     ---     ---     ---     ---

def STNSNG(self, context):
    node=GTBKR_NODE("NBAKE_SETTINGS"); lyt=context.scene.lytools;
    for i in range(4):
        node.inputs[1+i].default_value=getattr(lyt, f"bkr_nsng{i}");

    node=GTBKR_NODE("ADDROUGH"); node.inputs[1].default_value=lyt.bkr_nsng4;
    node=GTBKR_NODE("RMASK"); node.color_ramp.elements[1].position=lyt.bkr_rmask;

def STBKSIZE(self, context):
    lyt=context.scene.lytools;
    context.scene.render.resolution_x=lyt.bkr_size*lyt.bkr_res;
    context.scene.render.resolution_y=lyt.bkr_size*lyt.bkr_res;

#   ---     ---     ---     ---     ---

def UPMET(self, context):

    lyt=context.scene.lytools; node=GTBKR_NODE("METMASK");

    node.inputs[1].default_value=lyt.bkr_metmask;
    node.inputs[2].default_value=lyt.bkr_metbase;
    node.inputs[3].default_value=lyt.bkr_mettol;

def UPEMIT(self, context):

    lyt=context.scene.lytools; node=GTBKR_NODE("EMITMASK");

    node.inputs[1].default_value=lyt.bkr_emitmask;
    node.inputs[2].default_value=lyt.bkr_emitbase;
    node.inputs[3].default_value=lyt.bkr_emittol;

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

def UPBKRVIEW(self, context):

    lyt=context.scene.lytools; links=GTBKR_LINKS();

    node=GTBKR_NODE(viewModes_nd[lyt.bkr_view]);
    out_node=GTBKR_NODE("REOUT");

    out_idex=2 if lyt.bkr_view=="height" else 0;
    links.new(node.outputs[out_idex], out_node.inputs[0]);

class LYT_SceneSettings(PropertyGroup):

    bkr_view=EnumProperty (

        items       = viewModes,
        default     = "normal",
        update      = UPBKRVIEW,

        name        = "Cathegory",
        description = "Root folder to pick from"

    );

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

    bkr_rmask=FloatProperty (

        name        = "Rawmask tolerance",
        description = "Adjusts grey levels of the initial rawmask",

        default     = 0.338776,
        min         = 0.000001,
        max         = 1.0,

        update      = STNSNG

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

        name        = "Softness",
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

    bkr_nsng4=FloatProperty (

        name        = "Rough modifier",
        description = "Adds to roughness post normal calculations",

        default     = 0.0,
        min         = -1.0,
        max         = 4.0,

        update      = STNSNG

    );

    bkr_size=IntProperty (

        name        = "Size",
        description = "Final bake size, after de-scaling",

        default     = 256,
        min         = 2,
        max         = 8192,

        update      = STBKSIZE

    );

    bkr_res=IntProperty (

        name        = "Scale",
        description = "Resolution multiplier, renders at larger size then scales down",

        default     = 1,
        min         = 1,
        max         = 16,

        update      = STBKSIZE

    );

    bkr_metmask=FloatVectorProperty (

        name        = "Metal color",
        description = "Color for metallic mask",
        subtype     = 'COLOR',

        size        = 4,
        default     = [1.0,1.0,1.0,1.0],
        update      = UPMET

    );

    bkr_metbase=FloatProperty (

        name        = "Metal base",
        description = "Multiplier for metallic",

        default     = 0.0,
        min         = 0.0,
        max         = 2.0,

        update      = UPMET

    );

    bkr_mettol=FloatProperty (

        name        = "Metal tolerance",
        description = "Makes non-metallic colors more metallic",

        default     = 0.0,
        min         = 0.0,
        max         = 2.0,

        update      = UPMET

    );

    bkr_emitmask=FloatVectorProperty (

        name        = "Emit color",
        description = "Color for emission mask",
        subtype     = 'COLOR',

        size        = 4,
        default     = [1.0,1.0,1.0,1.0],
        update      = UPEMIT

    );

    bkr_emitbase=FloatProperty (

        name        = "Emit base",
        description = "Multiplier for emission",

        default     = 0.0,
        min         = 0.0,
        max         = 2.0,

        update      = UPEMIT

    );

    bkr_emittol=FloatProperty (

        name        = "Emit tolerance",
        description = "Makes non-emissive colors more emissive",

        default     = 0.0,
        min         = 0.0,
        max         = 2.0,

        update      = UPEMIT

    );

    bkr_fresnel=FloatProperty (

        name        = "Base Fresnel",
        description = "Base fresnel value",

        default     = 0.050,
        min         = 0.050,
        max         = 1.000

    );

#   ---     ---     ---     ---     ---

LYT_ATTRS=([

    "bkr_rmask",

    "bkr_nsng0",
    "bkr_nsng1",
    "bkr_nsng2",
    "bkr_nsng3",
    "bkr_nsng4",

    "bkr_size",
    "bkr_res",

    "bkr_metmask",
    "bkr_metbase",
    "bkr_mettol",

    "bkr_emitmask",
    "bkr_emitbase",
    "bkr_emittol",

    "bkr_fresnel"

]);

def SVLYTX(lyt):
    d={}; rtpath=lyt.bkr_f1[:-1];
    for k in LYT_ATTRS:
        if k == "bkr_metmask":
            d[k]=lyt.bkr_metmask[:];
        elif k == "bkr_emitmask":
            d[k]=lyt.bkr_emitmask[:];
        else:
            d[k]=getattr(lyt, k);

    path=rtpath+".lytx"; d=(str(d)).replace(" ", "");
    with open(path, "w+") as file: file.write(d);

def LDLYTX(lyt):
    s=""; path=lyt.bkr_f1[:-1]+".lytx";
    with open(path, "r") as file:
        s=file.read();

    d=eval(s);
    for k in LYT_ATTRS:
        if k not in d:
            continue;

        if k == "bkr_metmask":
            lyt.bkr_metmask[:]=d[k][:];
        elif k == "bkr_emitmask":
            lyt.bkr_emitmask[:]=d[k][:];
        else:
            setattr(lyt, k, d[k]);

#   ---     ---     ---     ---     ---

class LYT_SVBUTT(Operator):

    bl_idname      = "lytbkr.svlytx";
    bl_label       = "Saves settings for this material";

    bl_description = "Save current settings to a file associated with this material";

    def execute(self, context):

        lyt=context.scene.lytools; SVLYTX(lyt);
        self.report({'INFO'}, f"Material settings saved to <{lyt.bkr_f1[:-1]+'.lytx'}>");

        return {'FINISHED'};

class LYT_LDBUTT(Operator):

    bl_idname      = "lytbkr.ldlytx";
    bl_label       = "Loads settings for this material";

    bl_description = "Load settings from a file associated with this material";

    def execute(self, context):

        lyt=context.scene.lytools; path=lyt.bkr_f1[:-1]+".lytx";

        if os.path.exists(path):
            LDLYTX(lyt); self.report({'INFO'}, f"Loaded <{path}>");

        else:
            self.report({'WARNING'}, f"File <{path}> not found!");

        return {'FINISHED'};

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

        node=GTBKR_NODE("NBAKE_SETTINGS"); out_node=GTBKR_NODE("REOUT");
        links.new(node.outputs[0], out_node.inputs[0]);

        mix_node=GTBKR_NODE("OUTMIX");
        links.new(node.outputs[2], mix_node.inputs[0]);

        node=GTBKR_NODE("BAKE_FROM"); rtpath=lyt.bkr_f1;

        SVLYTX(lyt);
        usystem.use_mipmaps=1;

        context.scene.camera=context.scene.objects["CANVAS_CAM"];
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA';
                break;

#   ---     ---     ---     ---     ---
# render normal

        context.scene.render.engine='CYCLES';

        print("Baking normal... ");
        context.scene.render.image_settings.file_format='PNG';
        bpy.ops.render.opengl();

        path=rtpath+"normal.png";
        bpy.data.images["Render Result"].save_render(path);

        for link in mix_node.inputs[0].links:
            links.remove(link);

#   ---     ---     ---     ---     ---
# set ao as out then bake

        node=GTBKR_NODE("NBAKE_FROM");
        node.image.source='FILE'; node.image.filepath=path;

        context.scene.render.engine='BLENDER_RENDER';

        context.scene.cycles.bake_type='EMIT';

        print("Baking AO... ");
        bpy.ops.render.opengl(); path=rtpath+"tmp.png";
        bpy.data.images["Render Result"].save_render(path);

        node=GTBKR_NODE("AO_BAKETO");
        node.image.source='FILE'; node.image.filepath=path;

#   ---     ---     ---     ---     ---
# combine ao, rough, metalness & emit into orm+e

        context.scene.render.engine='CYCLES';

        node=GTBKR_NODE("BKORM");
        links.new(node.outputs[0], out_node.inputs[0]);
        links.new(GTBKR_NODE("EMITMASK").outputs[0], mix_node.inputs[0]);

        print("Combining ORM map... ");
        path=rtpath+"orm.png"; bpy.ops.render.opengl();
        bpy.data.images["Render Result"].save_render(path);

        for link in mix_node.inputs[0].links:
            links.remove(link);

#   ---     ---     ---     ---     ---
# set curv as out then bake

        node=GTBKR_NODE("SCURVY");
        links.new(node.outputs[0], out_node.inputs[0]);
        mix_node.inputs[0].default_value=1.0-lyt.bkr_fresnel;

        print("Baking curvature... ");
        path=rtpath+"curv.png"; bpy.ops.render.opengl();
        bpy.data.images["Render Result"].save_render(path);

        mix_node.inputs[0].default_value=1.0;

#   ---     ---     ---     ---     ---

        print("Resizing... ");
        node=GTBKR_NODE("NBAKE_FROM");
        node.image.scale(lyt.bkr_size, lyt.bkr_size); node.image.save();

        node.image.filepath=rtpath+"orm.png";
        node.image.scale(lyt.bkr_size, lyt.bkr_size); node.image.save();

        node.image.filepath=rtpath+"curv.png";
        node.image.scale(lyt.bkr_size, lyt.bkr_size); node.image.save();

        print("Cleaning up temp files... ");
        node=GTBKR_NODE("AO_BAKETO");
        path=node.image.filepath; node.image.source='GENERATED';

        os.system("@del %s"%path);

        print("Done!\n");
        usystem.use_mipmaps=umm_old; UPBKRVIEW(self, context);
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
        row    = layout.row(1);

        row.prop_enum(lyt, "bkr_view", "normal");
        row.prop_enum(lyt, "bkr_view", "albedo");
        row.prop_enum(lyt, "bkr_view", "height");
        row.prop_enum(lyt, "bkr_view", "rmask" );
        row.prop_enum(lyt, "bkr_view", "rough" );
        row.prop_enum(lyt, "bkr_view", "metal" );
        row.prop_enum(lyt, "bkr_view", "emit"  );

        layout.separator(); row=layout.row();
        row.prop(lyt, "bkr_f0"); row=layout.row();

        if lyt.bkr_f0:
            row.prop(lyt, "bkr_f1");

            if lyt.bkr_f1:

                layout.separator(); row=layout.row(1);

                row.operator("lytbkr.svlytx", text = "SAVE", icon = "SAVE_COPY");
                row.operator("lytbkr.ldlytx", text = "LOAD", icon = "FILE_REFRESH");

                layout.separator();

                row=layout.row(); row.label("Normal/Rough settings:");

                row=layout.row(); row.prop(lyt, "bkr_rmask");

                layout.separator();

                row=layout.row(); row.prop(lyt, "bkr_nsng0");
                row=layout.row(); row.prop(lyt, "bkr_nsng1");
                row=layout.row(); row.prop(lyt, "bkr_nsng2");
                row=layout.row(); row.prop(lyt, "bkr_nsng3");
                row=layout.row(); row.prop(lyt, "bkr_nsng4");
                row=layout.row(); row.prop(lyt, "bkr_fresnel");

                layout.separator();
                row=layout.row(); row.label("Metalness settings:");

                row=layout.row(); row.prop(lyt, "bkr_metbase");
                row=layout.row(); row.prop(lyt, "bkr_mettol" );
                row=layout.row(); row.prop(lyt, "bkr_metmask");

                layout.separator();

                row=layout.row(); row.label("Emission settings:");

                row=layout.row(); row.prop(lyt, "bkr_emitbase");
                row=layout.row(); row.prop(lyt, "bkr_emittol" );
                row=layout.row(); row.prop(lyt, "bkr_emitmask");

                layout.separator();

                row=layout.row(); row.prop(lyt, "bkr_size"); row.prop(lyt, "bkr_res");

                row=layout.row();
                row.operator("lytbkr.bkogl", text="BAKE", icon="RENDER_STILL");


#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_SceneSettings);
    register_class(LYT_BKOGL);
    register_class(LYT_SVBUTT);
    register_class(LYT_LDBUTT);
    register_class(LYT_renderPanel);
    Scene.lytools=PointerProperty(type=LYT_SceneSettings);

def unregister():
    del Scene.lytools;
    unregister_class(LYT_renderPanel);
    unregister_class(LYT_LDBUTT);
    unregister_class(LYT_SVBUTT);
    unregister_class(LYT_BKOGL);
    unregister_class(LYT_SceneSettings);