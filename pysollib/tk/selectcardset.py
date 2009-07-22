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

__all__ = ['SelectCardsetDialogWithPreview']

# imports
import os
import Tkinter

# PySol imports
from pysollib.mfxutil import KwStruct
from pysollib.util import CARDSET
from pysollib.resource import CSI

# Toolkit imports
from tkutil import loadImage
from tkwidget import MfxDialog, MfxScrolledCanvas
from tkcanvas import MfxCanvasImage
from selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from selecttree import SelectDialogTreeData, SelectDialogTreeCanvas


# ************************************************************************
# * Nodes
# ************************************************************************

class SelectCardsetLeaf(SelectDialogTreeLeaf):
    pass


class SelectCardsetNode(SelectDialogTreeNode):
    def _getContents(self):
        contents = []
        for obj in self.tree.data.all_objects:
            if self.select_func(obj):
                node = SelectCardsetLeaf(self.tree, self, text=obj.name, key=obj.index)
                contents.append(node)
        return contents or self.tree.data.no_contents


# ************************************************************************
# * Tree database
# ************************************************************************

class SelectCardsetData(SelectDialogTreeData):
    def __init__(self, manager, key):
        SelectDialogTreeData.__init__(self)
        self.all_objects = manager.getAllSortedByName()
        self.all_objects = [obj for obj in self.all_objects if not obj.error]
        self.no_contents = [ SelectCardsetLeaf(None, None, _("(no cardsets)"), key=None), ]
        #
        select_by_type = None
        items = CSI.TYPE.items()
        items.sort(lambda a, b: cmp(a[1], b[1]))
        nodes = []
        for key, name in items:
            if manager.registered_types.get(key):
                nodes.append(SelectCardsetNode(None, name, lambda cs, key=key: key == cs.si.type))
        if nodes:
            select_by_type = SelectCardsetNode(None, _("by Type"), tuple(nodes), expanded=1)
        #
        select_by_style = None
        items = CSI.STYLE.items()
        items.sort(lambda a, b: cmp(a[1], b[1]))
        nodes = []
        for key, name in items:
            if manager.registered_styles.get(key):
                nodes.append(SelectCardsetNode(None, name, lambda cs, key=key: key in cs.si.styles))
        if nodes:
            nodes.append(SelectCardsetNode(None, _("Uncategorized"), lambda cs: not cs.si.styles))
            select_by_style = SelectCardsetNode(None, _("by Style"), tuple(nodes))
        #
        select_by_nationality = None
        items = CSI.NATIONALITY.items()
        items.sort(lambda a, b: cmp(a[1], b[1]))
        nodes = []
        for key, name in items:
            if manager.registered_nationalities.get(key):
                nodes.append(SelectCardsetNode(None, name, lambda cs, key=key: key in cs.si.nationalities))
        if nodes:
            nodes.append(SelectCardsetNode(None, _("Uncategorized"), lambda cs: not cs.si.nationalities))
            select_by_nationality = SelectCardsetNode(None, _("by Nationality"), tuple(nodes))
        #
        select_by_date = None
        items = CSI.DATE.items()
        items.sort(lambda a, b: cmp(a[1], b[1]))
        nodes = []
        for key, name in items:
            if manager.registered_dates.get(key):
                nodes.append(SelectCardsetNode(None, name, lambda cs, key=key: key in cs.si.dates))
        if nodes:
            nodes.append(SelectCardsetNode(None, _("Uncategorized"), lambda cs: not cs.si.dates))
            select_by_date = SelectCardsetNode(None, _("by Date"), tuple(nodes))
        #
        self.rootnodes = filter(None, (
            SelectCardsetNode(None, _("All Cardsets"), lambda cs: 1, expanded=len(self.all_objects)<=12),
            SelectCardsetNode(None, _("by Size"), (
                SelectCardsetNode(None, _("Tiny cardsets"),   lambda cs: cs.si.size == CSI.SIZE_TINY),
                SelectCardsetNode(None, _("Small cardsets"),  lambda cs: cs.si.size == CSI.SIZE_SMALL),
                SelectCardsetNode(None, _("Medium cardsets"), lambda cs: cs.si.size == CSI.SIZE_MEDIUM),
                SelectCardsetNode(None, _("Large cardsets"),  lambda cs: cs.si.size == CSI.SIZE_LARGE),
                SelectCardsetNode(None, _("XLarge cardsets"), lambda cs: cs.si.size == CSI.SIZE_XLARGE),
            ), expanded=1),
            select_by_type,
            select_by_style,
            select_by_date,
            select_by_nationality,
        ))


