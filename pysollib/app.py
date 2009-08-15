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
import os, re
import traceback

# PySol imports
from mfxutil import destruct, Struct
from mfxutil import pickle, unpickle, UnpicklingError
from mfxutil import getusername, getprefdir
from mfxutil import latin1_to_ascii, print_err
from util import CARDSET, IMAGE_EXTENSIONS
from settings import PACKAGE, VERSION_TUPLE, WIN_SYSTEM
from resource import CSI, CardsetConfig, Cardset, CardsetManager
from resource import Tile, TileManager
from resource import Sample, SampleManager
from resource import Music, MusicManager
from images import Images, SubsampledImages
from pysolrandom import PysolRandom
from gamedb import GI, GAME_DB, loadGame
from options import Options
from settings import TOP_SIZE, TOOLKIT
from settings import DEBUG
from winsystems import TkSettings

# Toolkit imports
from pysoltk import wm_withdraw, loadImage
from pysoltk import MfxDialog, MfxMessageDialog, MfxExceptionDialog
from pysoltk import TclError, MfxScrolledCanvas
from pysoltk import PysolProgressBar
from pysoltk import PysolStatusbar, HelpStatusbar
from pysoltk import SelectCardsetDialogWithPreview
from pysoltk import SelectDialogTreeData
from pysoltk import HTMLViewer
from pysoltk import destroy_find_card_dialog
from pysoltk import destroy_solver_dialog

from actions import PysolMenubar
from actions import PysolToolbar
from help import help_about, destroy_help_html


# ************************************************************************
# * Statistics
# ************************************************************************

class _GameStatResult:
    def __init__(self):
        self.min = 0
        self.max = 0
        self.top = []
        self.num = 0
        self.total = 0 # sum of all values
        self.average = 0

    def update(self, gameid, value, game_number, game_start_time):
        # update min & max
        if not self.min or value < self.min:
            self.min = value
        if not self.max or value > self.max:
            self.max = value
        # calculate position & update top
        position = None
        n = 0
        for i in self.top:
            if value < i.value:
                position = n+1
                v = Struct(gameid=gameid,
                           value=value,
                           game_number=game_number,
                           game_start_time=game_start_time)
                self.top.insert(n, v)
                del self.top[TOP_SIZE:]
                break
            n += 1
        if not position and len(self.top) < TOP_SIZE:
            v = Struct(gameid=gameid,
                       value=value,
                       game_number=game_number,
                       game_start_time=game_start_time)
            self.top.append(v)
            position = len(self.top)
        # update average
        self.total += value
        self.num += 1
        self.average = float(self.total)/self.num
        return position


class GameStat:
    def __init__(self, id):
        self.gameid = id
        #
        self.num_total = 0
        #self.num_not_won = 0
        self.num_lost = 0
        self.num_won = 0
        self.num_perfect = 0
        #
        self.time_result = _GameStatResult()
        self.moves_result = _GameStatResult()
        self.total_moves_result = _GameStatResult()
        self.score_result = _GameStatResult()
        self.score_casino_result = _GameStatResult()

    def update(self, game, status):
        #
        game_number = game.getGameNumber(format=0)
        game_start_time = game.gstats.start_time
        # update number of games
        # status:
        # -1 - NOT WON (not played)
        # 0 - LOST
        # 1 - WON
        # 2 - PERFECT
        self.num_total += 1
        assert status in (0, 1, 2)
        if status == 0:
            self.num_lost += 1
            return
        elif status == 1:
            self.num_won += 1
        else: # status == 2
            self.num_perfect += 1

        score = game.getGameScore()
        ##print 'GameScore:', score
        score_p = None
        if score is not None:
            score_p = self.score_result.update(
                game.id, score, game_number, game_start_time)
        score = game.getGameScoreCasino()
        ##print 'GameScoreCasino:', score
        score_casino_p = None
        if score is not None:
            score_casino_p = self.score_casino_result.update(
                game.id, score, game_number, game_start_time)

        if status == 0:
            return

        game.updateTime()
        time_p = self.time_result.update(
            game.id, game.stats.elapsed_time, game_number, game_start_time)
        moves_p = self.moves_result.update(
            game.id, game.moves.index, game_number, game_start_time)
        total_moves_p = self.total_moves_result.update(
            game.id, game.stats.total_moves, game_number, game_start_time)

        return time_p, moves_p, total_moves_p, score_p, score_casino_p


