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
import tkinter

from pysollib.mygettext import _, n_

# ************************************************************************
# * constants
# ************************************************************************

EVENT_HANDLED   = "break"
EVENT_PROPAGATE = None

CURSOR_DRAG     = "hand1"
CURSOR_WATCH    = "watch"
CURSOR_DOWN_ARROW = 'sb_down_arrow'

ANCHOR_CENTER = tkinter.CENTER
ANCHOR_N      = tkinter.N
ANCHOR_NW     = tkinter.NW
ANCHOR_NE     = tkinter.NE
ANCHOR_S      = tkinter.S
ANCHOR_SW     = tkinter.SW
ANCHOR_SE     = tkinter.SE
ANCHOR_W      = tkinter.W
ANCHOR_E      = tkinter.E

COMPOUNDS = (
    ##(Tkinter.BOTTOM,  'bottom'),
    ##(Tkinter.CENTER,  'center'),
    ##(Tkinter.RIGHT,    'right'),
    (tkinter.NONE,   n_('Icons only')),
    (tkinter.TOP,    n_('Text below icons')),
    (tkinter.LEFT,   n_('Text beside icons')),
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

