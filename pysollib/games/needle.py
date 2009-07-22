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
# * Needle
# * Haystack
# * Pitchfork
# ************************************************************************

class Needle(Game):

    Hint_Class = CautiousDefaultHint
    ReserveStack_Class = StackWrapper(ReserveStack, max_cards=18)

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+max(9*l.XS, 5*l.XS+18*l.XOFFSET), l.YM+2*l.YS+12*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        stack = self.ReserveStack_Class(x, y, self)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
        s.reserves.append(stack)
        self.setRegion(s.reserves, (-999, -999, w-4*l.XS-l.CW/2, l.YM+l.YS-l.CH/2))

        x = w-4*l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS

        x, y = l.XM+(w-(l.XM+9*l.XS))/2, l.YM+l.YS
        for i in range(9):
            s.rows.append(AC_RowStack(x, y, self, max_move=1))
            x += l.XS

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in (4, 4, 3, 3):
            self.s.talon.dealRow(rows=self.s.rows[:i], frames=0)
            self.s.talon.dealRow(rows=self.s.rows[-i:], frames=0)
        self.startDealSample()
        for i in (2, 2, 2, 2):
            self.s.talon.dealRow(rows=self.s.rows[:i])
            self.s.talon.dealRow(rows=self.s.rows[-i:])

    shallHighlightMatch = Game._shallHighlightMatch_AC

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack in self.s.reserves:
            return 0
        return 1+int(len(to_stack.cards) != 0)


class Haystack(Needle):
    ReserveStack_Class = StackWrapper(ReserveStack, max_cards=8)


class Pitchfork(Needle):
    ReserveStack_Class = StackWrapper(OpenStack, max_accept=0)


# register the game
registerGame(GameInfo(318, Needle, "Needle",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(319, Haystack, "Haystack",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(367, Pitchfork, "Pitchfork",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))

