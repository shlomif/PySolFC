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

from pysollib.games.fortythieves import FortyThieves_Hint

# /***********************************************************************
# // Diplomat
# ************************************************************************/

class Diplomat(Game):
    Foundation_Class = SS_FoundationStack
    RowStack_Class = StackWrapper(RK_RowStack, max_move=1)
    Hint_Class = FortyThieves_Hint

    DEAL = (3, 1)
    FILL_EMPTY_ROWS = 0

    #
    # game layout
    #

    def createGame(self, max_rounds=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS, l.YM + 5*l.YS)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i/2))
            x = x + l.XS
        x, y = l.XM, y + l.YS
        for i in range(8):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        x, y, = l.XM, self.height - l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, "nn")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "nn")

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def startGame(self):
        for i in range(self.DEAL[0]):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(self.DEAL[1]):
            self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if self.FILL_EMPTY_ROWS and stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            elif self.s.talon.canDealCards():
                self.s.talon.dealCards()
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank


# /***********************************************************************
# // Lady Palk
# ************************************************************************/

class LadyPalk(Diplomat):
    RowStack_Class = RK_RowStack


# /***********************************************************************
# // Congress
# ************************************************************************/

class Congress(Diplomat):
    DEAL = (0, 1)
    FILL_EMPTY_ROWS = 1

    #
    # game layout (just rearrange the stacks a little bit)
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 7*l.XS, l.YM + 4*l.YS)

        # create stacks
        for i in range(4):
            for j in range(2):
                x, y = l.XM + (4+j)*l.XS, l.YM + i*l.YS
                s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
        for i in range(4):
            for j in range(2):
                x, y = l.XM + (3+3*j)*l.XS, l.YM + i*l.YS
                stack = self.RowStack_Class(x, y, self)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
        x, y, = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "ss")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")

        # define stack-groups
        l.defaultStackGroups()


# /***********************************************************************
# // Rows of Four
# ************************************************************************/

class RowsOfFour(Diplomat):
    def createGame(self):
        Diplomat.createGame(self, max_rounds=3)


# register the game
registerGame(GameInfo(149, Diplomat, "Diplomat",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(151, LadyPalk, "Lady Palk",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(150, Congress, "Congress",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(433, RowsOfFour, "Rows of Four",
                      GI.GT_FORTY_THIEVES, 2, 2))

