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
# * Parallels
# * British Blockade
# ************************************************************************

class Parallels_RowStack(BasicRowStack):
    def basicIsBlocked(self):
        index = self.index
        rows = self.game.s.rows
        if index < 10:
            return False
        if not rows[index-10].cards:
            return False
        if index >= 60: # last row
            return False
        if not rows[index+10].cards:
            return False
        return True


class Parallels_TalonStack(DealRowTalonStack):
    def dealCards(self, sound=False):
        return self.dealRow(sound=sound)

    def dealRow(self, rows=None, flip=1, reverse=0, frames=-1, sound=False):
        if not rows is None:
            return DealRowTalonStack.dealRowAvail(self, rows=rows, flip=flip,
                       reverse=reverse, frames=frames, sound=sound)
        rows = self.game.s.rows
        for r in rows[:10]:
            if not r.cards:
                return self._fillRow(frames=frames, sound=sound)
        column_ncards = []
        for i in range(10):
            column = [r for r in rows[i::10] if r.cards]
            column_ncards.append(len(column))
        max_col = max(column_ncards)
        if max(column_ncards) != min(column_ncards):
            return self._fillRow(frames=frames, sound=sound)
        r = rows[max_col*10:max_col*10+10]
        return DealRowTalonStack.dealRowAvail(self, rows=r, flip=flip,
                   reverse=reverse, frames=frames, sound=sound)

    def _fillRow(self, frames=-1, sound=False):
        rows = self.game.s.rows
        column_ncards = []
        for i in range(10):
            column = [r for r in rows[i::10] if r.cards]
            column_ncards.append(len(column))
        max_col = max(column_ncards)
        max_col = max(max_col, 1)
        n = 0
        rr = self.game.s.rows[:max_col*10]
        while True:
            filled = False
            for i in range(10):
                prev_s = None
                for s in rr[i::10]:
                    if not self.cards:
                        filled = False
                        break
                    if s.cards:
                        if prev_s:
                            DealRowTalonStack.dealRow(self, rows=[prev_s],
                                              frames=frames, sound=sound)
                            n += 1
                            filled = True
                        break
                    prev_s = s
            if not filled:
                break
        while True:
            filled = False
            for i in range(10):
                for s in rr[i::10]:
                    if not self.cards:
                        filled = False
                        break
                    if not s.cards:
                        DealRowTalonStack.dealRow(self, rows=[s],
                                          frames=frames, sound=sound)
                        n += 1
                        filled = True
                        break
            if not filled:
                break

        return n


class Parallels(Game):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        # set window
        self.setSize(l.XM+12*l.XS, l.YM+7*l.YS)
        # create stacks
        s.talon = Parallels_TalonStack(l.XM, l.YM, self)
        l.createText(s.talon, 's')
        n = 0
        y = l.YM
        for i in range(7):
            x = l.XM+l.XS
            for j in range(10):
                stack = Parallels_RowStack(x, y, self, max_accept=0)
                stack.index = n
                s.rows.append(stack)
                n += 1
                x += l.XS
            y += l.YS
        x, y = l.XM, l.YM+l.YS+l.YS/2
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            y += l.YS
        x, y = l.XM+11*l.XS, l.YM+l.YS+l.YS/2
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            y += l.YS

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (ACE, KING) and c.deck == 0,
                              (c.rank, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:10])


class BritishBlockade(Parallels):

    def fillStack(self, stack):
        if not stack.cards and stack in self.s.rows:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)


# register the game
registerGame(GameInfo(428, Parallels, "Parallels",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(615, BritishBlockade, "British Blockade",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))





