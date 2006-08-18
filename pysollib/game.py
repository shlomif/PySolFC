## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##


# imports
import time, types
from cStringIO import StringIO

# PySol imports
from mfxutil import Pickler, Unpickler, UnpicklingError
from mfxutil import destruct, Struct, SubclassResponsibility
from mfxutil import UnpicklingError, uclock, usleep
from mfxutil import format_time
from util import get_version_tuple, Timer
from util import ACE, QUEEN, KING
from version import VERSION, VERSION_TUPLE
from settings import PACKAGE, TOOLKIT, TOP_TITLE
from gamedb import GI
from resource import CSI
from pysolrandom import PysolRandom, LCRandom31
from pysoltk import EVENT_HANDLED, EVENT_PROPAGATE
from pysoltk import CURSOR_WATCH, ANCHOR_SW, ANCHOR_SE
from pysoltk import tkname, bind, wm_map
from pysoltk import after, after_idle, after_cancel
from pysoltk import MfxMessageDialog, MfxExceptionDialog
from pysoltk import MfxCanvasText, MfxCanvasImage
from pysoltk import MfxCanvasLine, MfxCanvasRectangle
from pysoltk import Card
from move import AMoveMove, AFlipMove, ATurnStackMove
from move import ANextRoundMove, ASaveSeedMove, AShuffleStackMove
from move import AUpdateStackMove, AFlipAllMove, ASaveStateMove
from move import ACloseStackMove, ASingleCardMove
from hint import DefaultHint
from help import helpAbout

PLAY_TIME_TIMEOUT = 200

