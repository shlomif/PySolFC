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

# Imports
import sys, math

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import FreeCellType_Hint
from pysollib.pysoltk import MfxCanvasText

from hanafuda_common import *


# ************************************************************************
#  * Flower Clock
#  ***********************************************************************/

class FlowerClock(AbstractFlowerGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(l.XM + l.XS * 10.5, l.YM + l.YS * 5.5)

        # Create clock
        xoffset = ( 1, 2, 2.5, 2, 1, 0, -1, -2, -2.5, -2, -1, 0 )
        yoffset = ( 0.25, 0.75, 1.9, 3, 3.5, 3.75, 3.5, 3, 1.9, 0.75, 0.25, 0 )
        x = l.XM + l.XS * 7
        y = l.CH / 3
        for i in range(12):
            x0 = x + xoffset[i] * l.XS
            y0 = y + yoffset[i] * l.YS
            s.foundations.append(FlowerClock_Foundation(x0, y0, self, ANY_SUIT, base_rank=3))
            t = MfxCanvasText(self.canvas, x0 + l.CW / 2, y0 + l.YS,
                              anchor="center", font=font,
                              text=self.SUITS[i])

        # Create row stacks
        for j in range(2):
            x, y = l.XM, l.YM + l.YS * j * 2.7
            for i in range(4):
                s.rows.append(FlowerClock_RowStack(x, y, self, yoffset=l.CH/4,
                                                   max_cards=8, max_accept=8))
                x = x + l.XS
        self.setRegion(s.rows, (0, 0, l.XS * 4, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(self.width - l.XS, self.height - l.YS, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        assert len(self.s.talon.cards) == 0

    def isGameWon(self):
        for i in self.s.foundations:
            if len(i.cards) != 4:
                return 0
            if i.cards[0].suit != i.id:
                return 0
        return 1

    def getAutoStacks(self, event=None):
        if event is None:
            return (self.sg.dropstacks, (), self.sg.dropstacks)
        else:
            return (self.sg.dropstacks, self.sg.dropstacks, self.sg.dropstacks)



# ************************************************************************
#  * Gaji
#  ***********************************************************************/

class Gaji(AbstractFlowerGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s

        # Set window size
        self.setSize(l.XM + l.XS * 13, l.YM * 2 + l.YS * 6)

        # Create left foundations
        x = l.XM
        y = l.YM
        s.foundations.append(Gaji_Foundation(x, y, self, -1, base_rank=0))
        x = x + l.XS
        s.foundations.append(Gaji_Foundation(x, y, self, -1, base_rank=1))

        # Create right foundations
        x = self.width - l.XS * 2
        s.foundations.append(Gaji_Foundation(x, y, self, -1, base_rank=2))
        x = x + l.XS
        s.foundations.append(Gaji_Foundation(x, y, self, -1, base_rank=3))

        # Create row stacks
        x = l.XS * 2.5 + l.XM
        for i in range(8):
            s.rows.append(Gaji_RowStack(x, y, self, yoffset=l.CH/2,
                            max_cards=12, max_accept=12))
            x = x + l.XS
        self.setRegion(s.rows, (l.XM + l.XS * 2, -999, l.XM + l.XS * 10, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(self.width - l.XS, self.height - l.YS, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def _shuffleHook(self, cards):
        topcards = [None, None, None, None]
        for c in cards[:]:
            if not topcards[c.rank]:
                if not ((c.suit == 10) and (c.rank == 3)):
                    topcards[c.rank] = c
                    cards.remove(c)
        return topcards + cards

    def startGame(self):
        assert len(self.s.talon.cards) == 48
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        r = self.s.rows
        self.s.talon.dealRow(rows=(r[0], r[1], r[2], r[5], r[6], r[7]))
        self.s.talon.dealRow(rows=(r[0], r[1], r[6], r[7]))
        self.s.talon.dealRow(rows=(r[0], r[7]))
        r = self.s.foundations
        self.s.talon.dealRow(rows=(r[3], r[2], r[1], r[0]))
        assert len(self.s.talon.cards) == 0

    def fillStack(self, stack):
        if stack in self.s.rows:
            if stack.cards and not stack.cards[-1].face_up:
                self.flipMove(stack)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if stack1 in self.s.foundations:
            return (card1.rank == card2.rank
                    and ((((card1.suit + 1) % 12) == card2.suit)
                    or (((card1.suit - 1) % 12) == card2.suit)))
        else:
            return ((card1.suit == card2.suit)
                    and ((card1.rank + 1 == card2.rank)
                    or (card1.rank - 1 == card2.rank)))



# ************************************************************************
#  * Oonsoo
#  ***********************************************************************/

class Oonsoo(AbstractFlowerGame):
    Layout_Method = Layout.oonsooLayout
    Talon_Class = DealRowTalonStack
    RowStack_Class = Oonsoo_SequenceStack
    Rows = 12
    Suit = ANY_SUIT
    BaseRank = 0
    Reserves = 0
    Strictness = 0

    #
    # Game layout
    #

    def createGame(self, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=self.Rows, reserves=self.Reserves,
                  texts=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self, suit=self.Suit,
                                              base_rank=self.BaseRank,
                                              yoffset=l.YOFFSET))
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self))
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * self.gameinfo.decks
        self.startDealSample()
        self.s.talon.dealRow(flip=0)
        self.s.talon.dealCards()

    def isGameWon(self):
        if len(self.s.talon.cards):
            return 0
        for s in self.s.rows:
            if (len(s.cards) != 4 or not cardsFaceUp(s.cards)
                    or not s.isHanafudaSequence(s.cards, self.Strictness)):
                return 0
        return 1



# ************************************************************************
# * Oonsoo Too
# ************************************************************************

class OonsooToo(Oonsoo):
    Reserves = 1



# ************************************************************************
# * Oonsoo Strict
# ************************************************************************

class OonsooStrict(Oonsoo):
    RowStack_Class = Hanafuda_SequenceStack
    Reserves = 2
    Strictness = 1



# ************************************************************************
# * Oonsoo Open
# ************************************************************************

class OonsooOpen(Oonsoo):
    BaseRank = ANY_RANK



# ************************************************************************
# * Oonsoo Times Two
# ************************************************************************

class OonsooTimesTwo(Oonsoo):
    Rows = 24
    Reserves = 1



# ************************************************************************
#  * Pagoda
#  ***********************************************************************/

class Pagoda(AbstractFlowerGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(l.XM + l.XS * 11, l.YS * 6)

        # Create foundations
        self.foundation_texts = []
        id = 0
        for j in range(4):
            x, y = l.XM + l.XS * 8, l.YM * 3 + l.YS * j * 1.5
            for i in range(3):
                s.foundations.append(Pagoda_Foundation(x, y, self, id))
                t = MfxCanvasText(self.canvas, x + l.CW / 2, y - 12,
                                  anchor="center", font=font)
                self.foundation_texts.append(t)
                x = x + l.XS
                id = id + 1

        # Build pagoda
        x, y = l.XM + l.XS, l.YM
        d = ( 0.4, 0.25, 0, 0.25, 0.4 )
        for i in range(5):
            s.reserves.append(ReserveStack(x + l.XS * i, y + l.YS * d[i], self))

        x, y = l.XM + l.XS * 2, y + l.YS * 1.1
        d = ( 0.25, 0, 0.25 )
        for i in range(3):
            s.reserves.append(ReserveStack(x + l.XS * i, y + l.YS * d[i], self))

        x, y = l.XM, y + l.YS * 1.1
        d = ( 0.5, 0.4, 0.25, 0, 0.25, 0.4, 0.5 )
        for i in range(7):
            s.reserves.append(ReserveStack(x + l.XS * i, y + l.YS * d[i], self))

        x, y = l.XM + l.XS, y + l.YS * 1.5
        for i in range(5):
            s.reserves.append(ReserveStack(x + l.XS * i, y, self))

        # Create talon
        x = l.XM + l.XS * 2.5
        y = l.YM + l.YS * 4.9
        s.talon = WasteTalonStack(x, y, self, num_deal=4, max_rounds=1)
        l.createText(s.talon, "sw")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game extras
    #

    def updateText(self):
        if self.preview > 1:
            return
        for i in range(12):
            s = self.s.foundations[i]
            if not len(s.cards) or len(s.cards) == 8:
                text = self.SUITS[i]
            elif len(s.cards) < 5:
                text = _("Rising")
            else:
                text = _("Setting")
            self.foundation_texts[i].config(text=text)

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * 2
        self.updateText()
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves, reverse=1)
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards and stack is self.s.waste:
            if self.canDealCards():
                self.dealCards()



# ************************************************************************
#  * Matsukiri
#  ***********************************************************************/

class MatsuKiri(AbstractFlowerGame):
    Strictness = 0

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s

        # Set window size
        self.setSize(l.XM * 3 + l.XS * 9, l.YM + l.YS * 6)

        # Create row stacks
        x = l.XM
        y = l.YM
        for i in range(8):
            s.rows.append(Matsukiri_RowStack(x, y, self, yoffset=l.CH/2,
                            max_cards=12, max_accept=12))
            x = x + l.XS
        self.setRegion(s.rows, (-999, -999, l.XM + (l.XS * 8) + 10, 999999))

        # Create foundation
        x = x + l.XM * 2
        s.foundations.append(MatsuKiri_Foundation(x, y, self, ANY_SUIT))
        self.setRegion(s.foundations, (l.XM + (l.XS * 8) + 10, -999, 999999, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(self.width - l.XS, self.height - l.YS, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        assert len(self.s.talon.cards) == 0

    def fillStack(self, stack):
        if stack in self.s.rows:
            if len(stack.cards) > 0 and not stack.cards[-1].face_up:
                self.flipMove(stack)


class MatsuKiriStrict(MatsuKiri):
    Strictness = 1


# ************************************************************************
#  * Great Wall
#  ***********************************************************************/

class GreatWall(AbstractFlowerGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        w, h = l.XM + l.XS * 15, l.YM + l.YS * 6.2
        self.setSize(w, h)

        # Create foundations
        self.foundation_texts = []
        x, y = (l.XM, l.XM, w - l.XS, w - l.XS), (l.YM, h / 2, l.YM, h / 2)
        for i in range(4):
            s.foundations.append(GreatWall_FoundationStack(x[i], y[i] + l.YM, self, -1, base_rank=i))
            self.foundation_texts.append(MfxCanvasText(self.canvas,
                                                       x[i] + l.CW / 2, y[i],
                                                       anchor="center", font=font))

        # Create row stacks
        x = l.XM + l.XS * 1.5
        y = l.YM
        for i in range(12):
            s.rows.append(GreatWall_RowStack(x, y, self, yoffset=l.CH/4,
                                                max_cards=26, max_accept=26))
            x = x + l.XS
        self.setRegion(s.rows, (l.XM + l.XS * 1.25, -999, self.width - l.XS * 1.25, 999999))

        # Create talon
        x = self.width / 2 - l.CW / 2
        y = self.height - l.YS * 1.2
        s.talon = InitialDealTalonStack(x, y, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game extras
    #

    def updateText(self):
        if self.preview > 1:
            return
        for i in range(4):
            l = len(self.s.foundations[i].cards) / 12
            if l == 0:
                t = ""
            elif l == 4:
                t = _("Filled")
            else:
                t = str(l) + (_("st"), _("nd"), _("rd"), _("th"))[l - 1] + _(" Deck")
            self.foundation_texts[i].config(text=str(t))

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * 4
        self.updateText()
        for i in range(15):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        assert len(self.s.talon.cards) == 0

    def fillStack(self, stack):
        if stack in self.s.rows:
            if len(stack.cards) > 0 and not stack.cards[-1].face_up:
                self.flipMove(stack)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if stack1 in self.s.foundations:
            return (card1.rank == card2.rank
                    and ((((card1.suit + 1) % 12) == card2.suit)
                    or (((card1.suit - 1) % 12) == card2.suit)))
        else:
            return (card1.rank + 1 == card2.rank
                    or card1.rank - 1 == card2.rank)



# ************************************************************************
# * Four Winds
# ************************************************************************

class FourWinds(AbstractFlowerGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(7 * l.XS, 5 * l.YS + 3 * l.YM)

        # Four winds
        TEXTS = (_("North"), _("East"), _("South"), _("West"),
                 _("NW"), _("NE"), _("SE"), _("SW"))

        # Create foundations
        x = l.XM * 3
        y = l.YM
        xoffset = (2.5, 5, 2.5, 0)
        yoffset = (0, 2, 4, 2)
        for i in range(4):
            x0 = x + (xoffset[i] * l.XS)
            y0 = y + (yoffset[i] * l.YS)
            s.foundations.append(FourWinds_Foundation(x0, y0, self, -1,
                                    max_cards=12, max_accept=1, base_rank=i))
            t = MfxCanvasText(self.canvas, x0 + l.CW / 2, y0 + l.YS + 5,
                              anchor="center", font=font,
                              text=TEXTS[i])

        # Create rows
        xoffset = (1.25, 3.75, 3.75, 1.25)
        yoffset = (0.75, 0.75, 3, 3)
        for i in range(4):
            x0 = x + (xoffset[i] * l.XS)
            y0 = y + (yoffset[i] * l.YS)
            s.rows.append(FourWinds_RowStack(x0, y0, self, yoffset=10,
                                    max_cards=3, max_accept=1, base_rank=ANY_RANK))
            t = MfxCanvasText(self.canvas, x0 + l.CW / 2, y0 + l.YS + 5,
                              anchor="center", font=font,
                              text=TEXTS[i+4])
        self.setRegion(s.rows, (x + l.XS, y + l.YS * 0.65, x + l.XS * 4 + 5, y + l.YS * 3 + 5))

        # Create talon
        x = x + 2 * l.XS
        y = y + 2 * l.YS
        s.talon = WasteTalonStack(x, y, self, num_deal=1, max_rounds=2)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # Define stack-groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48
        self.startDealSample()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards and stack is self.s.waste:
            if self.canDealCards():
                self.dealCards()



# ************************************************************************
# * Sumo
# ************************************************************************

class Sumo(AbstractFlowerGame):
    Layout_Method = Layout.sumoLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = Hanafuda_SS_FoundationStack
    RowStack_Class = Hanafuda_SequenceStack
    Hint_Class = FreeCellType_Hint

    #
    # Game layout
    #

    def createGame(self, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, reserves=2, texts=0, playcards=16)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    suit=r.suit, base_rank=3))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self, yoffset=l.YOFFSET))
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self))
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()



# ************************************************************************
# * Big Sumo
# ************************************************************************

class BigSumo(AbstractFlowerGame):
    Layout_Method = Layout.sumoLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = Hanafuda_SS_FoundationStack
    RowStack_Class = Hanafuda_SequenceStack

    #
    # Game layout
    #

    def createGame(self, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, reserves=4, texts=0, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    suit=r.suit, base_rank=3))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self, yoffset=l.YOFFSET))
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self))
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * 2
        for i in range(9):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[2:8])
        self.s.talon.dealCards()



