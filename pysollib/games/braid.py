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
import sys, math

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

class Braid_Hint(DefaultHint):
    # FIXME: demo is not too clever in this game
    pass

# ************************************************************************
# *
# ************************************************************************

class Braid_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=13, dir=0, base_rank=NO_RANK, max_move=0)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        stack_dir = self.game.getFoundationDir()
        if stack_dir == 0:
            card_dir = self.getRankDir(cards=(self.cards[-1], cards[0]))
            return card_dir in (1, -1)
        else:
            return (self.cards[-1].rank + stack_dir) % self.cap.mod == cards[0].rank


class Braid_BraidStack(OpenStack):
    def __init__(self, x, y, game, sine=0):
        OpenStack.__init__(self, x, y, game)
        self.CARD_YOFFSET = self.game.app.images.CARD_YOFFSET
        CW = self.game.app.images.CARDW
        if sine:
            # use a sine wave for the x offsets
            self.CARD_XOFFSET = []
            n = 9
            dx = 0.4 * CW * (2*math.pi/n)
            last_x = 0
            for i in range(n):
                x = int(round(dx * math.sin(i + 1)))
                ##print x, x - last_x
                self.CARD_XOFFSET.append(x - last_x)
                last_x = x
        else:
            self.CARD_XOFFSET = (-0.45*CW, 0.35*CW, 0.55*CW, -0.45*CW)


class Braid_RowStack(ReserveStack):
    def fillStack(self):
        if not self.cards and self.game.s.braid.cards:
            self.game.moveMove(1, self.game.s.braid, self)

    getBottomImage = Stack._getBraidBottomImage


class Braid_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if from_stack is self.game.s.braid or from_stack in self.game.s.rows:
            return False
        return ReserveStack.acceptsCards(self, from_stack, cards)

    getBottomImage = Stack._getTalonBottomImage


# ************************************************************************
# * Braid
# ************************************************************************

class Braid(Game):
    Hint_Class = Braid_Hint
    Foundation_Classes = [Braid_Foundation, Braid_Foundation]

    BRAID_CARDS = 20
    RANKS = RANKS           # pull into class Braid

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        font=self.app.getFont("canvas_default")

        # set window
        # (piles up to 20 cards are playable - needed for Braid_BraidStack)
        decks = self.gameinfo.decks
        h = max(4*l.YS + 30, l.YS+(self.BRAID_CARDS-1)*l.YOFFSET)
        self.setSize(l.XM+(8+decks)*l.XS, l.YM+h)

        # extra settings
        self.base_card = None

        # create stacks
        s.addattr(braid=None)      # register extra stack variable
        x, y = l.XM, l.YM
        for i in range(2):
            s.rows.append(Braid_RowStack(x + 0.5*l.XS, y, self))
            s.rows.append(Braid_RowStack(x + 4.5*l.XS, y, self))
            y = y + 3 * l.YS
        y = l.YM + l.YS
        for i in range(2):
            s.rows.append(Braid_ReserveStack(x, y, self))
            s.rows.append(Braid_ReserveStack(x + l.XS, y, self))
            s.rows.append(Braid_ReserveStack(x, y + l.YS, self))
            s.rows.append(Braid_ReserveStack(x + l.XS, y + l.YS, self))
            x = x + 4 * l.XS
        x, y = l.XM + l.XS * 5/2, l.YM
        s.braid = Braid_BraidStack(x, y, self)
        x, y = l.XM + 7 * l.XS, l.YM + l.YS * 3/2
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "s")
        l.createRoundText(s.talon, 'nn')
        x -= l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")
        y = l.YM
        for i in range(4):
            x = l.XM+8*l.XS
            for cl in self.Foundation_Classes:
                s.foundations.append(cl(x, y, self, suit=i))
                x += l.XS
            y = y + l.YS
        x = l.XM+8*l.XS+decks*l.XS/2
        self.texts.info = MfxCanvasText(self.canvas,
                                        x, y, anchor="n", font=font)

        # define stack-groups
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.openstacks = s.foundations + s.rows
        self.sg.dropstacks = [s.braid] + s.rows + [s.waste]


    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # do not play a trump as the base_card
        n = m = -1 - self.BRAID_CARDS - len(self.s.rows)
        while cards[n].suit >= len(self.gameinfo.suits):
            n = n - 1
        cards[n], cards[m] = cards[m], cards[n]
        return cards

    def startGame(self):
        self.base_card = None
        self.updateText()
        self.startDealSample()
        for i in range(self.BRAID_CARDS):
            self.s.talon.dealRow(rows=[self.s.braid], frames=4)
        self.s.talon.dealRow(frames=4)
        # deal base_card to foundations
        self.base_card = self.s.talon.cards[-1]
        to_stack = self.s.foundations[self.gameinfo.decks*self.base_card.suit]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack)
        self.updateText()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        # deal first card to WasteStack
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SSW

    def getHighlightPilesStacks(self):
        return ()

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


    #
    # game extras
    #

    def updateText(self):
        if self.preview > 1 or not self.texts.info:
            return
        if not self.base_card:
            t = ""
        else:
            t = self.RANKS[self.base_card.rank]
            dir = self.getFoundationDir()
            if dir == 1:
                t = t + _(" Ascending")
            elif dir == -1:
                t = t + _(" Descending")
        self.texts.info.config(text=t)


