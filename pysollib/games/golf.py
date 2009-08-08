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
import sys, types

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
# *
# ************************************************************************

class Golf_Hint(AbstractHint):
    # FIXME: this is very simple

    def computeHints(self):
        game = self.game
        # for each stack
        for r in game.sg.dropstacks:
            # try if we can drop a card to the Waste
            w, ncards = r.canDropCards(game.s.foundations)
            if not w:
                continue
            # this assertion must hold for Golf
            assert ncards == 1
            # clone the Waste (including the card that will be dropped) to
            # form our new foundations
            ww = (self.ClonedStack(w, stackcards=w.cards+[r.cards[-1]]), )
            # now search for a stack that would benefit from this card
            score, color = 10000 + r.id, None
            for t in game.sg.dropstacks:
                if not t.cards:
                    continue
                if t is r:
                    t = self.ClonedStack(r, stackcards=r.cards[:-1])
                if t.canFlipCard():
                    score = score + 100
                elif t.canDropCards(ww)[0]:
                    score = score + 100
            # add hint
            self.addHint(score, ncards, r, w, color)


# ************************************************************************
# *
# ************************************************************************

class Golf_Talon(WasteTalonStack):
    def canDealCards(self):
        if not WasteTalonStack.canDealCards(self):
            return False
        return not self.game.isGameWon()


class Golf_Waste(WasteStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=0, max_accept=1)
        WasteStack.__init__(self, x, y, game, **cap)

    def acceptsCards(self, from_stack, cards):
        if not WasteStack.acceptsCards(self, from_stack, cards):
            return False
        # check cards
        r1, r2 = self.cards[-1].rank, cards[0].rank
        if self.game.getStrictness() == 1:
            # nothing on a King
            if r1 == KING:
                return False
        return (r1 + 1) % self.cap.mod == r2 or (r2 + 1) % self.cap.mod == r1

    def getHelp(self):
        return _('Waste. Build up or down regardless of suit.')


class Golf_RowStack(BasicRowStack):
    def clickHandler(self, event):
        return self.doubleclickHandler(event)
    def getHelp(self):
        return _('Tableau. No building.')


# ************************************************************************
# * Golf
# ************************************************************************

class Golf(Game):
    Waste_Class = Golf_Waste
    Hint_Class = Golf_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        playcards = 5
        w1, w2 = 8*l.XS+l.XM, 2*l.XS
        if w2 + 52*l.XOFFSET > w1:
            l.XOFFSET = int((w1 - w2) / 52)
        self.setSize(w1, l.YM+3*l.YS+(playcards-1)*l.YOFFSET+l.TEXT_HEIGHT)

        # create stacks
        x, y = l.XM + l.XS / 2, l.YM
        for i in range(7):
            s.rows.append(Golf_RowStack(x, y, self))
            x = x + l.XS
        x, y = l.XM, self.height - l.YS
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        l.createText(s.talon, "n")
        x = x + l.XS
        s.waste = self.Waste_Class(x, y, self)
        s.waste.CARD_XOFFSET = l.XOFFSET
        l.createText(s.waste, "n")
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards:
                return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_RK

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return (self.sg.dropstacks, (), ())
        else:
            # rightclickHandler
            return (self.sg.dropstacks, self.sg.dropstacks, ())


# ************************************************************************
# *
# ************************************************************************

class DeadKingGolf(Golf):
    def getStrictness(self):
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if card1.rank == KING:
            return False
        return Golf.shallHighlightMatch(self, stack1, card1, stack2, card2)


class RelaxedGolf(Golf):
    Waste_Class = StackWrapper(Golf_Waste, mod=13)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * Elevator - Relaxed Golf in a Pyramid layout
# ************************************************************************

class Elevator_RowStack(Golf_RowStack):
    STEP = (1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6)

    def basicIsBlocked(self):
        r, step = self.game.s.rows, self.STEP
        i, n, l = self.id, 1, len(step)
        while i < l:
            i = i + step[i]
            n = n + 1
            for j in range(i, i+n):
                if r[j].cards:
                    return True
        return False


