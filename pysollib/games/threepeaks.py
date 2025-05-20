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

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.games.golf import Golf_Hint, Golf_Waste
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import OpenStack, StackWrapper, WasteTalonStack
from pysollib.util import ANY_RANK

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
    STEP = (3, 4, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9)

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=0, max_cards=1,
                  base_rank=ANY_RANK)
        OpenStack.__init__(self, x, y, game, **cap)

    def basicIsBlocked(self):
        r = self.game.s.rows
        i = self.id
        while i < 18:
            i = i + self.STEP[i]
            for j in range(2):
                if r[i + j].cards:
                    return True
        return False

    def clickHandler(self, event):
        result = OpenStack.doubleclickHandler(self, event)
        if result == 1 and not self.game.score_counted:
            self.game.sequence += 1
            self.game.computeHandScore()
            self.game.updateText()
        elif self.game.score_counted:
            self.game.score_counted = False
        return result

    def canSelect(self):
        return len(self.cards) > 0 and self.cards[-1].face_up


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
        # compute best XOFFSET
        xoffset = int(l.XS * 8 / self.gameinfo.ncards)
        l.XOFFSET = min(l.XOFFSET, xoffset)

        # Set window size
        w, h = l.XM + l.XS * 10, l.YM + l.YS * 4
        self.setSize(w, h)

        # Extra settings
        self.game_score = 0
        self.hand_score = self.sequence = 0
        self.score_counted = False
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
            self.texts.info = MfxCanvasText(
                self.canvas,
                l.XM + l.XS * 3, h - l.YM,
                anchor="sw",
                font=self.app.getFont("canvas_default"))

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self, flip=0):
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        self.game_score = self.game_score + self.hand_score
        self.hand_score = -52
        self.peaks = [0] * 3
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:18], flip=flip, frames=4)
        self.s.talon.dealRow(rows=self.s.rows[18:], flip=1, frames=4)
        self.s.talon.dealCards()

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards:
                return False
        if self.sequence:
            self.hand_score = self.hand_score + len(self.s.talon.cards) * 10
        self.computeHandScore()
        self.score_counted = True
        self.updateText()
        self.sequence = 0
        return True

    def updateText(self):
        if self.preview > 1 or not self.texts.info or not self.SCORING:
            return
        t = _('Score:\011This hand:  ') + str(self.hand_score)
        t = t + _('\011This game:  ') + str(self.game_score)
        self.texts.info.config(text=t)

    def parseGameInfo(self):
        if not self.SCORING:
            return ''
        t = _('Score:\011This hand:  ') + str(self.hand_score)
        t = t + _('\011This game:  ') + str(self.game_score)
        return t

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if stack1 == self.s.waste or stack2 == self.s.waste:
            return ((card1.rank + 1) % 13 == card2.rank or
                    (card1.rank - 1) % 13 == card2.rank)
        return False

    def computeHandScore(self):
        score, i = self.hand_score, 1
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
        # print 'getHandScore: score:', score

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

    def getStackSpeech(self, stack, cardindex):
        if stack not in self.s.rows:
            return Game.getStackSpeech(self, stack, cardindex)
        if len(stack.cards) == 0:
            return self.parseEmptyStack(stack)
        mainCard = self.parseCard(stack.cards[cardindex])
        coverCards = ()
        r, step = self.s.rows, stack.STEP
        i, mylen = stack.id, len(stack.STEP)
        if i < mylen:
            i = i + step[i]
            for j in range(2):
                if r[j + i].cards:
                    coverCards += (r[j + i],)
        if len(coverCards) > 0:
            mainCard += " - " + _("Covered by")
            for c in coverCards:
                mainCard += " - " + self.parseCard(c.cards[0])
        return mainCard


# ************************************************************************
# * Three Peaks Game Non-scoring
# ************************************************************************

class ThreePeaksNoScore(ThreePeaks):
    SCORING = 0

    def canUndo(self):
        return True


# ************************************************************************
# * Three Peaks Game Open
# ************************************************************************

class ThreePeaksOpen(ThreePeaks):
    SCORING = 0

    def canUndo(self):
        return True

    def startGame(self):
        ThreePeaks.startGame(self, flip=1)


# ************************************************************************
# * Three Peaks Game Open with scoring
# ************************************************************************

class ThreePeaksOpenScored(ThreePeaks):
    def startGame(self):
        ThreePeaks.startGame(self, flip=1)


# ************************************************************************
# * Ricochet
# ************************************************************************

class Ricochet_Talon(ThreePeaks_TalonStack):
    def dealCards(self, sound=False):
        old_state = self.game.enterState(self.game.S_FILL)
        self.game.saveStateMove(2 | 16)  # for undo
        self.game.lastStack = -1
        self.game.saveStateMove(1 | 16)  # for redo
        self.game.leaveState(old_state)
        ThreePeaks_TalonStack.dealCards(self, sound)


class Ricochet_Waste(Golf_Waste):
    def acceptsCards(self, from_stack, cards):
        for wall in self.game.walls:
            if self.game.lastStack in wall and from_stack.id in wall:
                return False
        return Golf_Waste.acceptsCards(self, from_stack, cards)


