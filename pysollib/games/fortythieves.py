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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from gypsy import DieRussische_Foundation


# ************************************************************************
# *
# ************************************************************************

class FortyThieves_Hint(CautiousDefaultHint):
    # FIXME: demo is not too clever in this game
    pass


# ************************************************************************
# * Forty Thieves
# *   rows build down by suit
# ************************************************************************

class FortyThieves(Game):
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SS_RowStack
    Hint_Class = FortyThieves_Hint

    FOUNDATION_MAX_MOVE = 1
    ROW_MAX_MOVE = 1
    DEAL = (0, 4)
    FILL_EMPTY_ROWS = 0

    #
    # game layout
    #

    def createGame(self, max_rounds=1, num_deal=1, rows=10, playcards=12, XCARDS=64, XOFFSET=None):
        # create layout
        if XOFFSET is None:
            l, s = Layout(self), self.s
        else:
            l, s = Layout(self, XOFFSET=XOFFSET), self.s

        # set window
        # (compute best XOFFSET - up to 64/72 cards can be in the Waste)
        decks = self.gameinfo.decks
        maxrows = max(rows, 4*decks)
        if maxrows <= 12:
            maxrows += 1
        w1, w2 = maxrows*l.XS+l.XM, 2*l.XS
        if w2 + XCARDS * l.XOFFSET > w1:
            l.XOFFSET = int((w1 - w2) / XCARDS)
        # (piles up to 12 cards are playable without overlap in default window size)
        h = max(2*l.YS, l.YS+(playcards-1)*l.YOFFSET)
        self.setSize(w1, l.YM + l.YS + h + l.YS + l.TEXT_HEIGHT)

        # create stacks
        # foundations
        x = l.XM + (maxrows - 4*decks) * l.XS / 2
        y = l.YM
        for i in range(4*decks):
            s.foundations.append(self.Foundation_Class(x, y, self,
                          suit=i/decks, max_move=self.FOUNDATION_MAX_MOVE))
            x = x + l.XS
        # rows
        x = l.XM + (maxrows - rows) * l.XS / 2
        y = l.YM + l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=self.ROW_MAX_MOVE))
            x = x + l.XS
        # talon, waste
        x = self.width - l.XS
        y = self.height - l.YS
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        l.createText(s.talon, "n")
        if max_rounds > 1:
            l.createRoundText(s.talon, 'nnn')
        x -= l.XS
        s.waste = WasteStack(x, y, self)
        s.waste.CARD_XOFFSET = -l.XOFFSET
        l.createText(s.waste, "n")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(self.DEAL[0]):
            self.s.talon.dealRow(flip=0, frames=0)
        for i in range(self.DEAL[1] - 1):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if self.FILL_EMPTY_ROWS and stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            elif self.s.talon.canDealCards():
                self.s.talon.dealCards()
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Busy Aces
# * Limited
# * Courtyard
# * Waning Moon
# * Lucas
# * Napoleon's Square
# * Carre Napoleon
# * Josephine
# * Marie Rose
# * Big Courtyard
# * San Juan Hill
# * Famous Fifty
# *   rows build down by suit
# ************************************************************************

class BusyAces(FortyThieves):
    DEAL = (0, 1)

    def createGame(self):
        FortyThieves.createGame(self, rows=12)


class Limited(BusyAces):
    DEAL = (0, 3)


class Courtyard(BusyAces):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    FILL_EMPTY_ROWS = 1


class WaningMoon(FortyThieves):
    def createGame(self):
        FortyThieves.createGame(self, rows=13)


class Lucas(WaningMoon):
    ROW_MAX_MOVE = UNLIMITED_MOVES


class NapoleonsSquare(FortyThieves):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    def createGame(self):
        FortyThieves.createGame(self, rows=12)


