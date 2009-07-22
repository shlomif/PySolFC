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
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# * Curds and Whey
# * Miss Muffet
# * Nordic
# ************************************************************************

class CurdsAndWhey_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        c1, c2 = self.cards[-1], cards[0]
        if c1.rank == c2.rank:
            return True
        if c1.suit == c2.suit:
            return c1.rank == c2.rank+1
        return False

    def canMoveCards(self, cards):
        return isSameSuitSequence(cards) or isRankSequence(cards, dir=0)

    def getHelp(self):
        return _('Tableau. Build down by suit or of the same rank.')


class CurdsAndWhey(Game):

    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(CurdsAndWhey_RowStack, base_rank=KING,
                                  max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS)

    #
    # game layout
    #

    def createGame(self, rows=13):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+rows*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self)
            s.rows.append(stack)
            x += l.XS

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isSameSuitSequence(s.cards):
                    return False
        return True

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank or (
            card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1)


class MissMuffet(CurdsAndWhey):

    def createGame(self):
        CurdsAndWhey.createGame(self, rows=10)

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(rows=[self.s.rows[0], self.s.rows[-1]], frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


class Nordic(MissMuffet):
    RowStack_Class = StackWrapper(CurdsAndWhey_RowStack, base_rank=ANY_RANK,
                                  max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS)


# ************************************************************************
# * Dumfries
# * Galloway
# * Robin
# ************************************************************************

class Dumfries_TalonStack(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler

class Dumfries_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        c1, c2 = self.cards[-1], cards[0]
        if c1.color == c2.color:
            return False
        return c1.rank == c2.rank or c1.rank == c2.rank+1

    def canMoveCards(self, cards):
        return len(cards) == 1 or len(cards) == len(self.cards)

class Dumfries(Game):

    ##Hint_Class = KlondikeType_Hint

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=0, texts=1, playcards=20)
        l.klondikeLayout(**layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = Dumfries_TalonStack(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(SS_FoundationStack(r.x, r.y, self,
                                                    suit=r.suit))
        for r in l.s.rows:
            s.rows.append(Dumfries_RowStack(r.x, r.y, self,
                                            max_move=UNLIMITED_MOVES,
                                            max_accept=UNLIMITED_ACCEPTS))
        # default
        l.defaultAll()
        self.sg.dropstacks.append(s.talon)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.fillStack()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.color != card2.color and abs(card1.rank-card2.rank) in (0, 1)


class Galloway(Dumfries):
    def createGame(self):
        Dumfries.createGame(self, rows=7)


class Robin(Dumfries):
    def createGame(self):
        Dumfries.createGame(self, rows=12)



# ************************************************************************
# * Arachnida
# * Harvestman
# ************************************************************************

class Arachnida_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        c1, c2 = self.cards[-1], cards[0]
        if c1.rank == c2.rank+1:
            return True
        return c1.rank == c2.rank

    def canMoveCards(self, cards):
        return isSameSuitSequence(cards) or isRankSequence(cards, dir=0)


class Arachnida(CurdsAndWhey):
    RowStack_Class = Arachnida_RowStack

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+12*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, "s")
        x += l.XS
        for i in range(10):
            stack = self.RowStack_Class(x, y, self, base_rank=ANY_RANK,
                                        max_move=UNLIMITED_MOVES,
                                        max_accept=UNLIMITED_ACCEPTS)
            s.rows.append(stack)
            x += l.XS
        s.foundations.append(AbstractFoundationStack(x, y, self, suit=ANY_SUIT,
                                                     max_accept=0, max_cards=104))
        l.createText(s.foundations[0], "s")

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(flip=0, frames=0)
        self.s.talon.dealRow(rows=self.s.rows[:4], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def canDealCards(self):
        if not CurdsAndWhey.canDealCards(self):
            return False
        # no row may be empty
        for r in self.s.rows:
            if not r.cards:
                return False
        return True

    def fillStack(self, stack):
        for r in self.s.rows:
            if len(r.cards) >= 13 and isSameSuitSequence(r.cards[-13:]):
                old_state = self.enterState(self.S_FILL)
                self.playSample("drop", priority=200)
                self.moveMove(13, r, self.s.foundations[0])
                self.leaveState(old_state)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank or abs(card1.rank-card2.rank) == 1


class Harvestman(Arachnida):
    RowStack_Class = CurdsAndWhey_RowStack


# ************************************************************************
# * German Patience
# * Bavarian Patience
# ************************************************************************

class GermanPatience(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self, rows=8):

        l, s = Layout(self), self.s

        w, h = l.XM+rows*l.XS, l.YM+2*l.YS+14*l.YOFFSET
        self.setSize(w, h)

        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self, max_cards=13, mod=13, dir=1, max_move=1))
            x += l.XS
        x, y = l.XM, h-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'n')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    def isGameWon(self):
        if self.s.waste.cards or self.s.talon.cards:
            return False
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13: # or not isRankSequence(s.cards):
                    return False
        return True


    shallHighlightMatch = Game._shallHighlightMatch_RKW


