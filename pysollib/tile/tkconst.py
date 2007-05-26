## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
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
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = ['EVENT_HANDLED',
           'EVENT_PROPAGATE',
           'CURSOR_DRAG',
           'CURSOR_WATCH',
           'CURSOR_DOWN_ARROW',
           'ANCHOR_CENTER',
           'ANCHOR_N',
           'ANCHOR_NW',
           'ANCHOR_NE',
           'ANCHOR_S',
           'ANCHOR_SW',
           'ANCHOR_SE',
           'ANCHOR_W',
           'ANCHOR_E',
           'TOOLBAR_BUTTONS',
           ]

# imports
import sys, os
import traceback
import Tkinter


# /***********************************************************************
# // constants
# ************************************************************************/

EVENT_HANDLED   = "break"
EVENT_PROPAGATE = None

CURSOR_DRAG     = "hand1"
CURSOR_WATCH    = "watch"
CURSOR_DOWN_ARROW = 'sb_down_arrow'

ANCHOR_CENTER = Tkinter.CENTER
ANCHOR_N      = Tkinter.N
ANCHOR_NW     = Tkinter.NW
ANCHOR_NE     = Tkinter.NE
ANCHOR_S      = Tkinter.S
ANCHOR_SW     = Tkinter.SW
ANCHOR_SE     = Tkinter.SE
ANCHOR_W      = Tkinter.W
ANCHOR_E      = Tkinter.E

COMPOUNDS = (
    ##(Tkinter.BOTTOM,  'bottom'),
    ##(Tkinter.CENTER,  'center'),
    ##(Tkinter.RIGHT,    'right'),
    (Tkinter.NONE,   n_('Icons only')),
    (Tkinter.TOP,    n_('Text below icons')),
    (Tkinter.LEFT,   n_('Text beside icons')),
    ('text',         n_('Text only')),
    )

TOOLBAR_BUTTONS = (
    "new",
    "restart",
    "open",
    "save",
    "undo",
    "redo",
    "autodrop",
    "shuffle",
    "pause",
    "statistics",
    "rules",
    "quit",
    "player",
    )

