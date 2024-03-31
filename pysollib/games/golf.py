#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

import pysollib.game
from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.games.pileon import FourByFour_Hint
from pysollib.hint import AbstractHint, CautiousDefaultHint, DefaultHint
from pysollib.hint import BlackHoleSolverWrapper
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        AbstractFoundationStack, \
        AutoDealTalonStack, \
        BasicRowStack, \
        DealRowTalonStack, \
        InitialDealTalonStack, \
        OpenStack, \
        RK_FoundationStack, \
        RK_RowStack, \
        ReserveStack, \
        SS_FoundationStack, \
        SS_RowStack, \
        Stack, \
        StackWrapper, \
        TalonStack, \
        UD_RK_RowStack, \
        WasteStack, \
        WasteTalonStack, \
        isSameSuitSequence
from pysollib.util import ACE, ANY_RANK, ANY_SUIT, DIAMOND, KING, NO_RANK, \
        RANKS, SUITS, UNLIMITED_REDEALS


class Golf_Hint(AbstractHint):
    # FIXME: this is very simple

    def computeHints(self):
        game = self.game
        # for each stack
        for r in game.sg.dropstacks:
            # try if we can drop a card to the Waste
            w, ncards = r.canDropCards(game.s.foundations)
            if not w:
                continue
            # this assertion must hold for Golf
            assert ncards == 1
            # clone the Waste (including the card that will be dropped) to
            # form our new foundations
            ww = (self.ClonedStack(w, stackcards=w.cards+[r.cards[-1]]), )
            # now search for a stack that would benefit from this card
            score, color = 10000 + r.id, None
            for t in game.sg.dropstacks:
                if not t.cards:
                    continue
                if t is r:
                    t = self.ClonedStack(r, stackcards=r.cards[:-1])
                if t.canFlipCard():
                    score = score + 100
                elif t.canDropCards(ww)[0]:
                    score = score + 100
            # add hint
            self.addHint(score, ncards, r, w, color)


# ************************************************************************
# *
# ************************************************************************

class Golf_Talon(WasteTalonStack):
    def canDealCards(self):
        if not WasteTalonStack.canDealCards(self):
            return False
        return not self.game.isGameWon()


class Golf_Waste(WasteStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=0, max_accept=1)
        WasteStack.__init__(self, x, y, game, **cap)

    def acceptsCards(self, from_stack, cards):
        if from_stack is self.game.s.talon:
            return True
        if not WasteStack.acceptsCards(self, from_stack, cards):
            return False
        # if there are jokers, they're wild
        if self.cards[-1].suit == 4 or cards[0].suit == 4:
            return True
        # check cards
        r1, r2 = self.cards[-1].rank, cards[0].rank
        if self.game.getStrictness() == 1:
            # nothing on a King
            if r1 == KING:
                return False
        return (r1 + 1) % self.cap.mod == r2 or (r2 + 1) % self.cap.mod == r1

    def getHelp(self):
        return _('Waste. Build up or down regardless of suit.')


class Golf_RowStack(BasicRowStack):
    def clickHandler(self, event):
        return self.doubleclickHandler(event)

    def getHelp(self):
        return _('Tableau. No building.')


# ************************************************************************
# * Golf
# ************************************************************************

class Golf(Game):
    Solver_Class = BlackHoleSolverWrapper(preset='golf', base_rank=0,
                                          queens_on_kings=True)
    Waste_Class = Golf_Waste
    Hint_Class = Golf_Hint

    #
    # game layout
    #

    def createGame(self, columns=7):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        playcards = 5
        w1, w2 = (columns + 1) * layout.XS + layout.XM, 2 * layout.XS

        totalcards = 52 * self.gameinfo.decks
        if w2 + totalcards * layout.XOFFSET > w1:
            layout.XOFFSET = int((w1 - w2) / totalcards)
        self.setSize(w1, layout.YM + 3 * layout.YS +
                     (playcards - 1) * layout.YOFFSET + layout.TEXT_HEIGHT)

        # create stacks
        x, y = layout.XM + layout.XS // 2, layout.YM
        for i in range(columns):
            s.rows.append(Golf_RowStack(x, y, self))
            x = x + layout.XS
        x, y = layout.XM, self.height - layout.YS
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        layout.createText(s.talon, "n")
        x = x + layout.XS
        s.waste = self.Waste_Class(x, y, self)
        s.waste.CARD_XOFFSET = layout.XOFFSET
        layout.createText(s.waste, "n")
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self, num_rows=5):
        self._startDealNumRows(num_rows - 1)
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards:
                return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_RK

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return (self.sg.dropstacks, (), ())
        else:
            # rightclickHandler
            return (self.sg.dropstacks, self.sg.dropstacks, ())


# ************************************************************************
# * Double Golf
# ************************************************************************

class DoubleGolf(Golf):

    def createGame(self):
        Golf.createGame(self, 9)

    def startGame(self):
        Golf.startGame(self, 7)


# ************************************************************************
# * Thieves
# ************************************************************************

class Thieves(Golf):
    pass


