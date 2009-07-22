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
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# * Bisley
# ************************************************************************

class Bisley(Game):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 2*l.XM+8*l.XS, max(2*(l.YM+l.YS+8*l.YOFFSET), l.YM+5*l.YS)
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(6):
            s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS
        x, y = l.XM, l.YM+l.YS+8*l.YOFFSET
        for i in range(6):
            s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS
        y = l.YM
        for i in range(4):
            x = l.XM+6*l.XS+l.XM
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_move=0))
            x += l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i,
                                 base_rank=KING, max_move=0, dir=-1))
            y += l.YS

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations[::2])

    def _shuffleHook(self, cards):
        # move Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == ACE, c.suit))

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Double Bisley
# ************************************************************************

class DoubleBisley(Bisley):

    Hint_Class = CautiousDefaultHint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+(8+2)*l.XS, l.YM+max(3*(l.YS+8*l.YOFFSET), 8*l.YS)
        self.setSize(w, h)

        # create stacks
        y = l.YM
        for i in range(3):
            x = l.XM
            for j in range(8):
                s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
                x += l.XS
            y += l.YS+8*l.YOFFSET

        y = l.YM
        for j in range(2):
            for i in range(4):
                x = l.XM+8*l.XS
                s.foundations.append(SS_FoundationStack(x, y, self,
                                     suit=j*2+i/2, max_move=0))
                x += l.XS
                s.foundations.append(SS_FoundationStack(x, y, self,
                     suit=j*2+i/2, base_rank=KING, max_move=0, dir=-1))
                y += l.YS

        s.talon = InitialDealTalonStack(l.XM, h-l.YS, self)

        # default
        l.defaultAll()


# ************************************************************************
# * Gloria
# ************************************************************************

class Gloria(Game):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+12*l.XS, l.YM+2*l.YS+2*(l.YS+5*l.YOFFSET)
        self.setSize(w, h)

        # create stacks
        y = l.YM+2*l.YS
        for i in range(2):
            x = l.XM
            for j in range(12):
                s.rows.append(BasicRowStack(x, y, self, max_accept=0))
                x += l.XS
            y += l.YS+5*l.YOFFSET

        x = l.XM+2*l.XS
        for j in range(2):
            for i in range(4):
                y = l.YM
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j*2+i/2))
                y += l.YS
                s.foundations.append(SS_FoundationStack(x, y, self,
                                     suit=j*2+i/2, base_rank=KING, dir=-1))
                x += l.XS

        s.reserves.append(ReserveStack(l.XM, l.YM, self))
        s.reserves.append(ReserveStack(w-l.XS, l.YM, self))

        s.talon = InitialDealTalonStack(l.XM, l.YM+l.YS, self)

        # default
        l.defaultAll()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations[1::2])

    def _shuffleHook(self, cards):
        # move Kings to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == KING, c.suit))


# ************************************************************************
# * Realm
# * Mancunian
# ************************************************************************

class Realm(Game):

    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(UD_AC_RowStack, base_rank=NO_RANK)

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 3*l.XM+8*l.XS, l.YM+2*l.YS+15*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = 2*l.XM, l.YM+l.YS
        for i in range(8):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        y = l.YM
        for i in range(4):
            x = l.XM+i*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_move=0))
            x += 2*l.XM+4*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i,
                                 base_rank=KING, max_move=0, dir=-1))

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    shallHighlightMatch = Game._shallHighlightMatch_AC


class Mancunian(Realm):
    RowStack_Class = StackWrapper(UD_RK_RowStack, base_rank=NO_RANK)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Hospital Patience
# ************************************************************************

class HospitalPatience(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+6*l.XS, l.YM+2*l.YS)

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=UNLIMITED_REDEALS, num_deal=3)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        x = l.XM+2*l.XS
        for i in range(4):
            y = l.YM
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_move=0))
            y += l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, i,
                                 base_rank=KING, max_move=0, dir=-1))
            x += l.XS

        l.defaultStackGroups()

    def startGame(self, flip=0, reverse=1):
        self.startDealSample()
        self.s.talon.dealCards()      # deal first card to WasteStack



# ************************************************************************
# * Board Patience
# ************************************************************************

class BoardPatience(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+10*l.XS, l.YM+2*l.YS+12*l.YOFFSET)

        # extra settings
        self.base_card = None

        # create stacks
        x, y = l.XM+3*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=i, mod=13))
            x = x + l.XS
        tx, ty, ta, tf = l.getTextAttr(s.foundations[-1], "ne")
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)
        x, y = l.XM, l.YM+l.YS
        for i in range(10):
            s.rows.append(UD_AC_RowStack(x, y, self, mod=13))
            x += l.XS

        x, y = l.XM, l.YM
        s.talon = InitialDealTalonStack(x, y, self)

        # default
        l.defaultAll()

    def updateText(self):
        if self.preview > 1:
            return
        if not self.texts.info:
            return
        if not self.base_card:
            t = ""
        else:
            t = RANKS[self.base_card.rank]
        self.texts.info.config(text=t)

    def startGame(self):
        # deal base_card to Foundations, update foundations cap.base_rank
        self.base_card = self.s.talon.getCard()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        n = self.base_card.suit
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, self.s.foundations[n], frames=0)
        # deal to rows
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    shallHighlightMatch = Game._shallHighlightMatch_ACW

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


# ************************************************************************
# * Cringle
# ************************************************************************

class Cringle(Game):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8.5*l.XS, l.YM + 3*l.YS + 14*l.XOFFSET)

        # create stacks
        x, y, = l.XM, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        x += l.XS/2
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            x += l.XS

        x, y = l.XM, l.YM+l.YS
        for j in range(4):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS
        x += l.XS/2
        for j in range(4):
            s.rows.append(AC_RowStack(x, y, self, dir=1))
            x += l.XS

        x, y = self.width-l.XS, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'n')
        x -= l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_AC





# register the game
registerGame(GameInfo(290, Bisley, "Bisley",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(372, DoubleBisley, "Double Bisley",
                      GI.GT_2DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(373, Gloria, "Gloria",
                      GI.GT_2DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(374, Realm, "Realm",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(375, Mancunian, "Mancunian",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(686, HospitalPatience, "Hospital Patience",
                      GI.GT_1DECK_TYPE, 1, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(692, BoardPatience, "Board Patience",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(747, Cringle, "Cringle",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED))

