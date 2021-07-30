import bpy, os, struct;

from bpy.types import Panel, Operator;
from bpy.utils import register_class, unregister_class;

from .         import NTBLKMGK, DLBLKMGK, UTJOJ, INJOJ;

#   ---     ---     ---     ---     ---

COMP_LEVELS={                               # level of precision used for each imtype
                                            # higher is more accurate producing bigger files
                                            # lower is more compression decay, but way lighter

    "a":4,                                  # albedo:   3-6, 7 with colorbug disabled
    "n":1,                                  # normal:   1-6
    "c":0,                                  # curvature 'precisionless' multi-grayscale
    "o":0                                   # orm       ^idem

};

#   ---     ---     ---     ---     ---

def TEXPACK():

    if "JOJ_EXPORT_DUMMY" not in bpy.data.images:
        im=bpy.data.images.new("JOJ_EXPORT_DUMMY", 64, 64);
        im.source='FILE'; im.use_alpha=1;

    im=bpy.data.images["JOJ_EXPORT_DUMMY"];

    imp=bpy.context.scene.lymport;
    base=imp.f0+"\\textures";
    materials=list(os.walk(base))[0][1];

    NTBLKMGK(imp.f0);

    for mat in materials:
        textures=list(os.walk(base+'\\'+mat))[0][2]
        textures=[tex for tex in textures if tex.endswith(".png")];

        for tex in textures:
            im.filepath=f"{base}\\{mat}\\{tex}";

            i=0 if   mat == materials[0]   \
                and  tex == textures [0]   \
                else 1;

            if i: i=0x444f4e45 if   mat == materials[-1] \
                               and  tex == textures [-1] \
                               else 1;

            buff=bytearray(); dim=(im.size[0]**2)*4*4;
            buff.extend(struct.pack('%sf'%len(im.pixels), *im.pixels)[0:dim]);
            with open(imp.f0+"\\PIXDUMP.hx", 'wb') as file:
                sign=bytearray(16);
                for x in range(16): sign[x]=36;

                file.write(sign);
                file.write(buff);

            matid, texid=tex.split("_");

            level=COMP_LEVELS[texid[0]];

            texid=matid+'_'+texid[0];

            UTJOJ(i, im.size[0], level, texid);

    DLBLKMGK();

def TEXUNPACK():

    imp=bpy.context.scene.lymport;
    base=imp.f0+"\\textures";
    NTBLKMGK(imp.f0);

    rend=bpy.context.scene.render;
    rend.image_settings.file_format='PNG';
    rend.image_settings.color_mode='RGBA';

    try:
        with open(imp.f0+"\\PIXDUMP.hx", 'wb') as file:
            sign=bytearray(16);
            for x in range(16): sign[x]=36;
            file.write(sign);

        count=0;
        with open(imp.f0+"\\MATE.joj", 'rb') as file:
            file.seek(24); x=file.read(4);
            count=struct.unpack("<i", x)[0];

        for i in range(count):

            INJOJ(i);
            with open(imp.f0+"\\PIXDUMP.hx", 'rb') as file:

                buff=file.read(20);
                name=(struct.unpack("%ss"%int(len(buff)), buff))[0].decode('utf-8');

                buff=file.read(4);
                dim=struct.unpack("<i", buff)[0];

                file.read(4); # discard fracl

                buff=file.read();
                pixels=struct.unpack("<%sf"%int(len(buff)/4), buff);

                name, imtype=name.split('_')[:2]; imtype=imtype[0];
                imtype={'o':"orm", 'a':"albedo", 'n':"normal", 'c':"curv"}[imtype];

                if f"{name}_{imtype}" not in bpy.data.images:
                    im=bpy.data.images.new(f"{name}_{imtype}", alpha=1, height=dim, width=dim);

                im=bpy.data.images[f"{name}_{imtype}"];
                im.source='GENERATED'; im.use_alpha=1;
                im.alpha_mode = 'STRAIGHT';

                fpath=imp.f0+f"\\textures\\{name}";
                if not os.path.exists(fpath):
                    os.makedirs(fpath);

                fpath=f"{fpath}\\{name}_{imtype}.png";

                im.filepath_raw = fpath;
                im.file_format = 'PNG';

                im.save(); im.source='FILE'; im.scale(dim, dim);
                im.pixels[:]=pixels[0:len(im.pixels)]; im.save();

    finally:
        INJOJ(0x444f4e45);
        DLBLKMGK();

#   ---     ---     ---     ---     ---

class LYT_JOJPACK(Operator):

    bl_idname      = "lymporter.jojmk";
    bl_label       = "Packs textures into a JOJ file";

    bl_description = "Compress textures into JOJ using BlackMagic";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        TEXPACK(); return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_JOJUNPACK(Operator):

    bl_idname      = "lymporter.jojget";
    bl_label       = "Unpacks JOJ file";

    bl_description = "Extracts usable textures from JOJ";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        TEXUNPACK(); return {'FINISHED'};

#   ---     ---     ---     ---     ---

class LYT_packagesPanel(Panel):

    bl_label       = 'PACKAGES';
    bl_idname      = 'LYT_packagesPanel';
    bl_space_type  = 'PROPERTIES';
    bl_region_type = 'WINDOW';
    bl_context     = 'world';
    bl_category    = 'LYT';

#   ---     ---     ---     ---     ---
    
    @classmethod
    def poll(cls, context):
        return context.scene != None and hasattr(context.scene, "lymport");

    def draw(self, context):
        layout=self.layout; imp=context.scene.lymport;
        row=layout.row();
        row.label("Package: "); row.prop(imp, "f0", text="");

        layout.separator();

        if imp.f0:
            row=layout.row();
            row.operator("lymporter.jojmk", text="PACK TEXTURES", icon="UGLYPACKAGE");
            row.operator("lymporter.jojget", text="UNPACK TEXTURES", icon="PACKAGE");

#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_packagesPanel);
    register_class(LYT_JOJPACK);
    register_class(LYT_JOJUNPACK);

def unregister():
    register_class(LYT_JOJUNPACK);
    register_class(LYT_JOJPACK);
    unregister_class(LYT_packagesPanel);

#   ---     ---     ---     ---     ---