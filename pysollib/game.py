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
import time
import math
import traceback
from gettext import ungettext
from cStringIO import StringIO

# PySol imports
from mfxutil import Pickler, Unpickler, UnpicklingError
from mfxutil import Image, ImageTk
from mfxutil import destruct, Struct, SubclassResponsibility
from mfxutil import uclock, usleep
from mfxutil import format_time, print_err
from settings import PACKAGE, TITLE, TOOLKIT, TOP_TITLE
from settings import VERSION, VERSION_TUPLE
from settings import DEBUG
from gamedb import GI
from pysolrandom import PysolRandom, LCRandom31
from pysoltk import EVENT_HANDLED, EVENT_PROPAGATE
from pysoltk import CURSOR_WATCH
from pysoltk import bind, wm_map
from pysoltk import after, after_idle, after_cancel
from pysoltk import MfxMessageDialog, MfxExceptionDialog
from pysoltk import MfxCanvasText, MfxCanvasLine, MfxCanvasRectangle
from pysoltk import Card
from pysoltk import reset_solver_dialog
from move import AMoveMove, AFlipMove, AFlipAndMoveMove
from move import ASingleFlipMove, ATurnStackMove
from move import ANextRoundMove, ASaveSeedMove, AShuffleStackMove
from move import AUpdateStackMove, AFlipAllMove, ASaveStateMove
from move import ASingleCardMove
from hint import DefaultHint
from help import help_about

PLAY_TIME_TIMEOUT = 200

# ************************************************************************
# * Base class for all solitaire games
# *
# * Handles:
# *   load/save
# *   undo/redo (using a move history)
# *   hints/demo
# ************************************************************************

