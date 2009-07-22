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
from pysollib.hint import FreeCellType_Hint, FreeCellSolverWrapper

from spider import Spider_AC_Foundation


# ************************************************************************
# * FreeCell
# ************************************************************************

class FreeCell(Game):
    Layout_Method = Layout.freeCellLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SuperMoveAC_RowStack
    ReserveStack_Class = ReserveStack
    Hint_Class = FreeCellType_Hint
    Solver_Class = FreeCellSolverWrapper()


    #
    # game layout
    #

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, reserves=4, texts=0)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        for r in l.s.reserves:
            s.reserves.append(self.ReserveStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        r = self.s.rows
        ##self.s.talon.dealRow(rows=(r[0], r[2], r[4], r[6]))
        self.s.talon.dealRow(rows=r[:4])

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Relaxed FreeCell
# ************************************************************************

class RelaxedFreeCell(FreeCell):
    RowStack_Class = AC_RowStack
    Solver_Class = FreeCellSolverWrapper(sm='unlimited')


# ************************************************************************
# * ForeCell
# ************************************************************************

class ForeCell(FreeCell):
    RowStack_Class = StackWrapper(FreeCell_AC_RowStack, base_rank=KING)
    Solver_Class = FreeCellSolverWrapper(esf='kings')

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)


# ************************************************************************
# * Challenge FreeCell
# * Super Challenge FreeCell
# ************************************************************************

class ChallengeFreeCell(FreeCell):
    def _shuffleHook(self, cards):
        # move Aces and Twos to top of the Talon
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (ACE, 1), (-c.rank, c.suit)))

class SuperChallengeFreeCell(ChallengeFreeCell):
    RowStack_Class = StackWrapper(FreeCell_AC_RowStack, base_rank=KING)
    Solver_Class = FreeCellSolverWrapper(esf='kings')


# ************************************************************************
# * Stalactites
# ************************************************************************

class Stalactites(FreeCell):
    Foundation_Class = StackWrapper(RK_FoundationStack, suit=ANY_SUIT, mod=13, min_cards=1)
    RowStack_Class = StackWrapper(BasicRowStack, max_move=1, max_accept=0)
    Solver_Class = None

    def createGame(self):
        FreeCell.createGame(self, reserves=2)

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)
        self._restoreGameHook(None)

    def _restoreGameHook(self, game):
        for s in self.s.foundations:
            s.cap.base_rank = s.cards[0].rank


# ************************************************************************
# * Double Freecell
# ************************************************************************

class DoubleFreecell(FreeCell):
    Solver_Class = None

    #
    # game layout
    #

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 3*l.XM+10*l.XS, 2*l.YM+2*l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        s.talon = self.Talon_Class(l.XM, h-l.YS, self)
        x, y = 3*l.XM + 6*l.XS, l.YM
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i, mod=13, max_cards=26))
            x += l.XS
        x, y = 2*l.XM, l.YM + l.YS + l.YM
        for i in range(10):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        x, y = l.XM, l.YM
        for i in range(6):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        # default
        l.defaultAll()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move 4 Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards,
                   lambda c: (c.rank == ACE and c.deck == 0, c.suit))

    def startGame(self):
        for i in range(9):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)


# ************************************************************************
# * Triple Freecell
# ************************************************************************

class TripleFreecell(FreeCell):
    Solver_Class = None

    #
    # game layout
    #

    def createGame(self, rows=13, reserves=10, playcards=20):

        # create layout
        l, s = Layout(self), self.s

        # set window
        decks = self.gameinfo.decks
        max_rows = max(decks*4, rows, reserves)
        w, h = l.XM+max_rows*l.XS, l.YM+3*l.YS+playcards*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        s.talon = self.Talon_Class(l.XM, h-l.YS, self)

        x, y = l.XM+(max_rows-decks*4)*l.XS/2, l.YM
        for j in range(4):
            for i in range(decks):
                s.foundations.append(self.Foundation_Class(x, y, self, suit=j))
                x += l.XS
        x, y = l.XM+(max_rows-reserves)*l.XS/2, l.YM+l.YS
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        x, y = l.XM+(max_rows-rows)*l.XS/2, l.YM+2*l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(11):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


