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
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# /***********************************************************************
# // Take Away
# ************************************************************************/

class TakeAway_Foundation(AbstractFoundationStack):

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return True
        c1, c2, mod = self.cards[-1], cards[0], self.cap.mod
        return (c1.rank == (c2.rank + 1) % mod or
                c2.rank == (c1.rank + 1) % mod)

class TakeAway(Game):

    RowStack_Class = BasicRowStack
    Foundation_Class = StackWrapper(TakeAway_Foundation, max_move=0, mod=13)

    #
    # game layout
    #

    def createGame(self, reserves=6):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 2*l.XM+10*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=0))
            x += l.XS
        x += l.XM
        for i in range(6):
            stack = self.Foundation_Class(x, y, self, suit=ANY_SUIT,
                                          base_rank=ANY_RANK)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.foundations.append(stack)
            x += l.XS
        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(10):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow()


# /***********************************************************************
# // Four Stacks
# ************************************************************************/

class FourStacks(TakeAway):
    RowStack_Class = StackWrapper(AC_RowStack, max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS)
    Foundation_Class = StackWrapper(AC_FoundationStack, max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS, dir=-1)


# register the game
registerGame(GameInfo(334, TakeAway, "Take Away",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(335, FourStacks, "Four Stacks",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0))





