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
from pysollib.hint import SpiderType_Hint, YukonType_Hint

# /***********************************************************************
# //
# ************************************************************************/

class Spider_Hint(SpiderType_Hint):
    # FIXME: demo is not too clever in this game

    BONUS_SAME_SUIT_MOVE = 400

    def _preferHighRankMoves(self):
        return 1

    def shallMovePile(self, r, t, pile, rpile):
        if not SpiderType_Hint.shallMovePile(self, r, t, pile, rpile):
            return 0
        rr = self.ClonedStack(r, stackcards=rpile)
        if rr.acceptsCards(t, pile):
            # the pile we are going to move from r to t
            # could be moved back from t ro r - this is
            # dangerous for as we can create loops...
            if len(t.cards) == 0:
                return 1
            if pile[0].suit == t.cards[-1].suit:
                # The pile will get moved onto the correct suit
                if len(rpile) == 0 or pile[0].suit != rpile[-1].suit:
                    return 1
            if self.level <= 1 and len(rpile) == 0:
                return 1
            return 0
        return 1


# /***********************************************************************
# //
# ************************************************************************/

class Spider_SS_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit=ANY_SUIT, **cap):
        kwdefault(cap, dir=-1, base_rank=KING,
                  min_accept=13, max_accept=13, max_move=0)
        apply(AbstractFoundationStack.__init__, (self, x, y, game, suit), cap)

    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # now check the cards
        return isSameSuitSequence(cards, self.cap.mod, self.cap.dir)


class Spider_AC_Foundation(Spider_SS_Foundation):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # now check the cards
        return isAlternateColorSequence(cards, self.cap.mod, self.cap.dir)


class Spider_RowStack(Spider_SS_RowStack):
    def canDropCards(self, stacks):
        if len(self.cards) < 13:
            return (None, 0)
        cards = self.cards[-13:]
        for s in stacks:
            if s is not self and s.acceptsCards(self, cards):
                return (s, 13)
        return (None, 0)


# /***********************************************************************
# // Relaxed Spider
# ************************************************************************/

