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
import os, re, sys, types
import gtk, gobject

# PySol imports
from pysollib.resource import CSI
from pysollib.mfxutil import kwdefault

# Toolkit imports
from tkwidget import MfxDialog
from pysoltree import PysolTreeView
from tkcanvas import MfxCanvas, MfxCanvasImage
from tkutil import loadImage


# ************************************************************************
# * Dialog
# ************************************************************************

class SelectCardsetDialogWithPreview(MfxDialog):
    _cardset_store = None

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

        if self._cardset_store is None:
            self._createStore()

        #padx, pady = kw.padx, kw.pady
        padx, pady = 5, 5
        # left
        # paned
        hpaned = gtk.HPaned()
        self.hpaned = hpaned
        hpaned.show()
        top_box.pack_start(hpaned, expand=True, fill=True)
        # tree
        treeview = PysolTreeView(self, self._cardset_store)
        self.treeview = treeview
        hpaned.pack1(treeview.scrolledwindow, True, True)
        ##treeview.treeview.expand_all()
        # right
        sw = gtk.ScrolledWindow()
        sw.show()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hpaned.pack2(sw, True, True)
        ##self.scrolledwindow = sw
        #
        self.preview = MfxCanvas(self)
        self.preview.show()
        sw.add(self.preview)
        #hpaned.pack2(self.preview, True, True)
        self.preview.setTile(app, app.tabletile_index, force=True)
        #
        hpaned.set_position(240)

        self.createButtons(bottom_box, kw)

        ##~self.updatePreview(key)

        self.show_all()
        gtk.main()


    def _selectCardset(self, all_cardsets, selecter):
        if selecter is None:
            return [(cs.index, cs.name) for cs in all_cardsets]
        return [(cs.index, cs.name) for cs in all_cardsets if selecter(cs)]


    def _addCardsets(self, store, root_iter, root_label, cardsets):
        iter = store.append(root_iter)
        store.set(iter, 0, root_label, 1, -1)
        for index, name in cardsets:
            child_iter = store.append(iter)
            ##~ name = _(name)
            store.set(child_iter, 0, name, 1, index)


    def _addCardsetsByType(self, store, root_label, all_cardsets,
                           cardset_types, selecter_type, registered):
        manager = self.manager
        root_iter = store.append(None)
        store.set(root_iter, 0, root_label, 1, -1)
        items = cardset_types.items()
        items.sort(lambda a, b: cmp(a[1], b[1]))
        added = False
        for key, label in items:
            if key not in getattr(manager, registered):
                continue
            cardsets = []
            for cs in all_cardsets:
                si = getattr(cs.si, selecter_type)
                if isinstance(si, int): # type
                    if key == si:
                        cardsets.append((cs.index, cs.name))
                else: # style, nationality, date
                    if key in si:
                        cardsets.append((cs.index, cs.name))
            if cardsets:
                added = True
                self._addCardsets(store, root_iter, label, cardsets)
        if added:
            selecter = lambda cs, selecter_type=selecter_type: \
                           not getattr(cs.si, selecter_type)
            cs = self._selectCardset(all_cardsets, selecter)
            if cs:
                self._addCardsets(store, root_iter, _('Uncategorized'), cs)
        else:
            iter = store.append(root_iter)
            store.set(iter, 0, _('(no cardsets)'), 1, -1)

    def _createStore(self):
        store = gtk.TreeStore(gobject.TYPE_STRING,
                              gobject.TYPE_INT)
        manager = self.manager
        all_cardsets = manager.getAllSortedByName()
        all_cardsets = [obj for obj in all_cardsets if not obj.error]

        cs = self._selectCardset(all_cardsets, None)
        self._addCardsets(store, None, 'All cadsets', cs)

        root_iter = store.append(None)
        store.set(root_iter, 0, _('by Size'), 1, -1)
        for label, selecter in (
            (_("Tiny cardsets"),   lambda cs: cs.si.size == CSI.SIZE_TINY),
            (_("Small cardsets"),  lambda cs: cs.si.size == CSI.SIZE_SMALL),
            (_("Medium cardsets"), lambda cs: cs.si.size == CSI.SIZE_MEDIUM),
            (_("Large cardsets"),  lambda cs: cs.si.size == CSI.SIZE_LARGE),
            (_("XLarge cardsets"), lambda cs: cs.si.size == CSI.SIZE_XLARGE),):
            cs = self._selectCardset(all_cardsets, selecter)
            if cs:
                self._addCardsets(store, root_iter, label, cs)

        self._addCardsetsByType(store, _('by Type'), all_cardsets,
                                CSI.TYPE, 'type', 'registered_types')
        self._addCardsetsByType(store, _('by Style'), all_cardsets,
                                CSI.STYLE, 'styles', 'registered_styles')
        self._addCardsetsByType(store, _('by Nationality'), all_cardsets,
                                CSI.NATIONALITY, 'nationalities',
                                'registered_nationalities')
        self._addCardsetsByType(store, _('by Date'), all_cardsets,
                                CSI.DATE, 'dates', 'registered_dates')

        self._cardset_store = store


    def getSelected(self):
        index = self.treeview.getSelected()
        if index < 0:
            return None
        return index


    def showSelected(self, w):
        key = self.getSelected()
        if key is not None:
            self.updatePreview(key)
        pass


    def updatePreview(self, key):
        if key == self.preview_key:
            return
        canvas = self.preview
        canvas.deleteAllItems()
        self.preview_images = []
        cs = self.manager.get(key)
        if not cs:
            self.preview_key = -1
            return
        names, columns = cs.getPreviewCardNames()
        try:
            #???names, columns = cs.getPreviewCardNames()
            for n in names:
                f = os.path.join(cs.dir, n + cs.ext)
                self.preview_images.append(loadImage(file=f))
        except:
            self.preview_key = -1
            self.preview_images = []
            return
        i, x, y, sx, sy, dx, dy = 0, 10, 10, 0, 0, cs.CARDW + 10, cs.CARDH + 10
        for image in self.preview_images:
            MfxCanvasImage(canvas, x, y, anchor="nw", image=image)
            sx, sy = max(x, sx), max(y, sy)
            i = i + 1
            if i % columns == 0:
                x, y = 10, y + dy
            else:
                x = x + dx
        canvas.config(width=sx+dx, height=sy+dy)
        canvas.set_scroll_region(0, 0, sx+dx, sy+dy)
        self.preview_key = key


    def initKw(self, kw):
        kwdefault(kw,
                  strings=(_("&Load"), _("&Cancel"), _("&Info..."),),
                  default=1,
                  resizable=1,
                  padx=10, pady=10,
                  width=600, height=400,
                  )
        return MfxDialog.initKw(self, kw)


    def createInfo(self):
        pass


    def done(self, button):
        b = button.get_data('user_data')
        if b == 2:
            self.createInfo()
            return
        if b == 0:
            self.key = self.getSelected()
            if not self.key:
                self.key = self.preview_key
        self.status = 0
        self.button = b
        self.hide()
        self.quit()




