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

import math

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.hint import DefaultHint
from pysollib.layout import Layout
from pysollib.stack import \
        AbstractFoundationStack, \
        AutoDealTalonStack, \
        BasicRowStack, \
        DealRowRedealTalonStack, \
        InitialDealTalonStack, \
        OpenStack, \
        ReserveStack, \
        SS_FoundationStack, \
        StackWrapper, \
        TalonStack
from pysollib.util import ANY_RANK, ANY_SUIT, JACK, KING, NO_RANK, \
    QUEEN, UNLIMITED_REDEALS

# ************************************************************************
# *
# ************************************************************************


class MonteCarlo_Hint(DefaultHint):
    # FIXME: demo is not too clever in this game
    pass


# ************************************************************************
# * Monte Carlo
# * Monte Carlo (2 Decks)
# ************************************************************************

class MonteCarlo_Talon(TalonStack):
    def canDealCards(self):
        free = 0
        for r in self.game.s.rows:
            if not r.cards:
                free = 1
            elif free:
                return True
        return free and len(self.cards)

    def dealCards(self, sound=False):
        self.game.updateStackMove(self.game.s.talon, 2 | 16)  # for undo
        n = self.game.fillEmptyStacks()
        self.game.updateStackMove(self.game.s.talon, 1 | 16)  # for redo
        return n


class MonteCarlo_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards[-1].rank != cards[0].rank:
            return False
        # now look if the stacks are neighbours
        return self.game.isNeighbour(from_stack, self)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1 and to_stack in self.game.s.rows
        if to_stack.cards:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            BasicRowStack.moveMove(
                self, ncards, to_stack, frames=frames, shadow=shadow)

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2 | 16)            # for undo
        if not game.demo:
            game.playSample("droppair", priority=200)
        game.moveMove(n, self, f, frames=frames, shadow=shadow)
        game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.fillStack()
        other_stack.fillStack()
        if self.game.FILL_STACKS_AFTER_DROP:
            game.fillEmptyStacks()
        game.updateStackMove(game.s.talon, 1 | 16)            # for redo
        game.leaveState(old_state)


class MonteCarlo(Game):
    Talon_Class = MonteCarlo_Talon
    Foundation_Class = StackWrapper(
        AbstractFoundationStack, max_accept=0)
    RowStack_Class = MonteCarlo_RowStack
    Hint_Class = MonteCarlo_Hint

    FILL_STACKS_AFTER_DROP = False
    FILL_STACKS_BEFORE_SHIFT = False

    #
    # game layout
    #

    def createGame(self, rows=5, cols=5):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (cols+1.5)*l.XS, l.YM + rows*l.YS)

        # create stacks
        for i in range(rows):
            for j in range(cols):
                x, y = l.XM + j*l.XS, l.YM + i*l.YS
                s.rows.append(self.RowStack_Class(x, y, self,
                                                  max_accept=1, max_cards=2,
                                                  dir=0, base_rank=NO_RANK))
        x, y = self.width - l.XS, l.YM
        s.foundations.append(self.Foundation_Class(x, y, self, suit=ANY_SUIT,
                             max_move=0, base_rank=ANY_RANK,
                             max_cards=self.gameinfo.ncards))
        l.createText(s.foundations[0], "s")
        y += 2*l.YS
        s.talon = self.Talon_Class(x, y, self, max_rounds=1)
        l.createText(s.talon, "s", text_format="%D")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self._startAndDealRow()

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank

    #
    # game extras
    #

    def isNeighbour(self, stack1, stack2):
        if not (0 <= stack1.id <= 24 and 0 <= stack2.id <= 24):
            return False
        column = stack2.id % 5
        diff = stack1.id - stack2.id
        if column == 0:
            return diff in (-5, -4, 1, 5, 6)
        elif column == 4:
            return diff in (-6, -5, -1, 4, 5)
        else:
            return diff in (-6, -5, -4, -1, 1, 4, 5, 6)

    def fillEmptyStacks(self):
        n = 0
        self.startDealSample()
        free = self.shiftCards()
        remcards = free > len(self.s.talon.cards) > 0
        if free > 0:
            for r in self.s.rows:
                if not r.cards:
                    if not self.s.talon.cards:
                        break
                    self.flipMove(self.s.talon)
                    self.moveMove(1, self.s.talon, r)
                    n += 1
        if remcards and self.FILL_STACKS_BEFORE_SHIFT:
            self.shiftCards()
        self.stopSamples()
        return n + free

    def shiftCards(self):
        free = 0
        for r in self.s.rows:
            assert len(r.cards) <= 1
            if not r.cards:
                free += 1
            elif free > 0 and (not self.FILL_STACKS_BEFORE_SHIFT
                               or not self.s.talon.cards):
                to_stack = self.allstacks[r.id - free]
                self.moveMove(1, r, to_stack, frames=4, shadow=0)
        return free