# /***********************************************************************
# // Base class for all solitaire games
# //
# // Handles:
# //   load/save
# //   undo/redo (using a move history)
# //   hints/demo
# ************************************************************************/

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
    S_PLAY = 0x30
    S_UNDO = 0x40
    S_REDO = 0x50

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
        ##timer = Timer("Game.create")
        old_busy = self.busy
        self.__createCommon(app)
        self.setCursor(cursor=CURSOR_WATCH)
        #print 'gameid:', self.id
        self.top.wm_title(PACKAGE + " - " + self.getTitleName())
        self.top.wm_iconname(PACKAGE + " - " + self.getTitleName())
        # create the game
        if self.app.intro.progress: self.app.intro.progress.update(step=1)
        ##print timer
        self.createGame()
        ##print timer
        # set some defaults
        self.sg.openstacks = filter(lambda s: s.cap.max_accept >= s.cap.min_accept, self.sg.openstacks)
        self.sg.hp_stacks = filter(lambda s: s.cap.max_move >= 2, self.sg.dropstacks)
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
        if self.app.debug:
            self._checkGame()
        # optimize regions
        self.optimizeRegions()
        # create cards
        ##print timer
        if not self.cards:
            self.cards = self.createCards(progress=self.app.intro.progress)
        self.initBindings()
        ##self.top.bind('<ButtonPress>', self.top._sleepEvent)
        ##self.top.bind('<3>', self.top._sleepEvent)
        ##print timer
        # update display properties
        self.top.wm_geometry("")        # cancel user-specified geometry
        self.canvas.setInitialSize(self.width, self.height)
        if self.app.debug >= 4:
            MfxCanvasRectangle(self.canvas, 0, 0, self.width, self.height,
                               width=2, fill=None, outline='green')
        # restore game geometry
        if self.app.opt.save_games_geometry:
            w, h = self.app.opt.games_geometry.get(self.id, (0, 0))
            w, h = max(w, self.width), max(h, self.height)
            self.canvas.config(width=w, height=h)
        #
        self.stats.update_time = time.time()
        self.busy = old_busy
        ##print timer
        self.showHelp()                 # just in case


    def _checkGame(self):
        class_name = self.__class__.__name__
        if self.s.foundations:
            ncards = 0
            for stack in self.s.foundations:
                ncards += stack.cap.max_cards
            if ncards != self.gameinfo.ncards:
                print 'WARNING: invalid sum of foundations.max_cards:', \
                      class_name, ncards, self.gameinfo.ncards
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
                    if not self.shallHighlightMatch in f:
                        print 'WARNING: shallHighlightMatch is not valid:', \
                              class_name, r.__class__
                    if r.cap.mod == 13 and self.shallHighlightMatch != f[1]:
                        print 'WARNING: shallHighlightMatch is not valid (wrap):', \
                              class_name, r.__class__
                    break


    def initBindings(self):
        # note: a Game is only allowed to bind self.canvas and not to self.top
        ##bind(self.canvas, "<1>", self.clickHandler)
        bind(self.canvas, "<2>", self.clickHandler)
        ##bind(self.canvas, "<3>", self.clickHandler)
        ##bind(self.canvas, "<Double-1>", self.undoHandler)
        ##bind(self.canvas, "<Double-1>", self.undoHandler)
        bind(self.canvas, "<1>", self.undoHandler)
        bind(self.canvas, "<3>", self.redoHandler)
        bind(self.top, '<Unmap>', self._unmapHandler)

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
        ##timer = Timer("Game.createPreview")
        old_busy = self.busy
        self.__createCommon(app)
        self.preview = max(1, self.canvas.preview)
        # create game
        self.createGame()
        ##print timer
        # set some defaults
        self.sg.openstacks = filter(lambda s: s.cap.max_accept >= s.cap.min_accept, self.sg.openstacks)
        self.sg.hp_stacks = filter(lambda s: s.cap.max_move >= 2, self.sg.dropstacks)
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
        if self.app and self.app.toolbar:
            self.app.toolbar.setCursor(cursor=cursor)


    #
    # game creation
    #

    # start a new name
    def newGame(self, random=None, restart=0, autoplay=1):
        self.finished = False
        old_busy, self.busy = self.busy, 1
        self.setCursor(cursor=CURSOR_WATCH)
        self.disableMenus()
        self.reset(restart=restart)
        self.resetGame()
        self.createRandom(random)
        ##print self.random, self.random.__dict__
        self.shuffle()
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        ##print self.app.starttimer
        for stack in self.allstacks:
            stack.updateText()
        self.updateText()
        self.updateStatus(player=self.app.opt.player,
                          gamenumber=self.getGameNumber(format=1),
                          moves=(0, 0),
                          stats=self.app.stats.getStats(self.app.opt.player, self.id))
        # unhide toplevel when we use a progress bar
        if not self.preview:
            wm_map(self.top, maximized=self.app.opt.wm_maximized)
            self.top.busyUpdate()
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
        # 3) move cards to stacks
        assert len(self.allstacks) == len(game.loadinfo.stacks)
        for i in range(len(self.allstacks)):
            for t in game.loadinfo.stacks[i]:
                card_id, face_up = t
                card = self.cards[card_id]
                if face_up:
                    card.showFace()
                else:
                    card.showBack()
                self.allstacks[i].addCard(card)
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
        ##print '--- resetGame ---'
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


    #
    # card creation & shuffling
    #

    # Create all cards for the game.
    def createCards(self, progress=None):
        ##timer = Timer("Game.createCards")
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
        ##print timer
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
        scards = map(lambda item: item[2], sitems)
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
    def _defaultHandler(self):
        self.interruptSleep()
        self.deleteStackDesc()
        if self.demo:
            self.stopDemo()

    def clickHandler(self, event):
        self._defaultHandler()
        self.event_handled = False
        return EVENT_PROPAGATE

    def undoHandler(self, event):
        if not self.app: return EVENT_PROPAGATE # FIXME (GTK)
        self._defaultHandler()
        if self.app.opt.mouse_undo and not self.event_handled:
            self.app.menubar.mUndo()
        self.event_handled = False
        return EVENT_PROPAGATE

    def redoHandler(self, event):
        if not self.app: return EVENT_PROPAGATE # FIXME (GTK)
        self._defaultHandler()
        if self.app.opt.mouse_undo and not self.event_handled:
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
                    continue
                if type(v) is types.StringType:
                    if sb: sb.updateText(gamenumber=v)
                    continue
            if k == "info":
                ##print 'updateStatus info:', v
                if v is None:
                    if sb: sb.updateText(info="")
                    continue
                if type(v) is types.StringType:
                    if sb: sb.updateText(info=v)
                    continue
            if k == "moves":
                if v is None:
                    ##if tb: tb.updateText(moves="Moves\n")
                    if sb: sb.updateText(moves="")
                    continue
                if type(v) is types.TupleType:
                    ##if tb: tb.updateText(moves="Moves\n%d/%d" % v)
                    if sb: sb.updateText(moves="%d/%d" % v)
                    continue
                if type(v) is types.IntType:
                    ##if tb: tb.updateText(moves="Moves\n%d" % v)
                    if sb: sb.updateText(moves="%d" % v)
                    continue
                if type(v) is types.StringType:
                    ##if tb: tb.updateText(moves=v)
                    if sb: sb.updateText(moves=v)
                    continue
            if k == "player":
                if v is None:
                    if tb: tb.updateText(player=_("Player\n"))
                    continue
                if type(v) in types.StringTypes:
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
                if type(v) is types.TupleType:
                    t = "%d: %d/%d" % (v[0]+v[1], v[0], v[1])
                    if sb: sb.updateText(stats=t)
                    continue
            if k == "time":
                if v is None:
                    if sb: sb.updateText(time='')
                if type(v) in types.StringTypes:
                    if sb: sb.updateText(time=v)
                continue
            raise AttributeError, k

    def _unmapHandler(self, event):
        # pause game if root window has been iconified
        if event.widget is self.top and not self.pause:
            self.app.menubar.mPause()


    #
    # sound support
    #

    def playSample(self, name, priority=0, loop=0):
        if self.app.opt.sound_samples.has_key(name) and \
               not self.app.opt.sound_samples[name]:
            return 0
        ##print "playSample:", name, priority, loop
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
            if a in (1, 2, 5):
                self.playSample("deal01", priority=100, loop=loop)
            elif a == 3:
                self.playSample("deal04", priority=100, loop=loop)
            elif a == 4:
                self.playSample("deal08", priority=100, loop=loop)


    #
    # misc. methods
    #

    def areYouSure(self, title=None, text=None, confirm=-1, default=0):
        if self.preview:
            return 1
        if confirm < 0:
            confirm = self.app.opt.confirm
        if confirm:
            if not title: title = PACKAGE
            if not text: text = _("Discard current game ?")
            self.playSample("areyousure")
            d = MfxMessageDialog(self.top, title=title, text=text,
                                 bitmap="question",
                                 strings=(_("&OK"), _("&Cancel")))
            if d.status != 0 or d.button != 0:
                return 0
        return 1

    def notYetImplemented(self):
        # don't used
        d = MfxMessageDialog(self.top, title="Not yet implemented",
                             text="This function is\nnot yet implemented.",
                             bitmap="error")

    # main animation method
    def animatedMoveTo(self, from_stack, to_stack, cards, x, y, tkraise=1, frames=-1, shadow=-1):
        if self.app.opt.animations == 0 or frames == 0:
            return
        if self.app.debug and not self.top.winfo_ismapped():
            return
        # init timer - need a high resolution for this to work
        clock, delay, skip = None, 1, 1
        if self.app.opt.animations >= 2:
            clock = uclock
        SPF = 0.15 / 8          # animation speed - seconds per frame
        if frames < 0:
            frames = 8
        assert frames >= 2
        if self.app.opt.animations == 3:        # slow
            frames = frames * 8
            SPF = SPF / 2
        elif self.app.opt.animations == 4:      # very slow
            frames = frames * 16
            SPF = SPF / 2
        elif self.app.opt.animations == 5:
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
            for s in shadows:
                s.move(mx, my)
            for card in cards:
                card.moveBy(mx, my)
            if i == 1 and shadow and from_stack:
                # create shadows in the first frame
                sx, sy = self.app.images.SHADOW_XOFFSET, self.app.images.SHADOW_YOFFSET
                shadows = from_stack.createShadows(cards, sx, sy)
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

    def winAnimation(self, perfect=0):
        # Stupid animation when you win a game.
        # FIXME: make this interruptible by a key- or mousepress
