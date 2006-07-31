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
from pysollib.pysoltk import MfxCanvasText


# /***********************************************************************
# //
# ************************************************************************/

class Pyramid_Hint(DefaultHint):
    # consider moving card to the Talon as well
    def step010(self, dropstacks, rows):
        rows = rows + (self.game.s.talon,)
        return DefaultHint.step010(self, dropstacks, rows)


# /***********************************************************************
# // basic logic for Talon, Waste and Rows
# ************************************************************************/

class Pyramid_StackMethods:
    def acceptsCards(self, from_stack, cards):
        if self.basicIsBlocked():
            return 0
        if from_stack is self or not self.cards or len(cards) != 1:
            return 0
        c = self.cards[-1]
        return c.face_up and cards[0].face_up and cards[0].rank + c.rank == 11

    def _dropKingClickHandler(self, event):
        if not self.cards:
            return 0
        c = self.cards[-1]
        if c.face_up and c.rank == KING and not self.basicIsBlocked():
            self.game.playSample("autodrop", priority=20)
            self.playMoveMove(1, self.game.s.foundations[0], sound=0)
            return 1
        return 0

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        if not self.game.demo:
            self.game.playSample("droppair", priority=200)
        assert n == 1 and self.acceptsCards(other_stack, [other_stack.cards[-1]])
        old_state = self.game.enterState(self.game.S_FILL)
        f = self.game.s.foundations[0]
        self.game.moveMove(n, self, f, frames=frames, shadow=shadow)
        self.game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.game.leaveState(old_state)
        self.fillStack()
        other_stack.fillStack()

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if to_stack in self.game.s.foundations:
            self.game.moveMove(ncards, self, to_stack, frames=frames, shadow=shadow)
            self.fillStack()
        else:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)


# /***********************************************************************
# //
# ************************************************************************/

class Pyramid_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # We accept any King. Pairs will get delivered by _dropPairMove.
        return cards[0].rank == KING


# note that this Talon can accept and drop cards
class Pyramid_Talon(Pyramid_StackMethods, FaceUpWasteTalonStack):
    def clickHandler(self, event):
        if self._dropKingClickHandler(event):
            return 1
        return FaceUpWasteTalonStack.clickHandler(self, event)

    def canDealCards(self):
        if not FaceUpWasteTalonStack.canDealCards(self):
            return 0
        return not self.game.isGameWon()

    def canDropCards(self, stacks):
        if self.cards:
            cards = self.cards[-1:]
            for s in stacks:
                if s is not self and s.acceptsCards(self, cards):
                    return (s, 1)
        return (None, 0)


class Pyramid_Waste(Pyramid_StackMethods, WasteStack):
    def clickHandler(self, event):
        if self._dropKingClickHandler(event):
            return 1
        return WasteStack.clickHandler(self, event)


class Pyramid_RowStack(Pyramid_StackMethods, OpenStack):
    def __init__(self, x, y, game):
        OpenStack.__init__(self, x, y, game, max_accept=1, max_cards=2)
        self.CARD_YOFFSET = 1

    STEP = (1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6)

    def basicIsBlocked(self):
        r, step = self.game.s.rows, self.STEP
        i, n = self.id, 1
        while i < 21:
            i = i + step[i]
            n = n + 1
            for j in range(i, i+n):
                if r[j].cards:
                    return 1
        return 0

    def clickHandler(self, event):
        if self._dropKingClickHandler(event):
            return 1
        return OpenStack.clickHandler(self, event)


# /***********************************************************************
# // Pyramid
# ************************************************************************/

class Pyramid(Game):
    Hint_Class = Pyramid_Hint
    Talon_Class = StackWrapper(Pyramid_Talon, max_rounds=3, max_accept=1)

    #
    # game layout
    #

    def createGame(self, rows=4, reserves=0, waste=True, texts=True):
        # create layout
        l, s = Layout(self), self.s

        # set window
        max_rows = max(9, reserves)
        w = l.XM + max_rows*l.XS
        h = l.YM + 4*l.YS
        if reserves:
            h += l.YS+2*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        for i in range(7):
            x = l.XM + (8-i) * l.XS / 2
            y = l.YM + i * l.YS / 2
            for j in range(i+1):
                s.rows.append(Pyramid_RowStack(x, y, self))
                x = x + l.XS

        x, y = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        if texts:
            l.createText(s.talon, "se")
            tx, ty, ta, tf = l.getTextAttr(s.talon, "ne")
            font=self.app.getFont("canvas_default")
            s.talon.texts.rounds = MfxCanvasText(self.canvas, tx, ty,
                                                 anchor=ta, font=font)
        if waste:
            y = y + l.YS
            s.waste = Pyramid_Waste(x, y, self, max_accept=1)
            l.createText(s.waste, "se")
        x, y = self.width - l.XS, l.YM
        s.foundations.append(Pyramid_Foundation(x, y, self,
                                suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                                max_move=0, max_cards=52))
        if reserves:
            x, y = l.XM+(max_rows-reserves)*l.XS/2, l.YM+4*l.YS
            for i in range(reserves):
                stack = self.Reserve_Class(x, y, self)
                s.reserves.append(stack)
                stack.CARD_YOFFSET = l.YOFFSET
                x += l.XS

        # define stack-groups
        l.defaultStackGroups()
        self.sg.openstacks.append(s.talon)
        self.sg.dropstacks.append(s.talon)


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getAutoStacks(self, event=None):
        return (self.sg.dropstacks, self.sg.dropstacks, ())

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + card2.rank == 11


