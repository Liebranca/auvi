import bpy, os;

from bpy.types import Scene, Material, Image, PropertyGroup, Panel, Operator;
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

IMTYPES={

    "ALBEDO":[0, 1],
    "ORM"   :[2,3],
    "CURV"  :[4],
    "NORMAL":[5,6]

};

def MATGNSIS():
    mat=bpy.context.active_object.active_material;
    mat.use_nodes=1; lyt=mat.lytools;

    ntree=mat.node_tree; nodes=ntree.nodes; nodes.clear();
    tc=nodes.new('ShaderNodeTexCoord'); tc.location=[0,0];
    tc.name=tc.label="TEXCOORD";

    vm=nodes.new('ShaderNodeVectorMath'); vm.location=[250, 0];
    vm.name=vm.label="VECMATH"; vm.operation='MULTIPLY';

    ntree.links.new(tc.outputs[2], vm.inputs[0]);
    vm.inputs[1].default_value=[1,1,1];

#   ---     ---     ---     ---     ---

    shd=nodes.new('ShaderNodeGroup');  shd.location=[750, 0];
    shd.node_tree=bpy.data.node_groups["LyShader"];
    shd.name=shd.label="SHADER";

    out=nodes.new('ShaderNodeOutput'); out.location=[1000, 0];
    out.name=out.label="OUT";

#   ---     ---     ---     ---     ---

    matname=lyt.mat_f1.split("\\")[-1]; y=600;

    for name in IMTYPES:
        im=nodes.new('ShaderNodeTexImage'); im.location=[500, y];
        im.name=im.label=name; y-=275;

        ntree.links.new(vm.outputs[0], im.inputs[0]);
        for i in range(len(IMTYPES[name])):
            ntree.links.new(im.outputs[i], shd.inputs[IMTYPES[name][i]]);

        imname=matname+name.lower();
        if imname not in bpy.data.images:
            new_img=bpy.data.images.new(imname, width=64, height=64);
            new_img.source='FILE'; new_img.filepath=lyt.mat_f1+name.lower()+'.png'

        im.image=bpy.data.images[imname];
        if name=="NORMAL": im.color_space='NONE';

    ntree.links.new(shd.outputs[0], out.inputs[0]);
    ntree.links.new(shd.outputs[1], out.inputs[1]);

#   ---     ---     ---     ---     ---

NDCHECK=["TEXCOORD", "SHADER", "OUT", "VECMATH"] + [key for key in IMTYPES];

def VALIDATE(mat):

    if mat.node_tree:
        for ndname in NDCHECK:
            if ndname not in mat.node_tree.nodes:
                return 0;

        return 1;

    return 0;

#   ---     ---     ---     ---     ---

DROOT="\\".join(__file__.split("\\")[:-2])+'\\data';

#   ---     ---     ---     ---     ---

def GTMAT_F0(self, context):
    w=list(os.walk(DROOT));
    return [tuple([w[0][0]+'\\'+s, s.capitalize(), '']) for s in w[0][1]];

def GTMAT_F1(self, context):
    mat=bpy.context.active_object.active_material;
    w=list(os.walk(mat.lytools.mat_f0));
    w=[pis for pis in w if "textures" in pis[1] or "textures" in pis[0]]; l=[];

    for pis in w:
        for s in pis[1]:
            if s!="textures":
                l.append( tuple( [pis[0]+'\\'+s+'\\'+s+'_', s.capitalize(), '' ]) );

    return l;

def UPIMPATH(self, context):
    mat=bpy.context.active_object.active_material;
    lyt=mat.lytools;

    for imname in IMTYPES:

        if imname not in mat.node_tree.nodes: continue;

        node=mat.node_tree.nodes[imname];
        node.image.filepath=lyt.mat_f1+imname.lower()+'.png';

    bpy.ops.file.make_paths_relative();

#   ---     ---     ---     ---     ---

def UPMAT(self, context):
    mat=context.object.active_material;
    lyt=mat.lytools; ntree=mat.node_tree;

    nd=ntree.nodes["SHADER"];
    nd.inputs[7].default_value=lyt.mat_fresnel;

