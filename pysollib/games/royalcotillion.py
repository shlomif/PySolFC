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
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from unionsquare import UnionSquare_Foundation


# ************************************************************************
# * Royal Cotillion
# ************************************************************************

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


# ************************************************************************
# * Odd and Even
# ************************************************************************

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
        l.createText(s.talon, "n")
        l.createRoundText(s.talon, 'nnn')
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "n")

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Kingdom
# ************************************************************************

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
            x += l.XS
        x, y, = l.XM, y + l.YS
        for i in range(8):
            s.reserves.append(ReserveStack(x, y, self, max_accept=0))
            x += l.XS
        x, y = l.XM + 3*l.XS, l.YM + 3*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "sw")
        x += l.XS
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


# ************************************************************************
# * Alhambra
# * Granada
# * Reserves
# * Grant's Reinforcement
# ************************************************************************

class Alhambra_Hint(CautiousDefaultHint):
    def _getDropCardScore(self, score, color, r, t, ncards):
        return 93000, color


class Alhambra_RowStack(UD_SS_RowStack):
    getBottomImage = Stack._getReserveBottomImage
    def getHelp(self):
        return _('Waste. Build up or down by suit.')


class Alhambra_Talon(DealRowTalonStack):
    def canDealCards(self):
        r_cards = sum([len(r.cards) for r in self.game.s.rows])
        if self.cards:
            return True
        elif r_cards and self.round != self.max_rounds:
            return True
        return False

    def _deal(self):
        num_cards = 0
        for r in self.game.s.rows:
            if self.cards:
                self.game.flipAndMoveMove(self, r)
                num_cards += 1

    def dealCards(self, sound=False):
        old_state = self.game.enterState(self.game.S_DEAL)
        num_cards = 0
        rows = self.game.s.rows
        r_cards = sum([len(r.cards) for r in self.game.s.rows])
        if self.cards:
            if sound and not self.game.demo:
                self.game.playSample("dealwaste")
            if len(self.game.s.rows) > 1:
                num_cards = self.dealRowAvail(sound=False, frames=4)
            else:
                num_cards = self._deal()
        elif r_cards and self.round != self.max_rounds:
            if sound:
                self.game.playSample("turnwaste", priority=20)
            for r in rows:
                for i in range(len(r.cards)):
                    self.game.moveMove(1, r, self, frames=0)
                    self.game.flipMove(self)
            if len(self.game.s.rows) > 1:
                num_cards = self.dealRowAvail(sound=False, frames=4)
            else:
                num_cards = self._deal()
            self.game.nextRoundMove(self)
        self.game.leaveState(old_state)
        return num_cards


class Alhambra(Game):
    Hint_Class = Alhambra_Hint

    RowStack_Class = StackWrapper(Alhambra_RowStack, base_rank=ANY_RANK)

    def createGame(self, rows=1, reserves=8, playcards=3):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+8*l.XS, l.YM+3.5*l.YS+playcards*l.YOFFSET
        h += l.TEXT_HEIGHT
        self.setSize(w, h)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    max_move=0))
            x = x + l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 max_move=0, base_rank=KING, dir=-1))
            x = x + l.XS
        x, y, = l.XM+(8-reserves)*l.XS/2, y+l.YS
        for i in range(reserves):
            stack = OpenStack(x, y, self, max_accept=0)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.reserves.append(stack)
            x = x + l.XS
        x, y = l.XM+(8-1-rows)*l.XS/2, self.height-l.YS
        s.talon = Alhambra_Talon(x, y, self, max_rounds=3)
        if rows == 1:
            l.createText(s.talon, 'sw')
        else:
            l.createText(s.talon, 'n')
        anchor = 'nn'
        if rows > 1:
            anchor = 'nnn'
        l.createRoundText(s.talon, anchor)

        x += l.XS
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self, mod=13, max_accept=1)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
            s.rows.append(stack)
            x += l.XS
            if rows == 1:
                l.createText(stack, 'se')
            else:
                l.createText(stack, 'n')

        # define stack-groups (non default)
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move one Aces and Kings of first deck to top of the Talon (i.e. first card to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.deck == 0 and c.rank in (ACE, KING), (c.rank, c.suit)), 8)

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SSW


class Granada(Alhambra):
    def createGame(self):
        Alhambra.createGame(self, rows=4)


class Reserves_RowStack(UD_RK_RowStack):
    getBottomImage = Stack._getReserveBottomImage
    def getHelp(self):
        return _('Waste. Build up or down regardless of suit.')

