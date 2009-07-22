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

from hanafuda_common import *

# ************************************************************************
# * Paulownia
# ************************************************************************

class Paulownia(AbstractFlowerGame):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = Hanafuda_SS_FoundationStack
    RowStack_Class = Hanafuda_SequenceStack
    MaxRounds = -1
    BaseRank = 0
    NumDeal = 1

    #
    # Game layout
    #

    def createGame(self, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                            max_rounds=self.MaxRounds, num_deal=self.NumDeal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                        suit=r.suit, base_rank=3))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                            base_rank=self.BaseRank, yoffset=l.YOFFSET))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * self.gameinfo.decks
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.rows[i + 1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()



class Pine(Paulownia):
    MaxRounds = 1
    NumDeal = 3


class Eularia(Paulownia):
    BaseRank = ANY_RANK


class Peony(Eularia):
    NumDeal = 3


class Iris(Peony):
    MaxRounds = 1



# ************************************************************************
# * Queue
# ************************************************************************

class LesserQueue(AbstractFlowerGame):
    Hint_Class = Queue_Hint
    BRAID_CARDS = 20
    BRAID_OFFSET = 1

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        decks = self.gameinfo.decks
        yoffset = l.YOFFSET*self.BRAID_OFFSET
        h = l.YM+max(l.YS*5.5, l.YS+self.BRAID_CARDS*yoffset+2*l.TEXT_MARGIN)
        self.setSize(l.XM + l.XS * 10.5, h)

        # extra settings
        self.base_card = None

        # Create rows, reserves
        s.addattr(braid = None)
        x, x0 = l.XM + l.XS * 2, (decks - 1.5) % 2.5
        for j in range(decks / 2):
            y = l.YM
            for i in range(2):
                s.rows.append(Queue_RowStack(x + l.XS * (x0 + j), y, self))
                s.rows.append(Queue_RowStack(x + l.XS * (4 + x0 + j + .5), y, self))
                y = y + l.YS * (3 + (decks > 2))
        y = l.YM + l.YS
        for i in range(2):
            s.rows.append(Queue_ReserveStack(x, y, self))
            s.rows.append(Queue_ReserveStack(x + l.XS, y, self))
            s.rows.append(Queue_ReserveStack(x, y + l.YS, self))
            s.rows.append(Queue_ReserveStack(x + l.XS, y + l.YS, self))
            if decks - 2:
                s.rows.append(Queue_ReserveStack(x, y + l.YS * 2, self))
                s.rows.append(Queue_ReserveStack(x + l.XS, y + l.YS * 2, self))
            x = x + l.XS * 4.5

        # Create braid
        x, y = l.XM + l.XS * 4.25, l.YM
        s.braid = Queue_BraidStack(x, y, self, yoffset=self.BRAID_OFFSET)

        # Create talon, waste
        x, y = l.XM, h-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "n")
        s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                             self.width/2, h-2*l.TEXT_MARGIN,
                                             anchor="center",
                                             font=self.app.getFont("canvas_default"))
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "n")

        # Create foundations
        x = l.XM
        for j in range(decks / 2):
            y = l.YM
            for i in range(4):
                s.foundations.append(Queue_Foundation(x, y, self, -1, mod=12,
                                        max_cards=12, base_suit=ANY_SUIT, base_rank=i, rank=i))
                s.foundations.append(Queue_Foundation(x + l.XS * (9.5 - j * 2), y, self, -1, mod=12,
                                        max_cards=12, base_suit=ANY_SUIT, base_rank=i, rank=i))
                y = y + l.YS
            x = x + l.XS
        self.texts.info = MfxCanvasText(self.canvas,
                                        self.width/2, h-l.TEXT_MARGIN,
                                        anchor="center",
                                        font=self.app.getFont("canvas_default"))

        # define stack-groups
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.openstacks = s.foundations + s.rows + s.reserves
        self.sg.dropstacks = [s.braid] + s.rows + [s.waste] + s.reserves


    #
    # game overrides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * self.gameinfo.decks
        self.startDealSample()
        self.base_card = None
        self.updateText()
        for i in range(self.BRAID_CARDS):
            self.s.talon.dealRow(rows = [self.s.braid])
        self.s.talon.dealRow()
        # deal base_card to foundations, update cap.base_rank
        self.base_card = self.s.talon.getCard()
        to_stack = self.s.foundations[2 * self.base_card.rank]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack)
        self.updateText()
        for s in self.s.foundations:
            s.cap.base_suit = self.base_card.suit
        # deal first card to WasteStack
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank == card2.rank and
                ((card1.suit + 1) % 12 == card2.suit or (card2.suit + 1) % 12 == card1.suit))

    def getHighlightPilesStacks(self):
        return ()

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_suit = self.base_card.suit

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


    #
    # game extras
    #

    def updateText(self):
        if self.preview > 1 or not self.texts.info:
            return
        if not self.base_card:
            t = ""
        else:
            t = self.SUITS[self.base_card.suit]
            dir = self.getFoundationDir()
            if dir == 1:
                t = t + _(" Ascending")
            elif dir == 11:
                t = t + _(" Descending")
        self.texts.info.config(text = t)

    def getFoundationDir(self):
        for s in self.s.foundations:
            if len(s.cards) >= 2:
                return (s.cards[-1].suit - s.cards[-2].suit) % 12
        return 0



