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
        OpenTalonStack, \
        ReserveStack, \
        StackWrapper

# ************************************************************************
# * Ishido
# ************************************************************************


class Ishido_RowStack(ReserveStack):
    def clickHandler(self, event):
        if (not self.cards and self.game.s.talon.cards and
                self.game.isValidPlay(self.id,
                                      self.game.s.talon.getCard().rank,
                                      self.game.s.talon.getCard().suit)):
            self.game.s.talon.playMoveMove(1, self)
            return 1
        return ReserveStack.clickHandler(self, event)

    rightclickHandler = clickHandler

    def acceptsCards(self, from_stack, cards):
        return not self.cards and self.game.isValidPlay(self.id,
                                                        cards[0].rank,
                                                        cards[0].suit)

    def canFlipCard(self):
        return False


class Ishido(Game):
    Talon_Class = OpenTalonStack
    RowStack_Class = StackWrapper(Ishido_RowStack, max_move=0)
    Hint_Class = None

    REQUIRE_ADJACENT = True
    STRICT_FOUR_WAYS = True

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        ta = "ss"
        x, y = l.XM, l.YM + 2 * l.YS

        w2 = max(2 * l.XS, x)
        # set window
        w, h = w2 + l.XM * 2 + l.CW * 12, l.YM * 2 + l.CH * 8
        self.setSize(w, h)

        # Create rows
        for j in range(8):
            x, y = w2 + l.XM, l.YM + l.CH * j
            for i in range(12):
                s.rows.append(self.RowStack_Class(x, y, self))
                x = x + l.CW

        s.talon = self.Talon_Class(l.XM, l.YM, self)
        l.createText(s.talon, anchor=ta)

        # define stack-groups
        l.defaultStackGroups()
        return l

    def startGame(self):
        self.moveMove(1, self.s.talon, self.s.rows[0], frames=0)
        self.s.rows[0].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[11], frames=0)
        self.s.rows[11].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[41], frames=0)
        self.s.rows[41].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[54], frames=0)
        self.s.rows[54].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[84], frames=0)
        self.s.rows[84].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[95], frames=0)
        self.s.rows[95].flipMove()
        self.s.talon.fillStack()

    def isGameWon(self):
        return len(self.s.talon.cards) == 0

    def isValidPlay(self, playSpace, playRank, playSuit):
        # check that there's an adjacent card
        adjacent = self.getAdjacent(playSpace)
        rankMatches = 0
        suitMatches = 0
        totalMatches = 0
        for i in adjacent:
            if len(i.cards) > 0:
                totalMatches += 1
                if i.cards[-1].rank == playRank:
                    rankMatches += 1
                if i.cards[-1].suit == playSuit:
                    suitMatches += 1

                if i.cards[-1].suit != playSuit and \
                        i.cards[-1].rank != playRank:
                    return False

        if self.REQUIRE_ADJACENT and totalMatches == 0:
            return False

        if self.STRICT_FOUR_WAYS:
            if totalMatches > 1 and (rankMatches == 0 or suitMatches == 0):
                return False
            if totalMatches == 4 and (rankMatches < 2 or suitMatches < 2):
                return False

        return True

    def getAdjacent(self, playSpace):
        adjacentRows = []
        if playSpace % 12 != 11:
            adjacentRows.append(self.s.rows[playSpace + 1])

        if playSpace % 12 != 0:
            adjacentRows.append(self.s.rows[playSpace - 1])

        if playSpace + 12 < 96:
            adjacentRows.append(self.s.rows[playSpace + 12])

        if playSpace - 12 > -1:
            adjacentRows.append(self.s.rows[playSpace - 12])

        return adjacentRows


class IshidoRelaxed(Ishido):
    STRICT_FOUR_WAYS = False


class FreeIshido(Ishido):
    REQUIRE_ADJACENT = False


class FreeIshidoRelaxed(Ishido):
    STRICT_FOUR_WAYS = False
    REQUIRE_ADJACENT = False


def r(id, gameclass, name, decks, redeals, skill_level):
    game_type = GI.GT_ISHIDO
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  ranks=list(range(6)), suits=list(range(6)),
                  category=GI.GC_ISHIDO)
    registerGame(gi)
    return gi


r(18000, Ishido, 'Ishido', 2, 0, GI.SL_MOSTLY_SKILL)
r(18001, IshidoRelaxed, 'Ishido Relaxed', 2, 0, GI.SL_MOSTLY_SKILL)
r(18002, FreeIshido, 'Free Ishido', 2, 0, GI.SL_MOSTLY_SKILL)
r(18003, FreeIshidoRelaxed, 'Free Ishido Relaxed', 2, 0, GI.SL_MOSTLY_SKILL)
