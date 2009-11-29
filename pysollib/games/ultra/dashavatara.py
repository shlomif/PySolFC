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
import sys, math, time

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
#  * Dashavatara Foundation Stacks
#  ***********************************************************************/

class Dashavatara_FoundationStack(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_move=0, max_cards=12)
        SS_FoundationStack.__init__(self, x, y, game, suit, **cap)

    def updateText(self):
        AbstractFoundationStack.updateText(self)
        self.game.updateText()


class Journey_Foundation(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=12, dir=0, base_rank=NO_RANK, max_move=0)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return 1
        stack_dir = self.game.getFoundationDir()
        if stack_dir == 0:
            card_dir = (cards[0].rank - self.cards[-1].rank) % self.cap.mod
            return card_dir in (1, 11)
        else:
            return (self.cards[-1].rank + stack_dir) % self.cap.mod == cards[0].rank



class AppachansWaterfall_Foundation(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, base_suit=0, mod=12, max_cards=120, max_move=0)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        if not (from_stack in self.game.s.rows and
                 AbstractFoundationStack.acceptsCards(self, from_stack, cards)):
            return 0
        pile, rank, suit = from_stack.getPile(), 0, 0
        if self.cards:
            rank = (self.cards[-1].rank + 1) % 12
            suit = self.cards[-1].suit + (rank == 0)
        if (not pile or len(pile) <= 11 - rank
                or not isSameSuitSequence(pile[-(12 - rank):])):
            return 0
        return cards[0].suit == suit and cards[0].rank == rank



# ************************************************************************
#  * Dashavatara Row Stacks
#  ***********************************************************************/