###        if not self.app.opt.win_animation:
###            return
        if not self.app.opt.animations:
            return
        if self.app.debug and not self.top.winfo_ismapped():
            return
        #self.top.busyUpdate()
        ##self.canvas.after(200)
        self.canvas.update_idletasks()
        old_a = self.app.opt.animations
        if old_a == 0:
            self.app.opt.animations = 1     # timer based
        elif old_a == 4:                    # very slow
            self.app.opt.animations = 3     # slow
        cards = []
        for s in self.allstacks:
            if s is not self.s.talon:
                for c in s.cards:
                    cards.append((c,s))
        # select some random cards
        acards = []
        for i in range(16):
            c, s = self.app.miscrandom.choice(cards)
            if not c in acards:
                acards.append(c)
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
##         if self.app.cardset.type == CSI.TYPE_TAROCK:
##             if rank >= 10:
##                 rank = rank + 1
        return self.app.images.getFace(deck, suit, rank)

    def getCardBackImage(self, deck, suit, rank):
        return self.app.images.getBack(deck, suit, rank)

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
        if self.app.debug >= 2:
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
                    assert not s in d[2]
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
    def dealCards(self, sound=1):
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
        raise SubclassResponsibility

    # the actual hint class (or None)
    Hint_Class = DefaultHint

    def getHintClass(self):
        return self.Hint_Class

    def getStrictness(self):
        return 0

    # can we save outself ?
    def canSaveGame(self):
        return 1
    # can we load this game ?
    def canLoadGame(self, version_tuple, game_version):
        return self.GAME_VERSION == game_version
    # can we set a bookmark ?
    def canSetBookmark(self):
        return self.canSaveGame()

    # can we undo/redo ?
    def canUndo(self):
        return 1
    def canRedo(self):
        return self.canUndo()


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
              self.stats.highlight_cards == 0):
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
                    if ret[0]: # playing time
                        top_msg = _('\nYou have reached\n#%d in the %s of playing time') % (ret[0], TOP_TITLE)
                    if 1 and ret[1]: # moves
                        if top_msg:
                            top_msg += _('\nand #%d in the %s of moves') % (ret[1], TOP_TITLE)
                        else:
                            top_msg = _('\nYou have reached\n#%d in the %s of moves') % (ret[1], TOP_TITLE)
                    if 0 and ret[2]: # total moves
                        if top_msg:
                            top_msg += _('\nand #%d in the %s of total moves') % (ret[1], TOP_TITLE)
                        else:
                            top_msg = _('\nYou have reached\n#%d in the %s of total moves') % (ret[1], TOP_TITLE)
                return top_msg
        elif not demo:
            # only update the session log
            if self.app.opt.update_player_stats:
                if self.gstats.loaded:
                    self.app.stats.updateLog(self.app.opt.player, self, -2)
                elif self.gstats.updated == 0 and self.stats.demo_updated == 0:
                    self.app.stats.updateLog(self.app.opt.player, self, -1)
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
            d = MfxMessageDialog(self.top, title=_("Game won"),
                                 text=_('''
Congratulations, this
was a truly perfect game !

Your playing time is %s
for %d moves.
%s
''') % (time, self.moves.index, top_msg),
                                 strings=(_("&New game"), None, _("&Cancel")),
                                 image=self.app.gimages.logos[5], separatorwidth=2)
        elif status == 1:
            top_msg = self.updateStats()
            time = self.getTime()
            self.finished = True
            self.playSample("gamewon", priority=1000)
            d = MfxMessageDialog(self.top, title=_("Game won"),
                                 text=_('''
Congratulations, you did it !

Your playing time is %s
for %d moves.
%s
''') % (time, self.moves.index, top_msg),
                                 strings=(_("&New game"), None, _("&Cancel")),
                                 image=self.app.gimages.logos[4], separatorwidth=2)
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
            if status == 2:
                self.winAnimation(perfect=1)
            elif status == 1:
                self.winAnimation()
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
    def autoPlay(self, autofaceup=-1, autodrop=-1, autodeal=-1, sound=1):
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
                        s.flipMove()
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

    def _autoDeal(self, sound=1):
        # default: deal a card to the waste if the waste is empty
        w = self.s.waste
        if w and len(w.cards) == 0 and self.canDealCards():
            return self.dealCards(sound=sound)
        return 0

    ## for find_card_dialog
    def highlightCard(self, suit, rank):
        if not self.app:
            return None
        col = self.app.opt.highlight_samerank_colors[1]
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

    def _highlightCards(self, info, sleep=1.5):
        if not info:
            return 0
        if self.pause:
            return 0
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
            r = MfxCanvasRectangle(self.canvas, x1-1, y1-1, x2+1, y2+1,
                                   width=4, fill=None, outline=color)
            if tkraise:
                r.tkraise(c2.item)
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
        color = self.app.opt.highlight_not_matching_color
        width = 6
        x0, y0 = x+width/2-self.canvas.xmargin, y+width/2-self.canvas.ymargin
        x1, y1 = x+w-width-self.canvas.xmargin, y+h-width-self.canvas.ymargin
        r = MfxCanvasRectangle(self.canvas, x0, y0, x1, y1,
                               width=width, fill=None, outline=color)
        self.canvas.update_idletasks()
        self.sleep(self.app.opt.highlight_cards_sleep)
        r.delete()
        self.canvas.update_idletasks()

    def highlightPiles(self, sleep=1.5):
        stackinfo = self.getHighlightPilesStacks()
        if not stackinfo:
            self.highlightNotMatching()
            return 0
        col = self.app.opt.highlight_piles_colors
        hi = []
        for si in stackinfo:
            for s in si[0]:
                pile = s.getPile()
                if pile and len(pile) >= si[1]:
                    hi.append((s, pile[0], pile[-1], col[1]))
        if not hi:
            self.highlightNotMatching()
            return 0
        return self._highlightCards(hi, sleep)

    #
    # highlight matching cards
    #

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return 0

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

    #
    # quick-play
    #

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        # prefer non-empty piles in to_stack
        return (len(to_stack.cards) != 0)

    def _getSpiderQuickPlayScore(self, ncards, from_stack, to_stack):
        # for spider-type stacks
        if to_stack.cards:
            # check suit
            return int(from_stack.cards[-1].suit == to_stack.cards[-1].suit)+1
        return 0

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
            return 0
        if self.random.origin == self.random.ORIGIN_SELECTED:
            return 0
        return 1

    def getGameBalance(self):
        return 0


    #
    # Hint - uses self.getHintClass()
    #

    # compute all hints for the current position
    # this is the only method that actually uses class Hint
    def getHints(self, level, taken_hint=None):
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
            assert to_stack.acceptsCards(from_stack, from_stack.cards[-ncards:])
        if sleep <= 0.0:
            return h
        info = (level == 1) or (level > 1 and self.app.debug >= 3)
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
                              fill=self.app.opt.hintarrow_color,
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
            sleep = self.app.opt.demo_sleep,
            last_deal = [],
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
        if player_moves == 0:
            timeout = 5000
        if 0 and self.app.debug and self.demo.mixed:
            timeout = 1000
        if self.isGameWon():
            finished = 1
            self.stopPlayTimer()
            if not self.top.winfo_ismapped():
                status = 2
            elif player_moves == 0:
                self.playSample("autopilotwon")
                s = self.app.miscrandom.choice((_("&Great"), _("&Cool"), _("&Yeah"), _("&Wow"))) # ??? accelerators
                d = MfxMessageDialog(self.top, title=PACKAGE+_(" Autopilot"),
                                     text=_("\nGame solved in %d moves.\n") % self.moves.index,
                                     image=self.app.gimages.logos[4], strings=(s,),
                                     separatorwidth=2, timeout=timeout)
                status = d.status
                self.finished = True
            else:
                ##s = self.app.miscrandom.choice((_("&OK"), _("&OK")))
                s = _("&OK")
                text = _("\nGame finished\n")
                if self.app.debug:
                    text += "\nplayer_moves: %d\ndemo_moves: %d\n" % (self.stats.player_moves, self.stats.demo_moves)
                d = MfxMessageDialog(self.top, title=PACKAGE+_(" Autopilot"),
                                     text=text, bitmap=bitmap, strings=(s,),
                                     padx=30, timeout=timeout)
                status = d.status
                self.finished = True
        elif finished:
            ##self.stopPlayTimer()
            if not self.top.winfo_ismapped():
                status = 2
            else:
                if player_moves == 0:
                    self.playSample("autopilotlost")
                s = self.app.miscrandom.choice((_("&Oh well"), _("&That's life"), _("&Hmm"))) # ??? accelerators
                d = MfxMessageDialog(self.top, title=PACKAGE+_(" Autopilot"),
                                     text=_("\nThis won't come out...\n"),
                                     bitmap=bitmap, strings=(s,),
                                     padx=30, timeout=timeout)
                status = d.status
        if finished:
            self.updateStats(demo=1)
            if self.demo and status == 2 and not self.app.debug:
                # timeout in dialog
                if self.stats.demo_moves > self.demo.start_demo_moves:
                    # we only increase the splash-screen counter if the last
                    # demo actually made a move
                    self.app.demo_counter =  self.app.demo_counter + 1
                    if self.app.demo_counter % 3 == 0:
                        if self.top.winfo_ismapped():
                            status = helpAbout(self.app, timeout=10000)
            if self.demo and status == 2:
                # timeout in dialog - start another demo
                demo = self.demo
                id = self.id
                if 1 and demo.mixed and self.app.debug:
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
                if 0 and self.app.debug:
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
        if self.app.debug:
            if not self.top.winfo_ismapped():
                sleep = -1.0
        # first try to deal cards to the Waste (unless there was a forced move)
        if not demo.hint or not demo.hint[6]:
            if self._autoDeal(sound=0):
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
            if self.dealCards() == 0:
                return 1
            # do not let games like Klondike and Canfield deal forever
            c = self.s.talon.getCard()
            if c in demo.last_deal:
                # We went through the whole Talon. Give up.
                return 1
            # Note that `None' is a valid entry in last_deal[]
            # (this means that all cards are on the Waste).
            demo.last_deal.append(c)
        elif from_stack == to_stack:
            # a flip-move
            from_stack.flipMove()
            demo.last_deal = []
        else:
            # a move-move
            from_stack.moveMove(ncards, to_stack, frames=-1)
            demo.last_deal = []
        ##print self.moves.index
        return 0

    def createDemoInfoText(self):
        ## TODO - the text placement is not fully ok
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
            font = self.app.getFont("canvas_large")
            self.demo.info_text = MfxCanvasText(self.canvas, ta[1], ta[2], anchor=ta[0],
                                                font=font, text=self.getDemoInfoText())

    def getDemoInfoText(self):
        return self.gameinfo.short_name

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

    # move type 3
    def turnStackMove(self, from_stack, to_stack, update_flags=1):
        assert from_stack and to_stack and (from_stack is not to_stack)
        assert len(to_stack.cards) == 0
        am = ATurnStackMove(from_stack, to_stack, update_flags=update_flags)
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

    # move type 10
    def closeStackMove(self, stack):
        assert stack
        am = ACloseStackMove(stack)
        self.__storeMove(am)
        am.do(self)

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
        # update view
        self.updateText()
        self.updateStatus(moves=(moves.index, self.stats.total_moves))
        self.updateMenus()
        self.updatePlayTime(do_after=0)

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
        self.updateText()
        self.updateStatus(moves=(self.moves.index, self.stats.total_moves))
        self.updateMenus()

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
        self.updateText()
        self.updateStatus(moves=(self.moves.index, self.stats.total_moves))
        self.updateMenus()


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
        except (Exception, UnpicklingError), ex:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            d = MfxExceptionDialog(self.top, ex, title=_("Load game error"),
                                   text=_("Error while loading game"))
        except:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            d = MfxMessageDialog(self.top, title=_("Load game error"), bitmap="error",
                                 text=_("""\
Internal error while loading game.

Please report this bug."""))
        else:
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


    def saveGame(self, filename, binmode=1):
        self.finishMove()       # just in case
        self.setCursor(cursor=CURSOR_WATCH)
        try:
            self._saveGame(filename, binmode)
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

    def _getUndumpVersion(self, version_tuple):
        if version_tuple > (4, 41): return 4
        if version_tuple > (4, 30): return 3
        if version_tuple > (4, 20): return 2
        if version_tuple > (3, 20): return 1
        if version_tuple >= (2, 99): return 0
        return -1

    def _undumpGame(self, p, app):
        self.updateTime()
        #
        err_txt = "Invalid or damaged %s save file" % PACKAGE
        #
        def pload(t=None, p=p):
            obj = p.load()
            if type(t) is types.TypeType:
                assert type(obj) is t, err_txt
            return obj
        #
        package = pload()
        assert type(package) is types.StringType and package == PACKAGE, err_txt
        version = pload()
        assert type(version) is types.StringType and len(version) <= 20, err_txt
        version_tuple = get_version_tuple(version)
        v = self._getUndumpVersion(version_tuple)
        assert v >= 0 and version_tuple <= VERSION_TUPLE, "Cannot load games saved with\n" + PACKAGE + " version " + version
        game_version = 1
        bookmark = 0
        if v >= 2:
            vt = pload()
            assert type(vt) is types.TupleType and vt == version_tuple, err_txt
            bookmark = pload()
            assert type(bookmark) is types.IntType and 0 <= bookmark <= 2, "Incompatible savegame format"
            game_version = pload()
            assert type(game_version) is types.IntType and game_version > 0, err_txt
            if v <= 3:
                bookmark = 0
        #
        id = pload()
        assert type(id) is types.IntType and id > 0, err_txt
        if not GI.PROTECTED_GAMES.has_key(id):
            game = app.constructGame(id)
            if game:
                if not game.canLoadGame(version_tuple, game_version):
                    destruct(game)
                    game = None
        assert game is not None, '''\
Cannot load this game from version %s
as the game rules have changed
in the current implementation.''' % version
        game.version = version
        game.version_tuple = version_tuple
        #
        #game.random = pload()
        #assert isinstance(game.random, PysolRandom), err_txt
        initial_seed = pload()
        assert type(initial_seed) is types.LongType
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
        nstacks = pload()
        #assert type(nstacks) is types.IntType and 1 <= nstacks <= 255, err_txt
        assert type(nstacks) is types.IntType and 1 <= nstacks, err_txt
        for i in range(nstacks):
            stack = []
            ncards = pload()
            assert type(ncards) is types.IntType and 0 <= ncards <= 1024, err_txt
            for j in range(ncards):
                card_id = pload(types.IntType)
                face_up = pload(types.IntType)
                stack.append((card_id, face_up))
            game.loadinfo.stacks.append(stack)
            game.loadinfo.ncards = game.loadinfo.ncards + ncards
        assert game.loadinfo.ncards == game.gameinfo.ncards, err_txt
        game.loadinfo.talon_round = pload()
        game.finished = pload()
        if 0 <= bookmark <= 1:
            if v >= 3:
                saveinfo = pload()
                assert isinstance(saveinfo, Struct), err_txt
                game.saveinfo.__dict__.update(saveinfo.__dict__)
                if v >= 4:
                    gsaveinfo = pload()
                    assert isinstance(gsaveinfo, Struct), err_txt
                    game.gsaveinfo.__dict__.update(gsaveinfo.__dict__)
            elif v >= 1:
                # not used
                talon_base_cards = pload(types.ListType)
        moves = pload()
        assert isinstance(moves, Struct), err_txt
        game.moves.__dict__.update(moves.__dict__)
        if 0 <= bookmark <= 1:
            gstats = pload()
            assert isinstance(gstats, Struct), err_txt
            game.gstats.__dict__.update(gstats.__dict__)
            stats = pload()
            assert isinstance(stats, Struct), err_txt
            game.stats.__dict__.update(stats.__dict__)
        game._loadGameHook(p)
        if v >= 4:
            dummy = pload(types.StringType)
            assert dummy == "EOF", err_txt
        if bookmark == 2:
            # copy back all variables that are not saved
            game.stats = self.stats
            game.gstats = self.gstats
            game.saveinfo = self.saveinfo
            game.gsaveinfo = self.gsaveinfo
        return game

    def _saveGame(self, filename, binmode=1):
        f = None
        try:
            if not self.canSaveGame():
                raise Exception, "Cannot save this game."
            f = open(filename, "wb")
            p = Pickler(f, binmode)
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
        #p.dump(self.random)
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
        if kw.has_key('info') and self.app.opt.statusbar and self.app.opt.num_cards:
            self.app.statusbar.updateText(info=kw['info'])
        if kw.has_key('help') and self.app.opt.helpbar:
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

