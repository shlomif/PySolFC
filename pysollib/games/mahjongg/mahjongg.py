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

__all__ = []

# Imports
import sys, re
import time
#from tkFont import Font
from gettext import ungettext

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault, Struct, Image
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.settings import TOOLKIT, DEBUG
from pysollib.pysoltk import MfxCanvasText, MfxCanvasImage
from pysollib.pysoltk import bind, EVENT_HANDLED, ANCHOR_NW
from pysollib.pysoltk import MfxMessageDialog


def factorial(x):
    if x <= 1:
        return 1
    a = 1
    for i in xrange(x):
        a *= (i+1)
    return a


# ************************************************************************
# *
# ************************************************************************

class Mahjongg_Hint(AbstractHint):
    # FIXME: no intelligence whatsoever is implemented here
    def computeHints(self):
        game = self.game
        # get free stacks
        stacks = []
        for r in game.s.rows:
            if r.cards and not r.basicIsBlocked():
                stacks.append(r)
        # find matching tiles
        i = 0
        for r in stacks:
            for t in stacks[i+1:]:
                if game.cardsMatch(r.cards[0], t.cards[0]):
                    # simple scoring...
                    ##score = 10000 + r.id + t.id
                    rb = r.blockmap
                    tb = t.blockmap
                    score = \
                          10000 + \
                          1000 * (len(rb.below) + len(tb.below)) + \
                          len(rb.all_left) + len(rb.all_right) + \
                          len(tb.all_left) + len(tb.all_right)
                    self.addHint(score, 1, r, t)
            i += 1


# ************************************************************************
# *
# ************************************************************************

#class Mahjongg_Foundation(AbstractFoundationStack):
class Mahjongg_Foundation(OpenStack):

    def __init__(self, x, y, game, suit=ANY_SUIT, **cap):
        kwdefault(cap, max_move=0, max_accept=0, max_cards=game.NCARDS)
        OpenStack.__init__(self, x, y, game, **cap)

    def acceptsCards(self, from_stack, cards):
        # We do not accept any cards - pairs will get
        # delivered by _dropPairMove() below.
        return 0

    def basicIsBlocked(self):
        return 1

    #def initBindings(self):
    #    pass

    def _position(self, card):
        #AbstractFoundationStack._position(self, card)
        OpenStack._position(self, card)

        fnds = self.game.s.foundations

        cols = (3, 2, 1, 0)
        for i in cols:
            for j in range(9):
                n = i*9+j
                if fnds[n].cards:
                    fnds[n].group.tkraise()
        return

    def getHelp(self):
        return ''


# ************************************************************************
# *
# ************************************************************************