class MonteCarlo2Decks(MonteCarlo):
    pass


# ************************************************************************
# * Weddings
# ************************************************************************

class Weddings_Talon(MonteCarlo_Talon):
    def canDealCards(self):
        free = 0
        for r in self.game.s.rows:
            if not r.cards:
                free = 1
            else:
                k = r.id
                while k >= 5 and not self.game.allstacks[k - 5].cards:
                    k = k - 5
                if k != r.id:
                    return True
        return free and len(self.cards)


class Weddings(MonteCarlo):
    Talon_Class = Weddings_Talon

    def fillEmptyStacks(self):
        free, n = 0, 0
        self.startDealSample()
        for r in self.s.rows:
            assert len(r.cards) <= 1
            if not r.cards:
                free = free + 1
            else:
                k = r.id
                while k >= 5 and not self.allstacks[k - 5].cards:
                    k = k - 5
                if k != r.id:
                    to_stack = self.allstacks[k]
                    self.moveMove(1, r, to_stack, frames=4, shadow=0)
        if free > 0:
            for r in self.s.rows:
                if not r.cards:
                    if not self.s.talon.cards:
                        break
                    self.flipMove(self.s.talon)
                    self.moveMove(1, self.s.talon, r)
                    n = n + 1
        self.stopSamples()
        return n


# ************************************************************************
# * Simple Carlo (Monte Carlo for Children, stacks do not
# * have to be neighbours)
# ************************************************************************

class SimpleCarlo(MonteCarlo):
    FILL_STACKS_AFTER_DROP = True

    def getAutoStacks(self, event=None):
        return ((), (), ())

    def isNeighbour(self, stack1, stack2):
        return 0 <= stack1.id <= 24 and 0 <= stack2.id <= 24


# ************************************************************************
# * Quatorze
# ************************************************************************

class Quatorze_RowStack(MonteCarlo_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards[-1].rank + cards[0].rank != 12:
            return False
        # now look if the stacks are neighbours
        return self.game.isNeighbour(from_stack, self)


class Quatorze(MonteCarlo):
    RowStack_Class = Quatorze_RowStack
    FILL_STACKS_AFTER_DROP = True
    FILL_STACKS_BEFORE_SHIFT = True

    def isNeighbour(self, stack1, stack2):
        return (stack1.id // 5 == stack2.id // 5 or
                stack1.id % 5 == stack2.id % 5)


# ************************************************************************
# * Simple Pairs
# ************************************************************************

class SimplePairs(MonteCarlo):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 6*l.XS, l.YM + 4*l.YS)

        # create stacks
        for i in range(3):
            for j in range(3):
                x, y = l.XM + (2*j+3)*l.XS//2, l.YM + (2*i+1)*l.YS//2
                s.rows.append(self.RowStack_Class(x, y, self,
                                                  max_accept=1, max_cards=2,
                                                  dir=0, base_rank=NO_RANK))
        x, y = l.XM, l.YM + 3*l.YS//2
        s.talon = AutoDealTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + 5*l.XS
        s.foundations.append(self.Foundation_Class(x, y, self, suit=ANY_SUIT,
                             max_move=0, max_cards=52, base_rank=ANY_RANK))
        l.createText(s.foundations[0], "s")

        # define stack-groups
        l.defaultStackGroups()

    def fillStack(self, stack):
        if stack in self.s.rows:
            if len(stack.cards) == 0 and len(self.s.talon.cards) > 0:
                self.flipMove(self.s.talon)
                self.moveMove(1, self.s.talon, stack)

    def isNeighbour(self, stack1, stack2):
        return 0 <= stack1.id <= 15 and 0 <= stack2.id <= 15


# ************************************************************************
# * Block Ten
# * Simple Tens
# ************************************************************************

