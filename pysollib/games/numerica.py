#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------

import time

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.hint import CautiousDefaultHint, DefaultHint
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        AC_RowStack, \
        AbstractFoundationStack, \
        BasicRowStack, \
        DealRowTalonStack, \
        InitialDealTalonStack, \
        OpenStack, \
        OpenTalonStack, \
        RK_FoundationStack, \
        RK_RowStack, \
        ReserveStack, \
        SC_FoundationStack, \
        SS_FoundationStack, \
        Stack, \
        StackWrapper, \
        TalonStack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ACE, ANY_RANK, ANY_SUIT, JACK, KING, NO_RANK, \
        RANKS, UNLIMITED_ACCEPTS, \
        UNLIMITED_CARDS


class Numerica_Hint(DefaultHint):
    # FIXME: demo is clueless

    # def _getDropCardScore(self, score, color, r, t, ncards):
    # FIXME: implement this method

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
        # return _('Tableau. Accepts any one card from the Waste.')
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

    def createGame(self, rows=4, reserve=False, max_rounds=1,
                   waste_max_cards=1):
        # create layout
        l, s = Layout(self), self.s
        decks = self.gameinfo.decks
        foundations = 4*decks

        # set window
        # (piles up to 20 cards are playable in default window size)
        h = max(2.5 * l.YS, 20 * l.YOFFSET)
        max_rows = max(rows, foundations)
        self.setSize(l.XM + (1.5 + max_rows) * l.XS + l.XM, l.YM + l.YS + h)

        # create stacks
        x0 = l.XM + l.XS * 3 // 2
        if decks == 1:
            x = x0 + (rows-4)*l.XS//2
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
        self.setRegion(s.rows, (x0-l.XS//2, y-l.CH//2, 999999, 999999))
        x, y = l.XM, l.YM+l.YS+l.YS//2*int(reserve)
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
# * Colours
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


class Colours(LadyBetty):
    Foundation_Class = StackWrapper(SC_FoundationStack, mod=13, suit=ANY_SUIT)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()          # deal first card to WasteStack

    def _shuffleHook(self, cards):
        # prepare first cards
        topcards = [None] * 4
        evencolor = -1
        oddcolor = -1
        for c in cards[:]:
            if 0 < c.rank <= 4 and topcards[c.rank - 1] is None:
                if c.rank % 2 == 0:
                    if evencolor != -1 and c.color != evencolor:
                        continue
                    if oddcolor != -1 and c.color == oddcolor:
                        continue
                    evencolor = c.color
                elif c.rank % 2 == 1:
                    if oddcolor != -1 and c.color != oddcolor:
                        continue
                    if evencolor != -1 and c.color == evencolor:
                        continue
                    oddcolor = c.color

                topcards[c.rank - 1] = c
                cards.remove(c)
        topcards.reverse()
        return cards + topcards


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
        # return _('Tableau. Accepts any one card from the Waste.')
        return _('Tableau. Build regardless of rank and suit.')


class PussInTheCorner(Numerica):

    def createGame(self, rows=4):
        l, s = Layout(self), self.s
        self.setSize(l.XM+5*l.XS, l.YM+4*l.YS)
        for x, y in ((l.XM,        l.YM),
                     (l.XM+4*l.XS, l.YM),
                     (l.XM,        l.YM+3*l.YS),
                     (l.XM+4*l.XS, l.YM+3*l.YS),
                     ):
            stack = PussInTheCorner_RowStack(x, y, self,
                                             max_accept=1, max_move=1)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            s.rows.append(stack)
        for x, y in ((l.XM+1.5*l.XS, l.YM + l.YS),
                     (l.XM+1.5*l.XS, l.YM + 2*l.YS),
                     (l.XM+2.5*l.XS, l.YM + l.YS),
                     (l.XM+2.5*l.XS, l.YM + 2*l.YS),
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
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.rank == ACE, c.suit))

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
    # Foundation_Class = SS_FoundationStack
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
                suit = int(i//2)
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
            # stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
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
                # r = self.s.foundations[c.suit*2]
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
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.rank == ACE, c.suit))

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
# * Housefly
# ************************************************************************

