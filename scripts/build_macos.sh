#!/usr/bin/env bash
# Local build mirroring .github/workflows/macos-package.yml.
# Needs a universal2 Python (python.org installer) for a universal2 app.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
VENV=".venv-macos-build"
CARDSETS_VER="3.1.0"

archs="$(lipo -archs "$("$PYTHON" -c 'import sys; print(sys.executable)')" 2>/dev/null || true)"
case "$archs" in
  *arm64*x86_64*|*x86_64*arm64*) ;;
  *) echo "WARNING: $PYTHON is not universal2 (archs: ${archs:-unknown});" \
          "the app will be single-arch." ;;
esac

if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
  echo "ERROR: $PYTHON has no tkinter."
  pyexe="$("$PYTHON" -c 'import os, sys; print(os.path.realpath(sys.executable))')"
  case "$pyexe" in
    /opt/homebrew/*|/usr/local/Cellar/*|/usr/local/opt/*)
      pyver="$("$PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
      echo "Homebrew Python: run 'brew install python-tk@${pyver}'." ;;
  esac
  exit 1
fi

echo "--> venv + dependencies"
"$PYTHON" -m venv "$VENV"
. "$VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install --no-binary=Pillow \
  Pillow attrs configobj py2app pycotap pygame-ce pysol-cards setuptools \
  ttkthemes accessible-output2

echo "--> pygame-ce assets py2app needs"
export PYGAME_HIDE_SUPPORT_PROMPT=1
PYGAME_DIR=$(python -c "import pygame, os; print(os.path.dirname(pygame.__file__))")
PYGAME_TAG=$(python -c "import pygame; print(pygame.__version__.split('.dev')[0])")
for asset in freesansbold.ttf pygame_icon.icns; do
  if [ ! -s "$PYGAME_DIR/$asset" ]; then
    curl -fsSL -o "$PYGAME_DIR/$asset" \
      "https://raw.githubusercontent.com/pygame-community/pygame-ce/${PYGAME_TAG}/src_py/${asset}"
  fi
done

echo "--> cardsets"
if ! ls data/cardset-* >/dev/null 2>&1; then
  tmp="$(mktemp -d)"
  curl -fsSL -o "$tmp/cs.tar.xz" \
    "https://sourceforge.net/projects/pysolfc/files/PySolFC-Cardsets/minimal/PySolFC-Cardsets--Minimal-${CARDSETS_VER}.tar.xz/download"
  tar -xJf "$tmp/cs.tar.xz" -C "$tmp"
  mv "$tmp"/PySolFC-Cardsets--Minimal-"${CARDSETS_VER}"/cardset-* data
  rm -rf "$tmp"
fi

echo "--> rules + translations"
make rules mo

echo "--> py2app"
rm -rf build dist
PYTHONPATH=. python setup_osx.py py2app
test -d dist/PySolFC.app
xattr -dr com.apple.quarantine dist/PySolFC.app

echo "--> arch check"
lipo -archs dist/PySolFC.app/Contents/MacOS/PySolFC

if command -v create-dmg >/dev/null; then
  echo "--> dmg"
  rm -f PySolFC.dmg
  create-dmg --volname "Install PySolFC" --volicon data/PySol.icns \
    --background html-src/images/pysollogo01.png --window-size 800 400 \
    --icon PySolFC.app 200 185 --app-drop-link 600 185 --skip-jenkins \
    PySolFC.dmg dist
fi

echo "Done: dist/PySolFC.app"
