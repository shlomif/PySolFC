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

from pysollib.games.braid import Braid_Foundation, Braid_BraidStack, \
     Braid_RowStack, Braid_ReserveStack, Braid
from pysollib.games.bakersdozen import Cruel_Talon


# ************************************************************************
# * Tarock Talon Stacks
# ************************************************************************

class Wicked_Talon(Cruel_Talon):
    pass


# ************************************************************************
# * Tarock Foundation Stacks
# ************************************************************************

class ImperialTrump_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        return cards[-1].rank < len(self.game.s.foundations[4].cards)


class Ponytail_Foundation(Braid_Foundation):
    pass


# ************************************************************************
# * Tarock Row Stacks
# ************************************************************************

class Tarock_OpenStack(OpenStack):
    def __init__(self, x, y, game, yoffset=-1, **cap):
        kwdefault(cap, max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS)
        OpenStack.__init__(self, x, y, game, **cap)
        if yoffset < 0:
            yoffset = game.app.images.CARD_YOFFSET
        self.CARD_YOFFSET = yoffset


class Tarock_AC_RowStack(Tarock_OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.cards:
            return 1
        if cards[0].rank != self.cards[-1].rank - 1:
            return 0
        elif cards[0].color == 2 or self.cards[-1].color == 2:
            return 1
        else:
            return cards[0].color != self.cards[-1].color


class Skiz_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.cards:
            if cards[0].suit == len(self.game.gameinfo.suits):
                return cards[0].rank == len(self.game.gameinfo.trumps) - 1
            else:
                return cards[0].rank == len(self.game.gameinfo.ranks) - 1
        return self.cards[-1].suit == cards[0].suit and self.cards[-1].rank - 1 == cards[0].rank


class Pagat_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.cards:
            return 1
        return self.cards[-1].suit == cards[0].suit and self.cards[-1].rank - 1 == cards[0].rank


class TrumpWild_RowStack(Tarock_OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.cards:
            if cards[0].suit == len(self.game.gameinfo.suits):
                return cards[0].rank == len(self.game.gameinfo.trumps) - 1
            else:
                return cards[0].rank == len(self.game.gameinfo.ranks) - 1
        if cards[0].rank != self.cards[-1].rank - 1:
            return 0
        elif cards[0].color == 2 or self.cards[-1].color == 2:
            return 1
        else:
            return cards[0].color != self.cards[-1].color


class TrumpOnly_RowStack(Tarock_OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.cards:
            return cards[0].suit == len(self.game.gameinfo.suits)
        return cards[0].color == 2 and cards[0].rank == self.cards[-1].rank - 1

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class Excuse_RowStack(Tarock_OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.cards:
            return 0
        return cards[0].rank == self.cards[-1].rank - 1


class WheelOfFortune_RowStack(Tarock_OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.cards:
            return 1
        return ((cards[0].suit == self.cards[-1].suit)
                and (cards[0].rank == self.cards[-1].rank - 1))

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class Ponytail_PonytailStack(Braid_BraidStack):
    pass


class Ponytail_RowStack(Braid_RowStack):
    pass


class Ponytail_ReserveStack(Braid_ReserveStack):
    pass


class Cavalier_RowStack(Tarock_AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not Tarock_AC_RowStack.acceptsCards(self, from_stack, cards):
            return 0
        return self.cards or len(cards) == 1

    def canMoveCards(self, cards):
        for i in range(len(cards) - 1):
            if not cards[i].suit == 4:
                if cards[i].color == cards[i + 1].color:
                    return 0
            if cards[i].rank - 1 != cards[i + 1].rank:
                return 0
        return 1


class Nasty_RowStack(SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if self.cards:
            return (cards[0].rank == self.cards[-1].rank - 1
                    and cards[0].suit == self.cards[-1].suit)
        return cards[0].rank == 13 + 8 * (cards[0].suit == 4)


# ************************************************************************
# *
# ************************************************************************

class Tarock_GameMethods:
    SUITS = (_("Wand"), _("Sword"), _("Cup"), _("Coin"), _("Trump"))
    RANKS = (_("Ace"), "2", "3", "4", "5", "6", "7", "8", "9", "10",
             _("Page"), _("Valet"), _("Queen"), _("King"))

    def getCardFaceImage(self, deck, suit, rank):
        return self.app.images.getFace(deck, suit, rank)


class AbstractTarockGame(Tarock_GameMethods, Game):
    pass


# ************************************************************************
# * Wheel of Fortune
# ************************************************************************

class WheelOfFortune(AbstractTarockGame):
    Hint_Class = CautiousDefaultHint

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(l.XM + l.XS * 11.5, l.YM + l.YS * 5.5)

        # Create wheel
        xoffset = (1, 2, 3, 3.9, 3, 2, 1, 0, -1, -2, -3,
                    -3.9, -3, -2, -1, 0, -2, -1, 0, 1, 2)
        yoffset = (0.2, 0.5, 1.1, 2.2, 3.3, 3.9, 4.2, 4.4,
                    4.2, 3.9, 3.3, 2.2, 1.1, 0.5, 0.2, 0,
                    1.8, 2.1, 2.2, 2.4, 2.6)
        x = l.XM + l.XS * 4
        y = l.YM
        for i in range(21):
            x0 = x + xoffset[i] * l.XS
            y0 = y + yoffset[i] * l.YS
            s.rows.append(WheelOfFortune_RowStack(x0, y0, self, yoffset=l.CH/4,
                          max_cards=2, max_move=1, max_accept=1))
        self.setRegion(s.rows, (-999, -999, l.XS * 9, 999999))

        # Create foundations
        x = self.width - l.XS * 2
        y = l.YM
        s.foundations.append(SS_FoundationStack(x, y, self, 0, max_cards=14))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 1, max_cards=14))
        y = y + l.YS
        s.foundations.append(SS_FoundationStack(x, y, self, 3, max_cards=14))
        x = x - l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 2, max_cards=14))
        x = x + l.XS * 0.5
        y = y + l.YS
        s.foundations.append(SS_FoundationStack(x, y, self, 4, max_cards=22))

        # Create talon
        x = self.width - l.XS
        y = self.height - l.YS * 1.5
        s.talon = WasteTalonStack(x, y, self, num_deal=2, max_rounds=1)
        l.createText(s.talon, "n")
        x = x - l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "n")

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 78
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[-5:])
        self.s.talon.dealRow(rows=self.s.rows[4:-5])
        self.s.talon.dealRow(rows=self.s.rows[:4])
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return 0


# ************************************************************************
# * Imperial Trumps
# ************************************************************************

class ImperialTrumps(AbstractTarockGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(l.XM + l.XS * 8, l.YM + l.YS * 5)


        # Create foundations
        x = l.XM + l.XS * 3
        y = l.YM
        for i in range(4):
            s.foundations.append(ImperialTrump_Foundation(x, y, self, i, max_cards=14))
            x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 4, max_cards=22))

        # Create talon
        x = l.XM
        s.talon = WasteTalonStack(x, y, self, num_deal=1, max_rounds=-1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # Create rows
        x = l.XM
        y = l.YM + l.YS + l.TEXT_HEIGHT
        for i in range(8):
            s.rows.append(TrumpWild_RowStack(x, y, self))
            x = x + l.XS
        self.setRegion(s.rows, (-999, y, 999999, 999999))

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self, reverse=1):
        assert len(self.s.talon.cards) == 78
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(reverse=reverse)
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return 0