class RelaxedSpider(Game):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = DealRowTalonStack
    Foundation_Class = Spider_SS_Foundation
    RowStack_Class = Spider_RowStack
    Hint_Class = Spider_Hint

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, waste=0, texts=1, playcards=23)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        if l.s.waste:
            s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=ANY_SUIT))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()

    def startGame(self, flip=0):
        for i in range(4):
            self.s.talon.dealRow(flip=flip, frames=0)
        r = self.s.rows
        rows = (r[0], r[3], r[6], r[9])
        self.s.talon.dealRow(rows=rows, flip=flip, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_RK
    getQuickPlayScore = Game._getSpiderQuickPlayScore


# /***********************************************************************
# // Spider
# ************************************************************************/

class Spider(RelaxedSpider):
    def canDealCards(self):
        if not RelaxedSpider.canDealCards(self):
            return 0
        # no row may be empty
        for r in self.s.rows:
            if not r.cards:
                return 0
        return 1

class Spider1Suit(Spider):
    pass
class Spider2Suits(Spider):
    pass

class OpenSpider(Spider):
    def startGame(self):
        Spider.startGame(self, flip=1)


# /***********************************************************************
# // Black Widow
# ************************************************************************/

class BlackWidow_RowStack(RK_RowStack, Spider_RowStack):
    def canDropCards(self, stacks):
        return Spider_RowStack.canDropCards(self, stacks)


class BlackWidow(Spider):
    RowStack_Class = BlackWidow_RowStack


# /***********************************************************************
# // Scheidungsgrund (aka Ground for a Divorce)
# ************************************************************************/

class GroundForADivorce_Talon(TalonStack):
    # A single click deals a new cards to each non-empty row.
    def dealCards(self, sound=1):
        if self.cards:
            rows = filter(lambda r: r.cards, self.game.s.rows)
            if not rows:
                # deal one card to first row if all rows are emtpy
                rows = self.game.s.rows[:1]
            return self.dealRowAvail(rows=rows, sound=sound)
        return 0


class GroundForADivorce(RelaxedSpider):
    Layout_Method = Layout.harpLayout
    Talon_Class = GroundForADivorce_Talon
    Foundation_Class = StackWrapper(Spider_SS_Foundation, base_rank=ANY_RANK, mod=13)
    RowStack_Class = StackWrapper(Spider_RowStack, mod=13)

    def createGame(self):
        RelaxedSpider.createGame(self, playcards=22)

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# /***********************************************************************
# // Grandmother's Game
# ************************************************************************/

class GrandmothersGame(RelaxedSpider):
    Layout_Method = Layout.harpLayout

    def createGame(self):
        RelaxedSpider.createGame(self, playcards=22)

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Spiderette (Spider with one deck and 7 rows)
# ************************************************************************/

class Spiderette(Spider):
    def createGame(self):
        Spider.createGame(self, rows=7, playcards=20)

    def startGame(self):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Baby Spiderette
# ************************************************************************/

class BabySpiderette(Spiderette):
    RowStack_Class = BlackWidow_RowStack


# /***********************************************************************
# // Will o' the Wisp (just like Spiderette)
# ************************************************************************/

class WillOTheWisp(Spiderette):
    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Simple Simon
# ************************************************************************/

class SimpleSimon(Spider):
    Talon_Class = InitialDealTalonStack

    def createGame(self):
        Spider.createGame(self, rows=10, texts=0)

    def startGame(self):
        for l in (9, 8, 7, 6, 5, 4, 3):
            self.s.talon.dealRow(rows=self.s.rows[:l], frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Rachel
# ************************************************************************/

class Rachel(RelaxedSpider):
    Talon_Class = StackWrapper(WasteTalonStack, max_rounds=1)
    RowStack_Class = RK_RowStack

    def createGame(self):
        RelaxedSpider.createGame(self, waste=1, rows=6, texts=1)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Scorpion - move cards like in Russian Solitaire
# // Scorpion Tail - building down by alternate color
# ************************************************************************/

class Scorpion_RowStack(Yukon_SS_RowStack, Spider_RowStack):
    canDropCards = Spider_RowStack.canDropCards

class Scorpion(RelaxedSpider):

    Hint_Class = YukonType_Hint
    RowStack_Class = StackWrapper(Scorpion_RowStack, base_rank=KING)

    def createGame(self):
        RelaxedSpider.createGame(self, rows=7, playcards=20)

    def startGame(self):
        for i in (4, 4, 4, 0, 0, 0):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def getHighlightPilesStacks(self):
        return ()


class ScorpionTail_RowStack(Yukon_AC_RowStack, Spider_RowStack):
    canDropCards = Spider_RowStack.canDropCards

class ScorpionTail(Scorpion):
    Foundation_Class = Spider_AC_Foundation
    RowStack_Class = StackWrapper(ScorpionTail_RowStack, base_rank=KING)

    shallHighlightMatch = Game._shallHighlightMatch_AC


class DoubleScorpion(Scorpion):
    Talon_Class = InitialDealTalonStack
    def createGame(self):
        RelaxedSpider.createGame(self, rows=10, playcards=26, texts=0)
    def startGame(self):
        for i in (5, 5, 5, 5, 0, 0, 0, 0, 0):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


class TripleScorpion(Scorpion):
    Talon_Class = InitialDealTalonStack
    def createGame(self):
        RelaxedSpider.createGame(self, rows=13, playcards=30, texts=0)
    def startGame(self):
        for i in (5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Wasp
# ************************************************************************/

class Wasp(Scorpion):
    RowStack_Class = Scorpion_RowStack      # anything on an empty space

    def startGame(self):
        for i in (3, 3, 3, 0, 0, 0):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=1, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Three Blind Mice
# // Farmer's Wife
# ************************************************************************/

class ThreeBlindMice(Scorpion):

    Talon_Class = InitialDealTalonStack
    ReserveStack_Class = OpenStack

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        # set window
        w, h = l.XM+10*l.XS, l.XM+2*l.XS+15*l.YOFFSET
        self.setSize(w, h)
        # create stacks
        s.talon = self.Talon_Class(w-l.XS, h-l.YS, self)
        x, y = l.XM+6*l.XS, l.YM
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=ANY_SUIT))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        for i in range(10):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        x, y = l.XM, l.YM
        for i in range(2):
            s.reserves.append(self.ReserveStack_Class(x, y, self))
            x += l.XS
        # default
        l.defaultAll()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.rows[:7], flip=1, frames=0)
            self.s.talon.dealRow(rows=self.s.rows[7:], flip=0, frames=0)
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)


class FarmersWife(ThreeBlindMice):
    Foundation_Class = Spider_AC_Foundation
    RowStack_Class = StackWrapper(ScorpionTail_RowStack, base_rank=KING)


