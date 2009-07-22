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
import sys, time

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.mfxutil import kwdefault


# ************************************************************************
# *
# ************************************************************************

class Numerica_Hint(DefaultHint):
    # FIXME: demo is clueless

    #def _getDropCardScore(self, score, color, r, t, ncards):
        #FIXME: implement this method

    def _getMoveWasteScore(self, score, color, r, t, pile, rpile):
        assert r in (self.game.s.waste, self.game.s.talon) and len(pile) == 1
        score = self._computeScore(r, t)
        return score, color

    def _computeScore(self, r, t):
        score = 30000
        if len(t.cards) == 0:
            score = score - (KING - r.cards[0].rank) * 1000
        elif t.cards[-1].rank < r.cards[0].rank:
            # FIXME: add intelligence here
            score = 10000 + t.cards[-1].rank - len(t.cards)
        elif t.cards[-1].rank == r.cards[0].rank:
            score = 20000
        else:
            score = score - (t.cards[-1].rank - r.cards[0].rank) * 1000
        return score


# ************************************************************************
# *
# ************************************************************************

class Numerica_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts any one card from the Waste pile
        return from_stack is self.game.s.waste and len(cards) == 1

    getBottomImage = Stack._getReserveBottomImage

    def getHelp(self):
        ##return _('Tableau. Accepts any one card from the Waste.')
        return _('Tableau. Build regardless of rank and suit.')


# ************************************************************************
# * Numerica
# ************************************************************************

class Numerica(Game):
    Hint_Class = Numerica_Hint
    Foundation_Class = StackWrapper(RK_FoundationStack, suit=ANY_SUIT)
    RowStack_Class = StackWrapper(Numerica_RowStack, max_accept=1)

    #
    # game layout
    #

    def createGame(self, rows=4, reserve=False, max_rounds=1, waste_max_cards=1):
        # create layout
        l, s = Layout(self), self.s
        decks = self.gameinfo.decks
        foundations = 4*decks

        # set window
        # (piles up to 20 cards are playable in default window size)
        h = max(2*l.YS, 20*l.YOFFSET)
        max_rows = max(rows, foundations)
        self.setSize(l.XM+(1.5+max_rows)*l.XS+l.XM, l.YM + l.YS + h)

        # create stacks
        x0 = l.XM + l.XS * 3 / 2
        if decks == 1:
            x = x0 + (rows-4)*l.XS/2
        else:
            x = x0
        y = l.YM
        for i in range(foundations):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
            x = x + l.XS
        x, y = x0, l.YM + l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        self.setRegion(s.rows, (x0-l.XS/2, y-l.CH/2, 999999, 999999))
        x, y = l.XM, l.YM+l.YS+l.YS/2*int(reserve)
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        if reserve or waste_max_cards > 1:
            l.createText(s.talon, 'ne')
        else:
            l.createText(s.talon, 'n')
        y = y + l.YS
        s.waste = WasteStack(x, y, self, max_cards=waste_max_cards)
        if waste_max_cards > 1:
            l.createText(s.waste, 'ne')
        if reserve:
            s.reserves.append(self.ReserveStack_Class(l.XM, l.YM, self))

        # define stack-groups
        l.defaultStackGroups()

        return l


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()          # deal first card to WasteStack

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def getHighlightPilesStacks(self):
        return ()


class Numerica2Decks(Numerica):
    def createGame(self):
        Numerica.createGame(self, rows=6)


# ************************************************************************
# * Lady Betty
# * Last Chance
# ************************************************************************

class LadyBetty(Numerica):
    Foundation_Class = SS_FoundationStack
    def createGame(self):
        Numerica.createGame(self, rows=6)


class LastChance_RowStack(Numerica_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        return from_stack is self.game.s.waste and len(cards) == 1


class LastChance_Reserve(OpenStack):
    def canFlipCard(self):
        return (len(self.game.s.talon.cards) == 0 and
                len(self.game.s.waste.cards) == 0 and
                self.cards and not self.cards[0].face_up)


class LastChance(LadyBetty):
    RowStack_Class = StackWrapper(LastChance_RowStack, max_accept=1)
    ReserveStack_Class = LastChance_Reserve

    def createGame(self):
        Numerica.createGame(self, rows=7, reserve=True)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves, flip=False)
        self.s.talon.dealCards()


# ************************************************************************
# * Puss in the Corner
# ************************************************************************

