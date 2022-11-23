#!/usr/bin/perl
# ---   *   ---   *   ---
# XFER
# Passes data from and to
# a more civilized age
#
# LIBRE SOFTWRE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import subprocess;
from arcana import ARPATH;

# ---   *   ---   *   ---

def DOS(cmd,args,dec=1):

  line=[cmd];
  line.extend(args);

  p=subprocess.Popen(

    line,
    stdout=subprocess.PIPE

  );

  s=p.communicate()[0];
  if(dec):s=s.decode();

  return s;

# ---   *   ---   *   ---
# store

def save(ob,path='./dump'):

  cmd=ARPATH+'/auvi/bin/coldpy';
  args=['-x',repr(type(ob)),repr(ob),path];

  DOS(cmd,args);

# ---   *   ---   *   ---
# retrieve

def load(path='./dump'):

  cmd=ARPATH+'/auvi/bin/coldpy';
  args=['-i',path];

  return eval(DOS(cmd,args));

# ---   *   ---   *   ---