# ************************************************************************
# *
# ************************************************************************

class DeadKingGolf(Golf):
    Solver_Class = BlackHoleSolverWrapper(preset='golf', base_rank=0)

    def getStrictness(self):
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if card1.rank == KING:
            return False
        return Golf.shallHighlightMatch(self, stack1, card1, stack2, card2)


class RelaxedGolf(Golf):
    Solver_Class = BlackHoleSolverWrapper(preset='golf', base_rank=0,
                                          wrap_ranks=True)
    Waste_Class = StackWrapper(Golf_Waste, mod=13)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


class DoublePutt(DoubleGolf):
    Solver_Class = BlackHoleSolverWrapper(preset='golf', base_rank=0,
                                          wrap_ranks=True)
    Waste_Class = StackWrapper(Golf_Waste, mod=13)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * Elevator - Relaxed Golf in a Pyramid layout
# ************************************************************************

class Elevator_RowStack(Golf_RowStack):
    STEP = (1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6)

    def basicIsBlocked(self):
        r, step = self.game.s.rows, self.STEP
        i, n, mylen = self.id, 1, len(step)
        while i < mylen:
            i = i + step[i]
            n = n + 1
            for j in range(i, i+n):
                if r[j].cards:
                    return True
        return False


class Elevator(RelaxedGolf):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        self.setSize(9*layout.XS+layout.XM, 4*layout.YS+layout.YM)

        # create stacks
        for i in range(7):
            x = layout.XM + (8-i) * layout.XS // 2
            y = layout.YM + i * layout.YS // 2
            for j in range(i+1):
                s.rows.append(Elevator_RowStack(x, y, self))
                x = x + layout.XS
        x, y = layout.XM, layout.YM
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        layout.createText(s.talon, "s")
        x = x + layout.XS
        s.waste = self.Waste_Class(x, y, self)
        layout.createText(s.waste, "s")
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:21], flip=0)
        self.s.talon.dealRow(rows=self.s.rows[21:])
        self.s.talon.dealCards()          # deal first card to WasteStack


class Escalator(pysollib.game.StartDealRowAndCards, Elevator):
    pass


# ************************************************************************
# * Black Hole
# ************************************************************************

class BlackHole_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards:
            r1, r2 = self.cards[-1].rank, cards[0].rank
            return (r1 + 1) % self.cap.mod == r2 or \
                (r2 + 1) % self.cap.mod == r1
        return True

    def getHelp(self):
        return _('Foundation. Build up or down regardless of suit.')


class BlackHole_RowStack(ReserveStack):
    def clickHandler(self, event):
        return self.doubleclickHandler(event)

    def getHelp(self):
        return _('Tableau. No building.')


class BlackHole(Game):
    RowStack_Class = StackWrapper(
        BlackHole_RowStack, max_accept=0, max_cards=3)
    Hint_Class = Golf_Hint
    Solver_Class = BlackHoleSolverWrapper(preset='black_hole')

    FOUNDATIONS = 1

    #
    # game layout
    #

    def createGame(self, playcards=5):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        w = max((1 + self.FOUNDATIONS) * layout.XS,
                layout.XS + (playcards - 1) * layout.XOFFSET)
        self.setSize(layout.XM + 5 * w, layout.YM + 4 * layout.YS)

        # create stacks
        y = layout.YM
        for i in range(5):
            x = layout.XM + i*w
            s.rows.append(self.RowStack_Class(x, y, self))
        for i in range(2):
            y = y + layout.YS
            for j in (0, 1, 3, 4):
                x = layout.XM + j*w
                s.rows.append(self.RowStack_Class(x, y, self))
        y = y + layout.YS
        for i in range(4):
            x = layout.XM + i*w
            s.rows.append(self.RowStack_Class(x, y, self))
        for r in s.rows:
            r.CARD_XOFFSET = layout.XOFFSET
            r.CARD_YOFFSET = 0
        x, y = layout.XM + 2*w, layout.YM + 3*layout.YS//2
        for f in range(self.FOUNDATIONS):
            s.foundations.append(BlackHole_Foundation(x, y, self,
                                 suit=ANY_SUIT, dir=0, mod=13, max_move=0,
                                 max_cards=52 * self.gameinfo.decks))
            layout.createText(s.foundations[f], "s")
            x += layout.XS
        x, y = layout.XM + 4*w, self.height - layout.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        layout.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move Ace to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(
            cards, lambda c: (c.id == 13, c.suit), 1)

    def startGame(self):
        self._startDealNumRows(2)
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return ((), (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return ((), self.sg.dropstacks, self.sg.dropstacks)


# ************************************************************************
# * Binary Star
# ************************************************************************

class BinaryStar(BlackHole):
    RowStack_Class = StackWrapper(
        ReserveStack, max_accept=0, max_cards=6)
    # TODO: Solver support
    Solver_Class = BlackHoleSolverWrapper(preset='binary_star')
    FOUNDATIONS = 2

    def _shuffleHook(self, cards):
        # move Ace and king to bottom of the Talon
        # (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(
            cards, lambda c: (c.id in (13, 38), c.suit), 2)

    def startGame(self):
        self._startDealNumRows(5)
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)


