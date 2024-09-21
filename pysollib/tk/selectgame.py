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
import tkinter
from collections import UserList

from pysollib.gamedb import GI
from pysollib.mfxutil import KwStruct, Struct, destruct
from pysollib.mfxutil import format_time
from pysollib.mygettext import _
from pysollib.resource import CSI
from pysollib.ui.tktile.selecttree import SelectDialogTreeData
from pysollib.ui.tktile.tkutil import unbind_destroy

from .selecttree import SelectDialogTreeCanvas
from .selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from .tkwidget import MfxDialog, MfxScrolledCanvas

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
                SelectGameNode(
                    None, _("Games with Separate Decks"),
                    lambda gi: gi.si.game_flags & GI.GT_SEPARATE_DECKS),
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
                      padx=10, pady=10,
                      buttonpadx=10, buttonpady=5,
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
        if button == 1:                # Rules
            doc = self.app.getGameRulesFilename(self.tree.selection_key)
            if not doc:
                return
            dir = os.path.join("html", "rules")
            from pysollib.help import help_html
            help_html(self.app, doc, dir, self.top)
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
        self.random = None
        if self.TreeDataHolder_Class.data is None:
            self.TreeDataHolder_Class.data = self.TreeData_Class(app)
        #
        self.top.wm_minsize(400, 200)
        sw = self.top.winfo_screenwidth()
        if sw >= 1100:
            w1, w2 = 250, 600
        elif sw >= 900:
            w1, w2 = 250, 500
        elif sw >= 800:
            w1, w2 = 220, 480
        else:
            w1, w2 = 200, 300
        # print sw, w1, w2
        w2 = max(200, min(w2, 10 + 12*(app.subsampled_images.CARDW+10)))
        # print sw, w1, w2
        # padx, pady = kw.padx, kw.pady
        padx, pady = kw.padx//2, kw.pady//2
        # PanedWindow
        paned_window = tkinter.PanedWindow(top_frame)
        paned_window.pack(expand=True, fill='both')
        left_frame = tkinter.Frame(paned_window)
        right_frame = tkinter.Frame(paned_window)
        paned_window.add(left_frame)
        paned_window.add(right_frame)
        # Tree
        font = app.getFont("default")
        self.tree = self.Tree_Class(self, left_frame, key=gameid,
                                    default=kw.default, font=font, width=w1)
        self.tree.frame.pack(padx=padx, pady=pady, expand=True, fill='both')
        # LabelFrame
        info_frame = tkinter.LabelFrame(right_frame, text=_('About game'))
        stats_frame = tkinter.LabelFrame(right_frame, text=_('Statistics'))
        info_frame.grid(row=0, column=0, padx=padx, pady=pady,
                        ipadx=padx, ipady=pady, sticky='nws')
        stats_frame.grid(row=0, column=1, padx=padx, pady=pady,
                         ipadx=padx, ipady=pady, sticky='nws')
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
            ('time',        _('Playing time:'),     stats_frame,  3),
            ('moves',       _('Moves:'),            stats_frame,  4),
            ('percent',     _('% won:'),            stats_frame,  5),
                ):
            title_label = tkinter.Label(f, text=t, justify='left', anchor='w')
            title_label.grid(row=row, column=0, sticky='nw')
            text_label = tkinter.Label(f, justify='left', anchor='w')
            text_label.grid(row=row, column=1, sticky='nw')
            self.info_labels[n] = (title_label, text_label)
        # info_frame.columnconfigure(1, weight=1)
        info_frame.rowconfigure(6, weight=1)
        stats_frame.rowconfigure(6, weight=1)
        # Canvas
        self.preview = MfxScrolledCanvas(right_frame, width=w2)
        self.preview.setTile(app, app.tabletile_index, force=True)
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
        self.mainloop(focus, kw.timeout)

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
            redeals = _('variable')
        elif gi.redeals == -1:
            redeals = _('unlimited')
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