class Game:
    # for self.gstats.updated
    U_PLAY       =  0
    U_WON        = -2
    U_LOST       = -3
    U_PERFECT    = -4

    # for self.moves.state
    S_INIT = 0x00
    S_DEAL = 0x10
    S_FILL = 0x20
    S_RESTORE = 0x30
    S_PLAY = 0x40
    S_UNDO = 0x50
    S_REDO = 0x60

    # for loading and saving - subclasses should override if
    # the format for a saved game changed (see also canLoadGame())
    GAME_VERSION = 1


    #
    # game construction
    #

    # only basic initialization here
    def __init__(self, gameinfo):
        self.preview = 0
        self.random = None
        self.gameinfo = gameinfo
        self.id = gameinfo.id
        assert self.id > 0
        self.busy = 0
        self.pause = False
        self.finished = False
        self.version = VERSION
        self.version_tuple = VERSION_TUPLE
        self.cards = []
        self.stackmap = {}              # dict with (x,y) tuples as key
        self.allstacks = []
        self.sn_groups = []  # snapshot groups; list of list of similar stacks
        self.snapshots = []
        self.failed_snapshots = []
        self.stackdesc_list = []
        self.demo_logo = None
        self.pause_logo = None
        self.s = Struct(                # stacks
            talon = None,
            waste = None,
            foundations = [],
            rows = [],
            reserves = [],
            internals = [],
        )
        self.sg = Struct(               # stack-groups
            openstacks = [],            #   for getClosestStack(): only on these stacks the player can place a card
            talonstacks = [],           #   for Hint
            dropstacks = [],            #   for Hint & getAutoStacks()
            reservestacks = [],         #   for Hint
##            hint = Struct(),            #   extra info for class Hint
            hp_stacks = [],             #   for getHightlightPilesStacks()
        )
        self.regions = Struct(          # for getClosestStack()
            # set by optimizeRegions():
            info = [],                  #   list of tuples(stacks, rect)
            remaining = [],             #   list of stacks in no region
            #
            data = [],                  #   raw data
        )
        self.event_handled = False      # if click event handled by Stack (???)
        self.reset()

    # main constructor
    def create(self, app):
        old_busy = self.busy
        self.__createCommon(app)
        self.setCursor(cursor=CURSOR_WATCH)
        #print 'gameid:', self.id
        self.top.wm_title(TITLE + " - " + self.getTitleName())
        self.top.wm_iconname(TITLE + " - " + self.getTitleName())
        # create the game
        if self.app.intro.progress: self.app.intro.progress.update(step=1)
        self.createGame()
        # set some defaults
        self.sg.openstacks = [s for s in self.sg.openstacks
                              if s.cap.max_accept >= s.cap.min_accept]
        self.sg.hp_stacks = [s for s in self.sg.dropstacks
                             if s.cap.max_move >= 2]
        self.createSnGroups()
        # convert stackgroups to tuples (speed)
        self.allstacks = tuple(self.allstacks)
        self.s.foundations = tuple(self.s.foundations)
        self.s.rows = tuple(self.s.rows)
        self.s.reserves = tuple(self.s.reserves)
        self.s.internals = tuple(self.s.internals)
        self.sg.openstacks = tuple(self.sg.openstacks)
        self.sg.talonstacks = tuple(self.sg.talonstacks)
        self.sg.dropstacks = tuple(self.sg.dropstacks)
        self.sg.reservestacks = tuple(self.sg.reservestacks)
        self.sg.hp_stacks = tuple(self.sg.hp_stacks)
        # init the stack view
        for stack in self.allstacks:
            stack.prepareStack()
            stack.assertStack()
        if self.s.talon:
            assert hasattr(self.s.talon, "round")
            assert hasattr(self.s.talon, "max_rounds")
        if DEBUG:
            self._checkGame()
        # optimize regions
        self.optimizeRegions()
        # create cards
        if not self.cards:
            self.cards = self.createCards(progress=self.app.intro.progress)
        self.initBindings()
        ##self.top.bind('<ButtonPress>', self.top._sleepEvent)
        ##self.top.bind('<3>', self.top._sleepEvent)
        # update display properties
        self.canvas.busy = True
        self.canvas.setInitialSize(self.width, self.height)
        if self.app.opt.save_games_geometry and \
               self.id in self.app.opt.games_geometry:
            # restore game geometry
            w, h = self.app.opt.games_geometry[self.id]
            self.canvas.config(width=w, height=h)
        self.top.wm_geometry("")        # cancel user-specified geometry
        self.top.update_idletasks()
        self.canvas.busy = False
        if DEBUG >= 4:
            MfxCanvasRectangle(self.canvas, 0, 0, self.width, self.height,
                               width=2, fill=None, outline='green')
        #
        self.stats.update_time = time.time()
        self.busy = old_busy
        self.showHelp()                 # just in case
        hint_class = self.getHintClass()
        if hint_class is not None:
            self.Stuck_Class = hint_class(self, 0)
        ##self.reallocateStacks()


    def _checkGame(self):
        class_name = self.__class__.__name__
        if self.s.foundations:
            ncards = 0
            for stack in self.s.foundations:
                ncards += stack.cap.max_cards
            if ncards != self.gameinfo.ncards:
                print_err('invalid sum of foundations.max_cards: '
                          '%s: %s %s' % (class_name, ncards, self.gameinfo.ncards),
                          2)
        if self.s.rows:
            from stack import AC_RowStack, UD_AC_RowStack, \
                 SS_RowStack, UD_SS_RowStack, \
                 RK_RowStack, UD_RK_RowStack, \
                 Spider_AC_RowStack, Spider_SS_RowStack
            r = self.s.rows[0]
            for c, f in (
                ((Spider_AC_RowStack, Spider_SS_RowStack),
                 (self._shallHighlightMatch_RK,
                  self._shallHighlightMatch_RKW)),
                ((AC_RowStack, UD_AC_RowStack),
                 (self._shallHighlightMatch_AC,
                  self._shallHighlightMatch_ACW)),
                ((SS_RowStack, UD_SS_RowStack),
                 (self._shallHighlightMatch_SS,
                  self._shallHighlightMatch_SSW)),
                ((RK_RowStack, UD_RK_RowStack),
                 (self._shallHighlightMatch_RK,
                  self._shallHighlightMatch_RKW)),):
                if isinstance(r, c):
                    if self.shallHighlightMatch not in f:
                        print_err('shallHighlightMatch is not valid: '
                                  ' %s, %s' % (class_name, r.__class__), 2)
                    if r.cap.mod == 13 and self.shallHighlightMatch != f[1]:
                        print_err('shallHighlightMatch is not valid (wrap): '
                                  ' %s, %s' % (class_name, r.__class__), 2)
                    break
        if self.s.talon.max_rounds > 1 and \
               self.s.talon.texts.rounds is None:
            print_err('max_rounds > 1, but talon.texts.rounds is None: '
                      '%s' % class_name, 2)
        elif self.s.talon.max_rounds <= 1 and \
             self.s.talon.texts.rounds is not None:
            print_err('max_rounds <= 1, but talon.texts.rounds is not None: '
                      '%s' % class_name, 2)


    def initBindings(self):
        # note: a Game is only allowed to bind self.canvas and not to self.top
        ##bind(self.canvas, "<Double-1>", self.undoHandler)
        bind(self.canvas, "<1>", self.undoHandler)
        bind(self.canvas, "<2>", self.dropHandler)
        bind(self.canvas, "<3>", self.redoHandler)
        bind(self.canvas, '<Unmap>', self._unmapHandler)
        bind(self.canvas, '<Configure>', self.configureHandler, add=True)

    def __createCommon(self, app):
        self.busy = 1
        self.app = app
        self.top = app.top
        self.canvas = app.canvas
        self.filename = ""
        self.drag = Struct(
            event = None,               # current event
            timer = None,               # current event timer
            start_x = 0,                # X coord of initial drag event
            start_y = 0,                # Y coord of initial drag event
            stack = None,               #
            cards = [],                 #
            index = -1,                 #
            shadows = [],               # list of canvas images
            shade_stack = None,         # stack currently shaded
            shade_img = None,           # canvas image
            canshade_stacks = [],       # list of stacks already tested
            noshade_stacks = [],        #   for this drag
        )
        if self.gstats.start_player is None:
            self.gstats.start_player = self.app.opt.player
        # optional MfxCanvasText items
        self.texts = Struct(
            info = None,                # misc info text
            help = None,                # a static help text
            misc = None,                #
            score = None,               # for displaying the score
            base_rank = None,           # for displaying the base_rank
        )

    def createPreview(self, app):
        old_busy = self.busy
        self.__createCommon(app)
        self.preview = max(1, self.canvas.preview)
        # create game
        self.createGame()
        # set some defaults
        self.sg.openstacks = [s for s in self.sg.openstacks
                              if s.cap.max_accept >= s.cap.min_accept]
        self.sg.hp_stacks = [s for s in self.sg.dropstacks
                             if s.cap.max_move >= 2]
        # init the stack view
        for stack in self.allstacks:
            stack.prepareStack()
            stack.assertStack()
        # optimize regions
        self.optimizeRegions()
        # create cards
        self.cards = self.createCards()
        #
        self.canvas.setInitialSize(self.width, self.height)
        self.busy = old_busy

    def destruct(self):
        # help breaking circular references
        for obj in self.cards:
            destruct(obj)
        for obj in self.allstacks:
            obj.destruct()
            destruct(obj)

    # Do not destroy game structure (like stacks and cards) here !
    def reset(self, restart=0):
        self.filename = ""
        self.demo = None
        self.solver = None
        self.hints = Struct(
            list = None,                # list of hints for the current move
            index = -1,
            level = -1,
        )
        self.saveinfo = Struct(         # needed for saving a game
            stack_caps = [],
        )
        self.loadinfo = Struct(         # used when loading a game
            stacks = None,
            talon_round = 1,
            ncards = 0,
        )
        self.snapshots = []
        self.failed_snapshots = []
        # local statistics are reset on each game restart
        self.stats = Struct(
            hints = 0,                  # number of hints consumed
            highlight_piles = 0,        # number of highlight piles consumed
            highlight_cards = 0,        # number of highlight matching cards consumed
            highlight_samerank = 0,     # number of highlight same rank consumed
            undo_moves = 0,             # number of undos
            redo_moves = 0,             # number of redos
            total_moves = 0,            # number of total moves in this game
            player_moves = 0,           # number of moves
            demo_moves = 0,             # number of moves while in demo mode
            autoplay_moves = 0,         # number of moves
            quickplay_moves = 0,        # number of quickplay moves
            goto_bookmark_moves = 0,    # number of goto bookmark
            shuffle_moves = 0,          # number of shuffles (Mahjongg)
            demo_updated = 0,           # did this game already update the demo stats ?
            update_time = time.time(),  # for updateTime()
            elapsed_time = 0.0,
            pause_start_time = 0.0,
        )
        self.startMoves()
        if restart:
            return
        # global statistics survive a game restart
        self.gstats = Struct(
            holded = 0,                 # is this a holded game
            loaded = 0,                 # number of times this game was loaded
            saved = 0,                  # number of times this game was saved
            restarted = 0,              # number of times this game was restarted
            goto_bookmark_moves = 0,    # number of goto bookmark
            updated = self.U_PLAY,      # did this game already update the player stats ?
            start_time = time.time(),   # game start time
            total_elapsed_time = 0.0,
            start_player = None,
        )
        # global saveinfo survives a game restart
        self.gsaveinfo = Struct(
            bookmarks = {},
            comment = "",
        )
        # some vars for win animation
        self.win_animation = Struct(
            timer = None,
            images = [],
            tk_images = [],             # saved tk images
            saved_images = {},          # saved resampled images
            canvas_images = [],         # ids of canvas images
            frame_num = 0,              # number of the current frame
            width = 0,
            height = 0,
            )

    def getTitleName(self):
        return self.app.getGameTitleName(self.id)

    def getGameNumber(self, format):
        s = str(self.random)
        if format: return "#" + s
        return s

    # this is called from within createGame()
    def setSize(self, w, h):
        self.width, self.height = int(round(w)), int(round(h))

    def setCursor(self, cursor):
        if self.canvas:
            self.canvas.config(cursor=cursor)
            ##self.canvas.update_idletasks()
        #if self.app and self.app.toolbar:
        #    self.app.toolbar.setCursor(cursor=cursor)


    #
    # game creation
    #

    # start a new name
    def newGame(self, random=None, restart=0, autoplay=1):
        self.finished = False
        old_busy, self.busy = self.busy, 1
        self.setCursor(cursor=CURSOR_WATCH)
        self.stopWinAnimation()
        self.disableMenus()
        self.redealAnimation()
        self.reset(restart=restart)
        self.resetGame()
        self.createRandom(random)
        ##print self.random, self.random.__dict__
        self.shuffle()
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        for stack in self.allstacks:
            stack.updateText()
        self.updateText()
        self.updateStatus(player=self.app.opt.player,
                          gamenumber=self.getGameNumber(format=1),
                          moves=(0, 0),
                          stats=self.app.stats.getStats(self.app.opt.player, self.id),
                          stuck='')
        reset_solver_dialog()
        # unhide toplevel when we use a progress bar
        if not self.preview:
            wm_map(self.top, maximized=self.app.opt.wm_maximized)
            self.top.busyUpdate()
        if TOOLKIT == 'gtk':
            ## FIXME
            if self.top:
                self.top.update_idletasks()
                self.top.show_now()
        #
        self.stopSamples()
        # let's go
        self.moves.state = self.S_INIT
        self.startGame()
        if self.gameinfo.si.game_flags & GI.GT_OPEN:
            if self.s.talon:
                assert len(self.s.talon.cards) == 0
            for stack in self.allstacks:
                if stack.is_visible:
                    for c in stack.cards:
                        assert c.face_up
        self.startMoves()
        for stack in self.allstacks:
            stack.updateText()
        self.updateSnapshots()
        self.updateText()
        self.updateStatus(moves=(0, 0))
        self.updateMenus()
        self.stopSamples()
        if autoplay:
            self.autoPlay()
            self.stats.player_moves = 0
        self.setCursor(cursor=self.app.top_cursor)
        self.stats.update_time = time.time()
        if not self.preview:
            self.startPlayTimer()
        self.busy = old_busy

    # restore a loaded game (see load/save below)
    def restoreGame(self, game, reset=1):
        old_busy, self.busy = self.busy, 1
        if reset:
            self.reset()
        self.resetGame()
        # 1) copy loaded variables
        self.filename = game.filename
        self.version = game.version
        self.version_tuple = game.version_tuple
        self.random = game.random
        self.moves = game.moves
        self.stats = game.stats
        self.gstats = game.gstats
        # 2) copy extra save-/loadinfo
        self.saveinfo = game.saveinfo
        self.gsaveinfo = game.gsaveinfo
        self.s.talon.round = game.loadinfo.talon_round
        self.finished = game.finished
        self.snapshots = game.snapshots
        # 3) move cards to stacks
        assert len(self.allstacks) == len(game.loadinfo.stacks)
        old_state = game.moves.state
        game.moves.state = self.S_RESTORE
        for i in range(len(self.allstacks)):
            for t in game.loadinfo.stacks[i]:
                card_id, face_up = t
                card = self.cards[card_id]
                if face_up:
                    card.showFace()
                else:
                    card.showBack()
                self.allstacks[i].addCard(card)
        game.moves.state = old_state
        # 4) update settings
        for stack_id, cap in self.saveinfo.stack_caps:
            ##print stack_id, cap
            self.allstacks[stack_id].cap.update(cap.__dict__)
        # 5) subclass settings
        self._restoreGameHook(game)
        # 6) update view
        for stack in self.allstacks:
            stack.updateText()
        self.updateText()
        self.updateStatus(player=self.app.opt.player,
                          gamenumber=self.getGameNumber(format=1),
                          moves=(self.moves.index, self.stats.total_moves),
                          stats=self.app.stats.getStats(self.app.opt.player, self.id))
        if not self.preview:
            self.updateMenus()
            wm_map(self.top, maximized=self.app.opt.wm_maximized)
        self.setCursor(cursor=self.app.top_cursor)
        self.stats.update_time = time.time()
        self.busy = old_busy
        #
        ##self.configureHandler()         # reallocateCards
        after(self.top, 200, self.configureHandler) # wait for canvas is mapped
        #
        if TOOLKIT == 'gtk':
            ## FIXME
            if self.top:
                self.top.update_idletasks()
                self.top.show_now()
        #
        self.startPlayTimer()

    # restore a bookmarked game (e.g. after changing the cardset)
    def restoreGameFromBookmark(self, bookmark):
        old_busy, self.busy = self.busy, 1
        file = StringIO(bookmark)
        p = Unpickler(file)
        game = self._undumpGame(p, self.app)
        assert game.id == self.id
        self.restoreGame(game, reset=0)
        destruct(game)
        self.busy = old_busy

    def resetGame(self):
        self.hints.list = None
        self.s.talon.removeAllCards()
        for stack in self.allstacks:
            ##print stack
            stack.resetGame()
            if TOOLKIT == 'gtk':
                # FIXME (pyramid like games)
                stack.group.tkraise()
        if self.preview <= 1:
            for t in (self.texts.score, self.texts.base_rank,):
                if t:
                    t.config(text="")

    def nextGameFlags(self, id, random=None):
        f = 0
        if id != self.id:
            f = f | 1
        if self.app.nextgame.cardset is not self.app.cardset:
            f = f | 2
        if random is not None:
            if random.__class__ is not self.random.__class__:
                f = f | 16
            elif random.initial_seed != self.random.initial_seed:
                f = f | 16
        return f

    # quit to outer mainloop in class App, possibly restarting
    # with another game from there
    def quitGame(self, id=0, random=None, loadedgame=None,
                 startdemo=0, bookmark=0, holdgame=0):
        self.updateTime()
        if bookmark:
            id, random = self.id, self.random
            file = StringIO()
            p = Pickler(file, 1)
            self._dumpGame(p, bookmark=1)
            self.app.nextgame.bookmark = file.getvalue()
        if id > 0:
            self.setCursor(cursor=CURSOR_WATCH)
        self.app.nextgame.id = id
        self.app.nextgame.random = random
        self.app.nextgame.loadedgame = loadedgame
        self.app.nextgame.startdemo = startdemo
        self.app.nextgame.holdgame = holdgame
        self.updateStatus(time=None, moves=None, gamenumber=None, stats=None)
        self.top.mainquit()

    # This should be called directly before newGame(),
    # restoreGame(), restoreGameFromBookmark() and quitGame().
    def endGame(self, restart=0, bookmark=0, holdgame=0):
        if self.preview:
            return
        self.app.wm_save_state()
        if self.pause:
            self.doPause()
        if holdgame:
            return
        if bookmark:
            return
        if restart:
            if self.moves.index > 0 and self.getPlayerMoves() > 0:
                self.gstats.restarted = self.gstats.restarted + 1
            return
        self.updateStats()
        stats = self.app.stats
        if self.shallUpdateBalance():
            b = self.getGameBalance()
            if b:
                stats.total_balance[self.id] = stats.total_balance.get(self.id, 0) + b
                stats.session_balance[self.id] = stats.session_balance.get(self.id, 0) + b
                stats.gameid_balance = stats.gameid_balance + b

    # restart the current game
    def restartGame(self):
        self.endGame(restart=1)
        self.newGame(restart=1, random=self.random)

    def reallocateStacks(self):
        w0, h0 = self.width, self.height
        iw = int(self.canvas.cget('width'))
        ih = int(self.canvas.cget('height'))
        vw = self.canvas.winfo_width()
        vh = self.canvas.winfo_height()
        if vw <= iw or vh <= ih:
            return
        xf = float(vw)/iw
        yf = float(vh)/ih
        for stack in self.allstacks:
            x0, y0 = stack.init_coord
            x, y = int(x0*xf), int(y0*yf)
            if x == stack.x and y == stack.y:
                continue
            stack.moveTo(x, y)

    def createRandom(self, random):
        if random is None:
            if isinstance(self.random, PysolRandom):
                state = self.random.getstate()
                self.app.gamerandom.setstate(state)
            # we want at least 17 digits
            seed = self.app.gamerandom.randrange(10000000000000000L,
                                                 PysolRandom.MAX_SEED)
            self.random = PysolRandom(seed)
            self.random.origin = self.random.ORIGIN_RANDOM
        else:
            self.random = random
            self.random.reset()
        ##print 'createRandom:', self.random
        ##print "createRandom: origin =", self.random.origin

    def enterState(self, state):
        old_state = self.moves.state
        if state < old_state:
            self.moves.state = state
        return old_state

    def leaveState(self, old_state):
        self.moves.state = old_state

    def getSnapshot(self):
        # generate hash (unique string) of current move
        sn = []
        for stack in self.allstacks:
            s = []
            for card in stack.cards:
                s.append('%d%03d%d' % (card.suit, card.rank, card.face_up))
            sn.append(''.join(s))
        sn = '-'.join(sn)
        # optimisation
        sn = hash(sn)
        return sn

    def createSnGroups(self):
        # group stacks by class and cap
        sg = {}
        for s in self.allstacks:
            for k in sg:
                if s.__class__ is k.__class__ and \
                       s.cap.__dict__ == k.cap.__dict__:
                    g = sg[k]
                    g.append(s.id)
                    break
            else:
                # new group
                sg[s] = [s.id]
        sg = sg.values()
        self.sn_groups = sg
        ##print sg


    def updateSnapshots(self):
        sn = self.getSnapshot()
        if sn in self.snapshots:
            ##self.updateStatus(snapshot=True)
            pass
        else:
            self.snapshots.append(sn)
            ##self.updateStatus(snapshot=False)


    #
    # card creation & shuffling
    #

    # Create all cards for the game.
    def createCards(self, progress=None):
        gi = self.gameinfo
        pstep = 0
        if progress:
            pstep = (100.0 - progress.percent) / gi.ncards
        cards = []
        id = 0
        x, y = self.s.talon.x, self.s.talon.y
        for deck in range(gi.decks):
            for suit in gi.suits:
                for rank in gi.ranks:
                    card = self._createCard(id, deck, suit, rank, x=x, y=y)
                    if card is None:
                        continue
                    cards.append(card)
                    id = id + 1
                    if progress: progress.update(step=pstep)
            trump_suit = len(gi.suits)
            for rank in gi.trumps:
                card = self._createCard(id, deck, trump_suit, rank, x=x, y=y)
                if card is None:
                    continue
                cards.append(card)
                id = id + 1
                if progress: progress.update(step=pstep)
        if progress: progress.update(percent=100)
        assert len(cards) == gi.ncards
        return cards

    def _createCard(self, id, deck, suit, rank, x, y):
        return Card(id, deck, suit, rank, game=self, x=x, y=y)

    # shuffle cards
    def shuffle(self):
        # get a fresh copy of the original game-cards
        cards = list(self.cards)
        # init random generator
        if isinstance(self.random, LCRandom31) and len(cards) == 52:
            # FreeCell mode
            fcards = []
            for i in range(13):
                for j in (0, 39, 26, 13):
                    fcards.append(cards[i + j])
            cards = fcards
        self.random.reset()         # reset to initial seed
        # shuffle
        self.random.shuffle(cards)
        # subclass hook
        cards = self._shuffleHook(cards)
        # finally add the shuffled cards to the Talon
        for card in cards:
            self.s.talon.addCard(card, update=0)
            card.showBack(unhide=0)

    # shuffle cards, but keep decks together
    def shuffleSeparateDecks(self):
        cards = []
        self.random.reset()
        n = self.gameinfo.ncards / self.gameinfo.decks
        for deck in range(self.gameinfo.decks):
            i = deck * n
            deck_cards = list(self.cards)[i:i+n]
            self.random.shuffle(deck_cards)
            cards.extend(deck_cards)
        cards = self._shuffleHook(cards)
        for card in cards:
            self.s.talon.addCard(card, update=0)
            card.showBack(unhide=0)

    # subclass overrideable (must use self.random)
    def _shuffleHook(self, cards):
        return cards

    # utility for use by subclasses
    def _shuffleHookMoveToTop(self, cards, func, ncards=999999):
        # move cards to top of the Talon (i.e. first cards to be dealt)
        cards, scards = self._shuffleHookMoveSorter(cards, func, ncards)
        return cards + scards

    def _shuffleHookMoveToBottom(self, cards, func, ncards=999999):
        # move cards to bottom of the Talon (i.e. last cards to be dealt)
        cards, scards = self._shuffleHookMoveSorter(cards, func, ncards)
        return scards + cards

    def _shuffleHookMoveSorter(self, cards, func, ncards):
        # note that we reverse the cards, so that smaller sort_orders
        # will be nearer to the top of the Talon
        sitems, i = [], len(cards)
        for c in cards[:]:
            select, sort_order = func(c)
            if select:
                cards.remove(c)
                sitems.append((sort_order, i, c))
                if len(sitems) >= ncards:
                    break
            i = i - 1
        sitems.sort()
        sitems.reverse()
        scards = [item[2] for item in sitems]
        return cards, scards


    #
    # menu support
    #

    def _finishDrag(self):
        if self.demo:
            self.stopDemo()
        if self.busy: return 1
        if self.drag.stack:
            self.drag.stack.finishDrag()
        return 0

    def _cancelDrag(self, break_pause=True):
        self.stopWinAnimation()
        if self.demo:
            self.stopDemo()
        if break_pause and self.pause:
            self.doPause()
        self.interruptSleep()
        self.deleteStackDesc()
        if self.busy: return 1
        if self.drag.stack:
            self.drag.stack.cancelDrag()
        return 0

    def updateMenus(self):
        if not self.preview:
            self.app.menubar.updateMenus()

    def disableMenus(self):
        if not self.preview:
            self.app.menubar.disableMenus()


    #
    # UI & graphics support
    #

    def _defaultHandler(self, event):
        if not self.app:
            return True                 # FIXME (GTK)
        if not self.app.opt.mouse_undo:
            return True
        if self.pause:
            self.app.menubar.mPause()
            return True
        # stop animation
        if not self.event_handled and self.stopWinAnimation():
            return True
        self.interruptSleep()
        if self.deleteStackDesc():
            # delete piles descriptions
            return True
        if self.demo:
            # stop demo
            self.stopDemo()
            return True
        if not self.event_handled and self.drag.stack:
            # cancel drag
            self.drag.stack.cancelDrag(event)
            return True
        return False                    # continue this event

    def dropHandler(self, event):
        if not self._defaultHandler(event) and not self.event_handled:
            self.app.menubar.mDrop()
        self.event_handled = False
        return EVENT_PROPAGATE

    def undoHandler(self, event):
        if not self._defaultHandler(event) and not self.event_handled:
            self.app.menubar.mUndo()
        self.event_handled = False
        return EVENT_PROPAGATE

    def redoHandler(self, event):
        if not self._defaultHandler(event) and not self.event_handled:
            self.app.menubar.mRedo()
        self.event_handled = False
        return EVENT_PROPAGATE

    def updateStatus(self, **kw):
        if self.preview:
            return
        tb, sb = self.app.toolbar, self.app.statusbar
        for k, v in kw.items():
            if k == "gamenumber":
                if v is None:
                    if sb: sb.updateText(gamenumber="")
                    #self.top.wm_title("%s - %s" % (TITLE, self.getTitleName()))
                    continue
                if isinstance(v, basestring):
                    if sb: sb.updateText(gamenumber=v)
                    #self.top.wm_title("%s - %s %s" % (TITLE,
                    #                                  self.getTitleName(), v))
                    continue
            if k == "info":
                ##print 'updateStatus info:', v
                if v is None:
                    if sb: sb.updateText(info="")
                    continue
                if isinstance(v, str):
                    if sb: sb.updateText(info=v)
                    continue
            if k == "moves":
                if v is None:
                    ##if tb: tb.updateText(moves="Moves\n")
                    if sb: sb.updateText(moves="")
                    continue
                if isinstance(v, tuple):
                    ##if tb: tb.updateText(moves="Moves\n%d/%d" % v)
                    if sb: sb.updateText(moves="%d/%d" % v)
                    continue
                if isinstance(v, int):
                    ##if tb: tb.updateText(moves="Moves\n%d" % v)
                    if sb: sb.updateText(moves="%d" % v)
                    continue
                if isinstance(v, str):
                    ##if tb: tb.updateText(moves=v)
                    if sb: sb.updateText(moves=v)
                    continue
            if k == "player":
                if v is None:
                    if tb: tb.updateText(player=_("Player\n"))
                    continue
                if isinstance(v, basestring):
                    if tb:
                        #if self.app.opt.toolbar_size:
                        if self.app.toolbar.getSize():
                            tb.updateText(player=_("Player\n") + v)
                        else:
                            tb.updateText(player=v)
                    continue
            if k == "stats":
                if v is None:
                    if sb: sb.updateText(stats="")
                    continue
                if isinstance(v, tuple):
                    t = "%d: %d/%d" % (v[0]+v[1], v[0], v[1])
                    if sb: sb.updateText(stats=t)
                    continue
            if k == "time":
                if v is None:
                    if sb: sb.updateText(time='')
                if isinstance(v, basestring):
                    if sb: sb.updateText(time=v)
                continue
            if k == 'stuck':
                if sb: sb.updateText(stuck=v)
                continue
            raise AttributeError(k)

    def _unmapHandler(self, event):
        # pause game if root window has been iconified
        if self.app and not self.pause:
            self.app.menubar.mPause()

    def configureHandler(self, event=None):
        if not self.canvas:
            return
        for stack in self.allstacks:
            stack.updatePositions()

    #
    # sound support
    #

    def playSample(self, name, priority=0, loop=0):
        ##print "Game.playSample:", name, priority, loop
        if name in self.app.opt.sound_samples and \
               not self.app.opt.sound_samples[name]:
            return 0
        if self.app.audio:
            return self.app.audio.playSample(name, priority=priority, loop=loop)
        return 0

    def stopSamples(self):
        if self.app.audio:
            self.app.audio.stopSamples()

    def stopSamplesLoop(self):
        if self.app.audio:
            self.app.audio.stopSamplesLoop()

    def startDealSample(self, loop=999999):
        a = self.app.opt.animations
        if a and not self.preview:
            self.canvas.update_idletasks()
        if self.app.audio and self.app.opt.sound and self.app.opt.sound_samples['deal']:
            if a in (1, 2, 3, 10):
                self.playSample("deal01", priority=100, loop=loop)
            elif a == 4:
                self.playSample("deal04", priority=100, loop=loop)
            elif a == 5:
                self.playSample("deal08", priority=100, loop=loop)


    #
    # misc. methods
    #

    def areYouSure(self, title=None, text=None, confirm=-1, default=0):
        if self.preview:
            return True
        if confirm < 0:
            confirm = self.app.opt.confirm
        if confirm:
            if not title: title = TITLE
            if not text: text = _("Discard current game ?")
            self.playSample("areyousure")
            d = MfxMessageDialog(self.top, title=title, text=text,
                                 bitmap="question",
                                 strings=(_("&OK"), _("&Cancel")))
            if d.status != 0 or d.button != 0:
                return False
        return True

    def notYetImplemented(self):
        # don't used
        d = MfxMessageDialog(self.top, title="Not yet implemented",
                             text="This function is\nnot yet implemented.",
                             bitmap="error")

    # main animation method
    def animatedMoveTo(self, from_stack, to_stack, cards, x, y,
                       tkraise=1, frames=-1, shadow=-1):
        # available values of app.opt.animations:
        #  0 - without animations
        #  1 - very fast (without timer)
        #  2 - fast (default)
        #  3 - medium (2/3 of fast speed)
        #  4 - slow (1/4 of fast speed)
        #  5 - very slow (1/8 of fast speed)
        #  10 - used internally in game preview
        if self.app.opt.animations == 0 or frames == 0:
            return
        # init timer - need a high resolution for this to work
        clock, delay, skip = None, 1, 1
        if self.app.opt.animations >= 2:
            clock = uclock
        SPF = 0.15 / 8          # animation speed - seconds per frame
        if frames < 0:
            frames = 8
        assert frames >= 2
        if self.app.opt.animations == 3:        # medium
            frames = frames * 3
            SPF = SPF / 2
        elif self.app.opt.animations == 4:      # slow
            frames = frames * 8
            SPF = SPF / 2
        elif self.app.opt.animations == 5:      # very slow
            frames = frames * 16
            SPF = SPF / 2
        elif self.app.opt.animations == 10:
            # this is used internally in game preview to speed up
            # the initial dealing
            if self.moves.state == self.S_INIT and frames > 4:
                frames = frames / 2
        if shadow < 0:
            shadow = self.app.opt.shadow
        shadows = ()
        # start animation
        if tkraise:
            for card in cards:
                card.tkraise()
        c0 = cards[0]
        dx, dy = (x - c0.x) / float(frames), (y - c0.y) / float(frames)
        tx, ty = 0, 0
        i = 1
        if clock: starttime = clock()
        while i < frames:
            mx, my = int(round(dx * i)) - tx, int(round(dy * i)) - ty
            tx, ty = tx + mx, ty + my
            if i == 1 and shadow and from_stack:
                # create shadows in the first frame
                sx, sy = self.app.images.SHADOW_XOFFSET, self.app.images.SHADOW_YOFFSET
                shadows = from_stack.createShadows(cards, sx, sy)
            for s in shadows:
                s.move(mx, my)
            for card in cards:
                card.moveBy(mx, my)
            self.canvas.update_idletasks()
            step = 1
            if clock:
                endtime = starttime + i*SPF
                sleep = endtime - clock()
                if delay and sleep >= 0.005:
                    # we're fast - delay
                    ##print "Delay frame", i, sleep
                    usleep(sleep)
                elif skip and sleep <= -0.75*SPF:
                    # we're slow - skip 1 or 2 frames
                    ##print "Skip frame", i, sleep
                    step = step + 1
                    if frames > 4 and sleep < -1.5*SPF: step = step + 1
                ##print i, step, mx, my; time.sleep(0.5)
            i = i + step
        # last frame: delete shadows, move card to final position
        for s in shadows:
            s.delete()
        dx, dy = x - c0.x, y - c0.y
        for card in cards:
            card.moveBy(dx, dy)
        self.canvas.update_idletasks()


    def doAnimatedFlipAndMove(self, from_stack, to_stack=None, frames=-1):
        if self.app.opt.animations == 0 or frames == 0:
            return False
        if not from_stack.cards:
            return False
        if TOOLKIT == 'gtk':
            return False
        if not Image:
            return False

        canvas = self.canvas
        card = from_stack.cards[-1]
        im1 = card._active_image._pil_image
        if card.face_up:
            im2 = card._back_image._pil_image
        else:
            im2 = card._face_image._pil_image
        w, h = im1.size
        id = card.item.id
        #
        SPF = 0.1/8                     # animation speed - seconds per frame
        frames = 4.0                    # num frames for each step
        if self.app.opt.animations == 3: # medium
            SPF = 0.1/8
            frames = 7.0
        elif self.app.opt.animations == 4: # slow
            SPF = 0.1/8
            frames = 12.0
        elif self.app.opt.animations == 5: # very slow
            SPF = 0.1/8
            frames = 24.0

        if to_stack is None:
            x0, y0 = from_stack.getPositionFor(card)
            x1, y1 = x0, y0
            dest_x, dest_y = 0, 0
        else:
            x0, y0 = from_stack.getPositionFor(card)
            x1, y1 = to_stack.getPositionForNextCard()
            dest_x, dest_y = x1-x0, y1-y0

        if dest_x == 0 and dest_y == 0:
            # flip
            #ascent_dx, ascent_dy = 0, self.app.images.SHADOW_YOFFSET/frames
            ascent_dx, ascent_dy = 0, h/10.0/frames
            min_size = w/10
            shrink_dx = (w-min_size) / (frames-1)
            shrink_dy = 0
        elif dest_y == 0:
            # move to left/right waste
            #ascent_dx, ascent_dy = 0, self.app.images.SHADOW_YOFFSET/frames
            ascent_dx, ascent_dy = 0, h/10.0/frames
            min_size = w/10
            shrink_dx = (w-min_size) / (frames-1)
            shrink_dy = 0
        elif dest_x == 0:
            # move to top/bottom waste
            if 0:
                ascent_dx, ascent_dy = 0, h/10.0/frames
                min_size = w/10
                shrink_dx = (w-min_size) / (frames-1)
                shrink_dy = 0
            elif 0:
                ascent_dx, ascent_dy = 0, 0
                min_size = h/10
                shrink_dx = 0
                shrink_dy = (h-min_size) / (frames-1)
            else:
                return False
        else:
            # dest_x != 0 and dest_y != 0
            return False

        move_dx = dest_x / frames / 2
        move_dy = dest_y / frames / 2
        xpos, ypos = float(x0), float(y0)

        card.tkraise()

        # step 1
        d_x = shrink_dx/2+move_dx-ascent_dx
        d_y = shrink_dy/2+move_dy-ascent_dy
        nframe = 0
        while nframe < frames:
            starttime = uclock()
            # resize img
            ww = w - nframe*shrink_dx
            hh = h - nframe*shrink_dy
            tmp = im1.resize((int(ww), int(hh)))
            tk_tmp = ImageTk.PhotoImage(image=tmp)
            canvas.itemconfig(id, image=tk_tmp)
            # move img
            xpos += d_x
            ypos += d_y
            card.moveTo(int(round(xpos)), int(round(ypos)))
            canvas.update_idletasks()

            nframe += 1
            t = (SPF-(uclock()-starttime))*1000 # milliseconds
            if t > 0:
                usleep(t/1000)
