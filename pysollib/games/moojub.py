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
        DealRowTalonStack, \
        OpenStack, \
        RK_FoundationStack, \
        ReserveStack, \
        SS_FoundationStack, \
        SS_RowStack, \
        Stack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ACE, ANY_SUIT, JACK, KING, QUEEN


# ************************************************************************
# * Moojub
# ************************************************************************

class Moojub_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if len(self.cards) > 0:
            return (self.cards[-1].suit == cards[0].suit and
                    RK_FoundationStack.acceptsCards(self, from_stack, cards))

        foundations = self.game.s.foundations

        # Checking each rule for starting a new foundation:
        # Only the next foundation can be built to.
        if self.id > 0 and len(foundations[self.id - 1].cards) == 0:
            return False
        # The suit must match the foundation directly to the left.
        if (self.id > 3 and
                foundations[self.id - 4].cards[0].suit != cards[0].suit):
            return False
        # Two foundations in the same column can't have the same suit.
        if self.id <= 3:
            for i in range(4):
                if (foundations[i].cards and
                        foundations[i].cards[0].suit == cards[0].suit):
                    return False
        # Only the lowest available card of a suit can start a foundation.
        for row in self.game.s.rows:
            if (row.cards and row.cards[-1].suit == cards[0].suit
                    and row.cards[-1].rank < cards[0].rank):
                return False
        # Can't start a foundation with a card that can be played on an
        # existing foundation.
        for foundation in foundations:
            if (foundation.cards and
                    foundation.cards[-1].suit == cards[0].suit and
                    (foundation.cards[-1].rank == cards[0].rank - 1 or
                     (foundation.cards[-1].rank == KING and
                      cards[0].rank == ACE))):
                return False
        return True


class Moojub(Game):
    Foundations = 8

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (l.XS * 1.5) + self.Foundations * l.XS,
                     l.YM + 5 * l.YS)

        # create stacks
        for j in range(self.Foundations):
            for i in range(4):
                x, y, = l.XM + (l.XS * (j + 1.5)), (l.YM + i * l.YS) + l.YS
                s.foundations.append(Moojub_Foundation(x, y, self, ANY_SUIT,
                                                       mod=13, max_move=0))

        for i in range(4):
            x, y, = l.XM, (l.YM + i * l.YS) + l.YS
            s.rows.append(OpenStack(x, y, self))

        x, y, = l.XM, l.YM
        s.talon = DealRowTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'se')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self._startAndDealRow()


# ************************************************************************
# * Four Kingdoms
# ************************************************************************

class FourKingdoms_KingFoundation(SS_FoundationStack):
    RequiredStacks = ()

    def acceptsCards(self, from_stack, cards):
        for stackID in self.RequiredStacks:
            if len(self.game.s.foundations[self.id + stackID].cards) == 0:
                return False
        return SS_FoundationStack.acceptsCards(self, from_stack, cards)

    def getHelp(self):
        return _('Castle.  From left to right, accepts the king, queen, '
                 'and jack of the suit, in that order.')


class FourKingdoms_QueenFoundation(FourKingdoms_KingFoundation):
    RequiredStacks = (-1,)


class FourKingdoms_JackFoundation(FourKingdoms_KingFoundation):
    RequiredStacks = (-1, -2)


class FourKingdoms_DungeonFoundation(FourKingdoms_KingFoundation):
    RequiredStacks = (1, 2, 3, 4)

    def getHelp(self):
        return _('Dungeon.  Accepts the ace (dragon) of the suit, but only '
                 'once the tower and castle are filled.')


class FourKingdoms_TowerFoundation(FourKingdoms_KingFoundation):
    def getHelp(self):
        return _('Tower.  Accepts the ten (wizard) of the suit.')


class FourKingdoms_SubjectsFoundation(FourKingdoms_KingFoundation):
    RequiredStacks = (-1, -2, -3)

    def getHelp(self):
        return _('Subjects.  Builds down by suit from 9 to 2, but can only '
                 'be built to once the castle is filled.')


