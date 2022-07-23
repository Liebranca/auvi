#!/usr/bin/python
# ---   *   ---   *   ---
# SPRITEBAKE

# ---   *   ---   *   ---

#    +-----+
# 4 .|..O..|.
# 3 .|.OOO.|.
# 2 .|OOOOO|.
# 1 .|.OOO.|.
# 0 .|..O..|.
#    +-----+
#
#   0123456
#
#^
#|
#Y
# X->

# ---   *   ---   *   ---

from .shapebake import ftbarr;
from importlib import reload;

import lytools;
reload(lytools);

def overwrite(im,a:list[float]):
  im.pixels[:]=a[:];

def test(im):

  lytools.im_c_nit(1);

  sz_x:int;
  sz_y:int;

  sz_x,sz_y=im.size;

  r=0.0;
  for i in range(0,len(im.pixels),4):

    r+=1.0/16.0;
    im.pixels[i]=r;

  arr=(lytools.c_float * len(im.pixels))();
  arr[:]=im.pixels[:];

  idex=lytools.im_c_take(
    sz_x,sz_y,4,arr

  );

  buf=lytools.im_c_get_buff(idex);

  for i in range(0,len(im.pixels),4):
    print(i,im.pixels[i],int(i/4),buf[int(i/4)]);

  lytools.im_c_del();

# ---   *   ---   *   ---
