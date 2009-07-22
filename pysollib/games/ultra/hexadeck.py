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
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# * Hex A Deck Foundation Stacks
# ************************************************************************

class HexADeck_FoundationStack(SS_FoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_move=0, max_cards=12)
        SS_FoundationStack.__init__(self, x, y, game, suit, **cap)


class HexATrump_Foundation(HexADeck_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        for s in self.game.s.foundations[:3]:
            if len(s.cards) != 16:
                return 0
        return 1


class Merlins_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=16, dir=0, base_rank=NO_RANK, max_move=0)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return 1
        stack_dir = self.game.getFoundationDir()
        if stack_dir == 0:
            card_dir = (cards[0].rank - self.cards[-1].rank) % self.cap.mod
            return card_dir in (1, 15)
        else:
            return (self.cards[-1].rank + stack_dir) % self.cap.mod == cards[0].rank


# ************************************************************************
# * Hex A Deck Row Stacks
# ************************************************************************

class HexADeck_OpenStack(OpenStack):

    def __init__(self, x, y, game, yoffset, **cap):
        kwdefault(cap, max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS, dir=-1)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def isRankSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not c1.rank + dir == c2.rank:
                return 0
            c1 = c2
        return 1

    def isAlternateColorSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if (c1.color < 2 and c1.color == c2.color
                    or not c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isSuitSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not ((c1.color == 2 or c2.color == 2
                    or c1.suit == c2.suit)
                    and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1


class HexADeck_RK_RowStack(HexADeck_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
                or not self.isRankSequence(cards)):
            return 0
        if not self.cards:
            return cards[0].rank == 15 or self.cap.base_rank == ANY_RANK
        return self.isRankSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards)
                and self.isRankSequence(cards))


class HexADeck_AC_RowStack(HexADeck_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
                or not self.isAlternateColorSequence(cards)):
            return 0
        if not self.cards:
            return cards[0].rank == 15 or self.cap.base_rank == ANY_RANK
        return self.isAlternateColorSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards)
                and self.isAlternateColorSequence(cards))


class HexADeck_SS_RowStack(HexADeck_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
                or not self.isSuitSequence(cards)):
            return 0
        if not self.cards:
            return cards[0].rank == 15 or self.cap.base_rank == ANY_RANK
        return self.isSuitSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards)
                and self.isSuitSequence(cards))


