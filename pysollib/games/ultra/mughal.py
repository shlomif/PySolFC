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

# Imports
import sys, math

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint, FreeCellType_Hint
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
#  * Mughal Foundation Stacks
#  ***********************************************************************/

class Mughal_FoundationStack(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, max_move=0)
        SS_FoundationStack.__init__(self, x, y, game, suit, **cap)

    def updateText(self):
        AbstractFoundationStack.updateText(self)
        self.game.updateText()


class Triumph_Foundation(AbstractFoundationStack):

    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=12, dir=0, base_rank=NO_RANK, max_move=0)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):

        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return 1
        stack_dir = self.game.getFoundationDir()
        if stack_dir == 0:
            card_dir = (cards[0].rank - self.cards[-1].rank) % self.cap.mod
            return card_dir in (1, 11)
        else:
            return (self.cards[-1].rank + stack_dir) % self.cap.mod == cards[0].rank



# ************************************************************************
#  * Mughal Row Stacks
#  ***********************************************************************/

class Mughal_OpenStack(OpenStack):

    def __init__(self, x, y, game, yoffset, **cap):
        kwdefault(cap, max_move=UNLIMITED_MOVES, max_cards=UNLIMITED_CARDS,
                  max_accept=UNLIMITED_ACCEPTS, base_rank=0, dir=-1)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def isRankSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not c1.rank + dir == c2.rank:
                return 0
            c1 = c2
        return 1

    def isAlternateColorSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not ((c1.suit + c2.suit) % 2
                    and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isAlternateForceSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not ((c1.suit < 4 and c2.suit > 3
                    or c1.suit > 3 and c2.suit < 4)
                    and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1

    def isSuitSequence(self, cards, dir=None):
        if not dir:
            dir = self.cap.dir
        c1 = cards[0]
        for c2 in cards[1:]:
            if not (c1.suit == c2.suit
                    and c1.rank + dir == c2.rank):
                return 0
            c1 = c2
        return 1


class Mughal_AC_RowStack(Mughal_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isAlternateColorSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isAlternateColorSequence([stackcards[-1], cards[0]])


class Mughal_AF_RowStack(Mughal_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isAlternateForceSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isAlternateForceSequence([stackcards[-1], cards[0]])


class Mughal_RK_RowStack(Mughal_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isRankSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isRankSequence([stackcards[-1], cards[0]])


class Mughal_SS_RowStack(Mughal_OpenStack):

    def acceptsCards(self, from_stack, cards):
        if (not self.basicAcceptsCards(from_stack, cards)
            or not self.isSuitSequence(cards)):
            return 0
        stackcards = self.cards
        if not len(stackcards):
            return cards[0].rank == 11 or self.cap.base_rank == ANY_RANK
        return self.isSuitSequence([stackcards[-1], cards[0]])


class Circles_RowStack(SS_RowStack):

    def __init__(self, x, y, game, base_rank, yoffset):
        SS_RowStack.__init__(self, x, y, game, base_rank=base_rank,
                                max_accept=1, max_move=1)
        self.CARD_YOFFSET = 1


class Triumph_BraidStack(OpenStack):

    def __init__(self, x, y, game, xoffset, yoffset):
        OpenStack.__init__(self, x, y, game)
        CW = self.game.app.images.CARDW
        self.CARD_YOFFSET = int(self.game.app.images.CARD_YOFFSET * yoffset)
        # use a sine wave for the x offsets
        self.CARD_XOFFSET = []
        j = 1
        for i in range(30):
            self.CARD_XOFFSET.append(int(math.cos(j) * xoffset))
            j = j + .9


class Triumph_StrongStack(ReserveStack):

    def fillStack(self):
        if not self.cards:
            if self.game.s.braidstrong.cards:
                self.game.moveMove(1, self.game.s.braidstrong, self)
            elif self.game.s.braidweak.cards:
                self.game.moveMove(1, self.game.s.braidweak, self)

    def getBottomImage(self):
        return self.game.app.images.getBraidBottom()


class Triumph_WeakStack(ReserveStack):

    def fillStack(self):
        if not self.cards:
            if self.game.s.braidweak.cards:
                self.game.moveMove(1, self.game.s.braidweak, self)
            elif self.game.s.braidstrong.cards:
                self.game.moveMove(1, self.game.s.braidstrong, self)

    def getBottomImage(self):
        return self.game.app.images.getBraidBottom()


class Triumph_ReserveStack(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if (from_stack is self.game.s.braidstrong or
                from_stack is self.game.s.braidweak or
                from_stack in self.game.s.rows):
            return 0
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()



# ************************************************************************
#  *
#  ***********************************************************************/

class AbstractMughalGame(Game):

    SUITS = (_("Crown"), _("Silver"), _("Saber"), _("Servant"),
             _("Harp"), _("Gold"), _("Document"), _("Stores"))
    RANKS = (_("Ace"), "2", "3", "4", "5", "6", "7", "8", "9", "10",
             _("Pradhan"), _("Raja"))
    COLORS = (_("Brown"), _("Black"), _("Red"), _("Yellow"),
              _("Green"), _("Grey"), _("Orange"), _("Tan"))
    FORCE = (_("Strong"), _("Weak"))

    def updateText(self):
        pass

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank
                or card2.rank + 1 == card1.rank)


class Triumph_Hint(DefaultHint):
    # FIXME: demo is not too clever in this game
    pass



# ************************************************************************
#  * Mughal Circles
#  ***********************************************************************/

class MughalCircles(AbstractMughalGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        w, h = l.XM + l.XS * 9, l.YM + l.YS * 7
        self.setSize(w, h)

        # Create row stacks
        x = w / 2 - l.CW / 2
        y = h / 2 - l.YS / 2
        x0 = (-1, -.8, 0, .8, 1, .8, 0, -.8,
            -2, -1.9, -1.5, -.8, 0, .8, 1.5, 1.9, 2, 1.9, 1.5, .8, 0, -.8, -1.5, -1.9)
        y0 = (0, -.8, -1, -.8, 0, .8, 1, .8,
            0, -.8, -1.5, -1.9, -2, -1.9, -1.5, -.8, 0, .8, 1.5, 1.9, 2, 1.9, 1.5, .8)
        for i in range(24):
            # FIXME:
            _x, _y = x+l.XS*x0[i]+l.XM*x0[i]*2, y+l.YS*y0[i]+l.YM*y0[i]*2
            if _x < 0: _x = 0
            if _y < 0: _y = 0
            s.rows.append(Circles_RowStack(_x, _y, self, base_rank=ANY_RANK, yoffset=0))

        # Create reserve stacks
        s.reserves.append(ReserveStack(l.XM, h - l.YS, self))
        s.reserves.append(ReserveStack(w - l.XS, h - l.YS, self))

        # Create foundations
        x = l.XM
        y = l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i, mod = 12,
                                             max_move = 0, max_cards = 12))
            y = y + l.YS
        x = self.width - l.XS
        y = l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i + 4, mod = 12,
                                             max_move = 0, max_cards = 12))
            y = y + l.YS
        # FIXME:
        _x1, _x2 = l.XM + l.XS, w - l.XS - l.XM
        for i in s.rows:
            if i.x < _x1: i.x = _x1
            elif i.x > _x2: i.x = _x2
        self.setRegion(s.rows, (_x1, 0, _x2, 999999))

        # Create talon
        s.talon = InitialDealTalonStack(l.XM + l.XS, l.YM, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 96
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.suit == card2.suit)
                and ((card1.rank + 1 == card2.rank)
                or (card1.rank - 1 == card2.rank)))



# ************************************************************************
#  * Eight Legions
#  ***********************************************************************/

class EightLegions(AbstractMughalGame):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        font = self.app.getFont("canvas_default")

        # Set window size
        self.setSize(l.XM * 3 + l.XS * 9, l.YM + l.YS * 6)

        # Create row stacks
        x = l.XM
        y = l.YM
        for i in range(8):
            s.rows.append(RK_RowStack(x, y, self, base_rank = 11,
                                        max_move = 12, max_cards = 99))
            x = x + l.XS

        # Create reserve stacks
        x = self.width - l.XS
        y = l.YM
        for i in range(6):
            s.reserves.append(ReserveStack(x, y, self))
            y = y + l.YS
        y = y - l.YS
        for i in range(4):
            x = x - l.XS
            s.reserves.append(ReserveStack(x, y, self))

        self.setRegion(s.rows, (0, 0, l.XM + l.XS * 8, l.YS * 5))

        # Create talon
        s.talon = DealRowTalonStack(l.XM, self.height - l.YS, self)
        l.createText(s.talon, "n")

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 96
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealCards()

    def isGameWon(self):
        if len(self.s.talon.cards):
            return 0
        for s in self.s.rows:
            if len(s.cards) != 12 or not isSameSuitSequence(s.cards):
                return 0
        return 1



# ************************************************************************
#  * Shamsher
#  ***********************************************************************/

class Shamsher(AbstractMughalGame):
    Layout_Method = Layout.ghulamLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = RK_RowStack
    BASE_RANK = ANY_RANK

    #
    # Game layout
    #

    def createGame(self, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=14, reserves=4, texts=0)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod=12, max_cards=12))

        # Create reserve stacks
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self, ))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self, max_cards=12,
                                suit=ANY_SUIT, base_rank=self.BASE_RANK))

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 96
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:12])
        self.s.talon.dealCards()



