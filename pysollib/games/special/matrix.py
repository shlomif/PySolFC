#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
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
# ---------------------------------------------------------------------------##

import math

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.pysoltk import bind
from pysollib.stack import \
        InitialDealTalonStack, \
        OpenStack
from pysollib.util import ANY_RANK

# ************************************************************************
# * Matrix Row Stack
# ************************************************************************


class Matrix_RowStack(OpenStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1, max_cards=1,
                  base_rank=ANY_RANK)
        OpenStack.__init__(self, x, y, game, **cap)

    def canFlipCard(self):
        return 0

    def canDropCards(self, stacks):
        return (None, 0)

    def cancelDrag(self, event=None):
        if event is None:
            self._stopDrag()

    def _findCard(self, event):
        # we need to override this because the shade may be hiding
        # the tile (from Tk's stacking view)
        return len(self.cards) - 1

    def _calcMouseBind(self, binding_format):
        return self.game.app.opt.calcCustomMouseButtonsBinding(binding_format)

    def initBindings(self):
        bind(
            self.group,
            self._calcMouseBind("<{mouse_button1}>"),
            self._Stack__clickEventHandler
        )
        bind(
            self.group,
            self._calcMouseBind("<Control-{mouse_button1}>"),
            self._Stack__controlclickEventHandler,
        )

    def getBottomImage(self):
        return self.game.app.images.getBlankBottom()

    def blockMap(self):
        ncards = self.game.gameinfo.ncards
        id, sqrt = self.id, int(math.sqrt(ncards))
        line, row, column = int(id / sqrt), [], []
        for r in self.game.s.rows[line * sqrt:sqrt + line * sqrt]:
            row.append(r.id)
        while id >= sqrt:
            id = id - sqrt
        while id < ncards:
            column.append(id)
            id = id + sqrt
        return [row, column]

    def basicIsBlocked(self):
        stack_map = self.blockMap()
        for j in range(2):
            for i in range(len(stack_map[j])):
                if not self.game.s.rows[stack_map[j][i]].cards:
                    return 0
        return 1

    def clickHandler(self, event):
        game = self.game
        row = game.s.rows
        if not self.cards or game.drag.stack is self or self.basicIsBlocked():
            return 1
        game.playSample("move", priority=10)
        stack_map = self.blockMap()
        for j in range(2):
            dir = 1
            for i in range(len(stack_map[j])):
                to_stack = row[stack_map[j][i]]
                if to_stack is self:
                    dir = -1
                if not to_stack.cards:
                    self._stopDrag()
                    step = 1
                    from_stack = row[stack_map[j][i + dir]]
                    while from_stack is not self:
                        from_stack.playMoveMove(
                            1, to_stack, frames=0, sound=False)
                        to_stack = from_stack
                        step = step + 1
                        from_stack = row[stack_map[j][i + dir * step]]
                    self.playMoveMove(1, to_stack, frames=0, sound=False)
                    return 1
        return 1

    def highlightMatchingCards(self, event):
        self.game.highlightNotMatching()


# ************************************************************************
# * Matrix Game
# ************************************************************************

class Matrix(Game):
    # FIXME: Re-enable hints if a good hint class can be built.
    # But if hints are re-enabled, make sure to disable stuck-checking.
    # You can't get stuck in Matrix games.
    Hint_Class = None

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        grid = math.sqrt(self.gameinfo.ncards)
        assert grid == int(grid)
        grid = int(grid)

        # Set window size
        w, h = l.XM * 2 + l.CW * grid, l.YM * 2 + l.CH * grid
        self.setSize(w, h)

        # Create rows
        for j in range(grid):
            x, y = l.XM, l.YM + l.CH * j
            for i in range(grid):
                s.rows.append(Matrix_RowStack(x, y, self))
                x = x + l.CW

        # Create talon
        x, y = -2*l.XS, 0               # invisible
        s.talon = InitialDealTalonStack(x, y, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game extras
    #

    def _shuffleHook(self, cards):
        # create solved game
        ncards = len(cards)-1
        for c in cards:
            if c.rank == ncards:
                cards.remove(c)
                break
        n = 0
        for i in range(ncards-1):
            for j in range(i+1, ncards):
                if cards[i].rank > cards[j].rank:
                    n += 1
        cards.reverse()
        if n % 2:
            cards[0], cards[1] = cards[1], cards[0]
        return [c]+cards

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:self.gameinfo.ncards - 1],
                             frames=3)

    def isGameWon(self):
        if self.busy:
            return 0
        s = self.s.rows
        mylen = len(s) - 1
        for r in s[:mylen]:
            if not r.cards or not r.cards[0].rank == r.id:
                return 0
        self.s.talon.dealRow(rows=s[mylen:], frames=0)
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1 == card2.rank) or
                (card1.rank - 1 == card2.rank))

    def parseCard(self, card):
        return str(card.rank + 1)


# ************************************************************************
# * Register a Matrix game
# ************************************************************************

def r(id, short_name, width):
    name = short_name
    ncards = width ** 2
    gi = GameInfo(
        id, Matrix, name,
        GI.GT_MATRIX, 1, 0, GI.SL_SKILL,
        category=GI.GC_TRUMP_ONLY, short_name=short_name,
        suits=(), ranks=(), trumps=list(range(ncards)),
        si={"decks": 1, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "matrix.html"
    registerGame(gi)
    return gi


def r2(id, short_name, width):
    name = short_name
    ncards = width ** 2
    gi = GameInfo(
        id, Matrix, name,
        GI.GT_MATRIX, 1, 0, GI.SL_SKILL,
        category=GI.GC_PUZZLE, short_name=short_name,
        subcategory=width,
        suits=(), ranks=(), trumps=list(range(ncards)),
        si={"decks": 1, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "matrix.html"
    registerGame(gi)
    return gi


r(22223, "Matrix 3x3", 3)
r(22224, "Matrix 4x4", 4)
r(22225, "Matrix 5x5", 5)
r(22226, "Matrix 6x6", 6)
r(22227, "Matrix 7x7", 7)
r(22228, "Matrix 8x8", 8)
r(22229, "Matrix 9x9", 9)
r(22230, "Matrix 10x10", 10)
# r(22240, "Matrix 20x20", 20)

r2(22303, "Picture Matrix 3x3", 3)
r2(22304, "Picture Matrix 4x4", 4)
r2(22305, "Picture Matrix 5x5", 5)
r2(22306, "Picture Matrix 6x6", 6)
r2(22307, "Picture Matrix 7x7", 7)
r2(22308, "Picture Matrix 8x8", 8)
r2(22309, "Picture Matrix 9x9", 9)
r2(22310, "Picture Matrix 10x10", 10)

del r
del r2