# ************************************************************************
# * Samuri
# ************************************************************************

class Samuri(AbstractFlowerGame):
    Layout_Method = Layout.samuriLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = Hanafuda_SS_FoundationStack
    RowStack_Class = Hanafuda_SequenceStack
    Rows = 7

    #
    # Game layout
    #

    def createGame(self, max_rounds=1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=self.Rows, waste=1, texts=1, playcards=21)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                            max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    suit=r.suit, base_rank=3))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self, yoffset=l.YOFFSET))

        # Define stack groups
        l.defaultAll()


    #
    # Game over rides
    #

    def startGame(self):
        decks = self.gameinfo.decks
        assert len(self.s.talon.cards) == 48 * decks
        for i in range(1 + (decks > 1)):
            self.s.talon.dealRow(flip=0, frames=0)
        max_row = len(self.s.rows)
        for i in range(max_row):
            self.s.talon.dealRow(rows=self.s.rows[i:max_row-i], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards and stack is self.s.waste:
            if self.canDealCards():
                self.dealCards()



# ************************************************************************
#  * Double Samuri
#  ***********************************************************************/

class DoubleSamuri(Samuri):
    Rows = 11



# ************************************************************************
#  * Super Samuri
#  ***********************************************************************/

class SuperSamuri(DoubleSamuri):
    pass



# ************************************************************************
# * Little Easy
# ************************************************************************

class LittleEasy(AbstractFlowerGame):
    Layout_Method = Layout.easyLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = FourWinds_Foundation
    RowStack_Class = Hanafuda_SequenceStack
    Rows = 7
    PlayCards = 10

    #
    # Game layout
    #

    def createGame(self, max_rounds=-1, num_deal=3, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=self.Rows, waste=1, texts=1, playcards=self.PlayCards)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                            max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self, yoffset=l.YOFFSET))
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * self.gameinfo.decks
        self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards and stack is self.s.waste:
            if self.canDealCards():
                self.dealCards()



