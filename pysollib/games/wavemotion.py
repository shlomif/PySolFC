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
# // Wave Motion
# ************************************************************************/

class WaveMotion_RowStack(SS_RowStack):
    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()

class WaveMotion(Game):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+8*l.XS, l.YM+2*l.YS+19*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(8):
            stack = WaveMotion_RowStack(x, y, self, base_rank=ANY_RANK)
            s.rows.append(stack)
            x += l.XS
        x, y = l.XM, l.YM+l.YS+12*l.YOFFSET
        for i in range(8):
            stack = OpenStack(x, y, self, max_accept=0)
            s.reserves.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            x += l.XS

        s.talon = InitialDealTalonStack(l.XM, l.YM, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow(rows=self.s.reserves[:4])

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isSameSuitSequence(s.cards):
                    return False
        return True
            
    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1


# register the game
registerGame(GameInfo(314, WaveMotion, "Wave Motion",
                      GI.GT_1DECK_TYPE, 1, 0))