class Cell11(TripleFreecell):
    def createGame(self):
        TripleFreecell.createGame(self, rows=12, reserves=11)

    def startGame(self):
        for i in range(12):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[1:-1])
        self.s.talon.dealRow(rows=[self.s.reserves[0],self.s.reserves[-1]])


class BigCell(TripleFreecell):
    RowStack_Class = AC_RowStack

    def createGame(self):
        TripleFreecell.createGame(self, rows=13, reserves=4)

    def startGame(self):
        for i in range(11):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Spidercells
# ************************************************************************

class Spidercells_RowStack(SuperMoveAC_RowStack):
    def canMoveCards(self, cards):
        if len(cards) == 13 and isAlternateColorSequence(cards):
            return True
        return SuperMoveAC_RowStack.canMoveCards(self, cards)
    def canDropCards(self, stacks):
        if len(self.cards) < 13:
            return (None, 0)
        cards = self.cards[-13:]
        for s in stacks:
            if s is not self and s.acceptsCards(self, cards):
                return (s, 13)
        return (None, 0)


class Spidercells(FreeCell):

    Solver_Class = None
    Foundation_Class = Spider_AC_Foundation
    RowStack_Class = Spidercells_RowStack

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, reserves=4, texts=0)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=ANY_SUIT))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self))
        # default
        l.defaultAll()


# ************************************************************************
# * Seven by Four
# * Seven by Five
# * Bath
# ************************************************************************

class SevenByFour(FreeCell):
    def createGame(self):
        FreeCell.createGame(self, rows=7)
    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[:3])

class SevenByFive(SevenByFour):
    def createGame(self):
        FreeCell.createGame(self, rows=7, reserves=5)

class Bath(FreeCell):
    Solver_Class = FreeCellSolverWrapper(esf='kings')
    RowStack_Class = StackWrapper(SuperMoveAC_RowStack, base_rank=KING)
    def createGame(self):
        FreeCell.createGame(self, rows=10, reserves=2)
    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.rows[i:], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[6:])
        self.s.talon.dealRow(rows=self.s.rows[7:])


# ************************************************************************
# * Clink
# ************************************************************************

class Clink(FreeCell):
    Solver_Class = None

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+2*l.YS+12*l.YOFFSET)
        # create stacks
        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)
        x, y = l.XM+l.XS, l.YM
        for i in range(2):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        x += 2*l.XS
        for i in range(2):
            s.foundations.append(AC_FoundationStack(x, y, self, suit=ANY_SUIT,
                                 max_cards=26, mod=13, max_move=0))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        for i in range(8):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS
        # default
        l.defaultAll()

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow(rows=self.s.foundations)

    def _shuffleHook(self, cards):
        # move two Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards,
                   lambda c: (c.rank == ACE and c.suit in (0, 2), (c.suit)))


# ************************************************************************
# * Repair
# ************************************************************************

class Repair(FreeCell):
    Solver_Class = FreeCellSolverWrapper(sm='unlimited')
    RowStack_Class = AC_RowStack

    def createGame(self):
        FreeCell.createGame(self, rows=10, reserves=4, playcards=26)

    def startGame(self):
        for i in range(9):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)


# ************************************************************************
# * Four Colours
# * German FreeCell
# ************************************************************************

class FourColours_RowStack(AC_RowStack):
    getBottomImage = Stack._getReserveBottomImage

class FourColours(FreeCell):
    Solver_Class = None
    RowStack_Class = AC_RowStack

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+2*l.YS+12*l.YOFFSET)
        # create stacks
        x, y = self.width-l.XS, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)
        x, y = l.XM, l.YM
        for i in range(4):
            s.reserves.append(ReserveStack(x, y, self, base_suit=i))
            x += l.XS
        x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        for i in range(7):
            s.rows.append(FourColours_RowStack(x, y, self))
            x += l.XS
        # default
        l.defaultAll()

    def dealOne(self, frames):
        suit = self.s.talon.cards[-1].suit
        self.s.talon.dealRow(rows=[self.s.rows[suit]], frames=frames)

    def startGame(self):
        for i in range(40):
            self.dealOne(frames=0)
        self.startDealSample()
        while self.s.talon.cards:
            self.dealOne(frames=-1)


class GermanFreeCell_Reserve(ReserveStack):
    getBottomImage = Stack._getSuitBottomImage


