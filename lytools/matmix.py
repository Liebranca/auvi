import bpy, bmesh, os; import numpy as np;

from bpy.types import Panel, Operator, PropertyGroup, Object, Material, Scene;
from bpy.utils import register_class, unregister_class;

from .blmod    import SHUT_OPS;
from .importer import WPIMP;

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

    i=0; h=0;
    for mat in me.materials:
        if not i: h+=1;
        j=i+(4*(h-1)); i=0 if i==3 else i+1;

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

    tot=len(ob.data.materials); j=0;
    for x in range(h):
        cmat=bpy.data.materials["COLORMASKING"].copy();

        if x:
            for y in range(4):
                imnode=cmat.node_tree.nodes[f"IM{y}"];
                imnode.image=imnode.image.copy();

        cmat.name=(ob.lytools.par.name)+f'_COLORMASK{x}'; i=0;
        ob.data.materials[x]=cmat; nodes=cmat.node_tree.nodes;
        jp=j+4 if len(me.materials)-j > 4 else len(me.materials);

        for mat in me.materials[j:jp]:
            nodes[f"IM{i}"].image.filepath=mat.node_tree.nodes["ALBEDO"].image.filepath;
            i=0 if i==3 else i+1; j+=1;

    for i in range(len(ob.data.materials)-1, -1, -1):
        ob.lytools.mix_idex=i;

    cl.select=0; ob.data.vertex_colors.active_index=0;

#   ---     ---     ---     ---     ---

def STALPHA(col, alpha):
    a=np.array(col.pixels); b=np.array((alpha.pixels[:])[0::4]);
    a[3::4]=0; a[3::4]=np.add(a[3::4], b); col.pixels=a;

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

    for key in ["albedo", "orm", "normal", "curv"]:

        print(f"{key}, ", end='', flush=1);

        for i in range(len(ob.data.materials)):
            mat=ob.data.materials[i]; ntree=mat.node_tree;
            for h in range(4):
                node=ntree.nodes[f"IM{h}"];
                if node.image.filepath:
                    path_split=node.image.filepath.split("\\");
                    base=(path_split[-1]).split("_")[0]; path="\\".join(path_split[:-1]);
                    node.image.filepath=f"{path}\\{base}_{key}.png";
                    node.image.use_alpha=0;

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

            for h in range(4):
                node=ntree.nodes[f"IM{h}"];
                if node.image.source: node.image.use_alpha=1;

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
# walkback changes

    for i in range(len(ob.data.materials)):
        mat=ob.data.materials[i]; ntree=mat.node_tree;
        for h in range(4):

            node=ntree.nodes[f"IM{h}"];
            if node.image.filepath:
                path_split=node.image.filepath.split("\\");
                base=(path_split[-1]).split("_")[0]; path="\\".join(path_split[:-1]);
                node.image.filepath=f"{path}\\{base}_albedo.png";

        ntree.links.new(ntree.nodes["OUTCOLOR"].outputs[0], ntree.nodes["MATOUT"].inputs[0]);

    ob.lytools.mix_idex=0;

#   ---     ---     ---     ---     ---
# create copy for unify mix

    cl=bpy.context.scene.objects.link(ob.copy()).object;
    cl.data=cl.data.copy();

    ob.name, cl.name = cl.name, ob.name;
    ob.data, cl.data = cl.data, ob.data;

    ob.name=f"{cl.lytools.par.name}_UNI"; ob.data.name=ob.name;

    for _ in range(len(cl.data.materials)-1):
        ob.active_material_index=0;
        bpy.ops.object.material_slot_remove();

    cmat=bpy.data.materials["COLORMASKING"].copy();
    cmat.name=f"{ob.lytools.par.name}_KOLORMASK";
    ob.data.materials[0]=cmat; nodes=cmat.node_tree.nodes;

    nodes["Attribute"].attribute_name="Mix";

    for i in range(len(cl.data.materials)):
        imnode=nodes[f"IM{i}"]; imname=f"{ob.lytools.par.name}{i}";
        if imname not in bpy.data.images:
            im=bpy.data.images.new(imname, height=ob.lytools.res, width=ob.lytools.res);
            im.source='FILE'; im.filepath=f"{rtpath}albedo{i}.png";

        imnode.image=bpy.data.images[imname];

    for poly in ob.data.polygons:
        poly.use_smooth=False;

    cl.select=0;

def BYETEMPS(path):

    files=list(os.walk(path))[0][2];

    for file in files:
        filepath=f"{path}\\{file}"; x=0;

        for i in range(4):
            if file.endswith(f"{i}.png"):
                os.system(f"del {filepath}");
                x=1; break;

        if x: continue;

        elif file.endswith("_hpnormal.png") or file.endswith("_hpao.png"):
            os.system(f"del {filepath}");

        elif file.endswith("curv_col.png"):
            os.system(f"del {filepath}");

