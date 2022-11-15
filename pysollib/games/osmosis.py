#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
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
# ---------------------------------------------------------------------------##

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.mygettext import _
from pysollib.stack import \
        AbstractFoundationStack, \
        BasicRowStack, \
        FullStackWrapper, \
        InitialDealTalonStack, \
        OpenStack, \
        ReserveStack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ANY_RANK, ANY_SUIT, UNLIMITED_REDEALS

# ************************************************************************
# * Osmium
# * Osmium II
# ************************************************************************


class Osmium_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # search foundation with max number of cards
        assert len(cards) == 1
        max_s, max_cards = None, -1
        for s in self.game.s.foundations:
            if len(s.cards) > max_cards:
                max_s, max_cards = s, len(s.cards)
        # if we have less cards, then rank must match the card in this
        # foundation
        if len(self.cards) < max_cards:
            if cards[0].rank != max_s.cards[len(self.cards)].rank:
                return False
        #
        return True

    def getHelp(self):
        return _('Foundation. Build in suit regardless of rank.')


class Osmium(Game):
    Foundation_Class = Osmium_Foundation

    #
    # game layout
    #

    def createGame(self, max_rounds=-1, num_deal=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 3*l.XM+3*l.XS+(4+13)*l.XOFFSET, l.YM+4*l.YS
        self.setSize(w, h)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(4):
            stack = BasicRowStack(x, y, self, max_move=1, max_accept=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.rows.append(stack)
            y = y + l.YS
        x, y, = 2*l.XM+l.XS+4*l.XOFFSET, l.YM
        for i in range(4):
            stack = self.Foundation_Class(x, y, self, suit=i,
                                          base_rank=ANY_RANK, max_move=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.foundations.append(stack)
            y = y + l.YS
        x, y, = self.width - l.XS, l.YM + l.YS
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        l.createText(s.talon, "sw")
        y = y + l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "sw")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self, flip=0):
        # deal first card to foundation
        base_card = self.s.talon.getCard()
        n = base_card.suit * self.gameinfo.decks
        to_stack = self.s.foundations[n]
        self.startDealSample()
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack)
        # deal cards
        for i in range(3):
            self.s.talon.dealRow(flip=flip)
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


class OsmiumII(Osmium):
    def startGame(self):
        Osmium.startGame(self, flip=1)


# ************************************************************************
# * Osmosis
# * Peek
# ************************************************************************

class Osmosis_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        assert len(cards) == 1
        indx = list(self.game.s.foundations).index(self)
        c0 = cards[0]
        below_found = self.game.s.foundations[indx-1]
        if indx == 0:
            if not self.cards:
                return True
            return c0.suit == self.cards[0].suit
        if not below_found.cards:
            return False
        if not self.cards:
            return c0.rank == below_found.cards[0].rank
        if c0.suit != self.cards[0].suit:
            return False
        for c1 in below_found.cards:
            if c0.rank == c1.rank:
                return True
        return False

    def getHelp(self):
        return _('Foundation. Build in suit regardless of rank.')


class Osmosis(Osmium):
    Foundation_Class = FullStackWrapper(
        Osmosis_Foundation, base_rank=ANY_RANK, suit=ANY_SUIT, max_move=0)

    def createGame(self, max_rounds=-1, num_deal=3):
        Osmium.createGame(self, num_deal=3)

    def startGame(self, flip=0):
        self.startDealSample()
        # deal cards
        for i in range(3):
            self.s.talon.dealRow(flip=flip)
        self.s.talon.dealRow()
        # deal one card to foundation
        self.s.talon.dealRow(rows=self.s.foundations[:1])
        # deal cards to WasteStack
        self.s.talon.dealCards()


class Peek(Osmosis):
    def startGame(self):
        Osmosis.startGame(self, flip=1)


# ************************************************************************
# * Open Osmium
# * Open Peek
# ************************************************************************

