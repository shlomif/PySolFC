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
# * Buffalo Bill
# * Little Billie
# ************************************************************************

class BuffaloBill(Game):

    #
    # game layout
    #

    def createGame(self, rows=(7, 7, 7, 5)):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+max(max(rows)*(l.XS+3*l.XOFFSET), 9*l.XS), l.YM+(len(rows)+2)*l.YS
        self.setSize(w, h)

        # create stacks
        x, y = l.XM+(w-l.XM-8*l.XS)/2, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 base_rank=KING, suit=i, dir=-1))
            x += l.XS
        n = 0
        y = l.YM+l.YS
        for i in rows:
            x = l.XM
            for j in range(i):
                stack = BasicRowStack(x, y, self, max_move=1, max_accept=0)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                x += l.XS+3*l.XOFFSET
                n += 1
            y += l.YS

        x, y = l.XM+(w-l.XM-8*l.XS)/2, h-l.YS
        for i in range(8):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


class LittleBillie(BuffaloBill):
    def createGame(self):
        #BuffaloBill.createGame(self, rows=(8, 8, 8))
        BuffaloBill.createGame(self, rows=(6,6,6,6))
    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        BuffaloBill.startGame(self)


# register the game
registerGame(GameInfo(338, BuffaloBill, "Buffalo Bill",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(421, LittleBillie, "Little Billie",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))


