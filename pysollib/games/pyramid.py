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
from pysollib.hint import DefaultHint
from pysollib.layout import Layout
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        AbstractFoundationStack, \
        BasicRowStack, \
        DealReserveRedealTalonStack, \
        DealRowTalonStack, \
        FaceUpWasteTalonStack, \
        InitialDealTalonStack, \
        OpenStack, \
        ReserveStack, \
        Stack, \
        StackWrapper, \
        TalonStack, \
        WasteStack, \
        WasteTalonStack, \
        getNumberOfFreeStacks
from pysollib.util import ANY_RANK, ANY_SUIT, JACK, KING, NO_RANK, QUEEN, \
        UNLIMITED_CARDS, UNLIMITED_REDEALS


# ************************************************************************
# *
# ************************************************************************

class Pyramid_Hint(DefaultHint):
    # consider moving card to the Talon as well
    def step010(self, dropstacks, rows):
        rows = rows + (self.game.s.talon,)
        return DefaultHint.step010(self, dropstacks, rows)


# ************************************************************************
# * basic logic for Talon, Waste and Rows
# ************************************************************************

class Pyramid_StackMethods:
    def acceptsCards(self, from_stack, cards):
        if self.basicIsBlocked():
            return False
        if from_stack is self or not self.cards or len(cards) != 1:
            return False
        c = self.cards[-1]
        return c.face_up and cards[0].face_up and cards[0].rank + c.rank == 11

    def _dropKingClickHandler(self, event):
        if not self.cards:
            return 0
        c = self.cards[-1]
        if c.face_up and c.rank == KING and not self.basicIsBlocked():
            self.game.playSample("autodrop", priority=20)
            self.playMoveMove(1, self.game.s.foundations[0], sound=False)
            return 1
        return 0

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        if not self.game.demo:
            self.game.playSample("droppair", priority=200)
        if not (n == 1
                and other_stack.cards
                and self.acceptsCards(other_stack, [other_stack.cards[-1]])):
            return
        old_state = self.game.enterState(self.game.S_FILL)
        f = self.game.s.foundations[0]
        self.game.moveMove(n, self, f, frames=frames, shadow=shadow)
        self.game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.game.leaveState(old_state)
        self.fillStack()
        other_stack.fillStack()

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if to_stack in self.game.s.foundations:
            self.game.moveMove(
                ncards, self, to_stack, frames=frames, shadow=shadow)
            self.fillStack()
        else:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)


# ************************************************************************
# *
# ************************************************************************

class Pyramid_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # We accept any King. Pairs will get delivered by _dropPairMove.
        return cards[0].rank == KING


# note that this Talon can accept and drop cards
class Pyramid_Talon(Pyramid_StackMethods, FaceUpWasteTalonStack):
    def clickHandler(self, event):
        if self._dropKingClickHandler(event):
            return 1
        return FaceUpWasteTalonStack.clickHandler(self, event)

    def releaseHandler(self, event, drag, sound=True):
        if self.game.app.opt.mouse_type == 'point-n-click':
            drag.stack.dragMove(drag, self, sound=sound)
            return
        FaceUpWasteTalonStack.releaseHandler(self, event, drag, sound)

    def canDealCards(self):
        if not FaceUpWasteTalonStack.canDealCards(self):
            return False
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
        self.blockmap = []

    def basicIsBlocked(self):
        for r in self.blockmap:
            if r.cards:
                return True
        return False

    def clickHandler(self, event):
        if self._dropKingClickHandler(event):
            return 1
        return OpenStack.clickHandler(self, event)

    getBottomImage = Stack._getNoneBottomImage

    def copyModel(self, clone):
        OpenStack.copyModel(self, clone)
        clone.blockmap = self.blockmap


# ************************************************************************
# * Pyramid
# ************************************************************************

