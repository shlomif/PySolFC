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

# Importing necessary modules from the pysollib library for the game
from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.hint import CautiousDefaultHint
from pysollib.layout import Layout
from pysollib.stack import (
    RK_RowStack,  # Row stack for holding cards
    SS_FoundationStack,  # Foundation stack where cards are placed to win
    WasteStack,  # Waste stack for discarded cards
    WasteTalonStack  # Talon stack for dealing cards
)

# ************************************************************************
# * Royal East
# ************************************************************************


class RoyalEast(Game):
    """
    Class representing the Royal East card game.
    It defines the layout, rules, and mechanics of the game.
    """

    Hint_Class = CautiousDefaultHint  # Setting the hint class for this game

    #
    # game layout
    #

    def createGame(self):
        """Set up the game layout and initialize the stacks."""
        # Initialize the layout and stack container
        l, s = Layout(self), self.s

        # Set the game window size
        self.setSize(l.XM + 5.5 * l.XS, l.YM + 4 * l.YS)

        # Initialize base card variable
        self.base_card = None

        # Create foundation stacks (where cards are stacked by suit)
        for i in range(4):
            dx, dy = ((0, 0), (2, 0), (0, 2), (2, 2))[i]
            x, y = (
                l.XM + (2 * dx + 5) * l.XS // 2,
                l.YM + (2 * dy + 1) * l.YS // 2
            )
            stack = SS_FoundationStack(x, y, self, i, mod=13, max_move=0)
            stack.CARD_YOFFSET = 0  # No vertical card offset
            s.foundations.append(stack)

        # Create row stacks (where cards are initially dealt)
        for i in range(5):
            dx, dy = ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2))[i]
            x, y = (
                l.XM + (2 * dx + 5) * l.XS // 2,
                l.YM + (2 * dy + 1) * l.YS // 2
            )
            stack = RK_RowStack(x, y, self, mod=13, max_move=1)
            stack.CARD_YOFFSET = 0  # No vertical card offset
            s.rows.append(stack)

        # Create the talon (where undealt cards are stored) and waste stacks
        x, y = l.XM, l.YM + 3 * l.YS // 2
        s.talon = WasteTalonStack(
            x, y, self, max_rounds=1
        )  # Talon with one round of cards
        l.createText(s.talon, "s")  # Label for the talon
        x = x + l.XS
        s.waste = WasteStack(x, y, self)  # Waste stack for discarded cards
        l.createText(s.waste, "s")  # Label for the waste

        # Define stack groups (standard Solitaire layout grouping)
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        """Start a new game by setting up the base card and dealing cards."""
        # Set the base card as the last card in the talon stack
        self.base_card = self.s.talon.cards[-1]

        # Set the base rank for each foundation stack based on the base card
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

        # Deal the base card to the corresponding foundation stack
        c = self.s.talon.getCard()
        to_stack = self.s.foundations[c.suit * self.gameinfo.decks]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack, frames=0)

        # Deal cards to row stacks
        self._startAndDealRowAndCards()

    def _restoreGameHook(self, game):
        """Restore the game from a saved state."""
        # Restore the base card based on its saved ID
        self.base_card = self.cards[game.loadinfo.base_card_id]

        # Set the base rank for the foundation stacks
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        """Load additional game state during game restoration."""
        # Register an additional variable to save the base card's ID
        self.loadinfo.addattr(base_card_id=None)
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        """Save the game state including the base card's ID."""
        p.dump(self.base_card.id)

    # Define matching highlights for the game
    shallHighlightMatch = Game._shallHighlightMatch_RKW


# Register the Royal East game in the game database
registerGame(GameInfo(93, RoyalEast, "Royal East",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
