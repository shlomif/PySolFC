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
from pysollib.mfxutil import kwdefault
from pysollib.pysoltk import Card, MfxCanvasText
from pysollib.settings import TOOLKIT
from pysollib.stack import \
        AbstractFoundationStack, \
        InitialDealTalonStack, \
        OpenStack
from pysollib.util import ANY_SUIT


# ************************************************************************
# * Samegame
# ************************************************************************

class Samegame_Hint(AbstractHint):
    # FIXME: no intelligence whatsoever is implemented here

    def computeHints(self):
        game = self.game
        for r in game.s.rows:
            if r.cards:
                removeStacks = r.getRemoveStacks()
                score = 100 * len(removeStacks)
                if score > 100:
                    self.addHint(score, 1, r, game.s.foundations[0])


class Samegame_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit=ANY_SUIT, **cap):
        kwdefault(cap, max_move=0, max_accept=0, max_cards=game.NCARDS)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        return 1


class Samegame_RowStack(OpenStack):
    def clickHandler(self, event):
        if len(self.cards) == 0:
            return False
        self.playMoveMove(1, self.game.s.foundations[0], sound=False)

    def rightclickHandler(self, event):
        return self.clickHandler(event)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1
        if to_stack in self.game.s.foundations:
            game = self.game
            removeStacks = self.getRemoveStacks()
            if len(removeStacks) < 2:
                return False

            old_state = game.enterState(game.S_FILL)
            game.updateStackMove(self, 2 | 16)
            for stack in removeStacks:
                game.moveMove(1, stack, game.s.foundations[0], frames=0)
            for stack in removeStacks:
                stack.fillStack()
            game.slideStacks()

            if not game.demo:
                game.playSample("drop", priority=200)

            game.updateStackMove(self, 1 | 16)  # for redo
            game.leaveState(old_state)
            return True
        else:
            return OpenStack.moveMove(self, ncards, to_stack, frames=frames,
                                      shadow=shadow)

    def fillStack(self):
        self.game.fillStack(self)

    def getRemoveStacks(self):
        removeStacks = [self]
        spotsChecked = 0
        while spotsChecked < len(removeStacks):
            adjacent = self.getAdjacent(removeStacks[spotsChecked].id)
            for adjacentStack in adjacent:
                if adjacentStack not in removeStacks and \
                        len(adjacentStack.cards) > 0 and \
                        adjacentStack.cards[0].suit == self.cards[0].suit:
                    removeStacks.append(adjacentStack)
            spotsChecked += 1
        return removeStacks

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


class AbstractSamegameGame(Game):
    Hint_Class = Samegame_Hint
    RowStack_Class = Samegame_RowStack

    COLORS = 3
    NCARDS = 144

    def createGame(self):
        cols, rows = self.L
        assert cols*rows == self.NCARDS

        # start layout
        l, s = Layout(self), self.s
        # dx, dy = 3, -3

        cs = self.app.images.cs
        if cs.version == 6 or cs.mahjongg3d:
            dx = l.XOFFSET
            dy = -l.YOFFSET
            d_x = cs.SHADOW_XOFFSET
            d_y = cs.SHADOW_YOFFSET
            self._delta_x, self._delta_y = dx, -dy
        else:
            dx = 3
            dy = -3
            d_x = 0
            d_y = 0
            self._delta_x, self._delta_y = 0, 0
        # TODO - This should be moved to subsample logic in the future.
        if self.preview > 1:
            d_x /= 2
            d_y /= 2

        font = self.app.getFont("canvas_default")

        # set window size
        dxx, dyy = abs(dx), abs(dy)
        cardw, cardh = l.CW - d_x, l.CH - d_y
        w = l.XM + dxx + cols * cardw + d_x + l.XM + l.XM
        h = l.YM + dyy + rows * cardh + d_y + l.YM
        self.setSize(w, h)

        #
        self.cols = [[] for i in range(cols)]
        cl = range(cols)
        for col in cl:
            for row in range(rows):
                x = l.XM + dxx + col * cardw
                y = l.YM + dyy + row * cardh
                stack = self.RowStack_Class(x, y, self)
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
        s.foundations.append(Samegame_Foundation(ivx, y, self))
        self.texts.info = MfxCanvasText(self.canvas,
                                        self.width - l.XM, y,
                                        anchor="nw", font=font)
        # the Talon is invisble
        s.talon = InitialDealTalonStack(-l.XS-self.canvas.xmargin,
                                        self.height-dyy, self)
        # Define stack groups
        l.defaultStackGroups()

    def startGame(self):
        assert len(self.s.talon.cards) == self.NCARDS
        # self.s.talon.dealRow(rows = self.s.rows, frames = 0)
        n = 12
        self.s.talon.dealRow(rows=self.s.rows[:self.NCARDS-n], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[self.NCARDS-n:])
        assert len(self.s.talon.cards) == 0

    def _createCard(self, id, deck, suit, rank, x, y):
        return Card(id, deck, id % self.COLORS, id % self.COLORS,
                    game=self, x=x, y=y)

    def fillStack(self, stack):
        to_stack = stack
        for from_stack in self.cols[stack.coln][stack.rown+1::-1]:
            if not from_stack.cards:
                continue
            self.moveMove(1, from_stack, to_stack, frames=0)
            to_stack = from_stack

    def slideStacks(self):
        # Slide to the left to fill empty columns.
        numrows = self.L[1]
        card = 0
        emptycols = 0
        for c in range(len(self.cols)):
            iscolempty = True
            colstart = card
            for r in range(numrows):
                if len(self.s.rows[card].cards) > 0:
                    iscolempty = False
                card += 1
            if iscolempty:
                emptycols += 1
            elif emptycols > 0:
                for r in range(colstart, card):
                    if len(self.s.rows[r].cards) > 0:
                        self.moveMove(1, self.s.rows[r],
                                      self.s.rows[r - (numrows * emptycols)],
                                      frames=0)

    def getAutoStacks(self, event=None):
        return ((), (), ())


