"""
Command to create a macOS app bundle:
    PYTHONPATH=. python3 setup_osx.py py2app
"""

import os
import shutil
import sys
from subprocess import CalledProcessError, call, check_output

from pysollib.settings import PACKAGE, VERSION

from setuptools import setup


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

# Use Freecell Solver, if it is installed.
# http://fc-solve.berlios.de/
SOLVER_LIB_PATH = "/usr/local/lib/libfreecell-solver.0.dylib"
SOLVER = ["/usr/local/bin/fc-solve"]
if not os.path.exists(SOLVER_LIB_PATH):
    SOLVER_LIB_PATH = None
    SOLVER = []

# libwebp (a Pillow dependency) depends on libsharpyuv via a bare
# @rpath reference that py2app's dependency walker doesn't follow.
# Bundle it explicitly, same as the solver lib above.
SHARPYUV_LIB_PATH = None
try:
    _webp_prefix = check_output(
        ["brew", "--prefix", "webp"]).decode().strip()
    _candidate = os.path.join(_webp_prefix, "lib", "libsharpyuv.0.dylib")
    if os.path.exists(_candidate):
        SHARPYUV_LIB_PATH = _candidate
except (OSError, CalledProcessError):
    pass

GETINFO_STRING = "PySol Fan Club Edition \
                %s %s, (C) 1998-2003 Markus F.X.J Oberhumer \
                (C) 2006-2007 Skomoroh" % (PACKAGE, VERSION)
PLIST = dict(
    CFBundleDevelopmentRegion='en_US',
    CFBundleExecutable=PACKAGE,
    CFBundleDisplayName=PACKAGE,
    CFBundleGetInfoString=GETINFO_STRING,
    CFBundleIdentifier='net.sourceforge.pysolfc',
    CFBundleName=PACKAGE,
    CFBundleVersion='%s' % VERSION,
    CFBundleShortVersionString='%s' % VERSION,
    NSHumanReadableCopyright="Copyright (C) 1998-2003 Markus F.X.J. Oberhumer",
    )
APP = ['pysol.py']
ICON_FILE = 'data/PySol.icns'
DATA_FILES = ['docs', 'data', 'locale', 'scripts', 'COPYING', 'README.md',
              ] + SOLVER
RESOURCES = []
FRAMEWORKS = ([SOLVER_LIB_PATH] if SOLVER_LIB_PATH else []) + \
             ([SHARPYUV_LIB_PATH] if SHARPYUV_LIB_PATH else [])
# with argv_emulation=True, the app window is not shown when launched
OPTIONS = dict(argv_emulation=False,
               emulate_shell_environment=True,
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

#
top = os.getcwd()
# Modify the fc-solve binary with install_name_tool to use the dependent
# libfreecell-solver dynamic library in the app bundle.
if SOLVER and "py2app" in sys.argv:
    os.chdir('dist/%s.app/Contents/Resources' % PACKAGE)
    call("install_name_tool -change \
         /usr/local/lib/libfreecell-solver.0.dylib \
         @executable_path/../Frameworks/libfreecell-solver.0.dylib fc-solve",
         shell=True
         )
    os.chdir(top)

# Point libwebp at the bundled libsharpyuv instead of its broken
# original rpath.
if SHARPYUV_LIB_PATH and "py2app" in sys.argv:
    frameworks_dir = os.path.join(
        top, 'dist', '%s.app' % PACKAGE, 'Contents', 'Frameworks')
    for name in os.listdir(frameworks_dir):
        if name.startswith('libwebp'):
            call([
                'install_name_tool', '-change',
                '@rpath/libsharpyuv.0.dylib',
                '@executable_path/../Frameworks/libsharpyuv.0.dylib',
                os.path.join(frameworks_dir, name),
                ])