# ************************************************************************
#  * Ashrafi
#  ***********************************************************************/

class Ashrafi(Shamsher):
    Layout_Method = Layout.ghulamLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = RK_RowStack
    BASE_RANK = 11

    #
    # Game layout
    #

    def createGame(self, **layout):
        Shamsher.createGame(self)



# ************************************************************************
#  * Ghulam
#  ***********************************************************************/

class Ghulam(Shamsher):
    Layout_Method = Layout.ghulamLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SS_RowStack
    BASE_RANK = ANY_RANK

    #
    # Game layout
    #

    def createGame(self, **layout):
        Shamsher.createGame(self)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.suit == card2.suit)
                and ((card1.rank + 1 == card2.rank)
                or (card1.rank - 1 == card2.rank)))



# ************************************************************************
#  * Tipati
#  ***********************************************************************/

class Tipati(AbstractMughalGame):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = RK_RowStack
    BASE_RANK = 11
    MAX_MOVE = 0

    #
    # Game layout
    #

    def createGame(self, max_rounds=1, num_deal=1, **layout):
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=1)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])

        # Create talon
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                            max_rounds = max_rounds, num_deal = num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)

        # Create foundations
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self,
                                    r.suit, mod = 12, max_cards = 12, max_move = self.MAX_MOVE))

        # Create row stacks
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self,
                                suit = ANY_SUIT, base_rank = self.BASE_RANK))

        # Define stack groups
        l.defaultAll()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == 96
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()




