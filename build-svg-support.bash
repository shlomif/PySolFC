#! /usr/bin/env bash
#
# build-svg-support.bash
# Copyright (C) 2019 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.
#

(
    set -e -x
    a="`pwd`"
    cd kcardgame
    git clone git://anongit.kde.org/kpat
    mkdir build-kpat/
    k="`pwd`"
    cd build-kpat
    cmake -DCMAKE_BUILD_TYPE=Debug ../kpat
    make
    cd ..
    mkdir b
    cd b
    cmake -DCMAKE_BUILD_TYPE=Debug ../binding-example/
    make
) || true
dir="`pwd`/kcardgame/b"
export PYTHONPATH="$dir" LD_LIBRARY_PATH="$dir"
