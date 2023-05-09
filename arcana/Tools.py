#!/usr/bin/python
# ---   *   ---   *   ---
# TOOLS
# Stuff I don't want to
# type twice
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import os;

# ---   *   ---   *   ---
# info

VERSION = 'v0.00.3b';
AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---

def bl_list2enum(l):
  return [(x.upper(),x,'') for x in l];

# ---   *   ---   *   ---
# generic code emitter

def codice(src,keys):

  for key,value in keys.items():
    src=src.replace(key,value);

  return src;

# ---   *   ---   *   ---
# attr is not meant to be written

def isro(o,attr):

  v=getattr(o,attr);

  try:
    setattr(o,attr,v);
    return 0;

  except AttributeError:
    return 1;

# ---   *   ---   *   ---
# converts path::to into path/to

def ns_path(s):
  return s.replace('::','/');

# ---   *   ---   *   ---
# gives base of fpath
# ie, fpath without filename

def dirof(s):
  l=s.split('/')[0::-1];

  if len(l) > 1:
    return '/'.join(l);

  else:
    return '';

# ---   *   ---   *   ---
# older than

def ot(a,b):

  a=os.stat(a).st_mtime;
  b=os.stat(b).st_mtime;

  return a < b;

# ---   *   ---   *   ---
# ^missing or older

def moo(a,b):

  return (
    not os.path.exists(a)
    or  ot(a,b)

  );

# ---   *   ---   *   ---
# ensure root+(path::to) exists

def chkdir(root,f):

  # get fpath
  key  = ns_path(f);
  base = root+dirof(key);

  # make dst if it's not there
  if not os.path.exists(base):
    os.makedirs(base);

  return root+key;

# ---   *   ---   *   ---
