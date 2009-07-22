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
from pysollib.hint import KlondikeType_Hint
from pysollib.pysoltk import MfxCanvasText

from spider import Spider_RowStack, Spider_SS_Foundation, Spider_Hint


# ************************************************************************
# * Double Klondike (Klondike with 2 decks and 9 rows)
# ************************************************************************

class DoubleKlondike(Game):
    Layout_Method = Layout.harpLayout
    Foundation_Class = SS_FoundationStack
    RowStack_Class = KingAC_RowStack
    Hint_Class = KlondikeType_Hint

    def createGame(self, max_rounds=-1, num_deal=1, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=9, waste=1, texts=1, playcards=19)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = WasteTalonStack(l.s.talon.x, l.s.talon.y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()
        # extra
        if max_rounds > 1:
            anchor = 'nn'
            if layout.get("texts"):
                anchor = 'nnn'
            l.createRoundText(s.talon, anchor)
        return l

    def startGame(self, flip=0):
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=flip, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Double Klondike by Threes
# ************************************************************************

class DoubleKlondikeByThrees(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, num_deal=3)


# ************************************************************************
# * Gargantua (Double Klondike with one redeal)
# * Pantagruel
# ************************************************************************

class Gargantua(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=2)

class Pantagruel(DoubleKlondike):
    RowStack_Class = AC_RowStack
    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=1)

# ************************************************************************
# * Harp (Double Klondike with 10 non-king rows and no redeal)
# ************************************************************************

class BigHarp(DoubleKlondike):
    RowStack_Class = AC_RowStack

    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=1, rows=10)

    #
    # game overrides
    #

    # no real need to override, but this way the layout
    # looks a little bit different
    def startGame(self):
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Steps (Harp with 7 rows)
# ************************************************************************

class Steps(DoubleKlondike):
    RowStack_Class = AC_RowStack

    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=2, rows=7)


# ************************************************************************
# * Triple Klondike
# * Triple Klondike by Threes
# * Chinese Klondike
# ************************************************************************

class TripleKlondike(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, rows=13)


class TripleKlondikeByThrees(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, rows=13, num_deal=3)


class ChineseKlondike(DoubleKlondike):
    RowStack_Class = StackWrapper(BO_RowStack, base_rank=KING)
    def createGame(self):
        DoubleKlondike.createGame(self, rows=12)


# ************************************************************************
# * Lady Jane
# * Inquisitor
# ************************************************************************

class LadyJane(DoubleKlondike):
    Hint_Class = Spider_Hint
    RowStack_Class = Spider_SS_RowStack

    def createGame(self):
        DoubleKlondike.createGame(self, rows=10, max_rounds=2, num_deal=3)
    def startGame(self):
        DoubleKlondike.startGame(self, flip=1)

    shallHighlightMatch = Game._shallHighlightMatch_RK
    getQuickPlayScore = Game._getSpiderQuickPlayScore


class Inquisitor(DoubleKlondike):
    RowStack_Class = SS_RowStack

    def createGame(self):
        DoubleKlondike.createGame(self, rows=10, max_rounds=3, num_deal=3)
    def startGame(self):
        DoubleKlondike.startGame(self, flip=1)
    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Arabella
# ************************************************************************

class Arabella(DoubleKlondike):
    Hint_Class = Spider_Hint
    RowStack_Class = StackWrapper(Spider_SS_RowStack, base_rank=KING)

    def createGame(self):
        DoubleKlondike.createGame(self, rows=13, max_rounds=1, playcards=24)
    def startGame(self):
        DoubleKlondike.startGame(self, flip=1)

    shallHighlightMatch = Game._shallHighlightMatch_RK
    getQuickPlayScore = Game._getSpiderQuickPlayScore


# ************************************************************************
# * Big Deal
# ************************************************************************

