#!/usr/bin/python
# ---   *   ---   *   ---
# SPRITEBAKE
# Makes your sheets
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

from .Meta import *;
from .Char import get_anim_list;
from arcana.Xfer import ARPATH,DOS;

# ---   *   ---   *   ---
# remembers your config

def save_settings():

  r=bpy.context.scene.render;

  return [

    r.image_settings.file_format,
    r.image_settings.color_mode,

    r.use_file_extension,

    r.resolution_x,
    r.resolution_y,

    r.filter_size,
    r.film_transparent,

    r.filepath,

    bpy.context.scene.frame_current,

  ];

# ---   *   ---   *   ---
# ^resets them

def load_settings(data):

  r=bpy.context.scene.render;

  ( r.image_settings.file_format,
    r.image_settings.color_mode,

    r.use_file_extension,

    r.resolution_x,
    r.resolution_y,

    r.filter_size,
    r.film_transparent,

    r.filepath,

    bpy.context.scene.frame_current,

  )=data;

# ---   *   ---   *   ---
# overwrite scene settings with
# hardcoded DA sprite render stuff

def set_render_config():

  r  = bpy.context.scene.render;
  sb = bpy.context.scene.da_spritebake;

  r.image_settings.file_format = 'PNG';
  r.image_settings.color_mode  = 'RGBA';

  r.use_file_extension         = True;

  r.resolution_x               = 2**sb.frame_sz;
  r.resolution_y               = r.resolution_x;

  r.filter_size                = 0.01;
  r.film_transparent           = True;

# ---   *   ---   *   ---
# out frames as *.png

def render(base,type,off):

  sc     = bpy.context.scene;
  j      = off;

  length = (sc.frame_end)-sc.frame_start;
  names  = [];

  for i in range(

    sc.frame_start,
    sc.frame_end+1

  ):

    n=i+off;
    sc.render.filepath=f"{base}{n}{type}";

    names.append(
      (f"{base}{n}".split('/'))[-1]

    );

    sc.frame_set(i);
    bpy.ops.render.opengl(write_still=True);

    j+=1;

  return [j,length,names];

# ---   *   ---   *   ---
# fork off to external bin

def call_joj_sprite(
  C,data

):

  args=[

    '-sd',data['srcdir'],
    '-o',data['srcdir']+'sheet',
    '-as',str(2**data['atlas_sz']),

  ];

  args.extend(data['files']);
  DOS(ARPATH+'/bin/joj-sprite',args);
  DOS(ARPATH+'/auvi/bin/ans',
    [data['srcdir']+'sheet.ans']

  );

  args=[

    '-o',data['srcdir']+'sheet',

    data['srcdir']+'sheet.joj',
    data['srcdir']+'sheet.crk',
    data['srcdir']+'sheet.ans',

  ];

  DOS(ARPATH+'/bin/daf',args);

# ---   *   ---   *   ---
# exec entry point

def run():

  C    = bpy.context;

  ob   = C.active_object
  sb   = C.scene.da_spritebake;
  char = ob.data.da_char;

  old  = save_settings();

  # hardcoding these as
  # they're not settable yet
  base = sb.outdir+'frame';
  type = '_a';

# ---   *   ---   *   ---
# walk animations for this character
# out them frame by frame

  set_render_config();

  old_anim =char.action;
  anims    =[

    anim for anim in get_anim_list(char,C)
    if 'TPOSE' not in anim.name

  ];

  i     = 0;
  j     = 1;
  tot   = 0;

  J     = len(anims);

  print(

    '\n'+('_'*24)+'\n\n' \

    "\x1b[37;1m<" \
    "\x1b[34;22mAR" \
    "\x1b[37;1m> " \

    "\x1b[32;1mRunning spritebake\x1b[0m\n"

  );

  srcdir = '/'.join(
    sb.outdir.split('/')[:-1]

  )+'/';

  joj_args={
    'srcdir':srcdir,

    'files':[],
    'atlas_sz':sb.atlas_sz

  };

  plout='';

  for anim in anims:

    print(f"\x1b[37;1m::\x1b[0m {j}/{J}");

    char.action    = anim;
    i,length,names = render(base,type,i);

    # shorten animkey
    tag=anim.name;
    tag=tag.replace(ob.data.name + '::','');

    plout=(

      plout

    + f"{j} {tag} "
    + f"{tot} {tot+length} "
    + f"{length}"

    + "\n"

    );

    joj_args['files'].extend(names);

    print('\n');

    j   += 1;
    tot += length+1;

  with open(
    joj_args['srcdir']+"sheet.ans",
    'w+'

  ) as f: f.write(plout);

  call_joj_sprite(C,joj_args);
  load_settings(old);

  print("\x1b[37;1m::\x1b[0m done\n");

  char.action=old_anim;

# ---   *   ---   *   ---
# making a class just for a one liner:
# GENIUS DESIGN

class DA_OT_Spritebake_Run(Operator):

  bl_idname      = "darkage.spritebake_run";
  bl_label       = "Render out spritesheet";

  bl_description = \
    "Renders out a spritesheet";

  def execute(self,C):

    run();
    return {'FINISHED'};

# ---   *   ---   *   ---

class DA_Spritebake(PropertyGroup):

  frame_sz: IntProperty(
    name        = 'Frame size',
    description =
      "Size of sprite frame, as a power of two",

    default     = 7,
    min         = 4,
    max         = 8,

  );

  atlas_sz: IntProperty(
    name        = 'Atlas size',
    description =
      "Size of atlas, as a power of two",

    default     = 7,
    min         = 7,
    max         = 13,

  );

  outdir: StringProperty(
    description = "Path to output directory",
    default     = '/tmp/',

  );

# ---   *   ---   *   ---

class DA_Spritebake_Panel(Panel):

  bl_label       = 'DarkAge Spritebake';
  bl_idname      = 'DA_PT_Spritebake_Panel';
  bl_space_type  = 'PROPERTIES';
  bl_region_type = 'WINDOW';
  bl_context     = 'render';
  bl_category    = 'DA';

# ---   *   ---   *   ---

  @classmethod
  def poll(cls,context):

    ob=context.active_object;

    return (
        ob!=None
    and isinstance(ob.data,Armature)

    );

# ---   *   ---   *   ---

  def draw(self,context):

    layout = self.layout;

    ob     = context.active_object;
    char   = ob.data.da_char;
    sb     = context.scene.da_spritebake;

# ---   *   ---   *   ---

    row=layout.row();
    row.prop(sb,"outdir",text='');

    row=layout.row();
    row.prop(sb,"frame_sz");

    row=layout.row();
    row.prop(sb,"atlas_sz");

    row=layout.row();
    row.operator(
      'darkage.spritebake_run',
      text='',
      icon='RENDER_ANIMATION'

    );

# ---   *   ---   *   ---

def register():

  bpy.da_blocks[__file__]=unregister;

  register_class(DA_Spritebake);
  register_class(DA_OT_Spritebake_Run);
  register_class(DA_Spritebake_Panel);

  Scene.da_spritebake=PointerProperty(
    type=DA_Spritebake

  );

def unregister():

  del Scene.da_spritebake;

  unregister_class(DA_Spritebake_Panel);
  unregister_class(DA_OT_Spritebake_Run);
  unregister_class(DA_Spritebake);

# ---   *   ---   *   ---
