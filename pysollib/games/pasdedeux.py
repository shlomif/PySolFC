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
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# *
# ************************************************************************

class PasDeDeux_Hint(AbstractHint):
    # FIXME: this is very simple

    def getDistance(self, stack, card):
        d = 0
        if card.rank != stack.id % 13:
            d = d + 1
        if card.suit != stack.id / 13:
            d = d + 1
        return d

    def computeHints(self):
        # find the single stack that can currently move a card
        rows = []
        for r in self.game.s.rows:
            if r.canMoveCards(r.cards):
                rows.append(r)
                break
        # for each stack
        for r in rows:
            r1_d = self.getDistance(r, r.cards[-1])
            column, row = r.id % 13, r.id / 13
            stack_ids = range(column, 52, 13) + range(13*row, 13*row+13)
            for i in stack_ids:
                t = self.game.s.rows[i]
                if t is r:
                    continue
                assert t.acceptsCards(r, r.cards)
                t1_d = self.getDistance(t, t.cards[-1])
                # compute distances after swap
                r2_d = self.getDistance(t, r.cards[-1])
                t2_d = self.getDistance(r, t.cards[-1])
                #
                rw, tw = 3, 2
                if self.game.s.talon.round >= 2:
                    rw, tw = 4, 2
                c = self.game.cards[t.cards[-1].id - 52]
                if 1 and c in self.game.s.waste.cards:
                    rw = rw - 1
                #
                score = int(((rw*r1_d + tw*t1_d) - (rw*r2_d + tw*t2_d)) * 1000)
                if score > 0:
                    self.addHint(score, 1, r, t)


# ************************************************************************
# * Pas de Deux
# ************************************************************************

class PasDeDeux_Waste(WasteStack):
    def canFlipCard(self):
        return False


class PasDeDeux_RowStack(ReserveStack):
    def canMoveCards(self, cards):
        if not ReserveStack.canMoveCards(self, cards):
            return False
        if not self.game.s.waste.cards:
            return False
        c = self.game.s.waste.cards[-1]
        return c.face_up and cards[0].suit == c.suit and cards[0].rank == c.rank

    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        # must be neighbours
        return self.game.isNeighbour(from_stack, self)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1 and to_stack in self.game.s.rows
        assert len(to_stack.cards) == 1
        self._swapPairMove(ncards, to_stack, frames=-1, shadow=0)
        if self.game.s.talon.canDealCards():
            self.game.s.talon.dealCards()
        else:
            # mark game as finished by turning the Waste face down
            assert self.game.s.waste.cards[-1].face_up
            self.game.flipMove(self.game.s.waste)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=frames, shadow=shadow)
        game.moveMove(n, swap, other_stack, frames=0)
        game.leaveState(old_state)

    def getBottomImage(self):
        suit = self.id / 13
        return self.game.app.images.getSuitBottom(suit)

    def quickPlayHandler(self, event, from_stacks=None, to_stacks=None):
        # find the single stack that can currently move a card
        for r in self.game.s.rows:
            if r.canMoveCards(r.cards):
                if self.acceptsCards(r, r.cards):
                    r.playMoveMove(len(r.cards), self)
                    return 1
                break
        return 0


class PasDeDeux(Game):
    Hint_Class = PasDeDeux_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, card_x_space=4), self.s

        # set window
        self.setSize(l.XM + 13*l.XS, l.YM + 5*l.YS)

        # create stacks
        for i in range(4):
            for j in range(13):
                x, y, = l.XM + j*l.XS, l.YM + i*l.YS
                s.rows.append(PasDeDeux_RowStack(x, y, self, max_accept=1, max_cards=2))
        x, y = self.width - 2*l.XS, self.height - l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, "se")
        l.createRoundText(s.talon, 'ne')
        x -= l.XS
        s.waste = PasDeDeux_Waste(x, y, self, max_move=0)
        l.createText(s.waste, "sw")
        s.internals.append(InvisibleStack(self))    # for _swapPairMove()

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def shuffle(self):
        self.shuffleSeparateDecks()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getAutoStacks(self, event=None):
        return ((), (), (self.sg.dropstacks))

    def isGameWon(self):
        for r in self.s.rows:
            if len(r.cards) != 1:
                return False
            c = r.cards[-1]
            if c.suit != r.id / 13 or c.rank != r.id % 13:
                return False
        return True

    #
    # game extras
    #

    def isNeighbour(self, stack1, stack2):
        column1, row1 = stack1.id % 13, stack1.id / 13
        column2, row2 = stack2.id % 13, stack2.id / 13
        return column1 == column2 or row1 == row2

    def getHighlightPilesStacks(self):
        # Pas de Deux special: highlight all moveable cards
        return ((self.s.rows, 1),)


# register the game
registerGame(GameInfo(153, PasDeDeux, "Pas de Deux",
                      GI.GT_MONTANA | GI.GT_SEPARATE_DECKS, 2, 1, GI.SL_MOSTLY_SKILL))