# ************************************************************************
# * Easy x One
# ************************************************************************

class EasyX1(LittleEasy):

    def createGame(self, **layout):
        LittleEasy.createGame(self, max_rounds=2, num_deal=1)



# ************************************************************************
# * Relax
# ************************************************************************

class Relax(EasyX1):
    RowStack_Class = Oonsoo_SequenceStack



# ************************************************************************
# * Big Easy
# ************************************************************************

class BigEasy(LittleEasy):
    Rows = 11



# ************************************************************************
# * Easy Supreme
# ************************************************************************

class EasySupreme(LittleEasy):
    Rows = 11
    PlayCards = 14



# ************************************************************************
# * Just For Fun
# ************************************************************************

class JustForFun(AbstractFlowerGame):
    Layout_Method = Layout.funLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = FourWinds_Foundation
    RowStack_Class = Hanafuda_SequenceStack
    Rows = 12
    Reserves = 2
    BaseRank = 0

    #
    # Game layout
    #

    def createGame(self, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=self.Rows, reserves=self.Reserves, texts=0, playcards=22)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                            base_rank=self.BaseRank, yoffset=l.YOFFSET))
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self))
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        decks = self.gameinfo.decks
        assert len(self.s.talon.cards) == 48 * decks
        for i in range((decks * 2) + 1):
            self.s.talon.dealRow(flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:len(self.s.talon.cards)])
        self.s.talon.dealCards()



