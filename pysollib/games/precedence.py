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
        ReserveStack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import KING


# ************************************************************************
# * Precedence
# ************************************************************************


class Precedence_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if (not self.cards):
            if (self.id > 0 and not self.game.s
                    .foundations[self.id - 1].cards):
                return False
            if self.id == 0:
                return cards[0].rank == KING
            return cards[0].rank == (self.game.s
                                     .foundations[self.id - 1]
                                     .cards[0].rank - 1) % 13
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        return True


class Precedence(Game):
    FOUNDATIONS = 8
    RESERVES = 0
    NUM_ROUNDS = 3

    TALON_STACK = WasteTalonStack
    WASTE_STACK = WasteStack
    RESERVE_STACK = ReserveStack

    def createGame(self):
        layout, s = Layout(self), self.s
        self.setSize(layout.XM + self.FOUNDATIONS * layout.XS,
                     layout.YM + 2 * layout.YS)
        x, y = layout.XM, layout.YM
        for i in range(self.FOUNDATIONS):
            c_max = (self.gameinfo.decks * 52) / self.FOUNDATIONS
            s.foundations.append(Precedence_Foundation(x, y, self, dir=-1,
                                                       mod=13,
                                                       max_move=0,
                                                       max_cards=c_max))
            x += layout.XS
        x, y = layout.XM + (layout.XS * 3), layout.YM + layout.YS
        s.talon = self.TALON_STACK(x, y, self,
                                   max_rounds=self.NUM_ROUNDS, num_deal=1)
        layout.createText(s.talon, 'nw')
        layout.createRoundText(s.talon, 'se', dx=layout.XS)
        x += layout.XS
        s.waste = self.WASTE_STACK(x, y, self)
        layout.createText(s.waste, 'ne')

        x += 2 * layout.XS
        for i in range(self.RESERVES):
            s.reserves.append(self.RESERVE_STACK(x, y, self, max_cards=104))
            x += layout.XS

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


# ************************************************************************
# * Display
# ************************************************************************

class Display_Talon(WasteTalonStack):
    def _redeal(self):
        game, num_cards = self.game, len(self.cards)
        if len(self.waste.cards) > 0:
            game.moveMove(1, self.waste, game.s.reserves[0], frames=2)
        rows = list(game.s.reserves)[:]
        rows.reverse()
        for r in rows:
            while r.cards:
                num_cards = num_cards + 1
                game.moveMove(1, r, self, frames=2)
                if self.cards[-1].face_up:
                    game.flipMove(self)
        assert len(self.cards) == num_cards
        self.game.nextRoundMove(self)

    def canDealCards(self):
        return ((self.round > 1 and len(self.cards) > 0)
                or (self.round == 1 and len(self.cards) == 0)
                or (len(self.waste.cards) == 0))

    def dealCards(self, sound=False):
        if self.cards:
            return WasteTalonStack.dealCards(self, sound=sound)
        if sound:
            self.game.startDealSample()
        self._redeal()
        if sound:
            self.game.stopSamples()
        return


class Display_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        return self.game.s.talon.round == 1 and from_stack == self.game.s.waste


class Display(Precedence):
    FOUNDATIONS = 13
    RESERVES = 3
    NUM_ROUNDS = 2

    TALON_STACK = Display_Talon
    RESERVE_STACK = Display_ReserveStack

    def _shuffleHook(self, cards):
        return cards

    def _autoDeal(self, sound=True):
        # only autodeal if there are cards in the talon.
        if len(self.s.talon.cards) > 0:
            return Game._autoDeal(self, sound=sound)


# register the game
registerGame(GameInfo(790, Precedence, "Precedence",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK,
                      altnames=("Order of Precedence", "Succession")))
registerGame(GameInfo(791, PrecedenceNoKing, "Precedence (No King)",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(832, Display, "Display",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_BALANCED))
