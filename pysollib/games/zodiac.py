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
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText



# ************************************************************************
# * Zodiac
# ************************************************************************

class Zodiac_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.game.s.waste.cards or self.game.s.talon.cards:
            return False
        return True


class Zodiac_RowStack(UD_SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not UD_SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows:
            return False
        return True


class Zodiac_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows:
            return False
        return True


class Zodiac(Game):

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+12*l.XS, l.YM+5*l.YS
        self.setSize(w, h)

        # create stacks
        x = l.XM
        for i in range(12):
            for y in (l.YM, l.YM+4*l.YS):
                stack = Zodiac_RowStack(x, y, self, base_rank=NO_RANK)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            x += l.XS

        x = l.XM+4*l.XS
        for i in range(4):
            y = l.YM+l.YS
            s.foundations.append(Zodiac_Foundation(x, y, self, suit=i))
            y += 2*l.YS
            s.foundations.append(Zodiac_Foundation(x, y, self, suit=i,
                                                   base_rank=KING, dir=-1))
            x += l.XS

        x, y = l.XM+2*l.XS, l.YM+2*l.YS
        for i in range(8):
            s.reserves.append(Zodiac_ReserveStack(x, y, self))
            x += l.XS

        x, y = l.XM+l.XS, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=UNLIMITED_REDEALS)
        l.createText(s.talon, 'sw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Twelve Sleeping Maids
# ************************************************************************

class TwelveSleepingMaids_Reserve(OpenStack):
    def canFlipCard(self):
        if not OpenStack.canFlipCard(self):
            return False
        for s in self.game.s.rows:
            if not s.cards:
                break
        else:
            return False
        i = list(self.game.s.reserves).index(self)
        if i == 0:
            return True
        if self.game.s.reserves[i-1].cards:
            return False
        return True


class TwelveSleepingMaids(Game):

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+12*l.XS, l.YM+3*l.YS+14*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(12):
            stack = TwelveSleepingMaids_Reserve(x, y, self)
            stack.CARD_YOFFSET = l.YOFFSET
            s.reserves.append(stack)
            x += l.XS

        x, y = l.XM+2*l.XS, l.YM+l.YS+3*l.YOFFSET
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2,
                                                    base_rank=KING, mod=13))
            x += l.XS

        x, y = l.XM+2*l.XS, l.YM+2*l.YS+3*l.YOFFSET
        for i in range(8):
            s.rows.append(SS_RowStack(x, y, self))
            x += l.XS

        x, y = self.width-l.XS, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 'n')
        l.createRoundText(s.talon, 'nnn')

        x -= l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.reserves, flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    shallHighlightMatch = Game._shallHighlightMatch_SS



# register the game
registerGame(GameInfo(467, Zodiac, "Zodiac",
                      GI.GT_2DECK_TYPE, 2, -1, GI.SL_BALANCED))
registerGame(GameInfo(722, TwelveSleepingMaids, "Twelve Sleeping Maids",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))