class GreaterQueue(LesserQueue):
    Hint_Class = Queue_Hint
    BRAID_CARDS = 40
    BRAID_OFFSET = .5



# ************************************************************************
# * Japanese Garden
# ************************************************************************

class JapaneseGarden(AbstractFlowerGame):
    Hint_Class = CautiousDefaultHint
    RowStack_Class = FlowerClock_RowStack
    WIDTH = 10
    HEIGHT = 6
    XROWS = 3
    YROWS = 2
    MAX_CARDS = 6
    MAX_MOVE = 1
    XRESERVES = 6
    YRESERVES = 2
    MAX_RESERVE = 0
    INITIAL_DEAL = 6
    DEAL_RESERVES = 1

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_card")

        # Set window size
        self.setSize(l.XM + l.XS * self.WIDTH, l.YM * 3 + l.YS * self.HEIGHT)

        # Create foundations
        x = self.width / 2 + l.XM / 2 - l.XS * 3
        y = l.YM
        for j in range(2):
            for i in range(6):
                s.foundations.append(Hanafuda_SS_FoundationStack(x, y, self, i + (j * 6),
                                    max_cards=4, max_accept=1, base_rank=3))
                x = x + l.XS
            x = self.width / 2 + l.XM / 2 - l.XS * 3
            y = y + l.YS

        # Create flower beds
        x = l.XM
        y = l.YM * 2 + l.YS * 2
        for j in range(self.YROWS):
            for i in range(self.XROWS):
                row = self.RowStack_Class(x, y, self, yoffset=0, max_accept=self.MAX_MOVE,
                                max_move=self.MAX_MOVE, max_cards=self.MAX_CARDS, base_rank=0)
                row.CARD_XOFFSET = l.CW / 2
                s.rows.append(row)
                x = x + self.width / self.XROWS
            x = l.XM
            y = y + l.YS
        self.setRegion(s.rows, (l.XM, l.YS * 2, 999999, y))

        # Create pool
        x = self.width / 2 + l.XM / 2 - (l.XS * self.XRESERVES) / 2
        for j in range(self.YRESERVES):
            for i in range(self.XRESERVES):
                s.reserves.append(ReserveStack(x, y, self, max_accept=self.MAX_RESERVE))
                x = x + l.XS
            x = self.width / 2 + l.XM / 2 - l.XS * (self.XRESERVES / 2)
            y = y + l.YS
        if s.reserves:
            self.setRegion(s.reserves, (l.XM, l.YS * (2 + self.YROWS), 999999, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(l.XM, l.YM, self)

        # Define stack-groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48
        self.startDealSample()
        for i in range(self.INITIAL_DEAL):
            self.s.talon.dealRow()
        if self.DEAL_RESERVES:
            self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealCards()



class JapaneseGardenII(JapaneseGarden):
    RowStack_Class = JapaneseGarden_RowStack



class JapaneseGardenIII(JapaneseGardenII):
    XROWS = 2
    YROWS = 4
    MAX_CARDS = 7
    XRESERVES = 0
    YRESERVES = 0
    DEAL_RESERVES = 0


class SixSages(JapaneseGarden):
    Hint_Class = CautiousDefaultHint
    XROWS = 2
    YROWS = 3
    MAX_CARDS = 9
    XRESERVES = 1
    YRESERVES = 1
    MAX_RESERVE = 1
    INITIAL_DEAL = 8
    DEAL_RESERVES = 0


class SixTengus(SixSages):
    RowStack_Class = HanafudaRK_RowStack
    HEIGHT = 5
    MAX_MOVE = 2
    XRESERVES = 0
    YRESERVES = 0



# ************************************************************************
# * Hanafuda Four Seasons
# ************************************************************************

class HanafudaFourSeasons(AbstractFlowerGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_card")

        # Set window size
        self.setSize(l.XM + l.XS * 7, l.YM + l.YS * 5)

        # Create rows
        x, y, offset = l.XM, l.YM, self.app.images.CARD_YOFFSET
        for i in range(6):
            s.rows.append(Samuri_RowStack(x, y, self, offset, max_cards=8,
                                                    max_accept=8, base_rank=0))
            x = x + l.XS + l.XM + (l.XM * (i == 2))
        x, y = l.XM, y + l.YS * 2.5
        for i in range(6):
            s.rows.append(Samuri_RowStack(x, y, self, offset, max_cards=8,
                                                    max_accept=8, base_rank=0))
            x = x + l.XS + l.XM + (l.XM * (i == 2))
        self.setRegion(s.rows, (0, 0, 999999, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(-l.XS, -l.YS, self)

        # Define stack-groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 48 * self.gameinfo.decks
        self.startDealSample()
        for i in range(4):
            self.s.talon.dealRow(flip=1)


    #
    # Game extras
    #

    def isGameWon(self):
        for r in self.s.rows:
            cards = r.cards
            if not len(cards) == 4:
                return 0
            if not (cards[0].suit == r.id
                    and r.isHanafudaSequence(cards)):
                return 0
        return 1



# ************************************************************************
# * Wisteria
# ************************************************************************

class Wisteria(AbstractFlowerGame):
    RowStack_Class = StackWrapper(Hanafuda_SequenceStack, base_rank=NO_RANK)

    #
    # game layout
    #

    def createGame(self, rows=13):
        # create layout
        l, s = Layout(self), self.s

        # set size
        self.setSize(l.XM + rows * l.XS, l.YM + 6 * l.YS)

        # create stacks
        x, y = self.width / 2 - l.XS * 3, l.YM
        for i in range(2):
            for suit in range(6):
                s.foundations.append(Hanafuda_SS_FoundationStack(x, y, self, suit=suit + (6 * i)))
                x = x + l.XS
            x, y = self.width / 2 - l.XS * 3, y + l.YS
        self.setRegion(self.s.foundations, (-999, -999, 999999, l.YM + l.YS * 2), priority=1)
        x, y = l.XM, l.YM + l.YS * 2
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self, yoffset=l.YOFFSET)
            s.rows.append(stack)
            x = x + l.XS
        s.talon = InitialDealTalonStack(l.XS, l.YS / 2, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        i = 0
        while self.s.talon.cards:
            if self.s.talon.cards[-1].rank == 0:
                if self.s.rows[i].cards:
                    i = i + 1
            self.s.talon.dealRow(rows=[self.s.rows[i]], frames=4)



# ************************************************************************
# * Flower Arrangement Hint
# ************************************************************************

class FlowerArrangement_Hint(AbstractHint):
    def computeHints(self):
        game = self.game

        # 2)See if we can move a card to the tableaux
        if not self.hints:
            for r in game.sg.dropstacks:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                if r in game.s.tableaux:
                    rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                    if rr.acceptsCards(None, pile):
                        # do not move a card that is already in correct place
                        continue
                    base_score = 80000 + (4 - r.cap.base_suit)
                else:
                    base_score = 80000
                # find a stack that would accept this card
                for t in game.s.tableaux:
                    if t is not r and t.acceptsCards(r, pile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 3)See if we can move a card from the tableaux
        #    to a row stack. This can only happen if there are
        #    no more cards to deal.
        if not self.hints:
            for r in game.s.tableaux:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                if rr.acceptsCards(None, pile):
                    # do not move a card that is already in correct place
                    continue
                # find a stack that would accept this card
                for t in game.s.rows:
                    if t is not r and t.acceptsCards(r, pile):
                        score = 70000 + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 4)See if we can move a card within the row stacks
        if not self.hints:
            for r in game.s.rows:
                pile = r.getPile()
                if not pile or len(pile) != 1 or len(pile) == len(r.cards):
                    continue
                base_score = 60000
                # find a stack that would accept this card
                for t in game.s.rows:
                    if t is not r and t.acceptsCards(r, pile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 5)See if we can deal cards
        if self.level >= 2:
            if game.canDealCards():
                self.addHint(self.SCORE_DEAL, 0, game.s.talon, None)


# ************************************************************************
# * Flower Arrangement Stacks
# ************************************************************************

class FlowerArrangement_TableauStack(Flower_OpenStack):
    def __init__(self, x, y, game, yoffset, **cap):
        kwdefault(cap, dir=-1, max_move=1, max_cards=4, max_accept=1, base_rank=3)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        # check that the base card is correct
        suits = range(self.cap.mod, (self.cap.mod + 4))
        if self.cards and (self.cards[0].rank == 3
                and self.cards[-1].suit in suits):
            return self.isHanafudaSequence([self.cards[-1], cards[0]])
        return not self.cards and cards[0].rank == 3 and cards[0].suit in suits

    def getBottomImage(self):
        return self.game.app.images.getSuitBottom()


class FlowerArrangement_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        # check
        return not (self.cards or self.game.s.talon.cards)

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()


# ************************************************************************
# * Flower Arrangement
# ************************************************************************

class FlowerArrangement(Game):
    Hint_Class = FlowerArrangement_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        TABLEAU_YOFFSET = min(9, max(3, l.YOFFSET / 3))

        # set window
        th = l.YS + 3 * TABLEAU_YOFFSET
        # (set piles so that at least 2/3 of a card is visible with 10 cards)
        h = (10-1)*l.YOFFSET + l.CH*2/3
        self.setSize(10*l.XS+l.XM, l.YM + 3*th + l.YM + h)

        # create stacks
        s.addattr(tableaux=[])     # register extra stack variable
        x = l.XM + 8 * l.XS + l.XS / 2
        y = l.YM
        for i in range(3):
            x = l.XM
            for j in range(8):
                s.tableaux.append(FlowerArrangement_TableauStack(x, y, self, TABLEAU_YOFFSET, mod=i * 4))
                x = x + l.XS
            y = y + th
        x, y = l.XM, y + l.YM
        for i in range(8):
            s.rows.append(FlowerArrangement_RowStack(x, y, self, max_accept=1))
            x = x + l.XS
        x = l.XM + 8 * l.XS + l.XS / 2
        y = self.height - l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, "se")

        # define stack-groups
        self.sg.openstacks = s.tableaux + s.rows
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.tableaux + s.rows

    #
    # game overrides
    #

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.tableaux, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        for stack in self.s.tableaux:
            if len(stack.cards) != 4:
                return 0
        return 1

    def fillStack(self, stack):
        if self.s.talon.cards:
            if stack in self.s.rows and len(stack.cards) == 0:
                self.s.talon.dealRow(rows=[stack])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 3 == card2.rank or card2.rank + 3 == card1.rank))

    def getHighlightPilesStacks(self):
        return ()


# ************************************************************************
# * Register the games
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level):
    game_type = game_type | GI.GT_HANAFUDA
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  suits=range(12), ranks=range(4))
    registerGame(gi)
    return gi

