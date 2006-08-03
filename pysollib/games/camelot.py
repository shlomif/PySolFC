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

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from numerica import Numerica_Hint


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


# /***********************************************************************
# // Sly Fox
# ************************************************************************/

class SlyFox_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows:
            if len(self.game.s.talon.cards) == 0:
                return True
            return self.game.num_dealled <= 0
        return True


class SlyFox_Talon(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        old_state = self.game.enterState(self.game.S_FILL)
        self.game.saveStateMove(2|16)            # for undo
        if old_state == self.game.S_PLAY and to_stack in self.game.s.rows:
            n = self.game.num_dealled
            if n < 0: n = 0
            self.game.num_dealled = (n+1)%20
        self.game.saveStateMove(1|16)            # for redo
        self.game.leaveState(old_state)
        OpenTalonStack.moveMove(self, ncards, to_stack, frames, shadow)


class SlyFox_RowStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack is self.game.s.talon


class SlyFox(Game):
    Hint_Class = Numerica_Hint

    num_dealled = -1

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+4*l.YS)

        x, y = l.XM, l.YM
        s.talon = SlyFox_Talon(x, y, self)
        s.waste = s.talon
        l.createText(s.talon, 'ne')
        tx, ty, ta, tf = l.getTextAttr(s.talon, "ss")
        font = self.app.getFont("canvas_default")
        self.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)

        y = l.YM
        for i in range(4):
            x = l.XM+1.5*l.XS
            for j in range(5):
                stack = SlyFox_RowStack(x, y, self, max_cards=UNLIMITED_CARDS)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        x, y = self.width-2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SlyFox_Foundation(x, y, self, suit=i))
            s.foundations.append(SlyFox_Foundation(x+l.XS, y, self, suit=i,
                                                   base_rank=KING, dir=-1))
            y += l.YS

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
           lambda c: (c.rank in (ACE, KING) and c.deck == 0, (c.suit, c.rank)))

    def startGame(self):
        self.num_dealled = -1
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.fillStack()

    def _restoreGameHook(self, game):
        self.num_dealled = game.loadinfo.num_dealled

    def _loadGameHook(self, p):
        self.loadinfo.addattr(num_dealled=p.load())

    def _saveGameHook(self, p):
        p.dump(self.num_dealled)

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.num_dealled = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.num_dealled]


    def fillStack(self, stack):
        if self.num_dealled == -1 and stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            self.s.talon.moveMove(1, stack)
            self.leaveState(old_state)


    def updateText(self):
        if self.preview > 1:
            return
        n = self.num_dealled
        if n < 0: n = 0
        text=str(n)+'/20'
        self.texts.misc.config(text=text)


class OpenSlyFox(SlyFox):

    def createGame(self):
        playcards = 6

        l, s = Layout(self), self.s
        self.setSize(l.XM+10*l.XS, l.YM+3*l.YS+2*playcards*l.YOFFSET+l.TEXT_HEIGHT)

        x, y = l.XM, l.YM
        s.talon = SlyFox_Talon(x, y, self)
        s.waste = s.talon
        l.createText(s.talon, 'ne')
        tx, ty, ta, tf = l.getTextAttr(s.talon, "ss")
        font = self.app.getFont("canvas_default")
        self.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)

        x += 2*l.XS
        for i in range(4):
            s.foundations.append(SlyFox_Foundation(x, y, self, suit=i))
            s.foundations.append(SlyFox_Foundation(x+4*l.XS, y, self, suit=i,
                                                   base_rank=KING, dir=-1))
            x += l.XS
        y = l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(2):
            x = l.XM
            for j in range(10):
                stack = SlyFox_RowStack(x, y, self, max_cards=UNLIMITED_CARDS)
                s.rows.append(stack)
                stack.CARD_YOFFSET = l.YOFFSET
                x += l.XS
            y += l.YS+playcards*l.YOFFSET

        l.defaultStackGroups()


# register the game
registerGame(GameInfo(280, Camelot, "Camelot",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(610, SlyFox, "Sly Fox",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(614, OpenSlyFox, "Open Sly Fox",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))