class Dashavatara_OpenStack(OpenStack):

    def __init__(self, x, y, game, yoffset, **cap):
        kwdefault(cap, max_move=UNLIMITED_MOVES, max_cards=UNLIMITED_CARDS,
                  max_accept=UNLIMITED_ACCEPTS, base_rank=0, dir=-1)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def currentForce(self, card):
        force = self._getForce(card)
        hour = time.localtime(time.time())[3]
        if not (hour >= 7 and hour <= 19):
            force = not force
        return force

    def _getForce(self, card):
        return int(card.suit >= 5)

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
            if not ((c1.suit + c2.suit) % 2
                    and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isAlternateForceSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        f1 = self._getForce(c1)
        for c2 in cards[1:]:
            f2 = self._getForce(c2)
            if f1 == f2 or c1.rank + dir != c2.rank:
                return 0
            c1 = c2
            f1 = f2
        return 1

    def isSuitSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not (c1.suit == c2.suit
                    and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1


class Dashavatara_AC_RowStack(Dashavatara_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isAlternateColorSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isAlternateColorSequence([stackcards[-1], cards[0]])


class Dashavatara_AF_RowStack(Dashavatara_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isAlternateForceSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isAlternateForceSequence([stackcards[-1], cards[0]])


class Dashavatara_RK_RowStack(Dashavatara_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isRankSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isRankSequence([stackcards[-1], cards[0]])


class Dashavatara_SS_RowStack(Dashavatara_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isSuitSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isSuitSequence([stackcards[-1], cards[0]])


class Circles_RowStack(SS_RowStack):

    def __init__(self, x, y, game, base_rank):
        SS_RowStack.__init__(self, x, y, game, base_rank=base_rank,
                                max_accept=1, max_move=1)
        self.CARD_YOFFSET = 1


class Journey_BraidStack(OpenStack):

    def __init__(self, x, y, game, xoffset, yoffset):
        OpenStack.__init__(self, x, y, game)
        CW = self.game.app.images.CARDW
        self.CARD_YOFFSET = int(self.game.app.images.CARD_YOFFSET * yoffset)
        # use a sine wave for the x offsets
        self.CARD_XOFFSET = []
        j = 1
        for i in range(30):
            self.CARD_XOFFSET.append(int(math.sin(j) * xoffset))
            j = j + .9


class Journey_StrongStack(ReserveStack):

    def fillStack(self):
        if not self.cards:
            if self.game.s.braidstrong.cards:
                self.game.moveMove(1, self.game.s.braidstrong, self)
            elif self.game.s.braidweak.cards:
                self.game.moveMove(1, self.game.s.braidweak, self)

    def getBottomImage(self):
        return self.game.app.images.getBraidBottom()


class Journey_WeakStack(ReserveStack):

    def fillStack(self):
        if not self.cards:
            if self.game.s.braidweak.cards:
                self.game.moveMove(1, self.game.s.braidweak, self)
            elif self.game.s.braidstrong.cards:
                self.game.moveMove(1, self.game.s.braidstrong, self)

    def getBottomImage(self):
        return self.game.app.images.getBraidBottom()


class Journey_ReserveStack(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if (from_stack is self.game.s.braidstrong or
                from_stack is self.game.s.braidweak or
                from_stack in self.game.s.rows):
            return 0
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()


class AppachansWaterfall_RowStack(RK_RowStack):

    def canDropCards(self, stacks):
        game, pile, stack, rank = self.game, self.getPile(), stacks[0], 0
        if stack.cards:
            rank = (stack.cards[-1].rank + 1) % 12
        if (not pile or len(pile) <= 11 - rank
                or not isSameSuitSequence(pile[-(12 - rank):])
                or not stack.acceptsCards(self, pile[-1:])):
            return (None, 0)
        return (stack, 1)



# ************************************************************************
# * Dashavatara Game Stacks
# ************************************************************************

class Dashavatara_TableauStack(Dashavatara_OpenStack):

    def __init__(self, x, y, game, base_rank, yoffset, **cap):
        kwdefault(cap, dir=3, max_move=99, max_cards=4, max_accept=1, base_rank=base_rank)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        # check that the base card is correct
        if self.cards and self.cards[0].rank != self.cap.base_rank:
            return 0
        if not self.cards:
            return cards[0].rank == self.cap.base_rank
        return (self.cards[-1].suit == cards[0].suit and
                self.cards[-1].rank + self.cap.dir == cards[0].rank)

    def getBottomImage(self):
        return self.game.app.images.getLetter(self.cap.base_rank)


class Dashavatara_ReserveStack(ReserveStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_cards=1, max_accept=1, base_rank=ANY_RANK)
        OpenStack.__init__(self, x, y, game, **cap)

    def acceptsCards(self, from_stack, cards):
        return (ReserveStack.acceptsCards(self, from_stack, cards)
                and self.game.s.talon.cards)


class Dashavatara_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        # check
        return not (self.cards or self.game.s.talon.cards)

    def canMoveCards(self, cards):
        return 1

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()


# ************************************************************************
#  *
#  ***********************************************************************/

class AbstractDashavataraGame(Game):

    SUITS = (_("Fish"), _("Tortoise"), _("Boar"), _("Lion"), _("Dwarf"),
             _("Axe"), _("Arrow"), _("Plow"), _("Lotus"), _("Horse"))
    RANKS = (_("Ace"), "2", "3", "4", "5", "6", "7", "8", "9", "10",
             _("Pradhan"), _("Raja"))
    COLORS = (_("Black"), _("Red"), _("Yellow"), _("Green"), _("Brown"),
              _("Orange"), _("Grey"), _("White"), _("Olive"), _("Crimson"))
    FORCE = (_("Strong"), _("Weak"))

    def updateText(self):
        pass

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit
                and (card1.rank + 1 == card2.rank
                or card1.rank - 1 == card2.rank))


class Journey_Hint(DefaultHint):
    # FIXME: demo is not too clever in this game
    pass


# ************************************************************************
#  * Dashavatara Circles
#  ***********************************************************************/

class DashavataraCircles(AbstractDashavataraGame):
    Hint_Class = CautiousDefaultHint

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        w, h = l.XM + l.XS * 9, l.YM + l.YS * 7
        self.setSize(w, h)

        # Create row stacks
        x = w / 2 - l.CW / 2
        y = h / 2 - l.YS / 2
        x0 = (-.7, .3, .7, -.3,
            -1.7, -1.5, -.6, .6, 1.5, 1.7, 1.5, .6, -.6, -1.5,
            -2.7, -2.5, -1.9, -1, 0, 1, 1.9, 2.5, 2.7, 2.5, 1.9, 1, 0, -1, -1.9, -2.5)
        y0 = (-.3, -.45, .3, .45,
            0, -.8, -1.25, -1.25, -.8, 0, .8, 1.25, 1.25, .8,
            0, -.9, -1.6, -2, -2.2, -2, -1.6, -.9, 0, .9, 1.6, 2, 2.2, 2, 1.6, .9)
        for i in range(30):
            # FIXME:
            _x, _y = x+l.XS*x0[i], y+l.YS*y0[i]+l.YM*y0[i]*2
            if _x < 0: _x = 0
            if _y < 0: _y = 0
            s.rows.append(Circles_RowStack(_x, _y, self, base_rank = ANY_RANK))

        # Create reserve stacks
        s.reserves.append(ReserveStack(l.XM, h - l.YS, self))
        s.reserves.append(ReserveStack(w - l.XS, h - l.YS, self))

        # Create foundations
        x, y = l.XM, l.YM
        for j in range(2):
            for i in range(5):
                s.foundations.append(SS_FoundationStack(x, y, self, i + j * 5, mod=12,
                                             max_move=0, max_cards=12))
                y = y + l.YS
            x, y = w - l.XS, l.YM
##         from pprint import pprint
##         pprint(s.rows)
##         print (l.XM + l.XS, 0, w - l.XS - l.XM, 999999)
        self.setRegion(s.rows, (l.XM + l.XS, 0, w - l.XS - l.XM, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(l.XM + l.XS, l.YM, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 120
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.rows, flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows, flip=1, frames=3)
        self.s.talon.dealCards()



# ************************************************************************
#  * Ten Avatars
#  ***********************************************************************/

class TenAvatars(AbstractDashavataraGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(l.XM * 3 + l.XS * 11, l.YM + l.YS * 6)

        # Create row stacks
        x = l.XM
        y = l.YM
        for i in range(10):
            s.rows.append(RK_RowStack(x, y, self, base_rank=11,
                                        max_move=12, max_cards=99))
            x = x + l.XS

        # Create reserve stacks
        x = self.width - l.XS
        y = l.YM
        for i in range(6):
            s.reserves.append(ReserveStack(x, y, self))
            y = y + l.YS
        y = y - l.YS
        for i in range(6):
            x = x - l.XS
            s.reserves.append(ReserveStack(x, y, self))

        self.setRegion(s.rows, (0, 0, l.XM + l.XS * 10, l.YS * 5))

        # Create talon
        s.talon = DealRowTalonStack(l.XM, self.height - l.YS, self)
        l.createText(s.talon, "n")

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 120
        for i in range(4):
            self.s.talon.dealRow(flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealCards()

    def isGameWon(self):
        if len(self.s.talon.cards):
            return 0
        for s in self.s.rows:
            if len(s.cards) != 12 or not isSameSuitSequence(s.cards):
                return 0
        return 1



# ************************************************************************
#  * Balarama
#  ***********************************************************************/

class Balarama(AbstractDashavataraGame):
    Layout_Method = Layout.ghulamLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = Dashavatara_AC_RowStack
    BASE_RANK = ANY_RANK

    #
    # Game layout
    #

    def createGame(self, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=16, reserves=4, texts=0)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=12, max_cards=12))

        # Create reserve stacks
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self, ))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self, l.YOFFSET,
                                suit=ANY_SUIT, base_rank=self.BASE_RANK, max_cards=12))

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 120
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.rows, flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows, flip=1, frames=3)
        self.s.talon.dealRow(rows=self.s.rows[:8], flip=1, frames=3)
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color % 2 != card2.color % 2 and
                (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank))



# ************************************************************************
#  * Hayagriva
#  ***********************************************************************/

class Hayagriva(Balarama):
    Layout_Method = Layout.ghulamLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = Dashavatara_RK_RowStack
    BASE_RANK = 11

    #
    # Game layout
    #

    def createGame(self, **layout):
        Balarama.createGame(self)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank)



# ************************************************************************
#  * Shanka
#  ***********************************************************************/

class Shanka(Balarama):
    Layout_Method = Layout.ghulamLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = Dashavatara_RK_RowStack
    BASE_RANK = 11

    #
    # Game layout
    #

    def createGame(self, **layout):
        Balarama.createGame(self, reserves=0)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if stack1 in self.s.foundations:
            return (card1.suit == card2.suit and
                    (card1.rank + 1 == card2.rank
                    or card2.rank + 1 == card1.rank))
        return (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank)



# ************************************************************************
#  * Surukh
#  ***********************************************************************/

class Surukh(Balarama):
    Layout_Method = Layout.ghulamLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = Dashavatara_AF_RowStack
    BASE_RANK = ANY_RANK

    #
    # Game layout
    #

    def createGame(self, **layout):
        Balarama.createGame(self, reserves=4)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if card1.suit <= 4:
            force0 = 0
        else:
            force0 = 1
        if card2.suit <= 4:
            force1 = 0
        else:
            force1 = 1
        return (force0 != force1
                and (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank))



# ************************************************************************
#  * Matsya
#  ***********************************************************************/

class Matsya(AbstractDashavataraGame):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = RK_RowStack
    BASE_RANK = 11

    #
    # Game layout
    #

    def createGame(self, max_rounds=1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, waste=1)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                            max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=12, max_cards=12, max_move=0))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                suit=ANY_SUIT, base_rank=self.BASE_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 120
        for i in range(10):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank)



