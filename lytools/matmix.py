import bpy, os;

from bpy.types import Panel, Operator, PropertyGroup, Object, Material, Scene;
from bpy.utils import register_class, unregister_class;

#   ---     ---     ---     ---     ---

from bpy.props import (

    BoolProperty,
    StringProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty

);

#   ---     ---     ---     ---     ---

MATNAMES=["", "", "", ""];

MATIDS=([

    (0,0,0),
    (0,0,1),
    (0,1,0),
    (1,0,0),

    (1,1,1)

]);

def MKMATID(mat, color):
    mat.use_nodes=1;
    ntree=mat.node_tree; nodes=ntree.nodes; nodes.clear();

    diff=nodes.new('ShaderNodeEmission');
    diff.inputs[0].default_value[0:3]=color[:];

    out=nodes.new('ShaderNodeOutputMaterial');
    ntree.links.new(diff.outputs[0], out.inputs[0]);

    im=nodes.new('ShaderNodeTexImage');
    im.image=bpy.data.images["BAKETO_MATID"];

    nodes.active=im;

def GTMATID(idex):

    if idex>=4: idex=4;

    name=f"MATID{idex}";
    if name not in bpy.data.materials:
        mat=bpy.data.materials.new(name=name);
        MKMATID(mat, MATIDS[idex]);

    else:
        mat=bpy.data.materials[name];

    return mat;

#   ---     ---     ---     ---     ---

def BKMATIDS(me):

    global MATNAMES; MATNAMES=["" for _ in range(4)];

    rend=bpy.context.scene.render;

    old_usta=rend.bake.use_selected_to_active;
    rend.bake.cage_extrusion=10;

    old_en=rend.engine;
    old_bk=bpy.context.scene.cycles.bake_type;

    old_mats=[]; i=0;
    for mat in me.materials:
        MATNAMES[i]=mat.name;
        cmat=GTMATID(i); old_mats.append(mat);
        me.materials[i]=cmat; i+=1;

    rend.bake.use_selected_to_active=1;
    rend.engine='CYCLES';

    ob=bpy.context.object;
    cl=bpy.context.scene.objects.link(ob.copy()).object;

    cl.data=cl.data.copy(); ob.name, cl.name = cl.name, ob.name;
    ob.data, cl.data = cl.data, ob.data;

    for _ in range(len(cl.data.materials)-1):
        ob.active_material_index=0;
        bpy.ops.object.material_slot_remove();

    rend.bake.use_pass_direct=0;
    rend.bake.use_pass_indirect=0;
    rend.bake.use_pass_color=1;

    bpy.ops.object.bake(type='EMIT');

    ob.data.materials[0]=bpy.data.materials["MATID_BAKE"];
    rend.engine='BLENDER_RENDER'; rend.use_bake_selected_to_active=0;
    old_ibk=rend.bake_type; rend.bake_type='FULL';

    cl.select=0; ob.select=1; bpy.context.scene.objects.active=ob;

    for d in ob.data.uv_textures[0].data:
        d.image=bpy.data.images['BAKETO_MATID'];

    bpy.ops.object.bake_image();

    rend.bake_type=old_ibk; rend.engine='CYCLES';
    cmat=bpy.data.materials["COLORMASKING"].copy();

    cmat.name=(ob.name)+'_COLORMASK';
    ob.data.materials[0]=cmat;

    nodes=cmat.node_tree.nodes;

    rend.use_bake_to_vertex_color=1; rend.bake.use_selected_to_active=old_usta;
    rend.engine=old_en; bpy.context.scene.cycles.bake_type=old_bk;

    i=0;
    for mat in me.materials:

        omat=old_mats[i]; me.materials[i]=omat;
        nodes[f"IM{i}"].image=omat.node_tree.nodes["ALBEDO"].image;

        i+=1;

    GTMIXMAT(None, bpy.context);

#   ---     ---     ---     ---     ---

def UPPROJ(self, context):

    mat=context.object.active_material;
    lyt=mat.lytools; idex=lyt.cur; ntree=mat.node_tree;

    if lyt.upchk:
        return;

    ramp=ntree.nodes[f"RAMP{idex}"];
    mapping=ntree.nodes[f"MAP{idex}"];
    tc=ntree.nodes["TEXCOORD"];
    im=ntree.nodes[f"IM{idex}"];

    if lyt.proj == 'FLAT' and im.projection == 'BOX':
        ntree.links.new(tc.outputs[2], mapping.inputs[0]);
    elif lyt.proj == 'BOX' and im.projection == 'FLAT':
        ntree.links.new(tc.outputs[3], mapping.inputs[0]);

    mapping.translation[:]=lyt.loc[:];
    mapping.scale[:]=lyt.scale[:];
    mapping.rotation[:]=lyt.rot[:];

    im.projection=lyt.proj;
    im.projection_blend=lyt.blend;

    if idex:
        ramp.color_ramp.elements[1].position=lyt.tol;
    else:
        ramp.color_ramp.elements[0].position=1-lyt.tol;

