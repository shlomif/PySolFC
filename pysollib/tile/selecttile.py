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

import os

from pysollib.mfxutil import KwStruct
from pysollib.mygettext import _
from pysollib.ui.tktile.selecttree import SelectDialogTreeData
from pysollib.ui.tktile.tkutil import bind

import six
from six.moves import tkinter
from six.moves import tkinter_colorchooser
from six.moves import tkinter_ttk as ttk

from .selecttree import SelectDialogTreeCanvas
from .selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from .tkwidget import MfxDialog, MfxScrolledCanvas


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
                node = SelectTileLeaf(
                    self.tree, self, text=obj.name, key=obj.index)
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
        self.all_objects = [tile for tile in self.all_objects
                            if tile.index > 0 and tile.filename]
        self.no_contents = [SelectTileLeaf(
            None, None, _("(no tiles)"), key=None), ]
        # e1 = isinstance(key, str) or len(self.all_objects) <= 17
        # e2 = 0
        self.rootnodes = (
            SelectTileNode(
                None, _("All Backgrounds"),
                lambda tile: 1, expanded=0),
            SelectTileNode(
                None, _("Textures"),
                lambda tile: os.path.basename(
                    os.path.dirname(tile.filename)) == 'tiles', expanded=0),
            SelectTileNode(
                None, _("Images"),
                lambda tile: (os.path.basename(
                              os.path.dirname(tile.filename)) in
                              ('stretch', 'save-aspect')), expanded=0),
            SelectTileNode(None, _("Solid Colors"), (
                SelectTileLeaf(None, None, _("Blue"), key="#0082df"),
                SelectTileLeaf(None, None, _("Green"), key="#008200"),
                SelectTileLeaf(None, None, _("Navy"), key="#000086"),
                SelectTileLeaf(None, None, _("Olive"), key="#868200"),
                SelectTileLeaf(None, None, _("Orange"), key="#f79600"),
                SelectTileLeaf(None, None, _("Teal"), key="#008286"),
            ), expanded=0),
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

        # Title bar height - based on parent window as this window
        # isn't visible yet.  Less accurate, but looks cleaner.
        th = int(parent.winfo_rooty() - parent.winfo_y())

        sw = self.top.winfo_screenwidth()
        sh = self.top.winfo_screenheight()

        h = int(sh * .8)
        w = int(sw * .8)
        w1 = int(min(275, sw / 2.5))
        geometry = ("%dx%d+%d+%d" % (w, h, (sw - w) / 2, ((sh - h) / 2) - th))
        self.top.wm_minsize(400, 200)

        padx, pady = 4, 4

        paned_window = ttk.PanedWindow(top_frame, orient='horizontal')
        paned_window.pack(expand=True, fill='both', padx=8, pady=8)
        left_frame = ttk.Frame(paned_window)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame)
        paned_window.add(right_frame)

        notebook = ttk.Notebook(left_frame)
        notebook.pack(expand=True, fill='both')
        tree_frame = ttk.Frame(notebook)
        notebook.add(tree_frame, text=_('Tree View'))
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text=_('Search'))

        font = app.getFont("default")
        padx, pady = 4, 4
        self.tree = self.Tree_Class(self, tree_frame, key=key,
                                    default=kw.default,
                                    font=font, width=w1)
        self.tree.frame.pack(padx=padx, pady=pady, expand=True, fill='both')

        # Search
        searchText = tkinter.StringVar()
        self.list_searchlabel = tkinter.Label(search_frame, text="Search:",
                                              justify='left', anchor='w')
        self.list_searchlabel.pack(side="top", fill='both', ipadx=1)
        self.list_searchtext = tkinter.Entry(search_frame,
                                             textvariable=searchText)
        self.list_searchtext.pack(side="top", fill='both',
                                  padx=padx, pady=pady, ipadx=1)
        searchText.trace('w', self.performSearch)

        self.list_scrollbar = tkinter.Scrollbar(search_frame)
        self.list_scrollbar.pack(side="right", fill='both')

        self.createBitmaps(search_frame, kw)
        self.list = tkinter.Listbox(search_frame, exportselection=False)
        self.list.pack(padx=padx, pady=pady, expand=True, side='left',
                       fill='both', ipadx=1)
        self.updateSearchList("")
        bind(self.list, '<<ListboxSelect>>', self.selectSearchResult)
        bind(self.list, '<FocusOut>',
             lambda e: self.list.selection_clear(0, 'end'))

        self.list.config(yscrollcommand=self.list_scrollbar.set)
        self.list_scrollbar.config(command=self.list.yview)

        self.preview = MfxScrolledCanvas(right_frame, hbar=0, vbar=0)
        self.preview.pack(side="right", fill='both', expand=True,
                          padx=padx, pady=pady)

        self.preview.canvas.preview = 1
        # create a preview of the current state
        self.preview_key = -1
        self.updatePreview(key)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.tree.frame

        self.mainloop(focus, kw.timeout, geometry=geometry)

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
            if isinstance(self.tree.selection_key, six.string_types):
                self.key = str(self.tree.selection_key)
            else:
                self.key = self.tree.selection_key
            self.tree.n_expansions = 1  # save xyview in any case
        if button == 10:        # "Solid color..."
            try:
                c = tkinter_colorchooser.askcolor(
                    master=self.top,
                    initialcolor=self.table_color,
                    title=_("Select table color"))
            except tkinter.TclError:
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

    def performSearch(self, *args):
        self.updateSearchList(self.list_searchtext.get())

    def updateSearchList(self, searchString):
        self.list.delete(0, "end")
        self.list.vbar_show = True
        tiles = self.manager.getAllSortedByName()

        results = []
        for tile in tiles:
            if tile.name == 'None':
                continue
            if self.app.checkSearchString(searchString, tile.name):
                results.append(tile.name)
        results.sort()
        pos = 0
        for result in results:
            self.list.insert(pos, result)
            pos += 1

    def selectSearchResult(self, event):
        if self.list.size() <= 0:
            return
        oldcur = self.list["cursor"]
        self.list["cursor"] = "watch"
        sel = self.list.get(self.list.curselection())
        cardset = self.manager.getByName(sel).index
        self.list.update_idletasks()
        self.tree.n_selections += 1
        self.tree.updateSelection(cardset)
        self.updatePreview(cardset)
        self.list["cursor"] = oldcur

    def updatePreview(self, key):
        if key == self.preview_key:
            return
        canvas = self.preview.canvas
        canvas.deleteAllItems()
        if isinstance(key, six.string_types):
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