class BavarianPatience(GermanPatience):
    def createGame(self, rows=10):
        GermanPatience.createGame(self, rows=10)


# ************************************************************************
# * Trusty Twelve
# * Knotty Nines
# * Sweet Sixteen
# ************************************************************************

class TrustyTwelve_Hint(AbstractHint):
    def computeHints(self):
        game = self.game
        for r in game.s.rows:
            for t in game.s.rows:
                if r is t:
                    continue
                card = r.cards[-1]
                if len(r.cards) == 1 and t.acceptsCards(r, [card]):
                    if len(t.cards) > 1:
                        self.addHint(6000+card.rank, 1, r, t)
                    else:
                        self.addHint(5000+card.rank, 1, r, t)


class TrustyTwelve(Game):
    Hint_Class = TrustyTwelve_Hint

    def createGame(self, rows=12):
        l, s = Layout(self), self.s
        self.setSize(l.XM+(rows+1)*l.XS, l.YM+l.YS+12*l.YOFFSET)
        x, y = l.XM, l.YM
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, "s")
        x += l.XS
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self, max_move=1))
            x += l.XS
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if not stack.cards and stack in self.s.rows:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    def isGameWon(self):
        return len(self.s.talon.cards) == 0

    shallHighlightMatch = Game._shallHighlightMatch_RK


class KnottyNines(TrustyTwelve):
    def createGame(self):
        TrustyTwelve.createGame(self, rows=9)


class SweetSixteen(TrustyTwelve):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+2*l.YS+20*l.YOFFSET)
        x, y = l.XM, l.YM
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, "s")
        y = l.YM
        for i in range(2):
            x = l.XM+l.XS
            for j in range(8):
                s.rows.append(AC_RowStack(x, y, self, max_move=1))
                x += l.XS
            y += l.YS+10*l.YOFFSET
        l.defaultStackGroups()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Glacier
# ************************************************************************

class Glacier(Game):

    def createGame(self, rows=12):
        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM+2*l.YS+l.TEXT_HEIGHT+20*l.YOFFSET)

        x, y = l.XM+(rows-4)/2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 mod=13, max_cards=26))
            x += l.XS
        x, y = l.XM, l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self, mod=13))
            x += l.XS
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, num_deal=2, max_rounds=1)
        l.createText(s.talon, 's')
        x = x + l.XS
        s.waste = WasteStack(x, y, self, max_cards=2)
        s.waste.CARD_XOFFSET = l.XOFFSET

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * Eight Packs (ex. Four Packs)
# * Four Packs
# ************************************************************************

class EightPacks(Game):
    RowStack_Class = SS_RowStack

    def createGame(self, max_rounds=3, width=10, playcards=14):
        l, s = Layout(self), self.s
        self.setSize(l.XM+width*l.XS,
                     l.YM+2*l.YS+l.TEXT_HEIGHT+playcards*l.YOFFSET)

        x, y = l.XM, l.YM
        for i in range(10):
            s.rows.append(self.RowStack_Class(x, y, self, dir=1))
            x += l.XS

        x, y = self.width-l.XS, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, 'n')
        l.createRoundText(s.talon, 'nnn')

        x -= l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def isGameWon(self):
        if self.s.talon.cards or self.s.waste.cards:
            return False
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13:
                    return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_SS


class FourPacks_RowStack(SS_RowStack):
    def canMoveCards(self, cards):
        if not self.basicCanMoveCards(cards):
            return False
        return len(cards) == len(self.cards)


class FourPacks(EightPacks):
    RowStack_Class = StackWrapper(FourPacks_RowStack, mod=13)

    def createGame(self):
        EightPacks.createGame(self, max_rounds=2, width=12, playcards=18)

    def isGameWon(self):
        if self.s.talon.cards or self.s.waste.cards:
            return False
        for s in self.s.rows:
            if s.cards:
                if s.cards[0].rank != ACE:
                    return False
                if len(s.cards) != 26:
                    return False
        return True


# register the game
registerGame(GameInfo(294, CurdsAndWhey, "Curds and Whey",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(311, Dumfries, "Dumfries",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(312, Galloway, "Galloway",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(313, Robin, "Robin",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(348, Arachnida, "Arachnida",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(349, MissMuffet, "Miss Muffet",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(352, Nordic, "Nordic",
                      GI.GT_SPIDER | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(414, GermanPatience, "German Patience",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(415, BavarianPatience, "Bavarian Patience",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(480, TrustyTwelve, "Trusty Twelve",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(481, KnottyNines, "Knotty Nines",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(482, SweetSixteen, "Sweet Sixteen",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(534, Harvestman, "Harvestman",
                      GI.GT_SPIDER | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(687, Glacier, "Glacier",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(724, EightPacks, "Eight Packs",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(762, FourPacks, "Four Packs",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_MOSTLY_SKILL))


