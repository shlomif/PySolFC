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


# /***********************************************************************
# // Baker's Game
# ************************************************************************/

# To simplify playing we also consider the number of free rows.
# Note that this only is legal if the game.s.rows have a
# cap.base_rank == ANY_RANK.
# See also the "SuperMove" section in the FreeCell FAQ.
class BakersGame_RowStack(SS_RowStack):
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
        return len(cards) <= max_move and SS_RowStack.canMoveCards(self, cards)

    def acceptsCards(self, from_stack, cards):
        max_move = self._getMaxMove(len(self.cards))
        return len(cards) <= max_move and SS_RowStack.acceptsCards(self, from_stack, cards)


class BakersGame(Game):
    Layout_Method = Layout.freeCellLayout
    Foundation_Class = SS_FoundationStack
    RowStack_Class = BakersGame_RowStack
    ##Hint_Class = FreeCellType_Hint
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {'sbb' : "suit" })

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
        s.talon = InitialDealTalonStack(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            self.s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        for r in l.s.reserves:
            self.s.reserves.append(ReserveStack(r.x, r.y, self))
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
        ##self.s.talon.dealRow(rows=(r[0], r[1], r[6], r[7]))
        self.s.talon.dealRow(rows=r[:4])

    shallHighlightMatch = Game._shallHighlightMatch_SS


# /***********************************************************************
# //
# ************************************************************************/

class KingOnlyBakersGame(BakersGame):
    RowStack_Class = StackWrapper(FreeCell_SS_RowStack, base_rank=KING)
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {'sbb' : "suit", 'esf' : "kings" })


# /***********************************************************************
# // Eight Off (Baker's Game in a different layout)
# ************************************************************************/

class EightOff(KingOnlyBakersGame):

    #
    # game layout
    #

    def createGame(self, rows=8, reserves=8):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 16 cards are playable without overlap in default window size)
        h = max(2*l.YS, l.YS+(16-1)*l.YOFFSET)
        maxrows = max(rows, reserves)
        self.setSize(l.XM + maxrows*l.XS, l.YM + l.YS + h + l.YS)

        # create stacks
        x, y = l.XM + (maxrows-4)*l.XS/2, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i))
            x = x + l.XS
        x, y = l.XM + (maxrows-rows)*l.XS/2, y + l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        x, y = l.XM + (maxrows-reserves)*l.XS/2, self.height - l.YS
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        self.setRegion(s.reserves, (-999, y - l.CH / 2, 999999, 999999))
        s.talon = InitialDealTalonStack(l.XM, l.YM, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        r = self.s.reserves
        self.s.talon.dealRow(rows=[r[0],r[2],r[4],r[6]])


# /***********************************************************************
# // Seahaven Towers (Baker's Game in a different layout)
# ************************************************************************/

class SeahavenTowers(KingOnlyBakersGame):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 20 cards are playable in default window size)
        h = max(3*l.YS, 20*l.YOFFSET)
        self.setSize(l.XM + 10*l.XS, l.YM + l.YS + h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            s.reserves.append(ReserveStack(x + (i+3)*l.XS, y, self))
        for suit in range(4):
            i = (9, 0, 1, 8)[suit]
            s.foundations.append(SS_FoundationStack(x + i*l.XS, y, self, suit))
        x, y = l.XM, l.YM + l.YS
        for i in range(10):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        self.setRegion(s.rows, (-999, y - l.CH / 2, 999999, 999999))
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # define stack-groups
        self.sg.openstacks = s.foundations + s.rows + s.reserves
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows + s.reserves
        self.sg.reservestacks = s.reserves

    #
    # game overrides
    #

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=(self.s.reserves[1:3]))


# /***********************************************************************
# //
# ************************************************************************/

class RelaxedSeahavenTowers(SeahavenTowers):
    RowStack_Class = KingSS_RowStack
    Hint_Class = FreeCellSolverWrapper(FreeCellType_Hint, {'sbb' : "suit", 'esf' : "kings", 'sm' : "unlimited",})


# /***********************************************************************
# // Penguin
# // Opus
# // Tuxedo
# ************************************************************************/

class Tuxedo(Game):

    RowStack_Class = SS_RowStack
    Hint_Class = FreeCellType_Hint

    def createGame(self, rows=7, reserves=7):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 16 cards are playable without overlap in default window size)
        h = max(3*l.YS, l.YS+(16-1)*l.YOFFSET)
        maxrows = max(rows, reserves)
        self.setSize(l.XM + (maxrows+1)*l.XS, l.YM + h + l.YS)

        # extra settings
        self.base_card = None

        # create stacks
        x, y = self.width - l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i, mod=13, max_move=0))
            y = y + l.YS
        self.setRegion(s.foundations, (x - l.CW/2, -999, 999999, 999999))
        x, y = l.XM + (maxrows-rows)*l.XS/2, l.YM
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self, mod=13))
            x = x + l.XS
        x, y = l.XM + (maxrows-reserves)*l.XS/2, self.height - l.YS
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        self.setRegion(s.reserves, (-999, y - l.CH / 2, 999999, 999999))
        s.talon = InitialDealTalonStack(l.XM+1, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[::3])

    shallHighlightMatch = Game._shallHighlightMatch_SSW


class Penguin(Tuxedo):
    GAME_VERSION = 2

    def _shuffleHook(self, cards):
        # move base cards to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c, rank=cards[-1].rank: (c.rank == rank, 0))

    def _updateStacks(self):
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        for s in self.s.rows:
            s.cap.base_rank = (self.base_card.rank - 1) % 13

    def startGame(self):
        self.base_card = self.s.talon.cards[-4]
        self._updateStacks()
        # deal base cards to Foundations
        for i in range(3):
            c = self.s.talon.getCard()
            assert c.rank == self.base_card.rank
            to_stack = self.s.foundations[c.suit * self.gameinfo.decks]
            self.flipMove(self.s.talon)
            self.moveMove(1, self.s.talon, to_stack, frames=0)
        # deal rows
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        self._updateStacks()

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


class Opus(Penguin):
    def createGame(self):
        Tuxedo.createGame(self, reserves=5)



# register the game
registerGame(GameInfo(45, BakersGame, "Baker's Game",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(26, KingOnlyBakersGame, "King Only Baker's Game",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(258, EightOff, "Eight Off",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(9, SeahavenTowers, "Seahaven Towers",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_SKILL,
                      altnames=("Sea Towers", "Towers") ))
registerGame(GameInfo(6, RelaxedSeahavenTowers, "Relaxed Seahaven Towers",
                      GI.GT_FREECELL | GI.GT_RELAXED | GI.GT_OPEN, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(64, Penguin, "Penguin",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Beak and Flipper",) ))
registerGame(GameInfo(427, Opus, "Opus",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(629, Tuxedo, "Tuxedo",
                      GI.GT_FREECELL | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
