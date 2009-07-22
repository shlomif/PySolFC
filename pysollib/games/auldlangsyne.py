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

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from numerica import Numerica_Hint


# ************************************************************************
# * Tam O'Shanter
# ************************************************************************

class TamOShanter(Game):
    Talon_Class = DealRowTalonStack
    Foundation_Class = RK_FoundationStack
    RowStack_Class = StackWrapper(BasicRowStack, max_move=1, max_accept=0)

    def createGame(self, rows=4, texts=False, yoffset=None):
        # create layout
        l, s = Layout(self), self.s

        # set window
        if yoffset is None:
            yoffset = l.YOFFSET
        max_rows = max(rows, 4*self.gameinfo.decks)
        self.setSize(l.XM+(2+max_rows)*l.XS, l.YM+2*l.YS+12*yoffset)

        # create stacks
        if texts:
            x, y, = l.XM, l.YM+l.YS/2
        else:
            x, y, = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, "s")
        if texts:
            l.createRoundText(s.talon, 'nn')
        x, y = l.XM+2*l.XS, l.YM
        for i in range(4*self.gameinfo.decks):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i%4))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self)
            s.rows.append(stack)
            stack.CARD_YOFFSET = yoffset
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


# ************************************************************************
# * Auld Lang Syne
# ************************************************************************

class AuldLangSyne(TamOShanter):
    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

# ************************************************************************
# * Strategy
# * Strategy +
# ************************************************************************

class Strategy_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # we only accept cards if there are no cards in the talon
        return len(self.game.s.talon.cards) == 0


class Strategy_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts any one card from the Talon
        return from_stack is self.game.s.talon and len(cards) == 1

    def canMoveCards(self, cards):
        if self.game.s.talon.cards:
            return False
        return BasicRowStack.canMoveCards(self, cards)

    def clickHandler(self, event):
        if self.game.s.talon.cards:
            self.game.s.talon.playMoveMove(1, self)
            return 1
        return BasicRowStack.clickHandler(self, event)

    def doubleclickHandler(self, event):
        if self.game.s.talon.cards:
            self.game.s.talon.playMoveMove(1, self)
            return 1
        return BasicRowStack.doubleclickHandler(self, event)

    getBottomImage = Stack._getReserveBottomImage

    def getHelp(self):
        return _('Tableau. Build regardless of rank and suit.')


class Strategy(Game):
    Hint_Class = Numerica_Hint

    def createGame(self, rows=8):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + rows*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = OpenTalonStack(x, y, self)
        l.createText(s.talon, "se")
        for i in range(4):
            x, y = l.XM + (i+2)*l.XS, l.YM
            s.foundations.append(Strategy_Foundation(x, y, self, suit=i, max_move=0))
        x, y = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(Strategy_RowStack(x, y,
                                            self, max_move=1, max_accept=1))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()
        self.sg.dropstacks.append(s.talon)

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.fillStack()


class StrategyPlus(Strategy):

    def createGame(self):
        Strategy.createGame(self, rows=6)

    def _shuffleHook(self, cards):
        return cards

    def startGame(self):
        self.s.talon.fillStack()

    def fillStack(self, stack):
        if stack is self.s.talon and stack.cards:
            old_state = self.enterState(self.S_FILL)
            c = stack.cards[-1]
            while c.rank == ACE:
                self.moveMove(1, stack, self.s.foundations[c.suit])
                if stack.canFlipCard():
                    stack.flipMove(animation=True)
                if not stack.cards:
                    break
                c = stack.cards[-1]
            self.leaveState(old_state)


# ************************************************************************
# * Interregnum
# ************************************************************************

class Interregnum_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if len(self.cards) == 12:
            # the final card must come from the reserve above the foundation
            return from_stack.id == self.id - 8
        else:
            # card must come from rows
            return from_stack in self.game.s.rows


