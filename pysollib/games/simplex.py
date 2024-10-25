#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------

import pysollib.game
from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.stack import \
        AbstractFoundationStack, \
        SequenceRowStack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ANY_RANK, ANY_SUIT

# ************************************************************************
# * Simplex
# ************************************************************************


# Helper function to check if all cards in a sequence have the same rank
def isSameRankSequence(cards):
    c0 = cards[0]  # Get the rank of the first card
    for c in cards[1:]:
        if c0.rank != c.rank:  # Compare ranks of all other cards
            return False
    return True


# Class to define the foundation stack for Simplex
class Simplex_Foundation(AbstractFoundationStack):
    # Function to check if group of cards can be accepted into the foundation
    def acceptsCards(self, from_stack, cards):
        if len(cards) != 4:
            return False
        return isSameRankSequence(cards)  # Cards must be of the same rank


# Class to define row stack behavior in Simplex
class Simplex_RowStack(SequenceRowStack):
    # Function to check if cards can be dropped into another stack
    def canDropCards(self, stacks):
        if len(self.cards) != 4:  # Only allows groups of 4 cards
            return (None, 0)
        for s in stacks:
            # If stack is not the current one and accepts the cards,
            # return the stack and number of cards
            if s is not self and s.acceptsCards(self, self.cards):
                return (s, 4)
        return (None, 0)

    # Function to check if cards form a valid sequence (same rank)
    def _isSequence(self, cards):
        return isSameRankSequence(cards)


# Main game class definition for Simplex
class Simplex(pysollib.game.StartDealRowAndCards, Game):

    # Function to create and initialize the game layout
    # and stack configurations
    def createGame(self, reserves=6):
        # Create the game layout object
        l, s = Layout(self), self.s

        # Set window dimensions based on the layout
        w, h = l.XM+10*l.XS, l.YM+2*l.YS+4*l.YOFFSET+l.TEXT_HEIGHT
        self.setSize(w, h)

        # Create and position stacks in the layout
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')  # Label the stack
        x += l.XS
        s.waste = WasteStack(x, y, self)  # Waste stack
        l.createText(s.waste, 's')  # Label the waste stack
        x += l.XS
        # Create the foundation stack with any rank and any suit
        stack = Simplex_Foundation(
            x, y, self,
            suit=ANY_SUIT, base_rank=ANY_RANK, max_cards=52)
        # Set horizontal offset for the cards to be displayed
        xoffset = (self.width-3*l.XS)//51
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = xoffset, 0
        s.foundations.append(stack)
        x, y = l.XM, l.YM+l.YS+l.TEXT_HEIGHT
        # Create 9 row stacks for card sequences
        for i in range(9):
            s.rows.append(Simplex_RowStack(x, y, self))
            x += l.XS

        # Define stack-groups and set up game structure
        l.defaultStackGroups()

    # Function to highlight matching card pairs
    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank


# Register the game to make it available in the PySol library
registerGame(GameInfo(436, Simplex, "Simplex",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
