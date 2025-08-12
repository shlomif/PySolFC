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
from pysollib.hint import AbstractHint
from pysollib.layout import Layout
from pysollib.mygettext import _
from pysollib.stack import \
        AbstractFoundationStack, \
        InitialDealTalonStack, \
        InvisibleStack, \
        ReserveStack
from pysollib.util import ANY_SUIT


class Pegged_Hint(AbstractHint):
    # FIXME: no intelligence whatsoever is implemented here
    def computeHints(self):
        game = self.game
        # get free stacks
        stacks = [r for r in game.s.rows if not r.cards]
        #
        for t in stacks:
            for dx, dy in game.STEPS:
                r = game.map.get((t.pos[0] + dx, t.pos[1] + dy))
                if not r or not r.cards or not t.acceptsCards(r, r.cards):
                    continue
                # braindead scoring...
                score = 10000 + game.app.miscrandom.randint(0, 9999)
                self.addHint(score, 1, r, t)


# ************************************************************************
# *
# ************************************************************************

class Pegged_RowStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return 0
        return self._getMiddleStack(from_stack) is not None

    def canDropCards(self, stacks):
        return (None, 0)

    def clickHandler(self, event):
        game = self.game
        for row in game.s.rows:
            if len(row.cards) < 1:
                return ReserveStack.clickHandler(self, event)
        self.game.emptyStack = self.id
        self.game.playSample("drop", priority=200)
        self.playMoveMove(1, self.game.s.foundations[0])
        return True

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if isinstance(to_stack, Pegged_Foundation):
            return ReserveStack.moveMove(self, ncards, to_stack, frames=frames,
                                         shadow=shadow)

        other_stack = to_stack._getMiddleStack(self)
        old_state = self.game.enterState(self.game.S_FILL)
        f = self.game.s.foundations[0]
        self.game.moveMove(ncards, self, to_stack, frames=0)
        self.game.playSample("drop", priority=200)
        self.game.moveMove(ncards, other_stack, f, frames=-1, shadow=shadow)
        self.game.leaveState(old_state)
        self.fillStack()
        other_stack.fillStack()

    def _getMiddleStack(self, from_stack):
        dx, dy = from_stack.pos[0] - self.pos[0], \
            from_stack.pos[1] - self.pos[1]
        if not self.game.STEP_MAP.get((dx, dy)):
            return None
        s = self.game.map.get((self.pos[0] + dx//2, self.pos[1] + dy//2))
        if not s or not s.cards:
            return None
        return s

    def copyModel(self, clone):
        ReserveStack.copyModel(self, clone)
        clone.pos = self.pos

    def highlightMatchingCards(self, event):
        self.game.highlightNotMatching()


class Pegged_Foundation(AbstractFoundationStack):

    def acceptsCards(self, from_stack, cards):
        game = self.game
        for row in game.s.rows:
            if len(row.cards) < 1:
                return False
        return True


# ************************************************************************
# * Pegged
# ************************************************************************

class Pegged(Game):
    Hint_Class = Pegged_Hint

    STEPS = ((-4, 0), (4, 0), (0, -4), (0, 4))
    ROWS = (3, 5, 7, 7, 7, 5, 3)
    EMPTY_STACK_ID = -1

    GAME_VERSION = 2

    #
    # game layout
    #

    def createGame(self):
        self.emptyStack = self.EMPTY_STACK_ID
        # create layout
        l, s = Layout(self), self.s

        # set window
        m = max(self.ROWS)
        self.setSize(l.XM + m * l.XS, l.YM + len(self.ROWS) * l.YS)

        # game extras 1)
        self.map = {}

        # create stacks
        for i, r in enumerate(self.ROWS):
            for j in range(r):
                d = m - r + 2 * j
                x, y = l.XM + d * l.XS // 2, l.YM + i * l.YS
                stack = Pegged_RowStack(x, y, self)
                stack.pos = (d, 2 * i)
                # print stack.id, stack.pos
                s.rows.append(stack)
                self.map[stack.pos] = stack
        x, y = self.getInvisibleCoords()
        s.foundations.append(
            Pegged_Foundation(
                x, y, self, ANY_SUIT, max_move=0,
                max_cards=self.gameinfo.ncards))
        l.createText(s.foundations[0], "s")
        y = self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)
        s.internals.append(InvisibleStack(self))

        # game extras 2)
        self.STEP_MAP = {}
        for step in self.STEPS:
            self.STEP_MAP[step] = 1
        if self.EMPTY_STACK_ID < 0:
            self.EMPTY_STACK_ID = len(s.rows) // 2

        # Define stack groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def shuffle(self):
        for card in reversed(self.cards):
            self.s.talon.addCard(card, update=0)
            card.showBack(unhide=0)

    def startGame(self):
        self.startDealSample()
        rows = list(self.s.rows[:])
        if self.app.opt.pegged_auto_remove:
            rows.remove(rows[self.EMPTY_STACK_ID])
        self.s.talon.dealRow(rows=rows, frames=4)
        if len(self.s.talon.cards) > 0:
            self.moveMove(len(self.s.talon.cards), self.s.talon,
                          self.s.foundations[0], frames=0)
        assert len(self.s.talon.cards) == 0

    def isGameWon(self):
        c = 0
        for s in self.s.foundations:
            c = c + len(s.cards)
        return c + 1 == self.gameinfo.si.ncards

    def getAutoStacks(self, event=None):
        return ((), (), ())

    def _restoreGameHook(self, game):
        self.emptyStack = game.loadinfo.dval.get('EmptyStack')

    def _loadGameHook(self, p):
        self.loadinfo.addattr(dval=p.load())

    def _saveGameHook(self, p):
        dval = {'EmptyStack': self.emptyStack}
        p.dump(dval)

    # Pegged special: check for a perfect game
    def getWinStatus(self):
        won, status, updated = Game.getWinStatus(self)
        if status == 2:
            stacks = [r for r in self.s.rows if r.cards]
            assert len(stacks) == 1
            if stacks[0].id != self.emptyStack:
                # not perfect
                return won, 1, self.U_WON
        return won, status, updated

    # Pegged special: highlight all moveable cards
    def getHighlightPilesStacks(self):
        rows = []
        for r in self.s.rows:
            if not r.cards:
                continue
            rx, ry = r.pos
            for dx, dy in self.STEPS:
                s = self.map.get((rx + dx, ry + dy))
                if s and not s.cards:
                    m = self.map.get((rx + dx//2, ry + dy//2))
                    if m and m.cards:
                        rows.append(r)
        return ((rows, 1),)

    def parseCard(self, card):
        return _("Card")


class PeggedCross1(Pegged):
    ROWS = (3, 3, 7, 7, 7, 3, 3)


class PeggedCross2(Pegged):
    ROWS = (3, 3, 3, 9, 9, 9, 3, 3, 3)


# The Continental Diamond layout - this one is commented
# because it's not known to  be possible to have a perfect
# game, though it is winnable.
# class PeggedDiamond(Pegged):
#     EMPTY_STACK_ID = 6
#     ROWS = (1, 3, 5, 7, 9, 7, 5, 3, 1)


class PeggedDiamond(Pegged):
    EMPTY_STACK_ID = 12
    ROWS = (1, 3, 5, 7, 7, 5, 3, 1)


class Pegged6x6(Pegged):
    EMPTY_STACK_ID = 14
    ROWS = (6, 6, 6, 6, 6, 6)


class Pegged7x7(Pegged):
    ROWS = (7, 7, 7, 7, 7, 7, 7)


# ************************************************************************
# * Pegged Triangle
# ************************************************************************

class PeggedTriangle1(Pegged):
    STEPS = ((-2, -4), (-2, 4), (-4, 0), (4, 0), (2, -4), (2, 4))
    ROWS = (1, 2, 3, 4, 5)
    EMPTY_STACK_ID = 4


class PeggedTriangle2(PeggedTriangle1):
    ROWS = (1, 2, 3, 4, 5, 6)


class PeggedStar(PeggedTriangle1):
    EMPTY_STACK_ID = 0
    ROWS = (1, 4, 3, 4, 1)


class PeggedHexagon(PeggedTriangle1):
    EMPTY_STACK_ID = 30
    ROWS = (5, 6, 7, 8, 9, 8, 7, 6, 5)


# ************************************************************************
# * register the games
# ************************************************************************

def r(id, gameclass, name):
    ncards = 0
    for n in gameclass.ROWS:
        ncards += n
    gi = GameInfo(id, gameclass, name,
                  GI.GT_PEGGED, 1, 0, GI.SL_SKILL,
                  category=GI.GC_TRUMP_ONLY,
                  suits=(), ranks=(), trumps=list(range(ncards)),
                  si={"decks": 1, "ncards": ncards},
                  rules_filename="pegged.html")
    registerGame(gi)
    return gi


r(180, Pegged, "Pegged Octagon")
r(181, PeggedCross1, "Pegged Cross 1")
r(182, PeggedCross2, "Pegged Cross 2")
r(183, Pegged6x6, "Pegged 6x6")
r(184, Pegged7x7, "Pegged 7x7")
r(210, PeggedTriangle1, "Pegged Triangle 1")
r(211, PeggedTriangle2, "Pegged Triangle 2")
r(839, PeggedDiamond, "Pegged Diamond")
r(840, PeggedStar, "Pegged Star")
r(945, PeggedHexagon, "Pegged Hexagon")
del r
