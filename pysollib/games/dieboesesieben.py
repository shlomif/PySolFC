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

from gypsy import DieKoenigsbergerin_Talon, DieRussische_Foundation

# ************************************************************************
# * Die böse Sieben
# ************************************************************************

class DieBoeseSieben_Talon(DieKoenigsbergerin_Talon):
    def canDealCards(self):
        return len(self.cards) or self.round != self.max_rounds

    def dealCards(self, sound=False):
        if self.cards:
            return DieKoenigsbergerin_Talon.dealCards(self, sound=sound)
        game, num_cards = self.game, len(self.cards)
        for r in game.s.rows:
            while r.cards:
                num_cards = num_cards + 1
                if r.cards[-1].face_up:
                    game.flipMove(r)
                game.moveMove(1, r, self, frames=0)
        assert len(self.cards) == num_cards
        if sound:
            game.startDealSample()
        # shuffle
        game.shuffleStackMove(self)
        # redeal
        game.nextRoundMove(self)
        n = len(game.s.rows)
        flip = (num_cards / n) & 1
        while self.cards:
            if len(self.cards) <= n:
                flip = 1
            self.dealRow(flip=flip)
            flip = not flip
        # done
        if sound:
            game.stopSamples()
        return num_cards


class DieBoeseSieben(Game):
    #
    # game layout
    #

    def createGame(self, rows=7):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + max(8,rows)*l.XS, l.YM + 5*l.YS)

        # create stacks
        for i in range(8):
            x, y, = l.XM + i*l.XS, l.YM
            s.foundations.append(DieRussische_Foundation(x, y, self, i/2, max_move=0, max_cards=8))
        for i in range(rows):
            x, y, = l.XM + (2*i+8-rows)*l.XS/2, l.YM + l.YS
            s.rows.append(AC_RowStack(x, y, self))
        s.talon = DieBoeseSieben_Talon(l.XM, self.height-l.YS, self, max_rounds=2)
        l.createText(s.talon, 'ne')
        l.createRoundText(s.talon, 'se')

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        for flip in (1, 0, 1, 0, 1, 0, 1):
            self.s.talon.dealRow(flip=flip)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# register the game
registerGame(GameInfo(120, DieBoeseSieben, "Bad Seven",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_MOSTLY_LUCK,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12),
                      altnames=("Die boese Sieben",) ))

