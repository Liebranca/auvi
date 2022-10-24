#!/usr/bin/perl

  use v5.36.0;
  use strict;
  use warnings;

  use lib $ENV{'ARPATH'}.'/lib/sys/';
  use Shb7;

  use lib $ENV{'ARPATH'}.'/lib/';
  use Avt;

# ---   *   ---   *   ---

Avt::set_config(

  name=>'auvi',
  scan=>'-x data,lytools,xforms',

  build=>'ar:auvi',

  xprt=>[qw(arcana/core/Ent.cpp)],
  libs=>[qw(stdc++)],

  post_build=>q(

    use Emit::Std;
    use Emit::Python;

    Emit::Std::outf(

      'Python','lib/Arcana.py',

      author=>'IBN-3DILA',
      include=>[['Avt.cwrap','*']],

      body=>\&Emit::Python::shwlbind,
      args=>['Arcana',['auvi']],

    );

  ),

);

Avt::scan();
Avt::config();
Avt::make();

# ---   *   ---   *   ---
1; # ret
