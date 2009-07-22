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
from pysollib.pysoltk import MfxCanvasText, get_text_width

# ************************************************************************
# *
# ************************************************************************

class Calculation_Hint(DefaultHint):
    # FIXME: demo logic is a complete nonsense
    def _getMoveWasteScore(self, score, color, r, t, pile, rpile):
        assert r is self.game.s.waste and len(pile) == 1
        score = 30000
        if len(t.cards) == 0:
            score = score - (KING - r.cards[0].rank) * 1000
        elif t.cards[-1].rank < r.cards[0].rank:
            score = 10000 + t.cards[-1].rank - len(t.cards)
        elif t.cards[-1].rank == r.cards[0].rank:
            score = 20000
        else:
            score = score - (t.cards[-1].rank - r.cards[0].rank) * 1000
        return score, color


# ************************************************************************
# *
# ************************************************************************

class BetsyRoss_Foundation(RK_FoundationStack):
    def updateText(self, update_empty=True):
        if self.game.preview > 1:
            return
        if self.texts.misc:
            if len(self.cards) == 0:
                if update_empty:
                    rank = self.cap.base_rank
                    self.texts.misc.config(text=RANKS[rank])
                else:
                    self.texts.misc.config(text="")
            elif len(self.cards) == self.cap.max_cards:
                self.texts.misc.config(text="")
            else:
                rank = (self.cards[-1].rank + self.cap.dir) % self.cap.mod
                self.texts.misc.config(text=RANKS[rank])


class Calculation_Foundation(BetsyRoss_Foundation):
    getBottomImage = Stack._getLetterImage


class Calculation_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts any one card from the Waste pile
        return from_stack is self.game.s.waste and len(cards) == 1

    getBottomImage = Stack._getReserveBottomImage

    def getHelp(self):
        return _('Tableau. Build regardless of rank and suit.')


# ************************************************************************
# * Calculation
# ************************************************************************

class Calculation(Game):
    Hint_Class = Calculation_Hint
    Foundation_Class = Calculation_Foundation
    RowStack_Class = StackWrapper(Calculation_RowStack, max_move=1, max_accept=1)

    #
    # game layout
    #

    def _getHelpText(self):
        help = (_('''\
1: 2 3 4 5 6 7 8 9 T J Q K
2: 4 6 8 T Q A 3 5 7 9 J K
3: 6 9 Q 2 5 8 J A 4 7 T K
4: 8 Q 3 7 J 2 6 T A 5 9 K'''))
        # calculate text_width
        lines = help.split('\n')
        lines.sort(lambda a, b: cmp(len(a), len(b)))
        max_line = lines[-1]
        text_width = get_text_width(max_line,
                                    font=self.app.getFont("canvas_fixed"))
        return help, text_width

    def createGame(self):

        # create layout
        l, s = Layout(self, TEXT_HEIGHT=40), self.s
        help, text_width = self._getHelpText()
        text_width += 2*l.XM

        # set window
        w = l.XM+5.5*l.XS+text_width
        h = max(2*l.YS, 20*l.YOFFSET)
        self.setSize(w, l.YM + l.YS + l.TEXT_HEIGHT + h)

        # create stacks
        x0 = l.XM + l.XS * 3 / 2
        x, y = x0, l.YM
        for i in range(4):
            stack = self.Foundation_Class(x, y, self,
                                          mod=13, dir=i+1, base_rank=i)
            s.foundations.append(stack)
            tx, ty, ta, tf = l.getTextAttr(stack, "s")
            font = self.app.getFont("canvas_default")
            stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)
            x = x + l.XS
        self.texts.help = MfxCanvasText(self.canvas, x + l.XM, y + l.CH / 2, text=help,
                                        anchor="w", font=self.app.getFont("canvas_fixed"))
        x = x0
        y = l.YM + l.YS + l.TEXT_HEIGHT
        for i in range(4):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        self.setRegion(s.rows, (-999, y-l.CH/2, 999999, 999999))
        x = l.XM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "n")
        y = y + l.YS
        s.waste = WasteStack(x, y, self, max_cards=1)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # prepare first cards
        topcards = [ None ] * 4
        for c in cards[:]:
            if c.rank <= 3 and topcards[c.rank] is None:
                topcards[c.rank] = c
                cards.remove(c)
        topcards.reverse()
        return cards + topcards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getHighlightPilesStacks(self):
        return ()


