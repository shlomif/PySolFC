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
from pysollib.hint import CautiousDefaultHint, FreeCellType_Hint
from pysollib.pysoltk import MfxCanvasText

# /***********************************************************************
# //
# ************************************************************************/

class BeleagueredCastleType_Hint(CautiousDefaultHint):
    # FIXME: demo is not too clever in this game
    pass


# /***********************************************************************
# // Streets and Alleys
# ************************************************************************/

class StreetsAndAlleys(Game):
    Hint_Class = BeleagueredCastleType_Hint

    #
    # game layout
    #

    def createGame(self, playcards=13, reserves=0):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (set size so that at least 13 cards are fully playable)
        w = max(3*l.XS, l.XS+(playcards-1)*l.XOFFSET)
        x0 = l.XM
        x1 = x0 + w + 2*l.XM
        x2 = x1 + l.XS + 2*l.XM
        x3 = x2 + w + l.XM
        self.setSize(x3, l.YM + (4+int(reserves!=0))*l.YS)

        # create stacks
        y = l.YM
        if reserves:
            x = x1 - int(l.XS*(reserves-1)/2)
            for i in range(reserves):
                s.reserves.append(ReserveStack(x, y, self))
                x += l.XS
            y += l.YS
        x = x1
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_move=0))
            y = y + l.YS
        for x in (x0, x2):
            y = l.YM+l.YS*int(reserves!=0)
            for i in range(4):
                stack = RK_RowStack(x, y, self, max_move=1, max_accept=1)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                y = y + l.YS
        x, y = self.width - l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)
        if reserves:
            l.setRegion(s.rows[:4], (-999, l.YM+l.YS-l.CH/2, x1-l.CW/2, 999999))

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRowAvail()
        assert len(self.s.talon.cards) == 0

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank - card2.rank) == 1


# /***********************************************************************
# // Beleaguered Castle
# ************************************************************************/

class BeleagueredCastle(StreetsAndAlleys):
    def _shuffleHook(self, cards):
        # move Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(2):
            self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)
        assert len(self.s.talon.cards) == 0


# /***********************************************************************
# // Citadel
# ************************************************************************/

class Citadel(StreetsAndAlleys):
    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    # move cards to the Foundations during dealing
    def startGame(self):
        frames = 4
        talon = self.s.talon
        self.startDealSample()
        talon.dealRow(rows=self.s.foundations, frames=frames)
        while talon.cards:
            for r in self.s.rows:
                self.flipMove(talon)
                for s in self.s.foundations:
                    if s.acceptsCards(self, talon.cards[-1:]):
                        self.moveMove(1, talon, s, frames=frames)
                        break
                else:
                    self.moveMove(1, talon, r, frames=frames)
                if not talon.cards:
                    break


# /***********************************************************************
# // Fortress
# ************************************************************************/

class Fortress(Game):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = UD_SS_RowStack
    Hint_Class = BeleagueredCastleType_Hint

    #
    # game layout
    #

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, waste=0, texts=0, playcards=16)
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
        return l


    #
    # game overrides
    #

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRowAvail()
        assert len(self.s.talon.cards) == 0

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 13 == card2.rank or
                 (card2.rank + 1) % 13 == card1.rank))

# /***********************************************************************
# // Bastion
# // Ten by One
# ************************************************************************/

class Bastion(Game):
    Layout_Method = Layout.freeCellLayout
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = UD_SS_RowStack
    ReserveStack_Class = ReserveStack
    Hint_Class = BeleagueredCastleType_Hint

    #
    # game layout
    #

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, reserves=2, texts=0, playcards=16)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        for r in l.s.reserves:
            s.reserves.append(self.ReserveStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()
        return l


    #
    # game overrides
    #

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(2):
            self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)


class TenByOne(Bastion):
    def createGame(self):
        Bastion.createGame(self, reserves=1)
    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRowAvail()


# /***********************************************************************
# // Chessboard
# ************************************************************************/

class Chessboard_Foundation(SS_FoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, mod=13, min_cards=1, max_move=0)
        apply(SS_FoundationStack.__init__, (self, x, y, game, suit), cap)

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            if len(cards) != 1 or not cards[0].face_up:
                return 0
            if cards[0].suit != self.cap.base_suit:
                return 0
            for s in self.game.s.foundations:
                if s.cards:
                    return cards[0].rank == s.cards[0].rank
            return 1
        return SS_FoundationStack.acceptsCards(self, from_stack, cards)


