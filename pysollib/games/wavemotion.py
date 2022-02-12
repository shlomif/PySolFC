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
        AC_RowStack, \
        InitialDealTalonStack, \
        OpenStack, \
        SS_RowStack, \
        StackWrapper, \
        isAlternateColorSequence, \
        isSameSuitSequence
from pysollib.util import ANY_RANK

# ************************************************************************
# * Wave Motion
# ************************************************************************


class WaveMotion(Game):
    RowStack_Class = SS_RowStack
    Reserve_Class = StackWrapper(OpenStack, max_accept=0)

    CAN_MOVE_RESERVES = False

    #
    # game layout
    #

    def createGame(self, rows=8, reserves=8, playcards=7):
        # create layout
        l, s = Layout(self), self.s

        # set window
        max_rows = max(rows, reserves)
        w, h = l.XM + max_rows*l.XS, l.YM + 2*l.YS + (14+playcards)*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM + (max_rows-rows) * l.XS // 2, l.YM
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self, base_rank=ANY_RANK)
            stack.getBottomImage = stack._getReserveBottomImage
            s.rows.append(stack)
            x += l.XS
        x, y = l.XM + (max_rows-reserves)*l.XS//2, l.YM+l.YS+14*l.YOFFSET
        for i in range(reserves):
            stack = self.Reserve_Class(x, y, self)
            s.reserves.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            x += l.XS

        s.talon = InitialDealTalonStack(l.XM, l.YM, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow(rows=self.s.reserves[:4])

    def isGameWon(self):
        cardsPlayed = False
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isSameSuitSequence(s.cards):
                    return False
                cardsPlayed = True
        if not cardsPlayed:
            return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Flourish
# ************************************************************************

class Flourish(WaveMotion):
    RowStack_Class = AC_RowStack

    def createGame(self):
        WaveMotion.createGame(self, rows=7, reserves=8, playcards=7)

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isAlternateColorSequence(s.cards):
                    return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Flow
# ************************************************************************

class Flow_ReserveStack(SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if len(self.cards) == 0 and len(cards) > 1:
            return False
        return SS_RowStack.acceptsCards(self, from_stack, cards)


class Flow(WaveMotion):
    Reserve_Class = StackWrapper(Flow_ReserveStack, base_rank=ANY_RANK)

    def createGame(self):
        WaveMotion.createGame(self, rows=8, reserves=8, playcards=14)


# register the game
registerGame(GameInfo(314, WaveMotion, "Wave Motion",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(753, Flourish, "Flourish",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(841, Flow, "Flow",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
