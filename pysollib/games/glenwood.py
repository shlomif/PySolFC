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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from canfield import Canfield_Hint

# /***********************************************************************
# // Glenwood
# ************************************************************************/

class Glenwood_Talon(WasteTalonStack):
    def canDealCards(self):
        if self.game.base_rank is None:
            return False
        return WasteTalonStack.canDealCards(self)

class Glenwood_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if self.game.base_rank is None:
            return 1
        if not self.cards:
            return cards[-1].rank == self.game.base_rank
        # check the rank
        return (self.cards[-1].rank + self.cap.dir) % self.cap.mod == cards[0].rank

class Glenwood_RowStack(AC_RowStack):
    def canMoveCards(self, cards):
        if self.game.base_rank is None:
            return False
        if not AC_RowStack.canMoveCards(self, cards):
            return False
        if len(cards) == 1 or len(self.cards) == len(cards):
            return True
        return False

    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards and from_stack is self.game.s.waste:
            for stack in self.game.s.reserves:
                if stack.cards:
                    return False
            return True
        if from_stack in self.game.s.rows and len(cards) != len(from_stack.cards):
            return False
        return True


class Glenwood_ReserveStack(OpenStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        OpenStack.moveMove(self, ncards, to_stack, frames, shadow)
        if self.game.base_rank is None and to_stack in self.game.s.foundations:
            old_state = self.game.enterState(self.game.S_FILL)
            self.game.saveStateMove(2|16)            # for undo
            self.game.base_rank = to_stack.cards[-1].rank
            self.game.saveStateMove(1|16)            # for redo
            self.game.leaveState(old_state)


class Glenwood(Game):

    Foundation_Class = Glenwood_Foundation
    RowStack_Class = Glenwood_RowStack
    ReserveStack_Class = Glenwood_ReserveStack #OpenStack
    Hint_Class = Canfield_Hint

    base_rank = None

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS + l.XM, 3*l.YM + 5*l.YS)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = Glenwood_Talon(x, y, self, max_rounds=2, num_deal=1)
        l.createText(s.talon, "ss")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")
        for i in range(4):
            x = 2*l.XM + (i+2)*l.XS
            s.foundations.append(self.Foundation_Class(x, y, self, i, dir=1,
                                 mod=13, base_rank=ANY_RANK, max_move=0))

        tx, ty, ta, tf = l.getTextAttr(None, "se")
        tx, ty = x + tx + l.XM, y + ty
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx, ty, anchor=ta, font=font)

        for i in range(4):
            x = 2*l.XM + (i+2)*l.XS
            y = 3*l.YM + l.YS
            s.rows.append(self.RowStack_Class(x, y, self, mod=13))
        for i in range(4):
            x = l.XM
            y = 3*l.YM + (i+1)*l.YS
            stack = self.ReserveStack_Class(x, y, self)
            s.reserves.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.base_rank = None
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    #
    # game extras
    #

    def updateText(self):
        if self.preview > 1:
            return
        if self.base_rank is None:
            t = ""
        else:
            t = RANKS[self.base_rank]
        self.texts.info.config(text=t)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color
                and ((card1.rank + 1) % 13 == card2.rank
                     or (card2.rank + 1) % 13 == card1.rank))

    def _restoreGameHook(self, game):
        self.base_rank = game.loadinfo.base_rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_rank=p.load())

    def _saveGameHook(self, p):
        p.dump(self.base_rank)

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.base_rank = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.base_rank]


# register the game
registerGame(GameInfo(282, Glenwood, "Glenwood",
                      GI.GT_CANFIELD, 1, 1))