##             else:
##                 nframe += 1
##                 xpos += d_x
##                 ypos += d_y

        # step 2
        d_x = -shrink_dx/2+move_dx+ascent_dx
        d_y = -shrink_dy/2+move_dy+ascent_dy
        nframe = 0
        while nframe < frames:
            starttime = uclock()
            # resize img
            ww = w - (frames-nframe-1)*shrink_dx
            hh = h - (frames-nframe-1)*shrink_dy
            tmp = im2.resize((int(ww), int(hh)))
            tk_tmp = ImageTk.PhotoImage(image=tmp)
            canvas.itemconfig(id, image=tk_tmp)
            # move img
            xpos += d_x
            ypos += d_y
            card.moveTo(int(round(xpos)), int(round(ypos)))
            canvas.update_idletasks()

            nframe += 1
            t = (SPF-(uclock()-starttime))*1000 # milliseconds
            if t > 0:
                usleep(t/1000)
##             else:
##                 nframe += 1
##                 xpos += d_x
##                 ypos += d_y

        card.moveTo(x1, y1)
        #canvas.update_idletasks()
        return True

    def animatedFlip(self, stack):
        if not self.app.opt.flip_animation:
            return False
        return self.doAnimatedFlipAndMove(stack)

    def animatedFlipAndMove(self, from_stack, to_stack, frames=-1):
        if not self.app.opt.flip_animation:
            return False
        return self.doAnimatedFlipAndMove(from_stack, to_stack, frames)


    def winAnimationEvent(self):
        # based on code from pygtk-demo
        FRAME_DELAY = 80
        CYCLE_LEN = 60
        starttime = uclock()
        images = self.win_animation.images
        saved_images = self.win_animation.saved_images # cached images
        canvas = self.canvas
        canvas.delete(*self.win_animation.canvas_images)
        self.win_animation.canvas_images = []

        x0 = int(int(canvas.cget('width'))*(canvas.xview()[0]))
        y0 = int(int(canvas.cget('height'))*(canvas.yview()[0]))
        width, height = self.win_animation.width, self.win_animation.height
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        x0 -= (width-cw)/2
        y0 -= (height-ch)/2

        tmp_tk_images = []
        raised_images = []
        n_images = len(images)
        xmid = width / 2.0
        ymid = height / 2.0
        radius = min(xmid, ymid) / 2.0

        f = float(self.win_animation.frame_num % CYCLE_LEN) / float(CYCLE_LEN)
        r = radius +(radius / 3.0) * math.sin(f * 2.0 * math.pi)
        img_index = 0

        for im in images:

            iw, ih = im.size

            ang = 2.0 * math.pi * img_index / n_images - f * 2.0 * math.pi
            xpos = x0 + int(xmid + r * math.cos(ang) - iw / 2.0)
            ypos = y0 + int(ymid + r * math.sin(ang) - ih / 2.0)

            if img_index & 1:
                k = math.sin(f * 2.0 * math.pi)
            else:
                k = math.cos(f * 2.0 * math.pi)
            k = k * k
            k = max(0.4, k)
            round_k = int(round(k*100))
            if img_index not in saved_images:
                saved_images[img_index] = {}
            if round_k in saved_images[img_index]:
                tk_tmp = saved_images[img_index][round_k]
            else:
                new_size = (int(iw*k), int(ih*k))
                if round_k == 100:
                    tmp = im
                else:
                    tmp = im.resize(new_size, resample=Image.BILINEAR)
                tk_tmp = ImageTk.PhotoImage(image=tmp)
                saved_images[img_index][round_k] = tk_tmp

            id = canvas.create_image(xpos, ypos, image=tk_tmp, anchor='nw')
            self.win_animation.canvas_images.append(id)
            if k > 0.6:
                raised_images.append(id)
            tmp_tk_images.append(tk_tmp)

            img_index += 1

        for id in raised_images:
            canvas.tag_raise(id)
        self.win_animation.frame_num = (self.win_animation.frame_num+1) % CYCLE_LEN
        self.win_animation.tk_images = tmp_tk_images
        canvas.update_idletasks()
        # loop
        t = FRAME_DELAY-int((uclock()-starttime)*1000)
        if t > 0:
            self.win_animation.timer = after(canvas, t, self.winAnimationEvent)
        else:
            self.win_animation.timer = after_idle(canvas, self.winAnimationEvent)

    def stopWinAnimation(self):
        if self.win_animation.timer:
            after_cancel(self.win_animation.timer) # stop loop
            self.win_animation.timer = None
            self.canvas.delete(*self.win_animation.canvas_images)
            self.win_animation.canvas_images = []
            self.win_animation.tk_images = [] # delete all images
            self.saved_images = {}
            self.canvas.showAllItems()
            return True
        return False

    def winAnimation(self, perfect=0):
        if self.preview:
            return
        #if not self.app.opt.animations:
        #    return
        if not self.app.opt.win_animation:
            return
        if TOOLKIT == 'gtk':
            return
        if not Image:
            return
        self.canvas.hideAllItems()
        # select some random cards
        cards = self.cards[:]
        scards = []
        ncards = min(10, len(cards))
        for i in xrange(ncards):
            c = self.app.miscrandom.choice(cards)
            scards.append(c)
            cards.remove(c)
        for c in scards:
            self.win_animation.images.append(c._face_image._pil_image)
        # compute visible geometry
        self.win_animation.width = self.canvas.winfo_width()
        self.win_animation.height = self.canvas.winfo_height()
        # run win animation in background
        ##after_idle(self.canvas, self.winAnimationEvent)
        after(self.canvas, 200, self.winAnimationEvent)
        return

    def redealAnimation(self):
        if self.preview:
            return
        if not self.app.opt.animations or not self.app.opt.redeal_animation:
            return
        cards = []
        for s in self.allstacks:
            if s is not self.s.talon:
                for c in s.cards:
                    cards.append((c,s))
        if not cards:
            return
        self.setCursor(cursor=CURSOR_WATCH)
        self.top.busyUpdate()
        self.canvas.update_idletasks()
        old_a = self.app.opt.animations
        if old_a == 0:
            self.app.opt.animations = 1     # very fast
        elif old_a == 3:                    # medium
            self.app.opt.animations = 2     # fast
        elif old_a == 4:                    # very slow
            self.app.opt.animations = 3     # slow
        # select some random cards
        acards = []
        scards = cards[:]
        for i in range(8):
            c, s = self.app.miscrandom.choice(scards)
            if c not in acards:
                acards.append(c)
                scards.remove((c,s))
                if not scards:
                    break
        # animate
        sx, sy = self.s.talon.x, self.s.talon.y
        w, h = self.width, self.height
        while cards:
            # get and un-tuple a random card
            t = self.app.miscrandom.choice(cards)
            c, s = t
            s.removeCard(c, update=0)
            # animation
            if c in acards or len(cards) <= 2:
                self.animatedMoveTo(s, None, [c], w/2, h/2, tkraise=0, shadow=0)
                self.animatedMoveTo(s, None, [c], sx, sy, tkraise=0, shadow=0)
            else:
                c.moveTo(sx, sy)
            cards.remove(t)
        self.app.opt.animations = old_a

    def sleep(self, seconds):
