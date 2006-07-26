##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
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
##---------------------------------------------------------------------------##

__all__ = []

# imports
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# /***********************************************************************
# // Grand Duchess
# ************************************************************************/

class GrandDuchess_Talon(RedealTalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds:
            return len(self.cards) != 0
        return not self.game.isGameWon()

    def dealCards(self, sound=0):
        rows = self.game.s.rows
        reserves = self.game.s.reserves
        if not self.cards:
            RedealTalonStack.redealCards(self, rows=rows+reserves, sound=0)
        if sound and not self.game.demo:
            self.game.startDealSample()
        num_cards = 0
        if self.round != 4:
            num_cards += self.dealRowAvail(rows=[reserves[0]], flip=0)
        num_cards += self.dealRowAvail()
        if self.round != 4:
            num_cards += self.dealRowAvail(rows=[reserves[1]], flip=0)
        if not self.cards:
            for s in reserves:
                self.game.flipAllMove(s)
        if sound and not self.game.demo:
            self.game.stopSamples()
        return num_cards


class GrandDuchess_Reserve(ArbitraryStack):
    def canFlipCard(self):
        return False


class GrandDuchess(Game):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+9*l.XS, l.YM+2*l.YS+18*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=i, base_rank=KING, dir=-1))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            stack = BasicRowStack(x, y, self, max_move=1, max_accept=0)
            stack.CARD_YOFFSET = l.YOFFSET
            s.rows.append(stack)
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        s.reserves.append(GrandDuchess_Reserve(x, y, self))
        x, y = l.XM+7*l.XS, l.YM+l.YS
        s.reserves.append(GrandDuchess_Reserve(x, y, self))

        x, y = self.width-l.XS, self.height-l.YS
        s.talon = GrandDuchess_Talon(x, y, self, max_rounds=4)
        l.createText(s.talon, 'n')
        tx, ty, ta, tf = l.getTextAttr(s.talon, "nn")
        font = self.app.getFont("canvas_default")
        s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                             tx, ty-l.TEXT_MARGIN,
                                             anchor=ta, font=font)
        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=[self.s.reserves[0]], flip=0)
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=[self.s.reserves[1]], flip=0)


    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


registerGame(GameInfo(557, GrandDuchess, "Grand Duchess",
                      GI.GT_2DECK_TYPE, 2, 3))