# ************************************************************************
#  * Kurma
#  ***********************************************************************/

class Kurma(Matsya):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SS_RowStack
    BASE_RANK = ANY_RANK

    #
    # Game layout
    #

    def createGame(self, **layout):
        Matsya.createGame(self, max_rounds=-1)



# ************************************************************************
#  * Varaha
#  ***********************************************************************/

class Varaha(Matsya):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SS_RowStack
    BASE_RANK = ANY_RANK

    #
    # Game layout
    #

    def createGame(self, **layout):
        Matsya.createGame(self, max_rounds=-1, num_deal=3)



# ************************************************************************
#  * Narasimha
#  ***********************************************************************/

class Narasimha(Matsya):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack
    BASE_RANK = 11

    #
    # Game layout
    #

    def createGame(self, **layout):
        Matsya.createGame(self, max_rounds=1, num_deal=1)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color % 2 != card2.color % 2
                and (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank))



# ************************************************************************
#  * Vamana
#  ***********************************************************************/

class Vamana(Matsya):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack
    BASE_RANK = 11

    #
    # Game layout
    #

    def createGame(self, **layout):
        Matsya.createGame(self, max_rounds=-1, num_deal=3)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color % 2 != card2.color % 2
                and (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank))



# ************************************************************************
#  * Parashurama
#  ***********************************************************************/

