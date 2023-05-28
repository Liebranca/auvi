#!/usr/bin/python
# ---   *   ---   *   ---
# GUTS RENDER
# Saves and restores
# render settings
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import bpy;

# ---   *   ---   *   ---
# info

class DA_Render:

  VERSION = 'v0.00.1b';
  AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# ROM

  SETTINGS={

    'render.engine':'CYCLES',

    'cycles.use_adaptive_sampling':True,
    'cycles.adaptive_threshold':0.500,

    'cycles.samples':8,
    'cycles.adaptive_min_samples':1,

    'cycles.time_limit':0,

    'cycles.max_bounces':1,
    'cycles.diffuse_bounces':1,
    'cycles.glossy_bounces':1,
    'cycles.transmission_bounces':1,
    'cycles.volume_bounces':0,
    'cycles.transparent_max_bounces':0,

    'cycles.blur_glossy':1.0,
    'cycles.caustics_reflective':False,
    'cycles.caustics_refractive':False,

    'render.bake.target':'IMAGE_TEXTURES',
    'render.bake.use_clear':True,
    'render.bake.margin_type':'ADJACENT_FACES',
    'render.bake.margin':2,

    'render.bake.use_selected_to_active':True,
    'render.bake.cage_extrusion':0.025,

    'cycles.bake_type':'COMBINED',
    'render.bake.view_from':'ABOVE_SURFACE',

    'render.bake.use_pass_direct':True,
    'render.bake.use_pass_indirect':False,
    'render.bake.use_pass_diffuse':False,
    'render.bake.use_pass_glossy':False,
    'render.bake.use_pass_transmission':False,
    'render.bake.use_pass_emit':True,

  };

# ---   *   ---   *   ---
# cstruc

  def __init__(self,C,dst,o={}):

    if not o:
      o=DA_Render.SETTINGS;

    self.config   = dict(o);
    self.previous = self.get_current();

    self.al       = C.collection.da_al;

    self.apply_config();

  def __del__(self):
    self.restore_previous();

# ---   *   ---   *   ---
# stores current config

  def get_current(self):

    return {

      key: eval('bpy.context.scene.'+key)
      for key in self.config.keys()

    };

# ---   *   ---   *   ---
# ^overwrites

  @staticmethod
  def set_config(o):
    for key,value in o.items():
      exec('bpy.context.scene.'+key+'=value');

# ---   *   ---   *   ---
# ^sugar

  def apply_config(self):
    DA_Render.set_config(self.config);

  def restore_previous(self):
    DA_Render.set_config(self.previous);

# ---   *   ---   *   ---
# initialize output images to
# match da_matbake props

  def nit_outim(self,ob):

    mat = ob.material_slots[0].material;
    mb  = ob.da_matbake;

    sz  = int(mb.render_sz);
    aa  = int(mb.render_scale.replace('x',''));

    for key in ['ALPHA','COLOR']:

      nd=mat.node_tree.nodes["BAKETO_"+key];
      im=nd.image;

      im.file_format      = 'PNG';

      im.source           = 'GENERATED';
      im.generated_width  = sz*aa;
      im.generated_height = sz*aa;

    self.config[
      'render.bake.margin'

    ]=sz>>4;

    return sz;

# ---   *   ---   *   ---
# get node holding image being
# baked to

  def getout(self,ob,mode='COLOR'):

    dst  = ob.da_matbake.dst;
    ndst = dst.material_slots[0].material;
    ndst = ndst.node_tree;

    im   = ndst.nodes["BAKETO_"+mode];

    return im;

# ---   *   ---   *   ---
# connects matbake output
# to material output surface

  def setout(self,ob,key,alpha):

    mode='ALPHA' if alpha else 'COLOR';

    self.setout_src(ob,mode);
    self.setout_dst(ob,mode);

# ---   *   ---   *   ---
# configures output for bake
# when using matbake node

  def setout_src(self,ob,mode):

    mb   = ob.da_matbake;
    mats = mb.get_materials();

#    [
#
#      slot.material
#      for slot in ob.material_slots
#
#      if slot.material != None
#
#    ];

    # ensure material output is
    # correct for each material
    for mat in mats:

      nt   = mat.node_tree;

      bake = nt.nodes['MATBAKE'];
      out  = nt.nodes['OUTPUT'];

      im   = nt.nodes['BAKETO_'+mode];

      nt.links.new(
        bake.outputs[key],
        out.inputs['Surface']

      );

      set_active_node(nt,im);

# ---   *   ---   *   ---
# ^touches output of
# destination object

  def setout_dst(self,ob,mode):

    dst  = ob.da_matbake.dst;
    ndst = dst.material_slots[0].material;
    ndst = ndst.node_tree;

    # for selected to active
    im=ndst.nodes['BAKETO_'+mode];
    set_active_node(ndst,im);


# ---   *   ---   *   ---
# render single output
# of matbake node

  def bake_layer(ob,key,alpha):

    bake_t='';

    if key == 'NormalBake':
      bake_t='NORMAL';

    else:
      bake_t='COMBINED';

    setout(ob,key,alpha);

    with redirect_stdout(io.StringIO()):
      bpy.ops.object.bake(type=bake_t);

# ---   *   ---   *   ---
# ^multiple layers of
# a packed texture

  def bake_image(ob,t,fpath):

    mode=False;

    for key in BAKE_TYPES[t]:
      bake_layer(ob,key,mode);
      mode=True;

    return combine_layers(ob,t,fpath);

# ---   *   ---   *   ---
# ^puts the two bakes together

  def combine_layers(ob,t,fpath):;

    out   = fpath+IMAGE_EXT[t];
    sz    = int(ob.da_matbake.render_sz);

    color = get_output_node(ob,'COLOR');
    alpha = get_output_node(ob,'ALPHA');

    # undo scaling
    color.image.scale(sz,sz);
    alpha.image.scale(sz,sz);

    # get color and alpha
    a=list(color.image.pixels);
    b=list(alpha.image.pixels);

    # ^roll together
    a[3::4]=b[0::4];
    color.image.pixels[:]=a[:];

    # save modified
    color.image.save(
      filepath = out,
      quality  = 100

    );

    return out;

# ---   *   ---   *   ---
