#!/bin/sh
set -Cefu

: ${PKGTREE:=/usr/local/packages/PySolFC}
PIP="$(printf '%s/env/bin/pip install --no-binary :all: ' "$PKGTREE")"
PYPROG="$(printf '%s/env/bin/python' "$PKGTREE")"
VERSION="$(env PYTHONPATH=`pwd` "$PYPROG" -c 'from pysollib.settings import VERSION ; print(VERSION)')"
XZBALL="$(printf 'dist/PySolFC-%s.tar.xz' "$VERSION")"
reqs='six random2 pillow'

make dist
for req in $reqs
do
    "$PIP" "$req"
done
"$PIP" --upgrade "$XZBALL"
