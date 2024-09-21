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
from pysollib.resource import CSI
from pysollib.ui.tktile.selecttree import SelectDialogTreeData
from pysollib.ui.tktile.tkcanvas import MfxCanvasImage
from pysollib.ui.tktile.tkutil import bind, loadImage
from pysollib.util import CARDSET

from six.moves import tkinter_ttk as ttk

from .selecttree import SelectDialogTreeCanvas
from .selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from .tkwidget import MfxDialog, MfxScrolledCanvas, PysolCombo, PysolScale


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
                node = SelectCardsetLeaf(
                    self.tree, self, text=obj.name, key=obj.index)
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
        self.no_contents = [SelectCardsetLeaf(
            None, None, _("(no cardsets)"), key=None), ]
        #
        select_by_type = None
        items = list(CSI.TYPE.items())
        items.sort(key=lambda x: x[1])
        nodes = []
        for key, name in items:
            if manager.registered_types.get(key):
                nodes.append(
                    SelectCardsetNode(
                        None, name, lambda cs, key=key: key == cs.si.type))
        if nodes:
            select_by_type = SelectCardsetNode(
                None, _("by Type"), tuple(nodes), expanded=1)
        #
        select_by_style = None
        items = list(CSI.STYLE.items())
        items.sort(key=lambda x: x[1])
        nodes = []
        for key, name in items:
            if manager.registered_styles.get(key):
                nodes.append(
                    SelectCardsetNode(
                        None, name, lambda cs, key=key: key in cs.si.styles))
        if nodes:
            if manager.uncategorized_styles:
                nodes.append(
                    SelectCardsetNode(
                        None, _("Uncategorized"), lambda cs: not cs.si.styles))
            select_by_style = SelectCardsetNode(
                None, _("by Style"), tuple(nodes))
        #
        select_by_nationality = None
        items = list(CSI.NATIONALITY.items())
        items.sort(key=lambda x: x[1])
        nodes = []
        for key, name in items:
            if manager.registered_nationalities.get(key):
                nodes.append(
                    SelectCardsetNode(
                        None, name,
                        lambda cs, key=key: key in cs.si.nationalities))
        if nodes:
            if manager.uncategorized_nationalities:
                nodes.append(
                    SelectCardsetNode(
                        None, _("Uncategorized"),
                        lambda cs: not cs.si.nationalities))
            select_by_nationality = SelectCardsetNode(
                None, _("by Nationality"), tuple(nodes))
        #
        select_by_date = None
        items = list(CSI.DATE.items())
        items.sort(key=lambda x: x[1])
        nodes = []
        for key, name in items:
            if manager.registered_dates.get(key):
                nodes.append(
                    SelectCardsetNode(
                        None, name, lambda cs, key=key: key in cs.si.dates))
        if nodes:
            if manager.uncategorized_dates:
                nodes.append(
                    SelectCardsetNode(
                        None, _("Uncategorized"), lambda cs: not cs.si.dates))
            select_by_date = SelectCardsetNode(
                None, _("by Date"), tuple(nodes))
        #
        self.rootnodes = [_f for _f in (
            SelectCardsetNode(
                None, _("All Cardsets"),
                lambda cs: 1, expanded=len(self.all_objects) <= 12),
            SelectCardsetNode(
                None, _("by Size"),
                (SelectCardsetNode(
                    None, _("Tiny cardsets"),
                    lambda cs: cs.si.size == CSI.SIZE_TINY),
                 SelectCardsetNode(
                    None, _("Small cardsets"),
                    lambda cs: cs.si.size == CSI.SIZE_SMALL),
                 SelectCardsetNode(
                    None, _("Medium cardsets"),
                    lambda cs: cs.si.size == CSI.SIZE_MEDIUM),
                 SelectCardsetNode(
                    None, _("Large cardsets"),
                    lambda cs: cs.si.size == CSI.SIZE_LARGE),
                 SelectCardsetNode(
                    None, _("Extra Large cardsets"),
                    lambda cs: cs.si.size == CSI.SIZE_XLARGE),
                 SelectCardsetNode(
                    None, _("Hi-Res cardsets"),
                    lambda cs: cs.si.size == CSI.SIZE_HIRES),
                 ), expanded=1),
            select_by_type,
            select_by_style,
            select_by_date,
            select_by_nationality,
        ) if _f]