class Statistics:
    def __init__(self):
        self.version_tuple = VERSION_TUPLE
        self.saved = 0
        # a dictionary of dictionaries of GameStat (keys: player and gameid)
        self.games_stats = {}
        # a dictionary of lists of tuples (key: player)
        self.prev_games = {}
        self.all_prev_games = {}
        self.session_games = {}
        # some simple balance scores (key: gameid)
        self.total_balance = {}     # a dictionary of integers
        self.session_balance = {}   # reset per session
        self.gameid_balance = 0     # reset when changing the gameid

    def new(self):
        return Statistics()

    #
    # player & demo statistics
    #

    def resetStats(self, player, gameid):
        self.__resetPrevGames(player, self.prev_games, gameid)
        self.__resetPrevGames(player, self.session_games, gameid)
        if player not in self.games_stats:
            return
        if gameid == 0:
            # remove all games
            try: del self.games_stats[player]
            except KeyError: pass
        else:
            try: del self.games_stats[player][gameid]
            except KeyError: pass

    def __resetPrevGames(self, player, games, gameid):
        if player not in games:
            return
        if gameid == 0:
            del games[player]
        else:
            games[player] = [g for g in games[player] if g[0] != gameid]

    def getStats(self, player, gameid):
        # returned (won, lost)
        return self.getFullStats(player, gameid)[:2]

    def getFullStats(self, player, gameid):
        # returned (won, lost, playing time, moves)
        stats = self.games_stats
        if player in stats and gameid in stats[player]:
            s = self.games_stats[player][gameid]
            return (s.num_won+s.num_perfect,
                    s.num_lost,
                    s.time_result.average,
                    s.moves_result.average,)
        return (0, 0, 0, 0)

    def getSessionStats(self, player, gameid):
        games = self.session_games.get(player, [])
        games = [g for g in games if g[0] == gameid]
        won = len([g for g in games if g[2] > 0])
        lost = len([g for g in games if g[2] == 0])
        return won, lost

    def updateStats(self, player, game, status):
        ret = None
        log = (game.id, game.getGameNumber(format=0), status,
               game.gstats.start_time, game.gstats.total_elapsed_time,
               VERSION_TUPLE, game.getGameScore(), game.getGameScoreCasino(),
               game.GAME_VERSION)
        # full log
        if status >= 0:
            if player is None:
                # demo
                ret = self.updateGameStat(player, game, status)
            else:
                # player
                if player not in self.prev_games:
                    self.prev_games[player] = []
                self.prev_games[player].append(log)
                if player not in self.all_prev_games:
                    self.all_prev_games[player] = []
                self.all_prev_games[player].append(log)
                ret = self.updateGameStat(player, game, status)
        # session log
        if player not in self.session_games:
            self.session_games[player] = []
        self.session_games[player].append(log)
        return ret

    def updateGameStat(self, player, game, status):
        #
        if player not in self.games_stats:
            self.games_stats[player] = {}
        if game.id not in self.games_stats[player]:
            game_stat = GameStat(game.id)
            self.games_stats[player][game.id] = game_stat
        else:
            game_stat = self.games_stats[player][game.id]
        if 'all' not in self.games_stats[player]:
            all_games_stat = GameStat('all')
            self.games_stats[player]['all'] = all_games_stat
        else:
            all_games_stat = self.games_stats[player]['all']
        all_games_stat.update(game, status)
        return game_stat.update(game, status)

##     def __setstate__(self, state):      # for backward compatible
##         if 'gameid' not in state:
##             self.gameid = None
##         self.__dict__.update(state)


# ************************************************************************
# * Comments
# ************************************************************************

class Comments:
    def __init__(self):
        self.version_tuple = VERSION_TUPLE
        self.saved = 0
        #
        self.comments = {}

    def new(self):
        return Comments()

    def setGameComment(self, gameid, text):
        player = None
        key = (1, gameid, player)
        self.comments[key] = str(text)

    def getGameComment(self, gameid):
        player = None
        key = (1, gameid, player)
        return self.comments.get(key, "")


# ************************************************************************
# * Application
# * This is the glue between the toplevel window and a Game.
# * Also handles all global resources.
# ************************************************************************

class Application:
    def __init__(self):
        self.gdb = GAME_DB
        self.opt = Options()
        self.startup_opt = self.opt.copy()
        self.stats = Statistics()
        self.comments = Comments()
        self.splashscreen = 1
        # visual components
        self.top = None                 # the root toplevel window
        self.top_bg = None              # default background
        self.top_cursor = None          # default cursor
        self.menubar = None
        self.toolbar = None
        self.canvas = None              # MfxCanvas
        self.scrolled_canvas = None     # MfxScrolledCanvas
        self.statusbar = None
        #
        self.game = None
        self.dataloader = None
        self.audio = None
        self.images = None
        self.subsampled_images = None
        self.gimages = Struct(          # global images
            demo = [],                  # demo logos
            pause = [],                 # pause logos
            logos = [],
            redeal = [],
        )
        #self.progress_bg = None
        self.progress_images = []
        self.cardset_manager = CardsetManager()
        self.cardset = None             # current cardset
        self.cardsets_cache = {}
        self.tabletile_manager = TileManager()
        self.tabletile_index = 0        # current table tile
        self.sample_manager = SampleManager()
        self.music_manager = MusicManager()
        self.music_playlist = []
        self.intro = Struct(
            progress = None,            # progress bar
        )
        # directory names
        config = os.path.normpath(getprefdir(PACKAGE))
        self.dn = Struct(
            config = config,
            plugins = os.path.join(config, "plugins"),
            savegames = os.path.join(config, "savegames"),
            maint = os.path.join(config, "maint"),          # debug
        )
        for k, v in self.dn.__dict__.items():
