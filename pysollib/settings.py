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

import sys, os

n_ = lambda x: x

#
#PACKAGE = 'PySolFC'
PACKAGE = 'PySol'
PACKAGE_URL = 'http://sourceforge.net/projects/pysolfc/'

VERSION = '4.82'
FC_VERSION = '0.9.3'
VERSION_TUPLE = (4, 82)

TOOLKIT = 'gtk'
TOOLKIT = 'tk'

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
if os.name == 'mac':
    pass

TOP_SIZE = 10
TOP_TITLE = n_('Top 10')