class CarreNapoleon(FortyThieves):
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=KING)

    def createGame(self):
        FortyThieves.createGame(self, rows=12)

    def _fillOne(self):
        for r in self.s.rows:
            if r.cards:
                c = r.cards[-1]
                for f in self.s.foundations:
                    if f.acceptsCards(r, [c]):
                        self.moveMove(1, r, f, frames=4, shadow=0)
                        return 1
        return 0

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        for i in range(4):
            self.s.talon.dealRow()
            while True:
                if not self._fillOne():
                    break
        self.s.talon.dealCards()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == 0, c.suit))


class Josephine(FortyThieves):
    ROW_MAX_MOVE = UNLIMITED_MOVES


class MarieRose(Josephine):
    DEAL = (0, 5)
    def createGame(self):
        FortyThieves.createGame(self, rows=12, playcards=16, XCARDS=96)


class BigCourtyard(Courtyard):
    def createGame(self):
        FortyThieves.createGame(self, rows=12, playcards=16, XCARDS=96)


class Express(Limited):
    def createGame(self):
        FortyThieves.createGame(self, rows=14, playcards=16, XCARDS=96)


class Carnation(Limited):
    def createGame(self):
        FortyThieves.createGame(self, rows=16, playcards=20, XCARDS=120)


class SanJuanHill(FortyThieves):

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        FortyThieves.startGame(self)


class FamousFifty(FortyThieves):
    DEAL = (0, 5)


# ************************************************************************
# * Deuces
# ************************************************************************

class Deuces(FortyThieves):
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=1)
    RowStack_Class = StackWrapper(SS_RowStack, mod=13)

    DEAL = (0, 1)

    def _shuffleHook(self, cards):
        # move Twos to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 1, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        FortyThieves.startGame(self)

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * Corona
# * Quadrangle
# ************************************************************************

class Corona(FortyThieves):
    FOUNDATION_MAX_MOVE = 0
    DEAL = (0, 3)
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        FortyThieves.createGame(self, rows=12)


class Quadrangle(Corona):
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=NO_RANK)
    RowStack_Class = StackWrapper(SS_RowStack, mod=13)

    def startGame(self):
        FortyThieves.startGame(self)
        self.s.talon.dealSingleBaseCard()

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * Forty and Eight
# ************************************************************************

class FortyAndEight(FortyThieves):
    def createGame(self):
        FortyThieves.createGame(self, max_rounds=2, rows=8, XCARDS=72)


# ************************************************************************
# * Little Forty
# ************************************************************************

class LittleForty(FortyThieves):
    RowStack_Class = Spider_SS_RowStack

    ROW_MAX_MOVE = UNLIMITED_MOVES
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        FortyThieves.createGame(self, max_rounds=4, num_deal=3, XOFFSET=0)

    shallHighlightMatch = Game._shallHighlightMatch_RK
    getQuickPlayScore = Game._getSpiderQuickPlayScore


# ************************************************************************
# * Streets
# * Maria
# * Number Ten
# * Rank and File
# * Emperor
# * Triple Line
# * Big Streets
# * Number Twelve
# * Roosevelt
# *   rows build down by alternate color
# ************************************************************************

class Streets(FortyThieves):
    RowStack_Class = AC_RowStack

    shallHighlightMatch = Game._shallHighlightMatch_AC


class Maria(Streets):
    def createGame(self):
        Streets.createGame(self, rows=9)


class NumberTen(Streets):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (2, 2)


class RankAndFile(Streets):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (3, 1)


class Emperor(Streets):
    DEAL = (3, 1)


class TripleLine(Streets):
    GAME_VERSION = 2

    FOUNDATION_MAX_MOVE = 0
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (0, 3)
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        Streets.createGame(self, max_rounds=2, rows=12)


class BigStreets(Streets):
    def createGame(self):
        FortyThieves.createGame(self, rows=12, XCARDS=96)


class NumberTwelve(NumberTen):
    def createGame(self):
        FortyThieves.createGame(self, rows=12, XCARDS=96)


class Roosevelt(Streets):
    DEAL = (0, 4)
    def createGame(self):
        Streets.createGame(self, rows=7)


# ************************************************************************
# * Red and Black
# * Zebra
# *   rows build down by alternate color, foundations up by alternate color
# ************************************************************************