class Elevator(RelaxedGolf):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(9*l.XS+l.XM, 4*l.YS+l.YM)

        # create stacks
        for i in range(7):
            x = l.XM + (8-i) * l.XS / 2
            y = l.YM + i * l.YS / 2
            for j in range(i+1):
                s.rows.append(Elevator_RowStack(x, y, self))
                x = x + l.XS
        x, y = l.XM, l.YM
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = self.Waste_Class(x, y, self)
        l.createText(s.waste, "s")
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:21], flip=0)
        self.s.talon.dealRow(rows=self.s.rows[21:])
        self.s.talon.dealCards()          # deal first card to WasteStack

class Escalator(Elevator):
    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Black Hole
# ************************************************************************

class BlackHole_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards:
            r1, r2 = self.cards[-1].rank, cards[0].rank
            return (r1 + 1) % self.cap.mod == r2 or (r2 + 1) % self.cap.mod == r1
        return True
    def getHelp(self):
        return _('Foundation. Build up or down regardless of suit.')


class BlackHole_RowStack(ReserveStack):
    def clickHandler(self, event):
        return self.doubleclickHandler(event)
    def getHelp(self):
        return _('Tableau. No building.')


class BlackHole(Game):
    RowStack_Class = StackWrapper(BlackHole_RowStack, max_accept=0, max_cards=3)
    Hint_Class = Golf_Hint

    #
    # game layout
    #

    def createGame(self, playcards=5):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w = max(2*l.XS, l.XS+(playcards-1)*l.XOFFSET)
        self.setSize(l.XM + 5*w, l.YM + 4*l.YS)

        # create stacks
        y = l.YM
        for i in range(5):
            x = l.XM + i*w
            s.rows.append(self.RowStack_Class(x, y, self))
        for i in range(2):
            y = y + l.YS
            for j in (0, 1, 3, 4):
                x = l.XM + j*w
                s.rows.append(self.RowStack_Class(x, y, self))
        y = y + l.YS
        for i in range(4):
            x = l.XM + i*w
            s.rows.append(self.RowStack_Class(x, y, self))
        for r in s.rows:
            r.CARD_XOFFSET = l.XOFFSET
            r.CARD_YOFFSET = 0
        x, y = l.XM + 2*w, l.YM + 3*l.YS/2
        s.foundations.append(BlackHole_Foundation(x, y, self, suit=ANY_SUIT,
                             dir=0, mod=13, max_move=0, max_cards=52))
        l.createText(s.foundations[0], "s")
        x, y = l.XM + 4*w, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move Ace to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.id == 13, c.suit), 1)

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return ((), (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return ((), self.sg.dropstacks, self.sg.dropstacks)



# ************************************************************************
# * Four Leaf Clovers
# ************************************************************************

class FourLeafClovers_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        # check the rank
        if self.cards:
            r1, r2 = self.cards[-1].rank, cards[0].rank
            return (r1 + 1) % self.cap.mod == r2
        return True
    def getHelp(self):
        return _('Foundation. Build up regardless of suit.')


class FourLeafClovers(Game):

    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        h = l.YS + 6*l.YOFFSET
        self.setSize(l.XM + 7*l.XS, l.YM + 2*h)

        # create stacks
        y = l.YM
        for i in range(7):
            x = l.XM + i*l.XS
            s.rows.append(UD_RK_RowStack(x, y, self, mod=13, base_rank=NO_RANK))
        y = l.YM+h
        for i in range(6):
            x = l.XM + i*l.XS
            s.rows.append(UD_RK_RowStack(x, y, self, mod=13, base_rank=NO_RANK))
        stack = FourLeafClovers_Foundation(l.XM+6*l.XS, self.height-l.YS, self,
                                           suit=ANY_SUIT, dir=0, mod=13,
                                           max_move=0, max_cards=52)
        s.foundations.append(stack)
        l.createText(stack, 'n')
        x, y = l.XM + 7*l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * All in a Row
# ************************************************************************

class AllInARow(BlackHole):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        h = l.YM+l.YS+4*l.YOFFSET
        self.setSize(l.XM+7*l.XS, 3*l.YM+2*h+l.YS)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(7):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        x, y = l.XM, l.YM+h
        for i in range(6):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        for r in s.rows:
            r.CARD_XOFFSET, r.CARD_YOFFSET = 0, l.YOFFSET

        x, y = l.XM, self.height-l.YS
        stack = BlackHole_Foundation(x, y, self, ANY_SUIT, dir=0, mod=13, max_move=0, max_cards=52, base_rank=ANY_RANK)
        s.foundations.append(stack)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = (self.width-l.XS)/51, 0
        l.createText(stack, 'n')
        x = self.width-l.XS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Robert
# * Wasatch
# ************************************************************************

class Robert(Game):

    def createGame(self, max_rounds=3, num_deal=1):
        l, s = Layout(self), self.s
        self.setSize(l.XM+4*l.XS, l.YM+2*l.YS)
        x, y = l.XM+3*l.XS/2, l.YM
        stack = BlackHole_Foundation(x, y, self, ANY_SUIT,
                                     dir=0, mod=13, max_move=0, max_cards=52)
        s.foundations.append(stack)
        l.createText(stack, 'ne')
        x, y = l.XM+l.XS, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        l.createText(s.talon, 'nw')
        if max_rounds > 0:
            l.createRoundText(self.s.talon, 'se', dx=l.XS)
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'ne')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()


class Wasatch(Robert):

    def createGame(self):
        Robert.createGame(self, max_rounds=UNLIMITED_REDEALS, num_deal=3)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()


# ************************************************************************
# * Diamond Mine
# ************************************************************************

DIAMOND = 3

class DiamondMine_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if cards[0].suit == DIAMOND:
            return False
        if self.cards:
            return self.cards[-1].suit != DIAMOND
        return True


class DiamondMine(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+13*l.XS, l.YM+2*l.YS+15*l.YOFFSET)

        x, y = l.XM+6*l.XS, l.YM
        s.foundations.append(SS_FoundationStack(x, y, self,
                             base_rank=ANY_RANK, suit=DIAMOND, mod=13))
        x, y = l.XM, l.YM+l.YS
        for i in range(13):
            s.rows.append(DiamondMine_RowStack(x, y, self))
            x += l.XS
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        l.defaultAll()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != 13:
            return False
        for s in self.s.rows:
            if len(s.cards) == 0:
                continue
            if len(s.cards) != 13:
                return False
            if not isSameSuitSequence(s.cards):
                return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Dolphin
# ************************************************************************

class Dolphin(Game):

    def createGame(self, rows=8, reserves=4, playcards=6):
        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM+3*l.YS+playcards*l.YOFFSET)

        dx = (self.width-l.XM-(reserves+1)*l.XS)/3
        x, y = l.XM+dx, l.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        x += dx
        max_cards = 52*self.gameinfo.decks
        s.foundations.append(RK_FoundationStack(x, y, self,
                             base_rank=ANY_RANK, mod=13, max_cards=max_cards))
        l.createText(s.foundations[0], 'ne')
        x, y = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(BasicRowStack(x, y, self))
            x += l.XS
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        l.defaultAll()

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


