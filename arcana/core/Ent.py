#!/usr/bin/python

# ---   *   ---   *   ---
# derps

import os,sys;

ARPATH=os.getenv('ARPATH');
if(ARPATH+'/lib/' not in sys.path):
  sys.path.append(ARPATH+'/lib/');

# ---   *   ---   *   ---
# deps

import bpy;
import struct;

import Arcana;

# ---   *   ---   *   ---

def rcolor(name):

  im=bpy.data.images[name];
  cnt=len(im.pixels);

  b=im.pixels[:];
  fret=Arcana.rcolor(b,cnt,1);

  im.pixels.foreach_set(fret[0][:cnt]);
  im.update();

# ---   *   ---   *   ---