class PussInTheCorner_Talon(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler

    def canDealCards(self):
        if self.round != self.max_rounds:
            return True
        return False

    def clickHandler(self, event):
        if self.cards:
            return OpenStack.clickHandler(self, event)
        else:
            return TalonStack.clickHandler(self, event)

    def dealCards(self, sound=False):
        ncards = 0
        old_state = self.game.enterState(self.game.S_DEAL)
        if not self.cards and self.round != self.max_rounds:
            self.game.nextRoundMove(self)
            self.game.startDealSample()
            for r in self.game.s.rows:
                while r.cards:
                    self.game.moveMove(1, r, self, frames=4)
                    self.game.flipMove(self)
                    ncards += 1
            self.fillStack()
            self.game.stopSamples()
        self.game.leaveState(old_state)
        return ncards


class PussInTheCorner_Foundation(SS_FoundationStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, base_suit=ANY_SUIT)
        SS_FoundationStack.__init__(self, x, y, game, ANY_SUIT, **cap)
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards:
            # check the color
            if cards[0].color != self.cards[-1].color:
                return False
        return True
    def getHelp(self):
        return _('Foundation. Build up by color.')


class PussInTheCorner_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts any one card from the Talon
        return from_stack is self.game.s.talon and len(cards) == 1

    getBottomImage = Stack._getReserveBottomImage

    def getHelp(self):
        ##return _('Tableau. Accepts any one card from the Waste.')
        return _('Tableau. Build regardless of rank and suit.')


class PussInTheCorner(Numerica):

    def createGame(self, rows=4):
        l, s = Layout(self), self.s
        self.setSize(l.XM+5*l.XS, l.YM+4*l.YS)
        for x, y in ((l.XM,        l.YM       ),
                     (l.XM+4*l.XS, l.YM       ),
                     (l.XM,        l.YM+3*l.YS),
                     (l.XM+4*l.XS, l.YM+3*l.YS),
                     ):
            stack = PussInTheCorner_RowStack(x, y, self,
                                             max_accept=1, max_move=1)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            s.rows.append(stack)
        for x, y in ((l.XM+1.5*l.XS, l.YM+  l.YS),
                     (l.XM+1.5*l.XS, l.YM+2*l.YS),
                     (l.XM+2.5*l.XS, l.YM+  l.YS),
                     (l.XM+2.5*l.XS, l.YM+2*l.YS),
                     ):
            s.foundations.append(PussInTheCorner_Foundation(x, y, self,
                                                            max_move=0))
        x, y = l.XM + 2*l.XS, l.YM
        s.waste = s.talon = PussInTheCorner_Talon(x, y, self, max_rounds=2)
        l.createText(s.talon, 'se')
        l.createRoundText(self.s.talon, 'ne')

        # define stack-groups
        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                    lambda c: (c.rank == ACE, c.suit))


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.fillStack()


    def _autoDeal(self, sound=True):
        return 0


# ************************************************************************
# * Frog
# * Fly
# * Fanny
# ************************************************************************

class Frog(Game):

    Hint_Class = Numerica_Hint
    ##Foundation_Class = SS_FoundationStack
    Foundation_Class = RK_FoundationStack

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS, l.YM + 2*l.YS+16*l.YOFFSET)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(8):
            if self.Foundation_Class is RK_FoundationStack:
                suit = ANY_SUIT
            else:
                suit = int(i/2)
            s.foundations.append(self.Foundation_Class(x, y, self,
                                 suit=suit, max_move=0))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        stack = OpenStack(x, y, self, max_accept=0)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
        s.reserves.append(stack)
        x += l.XS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x += l.XS
        s.waste = WasteStack(x, y, self, max_cards=1)
        x += l.XS
        for i in range(5):
            stack = Numerica_RowStack(x, y, self, max_accept=UNLIMITED_ACCEPTS)
            #stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.rows.append(stack)
            x = x + l.XS

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        n = 0
        f = 0
        while True:
            c = self.s.talon.cards[-1]
            if c.rank == ACE:
                r = self.s.foundations[f]
                f += 1
                ##r = self.s.foundations[c.suit*2]
            else:
                r = self.s.reserves[0]
                n += 1
            self.s.talon.dealRow(rows=[r])
            if n == 13:
                break
        self.s.talon.dealCards()


class Fly(Frog):

    Foundation_Class = RK_FoundationStack

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                    lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        for i in range(13):
            self.s.talon.dealRow(self.s.reserves)
        self.s.talon.dealCards()


class Fanny(Frog):

    Foundation_Class = RK_FoundationStack

    def startGame(self):
        self.startDealSample()
        for i in range(11):
            self.s.talon.dealRow(self.s.reserves, flip=0)
        self.s.talon.dealRow(self.s.reserves)
        self.s.talon.dealCards()


