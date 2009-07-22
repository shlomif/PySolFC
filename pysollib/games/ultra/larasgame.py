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

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

from pysollib.games.larasgame import LarasGame_Talon, LarasGame, LarasGame_Reserve


# ************************************************************************
# *
# ************************************************************************

class DojoujisGame_Talon(LarasGame_Talon):
    def getActiveRow(self):
        card = self.getCard()
        return card.rank + card.deck * 4


class DoubleKalisGame_Talon(LarasGame_Talon):
    def getActiveRow(self):
        card = self.getCard()
        return card.rank + card.deck * 12


class BridgetsGame_Reserve(OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return from_stack in self.game.s.foundations and cards[0].suit == 4
        return from_stack in self.game.s.rows

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


# ************************************************************************
# * Katrina's Game
# ************************************************************************

class KatrinasGame(LarasGame):
    DEAL_TO_TALON = 3
    MAX_ROUNDS = 2
    ROW_LENGTH = 5
    MAX_ROW = 22

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 14 + 8 * (i == 4)

    def Mod(self, i):
        return 14 + 8 * (i == 4)

    def Base_Rank(self, i, j):
        return (13 + 8 * (i == 4)) * (not j)

    def Deal_Rows(self, i):
        return 14 + 8 * (i % 2)

    def Base_Suit(self, i, j):
        return i

    #
    # Game overrides
    #

    def getCardFaceImage(self, deck, suit, rank):
        return self.app.images.getFace(deck, suit, rank)


# ************************************************************************
# * Relaxed Katrina's Game
# ************************************************************************

class RelaxedKatrinasGame(KatrinasGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 2


# ************************************************************************
# * Double Katrina's Game
# ************************************************************************

class DoubleKatrinasGame(RelaxedKatrinasGame):
    Reserve_Cards = 3
    MAX_ROUNDS = 3

    def Max_Cards(self, i):
        return 28 + 16 * (i == 4)


# ************************************************************************
# * Bridget's Game
# * In memory of Bridget Bishop
# * Hanged as a witch on June 10, 1692
# * Salem Massachusetts, U. S. A.
# * and the nineteen other women
# * and men who followed her
# ************************************************************************

class BridgetsGame(LarasGame):
    Reserve_Class = BridgetsGame_Reserve
    Reserve_Cards = 2
    MAX_ROUNDS = 2
    ROW_LENGTH = 5
    MAX_ROW = 16

    def Max_Cards(self, i):
        return 16 - 12 * (i == 4)

    def Mod(self, i):
        return 16 - 12 * (i == 4)

    def Base_Rank(self, i, j):
        return (15 - 12 * (i == 4)) * (not j)

    def Deal_Rows(self, i):
        return 16

    def Base_Suit(self, i, j):
        return i


# ************************************************************************
# * Double Bridget's Game
# ************************************************************************

class DoubleBridgetsGame(BridgetsGame):
    Reserve_Cards = 3
    MAX_ROUNDS = 3

    def Max_Cards(self, i):
        return 32 - 24 * (i == 4)


# ************************************************************************
# * Fatimeh's Game
# ************************************************************************

class FatimehsGame(LarasGame):
    DEAL_TO_TALON = 5
    MAX_ROUNDS = 3
    MAX_ROW = 12
    DIR = (1, 1)

    def Max_Cards(self, i):
        return 12

    def Mod(self, i):
        return 12

    def Base_Rank(self, i, j):
        return 0

    def Deal_Rows(self, i):
        return 12

    def Base_Suit(self, i, j):
        return i + j * 4


# ************************************************************************
# * Relaxed Fatimeh's Game
# ************************************************************************

class RelaxedFatimehsGame(FatimehsGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 2


# ************************************************************************
# * Kali's Game
# ************************************************************************

class KalisGame(FatimehsGame):
    DEAL_TO_TALON = 6
    ROW_LENGTH = 5

    def Base_Suit(self, i, j):
        return i + j * 5


# ************************************************************************
# * Relaxed Kali's Game
# ************************************************************************

class RelaxedKalisGame(KalisGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 2


# ************************************************************************
# * Double Kali's Game
# ************************************************************************

class DoubleKalisGame(RelaxedKalisGame):
    Talon_Class = DoubleKalisGame_Talon
    Reserve_Cards = 4
    MAX_ROUNDS = 4
    MAX_ROW = 24

    def Max_Cards(self, i):
        return 24

    def Deal_Rows(self, i):
        return 24


# ************************************************************************
# * Dojouji's Game
# ************************************************************************

class DojoujisGame(LarasGame):
    Talon_Class = DojoujisGame_Talon
    ROW_LENGTH = 6
    MAX_ROW = 8
    DIR = (-1, -1)

    def Max_Cards(self, i):
        return 8

    def Mod(self, i):
        return 4

    def Base_Rank(self, i, j):
        return 3

    def Deal_Rows(self, i):
        return 8

    def Base_Suit(self, i, j):
        return i + j * 6


# ************************************************************************
# * Double Dojouji's Game
# ************************************************************************

class DoubleDojoujisGame(DojoujisGame):
    MAX_ROW = 16

    def Max_Cards(self, i):
        return 16

    def Deal_Rows(self, i):
        return 16



# register the game
registerGame(GameInfo(13001, KatrinasGame, "Katrina's Game",
                      GI.GT_TAROCK, 2, 1, GI.SL_BALANCED,
                      ranks = range(14), trumps = range(22)))
registerGame(GameInfo(13002, BridgetsGame, "Bridget's Game",
                      GI.GT_HEXADECK, 2, 1, GI.SL_BALANCED,
                      ranks = range(16), trumps = range(4)))
registerGame(GameInfo(13003, FatimehsGame, "Fatimeh's Game",
                      GI.GT_MUGHAL_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(8), ranks = range(12)))
registerGame(GameInfo(13004, KalisGame, "Kali's Game",
                      GI.GT_DASHAVATARA_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(10), ranks = range(12)))
registerGame(GameInfo(13005, DojoujisGame, "Dojouji's Game",
                      GI.GT_HANAFUDA, 2, 0, GI.SL_BALANCED,
                      suits = range(12), ranks = range(4)))
registerGame(GameInfo(13008, RelaxedKatrinasGame, "Katrina's Game Relaxed",
                      GI.GT_TAROCK, 2, 1, GI.SL_BALANCED,
                      ranks = range(14), trumps = range(22)))
registerGame(GameInfo(13009, DoubleKatrinasGame, "Katrina's Game Doubled",
                      GI.GT_TAROCK, 4, 2, GI.SL_BALANCED,
                      ranks = range(14), trumps = range(22)))
registerGame(GameInfo(13010, DoubleBridgetsGame, "Bridget's Game Doubled",
                      GI.GT_HEXADECK, 4, 2, GI.SL_BALANCED,
                      ranks = range(16), trumps = range(4)))
registerGame(GameInfo(13011, RelaxedKalisGame, "Kali's Game Relaxed",
                      GI.GT_DASHAVATARA_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(10), ranks = range(12)))
registerGame(GameInfo(13012, DoubleKalisGame, "Kali's Game Doubled",
                      GI.GT_DASHAVATARA_GANJIFA, 2, 3, GI.SL_BALANCED,
                      suits = range(10), ranks = range(12)))
registerGame(GameInfo(13013, RelaxedFatimehsGame, "Fatimeh's Game Relaxed",
                      GI.GT_MUGHAL_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(8), ranks = range(12)))
registerGame(GameInfo(13014, DoubleDojoujisGame, "Dojouji's Game Doubled",
                      GI.GT_HANAFUDA, 4, 0, GI.SL_BALANCED,
                      suits = range(12), ranks = range(4)))