class RedAndBlack(Streets):
    Foundation_Class = AC_FoundationStack

    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (0, 1)

    def createGame(self):
        FortyThieves.createGame(self, rows=8)

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        Streets.startGame(self)


class Zebra(RedAndBlack):
    FOUNDATION_MAX_MOVE = 0
    ROW_MAX_MOVE = 1
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        FortyThieves.createGame(self, max_rounds=2, rows=8, XOFFSET=0)


# ************************************************************************
# * Indian
# * Midshipman
# * Mumbai
# *   rows build down by any suit but own
# ************************************************************************

class Indian(FortyThieves):
    RowStack_Class = BO_RowStack
    DEAL = (1, 2)

    def createGame(self):
        FortyThieves.createGame(self, XCARDS=74)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit != card2.suit
                and (card1.rank + 1 == card2.rank
                     or card2.rank + 1 == card1.rank))


class Midshipman(Indian):
    DEAL = (2, 2)

    def createGame(self):
        FortyThieves.createGame(self, rows=9)


class Mumbai(Indian):
    def createGame(self):
        FortyThieves.createGame(self, XCARDS=84, rows=13)


# ************************************************************************
# * Napoleon's Exile
# * Double Rail
# * Single Rail (1 deck)
# * Final Battle
# *   rows build down by rank
# ************************************************************************

class NapoleonsExile(FortyThieves):
    RowStack_Class = RK_RowStack

    DEAL = (0, 4)

    shallHighlightMatch = Game._shallHighlightMatch_RK


class DoubleRail(NapoleonsExile):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (0, 1)

    def createGame(self):
        FortyThieves.createGame(self, rows=5)


class SingleRail(DoubleRail):
    def createGame(self):
        FortyThieves.createGame(self, rows=4, XCARDS=48)


class FinalBattle(DoubleRail):
    def createGame(self):
        FortyThieves.createGame(self, rows=6)



# ************************************************************************
# * Octave
# ************************************************************************

class Octave_Talon(WasteTalonStack):

    def dealCards(self, sound=False):
        if self.round == self.max_rounds:
            return 0
        if self.cards:
            return WasteTalonStack.dealCards(self, sound)
        # last round
        num_cards = WasteTalonStack.dealCards(self, sound)
        wastes = [self.waste]+list(self.game.s.reserves)
        old_state = self.game.enterState(self.game.S_DEAL)
        if self.cards:
            if sound and not self.game.demo:
                self.game.startDealSample()
            num_cards = min(len(self.cards), 8)
            for i in range(num_cards):
                if not self.cards[-1].face_up:
                    self.game.flipMove(self)
                self.game.moveMove(1, self, wastes[i], frames=4, shadow=0)
            if sound and not self.game.demo:
                self.game.stopSamples()
        self.game.leaveState(old_state)
        return num_cards


class Octave_Waste(WasteStack):
    def updateText(self):
        if self.game.preview > 1 or self.texts.ncards is None:
            return
        if self.game.s.talon.round == self.game.s.talon.max_rounds:
            t = ''
        else:
            t = str(len(self.cards))
        self.texts.ncards.config(text=t)


class Octave(Game):
    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+9*l.XS, l.YM+3*l.YS+12*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM+l.XS/2, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=int(i/2), max_cards=10))
            x += l.XS

        x, y = l.XM+l.XS/2, l.YM+l.YS
        for i in range(8):
            s.rows.append(AC_RowStack(x, y, self,
                                      base_rank=ANY_RANK, max_move=1))
            x += l.XS

        x, y = l.XM, h-l.YS
        s.talon = Octave_Talon(x, y, self, max_rounds=2)
        l.createText(s.talon, "n")
        x += l.XS
        s.waste = Octave_Waste(x, y, self)
        l.createText(s.waste, 'n')
        x += l.XS
        for i in range(7):
            stack = WasteStack(x, y, self, max_accept=0)
            s.reserves.append(stack)
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        for s in self.s.foundations:
            if len(s.cards) != 10:
                return False
        for s in self.s.reserves:
            if s.cards:
                return False
        return not self.s.waste.cards

    shallHighlightMatch = Game._shallHighlightMatch_AC

    def _autoDeal(self, sound=True):
        ncards = len(self.s.waste.cards) + sum([len(i.cards) for i in self.s.reserves])
        if ncards == 0:
            return self.dealCards(sound=sound)
        return 0

    def fillStack(self, stack):
        if self.s.talon.round == self.s.talon.max_rounds:
            # last round
            if not stack.cards and self.s.talon.cards:
                if stack is self.s.waste or stack in self.s.reserves:
                    old_state = self.enterState(self.S_FILL)
                    self.flipMove(self.s.talon)
                    self.moveMove(1, self.s.talon, stack, frames=4, shadow=0)
                    self.leaveState(old_state)


