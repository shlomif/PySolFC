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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# /***********************************************************************
# //
# ************************************************************************/

class PileOn_RowStack(RK_RowStack):
    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class PileOn(Game):
    Hint_Class = DefaultHint
    ##Hint_Class = CautiousDefaultHint
    TWIDTH = 4     
    NSTACKS = 15
    PLAYCARDS = 4

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (set size so that at least 4 cards are fully playable)
        #w = max(2*l.XS, l.XS+(self.PLAYCARDS-1)*l.XOFFSET+2*l.XM)
        w = l.XS+(self.PLAYCARDS-1)*l.XOFFSET+3*l.XM
        twidth, theight = self.TWIDTH, int((self.NSTACKS-1)/self.TWIDTH+1)
        self.setSize(l.XM+twidth*w, l.YM+theight*l.YS)

        # create stacks
        y = l.YM
        for i in range(theight):
            x = l.XM
            for j in range(twidth):
                if i*twidth+j >= self.NSTACKS:
                    break
                stack = PileOn_RowStack(x, y, self, dir=0, max_cards=self.PLAYCARDS)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                x = x + w
            y = y + l.YS
        x, y = self.width - l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        self.sg.openstacks = s.rows
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self):
        r = self.s.rows[:-2]
        for i in range(self.PLAYCARDS-1):
            self.s.talon.dealRow(rows=r, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=r)

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards:
                if len(r.cards) != 4 or not r._isSequence(r.cards):
                    return 0
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank

class SmallPileOn(PileOn):
    TWIDTH = 3
    NSTACKS = 11
    PLAYCARDS = 4

class PileOn2Decks(PileOn):
    TWIDTH = 4
    NSTACKS = 15
    PLAYCARDS = 8


# register the game
registerGame(GameInfo(41, PileOn, "PileOn",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Fifteen Puzzle",) ))
registerGame(GameInfo(289, SmallPileOn, "Small PileOn",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 5, 6, 7, 8, 9, 10, 11, 12),
                      rules_filename = "pileon.html"))
## registerGame(GameInfo(341, PileOn2Decks, "PileOn (2 decks)",
##                       GI.GT_2DECK_TYPE | GI.GT_OPEN,, 2, 0))


