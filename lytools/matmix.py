import bpy, os; import numpy as np;

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

    ob.lytools.par=cl;
    ob.name=f"{cl.name}_MIX"; ob.data.name=ob.name;

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

        cmat.name=(ob.lytools.par.name)+f'_COLORMASK{x}'; i=0; j=0;
        ob.data.materials[x]=cmat; nodes=cmat.node_tree.nodes;

        for mat in me.materials:
            omat=me.materials[j];
            nodes[f"IM{i}"].image=omat.node_tree.nodes["ALBEDO"].image;

            i=0 if i==3 else i+1; j+=1;

    for i in range(len(ob.data.materials)-1, -1, -1):
        ob.lytools.mix_idex=i;

    cl.select=0;

#   ---     ---     ---     ---     ---

def STALPHA(col, alpha):
    a=np.array(col.pixels); b=np.array((alpha.pixels[:])[0::4]);
    a[3::4]=np.multiply(a[3::4], b); col.pixels=a;

def BKMIXMAT():

    rend=bpy.context.scene.render;
    ob=bpy.context.object;

#   ---     ---     ---     ---     ---
# set up

    rend.image_settings.file_format='PNG';
    rend.image_settings.color_mode='RGBA';

    folder=f"{ob.lytools.f0}\\textures\\{ob.lytools.par.name}"
    if not os.path.exists(folder): os.makedirs(folder);

    rtpath=f"{folder}\\{ob.lytools.par.name}_";

    rend.bake.use_selected_to_active=0;
    rend.engine='CYCLES';

    rend.bake.margin=int(ob.lytools.res/32);

#   ---     ---     ---     ---     ---
# loop thru mixes A

    print(f"Baking mix: ", end='', flush=1);
    for i in range(len(ob.data.materials)):

        mat=ob.data.materials[i]; ntree=mat.node_tree;
        cbake=ntree.nodes[f"CBAKE{i}"]; ntree.nodes.active=cbake;
        abake=ntree.nodes[f"ABAKE{i}"];

        cbake.image.generated_width=ob.lytools.res;
        cbake.image.generated_height=ob.lytools.res;
        abake.image.generated_width=ob.lytools.res;
        abake.image.generated_height=ob.lytools.res;

        mout=ntree.nodes["MATOUT"];
        cout=ntree.nodes["OUTCOLOR"];
        ntree.links.new(cout.outputs[0], mout.inputs[0]);

        cmix=ntree.nodes["MIXCOLOR"];
        amix=ntree.nodes["MIXALPHA"];

#   ---     ---     ---     ---     ---
# bake first three maps

    for key in ["albedo", "orm", "normal"]:

        print(f"{key}, ", end='', flush=1);

        for i in range(len(ob.data.materials)):
            mat=ob.data.materials[i]; ntree=mat.node_tree;
            for h in range(4):
                node=ntree.nodes[f"IM{h}"];
                if node.image.name != "DUMMY":
                    base=node.image.name.split("_")[0];
                    node.image=bpy.data.images[f"{base}_{key}"];

        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

        for i in range(len(ob.data.materials)):
            mat=ob.data.materials[i]; ntree=mat.node_tree;
            cbake=ntree.nodes[f"CBAKE{i}"];
            abake=ntree.nodes[f"ABAKE{i}"]; ntree.nodes.active=abake;

            impath=rtpath+f"{key}{i}.png";
            cbake.image.save_render(impath);

            amix=ntree.nodes["MIXALPHA"];
            cout=ntree.nodes["OUTCOLOR"];
            ntree.links.new(amix.outputs[0], cout.inputs[0]);

        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

        for i in range(len(ob.data.materials)):

            mat=ob.data.materials[i]; ntree=mat.node_tree;
            cbake=ntree.nodes[f"CBAKE{i}"];
            abake=ntree.nodes[f"ABAKE{i}"];

            impath=rtpath+f"{key}{i}.png";
            cbake.image.source='FILE';
            cbake.image.filepath=impath;

            STALPHA(cbake.image, abake.image);
            cbake.image.save_render(impath);

            cbake.image.source='GENERATED';
            ntree.nodes.active=cbake;

            cmix=ntree.nodes["MIXCOLOR"];
            cout=ntree.nodes["OUTCOLOR"];
            ntree.links.new(cmix.outputs[0], cout.inputs[0]);

#   ---     ---     ---     ---     ---
# set fresnel out and bake

    print("fresnel... ");

    for i in range(len(ob.data.materials)):

        mat=ob.data.materials[i]; ntree=mat.node_tree;
        fmix=ntree.nodes["FRESNELMIX"];

        for h in range(4):

            node=ntree.nodes[f"IM{h}"];
            if node.image.name != "DUMMY":
                base=node.image.name.split("_")[0];
                basemat=bpy.data.materials[base];
                v=basemat.node_tree.nodes["SHADER"].inputs[7].default_value;
                fmix.inputs[4+h].default_value=v;

        ntree.links.new(fmix.outputs[0], ntree.nodes["MATOUT"].inputs[0]);

    SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

    for i in range(len(ob.data.materials)):
        mat=ob.data.materials[i]; ntree=mat.node_tree;

        cbake=ntree.nodes[f"CBAKE{i}"];
        cbake.image.save_render(rtpath+f"fresnel{i}.png");

        cmix=ntree.nodes["MIXCOLOR"];
        cout=ntree.nodes["OUTCOLOR"];
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
# create copy for unify mix

    cl=bpy.context.scene.objects.link(ob.copy()).object;
    cl.data=cl.data.copy();

    ob.name, cl.name = cl.name, ob.name;
    ob.data, cl.data = cl.data, ob.data;

    for key, _key in zip(ob.lytools.__dict__.keys(), cl.lytools.__dict__.keys()):
        setattr(cl.lytools, key, cl.lytools[key]);
        setattr(ob.lytools, _key, ob.lytools[_key]);

    ob.name=f"{cl.lytools.par.name}_UNI"; ob.data.name=ob.name;

    for _ in range(len(cl.data.materials)-1):
        ob.active_material_index=0;
        bpy.ops.object.material_slot_remove();

    cmat=bpy.data.materials["COLORMASKING"].copy();
    cmat.name=f"{ob.lytools.par.name}_KOLORMASK_UNIFY";
    ob.data.materials[0]=cmat; nodes=cmat.node_tree.nodes;

    nodes["Attribute"].attribute_name="Mix";

    for i in range(len(cl.data.materials)):
        imnode=nodes[f"IM{i}"]; imname=f"{ob.lytools.par.name}{i}";
        if imname not in bpy.data.images:
            im=bpy.data.images.new(imname, height=ob.lytools.res, width=ob.lytools.res);
            im.source='FILE'; im.filepath=f"{rtpath}albedo{i}.png";

        imnode.image=im;

    cl.select=0;

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

    par=PointerProperty(type=Object);
    final=PointerProperty(type=Object);

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