# ************************************************************************
# * Fortune's Favor
# ************************************************************************

class FortunesFavor(Game):

    def createGame(self):

        l, s = Layout(self), self.s

        w, h = l.XM+8*l.XS, 2*l.YM+3*l.YS
        self.setSize(w, h)

        x, y = l.XM+3*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'se')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')
        y = 2*l.YM+l.YS
        for i in range(2):
            x = l.XM+2*l.XS
            for j in range(6):
                stack = SS_RowStack(x, y, self, max_move=1)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


    def fillStack(self, stack):
        if len(stack.cards) == 0:
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)


    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Octagon
# ************************************************************************

class Octagon(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s

        w1 = l.XS+12*l.XOFFSET
        w, h = l.XM+2*l.XS+2*w1, l.YM+4*l.YS
        self.setSize(w, h)

        for x, y in ((l.XM,                l.YM),
                     (l.XM+w1+2*l.XS+l.XM, l.YM),
                     (l.XM,                l.YM+3*l.YS),
                     (l.XM+w1+2*l.XS+l.XM, l.YM+3*l.YS),):
            stack = SS_RowStack(x, y, self, max_move=1)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.rows.append(stack)
        i = 0
        for x, y in ((l.XM+w1,                    l.YM),
                     (l.XM+w1+l.XS,               l.YM),
                     (l.XM+w1-2*l.XS-l.XS/2-l.XM, l.YM+1.5*l.YS),
                     (l.XM+w1-l.XS-l.XS/2-l.XM,   l.YM+1.5*l.YS),
                     (l.XM+w1+2*l.XS+l.XS/2+l.XM, l.YM+1.5*l.YS),
                     (l.XM+w1+3*l.XS+l.XS/2+l.XM, l.YM+1.5*l.YS),
                     (l.XM+w1,                    l.YM+3*l.YS),
                     (l.XM+w1+l.XS,               l.YM+3*l.YS),):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i%4))
            i += 1
        x, y = l.XM+w1, l.YM+1.5*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=4)
        l.createText(s.talon, 's')
        l.createRoundText(s.talon, 'nn')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        for i in range(5):
            self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Squadron
# ************************************************************************

class Squadron(FortyThieves):

    def createGame(self):
        l, s = Layout(self), self.s

        self.setSize(l.XM+12*l.XS, l.YM+max(4.5*l.YS, 2*l.YS+12*l.YOFFSET))

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')
        x += 2*l.XS
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS
        x, y = l.XM, l.YM+l.YS*3/2
        for i in range(3):
            s.reserves.append(ReserveStack(x, y, self))
            y += l.YS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(10):
            s.rows.append(SS_RowStack(x, y, self, max_move=1))
            x += l.XS

        l.defaultStackGroups()


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Waterloo
# ************************************************************************

class Waterloo(FortyThieves):

    RowStack_Class = Spider_SS_RowStack

    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (0, 1)

    def createGame(self):
        FortyThieves.createGame(self, rows=6)

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    getQuickPlayScore = Game._getSpiderQuickPlayScore
    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Junction
# * Crossroads
# ************************************************************************