##        if 0 and self.canvas:
##            self.canvas.update_idletasks()
        if seconds > 0:
            if self.top:
                self.top.interruptSleep()
                self.top.sleep(seconds)
            else:
                time.sleep(seconds)

    def interruptSleep(self):
        if self.top:
            self.top.interruptSleep()

    #
    # card image support
    #

    def getCardFaceImage(self, deck, suit, rank):
        return self.app.images.getFace(deck, suit, rank)

    def getCardBackImage(self, deck, suit, rank):
        return self.app.images.getBack()

    def getCardShadeImage(self):
        return self.app.images.getShade()

    #
    # layout support
    #

    def _getClosestStack(self, cx, cy, stacks, dragstack):
        closest, cdist = None, 999999999
        # Since we only compare distances,
        # we don't bother to take the square root.
        for stack in stacks:
            dist = (stack.x - cx)**2 + (stack.y - cy)**2
            if dist < cdist:
                closest, cdist = stack, dist
        return closest

    def getClosestStack(self, card, dragstack):
        cx, cy = card.x, card.y
        for stacks, rect in self.regions.info:
            if cx >= rect[0] and cx < rect[2] and cy >= rect[1] and cy < rect[3]:
                return self._getClosestStack(cx, cy, stacks, dragstack)
        return self._getClosestStack(cx, cy, self.regions.remaining, dragstack)

    # define a region for use in getClosestStack()
    def setRegion(self, stacks, rect, priority=0):
        assert len(stacks) > 0
        assert len(rect) == 4 and rect[0] < rect[2] and rect[1] < rect[3]
        if DEBUG >= 2:
            MfxCanvasRectangle(self.canvas, rect[0], rect[1], rect[2], rect[3],
                               width=2, fill=None, outline='red')
        for s in stacks:
            assert s and s in self.allstacks
            # verify that the stack lies within the rectangle
            x, y, r = s.x, s.y, rect
            ##print x, y, r
            assert r[0] <= x <= r[2] and r[1] <= y <= r[3]
            # verify that the stack is not already in another region
            # with the same priority
            for d in self.regions.data:
                if priority == d[0]:
                    assert s not in d[2]
        # add to regions
        self.regions.data.append((priority, -len(self.regions.data), tuple(stacks), tuple(rect)))

    # as getClosestStack() is called within the mouse motion handler
    # event it is worth optimizing a little bit
    def optimizeRegions(self):
        # sort regions.data by priority
        self.regions.data.sort()
        self.regions.data.reverse()
        # copy (stacks, rect) to regions.info
        self.regions.info = []
        for d in self.regions.data:
            self.regions.info.append((d[2], d[3]))
        self.regions.info = tuple(self.regions.info)
        # determine remaining stacks
        remaining = list(self.sg.openstacks)
        for stacks, rect in self.regions.info:
            for stack in stacks:
                while stack in remaining:
                    remaining.remove(stack)
        self.regions.remaining = tuple(remaining)
        ##print self.regions.info

    def getInvisibleCoords(self):
        # for InvisibleStack, etc
        ##x, y = -500, -500 - len(game.allstacks)
        cardw, cardh = self.app.images.CARDW, self.app.images.CARDH
        x, y = cardw + self.canvas.xmargin, cardh + self.canvas.ymargin
        return -x-10, -y-10


    #
    # Game - subclass overridable actions - IMPORTANT FOR GAME LOGIC
    #

    # create the game (create stacks, texts, etc.)
    def createGame(self):
        raise SubclassResponsibility

    # start the game (i.e. deal initial cards)
    def startGame(self):
        raise SubclassResponsibility

    # can we deal cards ?
    def canDealCards(self):
        # default: ask the Talon
        return self.s.talon and self.s.talon.canDealCards()

    # deal cards - return number of cards dealt
    def dealCards(self, sound=True):
        # default: set state to deal and pass dealing to Talon
        if self.s.talon and self.canDealCards():
            self.finishMove()
            old_state = self.enterState(self.S_DEAL)
            n = self.s.talon.dealCards(sound=sound)
            self.leaveState(old_state)
            self.finishMove()
            if not self.checkForWin():
                self.autoPlay()
            return n
        return 0

    # fill a stack if rules require it (e.g. Picture Gallery)
    def fillStack(self, stack):
        pass

    # redeal cards (used in RedealTalonStack; all cards already in talon)
    def redealCards(self):
        pass

    # the actual hint class (or None)
    Hint_Class = DefaultHint
    Solver_Class = None
    Stuck_Class = None

    def getHintClass(self):
        return self.Hint_Class

    def getStrictness(self):
        return 0

    # can we save outself ?
    def canSaveGame(self):
        return True
    # can we load this game ?
    def canLoadGame(self, version_tuple, game_version):
        return self.GAME_VERSION == game_version
    # can we set a bookmark ?
    def canSetBookmark(self):
        return self.canSaveGame()

    # can we undo/redo ?
    def canUndo(self):
        return True
    def canRedo(self):
        return self.canUndo()

    # Mahjongg
    def canShuffle(self):
        return False


    #
    # Game - stats handlers
    #

    # game changed - i.e. should we ask the player to discard the game
    def changed(self, restart=0):
        if self.gstats.updated < 0:
            return 0                    # already won or lost
        if self.gstats.loaded > 0:
            return 0                    # loaded games account for no stats
        if not restart:
            if self.gstats.restarted > 0:
                return 1                # game was restarted - always ask
            if self.gstats.goto_bookmark_moves > 0:
                return 1
        if self.moves.index == 0 or self.getPlayerMoves() == 0:
            return 0
        return 2

    def getWinStatus(self):
        won = self.isGameWon() != 0
        if not won or self.stats.hints > 0 or self.stats.demo_moves > 0:
            # sorry, you lose
            return won, 0, self.U_LOST
        if (self.stats.undo_moves == 0 and
            self.stats.goto_bookmark_moves == 0 and
###              self.stats.quickplay_moves == 0 and
            self.stats.highlight_piles == 0 and
            self.stats.highlight_cards == 0 and
            self.stats.shuffle_moves == 0):
            # perfect !
            return won, 2, self.U_PERFECT
        return won, 1, self.U_WON

    # update statistics when a game was won/ended/canceled/...
    def updateStats(self, demo=0):
        if self.preview:
            return ''
        if not demo:
            self.stopPlayTimer()
        won, status, updated = self.getWinStatus()
        if demo and self.getPlayerMoves() == 0:
            if not self.stats.demo_updated:
                # a pure demo game - update demo stats
                self.stats.demo_updated = updated
                self.app.stats.updateStats(None, self, won)
            return ''
        elif self.changed():
            # must update player stats
            self.gstats.updated = updated
            if self.app.opt.update_player_stats:
                ret = self.app.stats.updateStats(self.app.opt.player, self, status)
                self.updateStatus(stats=self.app.stats.getStats(self.app.opt.player, self.id))
                top_msg = ''
                if ret:
                    if ret[0] and ret[1]:
                        top_msg = _('''
You have reached
#%d in the %s of playing time
and #%d in the %s of moves.''') % (ret[0], TOP_TITLE, ret[1], TOP_TITLE)
                    elif ret[0]:        # playing time
                        top_msg = _('''
You have reached
#%d in the %s of playing time.''') % (ret[0], TOP_TITLE)
                    elif ret[1]:        # moves
                        top_msg = _('''
You have reached
#%d in the %s of moves.''') % (ret[1], TOP_TITLE)
                return top_msg
        elif not demo:
            # only update the session log
            if self.app.opt.update_player_stats:
                if self.gstats.loaded:
                    self.app.stats.updateStats(self.app.opt.player, self, -2)
                elif self.gstats.updated == 0 and self.stats.demo_updated == 0:
                    self.app.stats.updateStats(self.app.opt.player, self, -1)
        return ''

    def checkForWin(self):
        won, status, updated = self.getWinStatus()
        if not won:
            return 0
        self.finishMove()       # just in case
        if self.preview:
            return 1
        if self.finished:
            return 1
        if self.demo:
            return status
        if status == 2:
            top_msg = self.updateStats()
            time = self.getTime()
            self.finished = True
            self.playSample("gameperfect", priority=1000)
            self.winAnimation(perfect=1)
            text = ungettext('''Your playing time is %s\nfor %d move.''',
                             '''Your playing time is %s\nfor %d moves.''',
                             self.moves.index)
            text = text % (time, self.moves.index)
            d = MfxMessageDialog(self.top, title=_("Game won"),
                                 text=_('''
Congratulations, this
was a truly perfect game !

%s
%s
''') % (text, top_msg),
                                 strings=(_("&New game"), None, _("&Cancel")),
                                 image=self.app.gimages.logos[5])
        elif status == 1:
            top_msg = self.updateStats()
            time = self.getTime()
            self.finished = True
            self.playSample("gamewon", priority=1000)
            self.winAnimation()
            text = ungettext('''Your playing time is %s\nfor %d move.''',
                             '''Your playing time is %s\nfor %d moves.''',
                             self.moves.index)
            text = text % (time, self.moves.index)
            d = MfxMessageDialog(self.top, title=_("Game won"),
                                 text=_('''
Congratulations, you did it !

%s
%s
''') % (text, top_msg),
                                 strings=(_("&New game"), None, _("&Cancel")),
                                 image=self.app.gimages.logos[4])
        elif self.gstats.updated < 0:
            self.finished = True
            self.playSample("gamefinished", priority=1000)
            d = MfxMessageDialog(self.top, title=_("Game finished"), bitmap="info",
                                 text=_("\nGame finished\n"),
                                 strings=(_("&New game"), None, _("&Cancel")))
        else:
            self.finished = True
            self.playSample("gamelost", priority=1000)
            d = MfxMessageDialog(self.top, title=_("Game finished"), bitmap="info",
                                 text=_("\nGame finished, but not without my help...\n"),
                                 strings=(_("&New game"), _("&Restart"), _("&Cancel")))
        self.updateMenus()
        if d.status == 0 and d.button == 0:
            # new game
            self.endGame()
            self.newGame()
        elif d.status == 0 and d.button == 1:
            # restart game
            self.restartGame()
        return 1


    #
    # Game - subclass overridable methods (but usually not)
    #

    def isGameWon(self):
        # default: all Foundations must be filled
        c = 0
        for s in self.s.foundations:
            c = c + len(s.cards)
        return c == len(self.cards)

    def getFoundationDir(self):
        for s in self.s.foundations:
            if len(s.cards) >= 2:
                return s.getRankDir()
        return 0

    # determine the real number of player_moves
    def getPlayerMoves(self):
        player_moves = self.stats.player_moves
