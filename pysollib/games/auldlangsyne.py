## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
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

# /***********************************************************************
# // Tam O'Shanter
# ************************************************************************/

class TamOShanter(Game):
    Talon_Class = DealRowTalonStack
    RowStack_Class = StackWrapper(BasicRowStack, max_move=1, max_accept=0)

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 6*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, "ss")
        x, y = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(RK_FoundationStack(x, y, self))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            s.rows.append(self.RowStack_Class(x, y, self))
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


# /***********************************************************************
# // Auld Lang Syne
# ************************************************************************/

class AuldLangSyne(TamOShanter):
    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

# /***********************************************************************
# // Strategy
# ************************************************************************/

class Strategy_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # we only accept cards if there are no cards in the talon
        return len(self.game.s.talon.cards) == 0


class Strategy_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        # this stack accepts any one card from the Talon
        return from_stack is self.game.s.talon and len(cards) == 1

    def canMoveCards(self, cards):
        if self.game.s.talon.cards:
            return 0
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

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()

    def getHelp(self):
        return _('Row. Build regardless of rank and suit.')


class Strategy(Game):
    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 8*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = OpenTalonStack(x, y, self)
        l.createText(s.talon, "se")
        for i in range(4):
            x, y = l.XM + (i+2)*l.XS, l.YM
            s.foundations.append(Strategy_Foundation(x, y, self, suit=i, max_move=0))
        for i in range(8):
            x, y = l.XM + i*l.XS, l.YM + l.YS
            s.rows.append(Strategy_RowStack(x, y, self, max_move=1, max_accept=1))
            x = x + l.XS

        # define stack-groups
        l.defaultStackGroups()

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


# /***********************************************************************
# // Interregnum
# ************************************************************************/

class Interregnum_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if len(self.cards) == 12:
            # the final card must come from the reserve above the foundation
            return from_stack.id == self.id - 8
        else:
            # card must come from rows
            return from_stack in self.game.s.rows


class Interregnum(Game):
    GAME_VERSION = 2

    #
    # game layout
    #

    def createGame(self, rows=8):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + max(9,rows)*l.XS, l.YM + 5*l.YS)

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
            s.rows.append(BasicRowStack(x, y, self, max_accept=0, max_move=1))
        s.talon = DealRowTalonStack(self.width-l.XS, self.height-l.YS, self)
        l.createText(s.talon, "nn")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        # deal base_cards to reserves, update foundations cap.base_rank
        self.base_cards = []
        for i in range(8):
            self.base_cards.append(self.s.talon.getCard())
            self.s.foundations[i].cap.base_rank = (self.base_cards[i].rank + 1) % 13
            self.flipMove(self.s.talon)
            self.moveMove(1, self.s.talon, self.s.reserves[i])
        # deal other cards
        self.s.talon.dealRow()

    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1) % 13 == card2.rank or (card2.rank + 1) % 13 == card1.rank)

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

# /***********************************************************************
# // Colorado
# ************************************************************************/

class Colorado_RowStack(OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return 0
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
        self.setSize(l.XM+10*l.XS, 3*l.YM+4*l.YS)

        # create stacks
        x, y, = l.XS, l.YM
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self,
                                 suit=i, max_move=0))
            x = x + l.XS
        x += 2*l.XM
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self,
                                 suit=i, max_move=0, base_rank=KING, dir=-1))
            x = x + l.XS

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

        x, y = l.XM+9*l.XS, l.YM+3*l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "ss")
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


# /***********************************************************************
# // Amazons
# ************************************************************************/

class Amazons_Talon(DealRowTalonStack):
    def canDealCards(self):
        ## FIXME: this is to avoid loops in the demo
        if self.game.demo and self.game.moves.index >= 100:
            return False
        if self.round == self.max_rounds:
            return False
        return not self.game.isGameWon()

    def dealCards(self, sound=0):
        self.game.startDealSample()
        if not self.cards:
            self.game.nextRoundMove(self)
            n = self._moveAllToTalon()
            self.game.stopSamples()
            return n
        n = self.dealRowAvail()
        self.game.stopSamples()
        return n

    def dealRowAvail(self, rows=None, flip=1, reverse=0, frames=-1, sound=0):
        if rows is None:
            rows = []
            i = 0
            for f in self.game.s.foundations:
                if len(f.cards) < 7:
                    rows.append(self.game.s.rows[i])
                i += 1
        return DealRowTalonStack.dealRowAvail(self, rows=rows, flip=flip,
                   reverse=reverse, frames=frames, sound=sound)

    def _moveAllToTalon(self):
        # move all cards to the Talon
        num_cards = 0
        for r in self.game.s.rows:
            for i in range(len(r.cards)):
                num_cards += 1
                self.game.moveMove(1, r, self, frames=4)
                self.game.flipMove(self)
        return num_cards


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
        i = list(self.game.s.foundations).index(self)
        j = list(self.game.s.rows).index(from_stack)
        return i == j


class Amazons(Game):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 6*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = Amazons_Talon(x, y, self, max_rounds=-1)
        l.createText(s.talon, "ss")
        x, y = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(Amazons_Foundation(x, y, self, suit=i))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(4):
            s.rows.append(BasicRowStack(x, y, self, max_move=1, max_accept=0))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


    def getAutoStacks(self, event=None):
        return ((), (), self.sg.dropstacks)


# /***********************************************************************
# // Acquaintance
# ************************************************************************/

class Acquaintance_Talon(TalonStack): # TalonStack

    def canDealCards(self):
        if self.round == self.max_rounds and not self.cards:
            return False
        return not self.game.isGameWon()

    def _redeal(self):
        # move all cards to the Talon
        lr = len(self.game.s.rows)
        num_cards = 0
        assert len(self.cards) == 0
        rows = self.game.s.rows
        for r in rows:
            for i in range(len(r.cards)):
                num_cards = num_cards + 1
                self.game.moveMove(1, r, self, frames=4)
                self.game.flipMove(self)
        assert len(self.cards) == num_cards
        if num_cards == 0:          # game already finished
            return
        self.game.nextRoundMove(self)

    def dealCards(self, sound=0):
        if sound:
            self.game.startDealSample()
        if len(self.cards) == 0:
            self._redeal()
        n = self.dealRowAvail(sound=sound)
        if sound:
            self.game.stopSamples()
        return n

class Acquaintance(AuldLangSyne):
    Talon_Class = StackWrapper(Acquaintance_Talon, max_rounds=3)


# register the game
registerGame(GameInfo(172, TamOShanter, "Tam O'Shanter",
                      GI.GT_NUMERICA, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(95, AuldLangSyne, "Auld Lang Syne",
                      GI.GT_NUMERICA, 1, 0, GI.SL_LUCK))
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

