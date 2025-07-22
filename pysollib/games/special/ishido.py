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
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        OpenTalonStack, \
        ReserveStack, \
        StackWrapper

# ************************************************************************
# * Ishido
# ************************************************************************


class Ishido_Hint(AbstractHint):
    # FIXME: no intelligence whatsoever is implemented here

    def computeHints(self):
        game = self.game
        for r in game.s.rows:
            if (not r.cards and
                    game.isValidPlay(r.id,
                                     game.s.talon.getCard().rank,
                                     game.s.talon.getCard().suit)):
                adjacentPiles = game.getAdjacent(r.id)
                adjacent = 0
                for pile in adjacentPiles:
                    if len(pile.cards) > 0:
                        adjacent += 1
                self.addHint(100 * adjacent, 1, game.s.talon, r)


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


class Ishido_Talon(OpenTalonStack):

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if self.game.SCORING:
            game = self.game
            old_state = game.enterState(game.S_FILL)
            game.saveStateMove(2 | 16)  # for undo
            game.updateScore(to_stack.id)
            game.saveStateMove(1 | 16)  # for redo
            game.leaveState(old_state)
        OpenTalonStack.moveMove(self, ncards, to_stack, frames=frames,
                                shadow=shadow)

    def highlightMatchingCards(self, event):
        if len(self.cards) < 1:
            return 0
        info = []
        found = 0
        col_1 = self.game.app.opt.colors['cards_1']
        col_2 = self.game.app.opt.colors['cards_2']
        for s in self.game.s.rows:
            if len(s.cards) > 0:
                continue
            if self.game.isValidPlay(s.id, self.cards[-1].rank,
                                     self.cards[-1].suit):
                found = 1
                info.append((s, col_1))
        if found:
            if info:
                self.game.stats.highlight_cards += 1
            info.append((self, col_2))
            return self.game._highlightEmptyStack(
                info, self.game.app.opt.timeouts['highlight_cards'])
        if not self.basicIsBlocked():
            self.game.highlightNotMatching()
        return 0