class HowTheyRun(ThreeBlindMice):
    ReserveStack_Class = ReserveStack


# /***********************************************************************
# // Rouge et Noir
# ************************************************************************/

class RougeEtNoir_RowStack(KingAC_RowStack):
    def canDropCards(self, stacks):
        if not self.cards:
            return (None, 0)
        for s in stacks:
            for cards in (self.cards[-1:], self.cards[-13:]):
                if s is not self and s.acceptsCards(self, cards):
                    return (s, len(cards))
        return (None, 0)


class RougeEtNoir(Game):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = DealRowTalonStack
    RowStack_Class = RougeEtNoir_RowStack

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=10, waste=0, texts=1, playcards=23)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        if l.s.waste:
            s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for i in range(4):
            r = l.s.foundations[i]
            s.foundations.append(AC_FoundationStack(r.x, r.y, self, suit=i, max_move=0))
        for i in range(4):
            r = l.s.foundations[i+4]
            s.foundations.append(Spider_AC_Foundation(r.x, r.y, self))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()
        return l

    def startGame(self, flip=0, reverse=1):
        for i in range(3, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[:-i], flip=flip, frames=0, reverse=reverse)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:-1], reverse=reverse)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# /***********************************************************************
# // Mrs. Mop
# ************************************************************************/

class MrsMop(RelaxedSpider):

    Talon_Class = InitialDealTalonStack
    RowStack_Class = Spider_RowStack

    def createGame(self):
        RelaxedSpider.createGame(self, rows=13, playcards=24, texts=0)

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Cicely
# ************************************************************************/

class Cicely_Talon(DealRowTalonStack):
    def dealCards(self, sound=0):
        n = 0
        if sound:
            self.game.startDealSample()
        for i in range(4):
            n += self.dealRow(rows=self.game.s.rows, sound=0)
        if sound:
            self.game.stopSamples()
        return n


class Cicely(Game):

    Hint_Class = CautiousDefaultHint

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+10*l.XS, l.YM+max(5*l.YS, 2*l.YS+16*l.YOFFSET)
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM+l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            y += l.YS
        x, y = l.XM+9*l.XS, l.YM+l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i, base_rank=KING, dir=-1))
            y += l.YS
        x, y = l.XM+l.XS, l.YM
        for i in range(8):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        x, y = l.XM+l.XS, l.YM+l.YS
        for i in range(8):
            s.rows.append(UD_SS_RowStack(x, y, self))
            x += l.XS
        s.talon = Cicely_Talon(l.XM, l.YM, self)
        l.setRegion(s.rows, (l.XM+l.XS-l.CW/2, l.YM+l.YS-l.CH/2,
                             w-l.XS-l.CW/2, 999999))

        # default
        l.defaultAll()


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


    shallHighlightMatch = Game._shallHighlightMatch_SS


# /***********************************************************************
# // Trillium
# // Lily
# // Wake-Robin
# ************************************************************************/

class Trillium(Game):

    Hint_Class = Spider_Hint
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=ANY_RANK)

    def createGame(self, rows=13):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+rows*l.XS, l.YM+l.YS+24*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS

        s.talon = DealRowTalonStack(l.XM+(rows-1)*l.XS/2, h-l.YS, self)
        l.createText(s.talon, "se")

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(frames=0, flip=0)
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_AC

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isAlternateColorSequence(s.cards):
                    return False
        return True


class Lily(Trillium):
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=KING)


class WakeRobin(Trillium):
    RowStack_Class = RK_RowStack

    def createGame(self):
        Trillium.createGame(self, rows=9)

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isRankSequence(s.cards):
                    return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_RK


class TripleWakeRobin(WakeRobin):
    def createGame(self):
        Trillium.createGame(self, rows=13)


# /***********************************************************************
# // Chelicera
# ************************************************************************/

class Chelicera_RowStack(Yukon_SS_RowStack):
    def fillStack(self):
        if not self.cards:
            sound = self.game.app.opt.sound and self.game.app.opt.animations
            talon = self.game.s.talon
            if sound:
                self.game.startDealSample()
            for i in range(3):
                if talon.cards:
                    talon.dealToStacks([self], flip=1, frames=4)
            if sound:
                self.game.stopSamples()


