#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

import tkinter

from pysollib.mygettext import n_

# ************************************************************************
# * constants
# ************************************************************************

EVENT_HANDLED = "break"
EVENT_PROPAGATE = None

CURSOR_DRAG = "hand1"
CURSOR_WATCH = "watch"
CURSOR_DOWN_ARROW = 'sb_down_arrow'

ANCHOR_CENTER = tkinter.CENTER
ANCHOR_N = tkinter.N
ANCHOR_NW = tkinter.NW
ANCHOR_NE = tkinter.NE
ANCHOR_S = tkinter.S
ANCHOR_SW = tkinter.SW
ANCHOR_SE = tkinter.SE
ANCHOR_W = tkinter.W
ANCHOR_E = tkinter.E

COMPOUNDS = (
    # (tkinter.CENTER,  'center'),
    # (tkinter.RIGHT,    'right'),
    (tkinter.NONE,   n_('Icons only')),
    (tkinter.TOP,    n_('Text below icons')),
    (tkinter.BOTTOM, n_('Text above icons')),
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
    "hint",
    "pause",
    "statistics",
    "rules",
    "quit",
    "player",
    )

STATUSBAR_ITEMS = (
            ('stuck', "'You Are Stuck' indicator"),
            ('time',  'Playing time'),
            ('moves', 'Moves/Total moves'),
            ('gamenumber', 'Game number'),
            ('stats', 'Games played: won/lost'),
            ('info', 'Number of cards'),
            ('help', 'Help info')
)
