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
from pysollib.hint import AbstractHint
from pysollib.layout import Layout
from pysollib.stack import \
        InitialDealTalonStack, \
        InvisibleStack, \
        OpenStack

# ************************************************************************
# * Tile Puzzle Row Stack
# ************************************************************************


class TilePuzzle_RowStack(OpenStack):

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        self._swapPairMove(ncards, to_stack, frames=-1, shadow=0)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=frames, shadow=shadow)
        game.moveMove(n, swap, other_stack, frames=0)
        game.leaveState(old_state)

# ************************************************************************
# * Tile Puzzle Hint
# ************************************************************************


class TilePuzzle_Hint(AbstractHint):

    def computeHints(self):
        # The hint should point one piece to its correct location.
        rows = self.game.s.rows
        for row in rows:
            if row.cards[0].rank != row.id:
                self.addHint(5000, 1, row, rows[row.cards[0].rank])

# ************************************************************************
# * Tile Puzzle Game
# ************************************************************************


class TilePuzzle(Game):
    Hint_Class = TilePuzzle_Hint

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
                s.rows.append(TilePuzzle_RowStack(x, y, self,
                                                  max_accept=1, max_cards=2))
                x = x + l.CW

        # Create talon
        x, y = -2*l.XS, 0               # invisible
        s.talon = InitialDealTalonStack(x, y, self)

        s.internals.append(InvisibleStack(self))

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows, frames=3)

    def isGameWon(self):
        if self.busy:
            return 0
        s = self.s.rows
        for r in s[:len(s)]:
            if not r.cards[0].rank == r.id:
                return 0
        self.s.talon.dealRow(rows=s, frames=0)
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1 == card2.rank) or
                (card1.rank - 1 == card2.rank))

    def parseCard(self, card):
        return str(card.rank + 1)

# ************************************************************************
# * Register a Tile Puzzle game
# ************************************************************************


def r(id, short_name, width):
    name = short_name
    ncards = width ** 2
    gi = GameInfo(
        id, TilePuzzle, name,
        GI.GT_PUZZLE_TYPE, 1, 0, GI.SL_SKILL,
        category=GI.GC_PUZZLE, short_name=short_name,
        subcategory=width,
        suits=(), ranks=(), trumps=list(range(ncards)),
        si={"decks": 1, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "tilepuzzle.html"
    registerGame(gi)
    return gi


r(22353, "Tile Puzzle 3x3", 3)
r(22354, "Tile Puzzle 4x4", 4)
r(22355, "Tile Puzzle 5x5", 5)
r(22356, "Tile Puzzle 6x6", 6)
r(22357, "Tile Puzzle 7x7", 7)
r(22358, "Tile Puzzle 8x8", 8)
r(22359, "Tile Puzzle 9x9", 9)
r(22360, "Tile Puzzle 10x10", 10)

del r
