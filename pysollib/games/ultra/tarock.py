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

# Ultrasol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout

from pysollib.games.special.tarock import AbstractTarockGame, Grasshopper
from pysollib.games.threepeaks import ThreePeaksNoScore


# ************************************************************************
# *
# ************************************************************************

class Tarock_OpenStack(OpenStack):

    def __init__(self, x, y, game, yoffset=-1, **cap):
        kwdefault(cap, max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS, dir=-1)
        OpenStack.__init__(self, x, y, game, **cap)
        if yoffset < 0:
            yoffset = game.app.images.CARD_YOFFSET
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
            if not (c1.suit == c2.suit
                    and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isHighRankCard(self, card):
        maxcard = ([self.game.gameinfo.ranks[-1], self.game.gameinfo.trumps[-1]]
                    [(card.suit == len(self.game.gameinfo.suits))])
        return card.rank == maxcard or self.cap.base_rank == ANY_RANK

class Tarock_RK_RowStack(Tarock_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
                or not self.isRankSequence(cards)):
            return 0
        if not self.cards:
            return self.isHighRankCard(cards[0])
        return self.isRankSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards)
                and self.isRankSequence(cards))

class Tarock_SS_RowStack(Tarock_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
                or not self.isSuitSequence(cards)):
            return 0
        if not self.cards:
            return self.isHighRankCard(cards[0])
        return self.isSuitSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards)
                and self.isSuitSequence(cards))

class Tarock_AC_RowStack(Tarock_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isAlternateColorSequence(cards)):
            return 0
        if not self.cards:
            return self.isHighRankCard(cards[0])
        return self.isAlternateColorSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards)
                and self.isAlternateColorSequence(cards))

# ************************************************************************
# *
# ************************************************************************

class Cockroach(Grasshopper):
    MAX_ROUNDS = 1

class DoubleCockroach(Grasshopper):
    MAX_ROUNDS = 1

# ************************************************************************
# *
# ************************************************************************

class Corkscrew(AbstractTarockGame):
    RowStack_Class = StackWrapper(Tarock_RK_RowStack, base_rank=NO_RANK)

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
        for i in range(78 * self.gameinfo.decks - playcards):
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
                s.foundations.append(SS_FoundationStack(x, y, self, suit=suit,
                                        max_cards=14 + 8 * (suit == 4)))
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
            card = self.s.talon.cards[-1]
            if card.rank == 13 + 8 * (card.suit == 4):
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

class Serpent(Corkscrew):
    RowStack_Class = StackWrapper(Tarock_AC_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isAlternateColorSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))

# ************************************************************************
# *
# ************************************************************************

class Rambling(Corkscrew):
    RowStack_Class = StackWrapper(Tarock_SS_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isSuitSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))

# ************************************************************************
# * Le Grande Teton
# ************************************************************************

class LeGrandeTeton(ThreePeaksNoScore):
    pass



# ************************************************************************
# * register the games
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level):
    game_type = game_type | GI.GT_TAROCK | GI.GT_CONTRIB | GI.GT_ORIGINAL
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  ranks=range(14), trumps=range(22))
    registerGame(gi)
    return gi

r(13163, Cockroach, 'Cockroach', GI.GT_TAROCK, 1, 0, GI.SL_MOSTLY_SKILL)
r(13164, DoubleCockroach, 'Double Cockroach', GI.GT_TAROCK, 2, 0, GI.SL_MOSTLY_SKILL)
r(13165, Corkscrew, 'Corkscrew', GI.GT_TAROCK, 2, 0, GI.SL_MOSTLY_SKILL)
r(13166, Serpent, 'Serpent', GI.GT_TAROCK, 2, 0, GI.SL_MOSTLY_SKILL)
r(13167, Rambling, 'Rambling', GI.GT_TAROCK, 2, 0, GI.SL_MOSTLY_SKILL)
r(22232, LeGrandeTeton, 'Le Grande Teton', GI.GT_TAROCK, 1, 0, GI.SL_BALANCED)


