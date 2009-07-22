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
# *
# ************************************************************************

class Memory_RowStack(OpenStack):
    def clickHandler(self, event):
        game = self.game
        if len(self.cards) != 1 or self.cards[-1].face_up:
            return 1
        if game.other_stack is None:
            game.playSample("flip", priority=5)
            self.flipMove()
            game.other_stack = self
        else:
            assert len(game.other_stack.cards) == 1 and game.other_stack.cards[-1].face_up
            c1, c2 = self.cards[-1], game.other_stack.cards[0]
            self.flipMove()
            if self.game.cardsMatch(c1, c2):
                self._dropPairMove(1, game.other_stack)
            else:
                game.playSample("flip", priority=5)
                game.score = game.score - 1
                game.updateStatus(moves=game.moves.index+1) # update moves now
                game.updateText()
                game.canvas.update_idletasks()
                game.sleep(0.5)
                game.other_stack.flipMove()
                game.canvas.update_idletasks()
                game.sleep(0.2)
                self.flipMove()
            game.other_stack = None
        self.game.finishMove()
        return 1

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        game.playSample("droppair", priority=200)
        game.closed_cards = game.closed_cards - 2
        game.score = game.score + 5

    rightclickHandler = clickHandler
    doubleclickHandler = clickHandler

    def controlclickHandler(self, event):
        return 0
    def shiftclickHandler(self, event):
        return 0


# ************************************************************************
# * Memory
# ************************************************************************

class Memory24(Game):
    Hint_Class = None

    COLUMNS = 6
    ROWS = 4
    WIN_SCORE = 40
    PERFECT_SCORE = 60       # 5 * (6*4)/2

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # game extras
        self.other_stack = None
        self.closed_cards = -1
        self.score = 0

        # create text
        x, y = l.XM, self.ROWS*l.YS
        if self.preview <= 1:
            self.texts.score = MfxCanvasText(self.canvas, x, y, anchor="sw",
                                   font=self.app.getFont("canvas_large"))
            x = self.texts.score.bbox()[1][0] + 16

        # set window
        w = max(2*l.XS, x)
        self.setSize(l.XM + w + self.COLUMNS*l.XS, l.YM + self.ROWS*l.YS)

        # create stacks
        for i in range(self.ROWS):
            for j in range(self.COLUMNS):
                x, y = l.XM + w + j*l.XS, l.YM + i*l.YS
                s.rows.append(Memory_RowStack(x, y, self,
                               max_move=0, max_accept=0, max_cards=1))
        x, y = l.XM, l.YM
        s.talon = InitialDealTalonStack(x, y, self)
        l.createText(s.talon, anchor="n", text_format="%D")
        s.internals.append(InvisibleStack(self))

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        n = self.COLUMNS * self.ROWS
        assert len(self.s.talon.cards) == n
        self.other_stack = None
        self.closed_cards = n
        self.score = 0
        self.updateText()
        n = n - self.COLUMNS
        self.s.talon.dealRow(rows=self.s.rows[:n], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[n:], flip=0)
        assert len(self.s.talon.cards) == 0

    def isGameWon(self):
        return self.closed_cards == 0 and self.score >= self.WIN_SCORE

    def getAutoStacks(self, event=None):
        return ((), (), ())

    #
    # scoring
    #

    def updateText(self):
        if self.preview > 1 or not self.texts.score:
            return
        t = ""
        if self.closed_cards:
            t = _("Points: %d") % self.score
        else:
            if self.score >= self.WIN_SCORE:
                t = _("WON\n\n")
            t = t + _("Total: %d") % self.score
        self.texts.score.config(text=t)

    def getGameScore(self):
        return self.score

    # Memory special: check score for a perfect game
    def getWinStatus(self):
        won, status, updated = Game.getWinStatus(self)
        if status == 2 and self.score < self.PERFECT_SCORE:
            return won, 1, self.U_WON
        return won, status, updated

    #
    # game extras
    #

    def cardsMatch(self, card1, card2):
        return card1.suit == card2.suit and card1.rank == card2.rank

    def canSaveGame(self):
        return 0

    def canUndo(self):
        return 0

    def _restoreGameHook(self, game):
        if game.loadinfo.other_stack_id >= 0:
            self.other_stack = self.allstacks[game.loadinfo.other_stack_id]
        else:
            self.other_stack = None
        self.closed_cards = game.loadinfo.closed_cards
        self.score = game.loadinfo.score

    def _loadGameHook(self, p):
        self.loadinfo.addattr(other_stack_id=p.load())
        self.loadinfo.addattr(closed_cards=p.load())
        self.loadinfo.addattr(score=p.load())

    def _saveGameHook(self, p):
        if self.other_stack:
            p.dump(self.other_stack.id)
        else:
            p.dump(-1)
        p.dump(self.closed_cards)
        p.dump(self.score)


