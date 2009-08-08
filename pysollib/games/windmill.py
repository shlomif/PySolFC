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

from golf import BlackHole_Foundation


# ************************************************************************
# *
# ************************************************************************

class Windmill_Foundation(RK_FoundationStack):
    def getBottomImage(self):
        if self.cap.base_rank == ACE:
            return self.game.app.images.getLetter(ACE)
        return RK_FoundationStack.getBottomImage(self)


class Windmill_RowStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts one card from the Waste pile
        return from_stack is self.game.s.waste


# ************************************************************************
# * Windmill
# * Dutch Solitaire
# ************************************************************************

class Windmill(Game):

    Foundation_Classes = [
        StackWrapper(Windmill_Foundation, mod=13, min_cards=1, max_cards=52),
        StackWrapper(Windmill_Foundation, base_rank=KING, dir=-1),
        ]
    RowStack_Class = Windmill_RowStack

    FOUNDATIONS_LAYOUT = ((1,0.6), (3,0.6), (1,3.4), (3,3.4))
    ROWS_LAYOUT = ((2,0), (2,1), (0,2), (1,2), (3,2), (4,2), (2,3), (2,4))
    FILL_STACK = True

    #
    # game layout
    #

    def createGame(self, card_x_space=20):
        # create layout
        l, s = Layout(self, card_x_space=card_x_space), self.s

        # set window
        max_x = max([i[0] for i in self.FOUNDATIONS_LAYOUT+self.ROWS_LAYOUT])
        max_y = max([i[1] for i in self.FOUNDATIONS_LAYOUT+self.ROWS_LAYOUT])
        self.setSize((3+max_x)*l.XS+l.XM, (1+max_y)*l.YS+l.YM+l.YM)

        # create stacks
        x = l.XM
        y = l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")
        x0, y0 = x + l.XS, y
        for d in self.ROWS_LAYOUT:
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            stack = self.RowStack_Class(x, y, self)
            s.rows.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
        x, y = x0 + 2 * l.XS, y0 + 2 * l.YS
        fnd_cls = self.Foundation_Classes[0]
        s.foundations.append(fnd_cls(x, y, self))
        fnd_cls = self.Foundation_Classes[1]
        for d in self.FOUNDATIONS_LAYOUT:
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            s.foundations.append(fnd_cls(x, y, self))

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        for c in cards:
            if c.id == 0:
                break
        cards.remove(c)
        return cards + [c]

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=(self.s.foundations[0],))
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if self.FILL_STACK and len(stack.cards) == 0:
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)

    shallHighlightMatch = Game._shallHighlightMatch_RK

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        # disable auto drop - this would ruin the whole gameplay
        return ((), (), ())


class DutchSolitaire_RowStack(UD_RK_RowStack):
    getBottomImage = Stack._getReserveBottomImage


class DutchSolitaire(Windmill):
    Hint_Class = CautiousDefaultHint
    Foundation_Classes = [
        StackWrapper(BlackHole_Foundation, suit=ANY_SUIT, mod=13,
                     max_cards=UNLIMITED_CARDS, min_cards=1),
        StackWrapper(BlackHole_Foundation, suit=ANY_SUIT, mod=13,
                     max_cards=UNLIMITED_CARDS, min_cards=1),
        ]
    RowStack_Class = DutchSolitaire_RowStack

    FOUNDATIONS_LAYOUT = ((1,1), (3,1), (1,3), (3,3))
    ROWS_LAYOUT = ((2,0.5), (-0.5,2), (0.5,2), (3.5,2), (4.5,2), (2,3.5))
    FILL_STACK = False

    def createGame(self):
        Windmill.createGame(self, card_x_space=10)

    def _shuffleHook(self, cards):
        # move 5 Aces to top of the Talon (i.e. first cards to be dealt)
        def select_cards(c):
            if c.rank == ACE:
                if c.suit in (0, 1):
                    return True, c.suit
                if c.suit == 3 and c.deck == 0:
                    return True, c.suit
            return False, None
        return self._shuffleHookMoveToTop(cards, select_cards)

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(8):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getAutoStacks(self, event=None):
        return (self.sg.dropstacks, self.sg.dropstacks, self.sg.dropstacks)


# ************************************************************************
# * Napoleon's Tomb
# ************************************************************************

class NapoleonsTomb(Game):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, card_x_space=20, card_y_space=20), self.s

        # set window
        self.setSize(5*l.XS+l.XM, 3*l.YS+l.YM+l.YM)

        # create stacks
        x = l.XM
        y = l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")
        x0, y0 = x + l.XS, y
        for d in ((0,1), (1,0), (1,2), (2,1)):
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            s.rows.append(Windmill_RowStack(x, y, self))
        x, y = x0 + l.XS, y0 + l.YS
        s.foundations.append(Windmill_Foundation(x, y, self, base_rank=5,
                             mod=13, max_cards=24, dir=-1))
        for d in ((0.1, 0.1), (1.9, 0.1), (0.1, 1.9), (1.9, 1.9)):
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            s.foundations.append(Windmill_Foundation(x, y, self,
                                 max_cards=7, base_rank=6, mod=13))

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Corners
# ************************************************************************

