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
# * Sultan
# ************************************************************************

class Sultan(Game):

    #
    # game layout
    #

    def createGame(self, reserves=6):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 3*l.XM+5*l.XS, l.YM+4*l.YS+l.TEXT_HEIGHT+l.TEXT_MARGIN
        self.setSize(w, h)

        # create stacks
        lay = ((0,0,0,1,13),
               (2,0,0,1,13),
               (0,1,1,1,13),
               (2,1,1,1,13),
               (1,1,2,0,1),
               (1,2,2,1,13),
               (0,2,3,1,13),
               (2,2,3,1,13),
               (1,0,2,1,12),
               )
        for i, j, suit, max_accept, max_cards in lay:
            x, y = 2*l.XM+l.XS+i*l.XS, l.YM+j*l.YS
            stack = SS_FoundationStack(x, y, self, suit=suit,
                    max_move=0, max_accept=max_accept, max_cards=max_cards, mod=13)
            s.foundations.append(stack)

        x, y = l.XM, l.YM
        for i in range(reserves/2):
            s.rows.append(ReserveStack(x, y, self))
            y += l.YS

        x, y = 3*l.XM+4*l.XS, l.YM
        for i in range(reserves/2):
            s.rows.append(ReserveStack(x, y, self))
            y += l.YS

        x, y = 2*l.XM+1.5*l.XS, l.YM+3*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "s")
        l.createRoundText(self.s.talon, 'sss')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        cards = self._shuffleHookMoveToTop(cards,
                    lambda c: (c.rank == ACE and c.suit == 2 and c.deck == 0, c.suit))
        cards = self._shuffleHookMoveToTop(cards,
                    lambda c: (c.rank == KING, c.suit))
        return cards

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getAutoStacks(self, event=None):
        return (self.sg.dropstacks, (), self.sg.dropstacks)


class SultanPlus(Sultan):
    def createGame(self):
        Sultan.createGame(self, reserves=8)
 

# ************************************************************************
# * Boudoir
# ************************************************************************

class Boudoir(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+5.5*l.XS, l.YM+4*l.YS)

        x, y = l.XM, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 'ne')
        l.createRoundText(s.talon, 'nn')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        x, y = l.XM+1.5*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    max_cards=13))
            x += l.XS

        x = l.XM+1.5*l.XS
        y += l.YS
        for i in range(4):
            s.rows.append(AbstractFoundationStack(x, y, self, suit=i,
                          max_cards=1, max_move=0, base_rank=QUEEN))
            x += l.XS

        x = l.XM+1.5*l.XS
        y += l.YS
        for i in range(4):
            s.rows.append(AbstractFoundationStack(x, y, self, suit=i,
                          max_cards=1, max_move=0, base_rank=JACK))
            x += l.XS

        x = l.XM+1.5*l.XS
        y += l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 mod=13, max_cards=11, base_rank=9, dir=-1))
            x += l.XS

        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        # move 4 Queens to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == QUEEN and c.deck == 0, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:4])
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        return (len(self.s.talon.cards) + len(self.s.waste.cards)) == 0


# ************************************************************************
# * Captive Queens
# ************************************************************************

class CaptiveQueens(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+5.5*l.XS, l.YM+3*l.YS)

        x, y = l.XM, l.YM+l.YS/2
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "se")
        l.createRoundText(s.talon, 'nn')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")

        x, y = l.XM+1.5*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 mod=13, max_cards=6, base_rank=4, dir=-1))
            x += l.XS

        x, y = l.XM+1.5*l.XS, l.YM+l.YS
        for i in range(4):
            s.foundations.append(AbstractFoundationStack(x, y, self, suit=i,
                                 max_cards=1, max_move=0, base_rank=QUEEN))
            x += l.XS

        x, y = l.XM+1.5*l.XS, l.YM+2*l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 mod=13, max_cards=6, base_rank=5))
            x += l.XS

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()

    def isGameWon(self):
        return (len(self.s.talon.cards) + len(self.s.waste.cards)) == 0


# ************************************************************************
# * Contradance
# ************************************************************************

class Contradance(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+4*l.YS)

        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2,
                                 base_rank=4, dir=-1, mod=13, max_cards=6))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2,
                                 base_rank=5, max_cards=7))
            x += l.XS

        x, y = l.XM+3*l.XS, l.YM+3*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, 'n')
        l.createRoundText(self.s.talon, 'nnn')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        # move 5's and 6's to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (4, 5), (c.rank, c.suit)))


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Idle Aces
# ************************************************************************

