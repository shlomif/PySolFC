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
# //
# ************************************************************************/


class Tournament_Talon(TalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds and not self.cards:
            return False
        return not self.game.isGameWon()

    def dealCards(self, sound=0):
        if len(self.cards) == 0:
            self._redeal()
        self.game.startDealSample()
        n = 0
        for r in self.game.s.rows:
            for i in range(4):
                if not self.cards:
                    break
                n += self.dealRow([r])
        self.game.stopSamples()
        return n

    def _redeal(self):
        # move all cards to the Talon
        lr = len(self.game.s.rows)
        num_cards = 0
        assert len(self.cards) == 0
        for r in self.game.s.rows[::-1]:
            for i in range(len(r.cards)):
                num_cards = num_cards + 1
                self.game.moveMove(1, r, self, frames=0)
                self.game.flipMove(self)
        assert len(self.cards) == num_cards
        if num_cards == 0:          # game already finished
            return
        self.game.nextRoundMove(self)
        return


class Tournament(Game):

    ROW_YOFFSET = True

    #
    # game layout
    #

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+10*l.XS, max(l.YM+l.YS+20*l.YOFFSET, 2*l.YM+5*l.YS))

        # create stacks
        x, y, = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x = x + l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            x = x + l.XS
        x, y = l.XM+2*l.XS, 2*l.YM+l.YS
        for i in range(6):
            stack = BasicRowStack(x, y, self, max_move=1, max_accept=0)
            s.rows.append(stack)
            if not self.ROW_YOFFSET:
                stack.CARD_YOFFSET = 0
            x = x + l.XS

        x, y = l.XM, 2*l.YM+l.YS
        for i in range(4):
            self.s.reserves.append(ReserveStack(x, y, self))
            y += l.YS
        x, y = l.XM+9*l.XS, 2*l.YM+l.YS
        for i in range(4):
            self.s.reserves.append(ReserveStack(x, y, self))
            y += l.YS

        s.talon = Tournament_Talon(l.XM, l.YM, self, max_rounds=3)
        l.createText(s.talon, "se")
        tx, ty, ta, tf = l.getTextAttr(s.talon, "ne")
        font = self.app.getFont("canvas_default")
        s.talon.texts.rounds = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        for c in cards[-8:]:
            if c.rank in (ACE, KING):
                return cards
        #
        for c in cards:
            if c.rank in (ACE, KING):
                break
        cards.remove(c)
        return cards+[c]

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(self.s.reserves)
        for r in self.s.rows:
            for i in range(4):
                self.s.talon.dealRow([r])

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if not self.demo:
                self.startDealSample()
            for i in range(4):
                if not self.s.talon.cards:
                    break
                self.s.talon.dealRow([stack])
            if not self.demo:
                self.stopSamples()


class LaNivernaise(Tournament):
    ROW_YOFFSET = False

# /***********************************************************************
# // Kingsdown Eights
# ************************************************************************/

class KingsdownEights_Talon(DealRowTalonStack):
    def dealCards(self, sound=0):
        if len(self.cards) == 0:
            self._redeal()
        self.game.startDealSample()
        n = 0
        for r in self.game.s.reserves:
            for i in range(4):
                if not self.cards:
                    break
                n += self.dealRow([r])
        self.game.stopSamples()
        return n

class KingsdownEights_Row(AC_RowStack):
    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()

class KingsdownEights(Game):

    Hint_Class = CautiousDefaultHint

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+10*l.XS, max(l.YM+2*l.YS+12*l.YOFFSET,
                                       l.YM+5*l.YS))

        # create stacks
        x = l.XM
        for i in range(2):
            y = l.YM+l.YS
            for j in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j))
                y += l.YS
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM
        for i in range(8):
            stack = KingsdownEights_Row(x, y, self, max_move=1)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            s.rows.append(stack)
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(8):
            stack = OpenStack(x, y, self, max_accept=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.reserves.append(stack)
            x += l.XS
        s.talon = KingsdownEights_Talon(l.XM, l.YM, self, max_rounds=1)
        l.createText(s.talon, "se")

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# /***********************************************************************
# // Saxony
# ************************************************************************/

class Saxony_Reserve(SS_RowStack):
    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()
    def getHelp(self):
        return _('Reserve. Build down by suit.')


class Saxony(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+11*l.XS, 2*l.YM+max(2*l.YS+12*l.YOFFSET, 5*l.YS))

        x, y, = l.XM+1.5*l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i%4))
            x = x + l.XS
        x, y = l.XM+1.5*l.XS, 2*l.YM+l.YS
        for i in range(8):
            s.rows.append(BasicRowStack(x, y, self, max_move=1, max_accept=0))
            x = x + l.XS
        x, y = l.XM, 2*l.YM+l.YS
        for i in range(4):
            stack = Saxony_Reserve(x, y, self, max_move=1)
            self.s.reserves.append(stack)
            stack.CARD_YOFFSET = 0
            y += l.YS
        x, y = self.width-l.XS, 2*l.YM+l.YS
        for i in range(4):
            self.s.reserves.append(ReserveStack(x, y, self))
            y += l.YS
        s.talon = DealRowTalonStack(l.XM, l.YM, self)
        l.createText(s.talon, "ne")

        l.defaultStackGroups()


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()



# register the game
registerGame(GameInfo(303, Tournament, "Tournament",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(304, LaNivernaise, "La Nivernaise",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_MOSTLY_LUCK,
                      altnames = ("Napoleon's Flank", ),))
registerGame(GameInfo(386, KingsdownEights, "Kingsdown Eights",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(645, Saxony, "Saxony",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))




