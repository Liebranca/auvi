#!/usr/bin/python
# ---   *   ---   *   ---
# DAF
# Wraps around archiver
#
# LIBRE SOFTWARE
# Licensed under GNU GPL3
# be a bro and inherit
#
# CONTRIBUTORS
# lyeb,

# ---   *   ---   *   ---
# deps

import os,re;

from .Xfer import DOS;
from .Tools import dirof;

from . import WLog;

# ---   *   ---   *   ---
# info

class DAF:

  VERSION = 'v0.00.1b';
  AUTHOR  = 'IBN-3DILA';

# ---   *   ---   *   ---
# cstruc

  def __init__(self,fpath):
    self.fpath=fpath;
    self.files={};

    self.update_file_list();

# ---   *   ---   *   ---
# archive has been created

  def exists(self):

    return (
       os.path.exists(self.fpath+'.daf')
    or os.path.exists(self.fpath+'.dafz')

    );

# ---   *   ---   *   ---
# inspects archive

  def update_file_list(self):

    if not self.exists():
      return;

    me  = DOS('daf',['-i',self.fpath]);
    out = me.split("\n");

    self.files={

      f:self.fpath

      for f in out
      if len(f)

    };

# ---   *   ---   *   ---
# ^filename in ftab

  def has(self,f):
    return f in self.files;

# ---   *   ---   *   ---
# ^similar, check if *part* of
# name is present in ftab
#
# used to warn user about
# replacing/pushing files

  def replchk(self,f):

    # remove extension
    d={

      re.sub(r'\..*$','',key):0
      for key in self.files.keys()

    };

    # remove suffix
    d=[

      re.sub(r'_[A-F0-9]+$','',key)
      for key in d.keys()

    ];

    # ^count instances of name
    d={key:d.count(key) for key in d};

    # give blank suffix on no match
    if f not in d:
      return 0;

    # ^else idex of next suffix
    return d[f];

# ---   *   ---   *   ---
# handles reporting of invocations

  def invoke(

    self,

    cmd,args,

    files,
    title

  ):

    out = True;

    log = WLog.beget(title);
    me  = DOS(cmd,args);

    if len(me):
      log.err(me);
      out=False;

    else:
      for f in files:
        log.line(f);

    del log;
    return out;

# ---   *   ---   *   ---
# add files to archive
# or update existing

  def cpush(self,files):

    args=['-o',self.fpath];

    if self.exists():
      args.append('-u');

    args.extend(files);

    out=self.invoke(
      'daf',args,files,
      'DAF CPUSH'

    );

    if out:
      self.update_file_list();

    return out;

# ---   *   ---   *   ---
# unzip specific file list

  def extract(self,files,to=None):

    if to==None:
      to=dirof(self.fpath)+'/';

    flist = ','.join(files);
    args  = [
      '-o',to,
      '-f',flist

    ];

    args.append(self.fpath);

    return self.invoke(
      'undaf',args,files,
      'DAF EXTRACT'

    );

# ---   *   ---   *   ---
# ^whole archive

  def unpack(self,to=None):

    if to==None:
      to=dirof(self.fpath)+'/';

    args=['-o',to];
    args.append(self.fpath);

    return self.invoke(
      'undaf',args,self.files.keys(),
      'DAF UNPACK'

    );

# ---   *   ---   *   ---