class Pyramid(Game):
    Hint_Class = Pyramid_Hint
    Foundation_Class = Pyramid_Foundation
    Talon_Class = StackWrapper(Pyramid_Talon, max_rounds=3, max_accept=1)
    RowStack_Class = Pyramid_RowStack
    WasteStack_Class = Pyramid_Waste

    PYRAMID_Y_FACTOR = 2

    #
    # game layout
    #

    def _createPyramid(self, layout, x0, y0, size):
        rows = []
        # create stacks
        for i in range(size):
            x = x0 + (size-1-i) * layout.XS // 2
            y = y0 + i * layout.YS // self.PYRAMID_Y_FACTOR
            for j in range(i+1):
                stack = self.RowStack_Class(x, y, self)
                rows.append(stack)
                x = x + layout.XS
        # compute blocking
        n = 0
        for i in range(size-1):
            for j in range(i+1):
                k = n+i+1
                rows[n].blockmap = [rows[k], rows[k+1]]
                n += 1
        return rows

    def _createInvertedPyramid(self, layout, x0, y0, size):
        rows = []
        # create stacks
        for i in range(size):
            x = x0 + i * layout.XS // 2
            y = y0 + i * layout.YS // self.PYRAMID_Y_FACTOR
            for j in range(size-i):
                stack = self.RowStack_Class(x, y, self)
                rows.append(stack)
                x = x + layout.XS
        # compute blocking
        n = 0
        for i in range(size-1):
            for j in range(size-i):
                k = n+(size-i)
                if j == 0:              # left
                    rows[n].blockmap = [rows[k]]
                elif j == size-i-1:     # right
                    rows[n].blockmap = [rows[k-1]]
                else:
                    rows[n].blockmap = [rows[k-1], rows[k]]
                n += 1
        return rows

    def createGame(self, pyramid_len=7, reserves=0, waste=True, texts=True):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        max_rows = max(pyramid_len+2, reserves)
        w = layout.XM + max_rows*layout.XS
        h = layout.YM + layout.YS + \
            (pyramid_len-1)*layout.YS//self.PYRAMID_Y_FACTOR
        if reserves:
            h += layout.YS+2*layout.YOFFSET
        self.setSize(w, h)

        # create stacks
        decks = self.gameinfo.decks

        x, y = layout.XM+layout.XS, layout.YM
        s.rows = self._createPyramid(layout, x, y, pyramid_len)

        x, y = layout.XM, layout.YM
        s.talon = self.Talon_Class(x, y, self)
        if texts:
            layout.createText(s.talon, "se")
            if s.talon.max_rounds > 1:
                layout.createRoundText(s.talon, 'ne')
        if waste:
            y = y + layout.YS
            s.waste = self.WasteStack_Class(x, y, self, max_accept=1)
            layout.createText(s.waste, "se")
        x, y = self.width - layout.XS, layout.YM
        s.foundations.append(self.Foundation_Class(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52*decks))
        layout.createText(s.foundations[0], 's')
        if reserves:
            x = layout.XM+(max_rows-reserves)*layout.XS//2
            y = layout.YM+4*layout.YS
            for i in range(reserves):
                stack = self.Reserve_Class(x, y, self)
                s.reserves.append(stack)
                stack.CARD_YOFFSET = layout.YOFFSET
                x += layout.XS

        # define stack-groups
        layout.defaultStackGroups()
        self.sg.openstacks.append(s.talon)
        self.sg.dropstacks.append(s.talon)
        if s.waste:
            self.sg.openstacks.append(s.waste)

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getAutoStacks(self, event=None):
        return (self.sg.dropstacks, self.sg.dropstacks, ())

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + card2.rank == 11


# ************************************************************************
# * Relaxed Pyramid
# ************************************************************************

class RelaxedPyramid(Pyramid):
    # the pyramid must be empty
    def isGameWon(self):
        return getNumberOfFreeStacks(self.s.rows) == len(self.s.rows)


# ************************************************************************
# * Giza
# ************************************************************************

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
        self.s.talon.dealRow(frames=4)


# ************************************************************************
# * Thirteen
# * FIXME: UNFINISHED
# * (this doesn't work yet as 2 cards of the Waste should be playable)
# ************************************************************************

