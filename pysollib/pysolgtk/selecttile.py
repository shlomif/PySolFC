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

## import os, string, sys, types
import gobject, gtk
from gtk import gdk

# PySol imports
## from pysollib.mfxutil import destruct, Struct, KwStruct
from pysollib.resource import CSI
from pysollib.mfxutil import kwdefault

# Toolkit imports
## from tkutil import loadImage
from tkwidget import MfxDialog
from tkcanvas import MfxCanvas
from tkutil import setTransient
from pysoltree import PysolTreeView


class SelectTileDialogWithPreview(MfxDialog):

    def __init__(self, parent, title, app, manager, key=None, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, **kw)
        #
        top_box, bottom_box = self.createHBox()
        #
        if key is None:
            key = manager.getSelected()
        self.app = app
        self.manager = manager
        self.key = key
        self.preview_key = -1
        self.all_keys = []
        self.table_color = app.opt.colors['table']
        # paned
        hpaned = gtk.HPaned()
        self.hpaned = hpaned
        hpaned.show()
        top_box.pack_start(hpaned, expand=True, fill=True)
        #
        model = self._createStore(manager, key)
        treeview = PysolTreeView(self, model)
        self.treeview = treeview
        hpaned.pack1(treeview.scrolledwindow, True, True)
        treeview.treeview.expand_all()
        #
        self.preview = MfxCanvas(top_box) # width=w2
        hpaned.pack2(self.preview, True, True)
        self.preview.show()
        hpaned.set_position(240)

        self.createButtons(bottom_box, kw)

        self.updatePreview(key)

        self.show_all()
        gtk.main()


    def rowActivated(self, w, row, col):
        # FIXME
        print 'row-activated-event', row, col


    def getSelected(self):
        index = self.treeview.getSelected()
        if index < 0:
            return None
        return self.all_keys[index]


    def showSelected(self, w):
        key = self.getSelected()
        self.updatePreview(key)


    def _createStore(self, manager, key):
        self.all_keys = []
        index = 0
        #
        model = gtk.TreeStore(gobject.TYPE_STRING,
                              gobject.TYPE_INT)
        #
        iter = model.append(None)
        model.set(iter, 0, _('Solid color'), 1, -1)
        for color, value in ((_('Blue'),   '#0082df'),
                             (_('Green'),  '#008200'),
                             (_('Navy'),   '#000086'),
                             (_('Olive'),  '#868200'),
                             (_('Orange'), '#f79600'),
                             (_('Teal'),   '#008286'),):
            child_iter = model.append(iter)
            model.set(child_iter, 0, color, 1, index)
            self.all_keys.append(value)
            index += 1
        #
        tiles = manager.getAllSortedByName()
        tiles = [obj for obj in tiles if not obj.error]
        tiles = [tile for tile in tiles if tile.index > 0 and tile.filename]
        #
        iter = model.append(None)
        model.set(iter, 0, _('All Backgrounds'), 1, -1)
        if tiles:
            for tile in tiles:
                child_iter = model.append(iter)
                model.set(child_iter, 0, tile.name, 1, index)
                self.all_keys.append(tile.index)
                index += 1
        else:
            child_iter = model.append(iter)
            model.set(child_iter, 0, _('(no tiles)'), 1, -1)

        return model


    def updatePreview(self, key):
        ##print 'updatePreview:', key, type(key)
        if key is None:
            return
        if key == self.preview_key:
            return
        canvas = self.preview
        ##canvas.deleteAllItems()
        if isinstance(key, str):
            # solid color
            canvas.setTile(self.app, 0, force=True)
            canvas.config(bg=key)
            ##canvas.setTextColor(None)
            self.preview_key = key
            self.table_color = key
        else:
            # image
            if self.preview.setTile(self.app, key):
                self.preview_key = key
            else:
                self.preview_key = -1


    def initKw(self, kw):
        kwdefault(kw,
                  strings=(_('&OK'), _('&Solid color...'), _('&Cancel'),),
                  default=0,
                  resizable=1,
                  padx=10, pady=10,
                  width=600, height=400,
                  )
        return MfxDialog.initKw(self, kw)


    def _colorselOkClicked(self, w, d):
        c = d.colorsel.get_current_color()
        c = '#%02x%02x%02x' % (c.red/256, c.green/256, c.blue/256)
        d.destroy()
        self.updatePreview(c)
        self.treeview.unselectAll()


    def createColorsel(self):
        win = gtk.ColorSelectionDialog(_('Select table color'))
        win.help_button.destroy()
        win.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        if isinstance(self.preview_key, str):
            color =  self.preview_key
        else:
            color = self.app.opt.colors['table']
        win.colorsel.set_current_color(gdk.color_parse(color))
        win.connect('delete_event', lambda w, e: win.destroy())
        win.ok_button.connect('clicked', self._colorselOkClicked, win)
        win.cancel_button.connect('clicked', lambda w: win.destroy())
        setTransient(win, self)
        win.show()


    def done(self, button):
        b = button.get_data('user_data')
        if b == 1:
            self.createColorsel()
            return
        if b == 0:
            self.key = self.getSelected()
            if not self.key:
                self.key = self.preview_key
        self.status = 0
        self.button = b
        ##self.hide()
        self.quit()



