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
from pysollib.pysoltk import MfxCanvasText


# /***********************************************************************
# // Heads and Tails
# ************************************************************************/

class HeadsAndTails_Reserve(TalonStack):
    def clickHandler(self, event):
        # no deal
        return True


class HeadsAndTails(Game):

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
            from_stack.moveMove(1, stack)
            #stack.flipMove()
            self.leaveState(old_state)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.suit == card2.suit and abs(card1.rank - card2.rank) == 1


# register the game

registerGame(GameInfo(307, HeadsAndTails, "Heads and Tails",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))



