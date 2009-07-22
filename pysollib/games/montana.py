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
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# ************************************************************************
# *
# ************************************************************************

class Montana_Hint(DefaultHint):
    def computeHints(self):
        game = self.game
        RLEN, RSTEP, RBASE = game.RLEN, game.RSTEP, game.RBASE
        freerows = [s for s in game.s.rows if not s.cards]
        # for each stack
        for r in game.s.rows:
            if not r.cards:
                continue
            assert len(r.cards) == 1 and r.cards[-1].face_up
            c, pile, rpile = r.cards[0], r.cards, []
            if r.id % RSTEP > 0:
                left = game.s.rows[r.id - 1]
            else:
                left = None
                if c.rank == RBASE:
                    # do not move the leftmost card of a row if the rank is correct
                    continue
            for t in freerows:
                if self.shallMovePile(r, t, pile, rpile):
                    # FIXME: this scoring is completely simple
                    if left and left.cards:
                        # prefer low-rank left neighbours
                        score = 40000 + (self.K - left.cards[-1].rank)
                    else:
                        score = 50000
                    self.addHint(score, 1, r, t)


# ************************************************************************
# * Montana
# ************************************************************************

class Montana_Talon(TalonStack):
    def canDealCards(self):
        return self.round != self.max_rounds and not self.game.isGameWon()

    def _inSequence(self, card, suit, rank):
        return card.suit == suit and card.rank == rank

    def dealCards(self, sound=False):
        # move cards to the Talon, shuffle and redeal
        game = self.game
        RLEN, RSTEP, RBASE = game.RLEN, game.RSTEP, game.RBASE
        num_cards = 0
        assert len(self.cards) == 0
        rows = game.s.rows
        # move out-of-sequence cards from the Tableau to the Talon
        stacks = []
        gaps = [None] * 4
        for g in range(4):
            i = g * RSTEP
            r = rows[i]
            if r.cards and r.cards[-1].rank == RBASE:
                in_sequence, suit = 1, r.cards[-1].suit
            else:
                in_sequence, suit = 0, NO_SUIT
            for j in range(RSTEP):
                r = rows[i + j]
                if in_sequence:
                    if (not r.cards or
                        not self._inSequence(r.cards[-1], suit, RBASE+j)):
                        in_sequence = 0
                if not in_sequence:
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
            if not r in spaces:
                self.game.moveMove(1, self, r, frames=4)
        # done
        assert len(self.cards) == 0
        if sound:
            game.stopSamples()
        return num_cards

    def getRedealSpaces(self, stacks, gaps):
        # the spaces are directly after the sorted sequence in each row
        return gaps


class Montana_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id % self.game.RSTEP == 0:
            return cards[0].rank == self.game.RBASE
        left = self.game.s.rows[self.id - 1]
        return left.cards and left.cards[-1].suit == cards[0].suit and left.cards[-1].rank + 1 == cards[0].rank

    def clickHandler(self, event):
        if not self.cards:
            return self.quickPlayHandler(event)
        return BasicRowStack.clickHandler(self, event)

    # bottom to get events for an empty stack
    prepareBottom = Stack.prepareInvisibleBottom

    getBottomImage = Stack._getReserveBottomImage


