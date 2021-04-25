#! /usr/bin/env perl
#
# Short description for refactor-gamedb.pl
#
# Version 0.0.1
# Copyright (C) 2021 Shlomi Fish < https://www.shlomifish.org/ >
#
# Licensed under the terms of the MIT license.

use strict;
use warnings;
use 5.014;
use autodie;

use Path::Tiny qw/ path tempdir tempfile cwd /;

s@
\(\s*(n_\s*\("[^"]+"\))\s*,\s*
lambda\s*gi,\s*gt=(GT[A-Za-z_0-9]+)\s*:
\s*gi.si.game_type\s*==\s*gt\)
@_gen_select(title=$1, game_type=$2)@gmsx;