# /***********************************************************************
# // Relaxed Pyramid
# ************************************************************************/

class RelaxedPyramid(Pyramid):
    # the pyramid must be empty
    def isGameWon(self):
        return getNumberOfFreeStacks(self.s.rows) == len(self.s.rows)


# /***********************************************************************
# // Giza
# ************************************************************************/

class Giza_Reserve(Pyramid_StackMethods, OpenStack):
    def clickHandler(self, event):
        if self._dropKingClickHandler(event):
            return 1
        return OpenStack.clickHandler(self, event)


class Giza(Pyramid):
    Talon_Class = InitialDealTalonStack
    Reserve_Class = StackWrapper(Giza_Reserve, max_accept=1)

    def createGame(self):
        Pyramid.createGame(self, reserves=8, waste=False, texts=False)

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Thirteen
# // FIXME: UNFINISHED
# // (this doesn't work yet as 2 cards of the Waste should be playable)
# ************************************************************************/
# Thirteen #89404422185320919548

class Thirteen(Pyramid):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(7*l.XS+l.XM, 5*l.YS+l.YM)

        # create stacks
        for i in range(7):
            x = l.XM + (6-i) * l.XS / 2
            y = l.YM + l.YS + i * l.YS / 2
            for j in range(i+1):
                s.rows.append(Pyramid_RowStack(x, y, self))
                x = x + l.XS
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = Pyramid_Waste(x, y, self)
        l.createText(s.waste, "s")
        s.waste.CARD_XOFFSET = 14
        x, y = self.width - l.XS, l.YM
        s.foundations.append(Pyramid_Foundation(x, y, self,
                                suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                                max_move=0, max_cards=UNLIMITED_CARDS))

        # define stack-groups
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.openstacks = s.rows + self.sg.talonstacks
        self.sg.dropstacks = s.rows + self.sg.talonstacks


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:21], flip=0)
        self.s.talon.dealRow(rows=self.s.rows[21:])
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Thirteens
# ************************************************************************/

class Thirteens(Pyramid):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+5*l.XS, l.YM+4*l.YS)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(2):
            x = l.XM
            for j in range(5):
                s.rows.append(Giza_Reserve(x, y, self, max_accept=1))
                x += l.XS
            y += l.YS
        x, y = l.XM, self.height-l.YS
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, 'n')
        x, y = self.width-l.XS, self.height-l.YS
        s.foundations.append(Pyramid_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.rows:
            if not stack.cards and self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

# /***********************************************************************
# // Elevens
# // Suit Elevens
# ************************************************************************/

class Elevens_RowStack(Giza_Reserve):
    ACCEPTED_SUM = 9

    def acceptsCards(self, from_stack, cards):
        #if self.basicIsBlocked():
        #    return 0
        if from_stack is self or not self.cards or len(cards) != 1:
            return False
        c = self.cards[-1]
        return (c.face_up and cards[0].face_up
                and cards[0].rank + c.rank == self.ACCEPTED_SUM)

    def clickHandler(self, event):
        return OpenStack.clickHandler(self, event)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if to_stack in self.game.s.rows:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            self.game.moveMove(ncards, self, to_stack,
                               frames=frames, shadow=shadow)
            self.fillStack()


class Elevens_Reserve(ReserveStack):
    ACCEPTED_CARDS = (JACK, QUEEN, KING)

    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        c = cards[0]
        if not c.rank in self.ACCEPTED_CARDS:
            return False
        for s in self.game.s.reserves:
            if s.cards and s.cards[0].rank == c.rank:
                return False
        return True


class Elevens(Pyramid):

    RowStack_Class = Elevens_RowStack
    Reserve_Class = Elevens_Reserve

    def createGame(self, rows=3, cols=3, reserves=3, texts=False):

        l, s = Layout(self), self.s

        self.setSize(l.XM+(cols+2)*l.XS, l.YM+(rows+1.5)*l.YS)

        x, y = self.width-l.XS, l.YM
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, 's')
        x, y = self.width-l.XS, self.height-l.YS
        s.foundations.append(AbstractFoundationStack(x, y, self,
                             suit=ANY_SUIT, max_accept=0,
                             max_move=0, max_cards=52))
        y = l.YM
        for i in range(rows):
            x = l.XM
            for j in range(cols):
                s.rows.append(self.RowStack_Class(x, y, self, max_accept=1))
                x += l.XS
            y += l.YS
        x, y = l.XM, self.height-l.YS
        for i in range(reserves):
            stack = self.Reserve_Class(x, y, self)
            s.reserves.append(stack)
            stack.CARD_XOFFSET = l.XOFFSET # for fifteens
            x += l.XS

        if texts:
            stack = s.reserves[0]
            tx, ty, ta, tf = l.getTextAttr(stack, "n")
            font = self.app.getFont("canvas_default")
            stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)
        if stack in self.s.rows:
            if not stack.cards and self.s.talon.cards:
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
        reserves_ncards = 0
        for s in self.s.reserves:
            if s.cards:
                reserves_ncards += 1
        if reserves_ncards == len(self.s.reserves):
            if not self.demo:
                self.playSample("droppair", priority=200)
            for s in self.s.reserves:
                s.moveMove(1, self.s.foundations[0], frames=4)
        self.leaveState(old_state)