class Samegame3_20x10(AbstractSamegameGame):
    L = (20, 10)
    NCARDS = 200


class Samegame3_15x10(AbstractSamegameGame):
    L = (15, 10)
    NCARDS = 150


class Samegame3_25x15(AbstractSamegameGame):
    L = (25, 15)
    NCARDS = 375


class Samegame4_20x10(Samegame3_20x10):
    COLORS = 4


class Samegame4_15x10(Samegame3_15x10):
    COLORS = 4


class Samegame4_25x15(Samegame3_25x15):
    COLORS = 4


class Samegame5_20x10(Samegame3_20x10):
    COLORS = 5


class Samegame5_15x10(Samegame3_15x10):
    COLORS = 5


class Samegame5_25x15(Samegame3_25x15):
    COLORS = 5


class Samegame6_20x10(Samegame3_20x10):
    COLORS = 6


class Samegame6_15x10(Samegame3_15x10):
    COLORS = 6


class Samegame6_25x15(Samegame3_25x15):
    COLORS = 6


# ************************************************************************
# * register a Samegame type game
# ************************************************************************

def r(id, gameclass, name, rules_filename="samegame.html"):
    gi = GameInfo(id, gameclass, name,
                  GI.GT_SAMEGAME, 1, 0, GI.SL_MOSTLY_SKILL,
                  category=GI.GC_ISHIDO, short_name=name,
                  suits=list(range(1)), ranks=list(range(gameclass.NCARDS)),
                  si={"decks": 1, "ncards": gameclass.NCARDS})
    gi.ncards = gameclass.NCARDS
    gi.rules_filename = rules_filename
    registerGame(gi)
    return gi


r(19000, Samegame3_15x10, "Samegame 3 Colors 15x10")
r(19001, Samegame4_15x10, "Samegame 4 Colors 15x10")
r(19002, Samegame5_15x10, "Samegame 5 Colors 15x10")
r(19003, Samegame6_15x10, "Samegame 6 Colors 15x10")
r(19004, Samegame3_20x10, "Samegame 3 Colors 20x10")
r(19005, Samegame4_20x10, "Samegame 4 Colors 20x10")
r(19006, Samegame5_20x10, "Samegame 5 Colors 20x10")
r(19007, Samegame6_20x10, "Samegame 6 Colors 20x10")
r(19008, Samegame3_25x15, "Samegame 3 Colors 25x15")
r(19009, Samegame4_25x15, "Samegame 4 Colors 25x15")
r(19010, Samegame5_25x15, "Samegame 5 Colors 25x15")
r(19011, Samegame6_25x15, "Samegame 6 Colors 25x15")

del r