class BlockTen_RowStack(MonteCarlo_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards[-1].rank + cards[0].rank + 2 == 10:
            return True
        if self.cards[-1].rank > 9 and self.cards[-1].rank == cards[0].rank:
            return True

        return False


class BlockTen(SimplePairs):
    RowStack_Class = BlockTen_RowStack

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 48


class SimpleTens(BlockTen):
    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 36


# ************************************************************************
# * Crispy
# ************************************************************************

class Crispy_Talon(MonteCarlo_Talon):

    def canDealCards(self):
        if len(self.cards) == 0:
            return False
        return MonteCarlo_Talon.canDealCards(self)


class Crispy_RowStack(MonteCarlo_RowStack):

    getBottomImage = BasicRowStack._getReserveBottomImage

    def acceptsCards(self, from_stack, cards):
        cr = cards[0].rank
        if len(self.cards) == 0:
            if cr == KING:
                return self.id in (1, 2, 13, 14)
            elif cr == QUEEN:
                return self.id in (4, 7, 8, 11)
            elif cr == JACK:
                return self.id in (0, 3, 12, 15)
        if cr in (JACK, QUEEN, KING):
            return False
        return MonteCarlo_RowStack.acceptsCards(self, from_stack, cards)


class Crispy(SimpleCarlo):
    Talon_Class = Crispy_Talon
    RowStack_Class = Crispy_RowStack
    FILL_STACKS_AFTER_DROP = False
    FILL_STACKS_BEFORE_SHIFT = True

    def createGame(self):
        MonteCarlo.createGame(self, rows=4, cols=4)

    def isGameWon(self):
        for i in (1, 2, 13, 14):
            if len(self.s.rows[i].cards) != 0 and \
                    self.s.rows[i].cards[0].rank != KING:
                return False
        for i in (4, 7, 8, 11):
            if len(self.s.rows[i].cards) != 0 and \
                    self.s.rows[i].cards[0].rank != QUEEN:
                return False
        for i in (0, 3, 12, 15):
            if len(self.s.rows[i].cards) != 0 and \
                    self.s.rows[i].cards[0].rank != JACK:
                return False
        for i in (5, 6, 9, 10):
            if len(self.s.rows[i].cards) != 0:
                return False
        return len(self.s.talon.cards) == 0

    def shiftCards(self):
        free = 0
        for r in self.s.rows:
            assert len(r.cards) <= 1
            if not r.cards:
                free += 1
        return free


# ************************************************************************
# * Neighbour
# ************************************************************************

class Neighbour_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # We accept any King. Pairs will get delivered by _dropPairMove.
        return cards[0].rank == KING


class Neighbour_RowStack(MonteCarlo_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards[-1].rank + cards[0].rank != 11:
            return False
        # now look if the stacks are neighbours
        return self.game.isNeighbour(from_stack, self)

    def clickHandler(self, event):
        if self._dropKingClickHandler(event):
            return 1
        return MonteCarlo_RowStack.clickHandler(self, event)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1
        if self.cards[-1].rank == KING:
            assert to_stack in self.game.s.foundations
            BasicRowStack.moveMove(
                self, ncards, to_stack, frames=frames, shadow=shadow)
        else:
            MonteCarlo_RowStack.moveMove(
                self, ncards, to_stack, frames=frames, shadow=shadow)

    def _dropKingClickHandler(self, event):
        if not self.cards:
            return 0
        c = self.cards[-1]
        if c.face_up and c.rank == KING and not self.basicIsBlocked():
            self.game.playSample("autodrop", priority=20)
            self.playMoveMove(1, self.game.s.foundations[0], sound=False)
            return 1
        return 0

    def fillStack(self):
        if not self.cards and self.game.s.talon.canDealCards():
            old_state = self.game.enterState(self.game.S_FILL)
            self.game.s.talon.dealCards()
            self.game.leaveState(old_state)


class Neighbour(MonteCarlo):
    Foundation_Class = Neighbour_Foundation
    RowStack_Class = Neighbour_RowStack

    FILL_STACKS_AFTER_DROP = True

    def getAutoStacks(self, event=None):
        return ((), self.sg.dropstacks, ())

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + card2.rank == 11


# ************************************************************************
# * Fourteen
# * Double Fourteen
# * Juvenile
# ************************************************************************

class Fourteen_RowStack(MonteCarlo_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        return self.cards[-1].rank + cards[0].rank == 12


class Fourteen(Game):
    Foundation_Class = StackWrapper(AbstractFoundationStack, max_accept=0)
    RowStack_Class = Fourteen_RowStack

    FILL_STACKS_AFTER_DROP = False

    #
    # game layout
    #

    def createGame(self, colsperrow=6):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (colsperrow + 1) * l.XS, l.YM + 5 * l.YS)

        # create stacks
        for i in (0, 2.5):
            for j in range(colsperrow):
                x, y = l.XM + j*l.XS, l.YM + i*l.YS
                s.rows.append(self.RowStack_Class(x, y, self,
                                                  max_move=1, max_accept=1,
                                                  dir=0, base_rank=NO_RANK))
        x, y = l.XM + colsperrow * l.XS, l.YM
        s.foundations.append(self.Foundation_Class(x, y, self, suit=ANY_SUIT,
                             max_move=0, max_cards=(52 * self.gameinfo.decks),
                                                   base_rank=ANY_RANK))
        l.createText(s.foundations[0], "s")
        x, y = self.width - l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self._startDealNumRows(3)
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[:4])

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + card2.rank == 12


class DoubleFourteen(Fourteen):
    def createGame(self):
        Fourteen.createGame(self, colsperrow=9)

    def startGame(self):
        self._startDealNumRows(4)
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[:14])


