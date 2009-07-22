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
# * Heads and Tails
# ************************************************************************

class HeadsAndTails_Reserve(OpenStack):
    def canFlipCard(self):
        return False


class HeadsAndTails(Game):
    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        h = l.YS + 7*l.YOFFSET
        self.setSize(l.XM+10*l.XS, l.YM+l.YS+2*h)

        # create stacks
        x, y = self.width - l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        x, y = l.XM+l.XS, l.YM
        for i in range(8):
            s.rows.append(SS_RowStack(x, y, self,
                          dir=1, max_move=1, max_accept=1))
            x += l.XS
        x, y = l.XM+l.XS, l.YM+l.YS+h
        for i in range(8):
            s.rows.append(SS_RowStack(x, y, self,
                          dir=-1, max_move=1, max_accept=1))
            x += l.XS

        x, y = l.XM+l.XS, l.YM+h
        for i in range(8):
            stack = HeadsAndTails_Reserve(x, y, self)
            s.reserves.append(stack)
            l.createText(stack, "n")
            x += l.XS

        x, y = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            y += l.YS
        x, y = l.XM+9*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=i, base_rank=KING, dir=-1))
            y += l.YS

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(11):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            reserves = self.s.reserves
            si = list(self.s.rows).index(stack)%8
            from_stack = None
            if reserves[si].cards:
                from_stack = reserves[si]
            else:
                for i in range(1, 8):
                    n = si+i
                    if n < 8 and reserves[n].cards:
                        from_stack = reserves[n]
                        break
                    n = si-i
                    if n >= 0 and reserves[n].cards:
                        from_stack = reserves[n]
                        break
            if not from_stack:
                return
            old_state = self.enterState(self.S_FILL)
            from_stack.flipMove()
            from_stack.moveMove(1, stack)
            self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Barrier
# ************************************************************************


class Barrier_ReserveStack(OpenStack):
    def canFlipCard(self):
        return False


class Barrier(Game):

    def createGame(self):
        reserves = 8
        rows = 10
        max_rows = max(8, rows, reserves)

        l, s = Layout(self), self.s
        self.setSize(l.XM+max_rows*l.XS, l.YM+4*l.YS+12*l.YOFFSET)

        s.addattr(reserves2=[])         # register extra stack variables

        x, y = l.XM+(max_rows-reserves)*l.XS/2+l.XS/2, l.YM
        for i in range(reserves/2):
            stack = Barrier_ReserveStack(x, y, self)
            s.reserves2.append(stack)
            l.createText(stack, "ne")
            x += 2*l.XS
        x, y = l.XM+(max_rows-reserves)*l.XS/2, l.YM+l.YS
        for i in range(reserves):
            s.reserves.append(OpenStack(x, y, self))
            x += l.XS
        x, y = l.XM+(max_rows-rows)*l.XS/2, l.YM+2*l.YS
        for i in range(rows):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS
        x, y = l.XM+(max_rows-8)*l.XS/2, self.height-l.YS
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS
        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        l.defaultStackGroups()

    def startGame(self):
        rows = len(self.s.rows)
        reserves = len(self.s.reserves)
        n = (104-reserves-2*rows)/(reserves/2)
        for i in range(n):
            self.s.talon.dealRow(rows=self.s.reserves2, frames=0, flip=0)
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.reserves and not stack.cards:
            si = list(self.s.reserves).index(stack)
            from_stack = self.s.reserves2[si/2]
            if not from_stack.cards:
                return
            old_state = self.enterState(self.S_FILL)
            from_stack.flipMove()
            from_stack.moveMove(1, stack)
            self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# register the game

registerGame(GameInfo(307, HeadsAndTails, "Heads and Tails",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(708, Barrier, "Barrier",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED))

