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
# // Simplex
# ************************************************************************/

def isSameRankSequence(cards):
    c0 = cards[0]
    for c in cards[1:]:
        if c0.rank != c.rank:
            return False
    return True


class Simplex_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if len(cards) != 4:
            return False
        return isSameRankSequence(cards)


class Simplex_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isSameRankSequence(cards)


class Simplex(Game):

    def createGame(self, reserves=6):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+10*l.XS, l.YM+2*l.YS+9*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        x += l.XS
        s.waste = WasteStack(x, y, self)
        x += l.XS
        stack = Simplex_Foundation(x, y, self,
                    suit=ANY_SUIT, base_rank=ANY_RANK, max_cards=52)
        xoffset = (self.width-3*l.XS)/51
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = xoffset, 0
        s.foundations.append(stack)
        x, y = l.XM, l.YM+l.YS
        for i in range(9):
            s.rows.append(Simplex_RowStack(x, y, self))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank


# register the game
registerGame(GameInfo(436, Simplex, "Simplex",
                      GI.GT_1DECK_TYPE, 1, 0))
