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


# /***********************************************************************
# // Camelot
# ************************************************************************/

class Camelot_Hint(AbstractHint):

    def computeHints(self):
        game = self.game
        if game.is_fill:
            nhints = 0
            i = 0
            for r in game.s.rows:
                i += 1
                if not r.cards:
                    continue
                if r.cards[0].rank == 9:
                    self.addHint(5000, 1, r, game.s.foundations[0])
                    nhints += 1
                    continue
                for t in game.s.rows[i:]:
                    if t.acceptsCards(r, [r.cards[0]]):
                        self.addHint(5000, 1, r, t)
                        nhints += 1
            if nhints:
                return
        if game.s.talon.cards:
            for r in game.s.rows:
                if r.acceptsCards(game.s.talon, [game.s.talon.cards[-1]]):
                    self.addHint(5000, 1, game.s.talon, r)


class Camelot_RowStack(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if from_stack is self.game.s.talon:
            if len(self.cards) > 0:
                return False
            cr = cards[0].rank
            if cr == KING:
                return self.id in (0, 3, 12, 15)
            elif cr == QUEEN:
                return self.id in (1, 2, 13, 14)
            elif cr == JACK:
                return self.id in (4, 7, 8, 11)
            return True
        else:
            if len(self.cards) == 0:
                return False
            return self.cards[-1].rank + cards[0].rank == 8

    def canMoveCards(self, cards):
        if not self.game.is_fill:
            return False
        return cards[0].rank not in (KING, QUEEN, JACK)

    def clickHandler(self, event):
        game = self.game
        if game.is_fill and self.cards and self.cards[0].rank == 9:
            game.playSample("autodrop", priority=20)
            self.playMoveMove(1, game.s.foundations[0], sound=0)
            self.fillStack()
            return True
        return False

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if not to_stack is self.game.s.foundations[0]:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            ReserveStack.moveMove(self, ncards, to_stack, frames=frames, shadow=shadow)

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2|16)            # for undo
        if not game.demo:
            game.playSample("droppair", priority=200)
        game.moveMove(n, self, f, frames=frames, shadow=shadow)
        game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.fillStack()
        other_stack.fillStack()
        game.updateStackMove(game.s.talon, 1|16)            # for redo
        game.leaveState(old_state)


class Camelot_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        return True


class Camelot_Talon(OpenTalonStack):
    def fillStack(self):
        old_state = self.game.enterState(self.game.S_FILL)
        self.game.saveStateMove(2|16)            # for undo
        self.game.is_fill = self.game.isRowsFill()
        self.game.saveStateMove(1|16)            # for redo
        self.game.leaveState(old_state)
        OpenTalonStack.fillStack(self)


class Camelot(Game):

    Talon_Class = Camelot_Talon
    RowStack_Class = StackWrapper(Camelot_RowStack, max_move=0)
    Hint_Class = Camelot_Hint

    # game variables
    is_fill = False

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        # set window
        w = l.XS
        self.setSize(l.XM + w + 4*l.XS + w + l.XS, l.YM + 4*l.YS)
        # create stacks
        for i in range(4):
            for j in range(4):
                k = i+j*4
                x, y = l.XM + w + j*l.XS, l.YM + i*l.YS
                s.rows.append(self.RowStack_Class(x, y, self))
        x, y = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        x, y = l.XM + w + 4*l.XS + w, l.YM
        s.foundations.append(Camelot_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_accept=0, max_move=0, max_cards=52))
        # define stack-groups
        l.defaultStackGroups()
        return l

    #
    # game overrides
    #

    def startGame(self):
        self.is_fill = False
        self.nnn = 0
        self.s.talon.fillStack()


    def isGameWon(self):
        for i in (5, 6, 9, 10):
            if len(self.s.rows[i].cards) != 0:
                return False
        return len(self.s.talon.cards) == 0


    def isRowsFill(self):
        for i in range(16):
            if len(self.s.rows[i].cards) == 0:
                return False
        return True

    def _restoreGameHook(self, game):
        self.is_fill = game.loadinfo.is_fill

    def _loadGameHook(self, p):
        self.loadinfo.addattr(is_fill=p.load())

    def _saveGameHook(self, p):
        p.dump(self.is_fill)

    def getAutoStacks(self, event=None):
        return ((), (), ())

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.is_fill = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.is_fill]



# register the game
registerGame(GameInfo(280, Camelot, "Camelot",
                      GI.GT_1DECK_TYPE, 1, 0))

