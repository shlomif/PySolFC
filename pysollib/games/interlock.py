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
from pysollib.hint import Yukon_Hint
from pysollib.layout import Layout
from pysollib.stack import \
        AC_RowStack, \
        InitialDealTalonStack, \
        SS_FoundationStack, \
        StackWrapper, \
        WasteStack, \
        WasteTalonStack, \
        Yukon_AC_RowStack
from pysollib.util import ANY_RANK, KING


# ************************************************************************
# * Interlock
# ************************************************************************

class Interlock_StackMethods:
    STEP = (9, 9, 9, 9, 9, 9, 9, 9, 9,
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10)

    def basicIsBlocked(self):
        r, step = self.game.s.rows, self.STEP
        i, n, mylen = self.id, 1, len(step)
        while i < mylen:
            i = i + step[i]
            n = n + 1
            for j in range(i, i + n):
                if r[j].cards:
                    return True
        return False

    # TODO: The dropdown move logic can be done cleaner - too much duplication.
    def isDropdownMove(self, other_stack):
        if other_stack not in self.game.s.rows or len(self.cards) == 0 \
                or not self.cards[0].face_up:
            return False
        r, step = self.game.s.rows, self.STEP
        i, n, mylen = self.id, 1, len(step)
        while i < mylen:
            i = i + step[i]
            n = n + 1
            for j in range(i, i + n):
                if r[j].cards:
                    if r[j] != other_stack:
                        return False
        return True

    # Use this for dropdown moves, as they are an exception
    # to the normal accept cards logic.
    def dropdownAcceptsCards(self, cards):
        # cards must be an acceptable sequence
        if not self._isAcceptableSequence(cards):
            return False
        # [topcard + cards] must be an acceptable sequence
        if (self.cards and not
                self._isAcceptableSequence([self.cards[-1]] + cards)):
            return False
        return True


class Interlock_RowStack(Interlock_StackMethods, AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if len(self.cards) == 0 and self.id > self.STEP[0] - 1:
            return False
        if (self.isDropdownMove(from_stack) and
                len(cards) == len(from_stack.cards)):
            return self.dropdownAcceptsCards(cards)

        return AC_RowStack.acceptsCards(self, from_stack, cards)


class Interlock(Game):
    RowStack_Class = StackWrapper(Interlock_RowStack, base_rank=KING)
    Talon_Class = StackWrapper(WasteTalonStack, num_deal=1, max_rounds=-1)

    MAX_ROWS = 11
    PLAYCARDS = 13

    TEXT = True
    WASTE = True

    def createGame(self):
        lay, s = Layout(self), self.s
        self.setSize((max(self.MAX_ROWS, 7) * lay.XS) + lay.XM,
                     (2.5 * lay.YS) + (self.PLAYCARDS * lay.YOFFSET) + lay.YM)

        self.min_rows = self.MAX_ROWS - 2
        gap = max(7, self.MAX_ROWS) - self.min_rows
        # create stacks
        for i in range(3):
            x = lay.XM + (gap - i) * lay.XS // 2
            y = lay.YM + lay.TEXT_HEIGHT + lay.YS + i * lay.YS // 4
            for j in range(i + self.min_rows):
                s.rows.append(self.RowStack_Class(x, y, self))
                x = x + lay.XS

        x, y = lay.XM, lay.YM
        s.talon = self.Talon_Class(x, y, self)
        if self.TEXT:
            lay.createText(s.talon, "s")
        if self.WASTE:
            x += lay.XS
            s.waste = WasteStack(x, y, self)
            lay.createText(s.waste, "s")
        x += lay.XS * max(1, (self.MAX_ROWS - 6) // 2)
        for i in range(4):
            x += lay.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i,
                                                    mod=13, max_move=0))

        lay.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:19], flip=1, frames=0)
        self.s.talon.dealRow(rows=self.s.rows[19:])
        self.s.talon.dealCards()  # deal first card to WasteStack

    def _getClosestStack(self, cx, cy, stacks, dragstack):
        closest, cdist = None, 999999999
        # Since we only compare distances,
        # we don't bother to take the square root.
        for stack in stacks:
            # Interlock special: do not consider stacks
            # outside the bottom row that have been emptied.
            if len(stack.cards) == 0 and stack in self.s.rows[self.min_rows:]:
                continue
            dist = (stack.x - cx)**2 + (stack.y - cy)**2
            if dist < cdist:
                closest, cdist = stack, dist
        return closest


# ************************************************************************
# * Love A Duck
# ************************************************************************

class LoveADuck_RowStack(Interlock_StackMethods, Yukon_AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if len(self.cards) == 0 and self.id > self.STEP[0] - 1:
            return False
        if (self.isDropdownMove(from_stack) and
                len(cards) == len(from_stack.cards)):
            return self.dropdownAcceptsCards(cards)

        return Yukon_AC_RowStack.acceptsCards(self, from_stack, cards)

    def dropdownAcceptsCards(self, cards):
        if self.cards and not self._isYukonSequence(self.cards[-1], cards[0]):
            return False
        return True


class LoveADuck(Interlock):
    RowStack_Class = StackWrapper(LoveADuck_RowStack, base_rank=KING)
    Talon_Class = InitialDealTalonStack
    Waste_Class = None
    Hint_Class = Yukon_Hint

    PLAYCARDS = 25

    TEXT = False
    WASTE = False

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:19], flip=1, frames=0)
        for i in range(2):
            self.s.talon.dealRow(rows=self.s.rows[19:], flip=1, frames=0)
        self.s.talon.dealRow(rows=self.s.rows[19:])
        self.s.talon.dealCards()  # deal first card to WasteStack


# ************************************************************************
# * Guardian
# ************************************************************************

class Guardian_RowStack(Interlock_RowStack):
    STEP = (3, 3, 3, 4, 4, 4, 4)


class Guardian(Interlock):
    RowStack_Class = StackWrapper(Guardian_RowStack, base_rank=ANY_RANK)
    Talon_Class = StackWrapper(WasteTalonStack, num_deal=3, max_rounds=-1)

    MAX_ROWS = 5

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:7], flip=0, frames=0)
        self.s.talon.dealRow(rows=self.s.rows[7:])
        self.s.talon.dealCards()  # deal first card to WasteStack


# register the game
registerGame(GameInfo(852, Guardian, "Guardian",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(938, Interlock, "Interlock",
                      GI.GT_KLONDIKE | GI.GT_ORIGINAL, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(939, LoveADuck, "Love a Duck",
                      GI.GT_YUKON | GI.GT_OPEN, 1, 0, GI.SL_BALANCED))
