# !/usr/bin/env python
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


import math
import time
import traceback
from pickle import Pickler, Unpickler, UnpicklingError

import attr

from pysol_cards.cards import ms_rearrange
from pysol_cards.random import random__int2str

from pysollib.game.dump import pysolDumpGame
from pysollib.gamedb import GI
from pysollib.help import help_about
from pysollib.hint import DefaultHint
from pysollib.mfxutil import Image, ImageTk, USE_PIL
from pysollib.mfxutil import Struct, SubclassResponsibility, destruct
from pysollib.mfxutil import format_time, print_err
from pysollib.mfxutil import uclock, usleep
from pysollib.move import AFlipAllMove
from pysollib.move import AFlipAndMoveMove
from pysollib.move import AFlipMove
from pysollib.move import AMoveMove
from pysollib.move import ANextRoundMove
from pysollib.move import ASaveSeedMove
from pysollib.move import ASaveStateMove
from pysollib.move import AShuffleStackMove
from pysollib.move import ASingleCardMove
from pysollib.move import ASingleFlipMove
from pysollib.move import ATurnStackMove
from pysollib.move import AUpdateStackMove
from pysollib.mygettext import _
from pysollib.mygettext import ungettext
from pysollib.pysolrandom import LCRandom31, PysolRandom, construct_random
from pysollib.pysoltk import CURSOR_WATCH
from pysollib.pysoltk import Card
from pysollib.pysoltk import EVENT_HANDLED, EVENT_PROPAGATE
from pysollib.pysoltk import MfxCanvasLine, MfxCanvasRectangle, MfxCanvasText
from pysollib.pysoltk import MfxExceptionDialog, MfxMessageDialog
from pysollib.pysoltk import after, after_cancel, after_idle
from pysollib.pysoltk import bind, wm_map
from pysollib.settings import DEBUG
from pysollib.settings import PACKAGE, TITLE, TOOLKIT, TOP_SIZE
from pysollib.settings import VERSION, VERSION_TUPLE
from pysollib.struct_new import NewStruct

import random2

import six
from six import BytesIO
from six.moves import range

if TOOLKIT == 'tk':
    from pysollib.ui.tktile.solverdialog import reset_solver_dialog
else:
    from pysollib.pysoltk import reset_solver_dialog

# See: https://github.com/shlomif/PySolFC/issues/159 .
# 'factory=' is absent from older versions.
assert getattr(attr, '__version_info__', (0, 0, 0)) >= (18, 2, 0), (
        "Newer version of https://pypi.org/project/attrs/ is required.")


PLAY_TIME_TIMEOUT = 200
S_PLAY = 0x40

# ************************************************************************
# * Base class for all solitaire games
# *
# * Handles:
# *   load/save
# *   undo/redo (using a move history)
# *   hints/demo
# ************************************************************************


def _updateStatus_process_key_val(tb, sb, k, v):
    if k == "gamenumber":
        if v is None:
            if sb:
                sb.updateText(gamenumber="")
            # self.top.wm_title("%s - %s"
            # % (TITLE, self.getTitleName()))
            return
        if isinstance(v, six.string_types):
            if sb:
                sb.updateText(gamenumber=v)
            # self.top.wm_title("%s - %s %s" % (TITLE,
            # self.getTitleName(), v))
            return
    if k == "info":
        # print 'updateStatus info:', v
        if v is None:
            if sb:
                sb.updateText(info="")
            return
        if isinstance(v, str):
            if sb:
                sb.updateText(info=v)
            return
    if k == "moves":
        if v is None:
            # if tb: tb.updateText(moves="Moves\n")
            if sb:
                sb.updateText(moves="")
            return
        if isinstance(v, tuple):
            # if tb: tb.updateText(moves="Moves\n%d/%d" % v)
            if sb:
                sb.updateText(moves="%d/%d" % v)
            return
        if isinstance(v, int):
            # if tb: tb.updateText(moves="Moves\n%d" % v)
            if sb:
                sb.updateText(moves="%d" % v)
            return
        if isinstance(v, str):
            # if tb: tb.updateText(moves=v)
            if sb:
                sb.updateText(moves=v)
            return
    if k == "player":
        if v is None:
            if tb:
                tb.updateText(player=_("Player\n"))
            return
        if isinstance(v, six.string_types):
            if tb:
                # if self.app.opt.toolbar_size:
                if tb.getSize():
                    tb.updateText(player=_("Player\n") + v)
                else:
                    tb.updateText(player=v)
            return
    if k == "stats":
        if v is None:
            if sb:
                sb.updateText(stats="")
            return
        if isinstance(v, tuple):
            t = "%d: %d/%d" % (v[0]+v[1], v[0], v[1])
            if sb:
                sb.updateText(stats=t)
            return
    if k == "time":
        if v is None:
            if sb:
                sb.updateText(time='')
        if isinstance(v, six.string_types):
            if sb:
                sb.updateText(time=v)
        return
    if k == 'stuck':
        if sb:
            sb.updateText(stuck=v)
        return
    raise AttributeError(k)


def _stats__is_perfect(stats):
    """docstring for _stats__is_perfect"""
    return (stats.undo_moves == 0 and
            stats.goto_bookmark_moves == 0 and
            # stats.quickplay_moves == 0 and
            stats.highlight_piles == 0 and
            stats.highlight_cards == 0 and
            stats.shuffle_moves == 0)


def _highlightCards__calc_item(canvas, delta, cw, ch, s, c1, c2, color):
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
        y2 += ch
        if c2 is s.cards[-1]:  # top card
            x2 += cw
        else:
            if sx0 > 0:
                # left to right
                x2 += sx0
            else:
                # right to left
                x1 += cw
                x2 += cw + sx0
    elif sx0 == 0 and sy0 != 0:
        # vertical stack
        x2 += cw
        if c2 is s.cards[-1]:  # top card
            y2 += ch
        else:
            if sy0 > 0:
                # up to down
                y2 = y2 + sy0
            else:
                # down to up
                y1 += ch
                y2 += ch + sy0
    else:
        x2 += cw
        y2 += ch
        tkraise = True
    # print c1, c2, x1, y1, x2, y2
    x1, x2 = x1-delta[0], x2+delta[1]
    y1, y2 = y1-delta[2], y2+delta[3]
    if TOOLKIT == 'tk':
        r = MfxCanvasRectangle(canvas, x1, y1, x2, y2,
                               width=4, fill=None, outline=color)
        if tkraise:
            r.tkraise(c2.item)
    elif TOOLKIT == 'kivy':
        r = MfxCanvasRectangle(canvas, x1, y1, x2, y2,
                               width=4, fill=None, outline=color)
        if tkraise:
            r.tkraise(c2.item)
    elif TOOLKIT == 'gtk':
        r = MfxCanvasRectangle(canvas, x1, y1, x2, y2,
                               width=4, fill=None, outline=color,
                               group=s.group)
        if tkraise:
            i = s.cards.index(c2)
            for c in s.cards[i+1:]:
                c.tkraise(1)
    return r


@attr.s
class StackGroups(NewStruct):
    dropstacks = attr.ib(factory=list)
    hp_stacks = attr.ib(factory=list)  # for getHightlightPilesStacks()
    openstacks = attr.ib(factory=list)
    reservestacks = attr.ib(factory=list)
    talonstacks = attr.ib(factory=list)

    def to_tuples(self):
        """docstring for to_tuples"""
        self.openstacks = [s for s in self.openstacks
                           if s.cap.max_accept >= s.cap.min_accept]
        self.hp_stacks = [s for s in self.dropstacks
                          if s.cap.max_move >= 2]
        self.openstacks = tuple(self.openstacks)
        self.talonstacks = tuple(self.talonstacks)
        self.dropstacks = tuple(self.dropstacks)
        self.reservestacks = tuple(self.reservestacks)
        self.hp_stacks = tuple(self.hp_stacks)


@attr.s
class StackRegions(NewStruct):
    # list of tuples(stacks, rect)
    info = attr.ib(factory=list)
    # list of stacks in no region
    remaining = attr.ib(factory=list)
    data = attr.ib(factory=list)
    # init info (at the start)
    init_info = attr.ib(factory=list)

    def calc_info(self, xf, yf, widthpad=0, heightpad=0):
        """docstring for calc_info"""
        info = []
        for stacks, rect in self.init_info:
            newrect = (int(round((rect[0] + widthpad) * xf)),
                       int(round((rect[1] + heightpad) * yf)),
                       int(round((rect[2] + widthpad) * xf)),
                       int(round((rect[3] + heightpad) * yf)))
            info.append((stacks, newrect))
        self.info = tuple(info)

    def optimize(self, remaining):
        """docstring for optimize"""
        # sort data by priority
        self.data.sort()
        self.data.reverse()
        # copy (stacks, rect) to info
        self.info = []
        for d in self.data:
            self.info.append((d[2], d[3]))
        self.info = tuple(self.info)
        # determine remaining stacks
        for stacks, rect in self.info:
            for stack in stacks:
                while stack in remaining:
                    remaining.remove(stack)
        self.remaining = tuple(remaining)
        self.init_info = self.info


