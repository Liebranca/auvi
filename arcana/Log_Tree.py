#!/usr/bin/python
# ---   *   ---   *   ---
# LOG TREE
# Hierarchical prints
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

VERSION = 'v0.00.1b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---

class Log_Tree:

  def __init__(self,parent=None):

    self.lvl=(

      0

      if parent==None
      else parent.lvl

    );

    self.parent = parent;
    self.pad    = '';

    self.calc_pad();

  def __del__(self):

    while self.lvl > 1:
      self.end_scope();

    self.end_scope('RET');

  def beget(self,me):
    c=Log_Tree(self);
    c.beg_scope(me);

    return c;

# ---   *   ---   *   ---

  def line(self,me):
    print(self.pad+str(me));

  def err(self,me):
    self.line(f"\e[31;1m{me}\e[0m");

  def beg_scope(self,me):

    print();

    self.line(str(me)+"\n");
    self.lvl+=1;
    self.calc_pad();

  def end_scope(self,me=None):

    if me=="\n":
      print();

    elif me:
      self.line("\n"+str(me)+"\n");

    self.lvl-=1;
    self.calc_pad();

  def calc_pad(self):
    self.pad='  ' * self.lvl;

# ---   *   ---   *   ---