class Mahjongg_RowStack(OpenStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1, max_cards=2,
                  base_rank=NO_RANK)
        OpenStack.__init__(self, x, y, game, **cap)

    def basicIsBlocked(self):
        # any of above blocks
        for stack in self.blockmap.above:
            if stack.cards:
                return 1
        # any of left blocks - but we can try right as well
        for stack in self.blockmap.left:
            if stack.cards:
                break
        else:
            return 0
        # any of right blocks
        for stack in self.blockmap.right:
            if stack.cards:
                return 1
        return 0

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return 0
        return self.game.cardsMatch(self.cards[0], cards[-1])

    def canFlipCard(self):
        return 0

    def canDropCards(self, stacks):
        return (None, 0)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        ##print 'drop:', self.id, other_stack.id
        assert n == 1 and self.acceptsCards(other_stack, [other_stack.cards[-1]])
        if not self.game.demo:
            self.game.playSample("droppair", priority=200)
        old_state = self.game.enterState(self.game.S_FILL)
        c = self.cards[0]
        if c.suit == 3:
            if c.rank >= 8:
                i = 35
            elif c.rank >= 4:
                i = 34
            else:
                i = 30+c.rank
        elif c.rank == 9:
            i = 27+c.suit
        else:
            i = c.suit*9+c.rank
        f = self.game.s.foundations[i]
        self.game.moveMove(n, self, f, frames=frames, shadow=shadow)
        self.game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.game.leaveState(old_state)
        self.fillStack()
        other_stack.fillStack()

    #
    # Mahjongg special overrides
    #

    # Mahjongg special: we must preserve the relative stacking order
    # to keep our pseudo 3D look.
    def _position(self, card):
        OpenStack._position(self, card)
        #
        if TOOLKIT == 'tk':
            rows = [s for s in self.game.s.rows[:self.id] if s.cards]
            if rows:
                self.group.tkraise(rows[-1].group)
                return
            rows = [s for s in self.game.s.rows[self.id+1:] if s.cards]
            if rows:
                self.group.lower(rows[0].group)
                return
        elif TOOLKIT == 'gtk':
            # FIXME (this is very slow)
            for s in self.game.s.rows[self.id+1:]:
                s.group.tkraise()


    # In Mahjongg games type there are a lot of stacks, so we optimize
    # and don't create bindings that are not used anyway.
    def initBindings(self):
        group = self.group
        # FIXME: dirty hack to access the Stack's private methods
        #bind(group, "<1>", self._Stack__clickEventHandler)
        #bind(group, "<3>", self._Stack__controlclickEventHandler)
        #bind(group, "<Control-1>", self._Stack__controlclickEventHandler)
        #
        bind(group, "<1>", self.__clickEventHandler)
        bind(group, "<3>", self.__controlclickEventHandler)
        bind(group, "<Control-1>", self.__controlclickEventHandler)
        ##bind(group, "<Enter>", self._Stack__enterEventHandler)
        ##bind(group, "<Leave>", self._Stack__leaveEventHandler)

    def __defaultClickEventHandler(self, event, handler):
        self.game.event_handled = True # for Game.undoHandler
        if self.game.demo:
            self.game.stopDemo(event)
        if self.game.busy:
            return EVENT_HANDLED
        handler(event)
        return EVENT_HANDLED

    def __clickEventHandler(self, event):
        ##print 'click:', self.id
        return self.__defaultClickEventHandler(event, self.clickHandler)

    def __controlclickEventHandler(self, event):
        return self.__defaultClickEventHandler(event, self.controlclickHandler)

    def clickHandler(self, event):
        game = self.game
        drag = game.drag
        # checks
        if not self.cards:
            return 1
        card = self.cards[-1]
        from_stack = drag.stack
        if from_stack is self:
            # remove selection
            self.game.playSample("nomove")
            self._stopDrag()
            return 1
        if self.basicIsBlocked():
            ### remove selection
            ##self.game.playSample("nomove")
            return 1
        # possible move
        if from_stack:
            if self.acceptsCards(from_stack, from_stack.cards):
                self._stopDrag()
                # this code actually moves the tiles
                from_stack.playMoveMove(1, self, frames=0, sound=True)
                return 1
        drag.stack = self
        self.game.playSample("startdrag")
        # create the shade image (see stack.py, _updateShade)
        if drag.shade_img:
            #drag.shade_img.dtag(drag.shade_stack.group)
            drag.shade_img.delete()
            #game.canvas.delete(drag.shade_img)
            drag.shade_img = None
        img = game.app.images.getShadowCard(card.deck, card.suit, card.rank)
        if img is None:
            return 1
        img = MfxCanvasImage(game.canvas, self.x, self.y, image=img,
                             anchor=ANCHOR_NW, group=self.group)
        drag.shade_img = img
        # raise/lower the shade image to the correct stacking order
        img.tkraise(card.item)
        drag.shade_stack = self
        return 1

    def cancelDrag(self, event=None):
        if event is None:
            self._stopDrag()

    def _findCard(self, event):
        # we need to override this because the shade may be hiding
        # the tile (from Tk's stacking view)
        return len(self.cards) - 1

    def getBottomImage(self):
        return None


# ************************************************************************
# *
# ************************************************************************