class Chelicera(Game):

    Hint_Class = YukonType_Hint

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+8*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, "s")
        x += l.XS
        for i in range(7):
            s.rows.append(Chelicera_RowStack(x, y, self, base_rank=KING))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.rows[4:])

    def getHighlightPilesStacks(self):
        return ()

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isSameSuitSequence(s.cards):
                    return False
        return True


# /***********************************************************************
# // Scorpion Head
# ************************************************************************/

class ScorpionHead(Scorpion):

    Layout_Method = Layout.freeCellLayout

    def createGame(self, **layout):

        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=7, reserves=4)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])

        # create stacks
        s.talon = InitialDealTalonStack(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(Spider_SS_Foundation(r.x, r.y, self,
                                                      suit=ANY_SUIT))
        for r in l.s.rows:
            s.rows.append(Scorpion_RowStack(r.x, r.y, self,
                                            base_rank=KING))
        for r in l.s.reserves:
            s.reserves.append(ReserveStack(r.x, r.y, self))

        # default
        l.defaultAll()

    def startGame(self):
        rows = self.s.rows
        for i in (3,3,3,3,7,7):
            self.s.talon.dealRow(rows=rows[:i], flip=1, frames=0)
            self.s.talon.dealRow(rows=rows[i:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=rows[:3])


# /***********************************************************************
# // Spider Web
# ************************************************************************/

class SpiderWeb(RelaxedSpider):

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+2*l.YS+16*l.YOFFSET)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, "s")
        x += 2*l.XS
        s.reserves.append(ReserveStack(x, y, self))
        x += 2*l.XS
        for r in range(4):
            s.foundations.append(Spider_SS_Foundation(x, y, self,
                                                      suit=ANY_SUIT))
            x += l.XS
        x, y = l.XM+l.XS, l.YM+l.YS
        for r in range(7):
            s.rows.append(Spider_RowStack(x, y, self,
                                          base_rank=ANY_RANK))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[:3])


# /***********************************************************************
# // Simon Jester
# ************************************************************************/

class SimonJester(Spider):
    Talon_Class = InitialDealTalonStack

    def createGame(self):
        Spider.createGame(self, rows=14, texts=0)

    def startGame(self):
        for l in range(1, 14):
            self.s.talon.dealRow(rows=self.s.rows[:l], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[1:])

# /***********************************************************************
# // Applegate
# ************************************************************************/