class Reserves(Alhambra):
    RowStack_Class = StackWrapper(Reserves_RowStack, base_rank=NO_RANK)

    def createGame(self):
        Alhambra.createGame(self, reserves=4, playcards=11)

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(11):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_RKW


class GrantsReinforcement(Reserves):
    RowStack_Class = StackWrapper(Alhambra_RowStack, base_rank=NO_RANK)

    def fillStack(self, stack):
        for r in self.s.reserves:
            if r.cards:
                continue
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, r)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * Carpet
# ************************************************************************

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


# ************************************************************************
# * British Constitution
# ************************************************************************

class BritishConstitution_RowStackMethods:
    def acceptsCards(self, from_stack, cards):
        if self in self.game.s.rows[:8] and from_stack in self.game.s.rows[8:16]:
            return True
        if self in self.game.s.rows[8:16] and from_stack in self.game.s.rows[16:24]:
            return True
        if self in self.game.s.rows[16:24] and from_stack in self.game.s.rows[24:]:
            return True
        if self in self.game.s.rows[24:] and from_stack is self.game.s.waste:
            return True
        return False

class BritishConstitution_RowStack(BritishConstitution_RowStackMethods, AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return BritishConstitution_RowStackMethods.acceptsCards(self, from_stack, cards)

class NewBritishConstitution_RowStack(BritishConstitution_RowStackMethods, RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return BritishConstitution_RowStackMethods.acceptsCards(self, from_stack, cards)


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
            s.foundations.append(BritishConstitution_Foundation(x, y, self,
                                 suit=int(i/2), max_cards=11))
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
        y += l.YS+l.TEXT_HEIGHT
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

    shallHighlightMatch = Game._shallHighlightMatch_AC


class NewBritishConstitution(BritishConstitution):
    RowStack_Class = StackWrapper(NewBritishConstitution_RowStack, base_rank=JACK)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Twenty
# ************************************************************************

class Twenty_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        return len(self.cards) == 0
    def getHelp(self):
        return _('Tableau. Empty piles can be filled with any card.')

class Twenty(Game):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+10*l.XS, l.YM+3*l.YS+10*l.YOFFSET)

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

        for y in (l.YM+l.YS, l.YM+2*l.YS+5*l.YOFFSET):
            x = l.XM
            for i in range(10):
                s.rows.append(Twenty_RowStack(x, y, self,
                              base_rank=ANY_RANK, max_accept=1))
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


# ************************************************************************
# * Three Pirates
# ************************************************************************

class ThreePirates_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        num_cards = 0
        old_state = self.game.enterState(self.game.S_DEAL)
        if self.cards:
            if sound and not self.game.demo:
                self.game.playSample("dealwaste")
            num_cards = self.dealRowAvail(rows=self.game.s.reserves,
                                          sound=False, frames=4)
        self.game.leaveState(old_state)
        return num_cards


class ThreePirates(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        l, s = Layout(self), self.s

        self.setSize(l.XM+10*l.XS, l.YM+3*l.YS+16*l.YOFFSET)

        x, y, = l.XM+l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x = x + l.XS

        x, y, = l.XM, l.YM+l.YS
        for i in range(10):
            s.rows.append(SS_RowStack(x, y, self, max_move=1))
            x += l.XS

        x, y = l.XM, self.height-l.YS
        s.talon = ThreePirates_Talon(x, y, self)
        l.createText(s.talon, 'n')
        x += l.XS
        for i in (0,1,2):
            stack = WasteStack(x, y, self)
            s.reserves.append(stack)
            l.createText(stack, 'n')
            x += l.XS

        l.defaultStackGroups()

    def startGame(self):
        for i in (0,1,2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Frames
# ************************************************************************

class Frames_Hint(CautiousDefaultHint):
    def computeHints(self):
        CautiousDefaultHint.computeHints(self)
        if self.hints:
            return
        if not self.game.s.talon.cards:
            return
        for s in self.game.s.reserves:
            if s.cards:
                for r in self.game.s.rows:
                    if r.acceptsCards(s, s.cards):
                        self.addHint(5000, 1, s, r)


class Frames_Foundation(UnionSquare_Foundation):
    def acceptsCards(self, from_stack, cards):
        if not UnionSquare_Foundation.acceptsCards(self, from_stack, cards):
            return False
        return from_stack in self.game.s.rows


class Frames_RowStack(UD_SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not UD_SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not (from_stack in self.game.s.reserves or
                from_stack in self.game.s.rows):
            return False
        if len(self.cards) > 1:
            cs = self.cards+cards
            if not (isSameSuitSequence(cs, dir=1) or
                    isSameSuitSequence(cs, dir=-1)):
                return False
        if from_stack in self.game.s.reserves:
            if (hasattr(self.cap, 'column') and
                self.cap.column != from_stack.cap.column):
                return False
            if (hasattr(self.cap, 'row') and
                self.cap.row != from_stack.cap.row):
                return False
        return True


class Frames(Game):
    Hint_Class = Frames_Hint #CautiousDefaultHint

    def createGame(self):
        l, s = Layout(self), self.s

        self.setSize(l.XM+8*l.XS, l.YM+5*l.YS)

        x0, y0 = l.XM+2*l.XS, l.YM
        # foundations (corners)
        suit = 0
        for i, j in ((0,0),(5,0),(0,4),(5,4)):
            x, y = x0+i*l.XS, y0+j*l.YS
            s.foundations.append(Frames_Foundation(x, y, self,
                                 suit=suit, dir=0, max_cards=26))
            suit += 1
        # rows (frame)
        for i in (1,2,3,4):
            for j in (0,4):
                x, y = x0+i*l.XS, y0+j*l.YS
                stack = Frames_RowStack(x, y, self)
                s.rows.append(stack)
                stack.cap.addattr(column=i)
                stack.CARD_YOFFSET = 0
        for i in (0,5):
            for j in (1,2,3):
                x, y = x0+i*l.XS, y0+j*l.YS
                stack = Frames_RowStack(x, y, self)
                s.rows.append(stack)
                stack.cap.addattr(row=j)
                stack.CARD_YOFFSET = 0
        # reserves (picture)
        for j in (1,2,3):
            for i in (1,2,3,4):
                x, y = x0+i*l.XS, y0+j*l.YS
                stack = OpenStack(x, y, self)
                s.reserves.append(stack)
                stack.cap.addattr(column=i)
                stack.cap.addattr(row=j)
        # talon & waste
        x, y, = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards and stack in self.s.reserves:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.waste.moveMove(1, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Royal Rendezvous
# ************************************************************************

class RoyalRendezvous(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9.5*l.XS, l.YM+4.5*l.YS)

        y = l.YM
        # kings
        suit = 0
        for i in (0,1,6,7):
            x = l.XM+(1.5+i)*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit,
                                 base_rank=KING, max_cards=1))
            suit += 1
        # aces
        suit = 0
        for i in (2,3,4,5):
            x = l.XM+(1.5+i)*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit))
            suit += 1
        y += l.YS
        # twos
        suit = 0
        for i in (0,1,6,7):
            x = l.XM+(1.5+i)*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit,
                                 base_rank=1, dir=2, max_cards=6))
            suit += 1
        # aces
        suit = 0
        for i in (2,3,4,5):
            x = l.XM+(1.5+i)*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit,
                                 dir=2, max_cards=6))
            suit += 1

        y += 1.5*l.YS
        for i in (0,1):
            x = l.XM+1.5*l.XS
            for j in range(8):
                s.rows.append(OpenStack(x, y, self, max_accept=0))
                x += l.XS
            y += l.YS

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        # move twos to top
        cards = self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == 1 and c.deck == 0, c.suit))
        # move aces to top
        cards = self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))
        return cards


    def startGame(self):
        # deal aces
        self.s.talon.dealRow(rows=self.s.foundations[4:8], frames=0)
        self.s.talon.dealRow(rows=self.s.foundations[12:16], frames=0)
        # deal twos
        self.s.talon.dealRow(rows=self.s.foundations[8:12], frames=0)
        #
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    def fillStack(self, stack):
        if not stack.cards and stack in self.s.rows:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.waste.moveMove(1, stack)
                self.leaveState(old_state)