class ElevensToo(Elevens):

    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)
        reserves_ncards = 0
        for s in self.s.reserves:
            if s.cards:
                reserves_ncards += 1
        if reserves_ncards == 0:
            for r in self.s.rows:
                if not r.cards and self.s.talon.cards:
                    self.s.talon.flipMove()
                    self.s.talon.moveMove(1, r)
        elif reserves_ncards == len(self.s.reserves):
            if not self.demo:
                self.playSample("droppair", priority=200)
            for s in self.s.reserves:
                s.moveMove(1, self.s.foundations[0], frames=4)
            self.fillStack(stack)
        self.leaveState(old_state)


class SuitElevens_RowStack(Elevens_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not Elevens_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return cards[0].suit == self.cards[0].suit

class SuitElevens_Reserve(Elevens_Reserve):
    def acceptsCards(self, from_stack, cards):
        if not Elevens_Reserve.acceptsCards(self, from_stack, cards):
            return False
        for r in self.game.s.reserves:
            if r.cards and r.cards[0].suit != cards[0].suit:
                return False
        return True

class SuitElevens(Elevens):
    RowStack_Class = SuitElevens_RowStack
    Reserve_Class = SuitElevens_Reserve
    def createGame(self):
        Elevens.createGame(self, rows=3, cols=5)


# /***********************************************************************
# // Fifteens
# ************************************************************************/

class Fifteens_RowStack(Elevens_RowStack):
    ACCEPTED_SUM = 13
    def acceptsCards(self, from_stack, cards):
        if not Elevens_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return cards[0].rank < 9 and self.cards[0] < 9


class Fifteens_Reserve(ReserveStack):
    def updateText(self):
        if self.game.preview > 1 or self.texts.misc is None:
            return
        t = ''
        if self.cards:
            ranks = [c.rank for c in self.cards]
            for r in (9, JACK, QUEEN, KING):
                if r in ranks:
                    break
            else:
                n = sum([i+1 for i in ranks])
                t = str(n)
        self.texts.misc.config(text=t)


class Fifteens(Elevens):
    Hint_Class = None

    RowStack_Class = Fifteens_RowStack
    Reserve_Class = StackWrapper(Fifteens_Reserve, max_cards=UNLIMITED_CARDS)

    def createGame(self):
        Elevens.createGame(self, rows=4, cols=4, reserves=1, texts=True)

    def _dropReserve(self):
        reserve = self.s.reserves[0]
        if not self.demo:
            self.playSample("droppair", priority=200)
        while reserve.cards:
            reserve.moveMove(1, self.s.foundations[0], frames=4)
        self.fillStack()

    def fillStack(self, stack=None):
        old_state = self.enterState(self.S_FILL)
        reserve = self.s.reserves[0]
        if len(reserve.cards) == 0:
            for r in self.s.rows:
                if not r.cards and self.s.talon.cards:
                    self.s.talon.flipMove()
                    self.s.talon.moveMove(1, r)
        else:
            reserve_ranks = [c.rank for c in reserve.cards]
            reserve_ranks.sort()
            if (9 in reserve_ranks or JACK in reserve_ranks
                or QUEEN in reserve_ranks or KING in reserve_ranks):
                if reserve_ranks == [9, JACK, QUEEN, KING]:
                    self._dropReserve()
            else:
                reserve_sum = sum([c.rank+1 for c in reserve.cards])
                if reserve_sum == 15:
                    self._dropReserve()
        self.leaveState(old_state)



# register the game
registerGame(GameInfo(38, Pyramid, "Pyramid",
                      GI.GT_PAIRING_TYPE, 1, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(193, RelaxedPyramid, "Relaxed Pyramid",
                      GI.GT_PAIRING_TYPE | GI.GT_RELAXED, 1, 2, GI.SL_MOSTLY_LUCK))
##registerGame(GameInfo(44, Thirteen, "Thirteen",
##                      GI.GT_PAIRING_TYPE, 1, 0))
registerGame(GameInfo(592, Giza, "Giza",
                      GI.GT_PAIRING_TYPE | GI.GT_OPEN, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(593, Thirteens, "Thirteens",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(594, Elevens, "Elevens",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(595, ElevensToo, "Elevens Too",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(596, SuitElevens, "Suit Elevens",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_LUCK))
registerGame(GameInfo(597, Fifteens, "Fifteens",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))



