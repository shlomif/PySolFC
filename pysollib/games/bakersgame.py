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


# ************************************************************************
# * Baker's Game
# ************************************************************************

class BakersGame(Game):
    Layout_Method = Layout.freeCellLayout
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SuperMoveSS_RowStack
    Hint_Class = FreeCellType_Hint
    Solver_Class = FreeCellSolverWrapper(sbb='suit')

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


# ************************************************************************
# *
# ************************************************************************

class KingOnlyBakersGame(BakersGame):
    RowStack_Class = StackWrapper(FreeCell_SS_RowStack, base_rank=KING)
    Solver_Class = FreeCellSolverWrapper(sbb='suit', esf='kings')


# ************************************************************************
# * Eight Off (Baker's Game in a different layout)
# ************************************************************************

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


# ************************************************************************
# * Seahaven Towers (Baker's Game in a different layout)
# ************************************************************************

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


# ************************************************************************
# *
# ************************************************************************

class RelaxedSeahavenTowers(SeahavenTowers):
    RowStack_Class = KingSS_RowStack
    Solver_Class = FreeCellSolverWrapper(sbb='suit', esf='kings', sm='unlimited')


# ************************************************************************
# * Tuxedo
# * Penguin
# * Opus
# ************************************************************************

class Tuxedo(Game):

    RowStack_Class = StackWrapper(SS_RowStack, mod=13)
    ReserveStack_Class = ReserveStack
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, max_move=0)
    Hint_Class = FreeCellType_Hint
    Solver_Class = FreeCellSolverWrapper(sbb='suit', sm='unlimited')

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
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
            y = y + l.YS
        self.setRegion(s.foundations, (x - l.CW/2, -999, 999999, 999999))
        x, y = l.XM + (maxrows-rows)*l.XS/2, l.YM
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        x, y = l.XM + (maxrows-reserves)*l.XS/2, self.height - l.YS
        for i in range(reserves):
            s.reserves.append(self.ReserveStack_Class(x, y, self))
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
    Solver_Class = FreeCellSolverWrapper(sbb='suit', esf='kings', sm='unlimited')

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



# ************************************************************************
# * Flipper
# ************************************************************************

class Flipper_Row(AC_RowStack):
    def canFlipCard(self):
        if not OpenStack.canFlipCard(self):
            return False
        i = list(self.game.s.rows).index(self)
        return len(self.game.s.reserves[i].cards) == 0


class Flipper(Tuxedo):

    RowStack_Class = Flipper_Row
    Foundation_Class = SS_FoundationStack
    Hint_Class = DefaultHint
    Solver_Class = None

    def fillStack(self, stack):
        i = 0
        for s in self.s.reserves:
            r = self.s.rows[i]
            if r.cards:
                if ((s.cards and r.cards[-1].face_up) or
                    (not s.cards and not r.cards[-1].face_up)):
                    r.flipMove(animation=True)
            i += 1

    shallHighlightMatch = Game._shallHighlightMatch_AC



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
registerGame(GameInfo(713, Flipper, "Flipper",
                      GI.GT_FREECELL | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
