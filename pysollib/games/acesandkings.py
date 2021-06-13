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
    BasicRowStack, \
    OpenStack, \
    RK_FoundationStack, \
    WasteStack, \
    WasteTalonStack
from pysollib.util import KING, ACE


# ************************************************************************
# * Aces and Kings
# ************************************************************************

class AcesAndKings_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        return len(cards) == 1 and len(self.cards) == 0


class AcesAndKings(Game):
    #
    # game layout
    #
    def createGame(self, rows=4, max_rounds=1, num_deal=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (8.5 * l.XS), l.YM + (3 * l.YS))

        # create stacks
        x, y = l.XM, l.YM
        for i in range(2):
            stack = OpenStack(x, y, self)
            stack.CARD_XOFFSET = l.XOFFSET
            l.createText(stack, "sw")
            s.reserves.append(stack)
            x += 4.5 * l.XS

        x, y = l.XM, y + l.YS
        for i in range(4):
            s.foundations.append(RK_FoundationStack(x, y, self, suit=i,
                                                    base_rank=ACE, dir=1))
            x = x + l.XS
        x = x + (l.XS / 2)
        for i in range(4):
            s.foundations.append(RK_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            x = x + l.XS
        x, y = l.XM + l.XS, y + l.YS
        s.talon = WasteTalonStack(
            x, y, self, max_rounds=max_rounds, num_deal=num_deal)
        l.createText(s.talon, "sw")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se", text_format="%D")
        x += 2.5 * l.XS
        for i in range(rows):
            s.rows.append(AcesAndKings_RowStack(x, y, self, max_accept=1))
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
            self.s.talon.moveMove(1, stack)


# register the game
registerGame(GameInfo(800, AcesAndKings, "Aces and Kings",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
