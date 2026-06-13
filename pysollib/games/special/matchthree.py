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
from pysollib.mfxutil import kwdefault
from pysollib.mygettext import _
from pysollib.pysoltk import Card, MfxCanvasText
from pysollib.settings import TOOLKIT
from pysollib.stack import \
        AbstractFoundationStack, \
        InvisibleStack, \
        OpenStack, \
        RedealTalonStack
from pysollib.util import ANY_SUIT


# ************************************************************************
# * Match Three
# ************************************************************************


class MatchThree_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit=ANY_SUIT, **cap):
        kwdefault(cap, max_move=0, max_accept=0, max_cards=game.NCARDS)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        return False


class MatchThree_RowStack(OpenStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        game.saveStateMove(2 | 16)
        game.moves_left -= 1
        self._swapPairMove(ncards, to_stack, frames=-1, shadow=0)
        game.cascade()
        game.saveStateMove(1 | 16)
        game.leaveState(old_state)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=frames, shadow=shadow)
        game.moveMove(n, swap, other_stack, frames=0)
        game.leaveState(old_state)

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack not in self.getAdjacent(self.id):
            return False
        return bool(self.game.findMatchWithSwap(self, from_stack))

    def getAdjacent(self, playSpace):
        cols, rows = self.game.L
        s = self.game.s
        adjacentRows = []
        if playSpace % rows != (rows - 1):
            adjacentRows.append(s.rows[playSpace + 1])

        if playSpace % rows != 0:
            adjacentRows.append(s.rows[playSpace - 1])

        if playSpace + rows < (cols * rows):
            adjacentRows.append(s.rows[playSpace + rows])

        if playSpace - rows > -1:
            adjacentRows.append(s.rows[playSpace - rows])

        return adjacentRows