class Thirteen(Pyramid):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        self.setSize(7*layout.XS+layout.XM, 5*layout.YS+layout.YM)

        # create stacks
        for i in range(7):
            x = layout.XM + (6-i) * layout.XS // 2
            y = layout.YM + layout.YS + i * layout.YS // 2
            for j in range(i+1):
                s.rows.append(Pyramid_RowStack(x, y, self))
                x = x + layout.XS
        x, y = layout.XM, layout.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        layout.createText(s.talon, "s")
        x = x + layout.XS
        s.waste = Pyramid_Waste(x, y, self, max_accept=1)
        layout.createText(s.waste, "s")
        s.waste.CARD_XOFFSET = 14
        x, y = self.width - layout.XS, layout.YM
        s.foundations.append(Pyramid_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))

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


# ************************************************************************
# * Thirteens
# ************************************************************************

class Thirteens(Pyramid):

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        self.setSize(layout.XM+5*layout.XS, layout.YM+4*layout.YS)

        # create stacks
        x, y = layout.XM, layout.YM
        for i in range(2):
            x = layout.XM
            for j in range(5):
                s.rows.append(Giza_Reserve(x, y, self, max_accept=1))
                x += layout.XS
            y += layout.YS
        x, y = layout.XM, self.height-layout.YS
        s.talon = TalonStack(x, y, self)
        layout.createText(s.talon, 'n')
        x, y = self.width-layout.XS, self.height-layout.YS
        s.foundations.append(Pyramid_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))
        layout.createText(s.foundations[0], 'n')

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self._startAndDealRow()

    def fillStack(self, stack):
        if stack in self.s.rows:
            if not stack.cards and self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

# ************************************************************************
# * Elevens
# * Suit Elevens
# ************************************************************************


class Elevens_RowStack(Giza_Reserve):
    ACCEPTED_SUM = 9

    def acceptsCards(self, from_stack, cards):
        # if self.basicIsBlocked():
        #    return False
        if from_stack is self or not self.cards or len(cards) != 1:
            return False
        c = self.cards[-1]
        return (c.face_up and cards[0].face_up and
                cards[0].rank + c.rank == self.ACCEPTED_SUM)

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
        if c.rank not in self.ACCEPTED_CARDS:
            return False
        for s in self.game.s.reserves:
            if s.cards and s.cards[0].rank == c.rank:
                return False
        return True


class Elevens(Pyramid):

    RowStack_Class = Elevens_RowStack
    Reserve_Class = Elevens_Reserve

    def createGame(self, rows=3, cols=3, reserves=3, texts=False):

        layout, s = Layout(self), self.s

        self.setSize(
            layout.XM+(cols+2)*layout.XS,
            layout.YM+(rows+1.5)*layout.YS)

        x, y = self.width-layout.XS, layout.YM
        s.talon = TalonStack(x, y, self)
        layout.createText(s.talon, 's')
        x, y = self.width-layout.XS, self.height-layout.YS
        s.foundations.append(AbstractFoundationStack(x, y, self,
                             suit=ANY_SUIT, max_accept=0,
                             max_move=0, max_cards=52))
        layout.createText(s.foundations[0], 'n')
        y = layout.YM
        for i in range(rows):
            x = layout.XM
            for j in range(cols):
                s.rows.append(self.RowStack_Class(x, y, self, max_accept=1))
                x += layout.XS
            y += layout.YS
        x, y = layout.XM, self.height-layout.YS
        for i in range(reserves):
            stack = self.Reserve_Class(x, y, self)
            s.reserves.append(stack)
            stack.CARD_XOFFSET = layout.XOFFSET  # for fifteens
            x += layout.XS

        if texts:
            stack = s.reserves[0]
            tx, ty, ta, tf = layout.getTextAttr(stack, "n")
            font = self.app.getFont("canvas_default")
            stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                             anchor=ta, font=font)

        layout.defaultStackGroups()

    def startGame(self):
        self._startAndDealRow()

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

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        # FIXME
        return False


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


# ************************************************************************
# * Fifteens
# ************************************************************************

class Fifteens_RowStack(Elevens_RowStack):
    ACCEPTED_SUM = 13

    def acceptsCards(self, from_stack, cards):
        if not Elevens_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return cards[0].rank < 9 and self.cards[0].rank < 9


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
            if (9 in reserve_ranks or JACK in reserve_ranks or
                    QUEEN in reserve_ranks or KING in reserve_ranks):
                if reserve_ranks == [9, JACK, QUEEN, KING]:
                    self._dropReserve()
            else:
                reserve_sum = sum([c.rank+1 for c in reserve.cards])
                if reserve_sum == 15:
                    self._dropReserve()
        self.leaveState(old_state)


