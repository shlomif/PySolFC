## -*- coding: utf-8 -*-
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
from pysollib.hint import KlondikeType_Hint, YukonType_Hint

from spider import Spider_Hint


# /***********************************************************************
# // Gypsy
# ************************************************************************/

class Gypsy(Game):
    Layout_Method = Layout.gypsyLayout
    Talon_Class = DealRowTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack
    Hint_Class = KlondikeType_Hint

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=0, texts=1)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        if l.s.waste:
            s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# /***********************************************************************
# // Giant
# ************************************************************************/

class Giant_Foundation(SS_FoundationStack):
    def canMoveCards(self, cards):
        if not SS_FoundationStack.canMoveCards(self, cards):
            return 0
        # can only move cards if the Talon is empty
        return len(self.game.s.talon.cards) == 0


class Giant(Gypsy):
    Foundation_Class = Giant_Foundation

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Irmgard
# ************************************************************************/

class Irmgard_Talon(TalonStack):
    # A single click deals 9 (or 7) new cards to the RowStacks.
    def dealCards(self, sound=0):
        if self.cards:
            if len(self.cards) > 7:
                c = self.dealRow(sound=sound)
            else:
                c = self.dealRow(self.game.s.rows[1:8], sound=sound)
            return c
        return 0


class Irmgard(Gypsy):
    GAME_VERSION = 2

    Layout_Method = Layout.harpLayout
    Talon_Class = Irmgard_Talon
    RowStack_Class = KingAC_RowStack

    def createGame(self):
        Gypsy.createGame(self, rows=9, playcards=19)

    def startGame(self):
        r = self.s.rows
        for i in range(1, 5):
            self.s.talon.dealRow(rows=r[i:len(r)-i], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Die Königsbergerin
# ************************************************************************/

class DieKoenigsbergerin_Talon(DealRowTalonStack):
    # all Aces go to Foundations
    dealToStacks = DealRowTalonStack.dealToStacksOrFoundations


class DieKoenigsbergerin(Gypsy):
    Talon_Class = DieKoenigsbergerin_Talon
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)

    def startGame(self):
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow()


# /***********************************************************************
# // Die Russische
# ************************************************************************/

class DieRussische_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if self.cards:
            # check the rank - an ACE equals a Six
            rank = self.cards[-1].rank
            if rank == ACE:
                rank = 5
            if (rank + self.cap.dir) % self.cap.mod != cards[0].rank:
                return 0
        return 1


class DieRussische_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return 0
        # when empty, only accept a single card
        return self.cards or len(cards) == 1


class DieRussische(Gypsy):
    Talon_Class = InitialDealTalonStack
    Foundation_Class = StackWrapper(DieRussische_Foundation, min_cards=1)
    RowStack_Class = DieRussische_RowStack

    def createGame(self):
        Gypsy.createGame(self, rows=7, texts=0)

    def _shuffleHook(self, cards):
        # move one Ace to bottom of the Talon (i.e. last card to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == 0, c.suit), 1)

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow()
        c = self.s.talon.cards[-1]
        self.s.talon.dealRow(rows=(self.s.foundations[c.suit*2],))


# /***********************************************************************
# // Miss Milligan
# // Imperial Guards
# ************************************************************************/

class MissMilligan_ReserveStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return 0
        # Note that this reserve stack accepts sequences if both
        # the reserve stack and the Talon are empty.
        return len(self.cards) == 0 and len(self.game.s.talon.cards) == 0

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


class MissMilligan(Gypsy):
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = KingAC_RowStack
    ReserveStack_Class = MissMilligan_ReserveStack

    def createGame(self, rows=8, reserves=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + (1+max(8,rows))*l.XS, l.YM + (1+max(4, reserves))*l.YS)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        for i in range(8):
            x = x + l.XS
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i/2))
        x, y = l.XM, y + l.YS
        rx, ry = x + l.XS - l.XM/2, y - l.YM/2
        for i in range(reserves):
            s.reserves.append(self.ReserveStack_Class(x, y, self))
            y = y + l.YS
        if s.reserves:
            self.setRegion(s.reserves, (-999, ry, rx - 1, 999999))
        else:
            l.createText(s.talon, "ss")
            rx = -999
        x, y = l.XM + (8-rows)*l.XS/2, l.YM + l.YS
        for i in range(rows):
            x = x + l.XS
            s.rows.append(self.RowStack_Class(x, y, self))
        self.setRegion(s.rows, (rx, ry, 999999, 999999))

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


class ImperialGuards(MissMilligan):
    RowStack_Class = AC_RowStack


# /***********************************************************************
# // Nomad
# ************************************************************************/

class Nomad(MissMilligan):
    Foundation_Class = SS_FoundationStack
    RowStack_Class = AC_RowStack
    ReserveStack_Class = ReserveStack

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Milligan Cell
# ************************************************************************/

class MilliganCell(MissMilligan):
    ReserveStack_Class = ReserveStack

    def createGame(self):
        MissMilligan.createGame(self, reserves=4)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Milligan Harp
# // Carlton
# // Steve
# ************************************************************************/

class MilliganHarp(Gypsy):
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)

    def startGame(self, flip=0):
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=flip, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


class Carlton(MilliganHarp):
    def startGame(self):
        MilliganHarp.startGame(self, flip=1)


class Steve(Carlton):
    Hint_Class = Spider_Hint
    RowStack_Class = Spider_SS_RowStack

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank-card2.rank) == 1