class Applegate(Game):
    Hint_Class = YukonType_Hint

    def createGame(self):
        
        # create layout
        l, s = Layout(self), self.s
        self.setSize(l.XM+8*l.XS, l.YM+max(l.YS+16*l.YOFFSET, 4*l.YS))

        x, y = l.XM, l.YM
        s.talon = InitialDealTalonStack(x, y, self)
        x += l.XS
        for i in range(7):
            s.rows.append(Yukon_SS_RowStack(x, y, self, base_rank=KING, mod=13))
            x += l.XS
        x, y = l.XM, l.YM+l.YS
        for i in range(3):
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            y += l.YS

        # default
        l.defaultAll()

    def startGame(self):
        for i in (6, 6, 0, 0, 0):
            self.s.talon.dealRow(rows=self.s.rows[:7-i], frames=0)
            if i:
                self.s.talon.dealRow(rows=self.s.rows[7-i:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)

    def isGameWon(self):
        for s in self.s.rows:
            if len(s.cards) == 0:
                continue
            if len(s.cards) != 13 or not isSameSuitSequence(s.cards):
                return False
        return True

    def getHighlightPilesStacks(self):
        return ()

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# /***********************************************************************
# // Big Spider
# // Spider 3x3
# // Big Divorce
# // Spider (4 decks)
# // Very Big Divorce
# ************************************************************************/

class BigSpider(Spider):
    def createGame(self):
        Spider.createGame(self, rows=13, playcards=28)
    def startGame(self):
        for l in range(5):
            self.s.talon.dealRow(frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealRow()


class BigSpider1Suit(BigSpider):
    pass
class BigSpider2Suits(BigSpider):
    pass


class Spider3x3(BigSpider):
    def startGame(self):
        for l in range(4):
            self.s.talon.dealRow(frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealRow()


class GroundForADivorce3Decks(BigSpider):
    Talon_Class = GroundForADivorce_Talon
    Foundation_Class = StackWrapper(Spider_SS_Foundation, base_rank=ANY_RANK, mod=13)
    RowStack_Class = StackWrapper(Spider_RowStack, mod=13)
    def canDealCards(self):
        return Game.canDealCards(self)
    shallHighlightMatch = Game._shallHighlightMatch_RKW


class Spider4Decks(BigSpider):

    def createGame(self, rows=13):

        l, s = Layout(self), self.s
        w, h = l.XM+(rows+2)*l.XS, l.YM+max(l.YS+24*l.YOFFSET, 9*l.YS)
        self.setSize(w, h)

        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        l.setRegion(s.rows, (-999, -999, l.XM+rows*l.XS-l.CW/2, 999999))
        x = l.XM+rows*l.XS
        for i in range(2):
            y = l.YM
            for j in range(8):
                s.foundations.append(self.Foundation_Class(x, y, self))
                y += l.YS
            x += l.XS

        x, y = w-1.5*l.XS, h-l.YS
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, 'sw')

        l.defaultStackGroups()
        l.defaultRegions()


class GroundForADivorce4Decks(Spider4Decks):
    Talon_Class = GroundForADivorce_Talon
    Foundation_Class = StackWrapper(Spider_SS_Foundation, base_rank=ANY_RANK, mod=13)
    RowStack_Class = StackWrapper(Spider_RowStack, mod=13)
    def createGame(self):
        Spider4Decks.createGame(self, rows=12)
    def canDealCards(self):
        return Game.canDealCards(self)
    shallHighlightMatch = Game._shallHighlightMatch_RKW


# /***********************************************************************
# // York
# ************************************************************************/

class York(RelaxedSpider):

    Talon_Class = InitialDealTalonStack
    Foundation_Class = StackWrapper(Spider_SS_Foundation, base_rank=ANY_RANK, mod=13)
    RowStack_Class = StackWrapper(Spider_RowStack, mod=13)

    def createGame(self):
        RelaxedSpider.createGame(self, rows=12, playcards=26, texts=0)

    def startGame(self):
        for i in range(8):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[2:-2])

class BigYork(York):

    def createGame(self):
        RelaxedSpider.createGame(self, rows=14, playcards=26, texts=0)

    def startGame(self):
        for i in range(10):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=[self.s.rows[0],self.s.rows[-1]])

# /***********************************************************************
# // Spidike
# // Fred's Spider
# ************************************************************************/

class Spidike(RelaxedSpider):
    RowStack_Class = StackWrapper(Spider_SS_RowStack, base_rank=KING)

    def createGame(self, rows=7, playcards=18):
        l, s = Layout(self), self.s
        self.Layout_Method(l, rows=rows, waste=0, playcards=playcards)
        self.setSize(l.size[0], l.size[1])
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(SS_FoundationStack(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        l.defaultAll()

    def startGame(self):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


class FredsSpider(Spidike):
    RowStack_Class = Spider_SS_RowStack

    def createGame(self):
        Spidike.createGame(self, rows=10, playcards=23)

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


class FredsSpider3Decks(FredsSpider):

    def createGame(self):
        Spidike.createGame(self, rows=13, playcards=26)


# /***********************************************************************
# // Long Tail
# // Short Tail
# ************************************************************************/

class LongTail(RelaxedSpider):

    def createGame(self, rows=5, playcards=16):
        l, s = Layout(self), self.s

        decks = self.gameinfo.decks
        max_rows = max(2+decks*4, 2+rows)
        w, h = l.XM+max_rows*l.XS, l.YM+l.YS+playcards*l.YOFFSET
        self.setSize(w, h)

        x, y = l.XM, l.YM
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 'ne')

        x += (max_rows-decks*4)*l.XS
        for i in range(decks*4):
            s.foundations.append(Spider_SS_Foundation(x, y, self))
            x += l.XS

        x, y = l.XM, l.YM+l.YS
        stack = ReserveStack(x, y, self, max_cards=UNLIMITED_CARDS)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
        s.reserves.append(stack)
        l.createText(stack, 'ne')

        x += 2*l.XS
        for i in range(rows):
            s.rows.append(Spider_RowStack(x, y, self))
            x += l.XS

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves*2)


    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack in self.s.reserves:
            return 0
        return 1+RelaxedSpider.getQuickPlayScore(self, ncards, from_stack, to_stack)


class ShortTail(LongTail):
    def createGame(self):
        LongTail.createGame(self, rows=8, playcards=24)


