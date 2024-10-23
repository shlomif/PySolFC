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

# Importing necessary classes from the `pysollib` package to define the game
# and its components
from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.stack import (
    AbstractFoundationStack,
    BasicRowStack,
    OpenStack,
    ReserveStack,
    TalonStack
)
from pysollib.util import ANY_SUIT, JACK, KING, NO_RANK, QUEEN

# ************************************************************************
# * Clear the Dungeon (Game Definition)
# ************************************************************************


# Define a custom RowStack class for the "Clear the Dungeon" game
class ClearTheDungeon_RowStack(BasicRowStack):
    # Function that checks whether a move (card placement) is valid
    def acceptsCards(self, from_stack, cards):
        cardnum = 0
        goal_rank = 0
        goal_suit = 0
        total = 0
        # Loop through the cards in the row to establish game rules for
        # accepting new cards
        for card in self.cards:
            if card.face_up:  # Only consider face-up cards
                if cardnum == 0:
                    # Set the goal rank and suit based on the first face-up
                    # card
                    goal_rank = card.rank + 1
                    goal_suit = card.suit
                elif cardnum == 1:
                    # Add a value of 10 if the card is a joker, otherwise
                    # add its rank
                    if card.suit == 4:
                        total += 10
                    else:
                        total += (card.rank + 1)
                cardnum += 1

        # Determine the value of the new card being played
        if cards[0].suit == 4:  # Joker
            new_val = 10
        else:
            new_val = cards[0].rank + 1

        # Ensure the new card follows the rules for valid placement
        if cardnum == 1:
            if new_val + 10 < goal_rank:
                return False
        if cardnum == 2:
            if total + new_val < goal_rank:
                return False
        elif cardnum == 3:
            if cards[0].suit not in (goal_suit, 4):
                return False

        # If all conditions are satisfied, call the base class function
        return BasicRowStack.acceptsCards(self, from_stack, cards)


# Define the main game class for "Clear the Dungeon"
class ClearTheDungeon(Game):
    #
    # Define the layout of the game
    #

    def createGame(self):
        # Create the game layout
        l, s = Layout(self), self.s

        # Set the window size for the game layout
        self.setSize(l.XM + 5 * l.XS, l.YM + 2 * l.YS + 12 * l.YOFFSET)

        # Create different stacks in the game (rows, foundations, reserves,
        # talon)
        x, y = l.XM, l.YM
        for i in range(4):
            s.rows.append(ClearTheDungeon_RowStack(x, y, self,
                                                   max_move=0, max_accept=1,
                                                   dir=0, base_rank=NO_RANK))
            x += l.XS
        s.foundations.append(AbstractFoundationStack(x, y, self, suit=ANY_SUIT,
                                                     max_move=0, max_accept=0,
                                                     max_cards=52))
        # Position reserve stacks
        x, y = l.XM, self.height - l.YS
        for i in range(3):
            s.reserves.append(OpenStack(x, y, self, max_cards=1, max_accept=0))
            x += l.XS

        x += l.XS
        s.talon = TalonStack(x, y, self)  # Create the Talon stack
        l.createText(s.talon, "sw")

        y -= l.YS
        s.reserves.append(ReserveStack(x, y, self, max_accept=1, max_move=1,
                                       max_cards=52))

        # Define default stack groups for easier management
        l.defaultStackGroups()

    # Custom shuffle behavior to ensure that Jacks, Queens, and Kings are
    # dealt last
    def _shuffleHook(self, cards):
        topcards = []
        for c in cards[:]:
            if c.rank in (JACK, QUEEN, KING):
                topcards.append(c)
                cards.remove(c)
        topcards.reverse()  # Reverses the topcards to keep Jacks on top
        return cards + topcards

    # Initialize the game and deal the first cards
    def startGame(self):
        for r in self.s.rows:
            for j in range(2):
                self.s.talon.dealRow(rows=[r], flip=0, frames=0)
        self.startDealSample()  # Deals sample cards for the game
        self.s.talon.dealRow(rows=self.s.rows)
        self.s.talon.dealRow(rows=self.s.reserves[:3])

    # Function to manage the auto-filling of stacks
    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)

        # Move cards from the row stack to the foundation if certain
        # conditions are met
        for s in self.s.rows:
            num_cards = 0
            for c in s.cards:
                if c.face_up:
                    num_cards += 1
            if num_cards == 4:
                s.moveMove(4, self.s.foundations[0])
                if len(s.cards) > 0:
                    s.flipMove()

        # If the stack is in the reserves, deal a row from the talon
        if stack in self.s.reserves[:3]:
            for stack in self.s.reserves[:3]:
                if stack.cards:
                    self.leaveState(old_state)
                    return
            self.s.talon.dealRow(rows=self.s.reserves[:3], sound=1)
        self.leaveState(old_state)

    # Check if the game is won
    def isGameWon(self):
        for s in self.s.rows:
            if len(s.cards) > 0:
                return False
        return True

    # Return the auto-stacks for automatic card moves
    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


# Register the game in the game's database
registerGame(GameInfo(909, ClearTheDungeon, "Clear the Dungeon",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL,
                      subcategory=GI.GS_JOKER_DECK, trumps=list(range(2))))
