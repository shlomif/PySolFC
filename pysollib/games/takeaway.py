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
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# ************************************************************************
# * Take Away
# ************************************************************************

class TakeAway_Foundation(AbstractFoundationStack):

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return True
        c1, c2, mod = self.cards[-1], cards[0], self.cap.mod
        return (c1.rank == (c2.rank + 1) % mod or
                c2.rank == (c1.rank + 1) % mod)

    def closeStack(self):
        pass

    def getHelp(self):
        return _('Foundation. Build up or down regardless of suit.')


class TakeAway(Game):

    RowStack_Class = BasicRowStack
    Foundation_Class = StackWrapper(TakeAway_Foundation, max_move=0, mod=13)

    #
    # game layout
    #

    def createGame(self, reserves=6):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 2*l.XM+10*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=0))
            x += l.XS
        x += l.XM
        for i in range(6):
            stack = self.Foundation_Class(x, y, self, suit=ANY_SUIT,
                                          base_rank=ANY_RANK)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.foundations.append(stack)
            x += l.XS
        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(10):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow()


# ************************************************************************
# * Four Stacks
# ************************************************************************

class FourStacks_RowStack(AC_RowStack):
    getBottomImage = Stack._getReserveBottomImage    

class FourStacks(Game):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+10*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(10):
            s.rows.append(FourStacks_RowStack(x, y, self))
            x += l.XS
        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    def startGame(self):
        rows = self.s.rows[:4]
        for i in range(10):
            self.s.talon.dealRow(rows=rows, frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow(rows=rows)

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isAlternateColorSequence(s.cards):
                    return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Striptease
# ************************************************************************

class Striptease_RowStack(UD_RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return False
        if not self.cards:
            return True
        r1, r2 = self.cards[-1].rank, cards[0].rank
        if ((r1 == JACK and r2 == KING) or
            (r2 == JACK and r1 == KING)):
            return True
        return ((r1+1) % 13 == r2 or (r2+1) % 13 == r1)

    getBottomImage = Stack._getReserveBottomImage


class Striptease_Reserve(OpenStack):
    def canFlipCard(self):
        if not OpenStack.canFlipCard(self):
            return False
        for r in self.game.s.reserves:
            if len(r.cards) > 2:
                return False
        return True


class Striptease(TakeAway):

    def createGame(self):
        l, s = Layout(self), self.s
        w, h = l.XM+9*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        x, y = l.XM, l.YM
        for i in range(4):
            stack = Striptease_Reserve(x, y, self, max_move=1,
                                       min_cards=1, max_accept=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.reserves.append(stack)
            x += l.XS
        x += l.XS
        for i in range(4):
            stack = Striptease_RowStack(x, y, self, max_move=0, mod=13)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.rows.append(stack)
            x += l.XS
        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        l.defaultAll()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == QUEEN, None))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.s.talon.dealRow(rows=self.s.reserves, flip=0, frames=0)
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.reserves)

    def isGameWon(self):
        for r in self.s.reserves:
            if len(r.cards) != 1:
                return False
        return True

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        r1, r2 = card1.rank, card2.rank
        if r1 == QUEEN or r2 == QUEEN:
            return False
        if ((r1 == JACK and r2 == KING) or
            (r2 == JACK and r1 == KING)):
            return True
        return ((r1+1) % 13 == r2 or (r2+1) % 13 == r1)


# register the game
registerGame(GameInfo(334, TakeAway, "Take Away",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(335, FourStacks, "Four Stacks",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(654, Striptease, "Striptease",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))