# ************************************************************************
# * Triple Alliance
# ************************************************************************

class TripleAlliance_Reserve(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        r_ranks = []
        for r in self.game.s.reserves:
            if r.cards:
                r_ranks.append(r.cards[0].rank)
        if not r_ranks:
            return True
        r_ranks.append(cards[0].rank)
        r_ranks.sort()
        if len(r_ranks) == 2:
            return r_ranks[1]-r_ranks[0] in (1, 12)
        for i in range(3):
            j, k = (i+1) % 3, (i+2) % 3
            if ((r_ranks[i]+1) % 13 == r_ranks[j] and
                    (r_ranks[j]+1) % 13 == r_ranks[k]):
                return True
        return False


class TripleAlliance(Game):

    def createGame(self):

        layout, s = Layout(self), self.s
        w0 = layout.XS+5*layout.XOFFSET
        self.setSize(layout.XM+5*w0, layout.YM+5*layout.YS)

        x, y = layout.XM, layout.YM
        for i in range(3):
            s.reserves.append(TripleAlliance_Reserve(x, y, self))
            x += layout.XS
        x, y = self.width-layout.XS, layout.YM
        s.foundations.append(AbstractFoundationStack(x, y, self, suit=ANY_SUIT,
                             max_move=0, max_accept=0, max_cards=52))
        layout.createText(s.foundations[0], 'nw')
        y = layout.YM+layout.YS
        nstacks = 0
        for i in range(4):
            x = layout.XM
            for j in range(5):
                stack = BasicRowStack(x, y, self, max_accept=0)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = layout.XOFFSET, 0
                x += w0
                nstacks += 1
                if nstacks >= 18:
                    break
            y += layout.YS

        x, y = self.width-layout.XS, self.height-layout.YS
        s.talon = InitialDealTalonStack(x, y, self)

        layout.defaultStackGroups()

    def startGame(self):
        self._startDealNumRows(2)
        self.s.talon.dealRowAvail()

    def fillStack(self, stack):
        for r in self.s.reserves:
            if not r.cards:
                return
        if not self.demo:
            self.playSample("droppair", priority=200)
        old_state = self.enterState(self.S_FILL)
        for r in self.s.reserves:
            r.moveMove(1, self.s.foundations[0])
        self.leaveState(old_state)

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 51


# ************************************************************************
# * Pharaohs
# ************************************************************************

class Pharaohs(Pyramid):

    Talon_Class = InitialDealTalonStack
    RowStack_Class = Pyramid_RowStack

    PYRAMID_Y_FACTOR = 3

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        w = layout.XM + 9*layout.XS
        h = layout.YM + 5.67*layout.YS
        self.setSize(w, h)

        # create stacks
        x, y = layout.XM, layout.YM
        s.rows += self._createPyramid(layout, x, y, 2)
        x, y = layout.XM+2*layout.XS, layout.YM
        s.rows += self._createPyramid(layout, x, y, 7)
        x, y = layout.XM+2.5*layout.XS, layout.YM+3*layout.YS
        s.rows += self._createPyramid(layout, x, y, 6)

        x, y = layout.XM, self.height-layout.YS
        s.talon = self.Talon_Class(x, y, self)
        x, y = self.width - layout.XS, layout.YM
        s.foundations.append(Pyramid_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))
        layout.createText(s.foundations[0], 's')

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + card2.rank == 11 or
                card1.rank == card2.rank)


# ************************************************************************
# * Baroness
# ************************************************************************

class Baroness_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        rows = self.game.s.rows
        if len(self.cards) == 7:
            rows += self.game.s.reserves
        return self.dealRowAvail(rows=rows, sound=sound)


class Baroness_RowStack(Giza_Reserve):

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return False
        if not self.cards:
            return True
        return cards[0].rank + self.cards[-1].rank == 11

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if to_stack in self.game.s.rows and not to_stack.cards:
            return OpenStack.moveMove(self, ncards, to_stack, frames, shadow)
        return Giza_Reserve.moveMove(self, ncards, to_stack, frames, shadow)


