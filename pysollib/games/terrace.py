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
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# /***********************************************************************
# //
# ************************************************************************/

class Terrace_Talon(WasteTalonStack):
    def canDealCards(self):
        if self.game.getState() == 0:
            return 0
        return WasteTalonStack.canDealCards(self)


class Terrace_AC_Foundation(AC_FoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=13, min_cards=1, max_move=0)
        apply(AC_FoundationStack.__init__, (self, x, y, game, suit), cap)

    def acceptsCards(self, from_stack, cards):
        if self.game.getState() == 0:
            if len(cards) != 1 or not cards[0].face_up:
                return 0
            if cards[0].suit != self.cap.base_suit:
                return 0
            return from_stack in self.game.s.rows
        return AC_FoundationStack.acceptsCards(self, from_stack, cards)


class Terrace_SS_Foundation(SS_FoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=13, min_cards=1, max_move=0)
        apply(SS_FoundationStack.__init__, (self, x, y, game, suit), cap)

    def acceptsCards(self, from_stack, cards):
        if self.game.getState() == 0:
            if len(cards) != 1 or not cards[0].face_up:
                return 0
            if cards[0].suit != self.cap.base_suit:
                return 0
            return from_stack in self.game.s.rows
        return SS_FoundationStack.acceptsCards(self, from_stack, cards)


class Terrace_RowStack(AC_RowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, mod=13, max_move=1)
        apply(AC_RowStack.__init__, (self, x, y, game), cap)

    def acceptsCards(self, from_stack, cards):
        if self.game.getState() == 0:
            return 0
        if from_stack in self.game.s.reserves:
            return 0
        return AC_RowStack.acceptsCards(self, from_stack, cards)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        state = self.game.getState()
        if state > 0:
            AC_RowStack.moveMove(self, ncards, to_stack, frames=frames, shadow=shadow)
            return
        assert to_stack in self.game.s.foundations
        assert ncards == 1
        assert not self.game.s.waste.cards
        self.game.moveMove(ncards, self, to_stack, frames=frames, shadow=shadow)
        for s in self.game.s.foundations:
            s.cap.base_rank = to_stack.cards[0].rank
        freerows = filter(lambda s: not s.cards, self.game.s.rows)
        self.game.s.talon.dealRow(rows=freerows, sound=1)
        self.game.s.talon.dealCards()     # deal first card to WasteStack


    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


# /***********************************************************************
# // Terrace
# ************************************************************************/

class Terrace(Game):
    Foundation_Class = Terrace_AC_Foundation
    RowStack_Class = Terrace_RowStack
    ReserveStack_Class = OpenStack
    Hint_Class = CautiousDefaultHint

    INITIAL_RESERVE_CARDS = 11

    #
    # game layout
    #

    def createGame(self, rows=9, max_rounds=1, num_deal=1, playcards=16):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 16 cards are playable in default window size)
        decks = self.gameinfo.decks
        maxrows = max(rows, decks*4+1)
        w1, w2 = (maxrows - decks*4)*l.XS/2, (maxrows - rows)*l.XS/2
        h = max(3*l.YS, playcards*l.YOFFSET)
        self.setSize(l.XM + maxrows*l.XS + l.XM, l.YM + 3*l.YS + h)

        # extra settings
        self.base_card = None

        # create stacks
        x, y = l.XM + w1, l.YM
        s.talon = Terrace_Talon(x, y, self, max_rounds=max_rounds, num_deal=num_deal)
        l.createText(s.talon, "sw")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se", text_format="%D")
        x = x + 2*l.XS
        stack = self.ReserveStack_Class(x, y, self)
        stack.CARD_XOFFSET = l.XOFFSET
        l.createText(stack, "sw")
        s.reserves.append(stack)
        x, y = l.XM + w1, y + l.YS
        for i in range(4):
            for j in range(decks):
                s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
                x = x + l.XS
        x, y = l.XM + w2, y + l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS

        # define stack-groups
        l.defaultStackGroups()

    #
    # game extras
    #

    def getState(self):
        for s in self.s.foundations:
            if s.cards:
                return 1
        return 0

    #
    # game overrides
    #

    def startGame(self, nrows=4):
        self.startDealSample()
        for i in range(self.INITIAL_RESERVE_CARDS):
            self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow(rows=self.s.rows[:nrows])

    def fillStack(self, stack):
        if not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)

    def _restoreGameHook(self, game):
        for s in self.s.foundations:
            s.cap.base_rank = game.loadinfo.base_rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_rank=p.load())

    def _saveGameHook(self, p):
        base_rank = NO_RANK
        for s in self.s.foundations:
            if s.cards:
                base_rank = s.cards[0].rank
                break
        p.dump(base_rank)


# /***********************************************************************
# // Queen of Italy
# ************************************************************************/

class QueenOfItaly(Terrace):
    Foundation_Class = StackWrapper(Terrace_AC_Foundation, max_move=1)
    def fillStack(self, stack):
        pass


# /***********************************************************************
# // General's Patience
# ************************************************************************/

class GeneralsPatience(Terrace):
    Foundation_Class = Terrace_SS_Foundation
    INITIAL_RESERVE_CARDS = 13


# /***********************************************************************
# // Blondes and Brunettes
# ************************************************************************/

class BlondesAndBrunettes(Terrace):
    INITIAL_RESERVE_CARDS = 10

    def startGame(self):
        self.startDealSample()
        for i in range(self.INITIAL_RESERVE_CARDS):
            self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow()
        # deal base_card to Foundations
        c = self.s.talon.getCard()
        for s in self.s.foundations:
            s.cap.base_rank = c.rank
        self.s.talon.dealRow(rows=(self.s.foundations[2*c.suit],))
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getState(self):
        return 1


# /***********************************************************************
# // Falling Star
# ************************************************************************/

class FallingStar(BlondesAndBrunettes):
    INITIAL_RESERVE_CARDS = 11


# /***********************************************************************
# // Signora
# ************************************************************************/

class Signora(Terrace):
    def startGame(self):
        Terrace.startGame(self, nrows=9)


# /***********************************************************************
# // Madame
# ************************************************************************/

class Madame(Terrace):
    INITIAL_RESERVE_CARDS = 15
    def createGame(self):
        Terrace.createGame(self, rows=10, playcards=20)
    def startGame(self):
        Terrace.startGame(self, nrows=10)



# register the game
registerGame(GameInfo(135, Terrace, "Terrace",
                      GI.GT_TERRACE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(136, GeneralsPatience, "General's Patience",
                      GI.GT_TERRACE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(137, BlondesAndBrunettes, "Blondes and Brunettes",
                      GI.GT_TERRACE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(138, FallingStar, "Falling Star",
                      GI.GT_TERRACE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(431, QueenOfItaly, "Queen of Italy",
                      GI.GT_TERRACE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(499, Signora, "Signora",
                      GI.GT_TERRACE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(500, Madame, "Madame",
                      GI.GT_TERRACE, 3, 0, GI.SL_MOSTLY_SKILL))

