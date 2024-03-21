#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------

import os

from pysollib.gamedb import GI
from pysollib.mfxutil import KwStruct, Struct, destruct
from pysollib.mfxutil import format_time
from pysollib.mygettext import _
from pysollib.resource import CSI
from pysollib.ui.tktile.selecttree import SelectDialogTreeData
from pysollib.ui.tktile.tkutil import bind, unbind_destroy

from six.moves import UserList
from six.moves import tkinter
from six.moves import tkinter_ttk as ttk

from .selecttree import SelectDialogTreeCanvas
from .selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from .tkwidget import MfxDialog, MfxScrolledCanvas, PysolCombo

# ************************************************************************
# * Nodes
# ************************************************************************


class SelectGameLeaf(SelectDialogTreeLeaf):
    pass


class SelectGameNode(SelectDialogTreeNode):
    def _getContents(self):
        contents = []
        if isinstance(self.select_func, UserList):
            # key/value pairs
            for id, name in self.select_func:
                if id and name:
                    node = SelectGameLeaf(self.tree, self, name, key=id)
                    contents.append(node)
        else:
            for gi in self.tree.data.all_games_gi:
                if gi and self.select_func is None:
                    # All games
                    # name = '%s (%s)' % (gi.name, CSI.TYPE_NAME[gi.category])
                    name = gi.name
                    node = SelectGameLeaf(self.tree, self, name, key=gi.id)
                    contents.append(node)
                elif gi and self.select_func(gi):
                    name = gi.name
                    node = SelectGameLeaf(self.tree, self, name, key=gi.id)
                    contents.append(node)
        return contents or self.tree.data.no_games


# ************************************************************************
# * Tree database
# ************************************************************************