# ************************************************************************
# * Gnat
# ************************************************************************

class Gnat(Game):

    Hint_Class = Numerica_Hint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS, l.YM + 2*l.YS+16*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x += l.XS
        s.waste = WasteStack(x, y, self, max_cards=1)
        x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS

        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            s.rows.append(Numerica_RowStack(x, y, self, max_accept=UNLIMITED_ACCEPTS))
            x += l.XS
        x = l.XM+6*l.XS
        for i in range(2):
            y = l.YM + l.YS/2
            for j in range(3):
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
                y += l.YS
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                    lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()


# ************************************************************************
# * Gloaming
# * Chamberlain
# ************************************************************************

class Gloaming_Hint(Numerica_Hint):
    def computeHints(self):
        self.step010(self.game.s.rows, self.game.s.rows)
        self.step060(self.game.sg.reservestacks, self.game.s.rows)

    # try if we should move a card from a ReserveStack to a RowStack
    def step060(self, reservestacks, rows):
        for r in reservestacks:
            if not r.cards:
                continue
            for t in rows:
                if t.cards:
                    score = self._computeScore(r, t)
                    self.addHint(score, 1, r, t)
                else:
                    self.addHint(90000+r.cards[-1].rank, 1, r, t)


class Gloaming_RowStack(Numerica_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts any one card from reserves
        return from_stack in self.game.s.reserves


class Gloaming(Game):

    Hint_Class = Gloaming_Hint
    Foundation_Class = SS_FoundationStack

    def createGame(self, reserves=3, rows=5):
        # create layout
        l, s = Layout(self), self.s

        # set window
        n = 52/reserves+1
        w, h = l.XM + (reserves+rows+1)*l.XS, l.YM + 2*l.YS+n*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM+(reserves+rows+1-4)*l.XS/2, l.YM
        for i in range(4):
            if self.Foundation_Class is RK_FoundationStack:
                suit = ANY_SUIT
            else:
                suit = i
            s.foundations.append(self.Foundation_Class(x, y, self,
                                 suit=suit, max_move=0))
            x += l.XS

        x, y = l.XM, l.YM+l.YS
        for i in range(reserves):
            stack = OpenStack(x, y, self, max_accept=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.reserves.append(stack)
            x += l.XS

        x += l.XS
        for i in range(rows):
            s.rows.append(Gloaming_RowStack(x, y, self, max_accept=UNLIMITED_ACCEPTS))
            x += l.XS

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()


    def startGame(self):
        n = 52/len(self.s.reserves)+1
        for i in range(n-3):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRowAvail(rows=self.s.reserves)


class Chamberlain(Gloaming):
    Foundation_Class = RK_FoundationStack
    def createGame(self, reserves=3, rows=5):
        Gloaming.createGame(self, reserves=4, rows=3)


# ************************************************************************
# * Toad
# ************************************************************************


class Toad_TalonStack(DealRowTalonStack):
    def canDealCards(self):
        if not DealRowTalonStack.canDealCards(self):
            return False
        for r in self.game.s.reserves:
            if r.cards:
                return False
        return True
    def dealCards(self, sound=False):
        self.dealRow(rows=self.game.s.reserves, sound=sound)


class Toad(Game):
    Hint_Class = Gloaming_Hint

    def createGame(self, reserves=3, rows=5):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+11*l.XS, l.YM+6*l.YS
        self.setSize(w, h)

        # create stacks
        x, y = w-l.XS, h-l.YS
        s.talon = Toad_TalonStack(x, y, self)
        l.createText(s.talon, "n")
        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS
        x, y = l.XM+3*l.XS/2, l.YM+l.YS
        for i in range(5):
            s.rows.append(Gloaming_RowStack(x, y, self, max_accept=UNLIMITED_ACCEPTS))
            x += l.XS
        y = l.YM+l.YS/2
        for i in (3, 3, 3, 3, 1):
            x = l.XM+8*l.XS
            for j in range(i):
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
                x += l.XS
            y += l.YS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)


# ************************************************************************
# * Shifting
# ************************************************************************

class Shifting_Hint(Numerica_Hint):
    shallMovePile = DefaultHint._cautiousShallMovePile


class Shifting_RowStack(Numerica_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack is self.game.s.waste:
            return True
        if not self.cards:
            return cards[0].rank == KING
        if (from_stack in self.game.s.rows and
            self.cards[-1].rank-cards[0].rank == 1):
            return True
        return False


class Shifting(Numerica):
    Hint_Class = Shifting_Hint
    RowStack_Class = StackWrapper(Shifting_RowStack, max_accept=1)


# ************************************************************************
# * Strategerie
# ************************************************************************

class Strategerie_Talon(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler


class Strategerie_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack is self.game.s.talon or from_stack in self.game.s.reserves:
            return True
        return False

    getBottomImage = Stack._getReserveBottomImage

    def getHelp(self):
        return _('Tableau. Build regardless of rank and suit.')


class Strategerie_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack is self.game.s.talon:
            return True
        return False


class Strategerie(Game):
    Hint_Class = Numerica_Hint

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        l.freeCellLayout(rows=4, reserves=4, texts=1)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = Strategerie_Talon(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(RK_FoundationStack(r.x, r.y, self))
        for r in l.s.rows:
            s.rows.append(Strategerie_RowStack(r.x, r.y, self,
                                               max_accept=UNLIMITED_ACCEPTS))
        for r in l.s.reserves:
            s.reserves.append(Strategerie_ReserveStack(r.x, r.y, self))
        # default
        l.defaultAll()
        self.sg.dropstacks.append(s.talon)

    def startGame(self):
        self.startDealSample()
        self.s.talon.fillStack()


# ************************************************************************
# * Assembly
# * Anno Domini
# ************************************************************************

class Assembly_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return from_stack is self.game.s.waste
        return True


class Assembly(Numerica):
    Hint_Class = CautiousDefaultHint

    Foundation_Class = StackWrapper(RK_FoundationStack, suit=ANY_SUIT)
    RowStack_Class = StackWrapper(Assembly_RowStack, max_move=1)

    def createGame(self):
        Numerica.createGame(self, waste_max_cards=UNLIMITED_CARDS)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_RK


class AnnoDomini_Hint(DefaultHint):
    def step030(self, foundations, rows, dropstacks):
        pass


class AnnoDomini(Numerica):
    Hint_Class = AnnoDomini_Hint

    Foundation_Class = StackWrapper(SS_FoundationStack, suit=ANY_SUIT, mod=13)
    RowStack_Class = StackWrapper(AC_RowStack, mod=13)

    def createGame(self):
        l = Numerica.createGame(self, max_rounds=3, waste_max_cards=UNLIMITED_CARDS)
        year = str(time.localtime()[0])
        i = 0
        for s in self.s.foundations:
            # setup base_rank & base_suit
            s.cap.suit = i
            s.cap.base_suit = i
            d = int(year[i])
            if d == 0:
                d = JACK
            s.cap.base_rank = d
            i += 1
        l.createRoundText(self.s.talon, 'nn')

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_ACW


# ************************************************************************
# * Circle Nine
# * Measure
# * Double Measure
# ************************************************************************

class CircleNine_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack is self.game.s.talon

    def getHelp(self):
        return _('Tableau. Build regardless of rank and suit.')


class CircleNine(Game):
    Hint_Class = Numerica_Hint

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+7*l.XS, l.YM+3*l.YS)

        for i, j in ((1,0),
                     (2,0),
                     (3,0),
                     (4,0),
                     (5,1),
                     (3.5,2),
                     (2.5,2),
                     (1.5,2),
                     (0,1),
                     ):
            x, y = l.XM+(1+i)*l.XS, l.YM+j*l.YS
            stack = CircleNine_RowStack(x, y, self, max_accept=1,
                                        max_move=1, base_rank=NO_RANK)
            s.rows.append(stack)
            stack.CARD_YOFFSET = 0

        x, y = l.XM+3.5*l.XS, l.YM+l.YS
        stack = RK_FoundationStack(x, y, self, suit=ANY_SUIT, max_cards=52,
                                   max_move=0, mod=13, base_rank=ANY_RANK)
        s.foundations.append(stack)
        l.createText(stack, 'ne')
        x, y = l.XM, l.YM
        s.talon = Strategerie_Talon(x, y, self)
        l.createText(s.talon, 'ne')

        l.defaultStackGroups()
        self.sg.dropstacks.append(s.talon)


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow()
        self.s.talon.fillStack()


    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)


class Measure(CircleNine):

    Foundation_Class = StackWrapper(RK_FoundationStack, max_cards=52)

    def createGame(self, rows=8):
        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM+2*l.YS+10*l.YOFFSET)

        x, y = l.XM, l.YM
        s.talon = Strategerie_Talon(x, y, self)
        l.createText(s.talon, 'ne')
        x = self.width-l.XS
        stack = self.Foundation_Class(x, y, self, suit=ANY_SUIT, max_cards=52,
                                      max_move=0, mod=13, base_rank=ANY_RANK)
        s.foundations.append(stack)
        l.createText(stack, 'nw')

        x, y = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(CircleNine_RowStack(x, y, self, max_accept=1,
                          max_move=1, base_rank=NO_RANK))
            x += l.XS

        l.defaultStackGroups()
        self.sg.dropstacks.append(s.talon)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.fillStack()


class DoubleMeasure(Measure):
    Foundation_Class = StackWrapper(RK_FoundationStack, max_cards=104)

    def createGame(self, rows=8):
        Measure.createGame(self, rows=10)


# ************************************************************************
# * Amphibian
# ************************************************************************

class Amphibian(Game):
    Hint_Class = Gloaming_Hint

    def createGame(self, rows=5, reserves=4, playcards=15):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8 * l.XS, l.YM + 3*l.YS + playcards*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            for j in range(2):
                s.foundations.append(RK_FoundationStack(x, y, self,
                                                        suit=ANY_SUIT))
                x += l.XS
        x, y = l.XM+(8-rows)*l.XS/2, l.YM + l.YS
        for i in range(rows):
            s.rows.append(Gloaming_RowStack(x, y, self, max_accept=1))
            x += l.XS

        x, y = l.XM+(8-reserves-1)*l.XS/2, self.height-l.YS
        for i in range(reserves):
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            x += l.XS

        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, 'n')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)

    def fillStack(self, stack):
        if stack in self.s.reserves:
            for stack in self.s.reserves:
                if stack.cards:
                    return
            old_state = self.enterState(self.S_FILL)
            self.s.talon.dealRow(rows=self.s.reserves, sound=1)
            self.leaveState(old_state)