class Baroness(Pyramid):

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        self.setSize(
            layout.XM+9*layout.XS,
            layout.YM+max(3.5*layout.YS, layout.YS+12*layout.YOFFSET)
        )

        # create stacks
        x, y = layout.XM, layout.YM
        s.talon = Baroness_Talon(x, y, self)
        layout.createText(s.talon, 's')

        x += 2*layout.XS
        for i in range(5):
            stack = Baroness_RowStack(x, y, self, max_accept=1)
            s.rows.append(stack)
            stack.CARD_YOFFSET = layout.YOFFSET
            x += layout.XS
        x += layout.XS
        s.foundations.append(Pyramid_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))
        layout.createText(s.foundations[0], 's')
        x, y = layout.XM, self.height-layout.YS
        s.reserves.append(Giza_Reserve(x, y, self, max_accept=1))
        y -= layout.YS
        s.reserves.append(Giza_Reserve(x, y, self, max_accept=1))

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self._startAndDealRow()


# ************************************************************************
# * Apophis
# ************************************************************************

class Apophis_Hint(Pyramid_Hint):
    def computeHints(self):
        DefaultHint.computeHints(self)
        if self.hints:
            return
        reserves = self.game.s.reserves
        for i in range(3):
            for j in range(i+1, 3):
                r1 = reserves[i]
                r2 = reserves[j]
                if r1.cards and r2.acceptsCards(r1, r1.cards[-1:]):
                    self.addHint(50000+len(r1.cards)+len(r2.cards), 1, r1, r2)


class Apophis_RowStack(Pyramid_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return False
        if not self.cards:
            return False
        r0, r1 = cards[0].rank, self.cards[-1].rank
        return r0+r1 == 11


class Apophis(Pharaohs):
    Hint_Class = Apophis_Hint
    RowStack_Class = Apophis_RowStack

    PYRAMID_Y_FACTOR = 2

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        w = layout.XM + 9*layout.XS
        h = layout.YM + 4*layout.YS
        self.setSize(w, h)

        # create stacks
        x, y = layout.XM+1.5*layout.XS, layout.YM
        s.rows = self._createPyramid(layout, x, y, 7)

        x, y = layout.XM, layout.YM
        s.talon = DealReserveRedealTalonStack(x, y, self, max_rounds=3)
        layout.createText(s.talon, 'se')
        layout.createRoundText(s.talon, 'ne')

        y += layout.YS
        for i in range(3):
            stack = Pyramid_Waste(x, y, self, max_accept=1)
            s.reserves.append(stack)
            layout.createText(stack, 'se')
            y += layout.YS
        x, y = self.width - layout.XS, layout.YM
        s.foundations.append(Pyramid_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))
        layout.createText(s.foundations[0], 'nw')

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + card2.rank == 11

# ************************************************************************
# * Cheops
# ************************************************************************


class Cheops_StackMethods(Pyramid_StackMethods):
    def acceptsCards(self, from_stack, cards):
        if self.basicIsBlocked():
            return False
        if from_stack is self or not self.cards or len(cards) != 1:
            return False
        c = self.cards[-1]
        return (c.face_up and cards[0].face_up and
                abs(cards[0].rank-c.rank) in (0, 1))


class Cheops_Talon(Cheops_StackMethods, Pyramid_Talon):
    def clickHandler(self, event):
        return FaceUpWasteTalonStack.clickHandler(self, event)


class Cheops_Waste(Cheops_StackMethods, Pyramid_Waste):
    def clickHandler(self, event):
        return WasteStack.clickHandler(self, event)


class Cheops_RowStack(Cheops_StackMethods, Pyramid_RowStack):
    def clickHandler(self, event):
        return OpenStack.clickHandler(self, event)


class Cheops(Pyramid):

    Foundation_Class = StackWrapper(AbstractFoundationStack, max_accept=0)
    Talon_Class = StackWrapper(Cheops_Talon, max_rounds=1, max_accept=1)
    RowStack_Class = Cheops_RowStack
    WasteStack_Class = Cheops_Waste

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank-card2.rank) in (0, 1)