# ************************************************************************
#  * Ashwapati
#  ***********************************************************************/

class Ashwapati(Tipati):
    RowStack_Class = SS_RowStack
    BASE_RANK = ANY_RANK
    MAX_MOVE = 1

    #
    # Game layout
    #

    def createGame(self, **layout):
        Tipati.createGame(self, max_rounds = -1, num_deal = 1)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.suit == card2.suit)
                and ((card1.rank + 1 == card2.rank)
                or (card1.rank - 1 == card2.rank)))



# ************************************************************************
#  * Gajapati
#  ***********************************************************************/

class Gajapati(Tipati):
    RowStack_Class = SS_RowStack
    BASE_RANK = ANY_RANK
    MAX_MOVE = 1

    #
    # Game layout
    #

    def createGame(self, **layout):
        Tipati.createGame(self, max_rounds=-1, num_deal=3)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.suit == card2.suit)
                and ((card1.rank + 1 == card2.rank)
                or (card1.rank - 1 == card2.rank)))



# ************************************************************************
#  * Narpati
#  ***********************************************************************/

class Narpati(Tipati):
    RowStack_Class = AC_RowStack
    MAX_MOVE = 1

    #
    # Game layout
    #

    def createGame(self, **layout):
        Tipati.createGame(self, max_rounds=1, num_deal=1)



# ************************************************************************
#  * Garhpati
#  ***********************************************************************/

class Garhpati(Tipati):
    RowStack_Class = AC_RowStack

    #
    # Game layout
    #

    def createGame(self, **layout):
        Tipati.createGame(self, max_rounds=-1, num_deal=3)



# ************************************************************************
#  * Dhanpati
#  ***********************************************************************/

class Dhanpati(Tipati):

    #
    # Game layout
    #

    def createGame(self, **layout):
        Tipati.createGame(self, max_rounds=2, num_deal=3)



# ************************************************************************
# * Akbar's Triumph
# ************************************************************************