class Junction(Game):
    Foundation_Class = StackWrapper(DieRussische_Foundation, max_cards=8)

    def createGame(self, rows=7):
        
        l, s = Layout(self), self.s

        self.setSize(l.XM+10*l.XS, l.YM+3*l.YS+12*l.YOFFSET)

        y = l.YM
        for i in range(2):
            x = l.XM+2*l.XS
            for j in range(8):
                s.foundations.append(self.Foundation_Class(x, y, self,
                                                           suit=j%4))
                x += l.XS
            y += l.YS

        x, y = l.XM+(10-rows)*l.XS/2, l.YM+2*l.YS
        for i in range(rows):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    shallHighlightMatch = Game._shallHighlightMatch_AC


class Crossroads(Junction):
    Foundation_Class = StackWrapper(SS_FoundationStack, max_cards=13)

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


# ************************************************************************
# * The Spark
# ************************************************************************

class TheSpark_Talon(TalonStack):

    def canDealCards(self):
        return len(self.cards) > 0

    def dealCards(self, sound=False):
        old_state = self.game.enterState(self.game.S_DEAL)
        num_cards = 0
        if self.cards:
            if sound and not self.game.demo:
                self.game.playSample("dealwaste")
            for i in range(self.num_deal):
                for r in self.game.s.reserves:
                    if not self.cards:
                        break
                    self.game.flipMove(self)
                    self.game.moveMove(1, self, r, frames=4, shadow=0)
                    num_cards += 1
        self.game.leaveState(old_state)
        return num_cards


class TheSpark(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s

        w, h = l.XM+8*l.XS, l.YM+4*l.YS
        self.setSize(w, h)

        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=i/2, base_rank=KING, mod=13))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        s.talon = TheSpark_Talon(x, y, self, max_rounds=1, num_deal=3)
        l.createText(s.talon, 'se')
        y += l.YS
        for i in (0,1):
            stack = WasteStack(x, y, self)
            s.reserves.append(stack)
            l.createText(stack, 'se')
            y += l.YS
        y = l.YM+l.YS*3/2
        for i in range(2):
            x = l.XM+2*l.XS
            for j in range(6):
                stack = SS_RowStack(x, y, self, max_move=1)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == KING, c.suit))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Double Gold Mine
# ************************************************************************

class DoubleGoldMine_RowStack(AC_RowStack):
    getBottomImage = Stack._getReserveBottomImage

class DoubleGoldMine(Streets):

    RowStack_Class = DoubleGoldMine_RowStack

    ROW_MAX_MOVE = UNLIMITED_MOVES

    def createGame(self):
        Streets.createGame(self, rows=9, num_deal=3)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()


# ************************************************************************
# * Interchange
# * Unlimited
# * Breakwater
# * Forty Nine
# * Alternation
# * Triple Interchange
# ************************************************************************

class Interchange(FortyThieves):

    RowStack_Class = StackWrapper(SS_RowStack, base_rank=KING)

    ROW_MAX_MOVE = UNLIMITED_MOVES

    def createGame(self):
        FortyThieves.createGame(self, rows=7)

    def startGame(self):
        for i in (0,1,2):
            self.s.talon.dealRow(frames=0)
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


class Unlimited(Interchange):
    def createGame(self):
        FortyThieves.createGame(self, rows=7, XOFFSET=0,
                                max_rounds=UNLIMITED_REDEALS)


class Breakwater(Interchange):
    RowStack_Class = RK_RowStack
    shallHighlightMatch = Game._shallHighlightMatch_RK


class FortyNine_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards:
            return len(cards) == 1
        return True


class FortyNine(Interchange):
    RowStack_Class = FortyNine_RowStack

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_AC


class Alternation(Interchange):
    RowStack_Class = AC_RowStack
    shallHighlightMatch = Game._shallHighlightMatch_AC


class TripleInterchange(Interchange):
    RowStack_Class = SS_RowStack

    def createGame(self):
        FortyThieves.createGame(self, rows=9, XOFFSET=0,
                                max_rounds=UNLIMITED_REDEALS)

    def startGame(self):
        for i in (0,1,2,3):
            self.s.talon.dealRow(frames=0)
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


# ************************************************************************
# * Indian Patience
# ************************************************************************

