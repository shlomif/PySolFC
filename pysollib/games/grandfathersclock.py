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

class GrandfathersClock_Hint(CautiousDefaultHint):
    # FIXME: demo is not too clever in this game

    def _getDropCardScore(self, score, color, r, t, ncards):
        # drop all cards immediately
        return 92000, color


# /***********************************************************************
# // Grandfather's Clock
# ************************************************************************/

class GrandfathersClock(Game):
    Hint_Class = GrandfathersClock_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 9 cards are fully playable in default window size)
        dh = max(3*l.YS/2+l.CH, l.YS+(9-1)*l.YOFFSET)
        self.setSize(10*l.XS+l.XM, l.YM+2*dh)

        # create stacks
        for i in range(2):
            x, y = l.XM, l.YM + i*dh
            for j in range(4):
                s.rows.append(RK_RowStack(x, y, self, max_move=1, max_accept=1))
                x = x + l.XS
        y = l.YM + dh - l.CH / 2
        self.setRegion(s.rows[:4], (-999, -999, x - l.XM / 2, y))
        self.setRegion(s.rows[4:], (-999,    y, x - l.XM / 2, 999999))
        d = [ (0,0), (1,0.15), (2,0.5), (2.5,1.5), (2,2.5), (1,2.85) ]
        for i in range(len(d)):
            d.append( (0 - d[i][0], 3 - d[i][1]) )
        x0, y0 = l.XM, l.YM + dh - l.CH
        for i in range(12):
            j = (i + 5) % 12
            x = int(round(x0 + ( 6.5+d[j][0]) * l.XS))
            y = int(round(y0 + (-1.5+d[j][1]) * l.YS))
            suit = (1, 2, 0, 3) [i % 4]
            s.foundations.append(SS_FoundationStack(x, y, self, suit,
                                                    base_rank=i+1, mod=13,
                                                    max_move=0))
        s.talon = InitialDealTalonStack(self.width-l.XS, self.height-l.YS, self)

        # define stack-groups
        self.sg.openstacks = s.foundations + s.rows
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #
    def _shuffleHook(self, cards):
        # move clock cards to bottom of the Talon (i.e. last cards to be dealt)
        C, S, H, D = 0*13, 1*13, 2*13, 3*13
        ids = (1+S, 2+H, 3+C, 4+D, 5+S, 6+H, 7+C, 8+D, 9+S, 10+H, 11+C, 12+D)
        clocks = []
        for c in cards[:]:
            if c.id in ids:
                clocks.append(c)
                cards.remove(c)
        # sort clocks reverse by rank
        clocks.sort(lambda a, b: cmp(b.rank, a.rank))
        return clocks + cards

    def startGame(self):
        self.playSample("grandfathersclock", loop=1)
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    shallHighlightMatch = Game._shallHighlightMatch_RK

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        # disable auto drop - this would ruin the whole gameplay
        return ((), (), ())


# /***********************************************************************
# // Dial
# ************************************************************************/

class Dial(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+4*l.YS)

        x0, y0 = l.XM+2*l.XS, l.YM
        rank = 0
        for xx, yy in ((3.5, 0.15),
                       (4.5, 0.5),
                       (5,   1.5),
                       (4.5, 2.5),
                       (3.5, 2.85),
                       (2.5, 3),
                       (1.5, 2.85),
                       (0.5, 2.5),
                       (0,   1.5),
                       (0.5, 0.5),
                       (1.5, 0.15),
                       (2.5, 0),
                       (2.5, 1.5),
                       ):
            x = int(x0 + xx*l.XS)
            y = int(y0 + yy*l.YS)
            s.foundations.append(AC_FoundationStack(x, y, self, suit=ANY_SUIT,
                                 dir=0, max_cards=4, base_rank=rank, max_move=0))
            rank += 1

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()          # deal first card to WasteStack



# register the game
registerGame(GameInfo(261, GrandfathersClock, "Grandfather's Clock",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(682, Dial, "Dial",
                      GI.GT_1DECK_TYPE, 1, 1, GI.SL_LUCK))