#   ---     ---     ---     ---     ---

def BKPAR():

    ob=bpy.context.object; par=ob.lytools.hp; self_baked=ob==par;
    auto_smooth=ob.data.use_auto_smooth; mod_shrend=[];

    for obj in bpy.context.selected_objects:
        obj.select=0;

    ob.select=1; par.select=1;
    bpy.context.scene.objects.active=ob;

    if self_baked:

        par=bpy.context.scene.objects.link(ob.copy()).object;
        par.data=par.data.copy();

        if auto_smooth:
            ob.data.use_auto_smooth=0;

        for mod in ob.modifiers:
            mod_shrend.append(mod.show_render); mod.show_render=0;

        bm=bmesh.new();
        bm.from_object(ob, bpy.context.scene, face_normals=True);
        bm.to_mesh(par.data);
        bm.free();

    folder=f"{ob.lytools.f0}\\textures\\{ob.name}"
    if not os.path.exists(folder): os.makedirs(folder);

    rtpath=f"{folder}\\{ob.name}_";

#   ---     ---     ---     ---     ---
# setup

    res=ob.lytools.res;

    rend=bpy.context.scene.render;
    old_e=rend.engine; rend.engine='BLENDER_RENDER';

    rend.bake.margin=int(res/32);

    imname=ob.name+"_hpnormal";
    if imname not in bpy.data.images:
        bpy.data.images.new(imname, height=2, width=2);

    baketo=bpy.data.images[imname];
    baketo.generated_width=res*ob.lytools.res_aa;
    baketo.generated_height=res*ob.lytools.res_aa;

#   ---     ---     ---     ---     ---
# set image and bake normal

    uv_area=bpy.data.screens["UV Editing"].areas[1];
    uv_area.spaces.active.image=baketo;

    for uvface in ob.data.uv_textures.active.data:
        uvface.image=baketo;

    rend.use_bake_to_vertex_color=0;
    rend.use_bake_selected_to_active=1;
    rend.bake_distance=1.0; rend.bake_bias=0.1;

    rend.bake_type='NORMALS'; rend.bake_normal_space='TANGENT';

    SHUT_OPS(bpy.ops.object.bake_image);
    baketo.scale(res, res); baketo.save_render(rtpath+"hpnormal.png");

#   ---     ---     ---     ---     ---
# swap out and bake AO

    imname=ob.name+"_hpao";
    if imname not in bpy.data.images:
        bpy.data.images.new(imname, height=2, width=2);

    baketo=bpy.data.images[imname];
    baketo.generated_width=res*ob.lytools.res_aa;
    baketo.generated_height=res*ob.lytools.res_aa;

    rend.bake_type='AO';
    rend.use_bake_normalize=1; rend.bake_bias=2.0;

    uv_area.spaces.active.image=baketo;

    for uvface in ob.data.uv_textures.active.data:
        uvface.image=baketo;

    SHUT_OPS(bpy.ops.object.bake_image);
    baketo.scale(res, res); baketo.save_render(rtpath+"hpao.png");

#   ---     ---     ---     ---     ---
# walkback changes

    rend.use_bake_selected_to_active=1;
    rend.engine=old_e; par.select=0;

    if self_baked:
        bpy.data.meshes.remove(par.data);
        ob.data.use_auto_smooth=auto_smooth;

        i=0;
        for mod in ob.modifiers:
            mod.show_render=mod_shrend[i];

def BKUNI():

    rend=bpy.context.scene.render;
    ob=bpy.context.object; par=ob.lytools.par;

#   ---     ---     ---     ---     ---
# set up

    rend.image_settings.file_format='PNG';
    rend.image_settings.color_mode='RGBA';

    folder=f"{par.lytools.f0}\\textures\\{par.name}"
    if not os.path.exists(folder): os.makedirs(folder);

    rtpath=f"{folder}\\{par.name}_";

    rend.bake.use_selected_to_active=0;
    rend.engine='CYCLES';

    rend.bake.margin=int(par.lytools.res/32);

