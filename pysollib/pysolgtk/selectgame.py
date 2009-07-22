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

#from UserList import UserList

# PySol imports
from pysollib.mfxutil import destruct, Struct, KwStruct
from pysollib.mfxutil import kwdefault
from pysollib.mfxutil import format_time
from pysollib.gamedb import GI
from pysollib.help import help_html
from pysollib.resource import CSI

# Toolkit imports
from tkutil import unbind_destroy
from tkwidget import MfxDialog
from tkcanvas  import MfxCanvas, MfxCanvasText
from pysoltree import PysolTreeView


# ************************************************************************
# * Dialog
# ************************************************************************

class SelectGameDialogWithPreview(MfxDialog):
    #Tree_Class = SelectGameTreeWithPreview
    game_store = None
    #
    _paned_position = 300
    _expanded_rows = []
    _geometry = None
    _selected_row = None
    _vadjustment_position = None

    def __init__(self, parent, title, app, gameid, bookmark=None, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, **kw)
        #
        self.app = app
        self.gameid = gameid
        self.bookmark = bookmark
        self.random = None
        #
        if self.game_store is None:
            self.createGameStore()
        #
        top_box, bottom_box = self.createHBox()
        # paned
        hpaned = gtk.HPaned()
        self.hpaned = hpaned
        hpaned.show()
        top_box.pack_start(hpaned, expand=True, fill=True)
        # left
        self.treeview = PysolTreeView(self, self.game_store)
        hpaned.pack1(self.treeview.scrolledwindow, True, True)
        # right
        table = gtk.Table(2, 2, False)
        table.show()
        hpaned.pack2(table, True, True)
        # frames
        frame = gtk.Frame(label=_('About game'))
        frame.show()
        table.attach(frame,
                     0, 1,      0, 1,
                     gtk.FILL,  gtk.FILL,
                     0,         0)
        frame.set_border_width(4)
        info_frame = gtk.Table(2, 7, False)
        info_frame.show()
        frame.add(info_frame)
        info_frame.set_border_width(4)
        #
        frame = gtk.Frame(label=_('Statistics'))
        frame.show()
        table.attach(frame,
                     1, 2,      0, 1,
                     gtk.FILL,  gtk.FILL,
                     0,         0)
        frame.set_border_width(4)
        stats_frame = gtk.Table(2, 6, False)
        stats_frame.show()
        frame.add(stats_frame)
        stats_frame.set_border_width(4)
        # info
        self.info_labels = {}
        i = 0
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
            title_label = gtk.Label()
            title_label.show()
            title_label.set_text(t)
            title_label.set_alignment(0., 0.)
            title_label.set_property('xpad', 2)
            title_label.set_property('ypad', 2)
            f.attach(title_label,
                     0, 1,      row, row+1,
                     gtk.FILL,  0,
                     0,         0)
            text_label = gtk.Label()
            text_label.show()
            text_label.set_alignment(0., 0.)
            text_label.set_property('xpad', 2)
            text_label.set_property('ypad', 2)
            f.attach(text_label,
                     1, 2,      row, row+1,
                     gtk.FILL,  0,
                     0,         0)
            self.info_labels[n] = (title_label, text_label)
        # canvas
        self.preview = MfxCanvas(self)
        self.preview.show()
        table.attach(self.preview,
            0, 2,                            1, 2,
            gtk.EXPAND|gtk.FILL|gtk.SHRINK,  gtk.EXPAND|gtk.FILL|gtk.SHRINK,
            0,                               0)
        self.preview.set_border_width(4)
        self.preview.setTile(app, app.tabletile_index, force=True)

        # set the scale factor
        self.preview.preview = 2
        # create a preview of the current game
        self.preview_key = -1
        self.preview_game = None
        self.preview_app = None
        ##~ self.updatePreview(gameid, animations=0)
        ##~ SelectGameTreeWithPreview.html_viewer = None

        self.connect('unrealize', self._unrealizeEvent)

        self.createButtons(bottom_box, kw)
        self._restoreSettings()
        self.show_all()
        gtk.main()


    def _addGamesFromData(self, data, store, root_iter, root_label, all_games):
        gl = []
        for label, selecter in data:
            games = self._selectGames(all_games, selecter)
            if games:
                gl.append((label, games))
        if not gl:
            return
        iter = store.append(root_iter)
        store.set(iter, 0, root_label, 1, -1)
        for label, games in gl:
            self._addGames(store, iter, label, games)


    def _addGames(self, store, root_iter, root_label, games):
        if not games:
            return
        iter = store.append(root_iter)
        store.set(iter, 0, root_label, 1, -1)
        for id, name in games:
            child_iter = store.append(iter)
            store.set(child_iter, 0, name, 1, id)


    def _selectGames(self, all_games, selecter):
        # return list of tuples (gameid, gamename)
        if selecter is None:
            return [(gi.id, gi.name) for gi in all_games]
        elif selecter == 'alt':
            return all_games
        return [(gi.id, gi.name) for gi in all_games if selecter(gi)]


    def createGameStore(self):
        store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        app = self.app
        gdb = app.gdb

        all_games = map(gdb.get, gdb.getGamesIdSortedByName())
        #
        alter_games = gdb.getGamesTuplesSortedByAlternateName()
        for label, games, selecter in (
            (_('All Games'),       all_games,   None),
            (_('Alternate Names'), alter_games, 'alt'),
            (_('Popular Games'),   all_games, lambda gi: gi.si.game_flags & GI.GT_POPULAR),
            ):
            games = self._selectGames(games, selecter)
            self._addGames(store, None, label, games)

        # by type
        games = self._selectGames(all_games,
                                  lambda gi: gi.si.game_type == GI.GT_MAHJONGG)
        self._addGames(store, None, _("Mahjongg Games"), games)
        self._addGamesFromData(GI.SELECT_ORIENTAL_GAME_BY_TYPE, store,
                               None, _("Oriental Games"), all_games)
        self._addGamesFromData(GI.SELECT_SPECIAL_GAME_BY_TYPE, store,
                               None, _("Special Games"), all_games)
        self._addGamesFromData(GI.SELECT_GAME_BY_TYPE, store,
                               None, _("French games"), all_games)
        # by skill level
        data = (
          (_('Luck only'),    lambda gi: gi.skill_level == GI.SL_LUCK),
          (_('Mostly luck'),  lambda gi: gi.skill_level == GI.SL_MOSTLY_LUCK),
          (_('Balanced'),     lambda gi: gi.skill_level == GI.SL_BALANCED),
          (_('Mostly skill'), lambda gi: gi.skill_level == GI.SL_MOSTLY_SKILL),
          (_('Skill only'),   lambda gi: gi.skill_level == GI.SL_SKILL),
          )
        self._addGamesFromData(data, store, None,
                               _("by Skill Level"), all_games)

        # by game feature
        root_iter = store.append(None)
        store.set(root_iter, 0, _('by Game Feature'), 1, -1)
        data = (
            (_("32 cards"),     lambda gi: gi.si.ncards == 32),
            (_("48 cards"),     lambda gi: gi.si.ncards == 48),
            (_("52 cards"),     lambda gi: gi.si.ncards == 52),
            (_("64 cards"),     lambda gi: gi.si.ncards == 64),
            (_("78 cards"),     lambda gi: gi.si.ncards == 78),
            (_("104 cards"),    lambda gi: gi.si.ncards == 104),
            (_("144 cards"),    lambda gi: gi.si.ncards == 144),
            (_("Other number"), lambda gi: gi.si.ncards not in (32, 48, 52, 64, 78, 104, 144)),)
        self._addGamesFromData(data, store, root_iter,
                             _("by Number of Cards"), all_games)
        data = (
            (_("1 deck games"), lambda gi: gi.si.decks == 1),
            (_("2 deck games"), lambda gi: gi.si.decks == 2),
            (_("3 deck games"), lambda gi: gi.si.decks == 3),
            (_("4 deck games"), lambda gi: gi.si.decks == 4),)
        self._addGamesFromData(data, store, root_iter,
                             _("by Number of Decks"), all_games)
        data = (
            (_("No redeal"), lambda gi: gi.si.redeals == 0),
            (_("1 redeal"),  lambda gi: gi.si.redeals == 1),
            (_("2 redeals"), lambda gi: gi.si.redeals == 2),
            (_("3 redeals"), lambda gi: gi.si.redeals == 3),
            (_("Unlimited redeals"), lambda gi: gi.si.redeals == -1),
            ##(_("Variable redeals"), lambda gi: gi.si.redeals == -2),
            (_("Other number of redeals"), lambda gi: gi.si.redeals not in (-1, 0, 1, 2, 3)),)
        self._addGamesFromData(data, store, root_iter,
                               _("by Number of Redeals"), all_games)

        data = []
        for label, vg in GI.GAMES_BY_COMPATIBILITY:
            selecter = lambda gi, vg=vg: gi.id in vg
            data.append((label, selecter))
        self._addGamesFromData(data, store, root_iter,
                               _("by Compatibility"), all_games)

        # by PySol version
        data = []
        for version, vg in GI.GAMES_BY_PYSOL_VERSION:
            selecter = lambda gi, vg=vg: gi.id in vg
            label = _("New games in v. ") + version
            data.append((label, selecter))
        self._addGamesFromData(data, store, None,
                               _("by PySol version"), all_games)

        #
        data = (
            (_("Games for Children (very easy)"), lambda gi: gi.si.game_flags & GI.GT_CHILDREN),
            (_("Games with Scoring"),  lambda gi: gi.si.game_flags & GI.GT_SCORE),
            (_("Games with Separate Decks"),  lambda gi: gi.si.game_flags & GI.GT_SEPARATE_DECKS),
            (_("Open Games (all cards visible)"), lambda gi: gi.si.game_flags & GI.GT_OPEN),
            (_("Relaxed Variants"),  lambda gi: gi.si.game_flags & GI.GT_RELAXED),)
        self._addGamesFromData(data, store, None,
                               _("Other Categories"), all_games)

        #
        self._addGamesFromData(GI.SELECT_ORIGINAL_GAME_BY_TYPE, store,
                               None, _("Original Games"), all_games)
        ##self._addGamesFromData(GI.SELECT_CONTRIB_GAME_BY_TYPE, store,
        ##              None, _("Contrib Game"), all_games)

        SelectGameDialogWithPreview.game_store = store
        return


    def initKw(self, kw):
        kwdefault(kw,
                  strings=(_("&Select"), _("&Rules"), _("&Cancel"),),
                  default=0,
                  width=600, height=400,
                  )
        return MfxDialog.initKw(self, kw)


    def _unrealizeEvent(self, w):
        self.deletePreview(destroy=1)
        #self.preview.unbind_all()
        self._saveSettings()


    def _saveSettings(self):
        SelectGameDialogWithPreview._geometry = self.get_size()
        SelectGameDialogWithPreview._paned_position = self.hpaned.get_position()


    def _restoreSettings(self):
        if self._geometry:
            self.resize(self._geometry[0], self._geometry[1])
        self.hpaned.set_position(self._paned_position)


    def getSelected(self):
        index = self.treeview.getSelected()
        if index < 0:
            return None
        return index

    def showSelected(self, w):
        id = self.getSelected()
        if id:
            self.updatePreview(id)


    def deletePreview(self, destroy=0):
        self.preview_key = -1
        # clean up the canvas
        if self.preview:
            unbind_destroy(self.preview)
            self.preview.deleteAllItems()
            ##~ if destroy:
            ##~     self.preview.delete("all")
        #
        #for l in self.info_labels.values():
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
        canvas = self.preview
        #
        gi = self.app.gdb.get(gameid)
        if not gi:
            self.preview_key = -1
            return
        #
        if self.preview_app is None:
            self.preview_app = Struct(
                # variables
                audio = self.app.audio,
                canvas = canvas,
                cardset = self.app.cardset.copy(),
                comments = self.app.comments.new(),
                gamerandom = self.app.gamerandom,
                gdb = self.app.gdb,
                gimages = self.app.gimages,
                images = self.app.subsampled_images,
                menubar = None,
                miscrandom = self.app.miscrandom,
                opt = self.app.opt.copy(),
                startup_opt = self.app.startup_opt,
                stats = self.app.stats.new(),
                top = None,
                top_cursor = self.app.top_cursor,
                toolbar = None,
                # methods
                constructGame = self.app.constructGame,
                getFont = self.app.getFont,
            )
            self.preview_app.opt.shadow = 0
            self.preview_app.opt.shade = 0
        #
        self.preview_app.audio = None    # turn off audio for intial dealing
        if animations >= 0:
            self.preview_app.opt.animations = animations
        #
        if self.preview_game:
            self.preview_game.endGame()
            self.preview_game.destruct()
        ##self.top.wm_title("Select Game - " + self.app.getGameTitleName(gameid))
        title = self.app.getGameTitleName(gameid)
        self.set_title(_("Playable Preview - ") + title)
        #
        self.preview_game = gi.gameclass(gi)
        self.preview_game.createPreview(self.preview_app)
        tx, ty = 0, 0
        gw, gh = self.preview_game.width, self.preview_game.height
        ##~ canvas.config(scrollregion=(-tx, -ty, -tx, -ty))
        ##~ canvas.xview_moveto(0)
        ##~ canvas.yview_moveto(0)
        #
        random = None
        if gameid == self.gameid:
            random = self.app.game.random.copy()
        if gameid == self.gameid and self.bookmark:
            self.preview_game.restoreGameFromBookmark(self.bookmark)
        else:
            self.preview_game.newGame(random=random, autoplay=1)
        ##~ canvas.config(scrollregion=(-tx, -ty, gw, gh))
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
        rules_button = self.buttons[1]
        if self.app.getGameRulesFilename(gameid):
            rules_button.set_sensitive(True)
        else:
            rules_button.set_sensitive(False)

    def updateInfo(self, gameid):
        gi = self.app.gdb.get(gameid)
        # info
        name = gi.name
        altnames = '\n'.join(gi.altnames)
        category = _(CSI.TYPE[gi.category])
        type = ''
        if gi.si.game_type in GI.TYPE_NAMES:
            type = _(GI.TYPE_NAMES[gi.si.game_type])
        sl = {
            GI.SL_LUCK:         _('Luck only'),
            GI.SL_MOSTLY_LUCK:  _('Mostly luck'),
            GI.SL_BALANCED:     _('Balanced'),
            GI.SL_MOSTLY_SKILL: _('Mostly skill'),
            GI.SL_SKILL:        _('Skill only'),
            }
        skill_level = sl.get(gi.skill_level)
        if    gi.redeals == -2: redeals = _('variable')
        elif  gi.redeals == -1: redeals = _('unlimited')
        else:                   redeals = str(gi.redeals)
        # stats
        won, lost, time, moves = self.app.stats.getFullStats(self.app.opt.player, gameid)
        if won+lost > 0: percent = "%.1f" % (100.0*won/(won+lost))
        else: percent = "0.0"
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
                title_label.hide()
                text_label.hide()
            else:
                title_label.show()
                text_label.show()
            text_label.set_text(str(t))

    def done(self, button):
        button = button.get_data("user_data")
        print 'done', button
        if button == 0:                    # Ok or double click
            id = self.getSelected()
            if id:
                self.gameid = id
            ##~ self.tree.n_expansions = 1  # save xyview in any case
        if button == 1:                    # Rules
            id = self.getSelected()
            if id:
                doc = self.app.getGameRulesFilename(id)
                if not doc:
                    return
            dir = os.path.join("html", "rules")
            help_html(self.app, doc, dir, self)
            return

        self.status = 0
        self.button = button
        self.quit()


