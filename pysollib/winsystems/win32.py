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

from pysollib.settings import TOOLKIT, USE_TILE
if USE_TILE:
    from pysollib.tile import ttk

from common import base_init_root_window, BaseTkSettings


def init_root_window(root, app):
    base_init_root_window(root, app)
    if TOOLKIT == 'gtk':
        pass
    elif USE_TILE:
        theme = app.opt.tile_theme
        style = ttk.Style(root)
        if theme not in ('winnative', 'xpnative'):
            color = style.lookup('.', 'background')
            if color:
                root.tk_setPalette(color)
            ##root.option_add('*Menu.foreground', 'black')
            root.option_add('*Menu.activeBackground', '#08246b')
            root.option_add('*Menu.activeForeground', 'white')
        if theme == 'winnative':
            style.configure('Toolbutton', padding=2)
    else:
        #root.option_add(...)
        pass


class TkSettings(BaseTkSettings):
    canvas_padding = (1, 1)
    horizontal_toolbar_padding = (1, 0)
    toolbar_relief = 'groove'
    toolbar_borderwidth = 2
    if USE_TILE:
        toolbar_button_padding = (2, 0)

