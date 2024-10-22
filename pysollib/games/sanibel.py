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

# Importing necessary modules for the Sanibel card game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.games.gypsy import Gypsy  # Import Gypsy, base class for Sanibel
from pysollib.hint import Yukon_Hint  # Hint mechanism for Yukon-based games
from pysollib.layout import Layout  # Layout configuration for the game
from pysollib.stack import (
    SS_FoundationStack,  # Foundation stack for completed suits
    StackWrapper,  # Wrapper for stack with additional functionality
    WasteTalonStack,  # Talon stack for dealing cards
    Yukon_AC_RowStack  # Row stack class used in Yukon-like games
)

# ************************************************************************
# * Sanibel
# *   play similar to Yukon
# ************************************************************************


class Sanibel(Gypsy):
    """
    Class representing the Sanibel card game, a variant of Yukon.
    It uses a similar layout and gameplay mechanics to Yukon but with
    specific rules defined in the class.
    """

    Layout_Method = staticmethod(Layout.klondikeLayout)  # Use Klondike layout
    Talon_Class = StackWrapper(
        WasteTalonStack, max_rounds=1
    )  # One round Talon
    Foundation_Class = StackWrapper(
        SS_FoundationStack, max_move=0
    )  # Foundation stacks
    RowStack_Class = Yukon_AC_RowStack  # Row stack for Yukon gameplay
    Hint_Class = Yukon_Hint  # Hint system for Yukon-style games

    def createGame(self):
        """
        Set up the game with a specific number of rows, waste piles,
        and initial playcards.
        """
        # Create a Gypsy-like game with 10 rows, 1 waste stack,
        # and 23 playcards
        Gypsy.createGame(self, rows=10, waste=1, playcards=23)

    def startGame(self):
        """
        Start the game by dealing cards into the talon and rows.
        """
        # Deal the first three rows from the talon
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        # Deal 6 more rows
        self._startDealNumRows(6)
        # Deal the last row and cards from the talon
        self.s.talon.dealRow()
        self.s.talon.dealCards()  # Deal the first card to the WasteStack

    def getHighlightPilesStacks(self):
        """
        Returns an empty tuple, meaning no specific stacks will be highlighted.
        """
        return ()


# Register the Sanibel game in the game database with its associated info
registerGame(GameInfo(201, Sanibel, "Sanibel",
                      GI.GT_YUKON | GI.GT_CONTRIB | GI.GT_ORIGINAL, 2, 0,
                      GI.SL_MOSTLY_SKILL))
