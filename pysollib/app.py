#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
#  Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
#  Copyright (C) 2003 Mt. Hood Playing Card Co.
#  Copyright (C) 2005-2009 Skomoroh
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##


import os
import re
import sys
import traceback
from pickle import UnpicklingError

import pysollib.app_stat
from pysollib.actions import PysolMenubar
from pysollib.actions import PysolToolbar
from pysollib.app_stat_result import GameStatResult
from pysollib.app_statistics import Statistics
from pysollib.cardsetparser import read_cardset_config
from pysollib.gamedb import GAME_DB, GI, loadGame
from pysollib.help import destroy_help_html, help_about
from pysollib.images import Images, SubsampledImages
from pysollib.mfxutil import Struct, destruct
from pysollib.mfxutil import USE_PIL
from pysollib.mfxutil import getprefdir, getusername
from pysollib.mfxutil import latin1_normalize, print_err
from pysollib.mfxutil import pickle, unpickle
from pysollib.mygettext import _
from pysollib.options import Options
from pysollib.pysolrandom import PysolRandom, construct_random
from pysollib.pysoltk import HTMLViewer
from pysollib.pysoltk import MfxDialog, MfxExceptionDialog, MfxMessageDialog
from pysollib.pysoltk import MfxScrolledCanvas, TclError
from pysollib.pysoltk import PysolProgressBar
from pysollib.pysoltk import PysolStatusbar
from pysollib.pysoltk import SelectCardsetDialogWithPreview
from pysollib.pysoltk import SelectDialogTreeData
from pysollib.pysoltk import destroy_find_card_dialog
from pysollib.pysoltk import loadImage, wm_withdraw
from pysollib.resource import CSI, CardsetManager
from pysollib.resource import Music, MusicManager
from pysollib.resource import Sample, SampleManager
from pysollib.resource import Tile, TileManager
from pysollib.settings import DEBUG
from pysollib.settings import PACKAGE, VERSION_TUPLE  # , WIN_SYSTEM
from pysollib.settings import TOOLKIT
from pysollib.util import IMAGE_EXTENSIONS
from pysollib.winsystems import TkSettings
if TOOLKIT == 'tk':
    from pysollib.ui.tktile.solverdialog import destroy_solver_dialog
else:
    from pysollib.pysoltk import destroy_solver_dialog
if TOOLKIT == 'kivy':
    import logging

_GameStatResult = GameStatResult
GameStat = pysollib.app_stat.GameStat


# ************************************************************************
# * Application
# * This is the glue between the toplevel window and a Game.
# * Also handles all global resources.
# ************************************************************************

image_ext_re_str = "(" + "|".join(
    ["(?:\\" + e + ")" for e in IMAGE_EXTENSIONS]) + ")$"
image_ext_re = re.compile(image_ext_re_str, re.I | re.U)


