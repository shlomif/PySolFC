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
from pysollib.mfxutil import kwdefault, Struct
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.hint import KlondikeType_Hint
from pysollib.pysoltk import MfxCanvasText


# /***********************************************************************
# // Klondike
# ************************************************************************/

class Klondike(Game):
    Layout_Method = Layout.klondikeLayout
    Talon_Class = WasteTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = KingAC_RowStack
    Hint_Class = KlondikeType_Hint

    def createGame(self, max_rounds=-1, num_deal=1, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=7, waste=1, texts=1, playcards=16)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self,
                                   max_rounds=max_rounds, num_deal=num_deal)
        if l.s.waste:
            s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for r in l.s.foundations:
            s.foundations.append(self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()
        return l

    def startGame(self, flip=0, reverse=1):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=flip, frames=0, reverse=reverse)
        self.startDealSample()
        self.s.talon.dealRow(reverse=reverse)
        if self.s.waste:
            self.s.talon.dealCards()      # deal first card to WasteStack

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# /***********************************************************************
# // Vegas Klondike
# ************************************************************************/

class VegasKlondike(Klondike):
    getGameScore = Game.getGameScoreCasino
    getGameBalance = Game.getGameScoreCasino

    def createGame(self, max_rounds=1):
        Klondike.createGame(self, max_rounds=max_rounds)
        self.texts.score = MfxCanvasText(self.canvas,
                                         8, self.height - 8, anchor="sw",
                                         font=self.app.getFont("canvas_large"))

    def updateText(self):
        if self.preview > 1:
            return
        b1, b2 = self.app.stats.gameid_balance, 0
        if self.shallUpdateBalance():
            b2 = self.getGameBalance()
        if 0 and self.app.debug:
            t = "Balance %d/%d" % (b1, b2)
        else:
            t = _("Balance $%d") % (b1 + b2)
        self.texts.score.config(text=t)

    def getDemoInfoTextAttr(self, tinfo):
        return tinfo[1]     # "se" corner


# /***********************************************************************
# // Casino Klondike
# ************************************************************************/

class CasinoKlondike(VegasKlondike):
    def createGame(self):
        VegasKlondike.createGame(self, max_rounds=3)


# /***********************************************************************
# // Klondike by Threes
# ************************************************************************/

class KlondikeByThrees(Klondike):
    def createGame(self):
        Klondike.createGame(self, num_deal=3)


# /***********************************************************************
# // Thumb and Pouch
# ************************************************************************/

class ThumbAndPouch_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isAnySuitButOwnSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        return _('Row. Build down in any suit but the same.')


class ThumbAndPouch(Klondike):
    RowStack_Class = ThumbAndPouch_RowStack

    def createGame(self):
        Klondike.createGame(self, max_rounds=1)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit != card2.suit and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# /***********************************************************************
# // Whitehead
# ************************************************************************/

class Whitehead_RowStack(SS_RowStack):
    def _isAcceptableSequence(self, cards):
        return isSameColorSequence(cards, self.cap.mod, self.cap.dir)

class Whitehead(Klondike):
    RowStack_Class = Whitehead_RowStack
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        Klondike.createGame(self, max_rounds=1)

    def startGame(self):
        Klondike.startGame(self, flip=1)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# /***********************************************************************
# // Small Harp (Klondike in a different layout)
# ************************************************************************/

class SmallHarp(Klondike):
    Layout_Method = Layout.gypsyLayout

    def startGame(self):
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Eastcliff
# // Easthaven
# ************************************************************************/

class Eastcliff(Klondike):
    RowStack_Class = AC_RowStack

    def createGame(self):
        Klondike.createGame(self, max_rounds=1)

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        if self.s.waste:
            self.s.talon.dealCards()      # deal first card to WasteStack


class Easthaven(Eastcliff):
    Talon_Class = DealRowTalonStack
    def createGame(self):
        Klondike.createGame(self, max_rounds=1, waste=0)

class DoubleEasthaven(Easthaven):
    def createGame(self):
        Klondike.createGame(self, rows=8, max_rounds=1, waste=0, playcards=20)

class TripleEasthaven(Easthaven):
    def createGame(self):
        Klondike.createGame(self, rows=12, max_rounds=1, waste=0, playcards=26)