# ************************************************************************
# * Pagat
# ************************************************************************

class Pagat(AbstractTarockGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        h = max(3 * l.YS, 20 * l.YOFFSET)
        self.setSize(l.XM + 12 * l.XS, l.YM + l.YS + h)

        # Create foundations
        x = l.XM + l.XS * 3.5
        y = l.YM
        s.foundations.append(SS_FoundationStack(x, y, self, 0, max_cards=14))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 1, max_cards=14))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 4, max_cards=22))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 2, max_cards=14))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 3, max_cards=14))

        # Create reserves
        x = l.XM
        for i in range(3):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        x = x + l.XS * 6
        for i in range(3):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS

        # Create rows
        x = l.XM
        y = l.YM + l.YS * 1.1
        for i in range(12):
            s.rows.append(Pagat_RowStack(x, y, self))
            x = x + l.XS
        self.setRegion(s.rows, (-999, int(y), 999999, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 78
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[3:9])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Skiz
# ************************************************************************

class Skiz(AbstractTarockGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        h = max(3 * l.YS, 20 * l.YOFFSET)
        self.setSize(l.XM + 12 * l.XS, l.YM + l.YS + h)

        # Create foundations
        x = l.XM + l.XS * 3.5
        y = l.YM
        s.foundations.append(SS_FoundationStack(x, y, self, 0, max_cards=14))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 1, max_cards=14))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 4, max_cards=22))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 2, max_cards=14))
        x = x + l.XS
        s.foundations.append(SS_FoundationStack(x, y, self, 3, max_cards=14))

        # Create reserves
        x = l.XM
        for i in range(3):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        x = x + l.XS * 6
        for i in range(3):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS

        # Create rows
        x = l.XM
        y = l.YM + l.YS * 1.1
        for i in range(12):
            s.rows.append(Skiz_RowStack(x, y, self))
            x = x + l.XS
        self.setRegion(s.rows, (-999, int(y), 999999, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 78
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[3:9])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Fifteen Plus
# ************************************************************************

class FifteenPlus(AbstractTarockGame):
    Hint_Class = CautiousDefaultHint

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        h = max(5 * l.YS, 20 * l.YOFFSET)
        self.setSize(l.XM + 9 * l.XS, l.YM + l.YS + h)

        # Create foundations
        x = self.width - l.XS
        y = l.YM
        s.foundations.append(SS_FoundationStack(x, y, self, 4, max_cards=22))
        y = y + l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_cards=14))
            y = y + l.YS

        # Create rows
        x = l.XM
        y = l.YM
        for j in range(2):
            for i in range(8):
                s.rows.append(Tarock_AC_RowStack(x, y, self, max_move=1, max_accept=1))
                x = x + l.XS
            x = l.XM
            y = y + l.YS * 3
        self.setRegion(s.rows, (-999, -999, l.XM + l.XS * 8, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 78
        for i in range(2):
            self.s.talon.dealRow(flip=0, frames=0)
        for i in range(2):
            self.s.talon.dealRow(rows=self.s.rows[:15], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank))


# ************************************************************************
# * Excuse
# ************************************************************************

class Excuse(AbstractTarockGame):
    Hint_Class = CautiousDefaultHint
    GAME_VERSION = 2

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        h = max(5 * l.YS, 20 * l.YOFFSET)
        self.setSize(l.XM + 9 * l.XS, l.YM + l.YS + h)

        # Create foundations
        x = self.width - l.XS
        y = l.YM
        s.foundations.append(SS_FoundationStack(x, y, self, 4, max_cards=22))
        y = y + l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_cards=14))
            y = y + l.YS

        # Create rows
        x = l.XM
        y = l.YM
        for j in range(2):
            for i in range(8):
                s.rows.append(Excuse_RowStack(x, y, self,
                              max_move=1, max_accept=1, base_rank=NO_RANK))
                x = x + l.XS
            x = l.XM
            y = y + l.YS * 3
        self.setRegion(s.rows, (-999, -999, l.XM + l.XS * 8, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def _shuffleHook(self, cards):
        # move Kings to bottom of each stack (see Baker's Dozen)
        def isKing(c):
            return (c.suit < 4 and c.rank == 13) or (c.suit == 4 and c.rank == 21)
        i, n = 0, len(self.s.rows)
        kings = []
        for c in cards:
            if isKing(c):
                kings.append(i)
            i = i + 1
        for i in kings:
            j = i % n
            while j < i:
                if not isKing(cards[j]):
                    cards[i], cards[j] = cards[j], cards[i]
                    break
                j = j + n
        cards.reverse()
        return cards

    def startGame(self):
        assert len(self.s.talon.cards) == 78
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(rows=self.s.rows[:15], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:15])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank
                or card1.rank - 1 == card2.rank)


