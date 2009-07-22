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
import sys, types

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# *
# ************************************************************************

class StHelena_Talon(TalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds:
            return False
        return not self.game.isGameWon()

    def dealCards(self, sound=False):
        # move all cards to the Talon and redeal
        lr = len(self.game.s.rows)
        num_cards = 0
        assert len(self.cards) == 0
        for r in self.game.s.rows[::-1]:
            for i in range(len(r.cards)):
                num_cards = num_cards + 1
                self.game.moveMove(1, r, self, frames=0)
        assert len(self.cards) == num_cards
        if num_cards == 0:          # game already finished
            return 0
        # redeal
        self.cards.reverse()
        self.game.nextRoundMove(self)
        self.game.startDealSample()
        for i in range(lr):
            k = min(lr, len(self.cards))
            for j in range(k):
                self.game.moveMove(1, self, self.game.s.rows[j], frames=4)
        # done
        self.game.stopSamples()
        assert len(self.cards) == 0
        return num_cards


class StHelena_FoundationStack(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.game.s.talon.round == 1:
            if (self.cap.base_rank == KING and
                from_stack in self.game.s.rows[6:10:]):
                return False
            if (self.cap.base_rank == ACE and
                from_stack in self.game.s.rows[:4]):
                return False
        return True


class StHelena(Game):

    Hint_Class = CautiousDefaultHint
    Talon_Class = StackWrapper(StHelena_Talon, max_rounds=3)
    Foundation_Class = StHelena_FoundationStack
    RowStack_Class = StackWrapper(UD_RK_RowStack, base_rank=NO_RANK)

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 3*l.XM+6*l.XS, 3*l.YM+4*l.YS
        self.setSize(w, h)

        # create stacks
        lay = (
            (2, 1, 1, 0),
            (2, 2, 1, 0),
            (2, 3, 1, 0),
            (2, 4, 1, 0),
            (3, 5, 2, 1),
            (3, 5, 2, 2),
            (2, 4, 3, 3),
            (2, 3, 3, 3),
            (2, 2, 3, 3),
            (2, 1, 3, 3),
            (1, 0, 2, 2),
            (1, 0, 2, 1),
            )
        for xm, xs, ym, ys in lay:
            x, y = xm*l.XM+xs*l.XS, ym*l.YM+ys*l.YS
            stack = self.RowStack_Class(x, y, self, max_move=1, max_accept=1)
            stack.CARD_XOFFSET = stack.CARD_YOFFSET = 0
            s.rows.append(stack)
        x, y = 2*l.XM+l.XS, 2*l.YM+l.YS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i,
                                                       base_rank=KING, dir=-1))
            x = x + l.XS
        x, y = 2*l.XM+l.XS, 2*l.YM+2*l.YS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
            x = x + l.XS

        s.talon = self.Talon_Class(l.XM, l.YM, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.deck == 0 and c.rank in (0, 12), (-c.rank, c.suit)), 8)

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(self.s.foundations)

    shallHighlightMatch = Game._shallHighlightMatch_RK

# ************************************************************************
# * Box Kite
# ************************************************************************

class BoxKite(StHelena):
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = StackWrapper(UD_RK_RowStack, base_rank=NO_RANK, mod=13)

    shallHighlightMatch = Game._shallHighlightMatch_RKW



# ************************************************************************
# * Les Quatre Coins
# ************************************************************************

class LesQuatreCoins_RowStack(UD_RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not UD_RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return len(self.game.s.talon.cards) == 0


class LesQuatreCoins_Talon(RedealTalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds:
            return len(self.cards) != 0
        return not self.game.isGameWon()

    def dealCards(self, sound=False):
        if not self.cards:
            RedealTalonStack.redealCards(self, sound=False)
        if sound and not self.game.demo:
            self.game.startDealSample()
        rows = self.game.s.rows
        rows = rows[:1]+rows[4:8]+rows[2:3]+rows[1:2]+rows[8:]+rows[3:4]
        num_cards = self.dealRowAvail(rows=rows)
        if sound and not self.game.demo:
            self.game.stopSamples()
        return num_cards


class LesQuatreCoins_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        if self.game.s.talon.cards:
            if from_stack in self.game.s.rows[4:]:
                i = list(self.game.s.foundations).index(self)
                j = list(self.game.s.rows).index(from_stack)
                return i == j-4
        return True


class LesQuatreCoins(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+7*l.XS, l.YM+5*l.YS)

        for i, j in ((0,0),(5,0),(0,4),(5,4)):
            x, y = l.XM+l.XS+i*l.XS, l.YM+j*l.YS
            stack = LesQuatreCoins_RowStack(x, y, self,
                                            max_move=1, base_rank=NO_RANK)
            s.rows.append(stack)
            stack.CARD_YOFFSET = 0
        for x in (l.XM+2*l.XS, l.XM+5*l.XS):
            y = l.YM+l.YS/2
            for j in range(4):
                stack = LesQuatreCoins_RowStack(x, y, self,
                                                max_move=1, base_rank=NO_RANK)
                s.rows.append(stack)
                stack.CARD_YOFFSET = 0
                y += l.YS
        x, y = l.XM+3*l.XS, l.YM+l.YS/2
        for i in range(4):
            s.foundations.append(LesQuatreCoins_Foundation(x, y, self, suit=i))
            y += l.YS
        x, y = l.XM+4*l.XS, l.YM+l.YS/2
        for i in range(4):
            s.foundations.append(LesQuatreCoins_Foundation(x, y, self, suit=i,
                                 base_rank=KING, dir=-1))
            y += l.YS

        x, y = l.XM, l.YM+2*l.YS
        s.talon = LesQuatreCoins_Talon(x, y, self, max_rounds=3)
        l.createText(s.talon, 's')
        l.createRoundText(s.talon, 'nn')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Regal Family
# ************************************************************************

class RegalFamily_RowStack(UD_SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not UD_SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return len(self.game.s.talon.cards) == 0


class RegalFamily(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+5*l.YS)

        for i, j in ((0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),
                     (6,1),(6,2),(6,3),
                     (6,4),(5,4),(4,4),(3,4),(2,4),(1,4),(0,4),
                     (0,3),(0,2),(0,1)
                     ):
            x, y = l.XM+l.XS+i*l.XS, l.YM+j*l.YS
            stack = RegalFamily_RowStack(x, y, self,
                                         max_move=1, base_rank=NO_RANK)
            s.rows.append(stack)
            stack.CARD_YOFFSET = 0

        x, y = l.XM+3*l.XS, l.YM+l.YS
        for i in range(3):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 base_rank=9, mod=13, dir=-1))
            s.foundations.append(SS_FoundationStack(x, y+2*l.YS, self, suit=i,
                                 base_rank=9, mod=13, dir=-1))
            x += l.XS
        x, y = l.XM+3*l.XS, l.YM+2*l.YS
        s.foundations.append(SS_FoundationStack(x, y, self, suit=3,
                             base_rank=ACE, mod=13))
        x += 2*l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, suit=3,
                             base_rank=JACK, mod=13, dir=-1))

        x, y = l.XM, l.YM+2*l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 's')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


    shallHighlightMatch = Game._shallHighlightMatch_SS



# register the game
registerGame(GameInfo(302, StHelena, "St. Helena",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED,
                      altnames=("Napoleon's Favorite",
                                "Washington's Favorite")
                      ))
registerGame(GameInfo(408, BoxKite, "Box Kite",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(620, LesQuatreCoins, "Les Quatre Coins",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(621, RegalFamily, "Regal Family",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))

