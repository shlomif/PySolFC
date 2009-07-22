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
import os, re, sys
import gtk
from gtk import gdk

# PySol imports



# ************************************************************************
# *
# ************************************************************************

class PysolToolbarTk:
    def __init__(self, top, menubar, dir, size=0, relief=0, compound=None):
        self.top = top
        self.menubar = menubar
        self.dir = dir
        self.side = -1

        ui_info = '''
<ui>
  <toolbar  name='toolbar'>
    <toolitem action='newgame'/>
    <toolitem action='restart'/>
    <separator/>
    <toolitem action='open'/>
    <toolitem action='save'/>
    <separator/>
    <toolitem action='undo'/>
    <toolitem action='redo'/>
    <toolitem action='shuffle'/>
    <toolitem action='autodrop'/>
    <toolitem action='pause'/>
    <separator/>
    <toolitem action='stats'/>
    <toolitem action='rules'/>
    <separator/>
    <toolitem action='quit'/>
  </toolbar>
</ui>
'''
        ui_manager = self.top.ui_manager # created in menubar.py
        ui_manager_id = ui_manager.add_ui_from_string(ui_info)

        toolbar = ui_manager.get_widget("/toolbar")
        self.toolbar = toolbar
        toolbar.set_tooltips(True)
        toolbar.set_style(gtk.TOOLBAR_ICONS)

        self._attached = False


    #
    # wrappers
    #

    def _busy(self):
        return not (self.side and self.game and not self.game.busy and self.menubar)

    def destroy(self):
        self.toolbar.destroy()


    #
    # public methods
    #

    def getSide(self):
        return self.side

    def getSize(self):
        return 0

    def hide(self, resize=1):
        self.show(0, resize)

    def show(self, side=1, resize=1):
        if self.side == side:
            return 0
        self.side = side
        if not side:
            # hide
            self.toolbar.hide()
            return 1
        # show
        if side == 1:
            # top
            x, y = 1, 1
        elif side == 2:
            # bottom
            x, y = 1, 3
        elif side == 3:
            # left
            x, y = 0, 2
        else:
            # right
            x, y = 2, 2
        # set orient
        if side in (1, 2):
            orient =  gtk.ORIENTATION_HORIZONTAL
        else:
            orient =  gtk.ORIENTATION_VERTICAL
        self.toolbar.set_orientation(orient)
        if self._attached:
            self.top.table.remove(self.toolbar)
        row_span, column_span = 1, 1
        self.top.table.attach(self.toolbar,
                              x, x+1,     y, y+1,
                              gtk.FILL,   gtk.FILL,
                              0,          0)
        self.toolbar.show()
        self._attached = True
        return 1


    def setCursor(self, cursor):
        if self.side:
            if self.toolbar.window:
                self.toolbar.window.set_cursor(gdk.Cursor(v))

    def setRelief(self, relief):
        # FIXME
        pass

    def updateText(self, **kw):
        # FIXME
        pass

    def config(self, w, v):
        # FIXME
        pass

