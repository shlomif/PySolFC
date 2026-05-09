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
from pysollib.hint import DefaultHint
from pysollib.layout import Layout
from pysollib.settings import TOOLKIT
from pysollib.stack import \
    InitialDealTalonStack, \
    OpenStack, \
    SS_FoundationStack, \
    Stack
from pysollib.util import ANY_SUIT


# ************************************************************************
# * Fission
# ************************************************************************


class Fission_Reserve(OpenStack):

    def acceptsCards(self, from_stack, cards):
        return (from_stack in self.game.s.foundations and
                (len(self.cards) == 0 or
                 self.cards[0].suit == cards[0].suit))

    getBottomImage = Stack._getReserveBottomImage


class Fission_Foundation(SS_FoundationStack):

    def hasCardAbove(self):
        fs = self.game.s.foundations
        return self.id >= 7 and len(fs[self.id - 7].cards) > 0

    def hasCardBelow(self):
        fs = self.game.s.foundations
        if self.id >= len(fs) - 7:
            return False
        return len(fs[self.id + 7].cards) > 0

    def isIsolated(self):
        # No card above or below
        return (not self.hasCardAbove() and
                not self.hasCardBelow())

    def isTerminalCap(self):
        # Occupied above, no card below
        if not self.hasCardAbove():
            return False
        if self.id >= len(self.game.s.foundations) - 7:
            return True
        return not self.hasCardBelow()

    def acceptsCards(self, from_stack, cards):
        if len(self.cards) == 0:
            return False

        if not self.isIsolated():
            return False

        if self.cards[0].suit != cards[0].suit:
            return False

        return SS_FoundationStack.acceptsCards(self, from_stack, cards)

    def canMoveCards(self, cards):
        if self.hasCardBelow():
            return False

        return SS_FoundationStack.canMoveCards(self, cards)

    getBottomImage = Stack._getNoneBottomImage

    def _position(self, card):
        # Foundations overlap vertically (half YS).  Ensure lower rows
        # (higher id) continue to paint above upper rows.
        # Similar to Mahjongg.
        SS_FoundationStack._position(self, card)
        col = self.id % 7
        fnds = self.game.s.foundations
        same_column = [fnds[col + 7 * k] for k in range(7)]
        before = [s for s in same_column if s.id < self.id and s.cards]
        after = [s for s in same_column if s.id > self.id and s.cards]
        if TOOLKIT == 'tk':
            if before:
                self.group.tkraise(before[-1].group)
            if after:
                self.group.lower(after[0].group)
        elif TOOLKIT == 'kivy':
            if before:
                self.group.tkraise(before[-1].group)
            if after:
                self.group.lower(after[0].group)
        elif TOOLKIT == 'gtk':
            # gtk raise/lower not wired; re-stack the whole column
            for k in range(7):
                s = fnds[col + 7 * k]
                if s.cards:
                    s.group.tkraise()