class SelectGameData(SelectDialogTreeData):
    def __init__(self, app):
        SelectDialogTreeData.__init__(self)
        self.all_games_gi = list(map(
            app.gdb.get,
            app.gdb.getGamesIdSortedByName()))
        self.no_games = [SelectGameLeaf(None, None, _("(no games)"), None), ]
        #
        s_by_type = s_oriental = s_special = s_original = s_contrib = \
            s_mahjongg = None
        g = []
        for data in (GI.SELECT_GAME_BY_TYPE,
                     GI.SELECT_ORIENTAL_GAME_BY_TYPE,
                     GI.SELECT_SPECIAL_GAME_BY_TYPE,
                     GI.SELECT_ORIGINAL_GAME_BY_TYPE,
                     GI.SELECT_CONTRIB_GAME_BY_TYPE,
                     ):
            gg = []
            for name, select_func in data:
                if name is None or not list(filter(
                        select_func, self.all_games_gi)):
                    continue
                gg.append(SelectGameNode(None, _(name), select_func))
            g.append(gg)

        def select_mahjongg_game(gi):
            return gi.si.game_type == GI.GT_MAHJONGG

        gg = None
        if list(filter(select_mahjongg_game, self.all_games_gi)):
            gg = SelectGameNode(None, _("Mahjongg Games"),
                                select_mahjongg_game)
        g.append(gg)
        if g[0]:
            s_by_type = SelectGameNode(None, _("French Games"),
                                       tuple(g[0]), expanded=1)
        if g[1]:
            s_oriental = SelectGameNode(None, _("Oriental Games"),
                                        tuple(g[1]))
        if g[2]:
            s_special = SelectGameNode(None, _("Special Games"),
                                       tuple(g[2]))
        if g[3]:
            s_original = SelectGameNode(None, _("Original Games"),
                                        tuple(g[3]))
        # if g[4]:
        #   s_contrib = SelectGameNode(None, "Contributed Games", tuple(g[4]))
        if g[5]:
            s_mahjongg = g[5]
        #
        s_by_compatibility, gg = None, []
        for name, games in GI.GAMES_BY_COMPATIBILITY:
            def select_func(gi, games=games):
                return gi.id in games
            if name is None or not list(filter(
                    select_func, self.all_games_gi)):
                continue
            gg.append(SelectGameNode(None, name, select_func))
        if 1 and gg:
            s_by_compatibility = SelectGameNode(None, _("by Compatibility"),
                                                tuple(gg))
        #
        s_by_pysol_version, gg = None, []
        for name, games in GI.GAMES_BY_PYSOL_VERSION:
            def select_func(gi, games=games):
                return gi.id in games
            if name is None or not list(filter(
                    select_func, self.all_games_gi)):
                continue
            name = _("New games in v. %(version)s") % {'version': name}
            gg.append(SelectGameNode(None, name, select_func))
        if 1 and gg:
            s_by_pysol_version = SelectGameNode(None, _("by PySol version"),
                                                tuple(gg))
        s_by_inventors, gg = None, []
        for name, games in GI.GAMES_BY_INVENTORS:
            def select_func(gi, games=games):
                return gi.id in games
            if name is None or not list(filter(
                    select_func, self.all_games_gi)):
                continue
            gg.append(SelectGameNode(None, name, select_func))
        if 1 and gg:
            s_by_inventors = SelectGameNode(None, _("by Inventors"),
                                            tuple(gg))
        #
        ul_alternate_names = UserList(
            list(app.gdb.getGamesTuplesSortedByAlternateName()))
        #
        self.rootnodes = [_f for _f in (
            SelectGameNode(None, _("All Games"), None, expanded=0),
            SelectGameNode(None, _("Alternate Names"), ul_alternate_names),
            SelectGameNode(None, _("Popular Games"),
                           lambda gi: gi.si.game_flags & GI.GT_POPULAR),
            s_by_type,
            s_mahjongg,
            s_oriental,
            s_special,
            SelectGameNode(None, _("Custom Games"),
                           lambda gi: gi.si.game_type == GI.GT_CUSTOM),
            SelectGameNode(None, _('by Skill Level'), (
                SelectGameNode(None, _('Luck only'),
                               lambda gi: gi.skill_level == GI.SL_LUCK),
                SelectGameNode(None, _('Mostly luck'),
                               lambda gi: gi.skill_level == GI.SL_MOSTLY_LUCK),
                SelectGameNode(None, _('Balanced'),
                               lambda gi: gi.skill_level == GI.SL_BALANCED),
                SelectGameNode(
                    None, _('Mostly skill'),
                    lambda gi: gi.skill_level == GI.SL_MOSTLY_SKILL),
                SelectGameNode(None, _('Skill only'),
                               lambda gi: gi.skill_level == GI.SL_SKILL),
                )),
            SelectGameNode(None, _("by Game Feature"), (
                SelectGameNode(None, _("by Number of Cards"), (
                    SelectGameNode(None, _("32 cards"),
                                   lambda gi: gi.si.ncards == 32),
                    SelectGameNode(None, _("48 cards"),
                                   lambda gi: gi.si.ncards == 48),
                    SelectGameNode(None, _("52 cards"),
                                   lambda gi: gi.si.ncards == 52),
                    SelectGameNode(None, _("64 cards"),
                                   lambda gi: gi.si.ncards == 64),
                    SelectGameNode(None, _("78 cards"),
                                   lambda gi: gi.si.ncards == 78),
                    SelectGameNode(None, _("104 cards"),
                                   lambda gi: gi.si.ncards == 104),
                    SelectGameNode(None, _("144 cards"),
                                   lambda gi: gi.si.ncards == 144),
                    SelectGameNode(
                        None, _("Other number"),
                        lambda gi: gi.si.ncards not in (32, 48, 52,
                                                        64, 78, 104, 144)),
                )),
                SelectGameNode(None, _("by Number of Decks"), (
                    SelectGameNode(None, _("1 deck games"),
                                   lambda gi: gi.si.decks == 1),
                    SelectGameNode(None, _("2 deck games"),
                                   lambda gi: gi.si.decks == 2),
                    SelectGameNode(None, _("3 deck games"),
                                   lambda gi: gi.si.decks == 3),
                    SelectGameNode(None, _("4 deck games"),
                                   lambda gi: gi.si.decks == 4),
                )),
                SelectGameNode(None, _("by Number of Redeals"), (
                    SelectGameNode(None, _("No redeal"),
                                   lambda gi: gi.si.redeals == 0),
                    SelectGameNode(None, _("1 redeal"),
                                   lambda gi: gi.si.redeals == 1),
                    SelectGameNode(None, _("2 redeals"),
                                   lambda gi: gi.si.redeals == 2),
                    SelectGameNode(None, _("3 redeals"),
                                   lambda gi: gi.si.redeals == 3),
                    SelectGameNode(None, _("Unlimited redeals"),
                                   lambda gi: gi.si.redeals == -1),
                    SelectGameNode(None, _("Variable redeals"),
                                   lambda gi: gi.si.redeals == -2),
                    SelectGameNode(
                        None, _("Other number of redeals"),
                        lambda gi: gi.si.redeals not in (-2, -1, 0, 1, 2, 3)),
                )),
                s_by_compatibility,
            )),
            s_by_pysol_version,
            s_by_inventors,
            SelectGameNode(None, _("Other Categories"), (
                SelectGameNode(None, _("Games for Children (very easy)"),
                               lambda gi: gi.si.game_flags & GI.GT_CHILDREN),
                SelectGameNode(None, _("Games with Scoring"),
                               lambda gi: gi.si.game_flags & GI.GT_SCORE),
                SelectGameNode(None, _("Games with Stripped Decks"),
                               lambda gi: gi.si.game_flags & GI.GT_STRIPPED),
                SelectGameNode(None, _("Games with Separate Decks"),
                               lambda gi: gi.si.game_flags &
                               GI.GT_SEPARATE_DECKS),
                SelectGameNode(None, _("Games with Jokers"),
                               lambda gi: gi.category == GI.GC_FRENCH and
                               gi.subcategory == GI.GS_JOKER_DECK),
                SelectGameNode(None, _("Open Games (all cards visible)"),
                               lambda gi: gi.si.game_flags & GI.GT_OPEN),
                SelectGameNode(None, _("Relaxed Variants"),
                               lambda gi: gi.si.game_flags & GI.GT_RELAXED),
            )),
            s_original,
            s_contrib,
        ) if _f]


# ************************************************************************
# * Canvas that shows the tree
# ************************************************************************

class SelectGameTreeWithPreview(SelectDialogTreeCanvas):
    data = None


