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

__all__ = [
    'AbstractFlowerGame',
    'Queue_Hint',
    'Flower_FoundationStack',
    'Hanafuda_SS_FoundationStack',
    'FlowerClock_Foundation',
    'Gaji_Foundation',
    'Pagoda_Foundation',
    'MatsuKiri_Foundation',
    'GreatWall_FoundationStack',
    'FourWinds_Foundation',
    'Queue_Foundation',
    'Flower_OpenStack',
    'Hanafuda_SequenceStack',
    'Oonsoo_SequenceStack',
    'FlowerClock_RowStack',
    'Gaji_RowStack',
    'Matsukiri_RowStack',
    'Samuri_RowStack',
    'GreatWall_RowStack',
    'FourWinds_RowStack',
    'Queue_BraidStack',
    'Queue_RowStack',
    'Queue_ReserveStack',
    'JapaneseGarden_RowStack',
    'HanafudaRK_RowStack',
    ]


import sys, math

from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint


# ************************************************************************
#  *
#  ***********************************************************************/

class AbstractFlowerGame(Game):
    SUITS = (_("Pine"), _("Plum"), _("Cherry"), _("Wisteria"),
             _("Iris"), _("Peony"), _("Bush Clover"), _("Eularia"),
             _("Chrysanthemum"), _("Maple"), _("Willow"), _("Paulownia"))
    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.suit == card2.suit)
                and ((card1.rank + 1 == card2.rank)
                or (card1.rank - 1 == card2.rank)))

class Queue_Hint(DefaultHint):
    pass



# ************************************************************************
#  * Flower Foundation Stacks
#  ***********************************************************************/

class Flower_FoundationStack(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_cards=12, max_move=0, base_rank=ANY_RANK, base_suit=ANY_SUIT)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def updateText(self):
        AbstractFoundationStack.updateText(self)
        self.game.updateText()

    def isHanafudaSequence(self, s, strictness=1):
        for i in range(len(s) - 1):
            if s[i].suit != s[i + 1].suit:
                return 0
            if s[i].suit == 10 or strictness:
                a, b = s[i].rank, s[i + 1].rank
            else:
                a, b = self.swapTrashCards(s[i], s[i + 1])
            if a + 1 != b:
                return 0
        return cardsFaceUp(s)

    def swapTrashCards(self, carda, cardb):
        a, b = carda.rank, cardb.rank
        if a == 3 and b == 2:
            a, b = 2, 3
        elif a == 1 and b == 3:
            b = 2
        return a, b

    def getBaseCard(self):
        return ''                       # FIXME
    def getHelp(self):
        return ''                       # FIXME