class SelectCardsetByTypeData(SelectDialogTreeData):
    def __init__(self, manager, key):
        SelectDialogTreeData.__init__(self)
        self.all_objects = manager.getAllSortedByName()
        self.no_contents = [SelectCardsetLeaf(None, None, _("(no cardsets)"),
                            key=None), ]
        #
        items = list(CSI.TYPE.items())
        items.sort(key=lambda x: x[1])
        nodes = []
        for key, name in items:
            if manager.registered_types.get(key):
                nodes.append(
                    SelectCardsetNode(
                        None, name, lambda cs, key=key: key == cs.si.type))
        select_by_type = SelectCardsetNode(
            None, _("by Type"), tuple(nodes), expanded=1)
        #
        self.rootnodes = [_f for _f in (
            select_by_type,
        ) if _f]


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
        self.app = app
        self.criteria = SearchCriteria(manager)
        self.cardset_values = None
        # padx, pady = kw.padx, kw.pady
        padx, pady = 4, 4
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

        paned_window = ttk.PanedWindow(top_frame, orient='horizontal')
        paned_window.pack(expand=True, fill='both', padx=8, pady=8)
        left_frame = ttk.Frame(paned_window)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame)
        paned_window.add(right_frame)

        notebook = ttk.Notebook(left_frame)
        notebook.grid(row=0, column=0, sticky='nsew',
                      padx=padx, pady=pady)
        tree_frame = ttk.Frame(notebook)
        notebook.add(tree_frame, text=_('Tree View'))
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text=_('Search'))

        # Tree
        font = app.getFont("default")
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
            size_frame = ttk.Frame(notebook)
            notebook.add(size_frame, text=_('Card Size'))
            #
            var = tkinter.DoubleVar()
            var.set(app.opt.scale_x)
            self.scale_x = PysolScale(
                size_frame, label=_('Scale X:'),
                from_=0.5, to=4.0, resolution=0.1,
                orient='horizontal', variable=var,
                value=app.opt.scale_x,
                command=self._updateScale)
            self.scale_x.grid(
                row=1, column=0, sticky='ew', padx=padx, pady=pady)
            #
            var = tkinter.DoubleVar()
            var.set(app.opt.scale_y)
            self.scale_y = PysolScale(
                size_frame, label=_('Scale Y:'),
                from_=0.5, to=4.0, resolution=0.1,
                orient='horizontal', variable=var,
                value=app.opt.scale_y,
                command=self._updateScale)
            self.scale_y.grid(
                row=2, column=0, sticky='ew', padx=padx, pady=pady)
            #
            # sliders at new position
            cs = self.manager.get(self.tree.selection_key)

            var = tkinter.IntVar()
            self.x_offset = PysolScale(
                size_frame, label=_('X offset:'),
                from_=5, to=100, resolution=1,
                orient='horizontal', variable=var,
                value=cs.CARD_XOFFSET
                )

            self.x_offset.grid(row=3, column=0, sticky='ew',
                               padx=padx, pady=pady)

            var = tkinter.IntVar()
            self.y_offset = PysolScale(
                size_frame, label=_('Y offset:'),
                from_=5, to=100, resolution=1,
                orient='horizontal', variable=var,
                value=cs.CARD_YOFFSET
                )
            self.y_offset.grid(row=4, column=0, sticky='ew',
                               padx=padx, pady=pady)

            self.auto_scale = tkinter.BooleanVar()
            self.auto_scale.set(app.opt.auto_scale)
            check = ttk.Checkbutton(
                size_frame, text=_('Auto scaling'),
                variable=self.auto_scale,
                takefocus=False,
                command=self._updateAutoScale
                )
            check.grid(row=5, column=0, columnspan=2, sticky='ew',
                       padx=padx, pady=pady)
            #
            self.preserve_aspect = tkinter.BooleanVar()
            self.preserve_aspect.set(app.opt.preserve_aspect_ratio)
            self.aspect_check = ttk.Checkbutton(
                size_frame, text=_('Preserve aspect ratio'),
                variable=self.preserve_aspect,
                takefocus=False,
                # command=self._updateScale
                )
            self.aspect_check.grid(row=6, column=0, sticky='ew',
                                   padx=padx, pady=pady)

            self._updateAutoScale()
            size_frame.columnconfigure(0, weight=1)

        #
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        #
        self.preview = MfxScrolledCanvas(right_frame)
        self.preview.setTile(app, app.tabletile_index,
                             app.opt.tabletile_scale_method, force=True)
        self.preview.pack(fill='both', expand=True, padx=padx, pady=pady)
        self.preview.canvas.preview = 1
        # create a preview of the current state
        self.preview_key = -1
        self.preview_images = []
        self.scale_images = []
        self.updatePreview(key)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.tree.frame
        self.mainloop(focus, kw.timeout, geometry=geometry)

    def destroy(self):
        self.tree.updateNodesWithTree(self.tree.rootnodes, None)
        self.tree.destroy()
        self.preview.unbind_all()
        self.preview_images = []
        MfxDialog.destroy(self)

    def initKw(self, kw):
        s = (_("&Info..."), 10)
        kw = KwStruct(kw,
                      strings=(s, 'sep',
                               _("&Select"), _("&Cancel"),),
                      default=0,
                      resizable=True,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        if button in (0, 1):            # Load/Cancel
            self.key = self.tree.selection_key
            self.tree.n_expansions = 1  # save xyview in any case

            if button == 0:
                cardset = self.app.cardset_manager.get(self.key)
                if self.app.game is not None:
                    gi = self.app.getGameInfo(self.app.game.id)
                else:
                    gi = self.app.getGameInfo(self.app.nextgame.id)
                cs, cs_update_flag, t = \
                    self.app.getCompatibleCardset(gi, cardset, trychange=False)

                if cs is None:
                    self.app.requestCompatibleCardsetTypeDialog(cardset, gi, t)
                    return

            # save the values
            try:
                self.cardset_values = self.x_offset.get(), self.y_offset.get()
            except Exception:
                pass

            if USE_PIL:
                auto_scale = bool(self.auto_scale.get())
                if button == 1:
                    # no changes
                    self.cardset_values = None

                elif button == 0:
                    self.app.menubar.tkopt.auto_scale.set(auto_scale)

                    if auto_scale:
                        self.app.menubar.tkopt.spread_stacks.set(False)
                        self.scale_values = (self.app.opt.scale_x,
                                             self.app.opt.scale_y,
                                             auto_scale,
                                             False,
                                             bool(self.preserve_aspect.get()))
                    else:
                        self.scale_values = (self.scale_x.get(),
                                             self.scale_y.get(),
                                             auto_scale,
                                             self.app.opt.spread_stacks,
                                             self.app.opt.
                                             preserve_aspect_ratio)
        if button == 10:                # Info
            cs = self.manager.get(self.tree.selection_key)
            if not cs:
                return
            # title = CARDSET+" "+cs.name
            title = CARDSET.capitalize()+" "+cs.name
            d = CardsetInfoDialog(self.top, title=title, cardset=cs,
                                  images=self.preview_images)
            try:
                self.cardset_values = d.cardset_values
            except Exception:
                self.cardset_values = None

            return
        MfxDialog.mDone(self, button)

    def _updateAutoScale(self, v=None):
        if self.auto_scale.get():
            self.aspect_check.config(state='normal')
            self.scale_x.state('disabled')
            self.scale_y.state('disabled')
        else:
            self.aspect_check.config(state='disabled')
            self.scale_x.state('!disabled')
            self.scale_y.state('!disabled')

    def _updateScale(self, v):
        self.updatePreview()

    def basicSearch(self, *args):
        self.updateSearchList(self.list_searchtext.get())

    def updateSearchList(self, searchString):
        self.criteria.name = searchString
        self.performSearch()

    def performSearch(self):
        self.list.delete(0, "end")
        self.list.vbar_show = True
        cardsets = self.manager.getAllSortedByName()

        results = []
        for cardset in cardsets:
            if (self.criteria.size != ""
                    and self.criteria.sizeOptions[self.criteria.size]
                    != cardset.si.size):
                continue
            if (self.criteria.type != ""
                    and self.criteria.typeOptions[self.criteria.type]
                    != cardset.si.type):
                continue
            if (self.criteria.subtype != "" and
                    self.criteria.subtypeOptionsAll[self.criteria.subtype]
                    != cardset.si.subtype):
                continue
            if (self.criteria.style != ""
                    and self.criteria.styleOptions[self.criteria.style]
                    not in cardset.si.styles):
                continue
            if (self.criteria.date != ""
                    and self.criteria.dateOptions[self.criteria.date]
                    not in cardset.si.dates):
                continue
            if (self.criteria.nationality != ""
                    and self.criteria.natOptions[self.criteria.nationality]
                    not in cardset.si.nationalities):
                continue

            if self.criteria.compatible:
                if self.app.game is not None:
                    gi = self.app.getGameInfo(self.app.game.id)
                else:
                    gi = self.app.getGameInfo(self.app.nextgame.id)
                cs, cs_update_flag, t = \
                    self.app.getCompatibleCardset(gi, cardset, trychange=False)

                if cs is None:
                    continue

            if self.app.checkSearchString(self.criteria.name,
                                          cardset.name):
                results.append(cardset.name)
        results.sort(key=lambda x: x.lower())
        pos = 0
        for result in results:
            self.list.insert(pos, result)
            pos += 1

    def advancedSearch(self):
        d = SelectCardsetAdvancedSearch(self.top, _("Advanced search"),
                                        self.criteria, self.manager)
        if d.status == 0 and d.button == 0:
            self.criteria.name = d.name.get()

            self.list_searchtext.delete(0, "end")
            self.list_searchtext.insert(0, d.name.get())

            self.criteria.size = d.size.get()
            self.criteria.type = d.type.get()
            self.criteria.subtype = d.subtype.get()
            self.criteria.style = d.style.get()
            self.criteria.date = d.date.get()
            self.criteria.nationality = d.nationality.get()
            self.criteria.compatible = d.compatible.get()

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

    def updatePreview(self, key=None):
        if key == self.preview_key:
            return
        if key is None:
            key = self.key
        canvas = self.preview.canvas
        canvas.deleteAllItems()
        self.preview_images = []
        cs = self.manager.get(key)
        if not cs:
            self.preview_key = -1
            return
        names, columns = cs.getPreviewCardNames()

        # if cardset has changed, set default values
        if key != self.preview_key and USE_PIL:
            self.x_offset.config(value=cs.CARD_XOFFSET)
            self.x_offset.set(cs.CARD_XOFFSET)

            self.y_offset.config(value=cs.CARD_YOFFSET)
            self.y_offset.set(cs.CARD_YOFFSET)

        try:
            # ???names, columns = cs.getPreviewCardNames()
            for n in names:
                f = os.path.join(cs.dir, n + cs.ext)
                self.preview_images.append(loadImage(file=f))
        except Exception:
            self.preview_key = -1
            self.preview_images = []
            return
        i, x, y, sx, sy, dx, dy = 0, 10, 10, 0, 0, cs.CARDW + 10, cs.CARDH + 10
        if USE_PIL:
            xf = self.scale_x.get()
            yf = self.scale_y.get()
            dx = int(dx*xf)
            dy = int(dy*yf)
            self.scale_images = []
        for image in self.preview_images:
            if USE_PIL:
                image = image.resize(xf, yf)
                self.scale_images.append(image)
            MfxCanvasImage(canvas, x, y, anchor="nw", image=image)
            sx, sy = max(x, sx), max(y, sy)
            i = i + 1
            if i % columns == 0:
                x, y = 10, y + dy
            else:
                x = x + dx
        canvas.config(scrollregion=(0, 0, sx+dx, sy+dy),
                      width=sx+dx, height=sy+dy)
        # canvas.config(xscrollincrement=dx, yscrollincrement=dy)
        canvas.event_generate('<Configure>')  # update bg image
        self.preview_key = key
        self.key = key


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
        frame = ttk.Frame(top_frame)
        frame.pack(fill="both", expand=True, padx=5, pady=10)
        #
        #
        row = 0
        info_frame = ttk.LabelFrame(frame, text=_('About cardset'))
        info_frame.grid(row=row, column=0, columnspan=2, sticky='ew',
                        padx=0, pady=5, ipadx=5, ipady=5)
        row += 1
        styles = nationalities = year = None
        if cardset.si.styles:
            styles = '\n'.join([CSI.STYLE[i] for i in cardset.si.styles])
        if cardset.si.nationalities:
            nationalities = '\n'.join([CSI.NATIONALITY[i]
                                       for i in cardset.si.nationalities])
        if cardset.year:
            year = str(cardset.year)
        frow = 0
        for n, t in (
            # ('Version:', str(cardset.version)),
            (_('Type:'),          CSI.TYPE[cardset.type]),
            (_('Styles:'),        styles),
            (_('Nationality:'),   nationalities),
            (_('Year:'),          year),
            # (_('Number of cards:'), str(cardset.ncards)),
            (_('Size:'), '%d x %d' % (cardset.CARDW, cardset.CARDH)),
                ):
            if t is not None:
                label = ttk.Label(info_frame, text=n,
                                  anchor='w', justify='left')
                label.grid(row=frow, column=0, sticky='nw', padx=4)
                label = ttk.Label(info_frame, text=t,
                                  anchor='w', justify='left')
                label.grid(row=frow, column=1, sticky='nw', padx=4)
                frow += 1
        if images:
            try:
                from random import choice
                im = choice(images)
                f = os.path.join(cardset.dir, cardset.backname)
                self.back_image = loadImage(file=f)  # store the image
                label = ttk.Label(info_frame, image=im, padding=5)
                label.grid(row=0, column=2, rowspan=frow+1, sticky='ne')
                label = ttk.Label(info_frame, image=self.back_image,
                                  padding=(0, 5, 5, 5))  # left margin = 0
                label.grid(row=0, column=3, rowspan=frow+1, sticky='ne')

                info_frame.columnconfigure(2, weight=1)
                info_frame.rowconfigure(frow, weight=1)
            except Exception:
                pass

            row += 1

        # bg = top_frame["bg"]
        bg = 'white'
        text_w = tkinter.Text(frame, bd=1, relief="sunken", wrap="word",
                              padx=4, width=64, height=8, bg=bg)
        text_w.grid(row=row, column=0, sticky='nsew')
        sb = ttk.Scrollbar(frame)
        sb.grid(row=row, column=1, sticky='ns')
        text_w.configure(yscrollcommand=sb.set)
        sb.configure(command=text_w.yview)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        #
        text = ''
        fn = os.path.join(cardset.dir, "COPYRIGHT")
        try:
            with open(fn, "rt") as fh:
                text = fh.read()
        except Exception:
            pass
        if text:
            text_w.config(state="normal")
            text_w.insert("insert", text)
        text_w.config(state="disabled")
        #
        focus = self.createButtons(bottom_frame, kw)
        # focus = text_w
        self.mainloop(focus, kw.timeout)


class SearchCriteria:
    def __init__(self, manager):
        self.name = ""
        self.size = ""
        self.type = ""
        self.subtype = ""
        self.style = ""
        self.date = ""
        self.nationality = ""
        self.compatible = False

        self.sizeOptions = {"": -1,
                            "Tiny cardsets": CSI.SIZE_TINY,
                            "Small cardsets": CSI.SIZE_SMALL,
                            "Medium cardsets": CSI.SIZE_MEDIUM,
                            "Large cardsets": CSI.SIZE_LARGE,
                            "Extra Large cardsets": CSI.SIZE_XLARGE,
                            "Hi-Res cardsets": CSI.SIZE_HIRES}

        typeOptions = {-1: ""}
        for key, name in CSI.TYPE_NAME.items():
            if manager.registered_types.get(key):
                typeOptions[key] = name
        self.typeOptions = dict((v, k) for k, v in typeOptions.items())

        self.subtypeOptions = {"": -1}

        subtypeOptionsAll = {"": -1}
        for t in CSI.SUBTYPE_NAME.values():
            subtypeOptionsAll.update(t)
        self.subtypeOptionsAll = dict((v, k) for k, v in
                                      subtypeOptionsAll.items())

        styleOptions = {-1: ""}
        for key, name in CSI.STYLE.items():
            if manager.registered_styles.get(key):
                styleOptions[key] = name
        self.styleOptions = dict((v, k) for k, v in styleOptions.items())

        dateOptions = {-1: ""}
        for key, name in CSI.DATE.items():
            if manager.registered_dates.get(key):
                dateOptions[key] = name
        self.dateOptions = dict((v, k) for k, v in dateOptions.items())

        natOptions = {-1: ""}
        for key, name in CSI.NATIONALITY.items():
            if manager.registered_nationalities.get(key):
                natOptions[key] = name
        self.natOptions = dict((v, k) for k, v in natOptions.items())


class SelectCardsetAdvancedSearch(MfxDialog):
    def __init__(self, parent, title, criteria, manager, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)

        self.createBitmaps(top_frame, kw)
        #
        self.name = tkinter.StringVar()
        self.name.set(criteria.name)
        self.size = tkinter.StringVar()
        self.size.set(criteria.size)
        self.type = tkinter.StringVar()
        self.type.set(criteria.type)
        self.subtype = tkinter.StringVar()
        self.subtype.set(criteria.subtype)
        self.style = tkinter.StringVar()
        self.style.set(criteria.style)
        self.date = tkinter.StringVar()
        self.date.set(criteria.date)
        self.nationality = tkinter.StringVar()
        self.nationality.set(criteria.nationality)
        self.compatible = tkinter.BooleanVar()
        self.compatible.set(criteria.compatible)
        #
        row = 0

        labelName = tkinter.Label(top_frame, text="Name:", anchor="w")
        labelName.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textName = tkinter.Entry(top_frame, textvariable=self.name)
        textName.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        sizeValues = list(criteria.sizeOptions.keys())

        labelSize = tkinter.Label(top_frame, text="Size:", anchor="w")
        labelSize.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textSize = PysolCombo(top_frame, values=sizeValues,
                              textvariable=self.size, state='readonly')
        textSize.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        typeValues = list(criteria.typeOptions.keys())
        typeValues.sort()

        self.typeValues = criteria.typeOptions

        labelType = tkinter.Label(top_frame, text="Type:", anchor="w")
        labelType.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textType = PysolCombo(top_frame, values=typeValues,
                              textvariable=self.type, state='readonly',
                              selectcommand=self.updateSubtypes)
        textType.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        subtypeValues = list(criteria.subtypeOptions.keys())
        subtypeValues.sort()

        labelSubtype = tkinter.Label(top_frame, text="Subtype:",
                                     anchor="w")
        labelSubtype.grid(row=row, column=0, columnspan=1, sticky='ew',
                          padx=1, pady=1)
        textSubtype = PysolCombo(top_frame, values=subtypeValues,
                                 textvariable=self.subtype,
                                 state='readonly')
        textSubtype.grid(row=row, column=1, columnspan=4, sticky='ew',
                         padx=1, pady=1)
        self.subtypeSelect = textSubtype
        self.updateSubtypes()
        row += 1

        styleValues = list(criteria.styleOptions.keys())
        styleValues.sort()

        labelStyle = tkinter.Label(top_frame, text="Style:", anchor="w")
        labelStyle.grid(row=row, column=0, columnspan=1, sticky='ew',
                        padx=1, pady=1)
        textStyle = PysolCombo(top_frame, values=styleValues,
                               textvariable=self.style, state='readonly')
        textStyle.grid(row=row, column=1, columnspan=4, sticky='ew',
                       padx=1, pady=1)
        row += 1

        dateValues = list(criteria.dateOptions.keys())
        dateValues.sort()

        labelDate = tkinter.Label(top_frame, text="Date:", anchor="w")
        labelDate.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textDate = PysolCombo(top_frame, values=dateValues,
                              textvariable=self.date, state='readonly')
        textDate.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        natValues = list(criteria.natOptions.keys())
        natValues.sort()

        labelNationality = tkinter.Label(top_frame, text="Nationality:",
                                         anchor="w")
        labelNationality.grid(row=row, column=0, columnspan=1, sticky='ew',
                              padx=1, pady=1)
        textNationality = PysolCombo(top_frame, values=natValues,
                                     textvariable=self.nationality,
                                     state='readonly')
        textNationality.grid(row=row, column=1, columnspan=4, sticky='ew',
                             padx=1, pady=1)
        row += 1

        compatCheck = tkinter.Checkbutton(
            top_frame, variable=self.compatible,
            text=_("Compatible with current game"), anchor="w"
        )
        compatCheck.grid(row=row, column=0, columnspan=2, sticky='ew',
                         padx=1, pady=1)

        focus = self.createButtons(bottom_frame, kw)
        # focus = text_w
        self.mainloop(focus, kw.timeout)

    def updateSubtypes(self, *args):
        subtypeOptions = {-1: ""}
        key = self.typeValues[self.type.get()]
        if key in CSI.SUBTYPE_NAME:
            subtypeOptions.update(CSI.SUBTYPE_NAME[key])
            self.subtypeSelect['state'] = 'readonly'
            subtypeOptions = dict((v, k) for k, v in
                                  subtypeOptions.items())
            subtypeOptionsK = list(subtypeOptions.keys())
            subtypeOptionsK.sort()
            self.subtypeSelect['values'] = subtypeOptionsK
            if self.subtype.get() not in subtypeOptionsK:
                self.subtype.set("")
        else:
            self.subtypeSelect['state'] = 'disabled'
            self.subtype.set("")

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")), default=0,
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)
