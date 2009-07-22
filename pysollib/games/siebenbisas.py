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

class SiebenBisAs_Hint(CautiousDefaultHint):
    def computeHints(self):
        game = self.game
        freerows = [s for s in game.s.rows if not s.cards]
        # for each stack
        for r in game.sg.dropstacks:
            if not r.cards:
                continue
            assert len(r.cards) == 1 and r.cards[-1].face_up
            c, pile, rpile = r.cards[0], r.cards, []
            # try if we can drop the card
            t, ncards = r.canDropCards(self.game.s.foundations)
            if t:
                score, color = 0, None
                score, color = self._getDropCardScore(score, color, r, t, ncards)
                self.addHint(score, ncards, r, t, color)
            # try if we can move the card
            for t in freerows:
                if self.shallMovePile(r, t, pile, rpile):
                    # FIXME: this scoring
                    score = 50000
                    self.addHint(score, 1, r, t)

    def shallMovePile(self, from_stack, to_stack, pile, rpile):
        if from_stack is to_stack or not to_stack.acceptsCards(from_stack, pile):
            return 0
        # now check for loops
        rr = self.ClonedStack(from_stack, stackcards=rpile)
        if rr.acceptsCards(to_stack, pile):
            # the pile we are going to move could be moved back -
            # this is dangerous as we can create endless loops...
            return 0
        return 1

# ************************************************************************
# * Sieben bis As (Seven to Ace)
# ************************************************************************

class SiebenBisAs_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts only a card from a rowstack with an empty
        # left neighbour
        if not from_stack in self.game.s.rows:
            return False
        if from_stack.id % 10 == 0:
            return False
        return len(self.game.s.rows[from_stack.id - 1].cards) == 0


class SiebenBisAs_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.id % 10 != 0:
            # left neighbour
            s = self.game.s.rows[self.id - 1]
            if s.cards and s.cards[-1].suit == cards[0].suit and (s.cards[-1].rank + 1) % 13 == cards[0].rank:
                return True
        if self.id % 10 != 10 - 1:
            # right neighbour
            s = self.game.s.rows[self.id + 1]
            if s.cards and s.cards[-1].suit == cards[0].suit and (s.cards[-1].rank - 1) % 13 == cards[0].rank:
                return True
        return False

    # bottom to get events for an empty stack
    ###prepareBottom = Stack.prepareInvisibleBottom

    getBottomImage = Stack._getReserveBottomImage


class SiebenBisAs(Game):
    Hint_Class = SiebenBisAs_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 10*l.XS, l.YM + 5*l.YS)

        # create stacks
        for i in range(3):
            for j in range(10):
                x, y, = l.XM + j*l.XS, l.YM + (i+1)*l.YS
                s.rows.append(SiebenBisAs_RowStack(x, y, self, max_accept=1, max_cards=1))
        for i in range(2):
            x, y, = l.XM + (i+4)*l.XS, l.YM
            s.reserves.append(ReserveStack(x, y, self, max_accept=0))
        for i in range(4):
            x, y, = l.XM + (i+3)*l.XS, l.YM + 4*l.YS
            s.foundations.append(SiebenBisAs_Foundation(x, y, self, i, base_rank=6, mod=13, max_move=0, max_cards=8))
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)
        stacks = [r for r in self.s.rows if r.cards[-1].rank == 6]
        for r in stacks:
            self.moveMove(1, r, self.s.foundations[r.cards[-1].suit])

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * Maze
# ************************************************************************

class Maze_Hint(SiebenBisAs_Hint):
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


class Maze_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # left neighbour
        s = self.game.s.rows[(self.id - 1) % 54]
        if s.cards:
            if s.cards[-1].suit == cards[0].suit and s.cards[-1].rank + 1 == cards[0].rank:
                return True
            if s.cards[-1].rank == QUEEN and cards[0].rank == ACE:
                return True
        # right neighbour
        s = self.game.s.rows[(self.id + 1) % 54]
        if s.cards:
            if s.cards[-1].suit == cards[0].suit and s.cards[-1].rank - 1 == cards[0].rank:
                return True
        return False

    # bottom to get events for an empty stack
    prepareBottom = Stack.prepareInvisibleBottom

    getBottomImage = Stack._getReserveBottomImage


class Maze(Game):
    GAME_VERSION = 2

    Hint_Class = Maze_Hint #SiebenBisAs_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, card_x_space=4, card_y_space=4), self.s

        # set window
        self.setSize(l.XM + 9*l.XS, l.YM + 6*l.YS)

        # create stacks
        for i in range(6):
            for j in range(9):
                x, y, = l.XM + j*l.XS, l.YM + i*l.YS
                s.rows.append(Maze_RowStack(x, y, self, max_accept=1, max_cards=1))
        ##s.talon = InitialDealTalonStack(-2*l.XS, l.YM+5*l.YS/2, self)
        s.talon = InitialDealTalonStack(self.width-l.XS+1, self.height-l.YS, self)
        # create an invisble stack to hold the four Kings
        s.internals.append(InvisibleStack(self))

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        frames = 0
        for i in range(54):
##            if i == 8 or i == 17:       # these stay empty
            if i >= 52:                 # these stay empty
                continue
            c = self.s.talon.cards[-1]
            if c.rank == KING:
                self.s.talon.dealRow(rows=self.s.internals, frames=0)
            else:
                if frames == 0 and i >= 36:
                    self.startDealSample()
                    frames = -1
                self.s.talon.dealRow(rows=(self.s.rows[i],), frames=frames)

    def isGameWon(self):
        rows = [s for s in self.s.rows if s.cards]
        if len(rows) != 48:
            return False            # no cards dealt yet
        i = 0
        if 1:
            # allow wrap around: search first Ace
            while rows[i].cards[-1].rank != ACE:
                i = i + 1
            rows = rows + rows
        # now check for 4 sequences
        for j in (i+0, i+12, i+24, i+36):
            r1 = rows[j]
            r2 = rows[j+11]
            if (r2.id - r1.id) % 54 != 11:
                # found a space within the sequence
                return False
            if r1.cards[-1].rank != ACE or r2.cards[-1].rank != QUEEN:
                return False
            pile = getPileFromStacks(rows[j:j+12])
            if not pile or not isSameSuitSequence(pile, dir=1):
                return False
        return True


# register the game
registerGame(GameInfo(118, SiebenBisAs, "Sieben bis As",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12)))
registerGame(GameInfo(144, Maze, "Maze",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 48}))

