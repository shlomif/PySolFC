#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.hint import CautiousDefaultHint
from pysollib.layout import Layout
from pysollib.stack import (
    DealRowTalonStack,
    ReserveStack,
    SS_FoundationStack,
    SS_RowStack,
    StackWrapper,
    UD_SS_RowStack,
)
from pysollib.util import ACE, KING

# ************************************************************************
# * Carthage
# ************************************************************************

# Custom Talon class for the Carthage game. Handles the dealing of
# cards from the Talon.


class Carthage_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        if sound:
            self.game.startDealSample()
        # Check if the number of cards equals the number of rows, then
        # deal cards to rows.
        if len(self.cards) == len(self.game.s.rows):
            n = self.dealRowAvail(rows=self.game.s.rows, sound=False)
        else:
            # Otherwise, deal to reserves twice (used when rows
            # are full or initial deal phase).
            n = self.dealRowAvail(rows=self.game.s.reserves, sound=False)
            n += self.dealRowAvail(rows=self.game.s.reserves, sound=False)
        if sound:
            self.game.stopSamples()
        return n


class Carthage(Game):

    Hint_Class = CautiousDefaultHint
    Talon_Class = Carthage_Talon
    Foundation_Classes = (SS_FoundationStack, SS_FoundationStack)
    RowStack_Class = StackWrapper(SS_RowStack, max_move=1)

    # Game layout
    def createGame(self, rows=8, reserves=6, playcards=12):
        l, s = Layout(self), self.s

        # Set window size based on the number of decks and other
        # layout parameters.
        decks = self.gameinfo.decks
        foundations = decks * 4
        max_rows = max(foundations, rows)
        w, h = (l.XM + (max_rows + 1) * l.XS,
                l.YM + 3 * l.YS + playcards * l.YOFFSET)
        self.setSize(w, h)

        # Create stacks
        x, y = l.XM + l.XS + (max_rows - foundations) * l.XS // 2, l.YM
        for fclass in self.Foundation_Classes:
            for i in range(4):
                s.foundations.append(fclass(x, y, self, suit=i))
                x += l.XS

        x, y = l.XM + l.XS + (max_rows - rows) * l.XS // 2, l.YM + l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1))
            x += l.XS
        self.setRegion(s.rows, (-999, y - l.CH // 2,
                                999999, h - l.YS - l.CH // 2))

        d = (w - reserves * l.XS) // reserves
        x, y = l.XM, h - l.YS
        for i in range(reserves):
            stack = ReserveStack(x, y, self)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 2, 0
            s.reserves.append(stack)
            x += l.XS + d

        s.talon = self.Talon_Class(l.XM, l.YM, self)
        l.createText(s.talon, "s")

        # Define stack-groups
        l.defaultStackGroups()

    # Game overrides
    def startGame(self):
        self.s.talon.dealRow(rows=self.s.rows, frames=0)
        for i in range(5):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * Algerian Patience
# ************************************************************************

# Algerian Patience is a variation of Carthage with different rules
# for dealing and card movement.


class AlgerianPatience(Carthage):

    # Different foundation rules for stacking cards
    Foundation_Classes = (SS_FoundationStack,
                          StackWrapper(SS_FoundationStack, base_rank=KING,
                                       dir=-1))
    RowStack_Class = StackWrapper(UD_SS_RowStack, mod=13)

    # Hook for modifying the shuffle process, moves 4 Kings to the
    # top of the Talon.
    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.rank == KING and c.deck == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations[4:], frames=0)
        Carthage.startGame(self)


class AlgerianPatience3(Carthage):
    Foundation_Classes = (SS_FoundationStack,
                          SS_FoundationStack,
                          SS_FoundationStack)
    RowStack_Class = StackWrapper(UD_SS_RowStack, mod=13)

    # Modify the game layout to accommodate 8 rows, 8 reserves, and
    # 20 playcards.
    def createGame(self):
        Carthage.createGame(self, rows=8, reserves=8, playcards=20)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.rank == ACE, (c.deck, c.suit)))

    # Start the game by dealing rows to the foundations first, then
    # follow Carthage rules.
    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        Carthage.startGame(self)


# Register the Carthage, Algerian Patience, and Algerian
# Patience (3 Decks) games in the system.
registerGame(GameInfo(321, Carthage, "Carthage",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(322, AlgerianPatience, "Algerian Patience",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(457, AlgerianPatience3, "Algerian Patience (3 Decks)",
                      GI.GT_3DECK_TYPE | GI.GT_ORIGINAL, 3, 0,
                      GI.SL_MOSTLY_SKILL))