class DoubleDolphin(Dolphin):

    def createGame(self):
        Dolphin.createGame(self, rows=10, reserves=5, playcards=10)

    def startGame(self):
        for i in range(9):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


# ************************************************************************
# * Waterfall
# ************************************************************************

class Waterfall_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        c1 = cards[0]
        if not self.cards:
            return c1.rank == ACE and c1.suit == 0
        c2 = self.cards[-1]
        if c2.rank == KING:
            suit = (c2.suit+1) % 4
            rank = ACE
        else:
            suit = c2.suit
            rank = c2.rank+1
        return c1.suit == suit and c1.rank == rank


class Waterfall(Game):

    def createGame(self):
        rows = 8
        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM+2*l.YS+20*l.YOFFSET)

        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self))
            x += l.XS
        x, y = l.XM+(rows-1)*l.XS/2, self.height-l.YS
        s.foundations.append(Waterfall_Foundation(x, y, self, suit=ANY_SUIT,
                                                  max_cards=104))
        stack = s.foundations[0]
        tx, ty, ta, tf = l.getTextAttr(stack, 'se')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)
        x, y = self.width-l.XS, self.height-l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 'sw')

        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def updateText(self):
        if self.preview > 1:
            return
        f = self.s.foundations[0]
        if len(f.cards) == 104:
            t = ''
        elif len(f.cards) == 0:
            t = SUITS[0]
        else:
            c = f.cards[-1]
            if c.rank == KING:
                suit = (c.suit+1) % 4
            else:
                suit = c.suit
            t = SUITS[suit]
        f.texts.misc.config(text=t)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Vague