class Bits_RowStack(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if stackcards or cards[0].suit == 4:
            return 0
        i = int(self.id / 4)
        for r in self.game.s.rows[i * 4:self.id]:
            if not r.cards:
                return 0
        return ((self.game.s.foundations[i].cards[-1].rank + 1
                    >> (self.id % 4)) % 2 == (cards[0].rank + 1) % 2)


class Bytes_RowStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if stackcards or cards[0].suit == 4:
            return 0
        id = self.id - 16
        i = int(id / 2)
        for r in self.game.s.rows[16 + i * 2:self.id]:
            if not r.cards:
                return 0
        return self.game.s.foundations[i].cards[-1].rank == cards[0].rank


class HexAKlon_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if stackcards:
            if (stackcards[-1].suit == 4 or cards[0].suit == 4):
                return 1
        return AC_RowStack.acceptsCards(self, from_stack, cards)


class HexADeck_ACRowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if stackcards:
            if (stackcards[-1].suit == 4 or cards[0].suit == 4):
                return stackcards[-1].rank == cards[0].rank + 1
        return AC_RowStack.acceptsCards(self, from_stack, cards)


class Familiar_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return 0
        # Only take Wizards
        return cards[0].suit == 4

    def getBottomImage(self):
        return self.game.app.images.getSuitBottom(4)


class Merlins_BraidStack(OpenStack):
    def __init__(self, x, y, game):
        OpenStack.__init__(self, x, y, game)
        CW = self.game.app.images.CARDW
        self.CARD_YOFFSET = self.game.app.images.CARD_YOFFSET
        # use a sine wave for the x offsets
        self.CARD_XOFFSET = []
        j = 1
        for i in range(20):
            self.CARD_XOFFSET.append(int(math.sin(j) * 20))
            j = j + .9


class Merlins_RowStack(ReserveStack):
    def fillStack(self):
        if not self.cards and self.game.s.braid.cards:
            self.game.moveMove(1, self.game.s.braid, self)

    def getBottomImage(self):
        return self.game.app.images.getBraidBottom()


class Merlins_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if from_stack is self.game.s.braid or from_stack in self.game.s.rows:
            return 0
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()


# ************************************************************************
# *
# ************************************************************************

class AbstractHexADeckGame(Game):
    RANKS = (_("Ace"), "2", "3", "4", "5", "6", "7", "8", "9",
             "A", "B", "C", "D", "E", "F", "10")


class Merlins_Hint(DefaultHint):
    pass


# ************************************************************************
# * Bits n Bytes
# ************************************************************************

class BitsNBytes(Game):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(l.XM * 4 + l.XS * 8, l.YM + l.YS * 4)

        # Create bit stacks
        self.bit_texts = []
        y = l.YM
        for j in range(4):
            x = l.XM * 4 + l.XS * 7
            for i in range(4):
                s.rows.append(Bits_RowStack(x, y, self, max_cards=1,
                                    max_accept=1, base_suit=j, max_move=0))
                self.bit_texts.append(MfxCanvasText(self.canvas, x + l.CW / 2 , y + l.CH / 2,
                                        anchor="center", font=font))
                x = x - l.XS
            y = y + l.YS

        # Create byte stacks
        y = l.YM
        for j in range(4):
            x = l.XM * 3 + l.XS * 3
            for i in range(2):
                s.rows.append(Bytes_RowStack(x, y, self, max_cards=1,
                                    max_accept=1, base_suit=ANY_SUIT, max_move=0))
                x = x - l.XS
            y = y + l.YS

        # Create foundations
        x = l.XM * 2 + l.XS
        y = l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i, mod=1,
                                             max_move=0, max_cards=1))
            y = y + l.YS
        self.setRegion(s.rows, (0, 0, 999999, 999999))

        # Create talon
        x = l.XM
        y = l.YM
        s.talon = WasteTalonStack(x, y, self, num_deal=2, max_rounds=2)
        l.createText(s.talon, "s")
        y += l.YS + l.TEXT_HEIGHT
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def updateText(self):
        if self.preview > 1:
            return
        for j in range(4):
            if not len(self.s.foundations[j].cards):
                break
            s = self.s.foundations[j].cards[-1].rank + 1
            for i in range(4):
                self.bit_texts[i + j * 4].config(text = str(s % 2))
                s = int(s / 2)

    def _shuffleHook(self, cards):
        topcards, ranks = [None] * 4, [None] * 4
        for c in cards[:]:
            if not c.suit == 4:
                if not topcards[c.suit]:
                    haverank = 0
                    for i in range(4):
                        if c.rank == ranks[i]:
                            haverank = 1
                    if not haverank:
                        topcards[c.suit] = c
                        ranks[c.suit] = c.rank
                        cards.remove(c)
        cards = topcards + cards
        cards.reverse()
        return cards

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()

    def isGameWon(self):
        for s in self.s.rows:
            if not s.cards:
                return 0
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return 0


# ************************************************************************
# * Hex A Klon
# ************************************************************************

class HexAKlon(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = HexAKlon_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=-1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations[:4]:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))
        r = l.s.foundations[4]
        s.foundations.append(HexATrump_Foundation(r.x, r.y, self, 4, mod=4,
                                    max_move=0, max_cards=4, base_rank=ANY_RANK))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Hex A Klon by Threes
# ************************************************************************

class HexAKlonByThrees(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = HexAKlon_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=-1, num_deal=3, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations[:4]:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))
        r = l.s.foundations[4]
        s.foundations.append(HexATrump_Foundation(r.x, r.y, self, 4, mod=4,
                                    max_move=0, max_cards=4, base_rank=ANY_RANK))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * King Only Hex A Klon
# ************************************************************************

class KingOnlyHexAKlon(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = HexAKlon_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=-1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations[:4]:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))
        r = l.s.foundations[4]
        s.foundations.append(HexATrump_Foundation(r.x, r.y, self, 4, mod=4,
                                    max_move=0, max_cards=4, base_rank=ANY_RANK))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=15))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def _shuffleHook(self, cards):
        basecard = [None]
        for c in cards[:]:
            if c.suit == 4:
                if basecard[0] == None:
                    basecard[0] = c
                    cards.remove(c)
        cards = basecard + cards
        cards.reverse()
        return cards

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Klondike Plus 16
# ************************************************************************

