## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
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
## Markus F.X.J. Oberhumer
## <markus.oberhumer@jk.uni-linz.ac.at>
## http://wildsau.idv.uni-linz.ac.at/mfx/pysol.html
##
##---------------------------------------------------------------------------##


# imports
import sys
from gtk import gdk


# /***********************************************************************
# // constants
# ************************************************************************/

tkname = "gnome"
# (major version, minor version, micro version, patchlevel)
tkversion = (0, 0, 0, 0)

EVENT_HANDLED   = 1
EVENT_PROPAGATE = 0

CURSOR_DRAG   = gdk.HAND1
CURSOR_WATCH  = gdk.WATCH

TOOLBAR_BUTTONS = (
    "new",
    "restart",
    "open",
    "save",
    "undo",
    "redo",
    "autodrop",
    "pause",
    "statistics",
    "rules",
    "quit",
    "player",
    )