# ************************************************************************
# * Grasshopper
# * Double Grasshopper
# ************************************************************************

class Grasshopper(AbstractTarockGame):
    GAME_VERSION = 2
    MAX_ROUNDS = 2

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s

        # Set window size
        decks = self.gameinfo.decks
        self.setSize(2*l.XM + (2 + 5*decks)*l.XS, 3*l.YM + 5*l.YS)
        yoffset = min(l.YOFFSET, max(10, l.YOFFSET / 2))

        # Create talon
        x = l.XM
        y = l.YM
        s.talon = WasteTalonStack(x, y, self, num_deal=1, max_rounds=self.MAX_ROUNDS)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # Create foundations
        x = x + l.XM + l.XS
        for j in range(4):
            for i in range(decks):
                s.foundations.append(SS_FoundationStack(x, y, self, j, max_cards=14))
                x = x + l.XS
        for i in range(decks):
            s.foundations.append(SS_FoundationStack(x, y, self, 4, max_cards=22))
            x = x + l.XS

        # Create reserve
        x = l.XM
        y = l.YM + l.YS + l.TEXT_HEIGHT
        s.reserves.append(OpenStack(x, y, self))
        s.reserves[0].CARD_YOFFSET = (l.YOFFSET, yoffset)[decks == 2]

        # Create rows
        x = x + l.XM + l.XS
        for i in range(decks):
            s.rows.append(TrumpOnly_RowStack(x, y, self, yoffset=yoffset))
            x = x + l.XS
        for i in range(4*decks+1):
            s.rows.append(Tarock_AC_RowStack(x, y, self))
            x = x + l.XS
        self.setRegion(s.rows, (-999, y - l.YS, 999999, 999999))

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        decks = self.gameinfo.decks
        assert len(self.s.talon.cards) == 78 * decks
        self.startDealSample()
        for i in range(14 * decks):
            self.s.talon.dealRow(rows=self.s.reserves, flip=0, frames=4)
        self.s.reserves[0].flipMove()
        self.s.talon.dealRow(rows = self.s.rows[decks:])
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        r = self.s.reserves[0]
        if not stack.cards and stack in self.s.rows:
            if r.cards and stack.acceptsCards(r, r.cards[-1:]):
                r.moveMove(1, stack)
        if r.canFlipCard():
            r.flipMove()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1 == card2.rank
                or card1.rank - 1 == card2.rank)
                and card1.color != card2.color)