class IdleAces_AceFoundation(AbstractFoundationStack):

    def getBottomImage(self):
        return self.game.app.images.getLetter(ACE)


class IdleAces(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+7*l.XS, l.YM+4*l.YS)

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 's')
        l.createRoundText(s.talon, 'ne', dx=l.XS)
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')
        x0, y0 = l.XM+2*l.XS, l.YM
        k = 0
        for i, j in((2, 0), (0, 1.5), (4, 1.5), (2, 3)):
            x, y = x0+i*l.XS, y0+j*l.YS
            s.foundations.append(RK_FoundationStack(x, y, self,
                                 ##suit=ANY_SUIT,
                                 base_rank=KING, dir=-1, max_move=0))
            k += 1
        k = 0
        for i, j in((2, 1), (1, 1.5), (3, 1.5), (2, 2)):
            x, y = x0+i*l.XS, y0+j*l.YS
            s.foundations.append(RK_FoundationStack(x, y, self,
                                 ##suit=ANY_SUIT,
                                 base_rank=1, max_move=0, max_cards=12))
            k += 1
        k = 0
        for i, j in((1, 0.2), (3, 0.2), (1, 2.8), (3, 2.8)):
            x, y = x0+i*l.XS, y0+j*l.YS
            s.foundations.append(IdleAces_AceFoundation(x, y, self,
                                 suit=k, max_cards=1, max_move=0))
            k += 1

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (1, KING) and c.deck == 0, (-c.rank, c.suit)))


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations[:8])
        self.s.talon.dealCards()


# ************************************************************************
# * Lady of the Manor
# * Archway
# ************************************************************************

class LadyOfTheManor_RowStack(BasicRowStack):
    clickHandler = BasicRowStack.doubleclickHandler


class LadyOfTheManor_Reserve(OpenStack):
    clickHandler = OpenStack.doubleclickHandler


class LadyOfTheManor(Game):
    Foundation_Class_1 = RK_FoundationStack
    Foundation_Class_2 = RK_FoundationStack

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+max(4*l.YS, 3*l.YS+14*l.YOFFSET))

        x, y = l.XM, self.height-l.YS
        for i in range(4):
            suit = i
            if self.Foundation_Class_1 is RK_FoundationStack: suit = ANY_SUIT
            s.foundations.append(self.Foundation_Class_1(x, y, self, suit=suit))
            x += l.XS
        for i in range(4):
            suit = i
            if self.Foundation_Class_1 is RK_FoundationStack: suit = ANY_SUIT
            s.foundations.append(self.Foundation_Class_2(x, y, self, suit=suit))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            s.rows.append(LadyOfTheManor_RowStack(x, y, self, max_accept=0))
            x += l.XS
        for i, j in ((0,2), (0,1), (0,0),
                     (1,0), (2,0), (3,0), (4,0), (5,0), (6,0),
                     (7,0), (7,1), (7,2),):
            x, y = l.XM+i*l.XS, l.YM+j*l.YS
            s.reserves.append(LadyOfTheManor_Reserve(x, y, self, max_accept=0))

        s.talon = InitialDealTalonStack(self.width-l.XS, self.height-2*l.YS, self)

        l.defaultAll()


    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, c.suit))


    def startGame(self, flip=False):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(11):
            self.s.talon.dealRow(frames=0, flip=flip)
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        while self.s.talon.cards:
            self.flipMove(self.s.talon)
            c = self.s.talon.cards[-1]
            r = self.s.reserves[c.rank-1]
            self.moveMove(1, self.s.talon, r, frames=4)


# ************************************************************************
# * Matrimony
# ************************************************************************