# ************************************************************************
# * Four Leaf Clovers
# ************************************************************************

class FourLeafClovers_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards:
            r1, r2 = self.cards[-1].rank, cards[0].rank
            return (r1 + 1) % self.cap.mod == r2
        return True

    def getHelp(self):
        return _('Foundation. Build up regardless of suit.')


class FourLeafClovers(Game):

    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        h = layout.YS + 6*layout.YOFFSET
        self.setSize(layout.XM + 7*layout.XS, layout.YM + 2*h)

        # create stacks
        y = layout.YM
        for i in range(7):
            x = layout.XM + i*layout.XS
            s.rows.append(
                UD_RK_RowStack(x, y, self, mod=13, base_rank=NO_RANK))
        y = layout.YM+h
        for i in range(6):
            x = layout.XM + i*layout.XS
            s.rows.append(
                UD_RK_RowStack(x, y, self, mod=13, base_rank=NO_RANK))
        stack = FourLeafClovers_Foundation(
            layout.XM+6*layout.XS, self.height-layout.YS, self,
            suit=ANY_SUIT, dir=0, mod=13,
            max_move=0, max_cards=52)
        s.foundations.append(stack)
        layout.createText(stack, 'n')
        x, y = layout.XM + 7*layout.XS, self.height - layout.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self._startDealNumRowsAndDealSingleRow(3)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * All in a Row
# ************************************************************************

class AllInARow(BlackHole):

    Solver_Class = BlackHoleSolverWrapper(preset='all_in_a_row')

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        h = layout.YM+layout.YS+4*layout.YOFFSET
        self.setSize(layout.XM+7*layout.XS, 3*layout.YM+2*h+layout.YS)

        # create stacks
        x, y = layout.XM, layout.YM
        for i in range(7):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += layout.XS
        x, y = layout.XM, layout.YM+h
        for i in range(6):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += layout.XS
        for r in s.rows:
            r.CARD_XOFFSET, r.CARD_YOFFSET = 0, layout.YOFFSET

        x, y = layout.XM, self.height-layout.YS
        stack = BlackHole_Foundation(
            x, y, self, ANY_SUIT, dir=0, mod=13, max_move=0, max_cards=52,
            base_rank=ANY_RANK)
        s.foundations.append(stack)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = (self.width-layout.XS)//51, 0
        layout.createText(stack, 'n')
        x = self.width-layout.XS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self._startDealNumRowsAndDealSingleRow(3)


# ************************************************************************
# * All in a Row II
# ************************************************************************

class AllInARowII_RowStack(BlackHole_RowStack):
    def clickHandler(self, event):
        return self.rightclickHandler(event)


class AllInARowII_Reserve(RK_RowStack):
    getBottomImage = RK_RowStack._getReserveBottomImage

    def getHelp(self):
        return _('Reserve. Build up regardless of suit.')


class AllInARowII_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if from_stack not in self.game.s.reserves:
            return False
        if len(cards) == 1 or len(cards) != len(from_stack.cards):
            return False
        return True