class Gnat(Game):

    Hint_Class = Numerica_Hint

    def createGame(self, rows=4):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (4 + rows) * l.XS,
                     l.YM + 2 * l.YS + 16 * l.YOFFSET)

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
        for i in range(rows):
            s.rows.append(
                Numerica_RowStack(x, y, self, max_accept=UNLIMITED_ACCEPTS))
            x += l.XS
        x = l.XM + (2 + rows) * l.XS
        for i in range(2):
            y = l.YM + l.YS//2
            for j in range(3):
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
                y += l.YS
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()


class Housefly(Gnat):
    def createGame(self):
        Gnat.createGame(self, rows=6)


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
        n = 52//reserves+1
        w, h = l.XM + (reserves+rows+1)*l.XS, l.YM + 2*l.YS+n*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM+(reserves+rows+1-4)*l.XS//2, l.YM
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
            s.rows.append(
                Gloaming_RowStack(x, y, self, max_accept=UNLIMITED_ACCEPTS))
            x += l.XS

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    def startGame(self):
        n = 52//len(self.s.reserves)+1
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
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i//2))
            x += l.XS
        x, y = l.XM+3*l.XS//2, l.YM+l.YS
        for i in range(5):
            s.rows.append(
                Gloaming_RowStack(x, y, self, max_accept=UNLIMITED_ACCEPTS))
            x += l.XS
        y = l.YM+l.YS//2
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
        if from_stack is self.game.s.talon or \
                from_stack in self.game.s.reserves:
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


class AnnoDomini_Foundation(RK_FoundationStack):
    getBottomImage = RK_RowStack._getReserveBottomImage

    def acceptsCards(self, from_stack, cards):
        if len(cards) > 1:
            return False

        if len(self.cards) > 0:
            return (self.cards[-1].suit == cards[0].suit and
                    RK_FoundationStack.acceptsCards(self, from_stack, cards))

        foundations = self.game.s.foundations
        for i in range(4):
            if (foundations[i].cards and
                    foundations[i].cards[0].suit == cards[0].suit):
                return False
        if cards[0].rank != self.cap.base_rank:
            return False
        return True