class IndianPatience_RowStack(BO_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BO_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.game.s.talon.cards:
            return True
        if self.cards:
            if from_stack in self.game.s.rows and len(from_stack.cards) == 1:
                return False
            return len(self.cards) != 1
        return True

class IndianPatience(Indian):
    RowStack_Class = IndianPatience_RowStack

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if self.s.talon.cards:
                if len(self.s.talon.cards) == 1:
                    self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
            if self.s.talon.cards:
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
            if self.s.talon.cards:
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
            self.leaveState(old_state)


# ************************************************************************
# * Floradora
# ************************************************************************

class Floradora(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s

        self.setSize(l.XM+10*l.XS, l.YM+2*l.YS+12*l.YOFFSET+l.TEXT_HEIGHT)

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')
        x += l.XS
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i%4,
                                                    max_cards=12))
            x += l.XS
        x, y = l.XM, l.YM+l.YS+l.TEXT_HEIGHT
        s.foundations.append(RK_FoundationStack(x, y, self, suit=ANY_SUIT,
                             base_rank=KING, dir=0, max_cards=8))
        x += 3*l.XS
        for i in range(6):
            s.rows.append(RK_RowStack(x, y, self, max_move=1))
            x += l.XS

        l.defaultStackGroups()

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Blind Patience
# ************************************************************************

class BlindPatience_Hint(DefaultHint):
    SCORE_FLIP = 80000

    def shallMovePile(self, from_stack, to_stack, pile, rpile):
        if from_stack is to_stack or not to_stack.acceptsCards(from_stack, pile):
            return False
        #
        if len(rpile) == 0:
            return True
        # now check for loops
        rr = self.ClonedStack(from_stack, stackcards=rpile)
        if self.level < 2:
            # hint
            if to_stack.cards and not to_stack.cards[-1].face_up:
                if rr.cards and not rr.cards[-1].face_up:
                    return True
            if rr.cards and not rr.cards[-1].face_up:
                return True
            if not to_stack.cards:
                return True
        else:
            # demo mode
            if rr.cards and not rr.cards[-1].face_up:
                if len(rr.cards) < len(to_stack.cards):
                    return True
        if rr.acceptsCards(to_stack, pile):
            # the pile we are going to move could be moved back -
            # this is dangerous as we can create endless loops...
            return False
        return True


class BlindPatience_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if self.cards and not self.cards[-1].face_up:
            return True
        return AC_RowStack.acceptsCards(self, from_stack, cards)


class BlindPatience(FortyThieves):
    Hint_Class = BlindPatience_Hint
    RowStack_Class = BlindPatience_RowStack

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(flip=0)
        self.s.talon.dealCards()        # deal first card to WasteStack

    def getAutoStacks(self, event=None):
        if event is None:
            # do not auto flip
            return ([], self.sg.dropstacks, self.sg.dropstacks)
        return (self.sg.dropstacks, self.sg.dropstacks, self.sg.dropstacks)

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack in self.s.rows:
            if to_stack.cards:
                if to_stack.cards[-1].face_up:
                    # top card is face up
                    return 1001
                else:
                    return 1000
            else:
                return 999
        # prefer non-empty piles in to_stack
        return 1001 + int(len(to_stack.cards) != 0)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Foothold
# ************************************************************************

class Foothold(FortyThieves):
    RowStack_Class = UD_AC_RowStack
    DEAL = (0, 5)
    def createGame(self):
        FortyThieves.createGame(self, rows=8, playcards=16)
    shallHighlightMatch = Game._shallHighlightMatch_AC



# register the game
registerGame(GameInfo(13, FortyThieves, "Forty Thieves",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Napoleon at St.Helena",
                                "Le Cadran")))