class GermanFreeCell(SevenByFour):
    Solver_Class = None
    RowStack_Class = AC_RowStack
    ReserveStack_Class = GermanFreeCell_Reserve

    def createGame(self):
        FreeCell.createGame(self, rows=7)
        suit = 0
        for r in self.s.reserves:
            r.cap.base_suit = suit
            suit += 1


# ************************************************************************
# * Ocean Towers
# ************************************************************************

class OceanTowers(TripleFreecell):
    Solver_Class = FreeCellSolverWrapper(esf='kings', sbb='suit')
    RowStack_Class = StackWrapper(FreeCell_SS_RowStack, base_rank=KING)

    def createGame(self):
        TripleFreecell.createGame(self, rows=14, reserves=8, playcards=20)

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves[1:-1])

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * KingCell
# ************************************************************************

class KingCell(FreeCell):
    Solver_Class = FreeCellSolverWrapper(sbb='rank', esf='kings')
    RowStack_Class = StackWrapper(SuperMoveRK_RowStack, base_rank=KING)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Headquarters
# ************************************************************************

class Headquarters_Reserve(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        return len(self.cards) == 0


class Headquarters(Game):

    def createGame(self, rows=8, reserves=6):
        l, s = Layout(self), self.s
        w, h = l.XM+(rows+reserves+1)*l.XS, l.YM+3*l.YS+16*l.YOFFSET
        self.setSize(w, h)
        x, y = l.XM+(rows+reserves+1-8)*l.XS/2, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i%4))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        for i in range(reserves):
            stack = Headquarters_Reserve(x, y, self,
                                         max_cards=UNLIMITED_CARDS,
                                         max_accept=UNLIMITED_CARDS,
                                         max_move=UNLIMITED_CARDS)
            s.reserves.append(stack)
            stack.CARD_YOFFSET = l.YOFFSET
            x += l.XS
        x, y = l.XM+(reserves+1)*l.XS, l.YM+l.YS
        for j in range(rows):
            s.rows.append(AC_RowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS
        x, y = w-l.XS, h-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        l.defaultStackGroups()


    def startGame(self):
        for i in range(12):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Can Can
# ************************************************************************

class CanCan(FreeCell):
    Hint_Class = DefaultHint
    Solver_Class = None
    RowStack_Class = KingAC_RowStack
    ReserveStack_Class = StackWrapper(OpenStack, max_accept=0)

    def createGame(self):
        FreeCell.createGame(self, rows=13, reserves=3)

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRowAvail()


# ************************************************************************
# * Limpopo
# ************************************************************************

class Limpopo(Game):

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+10.5*l.XS, l.YM+2*l.YS+20*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM+l.YS/2
        for i in (0,1):
            stack = ReserveStack(x, y, self, max_cards=4)
            s.reserves.append(stack)
            stack.CARD_YOFFSET = l.YOFFSET
            l.createText(stack, 'n')
            x += l.XS

        x, y = l.XM+2.5*l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS

        x, y = l.XM+2.5*l.XS, l.YM+l.YS
        for i in range(8):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS

        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(12):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_AC



# register the game
registerGame(GameInfo(5, RelaxedFreeCell, "Relaxed FreeCell",
                      GI.GT_FREECELL | GI.GT_RELAXED | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(8, FreeCell, "FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(46, ForeCell, "ForeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(77, Stalactites, "Stalactites",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Grampus", "Old Mole") ))
registerGame(GameInfo(264, DoubleFreecell, "Double FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(265, TripleFreecell, "Triple FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(336, ChallengeFreeCell, "Challenge FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL,
                      rules_filename='freecell.html'))
registerGame(GameInfo(337, SuperChallengeFreeCell, "Super Challenge FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(363, Spidercells, "Spidercells",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(364, SevenByFour, "Seven by Four",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(365, SevenByFive, "Seven by Five",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(383, Bath, "Bath",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(394, Clink, "Clink",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(448, Repair, "Repair",
                      GI.GT_FREECELL | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(451, Cell11, "Cell 11",
                      GI.GT_FREECELL | GI.GT_OPEN, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(464, FourColours, "Four Colours",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(509, BigCell, "Big Cell",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(513, OceanTowers, "Ocean Towers",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(520, GermanFreeCell, "German FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(542, KingCell, "KingCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(648, Headquarters, "Headquarters",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(698, CanCan, "Can Can",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(746, Limpopo, "Limpopo",
                      GI.GT_FREECELL | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))

