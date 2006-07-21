#!/usr/bin/env python
# -*- mode: python; coding: iso8859-1; -*-
## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
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

# /***********************************************************************
# //
# ************************************************************************/

class SiebenBisAs_Hint(CautiousDefaultHint):
    def computeHints(self):
        game = self.game
        freerows = filter(lambda s: not s.cards, game.s.rows)
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


# /***********************************************************************
# // Sieben bis As (Seven to Ace)
# ************************************************************************/

class SiebenBisAs_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # this stack accepts only a card from a rowstack with an empty
        # left neighbour
        if not from_stack in self.game.s.rows:
            return 0
        if from_stack.id % 10 == 0:
            return 0
        return len(self.game.s.rows[from_stack.id - 1].cards) == 0


class SiebenBisAs_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        if self.id % 10 != 0:
            # left neighbour
            s = self.game.s.rows[self.id - 1]
            if s.cards and s.cards[-1].suit == cards[0].suit and (s.cards[-1].rank + 1) % 13 == cards[0].rank:
                return 1
        if self.id % 10 != 10 - 1:
            # right neighbour
            s = self.game.s.rows[self.id + 1]
            if s.cards and s.cards[-1].suit == cards[0].suit and (s.cards[-1].rank - 1) % 13 == cards[0].rank:
                return 1
        return 0

    # bottom to get events for an empty stack
    ###prepareBottom = Stack.prepareInvisibleBottom

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


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
        stacks = filter(lambda r: r.cards[-1].rank == 6, self.s.rows)
        for r in stacks:
            self.moveMove(1, r, self.s.foundations[r.cards[-1].suit])


# /***********************************************************************
# // Maze
# ************************************************************************/

class Maze_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        # left neighbour
        s = self.game.s.rows[(self.id - 1) % 54]
        if s.cards:
            if s.cards[-1].suit == cards[0].suit and s.cards[-1].rank + 1 == cards[0].rank:
                return 1
            if s.cards[-1].rank == QUEEN and cards[0].rank == ACE:
                return 1
        # right neighbour
        s = self.game.s.rows[(self.id + 1) % 54]
        if s.cards:
            if s.cards[-1].suit == cards[0].suit and s.cards[-1].rank - 1 == cards[0].rank:
                return 1
        return 0

    # bottom to get events for an empty stack
    prepareBottom = Stack.prepareInvisibleBottom

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class Maze(Game):
    GAME_VERSION = 2

    Hint_Class = SiebenBisAs_Hint

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
        rows = filter(lambda s: s.cards, self.s.rows)
        if len(rows) != 48:
            return 0            # no cards dealt yet
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
                return 0
            if r1.cards[-1].rank != ACE or r2.cards[-1].rank != QUEEN:
                return 0
            pile = getPileFromStacks(rows[j:j+12])
            if not pile or not isSameSuitSequence(pile, dir=1):
                return 0
        return 1


# register the game
registerGame(GameInfo(118, SiebenBisAs, "Sieben bis As",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12)))
registerGame(GameInfo(144, Maze, "Maze",
                      GI.GT_MONTANA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      si={"ncards": 48}))