class OpenOsmium(Game):
    Foundation_Class = Osmium_Foundation
    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 10 * l.XM + 10 * l.XS + (5 + 13) * l.XOFFSET, l.YM + 4 * l.YS
        self.setSize(w, h)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(4):
            stack = BasicRowStack(x, y, self, max_move=1, max_accept=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.rows.append(stack)
            y += l.YS
        x, y, = 2*l.XM+l.XS+5*l.XOFFSET, l.YM
        for i in range(4):
            stack = self.Foundation_Class(
                x, y, self, suit=i, base_rank=ANY_RANK, max_move=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.foundations.append(stack)
            y += l.YS
        x += l.XS
        x2 = x + (13 * l.XOFFSET)
        for i in range(4):
            y = l.YM + (l.YS * i)
            x = x2
            for j in range(8):
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
                x += l.XS
            y += l.YS

        x, y = w - l.XS, l.YM + (3 * l.YS)
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self._startDealNumRows(5)
        self.s.talon.dealRow(rows=self.s.reserves)


class OpenPeek(OpenOsmium):
    Foundation_Class = FullStackWrapper(
        Osmosis_Foundation, base_rank=ANY_RANK, suit=ANY_SUIT, max_move=0)


# ************************************************************************
# * Genesis
# ************************************************************************

class Genesis(Game):

    def createGame(self, rows=13, reserves=False):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM + rows * l.XS, l.YM + (3 * l.YS) + (15 * l.YOFFSET)
        self.setSize(w, h)

        # create stacks
        x, y, = l.XM+(rows-4)*l.XS//2, l.YM
        for i in range(4):
            stack = Osmosis_Foundation(
                x, y, self, i, base_rank=ANY_RANK, max_move=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.foundations.append(stack)
            x += l.XS

        x, y, = l.XM, h-2*l.YS-3*l.YOFFSET
        for i in range(rows):
            s.rows.append(BasicRowStack(x, y, self))
            x += l.XS

        x, y, = l.XM, h-l.YS-3*l.YOFFSET
        for i in range(rows):
            s.rows.append(BasicRowStack(x, y, self))
            x += l.XS

        if reserves:
            s.reserves.append(ReserveStack(l.XM, l.YM, self))
            s.reserves.append(ReserveStack(w-l.XS, l.YM, self))

        s.talon = InitialDealTalonStack(l.XM, l.YM, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.rows[13:], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:13])


class GenesisPlus(Genesis):
    def createGame(self):
        Genesis.createGame(self, reserves=True)


# ************************************************************************
# * Bridesmaids
# ************************************************************************

class Bridesmaids(Game):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+3*l.XS+12*l.XOFFSET, l.YM+4*l.YS
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=UNLIMITED_REDEALS,
                                  num_deal=3)
        l.createText(s.talon, 'se')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        x, y = l.XM+2*l.XS, l.YM
        for i in range(4):
            stack = Osmosis_Foundation(x, y, self, suit=ANY_SUIT,
                                       base_rank=ANY_RANK, max_move=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.foundations.append(stack)
            y += l.YS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self, flip=0):
        # deal first card to foundation
        self.s.talon.getCard()
        to_stack = self.s.foundations[0]
        self.startDealSample()
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack)
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Dimensions
# ************************************************************************

class Dimensions_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return True
        return cards[0].rank == self.cards[-1].rank or \
            cards[0].suit == self.cards[-1].suit


class Dimensions(Game):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM + 3 * l.XS + 24 * l.XOFFSET, l.YM + 3 * l.YS
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'se')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        x, y = l.XM+2*l.XS, l.YM
        for i in range(3):
            stack = Dimensions_Foundation(x, y, self, suit=ANY_SUIT,
                                          base_rank=ANY_RANK, max_move=0,
                                          max_cards=52)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.foundations.append(stack)
            y += l.YS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self, flip=0):
        self.s.talon.getCard()
        self.startDealSample()
        self.flipMove(self.s.talon)
        self.s.talon.dealCards()          # deal first card to WasteStack


# register the game
registerGame(GameInfo(59, Osmium, "Osmium",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(60, OsmiumII, "Osmium II",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(298, OpenOsmium, "Open Osmium",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(370, Genesis, "Genesis",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(371, GenesisPlus, "Genesis +",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(409, Bridesmaids, "Bridesmaids",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(715, Osmosis, "Osmosis",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_MOSTLY_LUCK,
                      altnames=("Treasure Trove",)))
registerGame(GameInfo(716, Peek, "Peek",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(856, OpenPeek, "Open Peek",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(864, Dimensions, "Dimensions",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
