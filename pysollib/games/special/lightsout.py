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
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.mygettext import _
from pysollib.settings import TOOLKIT
from pysollib.stack import \
        InitialDealTalonStack, \
        OpenStack
from pysollib.util import ANY_RANK

# ************************************************************************
# * Matrix Row Stack
# ************************************************************************


class LightsOut_RowStack(OpenStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1, max_cards=1,
                  base_rank=ANY_RANK)
        OpenStack.__init__(self, x, y, game, **cap)

    def canFlipCard(self):
        return 0

    def canDropCards(self, stacks):
        return (None, 0)

    def cancelDrag(self, event=None):
        if event is None:
            self._stopDrag()

    def _findCard(self, event):
        # we need to override this because the shade may be hiding
        # the tile (from Tk's stacking view)
        return len(self.cards) - 1

    def clickHandler(self, event):
        self.playFlipMove()

    def playFlipMove(self, sound=True, animation=False):
        rows = int(math.sqrt(self.game.gameinfo.ncards))

        playSpace = self.id

        if playSpace % rows != rows - 1:
            self.game.s.rows[playSpace + 1].flipMove()

        if playSpace % rows != 0:
            self.game.s.rows[playSpace - 1].flipMove()

        if playSpace + rows < rows ** 2:
            self.game.s.rows[playSpace + rows].flipMove()

        if playSpace - rows >= 0:
            self.game.s.rows[playSpace - rows].flipMove()

        return OpenStack.playFlipMove(self, sound, animation)

    def highlightMatchingCards(self, event):
        self.game.highlightNotMatching()


# Talon that can deal randomly flipped cards.
class LightsOut_Talon(InitialDealTalonStack):

    def dealToStacks(self, stacks, flip=1, reverse=0, frames=-1):
        if not self.cards or not stacks:
            return 0
        assert len(self.cards) >= len(stacks)
        old_state = self.game.enterState(self.game.S_DEAL)
        if reverse:
            stacks = list(reversed(stacks))
        for r in stacks:
            if self.getCard().face_up:
                # TODO: This probably needs a refactor.
                # For some reason, unless I do TWO flipMoves here,
                # the card will act flipped, but not show as flipped
                # when dealt.
                self.game.flipMove(self)
                self.game.flipMove(self)
            self.game.moveMove(1, self, r, frames=frames)
        self.game.leaveState(old_state)
        if TOOLKIT == 'kivy':
            self.game.top.waitAnimation()
        return len(stacks)


# ************************************************************************
# * Lights Out Game
# ************************************************************************

class LightsOut(Game):
    Hint_Class = None

    #
    # Game layout
    #

    def createGame(self):
        self.shownCards = tuple()

        l, s = Layout(self), self.s
        grid = math.sqrt(self.gameinfo.ncards)
        assert grid == int(grid)
        grid = int(grid)

        # Set window size
        w, h = l.XM * 2 + l.CW * grid, l.YM * 2 + l.CH * grid
        self.setSize(w, h)

        # Create rows
        for j in range(grid):
            x, y = l.XM, l.YM + l.CH * j
            for i in range(grid):
                s.rows.append(LightsOut_RowStack(x, y, self))
                x = x + l.CW

        # Create talon
        x, y = -2 * l.XS, 0               # invisible
        s.talon = LightsOut_Talon(x, y, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game extras
    #

    def _shuffleHook(self, cards):
        # no shuffling
        cards = self._shuffleHookMoveToTop(cards, lambda c: (1, -c.id))

        cards.reverse()
        return cards

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == self.gameinfo.ncards

        rows = int(math.sqrt(self.gameinfo.ncards))

        n = 0
        cards = self.s.talon.cards
        for card in cards:
            if self.random.randint(0, 1) == 1:
                card.face_up = not card.face_up
                if n % rows != rows - 1:
                    cards[n + 1].face_up = not cards[n + 1].face_up

                if n % rows != 0:
                    cards[n - 1].face_up = not cards[n - 1].face_up

                if n + rows < rows ** 2:
                    cards[n + rows].face_up = not cards[n + rows].face_up

                if n - rows >= 0:
                    cards[n - rows].face_up = not cards[n - rows].face_up

            n += 1

        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:self.gameinfo.ncards],
                             flip=0, frames=3)

    def isGameWon(self):
        if self.busy:
            return 0
        s = self.s.rows
        for r in s:
            if r.cards[0].face_up:
                return 0
        return 1

    def parseCard(self, card):
        if not card.face_up:
            return _("Face-down")
        return _("Face-up")

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1 == card2.rank) or
                (card1.rank - 1 == card2.rank))


# ************************************************************************
# * Register a Matrix game
# ************************************************************************

def r(id, short_name, width):
    name = short_name
    ncards = width ** 2
    gi = GameInfo(
        id, LightsOut, name,
        GI.GT_LIGHTS_OUT, 1, 0, GI.SL_SKILL,
        category=GI.GC_TRUMP_ONLY, short_name=short_name,
        suits=(), ranks=(), trumps=list(range(ncards)),
        si={"decks": 1, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "lightsout.html"
    registerGame(gi)
    return gi


r(22399, "Lights Out 3x3", 3)
r(22400, "Lights Out 4x4", 4)
r(22401, "Lights Out 5x5", 5)
r(22402, "Lights Out 6x6", 6)
r(22403, "Lights Out 7x7", 7)
r(22404, "Lights Out 8x8", 8)
r(22405, "Lights Out 9x9", 9)
r(22406, "Lights Out 10x10", 10)

del r