# ************************************************************************
# * Hopscotch
# ************************************************************************

class Hopscotch(Calculation):
    def _shuffleHook(self, cards):
        # prepare first cards
        topcards = [ None ] * 4
        for c in cards[:]:
            if c.suit == 0 and c.rank <= 3 and topcards[c.rank] is None:
                topcards[c.rank] = c
                cards.remove(c)
        topcards.reverse()
        return cards + topcards


# ************************************************************************
# * Betsy Ross
# ************************************************************************

class BetsyRoss(Calculation):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        help, text_width = self._getHelpText()
        text_width += 2*l.XM

        # set window
        self.setSize(5.5*l.XS+l.XM+text_width, l.YM+3*l.YS+l.TEXT_HEIGHT)

        # create stacks
        x0 = l.XM + l.XS * 3 / 2
        x, y = x0, l.YM
        for i in range(4):
            stack = BetsyRoss_Foundation(x, y, self, base_rank=i,
                                         max_cards=1, max_move=0, max_accept=0)
            s.foundations.append(stack)
            x += l.XS
        x = x0
        y = l.YM + l.YS
        for i in range(4):
            stack = BetsyRoss_Foundation(x, y, self, base_rank=2*i+1,
                                         mod=13, dir=i+1,
                                         max_cards=12, max_move=0)
            tx, ty, ta, tf = l.getTextAttr(stack, "s")
            font = self.app.getFont("canvas_default")
            stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)
            s.foundations.append(stack)
            x += l.XS
        self.texts.help = MfxCanvasText(self.canvas, x + l.XM, y + l.CH / 2,
                                        text=help, anchor="w",
                                        font=self.app.getFont("canvas_fixed"))
        x = l.XM
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "n")
        l.createRoundText(s.talon, 'nnn')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # prepare first cards
        topcards = [ None ] * 8
        for c in cards[:]:
            if c.rank <= 3 and topcards[c.rank] is None:
                topcards[c.rank] = c
                cards.remove(c)
            elif c.rank in (1, 3, 5, 7):
                i = 4 + (c.rank - 1) / 2
                if topcards[i] is None:
                    topcards[i] = c
                    cards.remove(c)
        topcards.reverse()
        return cards + topcards


# ************************************************************************
# * One234
# ************************************************************************

class One234_Foundation(BetsyRoss_Foundation):
    def canMoveCards(self, cards):
        if not BetsyRoss_Foundation.canMoveCards(self, cards):
            return False
        return len(self.cards) > 1
    def updateText(self):
        BetsyRoss_Foundation.updateText(self, update_empty=False)


class One234_RowStack(BasicRowStack):
    ##clickHandler = BasicRowStack.doubleclickHandler
    pass


class One234(Calculation):
    Foundation_Class = One234_Foundation
    RowStack_Class = StackWrapper(One234_RowStack, max_move=1, max_accept=0)

    def createGame(self):
        # create layout
        l, s = Layout(self, TEXT_HEIGHT=40), self.s
        help, text_width = self._getHelpText()
        text_width += 2*l.XM

        # set window
        # (piles up to 20 cards are playable in default window size)
        w = l.XM+max(4*l.XS+text_width, 8*l.XS)
        h = l.YM+2*l.YS+5*l.YOFFSET+l.TEXT_HEIGHT+l.YS
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            stack = self.Foundation_Class(x, y, self,
                                          mod=13, dir=i+1, base_rank=i)
            s.foundations.append(stack)
            tx, ty, ta, tf = l.getTextAttr(stack, "s")
            font = self.app.getFont("canvas_default")
            stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)
            x = x + l.XS
        self.texts.help = MfxCanvasText(self.canvas, x + l.XM, y + l.CH / 2, text=help,
                                        anchor="w", font=self.app.getFont("canvas_fixed"))
        x, y = l.XM, l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(8):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS

        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        return cards

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)


# ************************************************************************
# * Senior Wrangler
# ************************************************************************

