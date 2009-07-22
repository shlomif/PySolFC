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
# * Eiffel Tower
# ************************************************************************

class EiffelTower_RowStack(OpenStack):
    def __init__(self, x, y, game):
        OpenStack.__init__(self, x, y, game, max_move=0, max_accept=1)
        self.CARD_YOFFSET = 1

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        return self.cards[-1].rank + cards[0].rank == 12


class EiffelTower(Game):
    Talon_Class = WasteTalonStack
    Waste_Class = WasteStack

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8.5*l.XS, l.YM + 6*l.YS)

        # create stacks
        y = l.YM
        for d in ((1, 2.5), (2, 2), (3, 1.5), (4, 1), (5, 0.5), (5, 0.5)):
            x = l.XM + d[1] * l.XS
            for i in range(d[0]):
                s.rows.append(EiffelTower_RowStack(x, y, self))
                x = x + l.XS
            y = y + l.YS
        x = l.XM + 6 * l.XS
        y = l.YM + 5 * l.YS / 2
        s.waste = self.Waste_Class(x, y, self)
        l.createText(s.waste, "s")
        x = x + l.XS
        s.talon = self.Talon_Class(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        return len(self.s.talon.cards) == 0 and len(self.s.waste.cards) == 0

    def getAutoStacks(self, event=None):
        return ((), (), ())

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + card2.rank == 12


# ************************************************************************
# * Strict Eiffel Tower
# ************************************************************************

class StrictEiffelTower(EiffelTower):
    Waste_Class = StackWrapper(WasteStack, max_cards=2)


# register the game
registerGame(GameInfo(16, EiffelTower, "Eiffel Tower",
                      GI.GT_PAIRING_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
##registerGame(GameInfo(801, StrictEiffelTower, "Strict Eiffel Tower",
##                      GI.GT_PAIRING_TYPE, 2, 0))