class KlondikePlus16(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = HexAKlon_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=2, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=15))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * The Familiar
# ************************************************************************

class TheFamiliar(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=2, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=15))

        # Create reserve
        x, y = l.XM, self.height - l.YS
        s.reserves.append(Familiar_ReserveStack(x, y, self, max_cards=3))
        self.setRegion(s.reserves, (-999, y - l.YM, x + l.XS, 999999), priority=1)
        l.createText(s.reserves[0], "se")

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Two Familiars
# ************************************************************************

class TwoFamiliars(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=2, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=12, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=15))

        # Create reserve
        x, y = l.XM, self.height - l.YS
        s.reserves.append(Familiar_ReserveStack(x, y, self, max_cards=3))
        self.setRegion(s.reserves, (-999, y - l.YM, x + l.XS, 999999), priority=1)
        l.createText(s.reserves[0], "se")

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68 * 2
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Ten by Eight
# ************************************************************************

class TenByEight(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.gypsyLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=-1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, waste=1, playcards=30)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68 * 2
        frames = 0
        for i in range(8):
            if i == 5:
                frames = -1
                self.startDealSample()
            self.s.talon.dealRow(frames=frames)
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Drawbridge
# ************************************************************************

class Drawbridge(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.harpLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=2, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=7, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(len(self.s.rows) - 1):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Double Drawbridge
# ************************************************************************

class DoubleDrawbridge(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.harpLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=2, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68 * 2
        for i in range(len(self.s.rows) - 1):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Hidden Passages
# ************************************************************************

class HiddenPassages(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=2, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=7, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations[:4]:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))
        r = l.s.foundations[4]
        s.foundations.append(HexATrump_Foundation(r.x, r.y, self, 4, mod=4,
                                    max_move=0, max_cards=4, base_rank=ANY_RANK))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #
    def _shuffleHook(self, cards):
        topcards = [None] * 4
        for c in cards[:]:
            if c.rank == 0 and not c.suit == 4:
                topcards[c.suit] = c
                cards.remove(c)
        cards = topcards + cards
        cards.reverse()
        return cards

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        self.s.talon.dealRow(rows=self.s.foundations[:4], frames=0)
        for i in range(2):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Cluitjar's Lair
# ************************************************************************

class CluitjarsLair(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = HexADeck_ACRowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=7, waste=1, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations[:4]:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))
        r = l.s.foundations[4]
        s.foundations.append(HexATrump_Foundation(r.x, r.y, self, 4, mod=4,
                                    max_move=0, max_cards=4, base_rank=ANY_RANK))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #
    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(2):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Merlin's Meander
# ************************************************************************