class Chessboard_RowStack(UD_SS_RowStack):
    def canDropCards(self, stacks):
        if self.game.demo:
            return UD_SS_RowStack.canDropCards(self, stacks)
        for s in self.game.s.foundations:
            if s.cards:
                return UD_SS_RowStack.canDropCards(self, stacks)
        return (None, 0)


class Chessboard(Fortress):
    Foundation_Class = Chessboard_Foundation
    RowStack_Class = StackWrapper(Chessboard_RowStack, mod=13)

    def createGame(self):
        l = Fortress.createGame(self)
        tx, ty, ta, tf = l.getTextAttr(self.s.foundations[-1], "e")
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx + l.XM, ty, anchor=ta, font=font)

    def updateText(self):
        if self.preview > 1:
            return
        t = ""
        for s in self.s.foundations:
            if s.cards:
                t = RANKS[s.cards[0].rank]
                break
        self.texts.info.config(text=t)


# /***********************************************************************
# // Stronghold
# // Fastness
# ************************************************************************/

class Stronghold(StreetsAndAlleys):
    Hint_Class = FreeCellType_Hint
    def createGame(self):
        StreetsAndAlleys.createGame(self, reserves=1)

class Fastness(StreetsAndAlleys):
    Hint_Class = FreeCellType_Hint
    def createGame(self):
        StreetsAndAlleys.createGame(self, reserves=2)


# /***********************************************************************
# // Zerline
# ************************************************************************/

class Zerline_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        return not from_stack is self.game.s.waste

class Zerline(Game):
    Hint_Class = BeleagueredCastleType_Hint

    #
    # game layout
    #

    def createGame(self, rows=8, playcards=13, reserve_max_cards=4):
        # create layout
        l, s = Layout(self), self.s
        decks = self.gameinfo.decks

        # set window
        # (set size so that at least 13 cards are fully playable)
        w = max(3*l.XS, l.XS+playcards*l.XOFFSET)
        self.setSize(l.XM+2*w+decks*l.XS, 4*l.YM + (rows/2+1)*l.YS)

        # create stacks
        y = l.YM
        x = l.XM + w
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "ss")
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")
        x += l.XS
        stack = Zerline_ReserveStack(x, y, self, max_cards=reserve_max_cards)
        s.reserves.append(stack)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
        l.createText(stack, "ss")
        x = l.XM + w
        for j in range(decks):
            y = 4*l.YM+l.YS
            for i in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self, i,
                                     base_rank=KING, dir=1, max_move=0, mod=13))
                y += l.YS
            x += l.XS
        x = l.XM
        for j in range(2):
            y = 4*l.YM+l.YS
            for i in range(rows/2):
                stack = RK_RowStack(x, y, self, max_move=1, max_accept=1, base_rank=QUEEN)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                y += l.YS
            x += l.XM + w +decks*l.XS

        l.setRegion(s.rows[:4], (-999, 4*l.YM+l.YS-l.CH/2, w-l.CW/2, 999999))

        # define stack-groups
        l.defaultStackGroups()
        # set regions
        l.defaultRegions()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank - card2.rank) == 1

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        return int(to_stack in self.s.rows)


class Zerline3Decks(Zerline):
    def createGame(self):
        Zerline.createGame(self, rows=8, reserve_max_cards=6)


# /***********************************************************************
# // Chequers
# ************************************************************************/

class Chequers(Fortress):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (set size so that at least 7 cards are fully playable)
        dx = l.XM+l.XS+7*l.XOFFSET
        w = l.XM+max(5*dx, 9*l.XS+2*l.XM)
        h = l.YM+6*l.YS
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, "se")
        x = max(l.XS+3*l.XM, (self.width-l.XM-8*l.XS)/2)
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            x += l.XS
        y = l.YM+l.YS
        for i in range(5):
            x = l.XM
            for j in range(5):
                stack = UD_SS_RowStack(x, y, self)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                x += dx
            y += l.YS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if self.s.talon.cards and stack in self.s.rows and not stack.cards:
            self.s.talon.dealToStacks([stack])


# /***********************************************************************
# // Castle of Indolence
# ************************************************************************/

