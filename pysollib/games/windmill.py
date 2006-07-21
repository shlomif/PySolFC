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
# //
# ************************************************************************/

class Windmill_Foundation(RK_FoundationStack):
    def getBottomImage(self):
        if self.cap.base_rank == ACE:
            return self.game.app.images.getLetter(ACE)
        return RK_FoundationStack.getBottomImage(self)


class Windmill_RowStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return 0
        # this stack accepts one card from the Waste pile
        return from_stack is self.game.s.waste


# /***********************************************************************
# // Windmill
# ************************************************************************/

class Windmill(Game):

    FILL_STACK = True

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, card_x_space=20), self.s

        # set window
        self.setSize(7*l.XS+l.XM, 5*l.YS+l.YM+l.YM)

        # create stacks
        x = l.XM
        y = l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "ss")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")
        x0, y0 = x + l.XS, y
        for d in ((2,0), (2,1), (0,2), (1,2), (3,2), (4,2), (2,3), (2,4)):
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            s.rows.append(Windmill_RowStack(x, y, self))
        x, y = x0 + 2 * l.XS, y0 + 2 * l.YS
        s.foundations.append(Windmill_Foundation(x, y, self,
                             mod=13, min_cards=1, max_cards=52))
        for d in ((1,0.6), (3,0.6), (1,3.4), (3,3.4)):
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            s.foundations.append(Windmill_Foundation(x, y, self,
                                 base_rank=KING, dir=-1))

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        for c in cards:
            if c.id == 0:
                break
        cards.remove(c)
        return cards + [c]

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=(self.s.foundations[0],))
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if self.FILL_STACK and len(stack.cards) == 0:
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank)

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        # disable auto drop - this would ruin the whole gameplay
        return ((), (), ())



# /***********************************************************************
# // Napoleon's Tomb
# ************************************************************************/

class NapoleonsTomb(Windmill):

    FILL_STACK = False

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, card_x_space=20, card_y_space=20), self.s

        # set window
        self.setSize(5*l.XS+l.XM, 3*l.YS+l.YM+l.YM)

        # create stacks
        x = l.XM
        y = l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "ss")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")
        x0, y0 = x + l.XS, y
        for d in ((0,1), (1,0), (1,2), (2,1)):
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            s.rows.append(Windmill_RowStack(x, y, self))
        x, y = x0 + l.XS, y0 + l.YS
        s.foundations.append(Windmill_Foundation(x, y, self, base_rank=5,
                             mod=6, min_cards=1, max_cards=24,
                             max_move=0, dir=-1))
        for d in ((0.1, 0.1), (1.9, 0.1), (0.1, 1.9), (1.9, 1.9)):
            x, y = x0 + d[0] * l.XS, y0 + d[1] * l.YS
            s.foundations.append(Windmill_Foundation(x, y, self,
                                 max_cards=7, base_rank=6, max_move=0))

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        return cards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Corners
# ************************************************************************/

class Corners(Game):
    RowStack_Class = ReserveStack

    def createGame(self, max_rounds=3):
        # create layout
        l, s = Layout(self, card_x_space=20, card_y_space=20), self.s

        # set window
        self.setSize(5*l.XS+l.XM, 4*l.YS+3*l.YM)

        # create stacks
        x, y = l.XM+l.XS, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, "sw")
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "se")
        x0, y0 = l.XM, l.YM+l.YS
        i = 0
        for d in ((0,0), (4,0), (0,2), (4,2)):
            x, y = x0+d[0]*l.XS, y0+d[1]*l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    max_move=0, mod=13))
            i += 1
        for d in ((2,0), (1,1), (2,1), (3,1), (2,2)):
            x, y = x0+d[0]*l.XS, y0+d[1]*l.YS
            stack = self.RowStack_Class(x, y, self)
            s.rows.append(stack)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0

        # define stack-groups
        l.defaultStackGroups()


    def fillStack(self, stack):
        if len(stack.cards) == 0:
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)


    def _shuffleHook(self, cards):
        suits = []
        top_cards = []
        for c in cards[:]:
            if c.suit not in suits:
                suits.append(c.suit)
                cards.remove(c)
                top_cards.append(c)
                if len(suits) == 4:
                    break
        top_cards.sort(lambda a, b: cmp(b.suit, a.suit))
        return cards+top_cards


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Czarina
# // Four Seasons
# ************************************************************************/

class Czarina_RowStack(RK_RowStack):
    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class Czarina(Corners):
    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(Czarina_RowStack, mod=13, max_move=1)

    def createGame(self):
        # extra settings
        self.base_card = None
        Corners.createGame(self, max_rounds=1)

    def startGame(self):
        self.startDealSample()
        self.base_card = None
        # deal base_card to Foundations, update foundations cap.base_rank
        self.base_card = self.s.talon.getCard()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, self.s.foundations[self.base_card.suit])
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first 3 cards to WasteStack

    def _shuffleHook(self, cards):
        return cards

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1) % 13 == card2.rank or
                (card2.rank + 1) % 13 == card1.rank)

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


class FourSeasons(Czarina):
    def fillStack(self, stack):
        pass


# register the game
registerGame(GameInfo(30, Windmill, "Windmill",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(277, NapoleonsTomb, "Napoleon's Tomb",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(417, Corners, "Corners",
                      GI.GT_1DECK_TYPE, 1, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(483, Czarina, "Czarina",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(484, FourSeasons, "Four Seasons",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))