class Matrimony_Talon(DealRowTalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds and not self.cards:
            return False
        return not self.game.isGameWon()

    def _redeal(self):
        lr = len(self.game.s.rows)
        num_cards = 0
        assert len(self.cards) == 0
        rows = self.game.s.rows
        r = self.game.s.rows[-self.round]
        for i in range(len(r.cards)):
            num_cards += 1
            self.game.moveMove(1, r, self, frames=4)
            self.game.flipMove(self)
        assert len(self.cards) == num_cards
        self.game.nextRoundMove(self)
        return num_cards

    def dealCards(self, sound=False):
        if sound:
            self.game.startDealSample()
        num_cards = 0
        if len(self.cards) == 0:
            num_cards += self._redeal()
        if self.round == 1:
            num_cards += self.dealRowAvail(sound=False)
        else:
            rows = self.game.s.rows[-self.round+1:]
            num_cards += self.dealRowAvail(rows=rows, sound=False)
            while self.cards:
                num_cards += self.dealRowAvail(rows=self.game.s.rows, sound=False)
        if sound:
            self.game.stopSamples()
        return num_cards


class Matrimony(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+4*l.YS)

        s.talon = Matrimony_Talon(l.XM, l.YM, self, max_rounds=17)
        l.createText(s.talon, 'se')
        l.createRoundText(s.talon, 'ne')

        x, y = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 base_rank=JACK, dir=-1, mod=13))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 base_rank=QUEEN, dir=1, mod=13))
            x += l.XS
        y = l.YM+2*l.YS
        for i in range(2):
            x = l.XM
            for j in range(8):
                stack = LadyOfTheManor_RowStack(x, y, self, max_accept=0)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
            lambda c: (c.rank in (JACK, QUEEN) and c.deck == 0 and c.suit == 3,
                       (c.rank, c.suit)))


    def startGame(self):
        self.s.talon.dealRow(rows=[self.s.foundations[3],
                                   self.s.foundations[7]], frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Picture Patience
# * Patriarchs
# ************************************************************************

class PicturePatience(Game):

    def createGame(self, max_rounds=1):

        l, s = Layout(self), self.s
        w, h = 3*l.XM+5*l.XS, l.YM+4*l.YS
        if max_rounds > 1:
            h += l.TEXT_HEIGHT+l.TEXT_MARGIN
        self.setSize(w, h)

        x, y = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            y += l.YS
        x, y = 3*l.XM+4*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            y += l.YS
        y = l.YM
        for i in range(3):
            x = 2*l.XM+l.XS
            for j in range(3):
                s.rows.append(BasicRowStack(x, y, self,
                                            max_cards=1, max_accept=1))
                x += l.XS
            y += l.YS
        x, y = 2*l.XM+l.XS+l.XS/2, l.YM+3*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        x += l.XS
        s.waste = WasteStack(x, y, self)
        if max_rounds > 1:
            l.createText(s.talon, 's')
            l.createRoundText(s.talon, 'sss')
            l.createText(s.waste, 's')
        else:
            l.createText(s.talon, 'sw')
            l.createText(s.waste, 'se')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)


class Patriarchs(PicturePatience):
    def createGame(self):
        PicturePatience.createGame(self, max_rounds=2)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (ACE, KING) and c.deck == 0,
                              (c.rank, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


# ************************************************************************
# * Sixes and Sevens
# * Two Rings
# ************************************************************************

class SixesAndSevens(Game):

    def createGame(self, max_rounds=2):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+4*l.YS)

        y = l.YM
        for i in range(2):
            x = l.XM
            for j in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self,
                                     suit=j, base_rank=6, max_cards=7))
                x += l.XS
            y += l.YS
        for i in range(2):
            x = l.XM
            for j in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j,
                                     base_rank=5, dir=-1, max_cards=6))
                x += l.XS
            y += l.YS
        y = l.YM
        for i in range(3):
            x = l.XM+5*l.XS
            for j in range(3):
                s.rows.append(ReserveStack(x, y, self))
                x += l.XS
            y += l.YS
        x, y = l.XM+5*l.XS, l.YM+3*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'sw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
            lambda c: (c.rank in (5, 6), (-c.rank, c.deck, c.suit)))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


class TwoRings(Game):

    def createGame(self, max_rounds=2):

        l, s = Layout(self), self.s
        self.setSize(l.XM+10*l.XS, l.YM+5*l.YS)

        lay = (
            (1.5, 0  ),
            (2.5, 0.3),
            (3,   1.3),
            (2.5, 2.3),
            (1.5, 2.6),
            (0.5, 2.3),
            (0,   1.3),
            (0.5, 0.3),
            )

        suit = 0
        x0, y0 = l.XM+l.XS, l.YM
        for xx, yy in lay:
            x, y = x0+xx*l.XS, y0+yy*l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit/2,
                                 base_rank=6, max_cards=7))
            suit += 1
        suit = 0
        x0, y0 = l.XM+5*l.XS, l.YM
        for xx, yy in lay:
            x, y = x0+xx*l.XS, y0+yy*l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit/2,
                                 base_rank=5, dir=-1, max_cards=6))
            suit += 1

        x, y = l.XM, l.YM+4*l.YS
        for i in range(8):
            stack = BasicRowStack(x, y, self)
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)
            x += l.XS

        x += l.XS
        s.talon = DealRowRedealTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, 'nw')
        l.createRoundText(s.talon, 'sw')

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
            lambda c: (c.rank in (5, 6), (-c.rank, c.suit)))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Corner Suite
