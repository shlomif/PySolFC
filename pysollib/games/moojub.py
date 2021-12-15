#!/usr/bin/env python
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

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.stack import \
        DealRowTalonStack, \
        OpenStack, \
        RK_FoundationStack
from pysollib.util import ACE, ANY_SUIT, KING

# ************************************************************************
# * Moojub
# ************************************************************************


class Moojub_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if len(self.cards) > 0:
            return (self.cards[-1].suit == cards[0].suit and
                    RK_FoundationStack.acceptsCards(self, from_stack, cards))

        foundations = self.game.s.foundations

        # Checking each rule for starting a new foundation:
        # Only the next foundation can be built to.
        if self.id > 0 and len(foundations[self.id - 1].cards) == 0:
            return False
        # The suit must match the foundation directly to the left.
        if (self.id > 3 and
                foundations[self.id - 4].cards[0].suit != cards[0].suit):
            return False
        # Two foundations in the same column can't have the same suit.
        if self.id <= 3:
            for i in range(4):
                if (foundations[i].cards and
                        foundations[i].cards[0].suit == cards[0].suit):
                    return False
        # Only the lowest available card of a suit can start a foundation.
        for row in self.game.s.rows:
            if (row.cards and row.cards[-1].suit == cards[0].suit
                    and row.cards[-1].rank < cards[0].rank):
                return False
        # Can't start a foundation with a card that can be played on an
        # existing foundation.
        for foundation in foundations:
            if (foundation.cards and
                    foundation.cards[-1].suit == cards[0].suit and
                    (foundation.cards[-1].rank == cards[0].rank - 1 or
                     (foundation.cards[-1].rank == KING and
                      cards[0].rank == ACE))):
                return False
        return True


class Moojub(Game):
    Foundations = 8

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (l.XS * 1.5) + self.Foundations * l.XS,
                     l.YM + 5 * l.YS)

        # create stacks
        for j in range(self.Foundations):
            for i in range(4):
                x, y, = l.XM + (l.XS * (j + 1.5)), (l.YM + i * l.YS) + l.YS
                s.foundations.append(Moojub_Foundation(x, y, self, ANY_SUIT,
                                                       mod=13, max_move=0))

        for i in range(4):
            x, y, = l.XM, (l.YM + i * l.YS) + l.YS
            s.rows.append(OpenStack(x, y, self))

        x, y, = l.XM, l.YM
        s.talon = DealRowTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'se')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self._startAndDealRow()


# register the game
registerGame(GameInfo(845, Moojub, "Moojub",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
