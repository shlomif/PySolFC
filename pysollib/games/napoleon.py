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
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from braid import Braid_Foundation


# ************************************************************************
# * stacks
# ************************************************************************


class Napoleon_RowStack(UD_SS_RowStack):
    getBottomImage = Stack._getReserveBottomImage


class Napoleon_ReserveStack(BasicRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=0)
        BasicRowStack.__init__(self, x, y, game, **cap)


class Napoleon_SingleFreeCell(ReserveStack):
    def acceptsCards(self, from_stack, cards):
##        if from_stack.id >= 8:
##            # from_stack must be a Napoleon_RowStack
##            return False
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def canMoveCards(self, cards):
        if self.game.s.rows[8].cards and self.game.s.rows[9].cards:
            return False
        return ReserveStack.canMoveCards(self, cards)


class Napoleon_FreeCell(ReserveStack):
    def canMoveCards(self, cards):
        if self.game.s.rows[self.id-2].cards:
            return False
        return ReserveStack.canMoveCards(self, cards)


# ************************************************************************
# * Der kleine Napoleon
# ************************************************************************

class DerKleineNapoleon(Game):

    Hint_Class = CautiousDefaultHint
    Foundation_Class = Braid_Foundation
    RowStack_Class = StackWrapper(Napoleon_RowStack, mod=13)

    #
    # game layout
    #

    def createGame(self, cells=1):
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
        if cells == 1:
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
            s.foundations.append(self.Foundation_Class(x, y, self, i))
            y = y + l.YS
        # talon
        if cells == 1:
            ##x, y = l.XM, self.height - l.YS
            y = self.height + l.YS
        else:
            y = self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

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

    shallHighlightMatch = Game._shallHighlightMatch_SSW

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


# ************************************************************************
# * Der freie Napoleon (completely equivalent to Der kleine Napoleon,
# * just a different layout)
# ************************************************************************

class DerFreieNapoleon(DerKleineNapoleon):

    Foundation_Class = Braid_Foundation
    RowStack_Class = StackWrapper(Napoleon_RowStack, mod=13)
    ReserveStack_Class = Napoleon_ReserveStack
    FreeCell_Class = Napoleon_SingleFreeCell

    #
    # game layout
    #

    def createGame(self, cells=1, reserves=2, texts=True):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # set size so that at least 2/3 of a card is visible with 15 cards
        h = l.CH*2/3 + (15-1)*l.YOFFSET
        h = l.YS + max(h, 3*l.YS)
        max_rows = 8+max(cells, reserves)
        self.setSize(l.XM + 2*l.XM + max_rows*l.XS, l.YM + h)
        x1 = l.XM + 8*l.XS + 2*l.XM

        # create stacks
        y = l.YM + l.YS
        for j in range(8):
            x = l.XM + j*l.XS
            s.rows.append(self.RowStack_Class(x, y, self))
        for j in range(reserves):
            x = x1 + j*l.XS
            s.rows.append(self.ReserveStack_Class(x, y, self))
        self.setRegion(s.rows, (-999, y - l.CH/2, 999999, 999999))
        y = l.YM
        x = x1+(max(cells, reserves)-cells)*l.XS/2
        for i in range(cells):
            s.reserves.append(self.FreeCell_Class(x, y, self))
            x += l.XS
        # foundations
        x = l.XM + 2*l.XS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, i))
            x = x + l.XS
        if texts:
            tx, ty, ta, tf = l.getTextAttr(s.foundations[-1], "se")
            font = self.app.getFont("canvas_default")
            self.texts.info = MfxCanvasText(self.canvas, tx, ty, anchor=ta,
                                            font=font)
        # talon
        x, y = l.XM, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()


# ************************************************************************
# * Napoleon (two FreeCells instead of one SingleFreeCell)
# ************************************************************************

class Napoleon(DerKleineNapoleon):
    def createGame(self):
        DerKleineNapoleon.createGame(self, cells=2)


class FreeNapoleon(DerFreieNapoleon):
    FreeCell_Class = Napoleon_FreeCell
    def createGame(self):
        DerFreieNapoleon.createGame(self, cells=2)


# ************************************************************************
# * Master
# ************************************************************************

class Master(DerFreieNapoleon):

    Foundation_Class = SS_FoundationStack

    def createGame(self):
        DerFreieNapoleon.createGame(self, cells=2, texts=False)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToBottom(cards,
                                             lambda c: (c.rank == ACE, c.suit))


# ************************************************************************
# * The Little Corporal
# * Bonaparte
# ************************************************************************

class TheLittleCorporal_RowStack(UD_SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not UD_SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.reserves:
            return not self.cards
        return True


class TheLittleCorporal(DerFreieNapoleon):

    def createGame(self, rows=10):
        l, s = Layout(self), self.s
        # set size so that at least 2/3 of a card is visible with 15 cards
        h = l.CH*2/3 + (15-1)*l.YOFFSET
        h = l.YS + max(h, 3*l.YS)
        self.setSize(l.XM+rows*l.XS, l.YM + h)

        x, y = l.XM+(rows-8)*l.XS, l.YM
        for i in range(4):
            s.foundations.append(Braid_Foundation(x, y, self, suit=i))
            x += l.XS
        tx, ty, ta, tf = l.getTextAttr(s.foundations[-1], "se")
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx, ty, anchor=ta, font=font)
        x += 2*l.XS
        stack = ReserveStack(x, y, self, max_cards=UNLIMITED_CARDS)
        s.reserves.append(stack)
        l.createText(stack, 'se')
        x, y = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(TheLittleCorporal_RowStack(x, y, self, mod=13))
            x += l.XS

        # talon
        x, y = l.XM, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.rows, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[1:-1])
        self.s.talon.dealBaseCards(ncards=4)

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack in self.s.reserves:
            return 0
        return int(len(to_stack.cards) != 0)+1


class Bonaparte(TheLittleCorporal):

    def createGame(self):
        TheLittleCorporal.createGame(self, rows=8)

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealBaseCards(ncards=4)


# ************************************************************************
# * Busy Cards
# ************************************************************************

class BusyCards_FreeCell(ReserveStack):
    def canMoveCards(self, cards):
        if not ReserveStack.canMoveCards(self, cards):
            return False
        rows = self.game.s.rows
        index = list(self.game.s.reserves).index(self)
        if rows[2*index].cards or rows[2*index+1].cards:
            return False
        return True


class BusyCards(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        rows=12

        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM + 3*l.YS+16*l.YOFFSET)

        x, y = l.XM+(rows-8)*l.XS/2, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 base_rank=KING, dir=-1))
            x += l.XS

        x, y = l.XM+l.XS/2, l.YM+l.YS
        for i in range(rows/2):
            s.reserves.append(BusyCards_FreeCell(x, y, self))
            x += 2*l.XS

        x, y = l.XM, l.YM+2*l.YS
        for i in range(rows):
            s.rows.append(UD_SS_RowStack(x, y, self))
            x += l.XS

        x, y = l.XM, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
            lambda c: ((c.rank in (ACE,KING) and c.deck == 0), (c.rank, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_SS



# register the game
registerGame(GameInfo(167, DerKleineNapoleon, "Der kleine Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(168, DerFreieNapoleon, "Der freie Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(169, Napoleon, "Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(170, FreeNapoleon, "Free Napoleon",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(536, Master, "Master",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(537, TheLittleCorporal, "The Little Corporal",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(538, Bonaparte, "Bonaparte",
                      GI.GT_NAPOLEON | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(705, BusyCards, "Busy Cards",
                      GI.GT_NAPOLEON | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))

