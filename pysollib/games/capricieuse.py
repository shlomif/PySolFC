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

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

from gypsy import DieRussische_Foundation


# ************************************************************************
# * Capricieuse
# ************************************************************************

class Capricieuse(Game):
    Hint_Class = CautiousDefaultHint
    Talon_Class = StackWrapper(RedealTalonStack, max_rounds=3)
    RowStack_Class = UD_SS_RowStack

    #
    # game layout
    #

    def createGame(self, rows=12, round_text=True):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+rows*l.XS, l.YM+2*l.YS+15*l.YOFFSET)

        # create stacks
        x, y, = l.XM+(rows-8)*l.XS/2, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            x += l.XS
        x, y, = l.XM, y + l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1))
            x += l.XS
        s.talon = self.Talon_Class(l.XM, l.YM, self)
        if round_text:
            l.createRoundText(self.s.talon, 'ne')

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(self.s.foundations)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToBottom(cards,
            lambda c: (c.deck == 0 and c.rank in (0, 12), (c.rank, c.suit)), 8)

    def redealCards(self):
        while self.s.talon.cards:
            self.s.talon.dealRowAvail(frames=4)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Nationale
# ************************************************************************

class Nationale(Capricieuse):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = StackWrapper(UD_SS_RowStack, mod=13)

    def createGame(self):
        Capricieuse.createGame(self, round_text=False)

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * Strata
# ************************************************************************

class Strata(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+9*l.XS, l.YM+2*l.YS+12*l.YOFFSET)

        # create stacks
        x, y, = l.XM+l.XS, l.YM
        for i in range(8):
            s.foundations.append(DieRussische_Foundation(x, y, self,
                                 suit=i%4, max_cards=8))
            x += l.XS
        x, y, = l.XM+l.XS, l.YM+l.YS
        for i in range(8):
            s.rows.append(AC_RowStack(x, y, self, max_move=1, max_accept=1))
            x += l.XS
        s.talon = RedealTalonStack(l.XM, l.YM+l.YS/2, self, max_rounds=3)
        l.createRoundText(s.talon, 'nn')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def redealCards(self):
        while self.s.talon.cards:
            self.s.talon.dealRowAvail(frames=4)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Fifteen
# ************************************************************************

class Fifteen(Capricieuse):
    Talon_Class = InitialDealTalonStack

    def createGame(self):
        Capricieuse.createGame(self, rows=15, round_text=False)

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRowAvail()

    def _shuffleHook(self, cards):
        return cards


# ************************************************************************
# * Choice
# ************************************************************************

class Choice_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # check the suit
        num_cards = len(self.cards)
        for f in self.game.s.foundations:
            if len(f.cards) > num_cards:
                suit = f.cards[num_cards].suit
                break
        else:
            return True
        return cards[0].suit == suit


class Choice(Game):

    def createGame(self, rows=8, playcards=16):
        # create layout
        l, s = Layout(self), self.s

        # set window
        decks = self.gameinfo.decks
        max_rows = max(8, rows)
        self.setSize(l.XM + max_rows*l.XS,
                     l.YM + 2*l.YS + (playcards+4*decks)*l.YOFFSET)

        # create stacks
        x, y = l.XM + (max_rows-8)*l.XS/2, l.YM
        for i in range(8):
            stack = Choice_Foundation(x, y, self, base_rank=(i+5), dir=0,
                                      suit=ANY_SUIT, max_cards=(4*decks) )
            stack.CARD_YOFFSET = l.YOFFSET
            s.foundations.append(stack)
            x += l.XS

        x, y = l.XM + (max_rows-rows)*l.XS/2, l.YM + l.YS + (4*decks)*l.YOFFSET
        for i in range(rows):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS

        x, y = self.width - l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        for i in range(11):
            self.s.talon.dealRowAvail(frames=0)
        self.startDealSample()
        self.s.talon.dealRowAvail()

    shallHighlightMatch = Game._shallHighlightMatch_AC



# register the game
registerGame(GameInfo(292, Capricieuse, "Capricieuse",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(293, Nationale, "Nationale",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=('Zigzag Course',) ))
registerGame(GameInfo(606, Strata, "Strata",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 2, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12),
                      altnames=('Persian Patience',) ))
registerGame(GameInfo(673, Fifteen, "Fifteen",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(755, Choice, "Choice",
                      GI.GT_3DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(5, 6, 7, 8, 9, 10, 11, 12) ))

