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
from pysollib.pysoltk import MfxCanvasText

from fortythieves import FortyThieves_Hint
from spider import Spider_Hint


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
        self.setSize(l.XM+8*l.XS, l.YM+3*l.YS+12*l.YOFFSET+l.TEXT_HEIGHT)

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

    shallHighlightMatch = Game._shallHighlightMatch_RK


# /***********************************************************************
# // Lady Palk
# ************************************************************************/

class LadyPalk(Diplomat):
    RowStack_Class = RK_RowStack


# /***********************************************************************
# // Congress
# // Parliament
# ************************************************************************/

class Congress(Diplomat):
    DEAL = (0, 1)
    FILL_EMPTY_ROWS = 1

    Foundation_Classes = [SS_FoundationStack, SS_FoundationStack]

    #
    # game layout (just rearrange the stacks a little bit)
    #

    def createGame(self, max_rounds=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 7*l.XS, l.YM + 4*l.YS)

        # create stacks
        x = l.XM+4*l.XS
        for fnd_cls in self.Foundation_Classes:
            y = l.YM
            for i in range(4):
                s.foundations.append(fnd_cls(x, y, self, suit=i))
                y += l.YS
            x += l.XS
        for i in range(4):
            for j in range(2):
                x, y = l.XM + (3+3*j)*l.XS, l.YM + i*l.YS
                stack = self.RowStack_Class(x, y, self)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
        x, y, = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, "ss")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")
        if max_rounds > 1:
            tx, ty, ta, tf = l.getTextAttr(s.waste, "ne")
            font = self.app.getFont("canvas_default")
            s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                                 tx, ty,
                                                 anchor=ta,
                                                 font=font)

        # define stack-groups
        l.defaultStackGroups()


class Parliament(Congress):

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        Congress.startGame(self)


class Wheatsheaf(Congress):
    Foundation_Classes = [
        SS_FoundationStack,
        StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1),
        ]
    RowStack_Class = UD_SS_RowStack


# /***********************************************************************
# // Rows of Four
# ************************************************************************/

class RowsOfFour(Diplomat):
    def createGame(self):
        Diplomat.createGame(self, max_rounds=3)


# /***********************************************************************
# // Dieppe
# ************************************************************************/

class Dieppe(Diplomat):
    RowStack_Class = RK_RowStack

    def _dealToFound(self):
        talon = self.s.talon
        if not talon.cards:
            return False
        talon.flipMove()
        for f in self.s.foundations:
            if f.acceptsCards(talon, talon.cards[-1:]):
                talon.moveMove(1, f)
                return True
        return False

    def startGame(self):
        self.startDealSample()
        talon = self.s.talon
        for i in range(3):
            for r in self.s.rows:
                while True:
                    if not self._dealToFound():
                        break
                if talon.cards:
                    talon.moveMove(1, r)
        talon.dealCards()


# /***********************************************************************
# // Little Napoleon
# ************************************************************************/

class LittleNapoleon(Diplomat):
    RowStack_Class = Spider_SS_RowStack
    Hint_Class = Spider_Hint

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack.cards:
            return int(from_stack.cards[-1].suit == to_stack.cards[-1].suit)+1
        return 0


# /***********************************************************************
# // Twin Queens
# ************************************************************************/

class TwinQueens(Congress):
    Foundation_Classes = [
        StackWrapper(SS_FoundationStack, base_rank=KING, mod=13),
        StackWrapper(SS_FoundationStack, base_rank=KING, mod=13),
        ]
    RowStack_Class = StackWrapper(SS_RowStack, max_move=1)

    def createGame(self):
        Congress.createGame(self, max_rounds=2)



# register the game
registerGame(GameInfo(149, Diplomat, "Diplomat",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(151, LadyPalk, "Lady Palk",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(150, Congress, "Congress",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(433, RowsOfFour, "Rows of Four",
                      GI.GT_FORTY_THIEVES, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(485, Dieppe, "Dieppe",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(489, LittleNapoleon, "Little Napoleon",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(548, Parliament, "Parliament",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(549, Wheatsheaf, "Wheatsheaf",
                      GI.GT_FORTY_THIEVES, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(563, TwinQueens, "Twin Queens",
                      GI.GT_FORTY_THIEVES, 2, 1, GI.SL_MOSTLY_SKILL))