class AbstractMahjonggGame(Game):
    Hint_Class = Mahjongg_Hint
    RowStack_Class = Mahjongg_RowStack

    GAME_VERSION = 3

    NCARDS = 144

    def getTiles(self):
        # decode tile positions
        L = self.L

        assert L[0] == "0"
        assert (len(L) - 1) % 3 == 0

        tiles = []
        max_tl, max_tx, max_ty = -1, -1, -1
        t = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i in range(1, len(L), 3):
            n = t.find(L[i])
            level, height = n / 7, n % 7 + 1
            tx = t.find(L[i+1])
            ty = t.find(L[i+2])
            assert n >= 0 and tx >= 0 and ty >= 0
            max_tl = max(level + height - 1, max_tl)
            max_tx = max(tx, max_tx)
            max_ty = max(ty, max_ty)
            for tl in range(level, level + height):
                tiles.append((tl, tx, ty))
        assert len(tiles) == self.NCARDS
        #tiles.sort()
        #tiles = tuple(tiles)
        return tiles, max_tl, max_tx, max_ty


    #
    # game layout
    #

    def createGame(self):
        tiles, max_tl, max_tx, max_ty = self.getTiles()

        # start layout
        l, s = Layout(self), self.s
        show_removed = self.app.opt.mahjongg_show_removed

        ##dx, dy = 2, -2
        ##dx, dy = 3, -3
        cs = self.app.cardset
        if cs.version >= 6:
            dx = l.XOFFSET
            dy = -l.YOFFSET
            d_x = cs.SHADOW_XOFFSET
            d_y = cs.SHADOW_YOFFSET
            if self.preview:
                # Fixme
                dx, dy, d_x, d_y = dx/2, dy/2, d_x/2, d_y/2
            self._delta_x, self._delta_y = dx, -dy
        else:
            dx = 3
            dy = -3
            d_x = 0
            d_y = 0
            self._delta_x, self._delta_y = 0, 0
        #print dx, dy, d_x, d_y, cs.version

        font = self.app.getFont("canvas_default")

        # width of self.texts.info
        #ti_width = Font(self.canvas, font).measure(_('Remaining'))
        ti_width = 80

        # set window size
        dxx, dyy = abs(dx) * (max_tl+1), abs(dy) * (max_tl+1)
        # foundations dxx dyy
        if self.NCARDS > 144:
            fdxx = abs(dx)*8
            fdyy = abs(dy)*8
        else:
            fdxx = abs(dx)*4
            fdyy = abs(dy)*4
        cardw, cardh = l.CW - d_x, l.CH - d_y
        if show_removed:
            left_margin = l.XM + 4*cardw+fdxx+d_x + l.XM
        else:
            left_margin = l.XM
        tableau_width = (max_tx+2)*cardw/2+dxx+d_x
        right_margin = l.XM+ti_width+l.XM
        w = left_margin + tableau_width + right_margin
        h = l.YM + dyy + (max_ty + 2) * cardh / 2 + d_y + l.YM
        if show_removed:
            h = max(h, l.YM+fdyy+cardh*9+d_y+l.YM)
        self.setSize(w, h)

        # set game extras
        self.check_dist = l.CW*l.CW + l.CH*l.CH     # see _getClosestStack()

        # sort tiles (for 3D)
        tiles.sort(lambda a, b:
                   cmp(a[0], b[0]) or
                   cmp(-a[1]+a[2], -b[1]+b[2])
                   )

        # create a row stack for each tile and compute the tilemap
        tilemap = {}
        x0 = left_margin
        y0 = l.YM + dyy
        for level, tx, ty in tiles:
            #print level, tx, ty
            x = x0 + (tx * cardw) / 2 + level * dx
            y = y0 + (ty * cardh) / 2 + level * dy
            stack = self.RowStack_Class(x, y, self)
            ##stack.G = (level, tx, ty)
            stack.CARD_XOFFSET = dx
            stack.CARD_YOFFSET = dy
            s.rows.append(stack)
            # tilemap - each tile covers 4 positions
            tilemap[(level, tx, ty)] = stack
            tilemap[(level, tx+1, ty)] = stack
            tilemap[(level, tx, ty+1)] = stack
            tilemap[(level, tx+1, ty+1)] = stack

        # compute blockmap
        for stack in s.rows:
            level, tx, ty = tiles[stack.id]
            above, below, left, right, up, bottom = {}, {}, {}, {}, {}, {}
            # above blockers
            for tl in range(level+1, level+2):
                above[tilemap.get((tl, tx, ty))] = 1
                above[tilemap.get((tl, tx+1, ty))] = 1
                above[tilemap.get((tl, tx, ty+1))] = 1
                above[tilemap.get((tl, tx+1, ty+1))] = 1
            #
            for tl in range(level):
                below[tilemap.get((tl, tx, ty))] = 1
                below[tilemap.get((tl, tx+1, ty))] = 1
                below[tilemap.get((tl, tx, ty+1))] = 1
                below[tilemap.get((tl, tx+1, ty+1))] = 1
            # left blockers
            left[tilemap.get((level, tx-1, ty))] = 1
            left[tilemap.get((level, tx-1, ty+1))] = 1
            # right blockers
            right[tilemap.get((level, tx+2, ty))] = 1
            right[tilemap.get((level, tx+2, ty+1))] = 1
            # up blockers
            ##up[tilemap.get((level, tx, ty-1))] = 1
            ##up[tilemap.get((level, tx+1, ty-1))] = 1
            # bottom blockers
            ##bottom[tilemap.get((level, tx, ty+2))] = 1
            ##bottom[tilemap.get((level, tx+1, ty+2))] = 1
            # sanity check - assert that there are no overlapping tiles
            assert tilemap.get((level, tx, ty)) is stack
            assert tilemap.get((level, tx+1, ty)) is stack
            assert tilemap.get((level, tx, ty+1)) is stack
            assert tilemap.get((level, tx+1, ty+1)) is stack
            #
            above = tuple(filter(None, above.keys()))
            below = tuple(filter(None, below.keys()))
            left = tuple(filter(None, left.keys()))
            right = tuple(filter(None, right.keys()))
            ##up = tuple(filter(None, up.keys()))
            ##bottom = tuple(filter(None, bottom.keys()))

            # assemble
            stack.blockmap = Struct(
                above = above,
                below = below,
                left = left,
                right = right,
                ##up = up,
                ##bottom = bottom,
                all_left = None,
                all_right = None,
            )

        def get_all_left(s):
            if s.blockmap.all_left is None:
                s.blockmap.all_left = {}
            for t in s.blockmap.left:
                if t.blockmap.all_left is None:
                    get_all_left(t)
                s.blockmap.all_left.update(t.blockmap.all_left)
                s.blockmap.all_left[t] = 1
        def get_all_right(s):
            if s.blockmap.all_right is None:
                s.blockmap.all_right = {}
            for t in s.blockmap.right:
                if t.blockmap.all_right is None:
                    get_all_right(t)
                s.blockmap.all_right.update(t.blockmap.all_right)
                s.blockmap.all_right[t] = 1

        for r in s.rows:
            get_all_left(r)
            get_all_right(r)
        for r in s.rows:
            r.blockmap.all_left = tuple(r.blockmap.all_left.keys())
            r.blockmap.all_right = tuple(r.blockmap.all_right.keys())


        # create other stacks
        for i in range(4):
            for j in range(9):
                if show_removed:
                    x = l.XM+i*cardw
                    y = l.YM+fdyy+j*cardh
                else:
                    if TOOLKIT == 'tk':
                        x = -l.XS-self.canvas.xmargin
                        y = l.YM+dyy
                    elif TOOLKIT == 'gtk':
                        # FIXME
                        x = self.width -l.XS
                        y = self.height - l.YS
                stack = Mahjongg_Foundation(x, y, self)
                if show_removed:
                    stack.CARD_XOFFSET = dx
                    stack.CARD_YOFFSET = dy
                s.foundations.append(stack)

        self.texts.info = MfxCanvasText(self.canvas,
                                        self.width - l.XM - ti_width,
                                        l.YM + dyy,
                                        anchor="nw", font=font)
        # the Talon is invisble
        s.talon = InitialDealTalonStack(-l.XS-self.canvas.xmargin,
                                        self.height-dyy, self)

        # Define stack groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        if self.app.opt.mahjongg_create_solvable == 0:
            return cards
        # try to create a solvable game
        if self.app.opt.mahjongg_create_solvable == 1:
            # easy
            return self._shuffleHook1(cards[:])
        # hard
        new_cards = self._shuffleHook2(self.s.rows, cards)
        if new_cards is None:
            return cards
        return new_cards


    def _shuffleHook1(self, cards):
        # old version; it generate a very easy layouts
        old_cards = cards[:]
        rows = self.s.rows

        def is_blocked(s, new_cards):
            # any of above blocks
            for stack in s.blockmap.above:
                if new_cards[stack.id] is None:
                    return True
            # any of left blocks - but we can try right as well
            for stack in s.blockmap.left:
                if new_cards[stack.id] is None:
                    break
            else:
                return False
            # any of right blocks
            for stack in s.blockmap.right:
                if new_cards[stack.id] is None:
                    return True
            return False

        def create_solvable(cards, new_cards):
            if not cards:
                return new_cards
            # select two matching cards
            c1 = cards[0]
            del cards[0]
            c2 = None
            for i in xrange(len(cards)):
                if self.cardsMatch(c1, cards[i]):
                    c2 = cards[i]
                    del cards[i]
                    break
            #
            free_stacks = []            # none-blocked stacks
            for r in rows:
                if new_cards[r.id] is None and not is_blocked(r, new_cards):
                    free_stacks.append(r)
            if len(free_stacks) < 2:
                return None             # try another way
            #
            i = factorial(len(free_stacks))/2/factorial(len(free_stacks)-2)
            old_pairs = []
            for j in xrange(i):
                nc = new_cards[:]
                while True:
                    # create uniq pair
                    r1 = self.random.randrange(0, len(free_stacks))
                    r2 = self.random.randrange(0, len(free_stacks)-1)
                    if r2 >= r1:
                        r2 += 1
                    if (r1, r2) not in old_pairs and (r2, r1) not in old_pairs:
                        old_pairs.append((r1, r2))
                        break
                # add two selected cards to new_cards
                s1 = free_stacks[r1]
                s2 = free_stacks[r2]
                nc[s1.id] = c1
                nc[s2.id] = c2
                # check if this layout is solvable (backtracking)
                nc = create_solvable(cards[:], nc)
                if nc:
                    return nc
            return None                 # try another way

        new_cards = create_solvable(cards, [None]*len(cards))
        if new_cards:
            new_cards.reverse()
            return new_cards
        print 'oops! can\'t create a solvable game'
        return old_cards


    def _shuffleHook2(self, rows, cards):

        start_time = time.time()
        iters = [0]
        # limitations
        max_time = 5.0                  # seconds
        max_iters = 2*len(cards)

        def is_suitable(stack, cards):
            for s in stack.blockmap.below:
                if cards[s.id] == 1:
                    continue
                # check if below stacks are non-empty
                if cards[s.id] is None:
                    return False

            for s in stack.blockmap.left:
                if cards[s.id] == 1:
                    continue
                if cards[s.id] is None:
                    for t in s.blockmap.all_left:
                        if cards[t.id] == 1:
                            continue
                        if cards[t.id] is not None:
                            # we have empty stack between two non-empty
                            return False

            for s in stack.blockmap.right:
                if cards[s.id] == 1:
                    continue
                if cards[s.id] is None:
                    for t in s.blockmap.all_right:
                        if cards[t.id] == 1:
                            continue
                        if cards[t.id] is not None:
                            # we have empty stack between two non-empty
                            return False
            return True

        def create_solvable(cards, new_cards):
            iters[0] += 1
            if iters[0] > max_iters:
                return None
            if time.time() - start_time > max_time:
                return None
            if not cards:
                return new_cards

            nc = new_cards[:]

            # select two matching cards
            c1 = cards[0]
            del cards[0]
            c2 = None
            for i in xrange(len(cards)):
                if self.cardsMatch(c1, cards[i]):
                    c2 = cards[i]
                    del cards[i]
                    break

            # find suitable stacks
