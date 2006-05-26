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
# // Royal Cotillion
# ************************************************************************/

class RoyalCotillion_Foundation(SS_FoundationStack):
    def getBottomImage(self):
        if self.cap.base_rank == 1:
            return self.game.app.images.getLetter(1)
        return self.game.app.images.getSuitBottom(self.cap.base_suit)


class RoyalCotillion(Game):
    Foundation_Class = RoyalCotillion_Foundation

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 10*l.XS, l.YM + 4*l.YS)

        # create stacks
        for i in range(4):
            x, y, = l.XM + i*l.XS, l.YM
            s.rows.append(BasicRowStack(x, y, self, max_accept=0))
        for i in range(4):
            x, y, = l.XM + 4*l.XS, l.YM + i*l.YS
            s.foundations.append(self.Foundation_Class(x, y, self, i, dir=2, mod=13))
            x = x + l.XS
            s.foundations.append(self.Foundation_Class(x, y, self, i, dir=2, mod=13, base_rank=1))
        for i in range(4):
            for j in range(4):
                x, y, = l.XM + (j+6)*l.XS, l.YM + i*l.YS
                s.reserves.append(ReserveStack(x, y, self, max_accept=0))
        x, y = l.XM + l.XS, self.height - l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "sw")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.reserves and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return (self.sg.dropstacks, (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return (self.sg.dropstacks, self.sg.dropstacks, self.sg.dropstacks)


# /***********************************************************************
# // Odd and Even
# ************************************************************************/

class OddAndEven(RoyalCotillion):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, i, dir=2, mod=13))
            x = x + l.XS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, i, dir=2, mod=13, base_rank=1))
            x = x + l.XS
        for i in range(2):
            x, y, = l.XM + ((4,3)[i])*l.XS, l.YM + (i+1)*l.YS
            for j in range((4,5)[i]):
                s.reserves.append(ReserveStack(x, y, self, max_accept=0))
                x = x + l.XS
        x, y = l.XM, self.height - l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, "nn")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "nn")

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Kingdom
# ************************************************************************/

class Kingdom(RoyalCotillion):
    Foundation_Class = RK_FoundationStack

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(8):
            s.foundations.append(self.Foundation_Class(x, y, self, ANY_SUIT))
            x = x + l.XS
        x, y, = l.XM, y + l.YS
        for i in range(8):
            s.reserves.append(ReserveStack(x, y, self, max_accept=0))
            x = x + l.XS
        x, y = l.XM + 3*l.XS, y + 3*l.YS/2
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "sw")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move one Ace to top of the Talon (i.e. first card to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit), 1)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=(self.s.foundations[0],))
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Alhambra
# ************************************************************************/

class Alhambra_Waste(WasteStack):
    def acceptsCards(self, from_stack, cards):
        if not WasteStack.acceptsCards(self, from_stack, cards):
            return 0
        # check cards
        if not self.cards:
            return 0
        c1, c2 = self.cards[-1], cards[0]
        return c1.suit == c2.suit and ((c1.rank + 1) % self.cap.mod == c2.rank or (c2.rank + 1) % self.cap.mod == c1.rank)


class Alhambra(Game):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i, max_move=0))
            x = x + l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i, max_move=0,
                                                    base_rank=KING, dir=-1))
            x = x + l.XS
        x, y, = l.XM, y + l.YS
        for i in range(8):
            s.reserves.append(BasicRowStack(x, y, self, max_accept=0))
            x = x + l.XS
        x, y = l.XM + 3*l.XS, y + 2*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "sw")
        x = x + l.XS
        s.waste = Alhambra_Waste(x, y, self, mod=13, max_accept=1)
        l.createText(s.waste, "se")

        # define stack-groups (non default)
        s.rows.append(s.waste)
        l.defaultStackGroups()


    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move one Aces and Kings of first deck to top of the Talon (i.e. first card to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.deck == 0 and c.rank in (0, 12), (c.rank, c.suit)), 8)

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()


# /***********************************************************************
# // Carpet
# ************************************************************************/

