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

# imports
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# ************************************************************************
# * Tower of Hanoy
# ************************************************************************

class TowerOfHanoy_Hint(CautiousDefaultHint):
    # FIXME: demo is completely clueless
    pass


class TowerOfHanoy_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return 1
        return self.cards[-1].rank > cards[0].rank

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class TowerOfHanoy(Game):
    RowStack_Class = TowerOfHanoy_RowStack
    Hint_Class = TowerOfHanoy_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to XX cards are fully playable in default window size)
        h = max(2*l.YS, l.YS + (len(self.cards)-1)*l.YOFFSET + l.YM)
        self.setSize(l.XM + 5*l.XS, l.YM + l.YS + h)

        # create stacks
        for i in range(3):
            x, y, = l.XM + (i+1)*l.XS, l.YM
            s.rows.append(self.RowStack_Class(x, y, self, max_accept=1, max_move=1))
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow()

    def isGameWon(self):
        for s in self.s.rows:
            if len(s.cards) == len(self.cards):
                return 1
        return 0

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


# ************************************************************************
# * Hanoi Puzzle
# ************************************************************************

class HanoiPuzzle_RowStack(TowerOfHanoy_RowStack):
    def getBottomImage(self):
        if self.id == len(self.game.s.rows) - 1:
            return self.game.app.images.getSuitBottom()
        return self.game.app.images.getReserveBottom()


class HanoiPuzzle4(TowerOfHanoy):
    RowStack_Class = HanoiPuzzle_RowStack

    def _shuffleHook(self, cards):
        # no shuffling
        return self._shuffleHookMoveToTop(cards, lambda c: (1, -c.id))

    def startGame(self):
        self.startDealSample()
        for i in range(len(self.cards)):
            self.s.talon.dealRow(rows=self.s.rows[:1])

    def isGameWon(self):
        return len(self.s.rows[-1].cards) == len(self.cards)


class HanoiPuzzle5(HanoiPuzzle4):
    pass


class HanoiPuzzle6(HanoiPuzzle4):
    pass


# register the game
registerGame(GameInfo(124, TowerOfHanoy, "Tower of Hanoy",
                      GI.GT_PUZZLE_TYPE, 1, 0, GI.SL_SKILL,
                      suits=(2,), ranks=range(9)))
registerGame(GameInfo(207, HanoiPuzzle4, "Hanoi Puzzle 4",
                      GI.GT_PUZZLE_TYPE, 1, 0, GI.SL_SKILL,
                      suits=(2,), ranks=range(4),
                      rules_filename="hanoipuzzle.html"))
registerGame(GameInfo(208, HanoiPuzzle5, "Hanoi Puzzle 5",
                      GI.GT_PUZZLE_TYPE, 1, 0, GI.SL_SKILL,
                      suits=(2,), ranks=range(5),
                      rules_filename="hanoipuzzle.html"))
registerGame(GameInfo(209, HanoiPuzzle6, "Hanoi Puzzle 6",
                      GI.GT_PUZZLE_TYPE, 1, 0, GI.SL_SKILL,
                      suits=(2,), ranks=range(6),
                      rules_filename="hanoipuzzle.html"))