class Montana(Game):
    Talon_Class = StackWrapper(Montana_Talon, max_rounds=3)
    RowStack_Class = Montana_RowStack
    Hint_Class = Montana_Hint

    RLEN, RSTEP, RBASE = 52, 13, 1

    def createGame(self, round_text=True):
        decks = self.gameinfo.decks

        # create layout
        l, s = Layout(self, card_x_space=4), self.s

        # set window
        w, h = l.XM + self.RSTEP*l.XS, l.YM + (4*decks)*l.YS
        if round_text:
            h += l.YS
        self.setSize(w, h)

        # create stacks
        for k in range(decks):
            for i in range(4):
                x, y = l.XM, l.YM + (i+k*4)*l.YS
                for j in range(self.RSTEP):
                    s.rows.append(self.RowStack_Class(x, y, self,
                                  max_accept=1, max_cards=1))
                    x += l.XS
        if round_text:
            x, y = l.XM + (self.RSTEP-1)*l.XS/2, self.height-l.YS
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


    #
    # game overrides
    #

    def startGame(self):
        frames = 0
        for i in range(52):
            c = self.s.talon.cards[-1]
            if c.rank == ACE:
                self.s.talon.dealRow(rows=self.s.internals, frames=0)
            else:
                if frames == 0 and i >= 39:
                    self.startDealSample()
                    frames = 4
                self.s.talon.dealRow(rows=(self.s.rows[i],), frames=frames)

    def isGameWon(self):
        rows = self.s.rows
        for i in range(0, self.RLEN, self.RSTEP):
            if not rows[i].cards:
                return False
            suit = rows[i].cards[-1].suit
            for j in range(self.RSTEP - 1):
                r = rows[i + j]
                if not r.cards or r.cards[-1].rank != self.RBASE + j or r.cards[-1].suit != suit:
                    return False
        return True

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        return (self.sg.dropstacks, (), self.sg.dropstacks)

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if from_stack.cards:
            if from_stack.id % self.RSTEP == 0 and from_stack.cards[-1].rank == self.RBASE:
                # do not move the leftmost card of a row if the rank is correct
                return -1
        return 1


# ************************************************************************
# * Spaces
# ************************************************************************

class Spaces_Talon(Montana_Talon):
    def getRedealSpaces(self, stacks, gaps):
        # use four random spaces, ignore gaps
        # note: the random.seed is already saved in shuffleStackMove
        spaces = []
        while len(spaces) != 4:
            r = self.game.random.choice(stacks)
            if not r in spaces:
                spaces.append(r)
        return spaces

class Spaces(Montana):
    Talon_Class = StackWrapper(Spaces_Talon, max_rounds=3)


# ************************************************************************
# * Blue Moon
# ************************************************************************

class BlueMoon(Montana):
    RLEN, RSTEP, RBASE = 56, 14, 0

    def startGame(self):
        frames = 0
        for i in range(self.RLEN):
            if i == self.RLEN-self.RSTEP: # last row
                self.startDealSample()
                frames = -1
            if i % self.RSTEP == 0:     # left column
                continue
            self.s.talon.dealRow(rows=(self.s.rows[i],), frames=frames)
        ace_rows = [r for r in self.s.rows if r.cards and r.cards[-1].rank == ACE]
        j = 0
        for r in ace_rows:
            self.moveMove(1, r, self.s.rows[j])
            j += self.RSTEP


# ************************************************************************
# * Red Moon
# ************************************************************************

class RedMoon(BlueMoon):
    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        frames = 0
        r = self.s.rows
        self.s.talon.dealRow(rows=(r[0],r[14],r[28],r[42]), frames=frames)
        for i in range(4):
            if i == 3:
                self.startDealSample()
                frames = 4
            n = i * 14 + 2
            self.s.talon.dealRow(rows=r[n:n+12], frames=frames)


# ************************************************************************
# * Galary
# ************************************************************************


class Galary_Hint(Montana_Hint):
    def shallMovePile(self, from_stack, to_stack, pile, rpile):
        if from_stack is to_stack or not to_stack.acceptsCards(from_stack, pile):
            return False
        # now check for loops
        rr = self.ClonedStack(from_stack, stackcards=rpile)
        if rr.acceptsCards(to_stack, pile):
            # the pile we are going to move could be moved back -
            # this is dangerous as we can create endless loops...
            return False
        return True