#   ---     ---     ---     ---     ---

def GTMIXMAT(self, context):

    mat=context.object.active_material;
    lyt=mat.lytools; idex=lyt.cur; ntree=mat.node_tree;

    lyt.upchk=1; lyt.name=MATNAMES[idex];

    ramp=ntree.nodes[f"RAMP{idex}"];
    mapping=ntree.nodes[f"MAP{idex}"];
    tc=ntree.nodes["TEXCOORD"];
    im=ntree.nodes[f"IM{idex}"];

    lyt.loc[:]=mapping.translation[:];
    lyt.scale[:]=mapping.scale[:];
    lyt.rot[:]=mapping.rotation[:];

    lyt.proj=im.projection;
    lyt.blend=im.projection_blend;

    if idex:
        lyt.tol=ramp.color_ramp.elements[1].position;
    else:
        lyt.tol=1-ramp.color_ramp.elements[0].position;

    lyt.upchk=0;

#   ---     ---     ---     ---     ---

class LYT_MixMatSettings(PropertyGroup):

    upchk=BoolProperty(

        name        = "",
        description = "",
        default     = 0

    );

    name=StringProperty(

        name        = "",
        description = "",
        default     = ""

    );

    cur=IntProperty (

        name        = "Current",
        description = "Selected sub-material within the mix",

        default     = 0,
        min         = 0,
        max         = 3,

        update      = GTMIXMAT

    );

    proj=EnumProperty (

        items       = [('FLAT', 'UV',        'Use UV coordinates for texture mapping'),
                       ('BOX',  'Generated', 'Map textures through box projection'   )],

        update      = UPPROJ,
        name        = "Mapping",
        description = "Sets texture mapping mode"

    );

    blend=FloatProperty (

        name        = "Blend",
        description = "Blurs texture at the seams",

        default     = 0.05,
        min         = 0.0,
        max         = 1.0,

        update      = UPPROJ

    );

    tol=FloatProperty (

        name        = "Tolerance",
        description = "Affects mix with neighboring sub-materials",

        default     = 1.0,
        min         = 0.00001,
        max         = 1.0,

        update      = UPPROJ

    );

    scale=FloatVectorProperty (

        name        = "Scaling",
        description = "Scales UV/generated texture coordinates",
        subtype     = 'NONE',

        size        = 3,
        default     = [1.0,1.0,1.0],
        update      = UPPROJ

    );

    loc=FloatVectorProperty (

        name        = "Location",
        description = "Offsets UV/generated texture coordinates",
        subtype     = 'TRANSLATION',

        size        = 3,
        default     = [0.0,0.0,0.0],
        update      = UPPROJ

    );

    rot=FloatVectorProperty (

        name        = "Rotation",
        description = "Rotates UV/generated texture coordinates",
        subtype     = 'EULER',

        size        = 3,
        default     = [0.0,0.0,0.0],
        update      = UPPROJ

    );

#   ---     ---     ---     ---     ---

class LYT_BKMATID(Operator):

    bl_idname      = "lytbkr.bkmatid";
    bl_label       = "Bakes material IDs to an image";

    bl_description = "Bakes a color map representing material IDs";

#   ---     ---     ---     ---     ---

    def execute(self, context):

        if len(context.object.data.materials) > 4:
            self.report(
                {'WARNING'},
                f"Object {context.object.name} has more than 4 materials; op aborted"
            );

        else:
            BKMATIDS(context.object.data);

        return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_mixingPanel(Panel):

    bl_label       = 'LYT MIXER';
    bl_idname      = 'LYT_mixingPanel';
    bl_space_type  = 'PROPERTIES';
    bl_region_type = 'WINDOW';
    bl_context     = 'data';
    bl_category    = 'LYT';

#   ---     ---     ---     ---     ---
    
    @classmethod
    def poll(cls, context):
        return isinstance(context.object.data, bpy.types.Mesh);

    def draw(self, context):
        layout=self.layout; row=layout.row();
        row.operator("lytbkr.bkmatid", text="BAKE MATERIAL IDS", icon="COLOR");

        if "_COLORMASK" in context.object.data.materials[0].name:

            mat=context.object.active_material; lyt=mat.lytools;
            layout.separator();

            for prop in ["cur", "proj", "blend", "tol", "scale", "loc", "rot"]:
                if prop=="blend" and lyt.proj != 'BOX':
                    continue;

                row=layout.row();
                if prop=="cur":
                    row.label("Current: "); row.prop(lyt, prop, text=lyt.name);
                else:
                    row.prop(lyt, prop);

                if prop in ["tol", "cur"]:
                    layout.separator();

#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_MixMatSettings);
    register_class(LYT_mixingPanel);
    register_class(LYT_BKMATID);
    Material.lytools=PointerProperty(type=LYT_MixMatSettings);

def unregister():
    del Material.lytools;
    unregister_class(LYT_BKMATID);
    unregister_class(LYT_mixingPanel);
    unregister_class(LYT_MixMatSettings);

#   ---     ---     ---     ---     ---