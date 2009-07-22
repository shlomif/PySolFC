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
import os, locale

# PySol imports
from mfxutil import SubclassResponsibility
from mfxutil import Struct, openURL
from mfxutil import print_err
from pysolrandom import constructRandom
from settings import TITLE, PACKAGE_URL
from settings import TOP_TITLE
from settings import DEBUG
from gamedb import GI

# stats imports
from stats import FileStatsFormatter
from pysoltk import SingleGame_StatsDialog, AllGames_StatsDialog
from pysoltk import FullLog_StatsDialog, SessionLog_StatsDialog
from pysoltk import Status_StatsDialog, Top_StatsDialog
from pysoltk import ProgressionDialog
from pysoltk import GameInfoDialog

# toolkit imports
from pysoltk import MfxMessageDialog, MfxSimpleEntry
from pysoltk import MfxExceptionDialog
from pysoltk import PlayerOptionsDialog
from pysoltk import TimeoutsDialog
from pysoltk import ColorsDialog
from pysoltk import FontsDialog
from pysoltk import EditTextDialog
from pysoltk import create_find_card_dialog
from pysoltk import create_solver_dialog
from pysoltk import PysolMenubarTk, PysolToolbarTk
from help import help_about, help_html


# ************************************************************************
# * menubar
# ************************************************************************