class Ishido(Game):
    Talon_Class = Ishido_Talon
    RowStack_Class = StackWrapper(Ishido_RowStack, max_move=0)
    Hint_Class = Ishido_Hint

    REQUIRE_ADJACENT = True
    STRICT_FOUR_WAYS = True
    SCORING = False

    COLS = 12
    ROWS = 8

    COLORS = (_("Blue"), _("Red"), _("Yellow"), _("Green"),
              _("Purple"), _("Orange"))
    SHAPES = (_("Square"), _("Circle"), _("Triangle"), _("Diamond"),
              _("Pentagon"), _("Star"))

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        self.score = 0
        self.fourways = 0

        ta = "ss"
        x, y = l.XM, l.YM + 2 * l.YS

        w2 = max(2 * l.XS, x)
        # set window
        w, h = w2 + l.XM * 2 + l.CW * self.COLS, l.YM * 2 + l.CH * self.ROWS
        self.setSize(w, h)

        # Create rows
        for j in range(self.ROWS):
            x, y = w2 + l.XM, l.YM + l.CH * j
            for i in range(self.COLS):
                s.rows.append(self.RowStack_Class(x, y, self))
                x = x + l.CW

        s.talon = self.Talon_Class(l.XM, l.YM, self)
        l.createText(s.talon, anchor=ta)

        # create text
        x, y = l.XM, h - l.YM
        if self.preview <= 1:
            self.texts.score = MfxCanvasText(
                self.canvas, x, y, anchor="sw",
                font=self.app.getFont("canvas_large"))
            x = self.texts.score.bbox()[1][0] + 16

        # define stack-groups
        l.defaultStackGroups()
        return l

    def startGame(self):
        self.score = 0
        self.fourways = 0
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

    def _shuffleHook(self, cards):
        # prepare first cards
        symbols = []
        colors = []
        topcards = []
        for c in cards[:]:
            if c.suit not in colors and c.rank not in symbols:
                topcards.append(c)
                cards.remove(c)
                symbols.append(c.rank)
                colors.append(c.suit)
                if len(colors) >= 6 or len(symbols) >= 6:
                    break
        return cards + topcards

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

    def updateScore(self, playSpace):
        if len(self.s.talon.cards) == 3:
            self.score += 100
        elif len(self.s.talon.cards) == 2:
            self.score += 400
        elif len(self.s.talon.cards) == 1:
            self.score += 500

        if playSpace % 12 in (0, 11):
            return 0

        if playSpace + 12 > 96 or playSpace - 12 < -1:
            return 0

        adjacentPiles = self.getAdjacent(playSpace)
        adjacent = 0
        for pile in adjacentPiles:
            if len(pile.cards) > 0:
                adjacent += 1
        if adjacent >= 4:
            movescore = 8 + 25
        elif adjacent == 3:
            movescore = 4
        else:
            movescore = adjacent

        movescore *= (1 + self.fourways)

        if adjacent >= 4:
            self.fourways += 1

        self.score += movescore

    def updateText(self):
        if self.preview > 1 or not self.texts.score or not self.SCORING:
            return
        t = _("Points: %d") % self.score
        self.texts.score.config(text=t)

    def parseGameInfo(self):
        if not self.SCORING:
            return ''
        return _("Points: %d") % self.getGameScore()

    def parseStackInfo(self, stack):
        if stack not in self.s.rows:
            return ""
        row = (stack.id // self.COLS) + 1
        column = (stack.id % self.COLS) + 1
        return _("Row: %d, Column: %d") % (row, column)

    def getGameScore(self):
        return self.score

    def _restoreGameHook(self, game):
        self.score = game.loadinfo.score
        self.fourways = game.loadinfo.fourways

    def _loadGameHook(self, p):
        self.loadinfo.addattr(score=p.load())
        self.loadinfo.addattr(fourways=p.load())

    def _saveGameHook(self, p):
        p.dump(self.score)
        p.dump(self.fourways)

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.score = state[0]
        self.fourways = state[1]

    def getState(self):
        # save vars (for undo/redo)
        return [self.score, self.fourways]

    def getAdjacent(self, playSpace):
        adjacentRows = []
        if playSpace % self.COLS != self.COLS - 1:
            adjacentRows.append(self.s.rows[playSpace + 1])

        if playSpace % self.COLS != 0:
            adjacentRows.append(self.s.rows[playSpace - 1])

        if playSpace + self.COLS < (self.COLS * self.ROWS):
            adjacentRows.append(self.s.rows[playSpace + self.COLS])

        if playSpace - self.COLS > -1:
            adjacentRows.append(self.s.rows[playSpace - self.COLS])

        return adjacentRows

    def parseCard(self, card):
        if not card.face_up:
            return _("Face-down")
        color = self.COLORS[card.suit]
        shape = self.SHAPES[card.rank]
        return color + " - " + shape


class IshidoRelaxed(Ishido):
    STRICT_FOUR_WAYS = False


class FreeIshido(Ishido):
    REQUIRE_ADJACENT = False


class FreeIshidoRelaxed(Ishido):
    STRICT_FOUR_WAYS = False
    REQUIRE_ADJACENT = False


class IshidoScored(Ishido):
    SCORING = True


class LittleIshido(Ishido):
    ROWS = 6
    COLS = 8

    def startGame(self):
        self.score = 0
        self.fourways = 0
        self.moveMove(1, self.s.talon, self.s.rows[0], frames=0)
        self.s.rows[0].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[7], frames=0)
        self.s.rows[7].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[40], frames=0)
        self.s.rows[40].flipMove()
        self.moveMove(1, self.s.talon, self.s.rows[47], frames=0)
        self.s.rows[47].flipMove()
        self.s.talon.fillStack()

    def _shuffleHook(self, cards):
        # prepare first cards
        symbols = []
        colors = []
        topcards = []
        for c in cards[:]:
            if c.suit not in colors and c.rank not in symbols:
                topcards.append(c)
                cards.remove(c)
                symbols.append(c.rank)
                colors.append(c.suit)
                if len(colors) >= 4 or len(symbols) >= 4:
                    break
        return cards + topcards

class LittleIshidoRelaxed(LittleIshido):
    STRICT_FOUR_WAYS = False


def r(id, gameclass, name, decks, redeals, skill_level,
        game_type=GI.GT_ISHIDO, colors=6):
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                  ranks=list(range(colors)), suits=list(range(colors)),
                  category=GI.GC_ISHIDO)
    registerGame(gi)
    return gi


r(18000, Ishido, 'Ishido', 2, 0, GI.SL_MOSTLY_SKILL)
r(18001, IshidoRelaxed, 'Ishido Relaxed', 2, 0, GI.SL_MOSTLY_SKILL)
r(18002, FreeIshido, 'Free Ishido', 2, 0, GI.SL_MOSTLY_SKILL)
r(18003, FreeIshidoRelaxed, 'Free Ishido Relaxed', 2, 0, GI.SL_MOSTLY_SKILL)
r(18004, IshidoScored, 'Ishido Scored', 2, 0, GI.SL_MOSTLY_SKILL,
  game_type=GI.GT_ISHIDO | GI.GT_SCORE)
r(18005, LittleIshido, 'Little Ishido', 2, 0, GI.SL_MOSTLY_SKILL, colors=4)
r(18006, LittleIshidoRelaxed, 'Little Ishido Relaxed', 2, 0,
  GI.SL_MOSTLY_SKILL, colors=4)