class MerlinsMeander(AbstractHexADeckGame):
    Hint_Class = Merlins_Hint
    MERLINS_CARDS = 20

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 20 cards are playable - needed for Braid_BraidStack)
        h = max(4*l.YS + 30, l.YS+(self.MERLINS_CARDS-1)*l.YOFFSET)
        self.setSize(10*l.XS+l.XM, l.YM + h)

        # extra settings
        self.base_card = None

        # Create rows, reserves
        s.addattr(braid=None)      # register extra stack variable
        x, y = l.XM, l.YM
        for i in range(2):
            s.rows.append(Merlins_RowStack(x + l.XS * 0.5, y, self))
            s.rows.append(Merlins_RowStack(x + l.XS * 4.5, y, self))
            s.reserves.append(Familiar_ReserveStack(x + l.XS * 6.5, y, self, max_cards=3))
            y = y + l.YS * 3
        y = l.YM + l.YS
        for i in range(2):
            s.rows.append(Merlins_ReserveStack(x, y, self))
            s.rows.append(Merlins_ReserveStack(x + l.XS, y, self))
            s.rows.append(Merlins_ReserveStack(x, y + l.YS, self))
            s.rows.append(Merlins_ReserveStack(x + l.XS, y + l.YS, self))
            x = x + l.XS * 4

        # Create braid
        x, y = l.XM + l.XS * 2.2, l.YM
        s.braid = Merlins_BraidStack(x, y, self)

        # Create talon, waste
        x, y = l.XM + l.XS * 7, l.YM + l.YS * 1.5
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "s")
        s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                             x + l.CW / 2, y - l.YM,
                                             anchor="s",
                                             font=self.app.getFont("canvas_default"))
        x = x - l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # Create foundations
        x, y = l.XM + l.XS * 8, l.YM
        for i in range(4):
            s.foundations.append(Merlins_Foundation(x, y, self, i, mod=16,
                                                max_cards=16, base_rank=ANY_RANK))
            s.foundations.append(Merlins_Foundation(x + l.XS, y, self, i, mod=16,
                                                max_cards=16, base_rank=ANY_RANK))
            y = y + l.YS
        self.texts.info = MfxCanvasText(self.canvas,
                                        x + l.CW + l.XM / 2, y,
                                        anchor="n",
                                        font=self.app.getFont("canvas_default"))

        # define stack-groups
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.openstacks = s.foundations + s.rows + s.reserves
        self.sg.dropstacks = [s.braid] + s.rows + [s.waste] + s.reserves


    #
    # game overrides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68 * 2
        self.startDealSample()
        self.base_card = None
        self.updateText()
        for i in range(self.MERLINS_CARDS):
            self.s.talon.dealRow(rows=[self.s.braid])
        self.s.talon.dealRow()
        # deal base_card to foundations, update cap.base_rank
        self.base_card = self.s.talon.getCard()
        while self.base_card.suit == 4:
            self.s.talon.cards.remove(self.base_card)
            self.s.talon.cards.insert(0, self.base_card)
            self.base_card = self.s.talon.getCard()
        to_stack = self.s.foundations[2 * self.base_card.suit]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack)
        self.updateText()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        # deal first card to WasteStack
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 16 == card2.rank or (card2.rank + 1) % 16 == card1.rank))

    def getHighlightPilesStacks(self):
        return ()

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


    #
    # game extras
    #

    def updateText(self):
        if self.preview > 1 or not self.texts.info:
            return
        if not self.base_card:
            t = ""
        else:
            t = self.RANKS[self.base_card.rank]
            dir = self.getFoundationDir() % 16
            if dir == 1:
                t = t + _(" Ascending")
            elif dir == 15:
                t = t + _(" Descending")
        self.texts.info.config(text=t)

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards and s.cards[0].suit != 4:
                return 0
        if not len(self.s.talon.cards) and len(self.s.waste.cards) == 1:
            return self.s.waste.cards[0].suit == 4
        return len(self.s.talon.cards) + len(self.s.waste.cards) == 0


# ************************************************************************
# * Mage's Game
# ************************************************************************

class MagesGame(Game):
    Hint_Class = CautiousDefaultHint
    Layout_Method = Layout.gypsyLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, max_rounds=1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=12, texts=0, playcards=20)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                max_rounds=max_rounds, num_deal=num_deal)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=16, max_cards=16, max_move=1))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                    suit=ANY_SUIT, base_rank=ANY_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 68
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[2:10])
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))



# ************************************************************************
# *
# ************************************************************************