# ************************************************************************
# * Shady Lanes
# ************************************************************************

class ShadyLanes_Hint(CautiousDefaultHint):
    def computeHints(self):
        CautiousDefaultHint.computeHints(self)
        if self.hints:
            return
        for r in self.game.s.rows:
            if not r.cards:
                for s in self.game.s.reserves:
                    if s.cards:
                        self.addHint(5000-s.cards[0].rank, 1, s, r)


class ShadyLanes_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards:
            # check the rank
            if self.cards[-1].rank+1 != cards[0].rank:
                return False
        return True

    def getHelp(self):
        return _('Foundation. Build up by color.')


class ShadyLanes_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return from_stack in self.game.s.reserves
        return True


class ShadyLanes(Game):
    Hint_Class = ShadyLanes_Hint

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+5*l.YS)

        x, y = l.XM, l.YM
        for i in range(8):
            suit = i/2
            color = suit/2
            s.foundations.append(ShadyLanes_Foundation(x, y, self,
                          base_suit=suit, suit=ANY_SUIT, color=color))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            s.rows.append(ShadyLanes_RowStack(x, y, self, max_move=1))
            x += l.XS

        x, y = self.width-l.XS, l.YM+l.YS
        for i in range(4):
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            y += l.YS

        l.defaultStackGroups()


    def fillStack(self, stack):
        if not stack.cards and stack in self.s.reserves:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.waste.moveMove(1, stack)
                self.leaveState(old_state)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Four Winds