# ************************************************************************
# * Exit
# ************************************************************************

class Exit_RowStack(Elevens_RowStack):
    def acceptsCards(self, from_stack, cards):
        # if self.basicIsBlocked():
        #    return False
        if from_stack is self or not self.cards or len(cards) != 1:
            return False
        c1 = self.cards[-1]
        c2 = cards[0]
        # if not c1.face_up or not c2.face_up:
        #    return False
        return self.game._checkPair(c1, c2)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)


class Exit(Game):
    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        h1 = layout.YS+5*layout.YOFFSET
        self.setSize(layout.XM+7*layout.XS, layout.YM+2*h1+layout.YS)

        # create stacks
        y = layout.YM
        for i in (0, 1):
            x = layout.XM
            for j in range(5):
                stack = Exit_RowStack(x, y, self, base_rank=NO_RANK,
                                      max_move=1, max_accept=1, dir=0)
                s.rows.append(stack)
                stack.CARD_YOFFSET = layout.YOFFSET
                x += layout.XS
            y += h1
        x, y = self.width-layout.XS, layout.YM
        stack = Exit_RowStack(x, y, self, base_rank=NO_RANK,
                              max_move=1, max_accept=1, dir=0)
        s.reserves.append(stack)
        stack.CARD_YOFFSET = layout.YOFFSET
        x, y = self.width-layout.XS, self.height-layout.YS
        s.foundations.append(AbstractFoundationStack(x, y, self, suit=ANY_SUIT,
                             max_accept=0, max_move=0, max_cards=52))
        layout.createText(s.foundations[0], "n")
        x, y = layout.XM, self.height-layout.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        layout.defaultStackGroups()

    def _checkPair(self, c1, c2):
        if c1.rank + c2.rank == 9:      # A-10, 2-9, 3-8, 4-7, 5-6
            return True
        if c1.rank == JACK and c2.rank == JACK:
            return True
        if c1.rank + c2.rank == 23:     # Q-K
            return True
        return False

    def _shuffleHook(self, cards):
        swap_index = None
        for i in range(10):
            jack_indexes = []
            for j in range(5):
                k = i*5+j
                c = cards[k]
                if c.rank == JACK:
                    jack_indexes.append(k)
            if len(jack_indexes) == 3:
                swap_index = jack_indexes[1]
            if len(jack_indexes) >= 2:
                break
        if swap_index is not None:
            i = -1
            if cards[-1].rank == JACK:  # paranoia
                i = -2
            cards[swap_index], cards[i] = cards[i], cards[swap_index]
        cards.reverse()
        return cards

    def startGame(self):
        self.startDealSample()
        for i in range(10):
            for j in range(5):
                self.s.talon.dealRow(rows=[self.s.rows[i]], frames=4)
        self.s.talon.dealRow(rows=self.s.reserves, frames=4)
        self.s.talon.dealRow(rows=self.s.reserves, frames=4)

        #     def getAutoStacks(self, event=None):
        #         return ((), (), self.sg.dropstacks)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return self._checkPair(card1, card2)


# ************************************************************************
# * Two Pyramids
# ************************************************************************

class TwoPyramids(Pyramid):

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        w = layout.XM + 14*layout.XS
        h = layout.YM + 5*layout.YS
        self.setSize(w, h)

        # create stacks
        x, y = layout.XM, layout.YM+layout.YS
        s.rows = self._createPyramid(layout, x, y, 7)
        x += 7*layout.XS
        s.rows += self._createPyramid(layout, x, y, 7)

        x, y = layout.XM, layout.YM
        s.talon = self.Talon_Class(x, y, self)
        layout.createText(s.talon, "se")
        layout.createRoundText(s.talon, 'ne')

        y += layout.YS
        s.waste = self.WasteStack_Class(x, y, self, max_accept=1)
        layout.createText(s.waste, "se")
        x, y = self.width-layout.XS, layout.YM
        s.foundations.append(self.Foundation_Class(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=104))
        layout.createText(s.foundations[0], 'nw')
        # define stack-groups
        layout.defaultStackGroups()
        self.sg.openstacks.append(s.talon)
        self.sg.dropstacks.append(s.talon)
        self.sg.openstacks.append(s.waste)


