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
from pysollib.hint import FreeCellType_Hint, FreeCellSolverWrapper

from spider import Spider_AC_Foundation


# /***********************************************************************
# // FreeCell
# ************************************************************************/

# To simplify playing we also consider the number of free rows.
# Note that this only is legal if the game.s.rows have a
# cap.base_rank == ANY_RANK.
# See also the "SuperMove" section in the FreeCell FAQ.
class FreeCell_RowStack(AC_RowStack):
    def _getMaxMove(self, to_stack_ncards):
        max_move = getNumberOfFreeStacks(self.game.s.reserves) + 1
        n = getNumberOfFreeStacks(self.game.s.rows)
        if to_stack_ncards == 0:
            n = n - 1
        while n > 0 and max_move < 1000:
            max_move = max_move * 2
            n = n - 1
        return max_move

    def canMoveCards(self, cards):
        max_move = self._getMaxMove(1)
        return len(cards) <= max_move and AC_RowStack.canMoveCards(self, cards)

    def acceptsCards(self, from_stack, cards):
        max_move = self._getMaxMove(len(self.cards))
        return len(cards) <= max_move and AC_RowStack.acceptsCards(self, from_stack, cards)


class FreeCell(Game):
    Layout_Method = Layout.freeCellLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = FreeCell_RowStack
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {})


    #
    # game layout
    #

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, reserves=4, texts=0)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self))
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
        assert len(self.s.talon.cards) == 0

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# /***********************************************************************
# // Relaxed FreeCell
# ************************************************************************/

class RelaxedFreeCell(FreeCell):
    RowStack_Class = AC_RowStack
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {'sm' : "unlimited"})


# /***********************************************************************
# // ForeCell
# ************************************************************************/

class ForeCell(FreeCell):
    RowStack_Class = StackWrapper(FreeCell_AC_RowStack, base_rank=KING)
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {'esf' : "kings"})

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)
        assert len(self.s.talon.cards) == 0


# /***********************************************************************
# // Challenge FreeCell
# // Super Challenge FreeCell
# ************************************************************************/

class ChallengeFreeCell(FreeCell):
    def _shuffleHook(self, cards):
        # move Aces and Twos to top of the Talon
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (ACE, 1), (-c.rank, c.suit)))

class SuperChallengeFreeCell(ChallengeFreeCell):
    RowStack_Class = StackWrapper(FreeCell_AC_RowStack, base_rank=KING)
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {'esf' : "kings"})


# /***********************************************************************
# // Stalactites
# ************************************************************************/

class Stalactites(FreeCell):
    Foundation_Class = StackWrapper(RK_FoundationStack, suit=ANY_SUIT, mod=13, min_cards=1)
    RowStack_Class = StackWrapper(BasicRowStack, max_move=1, max_accept=0)
    Hint_Class = FreeCellType_Hint

    def createGame(self):
        FreeCell.createGame(self, reserves=2)

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)
        assert len(self.s.talon.cards) == 0
        self._restoreGameHook(None)

    def _restoreGameHook(self, game):
        for s in self.s.foundations:
            s.cap.base_rank = s.cards[0].rank


# /***********************************************************************
# // Double Freecell
# ************************************************************************/

class DoubleFreecell(FreeCell):
    Hint_Class = FreeCellType_Hint

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
        assert len(self.s.talon.cards) == 0


# /***********************************************************************
# // Triple Freecell
# ************************************************************************/

class TripleFreecell(FreeCell):
    Hint_Class = FreeCellType_Hint

    #
    # game layout
    #

    def createGame(self, rows=13, reserves=10, playcards=20):

        # create layout
        l, s = Layout(self), self.s

        # set window
        max_rows = max(12, rows, reserves)
        w, h = l.XM+max_rows*l.XS, l.YM+3*l.YS+playcards*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        s.talon = self.Talon_Class(l.XM, h-l.YS, self)

        x, y = l.XM+(max_rows-12)*l.XS/2, l.YM
        for i in range(3):
            for j in range(4):
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


# /***********************************************************************
# // Spidercells
# ************************************************************************/

class Spidercells_RowStack(FreeCell_RowStack):
    def canMoveCards(self, cards):
        if len(cards) == 13 and isAlternateColorSequence(cards):
            return True
        return FreeCell_RowStack.canMoveCards(self, cards)


class Spidercells(FreeCell):

    Hint_Class = FreeCellType_Hint
    Foundation_Class = Spider_AC_Foundation
    RowStack_Class = Spidercells_RowStack

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, reserves=4, texts=0)
        apply(self.Layout_Method, (l,), layout)
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


# /***********************************************************************
# // Seven by Four
# // Seven by Five
# // Bath
# ************************************************************************/

class SevenByFour(FreeCell):
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {})
    #Hint_Class = FreeCellType_Hint
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
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {'esf' : 'kings'})
    #Hint_Class = FreeCellType_Hint
    RowStack_Class = StackWrapper(FreeCell_RowStack, base_rank=KING)
    def createGame(self):
        FreeCell.createGame(self, rows=10, reserves=2)
    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.rows[i:], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[6:])
        self.s.talon.dealRow(rows=self.s.rows[7:])


# /***********************************************************************
# // Clink
# ************************************************************************/

class Clink(FreeCell):
    Hint_Class = FreeCellType_Hint

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


# /***********************************************************************
# // Repair
# ************************************************************************/

class Repair(FreeCell):
    Hint_Class = FreeCellType_Hint
    RowStack_Class = AC_RowStack

    def createGame(self):
        FreeCell.createGame(self, rows=10, reserves=4, playcards=26)

    def startGame(self):
        for i in range(9):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)


# /***********************************************************************
# // Four Colours
# ************************************************************************/

class FourColours_RowStack(AC_RowStack):
    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()

class FourColours(FreeCell):
    Hint_Class = FreeCellType_Hint
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



# register the game
registerGame(GameInfo(5, RelaxedFreeCell, "Relaxed FreeCell",
                      GI.GT_FREECELL | GI.GT_RELAXED | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(8, FreeCell, "FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(46, ForeCell, "ForeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(77, Stalactites, "Stalactites",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0,
                      altnames=("Grampus", "Old Mole") ))
registerGame(GameInfo(264, DoubleFreecell, "Double FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 2, 0))
registerGame(GameInfo(265, TripleFreecell, "Triple FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 3, 0))
registerGame(GameInfo(336, ChallengeFreeCell, "Challenge FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0,
                      rules_filename='freecell.html'))
registerGame(GameInfo(337, SuperChallengeFreeCell, "Super Challenge FreeCell",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(363, Spidercells, "Spidercells",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(364, SevenByFour, "Seven by Four",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(365, SevenByFive, "Seven by Five",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(383, Bath, "Bath",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(394, Clink, "Clink",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0))
registerGame(GameInfo(448, Repair, "Repair",
                      GI.GT_FREECELL | GI.GT_OPEN, 2, 0))
registerGame(GameInfo(451, Cell11, "Cell 11",
                      GI.GT_FREECELL | GI.GT_OPEN, 3, 0))
registerGame(GameInfo(464, FourColours, "Four Colours",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(509, BigCell, "Big Cell",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 3, 0))