# /***********************************************************************
# // Westcliff
# // Westhaven
# ************************************************************************/

class Westcliff(Eastcliff):
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10)


class Westhaven(Westcliff):
    Talon_Class = DealRowTalonStack

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10, waste=0)


# /***********************************************************************
# // Pas Seul
# ************************************************************************/

class PasSeul(Eastcliff):
    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=6)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Blind Alleys
# ************************************************************************/

class BlindAlleys(Eastcliff):
    def createGame(self):
        Klondike.createGame(self, max_rounds=2, rows=6)

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        Eastcliff.startGame(self)


# /***********************************************************************
# // Somerset
# // Morehead
# ************************************************************************/

class Somerset(Klondike):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = StackWrapper(AC_RowStack, max_move=1)
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10, waste=0, texts=0)

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.rows[i:], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[6:])
        self.s.talon.dealRow(rows=self.s.rows[7:])


class Morehead(Somerset):
    RowStack_Class = StackWrapper(ThumbAndPouch_RowStack, max_move=1)


# /***********************************************************************
# // Canister
# ************************************************************************/

class Canister(Klondike):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = RK_RowStack
    ###Hint_Class = CautiousDefaultHint

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=8, waste=0, texts=0)

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[2:6])


# /***********************************************************************
# // Agnes Sorel
# ************************************************************************/

class AgnesSorel(Klondike):
    Talon_Class = DealRowTalonStack
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=NO_RANK, max_move=0)
    RowStack_Class = StackWrapper(SC_RowStack, mod=13, base_rank=NO_RANK)

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, waste=0)

    def startGame(self):
        Klondike.startGame(self, flip=1)
        c = self.s.talon.dealSingleBaseCard()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color == card2.color and
                ((card1.rank + 1) % 13 == card2.rank or (card2.rank + 1) % 13 == card1.rank))


# /***********************************************************************
# // 8 x 8
# // Achtmal Acht
# ************************************************************************/

class EightTimesEight(Klondike):
    Layout_Method = Layout.gypsyLayout
    RowStack_Class = AC_RowStack

    def createGame(self):
        Klondike.createGame(self, rows=8)

    def startGame(self):
        for i in range(7):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


class AchtmalAcht(EightTimesEight):
    def createGame(self):
        l = Klondike.createGame(self, rows=8, max_rounds=3)
        s = self.s
        x, y = s.waste.x - l.XM, s.waste.y
        s.talon.texts.rounds = MfxCanvasText(self.canvas, x, y,
                                             anchor="ne",
                                             font=self.app.getFont("canvas_default"))


# /***********************************************************************
# // Batsford
# ************************************************************************/

class Batsford_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return 0
        # must be a King
        return cards[0].rank == KING
    def getHelp(self):
        return _('Reserve. Only Kings are acceptable.')

class Batsford(Klondike):
    def createGame(self, **layout):
        l = Klondike.createGame(self, rows=10, max_rounds=1, playcards=22)
        s = self.s
        x, y = l.XM, self.height - l.YS
        s.reserves.append(Batsford_ReserveStack(x, y, self, max_cards=3))
        self.setRegion(s.reserves, (-999, y - l.YM, x + l.XS, 999999), priority=1)
        l.createText(s.reserves[0], "se")
        l.defaultStackGroups()


# /***********************************************************************
# // Jumbo
# ************************************************************************/

class Jumbo(Klondike):
    def createGame(self):
        Klondike.createGame(self, rows=9, max_rounds=2)

    def startGame(self, flip=0):
        for i in range(9):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=flip, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

class OpenJumbo(Jumbo):
    def startGame(self):
        Jumbo.startGame(self, flip=1)


# /***********************************************************************
# // Stonewall
# // Flower Garden
# ************************************************************************/

class Stonewall(Klondike):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = AC_RowStack

    DEAL = (0, 1, 0, 1, -1, 0, 1)

    def createGame(self):
        l = Klondike.createGame(self, rows=6, max_rounds=1, texts=0)
        s = self.s
        h = max(self.height, l.YM+4*l.YS)
        self.setSize(self.width + l.XM+4*l.XS, h)
        for i in range(4):
            for j in range(4):
                x, y = self.width + (j-4)*l.XS, l.YM + i*l.YS
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
        l.defaultStackGroups()

    def startGame(self):
        frames = 0
        for flip in self.DEAL:
            if flip < 0:
                frames = -1
                self.startDealSample()
            else:
                self.s.talon.dealRow(flip=flip, frames=frames)
        self.s.talon.dealRow(rows=self.s.reserves)
        assert len(self.s.talon.cards) == 0