class AllInARowII(Game):

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        h = layout.YM+layout.YS + 4 * layout.YOFFSET
        self.setSize(layout.XM + 7 * layout.XS,
                     3 * layout.YM + 3 * h + layout.YS)

        # create stacks
        x, y = layout.XM, layout.YM
        for i in range(7):
            s.rows.append(AllInARowII_RowStack(x, y, self, max_accept=0))
            x += layout.XS
        x, y = layout.XM, layout.YM+h
        for i in range(6):
            s.rows.append(AllInARowII_RowStack(x, y, self, max_accept=0))
            x += layout.XS
        for r in s.rows:
            r.CARD_XOFFSET, r.CARD_YOFFSET = 0, layout.YOFFSET

        x, y = layout.XM, self.height-layout.YS
        stack = AllInARowII_Foundation(
            x, y, self, ANY_SUIT, dir=0, mod=13, max_move=0, max_cards=52,
            base_rank=ANY_RANK)
        s.foundations.append(stack)
        layout.createText(stack, 'se')

        y -= layout.YS
        stack = AllInARowII_Reserve(
            x, y, self, dir=1, mod=13, max_cards=52, base_rank=ANY_RANK)
        s.reserves.append(stack)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = ((self.width - layout.XS)
                                                  // 51, 0)
        x = self.width-layout.XS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self._startDealNumRowsAndDealSingleRow(3)

    def getStuck(self):
        if len(self.s.reserves[0].cards) > 1:
            return True
        return Game.getStuck(self)


# ************************************************************************
# * Robert
# * Bobby
# * Wasatch
# ************************************************************************

class Robert(Game):
    Foundation_Stack = BlackHole_Foundation

    def createGame(self, max_rounds=3, num_deal=1, num_foundations=1):
        layout, s = Layout(self), self.s
        self.setSize(layout.XM + max(4, num_foundations) * layout.XS,
                     layout.YM + layout.TEXT_HEIGHT + 2 * layout.YS)
        x, y = layout.XM, layout.YM
        if num_foundations == 1:
            x += 3 * layout.XS // 2
        elif num_foundations == 2:
            x += layout.XS
        for f in range(num_foundations):
            stack = self.Foundation_Stack(x, y, self, ANY_SUIT,
                                          dir=0, mod=13, max_move=0,
                                          max_cards=52,
                                          base_rank=ANY_RANK)
            s.foundations.append(stack)
            layout.createText(stack, 's')
            x += layout.XS

        x, y = layout.XM + (layout.XS * max((num_foundations // 2) - 1, 1)), \
            layout.YM + layout.YS + layout.TEXT_HEIGHT
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        layout.createText(s.talon, 'nw')
        if max_rounds > 0:
            layout.createRoundText(self.s.talon, 'se', dx=layout.XS)
        x += layout.XS
        s.waste = WasteStack(x, y, self)
        layout.createText(s.waste, 'ne')

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()


class Bobby(Robert):

    def createGame(self):
        Robert.createGame(self, num_foundations=2)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations[:1])
        self.s.talon.dealCards()


class Wasatch(Robert):

    def createGame(self):
        Robert.createGame(self, max_rounds=UNLIMITED_REDEALS, num_deal=3)


# ************************************************************************
# * Uintah
# * Double Uintah
# ************************************************************************

class Uintah_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if (self.cards[-1].color != cards[0].color):
            return False
        # check the rank
        if self.cards:
            r1, r2 = self.cards[-1].rank, cards[0].rank
            return (r1 + 1) % self.cap.mod == r2 or \
                (r2 + 1) % self.cap.mod == r1
        return True

    def getHelp(self):
        return _('Foundation. Build up or down by same color.')


class Uintah(Robert):
    Foundation_Stack = Uintah_Foundation

    def createGame(self):
        Robert.createGame(self, max_rounds=UNLIMITED_REDEALS, num_deal=3,
                          num_foundations=4)

    def _shuffleHook(self, cards):
        suits = []
        top_cards = []
        for c in cards[:]:
            if c.suit not in suits:
                suits.append(c.suit)
                top_cards.append(c)
                cards.remove(c)
            if len(suits) == 4:
                break
        top_cards.sort(key=lambda x: -x.suit)  # sort by suit
        return cards + top_cards


class DoubleUintah(Uintah):
    Foundation_Stack = Uintah_Foundation

    def createGame(self):
        Robert.createGame(self, max_rounds=UNLIMITED_REDEALS, num_deal=3,
                          num_foundations=8)

    def _shuffleHook(self, cards):
        top_cards = []
        for s in range(2):
            suits = []
            for c in cards[:]:
                if c.suit not in suits:
                    suits.append(c.suit)
                    top_cards.append(c)
                    cards.remove(c)
                if len(suits) == 4:
                    break
        top_cards.sort(key=lambda x: -x.suit)  # sort by suit
        return cards + top_cards


# ************************************************************************
# * Diamond Mine
# ************************************************************************

class DiamondMine_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if cards[0].suit == DIAMOND:
            return False
        if self.cards:
            return self.cards[-1].suit != DIAMOND
        return True


class DiamondMine(Game):

    def createGame(self):
        layout, s = Layout(self), self.s
        self.setSize(
            layout.XM+13*layout.XS,
            layout.YM+2*layout.YS+15*layout.YOFFSET)

        x, y = layout.XM+6*layout.XS, layout.YM
        s.foundations.append(SS_FoundationStack(x, y, self,
                             base_rank=ANY_RANK, suit=DIAMOND, mod=13))
        x, y = layout.XM, layout.YM+layout.YS
        for i in range(13):
            s.rows.append(DiamondMine_RowStack(x, y, self))
            x += layout.XS
        s.talon = InitialDealTalonStack(layout.XM, self.height-layout.YS, self)

        layout.defaultAll()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        self._startAndDealRow()

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != 13:
            return False
        for s in self.s.rows:
            if len(s.cards) == 0:
                continue
            if len(s.cards) != 13:
                return False
            if not isSameSuitSequence(s.cards):
                return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Dolphin
# ************************************************************************

class Dolphin(Game):

    def createGame(self, rows=8, reserves=4, playcards=6):
        layout, s = Layout(self), self.s
        self.setSize(
            layout.XM+rows*layout.XS,
            layout.YM+3*layout.YS+playcards*layout.YOFFSET)

        dx = (self.width-layout.XM-(reserves+1)*layout.XS)//3
        x, y = layout.XM+dx, layout.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x += layout.XS
        x += dx
        max_cards = 52 * self.gameinfo.decks
        s.foundations.append(RK_FoundationStack(x, y, self,
                             base_rank=ANY_RANK, mod=13, max_cards=max_cards))
        layout.createText(s.foundations[0], 'ne')
        x, y = layout.XM, layout.YM+layout.YS
        for i in range(rows):
            s.rows.append(BasicRowStack(x, y, self))
            x += layout.XS
        s.talon = InitialDealTalonStack(layout.XM, self.height-layout.YS, self)

        layout.defaultAll()

    def startGame(self):
        self._startDealNumRows(5)
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


class DoubleDolphin(Dolphin):

    def createGame(self):
        Dolphin.createGame(self, rows=10, reserves=5, playcards=10)

    def startGame(self):
        self._startDealNumRows(9)
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


# ************************************************************************
# * Waterfall
# ************************************************************************

class Waterfall_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        c1 = cards[0]
        if not self.cards:
            return c1.rank == ACE and c1.suit == 0
        c2 = self.cards[-1]
        if c2.rank == KING:
            suit = (c2.suit+1) % 4
            rank = ACE
        else:
            suit = c2.suit
            rank = c2.rank+1
        return c1.suit == suit and c1.rank == rank


class Waterfall(Game):

    def createGame(self):
        rows = 8
        layout, s = Layout(self), self.s
        self.setSize(layout.XM + rows * layout.XS,
                     layout.YM + 2 * layout.YS + 30 * layout.YOFFSET)

        x, y = layout.XM, layout.YM
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self))
            x += layout.XS
        x, y = layout.XM+(rows-1)*layout.XS//2, self.height-layout.YS
        s.foundations.append(Waterfall_Foundation(x, y, self, suit=ANY_SUIT,
                                                  max_cards=104))
        stack = s.foundations[0]
        tx, ty, ta, tf = layout.getTextAttr(stack, 'se')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)
        x, y = self.width-layout.XS, self.height-layout.YS
        s.talon = DealRowTalonStack(x, y, self)
        layout.createText(s.talon, 'sw')

        layout.defaultStackGroups()

    def startGame(self):
        self._startDealNumRowsAndDealSingleRow(3)

    def updateText(self):
        if self.preview > 1:
            return
        f = self.s.foundations[0]
        if len(f.cards) == 104:
            t = ''
        elif len(f.cards) == 0:
            t = SUITS[0]
        else:
            c = f.cards[-1]
            if c.rank == KING:
                suit = (c.suit+1) % 4
            else:
                suit = c.suit
            t = SUITS[suit]
        f.texts.misc.config(text=t)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Vague
