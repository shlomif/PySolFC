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


# imports
##import sys

from gtk import gdk

from gtk import ANCHOR_NW, ANCHOR_SW, ANCHOR_NE, ANCHOR_SE


# ************************************************************************
# * constants
# ************************************************************************

EVENT_HANDLED   = 1
EVENT_PROPAGATE = 0

CURSOR_DRAG     = gdk.HAND1
CURSOR_WATCH    = gdk.WATCH
CURSOR_DOWN_ARROW = gdk.SB_DOWN_ARROW

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

