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
from pysollib.stack import \
        OpenTalonStack, \
        ReserveStack, \
        Stack, \
        StackWrapper, \
        cardsFaceDown

# ************************************************************************
# * Crossword
# ************************************************************************


class Crossword_Hint(AbstractHint):

    def computeHints(self):
        game = self.game
        rows = game.s.rows
        for i in range(len(rows)):
            r = rows[i]
            if r.cards:
                continue
            if game.isValidPlay(r.id, game.s.talon.getCard().rank + 1):
                # TODO: Check a few moves ahead to get better hints.
                self.addHint(5000, 1, game.s.talon, r)


class Crossword_RowStack(ReserveStack):
    def clickHandler(self, event):
        if (not self.cards and self.game.s.talon.cards and
                self.game.isValidPlay(self.id,
                                      self.game.s.talon.getCard().rank + 1)):
            self.game.s.talon.playMoveMove(1, self)
            return 1
        return ReserveStack.clickHandler(self, event)

    rightclickHandler = clickHandler

    def acceptsCards(self, from_stack, cards):
        return not self.cards and self.game.isValidPlay(self.id,
                                                        cards[0].rank + 1)

    def canFlipCard(self):
        return False

    def closeStack(self):
        if self.cards[0].rank >= 10 and not cardsFaceDown(self.cards):
            self.flipMove()
        if len(self.game.s.talon.cards) == 4:
            self.game.s.talon.flipMove()
            for r in self.game.s.reserves:
                self.game.s.talon.moveMove(1, r)


class Crossword_FinalCard(ReserveStack):
    def rightclickHandler(self, event):
        if (self.cards):
            for r in self.game.s.rows:
                if (not r.cards and
                        self.game.isValidPlay(r.id, self.cards[0].rank + 1)):
                    self.playMoveMove(1, r)

    def acceptsCards(self, from_stack, cards):
        return (len(self.game.s.talon.cards) <= 4 and
                from_stack == self.game.s.talon)

    def canMoveCards(self, cards):
        return True

    getBottomImage = Stack._getNoneBottomImage


class Crossword(Game):
    Talon_Class = OpenTalonStack
    RowStack_Class = StackWrapper(Crossword_RowStack, max_move=0)
    FinalCards_Class = StackWrapper(Crossword_FinalCard, max_move=0)
    Hint_Class = Crossword_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        ta = "ss"
        x, y = l.XM, l.YM + 2 * l.YS

        # set window
        w = max(2 * l.XS, x)
        self.setSize(l.XM + w + 7 * l.XS + 50, l.YM + 7 * l.YS + 30)

        # create stacks
        for i in range(7):
            for j in range(7):
                x, y = l.XM + w + j * l.XS, l.YM + i * l.YS
                s.rows.append(self.RowStack_Class(x, y, self))
        x, y = l.XM, l.YM

        # set up spots for final cards
        for i in range(4):
            x, y = l.XM, w + l.YM + i * l.YS
            s.reserves.append(self.FinalCards_Class(x, y, self))
        x, y = l.XM, l.YM

        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, anchor=ta)

        # define rows to check for sequences
        r = s.rows
        self.crossword_rows = [
            r[0:7],  r[7:14], r[14:21], r[21:28],
            r[28:35], r[35:42], r[42:49],
            (r[0], r[0+7], r[0+14], r[0+21], r[0+28], r[0+35], r[0+42]),
            (r[1], r[1+7], r[1+14], r[1+21], r[1+28], r[1+35], r[1+42]),
            (r[2], r[2+7], r[2+14], r[2+21], r[2+28], r[2+35], r[2+42]),
            (r[3], r[3+7], r[3+14], r[3+21], r[3+28], r[3+35], r[3+42]),
            (r[4], r[4+7], r[4+14], r[4+21], r[4+28], r[4+35], r[4+42]),
            (r[5], r[5+7], r[5+14], r[5+21], r[5+28], r[5+35], r[5+42]),
            (r[6], r[6+7], r[6+14], r[6+21], r[6+28], r[6+35], r[6+42])
        ]
        self.crossword_rows = list(map(tuple, self.crossword_rows))

        # define stack-groups
        l.defaultStackGroups()
        return l

    def startGame(self):
        self.moveMove(1, self.s.talon, self.s.rows[24], frames=0)
        if self.s.rows[24].cards[0].rank < 10:
            self.s.rows[24].flipMove()
        self.s.talon.fillStack()

    def isGameWon(self):
        if len(self.s.talon.cards) == 0:
            for r in self.s.reserves:
                if (not r.cards):
                    return True
        return False

    def isValidPlay(self, playSpace, playRank):
        # check that there's an adjacent card
        if (not self.adjacentCard(playSpace)):
            return False

        # check the totals
        for hand in self.crossword_rows:
            count = 0  # count of the sequence
            hasEmpties = False  # Whether the sequence still has empty spaces
            lastFace = False  # Was the last card a face card?
            for s in hand:
                if s.id == playSpace:
                    rank = playRank
                elif s.cards:
                    rank = s.cards[0].rank + 1
                else:
                    rank = -1
                    hasEmpties = True
                    lastFace = False
                if (rank > -1):
                    if (rank < 11):
                        count += rank
                        lastFace = False
                    else:
                        if ((count % 2) != 0 and not hasEmpties) or lastFace:
                            return False
                        else:
                            count = 0
                            hasEmpties = False
                            lastFace = True
            if (count % 2) != 0 and not hasEmpties:
                return False
        return True

    def adjacentCard(self, playSpace):
        if (playSpace % 7 != 6 and self.s.rows[playSpace + 1].cards):
            return True

        if (playSpace % 7 != 0 and self.s.rows[playSpace - 1].cards):
            return True

        if (playSpace + 7 < 49 and self.s.rows[playSpace + 7].cards):
            return True

        if (playSpace - 7 > 0 and self.s.rows[playSpace - 7].cards):
            return True

        if (playSpace % 7 != 6 and playSpace - 6 > 0
                and self.s.rows[playSpace - 6].cards):
            return True

        if (playSpace % 7 != 0 and playSpace - 8 > 0
                and self.s.rows[playSpace - 8].cards):
            return True

        if (playSpace % 7 != 0 and playSpace + 6 < 49
                and self.s.rows[playSpace + 6].cards):
            return True

        if (playSpace % 7 != 6 and playSpace + 8 < 49
                and self.s.rows[playSpace + 8].cards):
            return True

        return False


# register the game
registerGame(GameInfo(778, Crossword, "Crossword",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
