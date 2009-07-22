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
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint


# ************************************************************************
# * Labyrinth
# ************************************************************************

class Labyrinth_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        top_stacks = []
        for i in range(8):
            for r in self.game.s.rows[i::8]:
                if not r.cards:
                    top_stacks.append(r)
                    break
        return self.dealRowAvail(rows=top_stacks, sound=sound)

class Labyrinth_RowStack(BasicRowStack):

    def clickHandler(self, event):
        BasicRowStack.doubleclickHandler(self, event)
        return True

    def basicIsBlocked(self):
        if self in self.game.s.rows[:8]:
            return False
        if self.id+8 >= len(self.game.allstacks):
            return False
        r = self.game.allstacks[self.id+8]
        if r in self.game.s.rows and r.cards:
            return True
        return False



class Labyrinth(Game):

    #
    # game layout
    #

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+8*l.XS, l.YM+l.YS+20*l.YOFFSET)

        # create stacks
        s.talon = Labyrinth_Talon(l.XM, l.YM, self)

        x, y, = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS

        x, y = l.XM, l.YM+l.YS
        for i in range(6):
            x = l.XM
            for j in range(8):
                s.rows.append(Labyrinth_RowStack(x, y, self, max_move=1))
                x += l.XS
            y += l.YOFFSET

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow(rows=self.s.rows[:8])


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def fillStack(self, stack):
        if stack in self.s.rows[:8] and not stack.cards:
            rows = self.s.rows
            to_stack = stack
            #if not self.demo:
            #    self.startDealSample()
            old_state = self.enterState(self.S_FILL)
            for r in rows[list(rows).index(stack)+8::8]:
                if r.cards:
                    self.moveMove(1, r, to_stack, frames=0)
                    to_stack = r
                else:
                    break
            if not stack.cards and self.s.talon.cards:
                self.s.talon.dealRow(rows=[stack])
            self.leaveState(old_state)
            #if not self.demo:
            #    self.stopSamples()


# register the game

#registerGame(GameInfo(400, Labyrinth, "Labyrinth",
#                      GI.GT_1DECK_TYPE, 1, 0))