# ************************************************************************
# * Double Your Fun
# ************************************************************************

class DoubleYourFun(JustForFun):
    Rows = 18
    Reserves = 4



# ************************************************************************
# * Firecracker
# ************************************************************************

class Firecracker(JustForFun):
    RowStack_Class = Oonsoo_SequenceStack
    Reserves = 0
    BaseRank = ANY_RANK



# ************************************************************************
# * Cherry Bomb
# ************************************************************************

class CherryBomb(Firecracker):
    Rows = 18



# ************************************************************************
# * Paulownia
# ************************************************************************

class Paulownia(AbstractFlowerGame):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = Hanafuda_SS_FoundationStack
    RowStack_Class = Hanafuda_SequenceStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=-1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                            max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                        suit=r.suit, base_rank=3))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                            base_rank = 0, yoffset=l.YOFFSET))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.rows[i + 1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()



# ************************************************************************
# *  Register the games
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level):
    game_type = game_type | GI.GT_HANAFUDA
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  suits=range(12), ranks=range(4))
    registerGame(gi)
    return gi

r(12345, Oonsoo, "Oonsoo", GI.GT_HANAFUDA, 1, 0, GI.SL_MOSTLY_SKILL)
r(12346, MatsuKiri, "MatsuKiri", GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12372, MatsuKiriStrict, 'MatsuKiri Strict', GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12347, Gaji, "Gaji", GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12348, FlowerClock, "Flower Clock", GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12349, Pagoda, "Pagoda", GI.GT_HANAFUDA, 2, 0, GI.SL_BALANCED)
r(12350, Samuri, "Samuri", GI.GT_HANAFUDA, 1, 0, GI.SL_BALANCED)
r(12351, GreatWall, "Great Wall", GI.GT_HANAFUDA, 4, 0, GI.SL_MOSTLY_SKILL)
r(12352, FourWinds, "Hanafuda Four Winds", GI.GT_HANAFUDA, 1, 1, GI.SL_MOSTLY_SKILL)
r(12353, Sumo, "Sumo", GI.GT_HANAFUDA, 1, 0, GI.SL_MOSTLY_SKILL)
r(12354, BigSumo, "Big Sumo", GI.GT_HANAFUDA, 2, 0, GI.SL_MOSTLY_SKILL)
r(12355, LittleEasy, "Little Easy", GI.GT_HANAFUDA, 1, -1, GI.SL_BALANCED)
r(12356, BigEasy, "Big Easy", GI.GT_HANAFUDA, 2, -1, GI.SL_BALANCED)
r(12357, EasySupreme, "Easy Supreme", GI.GT_HANAFUDA, 4, -1, GI.SL_BALANCED)
r(12358, JustForFun, "Just For Fun", GI.GT_HANAFUDA, 1, 0, GI.SL_MOSTLY_SKILL)
r(12359, Firecracker, "Firecracker", GI.GT_HANAFUDA, 1, 0, GI.SL_BALANCED)
r(12360, EasyX1, "Easy x One", GI.GT_HANAFUDA, 1, 1, GI.SL_BALANCED)
r(12361, Relax, "Relax", GI.GT_HANAFUDA, 1, 1, GI.SL_BALANCED)
r(12362, DoubleSamuri, "Double Samuri", GI.GT_HANAFUDA, 2, 0, GI.SL_BALANCED)
r(12363, SuperSamuri, "Super Samuri", GI.GT_HANAFUDA, 4, 0, GI.SL_BALANCED)
r(12364, DoubleYourFun, "Double Your Fun", GI.GT_HANAFUDA, 2, 0, GI.SL_MOSTLY_SKILL)
r(12365, CherryBomb, "Cherry Bomb", GI.GT_HANAFUDA, 2, 0, GI.SL_BALANCED)
r(12366, OonsooToo, "Oonsoo Too", GI.GT_HANAFUDA, 1, 0, GI.SL_MOSTLY_SKILL)
r(12367, OonsooStrict, "Oonsoo Strict", GI.GT_HANAFUDA, 1, 0, GI.SL_MOSTLY_SKILL)
r(12368, OonsooOpen, "Oonsoo Open", GI.GT_HANAFUDA, 1, 0, GI.SL_MOSTLY_SKILL)
r(12379, OonsooTimesTwo, "Oonsoo Times Two", GI.GT_HANAFUDA, 2, 0, GI.SL_MOSTLY_SKILL)

del r