##             suitable_stacks = []
##             for r in rows:
##                 if nc[r.id] is None and is_suitable(r, nc):
##                     suitable_stacks.append(r)
            suitable_stacks = [r for r in rows
                               if nc[r.id] is None and is_suitable(r, nc)]

            old_pairs = []
            i = factorial(len(suitable_stacks))/2/factorial(len(suitable_stacks)-2)
            for j in xrange(i):
                if iters[0] > max_iters:
                    return None
                if time.time() - start_time > max_time:
                    return None

                # select two suitable stacks
                while True:
                    # create a uniq pair
                    r1 = self.random.randrange(0, len(suitable_stacks))
                    r2 = self.random.randrange(0, len(suitable_stacks))
                    if r1 == r2:
                        continue
                    if (r1, r2) not in old_pairs and (r2, r1) not in old_pairs:
                        old_pairs.append((r1, r2))
                        break
                s1 = suitable_stacks[r1]
                s2 = suitable_stacks[r2]
                # check if s1 don't block s2
                nc[s1.id] = c1
                if not is_suitable(s2, nc):
                    nc[s1.id] = None
                    continue
                nc[s2.id] = c2
                # check if this layout is solvable (backtracking)
                ret = create_solvable(cards[:], nc)
                if ret:
                    ret = [x for x in ret if x != 1]
                    return ret
                nc[s1.id] = nc[s2.id] = None # try another way

            return None

        new_cards = [None]*len(self.s.rows) # None - empty stack, 1 - non-used
        drows = dict.fromkeys(rows)     # optimization
        for r in self.s.rows:
            if r not in drows:
                new_cards[r.id] = 1
        del drows

        while True:
            ret = create_solvable(cards[:], new_cards)
            if DEBUG:
                print 'create_solvable time:', time.time() - start_time
            if ret:
                ret.reverse()
                return ret
            if time.time() - start_time > max_time or \
                   iters[0] <= max_iters:
                print 'oops! can\'t create a solvable game'
                return None
            iters = [0]
        print 'oops! can\'t create a solvable game'
        return None

    def _mahjonggShuffle(self):
        talon = self.s.talon
        rows = []
        cards = []

        for r in self.s.rows:
            if r.cards:
                rows.append(r)
                cards.append(r.cards[0])
        if not rows:
            return

        if self.app.opt.mahjongg_create_solvable == 0:
            self.playSample('turnwaste')
            old_state = self.enterState(self.S_FILL)
            self.saveSeedMove()
            for r in rows:
                self.moveMove(1, r, talon, frames=0)
            self.shuffleStackMove(talon)
            for r in rows:
                self.moveMove(1, talon, r, frames=0)
            self.leaveState(old_state)
            self.finishMove()
            return

        self.playSample('turnwaste')
        old_state = self.enterState(self.S_FILL)
        self.saveSeedMove()

        new_cards = self._shuffleHook2(rows, cards)
        if new_cards is None:
            d = MfxMessageDialog(self.top, title=_('Warning'),
                                 text=_('''\
Sorry, I can\'t find
a solvable configuration.'''),
                                 bitmap='warning')
            self.leaveState(old_state)
            ##self.finishMove()
            # hack
            am = self.moves.current[0]
            am.undo(self)               # restore random
            self.moves.current = []
            return

        self.stats.shuffle_moves += 1
        # move new_cards to talon
        for c in new_cards:
            for r in rows:
                if r.cards and r.cards[0] is c:
                    self.moveMove(1, r, talon, frames=0)
                    break
        # deal
        for r in rows:
            self.moveMove(1, talon, r, frames=0)

        self.leaveState(old_state)
        self.finishMove()

    def canShuffle(self):
        return True

    def startGame(self):
        assert len(self.s.talon.cards) == self.NCARDS
        #self.s.talon.dealRow(rows = self.s.rows, frames = 0)
        n = 12
        self.s.talon.dealRow(rows=self.s.rows[:self.NCARDS-n], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[self.NCARDS-n:])
        assert len(self.s.talon.cards) == 0

    def isGameWon(self):
        return sum([len(f.cards) for f in self.s.foundations]) == self.NCARDS

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if stack1.basicIsBlocked() or stack2.basicIsBlocked():
            return 0
        return self.cardsMatch(card1, card2)

    def getAutoStacks(self, event=None):
        return ((), (), ())

    def updateText(self):
        if self.preview > 1 or self.texts.info is None:
            return

        # find matching tiles
        stacks = []
        for r in self.s.rows:
            if r.cards and not r.basicIsBlocked():
                stacks.append(r)
        f, i = 0, 0
        for r in stacks:
            n = 0
            for t in stacks[i+1:]:
                if self.cardsMatch(r.cards[0], t.cards[0]):
                    n += 1
            #if n == 3: n = 1
            #elif n == 2: n = 0
            n = n % 2
            f += n
            i += 1

        if f == 0:
            f = _('No Free\nMatching\nPairs')
        else:
            f = ungettext('%d Free\nMatching\nPair',
                          '%d Free\nMatching\nPairs',
                          f) % f
        t = sum([len(i.cards) for i in self.s.foundations])
        r1 = ungettext('%d\nTile\nRemoved\n\n',
                       '%d\nTiles\nRemoved\n\n',
                       t) % t
        r2 = ungettext('%d\nTile\nRemaining\n\n',
                       '%d\nTiles\nRemaining\n\n',
                       self.NCARDS - t) % (self.NCARDS - t)

        t = r1 + r2 + f
        self.texts.info.config(text=t)

    #
    # Mahjongg special overrides
    #

    def getHighlightPilesStacks(self):
        # Mahjongg special: highlight all moveable tiles
        return ((self.s.rows, 1),)

    def _highlightCards(self, info, sleep=1.5, delta=(1,1,1,1)):
        if not Image:
            delta = (-self._delta_x, 0, 0, -self._delta_y)
            return Game._highlightCards(self, info, sleep=sleep, delta=delta)

        if not info:
            return 0
        if self.pause:
            return 0
        self.stopWinAnimation()
        items = []
        for s, c1, c2, color in info:
            assert c1 is c2
            assert c1 in s.cards
            tkraise = False
            x, y = s.x, s.y
            img = self.app.images.getHighlightCard(c1.deck, c1.suit, c1.rank)
            if img is None:
                continue
            img = MfxCanvasImage(self.canvas, x, y, image=img,
                                 anchor=ANCHOR_NW, group=s.group)
            if self.drag.stack and s is self.drag.stack:
                img.tkraise(self.drag.shade_img)
            else:
                img.tkraise(c1.item)
            items.append(img)
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

    def getCardFaceImage(self, deck, suit, rank):
        if suit == 3:
            cs = self.app.cardset
            if len(cs.ranks) >= 12 and len(cs.suits) >= 4:
                # make Mahjongg type games playable with other cardsets
                if rank >= 8:       # flower
                    suit = 1
                    rank = len(cs.ranks) - 2
                elif rank >= 4:     # season
                    rank = max(10, len(cs.ranks) - 3)
                else:               # wind
                    suit = rank
                    rank = len(cs.ranks) - 1
        return self.app.images.getFace(deck, suit, rank)

    def getCardBackImage(self, deck, suit, rank):
        # We avoid screen updates caused by flipping cards - all
        # cards are face up anyway. The Talon should be invisible
        # or else the top tile of the Talon will be visible during
        # game start.
        return self.getCardFaceImage(deck, suit, rank)

    def _createCard(self, id, deck, suit, rank, x, y):
        ##if deck >= 1 and suit == 3 and rank >= 4:
        if deck%4 and suit == 3 and rank >= 4:
            return None
        return Game._createCard(self, id, deck, suit, rank, x, y)

    def _getClosestStack(self, cx, cy, stacks, dragstack):
        closest, cdist = None, 999999999
        # Since we only compare distances,
        # we don't bother to take the square root.
        for stack in stacks:
            dist = (stack.x - cx)**2 + (stack.y - cy)**2
            if dist < cdist:
                # Mahjongg special: if the stack is very close, do
                # not consider blocked stacks
                if dist > self.check_dist or not stack.basicIsBlocked():
                    closest, cdist = stack, dist
        return closest

    #
    # Mahjongg extras
    #

    def cardsMatch(self, card1, card2):
        if card1.suit != card2.suit:
            return 0
        if card1.suit == 3:
            if card1.rank >= 8:
                return card2.rank >= 8
            if card1.rank >= 4:
                return 7 >= card2.rank >= 4
        return card1.rank == card2.rank