##            if os.name == "nt":
##                v = os.path.normcase(v)
            v = os.path.normpath(v)
            self.dn.__dict__[k] = v
        # file names
        self.fn = Struct(
            opt      = os.path.join(self.dn.config, "options.dat"),
            opt_cfg  = os.path.join(self.dn.config, "options.cfg"),
            stats    = os.path.join(self.dn.config, "statistics.dat"),
            holdgame = os.path.join(self.dn.config, "holdgame.dat"),
            comments = os.path.join(self.dn.config, "comments.dat"),
        )
        for k, v in self.dn.__dict__.items():
            if os.name == "nt":
                v = os.path.normcase(v)
            v = os.path.normpath(v)
            self.fn.__dict__[k] = v
        # random generators
        self.gamerandom = PysolRandom()
        self.miscrandom = PysolRandom()
        # player
        player = getusername()
        if not player:
            player = "unknown"
        player = player[:30]
        self.opt.player = player
        # misc
        self.nextgame = Struct(
            id = 0,                     # start this game
            random = None,              # use this random generator
            loadedgame = None,          # data for loaded game
            startdemo = 0,              # start demo ?
            cardset = None,             # use this cardset
            holdgame = 0,               # hold this game on exit ?
            bookmark = None,            # goto this bookmark (load new cardset)
        )
        self.commandline = Struct(
            loadgame = None,            # load a game ?
            game = None,
            gameid = None,
        )
        self.demo_counter = 0


    # the PySol mainloop
    def mainloop(self):
        # copy startup options
        self.startup_opt = self.opt.copy()
        # try to load statistics
        try:
            self.loadStatistics()
        except:
            traceback.print_exc()
            pass
        # try to load comments
        try:
            self.loadComments()
        except:
            traceback.print_exc()
            pass
        # startup information
        if self.getGameClass(self.opt.last_gameid):
            self.nextgame.id = self.opt.last_gameid
        # load a holded or saved game
        id = self.gdb.getGamesIdSortedByName()[0]
        tmpgame = self.constructGame(id)
        if self.opt.game_holded > 0 and not self.nextgame.loadedgame:
            game = None
            try:
                game = tmpgame._loadGame(self.fn.holdgame, self)
            except:
                traceback.print_exc()
                game = None
            if game:
                if game.id == self.opt.game_holded and game.gstats.holded:
                    game.gstats.loaded = game.gstats.loaded - 1
                    game.gstats.holded = 0
                    self.nextgame.loadedgame = game
                else:
                    # not a holded game
                    game.destruct()
                    destruct(game)
            game = None
        if not self.nextgame.loadedgame:
            if self.commandline.loadgame:
                try:
                    self.nextgame.loadedgame = tmpgame._loadGame(self.commandline.loadgame, self)
                    self.nextgame.loadedgame.gstats.holded = 0
                except:
                    traceback.print_exc()
                    self.nextgame.loadedgame = None
            elif self.commandline.game is not None:
                gameid = self.gdb.getGameByName(self.commandline.game)
                if gameid is None:
                    print_err(_("can't find game: ") + self.commandline.game)
                else:
                    self.nextgame.id, self.nextgame.random = gameid, None
            elif self.commandline.gameid is not None:
                self.nextgame.id, self.nextgame.random = self.commandline.gameid, None
        self.opt.game_holded = 0
        tmpgame.destruct()
        destruct(tmpgame)
        tmpgame = None
        #
        # widgets
        #
        # create the menubar
        if self.intro.progress: self.intro.progress.update(step=1)
        self.menubar = PysolMenubar(self, self.top,
                                    progress=self.intro.progress)
        # create the statusbar(s)
        self.statusbar = PysolStatusbar(self.top)
        self.statusbar.show(self.opt.statusbar)
        self.statusbar.config('gamenumber', self.opt.statusbar_game_number)
        self.statusbar.config('stuck', self.opt.statusbar_stuck)
        self.helpbar = HelpStatusbar(self.top)
        self.helpbar.show(self.opt.helpbar)
        # create the canvas
        self.scrolled_canvas = MfxScrolledCanvas(self.top, propagate=True)
        self.canvas = self.scrolled_canvas.canvas
        padx, pady = TkSettings.canvas_padding
        self.scrolled_canvas.grid(row=1, column=1, sticky='nsew',
                                  padx=padx, pady=pady)
        self.top.grid_columnconfigure(1, weight=1)
        self.top.grid_rowconfigure(1, weight=1)
        self.setTile(self.tabletile_index, force=True)
        # create the toolbar
        dir = self.getToolbarImagesDir()
        self.toolbar = PysolToolbar(self.top, self.menubar, dir=dir,
                                    size=self.opt.toolbar_size,
                                    relief=self.opt.toolbar_relief,
                                    compound=self.opt.toolbar_compound)
        self.toolbar.show(self.opt.toolbar)
        if TOOLKIT == 'tk':
            for w, v in self.opt.toolbar_vars.items():
                self.toolbar.config(w, v)
        #
        if self.intro.progress: self.intro.progress.update(step=1)
        #
        try:
            # this is the mainloop
            while 1:
                assert self.cardset is not None
                id, random = self.nextgame.id, self.nextgame.random
                self.nextgame.id, self.nextgame.random = 0, None
                try:
                    self.runGame(id, random)
                except:
                    # try Klondike if current game fails
                    if id == 2:
                        raise           # internal error?
                    if DEBUG:
                        raise
                    traceback.print_exc()
                    self.nextgame.id = 2
                    self.freeGame()
                    continue
                if self.nextgame.holdgame:
                    assert self.nextgame.id <= 0
                    try:
                        self.game.gstats.holded = 1
                        self.game._saveGame(self.fn.holdgame)
                        self.opt.game_holded = self.game.id
                    except:
                        traceback.print_exc()
                        pass
                self.wm_save_state()
                # save game geometry
                if self.opt.save_games_geometry and not self.opt.wm_maximized:
                    w = self.canvas.winfo_width()
                    h = self.canvas.winfo_height()
                    geom = (w, h)
                    self.opt.games_geometry[self.game.id] = geom
                self.freeGame()
                #
                if self.nextgame.id <= 0:
                    break
                # load new cardset
                if self.nextgame.cardset is not self.cardset:
                    self.loadCardset(self.nextgame.cardset, id=self.nextgame.id, update=7+256)
                else:
                    self.requestCompatibleCardsetType(self.nextgame.id)
        finally:
            # hide main window
            self.wm_withdraw()
            #
            destroy_help_html()
            destroy_find_card_dialog()
            destroy_solver_dialog()
            # update options
            self.opt.last_gameid = id
            # save options
            try: self.saveOptions()
            except:
                traceback.print_exc()
                pass
            # save statistics
            try: self.saveStatistics()
            except:
                traceback.print_exc()
                pass
            # save comments
            try: self.saveComments()
            except:
                traceback.print_exc()
                pass
            # shut down audio
            try: self.audio.destroy()
            except:
                traceback.print_exc()
                pass


    def runGame(self, id, random=None):
        self.top.connectApp(self)
        # create game instance
        g = self.getGameClass(id)
        if g is None:
            id = 2          # start Klondike as default game
            random = None
            g = self.getGameClass(id)
            if g is None:
                # start first available game
                id = self.gdb.getGamesIdSortedByName()[0]
                g = self.getGameClass(id)
        gi = self.getGameInfo(id)
        assert gi is not None and gi.id == id
        self.game = self.constructGame(id)
        self.gdb.setSelected(id)
        self.game.busy = 1
        # create stacks and layout
        self.game.create(self)
        # connect with game
        self.menubar.connectGame(self.game)
        if self.toolbar: ##~
            self.toolbar.connectGame(self.game)
        self.game.updateStatus(player=self.opt.player)
        # update "Recent games" menubar entry
        if id in self.opt.recent_gameid:
            self.opt.recent_gameid.remove(id)
        self.opt.recent_gameid.insert(0, id)
        del self.opt.recent_gameid[self.opt.num_recent_games:]
        self.menubar.updateRecentGamesMenu(self.opt.recent_gameid)
        self.menubar.updateFavoriteGamesMenu()
        # hide/show "Shuffle" button
        self.toolbar.config(
            'shuffle',
            self.opt.toolbar_vars['shuffle'] and self.game.canShuffle())
        # delete intro progress bar
        if self.intro.progress:
            self.intro.progress.destroy()
            destruct(self.intro.progress)
            self.intro.progress = None
        # prepare game
        autoplay = 0
        if self.nextgame.loadedgame is not None:
            self.stats.gameid_balance = 0
            self.game.restoreGame(self.nextgame.loadedgame)
            destruct(self.nextgame.loadedgame)
        elif self.nextgame.bookmark is not None:
            self.game.restoreGameFromBookmark(self.nextgame.bookmark)
        else:
            self.stats.gameid_balance = 0
            self.game.newGame(random=random, autoplay=0)
            autoplay = 1
        self.nextgame.loadedgame = None
        self.nextgame.bookmark = None
        # splash screen
        if self.opt.splashscreen and self.splashscreen > 0:
            status = help_about(self, timeout=20000, sound=0)
            if status == 2:                 # timeout - start a demo
                if autoplay:
                    self.nextgame.startdemo = 1
        self.splashscreen = 0
        # start demo/autoplay
        if self.nextgame.startdemo:
            self.nextgame.startdemo = 0
            self.game.startDemo()
            self.game.createDemoInfoText()
        elif autoplay:
            self.game.autoPlay()
            self.game.stats.player_moves = 0
        # enter the Tk mainloop
        self.game.busy = 0
        self.top.mainloop()


    # free game
    def freeGame(self):
        # disconnect from game
        self.menubar.connectGame(None)
        self.toolbar.connectGame(None)
        # clean up the canvas
        self.canvas.deleteAllItems()
        self.canvas.update_idletasks()
        # destruct the game
        if self.game:
            self.game.destruct()
            destruct(self.game)
        self.game = None
        self.top.connectApp(None)


    #
    # UI support
    #

    def wm_save_state(self):
        if self.top:
            s = self.top.wm_state()
            ##print "wm_save_state", s
            if s == "zoomed": # Windows only
                self.opt.wm_maximized = True
            elif s == "normal":
                self.opt.wm_maximized = False

    def wm_withdraw(self):
        if self.intro.progress:
            self.intro.progress.destroy()
            destruct(self.intro.progress)
            self.intro.progress = None
        if self.top:
            wm_withdraw(self.top)
            self.top.busyUpdate()

    def loadImages1(self):
        # load dialog images
        dir = os.path.join("images", "logos")
        for f in ("joker07_40_774",
                  "joker08_40_774",
                  "joker07_50_774",
                  "joker08_50_774",
                  "joker11_100_774",
                  "joker10_100",):
            self.gimages.logos.append(self.dataloader.findImage(f, dir))
        if WIN_SYSTEM == 'win32':
            dir = os.path.join('images', 'dialog', 'default')
        else:
            dir = os.path.join('images', 'dialog', 'bluecurve')
        for f in ('error', 'info', 'question', 'warning'):
            fn = self.dataloader.findImage(f, dir)
            im = loadImage(fn)
            MfxMessageDialog.img[f] = im

        # load button images
        if 0 and TOOLKIT == 'tk':
            dir = os.path.join('images', 'buttons', 'bluecurve')
            for n, f in (
                (_('&OK'), 'ok'),
                (_('&Cancel'), 'cancel'),
                (_('&New game'), 'new'),
                ):
                fn = self.dataloader.findImage(f, dir)
                im = loadImage(fn)
                MfxDialog.button_img[n] = im

    def loadImages2(self):
        # load canvas images
        dir = "images"
        ##for f in ("noredeal", "redeal",):
        for f in ("stopsign", "redeal",):
            self.gimages.redeal.append(self.dataloader.findImage(f, dir))
        dir = os.path.join("images", "demo")
        for f in ("demo01", "demo02", "demo03", "demo04", "demo05",):
            self.gimages.demo.append(self.dataloader.findImage(f, dir))
        dir = os.path.join("images", "pause")
        for f in ("pause01", "pause02", "pause03",):
            self.gimages.pause.append(self.dataloader.findImage(f, dir))
        ##dir = os.path.join("images", "stats")
        ##for f in ("barchart",):
        ##    self.gimages.stats.append(self.dataloader.findImage(f, dir))

    def loadImages3(self):
        # load treeview images
        SelectDialogTreeData.img = []
        dir = os.path.join('images', 'tree')
        for f in ('folder', 'openfolder', 'node', 'emptynode'):
            fn = self.dataloader.findImage(f, dir)
            im = loadImage(fn)
            SelectDialogTreeData.img.append(im)

        # load htmlviewer images
        dir = os.path.join('images', 'htmlviewer')
        fn = self.dataloader.findImage('disk', dir)
        HTMLViewer.symbols_fn['disk'] = fn

    def loadImages4(self):
        # load all remaining images
        for k, v in self.gimages.__dict__.items():
            if isinstance(v, list):
                for i in range(len(v)):
                    if isinstance(v[i], str):
                        v[i] = loadImage(v[i])
                        if self.intro.progress:
                            self.intro.progress.update(step=1)
                self.gimages.__dict__[k] = tuple(v)

    def _getImagesDir(self, *dirs, **kwargs):
        check = kwargs.get('check', True)
        dirs = [str(d) for d in dirs]   # XXX: don't use unicode
        d =  os.path.join(self.dataloader.dir, 'images', *dirs)
        if check:
            if os.path.exists(d):
                return d
            return None
        return d

    def getFindCardImagesDir(self):
        return self._getImagesDir('cards')

    def getToolbarImagesDir(self):
        if self.opt.toolbar_size:
            size = 'large'
        else:
            size = 'small'
        style = self.opt.toolbar_style
        d = self._getImagesDir('toolbar', style, size)
        if d:
            return d
        return self._getImagesDir('toolbar', 'default', size, check=False)

    def setTile(self, i, force=0):
        if self.scrolled_canvas.setTile(self, i, force):
            tile = self.tabletile_manager.get(i)
            if i == 0:
                self.opt.colors['table'] = tile.color
                self.opt.tabletile_name = None
            else:
                self.opt.tabletile_name = tile.basename
            self.tabletile_index = i
            self.tabletile_manager.setSelected(i)
            return True
        return False

    def getFont(self, name):
        return self.opt.fonts.get(name)


    #
    # cardset
    #

    def updateCardset(self, id=0, update=7):
        cs = self.images.cs
        self.cardset = cs
        self.nextgame.cardset = cs
        # update settings
        self.cardset_manager.setSelected(cs.index)
        # update options
        self.images.setNegative(self.opt.negative_bottom)
        self.subsampled_images.setNegative(self.opt.negative_bottom)
        if update & 1:
            self.opt.cardset[0] = (cs.name, cs.backname)
        if update & 2:
            self.opt.cardset[cs.si.type] = (cs.name, cs.backname)
        gi = self.getGameInfo(id)
        if gi:
            if update & 256:
                try:
                    del self.opt.cardset[(1, gi.id)]
                except KeyError:
                    pass
            t = self.checkCompatibleCardsetType(gi, cs)
            if not t[1]:
                if update & 4:
                    self.opt.cardset[gi.category] = (cs.name, cs.backname)
                if update & 8:
                    self.opt.cardset[(1, gi.id)] = (cs.name, cs.backname)
        #from pprint import pprint; pprint(self.opt.cardset)

    def loadCardset(self, cs, id=0, update=7, progress=None):
        ##print 'loadCardset', cs.ident
        r = 0
        if cs is None or cs.error:
            return 0
        if cs is self.cardset:
            self.updateCardset(id, update=update)
            return 1
        # cache carsets
        # self.cardsets_cache:
        #   key: Cardset.type
        #   value: (Cardset.ident, Images, SubsampledImages)
        c = self.cardsets_cache.get(cs.type)
        if c and c[0] == cs.ident:
            #print 'load from cache', c
            self.images, self.subsampled_images = c[1], c[2]
            self.updateCardset(id, update=update)
            if self.menubar is not None:
                self.menubar.updateBackgroundImagesMenu()
            return 1
        #
        if progress is None:
            self.wm_save_state()
            self.wm_withdraw()
            title = _("Loading %s %s...") % (CARDSET, cs.name)
            color = self.opt.colors['table']
            if self.tabletile_index > 0:
                color = "#008200"
            progress = PysolProgressBar(self, self.top, title=title,
                                        color=color,
                                        images=self.progress_images)
        images = Images(self.dataloader, cs)
        try:
            if not images.load(app=self, progress=progress):
                raise Exception("Invalid or damaged "+CARDSET)
            simages = SubsampledImages(images)
            if self.opt.save_cardsets:
                c = self.cardsets_cache.get(cs.type)
                if c:
                    ##c[1].destruct()
                    destruct(c[1])
                self.cardsets_cache[cs.type] = (cs.ident, images, simages)
            elif self.images is not None:
                ##self.images.destruct()
                destruct(self.images)
            #
            if self.cardset and self.cardset.ident != cs.ident and \
                   self.cardset.type == cs.type:
                self.opt.games_geometry = {} # clear saved games geometry
            # update
            self.images = images
            self.subsampled_images = simages
            self.updateCardset(id, update=update)
            r = 1
        except (Exception, TclError, UnpicklingError), ex:
            traceback.print_exc()
            cs.error = 1
            # restore settings
            self.nextgame.cardset = self.cardset
            if self.cardset:
                self.cardset_manager.setSelected(self.cardset.index)
            ##images.destruct()
            destruct(images)
            d = MfxExceptionDialog(self.top, ex, title=CARDSET+_(" load error"),
                                   text=_("Error while loading ")+CARDSET)
        self.intro.progress = progress
        if r and self.menubar is not None:
            self.menubar.updateBackgroundImagesMenu()
        return r

    def checkCompatibleCardsetType(self, gi, cs):
        assert gi is not None
        assert cs is not None
        gc = gi.category
        cs_type = cs.si.type
        t0, t1 = None, None
        if gc == GI.GC_FRENCH:
            t0 = "French"
            if cs_type not in (CSI.TYPE_FRENCH,
                               ##CSI.TYPE_TAROCK,
                               ):
                t1 = t0
        elif gc == GI.GC_HANAFUDA:
            t0 = "Hanafuda"
            if cs_type not in (CSI.TYPE_HANAFUDA,):
                t1 = t0
        elif gc == GI.GC_TAROCK:
            t0 = "Tarock"
            if cs_type not in (CSI.TYPE_TAROCK,):
                t1 = t0
        elif gc == GI.GC_MAHJONGG:
            t0 = "Mahjongg"
            if cs_type not in (CSI.TYPE_MAHJONGG,):
                t1 = t0
        elif gc == GI.GC_HEXADECK:
            t0 = "Hex A Deck"
            if cs_type not in (CSI.TYPE_HEXADECK,):
                t1 = t0
        elif gc == GI.GC_MUGHAL_GANJIFA:
            t0 = "Mughal Ganjifa"
            if cs_type not in (CSI.TYPE_MUGHAL_GANJIFA,
                               CSI.TYPE_NAVAGRAHA_GANJIFA,
                               CSI.TYPE_DASHAVATARA_GANJIFA,):
                t1 = t0
        elif gc == GI.GC_NAVAGRAHA_GANJIFA:
            t0 = "Navagraha Ganjifa"
            if cs_type not in (CSI.TYPE_NAVAGRAHA_GANJIFA,
                               CSI.TYPE_DASHAVATARA_GANJIFA,):
                t1 = t0
        elif gc == GI.GC_DASHAVATARA_GANJIFA:
            t0 = "Dashavatara Ganjifa"
            if cs_type not in (CSI.TYPE_DASHAVATARA_GANJIFA,):
                t1 = t0
        elif gc == GI.GC_TRUMP_ONLY:
            t0 = "Trump only"
            if cs_type not in (CSI.TYPE_TRUMP_ONLY,):
                t1 = t0
            elif len(cs.trumps) < gi.ncards:    # not enough cards
                t1 = t0
        else:
            # we should not come here
            t0 = t1 = "Unknown"
        return t0, t1

    def getCompatibleCardset(self, gi, cs):
        if gi is None:
            return cs, 1
        # try current
        if cs:
            t = self.checkCompatibleCardsetType(gi, cs)
            if not t[1]:
                return cs, 1
        # try by gameid / category
        for key, flag in (((1, gi.id), 8), (gi.category, 4)):
            c = self.opt.cardset.get(key)
            if not c or len(c) != 2:
                continue
            cs = self.cardset_manager.getByName(c[0])
            if not cs:
                continue
            t = self.checkCompatibleCardsetType(gi, cs)
            if not t[1]:
                cs.updateCardback(backname=c[1])
                return cs, flag
        # ask
        return None, 0

    def requestCompatibleCardsetType(self, id):
        gi = self.getGameInfo(id)
        #
        cs, cs_update_flag = self.getCompatibleCardset(gi, self.cardset)
        if cs is self.cardset:
            return 0
        if cs is not None:
            self.loadCardset(cs, update=1)
            return 1
        #
        t = self.checkCompatibleCardsetType(gi, self.cardset)
        d = MfxMessageDialog(self.top, title=_("Incompatible ")+CARDSET,
                      bitmap="warning",
                      text=_('''The currently selected %s %s
is not compatible with the game
%s

Please select a %s type %s.
''') % (CARDSET, self.cardset.name, gi.name, t[0], CARDSET),
                      strings=(_("&OK"),), default=0)
        cs = self.__selectCardsetDialog(t)
        if cs is None:
            return -1
        self.loadCardset(cs, id=id)
        return 1

    def __selectCardsetDialog(self, t):
        key = self.cardset.index
        d = SelectCardsetDialogWithPreview(
            self.top, title=_("Please select a %s type %s") % (t[0], CARDSET),
            app=self, manager=self.cardset_manager, key=key,
            strings=(None, _("&OK"), _("&Cancel")), default=1)
        if d.status != 0 or d.button != 1:
            return None
        cs = self.cardset_manager.get(d.key)
        if cs is None or d.key == key:
            return None
        return cs


    #
    # load & save options, statistics and comments
    #

    def loadOptions(self):
        self.opt.setDefaults(self.top)
        if os.path.exists(self.fn.opt):
            # for backwards compatibility
            opt = unpickle(self.fn.opt)
            if opt:
                self.opt.__dict__.update(opt.__dict__)
            try:
                os.remove(self.fn.opt)
            except:
                pass
        self.opt.load(self.fn.opt_cfg)
        self.opt.setConstants()

    def loadStatistics(self):
        if not os.path.exists(self.fn.stats):
            return
        stats = unpickle(self.fn.stats)
        if stats:
            ##print "loaded:", stats.__dict__
            self.stats.__dict__.update(stats.__dict__)
        # start a new session
        self.stats.session_games = {}
        self.stats.session_balance = {}
        self.stats.gameid_balance = 0

    def loadComments(self):
        if not os.path.exists(self.fn.comments):
            return
        comments = unpickle(self.fn.comments)
        if comments:
            ##print "loaded:", comments.__dict__
            self.comments.__dict__.update(comments.__dict__)

    def __saveObject(self, obj, fn):
        obj.version_tuple = VERSION_TUPLE
        obj.saved += 1
        pickle(obj, fn, protocol=-1)

    def saveOptions(self):
        self.opt.save(self.fn.opt_cfg)

    def saveStatistics(self):
        self.__saveObject(self.stats, self.fn.stats)

    def saveComments(self):
        self.__saveObject(self.comments, self.fn.comments)


    #
    # access games database
    #

    def constructGame(self, id):
        gi = self.gdb.get(id)
        if gi is None:
            raise Exception("Unknown game (id %d)" % id)
        return gi.gameclass(gi)

    def getGamesIdSortedById(self):
        return self.gdb.getGamesIdSortedById()

    def getGamesIdSortedByName(self, player=''):
        return self.gdb.getGamesIdSortedByName()

    ##
    def getGamesIdSortedByPlayed(self, player=''):
        if player == '': player = self.opt.player
        def _cmp(a, b):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            wb, lb, tb, mb = self.stats.getFullStats(player, b)
            return cmp(wb+lb, wa+la)  # reverse
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(_cmp)
        return games

    def getGamesIdSortedByWon(self, player=''):
        if player == '': player = self.opt.player
        def _cmp(a, b):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            wb, lb, tb, mb = self.stats.getFullStats(player, b)
            return cmp(wb, wa)  # reverse
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(_cmp)
        return games

    def getGamesIdSortedByLost(self, player=''):
        if player == '': player = self.opt.player
        def _cmp(a, b):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            wb, lb, tb, mb = self.stats.getFullStats(player, b)
            return cmp(lb, la)  # reverse
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(_cmp)
        return games

    def getGamesIdSortedByPercent(self, player=''):
        if player == '': player = self.opt.player
        def _cmp(a, b):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            wb, lb, tb, mb = self.stats.getFullStats(player, b)
            if wa+la == 0 or wb+lb == 0:
                return cmp(wb+lb, wa+la)  # reverse
            return cmp(float(wb)/(wb+lb),
                       float(wa)/(wa+la))  # reverse
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(_cmp)
        return games

    def getGamesIdSortedByPlayingTime(self, player=''):
        if player == '': player = self.opt.player
        def _cmp(a, b):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            wb, lb, tb, mb = self.stats.getFullStats(player, b)
            return cmp(tb, ta)  # reverse
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(_cmp)
        return games

    def getGamesIdSortedByMoves(self, player=''):
        if player == '': player = self.opt.player
        def _cmp(a, b):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            wb, lb, tb, mb = self.stats.getFullStats(player, b)
            return cmp(mb, ma)  # reverse
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(_cmp)
        return games


    def getGameInfo(self, id):
        return self.gdb.get(id)

    def getGameClass(self, id):
        gi = self.gdb.get(id)
        if gi is None: return None
        return gi.gameclass

    def getGameTitleName(self, id):
        gi = self.gdb.get(id)
        if gi is None: return None
        return gi.name

    def getGameMenuitemName(self, id):
        gi = self.gdb.get(id)
        if gi is None: return None
        return gi.short_name

    def getGameRulesFilename(self, id):
        gi = self.gdb.get(id)
        if gi is None: return None
        if gi.rules_filename is not None:
            return gi.rules_filename
        n = gi.en_name                  # english name
        ##n = re.sub(r"[\[\(].*$", "", n)
        n = latin1_to_ascii(n)
        n = re.sub(r"[^\w]", "", n)
        n = n.lower() + ".html"
        f = os.path.join(self.dataloader.dir, "html", "rules", n)
        if not os.path.exists(f):
            n = ''
        gi.rules_filename = n    # cache the filename for next use
        return n

    def getGameSaveName(self, id):
        if os.path.supports_unicode_filenames: # new in python 2.3
            return self.getGameTitleName(id)
        gi = self.gdb.get(id)
        n = gi.en_name                  # english name
        if not n: return None