# * Thirty-Two Cards
# ************************************************************************

class Vague_RowStack(BasicRowStack):
    clickHandler = BasicRowStack.doubleclickHandler


class Vague(Game):
    Foundation_Classes = [StackWrapper(SS_FoundationStack,
                                       base_rank=ANY_RANK, mod=13)]

    SEPARATE_FOUNDATIONS = True
    SPREAD_FOUNDATION = False

    def createGame(self, rows=3, columns=6):
        layout, s = Layout(self), self.s
        decks = self.gameinfo.decks
        maxrows = max(columns, 2+decks*4)
        self.setSize(layout.XM+maxrows*layout.XS, layout.YM+(rows+1)*layout.YS)

        x, y = layout.XM, layout.YM
        s.talon = AutoDealTalonStack(x, y, self)
        layout.createText(s.talon, 'ne')

        x, y = layout.XM+2*layout.XS, layout.YM
        for found in self.Foundation_Classes:
            if self.SEPARATE_FOUNDATIONS:
                for i in range(4):
                    s.foundations.append(found(x, y, self, suit=i))
                    x += layout.XS
            else:
                s.foundations.append(found(x, y, self, suit=ANY_SUIT))
                if self.SPREAD_FOUNDATION:
                    w1, w2 = 6 * layout.XS + layout.XM, 2 * layout.XS

                    totalcards = self.gameinfo.ncards
                    if w2 + totalcards * layout.XOFFSET > w1:
                        layout.XOFFSET = int((w1 - w2) / totalcards)
                    s.foundations[0].CARD_XOFFSET = layout.XOFFSET

        y = layout.YM+layout.YS
        for i in range(rows):
            x = layout.XM + (maxrows-columns)*layout.XS//2
            for j in range(columns):
                s.rows.append(Vague_RowStack(x, y, self))
                x += layout.XS
            y += layout.YS

        layout.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.flipMove()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                if not self.s.talon.cards[-1].face_up:
                    self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return ((), (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return ((), self.sg.dropstacks, self.sg.dropstacks)


class ThirtyTwoCards(Vague):
    Foundation_Classes = [
        SS_FoundationStack,
        StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1)]

    def createGame(self):
        Vague.createGame(self, rows=4, columns=8)

    def startGame(self):
        self._startAndDealRow()


# ************************************************************************
# * Sticko
# ************************************************************************

class Sticko_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        r1, r2 = self.cards[-1].rank, cards[0].rank
        s1, s2 = self.cards[-1].suit, cards[0].suit
        c1, c2 = self.cards[-1].color, cards[0].color

        # Increase rank, same suit
        if ((r2 == r1 + 1 or (r2 == ACE and r1 == KING)
             or (r2 == 6 and r1 == ACE)) and s1 == s2):
            return True

        # Decrease rank, different suit but same color
        if ((r1 == r2 + 1 or (r1 == ACE and r2 == KING)
             or (r1 == 6 and r2 == ACE)) and s1 != s2 and c1 == c2):
            return True

        # Same rank, different color
        if r1 == r2 and c1 != c2:
            return True

        return False


class Sticko(Vague):
    Foundation_Classes = [StackWrapper(Sticko_Foundation,
                                       max_cards=32, )]
    SEPARATE_FOUNDATIONS = False
    SPREAD_FOUNDATION = True

    def createGame(self):
        Vague.createGame(self, rows=2, columns=8)

    def startGame(self):
        self._startAndDealRow()
        self.s.talon.flipMove()
        self.s.talon.moveMove(1, self.s.foundations[0])


# ************************************************************************
# * Devil's Solitaire
# ************************************************************************

class DevilsSolitaire_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards:
            return True
        if self.game.s.reserves[0].cards:
            c = self.game.s.reserves[0].cards[-1]
            return (c.rank+1) % 13 == cards[-1].rank
        return True


class DevilsSolitaire_WasteStack(WasteStack):
    clickHandler = WasteStack.doubleclickHandler


class DevilsSolitaire(Game):

    def createGame(self):
        layout, s = Layout(self), self.s
        self.setSize(
            layout.XM+9*layout.XS,
            layout.YM+3*layout.YS+7*layout.YOFFSET+2*layout.TEXT_HEIGHT)

        x, y = layout.XM+4*layout.XS, layout.YM
        stack = DevilsSolitaire_Foundation(
            x, y, self, suit=ANY_SUIT, base_rank=ANY_RANK, mod=13)
        tx, ty, ta, tf = layout.getTextAttr(stack, 'nw')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)
        s.foundations.append(stack)

        x, y = self.width-layout.XS, layout.YM
        stack = AbstractFoundationStack(
            x, y, self,
            suit=ANY_SUIT, max_move=0, max_cards=104,
            max_accept=0, base_rank=ANY_RANK)
        layout.createText(stack, 'nw')
        s.foundations.append(stack)

        x, y = layout.XM, layout.YM+layout.YS
        for i in range(4):
            s.rows.append(Vague_RowStack(x, y, self))
            x += layout.XS
        x += layout.XS
        for i in range(4):
            s.rows.append(Vague_RowStack(x, y, self))
            x += layout.XS

        x, y = layout.XM+4*layout.XS, layout.YM+layout.YS
        stack = OpenStack(x, y, self)
        stack.CARD_YOFFSET = layout.YOFFSET
        s.reserves.append(stack)

        x, y = layout.XM+4.5*layout.XS, self.height-layout.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        layout.createText(s.talon, 'se')
        layout.createRoundText(s.talon, 'n')
        x -= layout.XS
        s.waste = DevilsSolitaire_WasteStack(x, y, self)
        layout.createText(s.waste, 'sw')

        layout.defaultStackGroups()

    def startGame(self):
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)
        if stack in self.s.rows and not stack.cards:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
        f0 = self.s.foundations[0]
        if len(f0.cards) == 12:
            self.moveMove(1, self.s.reserves[0], f0, frames=4)
            f1 = self.s.foundations[1]
            for i in range(13):
                self.moveMove(1, f0, f1, frames=4)
        self.leaveState(old_state)

    def updateText(self):
        if self.preview > 1:
            return
        f = self.s.foundations[0]
        r = self.s.reserves[0]
        if not r.cards:
            t = ''
        else:
            c = r.cards[-1]
            t = RANKS[(c.rank+1) % 13]
        f.texts.misc.config(text=t)