registerGame(GameInfo(80, BusyAces, "Busy Aces",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(228, Limited, "Limited",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(79, WaningMoon, "Waning Moon",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(125, Lucas, "Lucas",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(109, Deuces, "Deuces",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(196, Corona, "Corona",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(195, Quadrangle, "Quadrangle",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(110, Courtyard, "Courtyard",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(23, FortyAndEight, "Forty and Eight",
                      GI.GT_FORTY_THIEVES, 2, 1, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(115, LittleForty, "Little Forty",         # was: 72
                      GI.GT_FORTY_THIEVES, 2, 3, GI.SL_BALANCED))
registerGame(GameInfo(76, Streets, "Streets",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(73, Maria, "Maria",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED,
                      altnames=("Maria Luisa",) ))
registerGame(GameInfo(70, NumberTen, "Number Ten",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(71, RankAndFile, "Rank and File",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED,
                      altnames=("Dress Parade") ))
registerGame(GameInfo(197, TripleLine, "Triple Line",
                      GI.GT_FORTY_THIEVES | GI.GT_XORIGINAL, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(126, RedAndBlack, "Red and Black",        # was: 75
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(113, Zebra, "Zebra",
                      GI.GT_FORTY_THIEVES, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(69, Indian, "Indian",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(74, Midshipman, "Midshipman",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(198, NapoleonsExile, "Napoleon's Exile",
                      GI.GT_FORTY_THIEVES | GI.GT_XORIGINAL, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(131, DoubleRail, "Double Rail",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(199, SingleRail, "Single Rail",
                      GI.GT_FORTY_THIEVES, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(295, NapoleonsSquare, "Napoleon's Square",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(310, Emperor, "Emperor",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(323, Octave, "Octave",
                      GI.GT_FORTY_THIEVES, 2, 1, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(332, Mumbai, "Mumbai",
                      GI.GT_FORTY_THIEVES, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(411, CarreNapoleon, "Carre Napoleon",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(416, FortunesFavor, "Fortune's Favor",
                      GI.GT_FORTY_THIEVES, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(426, Octagon, "Octagon",
                      GI.GT_FORTY_THIEVES, 2, 3, GI.SL_BALANCED))
registerGame(GameInfo(440, Squadron, "Squadron",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(462, Josephine, "Josephine",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(493, MarieRose, "Marie Rose",
                      GI.GT_FORTY_THIEVES, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(503, BigStreets, "Big Streets",
                      GI.GT_FORTY_THIEVES | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(504, NumberTwelve, "Number Twelve",
                      GI.GT_FORTY_THIEVES | GI.GT_ORIGINAL, 3, 0, GI.SL_BALANCED))
registerGame(GameInfo(505, BigCourtyard, "Big Courtyard",
                      GI.GT_FORTY_THIEVES | GI.GT_ORIGINAL, 3, 0, GI.SL_BALANCED))
registerGame(GameInfo(506, Express, "Express",
                      GI.GT_FORTY_THIEVES | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(514, Carnation, "Carnation",
                      GI.GT_FORTY_THIEVES | GI.GT_ORIGINAL, 4, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(528, FinalBattle, "Final Battle",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(529, SanJuanHill, "San Juan Hill",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(540, Waterloo, "Waterloo",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(556, Junction, "Junction",
                      GI.GT_FORTY_THIEVES, 4, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12) ))
registerGame(GameInfo(564, TheSpark, "The Spark",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(573, DoubleGoldMine, "Double Gold Mine",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(574, Interchange, "Interchange",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(575, Unlimited, "Unlimited",
                      GI.GT_FORTY_THIEVES, 2, -1, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(576, Breakwater, "Breakwater",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(577, FortyNine, "Forty Nine",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(578, IndianPatience, "Indian Patience",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(588, Roosevelt, "Roosevelt",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(628, Crossroads, "Crossroads",
                      GI.GT_FORTY_THIEVES, 4, 0, GI.SL_BALANCED))
registerGame(GameInfo(631, Alternation, "Alternation",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(632, Floradora, "Floradora",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(679, TripleInterchange, "Triple Interchange",
                      GI.GT_FORTY_THIEVES, 3, -1, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(683, FamousFifty, "Famous Fifty",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(751, BlindPatience, "Blind Patience",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(765, Foothold, "Foothold",
                      GI.GT_FORTY_THIEVES | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))

