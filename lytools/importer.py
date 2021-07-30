import bpy, os, struct;

from bpy.types import Panel, Operator, PropertyGroup, Scene;
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

DROOT="\\".join(__file__.split("\\")[:-2])+'\\data';

DTYPES=([

    ('objects',     'Object',   'Look for object data-blocks'   ),
    ('meshes',      'Mesh',     'Look for mesh data-blocks'     ),
    ('materials',   'Material', 'Look for material data-blocks' )

]);

LDMEM={'APD':{}, 'LNK':{}};

#   ---     ---     ---     ---     ---
# dull way of making sure certain datablocks are __linked__ from
# certain locations within the data folder on *every single*
# non-tool specific blendfile (basically all files derived from _asset.blend)

PRMBLKS={                                   # add entries to this dict at your own peril;

    "node_groups":["LyShader"]

};

def PERMABLOCKS():
    w=list(os.walk(DROOT)); folds=[w[0][0]+'\\'+s for s in w[0][1]]; blends=[];

    for fold in folds:
        w=list(os.walk(fold));
        for pis in w:
            for s in pis[2]:
                if ".blend" in s and ".blend1" not in s:
                    blends.append(pis[0]+'\\'+s);

    for blend in blends:
        if "matlib.blend" in blend:
            with bpy.data.libraries.load(blend, link=1, relative=1) \
            as (data_from, data_to):

                for cath, blocks in PRMBLKS.items():
                    blib=[b for b in getattr(data_from, cath) if b in blocks];
                    for block in blib:
                        if block not in getattr(data_to, cath):
                            getattr(data_to, cath).append(block);

#   ---     ---     ---     ---     ---

def WPIMP():
    path=bpy.context.blend_data.filepath.replace(".blend", ".lymp");
    n=bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "");

    d="{'APD':{}, 'LNK':{}}"; d=eval(d);

    with open(path, 'w+') as file:
        file.write(str(d));

    global LDMEM; LDMEM=d; bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);

def SVIMP(block, cat, src, lnk=0):

    path=bpy.context.blend_data.filepath.replace(".blend", ".lymp");
    n=bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "");

    if not os.path.exists(path):
        d="{'APD':{}, 'LNK':{}}";

    else:
        with open(path, 'r') as file:
            d=file.read();

    d=eval(d);
    top='LNK' if lnk else 'APD';

    if src not in d[top]:
        d[top][src]={};

    if cat not in d[top][src]:
        d[top][src][cat]=[];

    notif=0;
    if (not lnk) or (lnk and block not in d[top][src][cat]):
        d[top][src][cat].append(block);
    else:
        notif=1;

    with open(path, 'w+') as file:
        file.write(str(d));

    global LDMEM; LDMEM=d;

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);
    return notif;


#   ---     ---     ---     ---     ---

def GTSCN_F0(self, context):
    w=list(os.walk(DROOT));
    return [tuple([w[0][0]+'\\'+s, s.capitalize(), '']) for s in w[0][1]];

def GTSCN_F1(self, context):
    imp=bpy.context.scene.lymport;
    w=list(os.walk(imp.f0)); l=[];

    for pis in w:
        for s in pis[2]:
            if ".blend" in s and ".blend1" not in s:
                l.append( tuple([

                    pis[0]+'\\'+s,
                    s.capitalize().replace(".blend", ""),
                    ''

                ]) );

    return l;

def GTSCN_REL(self, context):

    imp=bpy.context.scene.lymport;
    i=0; fs=imp.f1.split("\\");
    for s in fs:
        if s=='data': break;
        i+=1;

    imp.rel = "\\".join(fs[i:]);

#   ---     ---     ---     ---     ---

def GTBLNAMES(self, context):

    names=[]; imp=context.scene.lymport;

    with bpy.data.libraries.load(imp.f1, link=1, relative=1) as (data_from, _):
        names = [name for name in getattr(data_from, imp.f2)];

    return [tuple([n, n, n]) for n in names];

#   ---     ---     ---     ---     ---

def GTBLOCK(lnk):

    imp=bpy.context.scene.lymport;

    with bpy.data.libraries.load(imp.f1, link=lnk, relative=1) as (data_from, data_to):
        blocks=getattr(data_from, imp.f2);
        blocks=[x for x in blocks if x == imp.f3];

        setattr(data_to, imp.f2, blocks);

    ob=getattr(data_to, imp.f2)[0];
    if imp.f2=='objects':
        l_ob=bpy.context.scene.objects.link(ob).object;
        l_ob.location=bpy.context.scene.cursor_location;

    GTSCN_REL(None, bpy.context); block_name=ob.name;
    return SVIMP(block_name, imp.f2, imp.rel, lnk);