class AkbarsTriumph(AbstractMughalGame):
    Hint_Class = Triumph_Hint

    BRAID_CARDS = 12
    BRAID_OFFSET = 1.1

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (piles up to 20 cards are playable - needed for Braid_BraidStack)
        decks = self.gameinfo.decks
        h = max(5 * l.YS + 35, l.YS + (self.BRAID_CARDS - 1) * l.YOFFSET)
        self.setSize(l.XM + l.XS * (7 + decks * 2), l.YM + h)

        # extra settings
        self.base_card = None

        # Create foundations, rows, reserves
        s.addattr(braidstrong = None)      # register extra stack variable
        s.addattr(braidweak = None)      # register extra stack variable
        x, y = l.XM, l.YM
        for j in range(4):
            for i in range(decks):
                s.foundations.append(Triumph_Foundation(x + l.XS * i, y, self,
                                                j, mod = 12, max_cards = 12))
            s.rows.append(Triumph_StrongStack(x + l.XS * decks, y, self))
            s.rows.append(Triumph_ReserveStack(x + l.XS * (1 + decks), y, self))
            y = y + l.YS
        x, y = x + l.XS * (5 + decks), l.YM
        for j in range(4):
            s.rows.append(Triumph_ReserveStack(x, y, self))
            s.rows.append(Triumph_WeakStack(x + l.XS, y, self))
            for i in range(decks, 0, -1):
                s.foundations.append(Triumph_Foundation(x + l.XS * (1 + i), y, self,
                                                j + 4, mod = 12, max_cards = 12))
            y = y + l.YS
        self.texts.info = MfxCanvasText(self.canvas,
                                        self.width / 2, h - l.YM / 2,
                                        anchor = "center",
                                        font = self.app.getFont("canvas_default"))

        # Create braids
        x, y = l.XM + l.XS * 2.3 + l.XS * decks, l.YM
        s.braidstrong = Triumph_BraidStack(x, y, self, xoffset = 12, yoffset = self.BRAID_OFFSET)
        x = x + l.XS * 1.4
        s.braidweak = Triumph_BraidStack(x, y, self, xoffset = -12, yoffset = self.BRAID_OFFSET)

        # Create talon
        x, y = l.XM + l.XS * 2 + l.XS * decks, h - l.YS - l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds = 3)
        l.createText(s.talon, "s")
        s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                             self.width / 2, h - l.YM * 2.5,
                                             anchor = "center",
                                             font=self.app.getFont("canvas_default"))
        x = x + l.XS * 2
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")

        # define stack-groups
        self.sg.talonstacks = [s.talon] + [s.waste]
        self.sg.openstacks = s.foundations + s.rows
        self.sg.dropstacks = [s.braidstrong] + [s.braidweak] + s.rows + [s.waste]


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.base_card = None
        self.updateText()
        for i in range(self.BRAID_CARDS):
            self.s.talon.dealRow(rows = [self.s.braidstrong])
        for i in range(self.BRAID_CARDS):
            self.s.talon.dealRow(rows = [self.s.braidweak])
        self.s.talon.dealRow()
        # deal base_card to foundations, update cap.base_rank
        self.base_card = self.s.talon.getCard()
        to_stack = self.s.foundations[self.base_card.suit * self.gameinfo.decks]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack)
        self.updateText()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        # deal first card to WasteStack
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 12 == card2.rank or (card2.rank + 1) % 12 == card1.rank))

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
            dir = self.getFoundationDir() % 12
            if dir == 1:
                t = t + _(" Ascending")
            elif dir == 11:
                t = t + _(" Descending")
        self.texts.info.config(text = t)



# ************************************************************************
# * Akbar's Conquest
# ************************************************************************

class AkbarsConquest(AkbarsTriumph):

    BRAID_CARDS = 16
    BRAID_OFFSET = .9



# ************************************************************************
# *
# ************************************************************************