# * Thirty Two Cards
# ************************************************************************

class Vague_RowStack(BasicRowStack):
    clickHandler = BasicRowStack.doubleclickHandler


class Vague(Game):
    Foundation_Classes = [StackWrapper(SS_FoundationStack,
                                       base_rank=ANY_RANK, mod=13)]

    def createGame(self, rows=3, columns=6):
        l, s = Layout(self), self.s
        decks = self.gameinfo.decks
        maxrows = max(columns, 2+decks*4)
        self.setSize(l.XM+maxrows*l.XS, l.YM+(rows+1)*l.YS)

        x, y = l.XM, l.YM
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, 'ne')

        x, y = l.XM+2*l.XS, l.YM
        for found in self.Foundation_Classes:
            for i in range(4):
                s.foundations.append(found(x, y, self, suit=i))
                x += l.XS

        y = l.YM+l.YS
        for i in range(rows):
            x = l.XM + (maxrows-columns)*l.XS/2
            for j in range(columns):
                s.rows.append(Vague_RowStack(x, y, self))
                x += l.XS
            y += l.YS

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.flipMove()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                if not self.s.talon.cards[-1].face_up:
                    self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return ((), (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return ((), self.sg.dropstacks, self.sg.dropstacks)


class ThirtyTwoCards(Vague):
    Foundation_Classes = [
        SS_FoundationStack,
        StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1)]

    def createGame(self):
        Vague.createGame(self, rows=4, columns=8)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Devil's Solitaire
# ************************************************************************

class DevilsSolitaire_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards:
            return True
        if self.game.s.reserves[0].cards:
            c = self.game.s.reserves[0].cards[-1]
            return (c.rank+1) % 13 == cards[-1].rank
        return True


class DevilsSolitaire_WasteStack(WasteStack):
    clickHandler = WasteStack.doubleclickHandler


class DevilsSolitaire(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+3*l.YS+7*l.YOFFSET+2*l.TEXT_HEIGHT)

        x, y = l.XM+4*l.XS, l.YM
        stack = DevilsSolitaire_Foundation(x, y, self,
                             suit=ANY_SUIT, base_rank=ANY_RANK, mod=13)
        tx, ty, ta, tf = l.getTextAttr(stack, 'nw')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)
        s.foundations.append(stack)

        x, y = self.width-l.XS, l.YM
        stack = AbstractFoundationStack(x, y, self,
                             suit=ANY_SUIT, max_move=0, max_cards=104,
                             max_accept=0, base_rank=ANY_RANK)
        l.createText(stack, 'nw')
        s.foundations.append(stack)

        x, y = l.XM, l.YM+l.YS
        for i in range(4):
            s.rows.append(Vague_RowStack(x, y, self))
            x += l.XS
        x += l.XS
        for i in range(4):
            s.rows.append(Vague_RowStack(x, y, self))
            x += l.XS

        x, y = l.XM+4*l.XS, l.YM+l.YS
        stack = OpenStack(x, y, self)
        stack.CARD_YOFFSET = l.YOFFSET
        s.reserves.append(stack)

        x, y = l.XM+4.5*l.XS, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 'n')
        l.createRoundText(s.talon, 'nnn')
        x -= l.XS
        s.waste = DevilsSolitaire_WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        l.defaultStackGroups()


    def startGame(self):
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)
        if stack in self.s.rows and not stack.cards:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
        f0 = self.s.foundations[0]
        if len(f0.cards) == 12:
            self.moveMove(1, self.s.reserves[0], f0, frames=4)
            f1 = self.s.foundations[1]
            for i in range(13):
                self.moveMove(1, f0, f1, frames=4)
        self.leaveState(old_state)

    def updateText(self):
        if self.preview > 1:
            return
        f = self.s.foundations[0]
        r = self.s.reserves[0]
        if not r.cards:
            t = ''
        else:
            c = r.cards[-1]
            t = RANKS[(c.rank+1) % 13]
        f.texts.misc.config(text=t)


