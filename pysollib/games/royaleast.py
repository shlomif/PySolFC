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

# ************************************************************************
# * Royal East
# ************************************************************************

class RoyalEast(Game):
    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 5.5*l.XS, l.YM + 4*l.YS)

        # extra settings
        self.base_card = None

        # create stacks
        for i in range(4):
            dx, dy = ((0, 0), (2, 0), (0, 2), (2, 2))[i]
            x, y = l.XM + (2*dx+5)*l.XS/2, l.YM + (2*dy+1)*l.YS/2
            stack = SS_FoundationStack(x, y, self, i, mod=13, max_move=0)
            stack.CARD_YOFFSET = 0
            s.foundations.append(stack)
        for i in range(5):
            dx, dy = ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2))[i]
            x, y = l.XM + (2*dx+5)*l.XS/2, l.YM + (2*dy+1)*l.YS/2
            stack = RK_RowStack(x, y, self, mod=13, max_move=1)
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)
        x, y = l.XM, l.YM + 3*l.YS/2
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.base_card = self.s.talon.cards[-1]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        # deal base card to Foundations
        c = self.s.talon.getCard()
        to_stack = self.s.foundations[c.suit * self.gameinfo.decks]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack, frames=0)
        # deal rows
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# register the game
registerGame(GameInfo(93, RoyalEast, "Royal East",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))