class Convolution(AbstractHexADeckGame):
    RowStack_Class = StackWrapper(HexADeck_RK_RowStack, base_rank=NO_RANK)

    #
    # game layout
    #

    def createGame(self, rows=9, reserves=8):
        # create layout
        l, s = Layout(self), self.s

        # set size
        maxrows = max(rows, reserves)
        self.setSize(l.XM + (maxrows + 2) * l.XS, l.YM + 6 * l.YS)

        #
        playcards = 4 * l.YS / l.YOFFSET
        xoffset, yoffset = [], []
        for i in range(playcards):
            xoffset.append(0)
            yoffset.append(l.YOFFSET)
        for i in range(68 * self.gameinfo.decks - playcards):
            xoffset.append(l.XOFFSET)
            yoffset.append(0)

        # create stacks
        x, y = l.XM + (maxrows - reserves) * l.XS / 2, l.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        x, y = l.XM + (maxrows - rows) * l.XS / 2, l.YM + l.YS
        self.setRegion(s.reserves, (-999, -999, 999999, y - l.YM / 2))
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self, yoffset=yoffset)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = yoffset
            s.rows.append(stack)
            x = x + l.XS
        x, y = l.XM + maxrows * l.XS, l.YM
        for i in range(2):
            for suit in range(5):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=suit, max_cards=16))
                y = y + l.YS
            x, y = x + l.XS, l.YM
        self.setRegion(self.s.foundations, (x - l.XS * 2, -999, 999999,
                        self.height - (l.YS + l.YM)), priority=1)
        s.talon = InitialDealTalonStack(self.width - 3 * l.XS / 2, self.height - l.YS, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        i = 0
        while self.s.talon.cards:
            if self.s.talon.cards[-1].rank == 15:
                if self.s.rows[i].cards:
                    i = i + 1
            self.s.talon.dealRow(rows=[self.s.rows[i]], frames=4)

    # must look at cards
    def _getClosestStack(self, cx, cy, stacks, dragstack):
        closest, cdist = None, 999999999
        for stack in stacks:
            if stack.cards and stack is not dragstack:
                dist = (stack.cards[-1].x - cx)**2 + (stack.cards[-1].y - cy)**2
            else:
                dist = (stack.x - cx)**2 + (stack.y - cy)**2
            if dist < cdist:
                closest, cdist = stack, dist
        return closest

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isRankSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))


# ************************************************************************
# *
# ************************************************************************

class Labyrinth(Convolution):
    RowStack_Class = StackWrapper(HexADeck_AC_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isAlternateColorSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))



# ************************************************************************
# *
# ************************************************************************

class Snakestone(Convolution):
    RowStack_Class = StackWrapper(HexADeck_SS_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isSuitSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))



# ************************************************************************
# *
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level):
    game_type = game_type | GI.GT_HEXADECK
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  suits=range(4), ranks=range(16), trumps=range(4))
    registerGame(gi)
    return gi


r(165, BitsNBytes, 'Bits n Bytes', GI.GT_HEXADECK, 1, 1, GI.SL_BALANCED)
r(166, HexAKlon, 'Hex A Klon', GI.GT_HEXADECK, 1, -1, GI.SL_BALANCED)
r(16666, KlondikePlus16, 'Klondike Plus 16', GI.GT_HEXADECK, 1, 1, GI.SL_BALANCED)
r(16667, HexAKlonByThrees, 'Hex A Klon by Threes', GI.GT_HEXADECK, 1, -1, GI.SL_BALANCED)
r(16668, KingOnlyHexAKlon, 'King Only Hex A Klon', GI.GT_HEXADECK, 1, -1, GI.SL_BALANCED)
r(16669, TheFamiliar, 'The Familiar', GI.GT_HEXADECK, 1, 1, GI.SL_BALANCED)
r(16670, TwoFamiliars, 'Two Familiars', GI.GT_HEXADECK, 2, 1, GI.SL_BALANCED)
r(16671, TenByEight, '10 x 8', GI.GT_HEXADECK, 2, -1, GI.SL_BALANCED)
r(16672, Drawbridge, 'Drawbridge', GI.GT_HEXADECK, 1, 1, GI.SL_BALANCED)
r(16673, DoubleDrawbridge, 'Double Drawbridge', GI.GT_HEXADECK, 2, 1, GI.SL_BALANCED)
r(16674, HiddenPassages, 'Hidden Passages', GI.GT_HEXADECK, 1, 1, GI.SL_MOSTLY_LUCK)
r(16675, CluitjarsLair, 'Cluitjar\'s Lair', GI.GT_HEXADECK, 1, 0, GI.SL_BALANCED)
r(16676, MerlinsMeander, 'Merlin\'s Meander', GI.GT_HEXADECK, 2, 2, GI.SL_BALANCED)
r(16677, MagesGame, 'Mage\'s Game', GI.GT_HEXADECK, 1, 0, GI.SL_BALANCED)
r(16678, Convolution, 'Convolution', GI.GT_HEXADECK, 2, 0, GI.SL_MOSTLY_SKILL)
r(16679, Labyrinth, 'Hex Labyrinth', GI.GT_HEXADECK, 2, 0, GI.SL_MOSTLY_SKILL)
r(16680, Snakestone, 'Snakestone', GI.GT_HEXADECK, 2, 0, GI.SL_MOSTLY_SKILL)

del r