## mahjongg util
def comp_cardset(ncards):
    # calc decks, ranks & trumps
    assert ncards % 4 == 0
    assert 0 < ncards <= 288 # ???
    decks = 1
    cards = ncards/4
    if ncards > 144:
        assert ncards % 8 == 0
        decks = 2
        cards = cards/2
    ranks, trumps = divmod(cards, 3)
    if ranks > 10:
        trumps += (ranks-10)*3
        ranks = 10
    if trumps > 4:
        trumps = 4+(trumps-4)*4
    assert 0 <= ranks <= 10 and 0 <= trumps <= 12
    return decks, ranks, trumps

# ************************************************************************
# * register a Mahjongg type game
# ************************************************************************

from new import classobj

def r(id, short_name, name=None, ncards=144, layout=None):
    assert layout
    if not name:
        name = "Mahjongg " + short_name
    classname = re.sub('\W', '', name)
    # create class
    gameclass = classobj(classname, (AbstractMahjonggGame,), {})
    gameclass.L = layout
    gameclass.NCARDS = ncards
    decks, ranks, trumps = comp_cardset(ncards)
    gi = GameInfo(id, gameclass, name,
                  GI.GT_MAHJONGG, 4*decks, 0, ##GI.SL_MOSTLY_SKILL,
                  category=GI.GC_MAHJONGG, short_name=short_name,
                  suits=range(3), ranks=range(ranks), trumps=range(trumps),
                  si={"decks": decks, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "mahjongg.html"
    registerGame(gi)
    return gi

