"""
Usage:
    python setup.py py2app
"""

import os, sys
import shutil
from subprocess import call
from setuptools import setup
from pysollib.settings import PACKAGE, VERSION

# build the rule pages
if not os.path.exists('data/html'):
    os.chdir('html-src')
    call('./gen-html.py', shell=True)
    os.chdir(os.pardir)
    shutil.copytree('html-src/images', 'html-src/html/images')
    try:
        shutil.rmtree('data/html')
    except OSError:
        pass
    shutil.copytree('html-src/html', 'data/html')

# build the HTML list of games
call("./scripts/all_games.py > docs/all_games.html", shell=True)

# Use Tile widgets, if they are installed.
# http://tktable.sourceforge.net/tile/
import Tkinter
root = Tkinter.Tk()
root.withdraw()
try:
    root.tk.call('package', 'require', 'tile', '0.7.8')
except:
    TILE = None
else:
    TILE = "tile0.7.8"
    TCL_EXTENSION_PATH = "/Library/Tcl"
finally:
    root.destroy()
    del root, Tkinter

# Use Freecell Solver, if it is installed.
# http://fc-solve.berlios.de/
SOLVER_LIB_PATH = "/usr/local/lib/libfreecell-solver.0.dylib"
SOLVER = ["/usr/local/bin/fc-solve"]
if not os.path.exists(SOLVER_LIB_PATH):
    SOLVER_LIB_PATH = None
    SOLVER = []

GETINFO_STRING = "PySol Fan Club Edition \
                %s %s, (C) 1998-2003 Markus F.X.J Oberhumer \
                (C) 2006-2007 Skomoroh" % (PACKAGE, VERSION)
PLIST = dict(
    CFBundleDevelopmentRegion = 'en_US',
    CFBundleExecutable = PACKAGE,
    CFBundleDisplayName = PACKAGE,
    CFBundleGetInfoString = GETINFO_STRING,
    CFBundleIdentifier = 'net.sourceforge.pysolfc',
    CFBundleName = PACKAGE,
    CFBundleVersion = '%s' % VERSION,
    CFBundleShortVersionString = '%s' % VERSION, 
    NSHumanReadableCopyright = "Copyright (C) 1998-2003 Markus F.X.J. Oberhumer",
    )
APP = ['pysol.py']
ICON_FILE = 'data/PySol.icns'
DATA_FILES = ['docs', 'data', 'scripts','COPYING', 'README'] + SOLVER
RESOURCES = [os.path.join(TCL_EXTENSION_PATH, TILE)] if TILE else []
FRAMEWORKS = [SOLVER_LIB_PATH] if SOLVER_LIB_PATH else []
OPTIONS = dict(argv_emulation=True,
               plist=PLIST,
               iconfile=ICON_FILE,
               resources=RESOURCES,
               frameworks=FRAMEWORKS,
               excludes=['pysollib.pysolgtk']
               )

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    )

##
top = os.getcwd()
# FIXME: a hack to get Tcl extensions working
# from inside the app bundle
if TILE and "py2app" in sys.argv:
    os.chdir('dist/%s.app/Contents/Frameworks' % PACKAGE)
    try:
        os.symlink('../Resources/%s' % TILE, TILE)
    except OSError:
        pass
    os.chdir(top)
# Modify the fc-solve binary with install_name_tool to use the dependent
# libfreecell-solver dynamic library in the app bundle.
if SOLVER and "py2app" in sys.argv:
    os.chdir('dist/%s.app/Contents/Resources' % PACKAGE)
    call("install_name_tool -change \
         /usr/local/lib/libfreecell-solver.0.dylib \
         @executable_path/../Frameworks/libfreecell-solver.0.dylib fc-solve",
         shell=True
         )