class Parashurama(Matsya):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = RK_RowStack
    BASE_RANK = 11

    #
    # Game layout
    #

    def createGame(self, **layout):
        Matsya.createGame(self, max_rounds=2, num_deal=3)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank)



# ************************************************************************
# * Journey to Cuddapah
# ************************************************************************

class Journey(AbstractDashavataraGame):
    Hint_Class = Journey_Hint

    BRAID_CARDS = 15
    BRAID_OFFSET = 1

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 20 cards are playable - needed for Braid_BraidStack)
        decks = self.gameinfo.decks
        h = max(5 * l.YS + 35, 2*l.YM + 2*l.YS + (self.BRAID_CARDS - 1) * l.YOFFSET*self.BRAID_OFFSET)
        self.setSize(l.XM + l.XS * (7 + decks * 2), l.YM + h)

        # extra settings
        self.base_card = None

        # Create foundations, rows, reserves
        s.addattr(braidstrong=None)      # register extra stack variable
        s.addattr(braidweak=None)      # register extra stack variable
        x, y = l.XM, l.YM
        for j in range(5):
            for i in range(decks):
                s.foundations.append(Journey_Foundation(x + l.XS * i, y, self,
                                                j, mod=12, max_cards=12))
            s.rows.append(Journey_StrongStack(x + l.XS * decks, y, self))
            s.rows.append(Journey_ReserveStack(x + l.XS * (1 + decks), y, self))
            y = y + l.YS
        x, y = x + l.XS * (5 + decks), l.YM
        for j in range(5):
            s.rows.append(Journey_ReserveStack(x, y, self))
            s.rows.append(Journey_WeakStack(x + l.XS, y, self))
            for i in range(decks, 0, -1):
                s.foundations.append(Journey_Foundation(x + l.XS * (1 + i), y, self,
                                                j + 5, mod=12, max_cards=12))
            y = y + l.YS
        self.texts.info = MfxCanvasText(self.canvas,
                                        self.width / 2, h - l.YM / 2,
                                        anchor="center",
                                        font = self.app.getFont("canvas_default"))

        # Create braids
        x, y = l.XM + l.XS * 2.15 + l.XS * decks, l.YM
        s.braidstrong = Journey_BraidStack(x, y, self, xoffset=12, yoffset=self.BRAID_OFFSET)
        x = x + l.XS * 1.7
        s.braidweak = Journey_BraidStack(x, y, self, xoffset=-12, yoffset=self.BRAID_OFFSET)

        # Create talon
        x, y = l.XM + l.XS * 2 + l.XS * decks, h - l.YS - l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "s")
        s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                             self.width / 2, h - l.YM * 2.5,
                                             anchor="center",
                                             font=self.app.getFont("canvas_default"))
        x = x + l.XS * 2
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # define stack-groups
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.openstacks = s.foundations + s.rows
        self.sg.dropstacks = [s.braidstrong] + [s.braidweak] + s.rows + [s.waste]


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.base_card = None
        self.updateText()
        for i in range(self.BRAID_CARDS):
            self.s.talon.dealRow(rows = [self.s.braidstrong])
        for i in range(self.BRAID_CARDS):
            self.s.talon.dealRow(rows = [self.s.braidweak])
        self.s.talon.dealRow()
        # deal base_card to foundations, update cap.base_rank
        self.base_card = self.s.talon.getCard()
        to_stack = self.s.foundations[self.base_card.suit * self.gameinfo.decks]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack)
        self.updateText()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        # deal first card to WasteStack
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 12 == card2.rank
                or (card2.rank + 1) % 12 == card1.rank))

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
            dir = self.getFoundationDir() % 12
            if dir == 1:
                t = t + _(" Ascending")
            elif dir == 11:
                t = t + _(" Descending")
        self.texts.info.config(text = t)