class Application:
    def __init__(self):
        self.gdb = GAME_DB
        self.opt = Options()
        self.startup_opt = self.opt.copy()
        self.stats = Statistics()
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
            demo=[],                  # demo logos
            pause=[],                 # pause logos
            logos=[],
            redeal=[],
        )
        # self.progress_bg = None
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
            progress=None,            # progress bar
        )
        # directory names
        config = os.path.normpath(getprefdir(PACKAGE))
        self.dn = Struct(
            config=config,
            plugins=os.path.join(config, "plugins"),
            savegames=os.path.join(config, "savegames"),
            maint=os.path.join(config, "maint"),          # debug
        )
        for k, v in self.dn.__dict__.items():
            #             if os.name == "nt":
            #                 v = os.path.normcase(v)
            v = os.path.normpath(v)
            self.dn.__dict__[k] = v
        # file names
        self.fn = Struct(
            opt=os.path.join(self.dn.config, "options.dat"),
            opt_cfg=os.path.join(self.dn.config, "options.cfg"),
            stats=os.path.join(self.dn.config, "statistics.dat"),
            holdgame=os.path.join(self.dn.config, "holdgame.dat"),
            comments=os.path.join(self.dn.config, "comments.dat"),
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
            id=0,                     # start this game
            random=None,              # use this random generator
            loadedgame=None,          # data for loaded game
            startdemo=0,              # start demo ?
            cardset=None,             # use this cardset
            holdgame=0,               # hold this game on exit ?
            bookmark=None,            # goto this bookmark (load new cardset)
        )
        self.commandline = Struct(
            loadgame=None,            # load a game ?
            game=None,
            gameid=None,
            deal=None,
        )
        self.demo_counter = 0

    # the PySol mainloop
    def mainloop(self):
        try:
            approc = self.mainproc()  # setup process
            approc.send(None)				# and go
        except StopIteration:
            pass

    def gameproc(self):
        while True:
            logging.info('App: gameproc waiting for game to start')
            (id_, random) = yield
            logging.info('App: game started {},{}'.format(id_, random))
            self.runGame(id_, random)

    def _load_held_or_saved_game(self, tmpgame):
        """docstring for _load_held_or_saved_game"""
        if self.opt.game_holded > 0 and not self.nextgame.loadedgame:
            game = None
            try:
                game = tmpgame._loadGame(self.fn.holdgame, self)
            except Exception:
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

    def _main_loop(self):
        """docstring for _main_loop"""
        try:
            # this is the mainloop
            while 1:
                assert self.cardset is not None
                id_, random = self.nextgame.id, self.nextgame.random
                self.nextgame.id, self.nextgame.random = 0, None
                try:
                    if TOOLKIT == 'kivy':
                        self.gproc.send((id_, random))
                        logging.info('App: sent for game to start')
                        yield
                        logging.info('App: game proc stopped')
                    else:
                        self.runGame(id_, random)
                except Exception:
                    # try Klondike if current game fails
                    if id_ == 2:
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
                    except Exception:
                        traceback.print_exc()
                        pass
                self.wm_save_state()
                # save game geometry
                geom = (self.canvas.winfo_width(), self.canvas.winfo_height())
                if self.opt.save_games_geometry and not self.opt.wm_maximized:
                    self.opt.games_geometry[self.game.id] = geom
                self.opt.game_geometry = geom
                self.freeGame()
                #
                if self.nextgame.id <= 0:
                    break
                # load new cardset
                if self.nextgame.cardset is not self.cardset:
                    self.loadCardset(
                        self.nextgame.cardset, id=self.nextgame.id,
                        update=7+256)
                else:
                    self.requestCompatibleCardsetType(self.nextgame.id)

        except Exception:
            traceback.print_exc()
            pass

        finally:
            # hide main window
            self.wm_withdraw()
            #
            destroy_help_html()
            destroy_find_card_dialog()
            destroy_solver_dialog()
            # update options
            self.opt.last_gameid = id_
            # save options
            try:
                self.saveOptions()
            except Exception:
                traceback.print_exc()
                pass
            # save statistics
            try:
                self.saveStatistics()
            except Exception:
                traceback.print_exc()
                pass
            # shut down audio
            try:
                self.audio.destroy()
            except Exception:
                traceback.print_exc()
                pass
            if TOOLKIT == 'kivy':
                self.top.quit()
                while True:
                    logging.info('App: mainloop end position')
                    yield

    def mainproc(self):
        # copy startup options
        self.startup_opt = self.opt.copy()
        # try to load statistics
        try:
            self.loadStatistics()
        except Exception:
            traceback.print_exc()
            pass
        # startup information
        if self.getGameClass(self.opt.last_gameid):
            self.nextgame.id = self.opt.last_gameid
        # load a holded or saved game
        tmpgame = self.constructGame(self.gdb.getGamesIdSortedByName()[0])
        self._load_held_or_saved_game(tmpgame)
        if not self.nextgame.loadedgame:
            if self.commandline.loadgame:
                try:
                    self.nextgame.loadedgame = tmpgame._loadGame(
                        self.commandline.loadgame, self)
                    self.nextgame.loadedgame.gstats.holded = 0
                except Exception:
                    traceback.print_exc()
                    self.nextgame.loadedgame = None
            elif self.commandline.game is not None:
                gameid = self.gdb.getGameByName(self.commandline.game)
                if gameid is None:
                    print_err(_("can't find game: %(game)s") % {
                        'game': self.commandline.game})
                    sys.exit(-1)
                else:
                    self.nextgame.id = gameid
                    deal = self.commandline.deal
                    self.nextgame.random = \
                        None if deal is None else construct_random(deal)
            elif self.commandline.gameid is not None:
                self.nextgame.id, self.nextgame.random = \
                    self.commandline.gameid, None
        self.opt.game_holded = 0
        tmpgame.destruct()
        destruct(tmpgame)
        tmpgame = None
        #
        # widgets
        #
        # create the menubar
        if self.intro.progress:
            self.intro.progress.update(step=1)
        self.menubar = PysolMenubar(self, self.top,
                                    progress=self.intro.progress)
        # create the statusbar(s)
        self.statusbar = PysolStatusbar(self.top)
        self.statusbar.show(self.opt.statusbar)
        for w, v in self.opt.statusbar_vars.items():
            self.statusbar.config(w, v)
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
        dirname = self.getToolbarImagesDir()
        self.toolbar = PysolToolbar(self.top, self.menubar, dir=dirname,
                                    size=self.opt.toolbar_size,
                                    relief=self.opt.toolbar_relief,
                                    compound=self.opt.toolbar_compound)
        self.toolbar.show(self.opt.toolbar)
        if TOOLKIT == 'tk':
            for w, v in self.opt.toolbar_vars.items():
                self.toolbar.config(w, v)
        #
        if self.intro.progress:
            self.intro.progress.update(step=1)
        #

        if TOOLKIT == 'kivy':
            self.gproc = self.gameproc()
            self.gproc.send(None)
        return self._main_loop()

    def runGame(self, id_, random=None):
        self.top.connectApp(self)
        # create game instance
        g = self.getGameClass(id_)
        if g is None:
            id_ = 2          # start Klondike as default game
            random = None
            g = self.getGameClass(id_)
            if g is None:
                # start first available game
                id_ = self.gdb.getGamesIdSortedByName()[0]
                g = self.getGameClass(id_)
        gi = self.getGameInfo(id_)
        assert gi is not None and gi.id == id_
        self.game = self.constructGame(id_)
        self.gdb.setSelected(id_)
        self.game.busy = 1
        # create stacks and layout
        self.game.create(self)
        # connect with game
        self.menubar.connectGame(self.game)
        if self.toolbar:  # ~
            self.toolbar.connectGame(self.game)
        self.game.updateStatus(player=self.opt.player)
        # update "Recent games" menubar entry
        if id_ in self.opt.recent_gameid:
            self.opt.recent_gameid.remove(id_)
        self.opt.recent_gameid.insert(0, id_)
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
            # print "wm_save_state", s
            if s == "zoomed":  # Windows only
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
        dirname = os.path.join("images", "logos")
        for f in ("joker07_40_774",
                  "joker08_40_774",
                  "joker07_50_774",
                  "joker08_50_774",
                  "joker11_100_774",
                  "joker10_100",):
            self.gimages.logos.append(self.dataloader.findImage(f, dirname))
        # if WIN_SYSTEM == 'win32':
        #     dirname = os.path.join('images', 'dialog', 'default')
        # else:
        #     dirname = os.path.join('images', 'dialog', 'bluecurve')
        dirname = os.path.join('images', 'dialog', 'remix')
        for f in ('error', 'info', 'question', 'warning'):
            fn = self.dataloader.findImage(f, dirname)
            im = loadImage(fn)
            MfxMessageDialog.img[f] = im

        # load button images
        if 0 and TOOLKIT == 'tk':
            dirname = os.path.join('images', 'buttons', 'bluecurve')
            for n, f in (
                (_('&OK'), 'ok'),
                (_('&Cancel'), 'cancel'),
                (_('&New game'), 'new'),
            ):
                fn = self.dataloader.findImage(f, dirname)
                im = loadImage(fn)
                MfxDialog.button_img[n] = im

    def loadImages2(self):
        # load canvas images
        dirname = "images"
        # for f in ("noredeal", "redeal",):
        for f in ("stopsign", "redeal",):
            self.gimages.redeal.append(self.dataloader.findImage(f, dirname))
        dirname = os.path.join("images", "demo")
        for f in ("demo01", "demo02", "demo03", "demo04", "demo05",):
            self.gimages.demo.append(self.dataloader.findImage(f, dirname))
        dirname = os.path.join("images", "pause")
        for f in ("pause01", "pause02", "pause03",):
            self.gimages.pause.append(self.dataloader.findImage(f, dirname))
        # dirname = os.path.join("images", "stats")
        # for f in ("barchart",):
        #     self.gimages.stats.append(self.dataloader.findImage(f, dirname))

    def loadImages3(self):
        # load treeview images
        SelectDialogTreeData.img = []
        dirname = os.path.join('images', 'tree')
        for f in ('folder', 'openfolder', 'node', 'emptynode'):
            fn = self.dataloader.findImage(f, dirname)
            im = loadImage(fn)
            SelectDialogTreeData.img.append(im)

        # load htmlviewer images
        dirname = os.path.join('images', 'htmlviewer')
        fn = self.dataloader.findImage('disk', dirname)
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
        d = os.path.join(self.dataloader.dir, 'images', *dirs)
        if check:
            if os.path.exists(d):
                return d
            return None
        return d

    def getFindCardImagesDir(self):
        return self._getImagesDir('cards')

    def getToolbarImagesDir(self):
        if self.opt.toolbar_size == 2:
            size = 'xlarge'
        elif self.opt.toolbar_size == 1:
            size = 'large'
        else:
            size = 'small'
        style = self.opt.toolbar_style
        if TOOLKIT == 'kivy':
            size = 'xlarge'
            style = 'remix light'
        d = self._getImagesDir('toolbar', style, size)
        if d:
            return d
        return self._getImagesDir('toolbar', 'default', size, check=False)

    def setTile(self, i, scaling=-1, force=0):
        if scaling == -1:
            scaling = self.opt.tabletile_scale_method
        if self.scrolled_canvas.setTile(self, i, scaling, force):
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
    # search logic
    #

    def checkSearchString(self, search_string, check_string):
        terms = search_string.split()
        if len(terms) == 0:
            return True
        for term in terms:
            if term.upper() not in check_string.upper():
                return False
        return True

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
        # from pprint import pprint; pprint(self.opt.cardset)

    def loadCardset(self, cs, id=0, update=7, progress=None,
                    tocache=False, noprogress=False):
        # print 'loadCardset', cs.ident
        r = 0
        if cs is None or cs.error:
            return 0
        if cs is self.cardset:
            if not tocache:
                self.updateCardset(id, update=update)
            return 1
        # cache carsets
        # self.cardsets_cache:
        #   key: Cardset.type
        #   value: (Cardset.ident, Images, SubsampledImages)
        c = self.cardsets_cache.get(cs.type)
        if c and c[0] == cs.ident:
            # print 'load from cache', c
            self.images, self.subsampled_images = c[1], c[2]
            if not tocache:
                self.updateCardset(id, update=update)
                if self.menubar is not None:
                    self.menubar.updateBackgroundImagesMenu()
            return 1
        #
        if progress is None and not noprogress:
            self.wm_save_state()
            self.wm_withdraw()
            title = _("Loading cardset %s...") % cs.name
            color = self.opt.colors['table']
            if self.tabletile_index > 0:
                color = "#008200"
            progress = PysolProgressBar(self, self.top, title=title,
                                        color=color,
                                        images=self.progress_images)
        images = Images(self.dataloader, cs)
        images.cardset_bottoms = self.opt.use_cardset_bottoms
        try:
            if not images.load(app=self, progress=progress):
                raise Exception("Invalid or damaged cardset")
            simages = SubsampledImages(images)
            if tocache:
                simages.setNegative(self.opt.negative_bottom)
            # The save cardsets option is deprecated, and its existence
            # directly conflicts with the ability to allow previews of
            # other cardset types.
            # if self.opt.save_cardsets:
            c = self.cardsets_cache.get(cs.type)
            if c:
                # c[1].destruct()
                destruct(c[1])
            self.cardsets_cache[cs.type] = (cs.ident, images, simages)
            if not tocache:
                # elif self.images is not None:
                #    # self.images.destruct()
                #    destruct(self.images)
                #
                if self.cardset:
                    if self.cardset.ident != cs.ident:
                        if self.cardset.type == cs.type:
                            # clear saved games geometry
                            self.opt.games_geometry = {}
                # update
                self.images = images
                self.subsampled_images = simages
                self.updateCardset(id, update=update)
            r = 1
        except (Exception, TclError, UnpicklingError) as ex:
            traceback.print_exc()
            cs.error = 1
            # restore settings
            self.nextgame.cardset = self.cardset
            if self.cardset:
                self.cardset_manager.setSelected(self.cardset.index)
            # images.destruct()
            destruct(images)
            MfxExceptionDialog(
                self.top, ex, title=_("Cardset load error"),
                text=_("Error while loading cardset"))
        self.intro.progress = progress
        if r and not tocache and self.menubar is not None:
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
                               # CSI.TYPE_TAROCK,
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
        elif gc == GI.GC_MATCHING:
            t0 = "Matching"
            if cs.ncards < (gi.ncards / 2):    # not enough cards
                t1 = t0
        else:
            # we should not come here
            t0 = t1 = "Unknown"
        return t0, t1

    def getCompatibleCardset(self, gi, cs, trychange=True):
        if gi is None:
            return cs, 1, None
        t = self.checkCompatibleCardsetType(gi, cs)
        # try current
        if cs:
            if not t[1]:
                return cs, 1, t
        if trychange:
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
                    return cs, flag, t
        # ask
        return None, 0, t

    def requestCompatibleCardsetType(self, id):
        gi = self.getGameInfo(id)
        #
        cs, cs_update_flag, t = self.getCompatibleCardset(gi, self.cardset)
        if cs is self.cardset:
            return 0
        if cs is not None:
            self.loadCardset(cs, update=1)
            return 1

        self.requestCompatibleCardsetTypeDialog(self.cardset, gi, t)

        cs = self.__selectCardsetDialog(t)
        if cs is None:
            return -1
        self.loadCardset(cs, id=id)
        return 1

    def requestCompatibleCardsetTypeDialog(self, cardset, gi, t):
        MfxMessageDialog(
            self.top, title=_("Incompatible cardset"),
            bitmap="warning",
            text=_('''The currently selected cardset %(cardset)s
        is not compatible with the game
        %(game)s

        Please select a %(correct_type)s type cardset.
        ''') % {'cardset': cardset.name, 'game': gi.name,
                'correct_type': t[0]}, strings=(_("&OK"),), default=0)

    def selectCardset(self, title, key):
        d = SelectCardsetDialogWithPreview(
            self.top, title=title, app=self,
            manager=self.cardset_manager, key=key)
        cs = self.cardset_manager.get(d.key)
        if d.status != 0 or d.button != 0 or d.key < 0 or cs is None:
            return None
        changed = False
        if USE_PIL:
            if (self.opt.scale_x, self.opt.scale_y,
                self.opt.auto_scale, self.opt.spread_stacks,
                self.opt.preserve_aspect_ratio) != \
                d.scale_values or \
                    (cs.CARD_XOFFSET, cs.CARD_YOFFSET) != d.cardset_values:
                changed = True
        if d.key == self.cardset.index and not changed:
            return None
        if USE_PIL:
            (self.opt.scale_x,
             self.opt.scale_y,
             self.opt.auto_scale,
             self.opt.spread_stacks,
             self.opt.preserve_aspect_ratio) = d.scale_values
            if not self.opt.auto_scale:
                self.images.resize(self.opt.scale_x, self.opt.scale_y,
                                   resample=self.opt.resampling)
            if d.cardset_values:
                cs.CARD_XOFFSET, cs.CARD_YOFFSET = d.cardset_values
                self.opt.offsets[cs.ident] = d.cardset_values
                self.images.setOffsets()
        return cs

    def __selectCardsetDialog(self, t):
        cs = self.selectCardset(
            _("Please select a %s type cardset") % t[0],
            self.cardset.index)
        return cs

    #
    # load & save options, and statistics
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
            except Exception:
                pass
        self.opt.load(self.fn.opt_cfg)
        self.opt.setConstants()

    def loadStatistics(self):
        if not os.path.exists(self.fn.stats):
            return
        stats = unpickle(self.fn.stats)
        if stats:
            # print "loaded:", stats.__dict__
            self.stats.__dict__.update(stats.__dict__)
        # start a new session
        self.stats.session_games = {}
        self.stats.session_balance = {}
        self.stats.gameid_balance = 0

    def __saveObject(self, obj, fn):
        obj.version_tuple = VERSION_TUPLE
        obj.saved += 1
        pickle(obj, fn, protocol=-1)

    def saveOptions(self):
        self.opt.save(self.fn.opt_cfg)

    def saveStatistics(self):
        self.__saveObject(self.stats, self.fn.stats)

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
        if player == '':
            player = self.opt.player

        def _key(a):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            return wa+la
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(key=_key)
        return games[::-1]

    def getGamesIdSortedByWon(self, player=''):
        if player == '':
            player = self.opt.player

        def _key(a):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            return wa
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(key=_key)
        return games[::-1]

    def getGamesIdSortedByLost(self, player=''):
        if player == '':
            player = self.opt.player

        def _key(a):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            return la
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(key=_key)
        return games[::-1]

    def getGamesIdSortedByPercent(self, player=''):
        if player == '':
            player = self.opt.player

        def _key(a):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            return float(wa)/(1 if wa+la == 0 else wa+la)
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(key=_key)
        return games[::-1]

    def getGamesIdSortedByPlayingTime(self, player=''):
        if player == '':
            player = self.opt.player

        def _key(a):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            return ta
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(key=_key)
        return games[::-1]

    def getGamesIdSortedByMoves(self, player=''):
        if player == '':
            player = self.opt.player

        def _key(a):
            wa, la, ta, ma = self.stats.getFullStats(player, a)
            return ma
        games = list(self.gdb.getGamesIdSortedByName())
        games.sort(key=_key)
        return games[::-1]

    def getGameInfo(self, id):
        return self.gdb.get(id)

    def getGameClass(self, id):
        gi = self.gdb.get(id)
        if gi is None:
            return None
        return gi.gameclass

    def getGameTitleName(self, id):
        gi = self.gdb.get(id)
        if gi is None:
            return None
        return gi.name

    def getGameMenuitemName(self, id):
        gi = self.gdb.get(id)
        if gi is None:
            return None
        return gi.short_name

    def getGameRulesFilename(self, id):
        gi = self.gdb.get(id)
        if gi is None:
            return None
        if gi.rules_filename is not None:
            return gi.rules_filename
        n = latin1_normalize(gi.en_name) + '.html'        # english name
        f = os.path.join(self.dataloader.dir, "html", "rules", n)
        if not os.path.exists(f):
            n = ''
        gi.rules_filename = n    # cache the filename for next use
        return n

    def getGameSaveName(self, id):
        if os.path.supports_unicode_filenames:
            return self.getGameTitleName(id)
        n = self.gdb.get(id).en_name                  # english name
        if not n:
            return None
        return re.sub(r"[\s]", "_", latin1_normalize(n))

    def _choice(self, lst):
        return self.miscrandom.choice(lst)

    def chooseRandomOutOfGames(self, games):
        return self._choice(games)

    def getRandomGameId(self):
        return self._choice(self.gdb.getGamesIdSortedById())

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

    def loadPlugins(self, dirname):
        for name in self._my_list_dir(dirname):
            m = re.search(r"^(.+)\.py$", name)
            n = os.path.join(dirname, name)
            if m and os.path.isfile(n):
                try:
                    loadGame(m.group(1), n)
                except Exception as ex:
                    if DEBUG:
                        traceback.print_exc()
                    print_err(_("error loading plugin %(file)s: %(err)s") %
                              {'file': n, 'err': ex})

    #
    # init cardsets
    #

    # read & parse a cardset config.txt file - see class Cardset in resource.py
    def _readCardsetConfig(self, dirname, filename):
        cs = read_cardset_config(dirname, filename)
        # set offsets from options.cfg
        if cs.ident in self.opt.offsets:
            cs.CARD_XOFFSET, cs.CARD_YOFFSET = self.opt.offsets[cs.ident]
        return cs

    def initCardsets(self):
        """Load all valid cardset config.txt files and ignore invalid ones.
        """
        screendepth = self.top.winfo_screendepth()
        manager = self.cardset_manager
        # find all available cardsets
        dirs = manager.getSearchDirs(self, ("cardsets", ""), "PYSOL_CARDSETS")
        if DEBUG:
            dirs += manager.getSearchDirs(self, "cardsets-*")
        found = []
        found_names = []  # (to check for duplicates)
        for dirname in dirs:
            try:
                subdirs = [os.path.join(dirname, subdir)
                           for subdir in os.listdir(dirname)
                           if subdir.startswith('cardset-')]
            except EnvironmentError:
                traceback.print_exc()
                continue
            subdirs.sort()
            for d in subdirs:
                config_txt_path = os.path.join(d, "config.txt")
                if not os.path.isfile(config_txt_path):
                    continue
                try:
                    cs = self._readCardsetConfig(d, config_txt_path)
                except Exception:
                    traceback.print_exc()
                    cs = None
                if not cs:
                    print_err('failed to parse cardset file: %s'
                              % config_txt_path)
                    continue
                back = cs.backnames[cs.backindex]
                back_im_path = os.path.join(d, back)
                shade_im_path = os.path.join(d, "shade" + cs.ext)
                if (cs.name not in found_names and
                        cs.ext in IMAGE_EXTENSIONS and
                        cs.CARDD <= screendepth and
                        os.path.isfile(back_im_path) and
                        os.path.isfile(shade_im_path)):
                    found.append(cs)
                    found_names.append(cs.name)

        # register cardsets
        for obj in found:
            if not manager.getByName(obj.name):
                manager.register(obj)
                # print obj.index, obj.name

    #
    # init tiles
    #
    def _init_tiles_process_dir(self, dirname, found, t):
        """docstring for _init_tiles_process_die"""
        names = []
        if dirname and os.path.isdir(dirname):
            names = os.listdir(dirname)
        for name in names:
            if not name or not image_ext_re.search(name):
                continue
            f = os.path.join(dirname, name)
            if not os.path.isfile(f):
                continue
            tile = Tile()
            tile.filename = f
            n = image_ext_re.sub("", name)
            if os.path.split(dirname)[-1] == 'stretch':
                tile.stretch = 1
            if os.path.split(dirname)[-1] == 'save-aspect':
                tile.stretch = 1
                tile.save_aspect = 1
            # n = re.sub("[-_]", " ", n)
            n = n.replace('_', ' ')
            tile.name = n
            key = n.lower()
            if key not in t:
                t.add(key)
                found.append((n, tile))

    def initTiles(self):
        manager = self.tabletile_manager
        # find all available tiles
        dirs = manager.getSearchDirs(
            self,
            ("tiles-*",
                os.path.join("tiles", "stretch"),
                os.path.join("tiles", "save-aspect")),
            "PYSOL_TILES")
        # print dirs
        found, t = [], set()
        for dirname in dirs:
            try:
                self._init_tiles_process_dir(dirname, found, t)
            except EnvironmentError:
                pass
        # register tiles
        found.sort()
        for f in found:
            obj = f[1]
            if not manager.getByName(obj.name):
                manager.register(obj)

    def _my_list_dir(self, dirname):
        """docstring for _my_list_dir"""
        if dirname and os.path.isdir(dirname):
            names = os.listdir(dirname)
            names = list(map(os.path.normcase, names))
            names.sort()
            return names
        else:
            return []

    #
    # init samples / music
    #

    def initResource(self, manager, dirs, ext_re, Resource_Class):
        found, t = [], set()
        for dirname in dirs:
            dirname = dirname.strip()
            if dirname:
                dirname = os.path.normpath(dirname)
            try:
                for name in self._my_list_dir(dirname):
                    if not name or not ext_re.search(name):
                        continue
                    f = os.path.join(dirname, name)
                    f = os.path.normpath(f)
                    if not os.path.isfile(f):
                        continue
                    obj = Resource_Class()
                    obj.filename = f
                    n = ext_re.sub("", name.strip())
                    obj.name = n
                    key = n.lower()
                    if key not in t:
                        t.add(key)
                        found.append((n, obj))
            except EnvironmentError:
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
        dirs = manager.getSearchDirs(
            self, ("sound", os.path.join("sound", "extra")))
        # print dirs
        ext_re = re.compile(r"\.((wav))$", re.I)
        self.initResource(manager, dirs, ext_re, Sample)

    def initMusic(self):
        music_manager = self.music_manager
        # find all available music songs
        dirs = music_manager.getSearchDirs(self, "music-*", "PYSOL_MUSIC")
        # print('dirs =', dirs)
        ext_re = re.compile(self.audio.EXTENSIONS)
        self.initResource(music_manager, dirs, ext_re, Music)
