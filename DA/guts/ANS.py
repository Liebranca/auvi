#!/usr/bin/python
# ---   *   ---   *   ---
# ANS
# Animation metadata
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

# ---   *   ---   *   ---
# info

class ANS:

  VERSION = 'v0.00.1b';
  AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# cstruc

  def __init__(self):

    self.anim = None;
    self.da   = None;

    self.tag  = '';
    self.out  = '';

    self.tot  = 0;
    self.idex = 0;

# ---   *   ---   *   ---
# ^process next entry

  def next(self,anim):

    self.anim = anim;
    self.da   = anim.da_anim;

    self.tag  = self.get_tag();

    self.get_plout();

# ---   *   ---   *   ---
# gets short tag from animation name

  def get_tag(self):

    tag = self.anim.name;
    l   = tag.split('::');

    return l[-1];

# ---   *   ---   *   ---
# cat next line to out

  def get_plout(self):

    length=self.anim.da_anim.get_length();

    self.out=(

      self.out

    + f"{self.idex} {self.tag} "
    + f"{self.tot} {self.tot+length} "
    + f"{length}"

    + "\n"

    );

    self.tot  += length;
    self.idex += 1;

# ---   *   ---   *   ---