# ************************************************************************
# * King Tut
# ************************************************************************

class KingTut(RelaxedPyramid):

    def createGame(self):
        layout, s = Layout(self), self.s

        w = layout.XM + max(7*layout.XS, 2*layout.XS+23*layout.XOFFSET)
        h = layout.YM + 5.5*layout.YS
        self.setSize(w, h)

        x, y = layout.XM+(w-7*layout.XS)//2, layout.YM
        s.rows = self._createPyramid(layout, x, y, 7)

        x, y = layout.XM, self.height-layout.YS
        s.talon = WasteTalonStack(
            x, y, self, max_rounds=UNLIMITED_REDEALS, num_deal=3)
        layout.createText(s.talon, "n")
        x += layout.XS
        s.waste = Pyramid_Waste(x, y, self, max_accept=1)
        s.waste.CARD_XOFFSET = layout.XOFFSET
        layout.createText(s.waste, "n")

        x, y = self.width - layout.XS, layout.YM
        s.foundations.append(self.Foundation_Class(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))
        layout.createText(s.foundations[0], 'nw')

        layout.defaultStackGroups()
        self.sg.openstacks.append(s.waste)


# ************************************************************************
# * Double Pyramid
# ************************************************************************

class DoublePyramid(Pyramid):
    def createGame(self):
        Pyramid.createGame(self, pyramid_len=9)


# ************************************************************************
# * Triangle
# ************************************************************************

class Triangle(Pyramid):

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        w = layout.XM + 10.5*layout.XS
        h = layout.YM + 4*layout.YS
        self.setSize(w, h)

        # create stacks
        x, y = layout.XM+2*layout.XS, layout.YM
        s.rows = self._createInvertedPyramid(layout, x, y, 7)

        x, y = layout.XM, layout.YM
        s.talon = self.Talon_Class(x, y, self)
        layout.createText(s.talon, "se")
        layout.createRoundText(s.talon, 'ne')

        y += layout.YS
        s.waste = self.WasteStack_Class(x, y, self, max_accept=1)
        layout.createText(s.waste, "se")
        x, y = self.width - layout.XS, layout.YM
        s.foundations.append(self.Foundation_Class(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=52))

        # define stack-groups
        layout.defaultStackGroups()
        self.sg.openstacks.append(s.talon)
        self.sg.dropstacks.append(s.talon)
        self.sg.openstacks.append(s.waste)


# ************************************************************************
# * Up and Down
# ************************************************************************

class UpAndDown(Pyramid):

    def createGame(self, pyramid_len=7, reserves=0, waste=True, texts=True):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        w = layout.XM + 13*layout.XS
        h = layout.YM + 4*layout.YS
        self.setSize(w, h)

        # create stacks
        x, y = layout.XM+layout.XS//2, layout.YM
        s.rows = self._createPyramid(layout, x, y, 7)
        x += 5.5*layout.XS
        s.rows += self._createInvertedPyramid(layout, x, y, 7)

        x, y = layout.XM, layout.YM
        s.talon = self.Talon_Class(x, y, self)
        layout.createText(s.talon, "se")
        layout.createRoundText(s.talon, 'ne')

        y += layout.YS
        s.waste = self.WasteStack_Class(x, y, self, max_accept=1)
        layout.createText(s.waste, "se")
        x, y = self.width - layout.XS, self.height-layout.YS
        s.foundations.append(self.Foundation_Class(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_move=0, max_cards=104))
        layout.createText(s.foundations[0], 'sw')

        # define stack-groups
        layout.defaultStackGroups()
        self.sg.openstacks.append(s.talon)
        self.sg.dropstacks.append(s.talon)
        self.sg.openstacks.append(s.waste)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Hurricane
# ************************************************************************

class Hurricane_Hint(DefaultHint):
    def step010(self, dropstacks, rows):
        rows = rows + self.game.s.reserves
        return DefaultHint.step010(self, dropstacks, rows)