class Galary_RowStack(Montana_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id % self.game.RSTEP == 0:
            return cards[0].rank == self.game.RBASE
        r = self.game.s.rows
        left = r[self.id - 1]
        if left.cards and left.cards[-1].suit == cards[0].suit \
               and left.cards[-1].rank + 1 == cards[0].rank:
            return True
        if self.id < len(r)-1:
            right = r[self.id + 1]
            if right.cards and right.cards[-1].suit == cards[0].suit \
                   and right.cards[-1].rank - 1 == cards[0].rank:
                return True
        return False


class Galary(RedMoon):
    RowStack_Class = Galary_RowStack
    Hint_Class = Galary_Hint


# ************************************************************************
# * Moonlight
# ************************************************************************

class Moonlight(Montana):
    RowStack_Class = Galary_RowStack
    Hint_Class = Galary_Hint


# ************************************************************************
# * Jungle
# ************************************************************************

class Jungle_RowStack(Montana_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id % self.game.RSTEP == 0:
            return cards[0].rank == self.game.RBASE
        left = self.game.s.rows[self.id - 1]
        return left.cards and left.cards[-1].rank + 1 == cards[0].rank

class Jungle(BlueMoon):
    Talon_Class = StackWrapper(Montana_Talon, max_rounds=2)
    RowStack_Class = Jungle_RowStack
    Hint_Class = Galary_Hint


# ************************************************************************
# * Spaces and Aces
# ************************************************************************

class SpacesAndAces_RowStack(Montana_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id % self.game.RSTEP == 0:
            return cards[0].rank == self.game.RBASE
        left = self.game.s.rows[self.id - 1]
        return left.cards and left.cards[-1].suit == cards[0].suit and left.cards[-1].rank < cards[0].rank


class SpacesAndAces(BlueMoon):
    Hint_Class = Galary_Hint
    Talon_Class = InitialDealTalonStack
    RowStack_Class = SpacesAndAces_RowStack

    def createGame(self):
        Montana.createGame(self, round_text=False)

    def startGame(self):
        frames = 0
        for i in range(self.RLEN):
            if i == self.RLEN-self.RSTEP: # last row
                self.startDealSample()
                frames = -1
            if i % self.RSTEP == 0:     # left column
                continue
            self.s.talon.dealRow(rows=(self.s.rows[i],), frames=frames)

# ************************************************************************
# * Paganini
# ************************************************************************

class Paganini_Talon(Montana_Talon):
    def _inSequence(self, card, suit, rank):
        card_rank = card.rank
        if card_rank >= 5:
            card_rank -= 4
        return card.suit == suit and card_rank == rank

class Paganini_RowStack(Montana_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id % self.game.RSTEP == 0:
            return cards[0].rank == self.game.RBASE
        left = self.game.s.rows[self.id - 1]
        if not left.cards:
            return False
        if left.cards[-1].suit != cards[0].suit:
            return False
        if left.cards[-1].rank == ACE:
            return cards[0].rank == 5
        return left.cards[-1].rank+1 == cards[0].rank

class Paganini(BlueMoon):
    RLEN, RSTEP, RBASE = 40, 10, 0

    Talon_Class = StackWrapper(Paganini_Talon, max_rounds=2)
    RowStack_Class = Paganini_RowStack

    def isGameWon(self):
        rows = self.s.rows
        for i in range(0, self.RLEN, self.RSTEP):
            if not rows[i].cards:
                return False
            suit = rows[i].cards[-1].suit
            for j in range(self.RSTEP - 1):
                r = rows[i + j]
                if not r.cards:
                    return False
                card = r.cards[-1]
                card_rank = card.rank
                if card_rank >= 5:
                    card_rank -= 4
                if card_rank != self.RBASE + j or card.suit != suit:
                    return False
        return True


# ************************************************************************
# * Spoilt
# ************************************************************************

class Spoilt_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        #if not BasicRowStack.acceptsCards(self, from_stack, cards):
        #    return False

        card = cards[0]
        RSTEP = self.game.RSTEP
        RBASE = self.game.RBASE
        row, col = divmod(self.id, RSTEP)
        # check rank
        if card.rank == ACE:
            if col != RSTEP-1:
                return False
        else:
            if card.rank - RBASE != col:
                return False
        # check suit
        suit = None
        for i in range(row*RSTEP, (row+1)*RSTEP):
            r = self.game.s.rows[i]
            if r.cards and r.cards[0].face_up:
                suit = r.cards[0].suit
                break
        if suit is not None:
            return card.suit == suit
        for r in self.game.s.rows:      # check other rows
            if r.cards and r.cards[0].face_up and r.cards[0].suit == card.suit:
                return False
        return True

    def canFlipCard(self):
        return False


class Spoilt_Waste(WasteStack):

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1 and to_stack in self.game.s.rows
        if to_stack.cards:
            self._swapPairMove(ncards, to_stack, frames=-1, shadow=0)
        else:
            WasteStack.moveMove(self, ncards, to_stack, frames, shadow)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.flipMove(other_stack)
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=frames, shadow=shadow)
        game.moveMove(n, swap, other_stack, frames=0)
        game.leaveState(old_state)


class Spoilt(Game):
    RSTEP, RBASE = 8, 6

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + self.RSTEP*l.XS, l.YM + 5.5*l.YS)

        # create stacks
        for i in range(4):
            x, y, = l.XM, l.YM + i*l.YS
            for j in range(self.RSTEP):
                s.rows.append(Spoilt_RowStack(x, y, self,
                              max_accept=1, max_cards=2, min_cards=1))
                x += l.XS
        x, y = self.width/2 - l.XS, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'n')
        x += l.XS
        s.waste = Spoilt_Waste(x, y, self, max_cards=1)

        # create an invisible stack
        s.internals.append(InvisibleStack(self))

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        for i in range(4):
            rows = self.s.rows[self.RSTEP*i+1:self.RSTEP*(i+1)]
            self.s.talon.dealRow(rows=rows, frames=4, flip=False)
        self.s.talon.dealCards()

    def isGameWon(self):
        for r in self.s.rows:
            if not r.cards:
                return False
            if not r.cards[0].face_up:
                return False
        return True

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        return (), (), ()


# ************************************************************************
# * Double Montana
# ************************************************************************

class DoubleMontana(Montana):
    Talon_Class = InitialDealTalonStack
    Hint_Class = Galary_Hint
    RLEN, RSTEP, RBASE = 112, 14, 0

    def createGame(self):
        Montana.createGame(self, round_text=False)

    def startGame(self):
        frames = 0
        for i in range(self.RLEN):
            if i == self.RLEN-self.RSTEP: # last row
                self.startDealSample()
                frames = -1
            if i % self.RSTEP == 0:     # left column
                continue
            self.s.talon.dealRow(rows=(self.s.rows[i],), frames=frames)



# register the game
registerGame(GameInfo(53, Montana, "Montana",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 48}, altnames="Gaps"))
registerGame(GameInfo(116, Spaces, "Spaces",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 48}))
registerGame(GameInfo(63, BlueMoon, "Blue Moon",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL,
                      altnames=("Rangoon",) ))
registerGame(GameInfo(117, RedMoon, "Red Moon",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(275, Galary, "Galary",
                      GI.GT_MONTANA | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(276, Moonlight, "Moonlight",
                      GI.GT_MONTANA | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 2, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 48}))
registerGame(GameInfo(380, Jungle, "Jungle",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 1, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(381, SpacesAndAces, "Spaces and Aces",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(706, Paganini, "Paganini",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 1, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 5, 6, 7, 8, 9, 10, 11, 12),
                      altnames=('Long Trip',) ))
registerGame(GameInfo(736, Spoilt, "Spoilt",
                      GI.GT_MONTANA, 1, 0, GI.SL_MOSTLY_LUCK,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12),
                      ))
registerGame(GameInfo(759, DoubleMontana, "Double Montana",
                      GI.GT_MONTANA | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))