class FlowerGarden(Stonewall):
    RowStack_Class = StackWrapper(RK_RowStack, max_move=1)
    Hint_Class = CautiousDefaultHint

    DEAL = (1, 1, 1, 1, -1, 1, 1)


# /***********************************************************************
# // King Albert
# // Raglan
# // Brigade
# ************************************************************************/

class KingAlbert(Klondike):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = StackWrapper(AC_RowStack, max_move=1)
    Hint_Class = CautiousDefaultHint

    ROWS = 9
    RESERVES = (2, 2, 2, 1)

    def createGame(self):
        l = Klondike.createGame(self, max_rounds=1, rows=self.ROWS, waste=0, texts=0)
        s = self.s
        rw, rh = max(self.RESERVES), len(self.RESERVES)
        h = max(self.height, l.YM+rh*l.YS)
        self.setSize(self.width + 2*l.XM+rw*l.XS, h)
        for i in range(rh):
            for j in range(self.RESERVES[i]):
                x, y = self.width + (j-rw)*l.XS, l.YM + i*l.YS
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
        l.defaultStackGroups()

    def startGame(self):
        Klondike.startGame(self, flip=1, reverse=0)
        self.s.talon.dealRow(rows=self.s.reserves)


class Raglan(KingAlbert):
    RESERVES = (2, 2, 2)

    def _shuffleHook(self, cards):
        # move Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.rows[i:], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[6:])
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow(rows=self.s.foundations)


class Brigade(Raglan):
    RowStack_Class = StackWrapper(RK_RowStack, max_move=1)

    ROWS = 7
    RESERVES = (4, 4, 4, 1)

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow(rows=self.s.foundations)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank)


# /***********************************************************************
# // Jane
# // Agnes Bernauer
# ************************************************************************/

class Jane_Talon(OpenTalonStack):
    def canFlipCard(self):
        return 0

    def canDealCards(self):
        return len(self.cards) >= 2

    def dealCards(self, sound=0):
        c = 0
        if len(self.cards) > 2:
            c = self.dealRow(self.game.s.reserves, sound=sound)
        if len(self.cards) == 2:
            self.game.flipMove(self)
            self.game.moveMove(1, self, self.game.s.waste, frames=4, shadow=0)
            self.game.flipMove(self)
            c = c + 1
        return c


class Jane(Klondike):
    Talon_Class = Jane_Talon
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=NO_RANK, min_cards=1)
    RowStack_Class = StackWrapper(AC_RowStack, mod=13, base_rank=NO_RANK)

    def createGame(self, max_rounds=1, reserves=7, **layout):
        kwdefault(layout, texts=0)
        l = apply(Klondike.createGame, (self, max_rounds), layout)
        s = self.s
        h = max(self.height, l.YM+4*l.YS)
        self.setSize(self.width + l.XM+2*l.XS, h)
        x0, y = self.width - 2*l.XS, l.YM
        for i in range(reserves):
            x = x0 + ((i+1) & 1) * l.XS
            stack = OpenStack(x, y, self, max_accept=0)
            stack.CARD_YOFFSET = l.YM / 3
            stack.is_open = 1
            s.reserves.append(stack)
            y = y + l.YS / 2
        # not needed, as no cards may be placed on the reserves
        ##self.setRegion(s.reserves, (x0-l.XM/2, -999, 999999, 999999), priority=1)
        l.defaultStackGroups()
        self.sg.dropstacks.append(s.talon)
        x, y = l.XM, self.height - l.YM
        # ???
        #self.texts.info = MfxCanvasText(self.canvas, x, y, anchor="sw",
        #                                font=self.app.getFont("canvas_default"))
        l.createText(s.talon, 'ss')

    def startGame(self, flip=0, reverse=1):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=flip, frames=0, reverse=reverse)
        self.startDealSample()
        self.s.talon.dealRow(reverse=reverse)
        self.s.talon.dealRow(rows=self.s.reserves)
        c = self.s.talon.dealSingleBaseCard()
        # update base rank of row stacks
        cap = Struct(base_rank=(c.rank - 1) % 13)
        for s in self.s.rows:
            s.cap.update(cap.__dict__)
            self.saveinfo.stack_caps.append((s.id, cap))

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % 13 == card2.rank or (card2.rank + 1) % 13 == card1.rank))

    def _autoDeal(self, sound=1):
        return 0