class Hanafuda_SS_FoundationStack(Flower_FoundationStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 3
        return self.isHanafudaSequence([cards[0], stackcards[-1]])

    def getBottomImage(self):
        return self.game.app.images.getSuitBottom(self.cap.suit)


class FlowerClock_Foundation(Flower_FoundationStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 3
        if not stackcards[-1].suit == cards[0].suit:
            return 0
        return stackcards[-1].rank == cards[0].rank + 1


class Gaji_Foundation(Flower_FoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_move=1, min_cards=1, max_accept=1, base_suit=ANY_SUIT)
        Flower_FoundationStack.__init__(self, x, y, game, suit, **cap)
        self.CARD_YOFFSET = self.game.app.images.CARD_YOFFSET

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        return ((((stackcards[-1].suit + 1) % 12) == cards[0].suit)
                    and (stackcards[-1].rank == cards[0].rank))

    def getBottomImage(self):
        return self.game.app.images.getLetter(self.cap.base_rank)


class Pagoda_Foundation(Flower_FoundationStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 3
        a, b = stackcards[-1].rank, cards[0].rank
        if len(stackcards) < 4:
            return a - 1 == b
        elif len(stackcards) > 4:
            return a + 1 == b
        else:
            return a == b

    def getBottomImage(self):
        return self.game.app.images.getSuitBottom(self.cap.suit)


class MatsuKiri_Foundation(Flower_FoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_move=0, max_cards=48, max_accept=4, min_accept=4)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)
        self.CARD_YOFFSET = self.game.app.images.CARDH / 10

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        if not self.isHanafudaSequence(cards, 0):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].suit == 0
        return stackcards[-1].suit + 1 == cards[0].suit

##     def getBottomImage(self):
##         return self.game.app.images.getBraidBottom()


class GreatWall_FoundationStack(Flower_FoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_cards=48, max_move=1, min_accept=1, max_accept=1)
        Flower_FoundationStack.__init__(self, x, y, game, suit, **cap)
        self.CARD_YOFFSET = self.game.app.images.CARDH / 20

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if stackcards:
            return ((stackcards[-1].suit + 1) % 12 == cards[0].suit
                    and cards[0].rank == self.cap.base_rank)
        else:
            return cards[0].suit == 0

    def getBottomImage(self):
        return self.game.app.images.getLetter(self.cap.base_rank)


class FourWinds_Foundation(Flower_FoundationStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not (cards[0].rank == self.cap.base_rank):
            return 0
        if not stackcards:
            return (cards[0].suit == 0)
        else:
            return (cards[0].suit == stackcards[-1].suit + 1)

##     def getBottomImage(self):
##         return self.game.app.images.getLetter(self.cap.base_rank)


class Queue_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=12, dir=0, base_suit=ANY_SUIT, max_move=0)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return cards[0].suit == self.game.base_card.suit
        stack_dir = self.game.getFoundationDir()
        if stack_dir == 0:
            card_dir = (cards[0].suit - self.cards[-1].suit) % 12
            return card_dir in (1, 11)
        else:
            return (self.cards[-1].suit + stack_dir) % 12 == cards[0].suit

    def getBottomImage(self):
        return self.game.app.images.getLetter(self.cap.base_rank)




# ************************************************************************
#  * Flower Row Stacks
#  ***********************************************************************/

class Flower_OpenStack(OpenStack):

    def __init__(self, x, y, game, yoffset, **cap):
        kwdefault(cap, max_move=99, max_cards=99, max_accept=99, base_rank=0, dir=1)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def isHanafudaSequence(self, cards, strictness=1):
        c1 = cards[0]
        for c2 in cards[1:]:
            if c1.suit != c2.suit:
                return 0
            if c1.suit == 10 or strictness:
                a, b = c1.rank, c2.rank
            else:
                a, b = self.swapTrashCards(c1, c2)
            if a + self.cap.dir != b:
                return 0
            c1 = c2
        return 1

    def swapTrashCards(self, carda, cardb):
        a, b = carda.rank, cardb.rank
        if a == 3 and b == 2:
            a, b = 2, 3
        elif a == 1 and b == 3:
            b = 2
        return a, b


class Hanafuda_SequenceStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isHanafudaSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 0 or self.cap.base_rank == ANY_RANK
        return self.isHanafudaSequence([stackcards[-1], cards[0]])


class Oonsoo_SequenceStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isHanafudaSequence(cards, 0)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 0 or self.cap.base_rank == ANY_RANK
        return self.isHanafudaSequence([stackcards[-1], cards[0]], 0)


class FlowerClock_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return 1
        return stackcards[-1].rank + 1 == cards[0].rank


class Gaji_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if ((not len(stackcards))
                or ((stackcards[-1].suit == 10) and (stackcards[-1].rank == 3))
                or ((cards[0].suit == 10) and (cards[0].rank == 3))):
            return 1
        elif stackcards[-1].suit != cards[0].suit:
            return 0
        a, b = self.swapTrashCards(stackcards[-1], cards[0])
        return a + 1 == b


class Matsukiri_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 0
        if cards[0].suit != stackcards[-1].suit:
            return 0
        if stackcards[-1].suit == 10 or self.game.Strictness:
            a, b = stackcards[-1].rank, cards[0].rank
        else:
            a, b = self.swapTrashCards(stackcards[-1], cards[0])
        return a + 1 == b

    def canDropCards(self, stacks):
        pile = self.getPile()
        if not pile or len(pile) <= 3:
            return (None, 0)
        f = self.game.s.foundations[0]
        if not f.cards:
            suit = 0
        else:
            suit = f.cards[-1].suit + 1
        if not pile[-1].suit == suit or not self.isHanafudaSequence(pile[-4:], 0):
            return (None, 0)
        return (f, 4)


class Samuri_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 0
        return stackcards[-1].suit == cards[0].suit and stackcards[-1].rank + 1 == cards[0].rank


class GreatWall_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if not stackcards:
            return cards[0].rank == 0
        if cards[0].rank == stackcards[-1].rank:
            return stackcards[-1].suit == (cards[0].suit + 1) % 12
        a, b = self.swapTrashCards(stackcards[-1], cards[0])
        return a + 1 == b


class FourWinds_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        stackcards = self.cards
        if len(cards) - 1 or len(stackcards) >= 3:
            return 0
        if not stackcards:
            return 1
        return ((cards[0].rank == stackcards[-1].rank) and (cards[0].suit == stackcards[-1].suit - 1))

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class Queue_BraidStack(OpenStack):

    def __init__(self, x, y, game, yoffset):
        OpenStack.__init__(self, x, y, game)
        CW = self.game.app.images.CARDW
        self.CARD_YOFFSET = int(self.game.app.images.CARD_YOFFSET * yoffset)
        # use a sine wave for the x offsets
        # compensate for card width
        offset = self.game.app.images.CARDW / 1.7
        self.CARD_XOFFSET = []
        j = 1
        for i in range(20):
            self.CARD_XOFFSET.append(int(math.sin(j) * offset))
            j = j + .9


class Queue_RowStack(ReserveStack):

    def fillStack(self):
        if not self.cards and self.game.s.braid.cards:
            self.game.moveMove(1, self.game.s.braid, self)

    def getBottomImage(self):
        return self.game.app.images.getBraidBottom()


class Queue_ReserveStack(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if from_stack is self.game.s.braid or from_stack in self.game.s.rows:
            return 0
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()


class JapaneseGarden_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
                or not from_stack in self.game.s.rows):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return 1
        return stackcards[-1].rank + 1 == cards[0].rank


class HanafudaRK_RowStack(Flower_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
                or not isRankSequence(cards, dir=1)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return 1
        return stackcards[-1].rank + 1 == cards[0].rank