def DLBLOCK(target, lnk):

    global LDMEM; imp=bpy.context.scene.lymport;
    GTSCN_REL(None, bpy.context); d=LDMEM;
    buck=getattr(bpy.data, imp.f2);

    top='LNK' if lnk else 'APD';

    if target=="$ALL":
        for n in d[top][imp.rel][imp.f2]:
            buck.remove(buck[n]);

        d[top][imp.rel][imp.f2]=[];

    else:
        buck.remove(buck[target]);
        d[top][imp.rel][imp.f2].remove(target);

    path=bpy.context.blend_data.filepath.replace(".blend", ".lymp");
    with open(path, 'w+') as file:
        file.write(str(d));

    LDMEM=d; bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

#   ---     ---     ---     ---     ---

class LYT_LIBGET(Operator):

    bl_idname      = "lymporter.libget";
    bl_label       = "Links selected data-block from blendfile";

    bl_description = "Looks for the selected datablock and links it";

    lnk            = BoolProperty(default=1);

#   ---     ---     ---     ---     ---

    def execute(self, context):
        notif=GTBLOCK(self.lnk);

        if notif:
            self.report(
                {'WARNING'},
                f"Data-block {context.scene.lymport.f3} already linked!"
            );

        return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_LIBDEL(Operator):

    bl_idname      = "lymporter.libdel";
    bl_label       = "Clear linked data-block from current blendfile";

    bl_description = "Removes linked atablocks from the current blendfile";

    lnk            = BoolProperty(default=1);
    target         = StringProperty(default='$ALL');

#   ---     ---     ---     ---     ---

    def execute(self, context):
        DLBLOCK(self.target, self.lnk); return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_ImporterSettings(PropertyGroup):

    rel=StringProperty(

        name        = "",
        description = "",
        default     = ""

    );

    f0=EnumProperty (

        items       = GTSCN_F0,

        name        = "Cathegory",
        description = "Root folder to pick from"

    );

    f1=EnumProperty (

        items       = GTSCN_F1,
        update      = GTSCN_REL,

        name        = "File",
        description = "Blend file to work with"

    );

    f2=EnumProperty (

        items       = DTYPES,
        default     = 'meshes',

        name        = "Data",
        description = "Type of block to import"

    );

    f3=EnumProperty (

        items       = GTBLNAMES,

        name        = "Block",
        description = "Datablock to import"

    );

#   ---     ---     ---     ---     ---

class LYT_importPanel(Panel):

    bl_label       = 'LYT IMPORT';
    bl_idname      = 'LYT_importPanel';
    bl_space_type  = 'PROPERTIES';
    bl_region_type = 'WINDOW';
    bl_context     = 'render_layer';
    bl_category    = 'LYT';

#   ---     ---     ---     ---     ---
    
    @classmethod
    def poll(cls, context):
        return context.scene != None;

    def draw(self, context):
        layout=self.layout; imp=context.scene.lymport;

        row=layout.row(); row.prop(imp, "f0");
        cat_ready=0; imp_ready=0;

        if imp.f0:
            row=layout.row(); row.prop(imp, "f1");

            if imp.f1:
                row=layout.row(); row.prop(imp, "f2"); cat_ready=1;

                if imp.f2:
                    row=layout.row(); row.prop(imp, "f3"); imp_ready=1;

        if imp_ready:

            layout.separator(); row=layout.row(1);

            oppy=row.operator("lymporter.libget", text="LINK", icon="LINK_BLEND");
            oppy.lnk=1;

            oppy=row.operator("lymporter.libget", text="APPEND", icon="APPEND_BLEND");
            oppy.lnk=0;

        if cat_ready:
            layout.separator(); d=LDMEM;

            row=layout.row(); row.label(f"Linked {imp.f2}:");
            if imp.rel in d['LNK']:
                if imp.f2 in d['LNK'][imp.rel]:
                    for key in d['LNK'][imp.rel][imp.f2]:
                        row=layout.row(); row.label(key);
                        oppy=row.operator(
                            "lymporter.libdel",
                            text="REMOVE",
                            icon="CANCEL"
                        );

                        oppy.target=key;
                        oppy.lnk=1;

            layout.separator();

            row=layout.row(); row.label(f"Appended {imp.f2}:");
            if imp.rel in d['APD']:
                if imp.f2 in d['APD'][imp.rel]:
                    for key in d['APD'][imp.rel][imp.f2]:
                        row=layout.row(); row.label(key);
                        oppy=row.operator(
                            "lymporter.libdel",
                            text="REMOVE",
                            icon="CANCEL"
                        );

                        oppy.target=key;
                        oppy.lnk=0;

        if hasattr(bpy.ops, "lytbkr"):
            if hasattr(bpy.ops.lytbkr, "clnup"):
                layout.separator(); row=layout.row();
                row.operator("lytbkr.clnup", text="CLEAN UP", icon="LOAD_FACTORY");

#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_ImporterSettings);
    register_class(LYT_LIBGET);
    register_class(LYT_LIBDEL);
    register_class(LYT_importPanel);
    Scene.lymport=PointerProperty(type=LYT_ImporterSettings);

def unregister():
    del Scene.lymport;
    unregister_class(LYT_importPanel);
    register_class(LYT_LIBDEL);
    unregister_class(LYT_LIBGET);
    unregister_class(LYT_ImporterSettings);

#   ---     ---     ---     ---     ---