class SelectGameTree(SelectGameTreeWithPreview):
    def singleClick(self, event=None):
        self.doubleClick(event)


# ************************************************************************
# * Dialog
# ************************************************************************

class SelectGameDialog(MfxDialog):
    Tree_Class = SelectGameTree
    TreeDataHolder_Class = SelectGameTreeWithPreview
    TreeData_Class = SelectGameData

    def __init__(self, parent, title, app, gameid, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)

        self.createBitmaps(top_frame, kw)
        #
        self.app = app
        self.gameid = gameid
        self.random = None
        if self.TreeDataHolder_Class.data is None:
            self.TreeDataHolder_Class.data = self.TreeData_Class(app)
        #
        self.top.wm_minsize(200, 200)
        font = app.getFont("default")
        self.tree = self.Tree_Class(self, top_frame, key=gameid,
                                    font=font, default=kw.default)
        self.tree.frame.pack(fill='both', expand=True,
                             padx=kw.padx, pady=kw.pady)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.tree.frame
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(None, None, _("&Cancel"),), default=0,
                      resizable=True,
                      separator=True,
                      )
        return MfxDialog.initKw(self, kw)

    def destroy(self):
        self.app = None
        self.tree.updateNodesWithTree(self.tree.rootnodes, None)
        self.tree.destroy()
        MfxDialog.destroy(self)

    def mDone(self, button):
        if button == 0:                 # Ok or double click
            self.gameid = self.tree.selection_key
            self.tree.n_expansions = 1  # save xyview in any case
        if button == 10:                # Rules
            doc = self.app.getGameRulesFilename(self.tree.selection_key)
            if not doc:
                return
            dir = os.path.join("html", "rules")
            from pysollib.help import help_html
            help_html(self.app, doc, dir, self.top)
            self.top.grab_release()  # Don't want the help window appear frozen
            return
        MfxDialog.mDone(self, button)


# ************************************************************************
# * Dialog
# ************************************************************************

