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


# ************************************************************************
# * Talon
# ************************************************************************

class Matriarchy_Waste(WasteStack):
    def updateText(self):
        WasteStack.updateText(self)
        if self.game.s.talon._updateMaxRounds():
            self.game.s.talon.updateText()


class Matriarchy_Talon(WasteTalonStack):
    DEAL = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 11, 10, 9, 8, 7, 6, 5)

    def _updateMaxRounds(self):
        # recompute max_rounds
        old = self.max_rounds
        self.max_rounds = 11
        rows = self.game.s.rows
        for i in (0, 2, 4, 6):
            l1 =  len(rows[i+0].cards) + len(rows[i+8].cards)
            l2 =  len(rows[i+1].cards) + len(rows[i+9].cards)
            assert l1 + l2 <= 26
            if l1 + l2 == 26:
                self.max_rounds = self.max_rounds + 2
            elif l1 >= 13 or l2 >= 13:
                self.max_rounds = self.max_rounds + 1
        if self.max_rounds == 19:
            # game is won
            self.max_rounds = 18
        return old != self.max_rounds

    def canDealCards(self):
        if self._updateMaxRounds():
            self.updateText()
        if not self.cards and not self.game.s.waste.cards:
            return False
        ncards = self.DEAL[self.round-1]
        assert ncards > 0
        return len(self.cards) >= ncards or self.round < self.max_rounds

    def dealCards(self, sound=False):
        # get number of cards to deal
        ncards = self.DEAL[self.round-1]
        assert ncards > 0
        # init
        waste = self.game.s.waste
        n = 0
        update_flags = 1
        # deal
        if self.cards:
            if sound and not self.game.demo:
                self.game.playSample("dealwaste")
        while n < ncards:
            # from self to waste
            while n < ncards:
                card = self.getCard()
                if not card:
                    break
                assert not card.face_up
                self.game.flipMove(self)
                self.game.moveMove(1, self, waste, frames=3, shadow=0)
                n = n + 1
            # turn from waste to self
            if n < ncards and len(waste.cards) > 0:
                assert len(self.cards) == 0
                assert self.round < self.max_rounds or update_flags == 0
                if sound:
                    self.game.playSample("turnwaste", priority=20)
                self.game.turnStackMove(waste, self)
                if update_flags:
                    self.game.nextRoundMove(self)
                # do not update self.round anymore in this deal
                update_flags = 0
        assert self.round <= self.max_rounds
        assert n == ncards
        assert len(self.game.s.waste.cards) > 0
        # done
        return n

    def updateText(self):
        if self.game.preview > 1:
            return
        WasteTalonStack.updateText(self, update_rounds=0)
        ## t = "Round %d" % self.round
        t = _("Round %d/%d") % (self.round, self.max_rounds)
        self.texts.rounds.config(text=t)
        t = _("Deal %d") % self.DEAL[self.round-1]
        self.texts.misc.config(text=t)


# ************************************************************************
# * Rows
# ************************************************************************

class Matriarchy_UpRowStack(SS_RowStack):
    def __init__(self, x, y, game, suit):
        SS_RowStack.__init__(self, x, y, game, suit=suit,
                             base_rank=KING, mod=13, dir=1,
                             min_cards=1, max_cards=12)
        self.CARD_YOFFSET = -self.CARD_YOFFSET

    getBottomImage = Stack._getSuitBottomImage


class Matriarchy_DownRowStack(SS_RowStack):
    def __init__(self, x, y, game, suit):
        SS_RowStack.__init__(self, x, y, game, suit=suit,
                             base_rank=QUEEN, mod=13, dir=-1,
                             min_cards=1, max_cards=12)

    getBottomImage = Stack._getSuitBottomImage


# ************************************************************************
# * Matriarchy
# ************************************************************************

class Matriarchy(Game):
    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (set piles so that at least 2/3 of a card is visible with 12 cards)
        h = max(2*l.YS, (12-1)*l.YOFFSET + l.CH*2/3)
        self.setSize(10*l.XS+l.XM, h + l.YM + h)

        # create stacks
        ##center, c1, c2 = self.height / 2, h, self.height - h
        center = self.height / 2
        c1, c2 = center-l.TEXT_HEIGHT/2, center+l.TEXT_HEIGHT/2
        x, y = l.XM, c1 - l.CH
        for i in range(8):
            s.rows.append(Matriarchy_UpRowStack(x, y, self, i/2))
            x = x + l.XS
        x, y = l.XM, c2
        for i in range(8):
            s.rows.append(Matriarchy_DownRowStack(x, y, self, i/2))
            x = x + l.XS
        x, y = x + l.XS / 2, c1 - l.CH / 2 - l.CH
        tx = x + l.CW / 2
        s.waste = Matriarchy_Waste(x, y, self)
        l.createText(s.waste, "s")
        y = c2 + l.CH / 2
        s.talon = Matriarchy_Talon(x, y, self, max_rounds=VARIABLE_REDEALS)
        l.createText(s.talon, "n")
        l.createRoundText(s.talon, 'ss')
        s.talon.texts.misc = MfxCanvasText(self.canvas,
                                           tx, center, anchor="center",
                                           font=self.app.getFont("canvas_large"))

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move Queens to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 11, c.suit), 8)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(self.s.rows[8:])
        self.s.talon.dealCards()          # deal first cards to WasteStack

    def isGameWon(self):
        return len(self.s.talon.cards) == 0 and len(self.s.waste.cards) == 0

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if card1.rank + card2.rank == QUEEN + KING:
            return False
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 13 == card2.rank or (card2.rank + 1) % 13 == card1.rank))


# register the game
registerGame(GameInfo(17, Matriarchy, "Matriarchy",
                      GI.GT_2DECK_TYPE, 2, VARIABLE_REDEALS, GI.SL_BALANCED))

