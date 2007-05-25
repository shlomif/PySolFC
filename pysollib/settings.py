##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
##---------------------------------------------------------------------------##

import os

n_ = lambda x: x                        # for gettext


#PACKAGE = 'PySolFC'
PACKAGE = 'PySol'
#PACKAGE_URL = 'http://pysolfc/sourceforge.net/'
PACKAGE_URL = 'http://sourceforge.net/projects/pysolfc/'

VERSION = '4.82'
FC_VERSION = '1.0.1'
VERSION_TUPLE = (10, 0, 1)

# Tk windowing system (auto determine in init.py)
WIN_SYSTEM = 'x11'                      # win32, x11, aqua, classic

# toolkit
TOOLKIT = 'tk'                          # or 'gtk'
USE_TILE = 'auto'                       # or True or False

# sound
# available values:
#   'pss' - PySol-Sound-Server (all)
#   'pygame' - PyGame (all)
#   'oss' (*nix)
#   'win' (windows)
#   'none' - disable
SOUND_MOD = 'auto'

# freecell-solver
USE_FREECELL_SOLVER = True
FCS_COMMAND = 'fc-solve'
##FCS_HOME = None                         # path to fcs presets files

# data dirs
DATA_DIRS = []
# you can add your extra directories here
if os.name == 'posix':
    DATA_DIRS = [
        '/usr/share/PySolFC',
        '/usr/local/share/PySolFC',
        '/usr/games/PySolFC',
        '/usr/local/games/PySolFC',
        ]
if os.name == 'nt':
    pass

TOP_SIZE = 10
TOP_TITLE = n_('Top 10')

# use menu for select game
SELECT_GAME_MENU = True

# debug
DEBUG = 0                               # must be integer
CHECK_GAMES = False                     # check duplicated names and classes