class SelectGameDialogWithPreview(SelectGameDialog):
    Tree_Class = SelectGameTreeWithPreview

    def __init__(self, parent, title, app, gameid, bookmark=None, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)

        self.createBitmaps(top_frame, kw)
        #
        self.app = app
        self.gameid = gameid
        self.bookmark = bookmark
        self.criteria = SearchCriteria()
        self.random = None
        if self.TreeDataHolder_Class.data is None:
            self.TreeDataHolder_Class.data = self.TreeData_Class(app)
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

        # print sw, w1, w2
        # w2 = max(200, min(w2, 10 + 12 * (app.subsampled_images.CARDW + 10)))
        # print sw, w1, w2
        # padx, pady = kw.padx, kw.pady
        # padx, pady = kw.padx/2, kw.pady/2
        padx, pady = 4, 4
        # PanedWindow
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

        # Tree
        font = app.getFont("default")
        self.tree = self.Tree_Class(self, tree_frame, key=gameid,
                                    default=kw.default, font=font,
                                    width=w1)
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

        # LabelFrame
        info_frame = ttk.LabelFrame(right_frame, text=_('About game'))
        info_frame.grid(row=0, column=0, padx=padx, pady=pady,
                        ipadx=4, ipady=4, sticky='nws')
        stats_frame = ttk.LabelFrame(right_frame, text=_('Statistics'))
        stats_frame.grid(row=0, column=1, padx=padx, pady=pady,
                         ipadx=4, ipady=4, sticky='nws')
        # Info
        self.info_labels = {}
        for n, t, f, row in (
            ('name',        _('Name:'),             info_frame,   0),
            ('altnames',    _('Alternate names:'),  info_frame,   1),
            ('category',    _('Category:'),         info_frame,   2),
            ('type',        _('Type:'),             info_frame,   3),
            ('skill_level', _('Skill level:'),      info_frame,   4),
            ('decks',       _('Decks:'),            info_frame,   5),
            ('redeals',     _('Redeals:'),          info_frame,   6),
            #
            ('played',      _('Played:'),           stats_frame,  0),
            ('won',         _('Won:'),              stats_frame,  1),
            ('lost',        _('Lost:'),             stats_frame,  2),
            ('time',        _('Avg. win time:'),     stats_frame,  3),
            ('moves',       _('Avg. win moves:'),    stats_frame,  4),
            ('percent',     _('% won:'),            stats_frame,  5),
                ):
            title_label = ttk.Label(f, text=t, justify='left', anchor='w')
            title_label.grid(row=row, column=0, sticky='nw', padx=4)
            text_label = ttk.Label(f, justify='left', anchor='w')
            text_label.grid(row=row, column=1, sticky='nw', padx=4)
            self.info_labels[n] = (title_label, text_label)
        # info_frame.columnconfigure(1, weight=1)
        info_frame.rowconfigure(6, weight=1)
        stats_frame.rowconfigure(6, weight=1)
        # Canvas
        self.preview = MfxScrolledCanvas(right_frame)
        self.preview.setTile(app, app.tabletile_index,
                             app.opt.tabletile_scale_method, force=True)
        self.preview.grid(row=1, column=0, columnspan=3,
                          padx=padx, pady=pady, sticky='nsew')
        right_frame.columnconfigure(1, weight=1)
        right_frame.rowconfigure(1, weight=1)
        #
        focus = self.createButtons(bottom_frame, kw)
        # set the scale factor
        self.preview.canvas.preview = 2
        # create a preview of the current game
        self.preview_key = -1
        self.preview_game = None
        self.preview_app = None
        self.updatePreview(gameid, animations=0)
        # focus = self.tree.frame
        self.mainloop(focus, kw.timeout, geometry=geometry)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=((_("&Rules"), 10), 'sep',
                               _("&Select"), _("&Cancel"),),
                      default=0,
                      )
        return SelectGameDialog.initKw(self, kw)

    def destroy(self):
        self.deletePreview(destroy=1)
        self.preview.unbind_all()
        SelectGameDialog.destroy(self)

    def deletePreview(self, destroy=0):
        self.preview_key = -1
        # clean up the canvas
        if self.preview:
            unbind_destroy(self.preview.canvas)
            self.preview.canvas.deleteAllItems()
            if destroy:
                self.preview.canvas.delete("all")
        #
        # for l in self.info_labels.values():
        #    l.config(text='')
        # destruct the game
        if self.preview_game:
            self.preview_game.endGame()
            self.preview_game.destruct()
            destruct(self.preview_game)
        self.preview_game = None
        # destruct the app
        if destroy:
            if self.preview_app:
                destruct(self.preview_app)
            self.preview_app = None

    def basicSearch(self, *args):
        self.updateSearchList(self.list_searchtext.get())

    def updateSearchList(self, searchString):
        self.criteria.name = searchString
        self.performSearch()

    def performSearch(self):
        self.list.delete(0, "end")
        self.list.vbar_show = True
        games = self.app.gdb.getAllGames()

        results = []
        for game in games:
            if (self.criteria.category != "" and
                    self.criteria.categoryOptions[self.criteria.category]
                    != game.category):
                continue
            if (self.criteria.subcategory != "" and
                    self.criteria.
                    subcategoryOptionsAll[self.criteria.subcategory]
                    != game.subcategory):
                continue
            if (self.criteria.type != ""
                    and self.criteria.typeOptions[self.criteria.type]
                    != game.si.game_type):
                continue
            if (self.criteria.skill != ""
                    and self.criteria.skillOptions[self.criteria.skill]
                    != game.skill_level):
                continue
            if (self.criteria.decks != ""
                    and self.criteria.deckOptions[self.criteria.decks]
                    != game.decks):
                continue
            if (self.criteria.redeals != "" and
                    self.criteria.redeals != "Other number of redeals"
                    and self.criteria.redealOptions[self.criteria.redeals]
                    != game.redeals):
                continue
            if self.criteria.redeals == "Other number of redeals"\
                    and game.redeals < 4:
                continue

            compat_okay = True
            for name, games in GI.GAMES_BY_COMPATIBILITY:
                if self.criteria.compat == name:
                    if game.id not in games:
                        compat_okay = False
                        break

            if not compat_okay:
                continue

            invent_okay = True
            for name, games in GI.GAMES_BY_INVENTORS:
                if self.criteria.inventor == name:
                    if game.id not in games:
                        invent_okay = False
                        break

            if not invent_okay:
                continue

            if self.criteria.version != "":
                version_okay = False
                version_found = False
                for name, games in GI.GAMES_BY_PYSOL_VERSION:
                    if self.criteria.version == name:
                        version_found = True
                        if game.id in games:
                            version_okay = True
                            break
                    elif ((not version_found and
                           self.criteria.versioncompare == "Present in")
                          or (version_found and
                              self.criteria.versioncompare == "New since")):
                        if game.id in games:
                            version_okay = True
                            break

                if not version_okay:
                    continue

            if self.criteria.statistics != '':
                won, lost = (self.app.stats.getStats
                             (self.app.opt.player, game.id))
                statoption = \
                    self.criteria.statisticsOptions[self.criteria.statistics]
                if statoption == 'played' and won + lost == 0:
                    continue
                elif statoption == 'won' and won == 0:
                    continue
                elif statoption == 'not won' and (won != 0 or lost == 0):
                    continue
                elif statoption == 'not played' and won + lost != 0:
                    continue

            if (self.criteria.popular and
                    not (game.si.game_flags & GI.GT_POPULAR)):
                continue
            if (self.criteria.recent and
                    not (game.id in self.app.opt.recent_gameid)):
                continue
            if (self.criteria.favorite and
                    not (game.id in self.app.opt.favorite_gameid)):
                continue
            if (self.criteria.children and
                    not (game.si.game_flags & GI.GT_CHILDREN)):
                continue
            if (self.criteria.scoring and
                    not (game.si.game_flags & GI.GT_SCORE)):
                continue
            if (self.criteria.stripped and
                    not (game.si.game_flags & GI.GT_STRIPPED)):
                continue
            if (self.criteria.separate and
                    not (game.si.game_flags & GI.GT_SEPARATE_DECKS)):
                continue
            if (self.criteria.open and not (game.si.game_flags & GI.GT_OPEN)):
                continue
            if (self.criteria.relaxed and
                    not (game.si.game_flags & GI.GT_RELAXED)):
                continue
            if (self.criteria.original and
                    not (game.si.game_flags & GI.GT_ORIGINAL)):
                continue

            if self.app.checkSearchString(self.criteria.name, game.name):
                results.append(game.name)
            if self.criteria.usealt:
                for altname in game.altnames:
                    if self.app.checkSearchString(self.criteria.name, altname):
                        results.append(altname)
        results.sort(key=lambda x: x.lower())
        pos = 0
        for result in results:
            self.list.insert(pos, result)
            pos += 1

    def advancedSearch(self):
        d = SelectGameAdvancedSearch(self.top, _("Advanced search"),
                                     self.criteria)
        if d.status == 0 and d.button == 0:
            self.criteria.name = d.name.get()

            self.list_searchtext.delete(0, "end")
            self.list_searchtext.insert(0, d.name.get())

            self.criteria.usealt = d.usealt.get()
            self.criteria.category = d.category.get()
            self.criteria.subcategory = d.subcategory.get()
            self.criteria.type = d.type.get()
            self.criteria.skill = d.skill.get()
            self.criteria.decks = d.decks.get()
            self.criteria.redeals = d.redeals.get()
            self.criteria.compat = d.compat.get()
            self.criteria.inventor = d.inventor.get()
            self.criteria.versioncompare = d.versioncompare.get()
            self.criteria.version = d.version.get()
            self.criteria.statistics = d.statistics.get()

            self.criteria.popular = d.popular.get()
            self.criteria.recent = d.recent.get()
            self.criteria.favorite = d.favorite.get()
            self.criteria.children = d.children.get()
            self.criteria.scoring = d.scoring.get()
            self.criteria.stripped = d.stripped.get()
            self.criteria.separate = d.separate.get()
            self.criteria.open = d.open.get()
            self.criteria.relaxed = d.relaxed.get()
            self.criteria.original = d.original.get()
            self.performSearch()

    def selectSearchResult(self, event):
        if self.list.size() <= 0:
            return
        oldcur = self.list["cursor"]
        self.list["cursor"] = "watch"
        sel = self.list.get(self.list.curselection())
        game = self.app.gdb.getGameByName(sel)
        self.list.update_idletasks()
        self.tree.n_selections += 1
        self.tree.updateSelection(game)
        self.updatePreview(game)
        self.list["cursor"] = oldcur

    def updatePreview(self, gameid, animations=10):
        if gameid == self.preview_key:
            return
        self.deletePreview()
        canvas = self.preview.canvas
        #
        gi = self.app.gdb.get(gameid)
        if not gi:
            self.preview_key = -1
            return
        #
        if self.preview_app is None:
            self.preview_app = Struct(
                # variables
                audio=self.app.audio,
                canvas=canvas,
                cardset=self.app.cardset.copy(),
                gamerandom=self.app.gamerandom,
                gdb=self.app.gdb,
                gimages=self.app.gimages,
                images=None,
                menubar=None,
                miscrandom=self.app.miscrandom,
                opt=self.app.opt.copy(),
                startup_opt=self.app.startup_opt,
                stats=self.app.stats.new(),
                top=None,
                top_cursor=self.app.top_cursor,
                toolbar=None,
                # methods
                constructGame=self.app.constructGame,
                getFont=self.app.getFont,
            )
            self.preview_app.opt.shadow = 0
            self.preview_app.opt.shade = 0
        #

        c = self.app.cardsets_cache.get(gi.category)
        c2 = None
        if c:
            c2 = c.get(gi.subcategory)
        if not c2:
            cardset = self.app.cardset_manager.getByName(
                self.app.opt.cardset[gi.category][gi.subcategory][0])
            self.app.loadCardset(cardset, id=gi.category,
                                 tocache=True, noprogress=True)
            c = self.app.cardsets_cache.get(gi.category)
            if c:
                c2 = c.get(gi.subcategory)
            if not c2:
                c = self.app.cardsets_cache.get(cardset.type)
                if c:
                    c2 = c.get(cardset.subtype)
        if c2:
            self.preview_app.images = c2[2]
        else:
            self.preview_app.images = self.app.subsampled_images

        self.preview_app.audio = None    # turn off audio for initial dealing
        if animations >= 0:
            self.preview_app.opt.animations = animations
        #
        if self.preview_game:
            self.preview_game.endGame()
            self.preview_game.destruct()
        # self.top.wm_title("Select Game - " +
        #   self.app.getGameTitleName(gameid))
        title = self.app.getGameTitleName(gameid)
        self.top.wm_title(_("Select Game - %(game)s") % {'game': title})
        #
        self.preview_game = gi.gameclass(gi)
        self.preview_game.createPreview(self.preview_app)
        #
        random = None
        if gameid == self.gameid:
            random = self.app.game.random.copy()
        if gameid == self.gameid and self.bookmark:
            self.preview_game.restoreGameFromBookmark(self.bookmark)
        else:
            self.preview_game.newGame(random=random, autoplay=1)
        gw, gh = self.preview_game.width, self.preview_game.height
        canvas.config(scrollregion=(0, 0, gw, gh))
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        #
        self.preview_app.audio = self.app.audio
        if self.app.opt.animations:
            self.preview_app.opt.animations = 10
        else:
            self.preview_app.opt.animations = 0
        # save seed
        self.random = self.preview_game.random.copy()
        self.random.origin = self.random.ORIGIN_PREVIEW
        self.preview_key = gameid
        #
        self.updateInfo(gameid)
        #
        rules_button = self.buttons[0]
        if self.app.getGameRulesFilename(gameid):
            rules_button.config(state="normal")
        else:
            rules_button.config(state="disabled")

    def updateInfo(self, gameid):
        gi = self.app.gdb.get(gameid)
        # info
        name = gi.name
        altnames = '\n'.join(gi.altnames)
        category = _(CSI.TYPE[gi.category])
        type = ''
        if gi.si.game_type in GI.TYPE_NAMES:
            type = _(GI.TYPE_NAMES[gi.si.game_type])
        skill_level = GI.SKILL_LEVELS.get(gi.skill_level)
        if gi.redeals == -2:
            redeals = _('Variable')
        elif gi.redeals == -1:
            redeals = _('Unlimited')
        else:
            redeals = str(gi.redeals)
        # stats
        won, lost, time, moves = self.app.stats.getFullStats(
            self.app.opt.player, gameid)
        if won+lost > 0:
            percent = "%.1f" % (100.0*won/(won+lost))
        else:
            percent = "0.0"
        time = format_time(time)
        moves = str(round(moves, 1))
        for n, t in (
            ('name',        name),
            ('altnames',    altnames),
            ('category',    category),
            ('type',        type),
            ('skill_level', skill_level),
            ('decks',       gi.decks),
            ('redeals',     redeals),
            ('played',      won+lost),
            ('won',         won),
            ('lost',        lost),
            ('time',        time),
            ('moves',       moves),
            ('percent',     percent),
                ):
            title_label, text_label = self.info_labels[n]
            if t in ('', None):
                title_label.grid_remove()
                text_label.grid_remove()
            else:
                title_label.grid()
                text_label.grid()
            text_label.config(text=t)


