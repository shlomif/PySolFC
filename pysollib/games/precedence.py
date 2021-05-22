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

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.stack import \
        RK_FoundationStack, \
        WasteStack, \
        WasteTalonStack


# ************************************************************************
# * Precedence
# ************************************************************************


class Precedence_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if (self.id > 0 and not self.game.s.foundations[self.id - 1].cards):
            return False
        return True


class Precedence(Game):

    def createGame(self):
        layout, s = Layout(self), self.s
        self.setSize(layout.XM + 8 * layout.XS, layout.YM + 2 * layout.YS)
        x, y = layout.XM, layout.YM
        c_rank = 12
        for i in range(8):
            s.foundations.append(Precedence_Foundation(x, y, self, dir=-1,
                                                       mod=13,
                                                       base_rank=c_rank,
                                                       max_move=0))
            x += layout.XS
            c_rank -= 1
        x, y = layout.XM + (layout.XS * 3), layout.YM + layout.YS
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=3, num_deal=1)
        layout.createText(s.talon, 'nw')
        layout.createRoundText(s.talon, 'se', dx=layout.XS)
        x += layout.XS
        s.waste = WasteStack(x, y, self)
        layout.createText(s.waste, 'ne')

        # define stack-groups
        layout.defaultStackGroups()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.rank == 12, c.suit), 1)

    def startGame(self):
        self.startDealSample()
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, self.s.foundations[0])
        self.s.talon.dealCards()


# ************************************************************************
# * Precedence (No King)
# ************************************************************************


class PrecedenceNoKing(Precedence):

    def _shuffleHook(self, cards):
        return cards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()


# register the game
registerGame(GameInfo(790, Precedence, "Precedence",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK,
                      altnames=("Order of Precedence")))
registerGame(GameInfo(791, PrecedenceNoKing, "Precedence (No King)",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