class BigDeal(DoubleKlondike):
    RowStack_Class = KingAC_RowStack

    def createGame(self, rows=12, max_rounds=2, XOFFSET=0):
        l, s = Layout(self), self.s
        self.setSize(l.XM+(rows+2)*l.XS, l.YM+8*l.YS)
        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        for i in range(2):
            y = l.YM
            for j in range(8):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j%4))
                y += l.YS
            x += l.XS
        x, y = l.XM, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, 'n')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        s.waste.CARD_XOFFSET = XOFFSET
        l.createText(s.waste, 'n')
        if max_rounds > 1:
            l.createRoundText(s.talon, 'nnn')
        self.setRegion(s.rows, (-999, -999, l.XM+rows*l.XS-l.CW/2, 999999),
                       priority=1)
        l.defaultStackGroups()


# ************************************************************************
# * Delivery
# ************************************************************************

class Delivery(BigDeal):
    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(SS_RowStack, max_move=1)

    def createGame(self):
        dx = self.app.images.CARDW/10
        BigDeal.createGame(self, rows=12, max_rounds=1, XOFFSET=dx)

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Double Kingsley
# ************************************************************************

class DoubleKingsley(DoubleKlondike):
    Foundation_Class = StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1)
    RowStack_Class = StackWrapper(KingAC_RowStack, base_rank=ACE, dir=1)

    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=1)


# ************************************************************************
# * Thieves of Egypt
# ************************************************************************

class ThievesOfEgypt(DoubleKlondike):
    Layout_Method = Layout.klondikeLayout

    def createGame(self):
        DoubleKlondike.createGame(self, rows=10, max_rounds=2)

    def startGame(self):
        # rows: 1 3 5 7 9 10 8 6 4 2
        row = 0
        for i in (0,2,4,6,8,9,7,5,3,1):
            for j in range(i):
                self.s.talon.dealRow(rows=[self.s.rows[row]], frames=0)
            row += 1
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Brush
# ************************************************************************

class Brush(DoubleKlondike):
    Layout_Method = Layout.klondikeLayout
    Foundation_Class = Spider_SS_Foundation
    RowStack_Class = Spider_RowStack
    Hint_Class = Spider_Hint

    def createGame(self):
        DoubleKlondike.createGame(self, rows=10, max_rounds=1)

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()        # deal first card to WasteStack

    shallHighlightMatch = Game._shallHighlightMatch_RK
    getQuickPlayScore = Game._getSpiderQuickPlayScore



# register the game
registerGame(GameInfo(21, DoubleKlondike, "Double Klondike",
                      GI.GT_KLONDIKE, 2, -1, GI.SL_BALANCED))
registerGame(GameInfo(28, DoubleKlondikeByThrees, "Double Klondike by Threes",
                      GI.GT_KLONDIKE, 2, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(25, Gargantua, "Gargantua",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(15, BigHarp, "Big Harp",
                      GI.GT_KLONDIKE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(51, Steps, "Steps",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(273, TripleKlondike, "Triple Klondike",
                      GI.GT_KLONDIKE, 3, -1, GI.SL_BALANCED))
registerGame(GameInfo(274, TripleKlondikeByThrees, "Triple Klondike by Threes",
                      GI.GT_KLONDIKE, 3, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(495, LadyJane, "Lady Jane",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(496, Inquisitor, "Inquisitor",
                      GI.GT_KLONDIKE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(497, Arabella, "Arabella",
                      GI.GT_KLONDIKE, 3, 0, GI.SL_BALANCED))
registerGame(GameInfo(545, BigDeal, "Big Deal",
                      GI.GT_KLONDIKE | GI.GT_ORIGINAL, 4, 1, GI.SL_BALANCED))
registerGame(GameInfo(562, Delivery, "Delivery",
                      GI.GT_FORTY_THIEVES | GI.GT_ORIGINAL, 4, 0, GI.SL_BALANCED))
registerGame(GameInfo(590, ChineseKlondike, "Chinese Klondike",
                      GI.GT_KLONDIKE, 3, -1, GI.SL_BALANCED,
                      suits=(0, 1, 2) ))
registerGame(GameInfo(591, Pantagruel, "Pantagruel",
                      GI.GT_KLONDIKE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(668, DoubleKingsley, "Double Kingsley",
                      GI.GT_KLONDIKE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(678, ThievesOfEgypt, "Thieves of Egypt",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(689, Brush, "Brush",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))

