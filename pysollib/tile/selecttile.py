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
import Tkinter
import ttk
import tkColorChooser

# PySol imports
from pysollib.mfxutil import KwStruct

# Toolkit imports
from tkwidget import MfxDialog, MfxScrolledCanvas
from selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from selecttree import SelectDialogTreeData, SelectDialogTreeCanvas


# ************************************************************************
# * Nodes
# ************************************************************************

class SelectTileLeaf(SelectDialogTreeLeaf):
    pass


class SelectTileNode(SelectDialogTreeNode):
    def _getContents(self):
        contents = []
        for obj in self.tree.data.all_objects:
            if self.select_func(obj):
                node = SelectTileLeaf(self.tree, self, text=obj.name, key=obj.index)
                contents.append(node)
        return contents or self.tree.data.no_contents


# ************************************************************************
# * Tree database
# ************************************************************************

class SelectTileData(SelectDialogTreeData):
    def __init__(self, manager, key):
        SelectDialogTreeData.__init__(self)
        self.all_objects = manager.getAllSortedByName()
        self.all_objects = [obj for obj in self.all_objects if not obj.error]
        self.all_objects = [tile for tile in self.all_objects if tile.index > 0 and tile.filename]
        self.no_contents = [ SelectTileLeaf(None, None, _("(no tiles)"), key=None), ]
        e1 = isinstance(key, str) or len(self.all_objects) <=17
        e2 = 1
        self.rootnodes = (
            SelectTileNode(None, _("Solid Colors"), (
                SelectTileLeaf(None, None, _("Blue"), key="#0082df"),
                SelectTileLeaf(None, None, _("Green"), key="#008200"),
                SelectTileLeaf(None, None, _("Navy"), key="#000086"),
                SelectTileLeaf(None, None, _("Olive"), key="#868200"),
                SelectTileLeaf(None, None, _("Orange"), key="#f79600"),
                SelectTileLeaf(None, None, _("Teal"), key="#008286"),
            ), expanded=e1),
            SelectTileNode(None, _("All Backgrounds"), lambda tile: 1, expanded=e2),
        )


# ************************************************************************
# * Canvas that shows the tree
# ************************************************************************

class SelectTileTree(SelectDialogTreeCanvas):
    data = None


# ************************************************************************
# * Dialog
# ************************************************************************

class SelectTileDialogWithPreview(MfxDialog):
    Tree_Class = SelectTileTree
    TreeDataHolder_Class = SelectTileTree
    TreeData_Class = SelectTileData

    def __init__(self, parent, title, app, manager, key=None, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        if key is None:
            key = manager.getSelected()
        self.app = app
        self.manager = manager
        self.key = key
        self.table_color = app.opt.colors['table']
        if self.TreeDataHolder_Class.data is None:
            self.TreeDataHolder_Class.data = self.TreeData_Class(manager, key)
        #
        self.top.wm_minsize(400, 200)
        if self.top.winfo_screenwidth() >= 800:
            w1, w2 = 200, 400
        else:
            w1, w2 = 200, 300
        font = app.getFont("default")
        padx, pady = 4, 4
        frame = ttk.Frame(top_frame)
        frame.pack(fill='both', expand=True,
                   padx=kw.padx-padx, pady=kw.pady-pady)
        self.tree = self.Tree_Class(self, frame, key=key, default=kw.default,
                                    font=font, width=w1)
        self.tree.frame.pack(side="left", fill='both', expand=False,
                             padx=padx, pady=pady)
        self.preview = MfxScrolledCanvas(frame, width=w2, hbar=0, vbar=0)
        self.preview.pack(side="right", fill='both', expand=True,
                          padx=padx, pady=pady)
        self.preview.canvas.preview = 1
        # create a preview of the current state
        self.preview_key = -1
        self.updatePreview(key)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.tree.frame
        self.mainloop(focus, kw.timeout)

    def destroy(self):
        self.tree.updateNodesWithTree(self.tree.rootnodes, None)
        self.tree.destroy()
        self.preview.unbind_all()
        MfxDialog.destroy(self)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=((_("&Solid color..."), 10),
                               'sep', _("&OK"), _("&Cancel"),),
                      default=0,
                      resizable=True,
                      font=None,
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        if button == 0:        # "OK" or double click
            if isinstance(self.tree.selection_key, basestring):
                self.key = str(self.tree.selection_key)
            else:
                self.key = self.tree.selection_key
            self.tree.n_expansions = 1  # save xyview in any case
        if button == 10:        # "Solid color..."
            try:
                c = tkColorChooser.askcolor(master=self.top,
                                            initialcolor=self.table_color,
                                            title=_("Select table color"))
            except Tkinter.TclError:
                pass
            else:
                if c and c[1]:
                    color = str(c[1])
                    self.key = color.lower()
                    self.table_color = self.key
                    self.tree.updateSelection(self.key)
                    self.updatePreview(self.key)
            return
        MfxDialog.mDone(self, button)

    def updatePreview(self, key):
        if key == self.preview_key:
            return
        canvas = self.preview.canvas
        canvas.deleteAllItems()
        if isinstance(key, basestring):
            # solid color
            canvas.config(bg=key)
            canvas.setTile(None)
            canvas.setTextColor(None)
            self.preview_key = key
            self.table_color = key
        else:
            # image
            tile = self.manager.get(key)
            if tile:
                if self.preview.setTile(self.app, key):
                    return
            self.preview_key = -1