class Fission_Hint(DefaultHint):

    SCORE_TOP_TIER_TO_FOUNDATION_MIN = 120000
    SCORE_ISOLATED_BUILD_MIN = 96000
    SCORE_TERMINAL_TO_RESERVE = 45000

    def _fission_top_movable_card(self, stack):
        if not stack.cards:
            return None
        card = stack.cards[-1]
        if not stack.canMoveCards([card]):
            return None
        return card

    def _getDropCardScore(self, score, color, r, t, ncards):
        score, color = DefaultHint._getDropCardScore(
            self, score, color, r, t, ncards)
        if r in self.game.s.reserves and t in self.game.s.foundations:
            score = max(score, self.SCORE_TOP_TIER_TO_FOUNDATION_MIN)
        elif (t in self.game.s.foundations and r in self.game.s.foundations
              and r.isTerminalCap()
              and t.isIsolated()):
            score = max(score, self.SCORE_TOP_TIER_TO_FOUNDATION_MIN)
        elif t in self.game.s.foundations:
            score = max(score, self.SCORE_ISOLATED_BUILD_MIN)
        return score, color

    def computeHints(self):
        foundations = self.game.s.foundations
        reserves = self.game.s.reserves

        # 1 - Reserve to foundation
        for r in reserves:
            card = self._fission_top_movable_card(r)
            if not card:
                continue
            pile = [card]
            for t in foundations:
                if not t.acceptsCards(r, pile):
                    continue
                score, color = self._getDropCardScore(
                    0, None, r, t, len(pile))
                self.addHint(score, len(pile), r, t, color)

        # 2 - Terminal to isolated foundation (same as reserve to foundation).
        for r in foundations:
            if not r.isTerminalCap():
                continue
            card = self._fission_top_movable_card(r)
            if not card:
                continue
            pile = [card]
            for t in foundations:
                if t is r or not t.isIsolated():
                    continue
                if not t.acceptsCards(r, pile):
                    continue
                score, color = self._getDropCardScore(
                    0, None, r, t, len(pile))
                self.addHint(score, len(pile), r, t, color)

        # 3) Isolated to isolated foundation
        for r in foundations:
            if not r.isIsolated():
                continue
            card = self._fission_top_movable_card(r)
            if not card:
                continue
            pile = [card]
            for t in foundations:
                if t is r or not t.isIsolated():
                    continue
                if not t.acceptsCards(r, pile):
                    continue
                score, color = self._getDropCardScore(
                    0, None, r, t, len(pile))
                self.addHint(score, len(pile), r, t, color)

        # 4) Terminal foundation to reserve.
        for f in foundations:
            if not f.isTerminalCap():
                continue
            card = self._fission_top_movable_card(f)
            if not card:
                continue
            pile = [card]
            rpile = f.cards[:-1]
            for t in reserves:
                if not t.acceptsCards(f, pile):
                    continue
                rr = self.ClonedStack(f, stackcards=rpile)
                if rr.acceptsCards(t, pile):
                    continue
                score = self.SCORE_TERMINAL_TO_RESERVE
                score, color = self._getMovePileScore(
                    score, None, f, t, pile, rpile)
                self.addHint(score, len(pile), f, t, color)


class Fission(Game):
    Hint_Class = Fission_Hint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        x, y = l.XM, l.YM + 2 * l.YS

        # set window
        w = max(2 * l.XS, x)
        self.setSize(l.XM + w + 7 * l.XS, l.YM + 4 * l.YS)

        # create stacks
        for i in range(7):
            for j in range(7):
                x, y = l.XM + w + j * l.XS, l.YM + i * (l.YS // 2)
                s.foundations.append(Fission_Foundation(x, y, self,
                                                        ANY_SUIT, mod=13))
        x, y = l.XM, l.YM

        # set up spots for final cards
        for i in range(4):
            x, y = l.XM, l.YM + i * l.YS
            s.reserves.append(Fission_Reserve(x, y, self, max_accept=1,
                                              max_cards=13))

        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()
        return l

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.s.talon.dealRowAvail(rows=self.s.reserves, frames=2)

    def fillStack(self, stack):
        if stack in self.s.foundations:
            movestacks = []
            checkstack = stack
            while checkstack is not None:
                checkstack = self.s.foundations[checkstack.id - 7]
                if len(checkstack.cards) > 0 and checkstack.id < stack.id:
                    movestacks.append(checkstack)
                else:
                    checkstack = None
            stacks = movestacks[:len(movestacks)//2]
            old_state = self.enterState(self.S_FILL)
            old_busy = self.busy
            self.busy = 1
            self.startDealSample()
            for src in stacks:
                self.moveMove(1, src, self.s.foundations[src.id + 7])
            self.stopSamples()
            self.busy = old_busy
            self.leaveState(old_state)

    def isGameWon(self):
        for f in self.s.foundations:
            if len(f.cards) == 0:
                continue
            if not f.isIsolated():
                return False

        return Game.isGameWon(self)


# register the game
registerGame(GameInfo(987, Fission, "Fission",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0,
                      GI.SL_MOSTLY_SKILL))