# ************************************************************************
# * Three Fir-trees
# ************************************************************************

class ThreeFirTrees_RowStack(Golf_RowStack):
    def __init__(self, x, y, game):
        Golf_RowStack.__init__(self, x, y, game, max_accept=0, max_cards=1)
        self.CARD_YOFFSET = 0
        self.blockmap = []

    def basicIsBlocked(self):
        for r in self.blockmap:
            if r.cards:
                return True
        return False

    getBottomImage = Stack._getNoneBottomImage


class FirTree_GameMethods:
    def _createFirTree(self, l, x0, y0):
        rows = []
        # create stacks
        for i in range(11):
            x = x0 + ((i+1)%2) * l.XS / 2
            y = y0 + i * l.YS / 4
            for j in range((i%2) + 1):
                rows.append(ThreeFirTrees_RowStack(x, y, self))
                x += l.XS
        # compute blocking
        n = 0
        for i in range(10):
            if i%2:
                rows[n].blockmap = [rows[n+2]]
                rows[n+1].blockmap = [rows[n+2]]
                n += 2
            else:
                rows[n].blockmap = [rows[n+1],rows[n+2]]
                n += 1
        return rows


class ThreeFirTrees(Golf, FirTree_GameMethods):
    Hint_Class = CautiousDefaultHint
    Waste_Class = Golf_Waste

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+max(7*l.XS, 2*l.XS+26*l.XOFFSET), l.YM+5*l.YS)

        x0, y0 = (self.width-7*l.XS)/2, l.YM
        for i in range(3):
            s.rows += self._createFirTree(l, x0, y0)
            x0 += 2.5*l.XS

        x, y = l.XM, self.height - l.YS
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        l.createText(s.talon, 'n')
        x += l.XS
        s.waste = self.Waste_Class(x, y, self)
        s.waste.CARD_XOFFSET = l.XOFFSET/4
        l.createText(s.waste, 'n')
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()


class RelaxedThreeFirTrees(ThreeFirTrees):
    Waste_Class = StackWrapper(Golf_Waste, mod=13)


# ************************************************************************
# * Napoleon Takes Moscow
# * Napoleon Leaves Moscow
# ************************************************************************

class NapoleonTakesMoscow(Game, FirTree_GameMethods):
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=KING, max_move=1)
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+10*l.XS, l.YM+3*l.YS+15*l.YOFFSET)

        x, y = l.XM+l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS

        x, y = l.XM, l.YM+l.YS
        for i in range(2):
            for j in range(4):
                s.rows.append(self.RowStack_Class(x, y, self))
                x += l.XS
            x += 2*l.XS

        x, y = l.XM+4*l.XS, l.YM+l.YS
        s.reserves += self._createFirTree(l, x, y)

        x, y = l.XM, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 'n')
        l.createRoundText(s.talon, 'nnn')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        # define stack-groups
        l.defaultStackGroups()
        
    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SS


class NapoleonLeavesMoscow(NapoleonTakesMoscow):
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=KING)
    Hint_Class = DefaultHint

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


# ************************************************************************
# * Flake
# * Flake (2 decks)
# ************************************************************************

from pileon import FourByFour_Hint