# ************************************************************************
# * Long Journey to Cuddapah
# ************************************************************************

class LongJourney(Journey):

    BRAID_CARDS = 20
    BRAID_OFFSET = .7



# ************************************************************************
#  * Appachan's Waterfall
#  ***********************************************************************/

class AppachansWaterfall(AbstractDashavataraGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        w, h = l.XM + l.XS * 10, l.YM + l.YS * 6
        self.setSize(w, h)

        # Create row stacks
        x, y = l.XM, l.YM
        for i in range(10):
            s.rows.append(AppachansWaterfall_RowStack(x, y, self, base_rank=ANY_RANK,
                                                        max_move=12, max_cards=99))
            x = x + l.XS
        self.setRegion(s.rows, (-999, -999, 999999, l.YM + l.YS * 5))

        # Create foundation
        x, y = w / 2 - l.CW / 2, h - l.YS
        s.foundations.append(AppachansWaterfall_Foundation(x, y, self, -1))

        # Create reserves
        s.reserves.append(ReserveStack(x - l.XS * 2, y, self))
        s.reserves.append(ReserveStack(x + l.XS * 2, y, self))

        # Create talon
        s.talon = DealRowTalonStack(l.XM, y, self)
        l.createText(s.talon, "n")

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 120
        for i in range(4):
            self.s.talon.dealRow(flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealCards()

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 120



# ************************************************************************
# * Hiranyaksha
# ************************************************************************

class Hiranyaksha(AbstractDashavataraGame):
    RowStack_Class = StackWrapper(Dashavatara_RK_RowStack, base_rank=NO_RANK)

    #
    # game layout
    #

    def createGame(self, rows=11, reserves=10):
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
        for i in range(96 * self.gameinfo.decks - playcards):
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
            stack = self.RowStack_Class(x, y, self, yoffset=l.YOFFSET)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = yoffset
            s.rows.append(stack)
            x = x + l.XS
        x, y = l.XM + maxrows * l.XS, l.YM
        for i in range(2):
            for suit in range(5):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=suit + (5 * i)))
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
            if self.s.talon.cards[-1].rank == 11:
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
# * Dashavatara Hint
# ************************************************************************

class Dashavatara_Hint(AbstractHint):
    def computeHints(self):
        game = self.game

        # 2)See if we can move a card to the tableaux
        if not self.hints:
            for r in game.sg.dropstacks:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                if r in game.s.tableaux:
                    rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                    if rr.acceptsCards(None, pile):
                        # do not move a card that is already in correct place
                        continue
                    base_score = 80000 + (4 - r.cap.base_suit)
                else:
                    base_score = 80000
                # find a stack that would accept this card
                for t in game.s.tableaux:
                    if t is not r and t.acceptsCards(r, pile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 3)See if we can move a card from the tableaux
        #    to a row stack. This can only happen if there are
        #    no more cards to deal.
        if not self.hints:
            for r in game.s.tableaux:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                if rr.acceptsCards(None, pile):
                    # do not move a card that is already in correct place
                    continue
                # find a stack that would accept this card
                for t in game.s.rows:
                    if t is not r and t.acceptsCards(r, pile):
                        score = 70000 + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 4)See if we can move a card within the row stacks
        if not self.hints:
            for r in game.s.rows:
                pile = r.getPile()
                if not pile or len(pile) != 1 or len(pile) == len(r.cards):
                    continue
                base_score = 60000
                # find a stack that would accept this card
                for t in game.s.rows:
                    if t is not r and t.acceptsCards(r, pile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 5)See if we can deal cards
        if self.level >= 2:
            if game.canDealCards():
                self.addHint(self.SCORE_DEAL, 0, game.s.talon, None)