class Juvenile(DoubleFourteen):

    def startGame(self):
        self.startDealSample()
        for i in range(2):
            self.s.talon.dealRow(rows=[self.s.rows[0]], frames=0)
        for i in range(5):
            self.s.talon.dealRow(rows=self.s.rows[:17], frames=0)
        self.s.talon.dealRow(rows=self.s.rows[:17])


# ************************************************************************
# * Nestor
# * Double Nestor
# ************************************************************************

class Nestor_RowStack(MonteCarlo_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        return self.cards[-1].rank == cards[0].rank


class Nestor(Game):
    Foundation_Class = StackWrapper(AbstractFoundationStack, max_accept=0)
    RowStack_Class = Nestor_RowStack

    FILL_STACKS_AFTER_DROP = False

    COLS = 8
    COLCARDS = 6

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + self.COLS * l.XS,
                     l.YM + 2 * l.YS + (self.COLCARDS + 6) * l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(self.COLS):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1,
                                              dir=0, base_rank=NO_RANK))
            x += l.XS
        x, y = l.XM + ((self.COLS / 2) - 2) * l.XS, self.height-l.YS
        for i in range(4):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1,
                                              dir=0, base_rank=NO_RANK))
            x += l.XS
        x, y = self.width-l.XS, self.height-l.YS
        s.foundations.append(self.Foundation_Class(x, y, self, suit=ANY_SUIT,
                             max_move=0, max_cards=(52 * self.gameinfo.decks),
                                                   base_rank=ANY_RANK))
        l.createText(s.foundations[0], "n")
        x, y = l.XM, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _checkRow(self, cards):
        for i in range(len(cards)):
            for j in range(i):
                if cards[i].rank == cards[j].rank:
                    return j
        return -1

    def _shuffleHook(self, cards):
        # no row will have two cards of the same rank
        for i in range(self.COLS):
            for t in range(1000):  # just in case
                j = self._checkRow(cards[i * self.COLCARDS:(i + 1)
                                   * self.COLCARDS])
                if j < 0:
                    break
                j += i * self.COLCARDS
                k = self.random.choice(list(range((i+1) * self.COLCARDS,
                                                  (52 * self.gameinfo.decks))))
                cards[j], cards[k] = cards[k], cards[j]
        cards.reverse()
        return cards

    def startGame(self):
        for r in self.s.rows[:self.COLS]:
            for j in range(self.COLCARDS):
                self.s.talon.dealRow(rows=[r], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[self.COLS:])

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank


class DoubleNestor(Nestor):
    COLS = 10
    COLCARDS = 10


# ************************************************************************
# * Vertical
# ************************************************************************

