#!/usr/bin/python
# ---   *   ---   *   ---
# STRIP
# Builds invisible NLA shit
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import bpy;

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

    r.filepath

  )=data;

# ---   *   ---   *   ---
# overwrite scene settings with
# hardcoded DA sprite render stuff

def set_render_config():

  r=bpy.context.scene.render;

  r.image_settings.file_format = 'PNG';
  r.image_settings.color_mode  = 'RGBA';

  r.use_file_extension         = True;

  r.resolution_x               = 128;
  r.resolution_y               = 128;

  r.filter_size                = 0.01;
  r.film_transparent           = True;

# ---   *   ---   *   ---
# out frames as *.png

def render(base,type):

  sc  = bpy.context.scene;

  for i in range(
    sc.frame_start,
    sc.frame_end+1

  ):

    sc.render.filepath=f"{base}{i}_{type}";

    sc.frame_set(i);
    bpy.ops.render.opengl();

# ---   *   ---   *   ---
# exec entry point

def run():

  old  = save_settings();

  # hardcoding these as
  # they're not settable yet
  base = './rend/frame';
  type = '_a';

  # out the images
  set_render_config();
  render(base,type);

  load_settings(old);

# ---   *   ---   *   ---
# pending
#
# this func should walk the actor's anims
# and instance them into the NLA
#
# transitions? tempting, but not yet

def make_strip():
  pass;

# ---   *   ---   *   ---
# pending
#
# ^should undo the work done by prev
#
# the problem with NLA is it fills the file
# with a ton of crap, I'd rather never do
# them by hand and I'd rather they don't
# stick around

def clear_strip():
  pass;

# ---   *   ---   *   ---