# ************************************************************************

class CornerSuite_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return from_stack is self.game.s.waste
        return True
    getBottomImage = Stack._getReserveBottomImage


class CornerSuite(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+5*l.XS, l.YM+5*l.YS)

        suit = 0
        for x, y in ((0,0), (4,0), (0,4), (4,4)):
            x, y = l.XM+x*l.XS, l.YM+y*l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit))
            suit += 1

        x, y = l.XM+3*l.XS/2, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'nw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        y = l.YM+l.YS
        for i in range(3):
            x = l.XM+l.XS
            for j in range(3):
                stack = CornerSuite_RowStack(x, y, self, max_move=1)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                x += l.XS
            y += l.YS

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Marshal
# ************************************************************************

class Marshal_Hint(CautiousDefaultHint):
    def _getDropCardScore(self, score, color, r, t, ncards):
        return 93000, color


class Marshal(Game):

    Hint_Class = Marshal_Hint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+5*l.YS)

        x, y = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            y += l.YS
        x, y = self.width-l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=i, base_rank=KING, dir=-1))
            y += l.YS
        x, y = (self.width-l.XS)/2, self.height-l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 'se')
        y = l.YM
        for i in range(4):
            x = l.XM+l.XS*3/2
            for j in range(6):
                stack = UD_SS_RowStack(x, y, self, base_rank=NO_RANK)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                x += l.XS
            y += l.YS

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.flipMove(self.s.talon)
                self.moveMove(1, self.s.talon, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Royal Aids
# ************************************************************************

class RoyalAids(Game):

    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+4*l.YS+l.TEXT_HEIGHT)

        x0 = l.XM+1.5*l.XS
        for k in (0,1):
            suit = 0
            for i, j in ((1,0), (0,0.5), (2,0.5), (1,1)):
                x, y = x0+i*l.XS, l.YM+j*l.YS
                s.foundations.append(AC_FoundationStack(x, y, self, suit=suit))
                suit += 1
            x0 += 3.5*l.XS

        x, y = l.XM, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=UNLIMITED_REDEALS)
        l.createText(s.talon, 'se')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        x, y = l.XM+3.75*l.XS, l.YM+2*l.YS
        for i in (0,1):
            stack = KingAC_RowStack(x, y, self, max_move=1)
            stack.getBottomImage = stack._getReserveBottomImage
            s.rows.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            x += l.XS
        x, y = l.XM+2.75*l.XS, l.YM+3*l.YS
        for i in range(4):
            stack = BasicRowStack(x, y, self)
            s.reserves.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            l.createText(stack, 's')
            x += l.XS

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()


    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Circle Eight
# ************************************************************************

class CircleEight(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+5*l.XS, l.YM+4*l.YS)

        for i, j in ((1,0),
                     (2,0),
                     (3,0),
                     (4,1.5),
                     (3,3),
                     (2,3),
                     (1,3),
                     (0,1.5),
                     ):
            x, y = l.XM+i*l.XS, l.YM+j*l.YS
            stack = RK_RowStack(x, y, self, dir=1, mod=13, max_move=0)
            s.rows.append(stack)
            stack.CARD_YOFFSET = 0

        x, y = l.XM+1.5*l.XS, l.YM+1.5*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, 'nw')
        l.createRoundText(self.s.talon, 'nn')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def isGameWon(self):
        return len(self.s.talon.cards) == 0 and len(self.s.waste.cards) == 0

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * Adela
# ************************************************************************

class Adela_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        index = list(self.game.s.foundations).index(self)
        index = index%8
        return len(self.game.s.foundations[index].cards) > 0