class Vertical(Nestor):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+9*l.XS, l.YM+2*l.YS+12*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(7):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1,
                                              dir=0, base_rank=NO_RANK))
            x += l.XS
        x, y = l.XM, self.height-l.YS
        for i in range(9):
            s.rows.append(self.RowStack_Class(x, y, self,
                                              max_move=1, max_accept=1,
                                              dir=0, base_rank=NO_RANK))
            x += l.XS
        x, y = self.width-l.XS, l.YM
        s.foundations.append(self.Foundation_Class(x, y, self, suit=ANY_SUIT,
                             max_move=0, max_cards=52, base_rank=ANY_RANK))
        l.createText(s.foundations[0], "s")
        x -= l.XS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(frames=0)
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.rows[:7], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:7])
        self.s.talon.dealRow(rows=[self.s.rows[3]])


# ************************************************************************
# * The Wish
# ************************************************************************

class TheWish(Game):

    FILL_STACKS_AFTER_DROP = False
    ROWS = 8

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + ((self.ROWS / 2) + 2) * l.XS,
                     2 * l.YM + 2 * l.YS + 6 * l.YOFFSET)

        currentrow = 0
        # create stacks
        for i in range(2):
            for j in range(math.ceil(self.ROWS / 2)):
                if currentrow < self.ROWS:
                    x, y = l.XM + j*l.XS, l.YM+i*(l.YM+l.YS+3*l.YOFFSET)
                    s.rows.append(Nestor_RowStack(x, y, self,
                                                  max_move=1, max_accept=1,
                                                  dir=0, base_rank=NO_RANK))
                    currentrow += 1

        x, y = self.width - l.XS, l.YM
        s.talon = InitialDealTalonStack(x, y, self)

        x, y = self.width - l.XS, self.height - l.YS
        s.foundations.append(
            AbstractFoundationStack(
                x, y, self, suit=ANY_SUIT,
                max_move=0, max_cards=32, max_accept=0, base_rank=ANY_RANK))
        l.createText(s.foundations[0], "n")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        self._startAndDealRow()

    def fillStack(self, stack):
        if stack.cards:
            self.flipMove(stack)

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank


class TheWishOpen(TheWish):
    def fillStack(self, stack):
        pass

    def startGame(self):
        self._startDealNumRowsAndDealSingleRow(3)


class PatientPairs(TheWish):
    ROWS = 13


class PatientPairsOpen(TheWishOpen):
    ROWS = 13


# ************************************************************************
# * Der letzte Monarch (The last Monarch)
# ************************************************************************


class DerLetzteMonarch_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if cards is None:
            # special hack for _getDropStack() below
            return SS_FoundationStack.acceptsCards(
                self, from_stack, from_stack.cards)
        #
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # We only accept cards from a Reserve. Other cards will get
        # delivered by _handlePairMove.
        return from_stack in self.game.s.reserves


class DerLetzteMonarch_RowStack(ReserveStack):
    def canDropCards(self, stacks):
        return (None, 0)

    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        # must be neighbours
        if not self.game.isNeighbour(from_stack, self):
            return False
        # must be able to move our card to the foundations or reserves
        return self._getDropStack() is not None

    def _getDropStack(self):
        if len(self.cards) != 1:
            return None
        for s in self.game.s.foundations:
            if s.acceptsCards(self, None):      # special hack
                return s
        for s in self.game.s.reserves:
            if not s.cards:
                return s
        return None

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1 and to_stack in self.game.s.rows
        assert len(to_stack.cards) == 1
        self._handlePairMove(ncards, to_stack, frames=-1, shadow=0)
        self.fillStack()

    def _handlePairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        s = other_stack._getDropStack()
        assert s is not None
        game.moveMove(n, other_stack, s, frames=frames, shadow=shadow)
        game.moveMove(n, self, other_stack, frames=0)
        game.leaveState(old_state)


class DerLetzteMonarch_ReserveStack(ReserveStack):
    def clickHandler(self, event):
        return self.doubleclickHandler(event)