class PysolMenubar(PysolMenubarTk):
    def __init__(self, app, top, progress=None):
        self.app = app
        self.top = top
        self.game = None
        # enabled/disabled - this is set by updateMenuState()
        self.menustate = Struct(
            save = 0,
            save_as = 0,
            hold_and_quit = 0,
            undo = 0,
            redo = 0,
            restart = 0,
            deal = 0,
            hint = 0,
            autofaceup = 0,
            autodrop = 0,
            shuffle = 0,
            autodeal = 0,
            quickplay = 0,
            demo = 0,
            highlight_piles = 0,
            find_card = 0,
            rules = 0,
            pause = 0,
            custom_game = 0,
        )
        PysolMenubarTk.__init__(self, app, top, progress)

    #
    # delegation to Game
    #

    def _finishDrag(self):
        return self.game is None or self.game._finishDrag()

    def _cancelDrag(self, break_pause=True):
        if self.game is None:
            return True
        ret = self.game._cancelDrag(break_pause=break_pause)
        self._setPauseMenu(self.game.pause)
        return ret

    def changed(self, *args, **kw):
        assert self.game is not None
        return self.game.changed(*args, **kw)


    #
    # menu updates
    #

    def _clearMenuState(self):
        ms = self.menustate
        for k, v in ms.__dict__.items():
            if isinstance(v, list):
                ms.__dict__[k] = [0] * len(v)
            else:
                ms.__dict__[k] = 0

    # update self.menustate for menu items and toolbar
    def _updateMenuState(self):
        self._clearMenuState()
        game = self.game
        assert game is not None
        opt = self.app.opt
        ms = self.menustate
        # 0 = DISABLED, 1 = ENABLED
        ms.save_as = game.canSaveGame()
        ms.hold_and_quit = ms.save_as
        if game.filename and ms.save_as:
            ms.save = 1
        if opt.undo:
            if game.canUndo() and game.moves.index > 0:
                ms.undo = 1
            if game.canRedo() and game.moves.index < len(game.moves.history):
                ms.redo = 1
        if game.moves.index > 0:
            ms.restart = 1
        if game.canDealCards():
            ms.deal = 1
        if game.getHintClass() is not None:
            if opt.hint:
                ms.hint = 1
            ###if not game.demo:       # if not already running
            ms.demo = 1
        autostacks = game.getAutoStacks()
        if autostacks[0]:
            ms.autofaceup = 1
        if autostacks[1] and game.s.foundations:
            ms.autodrop = 1
        if game.s.waste:
            ms.autodeal = 1
        if autostacks[2]:
            ms.quickplay = 1
        if opt.highlight_piles and game.getHighlightPilesStacks():
            ms.highlight_piles = 1
        if game.canFindCard():
            ms.find_card = 1
        if game.app.getGameRulesFilename(game.id):  # note: this may return ""
            ms.rules = 1
        if not game.finished:
            ms.pause = 1
        if game.gameinfo.si.game_type == GI.GT_CUSTOM:
            ms.custom_game = 1
        if game.canShuffle():
            if opt.shuffle:
                ms.shuffle = 1

    # update menu items and toolbar
    def _updateMenus(self):
        if self.game is None:
            return
        ms = self.menustate
        # File menu
        self.setMenuState(ms.save, "file.save")
        self.setMenuState(ms.save_as, "file.saveas")
        self.setMenuState(ms.hold_and_quit, "file.holdandquit")
        # Edit menu
        self.setMenuState(ms.undo, "edit.undo")
        self.setMenuState(ms.redo, "edit.redo")
        self.setMenuState(ms.redo, "edit.redoall")
        self.updateBookmarkMenuState()
        self.setMenuState(ms.restart, "edit.restart")
        self.setMenuState(ms.custom_game, "edit.editcurrentgame")
        # Game menu
        self.setMenuState(ms.deal, "game.dealcards")
        self.setMenuState(ms.autodrop, "game.autodrop")
        self.setMenuState(ms.shuffle, "game.shuffletiles")
        self.setMenuState(ms.pause, "game.pause")
        # Assist menu
        self.setMenuState(ms.hint, "assist.hint")
        self.setMenuState(ms.highlight_piles, "assist.highlightpiles")
        self.setMenuState(ms.find_card, "assist.findcard")
        self.setMenuState(ms.demo, "assist.demo")
        self.setMenuState(ms.demo, "assist.demoallgames")
        # Options menu
        self.setMenuState(ms.autofaceup, "options.automaticplay.autofaceup")
        self.setMenuState(ms.autodrop, "options.automaticplay.autodrop")
        self.setMenuState(ms.autodeal, "options.automaticplay.autodeal")
        self.setMenuState(ms.quickplay, "options.automaticplay.quickplay")
        # Help menu
        self.setMenuState(ms.rules, "help.rulesforthisgame")
        # Toolbar
        self.setToolbarState(ms.restart, "restart")
        self.setToolbarState(ms.save_as, "save")
        self.setToolbarState(ms.undo, "undo")
        self.setToolbarState(ms.redo, "redo")
        self.setToolbarState(ms.autodrop, "autodrop")
        self.setToolbarState(ms.shuffle, "shuffle")
        self.setToolbarState(ms.pause, "pause")
        self.setToolbarState(ms.rules, "rules")

    # update menu items and toolbar
    def updateMenus(self):
        if self.game is None:
            return
        self._updateMenuState()
        self._updateMenus()

    # disable menu items and toolbar
    def disableMenus(self):
        if self.game is None:
            return
        self._clearMenuState()
        self._updateMenus()


    #
    # File menu
    #

    def mNewGame(self, *args):
        if self._cancelDrag(): return
        if self.changed():
            if not self.game.areYouSure(_("New game")): return
        if self.game.nextGameFlags(self.game.id) == 0:
            self.game.endGame()
            self.game.newGame()
        else:
            self.game.endGame()
            self.game.quitGame(self.game.id)

    def _mSelectGame(self, id, random=None, force=False):
        if self._cancelDrag(): return
        if not force and self.game.id == id:
            return
        if self.changed():
            if not self.game.areYouSure(_("Select game")):
                return
        self.game.endGame()
        self.game.quitGame(id, random=random)

    def _mNewGameBySeed(self, seed, origin):
        try:
            random = constructRandom(seed)
            if random is None:
                return
            id = self.game.id
            if not self.app.getGameInfo(id):
                raise ValueError
        except (ValueError, TypeError), ex:
            d = MfxMessageDialog(self.top, title=_("Invalid game number"),
                                 text=_("Invalid game number\n") + str(seed),
                                 bitmap="error")
            return
        f = self.game.nextGameFlags(id, random)
        if f & 17 == 0:
            return
        random.origin = origin
        if f & 15 == 0:
            self.game.endGame()
            self.game.newGame(random=random)
        else:
            self.game.endGame()
            self.game.quitGame(id, random=random)

    def mNewGameWithNextId(self, *args):
        if self._cancelDrag(): return
        if self.changed():
            if not self.game.areYouSure(_("Select next game number")): return
        r = self.game.random
        seed = r.increaseSeed(r.initial_seed)
        seed = r.str(seed)
        self._mNewGameBySeed(seed, self.game.random.ORIGIN_NEXT_GAME)

    def mSelectGameById(self, *args):
        if self._cancelDrag(break_pause=False): return
        id, f = None, self.game.getGameNumber(format=0)
        d = MfxSimpleEntry(self.top, _("Select new game number"),
                           _("\n\nEnter new game number"), f,
                           strings=(_("&OK"), _("&Next number"), _("&Cancel")),
                           default=0, e_width=25)
        if d.status != 0: return
        if d.button == 2: return
        if d.button == 1:
            self.mNewGameWithNextId()
            return
        if self.changed():
            if not self.game.areYouSure(_("Select new game number")): return
        self._mNewGameBySeed(d.value, self.game.random.ORIGIN_SELECTED)



    def mSelectRandomGame(self, type='all'):
        if self._cancelDrag(): return
        if self.changed():
            if not self.game.areYouSure(_("Select random game")): return
        game_id = None
        games = []
        for g in self.app.gdb.getGamesIdSortedById():
            gi = self.app.getGameInfo(g)
            if 1 and gi.id == self.game.id:
                # force change of game
                continue
            if 1 and gi.category != self.game.gameinfo.category:
                # don't change game category
                continue
            won, lost = self.app.stats.getStats(self.app.opt.player, gi.id)
            if type == 'all':
                games.append(gi.id)
            elif type == 'won' and won > 0:
                games.append(gi.id)
            elif type == 'not won' and won == 0 and lost > 0:
                games.append(gi.id)
            elif type == 'not played' and won+lost == 0:
                games.append(gi.id)
        if games:
            game_id = self.app.getRandomGameId(games)
        if game_id and game_id != self.game.id:
            self.game.endGame()
            self.game.quitGame(game_id)

    def _mSelectNextGameFromList(self, gl, step):
        if self._cancelDrag(): return
        id = self.game.id
        gl = list(gl)
        if len(gl) < 2 or not id in gl:
            return
        if self.changed():
            if not self.game.areYouSure(_("Select next game")): return
        index = (gl.index(id) + step) % len(gl)
        self.game.endGame()
        self.game.quitGame(gl[index])

    def mSelectNextGameById(self, *args):
        self._mSelectNextGameFromList(self.app.gdb.getGamesIdSortedById(), 1)

    def mSelectPrevGameById(self, *args):
        self._mSelectNextGameFromList(self.app.gdb.getGamesIdSortedById(), -1)

    def mSelectNextGameByName(self, *args):
        self._mSelectNextGameFromList(self.app.gdb.getGamesIdSortedByName(), 1)

    def mSelectPrevGameByName(self, *args):
        self._mSelectNextGameFromList(self.app.gdb.getGamesIdSortedByName(), -1)

    def mSave(self, *args):
        if self._cancelDrag(break_pause=False): return
        if self.menustate.save_as:
            if self.game.filename:
                self.game.saveGame(self.game.filename)
            else:
                self.mSaveAs()

    def mHoldAndQuit(self, *args):
        if self._cancelDrag(): return
        self.game.endGame(holdgame=1)
        self.game.quitGame(holdgame=1)

    def mQuit(self, *args):
        if self._cancelDrag(): return
        if self.changed():
            if not self.game.areYouSure(_("Quit ") + TITLE): return
        self.game.endGame()
        self.game.quitGame()


    #
    # Edit menu
    #

    def mUndo(self, *args):
        if self._cancelDrag(): return
        if self.menustate.undo:
            self.game.playSample("undo")
            self.game.undo()

    def mRedo(self, *args):
        if self._cancelDrag(): return
        if self.menustate.redo:
            self.game.playSample("redo")
            self.game.redo()
            self.game.checkForWin()

    def mRedoAll(self, *args):
        if self._cancelDrag(): return
        if self.menustate.redo:
            self.app.top.busyUpdate()
            self.game.playSample("redo", loop=1)
            while self.game.moves.index < len(self.game.moves.history):
                self.game.redo()
                if self.game.checkForWin():
                    break
            self.game.stopSamples()

    def mSetBookmark(self, n, confirm=1):
        if self._cancelDrag(): return
        if not self.app.opt.bookmarks: return
        if not (0 <= n <= 8): return
        self.game.setBookmark(n, confirm=confirm)
        self.game.updateMenus()

    def mGotoBookmark(self, n, confirm=-1):
        if self._cancelDrag(): return
        if not self.app.opt.bookmarks: return
        if not (0 <= n <= 8): return
        self.game.gotoBookmark(n, confirm=confirm)
        self.game.updateMenus()

    def mClearBookmarks(self, *args):
        if self._cancelDrag(): return
        if not self.app.opt.bookmarks: return
        if not self.game.gsaveinfo.bookmarks: return
        if not self.game.areYouSure(_("Clear bookmarks"),
                                    _("Clear all bookmarks ?")):
            return
        self.game.gsaveinfo.bookmarks = {}
        self.game.updateMenus()

    def mRestart(self, *args):
        if self._cancelDrag(): return
        if self.game.moves.index == 0:
            return
        if self.changed(restart=1):
            if not self.game.areYouSure(_("Restart game"),
                                        _("Restart this game ?")):
                return
        self.game.restartGame()


    #
    # Game menu
    #

    def mDeal(self, *args):
        if self._cancelDrag(): return
        self.game.dealCards()

    def mDrop(self, *args):
        if self._cancelDrag(): return
        ##self.game.autoPlay(autofaceup=-1, autodrop=1)
        self.game.autoDrop(autofaceup=-1)

    def mDrop1(self, *args):
        if self._cancelDrag(): return
        ##self.game.autoPlay(autofaceup=1, autodrop=1)
        self.game.autoDrop(autofaceup=1)

    def mShuffle(self, *args):
        if self._cancelDrag(): return
        if self.menustate.shuffle:
            if self.game.canShuffle():
                self.game._mahjonggShuffle()

    def mFindCard(self, *args):
        create_find_card_dialog(self.game.top, self.game,
                                self.app.getFindCardImagesDir())

    def mSolver(self, *args):
        create_solver_dialog(self.game.top, self.app)

    def mEditGameComment(self, *args):
        if self._cancelDrag(break_pause=False): return
        game, gi = self.game, self.game.gameinfo
        t = " " + game.getGameNumber(format=1)
        cc = _("Comments for %s:\n\n") % (gi.name + t)
        c = game.gsaveinfo.comment or cc
        d = EditTextDialog(game.top, _("Comments for ")+t, text=c)
        if d.status == 0 and d.button == 0:
            text = d.text
            if text.strip() == cc.strip():
                game.gsaveinfo.comment = ""
            else:
                game.gsaveinfo.comment = d.text
                # save to file
                fn = os.path.join(self.app.dn.config, "comments.txt")
                fn = os.path.normpath(fn)
                if not text.endswith(os.linesep):
                    text += os.linesep
                enc = locale.getpreferredencoding()
                try:
                    fd = open(fn, 'a')
                    fd.write(text.encode(enc, 'replace'))
                except Exception, err:
                    d = MfxExceptionDialog(self.top, err,
                                           text=_("Error while writing to file"))
                else:
                    if fd: fd.close()
                    d = MfxMessageDialog(self.top, title=TITLE+_(" Info"), bitmap="info",
                                         text=_("Comments were appended to\n\n") + fn)
        self._setCommentMenu(bool(game.gsaveinfo.comment))


    #
    # Game menu - statistics
    #

    def _mStatsSave(self, player, filename, write_method):
        file = None
        if player is None:
            text = _("Demo statistics")
            filename = filename + "_demo"
        else:
            text = _("Your statistics")
        filename = os.path.join(self.app.dn.config, filename + ".txt")
        filename = os.path.normpath(filename)
        try:
            file = open(filename, "a")
            a = FileStatsFormatter(self.app, file)
            write_method(a, player)
        except EnvironmentError, ex:
            if file: file.close()
            d = MfxExceptionDialog(self.top, ex,
                                   text=_("Error while writing to file"))
        else:
            if file: file.close()
            d = MfxMessageDialog(self.top, title=TITLE+_(" Info"), bitmap="info",
                                 text=text + _(" were appended to\n\n") + filename)


    def mPlayerStats(self, *args, **kw):
        mode = kw.get("mode", 101)
        demo = 0
        gameid = None
        while mode > 0:
            if mode > 1000:
                demo = not demo
                mode = mode % 1000
            #
            d = Struct(status=-1, button=-1)
            if demo:
                player = None
                p0, p1, p2 = TITLE+_(" Demo"), TITLE+_(" Demo "), ""
            else:
                player = self.app.opt.player
                p0, p1, p2 = player, "", _(" for ") + player
            n = self.game.gameinfo.name
            #
            if mode == 100:
                d = Status_StatsDialog(self.top, game=self.game)
            elif mode == 101:
                header = p1 + _("Statistics for ") + n
                d = SingleGame_StatsDialog(self.top, header, self.app, player, gameid=self.game.id)
                gameid = d.selected_game
            elif mode == 102:
                header = p1 + _("Statistics") + p2
                d = AllGames_StatsDialog(self.top, header, self.app, player)
                gameid = d.selected_game
            elif mode == 103:
                header = p1 + _("Full log") + p2
                d = FullLog_StatsDialog(self.top, header, self.app, player)
            elif mode == 104:
                header = p1 + _("Session log") + p2
                d = SessionLog_StatsDialog(self.top, header, self.app, player)
            elif mode == 105:
                header = p1 + TOP_TITLE + _(" for ") + n
                d = Top_StatsDialog(self.top, header, self.app, player, gameid=self.game.id)
            elif mode == 106:
                header = _("Game Info")
                d = GameInfoDialog(self.top, header, self.app)
            elif mode == 107:
                header = _("Statistics progression")
                d = ProgressionDialog(self.top, header, self.app, player, gameid=self.game.id)
            elif mode == 202:
                # print stats to file
                write_method = FileStatsFormatter.writeStats
                self._mStatsSave(player, "stats", write_method)
            elif mode == 203:
                # print full log to file
                write_method = FileStatsFormatter.writeFullLog
                self._mStatsSave(player, "log", write_method)
            elif mode == 204:
                # print session log to file
                write_method = FileStatsFormatter.writeSessionLog
                self._mStatsSave(player, "log", write_method)
            elif mode == 301:
                # reset all player stats
                if self.game.areYouSure(_("Reset all statistics"),
                                        _("Reset ALL statistics and logs for player\n%s ?") % p0,
                                        confirm=1, default=1):
                    self.app.stats.resetStats(player, 0)
                    self.game.updateStatus(stats=self.app.stats.getStats(self.app.opt.player, self.game.id))
            elif mode == 302:
                # reset player stats for current game
                if self.game.areYouSure(_("Reset game statistics"),
                                        _('Reset statistics and logs for player\n%s\nand game\n%s ?') % (p0, n),
                                        confirm=1, default=1):
                    self.app.stats.resetStats(player, self.game.id)
                    self.game.updateStatus(stats=self.app.stats.getStats(self.app.opt.player, self.game.id))
            elif mode == 401:
                # start a new game with a gameid
                if gameid and gameid != self.game.id:
                    self.game.endGame()
                    self.game.quitGame(gameid)
            elif mode == 402:
                # start a new game with a gameid / gamenumber
                ## TODO
                pass
            else:
                print_err("stats problem: %s %s %s" % (mode, demo, player))
                pass
            if d.status != 0:
                break
            mode = d.button


    #
    # Assist menu
    #

    def mHint(self, *args):
        if self._cancelDrag(): return
        if self.app.opt.hint:
            if self.game.showHint(0, self.app.opt.timeouts['hint']):
                self.game.stats.hints += 1

    def mHint1(self, *args):
        if self._cancelDrag(): return
        if self.app.opt.hint:
            if self.game.showHint(1, self.app.opt.timeouts['hint']):
                self.game.stats.hints += 1

    def mHighlightPiles(self, *args):
        if self._cancelDrag(): return
        if self.app.opt.highlight_piles:
            if self.game.highlightPiles(self.app.opt.timeouts['highlight_piles']):
                self.game.stats.highlight_piles += 1

    def mDemo(self, *args):
        if self._cancelDrag(): return
        if self.game.getHintClass() is not None:
            self._mDemo(mixed=0)

    def mMixedDemo(self, *args):
        if self._cancelDrag(): return
        self._mDemo(mixed=1)

    def _mDemo(self, mixed):
        if self.changed():
            # only ask if there have been no demo moves or hints yet
            if self.game.stats.demo_moves == 0 and self.game.stats.hints == 0:
                if not self.game.areYouSure(_("Play demo")): return
        ##self.app.demo_counter = 0
        self.game.startDemo(mixed=mixed)


    #
    # Options menu
    #

    def mOptPlayerOptions(self, *args):
        if self._cancelDrag(break_pause=False): return
        d = PlayerOptionsDialog(self.top, _("Set player options"), self.app)
        if d.status == 0 and d.button == 0:
            self.app.opt.confirm = bool(d.confirm)
            self.app.opt.update_player_stats = bool(d.update_stats)
            self.app.opt.win_animation = bool(d.win_animation)
            ##n = string.strip(d.player)
            n = d.player[:30].strip()
            if 0 < len(n) <= 30:
                self.app.opt.player = n
                self.game.updateStatus(player=self.app.opt.player)
                self.game.updateStatus(stats=self.app.stats.getStats(self.app.opt.player, self.game.id))

    def mOptColors(self, *args):
        if self._cancelDrag(break_pause=False): return
        d = ColorsDialog(self.top, _("Set colors"), self.app)
        text_color = self.app.opt.colors['text']
        if d.status == 0 and d.button == 0:
            self.app.opt.colors['text'] = d.text_color
            self.app.opt.colors['piles'] = d.piles_color
            self.app.opt.colors['cards_1'] = d.cards_1_color
            self.app.opt.colors['cards_2'] = d.cards_2_color
            self.app.opt.colors['samerank_1'] = d.samerank_1_color
            self.app.opt.colors['samerank_2'] = d.samerank_2_color
            self.app.opt.colors['hintarrow'] = d.hintarrow_color
            self.app.opt.colors['not_matching'] = d.not_matching_color
            #
            if text_color != self.app.opt.colors['text']:
                self.app.setTile(self.app.tabletile_index, force=True)

    def mOptFonts(self, *args):
        if self._cancelDrag(break_pause=False): return
        d = FontsDialog(self.top, _("Set fonts"), self.app)
        if d.status == 0 and d.button == 0:
            self.app.opt.fonts.update(d.fonts)
            self._cancelDrag()
            self.game.endGame(bookmark=1)
            self.game.quitGame(bookmark=1)

    def mOptTimeouts(self, *args):
        if self._cancelDrag(break_pause=False): return
        d = TimeoutsDialog(self.top, _("Set timeouts"), self.app)
        if d.status == 0 and d.button == 0:
            self.app.opt.timeouts['demo'] = d.demo_timeout
            self.app.opt.timeouts['hint'] = d.hint_timeout
            self.app.opt.timeouts['raise_card'] = d.raise_card_timeout
            self.app.opt.timeouts['highlight_piles'] = d.highlight_piles_timeout
            self.app.opt.timeouts['highlight_cards'] = d.highlight_cards_timeout
            self.app.opt.timeouts['highlight_samerank'] = d.highlight_samerank_timeout


    #
    # Help menu
    #

    def mHelp(self, *args):
        if self._cancelDrag(break_pause=False): return
        help_html(self.app, "index.html", "html")

    def mHelpHowToPlay(self, *args):
        if self._cancelDrag(break_pause=False): return
        help_html(self.app, "howtoplay.html", "html")

    def mHelpRules(self, *args):
        if self._cancelDrag(break_pause=False): return
        if not self.menustate.rules:
            return
        dir = os.path.join("html", "rules")
        ## FIXME: plugins
        help_html(self.app, self.app.getGameRulesFilename(self.game.id), dir)

    def mHelpLicense(self, *args):
        if self._cancelDrag(break_pause=False): return
        help_html(self.app, "license.html", "html")

    def mHelpNews(self, *args):
        if self._cancelDrag(break_pause=False): return
        help_html(self.app, "news.html", "html")

    def mHelpWebSite(self, *args):
        openURL(PACKAGE_URL)

    def mHelpAbout(self, *args):
        if self._cancelDrag(break_pause=False): return
        help_about(self.app)

    #
    # misc
    #

    def mScreenshot(self, *args):
        if self._cancelDrag(): return
        f = os.path.join(self.app.dn.config, "screenshots")
        if not os.path.isdir(f):
            return
        f = os.path.join(f, self.app.getGameSaveName(self.game.id))
        i = 1
        while 1:
            fn = "%s-%d.ppm" % (f, i)
            if not os.path.exists(fn):
                break
            i = i + 1
            if i >= 10000:      # give up
                return
        self.top.screenshot(fn)

    def mPlayNextMusic(self, *args):
        if self._cancelDrag(break_pause=False): return
        if self.app.audio and self.app.opt.sound_music_volume > 0:
            self.app.audio.playNextMusic()
            if 1 and DEBUG:
                index = self.app.audio.getMusicInfo()
                music = self.app.music_manager.get(index)
                if music:
                    print "playing music:", music.filename

    def mIconify(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.top.wm_iconify()


# ************************************************************************
# * toolbar
# ************************************************************************

class PysolToolbar(PysolToolbarTk):
    def __init__(self, *args, **kwargs):
        self.game = None
        PysolToolbarTk.__init__(self, *args, **kwargs)

    #
    # public methods
    #

    def connectGame(self, game):
        self.game = game

    #
    # button event handlers - delegate to menubar
    #

    def mNewGame(self, *args):
        if not self._busy():
            self.menubar.mNewGame()
        return 1

    def mOpen(self, *args):
        if not self._busy():
            self.menubar.mOpen()
        return 1

    def mRestart(self, *args):
        if not self._busy():
            self.menubar.mRestart()
        return 1

    def mSave(self, *args):
        if not self._busy():
            self.menubar.mSaveAs()
        return 1

    def mUndo(self, *args):
        if not self._busy():
            self.menubar.mUndo()
        return 1

    def mRedo(self, *args):
        if not self._busy():
            self.menubar.mRedo()
        return 1

    def mDrop(self, *args):
        if not self._busy():
            self.menubar.mDrop()
        return 1

    def mShuffle(self, *args):
        if not self._busy():
            self.menubar.mShuffle()
        return 1

    def mPause(self, *args):
        if not self._busy():
            self.menubar.mPause()
        return 1

    def mPlayerStats(self, *args):
        if not self._busy():
            self.menubar.mPlayerStats()
        return 1

    def mHelpRules(self, *args):
        if not self._busy():
            self.menubar.mHelpRules()
        return 1

    def mQuit(self, *args):
        if not self._busy():
            self.menubar.mQuit()
        return 1

    def mOptPlayerOptions(self, *args):
        if not self._busy():
            self.menubar.mOptPlayerOptions()
        return 1

