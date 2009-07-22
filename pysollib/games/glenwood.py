#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

# ************************************************************************
# * Glenwood
# ************************************************************************

class Glenwood_Talon(WasteTalonStack):
    def canDealCards(self):
        if self.game.base_rank is None:
            return False
        return WasteTalonStack.canDealCards(self)

class Glenwood_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.game.base_rank is None:
            return True
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
            return False
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
    ReserveStack_Class = Glenwood_ReserveStack
    Hint_Class = Canfield_Hint

    base_rank = None

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 7*l.XS, l.YM + l.TEXT_HEIGHT + 5*l.YS)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = Glenwood_Talon(x, y, self, max_rounds=2, num_deal=1)
        l.createText(s.talon, "s")
        l.createRoundText(s.talon, 'ne', dx=l.XS)
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")
        x += 2*l.XS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, i, dir=1,
                                 mod=13, base_rank=ANY_RANK, max_move=0))
            x += l.XS

        tx, ty, ta, tf = l.getTextAttr(None, "ss")
        tx, ty = x - l.XS + tx, y + ty
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)

        for i in range(4):
            x = l.XM + (i+3)*l.XS
            y = l.YM+l.TEXT_HEIGHT+l.YS
            s.rows.append(self.RowStack_Class(x, y, self, mod=13))
        for i in range(4):
            x = l.XM
            y = l.YM+l.TEXT_HEIGHT+(i+1)*l.YS
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

    shallHighlightMatch = Game._shallHighlightMatch_ACW

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


# ************************************************************************
# * Double Fives
# ************************************************************************

class DoubleFives_Talon(RedealTalonStack):

    def moveToStock(self):
        stock = self.game.s.stock
        for r in self.game.s.reserves[:5]:
            if r.cards:
                r.moveMove(1, stock)
                stock.flipMove()

    def canDealCards(self):
        if self.game.base_rank is None:
            return False
        if self.round == self.max_rounds:
            return len(self.cards) != 0
        return not self.game.isGameWon()

    def dealCards(self, sound=False):
        old_state = self.game.enterState(self.game.S_DEAL)
        num_cards = 0
        if self.round == 1:
            if sound:
                self.game.startDealSample()
            self.moveToStock()
            if not self.cards:
                num_cards += self.redealCards(rows=[self.game.s.stock],
                                              frames=4, sound=False)
            else:
                num_cards += self.dealRowAvail(rows=self.game.s.reserves[:5],
                                               sound=False)
            if sound:
                self.game.stopSamples()
        else:
            if sound and not self.game.demo:
                self.game.playSample("dealwaste")
            self.game.flipMove(self)
            self.game.moveMove(1, self, self.game.s.reserves[0],
                               frames=4, shadow=0)
            num_cards += 1
        self.game.leaveState(old_state)
        return num_cards


class DoubleFives_RowStack(SS_RowStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        SS_RowStack.moveMove(self, ncards, to_stack, frames, shadow)
        if self.game.base_rank is None and to_stack in self.game.s.foundations:
            old_state = self.game.enterState(self.game.S_FILL)
            self.game.saveStateMove(2|16)            # for undo
            self.game.base_rank = to_stack.cards[-1].rank
            self.game.saveStateMove(1|16)            # for redo
            self.game.leaveState(old_state)


class DoubleFives_WasteStack(WasteStack):
    def updateText(self):
        if self.game.s.talon.round == 2:
            WasteStack.updateText(self)
        elif self.texts.ncards:
            self.texts.ncards.config(text='')


class DoubleFives_Stock(WasteStack):
    def canFlipCard(self):
        return False
    def updateText(self):
        if self.cards:
            WasteStack.updateText(self)
        else:
            self.texts.ncards.config(text='')


class DoubleFives(Glenwood):
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+11*l.XS, l.YM+3*l.YS+16*l.YOFFSET)

        # create stacks
        #
        x, y = l.XM, self.height-l.YS
        s.talon = DoubleFives_Talon(x, y, self, max_rounds=2, num_deal=1)
        l.createText(s.talon, "n")
        l.createRoundText(self.s.talon, 'nnn')
        x += l.XS
        for i in range(5):
            s.reserves.append(DoubleFives_WasteStack(x, y, self))
            x += l.XS
        l.createText(s.reserves[0], 'n')
        #
        x = self.width-l.XS
        s.addattr(stock=None)      # register extra stack variable
        s.stock = DoubleFives_Stock(x, y, self)
        l.createText(s.stock, "n")
        #
        x, y = l.XM, l.YM
        s.reserves.append(Glenwood_ReserveStack(x, y, self))
        x += l.XS
        s.reserves.append(Glenwood_ReserveStack(x, y, self))
        #
        x += 2*l.XS
        for i in range(8):
            s.foundations.append(Glenwood_Foundation(x, y, self, suit=i/2,
                                 mod=13, base_rank=ANY_RANK, max_move=0))
            x += l.XS
        tx, ty, ta, tf = l.getTextAttr(None, "ss")
        tx, ty = x - l.XS + tx, y + ty
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)
        x, y = l.XM+l.XS/2, l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(10):
            s.rows.append(DoubleFives_RowStack(x, y, self, mod=13, max_move=1))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.deck == 0, None))

    def startGame(self):
        self.base_rank = None
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves[-2:])

    def _autoDeal(self, sound=True):
        waste_cards = 0
        for r in self.s.reserves[:5]:
            waste_cards += len(r.cards)
        if waste_cards == 0 and self.canDealCards():
            return self.dealCards(sound=sound)
        return 0

    shallHighlightMatch = Game._shallHighlightMatch_SSW



# register the game
registerGame(GameInfo(282, Glenwood, "Dutchess",
                      GI.GT_CANFIELD, 1, 1, GI.SL_BALANCED,
                      altnames=("Duchess", "Glenwood",) ))
registerGame(GameInfo(587, DoubleFives, "Double Fives",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_BALANCED))

