import bpy, os;

from bpy.types import Panel, Operator, PropertyGroup, Object, Material, Scene;
from bpy.utils import register_class, unregister_class;

from .blmod    import SHUT_OPS;

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

MATIDS=([

    (0,0,0),
    (0,0,1),
    (0,1,0),
    (1,0,0)

]);

#   ---     ---     ---     ---     ---

def BKMATIDS(me):

    rend=bpy.context.scene.render;
    rend.bake.cage_extrusion=10;

#   ---     ---     ---     ---     ---
# do some math

    i=0; h=1;
    for mat in me.materials:
        j=i+(4*(h-1)); i=0 if i==3 else i+1;
        if not i: h+=1;

#   ---     ---     ---     ---     ---
# clone original and do castling

    rend.bake.use_selected_to_active=1;
    rend.engine='CYCLES';

    ob=bpy.context.object;
    cl=bpy.context.scene.objects.link(ob.copy()).object;

    cl.data=cl.data.copy(); ob.name, cl.name = cl.name, ob.name;
    ob.data, cl.data = cl.data, ob.data;

    ob.active_material_index=len(ob.data.materials)-1;
    for _ in range(len(cl.data.materials)-h):
        i=ob.active_material_index;
        bpy.ops.object.material_slot_remove();
        ob.active_material_index-=1;

    rend.bake.use_pass_direct=0;
    rend.bake.use_pass_indirect=0;
    rend.bake.use_pass_color=1;

    for vc in ob.data.vertex_colors:
        ob.data.vertex_colors.remove(vc);

    for vckey in ["Col", "Mix"]:
        ob.data.vertex_colors.new(name=vckey);

#   ---     ---     ---     ---     ---
# paste submat ids into 'COL' slot

    id_loops=[[], [], [], []];
    for poly in cl.data.polygons:
        i=poly.material_index;
        while i>3: i-=4;

        id_loops[i].extend([

            loop for loop in poly.loop_indices
            if loop not in id_loops[i]

            ]);

    ob.data.vertex_colors.active_index=0;
    vc=ob.data.vertex_colors["Col"]; i=0;

    for matid in id_loops:
        for loop_index in matid:
            vc.data[loop_index].color[:3]=MATIDS[i];

        i+=1;

#   ---     ---     ---     ---     ---
# paste mixmat color ids into 'MIX' slot

    ob.active_material_index=0; id_loops=[[], [], [], []];
    for poly in ob.data.polygons:
        id_loops[poly.material_index].extend([

            loop for loop in poly.loop_indices
            if loop not in id_loops[poly.material_index]

            ]);

    ob.data.vertex_colors.active_index=1;
    vc=ob.data.vertex_colors["Mix"]; i=0;

    for matid in id_loops:
        for loop_index in matid:
            vc.data[loop_index].color[:3]=MATIDS[i];

        i+=1;

#   ---     ---     ---     ---     ---
# assign textures

    tot=len(ob.data.materials);
    for x in range(h):
        cmat=bpy.data.materials["COLORMASKING"].copy();

        cmat.name=(ob.name)+f'_COLORMASK{x}'; i=0; j=0;
        ob.data.materials[x]=cmat; nodes=cmat.node_tree.nodes;

        for mat in me.materials:
            omat=me.materials[j];
            nodes[f"IM{i}"].image=omat.node_tree.nodes["ALBEDO"].image;

            i=0 if i==3 else i+1; j+=1;

    for i in range(len(ob.data.materials)-1, -1, -1):
        ob.lytools.mix_idex=i;

#   ---     ---     ---     ---     ---

def STALPHA(col, alpha):
    c_pixels=list(col.pixels); a_pixels=list(alpha.pixels);
    for j in range(0, len(c_pixels), 4): c_pixels[j+3]*=a_pixels[j];
    col.pixels[:]=c_pixels; col.update();

def BKMIXMAT():

    rend=bpy.context.scene.render;
    ob=bpy.context.object;

#   ---     ---     ---     ---     ---
# set up

    rend.image_settings.file_format='PNG';
    rend.image_settings.color_mode='RGBA';

    folder=f"{ob.lytools.f0}\\textures\\{ob.name}"
    if not os.path.exists(folder): os.makedirs(folder);

    rtpath=f"{folder}\\{ob.name}_";

    rend.bake.use_selected_to_active=0;
    rend.engine='CYCLES';

    rend.bake.use_pass_direct=0;
    rend.bake.use_pass_indirect=0;
    rend.bake.use_pass_color=1;