class AgnesBernauer_Talon(DealRowTalonStack):
    def dealCards(self, sound=0):
        return self.dealRowAvail(self.game.s.reserves, sound=sound)


class AgnesBernauer(Jane):
    Talon_Class = AgnesBernauer_Talon
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=NO_RANK, max_move=0)

    def createGame(self):
        Jane.createGame(self, max_rounds=1, waste=0, texts=1)

    def startGame(self):
        Jane.startGame(self, flip=1)


# /***********************************************************************
# // Senate
# ************************************************************************/

class Senate(Jane):

    def createGame(self, rows=4):

        playcards = 10

        l, s = Layout(self), self.s
        self.setSize(3*l.XM+(rows+6)*l.XS, l.YM+2*(l.YS+playcards*l.YOFFSET))

        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(SS_RowStack(x, y, self))
            x += l.XS

        for y in l.YM, l.YM+l.YS+playcards*l.YOFFSET:
            x = 2*l.XM+rows*l.XS
            for i in range(4):
                stack = OpenStack(x, y, self, max_accept=0)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
                s.reserves.append(stack)
                x += l.XS
        x = 3*l.XM+(rows+4)*l.XS
        for i in range(2):
            y = l.YM+l.YS
            for j in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j))
                y += l.YS
            x += l.XS
        x, y = 3*l.XM+(rows+5)*l.XS, l.YM
        s.talon = AgnesBernauer_Talon(x, y, self)
        l.createText(s.talon, 'sw')

        l.defaultStackGroups()


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow()


    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))

class SenatePlus(Senate):
    def createGame(self):
        Senate.createGame(self, rows=5)

# /***********************************************************************
# // Phoenix
# // Arizona
# ************************************************************************/

class Phoenix(Klondike):

    Hint_Class = CautiousDefaultHint
    RowStack_Class = AC_RowStack

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM + 10*l.XS, l.YM + 4*(l.YS+l.YM))

        for i in range(2):
            x = l.XM + i*l.XS
            for j in range(4):
                y = l.YM + j*(l.YS+l.YM)
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
        for i in range(2):
            x = l.XM + (8+i)*l.XS
            for j in range(4):
                y = l.YM + j*(l.YS+l.YM)
                s.reserves.append(OpenStack(x, y, self, max_accept=0))
        for i in range(4):
            s.foundations.append(SS_FoundationStack(l.XM+(3+i)*l.XS, l.YM, self, i))
        for i in range(6):
            s.rows.append(self.RowStack_Class(l.XM+(2+i)*l.XS, l.YM+l.YS, self))
        s.talon = InitialDealTalonStack(l.XM+int(4.5*l.XS), l.YM+3*(l.YS+l.YM), self)

        l.defaultStackGroups()

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)


class Arizona(Phoenix):
    RowStack_Class = RK_RowStack


# /***********************************************************************
# // Alternation
# ************************************************************************/

class Alternation(Klondike):

    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=ANY_RANK)

    def createGame(self):
        Klondike.createGame(self, max_rounds=1)

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.rows, flip=(i+1)%2, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Lanes
# ************************************************************************/

class Lanes(Klondike):

    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=ANY_RANK, max_move=1)

    def createGame(self):
        Klondike.createGame(self, rows=6, max_rounds=2)

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Thirty Six
# ************************************************************************/

class ThirtySix(Klondike):

    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = StackWrapper(RK_RowStack, base_rank=ANY_RANK)

    def createGame(self):
        Klondike.createGame(self, rows=6, max_rounds=1)

    def _fillOne(self):
        for r in self.s.rows:
            if r.cards:
                c = r.cards[-1]
                for f in self.s.foundations:
                    if f.acceptsCards(r, [c]):
                        self.moveMove(1, r, f, frames=4, shadow=0)
                        return 1
        return 0

    def startGame(self):
        self.startDealSample()
        for i in range(6):
            self.s.talon.dealRow()
            while True:
                if not self._fillOne():
                    break
        self.s.talon.dealCards()          # deal first card to WasteStack

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank-card2.rank) == 1