#   ---     ---     ---     ---     ---
# get nodes

    print(f"Baking unified mix: ", end='', flush=1);

    mat=ob.data.materials[0]; ntree=mat.node_tree;
    cbake=ntree.nodes["CBAKE0"]; ntree.nodes.active=cbake;
    abake=ntree.nodes["ABAKE0"];

    cbake.image.generated_width=ob.lytools.res;
    cbake.image.generated_height=ob.lytools.res;
    abake.image.generated_width=ob.lytools.res;
    abake.image.generated_height=ob.lytools.res;

    mout=ntree.nodes["MATOUT"];
    cout=ntree.nodes["OUTCOLOR"];
    ntree.links.new(cout.outputs[0], mout.inputs[0]);

    cmix=ntree.nodes["MIXCOLOR"];
    amix=ntree.nodes["MIXALPHA"];
    nmix=ntree.nodes["MIXNORMAL"];
    omix=ntree.nodes["MIXORM"];

#   ---     ---     ---     ---     ---
# initial bake

    for key in ["albedo", "orm", "normal", "curv"]:

        print(f"{key}, ", end='', flush=1);

        for h in range(4):
            node=ntree.nodes[f"IM{h}"];
            if node.image.filepath:
                base=par.name; imname=f"{base}_{key}{h}";
                if imname not in bpy.data.images:
                    bpy.data.images.new(imname, height=2, width=2);

                node.image=bpy.data.images[imname];

                node.image.source='FILE'; node.image.use_alpha=0;
                node.image.filepath=rtpath+f"{key}{h}.png"

        if key=="normal":
            hpbk_path=rtpath+"hpnormal.png";
            if os.path.exists(hpbk_path):

                base=par.name; imname=f"{base}_hpnormal";
                if imname not in bpy.data.images:
                    im=bpy.data.images.new(imname, height=2, width=2);

                node=ntree.nodes["NBAKE"];
                node.image=bpy.data.images[imname];

                node.image.source='FILE';
                node.image.filepath=hpbk_path;

                ntree.links.new(nmix.outputs[0], cout.inputs[0]);

        elif key=="orm":
            hpbk_path=rtpath+"hpao.png";
            if os.path.exists(hpbk_path):

                base=par.name; imname=f"{base}_hpao";
                if imname not in bpy.data.images:
                    im=bpy.data.images.new(imname, height=2, width=2);

                node=ntree.nodes["AOBAKE"];
                node.image=bpy.data.images[imname];

                node.image.source='FILE';
                node.image.filepath=hpbk_path;

                ntree.links.new(omix.outputs[0], cout.inputs[0]);

        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

        ntree.nodes.active=abake;

        impath=rtpath+f"{key}.png";
        cbake.image.save_render(impath);

        for h in range(4):
            node=ntree.nodes[f"IM{h}"];
            if node.image.filepath: node.image.use_alpha=1;

        ntree.links.new(amix.outputs[0], cout.inputs[0]);
        SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

        cbake.image.source='FILE';
        cbake.image.filepath=impath;
        STALPHA(cbake.image, abake.image);
        cbake.image.save_render(impath);

        cbake.image.source='GENERATED';
        ntree.nodes.active=cbake;

        ntree.links.new(cmix.outputs[0], cout.inputs[0]);

#   ---     ---     ---     ---     ---
# bake curv+fresnel

    print("combining curv... ");

    ncomb=ntree.nodes["NCOMB"];
    ncomb.image.source='FILE';
    ncomb.image.filepath=rtpath+"normal.png";
    ncomb.image.use_alpha=0;

    bcurv=ntree.nodes["BCURV"];
    bcurv.image.source='FILE';
    bcurv.image.filepath=rtpath+"curv.png"
    ncomb.image.use_alpha=0;

    ntree.nodes.active=cbake;
    scurvy=ntree.nodes["SCURVY"];

    ntree.links.new(scurvy.outputs[0], cout.inputs[0]);
    SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

    ntree.nodes.active=abake; impath=rtpath+f"curv_col.png";
    cbake.image.save_render(impath);

    bcurv.image.use_alpha=1;
    ntree.links.new(bcurv.outputs[1], cout.inputs[0]);
    SHUT_OPS(bpy.ops.object.bake, [], {'type':'EMIT'});

    cbake.image.source='FILE';
    cbake.image.filepath=impath;
    STALPHA(cbake.image, abake.image);
    cbake.image.save_render(rtpath+f"curv.png");

    ntree.links.new(cmix.outputs[0], cout.inputs[0]);

#   ---     ---     ---     ---     ---
# walkback changes

    for h in range(4):

        node=ntree.nodes[f"IM{h}"];
        if node.image.filepath:
            base=par.name; imname=f"{base}_albedo{h}";
            node.image=bpy.data.images[imname];
            #node.image.reload();

    ntree.links.new(ntree.nodes["OUTCOLOR"].outputs[0], ntree.nodes["MATOUT"].inputs[0]);

