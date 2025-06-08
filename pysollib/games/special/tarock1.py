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

from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.games.acesup import AcesUp
from pysollib.games.montana import Montana, Montana_Talon
from pysollib.games.special.tarock import AbstractTarockGame, Grasshopper
from pysollib.games.threepeaks import Golf_Waste, ThreePeaksNoScore
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.stack import \
        AbstractFoundationStack, \
        BasicRowStack, \
        InitialDealTalonStack, \
        InvisibleStack, \
        OpenStack, \
        ReserveStack, \
        SS_FoundationStack, \
        StackWrapper
from pysollib.util import ACE, ANY_RANK, NO_RANK, \
        UNLIMITED_ACCEPTS, UNLIMITED_MOVES


class Tarock_OpenStack(OpenStack):

    def __init__(self, x, y, game, yoffset=-1, **cap):
        kwdefault(
            cap, max_move=UNLIMITED_MOVES,
            max_accept=UNLIMITED_ACCEPTS, dir=-1)
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
            if (c1.color < 2 and c1.color == c2.color or
                    not c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isSuitSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not (c1.suit == c2.suit and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isHighRankCard(self, card):
        maxcard = ([self.game.gameinfo.ranks[-1],
                    self.game.gameinfo.trumps[-1]]
                   [(card.suit == len(self.game.gameinfo.suits))])
        return card.rank == maxcard or self.cap.base_rank == ANY_RANK


class Tarock_RK_RowStack(Tarock_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards) or
                not self.isRankSequence(cards)):
            return 0
        if not self.cards:
            return self.isHighRankCard(cards[0])
        return self.isRankSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards) and self.isRankSequence(cards))


class Tarock_SS_RowStack(Tarock_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards) or
                not self.isSuitSequence(cards)):
            return 0
        if not self.cards:
            return self.isHighRankCard(cards[0])
        return self.isSuitSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards) and self.isSuitSequence(cards))


class Tarock_AC_RowStack(Tarock_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards) \
               or not self.isAlternateColorSequence(cards):
            return 0
        if not self.cards:
            return self.isHighRankCard(cards[0])
        return self.isAlternateColorSequence([self.cards[-1], cards[0]])

    def canMoveCards(self, cards):
        return (self.basicCanMoveCards(cards) and
                self.isAlternateColorSequence(cards))

# ************************************************************************
# * Cockroach
# * Double Cockroach
# ************************************************************************


class Cockroach(Grasshopper):
    MAX_ROUNDS = 1


class DoubleCockroach(Grasshopper):
    MAX_ROUNDS = 1

