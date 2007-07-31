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

    def dealCards(self, sound=False):
        rows = self.game.s.rows
        reserves = self.game.s.reserves
        if not self.cards:
            RedealTalonStack.redealCards(self, rows=rows+reserves, sound=False)
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

    def createGame(self, rows=4):
        # create layout
        max_rows = max(10, 4+rows)
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+max_rows*l.XS, l.YM+2*l.YS+18*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = GrandDuchess_Talon(x, y, self, max_rounds=4)
        l.createText(s.talon, 'se')
        tx, ty, ta, tf = l.getTextAttr(s.talon, 'ne')
        font = self.app.getFont('canvas_default')
        s.talon.texts.rounds = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)

        x += 2*l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=i, base_rank=KING, dir=-1))
            x += l.XS
        x, y = l.XM+(max_rows-rows)*l.XS/2, l.YM+l.YS
        for i in range(rows):
            stack = BasicRowStack(x, y, self, max_move=1, max_accept=0)
            stack.CARD_YOFFSET = l.YOFFSET
            s.rows.append(stack)
            x += l.XS
        dx = (max_rows-rows)*l.XS/4-l.XS/2
        x, y = l.XM+dx, l.YM+l.YS
        s.reserves.append(GrandDuchess_Reserve(x, y, self))
        x, y = self.width-dx-l.XS, l.YM+l.YS
        s.reserves.append(GrandDuchess_Reserve(x, y, self))

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

    def redealCards(self):
        pass


    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


# /***********************************************************************
# // Parisienne
# ************************************************************************/

class Parisienne(GrandDuchess):
    def _shuffleHook(self, cards):
        # move one Ace and one King of each suit to top of the Talon
        # (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
            lambda c: (c.rank in (ACE, KING) and c.deck == 0, (c.rank, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        GrandDuchess.startGame(self)


class GrandDuchessPlus(GrandDuchess):
    def createGame(self):
        GrandDuchess.createGame(self, rows=6)



registerGame(GameInfo(557, GrandDuchess, "Grand Duchess",
                      GI.GT_2DECK_TYPE, 2, 3))
registerGame(GameInfo(617, Parisienne, "Parisienne",
                      GI.GT_2DECK_TYPE, 2, 3,
                      rules_filename='grandduchess.html',
                      altnames=('La Parisienne', 'Parisian') ))
registerGame(GameInfo(618, GrandDuchessPlus, "Grand Duchess +",
                      GI.GT_2DECK_TYPE, 2, 3))