class FourKingdoms_Reserve(ReserveStack):
    getBottomImage = Stack._getSuitBottomImage

    def acceptsCards(self, from_stack, cards):
        if cards[0].rank == ACE:
            return False
        checkStack = (6 * self.cap.base_suit) + 2
        for s in range(2):
            if len(self.game.s.foundations[checkStack + s].cards) == 0:
                return False
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def getHelp(self):
        return _('Guest Chambers.  A free cell, but only accepts cards of '
                 'the suit, and only once the king and queen are in the '
                 'castle.')


class FourKingdoms_RowStack(SS_RowStack):

    def acceptsCards(self, from_stack, cards):
        if self.cards and self.cards[-1].rank == ACE:
            return False
        return SS_RowStack.acceptsCards(self, from_stack, cards)


class FourKingdoms(Game):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (l.XS * 9),
                     l.YM + (6 * l.YS) + l.TEXT_HEIGHT)

        # create stacks
        for i in range(4):
            x, y = l.XM, l.YM + l.TEXT_HEIGHT + (l.YS * i)
            s.foundations.append(
                FourKingdoms_DungeonFoundation(x, y, self, i, base_rank=ACE,
                                               max_cards=1, max_accept=1))
            x += (1.5 * l.XS)
            s.foundations.append(
                FourKingdoms_TowerFoundation(x, y, self, i, base_rank=9,
                                             max_cards=1, max_accept=1))
            x += (3 * l.XS)
            s.foundations.append(
                FourKingdoms_KingFoundation(x, y, self, i, base_rank=KING,
                                            max_cards=1, max_accept=1))
            x += l.XS
            s.foundations.append(
                FourKingdoms_QueenFoundation(x, y, self, i, base_rank=QUEEN,
                                             max_cards=1, max_accept=1))
            x += l.XS
            s.foundations.append(
                FourKingdoms_JackFoundation(x, y, self, i, base_rank=JACK,
                                            max_cards=1, max_accept=1))
            x += (1.5 * l.XS)
            s.foundations.append(
                FourKingdoms_SubjectsFoundation(x, y, self, i, base_rank=8,
                                                dir=-1, max_cards=8,
                                                max_accept=1))

        # I know it seems weird to add the Guest Chambers out of position
        # order, but it makes it so much easier to manage the stack logic
        # later.
        for i in range(4):
            x, y = l.XM + (l.XS * 3), l.YM + l.TEXT_HEIGHT + (l.YS * i)
            s.reserves.append(
                FourKingdoms_Reserve(x, y, self, max_cards=1, max_accept=1))
            s.reserves[i].cap.base_suit = i

        if self.preview <= 1:
            self.setLabel(l, self.s.foundations[0], "Dungeon")
            self.setLabel(l, self.s.foundations[1], "Tower")
            self.setLabel(l, self.s.foundations[3], "Castle")
            self.setLabel(l, self.s.foundations[5], "Subjects")
            self.setLabel(l, self.s.reserves[0], "Guest")

        x, y, = l.XM, l.YM + l.TEXT_HEIGHT + (l.YS * 4)
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'se')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        x, y, = l.XM + l.XS, l.YM + l.TEXT_HEIGHT + (l.YS * 4)
        for i in range(7):
            x += l.XS
            s.rows.append(FourKingdoms_RowStack(x, y, self, dir=1))

        # define stack-groups
        l.defaultStackGroups()

    def setLabel(self, layout, stack, text):
        font = self.app.getFont("canvas_default")
        tx, ty, ta, tf = layout.getTextAttr(stack, anchor="n")
        stack.texts.misc = MfxCanvasText(self.canvas,
                                         tx, ty,
                                         anchor=ta,
                                         font=font)
        stack.texts.misc.config(text=_(text))

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0, flip=0)
        self._startAndDealRowAndCards()


# register the game
registerGame(GameInfo(845, Moojub, "Moojub",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(970, FourKingdoms, "Four Kingdoms",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
