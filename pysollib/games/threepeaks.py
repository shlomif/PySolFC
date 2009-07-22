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

# Imports

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from golf import Golf_Waste, Golf_Hint


# ************************************************************************
# * Three Peaks Row Stack
# ************************************************************************

class ThreePeaks_TalonStack(WasteTalonStack):

    def dealCards(self, sound=False):
        game = self.game
        game.sequence = 0
        old_state = game.enterState(game.S_DEAL)
        num_cards = 0
        waste = self.waste
        if self.cards:
            if sound and not self.game.demo:
                self.game.playSample("dealwaste")
            num_cards = min(len(self.cards), self.num_deal)
            assert len(waste.cards) + num_cards <= waste.cap.max_cards
            for i in range(num_cards):
                if not self.cards[-1].face_up:
                    game.flipMove(self)
                game.moveMove(1, self, waste, frames=4, shadow=0)
                self.fillStack()
        elif waste.cards and self.round != self.max_rounds:
            if sound:
                self.game.playSample("turnwaste", priority=20)
            num_cards = len(waste.cards)
            game.turnStackMove(waste, self)
            game.nextRoundMove(self)
        game.leaveState(old_state)
        return num_cards


class ThreePeaks_RowStack(OpenStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=0, max_cards=1,
                  base_rank=ANY_RANK)
        OpenStack.__init__(self, x, y, game, **cap)

    def basicIsBlocked(self):
        r, step = self.game.s.rows, (3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9)
        i = self.id
        while i < 18:
            i = i + step[i]
            for j in range(2):
                if r[i + j].cards:
                    return True
        return False

    clickHandler = OpenStack.doubleclickHandler


# ************************************************************************
# * Three Peaks Game
# ************************************************************************

class ThreePeaks(Game):

    Waste_Class = StackWrapper(Golf_Waste, mod=13)
    Hint_Class = Golf_Hint

    SCORING = 1

    #
    # Game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        decks = self.gameinfo.decks
        # compute best XOFFSET
        xoffset = int(l.XS * 8 / self.gameinfo.ncards)
        if xoffset < l.XOFFSET:
            l.XOFFSET = xoffset

        # Set window size
        w, h = l.XM + l.XS * 10, l.YM + l.YS * 4
        self.setSize(w, h)

        # Extra settings
        self.game_score = 52
        self.hand_score = self.sequence = 0
        self.peaks = [0] * 3

        # Create rows
        x, y = l.XM + l.XS * 1.5, l.YM
        for i in range(3):
            s.rows.append(ThreePeaks_RowStack(x, y, self))
            x = x + l.XS * 3
        x, y = l.XM + l.XS, y + l.YS * .5
        for i in range(3):
            s.rows.append(ThreePeaks_RowStack(x, y, self))
            x = x + l.XS
            s.rows.append(ThreePeaks_RowStack(x, y, self))
            x = x + l.XS * 2
        x, y = l.XM + l.XS * .5, y + l.YS * .5
        for i in range(9):
            s.rows.append(ThreePeaks_RowStack(x, y, self))
            x = x + l.XS
        x, y = l.XM, y + l.YS * .5
        for i in range(10):
            s.rows.append(ThreePeaks_RowStack(x, y, self))
            x = x + l.XS

        # Create talon
        x, y = l.XM, y + l.YM + l.YS
        s.talon = ThreePeaks_TalonStack(x, y, self, num_deal=1, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = self.Waste_Class(x, y, self)
        s.waste.CARD_XOFFSET = l.XOFFSET
        s.foundations.append(s.waste)
        l.createText(s.waste, "s")

        # Create text for scores
        if self.preview <= 1:
            self.texts.info = MfxCanvasText(self.canvas,
                                            l.XM + l.XS * 3, h - l.YM,
                                            anchor="sw",
                                            font=self.app.getFont("canvas_default"))

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        self.game_score = self.game_score + self.hand_score - 52
        self.hand_score = -52
        self.peaks = [0] * 3
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:18], flip=0, frames=4)
        self.s.talon.dealRow(rows=self.s.rows[18:], flip=1, frames=4)
        self.s.talon.dealCards()

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards:
                return False
        if self.sequence:
            self.hand_score = self.hand_score + len(self.s.talon.cards) * 10
        self.updateText()
        self.sequence = 0
        return True

    def updateText(self):
        if self.preview > 1 or not self.texts.info or not self.SCORING:
            return
        t = _('Score:\011This hand:  ') + str(self.getHandScore())
        t = t + _('\011This game:  ') + str(self.game_score)
        self.texts.info.config(text=t)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if stack1 == self.s.waste or stack2 == self.s.waste:
            return ((card1.rank + 1) % 13 == card2.rank
                    or (card1.rank - 1) % 13 == card2.rank)
        return False

    def getHandScore(self):
        score, i = self.hand_score, 1
        if self.busy:
            return score
        # First count the empty peaks
        for r in self.s.rows[:3]:
            if not r.cards:
                i = i * 2
        # Now give credit for newly emptied peaks
        for r in self.s.rows[:3]:
            if not r.cards and not self.peaks[r.id]:
                score, self.peaks[r.id] = score + 5 * i, 1
        # Now give credit for the sequence length
        if self.sequence and len(self.s.waste.cards) - 1:
            score = score + i * 2 ** int((self.sequence - 1) / 4)
        self.hand_score = score
        return score

    def canUndo(self):
        return False

    def _restoreGameHook(self, game):
        self.game_score = game.loadinfo.game_score
        self.hand_score = game.loadinfo.hand_score
        self.sequence = game.loadinfo.sequence
        self.peaks = game.loadinfo.peaks

    def _loadGameHook(self, p):
        self.loadinfo.addattr(game_score=0)
        self.loadinfo.game_score = p.load()
        self.loadinfo.addattr(hand_score=0)
        self.loadinfo.hand_score = p.load()
        self.loadinfo.addattr(sequence=0)
        self.loadinfo.sequence = p.load()
        self.loadinfo.addattr(peaks=[0]*3)
        self.loadinfo.peaks = p.load()

    def _saveGameHook(self, p):
        p.dump(self.game_score)
        p.dump(self.hand_score)
        p.dump(self.sequence)
        p.dump(self.peaks)


# ************************************************************************
# * Three Peaks Game Non-scoring
# ************************************************************************

class ThreePeaksNoScore(ThreePeaks):
    SCORING = 0

    def canUndo(self):
        return True



registerGame(GameInfo(22216, ThreePeaks, "Three Peaks",
                      GI.GT_PAIRING_TYPE | GI.GT_SCORE, 1, 0, GI.SL_BALANCED,
                      altnames=("Tri Peaks",)
                      ))
registerGame(GameInfo(22231, ThreePeaksNoScore, "Three Peaks Non-scoring",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_BALANCED))


