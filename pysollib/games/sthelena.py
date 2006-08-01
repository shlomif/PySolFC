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
import sys, types

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
# //
# ************************************************************************/

class StHelena_Talon(TalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds:
            return False
        return not self.game.isGameWon()

    def dealCards(self, sound=0):
        # move all cards to the Talon and redeal
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
        # redeal
        self.cards.reverse()
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


class StHelena_FoundationStack(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.game.s.talon.round == 1:
            if (self.cap.base_rank == KING and
                from_stack in self.game.s.rows[6:10:]):
                return False
            if (self.cap.base_rank == ACE and
                from_stack in self.game.s.rows[:4]):
                return False
        return True


class StHelena(Game):

    Hint_Class = CautiousDefaultHint
    Talon_Class = StackWrapper(StHelena_Talon, max_rounds=3)
    Foundation_Class = StHelena_FoundationStack
    RowStack_Class = StackWrapper(UD_RK_RowStack, base_rank=NO_RANK)

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 3*l.XM+6*l.XS, 3*l.YM+4*l.YS
        self.setSize(w, h)

        # create stacks
        lay = (
            (2, 1, 1, 0),
            (2, 2, 1, 0),
            (2, 3, 1, 0),
            (2, 4, 1, 0),
            (3, 5, 2, 1),
            (3, 5, 2, 2),
            (2, 4, 3, 3),
            (2, 3, 3, 3),
            (2, 2, 3, 3),
            (2, 1, 3, 3),
            (1, 0, 2, 2),
            (1, 0, 2, 1),
            )
        for xm, xs, ym, ys in lay:
            x, y = xm*l.XM+xs*l.XS, ym*l.YM+ys*l.YS
            stack = self.RowStack_Class(x, y, self, max_move=1, max_accept=1)
            stack.CARD_XOFFSET = stack.CARD_YOFFSET = 0
            s.rows.append(stack)
        x, y = 2*l.XM+l.XS, 2*l.YM+l.YS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i,
                                                       base_rank=KING, dir=-1))
            x = x + l.XS
        x, y = 2*l.XM+l.XS, 2*l.YM+2*l.YS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
            x = x + l.XS

        s.talon = self.Talon_Class(l.XM, l.YM, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.deck == 0 and c.rank in (0, 12), (-c.rank, c.suit)), 8)

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(self.s.foundations)

    shallHighlightMatch = Game._shallHighlightMatch_RK

# /***********************************************************************
# // Box Kite
# ************************************************************************/

class BoxKite(StHelena):
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = StackWrapper(UD_RK_RowStack, base_rank=NO_RANK, mod=13)

    shallHighlightMatch = Game._shallHighlightMatch_RKW



# register the game
registerGame(GameInfo(302, StHelena, "St. Helena",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED,
                      altnames=("Napoleon's Favorite",
                                "Washington's Favorite")
                      ))
registerGame(GameInfo(408, BoxKite, "Box Kite",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))

