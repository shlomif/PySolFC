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

from montecarlo import MonteCarlo_RowStack


# /***********************************************************************
# // Aces Up
# ************************************************************************/

class AcesUp_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        c = cards[0]
        for s in self.game.s.rows:
            if s is not from_stack and s.cards and s.cards[-1].suit == c.suit:
                if s.cards[-1].rank > c.rank or s.cards[-1].rank == ACE:
                    # found a higher rank or an Ace on the row stacks
                    return c.rank != ACE
        return 0


class AcesUp_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        return len(self.cards) == 0

    clickHandler = BasicRowStack.doubleclickHandler


class AcesUp(Game):
    Foundation_Class = AcesUp_Foundation
    Talon_Class = DealRowTalonStack
    RowStack_Class = StackWrapper(AcesUp_RowStack, max_accept=1)

    #
    # game layout
    #

    def createGame(self, rows=4, reserve=False, **layout):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (rows+3)*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        if reserve:
            l.createText(s.talon, "ne")
        else:
            l.createText(s.talon, "s")
        x = x + 3*l.XS/2
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        x = x + l.XS/2
        stack = self.Foundation_Class(x, y, self, suit=ANY_SUIT, max_move=0,
                                      dir=0, base_rank=ANY_RANK, max_cards=48)
        l.createText(stack, "s")
        s.foundations.append(stack)

        if reserve:
            x, y = l.XM, l.YM+l.YS
            s.reserves.append(self.ReserveStack_Class(x, y, self))

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != 48:
            return 0
        for s in self.s.rows:
            if len(s.cards) != 1 or s.cards[0].rank != ACE:
                return 0
        return 1

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return (self.sg.dropstacks, (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return (self.sg.dropstacks, self.sg.dropstacks, self.sg.dropstacks)


# /***********************************************************************
# // Fortunes
# ************************************************************************/

class Fortunes(AcesUp):
    RowStack_Class = StackWrapper(AcesUp_RowStack, max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS)


# /***********************************************************************
# // Russian Aces
# ************************************************************************/

class RussianAces_Talon(DealRowTalonStack):
    def dealCards(self, sound=0):
        rows = filter(lambda s: not s.cards, self.game.s.rows)
        if not rows:
            rows = self.game.s.rows
        return self.dealRowAvail(rows=rows, sound=sound)


class RussianAces(AcesUp):
    Talon_Class = RussianAces_Talon


# /***********************************************************************
# // Perpetual Motion
# ************************************************************************/

class PerpetualMotion_Talon(DealRowTalonStack):
    def canDealCards(self):
        ## FIXME: this is to avoid loops in the demo
        if self.game.demo and self.game.moves.index >= 500:
            return 0
        return not self.game.isGameWon()

    def dealCards(self, sound=0):
        if self.cards:
            return DealRowTalonStack.dealCards(self, sound=sound)
        game, num_cards = self.game, len(self.cards)
        rows = list(game.s.rows)[:]
        rows.reverse()
        for r in rows:
            while r.cards:
                num_cards = num_cards + 1
                game.moveMove(1, r, self, frames=4)
                if self.cards[-1].face_up:
                    game.flipMove(self)
        assert len(self.cards) == num_cards
        return DealRowTalonStack.dealCards(self, sound=sound)


class PerpetualMotion_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        return isRankSequence(cards, dir=0)


class PerpetualMotion_RowStack(RK_RowStack):
    def canDropCards(self, stacks):
        pile = self.getPile()
        if not pile or len(pile) != 4:
            return (None, 0)
        for s in stacks:
            if s is not self and s.acceptsCards(self, pile):
                return (s, 4)
        return (None, 0)


class PerpetualMotion(Game):

    #
    # game layout
    #

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 7*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = PerpetualMotion_Talon(x, y, self, max_rounds=-1)
        l.createText(s.talon, "s")
        x = x + 3*l.XS/2
        for i in range(4):
            s.rows.append(PerpetualMotion_RowStack(x, y, self, dir=0, base_rank=NO_RANK))
            x = x + l.XS
        x = l.XM + 6*l.XS
        stack = PerpetualMotion_Foundation(x, y, self, ANY_SUIT,
                                           base_rank=ANY_RANK,
                                           max_cards=52, max_move=0,
                                           min_accept=4, max_accept=4)
        l.createText(stack, "s")
        s.foundations.append(stack)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank


# /***********************************************************************
# //
# ************************************************************************/

class AcesUp5(AcesUp):

    def createGame(self):
        AcesUp.createGame(self, rows=5)

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 48


# /***********************************************************************
# // Cover
# ************************************************************************/

class Cover_RowStack(MonteCarlo_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        return self.cards[-1].suit == cards[0].suit


class Cover(AcesUp):
    Foundation_Class = StackWrapper(AbstractFoundationStack, max_accept=0)
    Talon_Class = TalonStack
    RowStack_Class = StackWrapper(Cover_RowStack, max_accept=1)

    FILL_STACKS_AFTER_DROP = 0 # for MonteCarlo_RowStack

    def fillStack(self, stack):
        if not self.s.talon.cards:
            return
        self.startDealSample()
        for r in self.s.rows:
            if not r.cards:
                self.flipMove(self.s.talon)
                self.moveMove(1, self.s.talon, r)
        self.stopSamples()


    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 48


# /***********************************************************************
# // Firing Squad
# ************************************************************************/

class FiringSquad_Foundation(AcesUp_Foundation):
    def acceptsCards(self, from_stack, cards):
        if not AcesUp_Foundation.acceptsCards(self, from_stack, cards):
            return False
        return from_stack in self.game.s.rows

class FiringSquad(AcesUp):
    Foundation_Class = FiringSquad_Foundation
    ReserveStack_Class = ReserveStack
    def createGame(self):
        AcesUp.createGame(self, reserve=True)



# register the game
registerGame(GameInfo(903, AcesUp, "Aces Up",                   # was: 52
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_LUCK,
                      altnames=("Aces High", "Drivel") ))
registerGame(GameInfo(206, Fortunes, "Fortunes",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(213, RussianAces, "Russian Aces",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(130, PerpetualMotion, "Perpetual Motion",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_MOSTLY_LUCK,
                      altnames="First Law"))
registerGame(GameInfo(353, AcesUp5, "Aces Up 5",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(552, Cover, "Cover",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(583, FiringSquad, "Firing Squad",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