# /***********************************************************************
# // Q.C.
# ************************************************************************/

class Q_C_(Klondike):

    Hint_Class = CautiousDefaultHint
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=ANY_RANK, max_move=1)

    def createGame(self):
        Klondike.createGame(self, rows=6, max_rounds=2)

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack
        self.fillAll()

    def fillOne(self, stack):
        if stack.cards:
            c = stack.cards[-1]
            for f in self.s.foundations:
                if f.acceptsCards(stack, [c]):
                    stack.moveMove(1, f)
                    return 1
        return 0

    def fillAll(self):
        # rows
        for r in self.s.rows:
            if self.fillOne(r):
                self.fillAll()
                return
        # waste
        if self.fillOne(self.s.waste):
            self.fillAll()

    def fillStack(self, stack):
        if stack in self.s.rows:
            if not stack.cards and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
        self.fillAll()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1


# /***********************************************************************
# // Northwest Territory
# ************************************************************************/

class NorthwestTerritory(KingAlbert):
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=KING)
    RESERVES = (4, 4, 4, 4)
    ROWS = 8

    def startGame(self):
        Klondike.startGame(self, flip=0, reverse=0)
        self.s.talon.dealRow(rows=self.s.reserves)


# /***********************************************************************
# // Aunt Mary
# ************************************************************************/

class AuntMary(Klondike):
    def createGame(self):
        Klondike.createGame(self, rows=6, max_rounds=1)
    def startGame(self):
        for i in range(5):
            j = i+1
            self.s.talon.dealRow(rows=self.s.rows[:j], frames=0, flip=1)
            self.s.talon.dealRow(rows=self.s.rows[j:], frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


# /***********************************************************************
# // Double Dot
# ************************************************************************/

class DoubleDot(Klondike):
    Talon_Class = DealRowTalonStack
    RowStack_Class = StackWrapper(RK_RowStack, dir=-2, mod=13)
    Foundation_Class = StackWrapper(SS_FoundationStack, dir=2, mod=13)

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=8, waste=0)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: ((c.rank == ACE and c.suit in (0,1)) or
                              (c.rank == 1 and c.suit in (2,3)), c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Seven Devils
# ************************************************************************/

class SevenDevils_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return not from_stack in self.game.s.reserves


class SevenDevils(Klondike):

    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(SevenDevils_RowStack, max_move=1)

    def createGame(self):
        
        l, s = Layout(self), self.s
        self.setSize(l.XM + 10*l.XS, l.YM+3*l.YS+12*l.YOFFSET)

        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS
        x, y = l.XM+l.XS/2, l.YM+l.YS
        for i in range(7):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        x0, y = self.width - 2*l.XS, l.YM
        for i in range(7):
            x = x0 + ((i+1) & 1) * l.XS
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            y = y + l.YS / 2
        x, y = l.XM, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'n')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        l.defaultStackGroups()


    def startGame(self, flip=0, reverse=1):
        Klondike.startGame(self)
        self.s.talon.dealRow(rows=self.s.reserves)


# /***********************************************************************
# // Moving Left
# ************************************************************************/

class MovingLeft(Klondike):

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10, playcards=24)

    def fillStack(self, stack):
        if not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if stack in self.s.rows:
                i = list(self.s.rows).index(stack)
                if i < 9:
                    from_stack = self.s.rows[i+1]
                    pile = from_stack.getPile()
                    if pile:
                        from_stack.moveMove(len(pile), stack)
            self.leaveState(old_state)


# register the game
registerGame(GameInfo(2, Klondike, "Klondike",
                      GI.GT_KLONDIKE, 1, -1))
registerGame(GameInfo(61, CasinoKlondike, "Casino Klondike",
                      GI.GT_KLONDIKE | GI.GT_SCORE, 1, 2))
registerGame(GameInfo(129, VegasKlondike, "Vegas Klondike",
                      GI.GT_KLONDIKE | GI.GT_SCORE, 1, 0))