class Corners(Game):
    RowStack_Class = ReserveStack

    def createGame(self, max_rounds=3):
        # create layout
        l, s = Layout(self, card_x_space=20, card_y_space=20), self.s

        # set window
        self.setSize(5*l.XS+l.XM, 4*l.YS+3*l.YM)

        # create stacks
        x, y = l.XM+1.5*l.XS, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, "sw")
        if max_rounds > 1:
            l.createRoundText(self.s.talon, 'nw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")
        x0, y0 = l.XM, l.YM+l.YS
        i = 0
        for d in ((0,0), (4,0), (0,2), (4,2)):
            x, y = x0+d[0]*l.XS, y0+d[1]*l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    max_move=0, mod=13))
            i += 1
        for d in ((2,0), (1,1), (2,1), (3,1), (2,2)):
            x, y = x0+d[0]*l.XS, y0+d[1]*l.YS
            stack = self.RowStack_Class(x, y, self)
            s.rows.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0

        # define stack-groups
        l.defaultStackGroups()


    def fillStack(self, stack):
        if len(stack.cards) == 0:
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)


    def _shuffleHook(self, cards):
        suits = []
        top_cards = []
        for c in cards[:]:
            if c.suit not in suits:
                suits.append(c.suit)
                cards.remove(c)
                top_cards.append(c)
                if len(suits) == 4:
                    break
        top_cards.sort(lambda a, b: cmp(b.suit, a.suit))
        return cards+top_cards


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Czarina
# * Four Seasons
# * Florentine Patience
# ************************************************************************

class Czarina_RowStack(RK_RowStack):
    getBottomImage = Stack._getReserveBottomImage


class Czarina(Corners):
    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(Czarina_RowStack, mod=13, max_move=1)

    def createGame(self, max_rounds=1):
        # extra settings
        self.base_card = None
        Corners.createGame(self, max_rounds=max_rounds)

    def startGame(self):
        self.startDealSample()
        self.base_card = None
        # deal base_card to Foundations, update foundations cap.base_rank
        self.base_card = self.s.talon.getCard()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, self.s.foundations[self.base_card.suit])
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first 3 cards to WasteStack

    def _shuffleHook(self, cards):
        return cards

    shallHighlightMatch = Game._shallHighlightMatch_RKW

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


class FourSeasons(Czarina):
    def fillStack(self, stack):
        pass

class FlorentinePatience(FourSeasons):
    def createGame(self):
        Czarina.createGame(self, max_rounds=2)


# ************************************************************************
# * Simplicity
# ************************************************************************

class Simplicity(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self, max_rounds=2):

        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+4*l.YS)

        self.base_card = None

        i = 0
        for x, y in ((l.XM,        l.YM),
                     (l.XM+7*l.XS, l.YM),
                     (l.XM,        l.YM+3*l.YS),
                     (l.XM+7*l.XS, l.YM+3*l.YS),
                     ):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i, mod=13))
            i += 1
        y = l.YM+l.YS
        for i in range(2):
            x = l.XM+l.XS
            for j in range(6):
                stack = AC_RowStack(x, y, self, max_move=1, mod=13)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS
        x, y = l.XM+3*l.XS, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'sw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        # deal base_card to Foundations, update foundations cap.base_rank
        self.base_card = self.s.talon.getCard()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, self.s.foundations[self.base_card.suit])
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    shallHighlightMatch = Game._shallHighlightMatch_ACW


    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


# register the game
registerGame(GameInfo(30, Windmill, "Windmill",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(277, NapoleonsTomb, "Napoleon's Tomb",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(417, Corners, "Corners",
                      GI.GT_1DECK_TYPE, 1, 2, GI.SL_MOSTLY_LUCK,
                      rules_filename='fourseasons.html'))
registerGame(GameInfo(437, Simplicity, "Simplicity",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK,
                      rules_filename='fourseasons.html'))
registerGame(GameInfo(483, Czarina, "Czarina",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK,
                      rules_filename='fourseasons.html'))
registerGame(GameInfo(484, FourSeasons, "Four Seasons",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK,
                      altnames=('Corner Card', 'Vanishing Cross') ))
registerGame(GameInfo(561, DutchSolitaire, "Dutch Solitaire",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(696, FlorentinePatience, "Florentine Patience",
                      GI.GT_1DECK_TYPE, 1, 1, GI.SL_MOSTLY_LUCK))