##        if self.moves.index > 0 and self.stats.demo_moves == self.moves.index:
##            player_moves = 0
        return player_moves

    def updateTime(self):
        if self.finished:
            return
        if self.pause:
            return
        t = time.time()
        d = t - self.stats.update_time
        if d > 0:
            self.stats.elapsed_time += d
            self.gstats.total_elapsed_time += d
        self.stats.update_time = t

    def getTime(self):
        self.updateTime()
        t = int(self.stats.elapsed_time)
        return format_time(t)


    #
    # Game - subclass overridable intelligence
    #

    def getAutoStacks(self, event=None):
        # returns (flipstacks, dropstacks, quickplaystacks)
        # default: sg.dropstacks
        return (self.sg.dropstacks, self.sg.dropstacks, self.sg.dropstacks)

    # handles autofaceup, autodrop and autodeal
    def autoPlay(self, autofaceup=-1, autodrop=-1, autodeal=-1, sound=True):
        if self.demo:
            return 0
        old_busy, self.busy = self.busy, 1
        if autofaceup < 0: autofaceup = self.app.opt.autofaceup
        if autodrop < 0: autodrop = self.app.opt.autodrop
        if autodeal < 0: autodeal = self.app.opt.autodeal
        moves = self.stats.total_moves
        n = self._autoPlay(autofaceup, autodrop, autodeal, sound=sound)
        self.finishMove()
        self.stats.autoplay_moves = self.stats.autoplay_moves + (self.stats.total_moves - moves)
        self.busy = old_busy
        return n

    def _autoPlay(self, autofaceup, autodrop, autodeal, sound):
        flipstacks, dropstacks, quickstacks = self.getAutoStacks()
        done_something = 1
        while done_something:
            done_something = 0
            # a) flip top cards face-up
            if autofaceup and flipstacks:
                for s in flipstacks:
                    if s.canFlipCard():
                        if sound:
                            self.playSample("autoflip", priority=5)
                        #~s.flipMove()
                        s.flipMove(animation=True)
                        done_something = 1
                        # each single flip is undo-able unless opt.autofaceup
                        self.finishMove()
                        if self.checkForWin():
                            return 1
            # b) drop cards
            if autodrop and dropstacks:
                for s in dropstacks:
                    to_stack, ncards = s.canDropCards(self.s.foundations)
                    if to_stack:
                        # each single drop is undo-able (note that this call
                        # is before the acutal move)
                        self.finishMove()
                        if sound:
                            self.playSample("autodrop", priority=30)
                        s.moveMove(ncards, to_stack)
                        done_something = 1
                        if self.checkForWin():
                            return 1
            # c) deal
            if autodeal:
                if self._autoDeal(sound=sound):
                    done_something = 1
                    self.finishMove()
                    if self.checkForWin():
                        return 1
        return 0

    def _autoDeal(self, sound=True):
        # default: deal a card to the waste if the waste is empty
        w = self.s.waste
        if w and len(w.cards) == 0 and self.canDealCards():
            return self.dealCards(sound=sound)
        return 0

    def autoDrop(self, autofaceup=-1):
        old_a = self.app.opt.animations
        if old_a == 3:                  # medium
            self.app.opt.animations = 2 # fast
        self.autoPlay(autofaceup=autofaceup, autodrop=1)
        self.app.opt.animations = old_a

    ## for find_card_dialog
    def highlightCard(self, suit, rank):
        if not self.app:
            return None
        col = self.app.opt.colors['samerank_1']
        info = []
        for s in self.allstacks:
            for c in s.cards:
                if c.suit == suit and c.rank == rank:
                    if s.basicShallHighlightSameRank(c):
                        info.append((s, c, c, col))
        return self._highlightCards(info, 0)

    ### highlight all moveable piles
    def getHighlightPilesStacks(self):
        # default: dropstacks with min pile length = 2
        if self.sg.hp_stacks:
            return ((self.sg.hp_stacks, 2),)
        return ()

    def _highlightCards(self, info, sleep=1.5, delta=(1,1,1,1)):
        if not info:
            return 0
        if self.pause:
            return 0
        self.stopWinAnimation()
        items = []
        for s, c1, c2, color in info:
            assert c1 in s.cards and c2 in s.cards
            tkraise = False
            if c1 is c2:
                # highlight single card
                sx0, sy0 = s.getOffsetFor(c1)
                x1, y1 = s.getPositionFor(c1)
                x2, y2 = x1, y1
                if c1 is s.cards[-1]:
                    # last card in the stack (for Pyramid-like games)
                    tkraise = True
            else:
                # highlight pile
                if len(s.CARD_XOFFSET) > 1:
                    sx0 = 0
                else:
                    sx0 = s.CARD_XOFFSET[0]
                if len(s.CARD_YOFFSET) > 1:
                    sy0 = 0
                else:
                    sy0 = s.CARD_YOFFSET[0]
                x1, y1 = s.getPositionFor(c1)
                x2, y2 = s.getPositionFor(c2)
            if sx0 != 0 and sy0 == 0:
                # horizontal stack
                y2 = y2 + self.app.images.CARDH
                if c2 is s.cards[-1]: # top card
                    x2 = x2 + self.app.images.CARDW
                else:
                    if sx0 > 0:
                        # left to right
                        x2 = x2 + sx0
                    else:
                        # right to left
                        x1 = x1 + self.app.images.CARDW
                        x2 = x2 + self.app.images.CARDW + sx0
            elif sx0 == 0 and sy0 != 0:
                # vertical stack
                x2 = x2 + self.app.images.CARDW
                if c2 is s.cards[-1]: # top card
                    y2 = y2 + self.app.images.CARDH
                else:
                    if sy0 > 0:
                        # up to down
                        y2 = y2 + sy0
                    else:
                        # down to up
                        y1 = y1 + self.app.images.CARDH
                        y2 = y2 + self.app.images.CARDH + sy0
            else:
                x2 = x2 + self.app.images.CARDW
                y2 = y2 + self.app.images.CARDH
                tkraise = True
            ##print c1, c2, x1, y1, x2, y2
            x1, x2 = x1-delta[0], x2+delta[1]
            y1, y2 = y1-delta[2], y2+delta[3]
            if TOOLKIT == 'tk':
                r = MfxCanvasRectangle(self.canvas, x1, y1, x2, y2,
                                       width=4, fill=None, outline=color)
                if tkraise:
                    r.tkraise(c2.item)
            elif TOOLKIT == 'gtk':
                r = MfxCanvasRectangle(self.canvas, x1, y1, x2, y2,
                                       width=4, fill=None, outline=color,
                                       group=s.group)
                if tkraise:
                    i = s.cards.index(c2)
                    for c in s.cards[i+1:]:
                        c.tkraise(1)
            items.append(r)
        if not items:
            return 0
        self.canvas.update_idletasks()
        if sleep:
            self.sleep(sleep)
            items.reverse()
            for r in items:
                r.delete()
            self.canvas.update_idletasks()
            return EVENT_HANDLED
        else:
            # remove items later (find_card_dialog)
            return items

    def highlightNotMatching(self):
        if self.demo:
            return
        if not self.app.opt.highlight_not_matching:
            return
        # compute visible geometry
        x = int(int(self.canvas.cget('width'))*(self.canvas.xview()[0]))
        y = int(int(self.canvas.cget('height'))*(self.canvas.yview()[0]))
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        #
        color = self.app.opt.colors['not_matching']
        width = 6
        xmargin, ymargin = self.canvas.xmargin, self.canvas.ymargin
        if self.preview:
            width = 4
            xmargin, ymargin = 0, 0
        x0, y0 = x+width/2-xmargin, y+width/2-ymargin
        x1, y1 = x+w-width/2-xmargin, y+h-width/2-ymargin
        r = MfxCanvasRectangle(self.canvas, x0, y0, x1, y1,
                               width=width, fill=None, outline=color)
        self.canvas.update_idletasks()
        self.sleep(self.app.opt.timeouts['highlight_cards'])
        r.delete()
        self.canvas.update_idletasks()

    def highlightPiles(self, sleep=1.5):
        stackinfo = self.getHighlightPilesStacks()
        if not stackinfo:
            self.highlightNotMatching()
            return 0
        col = self.app.opt.colors['piles']
        hi = []
        for si in stackinfo:
            for s in si[0]:
                pile = s.getPile()
                if pile and len(pile) >= si[1]:
                    hi.append((s, pile[0], pile[-1], col))
        if not hi:
            self.highlightNotMatching()
            return 0
        return self._highlightCards(hi, sleep)

    #
    # highlight matching cards
    #

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return False

    def _shallHighlightMatch_AC(self, stack1, card1, stack2, card2):
        # by alternate color
        return card1.color != card2.color and abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_ACW(self, stack1, card1, stack2, card2):
        # by alternate color with wrapping (only for french games)
        return (card1.color != card2.color
                and ((card1.rank + 1) % 13 == card2.rank
                     or (card2.rank + 1) % 13 == card1.rank))

    def _shallHighlightMatch_SS(self, stack1, card1, stack2, card2):
        # by same suit
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_SSW(self, stack1, card1, stack2, card2):
        # by same suit with wrapping (only for french games)
        return (card1.suit == card2.suit
                and ((card1.rank + 1) % 13 == card2.rank
                     or (card2.rank + 1) % 13 == card1.rank))

    def _shallHighlightMatch_RK(self, stack1, card1, stack2, card2):
        # by rank
        return abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_RKW(self, stack1, card1, stack2, card2):
        # by rank with wrapping (only for french games)
        return ((card1.rank + 1) % 13 == card2.rank
                or (card2.rank + 1) % 13 == card1.rank)

    def _shallHighlightMatch_BO(self, stack1, card1, stack2, card2):
        # by any suit but own
        return card1.suit != card2.suit and abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_BOW(self, stack1, card1, stack2, card2):
        # by any suit but own with wrapping (only for french games)
        return (card1.suit != card2.suit
                and ((card1.rank + 1) % 13 == card2.rank
                     or (card2.rank + 1) % 13 == card1.rank))

    def _shallHighlightMatch_SC(self, stack1, card1, stack2, card2):
        # by same color
        return card1.color == card2.color and abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_SCW(self, stack1, card1, stack2, card2):
        # by same color with wrapping (only for french games)
        return (card1.color == card2.color
                and ((card1.rank + 1) % 13 == card2.rank
                     or (card2.rank + 1) % 13 == card1.rank))


    #
    # quick-play
    #

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack in self.s.reserves:
            # if to_stack in reserves prefer empty stack
            ##return 1000 - len(to_stack.cards)
            return 1000 - int(len(to_stack.cards) != 0)
        # prefer non-empty piles in to_stack
        return 1001 + int(len(to_stack.cards) != 0)

    def _getSpiderQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack in self.s.reserves:
            # if to_stack in reserves prefer empty stack
            return 1000-len(to_stack.cards)
        # for spider-type stacks
        if to_stack.cards:
            # check suit
            same_suit = from_stack.cards[-ncards].suit == to_stack.cards[-1].suit
            return int(same_suit)+1002
        return 1001

    #
    # Score (I really don't like scores in Patience games...)
    #

    # update game-related canvas texts (i.e. self.texts)
    def updateText(self):
        pass

    def getGameScore(self):
        return None

    # casino type scoring
    def getGameScoreCasino(self):
        v = -len(self.cards)
        for s in self.s.foundations:
            v = v + 5 * len(s.cards)
        return v

    def shallUpdateBalance(self):
        # Update the balance unless this is a loaded game or
        # a manually selected game number.
        if self.gstats.loaded:
            return False
        if self.random.origin == self.random.ORIGIN_SELECTED:
            return False
        return True

    def getGameBalance(self):
        return 0


    #
    # Hint - uses self.getHintClass()
    #

    # compute all hints for the current position
    # this is the only method that actually uses class Hint
    def getHints(self, level, taken_hint=None):
        if level == 3:
            #if self.solver is None:
            #    return None
            return self.solver.getHints(taken_hint)
        hint_class = self.getHintClass()
        if hint_class is None:
            return None
        hint = hint_class(self, level)      # call constructor
        return hint.getHints(taken_hint)    # and return all hints

    # give a hint
    def showHint(self, level=0, sleep=1.5, taken_hint=None):
        if self.getHintClass() is None:
            self.highlightNotMatching()
            return None
        # reset list if level has changed
        if level != self.hints.level:
            self.hints.level = level
            self.hints.list = None
        # compute all hints
        if self.hints.list is None:
            self.hints.list = self.getHints(level, taken_hint)
            ###print self.hints.list
            self.hints.index = 0
        # get next hint from list
        if not self.hints.list:
            self.highlightNotMatching()
            return None
        h = self.hints.list[self.hints.index]
        self.hints.index = self.hints.index + 1
        if self.hints.index >= len(self.hints.list):
            self.hints.index = 0
        # paranoia - verify hint
        score, pos, ncards, from_stack, to_stack, text_color, forced_move = h
        assert from_stack and len(from_stack.cards) >= ncards
        if ncards == 0:
            # a deal move, should not happen with level=0/1
            assert level >= 2
            assert from_stack is self.s.talon
            return h
        elif from_stack == to_stack:
            # a flip move, should not happen with level=0/1
            assert level >= 2
            assert ncards == 1 and len(from_stack.cards) >= ncards
            return h
        else:
            # a move move
            assert to_stack
            assert 1 <= ncards <= len(from_stack.cards)
            if DEBUG:
                if not to_stack.acceptsCards(
                    from_stack, from_stack.cards[-ncards:]):
                    print '*fail accepts cards*', from_stack, to_stack, ncards
                if not from_stack.canMoveCards(from_stack.cards[-ncards:]):
                    print '*fail move cards*', from_stack, ncards
            ##assert from_stack.canMoveCards(from_stack.cards[-ncards:]) # FIXME: Pyramid
            assert to_stack.acceptsCards(from_stack, from_stack.cards[-ncards:])
        if sleep <= 0.0:
            return h
        info = (level == 1) or (level > 1 and DEBUG)
        if info and self.app.statusbar and self.app.opt.statusbar:
            self.app.statusbar.configLabel("info", text=_("Score %6d") % (score), fg=text_color)
        else:
            info = 0
        self.drawHintArrow(from_stack, to_stack, ncards, sleep)
        if info:
            self.app.statusbar.configLabel("info", text="", fg="#000000")
        return h


    def drawHintArrow(self, from_stack, to_stack, ncards, sleep):
        # compute position for arrow
        images = self.app.images
        x1, y1 = from_stack.getPositionFor(from_stack.cards[-ncards])
        x2, y2 = to_stack.getPositionFor(to_stack.getCard())
        x1, y1 = x1 + images.CARD_DX, y1 + images.CARD_DY
        x2, y2 = x2 + images.CARD_DX, y2 + images.CARD_DY
        if ncards == 1:
            x1 = x1 + images.CARDW / 2
            y1 = y1 + images.CARDH / 2
        elif from_stack.CARD_XOFFSET[0]:
            x1 = x1 + from_stack.CARD_XOFFSET[0] / 2
            y1 = y1 + images.CARDH / 2
        else:
            x1 = x1 + images.CARDW / 2
            y1 = y1 + from_stack.CARD_YOFFSET[0] / 2
        x2 = x2 + images.CARDW / 2
        y2 = y2 + images.CARDH / 2
        # draw the hint
        arrow = MfxCanvasLine(self.canvas, x1, y1, x2, y2, width=7,
                              fill=self.app.opt.colors['hintarrow'],
                              arrow="last", arrowshape=(30,30,10))
        self.canvas.update_idletasks()
        # wait
        self.sleep(sleep)
        # delete the hint
        if arrow is not None:
            arrow.delete()
        self.canvas.update_idletasks()


    #
    # Demo - uses showHint()
    #

    # start a demo
    def startDemo(self, mixed=1, level=2):
        assert level >= 2               # needed for flip/deal hints
        if not self.top:
            return
        self.demo = Struct(
            level = level,
            mixed = mixed,
            sleep = self.app.opt.timeouts['demo'],
            last_deal = [],
            snapshots = [],
            hint = None,
            keypress = None,
            start_demo_moves = self.stats.demo_moves,
            info_text = None,
        )
        self.hints.list = None
        self.createDemoInfoText()
        self.createDemoLogo()
        after_idle(self.top, self.demoEvent) # schedule first move

    # stop the demo
    def stopDemo(self, event=None):
        if not self.demo:
            return
        self.canvas.setTopImage(None)
        self.demo_logo = None
        self.demo = None
        self.updateMenus()

    # demo event - play one demo move and check for win/loss
    def demoEvent(self):
        # note: other events are allowed to stop self.demo at any time
        if not self.demo or self.demo.keypress:
            self.stopDemo()
            #self.updateMenus()
            return
        finished = self.playOneDemoMove(self.demo)
        self.finishMove()
        self.top.update_idletasks()
        self.hints.list = None
        player_moves = self.getPlayerMoves()
        d, status = None, 0
        bitmap = "info"
        timeout = 10000
        if 1 and player_moves == 0:
            timeout = 5000
        if self.demo and self.demo.level == 3:
            timeout = 0
        if self.isGameWon():
            self.updateTime()
            finished = 1
            self.finished = True
            self.stopPlayTimer()
            if not self.top.winfo_ismapped():
                status = 2
            elif player_moves == 0:
                self.playSample("autopilotwon", priority=1000)
                s = self.app.miscrandom.choice((_("&Great"), _("&Cool"),
                                                _("&Yeah"),  _("&Wow")))
                text = ungettext('\nGame solved in %d move.\n',
                                 '\nGame solved in %d moves.\n',
                                 self.moves.index)
                text = text % self.moves.index
                d = MfxMessageDialog(self.top, title=TITLE+_(" Autopilot"),
                                     text=text,
                                     image=self.app.gimages.logos[4],
                                     strings=(s,),
                                     separator=True,
                                     timeout=timeout)
                status = d.status
            else:
                ##s = self.app.miscrandom.choice((_("&OK"), _("&OK")))
                s = _("&OK")
                text = _("\nGame finished\n")
                if DEBUG:
                    text += "\nplayer_moves: %d\ndemo_moves: %d\n" % (self.stats.player_moves, self.stats.demo_moves)
                d = MfxMessageDialog(self.top, title=TITLE+_(" Autopilot"),
                                     text=text, bitmap=bitmap, strings=(s,),
                                     padx=30, timeout=timeout)
                status = d.status
        elif finished:
            ##self.stopPlayTimer()
            if not self.top.winfo_ismapped():
                status = 2
            else:
                if player_moves == 0:
                    self.playSample("autopilotlost", priority=1000)
                s = self.app.miscrandom.choice((_("&Oh well"), _("&That's life"), _("&Hmm"))) # ??? accelerators
                d = MfxMessageDialog(self.top, title=TITLE+_(" Autopilot"),
                                     text=_("\nThis won't come out...\n"),
                                     bitmap=bitmap, strings=(s,),
                                     padx=30, timeout=timeout)
                status = d.status
        if finished:
            self.updateStats(demo=1)
            if not DEBUG and self.demo and status == 2:
                # timeout in dialog
                if self.stats.demo_moves > self.demo.start_demo_moves:
                    # we only increase the splash-screen counter if the last
                    # demo actually made a move
                    self.app.demo_counter =  self.app.demo_counter + 1
                    if self.app.demo_counter % 3 == 0:
                        if self.top.winfo_ismapped():
                            status = help_about(self.app, timeout=10000)
            if self.demo and status == 2:
                # timeout in dialog - start another demo
                demo = self.demo
                id = self.id
                if 1 and demo.mixed and DEBUG:
                    # debug - advance game id to make sure we hit all games
                    gl = self.app.gdb.getGamesIdSortedById()
                    ##gl = self.app.gdb.getGamesIdSortedByName()
                    gl = list(gl)
                    index = (gl.index(self.id) + 1) % len(gl)
                    id = gl[index]
                elif demo.mixed:
                    # choose a random game
                    gl = self.app.gdb.getGamesIdSortedById()
                    while len(gl) > 1:
                        id = self.app.getRandomGameId()
                        if 0 or id != self.id:      # force change of game
                            break
                if self.nextGameFlags(id) == 0:
                    self.endGame()
                    self.newGame(autoplay=0)
                    self.startDemo(mixed=demo.mixed)
                else:
                    self.endGame()
                    self.stopDemo()
                    self.quitGame(id, startdemo=1)
            else:
                self.stopDemo()
                if DEBUG >= 10:
                    # debug - only for testing winAnimation()
                    self.endGame()
                    self.winAnimation()
                    self.newGame()
        else:
            # game not finished yet
            self.top.busyUpdate()
            if self.demo:
                after_idle(self.top, self.demoEvent) # schedule next move

    # play one demo move while in the demo event
    def playOneDemoMove(self, demo):
        if self.moves.index > 2000:
            # we're probably looping because of some bug in the hint code
            return 1
        sleep = demo.sleep
        # first try to deal cards to the Waste (unless there was a forced move)
        if not demo.hint or not demo.hint[6]:
            if self._autoDeal(sound=False):
                return 0
        # display a hint
        h = self.showHint(demo.level, sleep, taken_hint=demo.hint)
        demo.hint = h
        if not h:
            return 1
        # now actually play the hint
        score, pos, ncards, from_stack, to_stack, text_color, forced_move = h
        if ncards == 0:
            # a deal-move
            # do not let games like Klondike and Canfield deal forever
            if self.dealCards() == 0:
                return 1
            if 0:                       # old version, based on dealing card
                c = self.s.talon.getCard()
                if c in demo.last_deal:
                    # We went through the whole Talon. Give up.
                    return 1
                # Note that `None' is a valid entry in last_deal[]
                # (this means that all cards are on the Waste).
                demo.last_deal.append(c)
            else:                       # new version, based on snapshots
                # check snapshot
                sn = self.getSnapshot()
                if sn in demo.snapshots:
                    # not unique
                    return 1
                demo.snapshots.append(sn)
        elif from_stack == to_stack:
            # a flip-move
            from_stack.flipMove(animation=True)
            demo.last_deal = []
        else:
            # a move-move
            from_stack.moveMove(ncards, to_stack, frames=-1)
            demo.last_deal = []
        return 0

    def createDemoInfoText(self):
        ## TODO - the text placement is not fully ok
        if DEBUG:
            self.showHelp('help', self.getDemoInfoText())
        return
        if not self.demo or self.demo.info_text or self.preview:
            return
        tinfo = [
            ("sw", 8, self.height - 8),
            ("se", self.width - 8, self.height - 8),
            ("nw", 8, 8),
            ("ne", self.width - 8, 8),
        ]
        ta = self.getDemoInfoTextAttr(tinfo)
        if ta:
            #font = self.app.getFont("canvas_large")
            font = self.app.getFont("default")
            self.demo.info_text = MfxCanvasText(self.canvas, ta[1], ta[2],
                                                anchor=ta[0], font=font,
                                                text=self.getDemoInfoText())

    def getDemoInfoText(self):
        h = self.Hint_Class is None and 'None' or self.Hint_Class.__name__
        return '%s (%s)' % (self.gameinfo.short_name, h)

    def getDemoInfoTextAttr(self, tinfo):
        items1, items2 = [], []
        for s in self.allstacks:
            if s.is_visible:
                items1.append(s)
                items1.extend(list(s.cards))
                if not s.cards and s.cap.max_accept > 0:
                    items2.append(s)
                else:
                    items2.extend(list(s.cards))
        ti = self.__checkFreeSpaceForDemoInfoText(items1)
        if ti < 0:
            ti = self.__checkFreeSpaceForDemoInfoText(items2)
        if ti < 0:
            return None
        return tinfo[ti]

    def __checkFreeSpaceForDemoInfoText(self, items):
        CW, CH = self.app.images.CARDW, self.app.images.CARDH
        # note: these are translated by (-CW/2, -CH/2)
        x1, x2 = 3*CW/2, self.width - 5*CW/2
        y1, y2 = CH/2, self.height - 3*CH/2
        #
        m = [1, 1, 1, 1]
        for c in items:
            cx, cy = c.x, c.y
            if cy >= y2:
                if cx <= x1:
                    m[0] = 0
                elif cx >= x2:
                    m[1] = 0
            elif cy <= y1:
                if cx <= x1:
                    m[2] = 0
                elif cx >= x2:
                    m[3] = 0
        for mm in m:
            if mm:
                return mm
        return -1


    def createDemoLogo(self):
        if not self.app.gimages.demo:
            return
        if self.demo_logo or not self.app.opt.demo_logo:
            return
        if self.width <= 100 or self.height <= 100:
            return
        ##self.demo_logo = self.app.miscrandom.choice(self.app.gimages.demo)
        n = self.random.initial_seed % len(self.app.gimages.demo)
        self.demo_logo = self.app.gimages.demo[int(n)]
        self.canvas.setTopImage(self.demo_logo)

    #
    # stuck
    #

    def getStuck(self):
        h = self.Stuck_Class.getHints(None)
        if h:
            self.failed_snapshots = []
            return True
        if not self.canDealCards():
            return False
        # can deal cards: do we have any hints in previous deals ?
        sn = self.getSnapshot()
        if sn in self.failed_snapshots:
            return False
        self.failed_snapshots.append(sn)
        return True

    def updateStuck(self):
        # stuck
        if self.finished:
            return
        if self.Stuck_Class is None:
            return
        if self.getStuck():
            text = ''
        else:
            text = 'x'
            #self.playSample("autopilotlost", priority=1000)
        self.updateStatus(stuck=text)


    #
    # Handle moves (with move history for undo/redo)
    # Actual move is handled in a subclass of AtomicMove.
    #
    # Note:
    #   All playing moves (user actions, demo games) must get routed
    #   to Stack.moveMove() because the stack may add important
    #   triggers to a move (most notably fillStack and updateModel).
    #
    #   Only low-level game (Game.startGame, Game.dealCards, Game.fillStack)
    #   or stack methods (Stack.moveMove) should call the functions below
    #   directly.
    #

    def startMoves(self):
        self.moves = Struct(
            state = self.S_PLAY,
            history = [],        # list of lists of atomic moves
            index = 0,
            current = [],        # atomic moves for the current move
        )
        # reset statistics
        self.stats.undo_moves = 0
        self.stats.redo_moves = 0
        self.stats.player_moves = 0
        self.stats.demo_moves = 0
        self.stats.total_moves = 0
        self.stats.quickplay_moves = 0
        self.stats.goto_bookmark_moves = 0

    def __storeMove(self, am):
        if self.S_DEAL <= self.moves.state <= self.S_PLAY:
            self.moves.current.append(am)

    # move type 1
    def moveMove(self, ncards, from_stack, to_stack, frames=-1, shadow=-1):
        assert from_stack and to_stack and from_stack is not to_stack
        assert 0 < ncards <= len(from_stack.cards)
        am = AMoveMove(ncards, from_stack, to_stack, frames, shadow)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    # move type 2
    def flipMove(self, stack):
        assert stack
        am = AFlipMove(stack)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    def singleFlipMove(self, stack):
        # flip with animation (without "moveMove" in this move)
        assert stack
        am = ASingleFlipMove(stack)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    def flipAndMoveMove(self, from_stack, to_stack, frames=-1):
        assert from_stack and to_stack and (from_stack is not to_stack)
        am = AFlipAndMoveMove(from_stack, to_stack, frames)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    # move type 3
    def turnStackMove(self, from_stack, to_stack):
        assert from_stack and to_stack and (from_stack is not to_stack)
        assert len(to_stack.cards) == 0
        am = ATurnStackMove(from_stack, to_stack)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    # move type 4
    def nextRoundMove(self, stack):
        assert stack
        am = ANextRoundMove(stack)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    # move type 5
    def saveSeedMove(self):
        am = ASaveSeedMove(self)
        self.__storeMove(am)
        am.do(self)
        ##self.hints.list = None

    # move type 6
    def shuffleStackMove(self, stack):
        assert stack
        am = AShuffleStackMove(stack, self)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    # move type 7
    def updateStackMove(self, stack, flags):
        assert stack
        am = AUpdateStackMove(stack, flags)
        self.__storeMove(am)
        am.do(self)
        ##self.hints.list = None

    # move type 8
    def flipAllMove(self, stack):
        assert stack
        am = AFlipAllMove(stack)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None

    # move type 9
    def saveStateMove(self, flags):
        am = ASaveStateMove(self, flags)
        self.__storeMove(am)
        am.do(self)
        ##self.hints.list = None

    # for ArbitraryStack
    def singleCardMove(self, from_stack, to_stack, position, frames=-1, shadow=-1):
        am = ASingleCardMove(from_stack, to_stack, position, frames, shadow)
        self.__storeMove(am)
        am.do(self)
        self.hints.list = None


    # Finish the current move.
    def finishMove(self):
        current, moves, stats = self.moves.current, self.moves, self.stats
        if not current:
            return 0
        # invalidate hints
        self.hints.list = None
        # update stats
        if self.demo:
            stats.demo_moves += 1
            if moves.index == 0:
                stats.player_moves = 0  # clear all player moves
        else:
            stats.player_moves += 1
            if moves.index == 0:
                stats.demo_moves = 0    # clear all demo moves
        stats.total_moves += 1

        # try to detect a redo move in order to keep our history
        redo = 0
        if moves.index + 1 < len(moves.history):
            l, m = len(current), moves.history[moves.index]
            if l == len(m):
                for i in range(l):
                    a1 = current[i]
                    a2 = m[i]
                    if a1.__class__ is not a2.__class__ or a1.cmpForRedo(a2) != 0:
                        break
                else:
                    redo = 1
        # add current move to history (which is a list of lists)
        if redo:
            ###print "detected redo:", current
            # overwrite existing entry because minor things like
            # shadow/frames may have changed
            moves.history[moves.index] = current
            moves.index += 1
        else:
            # resize (i.e. possibly shorten list from previous undos)
            moves.history[moves.index : ] = [current]
            moves.index += 1
            assert moves.index == len(moves.history)

        moves.current = []
        self.updateSnapshots()
        # update view
        self.updateText()
        self.updateStatus(moves=(moves.index, self.stats.total_moves))
        self.updateMenus()
        self.updatePlayTime(do_after=0)
        self.updateStuck()
        reset_solver_dialog()

        return 1


    #
    # undo/redo layer
    #

    def undo(self):
        assert self.canUndo()
        assert self.moves.state == self.S_PLAY and len(self.moves.current) == 0
        assert 0 <= self.moves.index <= len(self.moves.history)
        if self.moves.index == 0:
            return
        self.moves.index -= 1
        m = self.moves.history[self.moves.index]
        m = m[:]
        m.reverse()
        self.moves.state = self.S_UNDO
        for atomic_move in m:
            atomic_move.undo(self)
        self.moves.state = self.S_PLAY
        self.stats.undo_moves += 1
        self.stats.total_moves += 1
        self.hints.list = None
        self.updateSnapshots()
        self.updateText()
        self.updateStatus(moves=(self.moves.index, self.stats.total_moves))
        self.updateMenus()
        self.updateStatus(stuck='')
        self.failed_snapshots = []
        reset_solver_dialog()
        

    def redo(self):
        assert self.canRedo()
        assert self.moves.state == self.S_PLAY and len(self.moves.current) == 0
        assert 0 <= self.moves.index <= len(self.moves.history)
        if self.moves.index == len(self.moves.history):
            return
        m = self.moves.history[self.moves.index]
        self.moves.index += 1
        if self.moves.index == len(self.moves.history):
            mm = self.moves.current
        else:
            mm = self.moves.history[self.moves.index]
        self.moves.state = self.S_REDO
        for atomic_move in m:
            atomic_move.redo(self)
        self.moves.state = self.S_PLAY
        self.stats.redo_moves += 1
        self.stats.total_moves += 1
        self.hints.list = None
        self.updateSnapshots()
        self.updateText()
        self.updateStatus(moves=(self.moves.index, self.stats.total_moves))
        self.updateMenus()
        self.updateStuck()
        reset_solver_dialog()


    #
    # subclass hooks
    #

    def setState(self, state):
        # restore saved vars (from undo/redo)
        pass
    def getState(self):
        # save vars (for undo/redo)
        return []


    #
    # bookmarks
    #

    def setBookmark(self, n, confirm=1):
        self.finishMove()       # just in case
        if not self.canSetBookmark():
            return 0
        if confirm < 0:
            confirm = self.app.opt.confirm
        if confirm and self.gsaveinfo.bookmarks.get(n):
            if not self.areYouSure(_("Set bookmark"),
                                   _("Replace existing bookmark %d ?") % (n+1)):
                return 0
        file = StringIO()
        p = Pickler(file, 1)
        try:
            self._dumpGame(p, bookmark=2)
            bm = (file.getvalue(), self.moves.index)
        except:
            pass
        else:
            self.gsaveinfo.bookmarks[n] = bm
            return 1
        return 0

    def gotoBookmark(self, n, confirm=-1, update_stats=1):
        self.finishMove()       # just in case
        bm = self.gsaveinfo.bookmarks.get(n)
        if not bm:
            return
        if confirm < 0:
            confirm = self.app.opt.confirm
        if confirm:
            if not self.areYouSure(_("Goto bookmark"),
                                   _("Goto bookmark %d ?") % (n+1)):
                return
        try:
            s, moves_index = bm
            self.setCursor(cursor=CURSOR_WATCH)
            file = StringIO(s)
            p = Unpickler(file)
            game = self._undumpGame(p, self.app)
            assert game.id == self.id
            # save state for undoGotoBookmark
            self.setBookmark(-1, confirm=0)
        except:
            del self.gsaveinfo.bookmarks[n]
            self.setCursor(cursor=self.app.top_cursor)
        else:
            if update_stats:
                self.stats.goto_bookmark_moves = self.stats.goto_bookmark_moves + 1
                self.gstats.goto_bookmark_moves = self.gstats.goto_bookmark_moves + 1
            self.restoreGame(game, reset=0)
            destruct(game)

    def undoGotoBookmark(self):
        self.gotoBookmark(-1, update_stats=0)


    #
    # load/save
    #

    def loadGame(self, filename):
        if self.changed():
            if not self.areYouSure(_("Open game")): return
        self.finishMove()       # just in case
        game = None
        self.setCursor(cursor=CURSOR_WATCH)
        self.disableMenus()
        try:
            game = self._loadGame(filename, self.app)
            game.gstats.holded = 0
        except AssertionError, ex:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            d = MfxMessageDialog(self.top, title=_("Load game error"), bitmap="error",
                                 text=_("""\
Error while loading game.

Probably the game file is damaged,
but this could also be a bug you might want to report."""))
            traceback.print_exc()
        except UnpicklingError, ex:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            d = MfxExceptionDialog(self.top, ex, title=_("Load game error"),
                                   text=_("Error while loading game"))
        except:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            d = MfxMessageDialog(self.top, title=_("Load game error"),
                                 bitmap="error", text=_("""\
Internal error while loading game.

Please report this bug."""))
            traceback.print_exc()
        else:
            if self.pause:
                # unselect pause-button
                self.app.menubar.mPause()
            self.filename = filename
            game.filename = filename
            # now start the new game
            ##print game.__dict__
            if self.nextGameFlags(game.id) == 0:
                self.endGame()
                self.restoreGame(game)
                destruct(game)
            else:
                self.endGame()
                self.quitGame(game.id, loadedgame=game)


    def saveGame(self, filename, protocol=-1):
        self.finishMove()       # just in case
        self.setCursor(cursor=CURSOR_WATCH)
        try:
            self._saveGame(filename, protocol)
        except Exception, ex:
            self.setCursor(cursor=self.app.top_cursor)
            d = MfxExceptionDialog(self.top, ex, title=_("Save game error"),
                                   text=_("Error while saving game"))
        else:
            self.filename = filename
            self.setCursor(cursor=self.app.top_cursor)


    #
    # low level load/save
    #

    def _loadGame(self, filename, app):
        game = None
        f = None
        try:
            f = open(filename, "rb")
            p = Unpickler(f)
            game = self._undumpGame(p, app)
            game.gstats.loaded = game.gstats.loaded + 1
        finally:
            if f: f.close()
        return game

    def _undumpGame(self, p, app):
        self.updateTime()
        #
        err_txt = _("Invalid or damaged %s save file") % PACKAGE
        #
        def pload(t=None, p=p):
            obj = p.load()
            if isinstance(t, type):
                assert isinstance(obj, t), err_txt
            return obj
        def validate(v, txt):
            if not v:
                raise UnpicklingError(txt)
        #
        package = pload(str)
        validate(package == PACKAGE, err_txt)
        version = pload(str)
        #validate(isinstance(version, str) and len(version) <= 20, err_txt)
        version_tuple = pload(tuple)
        validate(version_tuple >= (1,0), _('''\
Cannot load games saved with
%s version %s''') % (PACKAGE, version))
        game_version = 1
        bookmark = pload(int)
        validate(0 <= bookmark <= 2, err_txt)
        game_version = pload(int)
        validate(game_version > 0, err_txt)
        #
        id = pload(int)
        validate(id > 0, err_txt)
        if id not in GI.PROTECTED_GAMES:
            game = app.constructGame(id)
            if game:
                if not game.canLoadGame(version_tuple, game_version):
                    destruct(game)
                    game = None
        validate(game is not None, _('''\
Cannot load this game from version %s
as the game rules have changed
in the current implementation.''') % version)
        game.version = version
        game.version_tuple = version_tuple
        #
        initial_seed = pload(long)
        if initial_seed <= 32000:
            game.random = LCRandom31(initial_seed)
        else:
            game.random = PysolRandom(initial_seed)
        state = pload()
        game.random.setstate(state)
        #if not hasattr(game.random, "origin"):
        #    game.random.origin = game.random.ORIGIN_UNKNOWN
        game.loadinfo.stacks = []
        game.loadinfo.ncards = 0
        nstacks = pload(int)
        validate(1 <= nstacks, err_txt)
        for i in range(nstacks):
            stack = []
            ncards = pload(int)
            validate(0 <= ncards <= 1024, err_txt)
            for j in range(ncards):
                card_id = pload(int)
                face_up = pload(int)
                stack.append((card_id, face_up))
            game.loadinfo.stacks.append(stack)
            game.loadinfo.ncards = game.loadinfo.ncards + ncards
        validate(game.loadinfo.ncards == game.gameinfo.ncards, err_txt)
        game.loadinfo.talon_round = pload()
        game.finished = pload()
        if 0 <= bookmark <= 1:
            saveinfo = pload(Struct)
            game.saveinfo.__dict__.update(saveinfo.__dict__)
            gsaveinfo = pload(Struct)
            game.gsaveinfo.__dict__.update(gsaveinfo.__dict__)
        moves = pload(Struct)
        game.moves.__dict__.update(moves.__dict__)
        snapshots = pload(list)
        game.snapshots = snapshots
        if 0 <= bookmark <= 1:
            gstats = pload(Struct)
            game.gstats.__dict__.update(gstats.__dict__)
            stats = pload(Struct)
            game.stats.__dict__.update(stats.__dict__)
        game._loadGameHook(p)
        dummy = pload(str)
        validate(dummy == "EOF", err_txt)
        if bookmark == 2:
            # copy back all variables that are not saved
            game.stats = self.stats
            game.gstats = self.gstats
            game.saveinfo = self.saveinfo
            game.gsaveinfo = self.gsaveinfo
        return game

    def _saveGame(self, filename, protocol=-1):
        f = None
        try:
            if not self.canSaveGame():
                raise Exception("Cannot save this game.")
            f = open(filename, "wb")
            p = Pickler(f, protocol)
            self._dumpGame(p)
        finally:
            if f: f.close()

    def _dumpGame(self, p, bookmark=0):
        self.updateTime()
        assert 0 <= bookmark <= 2
        p.dump(PACKAGE)
        p.dump(VERSION)
        p.dump(VERSION_TUPLE)
        p.dump(bookmark)
        p.dump(self.GAME_VERSION)
        p.dump(self.id)
        #
        p.dump(self.random.initial_seed)
        p.dump(self.random.getstate())
        #
        p.dump(len(self.allstacks))
        for stack in self.allstacks:
            p.dump(len(stack.cards))
            for card in stack.cards:
                p.dump(card.id)
                p.dump(card.face_up)
        p.dump(self.s.talon.round)
        p.dump(self.finished)
        if 0 <= bookmark <= 1:
            p.dump(self.saveinfo)
            p.dump(self.gsaveinfo)
        p.dump(self.moves)
        p.dump(self.snapshots)
        if 0 <= bookmark <= 1:
            if bookmark == 0:
                self.gstats.saved = self.gstats.saved + 1
            p.dump(self.gstats)
            p.dump(self.stats)
        self._saveGameHook(p)
        p.dump("EOF")

    #
    # Playing time
    #

    def startPlayTimer(self):
        self.updateStatus(time=None)
        self.stopPlayTimer()
        self.play_timer = after(self.top, PLAY_TIME_TIMEOUT, self.updatePlayTime)

    def stopPlayTimer(self):
        if hasattr(self, 'play_timer') and self.play_timer:
            after_cancel(self.play_timer)
            self.play_timer = None
            self.updatePlayTime(do_after=0)

    def updatePlayTime(self, do_after=1):
        if not self.top: return
        if self.pause or self.finished: return
        if do_after:
            self.play_timer = after(self.top, PLAY_TIME_TIMEOUT, self.updatePlayTime)
        d = time.time() - self.stats.update_time + self.stats.elapsed_time
        self.updateStatus(time=format_time(d))


    #
    # Pause
    #

    def doPause(self):
        if self.finished:
            return
        if self.demo:
            self.stopDemo()
        if not self.pause:
            self.updateTime()
        self.pause = not self.pause
        if self.pause:
            ##self.updateTime()
            self.canvas.hideAllItems()
            n = self.random.initial_seed % len(self.app.gimages.pause)
            self.pause_logo = self.app.gimages.pause[int(n)]
            self.canvas.setTopImage(self.pause_logo)
        else:
            self.stats.update_time = time.time()
            self.updatePlayTime()
            self.canvas.setTopImage(None)
            self.pause_logo = None
            self.canvas.showAllItems()

    #
    # Help
    #

    def showHelp(self, *args):
        if self.preview:
            return
        kw = dict([(args[i], args[i+1]) for i in range(0, len(args), 2)])
        if not kw:
            kw = {'info': '', 'help': ''}
        if 'info' in kw and self.app.opt.statusbar and self.app.opt.num_cards:
            self.app.statusbar.updateText(info=kw['info'])
        if 'help' in kw and self.app.opt.helpbar:
            self.app.helpbar.updateText(info=kw['help'])

    #
    # Piles descriptions
    #

    def showStackDesc(self):
        from pysoltk import StackDesc
        from stack import InitialDealTalonStack
        sd_list = []
        for s in self.allstacks:
            sd = (s.__class__.__name__, s.cap.base_rank, s.cap.dir)
            if sd in sd_list:
                # one of each uniq pile
                continue
            if isinstance(s, InitialDealTalonStack):
                continue
            self.stackdesc_list.append(StackDesc(self, s))
            sd_list.append(sd)

    def deleteStackDesc(self):
        if self.stackdesc_list:
            for sd in self.stackdesc_list:
                sd.delete()
            self.stackdesc_list = []
            return True
        return False

    ## for find_card_dialog
    def canFindCard(self):
        return self.gameinfo.category == GI.GC_FRENCH

    #
    # subclass hooks
    #

    def _restoreGameHook(self, game):
        pass

    def _loadGameHook(self, p):
        pass

    def _saveGameHook(self, p):
        pass

