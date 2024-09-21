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
import tkinter

from pysollib.mfxutil import KwStruct, USE_PIL
from pysollib.mygettext import _
from pysollib.resource import TTI
from pysollib.ui.tktile.selecttree import SelectDialogTreeData
from pysollib.ui.tktile.tkutil import bind

from six.moves import tkinter_colorchooser
from six.moves import tkinter_ttk as ttk

from .selecttree import SelectDialogTreeCanvas
from .selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from .tkwidget import MfxDialog, MfxScrolledCanvas, PysolCombo


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
                None, _("Tiles"),
                lambda tile: os.path.basename(
                    os.path.dirname(tile.filename)) == 'tiles', expanded=0),
            SelectTileNode(
                None, _("Images"),
                lambda tile: (os.path.basename(
                    os.path.dirname(tile.filename)) in
                              ('stretch', 'save-aspect', 'stretch-4k',
                               'save-aspect-4k')), expanded=0),
            SelectTileNode(None, _("Solid Colors"), (
                SelectTileLeaf(None, None, _("Azure"), key="#0082df"),
                SelectTileLeaf(None, None, _("Black"), key="#000000"),
                SelectTileLeaf(None, None, _("Blue"), key="#0000ff"),
                SelectTileLeaf(None, None, _("Bright Green"), key="#00ff00"),
                SelectTileLeaf(None, None, _("Brown"), key="#684700"),
                SelectTileLeaf(None, None, _("Cyan"), key="#00ffff"),
                SelectTileLeaf(None, None, _("Grey"), key="#888888"),
                SelectTileLeaf(None, None, _("Green"), key="#008200"),
                SelectTileLeaf(None, None, _("Magenta"), key="#ff00ff"),
                SelectTileLeaf(None, None, _("Navy"), key="#000086"),
                SelectTileLeaf(None, None, _("Olive"), key="#868200"),
                SelectTileLeaf(None, None, _("Orange"), key="#f79600"),
                SelectTileLeaf(None, None, _("Pink"), key="#ff92fc"),
                SelectTileLeaf(None, None, _("Purple"), key="#8300ff"),
                SelectTileLeaf(None, None, _("Red"), key="#ff0000"),
                SelectTileLeaf(None, None, _("Teal"), key="#008286"),
                SelectTileLeaf(None, None, _("White"), key="#ffffff"),
                SelectTileLeaf(None, None, _("Yellow"), key="#ffff00"),
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
        self.criteria = SearchCriteria()
        self.key = key
        self.table_color = app.opt.colors['table']
        if self.TreeDataHolder_Class.data is None:
            self.TreeDataHolder_Class.data = self.TreeData_Class(manager, key)
        #

        pw = parent.winfo_width()
        ph = parent.winfo_height()
        py = parent.winfo_y()
        px = parent.winfo_x()

        h = int(ph * .8)
        w = int(pw * .8)
        w1 = int(min(275, pw / 2.5))
        geometry = ("%dx%d+%d+%d" % (w, h, px + ((pw - w) / 2),
                                     py + (int((ph - h) / 1.5))))
        self.top.wm_minsize(400, 200)

        padx, pady = 4, 4

        paned_window = ttk.PanedWindow(top_frame, orient='horizontal')
        paned_window.pack(expand=True, fill='both', padx=8, pady=8)
        left_frame = ttk.Frame(paned_window)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame)
        paned_window.add(right_frame)

        notebook = ttk.Notebook(left_frame)
        notebook.grid(row=0, column=0, sticky='nsew',
                      padx=padx, pady=pady, columnspan=2)
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
        searchbox = ttk.Frame(search_frame)
        searchText = tkinter.StringVar()
        self.list_searchlabel = tkinter.Label(searchbox, text="Search:",
                                              justify='left', anchor='w')
        self.list_searchlabel.pack(side="top", fill='both', ipadx=1)
        self.list_searchtext = tkinter.Entry(searchbox,
                                             textvariable=searchText)

        self.advSearch = tkinter.Button(searchbox, text='...',
                                        command=self.advancedSearch)
        self.advSearch.pack(side="right")

        self.list_searchtext.pack(side="top", fill='both',
                                  padx=padx, pady=pady, ipadx=1)
        searchText.trace('w', self.basicSearch)

        searchbox.pack(side="top", fill="both")

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

        if USE_PIL:
            self.scaleOptions = {"Default": 0,
                                 "Tile": 1,
                                 "Stretch": 2,
                                 "Preserve aspect ratio": 3}
            scaleValues = list(self.scaleOptions.keys())

            self.scaling = tkinter.StringVar()
            self.scaling.set(next(key for key, value in
                                  self.scaleOptions.items()
                             if value == app.opt.tabletile_scale_method))
            self.labelScale = tkinter.Label(left_frame, text="Image scaling:",
                                            anchor="w")

            self.textScale = PysolCombo(left_frame, values=scaleValues,
                                        state='readonly',
                                        textvariable=self.scaling,
                                        selectcommand=self.updateScaling)
            self.labelScale.grid(row=4, column=0, sticky='ew',
                                 padx=padx, pady=pady)
            self.textScale.grid(row=4, column=1, sticky='ew',
                                padx=padx, pady=pady)

        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.columnconfigure(1, weight=1)

        self.preview = MfxScrolledCanvas(right_frame, hbar=0, vbar=0)
        self.preview.pack(side="right", fill='both', expand=True,
                          padx=padx, pady=pady)

        self.preview.canvas.preview = 1
        # create a preview of the current state
        self.preview_key = -1
        self.preview_scaling = -1
        self.current_key = -1
        self.updatePreview(key, app.opt.tabletile_scale_method)
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
                               'sep', _("&Select"), _("&Cancel"),),
                      default=0,
                      resizable=True,
                      font=None,
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        if button == 0:  # "OK" or double click
            if isinstance(self.tree.selection_key, str):
                self.key = str(self.tree.selection_key)
            else:
                self.key = self.tree.selection_key
            self.tree.n_expansions = 1  # save xyview in any case
        if button == 10:  # "Solid color..."
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

    def basicSearch(self, *args):
        self.updateSearchList(self.list_searchtext.get())

    def updateScaling(self, *args):
        self.updatePreview(self.preview_key,
                           self.scaleOptions[self.scaling.get()])

    def updateSearchList(self, searchString):
        self.criteria.name = searchString
        self.performSearch()

    def performSearch(self):
        self.list.delete(0, "end")
        self.list.vbar_show = True
        tiles = self.manager.getAllSortedByName()

        results = []
        for tile in tiles:
            if tile.name == 'None':
                continue

            if (self.criteria.type == "Images" and os.path.basename(
                    os.path.dirname(tile.filename)) not in
                    ('stretch', 'save-aspect', 'stretch-4k',
                     'save-aspect-4k')):
                continue
            if (self.criteria.type == "Tiles" and os.path.basename(
                    os.path.dirname(tile.filename)) != 'tiles'):
                continue
            if (self.criteria.size != ""
                    and self.criteria.sizeOptions[self.criteria.size]
                    != tile.size):
                continue

            if self.app.checkSearchString(self.criteria.name,
                                          tile.name):
                results.append(tile.name)
        results.sort(key=lambda x: x.lower())
        pos = 0
        for result in results:
            self.list.insert(pos, result)
            pos += 1

    def advancedSearch(self):
        d = SelectTileAdvancedSearch(self.top, _("Advanced search"),
                                     self.criteria)
        if d.status == 0 and d.button == 0:
            self.criteria.name = d.name.get()

            self.list_searchtext.delete(0, "end")
            self.list_searchtext.insert(0, d.name.get())

            self.criteria.type = d.type.get()
            self.criteria.size = d.size.get()

            self.performSearch()

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

    def updatePreview(self, key, scaling=-1):
        if scaling < 0:
            scaling = self.preview_scaling
        if key == self.preview_key and scaling == self.preview_scaling:
            return
        canvas = self.preview.canvas
        canvas.deleteAllItems()

        self.preview_scaling = scaling
        if isinstance(key, str):
            if USE_PIL:
                self.textScale['state'] = 'disabled'
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
                if USE_PIL:
                    if tile.stretch:
                        self.textScale['state'] = 'readonly'
                    else:
                        self.textScale['state'] = 'disabled'
                if self.preview.setTile(self.app, key, scaling):
                    self.preview_key = key
                    return
            self.preview_key = -1


