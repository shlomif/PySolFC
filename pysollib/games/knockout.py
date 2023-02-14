#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.stack import \
        AbstractFoundationStack, \
        BasicRowStack, \
        DealRowTalonStack
from pysollib.util import ANY_RANK, CLUB, HEART


# ************************************************************************
# * Knockout
# * Knockout +
# ************************************************************************

class Knockout_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        game = self.game
        if game.cards_dealt == game.DEALS_BEFORE_SHUFFLE:
            if self.canDealCards():
                old_state = game.enterState(game.S_FILL)
                game.saveStateMove(2 | 16)  # for undo
                self.game.cards_dealt = 0
                game.saveStateMove(1 | 16)  # for redo
                game.leaveState(old_state)
                self.redealCards()
            else:
                return False

        old_state = game.enterState(game.S_FILL)
        game.saveStateMove(2 | 16)  # for undo
        self.game.cards_dealt += 1
        game.saveStateMove(1 | 16)  # for redo
        game.leaveState(old_state)

        return DealRowTalonStack.dealCards(self, sound)

    def canDealCards(self):
        game = self.game
        return (game.cards_dealt < game.DEALS_BEFORE_SHUFFLE
                or self.round < self.max_rounds)

    def canFlipCard(self):
        return False

    def redealCards(self):
        self.game.startDealSample()
        for r in self.game.s.rows:
            if r.cards:
                while r.cards:
                    self.game.moveMove(1, r, self, frames=4)
                    if self.cards[-1].face_up:
                        self.game.flipMove(self)
        assert self.round != self.max_rounds
        self.game.shuffleStackMove(self)
        self.game.nextRoundMove(self)


class Knockout_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        return cards[0].suit == self.cap.suit


class Knockout(Game):
    FOUNDATION_SUIT = CLUB
    DEALS_BEFORE_SHUFFLE = 5

    cards_dealt = 0

    def createGame(self, rows=3):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 4 cards are playable in default window size)
        h = max((2 * l.YS) + l.TEXT_HEIGHT, (4 * l.YOFFSET))
        self.setSize(l.XM + (1.5 + rows) * l.XS + l.XM, l.YM + h)

        # create stacks
        x0 = l.XM + (l.XS * 1.5)
        x = x0
        y = l.YM

        for i in range(rows):
            stack = BasicRowStack(x, y, self, max_cards=5,
                                  max_accept=0, max_move=1)

            s.rows.append(stack)
            x = x + l.XS
        self.setRegion(s.rows, (x0-l.XS//2, y-l.CH//2, 999999, 999999))
        x, y = l.XM, l.YM
        s.talon = Knockout_Talon(x, y, self, max_rounds=3)
        l.createText(s.talon, 'ne')
        l.createRoundText(s.talon, 's')
        y = y + l.YS + l.TEXT_HEIGHT
        s.foundations.append(Knockout_Foundation(x, y, self, max_move=0,
                                                 base_rank=ANY_RANK,
                                                 suit=self.FOUNDATION_SUIT))
        l.createText(s.foundations[0], 'se')

        # define stack-groups
        l.defaultStackGroups()

        return l

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == self.gameinfo.ncards / 4

    #
    # game overrides
    #

    def startGame(self):
        self.cards_dealt = 0
        self.startDealSample()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def fillStack(self, stack):
        if stack in self.s.rows:
            old_state = self.enterState(self.S_FILL)
            if not self.s.talon.cards[-1].face_up:
                self.s.talon.flipMove()
            self.s.talon.moveMove(1, stack, 4)
            self.leaveState(old_state)

    def _restoreGameHook(self, game):
        self.cards_dealt = game.loadinfo.cards_dealt

    def _loadGameHook(self, p):
        self.loadinfo.addattr(cards_dealt=p.load())

    def _saveGameHook(self, p):
        p.dump(self.cards_dealt)

    def getHighlightPilesStacks(self):
        return ()

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.cards_dealt = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.cards_dealt]


class KnockoutPlus(Knockout):
    DEALS_BEFORE_SHUFFLE = 8


# ************************************************************************
# * Herz zu Herz
# ************************************************************************

class HerzZuHerz(Knockout):
    FOUNDATION_SUIT = HEART

    def fillStack(self, stack):
        pass


# register the game
registerGame(GameInfo(850, Knockout, "Knockout",
                      GI.GT_1DECK_TYPE | GI.GT_STRIPPED, 1, 2, GI.SL_LUCK,
                      altnames=("Hope Deferred", "Hope"),
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12)))
registerGame(GameInfo(851, HerzZuHerz, "Herz zu Herz",
                      GI.GT_1DECK_TYPE | GI.GT_STRIPPED, 1, 2, GI.SL_LUCK,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12)))
registerGame(GameInfo(872, KnockoutPlus, "Knockout +",
                      GI.GT_1DECK_TYPE, 1, 2, GI.SL_LUCK,
                      altnames=("Abandon Hope",)))