class DoubleGrasshopper(Grasshopper):
    pass


# ************************************************************************
# * Ponytail
# ************************************************************************

class Ponytail(Tarock_GameMethods, Braid):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 20 cards are playable - needed for Ponytail_PonytailStack)
        h = max(5*l.YS + l.TEXT_HEIGHT, l.YS+(self.BRAID_CARDS-1)*l.YOFFSET)
        self.setSize(10*l.XS+l.XM, l.YM + h)

        # extra settings
        self.base_card = None

        # create stacks
        s.addattr(braid=None)      # register extra stack variable
        x, y = l.XM, l.YM
        for i in range(2):
            s.rows.append(Ponytail_RowStack(x + 0.5 * l.XS, y, self))
            s.rows.append(Ponytail_RowStack(x + 4.5 * l.XS, y, self))
            s.rows.append(Ponytail_RowStack(x + 5.5 * l.XS, y, self))
            s.rows.append(Ponytail_RowStack(x + 6.5 * l.XS, y, self))
            y = y + 4 * l.YS
        y = l.YM + l.YS
        for i in range(2):
            s.rows.append(Ponytail_ReserveStack(x, y, self))
            s.rows.append(Ponytail_ReserveStack(x + l.XS, y, self))
            s.rows.append(Ponytail_ReserveStack(x, y + l.YS, self))
            s.rows.append(Ponytail_ReserveStack(x + l.XS, y + l.YS, self))
            s.rows.append(Ponytail_ReserveStack(x, y + 2 * l.YS, self))
            s.rows.append(Ponytail_ReserveStack(x + l.XS, y + 2 * l.YS, self))
            x = x + 4 * l.XS
        x = l.XM + 5*l.XS/2
        y = l.YM
        s.braid = Ponytail_PonytailStack(x, y, self, sine=1)
        x = l.XM + 7 * l.XS
        y = l.YM + 2*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "s")
        s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                             x + l.CW / 2, y - l.YM,
                                             anchor="s",
                                             font=self.app.getFont("canvas_default"))
        x = x - l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")
        x = l.XM + 8 * l.XS
        y = l.YM
        for i in range(4):
            s.foundations.append(Ponytail_Foundation(x, y, self, i, mod=14, max_cards=14))
            s.foundations.append(Ponytail_Foundation(x + l.XS, y, self, i, mod=14, max_cards=14))
            y = y + l.YS
        s.foundations.append(Ponytail_Foundation(x, y, self, 4, mod=22, max_cards=22))
        s.foundations.append(Ponytail_Foundation(x + l.XS, y, self, 4, mod=22, max_cards=22))
        # ???
        self.texts.info = MfxCanvasText(self.canvas,
                                        x + l.CW + l.XM / 2, y + l.YS,
                                        anchor="n",
                                        font=self.app.getFont("canvas_default"))

        # define stack-groups
        self.sg.openstacks = s.foundations + s.rows
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.dropstacks = [s.braid] + s.rows + [s.waste]


