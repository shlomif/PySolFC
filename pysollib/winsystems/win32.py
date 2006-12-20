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

from pysollib.settings import TOOLKIT, USE_TILE
from pysollib.tile import Tile

from common import baseInitRootWindow, BaseTkSettings


class initRootWindow(baseInitRootWindow):
    def __init__(self, root, app):
        baseInitRootWindow.__init__(self, root, app)
        if TOOLKIT == 'gtk':
            pass
        elif USE_TILE:
            theme = app.opt.tile_theme
            style = Tile.Style(root)
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
    toolbar_relief = 'groove'
    toolbar_borderwidth = 2
    if USE_TILE:
        toolbar_button_padding = (2, 0)