class Carpet(Game):
    Foundation_Class = SS_FoundationStack

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 9*l.XS, l.YM + 4*l.YS)

        # create stacks
        for i in range(4):
            for j in range(5):
                x, y = l.XM + (j+3)*l.XS, l.YM + i*l.YS
                s.rows.append(ReserveStack(x, y, self))
        for i in range(4):
            dx, dy = ((2,1), (8,1), (2,2), (8,2))[i]
            x, y = l.XM + dx*l.XS, l.YM + dy*l.YS
            s.foundations.append(self.Foundation_Class(x, y, self, i))
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "se")
        y = y + l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // British Constitution
# ************************************************************************/

class BritishConstitution_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if self in self.game.s.rows[:8] and from_stack in self.game.s.rows[8:16]:
            return True
        if self in self.game.s.rows[8:16] and from_stack in self.game.s.rows[16:24]:
            return True
        if self in self.game.s.rows[16:24] and from_stack in self.game.s.rows[24:]:
            return True
        if self in self.game.s.rows[24:] and from_stack is self.game.s.waste:
            return True
        return False


class BritishConstitution_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows[:8]:
            return True
        return False


class BritishConstitution(Game):
    RowStack_Class = BritishConstitution_RowStack

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 9*l.XS, l.YM + 5*l.YS)

        # create stacks
        x, y = l.XM+l.XS, l.YM
        for i in range(8):
            s.foundations.append(BritishConstitution_Foundation(x, y, self, suit=int(i/2)))
            x += l.XS

        y = l.YM+l.YS
        for i in range(4):
            x = l.XM+l.XS
            for j in range(8):
                stack = self.RowStack_Class(x, y, self, max_move=1)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        y += l.YS+2*l.YM
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == ACE, c.suit))

    def fillStack(self, stack):
        if not stack.cards:
            if stack in self.s.rows[:24]:
                return
            old_state = self.enterState(self.S_FILL)
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows[24:] and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)


class NewBritishConstitution(BritishConstitution):
    RowStack_Class = StackWrapper(BritishConstitution_RowStack, base_rank=JACK)



# /***********************************************************************
# // Twenty
# ************************************************************************/

class Twenty_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        #if not BasicRowStack.acceptsCards(self, from_stack, cards):
        #    return False
        return len(self.cards) == 0

class Twenty(Game):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+10*l.XS, l.YM+3*l.XS+10*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 'se')
        x += 2*l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 base_rank=KING, dir=-1))
            x += l.XS

        for y in (l.YM+l.YS, l.YM+2*l.XS+5*l.YOFFSET):
            x = l.XM
            for i in range(10):
                s.rows.append(Twenty_RowStack(x, y, self))
                x += l.XS

        # define stack-groups
        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (ACE, KING) and c.deck == 1, (c.rank, c.suit)))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


    def fillStack(self, stack):
        if not stack.cards and stack in self.s.rows and self.s.talon.cards:
            old_state = self.enterState(self.S_FILL)
            self.flipMove(self.s.talon)
            self.s.talon.moveMove(1, stack)
            self.leaveState(old_state)



# register the game
registerGame(GameInfo(54, RoyalCotillion, "Royal Cotillion",
                      GI.GT_2DECK_TYPE, 2, 0))
registerGame(GameInfo(55, OddAndEven, "Odd and Even",
                      GI.GT_2DECK_TYPE, 2, 1))
registerGame(GameInfo(143, Kingdom, "Kingdom",
                      GI.GT_2DECK_TYPE, 2, 0))
registerGame(GameInfo(234, Alhambra, "Alhambra",
                      GI.GT_2DECK_TYPE, 2, 2))
registerGame(GameInfo(97, Carpet, "Carpet",
                      GI.GT_1DECK_TYPE, 1, 0))
registerGame(GameInfo(391, BritishConstitution, "British Constitution",
                      GI.GT_2DECK_TYPE, 2, 0,
                      ranks=range(11) # without Queens and Kings
                      ))
registerGame(GameInfo(392, NewBritishConstitution, "New British Constitution",
                      GI.GT_2DECK_TYPE, 2, 0,
                      ranks=range(11) # without Queens and Kings
                      ))
registerGame(GameInfo(443, Twenty, "Twenty",
                      GI.GT_2DECK_TYPE, 2, 0))