class Flake(Game):
    Hint_Class = FourByFour_Hint #CautiousDefaultHint

    def createGame(self, rows=6, playcards=18):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + rows*l.XS, l.YM + 2*l.YS + playcards*l.XOFFSET)

        # create stacks
        x, y, = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(UD_RK_RowStack(x, y, self, mod=13))
            x += l.XS

        x, y = l.XM + (rows-1)*l.XS/2, l.YM
        stack = BlackHole_Foundation(x, y, self, max_move=0, suit=ANY_SUIT,
                                     base_rank=ANY_RANK, dir=0, mod=13,
                                     max_cards=52*self.gameinfo.decks)
        s.foundations.append(stack)
        l.createText(stack, 'ne')

        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    shallHighlightMatch = Game._shallHighlightMatch_RKW


class Flake2Decks(Flake):
    def createGame(self):
        Flake.createGame(self, rows=8, playcards=22)
    def startGame(self):
        for i in range(12):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Beacon
# ************************************************************************

class Beacon(Game):

    def createGame(self, rows=8):
        # create layout
        l, s = Layout(self), self.s

        # set window
        playcards = 12
        self.setSize(l.XM+rows*l.XS, l.YM+3*l.YS+playcards*l.YOFFSET)

        # create stacks
        x, y = l.XM + (rows-1)*l.XS/2, l.YM
        stack = RK_FoundationStack(x, y, self, base_rank=ANY_RANK,
                                   max_cards=52, mod=13)
        s.foundations.append(stack)
        l.createText(stack, 'ne')

        x, y = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self, base_rank=NO_RANK, mod=13))
            x += l.XS

        x, y = l.XM, self.height-l.YS
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, 'se')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_RKW



# register the game
registerGame(GameInfo(36, Golf, "Golf",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(259, DeadKingGolf, "Dead King Golf",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(260, RelaxedGolf, "Relaxed Golf",
                      GI.GT_GOLF | GI.GT_RELAXED, 1, 0, GI.SL_BALANCED,
                      altnames=("Putt Putt",) ))
registerGame(GameInfo(40, Elevator, "Elevator",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED,
                      altnames=("Egyptian Solitaire", "Pyramid Golf") ))
registerGame(GameInfo(98, BlackHole, "Black Hole",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(267, FourLeafClovers, "Four Leaf Clovers",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(281, Escalator, "Escalator",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(405, AllInARow, "All in a Row",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(432, Robert, "Robert",
                      GI.GT_GOLF, 1, 2, GI.SL_LUCK))
registerGame(GameInfo(551, DiamondMine, "Diamond Mine",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(661, Dolphin, "Dolphin",
                      GI.GT_GOLF | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(662, DoubleDolphin, "Double Dolphin",
                      GI.GT_GOLF | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(709, Waterfall, "Waterfall",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(720, Vague, "Vague",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(723, DevilsSolitaire, "Devil's Solitaire",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED,
                      altnames=('Banner',) ))
registerGame(GameInfo(728, ThirtyTwoCards, "Thirty Two Cards",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_LUCK))
registerGame(GameInfo(731, ThreeFirTrees, "Three Fir-trees",
                      GI.GT_GOLF, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(733, NapoleonTakesMoscow, "Napoleon Takes Moscow",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(734, NapoleonLeavesMoscow, "Napoleon Leaves Moscow",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(749, Flake, "Flake",
                      GI.GT_GOLF | GI.GT_OPEN | GI.GT_ORIGINAL,
                      1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(750, Flake2Decks, "Flake (2 decks)",
                      GI.GT_GOLF | GI.GT_OPEN | GI.GT_ORIGINAL,
                      2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(763, Wasatch, "Wasatch",
                      GI.GT_1DECK_TYPE, 1, UNLIMITED_REDEALS, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(764, Beacon, "Beacon",
                      GI.GT_1DECK_TYPE | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(768, RelaxedThreeFirTrees, "Relaxed Three Fir-trees",
                      GI.GT_GOLF, 2, 0, GI.SL_BALANCED))