class LongBraid(Braid):
    BRAID_CARDS = 24


# ************************************************************************
# * Fort
# ************************************************************************

class Fort(Braid):

    Foundation_Classes = [SS_FoundationStack,
               StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1)]

    BRAID_CARDS = 21

    def _shuffleHook(self, cards):
        # move 4 Kings and 4 Aces to top of the Talon
        # (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
            lambda c: (c.rank in (ACE, KING) and c.deck == 0, (c.suit, c.rank)))

    def _restoreGameHook(self, game):
        pass
    def _loadGameHook(self, p):
        pass
    def _saveGameHook(self, p):
        pass

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        for i in range(self.BRAID_CARDS):
            self.s.talon.dealRow(rows=[self.s.braid], frames=4)
        self.s.talon.dealRow(frames=4)
        self.s.talon.dealCards()


# ************************************************************************
# * Backbone
# ************************************************************************

class Backbone_BraidStack(OpenStack):
    def __init__(self, x, y, game, **cap):
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = self.game.app.images.CARD_YOFFSET

    def basicIsBlocked(self):
        return len(self.game.s.reserves[2].cards) != 0


class Backbone(Game):

    Hint_Class = CautiousDefaultHint

    def createGame(self, rows=8):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+(rows+2)*l.XS, max(l.YM+3*l.XS+10*l.YOFFSET, l.YM+2*l.YS+11*l.YOFFSET+l.TEXT_HEIGHT)
        self.setSize(w, h)

        # create stacks
        y = l.YM
        for i in range(4):
            x = l.XM+(rows-8)*l.XS/2 +i*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x = l.XM+(rows/2+2)*l.XS +i*l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))

        x, y = l.XM+rows*l.XS/2, l.YM
        s.reserves.append(Backbone_BraidStack(x, y, self, max_accept=0))
        x += l.XS
        s.reserves.append(Backbone_BraidStack(x, y, self, max_accept=0))
        x, y = l.XM+(rows+1)*l.XS/2, l.YM+11*l.YOFFSET
        s.reserves.append(BasicRowStack(x, y, self, max_accept=0))

        x, y = l.XM, l.YM+l.YS
        for i in range(rows/2):
            s.rows.append(SS_RowStack(x, y, self, max_move=1))
            x += l.XS
        x, y = l.XM+(rows/2+2)*l.XS, l.YM+l.YS
        for i in range(rows/2):
            s.rows.append(SS_RowStack(x, y, self, max_move=1))
            x += l.XS

        x, y = l.XM+rows*l.XS/2, h-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "n")
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "n")

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        for i in range(10):
            self.s.talon.dealRow(rows=self.s.reserves[:2], frames=0)
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SS


class BackbonePlus(Backbone):
    def createGame(self):
        Backbone.createGame(self, rows=10)