# register the game
registerGame(GameInfo(10, RelaxedSpider, "Relaxed Spider",
                      GI.GT_SPIDER | GI.GT_RELAXED, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(11, Spider, "Spider",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Tarantula",) ))
registerGame(GameInfo(49, BlackWidow, "Black Widow",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Scarab",) ))
registerGame(GameInfo(14, GroundForADivorce, "Ground for a Divorce",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=('Scheidungsgrund',) ))
registerGame(GameInfo(114, GrandmothersGame, "Grandmother's Game",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(24, Spiderette, "Spiderette",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(47, BabySpiderette, "Baby Spiderette",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(48, WillOTheWisp, "Will o' the Wisp",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(50, SimpleSimon, "Simple Simon",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(194, Rachel, "Rachel",
                      GI.GT_SPIDER | GI.GT_XORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(29, Scorpion, "Scorpion",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(185, Wasp, "Wasp",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(220, RougeEtNoir, "Rouge et Noir",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(269, Spider1Suit, "Spider (1 suit)",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL,
                      suits=(0, 0, 0, 0),
                      rules_filename="spider.html"))
registerGame(GameInfo(270, Spider2Suits, "Spider (2 suits)",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL,
                      suits=(0, 0, 2, 2),
                      rules_filename="spider.html"))
registerGame(GameInfo(305, ThreeBlindMice, "Three Blind Mice",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(309, MrsMop, "Mrs. Mop",
                      GI.GT_SPIDER | GI.GT_OPEN, 2, 0, GI.SL_SKILL))
registerGame(GameInfo(341, Cicely, "Cicely",
                      GI.GT_SPIDER, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(342, Trillium, "Trillium",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(343, Lily, "Lily",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(344, Chelicera, "Chelicera",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(345, ScorpionHead, "Scorpion Head",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(346, ScorpionTail, "Scorpion Tail",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(359, SpiderWeb, "Spider Web",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(366, SimonJester, "Simon Jester",
                      GI.GT_SPIDER | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(382, Applegate, "Applegate",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(384, BigSpider, "Big Spider",
                      GI.GT_SPIDER, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(401, GroundForADivorce3Decks, "Big Divorce",
                      GI.GT_SPIDER, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(441, York, "York",
                      GI.GT_SPIDER | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_SKILL))
registerGame(GameInfo(444, BigYork, "Big York",
                      GI.GT_SPIDER | GI.GT_OPEN | GI.GT_ORIGINAL, 3, 0, GI.SL_SKILL))
registerGame(GameInfo(445, BigSpider1Suit, "Big Spider (1 suit)",
                      GI.GT_SPIDER, 3, 0, GI.SL_MOSTLY_SKILL,
                      suits=(0, 0, 0, 0),
                      rules_filename="bigspider.html"))
registerGame(GameInfo(446, BigSpider2Suits, "Big Spider (2 suits)",
                      GI.GT_SPIDER, 3, 0, GI.SL_MOSTLY_SKILL,
                      suits=(0, 0, 2, 2),
                      rules_filename="bigspider.html"))
registerGame(GameInfo(449, Spider3x3, "Spider 3x3",
                      GI.GT_SPIDER | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL,
                      suits=(0, 1, 2),
                      rules_filename="bigspider.html"))
registerGame(GameInfo(454, Spider4Decks, "Spider (4 decks)",
                      GI.GT_SPIDER, 4, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(455, GroundForADivorce4Decks, "Very Big Divorce",
                      GI.GT_SPIDER, 4, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(458, Spidike, "Spidike",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED)) # GT_GYPSY ?
registerGame(GameInfo(459, FredsSpider, "Fred's Spider",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(460, FredsSpider3Decks, "Fred's Spider (3 decks)",
                      GI.GT_SPIDER, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(461, OpenSpider, "Open Spider",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=('Beetle',) ))
registerGame(GameInfo(501, WakeRobin, "Wake-Robin",
                      GI.GT_SPIDER | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(502, TripleWakeRobin, "Wake-Robin (3 decks)",
                      GI.GT_SPIDER | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(511, DoubleScorpion, "Double Scorpion",
                      GI.GT_SPIDER, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(512, TripleScorpion, "Triple Scorpion",
                      GI.GT_SPIDER, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(543, FarmersWife, "Farmer's Wife",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(544, HowTheyRun, "How They Run",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(570, LongTail, "Long Tail",
                      GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(571, ShortTail, "Short Tail",
                      GI.GT_SPIDER | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))