class SearchCriteria:
    def __init__(self):
        self.name = ""
        self.usealt = True
        self.category = ""
        self.subcategory = ""
        self.type = ""
        self.skill = ""
        self.decks = ""
        self.redeals = ""
        self.compat = ""
        self.inventor = ""
        self.versioncompare = "New in"
        self.version = ""
        self.statistics = ""

        self.popular = False
        self.recent = False
        self.favorite = False
        self.children = False
        self.scoring = False
        self.stripped = False
        self.separate = False
        self.open = False
        self.relaxed = False
        self.original = False

        categoryOptions = {-1: ""}
        categoryOptions.update(CSI.TYPE_NAME)
        del categoryOptions[7]  # Navagraha Ganjifa is unused.
        self.categoryOptions = dict((v, k) for k, v in categoryOptions.items())

        self.subcategoryOptions = {"": -1}

        subcategoryOptionsAll = {"": -1}
        for t in CSI.SUBTYPE_NAME.values():
            subcategoryOptionsAll.update(t)
        self.subcategoryOptionsAll = dict((v, k) for k, v in
                                          subcategoryOptionsAll.items())

        typeOptions = {-1: ""}
        typeOptions.update(GI.TYPE_NAMES)
        del typeOptions[29]  # Simple games type is unused.
        self.typeOptions = dict((v, k) for k, v in typeOptions.items())

        self.deckOptions = {"": 0,
                            "1 deck games": 1,
                            "2 deck games": 2,
                            "3 deck games": 3,
                            "4 deck games": 4}

        skillOptions = {-1: ""}
        skillOptions.update(GI.SKILL_LEVELS)
        self.skillOptions = dict((v, k) for k, v in skillOptions.items())

        self.deckOptions = {"": 0,
                            "1 deck games": 1,
                            "2 deck games": 2,
                            "3 deck games": 3,
                            "4 deck games": 4}

        self.redealOptions = {"": -3,
                              "No redeal": 0,
                              "1 redeal": 1,
                              "2 redeals": 2,
                              "3 redeals": 3,
                              "Unlimited redeals": -1,
                              "Variable redeals": -2,
                              "Other number of redeals": 4}

        self.versionCompareOptions = ("New in", "Present in", "New since")

        self.statisticsOptions = {"": "all",
                                  "Games played": "played",
                                  "Games played and won": "won",
                                  "Games played and not won": "not won",
                                  "Games not played": "not played"}


