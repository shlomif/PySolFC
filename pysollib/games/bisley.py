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
# // Bisley
# ************************************************************************/

class Bisley(Game):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 2*l.XM+8*l.XS, max(2*(l.YM+l.YS+8*l.YOFFSET), l.YM+5*l.YS)
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(6):
            s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS
        x, y = l.XM, l.YM+l.YS+8*l.YOFFSET
        for i in range(6):
            s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS
        y = l.YM
        for i in range(4):
            x = l.XM+6*l.XS+l.XM
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_move=0))
            x += l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i,
                                 base_rank=KING, max_move=0, dir=-1))
            y += l.YS

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
        self.s.talon.dealRow(rows=self.s.foundations[::2])

    def _shuffleHook(self, cards):
        # move Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == ACE, c.suit))

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1


# /***********************************************************************
# // Double Bisley
# ************************************************************************/

class DoubleBisley(Bisley):

    Hint_Class = CautiousDefaultHint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+(8+4)*l.XS, l.YM+max(3*(l.YS+8*l.YOFFSET), 8*l.YS)
        self.setSize(w, h)

        # create stacks
        y = l.YM
        for i in range(3):
            x = l.XM
            for j in range(8):
                s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
                x += l.XS
            y += l.YS+8*l.YOFFSET

        y = l.YM
        for j in range(2):
            for i in range(4):
                x = l.XM+8*l.XS
                s.foundations.append(SS_FoundationStack(x, y, self,
                                     suit=j*2+i/2, max_move=0))
                x += l.XS
                s.foundations.append(SS_FoundationStack(x, y, self,
                     suit=j*2+i/2, base_rank=KING, max_move=0, dir=-1))
                y += l.YS

        s.talon = InitialDealTalonStack(l.XM, h-l.YS, self)

        # default
        l.defaultAll()


# /***********************************************************************
# // Gloria
# ************************************************************************/

class Gloria(Game):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+12*l.XS, l.YM+2*l.YS+2*(l.YS+5*l.YOFFSET)
        self.setSize(w, h)

        # create stacks
        y = l.YM+2*l.YS
        for i in range(2):
            x = l.XM
            for j in range(12):
                s.rows.append(BasicRowStack(x, y, self, max_accept=0))
                x += l.XS
            y += l.YS+5*l.YOFFSET

        x = l.XM+2*l.XS
        for j in range(2):
            for i in range(4):
                y = l.YM
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j*2+i/2))
                y += l.YS
                s.foundations.append(SS_FoundationStack(x, y, self,
                                     suit=j*2+i/2, base_rank=KING, dir=-1))
                x += l.XS

        s.reserves.append(ReserveStack(l.XM, l.YM, self))
        s.reserves.append(ReserveStack(w-l.XS, l.YM, self))

        s.talon = InitialDealTalonStack(l.XM, l.YM+l.YS, self)

        # default
        l.defaultAll()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations[1::2])

    def _shuffleHook(self, cards):
        # move Kings to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == KING, c.suit))


# /***********************************************************************
# // Realm
# // Mancunian
# ************************************************************************/

class Realm(Game):

    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(UD_AC_RowStack, base_rank=NO_RANK)

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+8*l.XS, l.YM+2*l.YS+15*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = 2*l.XM, l.YM+l.YS
        for i in range(8):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        y = l.YM
        for i in range(4):
            x = l.XM+i*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_move=0))
            x += 2*l.XM+4*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i,
                                 base_rank=KING, max_move=0, dir=-1))

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.color != card2.color and abs(card1.rank-card2.rank) == 1


class Mancunian(Realm):
    RowStack_Class = StackWrapper(UD_RK_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank-card2.rank) == 1


# register the game
registerGame(GameInfo(290, Bisley, "Bisley",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(372, DoubleBisley, "Double Bisley",
                      GI.GT_2DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0))
registerGame(GameInfo(373, Gloria, "Gloria",
                      GI.GT_2DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0))
registerGame(GameInfo(374, Realm, "Realm",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0))
registerGame(GameInfo(375, Mancunian, "Mancunian",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0))

