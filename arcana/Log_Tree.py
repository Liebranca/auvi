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

VERSION = 'v0.00.2b';
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

    self.child  = [];

    self.calc_pad();

  def __del__(self):

    while self.lvl > 1:
      self.end_scope();

    self.end_scope('RET');

    if self.parent:
      self.parent.bury(self);

  def beget(self,me):

    par=self;

    if len(self.child):
      par=self.child[-1];

    c=Log_Tree(par);
    c.beg_scope(me);

    self.child.append(c);

    return c;

  def bury(self,c):

    if c in self.child:
      self.child.remove(c);

# ---   *   ---   *   ---

  def line(self,me):
    print(self.pad+str(me));

  def err(self,me):
    self.line(f"\033[31;1m{me}\033[0m");

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