class Adela(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+9.5*l.XS, l.YM+4*l.YS)

        x, y = l.XM+l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i%4,
                                 base_rank=JACK, dir=-1, max_cards=11))
            x += l.XS
        x, y = l.XM+l.XS, l.YM+l.YS
        for i in range(8):
            s.foundations.append(Adela_Foundation(x, y, self, suit=i%4,
                                 base_rank=QUEEN, max_cards=1))
            x += l.XS
        x, y = l.XM+l.XS, l.YM+2*l.YS
        for i in range(8):
            s.foundations.append(Adela_Foundation(x, y, self, suit=i%4,
                                 base_rank=KING, max_cards=1))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 'n')
        x, y = l.XM+l.XS/2, l.YM+3*l.YS
        for i in range(9):
            stack = SS_RowStack(x, y, self, max_move=1, dir=1)
            s.rows.append(stack)
            stack.CARD_YOFFSET = 0
            x += l.XS
            
        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.flipMove(self.s.talon)
                self.moveMove(1, self.s.talon, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Toni
# ************************************************************************

class Toni(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8.5*l.XS, l.YM+4*l.YS)

        y = l.YM
        suit = 0
        for i in (0,1,3,4):
            x = l.XM+(2+i)*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit))
            suit += 1

        x, y = l.XM+4*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            y += l.YS

        for i, j in ((0,0),(1,0),(2,0),(5,0),(6,0),(7,0),
                     (0,1),(1,1),(2,1),(5,1),(6,1),(7,1),
                     ):
            x, y = l.XM+(0.5+i)*l.XS, l.YM+(1.5+j)*l.YS
            stack = BasicRowStack(x, y, self, max_accept=0)
            s.rows.append(stack)
            stack.CARD_YOFFSET = 0

        x, y = l.XM, l.YM
        s.talon = DealRowRedealTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 'se')
        l.createRoundText(s.talon, 'ne')

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
           lambda c: (c.rank in (ACE, KING) and c.deck == 0, (c.rank, c.suit)))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Khedive
# ************************************************************************

class Khedive(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+10*l.XS, l.YM+5*l.YS)

        x, y = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            s.foundations.append(SS_FoundationStack(x+6*l.XS, y, self, suit=i))
            x += l.XS

        x, y = l.XM+4*l.XS, l.YM
        r = range(11)
        for i in range(5,0,-1):
            for j in r[i:-i]:
                x, y = l.XM+(j-0.5)*l.XS, l.YM+(5-i)*l.YS
                s.rows.append(BasicRowStack(x, y, self, max_accept=0))


        x, y = l.XM, l.YM+1.5*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)


# ************************************************************************
# * Phalanx
# ************************************************************************

class Phalanx(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+5*l.YS)

        y = l.YM
        for i in range(5):
            x = l.XM+(8-i)*l.XS/2
            for j in range(i+1):
                s.rows.append(ReserveStack(x, y, self))
                x += l.XS
            y += l.YS

        suit = 0
        for xx, yy in ((1.5, 1.5),
                       (1,   2.5),
                       (6.5, 1.5),
                       (7,   2.5)):
            x, y = l.XM+xx*l.XS, l.YM+yy*l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, suit))
            suit += 1

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()



# ************************************************************************
# * Grandee
# * Turncoats
# * Voracious
# ************************************************************************

class Grandee(Game):
    Hint_Class = CautiousDefaultHint
    Talon_Class = DealRowTalonStack
    RowStack_Class = SS_RowStack

    def createGame(self, waste=False, rows=14):

        # create layout
        l, s = Layout(self), self.s

        # set window
        decks = self.gameinfo.decks
        w = max(decks*4, rows/2)
        self.setSize(l.XM+w*l.XS, l.YM+5*l.YS)

        # create stacks
        x, y = l.XM + (w-decks*4)*l.XS/2, l.YM
        for i in range(4):
            for j in range(decks):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
                x += l.XS

        y = l.YM+1.5*l.YS
        for i in range(2):
            x = l.XM + (w-rows/2)*l.XS/2
            for j in range(rows/2):
                stack = self.RowStack_Class(x, y, self, max_move=1)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        x, y = self.width-l.XS, self.height-l.YS
        s.talon = self.Talon_Class(x, y, self)
        if waste:
            l.createText(s.talon, 'n')
            x -= l.XS
            s.waste = WasteStack(x, y, self)
            l.createText(s.waste, 'n')
        else:
            l.createText(s.talon, 'sw')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_SS


class Turncoats(Grandee):
    Talon_Class = TalonStack
    RowStack_Class = StackWrapper(UD_AC_RowStack, base_rank=NO_RANK)

    def createGame(self):
        Grandee.createGame(self, rows=12)

    def fillStack(self, stack):
        if not stack.cards:
            if stack in self.s.rows and self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_AC


class Voracious(Grandee):
    Talon_Class = StackWrapper(WasteTalonStack, max_rounds=1)
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=NO_RANK)

    def createGame(self):
        Grandee.createGame(self, waste=True, rows=12)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards:
            if stack in self.s.rows:
                old_state = self.enterState(self.S_FILL)
                if not self.s.waste.cards:
                    self.s.talon.dealCards()
                if self.s.waste.cards:
                    self.s.waste.moveMove(1, stack)
                self.leaveState(old_state)