class AbstractMatchThreeGame(Game):
    RowStack_Class = MatchThree_RowStack

    NCOLORS = 4
    NCARDS = 144

    COLORS = (_("Blue"), _("Red"), _("Yellow"), _("Green"),
              _("Purple"), _("Orange"))

    WIN_SCORE = 8000

    def createGame(self):
        cols, rows = self.L

        self.score = 0
        self.moves_left = 30
        self.multiplier = 1
        self._matchthree_in_combo = False

        # start layout
        l, s = Layout(self), self.s
        # dx, dy = 3, -3

        cs = self.app.images.cs
        if cs.version == 6 or cs.mahjongg3d:
            dx = l.XOFFSET
            dy = -l.YOFFSET
            d_x = cs.SHADOW_XOFFSET
            d_y = cs.SHADOW_YOFFSET
        else:
            dx = 3
            dy = -3
            d_x = 0
            d_y = 0
        # TODO - This should be moved to subsample logic in the future.
        if self.preview > 1:
            d_x /= 2
            d_y /= 2

        dxx, dyy = abs(dx), abs(dy)
        cardw, cardh = l.CW - d_x, l.CH - d_y
        h = l.YM + dyy + rows * cardh + d_y + l.YM

        # Side panel text.
        x, y = l.XM, h - l.YM
        if self.preview <= 1:
            self.texts.score = MfxCanvasText(
                self.canvas, x, y, anchor="sw",
                font=self.app.getFont("canvas_large"))
            self.updateText()
            x = self.texts.score.bbox()[1][0] + 16

        side = max(2 * l.XS, x)
        grid_w = dxx + cols * cardw + d_x + l.XM + l.XM
        self.setSize(side + grid_w, h)

        #
        self.cols = [[] for i in range(cols)]
        cl = range(cols)
        for col in cl:
            for row in range(rows):
                x = l.XM + side + dxx + col * cardw
                y = l.YM + dyy + row * cardh
                stack = self.RowStack_Class(
                    x, y, self, max_accept=1, max_cards=2)
                stack.CARD_XOFFSET = 0
                stack.CARD_YOFFSET = 0
                stack.coln, stack.rown = col, row
                s.rows.append(stack)
                self.cols[col].append(stack)

        # create other stacks
        y = l.YM + dyy
        ivx = -l.XS-self.canvas.xmargin
        if TOOLKIT == 'kivy':
            ivx = -1000
        s.foundations.append(MatchThree_Foundation(ivx, y, self))
        # the Talon is invisble
        s.talon = RedealTalonStack(-l.XS-self.canvas.xmargin,
                                   self.height-dyy, self)
        s.internals.append(InvisibleStack(self))
        # Define stack groups
        l.defaultStackGroups()

    def startGame(self):
        self.score = 0
        self.moves_left = 30
        self.multiplier = 1
        self._matchthree_in_combo = False
        self.updateText()
        assert len(self.s.talon.cards) == self.NCARDS
        self.s.talon.dealRow(rows=self.s.rows[:self.NCARDS], frames=0)
        self.cascade(scoring=False)

    def _createCard(self, id, deck, suit, rank, x, y):
        return Card(id, deck, id % self.NCOLORS, id % self.NCOLORS,
                    game=self, x=x, y=y)

    def refreshTalon(self):
        if self.s.talon.cards:
            return
        waste = self.s.foundations[0].cards
        if waste:
            self.moveMove(len(waste), self.s.foundations[0], self.s.talon,
                          frames=0)
            self.shuffleStackMove(self.s.talon)

    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)
        column = self.cols[stack.coln]
        nrows = len(column)

        # Gravity: pack tiles to the bottom of the column.
        dest = nrows - 1
        for src in range(nrows - 1, -1, -1):
            if column[src].cards:
                if src != dest:
                    self.moveMove(1, column[src], column[dest], frames=0)
                dest -= 1

        # New tiles from the talon fill empty cells at the top.
        for r in range(dest, -1, -1):
            deal_stack = column[r]
            if deal_stack.cards:
                continue
            self.refreshTalon()
            if not self.s.talon.cards:
                break
            self.moveMove(1, self.s.talon, deal_stack, frames=0)
            if not deal_stack.cards[-1].face_up:
                self.flipMove(deal_stack)
        self.leaveState(old_state)

    def cascade(self, scoring=True):
        removestacks = []
        for r in self.s.rows:
            for st in self.findMatch(r):
                if st not in removestacks:
                    removestacks.append(st)
        if not removestacks:
            if scoring and self._matchthree_in_combo:
                self.multiplier = 1
                self._matchthree_in_combo = False
            return

        # Show this cascade step before removing tiles.
        if (scoring and not self.demo and
                self.app.opt.match_three_cascade):
            self.updateText()
            self._highlightCascadeMatch(removestacks)

        old_state = self.enterState(self.S_FILL)
        for re in removestacks:
            self.moveMove(1, re, self.s.foundations[0], frames=0)
        if scoring:
            self._matchthree_in_combo = True
            self.score += int(self.multiplier * (
                100 + max(0, len(removestacks) - 3) * 20))
            self.multiplier = min(self.multiplier + 0.5, 2.5)
        for re in removestacks:
            if len(re.cards) == 0:
                self.fillStack(re)
        self.leaveState(old_state)
        self.cascade(scoring=scoring)

    def parseCard(self, card):
        return self.COLORS[card.suit]

    def parseStackInfo(self, stack):
        if stack not in self.s.rows:
            return ""
        row = (stack.id % self.L[1]) + 1
        column = (stack.id // self.L[1]) + 1
        return _("Row: %d, Column: %d") % (row, column)

    def isGameWon(self):
        return self.score >= self.WIN_SCORE and self.moves_left >= 0

    def getAutoStacks(self, event=None):
        return ((), (), ())

    def _restoreGameHook(self, game):
        self.score = game.loadinfo.score
        self.moves_left = game.loadinfo.moves_left

    def _loadGameHook(self, p):
        self.loadinfo.addattr(score=p.load())
        self.loadinfo.addattr(moves_left=p.load())

    def _saveGameHook(self, p):
        score = self.score
        p.dump(score)
        moves_left = self.moves_left
        p.dump(moves_left)

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.score = state[0]
        self.moves_left = state[1]

    def getState(self):
        # save vars (for undo/redo)
        return [self.score, self.moves_left]

    #
    # scoring
    #

    def updateText(self):
        if self.preview > 1 or not self.texts.score:
            return
        t = _("Points: %d") % self.score + "\n"
        t += _("Goal: %d") % self.WIN_SCORE + "\n"
        t += _("Moves left: %d") % max(0, self.moves_left)
        self.texts.score.config(text=t)

    def parseGameInfo(self):
        return _("Points: %d") % self.score

    def getGameScore(self):
        return self.score

    def getBoard(self, swap=None):
        # grid[col][row] is suit int or None if empty.
        cols, rows = self.L
        grid = [[None] * rows for _ in range(cols)]
        for st in self.s.rows:
            if st.cards:
                grid[st.coln][st.rown] = st.cards[-1].suit
        if swap is not None:
            a, b = swap
            c1, r1, c2, r2 = a.coln, a.rown, b.coln, b.rown
            grid[c1][r1], grid[c2][r2] = grid[c2][r2], grid[c1][r1]
        return grid

    def getStackAt(self, col, row):
        cols, rows = self.L
        if not (0 <= col < cols and 0 <= row < rows):
            return None
        return self.s.rows[col * rows + row]

    def getMaximalLine(self, grid, col, row, dcol, drow):
        cols, rows = self.L
        if not (0 <= col < cols and 0 <= row < rows):
            return []
        suit = grid[col][row]
        if suit is None:
            return []
        c, r = col, row
        while True:
            nc, nr = c - dcol, r - drow
            if not (0 <= nc < cols and 0 <= nr < rows) or grid[nc][nr] != suit:
                break
            c, r = nc, nr
        line = []
        while True:
            if not (0 <= c < cols and 0 <= r < rows) or grid[c][r] != suit:
                break
            line.append((c, r))
            c, r = c + dcol, r + drow
        return line

    def findMatch(self, stack):
        if stack not in self.s.rows or not stack.cards:
            return []
        grid = self.getBoard()
        col, row = stack.coln, stack.rown
        if grid[col][row] is None:
            return []
        horiz = self.getMaximalLine(grid, col, row, 1, 0)
        vert = self.getMaximalLine(grid, col, row, 0, 1)

        matched = []
        if len(horiz) >= 3:
            matched.extend(horiz)
        if len(vert) >= 3:
            matched.extend(vert)
        if not matched:
            return []

        seen = set()
        stacks = []
        for c, r in matched:
            if (c, r) in seen:
                continue
            seen.add((c, r))
            st = self.getStackAt(c, r)
            if st:
                stacks.append(st)
        return stacks

    def findMatchWithSwap(self, stack_a, stack_b):
        if stack_b not in stack_a.getAdjacent(stack_a.id):
            return []
        if not stack_a.cards or not stack_b.cards:
            return []

        grid = self.getBoard(swap=(stack_a, stack_b))
        matched = []
        seen = set()
        for st in self.s.rows:
            col, row = st.coln, st.rown
            if grid[col][row] is None:
                continue
            for line in (
                self.getMaximalLine(grid, col, row, 1, 0),
                self.getMaximalLine(grid, col, row, 0, 1),
            ):
                if len(line) >= 3:
                    for c, r in line:
                        if (c, r) not in seen:
                            seen.add((c, r))
                            matched.append(self.getStackAt(c, r))
        return matched

    def _highlightCascadeMatch(self, stacks):
        if not stacks or self.demo:
            return
        col = self.app.opt.colors['cards_1']
        info = []
        for st in stacks:
            if st.cards:
                c = st.cards[-1]
                info.append((st, c, c, col))
        if not info:
            return
        self.stats.highlight_cards += 1
        self._highlightCards(info, self.app.opt.timeouts['hint'])


# Number of cards in each game:
# Four times the number of spaces on the board.
# Round up to the nearest multiple of the number of colors.

class MatchThree4_6x6(AbstractMatchThreeGame):
    L = (6, 6)
    NCARDS = 144
    WIN_SCORE = 8000


class MatchThree4_7x7(AbstractMatchThreeGame):
    L = (7, 7)
    NCARDS = 196
    WIN_SCORE = 9500


class MatchThree4_8x8(AbstractMatchThreeGame):
    L = (8, 8)
    NCARDS = 256
    WIN_SCORE = 11000


class MatchThree5_6x6(MatchThree4_6x6):
    NCOLORS = 5
    NCARDS = 145
    WIN_SCORE = 6000


class MatchThree5_7x7(MatchThree4_7x7):
    NCOLORS = 5
    NCARDS = 200
    WIN_SCORE = 7500


class MatchThree5_8x8(MatchThree4_8x8):
    NCOLORS = 5
    NCARDS = 260
    WIN_SCORE = 9000


class MatchThree6_6x6(MatchThree4_6x6):
    NCOLORS = 6
    NCARDS = 144
    WIN_SCORE = 4000


class MatchThree6_7x7(MatchThree4_7x7):
    NCOLORS = 6
    NCARDS = 198
    WIN_SCORE = 5500


class MatchThree6_8x8(MatchThree4_8x8):
    NCOLORS = 6
    NCARDS = 258
    WIN_SCORE = 7000

# 10X10 is too easy to be worth including, commented for now.
# class MatchThree4_10x10(AbstractMatchThreeGame):
#     L = (10, 10)
#     NCARDS = 400
# class MatchThree5_10x10(MatchThree4_10x10):
#     NCOLORS = 5
#     NCARDS = 400
# class MatchThree6_10x10(MatchThree4_10x10):
#     NCOLORS = 6
#     NCARDS = 402


# ************************************************************************
# * register a MatchThree type game
# ************************************************************************

def r(id, gameclass, name, rules_filename="matchthree.html"):
    gi = GameInfo(id, gameclass, name,
                  GI.GT_MATCH_THREE | GI.GT_SCORE, 1, 0,
                  GI.SL_MOSTLY_SKILL, category=GI.GC_ISHIDO, short_name=name,
                  suits=list(range(1)), ranks=list(range(gameclass.NCARDS)),
                  si={"decks": 1, "ncards": gameclass.NCARDS})
    gi.ncards = gameclass.NCARDS
    gi.rules_filename = rules_filename
    registerGame(gi)
    return gi


r(19501, MatchThree4_6x6, "Match Three 4 Colors 6x6")
r(19502, MatchThree5_6x6, "Match Three 5 Colors 6x6")
r(19503, MatchThree6_6x6, "Match Three 6 Colors 6x6")
r(19504, MatchThree4_7x7, "Match Three 4 Colors 7x7")
r(19505, MatchThree5_7x7, "Match Three 5 Colors 7x7")
r(19506, MatchThree6_7x7, "Match Three 6 Colors 7x7")
r(19507, MatchThree4_8x8, "Match Three 4 Colors 8x8")
r(19508, MatchThree5_8x8, "Match Three 5 Colors 8x8")
r(19509, MatchThree6_8x8, "Match Three 6 Colors 8x8")
# r(19507, MatchThree4_10x10, "Match Three 4 Colors 10x10")
# r(19508, MatchThree5_10x10, "Match Three 5 Colors 10x10")
# r(19509, MatchThree6_10x10, "Match Three 6 Colors 10x10")

del r
