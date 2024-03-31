#! /bin/bash
#
# repack-min-cardsets.bash
# Copyright (C) 2018 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.
#

set -e -x

src_base="PySolFC-Cardsets"
dest_base="$src_base--Minimal"
ver="3.0.0"
src_vbase="$src_base-3.0"
dest_vbase="$dest_base-3.0.0"
src_arc="$src_vbase.tar.bz2"

if ! test -f "$src_arc"
then
    wget -c "https://sourceforge.net/projects/pysolfc/files/$src_base/$src_vbase/$src_arc/download" -O "$src_arc"
fi

tar -xvf "$src_arc"
rm -rf "$dest_vbase"
mkdir -p "$dest_vbase"
cat scripts/cardsets_to_bundle | (while read b
do
    cp -a "$src_vbase/$b" "$dest_vbase/$b"
done)

tar -cavf "$dest_vbase.tar.xz" "$dest_vbase"