# /***********************************************************************
# // Lexington Harp
# // Brunswick
# // Mississippi
# // Griffon
# ************************************************************************/

class LexingtonHarp(MilliganHarp):
    GAME_VERSION = 2
    RowStack_Class = Yukon_AC_RowStack
    Hint_Class = YukonType_Hint
    def getHighlightPilesStacks(self):
        return ()


class Brunswick(LexingtonHarp):
    def startGame(self):
        LexingtonHarp.startGame(self, flip=1)


class Mississippi(LexingtonHarp):
    def createGame(self):
        LexingtonHarp.createGame(self, rows=7)


class Griffon(Mississippi):
    def startGame(self):
        Mississippi.startGame(self, flip=1)


# /***********************************************************************
# // Blockade
# // Phantom Blockade
# ************************************************************************/

class Blockade(Gypsy):
    Layout_Method = Layout.klondikeLayout
    RowStack_Class = SS_RowStack

    def createGame(self):
        Gypsy.createGame(self, rows=12)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards and self.s.talon.cards:
            old_state = self.enterState(self.S_FILL)
            self.s.talon.flipMove()
            self.s.talon.moveMove(1, stack)
            self.leaveState(old_state)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                abs(card1.rank-card2.rank) == 1)


class PhantomBlockade(Gypsy):
    Layout_Method = Layout.klondikeLayout
    RowStack_Class = KingAC_RowStack

    def createGame(self):
        Gypsy.createGame(self, rows=13, playcards=24)

    def startGame(self):
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Cone
# ************************************************************************/

class Cone_Talon(DealRowTalonStack):
    def canDealCards(self):
        if not DealRowTalonStack.canDealCards(self):
            return False
        for r in self.game.s.rows:
            if not r.cards:
                return False
        return True

    def dealCards(self, sound=0):
        rows = self.game.s.rows
        if len(self.cards) == 4:
            rows = self.game.s.reserves
        self.dealRowAvail(rows=rows, sound=sound)


class Cone(Gypsy):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+9*l.XS, 3*l.YM+5*l.YS)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = Cone_Talon(x, y, self)
        l.createText(s.talon, 's')
        y += l.YS+2*l.YM
        for i in range(4):
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            y += l.YS
        x, y = l.XM+l.XS, l.YM
        for i in range(7):
            s.rows.append(AC_RowStack(x, y, self, mod=13))
            x += l.XS
        #y += l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    mod=13, max_cards=26))
            y += l.YS
        
        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        for i in (1, 2, 3):
            self.s.talon.dealRow(rows=self.s.rows[i:-i])


# /***********************************************************************
# // Surprise
# ************************************************************************/

class Surprise_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        return len(self.game.s.talon.cards) == 0

class Surprise(Gypsy):

    def createGame(self, rows=8, reserves=1):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+11*l.XS, l.YM+2*l.YS+12*l.YOFFSET+20)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, 's')
        x += l.XS
        stack = Surprise_ReserveStack(x, y, self, max_cards=3)
        xoffset = min(l.XOFFSET, l.XS/3)
        stack.CARD_XOFFSET = xoffset
        s.reserves.append(stack)
        x += 2*l.XS
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS
        x, y = l.XM, l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(11):
            s.rows.append(KingAC_RowStack(x, y, self))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(1, 6):
            self.s.talon.dealRow(rows=self.s.rows[i:-i], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Elba
# ************************************************************************/

class Elba(Gypsy):
    Layout_Method = Layout.klondikeLayout
    RowStack_Class = KingAC_RowStack

    def createGame(self):
        Gypsy.createGame(self, rows=10)

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Millie
# ************************************************************************/

class Millie(Gypsy):
    Layout_Method = Layout.klondikeLayout
    RowStack_Class = AC_RowStack

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


# register the game
registerGame(GameInfo(1, Gypsy, "Gypsy",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(65, Giant, "Giant",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(3, Irmgard, "Irmgard",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(119, DieKoenigsbergerin, "Die Königsbergerin",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(174, DieRussische, "Russian Patience",
                      GI.GT_2DECK_TYPE | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 6, 7, 8, 9, 10, 11, 12),
                      altnames=("Die Russische",) ))
registerGame(GameInfo(62, MissMilligan, "Miss Milligan",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(200, Nomad, "Nomad",
                      GI.GT_GYPSY | GI.GT_CONTRIB | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(78, MilliganCell, "Milligan Cell",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(217, MilliganHarp, "Milligan Harp",
                      GI.GT_GYPSY, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(218, Carlton, "Carlton",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(68, LexingtonHarp, "Lexington Harp",
                      GI.GT_YUKON, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(154, Brunswick, "Brunswick",
                      GI.GT_YUKON, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(121, Mississippi, "Mississippi",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(122, Griffon, "Griffon",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(226, Blockade, "Blockade",
                      GI.GT_GYPSY, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(412, Cone, "Cone",
                      GI.GT_GYPSY, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(463, Surprise, "Surprise",
                      GI.GT_GYPSY, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(469, PhantomBlockade, "Phantom Blockade",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(478, Elba, "Elba",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(486, ImperialGuards, "Imperial Guards",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(487, Millie, "Millie",
                      GI.GT_GYPSY, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(498, Steve, "Steve",
                      GI.GT_GYPSY, 2, 0, GI.SL_BALANCED))