# * Boxing the Compass
# ************************************************************************

class FourWinds(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+6*l.YS)

        # vertical rows
        x = l.XM+l.XS
        for i in (0, 1):
            y = l.YM+l.YS
            for j in range(4):
                stack = ReserveStack(x, y, self, base_suit=i)
                stack.getBottomImage = stack._getSuitBottomImage
                s.rows.append(stack)
                y += l.YS
            x += 6*l.XS
        # horizontal rows
        y = l.YM+l.YS
        for i in (2, 3):
            x = l.XM+2.5*l.XS
            for j in range(4):
                stack = ReserveStack(x, y, self, base_suit=i)
                stack.getBottomImage = stack._getSuitBottomImage
                s.rows.append(stack)
                x += l.XS
            y += 3*l.YS
        # foundations
        decks = self.gameinfo.decks
        for k in range(decks):
            suit = 0
            for i, j in ((0, 3-decks*0.5+k),
                         (8, 3-decks*0.5+k),
                         (4.5-decks*0.5+k, 0),
                         (4.5-decks*0.5+k, 5)):
                x, y = l.XM+i*l.XS, l.YM+j*l.YS
                s.foundations.append(SS_FoundationStack(x, y, self,
                                     suit=suit, max_move=0))
                suit += 1
        # talon & waste
        x, y = l.XM+3.5*l.XS, l.YM+2.5*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=2)
        l.createText(s.talon, 's')
        l.createRoundText(self.s.talon, 'nn')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')

        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))


class BoxingTheCompass(FourWinds):
    pass


# ************************************************************************
# * Colonel
# ************************************************************************

class Colonel_Hint(DefaultHint):
    def _getMoveCardBonus(self, r, t, pile, rpile):
        if r in self.game.s.rows and t in self.game.s.rows:
            if rpile:
                return 0
        return DefaultHint._getMoveCardBonus(self, r, t, pile, rpile)


class Colonel_RowStack(SS_RowStack):

    def _getStackIndex(self, stack):
        index = list(self.game.s.rows).index(stack)
        if index < 12:
            row = 0
        elif 12 <= index < 24:
            row = 1
        else:
            row = 2
        return index, row

    def acceptsCards(self, from_stack, cards):
        if not SS_RowStack.acceptsCards(self, from_stack, cards):
            return False

        self_index, self_row = self._getStackIndex(self)

        if self_row in (1,2):
            above_stack = self.game.s.rows[self_index-12]
            if not above_stack.cards:
                return False

        below_stack = None
        if self_row in (0,1):
            below_stack = self.game.s.rows[self_index+12]

        # from_stack is waste
        if from_stack is self.game.s.waste:
            if below_stack is None or not below_stack.cards:
                return True
            else:
                return False

        #  from_stack in rows
        from_index, from_row = self._getStackIndex(from_stack)
        if below_stack and below_stack.cards:
            return from_stack is below_stack
        return from_row > self_row

    def canMoveCards(self, cards):
        self_index, self_row = self._getStackIndex(self)
        if self_row in (0,1):
            below_stack = self.game.s.rows[self_index+12]
            if below_stack.cards:
                return False
        return SS_RowStack.canMoveCards(self, cards)

    getBottomImage = Stack._getReserveBottomImage


class Colonel(Game):
    Hint_Class = Colonel_Hint

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+12*l.XS, l.YM+5*l.YS)

        x, y = l.XM+2*l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2,
                                                    max_move=0))
            x += l.XS

        y = l.YM+l.YS
        for i in range(3):
            x = l.XM
            for j in range(12):
                stack = Colonel_RowStack(x, y, self, max_move=1)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        x, y = l.XM+5*l.XS, l.YM+4*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'sw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * The Red and the Black
# ************************************************************************