# ************************************************************************
# * Three Fir-trees
# ************************************************************************

class ThreeFirTrees_RowStack(Golf_RowStack):
    def __init__(self, x, y, game):
        Golf_RowStack.__init__(self, x, y, game, max_accept=0, max_cards=1)
        self.CARD_YOFFSET = 0
        self.blockmap = []

    def basicIsBlocked(self):
        for r in self.blockmap:
            if r.cards:
                return True
        return False

    getBottomImage = Stack._getNoneBottomImage


class FirTree_GameMethods:
    def _createFirTree(self, layout, x0, y0):
        rows = []
        # create stacks
        for i in range(11):
            x = x0 + ((i+1) % 2) * layout.XS // 2
            y = y0 + i * layout.YS // 4
            for j in range((i % 2) + 1):
                rows.append(ThreeFirTrees_RowStack(x, y, self))
                x += layout.XS
        # compute blocking
        n = 0
        for i in range(10):
            if i % 2:
                rows[n].blockmap = [rows[n+2]]
                rows[n+1].blockmap = [rows[n+2]]
                n += 2
            else:
                rows[n].blockmap = [rows[n+1], rows[n+2]]
                n += 1
        return rows


class ThreeFirTrees(Golf, FirTree_GameMethods):
    Hint_Class = CautiousDefaultHint
    Waste_Class = Golf_Waste

    def createGame(self):

        layout, s = Layout(self), self.s
        self.setSize(
            layout.XM+max(7*layout.XS, 2*layout.XS+26*layout.XOFFSET),
            layout.YM+5*layout.YS)

        x0, y0 = (self.width-7*layout.XS)//2, layout.YM
        for i in range(3):
            s.rows += self._createFirTree(layout, x0, y0)
            x0 += 2.5*layout.XS

        x, y = layout.XM, self.height - layout.YS
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        layout.createText(s.talon, 'n')
        x += layout.XS
        s.waste = self.Waste_Class(x, y, self)
        s.waste.CARD_XOFFSET = layout.XOFFSET//4
        layout.createText(s.waste, 'n')
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()


