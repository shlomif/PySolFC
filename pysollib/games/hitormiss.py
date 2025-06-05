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
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        AbstractFoundationStack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ANY_SUIT, RANKS, \
        UNLIMITED_REDEALS, \
        VARIABLE_REDEALS


# ************************************************************************
# *
# ************************************************************************

class HitOrMiss_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        game = self.game
        return game.rank == cards[0].rank  # check the rank

    def getHelp(self):
        return _('Foundation. Place cards here that match the declared rank.')


class HitOrMiss_Talon(WasteTalonStack):
    def canDealCards(self):
        game = self.game
        if (game.deadDeals == 2 and len(self.cards) == 0 and
                self.max_rounds == VARIABLE_REDEALS):
            return False
        return True

    def dealCards(self, sound=False):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        game.saveStateMove(2 | 16)  # for undo
        if len(self.cards) > 0:
            game.rank += 1
        else:
            game.deadDeals += 1
        if game.rank > 12:
            game.rank = 0
        game.saveStateMove(1 | 16)  # for redo
        game.leaveState(old_state)
        return WasteTalonStack.dealCards(self, sound)

    def getHelp(self):
        return _('Talon. Unlimited redeals, until running through the deck '
                 'twice with no hits.')


class HitOrMiss_Waste(WasteStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game = self.game
        if to_stack in game.s.foundations:
            old_state = game.enterState(game.S_FILL)
            game.saveStateMove(2 | 16)  # for undo
            game.deadDeals = 0
            game.saveStateMove(1 | 16)  # for redo
            game.leaveState(old_state)
        WasteStack.moveMove(self, ncards, to_stack, frames, shadow)
        game.s.talon.dealCards()


# ************************************************************************
# * Hit Or Miss
# ************************************************************************

class HitOrMiss(Game):
    MaxRounds = VARIABLE_REDEALS

    def createGame(self):
        layout, s = Layout(self), self.s
        self.rank = -1
        self.deadDeals = 1
        self.setSize(layout.XM + 4 * layout.XS, layout.YM + 2 * layout.YS)
        x, y = layout.XM + 3 * layout.XS // 2, layout.YM
        stack = HitOrMiss_Foundation(x, y, self, ANY_SUIT,
                                     dir=0, mod=13, max_move=0, max_cards=52)
        s.foundations.append(stack)
        layout.createText(stack, 'ne')
        x, y = layout.XM+layout.XS, layout.YM+layout.YS
        s.talon = HitOrMiss_Talon(x, y, self,
                                  max_rounds=self.MaxRounds, num_deal=1)
        layout.createText(s.talon, 'nw')

        x += layout.XS
        s.waste = HitOrMiss_Waste(x, y, self)
        layout.createText(s.waste, 'ne')
        x += layout.XS * 1.1
        y = layout.YM + 1.4 * layout.YS
        if self.preview <= 1:
            self.texts.base_rank = \
                MfxCanvasText(self.canvas, x, y, anchor="nw",
                              font=self.app.getFont("canvas_large"))

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self.rank = -1
        self.deadDeals = 1
        self.justHit = False
        self.startDealSample()
        self.s.talon.dealCards()

    def updateText(self):
        if self.preview > 1:
            return
        self.texts.base_rank.config(text=RANKS[self.rank])

    def _restoreGameHook(self, game):
        self.rank = game.loadinfo.dval.get('Rank')
        self.deadDeals = game.loadinfo.dval.get('DeadDeals')

    def _loadGameHook(self, p):
        self.loadinfo.addattr(dval=p.load())

    def _saveGameHook(self, p):
        dval = {'Rank': self.rank, 'DeadDeals': self.deadDeals}
        p.dump(dval)

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.rank = state[0]
        self.deadDeals = state[1]

    def getState(self):
        # save vars (for undo/redo)
        return [self.rank, self.deadDeals]

    def getSnapshotHash(self):
        # Takes the chosen rank into account when determining
        # if the game is stuck.
        return Game.getSnapshotHash(self) + str(self.rank)

    def parseGameInfo(self):
        return RANKS[self.rank]


class HitOrMissUnlimited(HitOrMiss):
    MaxRounds = UNLIMITED_REDEALS


# register the game
registerGame(GameInfo(774, HitOrMiss, "Hit or Miss",
                      GI.GT_1DECK_TYPE, 1, VARIABLE_REDEALS,
                      GI.SL_LUCK, altnames=("Roll Call",)))
registerGame(GameInfo(865, HitOrMissUnlimited, "Hit or Miss Unlimited",
                      GI.GT_1DECK_TYPE | GI.GT_CHILDREN, 1, UNLIMITED_REDEALS,
                      GI.SL_LUCK))