r(12369, Paulownia, 'Paulownia', GI.GT_HANAFUDA, 1, -1, GI.SL_BALANCED)
r(12370, LesserQueue, 'Lesser Queue', GI.GT_HANAFUDA, 2, 2, GI.SL_BALANCED)
r(12371, GreaterQueue, 'Greater Queue', GI.GT_HANAFUDA, 4, 2, GI.SL_BALANCED)
r(12373, JapaneseGarden, 'Japanese Garden', GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12374, JapaneseGardenII, 'Japanese Garden II', GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12375, SixSages, 'Six Sages', GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12376, SixTengus, 'Six Tengus', GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12377, JapaneseGardenIII, 'Japanese Garden III', GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12378, HanafudaFourSeasons, 'Hanafuda Four Seasons', GI.GT_HANAFUDA | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL)
r(12380, Eularia, 'Eularia', GI.GT_HANAFUDA, 1, -1, GI.SL_BALANCED)
r(12381, Peony, 'Peony', GI.GT_HANAFUDA, 1, -1, GI.SL_BALANCED)
r(12382, Iris, 'Iris', GI.GT_HANAFUDA, 1, 0, GI.SL_BALANCED)
r(12383, Pine, 'Pine', GI.GT_HANAFUDA, 1, 0, GI.SL_BALANCED)
r(12384, Wisteria, 'Wisteria', GI.GT_HANAFUDA, 1, 0, GI.SL_MOSTLY_SKILL)
r(12385, FlowerArrangement, 'Flower Arrangement', GI.GT_HANAFUDA, 2, 0, GI.SL_BALANCED)

del r