class RelaxedThreeFirTrees(ThreeFirTrees):
    Waste_Class = StackWrapper(Golf_Waste, mod=13)


# ************************************************************************
# * Napoleon Takes Moscow
# * Napoleon Leaves Moscow
# ************************************************************************

class NapoleonTakesMoscow(Game, FirTree_GameMethods):
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=KING, max_move=1)
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        layout, s = Layout(self), self.s
        self.setSize(layout.XM + 10 * layout.XS,
                     layout.YM + 3 * layout.YS + 15 * layout.YOFFSET +
                     layout.TEXT_HEIGHT)

        x, y = layout.XM+layout.XS, layout.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i//2))
            x += layout.XS

        x, y = layout.XM, layout.YM+layout.YS
        for i in range(2):
            for j in range(4):
                s.rows.append(self.RowStack_Class(x, y, self))
                x += layout.XS
            x += 2*layout.XS

        x, y = layout.XM+4*layout.XS, layout.YM+layout.YS
        s.reserves += self._createFirTree(layout, x, y)

        x, y = layout.XM, self.height - layout.YS - layout.TEXT_HEIGHT
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        layout.createText(s.talon, 's')
        layout.createRoundText(s.talon, 'n')
        x += layout.XS
        s.waste = WasteStack(x, y, self)
        layout.createText(s.waste, 's')

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self._startDealNumRowsAndDealRowAndCards(3)

    shallHighlightMatch = Game._shallHighlightMatch_SS


class NapoleonLeavesMoscow(NapoleonTakesMoscow):
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=KING)
    Hint_Class = DefaultHint

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self._startDealNumRowsAndDealRowAndCards(4)


# ************************************************************************
# * Carcassonne
# ************************************************************************

class Carcassonne(Game, FirTree_GameMethods):

    def createGame(self):

        layout, s = Layout(self), self.s
        self.setSize(layout.XM + 10 * layout.XS,
                     layout.YM + 3 * layout.YS + 15 * layout.YOFFSET +
                     layout.TEXT_HEIGHT)

        x, y = layout.XM+layout.XS, layout.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += layout.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    dir=-1))
            x += layout.XS

        x, y = layout.XM, layout.YM+layout.YS
        for i in range(2):
            for j in range(4):
                s.rows.append(UD_RK_RowStack(x, y, self, base_rank=NO_RANK))
                x += layout.XS
            x += 2*layout.XS

        x, y = layout.XM+4*layout.XS, layout.YM+layout.YS
        s.reserves += self._createFirTree(layout, x, y)

        x, y = layout.XM, self.height - layout.YS - layout.TEXT_HEIGHT
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        layout.defaultStackGroups()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(
            cards,
            lambda c: (c.rank in (ACE, KING), (c.deck, c.rank, c.suit)))

    def _fillOne(self):
        for r in self.s.rows:
            if r.cards:
                c = r.cards[-1]
                for f in self.s.foundations:
                    if f.acceptsCards(r, [c]):
                        self.moveMove(1, r, f, frames=3, shadow=0)
                        return 1
        return 0

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self._startDealNumRows(1)
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(9):
            self.s.talon.dealRow(frames=3)
            while True:
                if not self._fillOne():
                    break
        self.s.talon.dealCards()

# ************************************************************************
# * Flake
# * Flake (2 Decks)
# ************************************************************************


class Flake(Game):
    Hint_Class = FourByFour_Hint  # CautiousDefaultHint

    def createGame(self, rows=6, playcards=18):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        self.setSize(
            layout.XM + rows * layout.XS,
            layout.YM + 2 * layout.YS + playcards * layout.XOFFSET)

        # create stacks
        x, y, = layout.XM, layout.YM+layout.YS
        for i in range(rows):
            s.rows.append(UD_RK_RowStack(x, y, self, mod=13))
            x += layout.XS

        x, y = layout.XM + (rows - 1) * layout.XS // 2, layout.YM
        stack = BlackHole_Foundation(x, y, self, max_move=0, suit=ANY_SUIT,
                                     base_rank=ANY_RANK, dir=0, mod=13,
                                     max_cards=52 * self.gameinfo.decks)
        s.foundations.append(stack)
        layout.createText(stack, 'ne')

        x, y = layout.XM, layout.YM
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self._startDealNumRows(7)
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    shallHighlightMatch = Game._shallHighlightMatch_RKW


