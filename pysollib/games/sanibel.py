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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint, Yukon_Hint
from pysollib.games.gypsy import Gypsy


# ************************************************************************
# * Sanibel
# *   play similar to Yukon
# ************************************************************************

class Sanibel(Gypsy):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = StackWrapper(WasteTalonStack, max_rounds=1)
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = Yukon_AC_RowStack
    Hint_Class = Yukon_Hint

    def createGame(self):
        Gypsy.createGame(self, rows=10, waste=1, playcards=23)

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getHighlightPilesStacks(self):
        return ()


registerGame(GameInfo(201, Sanibel, "Sanibel",
                      GI.GT_YUKON | GI.GT_CONTRIB | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))

