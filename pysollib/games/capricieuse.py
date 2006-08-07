##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
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
##---------------------------------------------------------------------------##

__all__ = []

# imports

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

from gypsy import DieRussische_Foundation


# /***********************************************************************
# // Capricieuse
# ************************************************************************/

class Capricieuse(Game):

    Talon_Class = StackWrapper(RedealTalonStack, max_rounds=3)
    RowStack_Class = UD_SS_RowStack

    #
    # game layout
    #

    def createGame(self, **layout):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+12*l.XS, l.YM+2*l.YS+15*l.YOFFSET)

        # create stacks
        x, y, = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x = x + l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            x = x + l.XS
        x, y, = l.XM, y + l.YS
        for i in range(12):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1))
            x = x + l.XS
        s.talon = self.Talon_Class(l.XM, l.YM, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(self.s.foundations)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToBottom(cards,
            lambda c: (c.deck == 0 and c.rank in (0, 12), (c.rank, c.suit)), 8)

    def redealCards(self):
        while self.s.talon.cards:
            self.s.talon.dealRowAvail(frames=4)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# /***********************************************************************
# // Nationale
# ************************************************************************/

class Nationale(Capricieuse):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = StackWrapper(UD_SS_RowStack, mod=13)

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# /***********************************************************************
# // Strata
# ************************************************************************/

class Strata(Game):

    def createGame(self, **layout):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+9*l.XS, l.YM+2*l.YS+12*l.YOFFSET)

        # create stacks
        x, y, = l.XM+l.XS, l.YM
        for i in range(8):
            s.foundations.append(DieRussische_Foundation(x, y, self,
                                 suit=i%4, max_cards=8))
            x = x + l.XS
        x, y, = l.XM+l.XS/2, l.YM+l.YS
        for i in range(8):
            s.rows.append(AC_RowStack(x, y, self, max_move=1, max_accept=1))
            x = x + l.XS
        s.talon = RedealTalonStack(l.XM, l.YM, self, max_rounds=2)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def redealCards(self):
        while self.s.talon.cards:
            self.s.talon.dealRowAvail(frames=4)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# register the game
registerGame(GameInfo(292, Capricieuse, "Capricieuse",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(293, Nationale, "Nationale",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(606, Strata, "Strata",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 1, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12) ))