@attr.s
class GameStacks(NewStruct):
    talon = attr.ib(default=None)
    waste = attr.ib(default=None)
    foundations = attr.ib(factory=list)
    rows = attr.ib(factory=list)  # for getHightlightPilesStacks()
    reserves = attr.ib(factory=list)
    internals = attr.ib(factory=list)

    def to_tuples(self):
        self.foundations = tuple(self.foundations)
        self.rows = tuple(self.rows)
        self.reserves = tuple(self.reserves)
        self.internals = tuple(self.internals)


@attr.s
class GameDrag(NewStruct):
    event = attr.ib(default=None)
    timer = attr.ib(default=None)
    start_x = attr.ib(default=0)
    start_y = attr.ib(default=0)
    index = attr.ib(default=-1)
    stack = attr.ib(default=None)
    shade_stack = attr.ib(default=None)
    shade_img = attr.ib(default=None)
    cards = attr.ib(factory=list)
    canshade_stacks = attr.ib(factory=list)
    noshade_stacks = attr.ib(factory=list)
    shadows = attr.ib(factory=list)


@attr.s
class GameTexts(NewStruct):
    info = attr.ib(default=None)
    help = attr.ib(default=None)
    misc = attr.ib(default=None)
    score = attr.ib(default=None)
    base_rank = attr.ib(default=None)
    list = attr.ib(factory=list)


@attr.s
class GameHints(NewStruct):
    list = attr.ib(default=None)
    index = attr.ib(default=-1)
    level = attr.ib(default=-1)


@attr.s
class GameStatsStruct(NewStruct):
    hints = attr.ib(default=0)                  # number of hints consumed
    # number of highlight piles consumed
    highlight_piles = attr.ib(default=0)
    # number of highlight matching cards consumed
    highlight_cards = attr.ib(default=0)
    # number of highlight same rank consumed
    highlight_samerank = attr.ib(default=0)
    undo_moves = attr.ib(default=0)             # number of undos
    redo_moves = attr.ib(default=0)             # number of redos
    # number of total moves in this game
    total_moves = attr.ib(default=0)
    player_moves = attr.ib(default=0)           # number of moves
    # number of moves while in demo mode
    demo_moves = attr.ib(default=0)
    autoplay_moves = attr.ib(default=0)         # number of moves
    quickplay_moves = attr.ib(default=0)        # number of quickplay moves
    goto_bookmark_moves = attr.ib(default=0)    # number of goto bookmark
    shuffle_moves = attr.ib(default=0)          # number of shuffles (Mahjongg)
    # did this game already update the demo stats ?
    demo_updated = attr.ib(default=0)
    update_time = attr.ib()

    @update_time.default
    def _foofoo(self):
        return time.time()  # for updateTime()
    elapsed_time = attr.ib(default=0.0)
    pause_start_time = attr.ib(default=0.0)

    def _reset_statistics(self):
        """docstring for _reset_stats"""
        self.undo_moves = 0
        self.redo_moves = 0
        self.player_moves = 0
        self.demo_moves = 0
        self.total_moves = 0
        self.quickplay_moves = 0
        self.goto_bookmark_moves = 0


_GLOBAL_U_PLAY = 0


@attr.s
class GameGlobalStatsStruct(NewStruct):
    holded = attr.ib(default=0)                 # is this a holded game
    # number of times this game was loaded
    loaded = attr.ib(default=0)
    # number of times this game was saved
    saved = attr.ib(default=0)
    # number of times this game was restarted
    restarted = attr.ib(default=0)
    goto_bookmark_moves = attr.ib(default=0)    # number of goto bookmark
    # did this game already update the player stats ?
    updated = attr.ib(default=_GLOBAL_U_PLAY)
    start_time = attr.ib()

    @start_time.default
    def _foofoo(self):
        return time.time()  # for updateTime()
    total_elapsed_time = attr.ib(default=0.0)
    start_player = attr.ib(default=None)


@attr.s
class GameWinAnimation(NewStruct):
    timer = attr.ib(default=None)
    images = attr.ib(factory=list)
    tk_images = attr.ib(factory=list)             # saved tk images
    saved_images = attr.ib(factory=dict)          # saved resampled images
    canvas_images = attr.ib(factory=list)         # ids of canvas images
    frame_num = attr.ib(default=0)              # number of the current frame
    width = attr.ib(default=0)
    height = attr.ib(default=0)


@attr.s
class GameMoves(NewStruct):
    current = attr.ib(factory=list)
    history = attr.ib(factory=list)
    index = attr.ib(default=0)
    state = attr.ib(default=S_PLAY)


# used when loading a game
@attr.s
class GameLoadInfo(NewStruct):
    ncards = attr.ib(default=0)
    stacks = attr.ib(factory=list)
    talon_round = attr.ib(default=1)


# global saveinfo survives a game restart
@attr.s
class GameGlobalSaveInfo(NewStruct):
    bookmarks = attr.ib(factory=dict)
    comment = attr.ib(default="")


# Needed for saving a game
@attr.s
class GameSaveInfo(NewStruct):
    stack_caps = attr.ib(factory=list)


_Game_LOAD_CLASSES = [GameGlobalSaveInfo, GameGlobalStatsStruct, GameMoves,
                      GameSaveInfo, GameStatsStruct, ]