# ************************************************************************
# * Corkscrew
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
        playcards = 4 * l.YS // l.YOFFSET
        xoffset, yoffset = [], []
        for i in range(playcards):
            xoffset.append(0)
            yoffset.append(l.YOFFSET)
        for i in range(78 * self.gameinfo.decks - playcards):
            xoffset.append(l.XOFFSET)
            yoffset.append(0)

        # create stacks
        x, y = l.XM + (maxrows - reserves) * l.XS // 2, l.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        x, y = l.XM + (maxrows - rows) * l.XS // 2, l.YM + l.YS
        self.setRegion(s.reserves, (-999, -999, 999999, y - l.YM // 2))
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self, yoffset=l.YOFFSET)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = yoffset
            s.rows.append(stack)
            x = x + l.XS
        x, y = l.XM + maxrows * l.XS, l.YM
        for i in range(2):
            for suit in range(5):
                s.foundations.append(
                    SS_FoundationStack(
                        x, y, self, suit=suit,
                        max_cards=14 + 8 * (suit == 4)))
                y = y + l.YS
            x, y = x + l.XS, l.YM
        self.setRegion(
            self.s.foundations,
            (x - l.XS * 2, -999, 999999,
             self.height - (l.YS + l.YM)), priority=1)
        s.talon = InitialDealTalonStack(
            self.width - 3 * l.XS // 2, self.height - l.YS, self)

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
                dist = (stack.cards[-1].x - cx)**2 + \
                    (stack.cards[-1].y - cy)**2
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
# * Serpent
# ************************************************************************


class Serpent(Corkscrew):
    RowStack_Class = StackWrapper(Tarock_AC_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isAlternateColorSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))

# ************************************************************************
# * Rambling
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


class LeGrandeTeton(AbstractTarockGame, ThreePeaksNoScore):
    Waste_Class = StackWrapper(Golf_Waste, mod=14)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if stack1 == self.s.waste or stack2 == self.s.waste:
            return ((card1.rank + 1) % 14 == card2.rank or
                    (card1.rank - 1) % 14 == card2.rank)
        return False


# ************************************************************************
# * Fool's Up
# ************************************************************************

class FoolsUp_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        c = cards[0]
        for s in self.game.s.rows:
            if s is not from_stack and s.cards and s.cards[-1].suit == c.suit:
                if c.suit == 4:
                    if s.cards[-1].rank > c.rank:
                        return True
                else:
                    if s.cards[-1].rank > c.rank or s.cards[-1].rank == ACE:
                        # found a higher rank or an Ace on the row stacks
                        return c.rank != ACE
        return False


class FoolsUp(AcesUp):
    Foundation_Class = StackWrapper(FoolsUp_Foundation, max_cards=73)

    def createGame(self):
        AcesUp.createGame(self, rows=5)

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != 73:
            return False
        for s in self.s.rows:
            if len(s.cards) != 1:
                return False
            if s.cards[0].suit == 4 and s.cards[0].rank != 21:
                return False
            if s.cards[0].suit < 4 and s.cards[0].rank != ACE:
                return False
        return True


# ************************************************************************
# * Trumps Row
# ************************************************************************

class TrumpsRow_Talon(Montana_Talon):
    def dealCards(self, sound=False):
        # move cards to the Talon, shuffle and redeal
        game = self.game
        decks = game.gameinfo.decks
        RSTEP, RBASE = game.RSTEP, game.RBASE
        num_cards = 0
        assert len(self.cards) == 0
        rows = game.s.rows
        # move out-of-sequence cards from the Tableau to the Talon
        stacks = []
        gaps = [None] * (5 * decks)
        for g in range(5 * decks):
            NRSTEP = RSTEP
            if g == game.TRUMPSUIT:
                NRSTEP = 22
            i = min(77, g * RSTEP)
            print(i)
            r = rows[i]
            if r.cards and r.id < RSTEP * self.game.TRUMPSUIT and \
                    r.cards[-1].rank == RBASE and \
                    r.cards[-1].suit != self.game.TRUMPSUIT:
                in_sequence, suit = 1, r.cards[-1].suit
            elif r.id == RSTEP * self.game.TRUMPSUIT and \
                    r.cards[-1].rank == RBASE and \
                    r.cards[-1].suit == self.game.TRUMPSUIT:
                in_sequence, suit = 1, self.game.TRUMPSUIT
            else:
                in_sequence, suit = 0, 999999

            for j in range(NRSTEP):
                if i + j >= 78:
                    continue
                r = rows[i + j]
                if in_sequence:
                    if (not r.cards or
                            not self._inSequence(r.cards[-1], suit, RBASE+j)):
                        in_sequence = 0
                if not in_sequence:
                    if r not in stacks:
                        stacks.append(r)
                        if gaps[g] is None:
                            gaps[g] = r
                        if r.cards:
                            game.moveMove(1, r, self, frames=0)
                            num_cards = num_cards + 1
        assert len(self.cards) == num_cards
        assert len(stacks) == num_cards + len(gaps)
        if num_cards == 0:          # game already finished
            return 0
        if sound:
            game.startDealSample()
        # shuffle
        game.shuffleStackMove(self)
        # redeal
        game.nextRoundMove(self)
        spaces = self.getRedealSpaces(stacks, gaps)
        for r in stacks:
            if r not in spaces:
                self.game.moveMove(1, self, r, frames=4)
        # done
        assert len(self.cards) == 0
        if sound:
            game.stopSamples()
        return num_cards


class TrumpsRow_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id % self.game.RSTEP == 0:
            return cards[0].rank == self.game.RBASE and \
                cards[0].suit != self.game.TRUMPSUIT
        left = self.game.s.rows[self.id - 1]
        return left.cards and left.cards[-1].suit == cards[0].suit \
            and left.cards[-1].rank + 1 == cards[0].rank

    def clickHandler(self, event):
        if not self.cards:
            return self.quickPlayHandler(event)
        return BasicRowStack.clickHandler(self, event)

    getBottomImage = BasicRowStack._getBlankBottomImage


class TrumpsRow_TrumpRowStack(TrumpsRow_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id == self.game.RSTEP * self.game.TRUMPSUIT:
            return cards[0].rank == self.game.RBASE and \
                cards[0].suit == self.game.TRUMPSUIT
        left = self.game.s.rows[self.id - 1]
        return left.cards and left.cards[-1].suit == cards[0].suit \
            and left.cards[-1].rank + 1 == cards[0].rank


class TrumpsRow(Montana):
    Talon_Class = StackWrapper(TrumpsRow_Talon, max_rounds=5)
    RLEN, RSTEP, RBASE = 78, 14, 1
    TRUMPSUIT = 4

    def createGame(self, round_text=True):
        decks = self.gameinfo.decks

        # create layout
        l, s = Layout(self, card_x_space=4), self.s

        # set window
        w, h = l.XM + self.RSTEP*l.XS, l.YM + (6.25*decks)*l.YS
        if round_text:
            h += l.YS
        self.setSize(w, h)

        # create stacks
        for k in range(decks):
            for i in range(4):
                x, y = l.XM, l.YM + (i+k*4)*l.YS
                for j in range(self.RSTEP):
                    s.rows.append(TrumpsRow_RowStack(x, y, self,
                                  max_accept=1, max_cards=1))
                    x += l.XS
            x, y = l.XM, l.YM + (4.25 + k * 4) * l.YS
            for j in range(self.RSTEP):
                s.rows.append(TrumpsRow_TrumpRowStack(x, y, self,
                                                      max_accept=1,
                                                      max_cards=1))
                x += l.XS
            x, y = l.XM, l.YM + (5.25 + k * 4) * l.YS
            for j in range(22 - self.RSTEP):
                s.rows.append(TrumpsRow_TrumpRowStack(x, y, self,
                                                      max_accept=1,
                                                      max_cards=1))
                x += l.XS
        if round_text:
            x, y = l.XM + (self.RSTEP-1)*l.XS//2, self.height-l.YS
            s.talon = self.Talon_Class(x, y, self)
            l.createRoundText(s.talon, 'se')
        else:
            # Talon is invisible
            x, y = self.getInvisibleCoords()
            s.talon = self.Talon_Class(x, y, self)
        if self.RBASE:
            # create an invisible stack to hold the four Aces
            s.internals.append(InvisibleStack(self))

        # define stack-groups
        l.defaultStackGroups()

    def isGameWon(self):
        rows = self.s.rows
        for i in range(0, self.RSTEP * self.TRUMPSUIT, self.RSTEP):
            if not rows[i].cards:
                return False
            suit = rows[i].cards[-1].suit
            for j in range(self.RSTEP - 1):
                r = rows[i + j]
                if not r.cards or r.cards[-1].rank != self.RBASE + j \
                        or r.cards[-1].suit != suit:
                    return False
        if not rows[self.RSTEP * self.TRUMPSUIT].cards:
            return False
        suit = self.TRUMPSUIT
        for j in range(21):
            r = rows[self.RSTEP * self.TRUMPSUIT + j]
            if not r.cards or r.cards[-1].rank != self.RBASE + j \
                    or r.cards[-1].suit != suit:
                return False
        return True


# ************************************************************************
# * register the games
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level,
      numcards=78, altnames=()):
    game_type = game_type | GI.GT_TAROCK | GI.GT_CONTRIB | GI.GT_ORIGINAL
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  ranks=list(range(14)), trumps=list(range(22)),
                  altnames=altnames, si={"ncards": numcards})
    registerGame(gi)
    return gi


r(13163, Cockroach, 'Cockroach', GI.GT_TAROCK, 1, 0, GI.SL_MOSTLY_SKILL)
r(13164, DoubleCockroach, 'Double Cockroach', GI.GT_TAROCK, 2, 0,
  GI.SL_MOSTLY_SKILL)
r(13165, Corkscrew, 'Corkscrew', GI.GT_TAROCK | GI.GT_OPEN, 2, 0,
  GI.SL_MOSTLY_SKILL)
r(13166, Serpent, 'Serpent', GI.GT_TAROCK | GI.GT_OPEN, 2, 0,
  GI.SL_MOSTLY_SKILL)
r(13167, Rambling, 'Rambling', GI.GT_TAROCK | GI.GT_OPEN, 2, 0,
  GI.SL_MOSTLY_SKILL)
r(13168, FoolsUp, "Fool's Up", GI.GT_TAROCK, 1, 0, GI.SL_LUCK,
  altnames=('Solitairot'))
r(13169, TrumpsRow, "Trumps Row", GI.GT_TAROCK, 1, 4, GI.SL_MOSTLY_SKILL,
  numcards=73)
r(22232, LeGrandeTeton, 'Le Grande Teton', GI.GT_TAROCK, 1, 0, GI.SL_BALANCED)