# ************************************************************************
# * Cavalier
# * Five Aces
# * Wicked
# * Nasty
# ************************************************************************

class Cavalier(AbstractTarockGame):
    Layout_Method = Layout.bakersDozenLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = Cavalier_RowStack

    #
    # Game layout
    #

    def createGame(self, **layout):
        # Create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=18, playcards=19)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create foundations
        for r in l.s.foundations:
            n = 14 + 8 * (r.suit == 4)
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, r.suit,
                                 mod=n, max_cards=n))

        # Create rows
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)

        # Define stack groups
        l.defaultAll()


    #
    # Game over rides
    #

    def startGame(self, flip=(0, 1, 0), foundations=0):
        assert len(self.s.talon.cards) == 78
        for f in flip:
            self.s.talon.dealRow(flip=f, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        if foundations:
            self.s.talon.dealRow(rows=self.s.rows[0:1])
            self.s.talon.dealRow(rows=self.s.foundations)
        else:
            self.s.talon.dealRow(rows=self.s.rows[:6])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1 == card2.rank
                or card1.rank - 1 == card2.rank)
                and ((card1.suit == 4 or card2.suit == 4)
                or card1.color != card2.color))


class FiveAces(Cavalier):
    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        Cavalier.startGame(self, foundations=1)


class Wicked(FiveAces):
    Talon_Class = StackWrapper(Wicked_Talon, max_rounds=-1)
    RowStack_Class = StackWrapper(SS_RowStack, max_move=1, max_accept=1, base_rank=NO_RANK)
    Hint_Class = CautiousDefaultHint

    def startGame(self):
        Cavalier.startGame(self, flip=(1, 1, 1), foundations=1)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1 == card2.rank
                or card1.rank - 1 == card2.rank)
                and card1.suit == card2.suit)


class Nasty(Wicked):
    RowStack_Class = StackWrapper(Nasty_RowStack, max_move=1, max_accept=1, base_rank=ANY_RANK)


# ************************************************************************
# * register the games
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level):
    game_type = game_type | GI.GT_TAROCK | GI.GT_CONTRIB | GI.GT_ORIGINAL
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  ranks=range(14), trumps=range(22))
    registerGame(gi)
    return gi

r(157, WheelOfFortune, "Wheel of Fortune", GI.GT_TAROCK, 1, 0, GI.SL_BALANCED)
r(158, ImperialTrumps, "Imperial Trumps", GI.GT_TAROCK, 1, -1, GI.SL_BALANCED)
r(159, Pagat, "Pagat", GI.GT_TAROCK | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(160, Skiz, "Skiz", GI.GT_TAROCK | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(161, FifteenPlus, "Fifteen plus", GI.GT_TAROCK, 1, 0, GI.SL_BALANCED)
r(162, Excuse, "Excuse", GI.GT_TAROCK | GI.GT_OPEN, 1, 0, GI.SL_BALANCED)
r(163, Grasshopper, "Grasshopper", GI.GT_TAROCK, 1, 1, GI.SL_MOSTLY_SKILL)
r(164, DoubleGrasshopper, "Double Grasshopper", GI.GT_TAROCK, 2, 1, GI.SL_MOSTLY_SKILL)
r(179, Ponytail, "Ponytail", GI.GT_TAROCK, 2, 2, GI.SL_MOSTLY_SKILL)
r(202, Cavalier, "Cavalier", GI.GT_TAROCK, 1, 0, GI.SL_MOSTLY_SKILL)
r(203, FiveAces, "Five Aces", GI.GT_TAROCK, 1, 0, GI.SL_MOSTLY_SKILL)
r(204, Wicked, "Wicked", GI.GT_TAROCK | GI.GT_OPEN, 1, -1, GI.SL_BALANCED)
r(205, Nasty, "Nasty", GI.GT_TAROCK | GI.GT_OPEN, 1, -1, GI.SL_BALANCED)

del r

