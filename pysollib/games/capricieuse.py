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
# // Capricieuse
# ************************************************************************/

class Capricieuse_Talon(TalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds:
            return False
        return not self.game.isGameWon()

    def dealCards(self, sound=0):
        # move all cards to the Talon, shuffle and redeal
        lr = len(self.game.s.rows)
        num_cards = 0
        assert len(self.cards) == 0
        for r in self.game.s.rows[::-1]:
            for i in range(len(r.cards)):
                num_cards = num_cards + 1
                self.game.moveMove(1, r, self, frames=0)
        assert len(self.cards) == num_cards
        if num_cards == 0:          # game already finished
            return 0
        # shuffle
        self.game.shuffleStackMove(self)
        # redeal
        self.game.nextRoundMove(self)
        self.game.startDealSample()
        for i in range(lr):
            k = min(lr, len(self.cards))
            for j in range(k):
                self.game.moveMove(1, self, self.game.s.rows[j], frames=4)
        # done
        self.game.stopSamples()
        assert len(self.cards) == 0
        return num_cards


class Capricieuse(Game):

    Talon_Class = StackWrapper(Capricieuse_Talon, max_rounds=3)
    RowStack_Class = UD_SS_RowStack

    #
    # game layout
    #

    def createGame(self, **layout):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+12*l.XS, l.YM+l.YS+20*l.YOFFSET)

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
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.deck == 0 and c.rank in (0, 12), (c.rank, c.suit)), 8)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % stack1.cap.mod == card2.rank or
                 (card2.rank + 1) % stack1.cap.mod == card1.rank))


# /***********************************************************************
# // Nationale
# ************************************************************************/

class Nationale(Capricieuse):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = StackWrapper(UD_SS_RowStack, mod=13)


# register the game
registerGame(GameInfo(292, Capricieuse, "Capricieuse",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(293, Nationale, "Nationale",
                      GI.GT_BAKERS_DOZEN | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))