#   ---     ---     ---     ---     ---
# loop thru mixes

    for i in range(len(ob.data.materials)):

        print(f"Baking mix {i}: ", end='', flush=1);
        ob.lytools.mix_idex=i;

        mat=ob.active_material; ntree=mat.node_tree;

        cout = ntree.nodes["OUTCOLOR"];

        nmix, cmix = ntree.nodes["MIXNORMAL"], ntree.nodes["MIXCOLOR"];
        omix, nbaketo = ntree.nodes["MIXORM"], ntree.nodes["NBAKE"];
        fmix, amix = ntree.nodes["FRESNELMIX"], ntree.nodes["MIXALPHA"];
        aobaketo, ncombined = ntree.nodes["AOBAKE"], ntree.nodes["NCOMB"];
        result, resalpha = ntree.nodes["RESULT"], ntree.nodes["RESALPHA"];

        ntree.nodes.active=result;
        result.image.generated_width=ob.lytools.res;
        result.image.generated_height=ob.lytools.res;
        resalpha.image.generated_width=ob.lytools.res;
        resalpha.image.generated_height=ob.lytools.res;

#   ---     ---     ---     ---     ---
# bake albedo

        print("albedo, ", end='', flush=1); impath=rtpath+f"albedo{i}.png";

        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});
        result.image.save_render(impath);

        ntree.nodes.active=resalpha;
        ntree.links.new(amix.outputs[0], cout.inputs[0]);
        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

        result.image.source='FILE'; result.image.filepath=impath;
        STALPHA(result.image, resalpha.image); result.image.save_render(impath);

        result.image.source='GENERATED';

        ntree.nodes.active=result;
        ntree.links.new(cmix.outputs[0], cout.inputs[0]);

#   ---     ---     ---     ---     ---
# set orm+e and bake

        print("ORM+E, ", end='', flush=1); impath=rtpath+f"orm{i}.png";

        for h in range(4):

            node=ntree.nodes[f"IM{h}"];
            if node.image.name != "DUMMY":
                base=node.image.name.split("_")[0];
                node.image=bpy.data.images[base+"_orm"];

        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});
        result.image.save_render(impath);

        ntree.nodes.active=resalpha;
        ntree.links.new(amix.outputs[0], cout.inputs[0]);
        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

        result.image.source='FILE'; result.image.filepath=impath;
        STALPHA(result.image, resalpha.image); result.image.save_render(impath);

        result.image.source='GENERATED';

        ntree.nodes.active=result;
        ntree.links.new(cmix.outputs[0], cout.inputs[0]);

#   ---     ---     ---     ---     ---
# set normal and bake

        print("normals, ", end='', flush=1); impath=rtpath+f"normal{i}.png";

        for h in range(4):

            node=ntree.nodes[f"IM{h}"];
            if node.image.name != "DUMMY":
                base=node.image.name.split("_")[0];
                node.image=bpy.data.images[base+"_normal"];

        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});
        result.image.save_render(impath);

        ntree.nodes.active=resalpha;
        ntree.links.new(amix.outputs[0], cout.inputs[0]);
        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

        result.image.source='FILE'; result.image.filepath=impath;
        STALPHA(result.image, resalpha.image); result.image.save_render(impath);

        result.image.source='GENERATED';

        ntree.nodes.active=result;
        ntree.links.new(cmix.outputs[0], cout.inputs[0]);

#   ---     ---     ---     ---     ---
# set fresnel out and bake

        print("fresnel... ");

        for h in range(4):

            node=ntree.nodes[f"IM{h}"];
            if node.image.name != "DUMMY":
                base=node.image.name.split("_")[0];
                basemat=bpy.data.materials[base];
                v=basemat.node_tree.nodes["SHADER"].inputs[7].default_value;
                fmix.inputs[4+h].default_value=v;

        ntree.links.new(fmix.outputs[0], ntree.nodes["MATOUT"].inputs[0]);

        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});
        result.image.save_render(rtpath+f"fresnel{i}.png");
        ntree.links.new(cmix.outputs[0], cout.inputs[0]);

#   ---     ---     ---     ---     ---
# walkback changes

        for h in range(4):

            node=ntree.nodes[f"IM{h}"];
            if node.image.name != "DUMMY":
                base=node.image.name.split("_")[0];
                node.image=bpy.data.images[base+"_albedo"];
                node.image.reload();

        ntree.links.new(ntree.nodes["OUTCOLOR"].outputs[0], ntree.nodes["MATOUT"].inputs[0]);

    ob.lytools.mix_idex=0;

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