# ************************************************************************
# * Dashavatara
# ************************************************************************

class Dashavatara(Game):
    Hint_Class = Dashavatara_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        TABLEAU_YOFFSET = min(9, max(3, l.YOFFSET / 3))

        # set window
        th = l.YS + 3 * TABLEAU_YOFFSET
        # (set piles so that at least 2/3 of a card is visible with 10 cards)
        h = 10 * l.YOFFSET + l.CH * 2/3
        self.setSize(11 * l.XS + l.XM * 2, l.YM + 3 * th + l.YM + h)

        # create stacks
        s.addattr(tableaux=[])     # register extra stack variable
        x = l.XM + 8 * l.XS + l.XS / 2
        y = l.YM
        for i in range(3, 0, -1):
            x = l.XM
            for j in range(10):
                s.tableaux.append(Dashavatara_TableauStack(x, y, self, i - 1, TABLEAU_YOFFSET))
                x = x + l.XS
            x = x + l.XM
            s.reserves.append(Dashavatara_ReserveStack(x, y, self))
            y = y + th
        x, y = l.XM, y + l.YM
        for i in range(10):
            s.rows.append(Dashavatara_RowStack(x, y, self, max_accept=1))
            x = x + l.XS
        x = self.width - l.XS
        y = self.height - l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, "sw")

        # define stack-groups
        self.sg.openstacks = s.tableaux + s.rows + s.reserves
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.tableaux + s.rows

    #
    # game overrides
    #

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.tableaux, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        for stack in self.s.tableaux:
            if len(stack.cards) != 4:
                return 0
        return 1

    def fillStack(self, stack):
        if self.s.talon.cards:
            if stack in self.s.rows and len(stack.cards) == 0:
                self.s.talon.dealRow(rows=[stack])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 3 == card2.rank or card2.rank + 3 == card1.rank))

    def getHighlightPilesStacks(self):
        return ()


# ************************************************************************
#  *
#  ***********************************************************************/

def r(id, gameclass, name, game_type, decks, redeals, skill_level):
    game_type = game_type | GI.GT_DASHAVATARA_GANJIFA
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  suits=range(10), ranks=range(12))
    registerGame(gi)
    return gi

r(15406, Matsya, "Matsya", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_BALANCED)
r(15407, Kurma, "Kurma", GI.GT_DASHAVATARA_GANJIFA, 1, -1, GI.SL_BALANCED)
r(15408, Varaha, "Varaha", GI.GT_DASHAVATARA_GANJIFA, 1, -1, GI.SL_BALANCED)
r(15409, Narasimha, "Narasimha", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_BALANCED)
r(15410, Vamana, "Vamana", GI.GT_DASHAVATARA_GANJIFA, 1, -1, GI.SL_BALANCED)
r(15411, Parashurama, "Parashurama", GI.GT_DASHAVATARA_GANJIFA, 1, 1, GI.SL_BALANCED)
r(15412, TenAvatars, "Ten Avatars", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(15413, DashavataraCircles, "Dashavatara Circles", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(15414, Balarama, "Balarama", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(15415, Hayagriva, "Hayagriva", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(15416, Shanka, "Shanka", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(15417, Journey, "Journey to Cuddapah", GI.GT_DASHAVATARA_GANJIFA, 1, 2, GI.SL_BALANCED)
r(15418, LongJourney, "Long Journey to Cuddapah", GI.GT_DASHAVATARA_GANJIFA, 2, 2, GI.SL_BALANCED)
r(15419, Surukh, "Surukh", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_BALANCED)
r(15420, AppachansWaterfall, "Appachan's Waterfall", GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(15421, Hiranyaksha, 'Hiranyaksha', GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(15422, Dashavatara, 'Dashavatara', GI.GT_DASHAVATARA_GANJIFA, 1, 0, GI.SL_BALANCED)

del r