# ************************************************************************
# * Big Braid
# ************************************************************************

class BigBraid(Braid):
    Foundation_Classes = [Braid_Foundation, Braid_Foundation, Braid_Foundation]


# ************************************************************************
# * Casket
# ************************************************************************

class Casket_Hint(CautiousDefaultHint):
    def computeHints(self):
        CautiousDefaultHint.computeHints(self)
        if self.hints:
            return
        if not self.game.s.waste.cards:
            return
        r = self.game.s.waste.cards[-1].rank
        if 0 <= r <= 3:
            to_stack = self.game.s.reserves[0]
        elif 4 <= r <= 7:
            to_stack = self.game.s.reserves[1]
        else:
            to_stack = self.game.s.reserves[2]
        self.addHint(5000, 1, self.game.s.waste, to_stack)


class JewelsStack(OpenStack):
    def canFlipCard(self):
        return False


class Casket_RowStack(SS_RowStack):

    getBottomImage = Stack._getReserveBottomImage

    def acceptsCards(self, from_stack, cards):
        if not SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            # don't accepts from lid
            return from_stack not in self.game.s.lid
        return True


class Casket_Reserve(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack is self.game.s.waste


class Casket(Game):
    Hint_Class = Casket_Hint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+10*l.XS, l.YM+4.5*l.YS)

        # register extra stack variables
        s.addattr(jewels=None)
        s.addattr(lid=[])

        # create stacks
        # Lid
        x0, y0 = l.XM+2.5*l.XS, l.YM
        for xx, yy in ((0, 0.5),
                       (1, 0.25),
                       (2, 0),
                       (3, 0.25),
                       (4, 0.5),
                       ):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            s.lid.append(BasicRowStack(x, y, self, max_accept=0))

        # Casket
        x0, y0 = l.XM+3*l.XS, l.YM+1.5*l.YS
        for xx, yy in ((0,0),            (3,0),
                       (0,1),            (3,1),
                       (0,2),(1,2),(2,2),(3,2),
                       ):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            stack = Casket_RowStack(x, y, self, max_move=1)
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)

        # Reserves
        x, y = l.XM, l.YM+1.5*l.YS
        for i in range(3):
            stack = Casket_Reserve(x, y, self, max_cards=UNLIMITED_CARDS)
            l.createText(stack, "ne")
            s.reserves.append(stack)
            y += l.YS

        # Foundations
        x = l.XM+8*l.XS
        for i in range(2):
            y = l.YM
            for j in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j))
                y += l.YS
            x += l.XS

        # Jewels
        x, y = l.XM+4.5*l.XS, l.YM+2*l.YS
        s.jewels = JewelsStack(x, y, self)
        l.createText(s.jewels, "s")

        # waste & talon
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x += l.XS
        s.waste = WasteStack(x, y, self, max_cards=1)

        # define stack-groups
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.openstacks = s.foundations + s.rows + s.reserves
        self.sg.dropstacks = s.lid + s.rows + [s.waste] + s.reserves


    def startGame(self):
        for i in range(13):
            self.s.talon.dealRow(rows=[self.s.jewels], frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealToStacksOrFoundations(stacks=self.s.lid)
        self.s.talon.dealToStacksOrFoundations(stacks=self.s.rows)
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards and stack in self.s.lid:
            if self.s.jewels.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.jewels.flipMove()
                self.s.jewels.moveMove(1, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Well
# ************************************************************************

class Well_TalonStack(DealRowRedealTalonStack):

    def canDealCards(self):
        return DealRowRedealTalonStack.canDealCards(self, rows=self.game.s.wastes)

    def dealCards(self, sound=False):
        num_cards = 0
        if sound and self.game.app.opt.animations:
            self.game.startDealSample()
        if not self.cards:
            # move all cards to talon
            num_cards = self._redeal(rows=self.game.s.wastes, frames=3)
            self.game.nextRoundMove(self)
        wastes = self.game.s.wastes[:(6-self.round)]
        num_cards += self.dealRowAvail(rows=wastes, frames=4, sound=False)
        if sound:
            self.game.stopSamples()
        return num_cards


class Well(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+6*l.XS, l.YM+6*l.YS+l.TEXT_HEIGHT)

        # register extra stack variables
        s.addattr(wastes=[])

        # foundations
        suit = 0
        x0, y0 = l.XM+1.5*l.XS, l.YM+1.5*l.YS+l.TEXT_HEIGHT
        for xx, yy in ((3,0),
                       (0,3),
                       (3,3),
                       (0,0)):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            s.foundations.append(SS_FoundationStack(x, y, self, suit=suit,
                                 base_rank=KING, mod=13, max_cards=26,
                                 dir=-1, max_move=0))
            suit += 1

        # rows
        x0, y0 = l.XM+l.XS, l.YM+l.YS+l.TEXT_HEIGHT
        for xx, yy in ((0,2),
                       (2,0),
                       (4,2),
                       (2,4)):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            stack = SS_RowStack(x, y, self, dir=1, mod=13, max_move=1)
            stack.getBottomImage = stack._getReserveBottomImage
            stack.CARD_YOFFSET = 0
            s.rows.append(stack)

        # left stack
        x, y = l.XM, l.YM+l.YS+l.TEXT_HEIGHT
        stack = SS_RowStack(x, y, self, base_rank=ACE, dir=1, mod=13, max_move=1)
        stack.getBottomImage = stack._getReserveBottomImage
        stack.CARD_YOFFSET = 0
        s.rows.append(stack)

        # reserves
        x0, y0 = l.XM+2*l.XS, l.YM+2*l.YS+l.TEXT_HEIGHT
        for xx, yy, anchor in ((0,1,'e'),
                               (1,0,'s'),
                               (2,1,'w'),
                               (1,2,'n')):
            x, y = x0+xx*l.XS, y0+yy*l.YS
            stack = OpenStack(x, y, self)
            l.createText(stack, anchor)
            s.reserves.append(stack)

        # wastes
        x, y = l.XM+l.XS, l.YM
        for i in range(5):
            stack = WasteStack(x, y, self)
            l.createText(stack, 's', text_format='%D')
            s.wastes.append(stack)
            x += l.XS

        # talon
        x, y = l.XM, l.YM
        s.talon = Well_TalonStack(x, y, self, max_rounds=5)
        l.createText(s.talon, "s")

        # define stack-groups
        self.sg.talonstacks = [s.talon] + s.wastes
        self.sg.openstacks = s.foundations + s.rows
        self.sg.dropstacks = s.rows + s.wastes + s.reserves
        

    def startGame(self):
        for i in range(10):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:4])
        self.s.talon.dealCards()


    def fillStack(self, stack):
        if not stack.cards and stack in self.s.rows[:4]:
            indx = list(self.s.rows).index(stack)
            r = self.s.reserves[indx]
            if r.cards:
                old_state = self.enterState(self.S_FILL)
                r.moveMove(1, stack)
                self.leaveState(old_state)

    shallHighlightMatch = Game._shallHighlightMatch_SSW



# register the game
registerGame(GameInfo(12, Braid, "Braid",
                      GI.GT_NAPOLEON, 2, 2, GI.SL_BALANCED,
                      altnames=("Der Zopf", "Plait", "Pigtail") ))
registerGame(GameInfo(175, LongBraid, "Long Braid",
                      GI.GT_NAPOLEON, 2, 2, GI.SL_BALANCED,
                      altnames=("Der lange Zopf",) ))
registerGame(GameInfo(358, Fort, "Fort",
                      GI.GT_NAPOLEON, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(376, Backbone, "Backbone",
                      GI.GT_NAPOLEON, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(377, BackbonePlus, "Backbone +",
                      GI.GT_NAPOLEON, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(510, BigBraid, "Big Braid",
                      GI.GT_NAPOLEON | GI.GT_ORIGINAL, 3, 2, GI.SL_BALANCED))
registerGame(GameInfo(694, Casket, "Casket",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(717, Well, "Well",
                      GI.GT_2DECK_TYPE, 2, 4, GI.SL_BALANCED))
