## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
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
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##


# imports
import os, string, sys, types
import Tkinter, tkColorChooser

# PySol imports
from pysollib.mfxutil import destruct, Struct, KwStruct
from pysollib.resource import CSI

# Toolkit imports
from tkutil import loadImage
from tkwidget import MfxDialog, MfxScrolledCanvas
from selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from selecttree import SelectDialogTreeData, SelectDialogTreeCanvas


# /***********************************************************************
# // Nodes
# ************************************************************************/

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


# /***********************************************************************
# // Tree database
# ************************************************************************/

class SelectTileData(SelectDialogTreeData):
    def __init__(self, manager, key):
        SelectDialogTreeData.__init__(self)
        self.all_objects = manager.getAllSortedByName()
        self.all_objects = filter(lambda obj: not obj.error, self.all_objects)
        self.all_objects = filter(lambda tile: tile.index > 0 and tile.filename, self.all_objects)
        self.no_contents = [ SelectTileLeaf(None, None, _("(no tiles)"), key=None), ]
        e1 = type(key) is types.StringType or len(self.all_objects) <=17
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


# /***********************************************************************
# // Canvas that shows the tree
# ************************************************************************/

class SelectTileTree(SelectDialogTreeCanvas):
    data = None


# /***********************************************************************
# // Dialog
# ************************************************************************/

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
        self.table_color = app.opt.table_color
        if self.TreeDataHolder_Class.data is None:
            self.TreeDataHolder_Class.data = self.TreeData_Class(manager, key)
        #
        self.top.wm_minsize(400, 200)
        if self.top.winfo_screenwidth() >= 800:
            w1, w2 = 200, 400
        else:
            w1, w2 = 200, 300
        font = app.getFont("default")
        self.tree = self.Tree_Class(self, top_frame, key=key,
                                    default=kw.default,
                                    font=font,
                                    width=w1)
        self.tree.frame.pack(side="left", fill=Tkinter.BOTH, expand=0, padx=kw.padx, pady=kw.pady)
        self.preview = MfxScrolledCanvas(top_frame, width=w2, hbar=0, vbar=0)
        self.preview.pack(side="right", fill=Tkinter.BOTH, expand=1,
                          padx=kw.padx, pady=kw.pady)
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
                      strings=(_("&OK"), _("&Solid color..."), _("&Cancel"),),
                      default=0,
                      resizable=1,
                      font=None,
                      padx=10, pady=10,
                      buttonpadx=10, buttonpady=5,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        if button == 0:        # "OK" or double click
            if type(self.tree.selection_key) in types.StringTypes:
                self.key = str(self.tree.selection_key)
            else:
                self.key = self.tree.selection_key
            self.tree.n_expansions = 1  # save xyview in any case
        if button == 1:        # "Solid color..."
            c = tkColorChooser.askcolor(master=self.top,
                                        initialcolor=self.table_color,
                                        title=_("Select table color"))
            if c and c[1]:
                color = str(c[1])
                self.key = color.lower()
                self.table_color = self.key
                self.tree.updateSelection(self.key)
                self.updatePreview(self.key)
            return
        MfxDialog.mDone(self, button)

    def updatePreview(self, key):
        ##print key
        if key == self.preview_key:
            return
        canvas = self.preview.canvas
        canvas.deleteAllItems()
        if type(key) in types.StringTypes:
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