class Ricochet_RowStack(ThreePeaks_RowStack):
    STEP = (8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 12, 12, 12, 12,
            12, 12, 12, 12, 12, 12)

    def basicIsBlocked(self):
        r = self.game.s.rows
        i = self.id
        while i < 20:
            i = i + self.STEP[i]
            for j in range(2):
                d = i + j
                if d > 31:
                    d = 20
                if r[d].cards:
                    return True
        return False

    def clickHandler(self, event):
        result = OpenStack.doubleclickHandler(self, event)
        return result

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        OpenStack.moveMove(self, ncards, to_stack, frames, shadow)
        old_state = self.game.enterState(self.game.S_FILL)
        self.game.saveStateMove(2 | 16)  # for undo
        self.game.lastStack = self.id
        self.game.saveStateMove(1 | 16)  # for redo
        self.game.leaveState(old_state)


class Ricochet(Game):

    Waste_Class = StackWrapper(Ricochet_Waste, mod=13)
    Hint_Class = Golf_Hint

    #
    # Game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # compute best XOFFSET
        xoffset = int(l.XS * 8 / self.gameinfo.ncards)
        l.XOFFSET = min(l.XOFFSET, xoffset)

        # Set window size
        w, h = l.XM + l.XS * 6, l.YM + l.YS * 6
        self.setSize(w, h)
        self.lastStack = -1
        self.walls = ((0, 1, 8, 9, 10, 20, 21, 22, 23),
                      (2, 3, 11, 12, 13, 23, 24, 25, 26),
                      (4, 5, 14, 15, 16, 26, 27, 28, 29),
                      (6, 7, 17, 18, 19, 29, 30, 31, 20))

        # Create rows
        x, y = l.XM + l.XS * 2, l.YM

        s.rows.append(Ricochet_RowStack(x, y, self))
        x += l.XS
        s.rows.append(Ricochet_RowStack(x, y, self))
        x += l.XS * 2
        y += l.YS * 2
        s.rows.append(Ricochet_RowStack(x, y, self))
        y += l.YS
        s.rows.append(Ricochet_RowStack(x, y, self))
        x -= l.XS * 2
        y += l.YS * 2
        s.rows.append(Ricochet_RowStack(x, y, self))
        x -= l.XS
        s.rows.append(Ricochet_RowStack(x, y, self))
        x -= l.XS * 2
        y -= l.YS * 2
        s.rows.append(Ricochet_RowStack(x, y, self))
        y -= l.YS
        s.rows.append(Ricochet_RowStack(x, y, self))

        x, y = l.XM + l.XS * .5, l.YM + l.YS * .5
        for i in range(3):
            x += l.XS
            s.rows.append(Ricochet_RowStack(x, y, self))
        x += l.XS
        for i in range(3):
            y += l.YS
            s.rows.append(Ricochet_RowStack(x, y, self))
        y += l.YS
        for i in range(3):
            x -= l.XS
            s.rows.append(Ricochet_RowStack(x, y, self))
        x -= l.XS
        for i in range(3):
            y -= l.YS
            s.rows.append(Ricochet_RowStack(x, y, self))

        x, y = l.XM, l.YM + l.YS
        for i in range(4):
            x += l.XS
            s.rows.append(Ricochet_RowStack(x, y, self))
        for i in range(3):
            y += l.YS
            s.rows.append(Ricochet_RowStack(x, y, self))
        for i in range(3):
            x -= l.XS
            s.rows.append(Ricochet_RowStack(x, y, self))
        for i in range(2):
            y -= l.YS
            s.rows.append(Ricochet_RowStack(x, y, self))

        # Create talon
        x, y = l.XM + l.XS * 2, l.YM + l.YS * 2.5
        s.talon = Ricochet_Talon(x, y, self, num_deal=1, max_rounds=1)
        l.createText(s.talon, "s")
        x += l.XS
        s.waste = self.Waste_Class(x, y, self)
        s.foundations.append(s.waste)
        l.createText(s.waste, "s")

        # Create text for scores
        if self.preview <= 1:
            self.texts.info = MfxCanvasText(
                self.canvas,
                l.XM + l.XS * 3, h - l.YM,
                anchor="sw",
                font=self.app.getFont("canvas_default"))

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self, flip=0):
        self.lastStack = -1
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:20], flip=flip, frames=4)
        self.s.talon.dealRow(rows=self.s.rows[20:], flip=1, frames=4)
        self.s.talon.dealCards()

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards:
                return False
        return True

    def _restoreGameHook(self, game):
        self.lastStack = game.loadinfo.dval.get('lastStack')

    def _loadGameHook(self, p):
        self.loadinfo.addattr(dval=p.load())

    def _saveGameHook(self, p):
        dval = {'lastStack': self.lastStack}
        p.dump(dval)

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.lastStack = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.lastStack]


registerGame(GameInfo(22216, ThreePeaks, "Three Peaks (Scored)",
                      GI.GT_GOLF | GI.GT_SCORE, 1, 0, GI.SL_BALANCED,
                      rules_filename="threepeaks.html"))
registerGame(GameInfo(22217, ThreePeaksOpen, "Three Peaks (Open)",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_BALANCED,
                      rules_filename="threepeaks.html"))
registerGame(GameInfo(22218, ThreePeaksOpenScored, "Three Peaks (Scored/Open)",
                      GI.GT_GOLF | GI.GT_OPEN | GI.GT_SCORE, 1, 0,
                      GI.SL_BALANCED, rules_filename="threepeaks.html"))
registerGame(GameInfo(22231, ThreePeaksNoScore, "Three Peaks",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED,
                      altnames=("Tri Peaks",)))
registerGame(GameInfo(924, Ricochet, "Ricochet",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
