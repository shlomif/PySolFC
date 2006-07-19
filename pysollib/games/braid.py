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

# /***********************************************************************
# //
# ************************************************************************/

class Braid_Hint(DefaultHint):
    # FIXME: demo is not too clever in this game
    pass

# /***********************************************************************
# //
# ************************************************************************/

class Braid_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=13, dir=0, base_rank=NO_RANK, max_move=0)
        apply(AbstractFoundationStack.__init__, (self, x, y, game, suit), cap)

    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return 1
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

    def getBottomImage(self):
        return self.game.app.images.getBraidBottom()


class Braid_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if from_stack is self.game.s.braid or from_stack in self.game.s.rows:
            return 0
        return ReserveStack.acceptsCards(self, from_stack, cards)

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()


# /***********************************************************************
# // Braid
# ************************************************************************/

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
        l.createText(s.talon, "ss")
        s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                             x + l.CW / 2, y - l.YM,
                                             anchor="s",
                                             font=self.app.getFont("canvas_default"))
        x = x - l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")
        y = l.YM
        for i in range(4):
            x = l.XM+8*l.XS
            for cl in self.Foundation_Classes:
                s.foundations.append(cl(x, y, self, suit=i))
                x += l.XS
            y = y + l.YS
        x = 8*l.XS+decks*l.XS/2+l.XM/2
        self.texts.info = MfxCanvasText(self.canvas,
                                        x, y, anchor="n",
                                        font=self.app.getFont("canvas_default"))

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

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 13 == card2.rank or (card2.rank + 1) % 13 == card1.rank))

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


# /***********************************************************************
# // Fort
# ************************************************************************/

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


# /***********************************************************************
# // Backbone
# ************************************************************************/

class Backbone_BraidStack(OpenStack):
    def __init__(self, x, y, game, **cap):
        apply(OpenStack.__init__, (self, x, y, game), cap)
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
        l.createText(s.talon, "nn")
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "nn")

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        for i in range(10):
            self.s.talon.dealRow(rows=self.s.reserves[:2], frames=0)
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1


class BackbonePlus(Backbone):
    def createGame(self):
        Backbone.createGame(self, rows=10)


# /***********************************************************************
# // Big Braid
# ************************************************************************/

class BigBraid(Braid):
    Foundation_Classes = [Braid_Foundation, Braid_Foundation, Braid_Foundation]



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