class SelectGameAdvancedSearch(MfxDialog):
    def __init__(self, parent, title, criteria, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)

        self.createBitmaps(top_frame, kw)
        #
        self.name = tkinter.StringVar()
        self.name.set(criteria.name)
        self.usealt = tkinter.BooleanVar()
        self.usealt.set(criteria.usealt)
        self.category = tkinter.StringVar()
        self.category.set(criteria.category)
        self.subcategory = tkinter.StringVar()
        self.subcategory.set(criteria.subcategory)
        self.type = tkinter.StringVar()
        self.type.set(criteria.type)
        self.skill = tkinter.StringVar()
        self.skill.set(criteria.skill)
        self.decks = tkinter.StringVar()
        self.decks.set(criteria.decks)
        self.redeals = tkinter.StringVar()
        self.redeals.set(criteria.redeals)
        self.compat = tkinter.StringVar()
        self.compat.set(criteria.compat)
        self.inventor = tkinter.StringVar()
        self.inventor.set(criteria.inventor)
        self.versioncompare = tkinter.StringVar()
        self.versioncompare.set(criteria.versioncompare)
        self.version = tkinter.StringVar()
        self.version.set(criteria.version)
        self.statistics = tkinter.StringVar()
        self.statistics.set(criteria.statistics)

        self.popular = tkinter.BooleanVar()
        self.popular.set(criteria.popular)
        self.recent = tkinter.BooleanVar()
        self.recent.set(criteria.recent)
        self.favorite = tkinter.BooleanVar()
        self.favorite.set(criteria.favorite)
        self.children = tkinter.BooleanVar()
        self.children.set(criteria.children)
        self.scoring = tkinter.BooleanVar()
        self.scoring.set(criteria.scoring)
        self.stripped = tkinter.BooleanVar()
        self.stripped.set(criteria.stripped)
        self.separate = tkinter.BooleanVar()
        self.separate.set(criteria.separate)
        self.open = tkinter.BooleanVar()
        self.open.set(criteria.open)
        self.relaxed = tkinter.BooleanVar()
        self.relaxed.set(criteria.relaxed)
        self.original = tkinter.BooleanVar()
        self.original.set(criteria.original)

        #
        row = 0

        labelName = tkinter.Label(top_frame, text="Name:", anchor="w")
        labelName.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textName = tkinter.Entry(top_frame, textvariable=self.name)
        textName.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        altCheck = tkinter.Checkbutton(top_frame, variable=self.usealt,
                                       text=_("Check alternate names"),
                                       anchor="w")
        altCheck.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        categoryValues = list(criteria.categoryOptions.keys())
        categoryValues.sort()

        self.categoryValues = criteria.categoryOptions

        labelCategory = tkinter.Label(top_frame, text="Category:", anchor="w")
        labelCategory.grid(row=row, column=0, columnspan=1, sticky='ew',
                           padx=1, pady=1)
        textCategory = PysolCombo(top_frame, values=categoryValues,
                                  textvariable=self.category, state='readonly',
                                  selectcommand=self.updateSubcategories)
        textCategory.grid(row=row, column=1, columnspan=4, sticky='ew',
                          padx=1, pady=1)
        row += 1

        subcategoryValues = list(criteria.subcategoryOptions.keys())
        subcategoryValues.sort()

        labelSubcategory = tkinter.Label(top_frame, text="Subcategory:",
                                         anchor="w")
        labelSubcategory.grid(row=row, column=0, columnspan=1, sticky='ew',
                              padx=1, pady=1)
        textSubcategory = PysolCombo(top_frame, values=subcategoryValues,
                                     textvariable=self.subcategory,
                                     state='readonly')
        textSubcategory.grid(row=row, column=1, columnspan=4, sticky='ew',
                             padx=1, pady=1)
        self.subcategorySelect = textSubcategory
        self.updateSubcategories()
        row += 1

        typeValues = list(criteria.typeOptions.keys())
        typeValues.sort()

        labelType = tkinter.Label(top_frame, text="Type:", anchor="w")
        labelType.grid(row=row, column=0, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        textType = PysolCombo(top_frame, values=typeValues,
                              textvariable=self.type, state='readonly')
        textType.grid(row=row, column=1, columnspan=4, sticky='ew',
                      padx=1, pady=1)
        row += 1

        skillValues = list(criteria.skillOptions.keys())

        labelSkill = tkinter.Label(top_frame, text="Skill level:", anchor="w")
        labelSkill.grid(row=row, column=0, columnspan=1, sticky='ew',
                        padx=1, pady=1)
        textSkill = PysolCombo(top_frame, values=skillValues,
                               textvariable=self.skill, state='readonly')
        textSkill.grid(row=row, column=1, columnspan=4, sticky='ew',
                       padx=1, pady=1)
        row += 1

        deckValues = list(criteria.deckOptions.keys())

        labelDecks = tkinter.Label(top_frame, text="Decks:", anchor="w")
        labelDecks.grid(row=row, column=0, columnspan=1, sticky='ew',
                        padx=1, pady=1)
        textDecks = PysolCombo(top_frame, values=deckValues,
                               textvariable=self.decks, state='readonly')
        textDecks.grid(row=row, column=1, columnspan=4, sticky='ew',
                       padx=1, pady=1)
        row += 1

        redealValues = list(criteria.redealOptions.keys())

        labelRedeals = tkinter.Label(top_frame, text="Redeals:", anchor="w")
        labelRedeals.grid(row=row, column=0, columnspan=1, sticky='ew',
                          padx=1, pady=1)
        textRedeals = PysolCombo(top_frame, values=redealValues,
                                 textvariable=self.redeals, state='readonly')
        textRedeals.grid(row=row, column=1, columnspan=4, sticky='ew',
                         padx=1, pady=1)
        row += 1

        compatValues = list()
        compatValues.append("")
        for name, games in GI.GAMES_BY_COMPATIBILITY:
            compatValues.append(name)

        labelCompat = tkinter.Label(top_frame, text="Compatibility:",
                                    anchor="w")
        labelCompat.grid(row=row, column=0, columnspan=1, sticky='ew',
                         padx=1, pady=1)
        textCompat = PysolCombo(top_frame, values=compatValues,
                                textvariable=self.compat, state='readonly')
        textCompat.grid(row=row, column=1, columnspan=4, sticky='ew',
                        padx=1, pady=1)
        row += 1

        inventorValues = list()
        inventorValues.append("")
        for name, games in GI.GAMES_BY_INVENTORS:
            inventorValues.append(name)

        labelInventor = tkinter.Label(top_frame, text="Inventor:", anchor="w")
        labelInventor.grid(row=row, column=0, columnspan=1, sticky='ew',
                           padx=1, pady=1)
        textInventor = PysolCombo(top_frame, values=inventorValues,
                                  textvariable=self.inventor, state='readonly')
        textInventor.grid(row=row, column=1, columnspan=4, sticky='ew',
                          padx=1, pady=1)
        row += 1

        versionCompareValues = list(criteria.versionCompareOptions)
        versionValues = list()
        versionValues.append("")
        for name, games in GI.GAMES_BY_PYSOL_VERSION:
            versionValues.append(name)

        labelVersion = tkinter.Label(top_frame, text="PySol Version:",
                                     anchor="w")
        labelVersion.grid(row=row, column=0, columnspan=1, sticky='ew',
                          padx=1, pady=1)
        textVersionCompare = PysolCombo(top_frame, values=versionCompareValues,
                                        textvariable=self.versioncompare,
                                        state='readonly')
        textVersionCompare.grid(row=row, column=1, columnspan=2, sticky='ew',
                                padx=1, pady=1)
        textVersion = PysolCombo(top_frame, values=versionValues,
                                 textvariable=self.version, state='readonly')
        textVersion.grid(row=row, column=3, columnspan=2, sticky='ew',
                         padx=1, pady=1)
        row += 1

        statisticsValues = list(criteria.statisticsOptions.keys())

        labelStats = tkinter.Label(top_frame, text="Statistics:", anchor="w")
        labelStats.grid(row=row, column=0, columnspan=1, sticky='ew',
                        padx=1, pady=1)
        textStats = PysolCombo(top_frame, values=statisticsValues,
                               textvariable=self.statistics, state='readonly')
        textStats.grid(row=row, column=1, columnspan=4, sticky='ew',
                       padx=1, pady=1)
        row += 1

        col = 0
        popularCheck = tkinter.Checkbutton(top_frame, variable=self.popular,
                                           text=_("Popular"), anchor="w")
        popularCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                          padx=1, pady=1)
        col += 2

        recentCheck = tkinter.Checkbutton(top_frame, variable=self.recent,
                                          text=_("Recent"), anchor="w")
        recentCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                         padx=1, pady=1)
        col += 2

        favoriteCheck = tkinter.Checkbutton(top_frame, variable=self.favorite,
                                            text=_("Favorite"), anchor="w")
        favoriteCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                           padx=1, pady=1)

        row += 1
        col = 0

        childCheck = tkinter.Checkbutton(top_frame, variable=self.children,
                                         text=_("Children's"), anchor="w")
        childCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                        padx=1, pady=1)
        col += 2

        scoreCheck = tkinter.Checkbutton(top_frame, variable=self.scoring,
                                         text=_("Scored"), anchor="w")
        scoreCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                        padx=1, pady=1)
        col += 2

        stripCheck = tkinter.Checkbutton(top_frame, variable=self.stripped,
                                         text=_("Stripped Deck"), anchor="w")
        stripCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                        padx=1, pady=1)
        row += 1
        col = 0

        sepCheck = tkinter.Checkbutton(top_frame, variable=self.separate,
                                       text=_("Separate Decks"), anchor="w")
        sepCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                      padx=1, pady=1)
        col += 2

        openCheck = tkinter.Checkbutton(top_frame, variable=self.open,
                                        text=_("Open"), anchor="w")
        openCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                       padx=1, pady=1)
        col += 2

        relaxedCheck = tkinter.Checkbutton(top_frame, variable=self.relaxed,
                                           text=_("Relaxed"), anchor="w")
        relaxedCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                          padx=1, pady=1)
        row += 1
        col = 0

        originalCheck = tkinter.Checkbutton(top_frame, variable=self.original,
                                            text=_("Original"), anchor="w")
        originalCheck.grid(row=row, column=col, columnspan=1, sticky='ew',
                           padx=1, pady=1)

        focus = self.createButtons(bottom_frame, kw)
        # focus = text_w
        self.mainloop(focus, kw.timeout)

    def updateSubcategories(self, *args):
        subcategoryOptions = {-1: ""}
        key = self.categoryValues[self.category.get()]
        if key in CSI.SUBTYPE_NAME:
            subcategoryOptions.update(CSI.SUBTYPE_NAME[key])
            self.subcategorySelect['state'] = 'readonly'
            subcategoryOptions = dict((v, k) for k, v in
                                      subcategoryOptions.items())
            subcategoryOptionsK = list(subcategoryOptions.keys())
            subcategoryOptionsK.sort()
            self.subcategorySelect['values'] = subcategoryOptionsK
            if self.subcategory.get() not in subcategoryOptionsK:
                self.subcategory.set("")
        else:
            self.subcategorySelect['state'] = 'disabled'
            self.subcategory.set("")

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")), default=0,
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)
