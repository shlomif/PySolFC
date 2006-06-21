## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
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
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
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
from pysollib.pysoltk import MfxCanvasText

from pysollib.games.braid import Braid_Foundation


# /***********************************************************************
# // stacks
# ************************************************************************/

class Napoleon_Talon(InitialDealTalonStack):
    pass


class Napoleon_Foundation(Braid_Foundation):
    pass


class Napoleon_RowStack(UD_SS_RowStack):
    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class Napoleon_ReserveStack(BasicRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=0)
        apply(BasicRowStack.__init__, (self, x, y, game), cap)


class Napoleon_SingleFreeCell(ReserveStack):
    def acceptsCards(self, from_stack, cards):
##        if from_stack.id >= 8:
##            # from_stack must be a Napoleon_RowStack
##            return 0
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def canMoveCards(self, cards):
        if self.game.s.rows[8].cards and self.game.s.rows[9].cards:
            return 0
        return ReserveStack.canMoveCards(self, cards)


class Napoleon_FreeCell(ReserveStack):
    def canMoveCards(self, cards):
        if self.game.s.rows[self.id-2].cards:
            return 0
        return ReserveStack.canMoveCards(self, cards)


# /***********************************************************************
# // Der kleine Napoleon
# ************************************************************************/

class DerKleineNapoleon(Game):

    RowStack_Class = StackWrapper(Napoleon_RowStack, mod=13)

    #
    # game layout
    #

    def createGame(self, reserves=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 2*24 + 2*l.XM + 11*l.XS, l.YM + 5*l.YS + 2*l.XM)
        x0 = l.XM + 24 + 4*l.XS
        x1 = x0 + l.XS + l.XM
        x2 = x1 + l.XS + l.XM

        # create stacks
        y = l.YM
        for i in range(4):
            s.rows.append(self.RowStack_Class(x0, y, self))
            s.rows.append(self.RowStack_Class(x2, y, self))
            y = y + l.YS
        y = self.height - l.YS
        if reserves == 1:
            s.rows.append(Napoleon_ReserveStack(x0, y, self))
            s.rows.append(Napoleon_ReserveStack(x2, y, self))
            s.reserves.append(Napoleon_SingleFreeCell(x1, y, self))
        else:
            s.rows.append(Napoleon_ReserveStack(x0 - l.XS, y, self))
            s.rows.append(Napoleon_ReserveStack(x2 + l.XS, y, self))
            s.reserves.append(Napoleon_FreeCell(x0, y, self))
            s.reserves.append(Napoleon_FreeCell(x2, y, self))
        # foundations
        x, y = x1, l.YM
        for i in range(4):
            s.foundations.append(Napoleon_Foundation(x, y, self, i))
            y = y + l.YS
        # talon
        if reserves == 1:
            ##x, y = l.XM, self.height - l.YS
            y = self.height + l.YS
        else:
            y = self.height - l.YS
        s.talon = Napoleon_Talon(x, y, self)

        # update stack building direction
        for r in s.rows:
            if r.id & 1 == 0:
                r.CARD_XOFFSET = 4*[-l.XS] + 13*[-2]
            else:
                r.CARD_XOFFSET = 4*[l.XS] + 13*[2]
            r.CARD_YOFFSET = 0

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move 4 cards of the same rank to bottom of the Talon (i.e. last cards to be dealt)
        rank = cards[-1].rank
        return self._shuffleHookMoveToBottom(cards, lambda c, rank=rank: (c.rank == rank, c.suit))

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.rows[:8], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:8])
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.rows[8:])
        self.s.talon.dealBaseCards(ncards=4)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 13 == card2.rank or (card2.rank + 1) % 13 == card1.rank))

    #
    # game extras
    #

    def updateText(self):
        if self.preview > 1 or not self.texts.info:
            return
        t = ""
        f = self.s.foundations[0]
        if f.cards:
            t = RANKS[f.cards[0].rank]
            dir = self.getFoundationDir()
            if dir == 1:
                t = t + _(" Ascending")
            elif dir == -1:
                t = t + _(" Descending")
        self.texts.info.config(text=t)


# /***********************************************************************
# // Der freie Napoleon (completely equivalent to Der kleine Napoleon,
# // just a different layout)
# ************************************************************************/

class DerFreieNapoleon(DerKleineNapoleon):

    RowStack_Class = StackWrapper(Napoleon_RowStack, mod=13)
    #
    # game layout
    #

    def createGame(self, reserves=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # set size so that at least 2/3 of a card is visible with 15 cards
        h = l.CH*2/3 + (15-1)*l.YOFFSET
        h = l.YS + max(h, 3*l.YS)
        self.setSize(l.XM + 2*l.XM + 10*l.XS, l.YM + h)
        x1 = l.XM + 8*l.XS + 2*l.XM

        # create stacks
        y = l.YM + l.YS
        for j in range(8):
            x = l.XM + j*l.XS
            s.rows.append(self.RowStack_Class(x, y, self))
        for j in range(2):
            x = x1 + j*l.XS
            s.rows.append(Napoleon_ReserveStack(x, y, self))
        self.setRegion(s.rows, (-999, y - l.YM/2, 999999, 999999))
        y = l.YM
        if reserves == 1:
            s.reserves.append(Napoleon_SingleFreeCell(x1 + l.XS/2, y, self))
        else:
            s.reserves.append(Napoleon_FreeCell(x1, y, self))
            s.reserves.append(Napoleon_FreeCell(x1 + l.XS, y, self))
        # foundations
        x = l.XM + 2*l.XS
        for i in range(4):
            s.foundations.append(Napoleon_Foundation(x, y, self, i))
            x = x + l.XS
        tx, ty, ta, tf = l.getTextAttr(s.foundations[-1], "se")
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx, ty, anchor=ta, font=font)
        # talon
        x, y = l.XM, self.height - l.YS
        s.talon = Napoleon_Talon(x, y, self)

        # define stack-groups
        l.defaultStackGroups()


# /***********************************************************************
# // Napoleon (two FreeCells instead of one SingleFreeCell)
# ************************************************************************/

class Napoleon(DerKleineNapoleon):
    def createGame(self):
        DerKleineNapoleon.createGame(self, reserves=2)


class FreeNapoleon(DerFreieNapoleon):
    def createGame(self):
        DerFreieNapoleon.createGame(self, reserves=2)


# register the game
registerGame(GameInfo(167, DerKleineNapoleon, "Der kleine Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(168, DerFreieNapoleon, "Der freie Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(169, Napoleon, "Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(170, FreeNapoleon, "Free Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))