class DerLetzteMonarch(Game):
    Talon_Class = InitialDealTalonStack

    #
    # game layout
    #

    def createGame(self, texts=False):
        # create layout
        l, s = Layout(self, card_x_space=4), self.s

        # set window
        decks = self.gameinfo.decks
        if decks == 1:
            w = l.XM + 13*l.XS
            dx = 0
        else:
            w = l.XM + 15*l.XS
            dx = l.XS
        h = l.YM + 5*l.YS
        self.setSize(w, h)

        # create stacks
        for i in range(4):
            for j in range(13):
                x, y, = dx + l.XM + j*l.XS, l.YM + (i+1)*l.YS
                s.rows.append(
                    DerLetzteMonarch_RowStack(
                        x, y, self, max_accept=1, max_cards=2))
        for i in range(4):
            x, y, = l.XM + (i+2)*l.XS, l.YM
            s.reserves.append(
                DerLetzteMonarch_ReserveStack(
                    x, y, self, max_accept=0))
        for i in range(4*decks):
            x, y, = l.XM + (i+7)*l.XS, l.YM
            s.foundations.append(DerLetzteMonarch_Foundation(x, y, self,
                                 suit=i % 4, max_move=0))
        s.talon = self.Talon_Class(l.XM, l.YM, self)
        if texts:
            l.createText(s.talon, 'ne')

        # define stack-groups (non default)
        self.sg.talonstacks = [s.talon]
        self.sg.openstacks = s.foundations + s.rows
        self.sg.dropstacks = s.rows + s.reserves
        self.sg.reservestacks = s.reserves

    #
    # game overrides
    #

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.rows[:39], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[39:])

    def isGameWon(self):
        c = 0
        for s in self.s.foundations:
            c = c + len(s.cards)
        return c == self.gameinfo.ncards-1

    def getAutoStacks(self, event=None):
        return ((), self.s.reserves, ())

    def getDemoInfoText(self):
        return "Der letzte\nMonarch"

    #
    # game extras
    #

    def isNeighbour(self, stack1, stack2):
        if not (0 <= stack1.id <= 51 and 0 <= stack2.id <= 51):
            return False
        column = stack2.id % 13
        diff = stack1.id - stack2.id
        if column == 0:
            return diff in (-13, 1, 13)
        elif column == 12:
            return diff in (-13, -1, 13)
        else:
            return diff in (-13, -1, 1, 13)


class TheLastMonarchII(DerLetzteMonarch):
    Talon_Class = AutoDealTalonStack

    def createGame(self):
        DerLetzteMonarch.createGame(self, texts=True)

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)


# ************************************************************************
# * Doublets
# ************************************************************************

class DoubletsII(Game):
    FILL_STACKS_AFTER_DROP = False  # for Nestor_RowStack

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+12*l.XS, l.YM+3*l.YS+3*l.YOFFSET)

        x, y = l.XM, l.YM
        for i in range(12):
            s.rows.append(Nestor_RowStack(x, y, self,
                                          max_move=1, max_accept=1,
                                          dir=0, base_rank=NO_RANK))
            x += l.XS
        x, y = l.XM, self.height-l.YS
        s.talon = AutoDealTalonStack(x, y, self)
        l.createText(s.talon, 'n')

        x, y = self.width-l.XS, self.height-l.YS
        s.foundations.append(AbstractFoundationStack(x, y, self, suit=ANY_SUIT,
                             max_move=0, max_cards=52,
                             base_rank=ANY_RANK, max_accept=0))
        l.createText(s.foundations[0], "n")

        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0, flip=0)
        self._startAndDealRow()

    def fillStack(self, stack):
        if stack in self.s.rows:
            if stack.cards:
                stack.flipMove(animation=True)
            else:
                if self.s.talon.cards:
                    old_state = self.enterState(self.S_FILL)
                    self.s.talon.flipMove()
                    self.s.talon.moveMove(1, stack)
                    self.leaveState(old_state)


# ************************************************************************
# * Right and Left
# ************************************************************************

class RightAndLeft_Talon(DealRowRedealTalonStack):
    def _redeal(self, rows=None, reverse=False, frames=0):
        return DealRowRedealTalonStack._redeal(self, rows=rows,
                                               reverse=reverse, frames=3)


class RightAndLeft(Game):

    FILL_STACKS_AFTER_DROP = False

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+5*l.XS, l.YM+3*l.YS)

        # create stacks
        x, y = l.XM+l.XS, l.YM+2*l.YS
        s.talon = RightAndLeft_Talon(x, y, self, max_rounds=UNLIMITED_REDEALS)

        l.createText(s.talon, 'se')
        x, y = l.XM+0.5*l.XS, l.YM
        for i in range(2):
            stack = Nestor_RowStack(x, y, self, max_move=1, max_accept=1,
                                    dir=0, base_rank=NO_RANK)
            stack.CARD_YOFFSET = 0
            l.createText(stack, 's')
            s.rows.append(stack)
            x += l.XS

        x += 1.5*l.XS
        s.foundations.append(AbstractFoundationStack(x, y, self, suit=ANY_SUIT,
                             max_move=0, max_cards=104,
                             max_accept=0, base_rank=ANY_RANK))
        l.createText(s.foundations[0], 's')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self._startAndDealRow()