def UPPROJ(self, context):

    mat=context.object.active_material;
    lyt=mat.lytools; ntree=mat.node_tree;

    im=ntree.nodes["ALBEDO"];
    tc, vm = ntree.nodes["TEXCOORD"], ntree.nodes["VECMATH"];

    if lyt.mat_proj == 'FLAT' and im.projection == 'BOX':
        ntree.links.new(tc.outputs[2], vm.inputs[0]);
    elif lyt.mat_proj == 'BOX' and im.projection == 'FLAT':
        ntree.links.new(tc.outputs[3], vm.inputs[0]);

    for imname in IMTYPES:
        im=ntree.nodes[imname];
        im.projection=lyt.mat_proj;
        im.projection_blend=lyt.mat_blend;

    vm.inputs[1].default_value[0:2] = lyt.mat_scale[:];

#   ---     ---     ---     ---     ---

class LYT_MaterialSettings(PropertyGroup):

    mat_f0=EnumProperty (

        items       = GTMAT_F0,
        update      = UPIMPATH,

        name        = "Cathegory",
        description = "Root folder to pick from"

    );

    mat_f1=EnumProperty (

        items       = GTMAT_F1,
        update      = UPIMPATH,

        name        = "Material",
        description = "Material folder to work with"

    );

    mat_proj=EnumProperty (

        items       = [('FLAT', 'UV',        'Use UV coordinates for texture mapping'),
                       ('BOX',  'Generated', 'Map textures through box projection'   )],

        update      = UPPROJ,
        name        = "Mapping",
        description = "Sets texture mapping mode"

    );

    mat_scale=FloatVectorProperty (

        name        = "Scaling",
        description = "Scales UV/generated texture coordinates",
        subtype     = 'NONE',

        size        = 2,
        default     = [1.0,1.0],
        update      = UPPROJ

    );

    mat_blend=FloatProperty (

        name        = "Blend",
        description = "Blurs texture at the seams",

        default     = 0.05,
        min         = 0.0,
        max         = 1.0,

        update      = UPPROJ

    );

    mat_fresnel=FloatProperty (

        name        = "Fresnel",
        description = "Brightens material at the edges",

        default     = 0.075,
        min         = 0.0,
        max         = 1.0,

        update      = UPMAT

    );

#   ---     ---     ---     ---     ---

class LYT_INITMAT(Operator):

    bl_idname      = "lytmat.initmat";
    bl_label       = "Initialize material template";

    bl_description = "Clears current nodetree and sets up default material template";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        MATGNSIS(); return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_materialPanel(Panel):

    bl_label       = 'LYT MATE';
    bl_idname      = 'LYT_materialPanel';
    bl_space_type  = 'PROPERTIES';
    bl_region_type = 'WINDOW';
    bl_context     = 'material';
    bl_category    = 'LYT';

#   ---     ---     ---     ---     ---
    
    @classmethod
    def poll(cls, context):
        return context.object!=None;

    def draw(self, context):

        layout = self.layout;

        scene  = context.scene;
        mat    = context.active_object.active_material;
        lyt    = context.active_object.active_material.lytools;

        row=layout.row(); row.prop(lyt, "mat_f0");

        if lyt.mat_f0:
            row=layout.row(); row.prop(lyt, "mat_f1");

            if not VALIDATE(mat):
                row=layout.row(); row.operator("lytmat.initmat", text="INIT", icon="SMOOTH");

            else:

                layout.separator();

                row=layout.row(); row.prop(lyt, "mat_proj");
                if lyt.mat_proj == 'BOX':
                    row=layout.row(); row.prop(lyt, "mat_blend");

                row=layout.row(); row.prop(lyt, "mat_scale");

                layout.separator();

                row=layout.row(); row.prop(lyt, "mat_fresnel");

#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_MaterialSettings);
    register_class(LYT_INITMAT);
    register_class(LYT_materialPanel);
    Material.lytools=PointerProperty(type=LYT_MaterialSettings);

def unregister():
    del Material.lytools;
    unregister_class(LYT_materialPanel);
    unregister_class(LYT_INITMAT);
    unregister_class(LYT_MaterialSettings);

#   ---     ---     ---     ---     ---