# ************************************************************************
# * Desert Island
# ************************************************************************

class DesertIsland(Game):

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+8*l.XS, l.YM+5*l.YS)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                                    suit=i/2, max_cards=10))
            x += l.XS

        y = l.YM+l.YS
        for i in range(3):
            x = l.XM
            for j in range(8):
                ##stack = SS_RowStack(x, y, self, max_move=1)
                stack = ReserveStack(x, y, self)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        x, y = self.width-l.XS, self.height-l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 'sw')

        # define stack-groups
        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        for s in self.s.foundations:
            if len(s.cards) != 10:
                return False
        return True


# ************************************************************************
# * Catherine the Great
# ************************************************************************

class CatherineTheGreat(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self, reserves=6):

        l, s = Layout(self), self.s
        w, h = 3*l.XM+5*l.XS, l.YM+5*l.YS
        self.setSize(w, h)

        lay = ((0,2,0,QUEEN,-1),
               (0,1,0,QUEEN,-1),
               (0,0,1,QUEEN,-1),
               (2,0,1,QUEEN,-1),
               (1,0,2,QUEEN,-1),
               (2,1,3,QUEEN,-1),
               (2,2,3,QUEEN,-1),
               (1,1,2,KING,1),
               )
        for xx, yy, suit, base_rank, dir in lay:
            x, y = 2*l.XM+l.XS+xx*l.XS, l.YM+yy*l.YS
            stack = SS_FoundationStack(x, y, self, suit=suit,
                                       max_move=0, base_rank=base_rank,
                                       dir=dir, mod=13)
            s.foundations.append(stack)

        for x, y in ((l.XM,          l.YM),
                     (3*l.XM+4*l.XS, l.YM)):
            for i in range(5):
                stack = RK_RowStack(x, y, self, dir=1,
                                    base_rank=NO_RANK,
                                    max_move=1, mod=13)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
                y += l.YS

        x, y = 2*l.XM+1.5*l.XS, l.YM+4*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'n')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        def select_func(card):
            if card.rank == KING and card.suit == 2 and card.deck == 0:
                return (True, 999)
            if card.rank == QUEEN:
                if card.suit == 2 and card.deck == 0:
                    return (False, 0)
                return (True, card.suit)
            return (False, 0)
        cards = self._shuffleHookMoveToTop(cards, select_func)
        return cards

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()        # deal first card to WasteStack

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_RKW



# register the game
registerGame(GameInfo(330, Sultan, "Sultan",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK,
                      altnames=("Sultan of Turkey",) ))
registerGame(GameInfo(331, SultanPlus, "Sultan +",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(354, Boudoir, "Boudoir",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(410, CaptiveQueens, "Captive Queens",
                      GI.GT_1DECK_TYPE, 1, 2, GI.SL_MOSTLY_LUCK,
                      altnames=("Quadrille",) ))
registerGame(GameInfo(418, Contradance, "Contradance",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_LUCK,
                      altnames=("Cotillion",) ))
registerGame(GameInfo(419, IdleAces, "Idle Aces",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(423, LadyOfTheManor, "Lady of the Manor",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK,
                      altnames=("Vassal", "La Chatelaine") ))
registerGame(GameInfo(424, Matrimony, "Matrimony",
                      GI.GT_2DECK_TYPE, 2, 16, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(429, Patriarchs, "Patriarchs",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(438, SixesAndSevens, "Sixes and Sevens",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(477, CornerSuite, "Corner Suite",
                      GI.GT_2DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(559, Marshal, "Marshal",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(565, RoyalAids, "Royal Aids",
                      GI.GT_2DECK_TYPE, 2, UNLIMITED_REDEALS, GI.SL_BALANCED))
registerGame(GameInfo(598, PicturePatience, "Picture Patience",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK,
                      rules_filename="patriarchs.html"))
registerGame(GameInfo(635, CircleEight, "Circle Eight",
                      GI.GT_1DECK_TYPE, 1, 1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(646, Adela, "Adela",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(660, Toni, "Toni",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(691, Khedive, "Khedive",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(729, TwoRings, "Two Rings",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(730, Phalanx, "Phalanx",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(742, Grandee, "Grandee",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(743, Turncoats, "Turncoats",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(744, Voracious, "Voracious",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(745, DesertIsland, "Desert Island",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(761, CatherineTheGreat, "Catherine the Great",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