# ************************************************************************
# * Aglet
# ************************************************************************

class Aglet(Game):

    def createGame(self, playcards=20, rows=8, reserves=1):

        decks = self.gameinfo.decks
        l, s = Layout(self), self.s
        self.setSize(l.XM+(reserves+0.5+rows)*l.XS,
                     l.YM+max(2*l.YS+7*l.YOFFSET, l.YS+playcards*l.YOFFSET))

        x, y = self.width-l.XS, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        x, y = l.XM, l.YM
        for i in range(reserves):
            stack = ReserveStack(x, y, self, max_cards=UNLIMITED_CARDS)
            stack.CARD_YOFFSET = l.YOFFSET
            s.reserves.append(stack)
            x += l.XS

        x, y = l.XM + (reserves+0.5+(rows-decks*4)/2.0)*l.XS, l.YM
        for i in range(4):
            s.foundations.append(RK_FoundationStack(x, y, self, suit=ANY_SUIT))
            x += l.XS

        x, y = l.XM+(reserves+0.5)*l.XS, l.YM+l.YS
        for i in range(rows):
            s.rows.append(BasicRowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS

        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRowAvail()
        self.s.talon.dealRowAvail()



# register the game
registerGame(GameInfo(257, Numerica, "Numerica",
                      GI.GT_NUMERICA | GI.GT_CONTRIB, 1, 0, GI.SL_BALANCED,
                      altnames=("Sir Tommy",) ))
registerGame(GameInfo(171, LadyBetty, "Lady Betty",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(355, Frog, "Frog",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(356, Fly, "Fly",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED,
                      rules_filename='frog.html'))
registerGame(GameInfo(357, Gnat, "Gnat",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(378, Gloaming, "Gloaming",
                      GI.GT_NUMERICA | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(379, Chamberlain, "Chamberlain",
                      GI.GT_NUMERICA | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(402, Toad, "Toad",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(430, PussInTheCorner, "Puss in the Corner",
                      GI.GT_NUMERICA, 1, 1, GI.SL_BALANCED))
registerGame(GameInfo(435, Shifting, "Shifting",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(472, Strategerie, "Strategerie",
                      GI.GT_NUMERICA, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(558, Numerica2Decks, "Numerica (2 decks)",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(589, LastChance, "Last Chance",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(599, Assembly, "Assembly",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(600, AnnoDomini, "Anno Domini",
                      GI.GT_NUMERICA, 1, 2, GI.SL_BALANCED))
registerGame(GameInfo(613, Fanny, "Fanny",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(641, CircleNine, "Circle Nine",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(643, Measure, "Measure",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(644, DoubleMeasure, "Double Measure",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(754, Amphibian, "Amphibian",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(760, Aglet, "Aglet",
                      GI.GT_1DECK_TYPE | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))