def UPMIXPAR(self, context):

    ob=context.object;

    if self.mix_idex > len(ob.data.materials)-1:
        self.mix_idex = len(ob.data.materials)-1;
        return;

    mat=ob.active_material; ntree=mat.node_tree;
    out, act=ntree.nodes["MATOUT"], ntree.nodes["INACTIVE"];
    ntree.links.new(act.outputs[0], out.inputs[0]);

    ob.active_material_index=self.mix_idex;

    mat=ob.active_material; ntree=mat.node_tree;
    out, act=ntree.nodes["MATOUT"], ntree.nodes["OUTCOLOR"];
    ntree.links.new(act.outputs[0], out.inputs[0]);

    GTMIXMAT(None, context);

#   ---     ---     ---     ---     ---

DROOT="\\".join(__file__.split("\\")[:-2])+'\\data';

def GTF0(self, context):
    w=list(os.walk(DROOT));
    return [tuple([w[0][0]+'\\'+s, s.capitalize(), '']) for s in w[0][1]];

def GTMIXMAT(self, context):

    mat=context.object.active_material;
    lyt=mat.lytools; idex=lyt.cur; ntree=mat.node_tree;

    lyt.upchk=1; lyt.name=ntree.nodes[f"IM{idex}"].image.name.split("_")[0];

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

class LYT_MixObjSettings(PropertyGroup):

    mix_idex=IntProperty(

        name        = "Mix",
        description = "Current sub-material container",
        update      = UPMIXPAR,

        default     = 0,
        min         = 0,
        max         = 3

    );

    mix_name=StringProperty(

        name        = "Parent name",
        description = "Name of object the mix is derived from",

    );

    f0=EnumProperty(

        items       = GTF0,
        name        = "Cathegory",
        description = "Parent folder to save baked textures to"

    );

    res=IntProperty(

        name        = "Size",
        description = "Output resolution for resulting bake",

        default     = 256,
        min         = 2,
        max         = 8192

    );

#   ---     ---     ---     ---     ---

class LYT_BKMATID(Operator):

    bl_idname      = "lytbkr.bkmatid";
    bl_label       = "Bakes material IDs to an image";

    bl_description = "Bakes a color map representing material IDs";

#   ---     ---     ---     ---     ---

    def execute(self, context):

        if len(context.object.data.materials) > 16:
            self.report(
                {'WARNING'},
                f"Object {context.object.name} has more than 16 materials; op aborted"
            );

        else:
            BKMATIDS(context.object.data);

        return {'FINISHED'};

class LYT_BKMIX(Operator):

    bl_idname      = "lytbkr.bkmix";
    bl_label       = "Bakes images from sub-materials";

    bl_description = "Bakes textures from mix into a composite";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        BKMIXMAT(); return {'FINISHED'};

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

        if "_COLORMASK" in context.object.active_material.name:

            mat=context.object.active_material; lyt=mat.lytools;
            layout.separator();

            row=layout.row(); row.prop(context.object.lytools, "f0");
            row=layout.row(); row.prop(context.object.lytools, "mix_idex");

            layout.separator();

            for prop in ["cur", "proj", "blend", "tol", "scale", "loc", "rot"]:
                if prop=="blend" and lyt.proj != 'BOX':
                    continue;

                row=layout.row();
                if prop=="cur":
                    name=lyt.name if lyt.name else "EMPTY";
                    row.label("Current: "); row.prop(lyt, prop, text=name);
                else:
                    row.prop(lyt, prop);

                if prop in ["tol", "cur"]:
                    layout.separator();

            layout.separator();
            row=layout.row(); row.prop(context.object.lytools, "res");
            row.operator("lytbkr.bkmix", text="BAKE MIX", icon="RENDER_STILL");

#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_MixObjSettings);
    register_class(LYT_MixMatSettings);
    register_class(LYT_mixingPanel);
    register_class(LYT_BKMATID);
    register_class(LYT_BKMIX);
    Object.lytools=PointerProperty(type=LYT_MixObjSettings);
    Material.lytools=PointerProperty(type=LYT_MixMatSettings);

def unregister():
    del Object.lytools;
    del Material.lytools;
    unregister_class(LYT_BKMIX);
    unregister_class(LYT_BKMATID);
    unregister_class(LYT_mixingPanel);
    unregister_class(LYT_MixMatSettings);
    unregister_class(LYT_MixObjSettings);

#   ---     ---     ---     ---     ---