class Vajra(AbstractMughalGame):
    RowStack_Class = StackWrapper(Mughal_RK_RowStack, base_rank=NO_RANK)

    #
    # game layout
    #

    def createGame(self, rows=9, reserves=8):
        # create layout
        l, s = Layout(self), self.s

        # set size
        maxrows = max(rows, reserves)
        self.setSize(l.XM + (maxrows + 2) * l.XS, l.YM + 6 * l.YS)

        #
        playcards = 4 * l.YS / l.YOFFSET
        xoffset, yoffset = [], []
        for i in range(playcards):
            xoffset.append(0)
            yoffset.append(l.YOFFSET)
        for i in range(96 * self.gameinfo.decks - playcards):
            xoffset.append(l.XOFFSET)
            yoffset.append(0)

        # create stacks
        x, y = l.XM + (maxrows - reserves) * l.XS / 2, l.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        x, y = l.XM + (maxrows - rows) * l.XS / 2, l.YM + l.YS
        self.setRegion(s.reserves, (-999, -999, 999999, y - l.YM / 2))
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self, yoffset=l.YOFFSET)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = yoffset
            s.rows.append(stack)
            x = x + l.XS
        x, y = l.XM + maxrows * l.XS, l.YM
        for i in range(2):
            for suit in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=suit + (4 * i)))
                y = y + l.YS
            x, y = x + l.XS, l.YM
        self.setRegion(self.s.foundations, (x - l.XS * 2, -999, 999999,
                        self.height - (l.YS + l.YM)), priority=1)
        s.talon = InitialDealTalonStack(self.width - 3 * l.XS / 2, self.height - l.YS, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        i = 0
        while self.s.talon.cards:
            if self.s.talon.cards[-1].rank == 11:
                if self.s.rows[i].cards:
                    i = i + 1
            self.s.talon.dealRow(rows=[self.s.rows[i]], frames=4)

    # must look at cards
    def _getClosestStack(self, cx, cy, stacks, dragstack):
        closest, cdist = None, 999999999
        for stack in stacks:
            if stack.cards and stack is not dragstack:
                dist = (stack.cards[-1].x - cx)**2 + (stack.cards[-1].y - cy)**2
            else:
                dist = (stack.x - cx)**2 + (stack.y - cy)**2
            if dist < cdist:
                closest, cdist = stack, dist
        return closest

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isRankSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))


# ************************************************************************
# *
# ************************************************************************

class Danda(Vajra):
    RowStack_Class = StackWrapper(Mughal_AF_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isAlternateForceSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))



# ************************************************************************
# *
# ************************************************************************

class Khadga(Vajra):
    RowStack_Class = StackWrapper(Mughal_AC_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isAlternateColorSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))



# ************************************************************************
# *
# ************************************************************************

class Makara(Vajra):
    RowStack_Class = StackWrapper(Mughal_SS_RowStack, base_rank=NO_RANK)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        row = self.s.rows[0]
        sequence = row.isSuitSequence
        return (sequence([card1, card2]) or sequence([card2, card1]))



# ************************************************************************
# * Ashta Dikapala Game Stacks
# ************************************************************************

class Dikapala_TableauStack(Mughal_OpenStack):

    def __init__(self, x, y, game, base_rank, yoffset, **cap):
        kwdefault(cap, dir=3, max_move=99, max_cards=4, max_accept=1, base_rank=base_rank)
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        # check that the base card is correct
        if self.cards and self.cards[0].rank != self.cap.base_rank:
            return 0
        if not self.cards:
            return cards[0].rank == self.cap.base_rank
        return (self.cards[-1].suit == cards[0].suit and
                self.cards[-1].rank + self.cap.dir == cards[0].rank)

    def getBottomImage(self):
        return self.game.app.images.getLetter(self.cap.base_rank)


class Dikapala_ReserveStack(ReserveStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_cards=1, max_accept=1, base_rank=ANY_RANK)
        OpenStack.__init__(self, x, y, game, **cap)

    def acceptsCards(self, from_stack, cards):
        return (ReserveStack.acceptsCards(self, from_stack, cards)
                and self.game.s.talon.cards)


class Dikapala_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        # check
        return not (self.cards or self.game.s.talon.cards)

    def canMoveCards(self, cards):
        return 1

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()


# ************************************************************************
# * Dikapala Hint
# ************************************************************************

class Dikapala_Hint(AbstractHint):
    def computeHints(self):
        game = self.game

        # 2)See if we can move a card to the tableaux
        if not self.hints:
            for r in game.sg.dropstacks:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                if r in game.s.tableaux:
                    rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                    if rr.acceptsCards(None, pile):
                        # do not move a card that is already in correct place
                        continue
                    base_score = 80000 + (4 - r.cap.base_suit)
                else:
                    base_score = 80000
                # find a stack that would accept this card
                for t in game.s.tableaux:
                    if t is not r and t.acceptsCards(r, pile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 3)See if we can move a card from the tableaux
        #    to a row stack. This can only happen if there are
        #    no more cards to deal.
        if not self.hints:
            for r in game.s.tableaux:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                if rr.acceptsCards(None, pile):
                    # do not move a card that is already in correct place
                    continue
                # find a stack that would accept this card
                for t in game.s.rows:
                    if t is not r and t.acceptsCards(r, pile):
                        score = 70000 + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 4)See if we can move a card within the row stacks
        if not self.hints:
            for r in game.s.rows:
                pile = r.getPile()
                if not pile or len(pile) != 1 or len(pile) == len(r.cards):
                    continue
                base_score = 60000
                # find a stack that would accept this card
                for t in game.s.rows:
                    if t is not r and t.acceptsCards(r, pile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 5)See if we can deal cards
        if self.level >= 2:
            if game.canDealCards():
                self.addHint(self.SCORE_DEAL, 0, game.s.talon, None)


