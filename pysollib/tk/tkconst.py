#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
import Tkinter


# ************************************************************************
# * constants
# ************************************************************************

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

