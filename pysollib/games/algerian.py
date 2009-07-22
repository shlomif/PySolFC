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


# ************************************************************************
# * Carthage
# ************************************************************************

class Carthage_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        if sound:
            self.game.startDealSample()
        if len(self.cards) == len(self.game.s.rows):
            n = self.dealRowAvail(rows=self.game.s.rows, sound=False)
        else:
            n = self.dealRowAvail(rows=self.game.s.reserves, sound=False)
            n += self.dealRowAvail(rows=self.game.s.reserves, sound=False)
        if sound:
            self.game.stopSamples()
        return n


class Carthage(Game):

    Hint_Class = CautiousDefaultHint
    Talon_Class = Carthage_Talon
    Foundation_Classes = (SS_FoundationStack,
                          SS_FoundationStack)
    RowStack_Class = StackWrapper(SS_RowStack, max_move=1)

    #
    # game layout
    #

    def createGame(self, rows=8, reserves=6, playcards=12):
        # create layout
        l, s = Layout(self), self.s

        # set window
        decks = self.gameinfo.decks
        foundations = decks*4
        max_rows = max(foundations, rows)
        w, h = l.XM+(max_rows+1)*l.XS, l.YM+3*l.YS+playcards*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM+l.XS+(max_rows-foundations)*l.XS/2, l.YM
        for fclass in self.Foundation_Classes:
            for i in range(4):
                s.foundations.append(fclass(x, y, self, suit=i))
                x += l.XS

        x, y = l.XM+l.XS+(max_rows-rows)*l.XS/2, l.YM+l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1))
            x += l.XS
        self.setRegion(s.rows, (-999, y-l.CH/2, 999999, h-l.YS-l.CH/2))

        d = (w-reserves*l.XS)/reserves
        x, y = l.XM, h-l.YS
        for i in range(reserves):
            stack = ReserveStack(x, y, self)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 2, 0
            s.reserves.append(stack)
            x += l.XS+d

        s.talon = self.Talon_Class(l.XM, l.YM, self)
        l.createText(s.talon, "s")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.rows, frames=0)
        for i in range(5):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * Algerian Patience
# ************************************************************************

class AlgerianPatience(Carthage):

    Foundation_Classes = (SS_FoundationStack,
                          StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1))
    RowStack_Class = StackWrapper(UD_SS_RowStack, mod=13)

    def _shuffleHook(self, cards):
        # move 4 Kings to top of the Talon
        return self._shuffleHookMoveToTop(cards,
               lambda c: (c.rank == KING and c.deck == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations[4:], frames=0)
        Carthage.startGame(self)


class AlgerianPatience3(Carthage):
    Foundation_Classes = (SS_FoundationStack,
                          SS_FoundationStack,
                          SS_FoundationStack)
    RowStack_Class = StackWrapper(UD_SS_RowStack, mod=13)

    def createGame(self):
        Carthage.createGame(self, rows=8, reserves=8, playcards=20)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
               lambda c: (c.rank == ACE, (c.deck, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        Carthage.startGame(self)



# register the game
registerGame(GameInfo(321, Carthage, "Carthage",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(322, AlgerianPatience, "Algerian Patience",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(457, AlgerianPatience3, "Algerian Patience (3 decks)",
                      GI.GT_3DECK_TYPE | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL))