class SeniorWrangler_Talon(DealRowTalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds:
            return False
        return not self.game.isGameWon()

    def dealCards(self, sound=False):
        num_cards = 0
        r = self.game.s.rows[self.round-1]
        if not r.cards:
            self.game.nextRoundMove(self)
            return 1
        if sound:
            self.game.startDealSample()
        old_state = self.game.enterState(self.game.S_DEAL)
        while r.cards:
            self.game.flipMove(r)
            self.game.moveMove(1, r, self, frames=4, shadow=0)
        self.dealRowAvail(rows=self.game.s.rows[self.round-1:], sound=False)
        while self.cards:
            num_cards += self.dealRowAvail(sound=False)
        self.game.nextRoundMove(self)
        self.game.leaveState(old_state)
        if sound:
            self.game.stopSamples()
        return num_cards

class SeniorWrangler_RowStack(BasicRowStack):
    #clickHandler = BasicRowStack.doubleclickHandler
    pass


class SeniorWrangler(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9.5*l.XS, l.YM+3*l.YS)

        x, y = l.XM+1.5*l.XS, l.YM
        for i in range(8):
            stack = BetsyRoss_Foundation(x, y, self, base_rank=i,
                                         mod=13, dir=i+1, max_move=0)
            tx, ty, ta, tf = l.getTextAttr(stack, "s")
            font = self.app.getFont("canvas_default")
            stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)
            s.foundations.append(stack)
            x = x + l.XS
        x, y = l.XM+1.5*l.XS, l.YM+2*l.YS
        for i in range(8):
            stack = SeniorWrangler_RowStack(x, y, self, max_accept=0)
            s.rows.append(stack)
            stack.CARD_YOFFSET = 0
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        s.talon = SeniorWrangler_Talon(x, y, self, max_rounds=9)
        l.createRoundText(s.talon, 'nn')

        # define stack-groups
        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        top = []
        ranks = []
        for c in cards[:]:
            if c.rank in range(8) and c.rank not in ranks:
                ranks.append(c.rank)
                cards.remove(c)
                top.append(c)
        top.sort(lambda a, b: cmp(b.rank, a.rank))
        return cards+top


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations[:8], frames=0)
        for i in range(11):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * S Patience
# ************************************************************************

class SPatience(Game):
    Hint_Class = Calculation_Hint

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+7.5*l.XS, l.YM+3.8*l.YS)

        x0, y0 = l.XM, l.YM
        for xx, yy in ((4, 0.4),
                       (3, 0.2),
                       (2, 0.0),
                       (1, 0.2),
                       (0, 0.7),
                       (1, 1.2),
                       (2, 1.4),
                       (3, 1.6),
                       (4, 2.0),
                       (3, 2.6),
                       (2, 2.8),
                       (1, 2.6),
                       (0, 2.4),
                       ):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            s.foundations.append(RK_FoundationStack(x, y, self, suit=ANY_SUIT,
                                 max_cards=8, mod=13, max_move=0))

        x, y = l.XM+5.5*l.XS, l.YM+2*l.YS
        for i in (0,1):
            stack = Calculation_RowStack(x, y, self, max_move=1, max_accept=1)
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)
            l.createText(stack, 's')
            x += l.XS
        x, y = l.XM+5.5*l.XS, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'nw')
        x += l.XS
        s.waste = WasteStack(x, y, self, max_cards=1)

        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        top = []
        ranks = []
        for c in cards[:]:
            if c.rank not in ranks:
                ranks.append(c.rank)
                cards.remove(c)
                top.append(c)
        top.sort(lambda a, b: cmp(b.rank, a.rank))
        return cards+top[7:]+top[:7]

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()



# register the game
registerGame(GameInfo(256, Calculation, "Calculation",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Progression",) ))
registerGame(GameInfo(94, Hopscotch, "Hopscotch",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(134, BetsyRoss, "Betsy Ross",
                      GI.GT_1DECK_TYPE, 1, 2, GI.SL_MOSTLY_LUCK,
                      altnames=("Fairest", "Four Kings", "Musical Patience",
                                "Quadruple Alliance", "Plus Belle") ))
registerGame(GameInfo(550, One234, "One234",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(653, SeniorWrangler, "Senior Wrangler",
                      GI.GT_2DECK_TYPE, 2, 8, GI.SL_BALANCED))
registerGame(GameInfo(704, SPatience, "S Patience",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))