# ************************************************************************
# * Aces Square
# ************************************************************************

class AcesSquare_RowStack(MonteCarlo_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards[-1].rank == 0 or cards[0].rank == 0:
            return False

        return (self.game.isNeighbour(from_stack, self)
                and self.cards[-1].suit == cards[0].suit)


class AcesSquare(MonteCarlo):
    Talon_Class = AutoDealTalonStack
    RowStack_Class = AcesSquare_RowStack

    def createGame(self):
        MonteCarlo.createGame(self, rows=4, cols=4)

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 48

    def fillStack(self, stack):
        if stack in self.s.rows:
            if len(stack.cards) == 0 and len(self.s.talon.cards) > 0:
                self.flipMove(self.s.talon)
                self.moveMove(1, self.s.talon, stack)

    def isNeighbour(self, stack1, stack2):
        return (stack1.id // 4 == stack2.id // 4 or
                stack1.id % 4 == stack2.id % 4)


# register the game
registerGame(GameInfo(89, MonteCarlo, "Monte Carlo",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK,
                      altnames=("Quilt",)))
registerGame(GameInfo(216, MonteCarlo2Decks, "Monte Carlo (2 Decks)",
                      GI.GT_PAIRING_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(212, Weddings, "Weddings",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(90, SimpleCarlo, "Simple Carlo",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(91, SimplePairs, "Simple Pairs",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_LUCK,
                      altnames=("Jamestown", "Pirate Gold", "Treasure Hunt",
                                "Hunter")))
registerGame(GameInfo(92, Neighbour, "Neighbour",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(96, Fourteen, "Fourteen",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 1, 0,
                      GI.SL_MOSTLY_LUCK, altnames=("Fourteen Out",
                                                   "Fourteen Puzzle",
                                                   "Take Fourteen")))
registerGame(GameInfo(235, Nestor, "Nestor",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 1, 0,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(152, DerLetzteMonarch, "The Last Monarch",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Der letzte Monarch",)))
registerGame(GameInfo(328, TheWish, "The Wish",
                      GI.GT_PAIRING_TYPE | GI.GT_STRIPPED, 1, 0,
                      GI.SL_MOSTLY_LUCK, ranks=(0, 6, 7, 8, 9, 10, 11, 12)))
registerGame(GameInfo(329, TheWishOpen, "The Wish (Open)",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL |
                      GI.GT_STRIPPED, 1, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12),
                      rules_filename="thewish.html"))
registerGame(GameInfo(368, Vertical, "Vertical",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 1, 0,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(649, DoubletsII, "Doublets II",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(663, TheLastMonarchII, "The Last Monarch II",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0,
                      GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(727, RightAndLeft, "Right and Left",
                      GI.GT_PAIRING_TYPE, 2, -1, GI.SL_LUCK))
registerGame(GameInfo(801, DoubleNestor, "Double Nestor",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 2, 0,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(810, Quatorze, "Quatorze",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(829, BlockTen, "Block Ten",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(862, SimpleTens, "Simple Tens",
                      GI.GT_PAIRING_TYPE | GI.GT_STRIPPED, 1, 0, GI.SL_LUCK,
                      ranks=(0, 1, 2, 3, 4, 5, 6, 7, 8),
                      altnames=("Add Up Tens",)))
registerGame(GameInfo(867, DoubleFourteen, "Double Fourteen",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 2, 0,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(874, PatientPairs, "Patient Pairs",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK,
                      altnames=("Isabel",)))
registerGame(GameInfo(875, PatientPairsOpen, "Patient Pairs (Open)",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 1, 0,
                      GI.SL_MOSTLY_SKILL, rules_filename="patientpairs.html"))
registerGame(GameInfo(898, AcesSquare, "Aces Square",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(923, Crispy, "Crispy",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(935, Juvenile, "Juvenile",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 2, 0,
                      GI.SL_MOSTLY_LUCK))
