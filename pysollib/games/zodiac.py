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
# // Zodiac
# ************************************************************************/

class Zodiac_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.game.s.waste.cards or self.game.s.talon.cards:
            return False
        return True


class Zodiac_RowStack(UD_SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not UD_SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows:
            return False
        return True

class Zodiac_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows:
            return False
        return True



class Zodiac(Game):

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+12*l.XS, l.YM+5*l.YS
        self.setSize(w, h)

        # create stacks
        x = l.XM
        for i in range(12):
            for y in (l.YM, l.YM+4*l.YS):
                stack = Zodiac_RowStack(x, y, self, base_rank=NO_RANK)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            x += l.XS

        x = l.XM+4*l.XS
        for i in range(4):
            y = l.YM+l.YS
            s.foundations.append(Zodiac_Foundation(x, y, self, suit=i))
            y += 2*l.YS
            s.foundations.append(Zodiac_Foundation(x, y, self, suit=i,
                                                   base_rank=KING, dir=-1))
            x += l.XS

        x, y = l.XM+2*l.XS, l.YM+2*l.YS
        for i in range(8):
            s.reserves.append(Zodiac_ReserveStack(x, y, self))
            x += l.XS

        x, y = l.XM+l.XS, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=UNLIMITED_REDEALS)
        l.createText(s.talon, 'sw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    shallHighlightMatch = Game._shallHighlightMatch_SS


# register the game
registerGame(GameInfo(467, Zodiac, "Zodiac",
                      GI.GT_2DECK_TYPE, 2, -1, GI.SL_BALANCED))