class Game(object):
    # for self.gstats.updated
    U_PLAY = _GLOBAL_U_PLAY
    U_WON = -2
    U_LOST = -3
    U_PERFECT = -4

    # for self.moves.state
    S_INIT = 0x00
    S_DEAL = 0x10
    S_FILL = 0x20
    S_RESTORE = 0x30
    S_UNDO = 0x50
    S_PLAY = S_PLAY
    S_REDO = 0x60

    # for loading and saving - subclasses should override if
    # the format for a saved game changed (see also canLoadGame())
    GAME_VERSION = 1

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
        self.stuck = False
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
        self.s = GameStacks()
        self.sg = StackGroups()
        self.regions = StackRegions()
        self.init_size = (0, 0)
        self.center_offset = (0, 0)
        self.event_handled = False      # if click event handled by Stack (???)
        self.reset()

    # main constructor
    def create(self, app):
        # print 'Game.create'
        old_busy = self.busy
        self.__createCommon(app)
        self.setCursor(cursor=CURSOR_WATCH)
        # print 'gameid:', self.id
        self.top.wm_title(TITLE + " - " + self.getTitleName())
        self.top.wm_iconname(TITLE + " - " + self.getTitleName())
        # create the game
        if self.app.intro.progress:
            self.app.intro.progress.update(step=1)
        self.createGame()
        # set some defaults
        self.createSnGroups()
        # convert stackgroups to tuples (speed)
        self.allstacks = tuple(self.allstacks)
        self.sg.to_tuples()
        self.s.to_tuples()
        # init the stack view
        for stack in self.allstacks:
            stack.prepareStack()
            stack.assertStack()
        if self.s.talon:
            assert hasattr(self.s.talon, "round")
            assert hasattr(self.s.talon, "max_rounds")
        if DEBUG:
            self._checkGame()
        self.optimizeRegions()
        # create cards
        if not self.cards:
            self.cards = self.createCards(progress=self.app.intro.progress)
        self.initBindings()
        # self.top.bind('<ButtonPress>', self.top._sleepEvent)
        # self.top.bind('<3>', self.top._sleepEvent)
        # update display properties
        self.canvas.busy = True
        # geometry
        mycond = (self.app.opt.save_games_geometry and
                  self.id in self.app.opt.games_geometry)
        if mycond:
            # restore game geometry
            w, h = self.app.opt.games_geometry[self.id]
            self.canvas.config(width=w, height=h)
        if True and USE_PIL:
            if self.app.opt.auto_scale:
                w, h = self.app.opt.game_geometry
                self.canvas.setInitialSize(w, h, margins=False,
                                           scrollregion=False)
                # self.canvas.config(width=w, height=h)
                # dx, dy = self.canvas.xmargin, self.canvas.ymargin
                # self.canvas.config(scrollregion=(-dx, -dy, dx, dy))
            else:
                if not mycond:
                    w = int(round(self.width * self.app.opt.scale_x))
                    h = int(round(self.height * self.app.opt.scale_y))
                    self.canvas.setInitialSize(w, h)
                self.top.wm_geometry("")    # cancel user-specified geometry
            # preserve texts positions
            for t in ('info', 'help', 'misc', 'score', 'base_rank'):
                item = getattr(self.texts, t)
                if item:
                    coords = self.canvas.coords(item)
                    setattr(self.init_texts, t, coords)
            #
            for item in self.texts.list:
                coords = self.canvas.coords(item)
                self.init_texts.list.append(coords)
            # resize
            self.resizeGame()
            # fix coords of cards (see self.createCards)
            x, y = self.s.talon.x, self.s.talon.y
            for c in self.cards:
                c.moveTo(x, y)
        else:
            # no PIL
            self.canvas.setInitialSize(self.width, self.height)
            self.top.wm_geometry("")    # cancel user-specified geometry
        # done; update view
        self.top.update_idletasks()
        self.canvas.busy = False
        if DEBUG >= 4:
            MfxCanvasRectangle(self.canvas, 0, 0, self.width, self.height,
                               width=2, fill=None, outline='green')
        #
        self.stats.update_time = time.time()
        self.showHelp()                 # just in case
        hint_class = self.getHintClass()
        if hint_class is not None:
            self.Stuck_Class = hint_class(self, 0)
        self.busy = old_busy

    def _checkGame(self):
        class_name = self.__class__.__name__
        if self.s.foundations:
            ncards = 0
            for stack in self.s.foundations:
                ncards += stack.cap.max_cards
            if ncards != self.gameinfo.ncards:
                print_err('invalid sum of foundations.max_cards: '
                          '%s: %s %s' %
                          (class_name, ncards, self.gameinfo.ncards),
                          2)
        if self.s.rows:
            from pysollib.stack import AC_RowStack, UD_AC_RowStack, \
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
        if self.s.talon.max_rounds > 1 and self.s.talon.texts.rounds is None:
            print_err('max_rounds > 1, but talon.texts.rounds is None: '
                      '%s' % class_name, 2)
        elif (self.s.talon.max_rounds <= 1 and
              self.s.talon.texts.rounds is not None):
            print_err('max_rounds <= 1, but talon.texts.rounds is not None: '
                      '%s' % class_name, 2)

    def _calcMouseBind(self, binding_format):
        """docstring for _calcMouseBind"""
        return self.app.opt.calcCustomMouseButtonsBinding(binding_format)

    def initBindings(self):
        # note: a Game is only allowed to bind self.canvas and not to self.top
        # bind(self.canvas, "<Double-1>", self.undoHandler)
        bind(self.canvas,
             self._calcMouseBind("<{mouse_button1}>"), self.undoHandler)
        bind(self.canvas,
             self._calcMouseBind("<{mouse_button2}>"), self.dropHandler)
        bind(self.canvas,
             self._calcMouseBind("<{mouse_button3}>"), self.redoHandler)
        bind(self.canvas, '<Unmap>', self._unmapHandler)
        bind(self.canvas, '<Configure>', self._configureHandler, add=True)

    def __createCommon(self, app):
        self.busy = 1
        self.app = app
        self.top = app.top
        self.canvas = app.canvas
        self.filename = ""
        self.drag = GameDrag()
        if self.gstats.start_player is None:
            self.gstats.start_player = self.app.opt.player
        # optional MfxCanvasText items
        self.texts = GameTexts()
        # initial position of the texts
        self.init_texts = GameTexts()

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
        self.hints = GameHints()
        self.saveinfo = GameSaveInfo()
        self.loadinfo = GameLoadInfo()
        self.snapshots = []
        self.failed_snapshots = []
        # local statistics are reset on each game restart
        self.stats = GameStatsStruct()
        self.startMoves()
        if restart:
            return
        # global statistics survive a game restart
        self.gstats = GameGlobalStatsStruct()
        self.gsaveinfo = GameGlobalSaveInfo()
        # some vars for win animation
        self.win_animation = GameWinAnimation()

    def getTitleName(self):
        return self.app.getGameTitleName(self.id)

    def getGameNumber(self, format):
        s = self.random.getSeedAsStr()
        if format:
            return "# " + s
        return s

    # this is called from within createGame()
    def setSize(self, w, h):
        self.width, self.height = int(round(w)), int(round(h))
        dx, dy = self.canvas.xmargin, self.canvas.ymargin
        self.init_size = self.width+2*dx, self.height+2*dy

    def setCursor(self, cursor):
        if self.canvas:
            self.canvas.config(cursor=cursor)
            # self.canvas.update_idletasks()
        # if self.app and self.app.toolbar:
        # self.app.toolbar.setCursor(cursor=cursor)

    def newGame(self, random=None, restart=0, autoplay=1, shuffle=True,
                dealer=None):
        self.finished = False
        self.stuck = False
        old_busy, self.busy = self.busy, 1
        self.setCursor(cursor=CURSOR_WATCH)
        self.stopWinAnimation()
        self.disableMenus()
        if shuffle:
            self.redealAnimation()
        self.reset(restart=restart)
        self.resetGame()
        self.createRandom(random)
        if shuffle:
            self.shuffle()
            assert len(self.s.talon.cards) == self.gameinfo.ncards
        for stack in self.allstacks:
            stack.updateText()
        self.updateText()
        self.updateStatus(
            player=self.app.opt.player,
            gamenumber=self.getGameNumber(format=1),
            moves=(0, 0),
            stats=self.app.stats.getStats(
                self.app.opt.player,
                self.id),
            stuck='')
        reset_solver_dialog()
        # unhide toplevel when we use a progress bar
        if not self.preview:
            wm_map(self.top, maximized=self.app.opt.wm_maximized)
            self.top.busyUpdate()
        if TOOLKIT == 'gtk':
            # FIXME
            if self.top:
                self.top.update_idletasks()
                self.top.show_now()
        self.stopSamples()
        self.moves.state = self.S_INIT
        if dealer:
            dealer()
        else:
            if not self.preview:
                self.resizeGame()
            self.startGame()
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
            # print stack_id, cap
            self.allstacks[stack_id].cap.update(cap.__dict__)
        # 5) subclass settings
        self._restoreGameHook(game)
        # 6) update view
        for stack in self.allstacks:
            stack.updateText()
        self.updateText()
        self.updateStatus(
            player=self.app.opt.player,
            gamenumber=self.getGameNumber(format=1),
            moves=(self.moves.index, self.stats.total_moves),
            stats=self.app.stats.getStats(self.app.opt.player, self.id))
        if not self.preview:
            self.updateMenus()
            wm_map(self.top, maximized=self.app.opt.wm_maximized)
        self.setCursor(cursor=self.app.top_cursor)
        self.stats.update_time = time.time()
        self.busy = old_busy
        # wait for canvas is mapped
        after(self.top, 200, self._configureHandler)
        if TOOLKIT == 'gtk':
            # FIXME
            if self.top:
                self.top.update_idletasks()
                self.top.show_now()
        self.startPlayTimer()

    def restoreGameFromBookmark(self, bookmark):
        old_busy, self.busy = self.busy, 1
        file = BytesIO(bookmark)
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
            f |= 1
        if self.app.nextgame.cardset is not self.app.cardset:
            f |= 2
        if random is not None:
            if ((random.__class__ is not self.random.__class__) or
                    random.initial_seed != self.random.initial_seed):
                f |= 16
        return f

    # quit to outer mainloop in class App, possibly restarting
    # with another game from there
    def quitGame(self, id=0, random=None, loadedgame=None,
                 startdemo=0, bookmark=0, holdgame=0):
        self.updateTime()
        if bookmark:
            id, random = self.id, self.random
            f = BytesIO()
            self._dumpGame(Pickler(f, 1), bookmark=1)
            self.app.nextgame.bookmark = f.getvalue()
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
                self.gstats.restarted += 1
            return
        self.updateStats()
        stats = self.app.stats
        if self.shallUpdateBalance():
            b = self.getGameBalance()
            if b:
                stats.total_balance[self.id] = \
                    stats.total_balance.get(self.id, 0) + b
                stats.session_balance[self.id] = \
                    stats.session_balance.get(self.id, 0) + b
                stats.gameid_balance = stats.gameid_balance + b

    def restartGame(self):
        self.endGame(restart=1)
        self.newGame(restart=1, random=self.random)

    def resizeImages(self, manually=False):
        self.center_offset = (0, 0)
        if self.canvas.winfo_ismapped():
            # apparent size of canvas
            vw = self.canvas.winfo_width()
            vh = self.canvas.winfo_height()
        else:
            # we have no a real size of canvas
            # (winfo_width / winfo_reqwidth)
            # so we use a saved size
            vw, vh = self.app.opt.game_geometry
            if not vw:
                # first run of the game
                return 1, 1, 1, 1
        # requested size of canvas (createGame -> setSize)
        iw, ih = self.init_size

        # resizing images and cards
        if (self.app.opt.auto_scale or
                (self.app.opt.spread_stacks and not manually)):
            # calculate factor of resizing
            xf = float(vw)/iw
            yf = float(vh)/ih
            if (self.app.opt.preserve_aspect_ratio
                    and not self.app.opt.spread_stacks):
                xf = yf = min(xf, yf)
        else:
            xf, yf = self.app.opt.scale_x, self.app.opt.scale_y
        self.center_offset = self.getCenterOffset(vw, vh, iw, ih, xf, yf)
        if (not self.app.opt.spread_stacks or manually):
            # images
            self.app.images.resize(xf, yf, resample=self.app.opt.resampling)
        # cards
        for card in self.cards:
            card.update(card.id, card.deck, card.suit, card.rank, self)
        return xf, yf, self.app.images._xfactor, self.app.images._yfactor

    def getCenterOffset(self, vw, vh, iw, ih, xf, yf):
        if (not self.app.opt.center_layout or self.app.opt.spread_stacks or
                (self.app.opt.auto_scale and not
                 self.app.opt.preserve_aspect_ratio)):
            return 0, 0
        if ((vw > iw and vh > ih) or self.app.opt.auto_scale):
            return (vw / xf - iw) / 2, (vh / yf - ih) / 2
        elif (vw >= iw and vh < ih):
            return (vw / xf - iw) / 2, 0
        elif (vw < iw and vh >= ih):
            return 0, (vh / yf - ih) / 2
        else:
            return 0, 0

    def resizeGame(self, card_size_manually=False):
        # if self.busy:
        # return
        if not USE_PIL:
            return
        self.deleteStackDesc()
        xf, yf, xf0, yf0 = \
            self.resizeImages(manually=card_size_manually)
        cw, ch = self.center_offset[0], self.center_offset[1]
        for stack in self.allstacks:

            if (self.app.opt.spread_stacks):
                # Do not move Talons
                # (because one would need to reposition
                # 'empty cross' and 'redeal' figures)
                # But in that case,
                # games with talon not placed top-left corner
                # will get it misplaced when auto_scale
                # e.g. Suit Elevens
                # => player can fix that issue by setting auto_scale false
                if stack is self.s.talon:
                    # stack.init_coord=(x, y)
                    if card_size_manually:
                        stack.resize(xf, yf0, widthpad=cw, heightpad=ch)
                    else:
                        stack.resize(xf0, yf0, widthpad=cw, heightpad=ch)
                else:
                    stack.resize(xf, yf0, widthpad=cw, heightpad=ch)
            else:
                stack.resize(xf, yf, widthpad=cw, heightpad=ch)
            stack.updatePositions()
        self.regions.calc_info(xf, yf, widthpad=cw, heightpad=ch)
        # texts
        for t in ('info', 'help', 'misc', 'score', 'base_rank'):
            init_coord = getattr(self.init_texts, t)
            if init_coord:
                item = getattr(self.texts, t)
                x, y = int(round((init_coord[0] + cw) * xf)), \
                    int(round((init_coord[1] + ch) * yf))
                self.canvas.coords(item, x, y)
        for i in range(len(self.texts.list)):
            init_coord = self.init_texts.list[i]
            item = self.texts.list[i]
            x, y = int(round((init_coord[0] + cw) * xf)), \
                int(round((init_coord[1] + ch) * yf))
            self.canvas.coords(item, x, y)

    def createRandom(self, random):
        if random is None:
            if isinstance(self.random, PysolRandom):
                state = self.random.getstate()
                self.app.gamerandom.setstate(state)
            # we want at least 17 digits
            seed = self.app.gamerandom.randrange(
                int('10000000000000000'),
                PysolRandom.MAX_SEED
            )
            self.random = PysolRandom(seed)
            self.random.origin = self.random.ORIGIN_RANDOM
        else:
            self.random = random
            self.random.reset()

    def enterState(self, state):
        old_state = self.moves.state
        if state < old_state:
            self.moves.state = state
        return old_state

    def leaveState(self, old_state):
        self.moves.state = old_state

    def getSnapshotHash(self):
        # generate hash (unique string) of current move
        sn = []
        for stack in self.allstacks:
            s = []
            for card in stack.cards:
                s.append('%d%03d%d' % (card.suit, card.rank, card.face_up))
            sn.append(''.join(s))
        sn = '-'.join(sn)
        return sn

    def getSnapshot(self):
        # optimisation
        sn = hash(self.getSnapshotHash())
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
        sg = list(sg.values())
        self.sn_groups = sg

    def updateSnapshots(self):
        sn = self.getSnapshot()
        if sn in self.snapshots:
            # self.updateStatus(snapshot=True)
            pass
        else:
            self.snapshots.append(sn)
            # self.updateStatus(snapshot=False)

    # Create all cards for the game.
    def createCards(self, progress=None):
        gi = self.gameinfo
        pstep = 0
        if progress:
            pstep = (100.0 - progress.percent) / gi.ncards
        cards = []
        id = [0]
        x, y = self.s.talon.x, self.s.talon.y
        for deck in range(gi.decks):
            def _iter_ranks(ranks, suit):
                for rank in ranks:
                    card = self._createCard(id[0], deck, suit, rank, x=x, y=y)
                    if card is None:
                        continue
                    cards.append(card)
                    id[0] += 1
                    if progress:
                        progress.update(step=pstep)
            for suit in gi.suits:
                _iter_ranks(gi.ranks, suit)
            _iter_ranks(gi.trumps, len(gi.suits))
        if progress:
            progress.update(percent=100)
        assert len(cards) == gi.ncards
        return cards

    def _createCard(self, id, deck, suit, rank, x, y):
        return Card(id, deck, suit, rank, game=self, x=x, y=y)

    # shuffle cards
    def shuffle(self):
        # get a fresh copy of the original game-cards
        cards = list(self.cards)
        # init random generator
        if isinstance(self.random, LCRandom31):
            cards = ms_rearrange(cards)
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
        n = self.gameinfo.ncards // self.gameinfo.decks
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

    def _shuffleHookMoveSorter(self, cards, cb, ncards):
        extracted, i, new = [], len(cards), []
        for c in cards:
            select, ord_ = cb(c)
            if select:
                extracted.append((ord_, i, c))
                if len(extracted) >= ncards:
                    new += cards[(len(cards)-i+1):]
                    break
            else:
                new.append(c)
            i -= 1
        return new, [x[2] for x in reversed(sorted(extracted))]

    def _finishDrag(self):
        if self.demo:
            self.stopDemo()
        if self.busy:
            return 1
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
        if self.busy:
            return 1
        if self.drag.stack:
            self.drag.stack.cancelDrag()
        return 0

    def updateMenus(self):
        if not self.preview:
            self.app.menubar.updateMenus()

    def disableMenus(self):
        if not self.preview:
            self.app.menubar.disableMenus()

    def _defaultHandler(self, event):
        if not self.app:
            return True                 # FIXME (GTK)
        if not self.app.opt.mouse_undo:
            return True
        if self.pause:
            self.app.menubar.mPause()
            return True
        if not self.event_handled and self.stopWinAnimation():
            return True
        self.interruptSleep()
        if self.deleteStackDesc():
            # delete piles descriptions
            return True
        if self.demo:
            self.stopDemo()
            return True
        if not self.event_handled and self.drag.stack:
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
        for k, v in six.iteritems(kw):
            _updateStatus_process_key_val(tb, sb, k, v)

    def _unmapHandler(self, event):
        # pause game if root window has been iconified
        if self.app and not self.pause:
            self.app.menubar.mPause()

    _resizeHandlerID = None

    def _resizeHandler(self):
        self._resizeHandlerID = None
        self.resizeGame()

    def _configureHandler(self, event=None):
        if False:  # if not USE_PIL:
            return
        if not self.app:
            return
        if not self.canvas:
            return
        if (not self.app.opt.auto_scale and
                not self.app.opt.spread_stacks and
                not self.app.opt.center_layout):
            return
        if self.preview:
            return
        if self._resizeHandlerID:
            self.canvas.after_cancel(self._resizeHandlerID)
        self._resizeHandlerID = self.canvas.after(250, self._resizeHandler)

    def playSample(self, name, priority=0, loop=0):

        if name.startswith('deal'):
            sampleopt = 'deal'
        elif name not in self.app.opt.sound_samples:
            sampleopt = 'extra'
        else:
            sampleopt = name

        if sampleopt in self.app.opt.sound_samples and \
           not self.app.opt.sound_samples[sampleopt]:
            return 0
        if self.app.audio:
            return self.app.audio.playSample(
                name,
                priority=priority,
                loop=loop)
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
        if self.app.audio and self.app.opt.sound:
            if a in (1, 2, 3, 10):
                self.playSample("deal01", priority=100, loop=loop)
            elif a == 4:
                self.playSample("deal04", priority=100, loop=loop)
            elif a == 5:
                self.playSample("deal08", priority=100, loop=loop)

    def areYouSure(self, title=None, text=None, confirm=-1, default=0):
        if TOOLKIT == 'kivy':
            return True
        if self.preview:
            return True
        if confirm < 0:
            confirm = self.app.opt.confirm
        if confirm:
            if not title:
                title = TITLE
            if not text:
                text = _("Discard current game?")
            self.playSample("areyousure")
            d = MfxMessageDialog(self.top, title=title, text=text,
                                 bitmap="question",
                                 strings=(_("&OK"), _("&Cancel")))
            if d.status != 0 or d.button != 0:
                return False
        return True

    def notYetImplemented(self):
        MfxMessageDialog(self.top, title="Not yet implemented",
                         text="This function is\nnot yet implemented.",
                         bitmap="error")

    # main animation method
    def animatedMoveTo(self, from_stack, to_stack, cards, x, y,
                       tkraise=1, frames=-1, shadow=-1):
        # available values of app.opt.animations:
        # 0 - without animations
        # 1 - very fast (without timer)
        # 2 - fast (default)
        # 3 - medium (2/3 of fast speed)
        # 4 - slow (1/4 of fast speed)
        # 5 - very slow (1/8 of fast speed)
        # 10 - used internally in game preview
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
            frames *= 3
            SPF /= 2
        elif self.app.opt.animations == 4:      # slow
            frames *= 8
            SPF /= 2
        elif self.app.opt.animations == 5:      # very slow
            frames *= 16
            SPF /= 2
        elif self.app.opt.animations == 10:
            # this is used internally in game preview to speed up
            # the initial dealing
            # if self.moves.state == self.S_INIT and frames > 4:
            #     frames //= 2
            return
        if shadow < 0:
            shadow = self.app.opt.shadow
        shadows = ()
        # start animation
        if TOOLKIT == 'kivy':
            c0 = cards[0]
            dx, dy = (x - c0.x), (y - c0.y)
            for card in cards:
                base = float(self.app.opt.animations)
                duration = base*0.1
                card.animatedMove(dx, dy, duration)
            return

        if tkraise:
            for card in cards:
                card.tkraise()
        c0 = cards[0]
        dx, dy = (x - c0.x) / float(frames), (y - c0.y) / float(frames)
        tx, ty = 0, 0
        i = 1
        if clock:
            starttime = clock()
        while i < frames:
            mx, my = int(round(dx * i)) - tx, int(round(dy * i)) - ty
            tx, ty = tx + mx, ty + my
            if i == 1 and shadow and from_stack:
                # create shadows in the first frame
                sx, sy = self.app.images.SHADOW_XOFFSET, \
                    self.app.images.SHADOW_YOFFSET
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
                    # print "Delay frame", i, sleep
                    usleep(sleep)
                elif skip and sleep <= -0.75*SPF:
                    # we're slow - skip 1 or 2 frames
                    # print "Skip frame", i, sleep
                    step += 1
                    if frames > 4 and sleep < -1.5*SPF:
                        step += 1
                # print i, step, mx, my; time.sleep(0.5)
            i += step
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

        SPF = 0.1/8                     # animation speed - seconds per frame
        frames = 4.0                    # num frames for each step
        if self.app.opt.animations == 3:  # medium
            SPF = 0.1/8
            frames = 7.0
        elif self.app.opt.animations == 4:  # slow
            SPF = 0.1/8
            frames = 12.0
        elif self.app.opt.animations == 5:  # very slow
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
            # ascent_dx, ascent_dy = 0, self.app.images.SHADOW_YOFFSET/frames
            ascent_dx, ascent_dy = 0, h/10.0/frames
            min_size = w/10
            shrink_dx = (w-min_size) / (frames-1)
            shrink_dy = 0
        elif dest_y == 0:
            # move to left/right waste
            # ascent_dx, ascent_dy = 0, self.app.images.SHADOW_YOFFSET/frames
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
            t = (SPF-(uclock()-starttime))*1000   # milliseconds
            if t > 0:
                usleep(t/1000)
                # else:
                # nframe += 1
                # xpos += d_x
                # ypos += d_y

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
            t = (SPF-(uclock()-starttime))*1000  # milliseconds
            if t > 0:
                usleep(t/1000)
                # else:
                # nframe += 1
                # xpos += d_x
                # ypos += d_y

        card.moveTo(x1, y1)
        # canvas.update_idletasks()
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
        saved_images = self.win_animation.saved_images  # cached images
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
        r = radius + (radius / 3.0) * math.sin(f * 2.0 * math.pi)
        img_index = 0

        for im in images:

            iw, ih = im.size

            ang = 2.0 * math.pi * img_index / n_images - f * 2.0 * math.pi
            xpos = x0 + int(xmid + r * math.cos(ang) - iw / 2.0)
            ypos = y0 + int(ymid + r * math.sin(ang) - ih / 2.0)

            k = (math.sin if img_index & 1 else math.cos)(f * 2.0 * math.pi)
            k = max(0.4, k ** 2)
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
        self.win_animation.frame_num = \
            (self.win_animation.frame_num+1) % CYCLE_LEN
        self.win_animation.tk_images = tmp_tk_images
        canvas.update_idletasks()
        # loop
        t = FRAME_DELAY-int((uclock()-starttime)*1000)
        if t > 0:
            self.win_animation.timer = after(canvas, t, self.winAnimationEvent)
        else:
            self.win_animation.timer = after_idle(
                canvas,
                self.winAnimationEvent)

    def stopWinAnimation(self):
        if self.win_animation.timer:
            after_cancel(self.win_animation.timer)  # stop loop
            self.win_animation.timer = None
            self.canvas.delete(*self.win_animation.canvas_images)
            self.win_animation.canvas_images = []
            self.win_animation.tk_images = []  # delete all images
            self.saved_images = {}
            self.canvas.showAllItems()
            return True
        return False

    def winAnimation(self, perfect=0):
        if self.preview:
            return
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
        for i in range(ncards):
            c = self.app.miscrandom.choice(cards)
            scards.append(c)
            cards.remove(c)
        for c in scards:
            self.win_animation.images.append(c._face_image._pil_image)
        # compute visible geometry
        self.win_animation.width = self.canvas.winfo_width()
        self.win_animation.height = self.canvas.winfo_height()
        # run win animation in background
        # after_idle(self.canvas, self.winAnimationEvent)
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
                    cards.append((c, s))
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
                scards.remove((c, s))
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
                self.animatedMoveTo(
                    s, None, [c], w//2, h//2, tkraise=0, shadow=0)
                self.animatedMoveTo(s, None, [c], sx, sy, tkraise=0, shadow=0)
            else:
                c.moveTo(sx, sy)
            cards.remove(t)
        self.app.opt.animations = old_a

    def sleep(self, seconds):
        # if 0 and self.canvas:
        # self.canvas.update_idletasks()
        if seconds > 0:
            if self.top:
                self.top.interruptSleep()
                self.top.sleep(seconds)
            else:
                time.sleep(seconds)

    def interruptSleep(self):
        if self.top:
            self.top.interruptSleep()

    def getCardFaceImage(self, deck, suit, rank):
        return self.app.images.getFace(deck, suit, rank)

    def getCardBackImage(self, deck, suit, rank):
        return self.app.images.getBack()

    def getCardShadeImage(self):
        return self.app.images.getShade()

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
            if cx >= rect[0] and cx < rect[2] \
                    and cy >= rect[1] and cy < rect[3]:
                return self._getClosestStack(cx, cy, stacks, dragstack)
        return self._getClosestStack(cx, cy, self.regions.remaining, dragstack)

    # define a region for use in getClosestStack()
    def setRegion(self, stacks, rect, priority=0):
        assert len(stacks) > 0
        assert len(rect) == 4 and rect[0] < rect[2] and rect[1] < rect[3]
        if DEBUG >= 2:
            xf, yf = self.app.images._xfactor, self.app.images._yfactor
            MfxCanvasRectangle(self.canvas,
                               xf*rect[0], yf*rect[1], xf*rect[2], yf*rect[3],
                               width=2, fill=None, outline='red')
        for s in stacks:
            assert s and s in self.allstacks
            # verify that the stack lies within the rectangle
            r = rect
            if USE_PIL:
                x, y = s.init_coord
            else:
                x, y = s.x, s.y
            assert r[0] <= x <= r[2] and r[1] <= y <= r[3]
            # verify that the stack is not already in another region
            # with the same priority
            for d in self.regions.data:
                if priority == d[0]:
                    assert s not in d[2]
        # add to regions
        self.regions.data.append(
            (priority, -len(self.regions.data), tuple(stacks), tuple(rect)))

    # as getClosestStack() is called within the mouse motion handler
    # event it is worth optimizing a little bit
    def optimizeRegions(self):
        return self.regions.optimize(list(self.sg.openstacks))

    def getInvisibleCoords(self):
        # for InvisibleStack, etc
        # x, y = -500, -500 - len(game.allstacks)
        cardw, cardh = self.app.images.CARDW, self.app.images.CARDH
        xoffset = self.app.images.CARD_XOFFSET
        yoffset = self.app.images.CARD_YOFFSET
        x = cardw + xoffset + self.canvas.xmargin
        y = cardh + yoffset + self.canvas.ymargin
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

    def canSaveGame(self):
        return True

    def canLoadGame(self, version_tuple, game_version):
        return self.GAME_VERSION == game_version

    def canSetBookmark(self):
        return self.canSaveGame()

    def canUndo(self):
        return True

    def canRedo(self):
        return self.canUndo()

    # Mahjongg
    def canShuffle(self):
        return False

    # game changed - i.e. should we ask the player to discard the game
    def changed(self, restart=False):
        if self.gstats.updated < 0:
            return 0                    # already won or lost
        # if self.gstats.loaded > 0:
        #     return 0                    # loaded games account for no stats
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
        if (not won or (self.stats.hints > 0 and not self.app.opt.free_hint)
                or self.stats.demo_moves > 0):
            # sorry, you lose
            return won, 0, self.U_LOST
        if _stats__is_perfect(self.stats) and self.stats.hints < 1:
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
                ret = self.app.stats.updateStats(
                    self.app.opt.player, self, status)
                self.updateStatus(
                    stats=self.app.stats.getStats(
                        self.app.opt.player, self.id))
                top_msg = ''
                if ret:
                    if ret[0] and ret[1]:
                        top_msg = _(
                            '\nYou have reached\n# %(timerank)d in the top ' +
                            '%(tops)d of playing time\nand # %(movesrank)d ' +
                            'in the top %(tops)d of moves.') % {
                                'timerank': ret[0],
                                'movesrank': ret[1],
                                'tops': TOP_SIZE}
                    elif ret[0]:        # playing time
                        top_msg = _(
                            '\nYou have reached\n# %(timerank)d in the top ' +
                            '%(tops)d of playing time.') % {
                                'timerank': ret[0],
                                'tops': TOP_SIZE}
                    elif ret[1]:        # moves
                        top_msg = _(
                            '\nYou have reached\n# %(movesrank)d in the top ' +
                            '%(tops)s of moves.') % {
                                'movesrank': ret[1],
                                'tops': TOP_SIZE}
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
            return False
        self.finishMove()       # just in case
        if self.preview:
            return True
        if self.finished:
            return True
        if self.demo:
            return status
        if TOOLKIT == 'kivy':
            if not self.app.opt.display_win_message:
                return True
            self.top.waitAnimation()
        if status == 2:
            top_msg = self.updateStats()
            time = self.getTime()
            self.finished = True
            self.playSample("gameperfect", priority=1000)
            self.winAnimation(perfect=1)
            text = ungettext('Your playing time is %(time)s\nfor %(n)d move.',
                             'Your playing time is %(time)s\nfor %(n)d moves.',
                             self.moves.index)
            text = text % {'time': time, 'n': self.moves.index}
            congrats = _('Congratulations, this\nwas a truly perfect game!')
            d = MfxMessageDialog(
                self.top, title=_("Game won"),
                text='\n' + congrats + '\n\n' + text + '\n' + top_msg + '\n',
                strings=(_("&New game"), None, _("&Back to game"),
                         _("&Cancel")),
                image=self.app.gimages.logos[5])
        elif status == 1:
            top_msg = self.updateStats()
            time = self.getTime()
            self.finished = True
            self.playSample("gamewon", priority=1000)
            self.winAnimation()
            text = ungettext('Your playing time is %(time)s\nfor %(n)d move.',
                             'Your playing time is %(time)s\nfor %(n)d moves.',
                             self.moves.index)
            text = text % {'time': time, 'n': self.moves.index}
            congrats = _('Congratulations, you did it!')
            d = MfxMessageDialog(
                self.top, title=_("Game won"),
                text='\n' + congrats + '\n\n' + text + '\n' + top_msg + '\n',
                strings=(_("&New game"), None, _("&Back to game"),
                         _("&Cancel")),
                image=self.app.gimages.logos[4])
        elif self.gstats.updated < 0:
            self.finished = True
            self.playSample("gamefinished", priority=1000)
            d = MfxMessageDialog(
                self.top, title=_("Game finished"), bitmap="info",
                text=_("\nGame finished\n"),
                strings=(_("&New game"), None, None, _("&Close")))
        else:
            self.finished = True
            self.playSample("gamelost", priority=1000)
            text = "Game finished, but not without my help..."
            hintsused = ("You used %(h)s hint(s) during this game."
                         % {'h': self.stats.hints})
            d = MfxMessageDialog(
                self.top, title=_("Game finished"), bitmap="info",
                text=_(text + '\n\n' + hintsused),
                strings=(_("&New game"), _("&Restart"), None, _("&Cancel")))
        self.updateMenus()
        if TOOLKIT == 'kivy':
            return True
        if d.status == 0 and d.button == 0:
            # new game
            self.endGame()
            self.newGame()
        elif d.status == 0 and d.button == 1:
            # restart game
            self.restartGame()
        elif d.status == 0 and d.button == 2:
            self.stopWinAnimation()
        return True

    #
    # Game - subclass overridable methods (but usually not)
    #

    def isGameWon(self):
        # default: all Foundations must be filled
        return sum([len(s.cards) for s in self.s.foundations]) == \
            len(self.cards)

    def getFoundationDir(self):
        for s in self.s.foundations:
            if len(s.cards) >= 2:
                return s.getRankDir()
        return 0

    # determine the real number of player_moves
    def getPlayerMoves(self):
        return self.stats.player_moves

    def updateTime(self):
        if self.finished or self.pause:
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
        if autofaceup < 0:
            autofaceup = self.app.opt.autofaceup
        if autodrop < 0:
            autodrop = self.app.opt.autodrop
        if autodeal < 0:
            autodeal = self.app.opt.autodeal
        moves = self.stats.total_moves
        n = self._autoPlay(autofaceup, autodrop, autodeal, sound=sound)
        self.finishMove()
        self.stats.autoplay_moves += (self.stats.total_moves - moves)
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
                        # ~s.flipMove()
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
                        # is before the actual move)
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
        if old_a == 3:                   # medium
            self.app.opt.animations = 2  # fast
        self.autoPlay(autofaceup=autofaceup, autodrop=1)
        self.app.opt.animations = old_a

    # for find_card_dialog
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

    # highlight all moveable piles
    def getHighlightPilesStacks(self):
        # default: dropstacks with min pile length = 2
        if self.sg.hp_stacks:
            return ((self.sg.hp_stacks, 2),)
        return ()

    def _highlightCards(self, info, sleep=1.5, delta=(1, 1, 1, 1)):
        if not info:
            return 0
        if self.pause:
            return 0
        self.stopWinAnimation()
        cw, ch = self.app.images.getSize()
        items = []
        for s, c1, c2, color in info:
            items.append(
                _highlightCards__calc_item(
                    self.canvas, delta, cw, ch, s, c1, c2, color))
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

        color = self.app.opt.colors['not_matching']
        width = 6
        xmargin, ymargin = self.canvas.xmargin, self.canvas.ymargin
        if self.preview:
            width = 4
            xmargin, ymargin = 0, 0
        x0, y0 = x+width//2-xmargin, y+width//2-ymargin
        x1, y1 = x+w-width//2-xmargin, y+h-width//2-ymargin
        r = MfxCanvasRectangle(self.canvas, x0, y0, x1, y1,
                               width=width, fill=None, outline=color)

        if TOOLKIT == "kivy":
            r.canvas.canvas.ask_update()
            r.delete_deferred(self.app.opt.timeouts['highlight_cards'])
            return

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
        return (card1.color != card2.color and
                ((card1.rank + 1) % 13 == card2.rank or
                 (card2.rank + 1) % 13 == card1.rank))

    def _shallHighlightMatch_SS(self, stack1, card1, stack2, card2):
        # by same suit
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_SSW(self, stack1, card1, stack2, card2):
        # by same suit with wrapping (only for french games)
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 13 == card2.rank or
                 (card2.rank + 1) % 13 == card1.rank))

    def _shallHighlightMatch_RK(self, stack1, card1, stack2, card2):
        # by rank
        return abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_RKW(self, stack1, card1, stack2, card2):
        # by rank with wrapping (only for french games)
        return ((card1.rank + 1) % 13 == card2.rank or
                (card2.rank + 1) % 13 == card1.rank)

    def _shallHighlightMatch_BO(self, stack1, card1, stack2, card2):
        # by any suit but own
        return card1.suit != card2.suit and abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_BOW(self, stack1, card1, stack2, card2):
        # by any suit but own with wrapping (only for french games)
        return (card1.suit != card2.suit and
                ((card1.rank + 1) % 13 == card2.rank or
                 (card2.rank + 1) % 13 == card1.rank))

    def _shallHighlightMatch_SC(self, stack1, card1, stack2, card2):
        # by same color
        return card1.color == card2.color and abs(card1.rank-card2.rank) == 1

    def _shallHighlightMatch_SCW(self, stack1, card1, stack2, card2):
        # by same color with wrapping (only for french games)
        return (card1.color == card2.color and
                ((card1.rank + 1) % 13 == card2.rank or
                 (card2.rank + 1) % 13 == card1.rank))

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack in self.s.reserves:
            # if to_stack in reserves prefer empty stack
            # return 1000 - len(to_stack.cards)
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
            same_suit = (from_stack.cards[-ncards].suit ==
                         to_stack.cards[-1].suit)
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

    # compute all hints for the current position
    # this is the only method that actually uses class Hint
    def getHints(self, level, taken_hint=None):
        if level == 3:
            # if self.solver is None:
            # return None
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
            # print self.hints.list
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
                    print('*fail accepts cards*', from_stack, to_stack, ncards)
                if not from_stack.canMoveCards(from_stack.cards[-ncards:]):
                    print('*fail move cards*', from_stack, ncards)
            # assert from_stack.canMoveCards(from_stack.cards[-ncards:])
            # FIXME: Pyramid
            assert to_stack.acceptsCards(
                from_stack, from_stack.cards[-ncards:])
        if sleep <= 0.0:
            return h
        info = (level == 1) or (level > 1 and DEBUG)
        if info and self.app.statusbar and self.app.opt.statusbar:
            self.app.statusbar.configLabel(
                "info", text=_("Score %6d") % (score), fg=text_color)
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
        cw, ch = images.getSize()
        dx, dy = images.getDelta()
        x1, y1 = x1 + dx, y1 + dy
        x2, y2 = x2 + dx, y2 + dy
        if ncards == 1:
            x1 += cw // 2
            y1 += ch // 2
        elif from_stack.CARD_XOFFSET[0]:
            x1 += from_stack.CARD_XOFFSET[0] // 2
            y1 += ch // 2
        else:
            x1 += cw // 2
            y1 += from_stack.CARD_YOFFSET[0] // 2
        x2 += cw // 2
        y2 += ch // 2
        # draw the hint
        arrow = MfxCanvasLine(self.canvas, x1, y1, x2, y2, width=7,
                              fill=self.app.opt.colors['hintarrow'],
                              arrow="last", arrowshape=(30, 30, 10))
        self.canvas.update_idletasks()
        # wait
        if TOOLKIT == "kivy":
            arrow.delete_deferred(sleep)
            return
        # wait
        self.sleep(sleep)
        # delete the hint
        if arrow is not None:
            arrow.delete()
        self.canvas.update_idletasks()

    #
    # Demo - uses showHint()
    #

    def startDemo(self, mixed=1, level=2):
        assert level >= 2               # needed for flip/deal hints
        if not self.top:
            return
        self.demo = Struct(
            level=level,
            mixed=mixed,
            sleep=self.app.opt.timeouts['demo'],
            last_deal=[],
            snapshots=[],
            hint=None,
            keypress=None,
            start_demo_moves=self.stats.demo_moves,
            info_text=None,
        )
        self.hints.list = None
        self.createDemoInfoText()
        self.createDemoLogo()
        after_idle(self.top, self.demoEvent)  # schedule first move

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
            # self.updateMenus()
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
                d = MfxMessageDialog(self.top,
                                     title=_("%s Autopilot") % TITLE,
                                     text=text,
                                     image=self.app.gimages.logos[4],
                                     strings=(s,),
                                     separator=True,
                                     timeout=timeout)
                status = d.status
            else:
                # s = self.app.miscrandom.choice((_("&OK"), _("&OK")))
                s = _("&OK")
                text = _("\nGame finished\n")
                if DEBUG:
                    text += "\nplayer_moves: %d\ndemo_moves: %d\n" % \
                        (self.stats.player_moves, self.stats.demo_moves)
                d = MfxMessageDialog(self.top,
                                     title=_("%s Autopilot") % TITLE,
                                     text=text, bitmap=bitmap, strings=(s,),
                                     padx=30, timeout=timeout)
                status = d.status
        elif finished:
            # self.stopPlayTimer()
            if not self.top.winfo_ismapped():
                status = 2
            else:
                if player_moves == 0:
                    self.playSample("autopilotlost", priority=1000)
                s = self.app.miscrandom.choice(
                        (_("&Oh well"), _("&That's life"), _("&Hmm")))
                # ??? accelerators
                d = MfxMessageDialog(self.top,
                                     title=_("%s Autopilot") % TITLE,
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
                    self.app.demo_counter += 1
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
                    # gl = self.app.gdb.getGamesIdSortedByName()
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
                after_idle(self.top, self.demoEvent)  # schedule next move

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
        # TODO - the text placement is not fully ok
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
            # font = self.app.getFont("canvas_large")
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
        x1, x2 = 3*CW//2, self.width - 5*CW//2
        y1, y2 = CH//2, self.height - 3*CH//2
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
        # self.demo_logo = self.app.miscrandom.choice(self.app.gimages.demo)
        n = self.random.initial_seed % len(self.app.gimages.demo)
        self.demo_logo = self.app.gimages.demo[int(n)]
        self.canvas.setTopImage(self.demo_logo)

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
        if self.finished or self.Stuck_Class is None or self.isGameWon() != 0:
            return
        if self.getStuck():
            text = ''
            self.stuck = False
        else:
            text = 'x'
            if (not self.stuck and not self.demo and
                    self.app.opt.stuck_notification):
                self.playSample("gamelost", priority=1000)
                self.updateStatus(stuck='x')
                d = MfxMessageDialog(
                    self.top, title=_("You are Stuck"), bitmap="info",
                    text=_("\nThere are no moves left...\n"),
                    strings=(_("&New game"), _("&Restart"), None,
                             _("&Cancel")))
                if TOOLKIT != 'kivy':
                    if d.status == 0 and d.button == 0:
                        # new game
                        self.endGame()
                        self.newGame()
                        return
                    elif d.status == 0 and d.button == 1:
                        # restart game
                        self.restartGame()
                        return
            self.stuck = True
            # self.playSample("autopilotlost", priority=1000)
        self.updateStatus(stuck=text)

    #
    # Handle moves (with move history for undo/redo)
    # Actual move is handled in a subclass of AtomicMove.
    #
    # Note:
    # All playing moves (user actions, demo games) must get routed
    # to Stack.moveMove() because the stack may add important
    # triggers to a move (most notably fillStack and updateModel).
    #
    # Only low-level game (Game.startGame, Game.dealCards, Game.fillStack)
    # or stack methods (Stack.moveMove) should call the functions below
    # directly.
    #

    def startMoves(self):
        self.moves = GameMoves()
        self.stats._reset_statistics()

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
        # self.hints.list = None

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
        # #self.hints.list = None

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
        # self.hints.list = None

    # for ArbitraryStack
    def singleCardMove(self, from_stack, to_stack, position,
                       frames=-1, shadow=-1):
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
            mylen, m = len(current), moves.history[moves.index]
            if mylen == len(m):
                for i in range(mylen):
                    a1 = current[i]
                    a2 = m[i]
                    if a1.__class__ is not a2.__class__ or \
                            a1.cmpForRedo(a2) != 0:
                        break
                else:
                    redo = 1
        # try to detect an undo move for stuck-checking
        undo = 0
        if len(moves.history) > 0:
            mylen, m = len(current), moves.history[moves.index - 1]
            if mylen == len(m):
                for i in range(mylen):
                    a1 = current[i]
                    a2 = m[i]
                    if a1.__class__ is not a2.__class__ or \
                            a1.cmpForUndo(a2) != 0:
                        break
                else:
                    undo = 1
        # add current move to history (which is a list of lists)
        if redo:
            # print "detected redo:", current
            # overwrite existing entry because minor things like
            # shadow/frames may have changed
            moves.history[moves.index] = current
            moves.index += 1
        else:
            # resize (i.e. possibly shorten list from previous undos)
            moves.history[moves.index:] = [current]
            moves.index += 1
            assert moves.index == len(moves.history)

        moves.current = []
        self.updateSnapshots()
        # update view
        self.updateText()
        self.updateStatus(moves=(moves.index, self.stats.total_moves))
        self.updateMenus()
        self.updatePlayTime(do_after=0)
        if not undo:
            self.updateStuck()
        reset_solver_dialog()

        return 1

    def undo(self):
        assert self.canUndo()
        assert self.moves.state == self.S_PLAY and len(self.moves.current) == 0
        assert 0 <= self.moves.index <= len(self.moves.history)
        if self.moves.index == 0:
            return
        self.moves.index -= 1
        self.moves.state = self.S_UNDO
        for atomic_move in reversed(self.moves.history[self.moves.index]):
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
            if not self.areYouSure(
                    _("Set bookmark"),
                    _("Replace existing bookmark %d?") % (n+1)):
                return 0
        f = BytesIO()
        try:
            self._dumpGame(Pickler(f, 1), bookmark=2)
            bm = (f.getvalue(), self.moves.index)
        except Exception:
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
                                   _("Goto bookmark %d?") % (n+1)):
                return
        try:
            s, moves_index = bm
            self.setCursor(cursor=CURSOR_WATCH)
            file = BytesIO(s)
            p = Unpickler(file)
            game = self._undumpGame(p, self.app)
            assert game.id == self.id
            # save state for undoGotoBookmark
            self.setBookmark(-1, confirm=0)
        except Exception:
            del self.gsaveinfo.bookmarks[n]
            self.setCursor(cursor=self.app.top_cursor)
        else:
            if update_stats:
                self.stats.goto_bookmark_moves += 1
                self.gstats.goto_bookmark_moves += 1
            self.restoreGame(game, reset=0)
            destruct(game)

    def undoGotoBookmark(self):
        self.gotoBookmark(-1, update_stats=0)

    def loadGame(self, filename):
        if self.changed():
            if not self.areYouSure(_("Open game")):
                return
        self.finishMove()       # just in case
        game = None
        self.setCursor(cursor=CURSOR_WATCH)
        self.disableMenus()
        try:
            game = self._loadGame(filename, self.app)
            game.gstats.holded = 0
        except AssertionError:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            MfxMessageDialog(
                self.top, title=_("Load game error"), bitmap="error",
                text=_(
                    "Error while loading game.\n\n" +
                    "Probably the game file is damaged,\n" +
                    "but this could also be a bug you might want to report."))
            traceback.print_exc()
        except UnpicklingError as ex:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            MfxExceptionDialog(self.top, ex, title=_("Load game error"),
                               text=_("Error while loading game"))
        except Exception:
            self.updateMenus()
            self.setCursor(cursor=self.app.top_cursor)
            MfxMessageDialog(
                self.top, title=_("Load game error"),
                bitmap="error", text=_(
                    """Internal error while loading game.\n\n""" +
                    "Please report this bug."))
            traceback.print_exc()
        else:
            if self.pause:
                # unselect pause-button
                self.app.menubar.mPause()
            self.filename = filename
            game.filename = filename
            # now start the new game
            # print game.__dict__
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
        except Exception as ex:
            self.setCursor(cursor=self.app.top_cursor)
            MfxExceptionDialog(self.top, ex, title=_("Save game error"),
                               text=_("Error while saving game"))
        else:
            self.filename = filename
            self.setCursor(cursor=self.app.top_cursor)

    #
    # low level load/save
    #

    def _loadGame(self, filename, app):
        game = None
        with open(filename, "rb") as f:
            game = self._undumpGame(Unpickler(f), app)
            game.gstats.loaded += 1
        return game

    def _undumpGame(self, p, app):
        self.updateTime()
        #
        err_txt = _("Invalid or damaged %s save file") % PACKAGE
        #

        def pload(t=None, p=p):
            obj = p.load()
            if isinstance(t, type):
                if not isinstance(obj, t):
                    # accept old storage format in case:
                    if t in _Game_LOAD_CLASSES:
                        assert isinstance(obj, Struct), err_txt
                    else:
                        assert False, err_txt
            return obj

        def validate(v, txt):
            if not v:
                raise UnpicklingError(txt)
        #
        package = pload(str)
        validate(package == PACKAGE, err_txt)
        version = pload(str)
        # validate(isinstance(version, str) and len(version) <= 20, err_txt)
        version_tuple = pload(tuple)
        validate(
            version_tuple >= (1, 0),
            _('Cannot load games saved with\n%(app)s version %(ver)s') % {
                'app': PACKAGE,
                'ver': version})
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
        validate(
            game is not None,
            _('Cannot load this game from version %s\n' +
              'as the game rules have changed\n' +
              'in the current implementation.') % version)
        game.version = version
        game.version_tuple = version_tuple
        #
        initial_seed = random__int2str(pload(int))
        game.random = construct_random(initial_seed)
        state = pload()
        if (game.random is not None and
                not isinstance(game.random, random2.Random) and
                isinstance(state, int)):
            game.random.setstate(state)
        # if not hasattr(game.random, "origin"):
        # game.random.origin = game.random.ORIGIN_UNKNOWN
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
            saveinfo = pload(GameSaveInfo)
            game.saveinfo.__dict__.update(saveinfo.__dict__)
            gsaveinfo = pload(GameGlobalSaveInfo)
            game.gsaveinfo.__dict__.update(gsaveinfo.__dict__)
        moves = pload(GameMoves)
        game.moves.__dict__.update(moves.__dict__)
        snapshots = pload(list)
        game.snapshots = snapshots
        if 0 <= bookmark <= 1:
            gstats = pload(GameGlobalStatsStruct)
            game.gstats.__dict__.update(gstats.__dict__)
            stats = pload(GameStatsStruct)
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
        if self.canSaveGame():
            with open(filename, "wb") as f:
                self._dumpGame(Pickler(f, protocol))

    def _dumpGame(self, p, bookmark=0):
        return pysolDumpGame(self, p, bookmark)

    def startPlayTimer(self):
        self.updateStatus(time=None)
        self.stopPlayTimer()
        self.play_timer = after(
            self.top, PLAY_TIME_TIMEOUT, self.updatePlayTime)

    def stopPlayTimer(self):
        if hasattr(self, 'play_timer') and self.play_timer:
            after_cancel(self.play_timer)
            self.play_timer = None
            self.updatePlayTime(do_after=0)

    def updatePlayTime(self, do_after=1):
        if not self.top:
            return
        if self.pause or self.finished:
            return
        if do_after:
            self.play_timer = after(
                self.top, PLAY_TIME_TIMEOUT, self.updatePlayTime)
        d = time.time() - self.stats.update_time + self.stats.elapsed_time
        self.updateStatus(time=format_time(d))

    def doPause(self):
        if self.finished:
            return
        if self.demo:
            self.stopDemo()
        if not self.pause:
            self.updateTime()
        self.pause = not self.pause
        if self.pause:
            # self.updateTime()
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

    def showHelp(self, *args):
        if self.preview:
            return
        kw = dict([(args[i], args[i+1]) for i in range(0, len(args), 2)])
        if not kw:
            kw = {'info': '', 'help': ''}
        if 'info' in kw and self.app.opt.statusbar:
            self.app.statusbar.updateText(info=kw['info'])
        if 'help' in kw and self.app.opt.statusbar:
            self.app.statusbar.updateText(help=kw['help'])

    #
    # Piles descriptions
    #

    def showStackDesc(self):
        from pysollib.pysoltk import StackDesc
        from pysollib.stack import InitialDealTalonStack
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

    # for find_card_dialog
    def canFindCard(self):
        return self.gameinfo.category != GI.GC_MATCHING

    #
    # subclass hooks
    #

    def _restoreGameHook(self, game):
        pass

    def _loadGameHook(self, p):
        pass

    def _saveGameHook(self, p):
        pass

    def _dealNumRows(self, n):
        for i in range(n):
            self.s.talon.dealRow(frames=0)

    def _startDealNumRows(self, n):
        self._dealNumRows(n)
        self.startDealSample()

    def _startDealNumRowsAndDealSingleRow(self, n):
        self._startDealNumRows(n)
        self.s.talon.dealRow()

    def _startAndDealRow(self):
        self._startDealNumRowsAndDealSingleRow(0)

    def _startDealNumRowsAndDealRowAndCards(self, n):
        self._startDealNumRowsAndDealSingleRow(n)
        self.s.talon.dealCards()

    def _startAndDealRowAndCards(self):
        self._startAndDealRow()
        self.s.talon.dealCards()


class StartDealRowAndCards(object):
    def startGame(self):
        self._startAndDealRowAndCards()
