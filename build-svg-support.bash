#! /usr/bin/env bash
#
# build-svg-support.bash
# Copyright (C) 2019 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.
#

(
    set -e -x
    build_type="Release"
    build_args="cmake -DCMAKE_BUILD_TYPE=$build_type"
    build()
    {
        $build_args "$@"
    }
    a="`pwd`"
    cd kcardgame
    # git clone git://anongit.kde.org/kpat
    git clone https://github.com/KDE/kpat
    mkdir build-kpat/
    k="`pwd`"
    cd build-kpat
    build ../kpat
    make
    cd ..
    mkdir b
    cd b
    build ../binding-example/
    make
) || true
dir="`pwd`/kcardgame/b"
export PYTHONPATH="$dir" LD_LIBRARY_PATH="$dir"