class TheRedAndTheBlack_Foundation(AC_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack is self.game.s.waste or from_stack in self.game.s.rows:
            return True
        return False

class TheRedAndTheBlack_Reserve(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack is self.game.s.waste:
            return True
        return False


class TheRedAndTheBlack(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM + 8*l.XS, l.YM + 4.5*l.YS)

        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(TheRedAndTheBlack_Foundation(x, y, self,
                                                              suit=i/2))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            stack = AC_RowStack(x, y, self, max_move=1)
            stack.getBottomImage = stack._getReserveBottomImage
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+2*l.YS
        for i in range(4):
            s.reserves.append(TheRedAndTheBlack_Reserve(x, y, self))
            x += l.XS
        x, y = l.XM+3*l.XS, l.YM+3.5*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "sw")
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()       # deal first card to WasteStack

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == ACE, c.suit))

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Twilight Zone
# ************************************************************************

class TwilightZone_Foundation(AC_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack is self.game.s.waste or \
               from_stack in self.game.s.reserves:
            return False
        return True


class TwilightZone_Talon(OpenTalonStack, WasteTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler

    def prepareStack(self):
        OpenTalonStack.prepareStack(self)
        self.waste = self.game.s.waste

    canDealCards = WasteTalonStack.canDealCards
    dealCards = WasteTalonStack.dealCards


class TwilightZone_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack is self.game.s.waste:
            return False
        return True


class TwilightZone_Waste(WasteStack):
    def acceptsCards(self, from_stack, cards):
        if not WasteStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack is self.game.s.talon


class TwilightZone(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+7*l.XS, l.YM+5*l.YS)

        # create stacks
        y = l.YM
        for i in range(2):
            x = l.XM+3*l.XS
            for j in range(4):
                s.foundations.append(TwilightZone_Foundation(x, y, self,
                                                             suit=j))
                x += l.XS
            y += l.YS

        x, y = l.XM+3*l.XS, l.YM+2*l.YS
        for i in range(4):
            stack = TwilightZone_RowStack(x, y, self, max_move=1)
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)
            x += l.XS

        x, y = l.XM+3*l.XS, l.YM+4*l.YS
        for i in range(4):
            s.reserves.append(OpenStack(x, y, self))
            x += l.XS


        x, y = l.XM, l.YM+l.YS/2
        s.talon = TwilightZone_Talon(x, y, self, max_move=1, max_rounds=2)
        l.createText(s.talon, 's')
        l.createRoundText(s.talon, 'nn')
        x += l.XS
        s.waste = TwilightZone_Waste(x, y, self, max_accept=1)
        l.createText(s.waste, 's')


        # define stack-groups
        l.defaultStackGroups()
        self.sg.dropstacks.append(s.talon)
        self.sg.openstacks.append(s.waste)


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.fillStack()

    def fillStack(self, stack):
        if not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if stack in self.s.rows:
                i = list(self.s.rows).index(stack)
                from_stack = self.s.reserves[i]
                if from_stack.cards:
                    from_stack.moveMove(1, stack)
            elif stack in self.s.reserves:
                from_stack = self.s.waste
                if not from_stack.cards:
                    from_stack = self.s.talon
                if from_stack.cards:
                    from_stack.moveMove(1, stack)
            self.leaveState(old_state)

    def _autoDeal(self, sound=True):
        return 0

    shallHighlightMatch = Game._shallHighlightMatch_AC



# register the game
registerGame(GameInfo(54, RoyalCotillion, "Royal Cotillion",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_LUCK))
registerGame(GameInfo(55, OddAndEven, "Odd and Even",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_LUCK))
registerGame(GameInfo(143, Kingdom, "Kingdom",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(234, Alhambra, "Alhambra",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(97, Carpet, "Carpet",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(391, BritishConstitution, "British Constitution",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED,
                      ranks=range(11), # without Queens and Kings
                      altnames=("Constitution",) ))
registerGame(GameInfo(392, NewBritishConstitution, "New British Constitution",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED,
                      ranks=range(11) # without Queens and Kings
                      ))
registerGame(GameInfo(443, Twenty, "Twenty",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(465, Granada, "Granada",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(579, ThreePirates, "Three Pirates",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(608, Frames, "Frames",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(609, GrantsReinforcement, "Grant's Reinforcement",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(638, RoyalRendezvous, "Royal Rendezvous",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(639, ShadyLanes, "Shady Lanes",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(675, FourWinds, "Four Winds",
                      GI.GT_1DECK_TYPE, 1, 1, GI.SL_BALANCED))
registerGame(GameInfo(676, BoxingTheCompass, "Boxing the Compass",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(693, Colonel, "Colonel",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(695, TheRedAndTheBlack, "The Red and the Black",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(748, TwilightZone, "Twilight Zone",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(752, Reserves, "Reserves",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))

