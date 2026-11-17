#!/usr/bin/env bash

# Script de packaging PySolFC pour macOS (Apple Silicon / Intel)
set -e

echo "--> Installation des dépendances de build..."
pip install pyinstaller

echo "--> Création du script d execution..."
cat << "EOF" > run_app.py
import os
import sys

resource_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
os.chdir(resource_path)
sys.argv[0] = os.path.join(resource_path, "pysol.py")

from pysollib.main import main
sys.exit(main(sys.argv))
EOF

echo "--> Compilation du bundle .app avec PyInstaller..."
pyinstaller --noconfirm --onedir --windowed \n  --name "PySolFC" \n  --add-data "data:data" \n  --add-data "images:images" \n  --add-data "cardsets:cardsets" \n  --add-data "html:html" \n  --collect-all "pysollib" \n  run_app.py

rm -f run_app.py

echo "--> Build terminé : dist/PySolFC.app"