class Memory30(Memory24):
    COLUMNS = 6
    ROWS = 5
    WIN_SCORE = 45
    PERFECT_SCORE = 75      # 5 * (6*5)/2


class Memory40(Memory24):
    COLUMNS = 8
    ROWS = 5
    WIN_SCORE = 50
    PERFECT_SCORE = 100     # 5 * (8*5)/2


# ************************************************************************
# * Concentration
# ************************************************************************

class Concentration_RowStack(Memory_RowStack):
    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        game.playSample("droppair", priority=200)
        game.closed_cards = game.closed_cards - 2
        game.score = game.score + 5
        #
        old_state = game.enterState(game.S_FILL)
        f = game.s.talon
        game.moveMove(n, self, f, frames=frames, shadow=shadow)
        game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        game.leaveState(old_state)


class Concentration(Memory24):
    COLUMNS = 13
    ROWS = 4
    WIN_SCORE = 50
    PERFECT_SCORE = 130     # 5 * (13*4)/2

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, card_x_space=4), self.s

        # game extras
        self.other_stack = None
        self.closed_cards = -1
        self.score = 0

        # set window
        self.setSize(l.XM + self.COLUMNS*l.XS, l.YM + (self.ROWS+1)*l.YS)

        # create stacks
        for i in range(self.ROWS):
            for j in range(self.COLUMNS):
                x, y = l.XM + j*l.XS, l.YM + i*l.YS
                s.rows.append(Concentration_RowStack(x, y, self,
                               max_move=0, max_accept=0, max_cards=1))
        x, y = l.XM + self.COLUMNS*l.XS/2, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)
        l.createText(s.talon, dx=-10, anchor="sw", text_format="%D")

        # create text
        x, y = l.XM, self.height - l.YM
        if self.preview <= 1:
            self.texts.score = MfxCanvasText(self.canvas, x, y,
                                             anchor="sw",
                                             font=self.app.getFont("canvas_large"))

        # define stack-groups
        l.defaultStackGroups()

    #
    # game extras
    #

    def cardsMatch(self, card1, card2):
        return card1.rank == card2.rank


# register the game
registerGame(GameInfo(176, Memory24, "Memory 24",
                      GI.GT_MEMORY | GI.GT_SCORE, 2, 0, GI.SL_SKILL,
                      suits=(0,2), ranks=(0,8,9,10,11,12)))
registerGame(GameInfo(219, Memory30, "Memory 30",
                      GI.GT_MEMORY | GI.GT_SCORE, 2, 0, GI.SL_SKILL,
                      suits=(0,2,3), ranks=(0,9,10,11,12)))
registerGame(GameInfo(177, Memory40, "Memory 40",
                      GI.GT_MEMORY | GI.GT_SCORE, 2, 0, GI.SL_SKILL,
                      suits=(0,2), ranks=(0,4,5,6,7,8,9,10,11,12)))
registerGame(GameInfo(178, Concentration, "Concentration",
                      GI.GT_MEMORY | GI.GT_SCORE, 1, 0, GI.SL_SKILL))