registerGame(GameInfo(18, KlondikeByThrees, "Klondike by Threes",
                      GI.GT_KLONDIKE, 1, -1))
registerGame(GameInfo(58, ThumbAndPouch, "Thumb and Pouch",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(67, Whitehead, "Whitehead",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(39, SmallHarp, "Small Harp",
                      GI.GT_KLONDIKE, 1, -1,
                      altnames=("Die kleine Harfe",) ))
registerGame(GameInfo(66, Eastcliff, "Eastcliff",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(224, Easthaven, "Easthaven",
                      GI.GT_GYPSY, 1, 0))
registerGame(GameInfo(33, Westcliff, "Westcliff",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(225, Westhaven, "Westhaven",
                      GI.GT_GYPSY, 1, 0))
registerGame(GameInfo(107, PasSeul, "Pas Seul",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(81, BlindAlleys, "Blind Alleys",
                      GI.GT_KLONDIKE, 1, 1))
registerGame(GameInfo(215, Somerset, "Somerset",
                      GI.GT_KLONDIKE | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(231, Canister, "Canister",
                      GI.GT_KLONDIKE | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(229, AgnesSorel, "Agnes Sorel",
                      GI.GT_GYPSY, 1, 0))
registerGame(GameInfo(4, EightTimesEight, "8 x 8",
                      GI.GT_KLONDIKE, 2, -1))
registerGame(GameInfo(127, AchtmalAcht, "Eight Times Eight",
                      GI.GT_KLONDIKE, 2, 2,
                      altnames=("Achtmal Acht",) ))
registerGame(GameInfo(133, Batsford, "Batsford",
                      GI.GT_KLONDIKE, 2, 0))
registerGame(GameInfo(221, Stonewall, "Stonewall",
                      GI.GT_RAGLAN, 1, 0))
registerGame(GameInfo(222, FlowerGarden, "Flower Garden",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0,
                      altnames=("The Bouquet", "The Garden",) ))
registerGame(GameInfo(233, KingAlbert, "King Albert",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0,
                      altnames=("Idiot's Delight",) ))
registerGame(GameInfo(232, Raglan, "Raglan",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(223, Brigade, "Brigade",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(230, Jane, "Jane",
                      GI.GT_RAGLAN, 1, 0))
registerGame(GameInfo(236, AgnesBernauer, "Agnes Bernauer",
                      GI.GT_RAGLAN, 1, 0))
registerGame(GameInfo(263, Phoenix, "Phoenix",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(283, Jumbo, "Jumbo",
                      GI.GT_KLONDIKE, 2, 1))
registerGame(GameInfo(333, OpenJumbo, "Open Jumbo",
                      GI.GT_KLONDIKE, 2, 1))
registerGame(GameInfo(297, Alternation, "Alternation",
                      GI.GT_KLONDIKE, 2, 0))
registerGame(GameInfo(326, Lanes, "Lanes",
                      GI.GT_KLONDIKE, 1, 1))
registerGame(GameInfo(327, ThirtySix, "Thirty Six",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(350, Q_C_, "Q.C.",
                      GI.GT_KLONDIKE, 2, 1))
registerGame(GameInfo(361, NorthwestTerritory, "Northwest Territory",
                      GI.GT_RAGLAN, 1, 0))
registerGame(GameInfo(362, Morehead, "Morehead",
                      GI.GT_KLONDIKE | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(388, Senate, "Senate",
                      GI.GT_RAGLAN, 2, 0))
registerGame(GameInfo(389, SenatePlus, "Senate +",
                      GI.GT_RAGLAN, 2, 0))
registerGame(GameInfo(390, Arizona, "Arizona",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(407, AuntMary, "Aunt Mary",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(420, DoubleDot, "Double Dot",
                      GI.GT_KLONDIKE, 1, 0))
registerGame(GameInfo(434, SevenDevils, "Seven Devils",
                      GI.GT_RAGLAN, 2, 0))
registerGame(GameInfo(452, DoubleEasthaven, "Double Easthaven",
                      GI.GT_GYPSY, 2, 0))
registerGame(GameInfo(453, TripleEasthaven, "Triple Easthaven",
                      GI.GT_GYPSY, 3, 0))
registerGame(GameInfo(470, MovingLeft, "Moving Left",
                      GI.GT_KLONDIKE, 2, 0))