# ************************************************************************
# * Ashta Dikapala
# ************************************************************************

class AshtaDikapala(Game):
    Hint_Class = Dikapala_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        TABLEAU_YOFFSET = min(9, max(3, l.YOFFSET / 3))

        # set window
        th = l.YS + 3 * TABLEAU_YOFFSET
        # (set piles so that at least 2/3 of a card is visible with 10 cards)
        h = 8 * l.YOFFSET + l.CH * 2/3
        self.setSize(9 * l.XS + l.XM * 2, l.YM + 3 * th + l.YM + h)

        # create stacks
        s.addattr(tableaux=[])     # register extra stack variable
        x = l.XM + 8 * l.XS + l.XS / 2
        y = l.YM
        for i in range(3, 0, -1):
            x = l.XM
            for j in range(8):
                s.tableaux.append(Dikapala_TableauStack(x, y, self, i - 1, TABLEAU_YOFFSET))
                x = x + l.XS
            x = x + l.XM
            s.reserves.append(Dikapala_ReserveStack(x, y, self))
            y = y + th
        x, y = l.XM, y + l.YM
        for i in range(8):
            s.rows.append(Dikapala_RowStack(x, y, self, max_accept=1))
            x = x + l.XS
        x = self.width - l.XS
        y = self.height - l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, "sw")

        # define stack-groups
        self.sg.openstacks = s.tableaux + s.rows + s.reserves
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.tableaux + s.rows

    #
    # game overrides
    #

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.tableaux, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        for stack in self.s.tableaux:
            if len(stack.cards) != 4:
                return 0
        return 1

    def fillStack(self, stack):
        if self.s.talon.cards:
            if stack in self.s.rows and len(stack.cards) == 0:
                self.s.talon.dealRow(rows=[stack])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 3 == card2.rank or card2.rank + 3 == card1.rank))

    def getHighlightPilesStacks(self):
        return ()


# ************************************************************************
# *
# ************************************************************************

def r(id, gameclass, name, game_type, decks, redeals, skill_level):
    game_type = game_type | GI.GT_MUGHAL_GANJIFA
    gi = GameInfo(id, gameclass, name, game_type, decks, redeals, skill_level,
                    suits=range(8), ranks=range(12))
    registerGame(gi)
    return gi

r(14401, MughalCircles, 'Mughal Circles', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(14402, Ghulam, 'Ghulam', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(14403, Shamsher, 'Shamsher', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(14404, EightLegions, 'Eight Legions', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(14405, Ashrafi, 'Ashrafi', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(14406, Tipati, 'Tipati', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_BALANCED)
r(14407, Ashwapati, 'Ashwapati', GI.GT_MUGHAL_GANJIFA, 1, -1, GI.SL_BALANCED)
r(14408, Gajapati, 'Gajapati', GI.GT_MUGHAL_GANJIFA, 1, -1, GI.SL_BALANCED)
r(14409, Narpati, 'Narpati', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_BALANCED)
r(14410, Garhpati, 'Garhpati', GI.GT_MUGHAL_GANJIFA, 1, -1, GI.SL_BALANCED)
r(14411, Dhanpati, 'Dhanpati', GI.GT_MUGHAL_GANJIFA, 1, 1, GI.SL_BALANCED)
r(14412, AkbarsTriumph, 'Akbar\'s Triumph', GI.GT_MUGHAL_GANJIFA, 1, 2, GI.SL_BALANCED)
r(14413, AkbarsConquest, 'Akbar\'s Conquest', GI.GT_MUGHAL_GANJIFA, 2, 2, GI.SL_BALANCED)
r(16000, Vajra, 'Vajra', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(16001, Danda, 'Danda', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(16002, Khadga, 'Khadga', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(16003, Makara, 'Makara', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_MOSTLY_SKILL)
r(16004, AshtaDikapala, 'Ashta Dikapala', GI.GT_MUGHAL_GANJIFA, 1, 0, GI.SL_BALANCED)

del r