class CastleOfIndolence(Game):
    Hint_Class = BeleagueredCastleType_Hint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (set size so that at least 13 cards are fully playable)
        w = max(3*l.XS, l.XS+13*l.XOFFSET)
        self.setSize(l.XM+2*w+2*l.XS, l.YM + 5*l.YS)

        # create stacks
        x, y = l.XM, l.YM+4*l.YS
        s.talon = InitialDealTalonStack(x, y, self)
        x, y = l.XM+w-l.XS, l.YM+4*l.YS
        for i in range(4):
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            x += l.XS

        x = l.XM + w
        for x in (l.XM + w, l.XM + w + l.XS):
            y = l.YM
            for i in range(4):
                s.foundations.append(RK_FoundationStack(x, y, self,
                                     max_move=0))
                y += l.YS

        for x in (l.XM, l.XM + w +2*l.XS):
            y = l.YM
            for i in range(4):
                stack = RK_RowStack(x, y, self, max_move=1, max_accept=1, base_rank=ANY_RANK)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                y += l.YS
        l.setRegion(s.rows[:4], (-999, -999, w-l.CW/2, l.YM+4*l.YS-l.CH/2))

        # define stack-groups
        l.defaultStackGroups()
        # set regions
        l.defaultRegions()

    def startGame(self):
        for i in range(13):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank - card2.rank) == 1


# /***********************************************************************
# // Rittenhouse
# ************************************************************************/

class Rittenhouse_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows:
            ri = list(self.game.s.rows).index(from_stack)
            fi = list(self.game.s.foundations).index(self)
            if ri < 4:
                return ri == fi
            if ri == 4:
                return True
            return ri-1 == fi
        return False


class Rittenhouse(Game):
    Hint_Class = BeleagueredCastleType_Hint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+9*l.XS, l.YM+3*l.YS+12*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(4):
            s.foundations.append(Rittenhouse_Foundation(x, y, self, max_move=0))
            x += l.XS
        x += l.XS
        for i in range(4):
            s.foundations.append(Rittenhouse_Foundation(x, y, self,
                                 base_rank=KING, dir=-1, max_move=0))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        for i in range(9):
            s.rows.append(UD_RK_RowStack(x, y, self))
            x += l.XS

        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        # default
        l.defaultAll()


    def startGame(self):
        # move cards to the Foundations during dealing
        talon = self.s.talon
        self.startDealSample()
        while talon.cards:
            talon.dealRowAvail()
            self.fillAll()

    def fillAll(self):
        while True:
            if not self._fillOne():
                break

    def _fillOne(self):
        for r in self.s.rows:
            for s in self.s.foundations:
                if s.acceptsCards(r, r.cards[-1:]):
                    self.moveMove(1, r, s)
                    return 1
        return 0

    def fillStack(self, stack):
        self.fillAll()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank - card2.rank) == 1


# /***********************************************************************
# // Lightweight
# // Castle Mount
# ************************************************************************/

class Lightweight(StreetsAndAlleys):
    DEAL = (7, 1)
    RowStack_Class = StackWrapper(RK_RowStack, base_rank=KING)

    def createGame(self, rows=12, playcards=20):
        l, s = Layout(self), self.s
        decks = self.gameinfo.decks
        max_rows = max(decks*4, rows)
        self.setSize(l.XM+max_rows*l.XS, l.YM+2*l.YS+playcards*l.YOFFSET)

        x, y = l.XM+(max_rows-decks*4)*l.XS/2, l.YM
        for i in range(4):
            for j in range(decks):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                        max_move=0))
                x += l.XS
        x, y = l.XM+(max_rows-rows)*l.XS/2, l.YM+l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        s.talon = InitialDealTalonStack(self.width-l.XS, self.height-l.YS, self)

        l.defaultAll()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(self.DEAL[0]):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(self.DEAL[1]):
            self.s.talon.dealRowAvail()


class CastleMount(Lightweight):
    DEAL = (11, 1)
    RowStack_Class = Spider_SS_RowStack

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1) % stack1.cap.mod == card2.rank or
                (card2.rank + 1) % stack1.cap.mod == card1.rank)

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack.cards:
            return int(from_stack.cards[-1].suit == to_stack.cards[-1].suit)+1
        return 0



# register the game
registerGame(GameInfo(146, StreetsAndAlleys, "Streets and Alleys",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(34, BeleagueredCastle, "Beleaguered Castle",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(145, Citadel, "Citadel",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(147, Fortress, "Fortress",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(148, Chessboard, "Chessboard",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(300, Stronghold, "Stronghold",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(301, Fastness, "Fastness",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(306, Zerline, "Zerline",
                      GI.GT_BELEAGUERED_CASTLE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(324, Bastion, "Bastion",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(325, TenByOne, "Ten by One",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(351, Chequers, "Chequers",
                      GI.GT_BELEAGUERED_CASTLE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(393, CastleOfIndolence, "Castle of Indolence",
                      GI.GT_BELEAGUERED_CASTLE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(395, Zerline3Decks, "Zerline (3 decks)",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(400, Rittenhouse, "Rittenhouse",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(507, Lightweight, "Lightweight",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(508, CastleMount, "Castle Mount",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 3, 0, GI.SL_MOSTLY_SKILL))