class SelectCardsetByTypeData(SelectDialogTreeData):
    def __init__(self, manager, key):
        SelectDialogTreeData.__init__(self)
        self.all_objects = manager.getAllSortedByName()
        self.no_contents = [ SelectCardsetLeaf(None, None, _("(no cardsets)"), key=None), ]
        #
        items = CSI.TYPE.items()
        items.sort(lambda a, b: cmp(a[1], b[1]))
        nodes = []
        for key, name in items:
            if manager.registered_types.get(key):
                nodes.append(SelectCardsetNode(None, name, lambda cs, key=key: key == cs.si.type))
        select_by_type = SelectCardsetNode(None, _("by Type"), tuple(nodes), expanded=1)
        #
        self.rootnodes = filter(None, (
            select_by_type,
        ))


# ************************************************************************
# * Canvas that shows the tree
# ************************************************************************

class SelectCardsetTree(SelectDialogTreeCanvas):
    data = None


class SelectCardsetByTypeTree(SelectDialogTreeCanvas):
    data = None


# ************************************************************************
# * Dialog
# ************************************************************************

class SelectCardsetDialogWithPreview(MfxDialog):
    Tree_Class = SelectCardsetTree
    TreeDataHolder_Class = SelectCardsetTree
    TreeData_Class = SelectCardsetData

    def __init__(self, parent, title, app, manager, key=None, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        if key is None:
            key = manager.getSelected()
        self.manager = manager
        self.key = key
        #padx, pady = kw.padx, kw.pady
        padx, pady = 5, 5
        if self.TreeDataHolder_Class.data is None:
            self.TreeDataHolder_Class.data = self.TreeData_Class(manager, key)
        #
        self.top.wm_minsize(400, 200)
        if self.top.winfo_screenwidth() >= 800:
            w1, w2 = 216, 400
        else:
            w1, w2 = 200, 300
        paned_window = Tkinter.PanedWindow(top_frame)
        paned_window.pack(expand=True, fill='both')
        left_frame = Tkinter.Frame(paned_window)
        right_frame = Tkinter.Frame(paned_window)
        paned_window.add(left_frame)
        paned_window.add(right_frame)

        font = app.getFont("default")
        self.tree = self.Tree_Class(self, left_frame, key=key,
                                    default=kw.default,
                                    font=font, width=w1)
        self.tree.frame.pack(fill='both', expand=True, padx=padx, pady=pady)
        self.preview = MfxScrolledCanvas(right_frame, width=w2)
        self.preview.setTile(app, app.tabletile_index, force=True)
        self.preview.pack(fill='both', expand=True, padx=padx, pady=pady)
        self.preview.canvas.preview = 1
        # create a preview of the current state
        self.preview_key = -1
        self.preview_images = []
        self.updatePreview(key)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.tree.frame
        self.mainloop(focus, kw.timeout)

    def destroy(self):
        self.tree.updateNodesWithTree(self.tree.rootnodes, None)
        self.tree.destroy()
        self.preview.unbind_all()
        self.preview_images = []
        MfxDialog.destroy(self)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Load"), _("&Cancel"),),
                      default=0,
                      resizable=True,
                      padx=10, pady=10,
                      buttonpadx=10, buttonpady=5,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        if button in (0, 1):               # Ok/Load
            self.key = self.tree.selection_key
            self.tree.n_expansions = 1  # save xyview in any case
        if button in (3, 4):
            cs = self.manager.get(self.tree.selection_key)
            if not cs:
                return
            ##title = CARDSET+" "+cs.name
            title = CARDSET.capitalize()+" "+cs.name
            CardsetInfoDialog(self.top, title=title, cardset=cs, images=self.preview_images)
            return
        MfxDialog.mDone(self, button)

    def updatePreview(self, key):
        if key == self.preview_key:
            return
        canvas = self.preview.canvas
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
        canvas.config(scrollregion=(0, 0, sx+dx, sy+dy),
                      width=sx+dx, height=sy+dy)
        canvas.event_generate('<Configure>') # update bg image
        #canvas.config(xscrollincrement=dx, yscrollincrement=dy)
        self.preview_key = key


class SelectCardsetByTypeDialogWithPreview(SelectCardsetDialogWithPreview):
    Tree_Class = SelectCardsetByTypeTree
    TreeDataHolder_Class = SelectCardsetByTypeTree
    TreeData_Class = SelectCardsetByTypeData

# ************************************************************************
# * Cardset Info
# ************************************************************************

class CardsetInfoDialog(MfxDialog):
    def __init__(self, parent, title, cardset, images, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        frame = Tkinter.Frame(top_frame)
        frame.pack(fill="both", expand=True, padx=5, pady=10)
        #
        #
        info_frame = Tkinter.LabelFrame(frame, text=_('About cardset'))
        info_frame.grid(row=0, column=0, columnspan=2, sticky='ew',
                        padx=0, pady=5, ipadx=5, ipady=5)
        styles = nationalities = year = None
        if cardset.si.styles:
            styles = '\n'.join([CSI.STYLE[i] for i in cardset.si.styles])
        if cardset.si.nationalities:
            nationalities = '\n'.join([CSI.NATIONALITY[i]
                                       for i in cardset.si.nationalities])
        if cardset.year:
            year = str(cardset.year)
        row = 0
        for n, t in (
            ##('Version:', str(cardset.version)),
            (_('Type:'),          CSI.TYPE[cardset.type]),
            (_('Styles:'),        styles),
            (_('Nationality:'),   nationalities),
            (_('Year:'),          year),
            ##(_('Number of cards:'), str(cardset.ncards)),
            (_('Size:'), '%d x %d' % (cardset.CARDW, cardset.CARDH)),
            ):
            if t is not None:
                l = Tkinter.Label(info_frame, text=n,
                                  anchor='w', justify='left')
                l.grid(row=row, column=0, sticky='nw')
                l = Tkinter.Label(info_frame, text=t,
                                  anchor='w', justify='left')
                l.grid(row=row, column=1, sticky='nw')
                row += 1
        if images:
            try:
                from random import choice
                im = choice(images)
                f = os.path.join(cardset.dir, cardset.backname)
                self.back_image = loadImage(file=f)
                canvas = Tkinter.Canvas(info_frame,
                                        width=2*im.width()+30,
                                        height=im.height()+2)
                canvas.create_image(10, 1, image=im, anchor='nw')
                canvas.create_image(im.width()+20, 1,
                                    image=self.back_image, anchor='nw')
                canvas.grid(row=0, column=2, rowspan=row+1, sticky='ne')
                info_frame.columnconfigure(2, weight=1)
                info_frame.rowconfigure(row, weight=1)
            except:
                pass
        ##bg = top_frame["bg"]
        bg = 'white'
        text_w = Tkinter.Text(frame, bd=1, relief="sunken", wrap="word",
                              padx=4, width=64, height=16, bg=bg)
        text_w.grid(row=1, column=0, sticky='nsew')
        sb = Tkinter.Scrollbar(frame)
        sb.grid(row=1, column=1, sticky='ns')
        text_w.configure(yscrollcommand=sb.set)
        sb.configure(command=text_w.yview)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        #
        text = ''
        f = os.path.join(cardset.dir, "COPYRIGHT")
        try:
            text = open(f).read()
        except:
            pass
        if text:
            text_w.config(state="normal")
            text_w.insert("insert", text)
        text_w.config(state="disabled")
        #
        focus = self.createButtons(bottom_frame, kw)
        #focus = text_w
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),),
                      default=0,
                      resizable=True,
                      separator=True,
                      padx=10, pady=10,
                      buttonpadx=10, buttonpady=5,
                      )
        return MfxDialog.initKw(self, kw)