class SearchCriteria:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.size = ""

        self.sizeOptions = {"": -1,
                            "Tile": TTI.SIZE_TILE,
                            "SD": TTI.SIZE_SD,
                            "HD": TTI.SIZE_HD,
                            "4K": TTI.SIZE_4K}
        self.typeOptions = ("", "Images", "Tiles")


class SelectTileAdvancedSearch(MfxDialog):
    def __init__(self, parent, title, criteria, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)

        self.createBitmaps(top_frame, kw)
        #
        self.name = tkinter.StringVar()
        self.name.set(criteria.name)
        self.type = tkinter.StringVar()
        self.type.set(criteria.type)
        self.size = tkinter.StringVar()
        self.size.set(criteria.size)
        #
        row = 0

        labelName = tkinter.Label(top_frame, text="Name:", anchor="w")
        labelName.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textName = tkinter.Entry(top_frame, textvariable=self.name)
        textName.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        typeValues = list(criteria.typeOptions)

        labelType = tkinter.Label(top_frame, text="Type:", anchor="w")
        labelType.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textType = PysolCombo(top_frame, values=typeValues,
                              textvariable=self.type, state='readonly')
        textType.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1
        if USE_PIL:
            sizeValues = list(criteria.sizeOptions.keys())

            labelSize = tkinter.Label(top_frame, text="Size:", anchor="w")
            labelSize.grid(row=row, column=0, columnspan=1, sticky='ew',
                           padx=1, pady=1)
            textSize = PysolCombo(top_frame, values=sizeValues,
                                  textvariable=self.size, state='readonly')
            textSize.grid(row=row, column=1, columnspan=4, sticky='ew',
                          padx=1, pady=1)
            row += 1

        focus = self.createButtons(bottom_frame, kw)
        # focus = text_w
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")), default=0,
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)