class Interregnum(Game):
    GAME_VERSION = 2

    Talon_Class = DealRowTalonStack
    RowStack_Class = StackWrapper(BasicRowStack, max_accept=0, max_move=1)

    #
    # game layout
    #

    def createGame(self, rows=8, playcards=12, texts=False):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+max(9,rows)*l.XS, l.YM+3*l.YS+playcards*l.YOFFSET)

        # extra settings
        self.base_cards = None

        # create stacks
        for i in range(8):
            x, y, = l.XM + i*l.XS, l.YM
            s.reserves.append(ReserveStack(x, y, self, max_accept=0))
        for i in range(8):
            x, y, = l.XM + i*l.XS, l.YM + l.YS
            s.foundations.append(Interregnum_Foundation(x, y, self, mod=13, max_move=0))
        for i in range(rows):
            x, y, = l.XM + (2*i+8-rows)*l.XS/2, l.YM + 2*l.YS
            s.rows.append(self.RowStack_Class(x, y, self))
        s.talon = self.Talon_Class(self.width-l.XS, self.height-l.YS, self)
        if texts:
            l.createRoundText(s.talon, 'nn')
        else:
            l.createText(s.talon, "n")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        # deal base_cards to reserves, update foundations cap.base_rank
        self.base_cards = []
        for i in range(8):
            self.base_cards.append(self.s.talon.getCard())
            self.s.foundations[i].cap.base_rank = (self.base_cards[i].rank + 1) % 13
            self.flipMove(self.s.talon)
            self.moveMove(1, self.s.talon, self.s.reserves[i])

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)

    shallHighlightMatch = Game._shallHighlightMatch_RKW

    def _restoreGameHook(self, game):
        self.base_cards = [None] * 8
        for i in range(8):
            id = game.loadinfo.base_card_ids[i]
            self.base_cards[i] = self.cards[id]
            self.s.foundations[i].cap.base_rank = (self.base_cards[i].rank + 1) % 13

    def _loadGameHook(self, p):
        ids = []
        for i in range(8):
            ids.append(p.load())
        self.loadinfo.addattr(base_card_ids=ids)    # register extra load var.

    def _saveGameHook(self, p):
        for c in self.base_cards:
            p.dump(c.id)


# ************************************************************************
# * Primrose
# ************************************************************************

class Primrose_Talon(DealRowTalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds and not self.cards:
            return False
        return not self.game.isGameWon()

    def _redeal(self):
        lr = len(self.game.s.rows)
        rows = self.game.s.rows
        r = self.game.s.rows[self.round-1]
        for i in range(len(r.cards)):
            self.game.moveMove(1, r, self, frames=4)
            self.game.flipMove(self)
        self.game.nextRoundMove(self)

    def dealCards(self, sound=False):
        if sound:
            self.game.startDealSample()
        if len(self.cards) == 0:
            self._redeal()
        if self.round == 1:
            n = self.dealRowAvail(sound=False)
        else:
            rows = self.game.s.rows
            n = self.dealRowAvail(rows=rows[self.round-2:], sound=False)
            #n = 0
            while self.cards:
                n += self.dealRowAvail(rows=rows, sound=False)
        if sound:
            self.game.stopSamples()
        return n


class Primrose(Interregnum):
    Talon_Class = StackWrapper(Primrose_Talon, max_rounds=9)

    def createGame(self):
        Interregnum.createGame(self, playcards=16, texts=True)

    def startGame(self):
        for i in range(11):
            self.s.talon.dealRow(frames=0)
        Interregnum.startGame(self)


# ************************************************************************
# * Colorado
# ************************************************************************

class Colorado_RowStack(OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts any one card from the Waste
        return from_stack is self.game.s.waste and len(cards) == 1


class Colorado(Game):

    Foundation_Class = SS_FoundationStack
    RowStack_Class = Colorado_RowStack

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+10*l.XS, l.YM+4*l.YS+l.TEXT_HEIGHT)

        # create stacks
        x, y, = l.XS, l.YM
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self,
                                 suit=i, max_move=0))
            x += l.XS
        x += 2*l.XM
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self,
                                 suit=i, max_move=0, base_rank=KING, dir=-1))
            x += l.XS

        y = l.YM+l.YS
        for i in range(2):
            x = l.XM
            for j in range(10):
                stack = self.RowStack_Class(x, y, self,
                                            max_move=1, max_accept=1)
                s.rows.append(stack)
                stack.CARD_XOFFSET = stack.CARD_YOFFSET = 0
                x += l.XS
            y += l.YS

        x, y = l.XM + 9*l.XS, self.height - l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "n")
        x -= l.XS
        s.waste = WasteStack(x, y, self, max_cards=1)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards, lambda c: (c.deck == 0 and c.rank in (0, 12), (c.rank, c.suit)), 8)

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards and self.s.waste.cards:
            self.s.waste.moveMove(1, stack)


# ************************************************************************
# * Amazons
# ************************************************************************

class Amazons_Talon(RedealTalonStack):

    def canDealCards(self):
        return not self.game.isGameWon()

    def dealCards(self, sound=False):
        if not self.cards:
            RedealTalonStack.redealCards(self, frames=4, sound=sound)
        return self.dealRowAvail(sound=sound)

    def dealRowAvail(self, rows=None, flip=1, reverse=0, frames=-1, sound=False):
        if rows is None:
            rows = []
            i = 0
            for f in self.game.s.foundations:
                if len(f.cards) < 7:
                    rows.append(self.game.s.rows[i])
                i += 1
        return RedealTalonStack.dealRowAvail(self, rows=rows, flip=flip,
                   reverse=reverse, frames=frames, sound=sound)