class Flake2Decks(Flake):
    def createGame(self):
        Flake.createGame(self, rows=8, playcards=22)

    def startGame(self):
        self._startDealNumRowsAndDealSingleRow(12)


# ************************************************************************
# * Beacon
# ************************************************************************

class Beacon(Game):

    def createGame(self, rows=8):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        playcards = 12
        self.setSize(
            layout.XM+rows*layout.XS,
            layout.YM + 3 * layout.YS + playcards * layout.YOFFSET)

        # create stacks
        x, y = layout.XM + (rows - 1) * layout.XS // 2, layout.YM
        stack = RK_FoundationStack(x, y, self, base_rank=ANY_RANK,
                                   max_cards=52, mod=13)
        s.foundations.append(stack)
        layout.createText(stack, 'ne')

        x, y = layout.XM, layout.YM+layout.YS
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self, base_rank=NO_RANK, mod=13))
            x += layout.XS

        x, y = layout.XM, self.height-layout.YS
        s.talon = TalonStack(x, y, self)
        layout.createText(s.talon, 'se')

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self._startDealNumRowsAndDealSingleRow(3)

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# register the game
registerGame(GameInfo(36, Golf, "Golf",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED,
                      altnames=("One Foundation",)))
registerGame(GameInfo(259, DeadKingGolf, "Dead King Golf",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(260, RelaxedGolf, "Relaxed Golf",
                      GI.GT_GOLF | GI.GT_RELAXED, 1, 0, GI.SL_BALANCED,
                      altnames=("Putt Putt",)))
registerGame(GameInfo(40, Elevator, "Elevator",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED,
                      altnames=("Egyptian Solitaire", "Pyramid Golf")))
registerGame(GameInfo(98, BlackHole, "Black Hole",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(267, FourLeafClovers, "Four Leaf Clovers",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(281, Escalator, "Escalator",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(405, AllInARow, "All in a Row",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Quasar",)))
registerGame(GameInfo(432, Robert, "Robert",
                      GI.GT_GOLF, 1, 2, GI.SL_LUCK))
registerGame(GameInfo(551, DiamondMine, "Diamond Mine",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(661, Dolphin, "Dolphin",
                      GI.GT_GOLF | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(662, DoubleDolphin, "Double Dolphin",
                      GI.GT_GOLF | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(709, Waterfall, "Waterfall",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(720, Vague, "Vague",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(723, DevilsSolitaire, "Devil's Solitaire",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED,
                      altnames=('Banner',)))
registerGame(GameInfo(728, ThirtyTwoCards, "Thirty-Two Cards",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_LUCK))
registerGame(GameInfo(731, ThreeFirTrees, "Three Fir-trees",
                      GI.GT_GOLF, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(733, NapoleonTakesMoscow, "Napoleon Takes Moscow",
                      GI.GT_NAPOLEON, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(734, NapoleonLeavesMoscow, "Napoleon Leaves Moscow",
                      GI.GT_NAPOLEON, 2, 2, GI.SL_BALANCED,
                      altnames=("Napoleon at Friedland",)))
registerGame(GameInfo(749, Flake, "Flake",
                      GI.GT_GOLF | GI.GT_OPEN | GI.GT_ORIGINAL,
                      1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(750, Flake2Decks, "Flake (2 Decks)",
                      GI.GT_GOLF | GI.GT_OPEN | GI.GT_ORIGINAL,
                      2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(763, Wasatch, "Wasatch",
                      GI.GT_GOLF, 1, UNLIMITED_REDEALS,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(764, Beacon, "Beacon",
                      GI.GT_1DECK_TYPE | GI.GT_ORIGINAL, 1, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(768, RelaxedThreeFirTrees, "Relaxed Three Fir-trees",
                      GI.GT_GOLF | GI.GT_RELAXED, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(777, DoubleGolf, "Double Golf",
                      GI.GT_GOLF, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(783, Uintah, "Uintah",
                      GI.GT_GOLF, 1, UNLIMITED_REDEALS,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(812, Sticko, "Sticko",
                      GI.GT_1DECK_TYPE | GI.GT_STRIPPED, 1, 0, GI.SL_BALANCED,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12)))
registerGame(GameInfo(868, Bobby, "Bobby",
                      GI.GT_GOLF, 1, 2, GI.SL_LUCK))
registerGame(GameInfo(880, Carcassonne, "Carcassonne",
                      GI.GT_NAPOLEON | GI.GT_OPEN, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(891, AllInARowII, "All in a Row II",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(892, DoublePutt, "Double Putt",
                      GI.GT_GOLF, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(906, Thieves, "Thieves",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED,
                      subcategory=GI.GS_JOKER_DECK, trumps=list(range(2))))
registerGame(GameInfo(941, BinaryStar, "Binary Star",
                      GI.GT_GOLF | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Black Holes",)))
registerGame(GameInfo(959, DoubleUintah, "Double Uintah",
                      GI.GT_GOLF, 2, UNLIMITED_REDEALS,
                      GI.SL_MOSTLY_LUCK))