##         m = re.search(r"^(.*)([\[\(](\w+).*[\]\)])\s*$", n)
##         if m:
##             n = m.group(1) + "_" + m.group(2).lower()
        n = latin1_to_ascii(n)
        n = n.lower()
        n = re.sub(r"[\s]", "_", n)
        n = re.sub(r"[^\w]", "", n)
        return n

    def getRandomGameId(self, games=None):
        if games is None:
            return self.miscrandom.choice(self.gdb.getGamesIdSortedById())
        return self.miscrandom.choice(games)

    def getAllUserNames(self):
        names = []
        for n in self.stats.games_stats.keys():
            if n is None:               # demo
                continue
            if self.stats.games_stats[n]:
                names.append(n)
        if self.opt.player not in names:
            names.append(self.opt.player)
        names.sort()
        return names

    def getGamesForSolver(self):
        return self.gdb.getGamesForSolver()

    #
    # plugins
    #

    def loadPlugins(self, dir):
        if not dir or not os.path.isdir(dir):
            return
        names = os.listdir(dir)
        names = map(os.path.normcase, names)
        names.sort()
        for name in names:
            m = re.search(r"^(.+)\.py$", name)
            n = os.path.join(dir, name)
            if m and os.path.isfile(n):
                try:
                    loadGame(m.group(1), n)
                except Exception, ex:
                    if DEBUG:
                        traceback.print_exc()
                    print_err(_("error loading plugin %s: %s") % (n, ex))


    #
    # init cardsets
    #

    # read & parse a cardset config.txt file - see class Cardset in resource.py
    def _readCardsetConfig(self, dir, filename):
        f = None
        try:
            f = open(filename, "r")
            lines = f.readlines()
        finally:
            if f: f.close()
        lines = [l.strip() for l in lines]
        if not lines[0].startswith("PySol"):
            return None
        config = CardsetConfig()
        if not self._parseCardsetConfig(config, lines):
            ##print filename, 'invalid config'
            return None
        if config.CARDD > self.top.winfo_screendepth():
            return None
        cs = Cardset()
        cs.dir = dir
        cs.update(config.__dict__)
        return cs

    def _parseCardsetConfig(self, cs, line):
        def perr(line, field=None, msg=''):
            if not DEBUG:
                return
            if field:
                print_err('_parseCardsetConfig error: line #%d, field #%d %s'
                          % (line, field, msg))
            else:
                print_err('_parseCardsetConfig error: line #%d: %s'
                          % (line, msg))
        if len(line) < 6:
            perr(1, msg='number of lines')
            return 0
        # line[0]: magic identifier, possible version information
        fields = [f.strip() for f in line[0].split(';')]
        if len(fields) >= 2:
            m = re.search(r"^(\d+)$", fields[1])
            if m: cs.version = int(m.group(1))
        if cs.version >= 3:
            if len(fields) < 5:
                perr(1, msg='number of fields')
                return 0
            cs.ext = fields[2]
            m = re.search(r"^(\d+)$", fields[3])
            if not m:
                perr(1, 3, 'not integer')
                return 0
            cs.type = int(m.group(1))
            m = re.search(r"^(\d+)$", fields[4])
            if not m:
                perr(1, 4, 'not integer')
                return 0
            cs.ncards = int(m.group(1))
        if cs.version >= 4:
            if len(fields) < 6:
                perr(1, msg='number of fields')
                return 0
            styles = fields[5].split(",")
            for s in styles:
                m = re.search(r"^\s*(\d+)\s*$", s)
                if not m:
                    perr(1, 5, 'not integer')
                    return 0
                s = int(m.group(1))
                if s not in cs.styles:
                    cs.styles.append(s)
        if cs.version >= 5:
            if len(fields) < 7:
                perr(1, msg='number of fields')
                return 0
            m = re.search(r"^(\d+)$", fields[6])
            if not m:
                perr(1, 6, 'not integer')
                return 0
            cs.year = int(m.group(1))
        if len(cs.ext) < 2 or cs.ext[0] != ".":
            perr(1, msg='invalid extention')
            return 0
        # line[1]: identifier/name
        if not line[1]:
            perr(2, msg='empty line')
            return 0
        cs.ident = line[1]
        m = re.search(r"^(.*;)?([^;]+)$", cs.ident)
        if not m:
            perr(2, msg='invalid format')
            return 0
        cs.name = m.group(2).strip()
        # line[2]: CARDW, CARDH, CARDD
        m = re.search(r"^(\d+)\s+(\d+)\s+(\d+)", line[2])
        if not m:
            perr(3, msg='invalid format')
            return 0
        cs.CARDW, cs.CARDH, cs.CARDD = int(m.group(1)), int(m.group(2)), int(m.group(3))
        # line[3]: CARD_UP_YOFFSET, CARD_DOWN_YOFFSET, SHADOW_XOFFSET, SHADOW_YOFFSET
        m = re.search(r"^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line[3])
        if not m:
            perr(4, msg='invalid format')
            return 0
        cs.CARD_XOFFSET = int(m.group(1))
        cs.CARD_YOFFSET = int(m.group(2))
        cs.SHADOW_XOFFSET = int(m.group(3))
        cs.SHADOW_YOFFSET = int(m.group(4))
        # line[4]: default background
        back = line[4]
        if not back:
            perr(5, msg='empty line')
            return 0
        # line[5]: all available backgrounds
        cs.backnames = [f.strip() for f in line[5].split(';')]
        if back in cs.backnames:
            cs.backindex = cs.backnames.index(back)
        else:
            cs.backnames.insert(0, back)
            cs.backindex = 0
        ##if cs.type != 1: print cs.type, cs.name
        return 1

    def initCardsets(self):
        manager = self.cardset_manager
        # find all available cardsets
        dirs = manager.getSearchDirs(self, ("cardsets", ""), "PYSOL_CARDSETS")
        if DEBUG:
            dirs = dirs + manager.getSearchDirs(self, "cardsets-*")
        ##print dirs
        found, t = [], {}
        for dir in dirs:
            dir = dir.strip()
            try:
                names = []
                if dir and os.path.isdir(dir) and dir not in t:
                    t[dir] = 1
                    names = os.listdir(dir)
                    names.sort()
                for name in names:
                    if not name.startswith('cardset-'): continue
                    d = os.path.join(dir, name)
                    if not os.path.isdir(d): continue
                    f1 = os.path.join(d, "config.txt")
                    f2 = os.path.join(d, "COPYRIGHT")
                    if os.path.isfile(f1) and os.path.isfile(f2):
                        try:
                            cs = self._readCardsetConfig(d, f1)
                            if cs:
                                ##from pprint import pprint
                                ##print cs.name
                                ##pprint(cs.__dict__)
                                back = cs.backnames[cs.backindex]
                                f1 = os.path.join(d, back)
                                f2 = os.path.join(d, "shade" + cs.ext)
                                if (cs.ext in IMAGE_EXTENSIONS and
                                    os.path.isfile(f1) and os.path.isfile(f2)):
                                    found.append(cs)
                                    #print '+', cs.name
                            else:
                                print_err('fail _readCardsetConfig: %s %s'
                                          % (d, f1))
                                pass
                        except Exception, err:
                            ##traceback.print_exc()
                            pass
            except EnvironmentError, ex:
                pass
        # register cardsets
        for obj in found:
            if not manager.getByName(obj.name):
                manager.register(obj)
                ##print obj.index, obj.name


    #
    # init tiles
    #

    def initTiles(self):
        manager = self.tabletile_manager
        # find all available tiles
        dirs = manager.getSearchDirs(self,
                           ("tiles-*",
                            os.path.join("tiles", "stretch"),
                            os.path.join("tiles", "save-aspect")),
                           "PYSOL_TILES")
        ##print dirs
        s = "((\\" + ")|(\\".join(IMAGE_EXTENSIONS) + "))$"
        ext_re = re.compile(s, re.I | re.U)
        found, t = [], {}
        for dir in dirs:
            try:
                names = []
                if dir and os.path.isdir(dir):
                    names = os.listdir(dir)
                for name in names:
                    if not name or not ext_re.search(name):
                        continue
                    f = os.path.join(dir, name)
                    if not os.path.isfile(f):
                        continue
                    tile = Tile()
                    tile.filename = f
                    n = ext_re.sub("", name)
                    if os.path.split(dir)[-1] == 'stretch':
                        tile.stretch = 1
                    if os.path.split(dir)[-1] == 'save-aspect':
                        tile.stretch = 1
                        tile.save_aspect = 1
                    #n = re.sub("[-_]", " ", n)
                    n = n.replace('_', ' ')
                    tile.name = n
                    key = n.lower()
                    if key not in t:
                        t[key] = 1
                        found.append((n, tile))
            except EnvironmentError, ex:
                pass
        # register tiles
        found.sort()
        for f in found:
            obj = f[1]
            if not manager.getByName(obj.name):
                manager.register(obj)


    #
    # init samples / music
    #

    def initResource(self, manager, dirs, ext_re, Resource_Class):
        found, t = [], {}
        for dir in dirs:
            dir = dir.strip()
            if dir:
                dir = os.path.normpath(dir)
            try:
                names = []
                if dir and os.path.isdir(dir):
                    names = os.listdir(dir)
                    names = map(os.path.normcase, names)
                    names.sort()
                for name in names:
                    if not name or not ext_re.search(name):
                        continue
                    f = os.path.join(dir, name)
                    f = os.path.normpath(f)
                    if not os.path.isfile(f):
                        continue
                    obj = Resource_Class()
                    obj.filename = f
                    n = ext_re.sub("", name.strip())
                    obj.name = n
                    key = n.lower()
                    if key not in t:
                        t[key] = 1
                        found.append((n, obj))
            except EnvironmentError, ex:
                pass
        # register songs
        found.sort()
        if manager:
            for f in found:
                obj = f[1]
                if not manager.getByName(obj.name):
                    manager.register(obj)
        return found


    def initSamples(self):
        manager = self.sample_manager
        # find all available samples
        dirs = manager.getSearchDirs(self, ("sound", os.path.join("sound", "extra")))
        ##print dirs
        ext_re = re.compile(r"\.((wav))$", re.I)
        self.initResource(manager, dirs, ext_re, Sample)


    def initMusic(self):
        manager = self.music_manager
        # find all available music songs
        dirs = manager.getSearchDirs(self, "music-*", "PYSOL_MUSIC")
        ##print dirs
        ext_re = re.compile(self.audio.EXTENSIONS)
        self.initResource(manager, dirs, ext_re, Music)