class Amazons_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack not in self.game.s.rows:
            return False
        if cards[0].rank == ACE:
            return True
        if not self.cards:
            return False
        rank = self.cards[-1].rank
        if rank == ACE:
            rank = 5
        if (rank + self.cap.dir) % self.cap.mod != cards[0].rank:
            return False
        if cards[0].rank == QUEEN:
            return True
        i = list(self.game.s.foundations).index(self)
        j = list(self.game.s.rows).index(from_stack)
        return i == j


class Amazons(AuldLangSyne):
    Talon_Class = StackWrapper(Amazons_Talon, max_rounds=-1)
    Foundation_Class = StackWrapper(Amazons_Foundation, max_cards=7)

    def _shuffleHook(self, cards):
        return cards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Scuffle
# * Acquaintance
# ************************************************************************

class Scuffle_Talon(RedealTalonStack):

    def canDealCards(self):
        if self.round == self.max_rounds:
            return len(self.cards) != 0
        return not self.game.isGameWon()

    def dealCards(self, sound=False, shuffle=True):
        if self.cards:
            return self.dealRowAvail(sound=sound)
        self.redealCards(frames=4, shuffle=shuffle, sound=sound)
        return self.dealRowAvail(sound=sound)


class Scuffle(AuldLangSyne):
    Talon_Class = StackWrapper(Scuffle_Talon, max_rounds=3)
    def createGame(self):
        AuldLangSyne.createGame(self, texts=True, yoffset=0)


class Acquaintance_Talon(Scuffle_Talon):
    def dealCards(self, sound=False):
        Scuffle_Talon.dealCards(self, sound=sound, shuffle=False)


class Acquaintance(AuldLangSyne):
    Talon_Class = StackWrapper(Acquaintance_Talon, max_rounds=3)
    def createGame(self, texts=False, yoffset=None):
        AuldLangSyne.createGame(self, texts=True)


class DoubleAcquaintance(AuldLangSyne):
    Talon_Class = StackWrapper(Acquaintance_Talon, max_rounds=3)
    def createGame(self):
        AuldLangSyne.createGame(self, rows=8, texts=True)


# ************************************************************************
# * Formic
# ************************************************************************

class Formic_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        return ((self.cards[-1].rank+1) % 13 == cards[0].rank or
                (self.cards[-1].rank-1) % 13 == cards[0].rank)

    def getHelp(self):
        return _('Foundation. Build up or down regardless of suit.')


class Formic(TamOShanter):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+6*l.XS, l.YM+2*l.YS+12*l.YOFFSET)

        x, y, = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, "s")
        x, y = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(Formic_Foundation(x, y, self,
                                 suit=ANY_SUIT, base_rank=ANY_RANK,
                                 max_cards=52, max_move=0))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            s.rows.append(BasicRowStack(x, y, self, max_move=1, max_accept=0))
            x += l.XS

        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        suits = []
        top_cards = []
        for c in cards[:]:
            if c.suit not in suits:
                suits.append(c.suit)
                top_cards.append(c)
                cards.remove(c)
            if len(suits) == 4:
                break
        top_cards.sort(lambda a, b: cmp(b.suit, a.suit)) # sort by suit
        return cards+top_cards

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()



# register the game
registerGame(GameInfo(172, TamOShanter, "Tam O'Shanter",
                      GI.GT_NUMERICA, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(95, AuldLangSyne, "Auld Lang Syne",
                      GI.GT_NUMERICA, 1, 0, GI.SL_LUCK,
                      altnames=("Patience",) ))
registerGame(GameInfo(173, Strategy, "Strategy",
                      GI.GT_NUMERICA, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(123, Interregnum, "Interregnum",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(296, Colorado, "Colorado",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(406, Amazons, "Amazons",
                      GI.GT_NUMERICA, 1, -1, GI.SL_LUCK,
                      ranks=(0, 6, 7, 8, 9, 10, 11),
                      ))
registerGame(GameInfo(490, Acquaintance, "Acquaintance",
                      GI.GT_NUMERICA, 1, 2, GI.SL_BALANCED))
registerGame(GameInfo(553, Scuffle, "Scuffle",
                      GI.GT_NUMERICA, 1, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(560, DoubleAcquaintance, "Double Acquaintance",
                      GI.GT_NUMERICA, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(569, Primrose, "Primrose",
                      GI.GT_NUMERICA, 2, 8, GI.SL_BALANCED))
registerGame(GameInfo(636, StrategyPlus, "Strategy +",
                      GI.GT_NUMERICA, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(688, Formic, "Formic",
                      GI.GT_NUMERICA, 1, 0, GI.SL_MOSTLY_SKILL))

