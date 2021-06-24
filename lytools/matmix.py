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

MATNAMES=[];

MATIDS=([

    (0,0,0),
    (0,0,1),
    (0,1,0),
    (1,0,0)

]);

#   ---     ---     ---     ---     ---

def BKMATIDS(me):

    global MATNAMES; MATNAMES=["" for _ in range(16)];

    rend=bpy.context.scene.render;
    rend.bake.cage_extrusion=10;

#   ---     ---     ---     ---     ---
# assign solid colors to material slots

    i=0; h=1;
    for mat in me.materials:
        j=i+(4*(h-1)); MATNAMES[j]=mat.name;
        i=0 if i==3 else i+1;
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

        cmat.name=(ob.name)+'_COLORMASK'; i=0; j=0;
        ob.data.materials[x]=cmat; nodes=cmat.node_tree.nodes;

        for mat in me.materials:
            omat=me.materials[j];
            nodes[f"IM{i}"].image=omat.node_tree.nodes["ALBEDO"].image;

            i=0 if i==3 else i+1; j+=1;

    for i in range(len(ob.data.materials)-1, -1, -1):
        ob.lyt_mix_idex=i;

#   ---     ---     ---     ---     ---

def BKMIX():

    mat=bpy.context.object.active_material;
    ntree=mat.node_tree;

    aout, cout = ntree.nodes["OUTALPHA"], ntree.nodes["OUTCOLOR"];
    nmix, cmix = ntree.nodes["MIXNORMAL"], ntree.nodes["MIXCOLOR"];
    omix, nbaketo = ntree.nodes["MIXORM"], ntree.nodes["NBAKETO"];
    fmix, amix = ntree.nodes["FRESNELMIX"], ntree.nodes["MIXALPHA"];
    aobaketo, ncombined = ntree.nodes["AOBAKE"], ntree.nodes["NCOMB"];
    afac, result = ntree.nodes["FACALPHA"], ntree.nodes["RESULT"];

#   ---     ---     ---     ---     ---
# bake albedo...

    

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
    if self.lyt_mix_idex > len(self.data.materials)-1:
        self.lyt_mix_idex = len(self.data.materials)-1;
        return;

    mat=self.active_material; ntree=mat.node_tree;
    out, act=ntree.nodes["MATOUT"], ntree.nodes["INACTIVE"];
    ntree.links.new(act.outputs[0], out.inputs[0]);

    self.active_material_index=self.lyt_mix_idex;

    mat=self.active_material; ntree=mat.node_tree;
    out, act=ntree.nodes["MATOUT"], ntree.nodes["ACTIVE"];
    ntree.links.new(act.outputs[0], out.inputs[0]);

    GTMIXMAT(self, context);

#   ---     ---     ---     ---     ---

def GTMIXMAT(self, context):

    mat=context.object.active_material;
    lyt=mat.lytools; idex=lyt.cur; ntree=mat.node_tree;

    lyt.upchk=1; lyt.name=MATNAMES[idex+(4*context.object.active_material_index)];

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

        if len(context.object.data.materials) > 16:
            self.report(
                {'WARNING'},
                f"Object {context.object.name} has more than 16 materials; op aborted"
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

        
        if "_COLORMASK" in context.object.active_material.name:

            mat=context.object.active_material; lyt=mat.lytools;
            layout.separator();

            row=layout.row(); row.prop(context.object, "lyt_mix_idex");

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
    Object.lyt_mix_idex=IntProperty(

        name        = "Mix",
        description = "Current sub-material container",
        update      = UPMIXPAR,

        default     = 0,
        min         = 0,
        max         = 3

    );

def unregister():
    del Object.lyt_mix_idex;
    del Material.lytools;
    unregister_class(LYT_BKMATID);
    unregister_class(LYT_mixingPanel);
    unregister_class(LYT_MixMatSettings);

#   ---     ---     ---     ---     ---