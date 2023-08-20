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
        AbstractFoundationStack, \
        BasicRowStack, \
        OpenStack, \
        ReserveStack, \
        TalonStack
from pysollib.util import ANY_SUIT, JACK, KING, NO_RANK, QUEEN

# ************************************************************************
# * Clear the Dungeon
# ************************************************************************


class ClearTheDungeon_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        cardnum = 0
        goal_rank = 0
        goal_suit = 0
        total = 0
        for card in self.cards:
            if card.face_up:
                if cardnum == 0:
                    goal_rank = card.rank + 1
                    goal_suit = card.suit
                elif cardnum == 1:
                    if card.suit == 4:
                        total += 10
                    else:
                        total += (card.rank + 1)
                cardnum += 1
        if cards[0].suit == 4:
            new_val = 10
        else:
            new_val = cards[0].rank + 1
        if cardnum == 1:
            if new_val + 10 < goal_rank:
                return False
        if cardnum == 2:
            if total + new_val < goal_rank:
                return False
        elif cardnum == 3:
            if cards[0].suit not in (goal_suit, 4):
                return False

        return BasicRowStack.acceptsCards(self, from_stack, cards)


class ClearTheDungeon(Game):
    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 5 * l.XS,
                     l.YM + 2 * l.YS + 12 * l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            s.rows.append(ClearTheDungeon_RowStack(x, y, self,
                                                   max_move=0, max_accept=1,
                                                   dir=0, base_rank=NO_RANK))
            x += l.XS
        s.foundations.append(AbstractFoundationStack(x, y, self, suit=ANY_SUIT,
                                                     max_move=0, max_accept=0,
                                                     max_cards=52))
        x, y = l.XM, self.height - l.YS
        for i in range(3):
            s.reserves.append(OpenStack(x, y, self, max_cards=1, max_accept=0))
            x += l.XS

        x += l.XS
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, "sw")

        y -= l.YS
        s.reserves.append(ReserveStack(x, y, self, max_accept=1, max_move=1,
                                       max_cards=52))

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        topcards = []
        for c in cards[:]:
            if c.rank in (JACK, QUEEN, KING):
                topcards.append(c)
                cards.remove(c)
        topcards.reverse()
        return cards + topcards

    def startGame(self):
        for r in self.s.rows:
            for j in range(2):
                self.s.talon.dealRow(rows=[r], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows)
        self.s.talon.dealRow(rows=self.s.reserves[:3])

    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)

        for s in self.s.rows:
            num_cards = 0
            for c in s.cards:
                if c.face_up:
                    num_cards += 1
            if num_cards == 4:
                s.moveMove(4, self.s.foundations[0])
                if len(s.cards) > 0:
                    s.flipMove()

        if stack in self.s.reserves[:3]:
            for stack in self.s.reserves[:3]:
                if stack.cards:
                    self.leaveState(old_state)
                    return
            self.s.talon.dealRow(rows=self.s.reserves[:3], sound=1)
        self.leaveState(old_state)

    def isGameWon(self):
        for s in self.s.rows:
            if len(s.cards) > 0:
                return False
        return True

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


# register the game
registerGame(GameInfo(909, ClearTheDungeon, "Clear the Dungeon",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL,
                      subcategory=GI.GS_JOKER_DECK, trumps=list(range(2))))