def CLNUP():
    images=[im for im in bpy.data.images if 'IM' not in im.name and 'BAKE' not in im.name];
    for image in images: bpy.data.images.remove(image);

    for material in bpy.data.materials:
        if material.name!="COLORMASKING":
            bpy.data.materials.remove(material);

    for mesh in bpy.data.meshes: bpy.data.meshes.remove(mesh);

    WPIMP();

    for image in bpy.data.images:
        if 'IM' not in image.name: image.source='GENERATED';

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);

#   ---     ---     ---     ---     ---

def GTOTHERS(self, context):
    return [tuple(["_", "NONE", ""]), tuple([context.object.name, "SELF", ""])]\
           +[tuple([ob.name, ob.name, ""]) for ob in bpy.data.objects
            if ob != context.object and isinstance(ob.data, bpy.types.Mesh)]

def STPAR(self, context):
    self.hp=bpy.data.objects[self.hp_name] if self.hp_name != '_' else None;

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

    res_aa=IntProperty(

        name        = "HP Scale",
        description = "Smooths the high poly bake by rendering at a larger size",

        default     = 1,
        min         = 1,
        max         = 16

    );

    par=PointerProperty(type=Object);
    hp=PointerProperty(type=Object);

    hp_name=EnumProperty(

        items       = GTOTHERS,
        update      = STPAR,

        name        = "High poly",
        description = "Select high poly version for AO and normal baking"

    );

#   ---     ---     ---     ---     ---

class LYT_BKPAR(Operator):

    bl_idname      = "lytbkr.bkpar";
    bl_label       = "Bakes AO and normal of selected high-poly";

    bl_description = "Bake AO and normal of selected high-poly mesh to active object";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        BKPAR(); return {'FINISHED'};

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

class LYT_BKUNI(Operator):

    bl_idname      = "lytbkr.bkuni";
    bl_label       = "Bakes unified material";

    bl_description = "Bake unified material from the result of multiple mixes";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        BKUNI(); return {'FINISHED'};

class LYT_CLNUP(Operator):

    bl_idname      = "lytbkr.clnup";
    bl_label       = "Wipes the file clean";

    bl_description = "NO UNDO: cleans up blend and saves";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        CLNUP(); return {'FINISHED'};

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
        layout=self.layout;

        row=layout.row();
        row.prop(context.object.lytools, "f0");
        row.prop(context.object.lytools, "res");

        draw_bkmatid_button=len([

            1 for m in context.object.data.materials
            if "_COLORMASK" in m.name
            or "_KOLORMASK" in m.name

        ]) == 0;

        if draw_bkmatid_button:

            layout.separator(); row=layout.row();
            row.prop(context.object.lytools, "hp_name");

            if context.object.lytools.hp:
                row=layout.row(); row.prop(context.object.lytools, "res_aa");
                row.operator("lytbkr.bkpar", text="BAKE HI-POLY", icon="MOD_SUBSURF");

            layout.separator(); row=layout.row();
            row.operator("lytbkr.bkmatid", text="BAKE MATERIAL IDS", icon="COLOR");

        elif "_COLORMASK" in context.object.active_material.name:

            mat=context.object.active_material; lyt=mat.lytools;
            layout.separator();

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

            layout.separator(); row=layout.row();
            row.operator("lytbkr.bkmix", text="BAKE MIX", icon="RENDER_STILL");

        elif "_KOLORMASK" in context.object.active_material.name:
            mat=context.object.active_material; lyt=mat.lytools;
            layout.separator(); row=layout.row();

            name=lyt.name if lyt.name else "EMPTY";
            row.label("Current: "); row.prop(lyt, "cur", text=name);
            row=layout.row(); row.prop(lyt, "tol");

            row=layout.row();
            row.operator("lytbkr.bkuni", text="UNIFY", icon="RENDER_STILL");

#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_MixObjSettings);
    register_class(LYT_MixMatSettings);
    register_class(LYT_mixingPanel);
    register_class(LYT_BKMATID);
    register_class(LYT_BKMIX);
    register_class(LYT_BKPAR);
    register_class(LYT_BKUNI);
    register_class(LYT_CLNUP);
    Object.lytools=PointerProperty(type=LYT_MixObjSettings);
    Material.lytools=PointerProperty(type=LYT_MixMatSettings);

def unregister():
    del Object.lytools;
    del Material.lytools;
    unregister_class(LYT_CLNUP);
    unregister_class(LYT_BKUNI);
    unregister_class(LYT_BKPAR);
    unregister_class(LYT_BKMIX);
    unregister_class(LYT_BKMATID);
    unregister_class(LYT_mixingPanel);
    unregister_class(LYT_MixMatSettings);
    unregister_class(LYT_MixObjSettings);

#   ---     ---     ---     ---     ---