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
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
    BasicRowStack, \
    OpenStack, \
    RK_FoundationStack, \
    StackWrapper, \
    UD_RK_RowStack, \
    WasteStack, \
    WasteTalonStack
from pysollib.util import ACE, KING, NO_RANK, QUEEN, RANKS, \
    UNLIMITED_ACCEPTS, \
    UNLIMITED_CARDS


# ************************************************************************
# * Aces and Kings
# ************************************************************************

class AcesAndKings(Game):
    RowStack_Class = BasicRowStack
    Foundation_Class = RK_FoundationStack

    NUM_RESERVES = 2
    NUM_TABLEAU = 4
    FOUNDATION_SETS = ((ACE, KING),)

    PLAYCARDS = 0

    #
    # game layout
    #
    def createGame(self, max_rounds=1, num_deal=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (8.5 * l.XS), l.YM +
                     ((2 + len(self.FOUNDATION_SETS)) * l.YS) +
                     (self.PLAYCARDS * l.YOFFSET))

        # create stacks
        x, y = 2 * l.XM, l.YM

        w1, w2 = (10 * (l.XS + l.XM)) / self.NUM_RESERVES, 2 * l.XS
        if w2 + 13 * l.XOFFSET > w1:
            l.XOFFSET = int((w1 - w2) / 13)

        for i in range(self.NUM_RESERVES):
            stack = OpenStack(x, y, self)
            stack.CARD_XOFFSET = l.XOFFSET
            l.createText(stack, "sw")
            s.reserves.append(stack)
            x += (9 / self.NUM_RESERVES) * l.XS

        x, y = l.XM, y + l.YS

        font = self.app.getFont("canvas_default")

        for i in self.FOUNDATION_SETS:
            for j in range(4):
                stack = self.Foundation_Class(x, y, self, suit=j,
                                              base_rank=i[0], dir=1,
                                              max_cards=(13 - i[0]),
                                              mod=13)
                stack.getBottomImage = stack._getReserveBottomImage
                if self.preview <= 1:
                    stack.texts.misc = MfxCanvasText(self.canvas,
                                                     x + l.CW // 2,
                                                     y + l.CH // 2,
                                                     anchor="center",
                                                     font=font)
                    stack.texts.misc.config(text=(RANKS[i[0]][0]))
                s.foundations.append(stack)

                x = x + l.XS
            x = x + (l.XS / 2)
            for j in range(4):
                stack = self.Foundation_Class(x, y, self, suit=j,
                                              base_rank=i[1], dir=-1,
                                              max_cards=(i[1] + 1),
                                              mod=13)
                stack.getBottomImage = stack._getReserveBottomImage
                if self.preview <= 1:
                    stack.texts.misc = MfxCanvasText(self.canvas,
                                                     x + l.CW // 2,
                                                     y + l.CH // 2,
                                                     anchor="center",
                                                     font=font)
                    stack.texts.misc.config(text=(RANKS[i[1]][0]))
                s.foundations.append(stack)

                x = x + l.XS
            x, y = l.XM, y + l.YS
        x += (2.5 * l.XM)
        s.talon = WasteTalonStack(
            x, y, self, max_rounds=max_rounds, num_deal=num_deal)
        l.createText(s.talon, "sw")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se", text_format="%D")
        x = ((8.5 - self.NUM_TABLEAU) * l.XS) + l.XM
        for i in range(self.NUM_TABLEAU):
            s.rows.append(self.RowStack_Class(x, y, self, max_accept=1,
                                              max_cards=1))
            x = x + l.XS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        for i in range(13):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.s.talon.dealRow(rows=self.s.rows)
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards and stack in self.s.rows and self.s.talon.cards:
            old_state = self.enterState(self.S_FILL)
            self.s.talon.moveMove(1, stack)
            self.leaveState(old_state)


# ************************************************************************
# * Acey and Kingsley
# ************************************************************************

class AceyAndKingsley(AcesAndKings):
    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(
            cards,
            lambda c: (c.rank in (ACE, KING) and c.deck == 0,
                       (c.rank, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        AcesAndKings.startGame(self)


# ************************************************************************
# * Racing Aces
# ************************************************************************

class RacingAces(AcesAndKings):
    NUM_RESERVES = 3
    NUM_TABLEAU = 6
    FOUNDATION_SETS = ((ACE, KING), (6, 5))


# ************************************************************************
# * Deuces and Queens
# ************************************************************************

class DeucesAndQueens(AcesAndKings):
    RowStack_Class = StackWrapper(UD_RK_RowStack, max_accept=UNLIMITED_ACCEPTS,
                                  max_cards=UNLIMITED_CARDS, mod=13,
                                  base_rank=NO_RANK)
    Foundation_Class = StackWrapper(RK_FoundationStack, max_cards=13)

    NUM_RESERVES = 3
    FOUNDATION_SETS = ((1, QUEEN),)
    PLAYCARDS = 12


# register the game
registerGame(GameInfo(800, AcesAndKings, "Aces and Kings",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(814, AceyAndKingsley, "Acey and Kingsley",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(820, RacingAces, "Racing Aces",
                      GI.GT_3DECK_TYPE, 3, 0, GI.SL_BALANCED))
registerGame(GameInfo(911, DeucesAndQueens, "Deuces and Queens",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