class Hurricane_StackMethods(Pyramid_StackMethods):

    def acceptsCards(self, from_stack, cards):
        if from_stack is self:
            return False
        if len(cards) != 1:
            return False
        if not self.cards:
            return False
        c1 = self.cards[-1]
        c2 = cards[0]
        return c1.face_up and c2.face_up and c1.rank + c2.rank == 12

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if to_stack in self.game.s.rows or \
               to_stack in self.game.s.reserves:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            self.game.moveMove(ncards, self, to_stack,
                               frames=frames, shadow=shadow)
            self.fillStack()


class Hurricane_RowStack(Hurricane_StackMethods, BasicRowStack):
    pass


class Hurricane_Reserve(Hurricane_StackMethods, OpenStack):
    pass


class Hurricane(Pyramid):
    Hint_Class = Hurricane_Hint

    def createGame(self):
        # create layout
        layout, s = Layout(self), self.s

        # set window
        ww = layout.XS + max(2*layout.XOFFSET, layout.XS//2)
        w = layout.XM + 1.5*layout.XS + 4*ww
        h = layout.YM + 3*layout.YS
        self.setSize(w, h)

        # create stacks
        for xx,  yy in ((0, 0), (1, 0), (2, 0), (3, 0),
                        (0, 1),             (3, 1),
                        (0, 2), (1, 2), (2, 2), (3, 2),
                        ):
            x, y = layout.XM + 1.5*layout.XS + ww*xx, layout.YM + layout.YS*yy
            stack = Hurricane_Reserve(x, y, self, max_accept=1)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = layout.XOFFSET, 0
            s.reserves.append(stack)

        d = 3*ww - 4*layout.XS - 2*layout.XOFFSET
        x = layout.XM + 1.5*layout.XS + layout.XS+2*layout.XOFFSET + d//2
        y = layout.YM+layout.YS
        for i in range(3):
            stack = Hurricane_RowStack(x, y, self, max_accept=1)
            s.rows.append(stack)
            x += layout.XS

        x, y = layout.XM, layout.YM
        s.talon = TalonStack(x, y, self)
        layout.createText(s.talon, 'ne')
        y += 2*layout.YS
        s.foundations.append(AbstractFoundationStack(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_accept=0, max_move=0, max_cards=52))
        layout.createText(s.foundations[0], 'ne')

        # define stack-groups
        layout.defaultStackGroups()

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards and self.s.talon.cards:
            old_state = self.enterState(self.S_FILL)
            self.s.talon.flipMove()
            self.s.talon.moveMove(1, stack)
            self.leaveState(old_state)


# register the game
registerGame(GameInfo(38, Pyramid, "Pyramid",
                      GI.GT_PAIRING_TYPE, 1, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(193, RelaxedPyramid, "Relaxed Pyramid",
                      GI.GT_PAIRING_TYPE | GI.GT_RELAXED, 1, 2,
                      GI.SL_MOSTLY_LUCK,
                      altnames=("Pyramid's Stones",)))
# registerGame(GameInfo(44, Thirteen, "Thirteen",
#                       GI.GT_PAIRING_TYPE, 1, 0))
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
registerGame(GameInfo(619, TripleAlliance, "Triple Alliance",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(655, Pharaohs, "Pharaohs",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(657, Baroness, "Baroness",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_BALANCED,
                      altnames=('Five Piles',)))
registerGame(GameInfo(658, Apophis, "Apophis",
                      GI.GT_PAIRING_TYPE, 1, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(659, Cheops, "Cheops",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(674, Exit, "Exit",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(677, TwoPyramids, "Two Pyramids",
                      GI.GT_PAIRING_TYPE | GI.GT_ORIGINAL, 2, 2,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(681, KingTut, "King Tut",
                      GI.GT_PAIRING_TYPE, 1, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(699, DoublePyramid, "Double Pyramid",
                      GI.GT_PAIRING_TYPE, 2, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(700, Triangle, "Triangle",
                      GI.GT_PAIRING_TYPE, 1, 2, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(701, UpAndDown, "Up and Down",
                      GI.GT_PAIRING_TYPE | GI.GT_ORIGINAL, 2, 2,
                      GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(735, Hurricane, "Hurricane",
                      GI.GT_PAIRING_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