class AnnoDomini(Numerica):
    Hint_Class = AnnoDomini_Hint

    Foundation_Class = StackWrapper(AnnoDomini_Foundation,
                                    suit=ANY_SUIT, mod=13)
    RowStack_Class = StackWrapper(AC_RowStack, mod=13)

    GAME_VERSION = 2

    def createGame(self):
        lay = Numerica.createGame(
            self, max_rounds=3, waste_max_cards=UNLIMITED_CARDS)
        self.year = str(time.localtime()[0])
        i = 0
        font = self.app.getFont("canvas_default")
        for s in self.s.foundations:
            d = int(self.year[i])
            if d == 0:
                d = JACK
            s.cap.base_rank = d
            if self.preview <= 1:
                label = RANKS[d][0]
                if label == "1":
                    label = "10"
                s.texts.misc = MfxCanvasText(self.canvas,
                                             s.x + lay.CW // 2,
                                             s.y + lay.CH // 2,
                                             anchor="center",
                                             font=font)
                s.texts.misc.config(text=label)
            i += 1
        lay.createRoundText(self.s.talon, 'nn')

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def _restoreGameHook(self, game):
        self.year = game.loadinfo.year
        i = 0
        for s in self.s.foundations:
            d = int(self.year[i])
            if d == 0:
                d = JACK
            s.cap.base_rank = i
            if self.preview <= 1:
                label = RANKS[d][0]
                if label == "1":
                    label = "10"
                s.texts.misc.config(text=label)
                i += 1

    def _loadGameHook(self, p):
        self.loadinfo.addattr(year=None)    # register extra load var.
        self.loadinfo.year = p.load()

    def _saveGameHook(self, p):
        p.dump(self.year)

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

        for i, j in ((1, 0),
                     (2, 0),
                     (3, 0),
                     (4, 0),
                     (5, 1),
                     (3.5, 2),
                     (2.5, 2),
                     (1.5, 2),
                     (0, 1),
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
        x, y = l.XM+(8-rows)*l.XS//2, l.YM + l.YS
        for i in range(rows):
            s.rows.append(Gloaming_RowStack(x, y, self, max_accept=1))
            x += l.XS

        x, y = l.XM+(8-reserves-1)*l.XS//2, self.height-l.YS
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
        self.setSize(l.XM + (reserves + 0.5+rows) * l.XS,
                     l.YM + max(2 * l.YS + 7 * l.YOFFSET,
                                l.YS + playcards * l.YOFFSET))

        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        x, y = l.XM, l.YM
        for i in range(reserves):
            stack = ReserveStack(x, y, self, max_cards=UNLIMITED_CARDS)
            stack.CARD_YOFFSET = l.YOFFSET
            s.reserves.append(stack)
            x += l.XS

        x, y = l.XM + (reserves + 0.5 + (rows-decks * 4) / 2.0) * l.XS, l.YM
        for i in range(4):
            s.foundations.append(RK_FoundationStack(x, y, self, suit=ANY_SUIT))
            x += l.XS

        x, y = l.XM+(reserves + 0.5) * l.XS, l.YM + l.YS
        for i in range(rows):
            s.rows.append(BasicRowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS

        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self._startDealNumRows(4)
        self.s.talon.dealRowAvail()
        self.s.talon.dealRowAvail()


# ************************************************************************
# * Ladybug
# ************************************************************************

class Ladybug_RowStack(Numerica_RowStack):
    def acceptsCards(self, from_stack, cards):
        return Numerica_RowStack.acceptsCards(self, from_stack, cards) \
               and self.game.isValidPlay(self.id, cards[0].rank)


class Ladybug_Talon(WasteTalonStack):
    def canDealCards(self):
        if not self.game.used and len(self.game.s.waste.cards) > 0:
            return False
        return WasteTalonStack.canDealCards(self)

    def dealCards(self, sound=False):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        game.saveStateMove(2 | 16)  # for undo
        game.used = False
        game.saveStateMove(1 | 16)  # for redo
        game.leaveState(old_state)
        return WasteTalonStack.dealCards(self, sound)


class Ladybug_Waste(WasteStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game = self.game
        if to_stack in game.s.rows:
            old_state = game.enterState(game.S_FILL)
            game.saveStateMove(2 | 16)  # for undo
            game.used = True
            game.saveStateMove(1 | 16)  # for redo
            game.leaveState(old_state)
        WasteStack.moveMove(self, ncards, to_stack, frames, shadow)
        game.s.talon.updateText(self)


class Ladybug(Game):
    used = False

    def createGame(self, rows=7):
        self.used = False
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 4 cards are playable in default window size)
        h = max(2 * l.YS, (4 * l.YOFFSET) + l.TEXT_HEIGHT)
        self.setSize(l.XM + (1.5 + rows) * l.XS + l.XM, l.YM + h)

        # create stacks
        x0 = l.XM + (l.XS * 1.5)
        x = x0
        y = l.YM + l.TEXT_HEIGHT

        font = self.app.getFont("canvas_default")
        for i in range(rows):
            stack = Ladybug_RowStack(x, y, self, max_cards=4,
                                     max_accept=1, max_move=0)
            if self.preview <= 1:
                tx, ty, ta, tf = l.getTextAttr(stack, anchor="n")
                stack.texts.misc = MfxCanvasText(self.canvas,
                                                 tx, ty,
                                                 anchor=ta,
                                                 font=font)
            s.rows.append(stack)
            x = x + l.XS
        self.setRegion(s.rows, (x0-l.XS//2, y-l.CH//2, 999999, 999999))
        x, y = l.XM, l.YM
        s.talon = Ladybug_Talon(x, y, self, max_rounds=-2, num_deal=3)
        l.createText(s.talon, 'ne')
        y = y + l.YS
        s.waste = Ladybug_Waste(x, y, self)
        l.createText(s.waste, 'ne')

        # define stack-groups
        l.defaultStackGroups()

        return l

    def isValidPlay(self, row, playRank):
        total = self.getTotal(self.s.rows[row], playRank)

        if total > 10:
            return False
        if total < 10 and len(self.s.rows[row].cards) == 3:
            return False
        return True

    def getTotal(self, row, extraRank=-1):
        cards = row.cards
        total = 0
        hasTen = False

        for card in cards:
            if card.rank < 9:
                total += card.rank + 1
            elif card.rank == 9:
                hasTen = True

        if extraRank > -1:
            if extraRank < 9:
                total += extraRank + 1
            elif extraRank == 9:
                hasTen = True

        if hasTen and total < 10:
            return 10

        return total

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows)
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def updateText(self):
        if self.preview > 1:
            return
        for row in self.s.rows:
            row.texts.misc.config(text=str(self.getTotal(row)))

    def isGameWon(self):
        for row in self.s.rows:
            if len(row.cards) != 4:
                return False
        return True

    def _restoreGameHook(self, game):
        self.used = game.loadinfo.used

    def _loadGameHook(self, p):
        self.loadinfo.addattr(used=p.load())

    def _saveGameHook(self, p):
        p.dump(self.used)

    def getHighlightPilesStacks(self):
        return ()

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.used = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.used]


# ************************************************************************
# * The Bogey
# ************************************************************************

class TheBogey_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return 1
        return (self.cards[-1].rank > cards[0].rank
                and self.cards[-1].suit == cards[0].suit)

    def canMoveCards(self, cards):
        return False


class TheBogey_BogeyDraw(OpenStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        OpenStack.moveMove(self, ncards, to_stack, frames=frames,
                           shadow=shadow)
        rows = [r for r in self.game.s.rows if not len(r.cards) > 0]
        self.game.startDealSample()
        self.game.s.talon.dealRowAvail(rows=rows)
        rows2 = [r for r in self.game.s.rows if not len(r.cards) > 0]
        if len(rows2) > 0:
            self.game.s.talon.redeal(sound=False)
            self.game.s.talon.dealRowAvail(rows=rows2)
        self.game.stopSamples()


class TheBogey_RowStack(OpenStack):

    def canMoveCards(self, cards):
        if len(self.game.s.reserves[0].cards) > 0:
            return False
        return OpenStack.canMoveCards(self, cards)


class TheBogey_Talon(TalonStack):
    def canDealCards(self):
        return (len(self.game.s.reserves[0].cards) < 1 and
                (len(self.cards) > 0 or
                 len(self.game.s.reserves[0].cards) > 0))

    def dealCards(self, sound=False):
        if len(self.cards) < 1:
            self.redeal(sound=sound)
        if sound:
            self.game.playSample("dealwaste")
        self.flipMove()
        self.moveMove(1, self.game.s.reserves[0])

    def redeal(self, sound=False):
        if len(self.game.s.reserves[1].cards) > 0:
            assert len(self.cards) == 0
            if sound:
                self.game.playSample("turnwaste", priority=20)
            self.game.turnStackMove(self.game.s.reserves[1], self)
            self.game.shuffleStackMove(self)
            self.game.nextRoundMove(self)


class TheBogey_Discard(OpenStack):
    getBottomImage = Stack._getReserveBottomImage

    def acceptsCards(self, from_stack, cards):
        return len(self.game.s.reserves[0].cards) < 1

    def canMoveCards(self, cards):
        return False


class TheBogey(Game):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 12 * l.XS, l.YM + 2 * l.YS + 13 * l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(12):
            s.foundations.append(TheBogey_Foundation(x, y, self, dir=-1,
                                                     suit=ANY_SUIT))
            s.foundations[i].CARD_YOFFSET = l.YOFFSET
            x += l.XS

        x, y = l.XM, self.height - l.YS

        s.talon = TheBogey_Talon(x, y, self, max_rounds=-1)
        l.createText(s.talon, 'n')

        x += l.XS
        s.reserves.append(TheBogey_BogeyDraw(x, y, self))

        x += 3 * l.XS

        for i in range(5):
            s.rows.append(TheBogey_RowStack(x, y, self, max_cards=1,
                                            max_accept=0))
            x += l.XS

        x += 2 * l.XS
        s.reserves.append(TheBogey_Discard(x, y, self))
        l.createText(s.reserves[1], 'n')

        self.setRegion(s.reserves, (-999, y - l.CH // 2, 999999, 999999))

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows)


# ************************************************************************
# * Ninety-One
# ************************************************************************

class NinetyOne_RowStack(OpenStack):

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        OpenStack.moveMove(self, ncards, to_stack, frames=frames,
                           shadow=shadow)
        if to_stack in self.game.s.rows:
            self.game.checkTotal()


class NinetyOne(Game):
    Hint_Class = None

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        self.setSize(l.XM + 7 * l.XS, l.YM + 2 * l.YS)

        x, y = l.XM, l.YM
        # create stacks
        for j in range(7):
            s.rows.append(NinetyOne_RowStack(x, y, self, max_move=1,
                                             max_accept=1))
            x += l.XS
        x, y = l.XM, l.YM + l.YS
        for j in range(6):
            s.rows.append(NinetyOne_RowStack(x, y, self, max_move=1,
                                             max_accept=1))
            x += l.XS

        # create text
        if self.preview <= 1:
            y += l.YS // 2
            self.texts.score = MfxCanvasText(
                self.canvas, x, y, anchor="sw",
                font=self.app.getFont("canvas_large"))

        x, y = self.getInvisibleCoords()
        s.talon = InitialDealTalonStack(x, y, self)
        s.foundations.append(AbstractFoundationStack(x, y, self,
                                                     max_move=0,
                                                     max_accept=0,
                                                     suit=ANY_SUIT))

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self._startAndDealRow()

    def updateText(self):
        if self.preview > 1 or not self.texts.score:
            return
        self.texts.score.config(text=str(self.getTotal()))

    def getTotal(self):
        total = 0
        for r in self.s.rows:
            if len(r.cards) == 0:
                continue
            total += r.cards[-1].rank + 1
        return total

    def checkTotal(self):
        self.updateText()
        if self.getTotal() == 91:
            for r in self.s.rows:
                if len(r.cards) == 0:
                    return
            self.startDealSample()
            old_state = self.enterState(self.S_FILL)
            for r in self.s.rows:
                r.moveMove(1, self.s.foundations[0])
            self.leaveState(old_state)
            self.stopSamples()
            self.checkTotal()

    def getAutoStacks(self, event=None):
        return ((), (), ())


# register the game
registerGame(GameInfo(257, Numerica, "Numerica",
                      GI.GT_NUMERICA | GI.GT_CONTRIB, 1, 0, GI.SL_BALANCED,
                      altnames=("Sir Tommy", "Old Patience", "Try Again")))
registerGame(GameInfo(171, LadyBetty, "Lady Betty",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(355, Frog, "Frog",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(356, Fly, "Fly",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(357, Gnat, "Gnat",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(378, Gloaming, "Gloaming",
                      GI.GT_NUMERICA | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(379, Chamberlain, "Chamberlain",
                      GI.GT_NUMERICA | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(402, Toad, "Toad",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED,
                      altnames=("Toad in the Hole")))
registerGame(GameInfo(430, PussInTheCorner, "Puss in the Corner",
                      GI.GT_NUMERICA, 1, 1, GI.SL_BALANCED))
registerGame(GameInfo(435, Shifting, "Shifting",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(472, Strategerie, "Strategerie",
                      GI.GT_NUMERICA, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(558, Numerica2Decks, "Numerica (2 Decks)",
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
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(644, DoubleMeasure, "Double Measure",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 2, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(754, Amphibian, "Amphibian",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 2, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(760, Aglet, "Aglet",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(836, Ladybug, "Ladybug",
                      GI.GT_1DECK_TYPE, 1, -2, GI.SL_BALANCED))
registerGame(GameInfo(899, Housefly, "Housefly",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(931, TheBogey, "The Bogey",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(958, NinetyOne, "Ninety-One",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(972, Colours, "Colours",
                      GI.GT_NUMERICA, 1, 0, GI.SL_BALANCED))
