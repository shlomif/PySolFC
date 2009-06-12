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

import sys, os
import Tkinter

from pysollib.settings import TOOLKIT, USE_TILE
if USE_TILE:
    from pysollib.tile import ttk
from pysollib.macosx.appSupport import hideTkConsole

from common import base_init_root_window, BaseTkSettings


def init_root_window(root, app):
    base_init_root_window(root, app)
    if TOOLKIT == 'tk':
        hideTkConsole(root)
    if TOOLKIT == 'gtk':
        pass
    elif USE_TILE:
        style = ttk.Style(root)
        color = style.lookup('.', 'background')
        if color:
            root.tk_setPalette(color)   # for non-ttk widgets

        if app.opt.tile_theme == 'aqua':
            # standard Tk scrollbars work on OS X, but ttk ones look weird
            ttk.Scrollbar = Tkinter.Scrollbar

    else:                               # pure Tk
        #root.option_add(...)
        pass


class TkSettings(BaseTkSettings):
    pass

