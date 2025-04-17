#!/bin/bash
set -Cefu

: ${PKGTREE:=/usr/local/packages/PySolFC}
PIP="${PKGTREE}/env/bin/pip"
PYPROG="${PKGTREE}/env/bin/python"
VERSION="$(env PYTHONPATH=`pwd` "$PYPROG" -c 'from pysollib.settings import VERSION ; print(VERSION)')"
XZBALL="dist/PySolFC-${VERSION}.tar.xz"
reqs=(pillow pygame)

make dist

"$PIP" install wheel
"$PIP" install "${reqs[@]}"

"$PIP" install --upgrade "$XZBALL"
