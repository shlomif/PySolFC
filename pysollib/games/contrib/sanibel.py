##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
## Copyright (C) 1998-2000 Markus Franz Xaver Johannes Oberhumer
##
## Sanibel
## Copyright (C) 1998,2000 John Stoneham <obijohn99@aol.com>
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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.games.gypsy import Gypsy
from pysollib.games.yukon import Yukon_Hint

# /************************************************************************
# // Sanibel
# //   play similar to Yukon
# *************************************************************************/

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
                      GI.GT_YUKON | GI.GT_CONTRIB | GI.GT_ORIGINAL, 2, 0))

