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
from pysollib.pysoltk import MfxCanvasText

# ************************************************************************
# * Doublets
# ************************************************************************

class Doublets_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards:
            # check the rank
            if (2 * self.cards[-1].rank + 1) % self.cap.mod != cards[0].rank:
                return False
        return True


class Doublets(Game):
    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 5.5*l.XS, l.YM + 4*l.YS)

        # create stacks
        for dx, dy in ((0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)):
            x, y = l.XM + (2*dx+5)*l.XS/2, l.YM + (2*dy+1)*l.YS/2
            s.rows.append(ReserveStack(x, y, self))
        dx, dy = 1, 2
        x, y = l.XM + (2*dx+5)*l.XS/2, l.YM + (2*dy+1)*l.YS/2
        s.foundations.append(Doublets_Foundation(x, y, self, ANY_SUIT,
                                                 dir=0, mod=13,
                                                 max_move=0, max_cards=48))
        l.createText(s.foundations[0], "s")
##        help = "A, 2, 4, 8, 3, 6, Q, J, 9, 5, 10, 7, A, ..."
##        self.texts.help = MfxCanvasText(self.canvas, x + l.CW/2, y + l.YS + l.YM, anchor="n", text=help)
        x, y = l.XM, l.YM + 3*l.YS/2
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")
        l.createRoundText(s.talon, 'nn')

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move all Kings in the first 8 cards to the bottom
        kings, topcards = [], []
        for c in cards[:]:
            cards.remove(c)
            if c.rank == KING:
                kings.append(c)
            else:
                topcards.append(c)
                if len(topcards) == 8:
                    break
        return kings + cards + topcards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        if self.s.talon.cards or self.s.waste.cards:
            return False
        return len(self.s.foundations[0].cards) == 48

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            elif self.s.talon.canDealCards():
                self.s.talon.dealCards()
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


# register the game
registerGame(GameInfo(111, Doublets, "Doublets",
                      GI.GT_1DECK_TYPE, 1, 2, GI.SL_MOSTLY_LUCK,
                      altnames=('Double or Quits',) ))

