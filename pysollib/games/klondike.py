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
from pysollib.hint import FreeCellSolverWrapper
from pysollib.pysoltk import MfxCanvasText

from canfield import CanfieldRush_Talon


# ************************************************************************
# * Klondike
# ************************************************************************

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
        self.Layout_Method(l, **layout)
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

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Vegas Klondike
# ************************************************************************

class VegasKlondike(Klondike):
    getGameScore = Game.getGameScoreCasino
    getGameBalance = Game.getGameScoreCasino

    def createGame(self, max_rounds=1):
        l = Klondike.createGame(self, max_rounds=max_rounds)
        self.texts.score = MfxCanvasText(self.canvas,
                                         8, self.height - 8, anchor="sw",
                                         font=self.app.getFont("canvas_large"))
        return l

    def updateText(self):
        if self.preview > 1:
            return
        b1, b2 = self.app.stats.gameid_balance, 0
        if self.shallUpdateBalance():
            b2 = self.getGameBalance()
        t = _("Balance $%d") % (b1 + b2)
        self.texts.score.config(text=t)

    def getDemoInfoTextAttr(self, tinfo):
        return tinfo[1]     # "se" corner


# ************************************************************************
# * Casino Klondike
# ************************************************************************

class CasinoKlondike(VegasKlondike):
    def createGame(self):
        l = VegasKlondike.createGame(self, max_rounds=3)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)


# ************************************************************************
# * Klondike by Threes
# ************************************************************************

class KlondikeByThrees(Klondike):
    def createGame(self):
        Klondike.createGame(self, num_deal=3)


# ************************************************************************
# * Thumb and Pouch
# * Chinaman
# ************************************************************************

class ThumbAndPouch(Klondike):
    RowStack_Class = BO_RowStack

    def createGame(self):
        Klondike.createGame(self, max_rounds=1)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit != card2.suit
                and (card1.rank + 1 == card2.rank
                     or card2.rank + 1 == card1.rank))


class Chinaman(ThumbAndPouch):
    RowStack_Class = StackWrapper(BO_RowStack, base_rank=KING)

    def createGame(self):
        l = Klondike.createGame(self, num_deal=3,
                                max_rounds=2, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)


# ************************************************************************
# * Whitehead
# ************************************************************************

class Whitehead_RowStack(SS_RowStack):
    def _isAcceptableSequence(self, cards):
        return isSameColorSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        return _('Tableau. Build down by color. Sequences of cards in the same suit can be moved as a unit.')

class Whitehead(Klondike):
    RowStack_Class = Whitehead_RowStack
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        Klondike.createGame(self, max_rounds=1)

    def startGame(self):
        Klondike.startGame(self, flip=1)

    shallHighlightMatch = Game._shallHighlightMatch_SS
    getQuickPlayScore = Game._getSpiderQuickPlayScore


# ************************************************************************
# * Small Harp (Klondike in a different layout)
# ************************************************************************

class SmallHarp(Klondike):
    Layout_Method = Layout.gypsyLayout

    def startGame(self):
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Eastcliff
# * Easthaven
# ************************************************************************

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


# ************************************************************************
# * Westcliff
# * Westhaven
# ************************************************************************

class Westcliff(Eastcliff):
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10)


class Westhaven(Westcliff):
    Talon_Class = DealRowTalonStack

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10, waste=0)


# ************************************************************************
# * Pas Seul
# ************************************************************************

class PasSeul(Eastcliff):
    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=6)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# ************************************************************************
# * Blind Alleys
# ************************************************************************

class BlindAlleys(Eastcliff):
    def createGame(self):
        l = Klondike.createGame(self, max_rounds=2, rows=6, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        Eastcliff.startGame(self)


# ************************************************************************
# * Somerset
# * Morehead
# * Usk
# ************************************************************************

class Somerset(Klondike):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = SuperMoveAC_RowStack
    Hint_Class = CautiousDefaultHint
    Solver_Class = FreeCellSolverWrapper()

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10, waste=0, texts=0)

    def startGame(self):
        for i in range(6):
            self.s.talon.dealRow(rows=self.s.rows[i:], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[6:])
        self.s.talon.dealRow(rows=self.s.rows[7:])


class Morehead(Somerset):
    RowStack_Class = StackWrapper(BO_RowStack, max_move=1)
    Solver_Class = None


class Usk(Somerset):

    Talon_Class = RedealTalonStack
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=KING)
    Solver_Class = None

    def createGame(self):
        l = Klondike.createGame(self, max_rounds=2, rows=10,
                                waste=False, texts=False, round_text=True)
        l.createRoundText(self.s.talon, 'ne')

    def redealCards(self):
        n = 0
        while self.s.talon.cards:
            self.s.talon.dealRowAvail(rows=self.s.rows[n:], frames=4)
            n += 1

# ************************************************************************
# * Canister
# * American Canister
# * British Canister
# ************************************************************************

class AmericanCanister(Klondike):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = AC_RowStack
    Solver_Class = FreeCellSolverWrapper(sm='unlimited')

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=8, waste=0, texts=0)

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[2:6])


class Canister(AmericanCanister):
    RowStack_Class = RK_RowStack
    Solver_Class = FreeCellSolverWrapper(sbb='rank', sm='unlimited')
    shallHighlightMatch = Game._shallHighlightMatch_RK


class BritishCanister(AmericanCanister):
    RowStack_Class = StackWrapper(KingAC_RowStack, max_move=1)
    Solver_Class = FreeCellSolverWrapper(esf='kings')


# ************************************************************************
# * Agnes Sorel
# ************************************************************************

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
                ((card1.rank + 1) % 13 == card2.rank or
                 (card2.rank + 1) % 13 == card1.rank))


# ************************************************************************
# * 8 x 8
# * Achtmal Acht
# * Eight by Eight
# ************************************************************************

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
        l = Klondike.createGame(self, rows=8, max_rounds=3, round_text=True)
        l.createRoundText(self.s.talon, 'sw', dx=-l.XS)


class EightByEight_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return len(cards) == 1
        return True

class EightByEight(EightTimesEight):
    Layout_Method = Layout.klondikeLayout ##gypsyLayout
    Talon_Class = CanfieldRush_Talon
    RowStack_Class = EightByEight_RowStack

    def createGame(self):
        l = Klondike.createGame(self, rows=8, playcards=20,
                                max_rounds=3, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Batsford
# * Batsford Again
# ************************************************************************

class Batsford_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        # must be a King
        return cards[0].rank == KING
    def getHelp(self):
        return _('Reserve. Only Kings are acceptable.')

class Batsford(Klondike):
    def createGame(self, **layout):
        kwdefault(layout, rows=10, max_rounds=1, playcards=22)
        round_text = (layout['max_rounds'] > 1)
        layout['round_text'] = round_text
        l = Klondike.createGame(self, **layout)
        s = self.s
        x, y = l.XM, self.height - l.YS
        s.reserves.append(Batsford_ReserveStack(x, y, self, max_cards=3))
        self.setRegion(s.reserves, (-999, y - l.YM - l.CH/2, x + l.XS - l.CW/2, 999999), priority=1)
        l.createText(s.reserves[0], "se")
        if round_text:
            l.createRoundText(self.s.talon, 'ne', dx=l.XS)
        l.defaultStackGroups()


class BatsfordAgain(Batsford):
    def createGame(self):
        Batsford.createGame(self, max_rounds=2)


# ************************************************************************
# * Jumbo
# ************************************************************************

class Jumbo(Klondike):
    def createGame(self):
        l = Klondike.createGame(self, rows=9, max_rounds=2, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)

    def startGame(self, flip=0):
        for i in range(9):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=flip, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

class OpenJumbo(Jumbo):
    def startGame(self):
        Jumbo.startGame(self, flip=1)


# ************************************************************************
# * Stonewall
# * Flower Garden
# ************************************************************************

class Stonewall(Klondike):
    Talon_Class = InitialDealTalonStack
    RowStack_Class = AC_RowStack

    DEAL = (0, 1, 0, 1, -1, 0, 1)

    def createGame(self):
        l = Klondike.createGame(self, rows=6, waste=0, max_rounds=1, texts=0)
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


class FlowerGarden(Stonewall):
    RowStack_Class = StackWrapper(RK_RowStack, max_move=1)
    Hint_Class = CautiousDefaultHint

    DEAL = (1, 1, 1, 1, -1, 1, 1)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * King Albert
# * Raglan
# * Brigade
# * Queen Victoria
# ************************************************************************

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

    shallHighlightMatch = Game._shallHighlightMatch_RK


class QueenVictoria(KingAlbert):
    RowStack_Class = AC_RowStack


# ************************************************************************
# * Jane
# * Agnes Bernauer
# ************************************************************************

class Jane_Talon(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler

    def canFlipCard(self):
        return False

    def canDealCards(self):
        return len(self.cards) >= 2

    def dealCards(self, sound=False):
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

    def createGame(self, max_rounds=1, rows=7, reserves=7, playcards=16):
        l, s = Layout(self), self.s
        maxrows = max(rows, 7)
        w = l.XM+maxrows*l.XS+l.XM+2*l.XS
        h = max(l.YM+2*l.YS+playcards*l.YOFFSET+l.TEXT_HEIGHT, l.YM+4*l.YS)
        self.setSize(w, h)

        x, y = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)

        x += 2*l.XS
        for i in range(4):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
            x += l.XS

        x, y = l.XM, l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS

        x0, y = self.width - 2*l.XS, l.YM
        for i in range(reserves):
            x = x0 + ((i+1) & 1) * l.XS
            stack = OpenStack(x, y, self, max_accept=0)
            stack.CARD_YOFFSET = l.YM / 3
            s.reserves.append(stack)
            y = y + l.YS / 2
        # not needed, as no cards may be placed on the reserves
        ##self.setRegion(s.reserves, (x0-l.XM/2, -999, 999999, 999999), priority=1)
        l.defaultStackGroups()
        self.sg.dropstacks.append(s.talon)

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

    shallHighlightMatch = Game._shallHighlightMatch_ACW

    def _autoDeal(self, sound=True):
        return 0


class AgnesBernauer_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        return self.dealRowAvail(self.game.s.reserves, sound=sound)


class AgnesBernauer(Jane):
    Talon_Class = AgnesBernauer_Talon
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=NO_RANK, max_move=0)

    def startGame(self):
        Jane.startGame(self, flip=1)


# ************************************************************************
# * Senate
# ************************************************************************

class Senate(Jane):

    def createGame(self, rows=4):

        playcards = 10

        l, s = Layout(self), self.s
        self.setSize(l.XM+(rows+7)*l.XS, l.YM+2*(l.YS+playcards*l.YOFFSET))

        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(SS_RowStack(x, y, self))
            x += l.XS

        for y in l.YM, l.YM+l.YS+playcards*l.YOFFSET:
            x = l.XM+rows*l.XS+l.XS/2
            for i in range(4):
                stack = OpenStack(x, y, self, max_accept=0)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
                s.reserves.append(stack)
                x += l.XS
        x = l.XM+(rows+5)*l.XS
        for i in range(2):
            y = l.YM+l.YS
            for j in range(4):
                s.foundations.append(SS_FoundationStack(x, y, self, suit=j))
                y += l.YS
            x += l.XS
        x, y = self.width-l.XS, l.YM
        s.talon = AgnesBernauer_Talon(x, y, self)
        l.createText(s.talon, 'nw')

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

    shallHighlightMatch = Game._shallHighlightMatch_SS


class SenatePlus(Senate):
    def createGame(self):
        Senate.createGame(self, rows=5)

# ************************************************************************
# * Phoenix
# * Arizona
# ************************************************************************

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

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Lanes
# ************************************************************************

class Lanes(Klondike):

    Hint_Class = CautiousDefaultHint
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=ANY_RANK, max_move=1)

    def createGame(self):
        l = Klondike.createGame(self, rows=6, max_rounds=2, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)

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


# ************************************************************************
# * Thirty Six
# ************************************************************************

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

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Q.C.
# ************************************************************************

class Q_C_(Klondike):

    Hint_Class = CautiousDefaultHint
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=ANY_RANK, max_move=1)

    def createGame(self):
        l = Klondike.createGame(self, rows=6, max_rounds=2)
        l.createRoundText(self.s.talon, 'sss')

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        while self.s.talon.cards:
            self.s.talon.dealCards()    # deal first card to WasteStack
            if not self.fillWaste():
                break

    def fillWaste(self):
        waste = self.s.waste
        if waste.cards:
            c = waste.cards[-1]
            for f in self.s.foundations:
                if f.acceptsCards(self.s.waste, [c]):
                    waste.moveMove(1, f)
                    return True
        return False

    def fillStack(self, stack=None):
        waste = self.s.waste
        while True:
            if not self.fillWaste():
                break
        if stack in self.s.rows and not stack.cards:
            if not waste.cards:
                while self.s.talon.cards:
                    self.s.talon.dealCards()
                    if not self.fillWaste():
                        break
            if waste.cards:
                waste.moveMove(1, stack)


    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Northwest Territory
# * Artic Garden
# ************************************************************************

class NorthwestTerritory(KingAlbert):
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=KING)
    RESERVES = (4, 4, 4, 4)
    ROWS = 8
    def startGame(self):
        Klondike.startGame(self, flip=0, reverse=0)
        self.s.talon.dealRow(rows=self.s.reserves)


class ArticGarden(NorthwestTerritory):
    def startGame(self):
        Klondike.startGame(self, flip=1, reverse=0)
        self.s.talon.dealRow(rows=self.s.reserves)


# ************************************************************************
# * Aunt Mary
# ************************************************************************

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


# ************************************************************************
# * Double Dot
# ************************************************************************

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

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return abs(card1.rank-card2.rank) == 2

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * Seven Devils
# ************************************************************************

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


# ************************************************************************
# * Moving Left
# * Souter
# ************************************************************************

class MovingLeft(Klondike):

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=10, playcards=24)

    def fillStack(self, stack):
        if not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if stack in self.s.rows:
                i = list(self.s.rows).index(stack)
                if i < len(self.s.rows)-1:
                    from_stack = self.s.rows[i+1]
                    pile = from_stack.getPile()
                    if pile:
                        from_stack.moveMove(len(pile), stack)
            self.leaveState(old_state)


class Souter(MovingLeft):
    def createGame(self):
        l = Klondike.createGame(self, max_rounds=2, rows=10,
                                playcards=24, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)


# ************************************************************************
# * Big Forty
# * Ali Baba
# * Cassim
# ************************************************************************

class BigForty(Klondike):
    RowStack_Class = SS_RowStack

    def createGame(self):
        Klondike.createGame(self, rows=10)

    def startGame(self):
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_SS


class AliBaba(BigForty):
    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))
    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        BigForty.startGame(self)


class Cassim(AliBaba):
    def createGame(self):
        Klondike.createGame(self, rows=7)


# ************************************************************************
# * Saratoga
# ************************************************************************

class Saratoga(Klondike):
    def createGame(self):
        Klondike.createGame(self, num_deal=3)
    def startGame(self):
        Klondike.startGame(self, flip=1)


# ************************************************************************
# * Whitehorse
# ************************************************************************

class Whitehorse(Klondike):

    def createGame(self):
        Klondike.createGame(self, num_deal=3)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if stack in self.s.rows:
                if not self.s.waste.cards:
                    self.s.talon.dealCards()
                if self.s.waste.cards:
                    self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)


# ************************************************************************
# * Boost
# ************************************************************************

class Boost(Klondike):
    def createGame(self):
        l = Klondike.createGame(self, rows=4, max_rounds=3, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)


# ************************************************************************
# * Gold Rush
# ************************************************************************

class GoldRush(Klondike):
    Talon_Class = CanfieldRush_Talon
    def createGame(self):
        l = Klondike.createGame(self, max_rounds=3, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)


# ************************************************************************
# * Gold Mine
# ************************************************************************

class GoldMine_RowStack(AC_RowStack):
    getBottomImage = Stack._getReserveBottomImage


class GoldMine(Klondike):
    RowStack_Class = GoldMine_RowStack

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, num_deal=3)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealCards()


# ************************************************************************
# * Lucky Thirteen
# * Lucky Piles
# ************************************************************************

class LuckyThirteen(Game):
    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(RK_RowStack, base_rank=NO_RANK)

    def createGame(self, xoffset=0, playcards=0):
        l, s = Layout(self), self.s
        if xoffset:
            xoffset = l.XOFFSET
        w0 = l.XS+playcards*l.XOFFSET
        self.setSize(l.XM + 5*w0, l.YM+4*l.YS)

        x, y = l.XM, l.YM+l.YS
        for i in range(5):
            stack = self.RowStack_Class(x, y, self, max_move=1)
            s.rows.append(stack)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = 0
            x += w0
        x, y = l.XM+w0, l.YM+2*l.YS
        for i in range(3):
            stack = self.RowStack_Class(x, y, self, max_move=1)
            s.rows.append(stack)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = 0
            x += w0
        x, y = l.XM, l.YM+3*l.YS
        for i in range(5):
            stack = self.RowStack_Class(x, y, self, max_move=1)
            s.rows.append(stack)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = 0
            x += w0
        x, y = (self.width-4*l.XS)/2, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self, max_rounds=1)

        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_RK


class LuckyPiles(LuckyThirteen):
    RowStack_Class = StackWrapper(UD_SS_RowStack, base_rank=KING)

    def createGame(self):
        LuckyThirteen.createGame(self, xoffset=1, playcards=7)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Legion
# ************************************************************************

class Legion(Klondike):

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=8)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        for i in (1,2,3):
            self.s.talon.dealRow(rows=self.s.rows[i:-i], flip=0)
            self.s.talon.dealRow(rows=self.s.rows[i:-i])
        self.s.talon.dealCards()


# ************************************************************************
# * Big Bertha
# ************************************************************************

class BigBertha(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+15*l.XS, l.YM+3*l.YS+15*l.YOFFSET)

        x, y = l.XM, l.YM
        s.talon = InitialDealTalonStack(x, y, self)

        x, y = l.XM+3.5*l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=i%4, max_cards=12))
            x += l.XS

        x, y = l.XM, l.YM+l.YS
        for i in range(15):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS

        x, y = l.XM, self.height-l.YS
        for i in range(14):
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            x += l.XS

        s.foundations.append(RK_FoundationStack(x, y, self, suit=ANY_SUIT,
                             base_rank=KING, dir=0, max_cards=8))

        l.defaultStackGroups()


    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Athena
# ************************************************************************

class Athena(Klondike):

    def startGame(self):
        self.s.talon.dealRow(frames=0, flip=0)
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0, flip=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


# ************************************************************************
# * Kingsley
# ************************************************************************

class Kingsley(Klondike):

    Foundation_Class = StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1)
    RowStack_Class = StackWrapper(KingAC_RowStack, base_rank=ACE, dir=1)

    def createGame(self):
        Klondike.createGame(self, max_rounds=1)


# ************************************************************************
# * Scarp
# ************************************************************************

class Scarp(Klondike):
    Talon_Class = DealRowTalonStack
    RowStack_Class = AC_RowStack

    def createGame(self):
        Klondike.createGame(self, max_rounds=1, rows=13, waste=0, playcards=28)

    def startGame(self):
        Klondike.startGame(self, flip=1)


# ************************************************************************
# * Eight Sages
# ************************************************************************

class EightSages_Row(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack is self.game.s.waste

class EightSages(Klondike):
    RowStack_Class = EightSages_Row

    def createGame(self):
        l = Klondike.createGame(self, max_rounds=2, rows=8,
                                playcards=12, round_text=True)
        l.createRoundText(self.s.talon, 'ne', dx=l.XS)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()



# register the game
registerGame(GameInfo(2, Klondike, "Klondike",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(61, CasinoKlondike, "Casino Klondike",
                      GI.GT_KLONDIKE | GI.GT_SCORE, 1, 2, GI.SL_BALANCED))
registerGame(GameInfo(129, VegasKlondike, "Vegas Klondike",
                      GI.GT_KLONDIKE | GI.GT_SCORE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(18, KlondikeByThrees, "Klondike by Threes",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(58, ThumbAndPouch, "Thumb and Pouch",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(67, Whitehead, "Whitehead",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(39, SmallHarp, "Small Harp",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED,
                      altnames=("Die kleine Harfe",) ))
registerGame(GameInfo(66, Eastcliff, "Eastcliff",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(224, Easthaven, "Easthaven",
                      GI.GT_GYPSY, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(33, Westcliff, "Westcliff",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(225, Westhaven, "Westhaven",
                      GI.GT_GYPSY, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(107, PasSeul, "Pas Seul",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(81, BlindAlleys, "Blind Alleys",
                      GI.GT_KLONDIKE, 1, 1, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(215, Somerset, "Somerset",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(231, Canister, "Canister",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(229, AgnesSorel, "Agnes Sorel",
                      GI.GT_GYPSY, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(4, EightTimesEight, "8 x 8",
                      GI.GT_KLONDIKE, 2, -1, GI.SL_BALANCED))
registerGame(GameInfo(127, AchtmalAcht, "Eight Times Eight",
                      GI.GT_KLONDIKE, 2, 2, GI.SL_BALANCED,
                      altnames=("Achtmal Acht",) ))
registerGame(GameInfo(133, Batsford, "Batsford",
                      GI.GT_KLONDIKE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(221, Stonewall, "Stonewall",
                      GI.GT_RAGLAN, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(222, FlowerGarden, "Flower Garden",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("The Bouquet", "The Garden",) ))
registerGame(GameInfo(233, KingAlbert, "King Albert",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Idiot's Delight",) ))
registerGame(GameInfo(232, Raglan, "Raglan",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(223, Brigade, "Brigade",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(230, Jane, "Jane",
                      GI.GT_RAGLAN, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(236, AgnesBernauer, "Agnes Bernauer",
                      GI.GT_RAGLAN, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(263, Phoenix, "Phoenix",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(283, Jumbo, "Jumbo",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(333, OpenJumbo, "Open Jumbo",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(326, Lanes, "Lanes",
                      GI.GT_KLONDIKE, 1, 1, GI.SL_BALANCED))
registerGame(GameInfo(327, ThirtySix, "Thirty Six",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(350, Q_C_, "Q.C.",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(361, NorthwestTerritory, "Northwest Territory",
                      GI.GT_RAGLAN, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(362, Morehead, "Morehead",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(388, Senate, "Senate",
                      GI.GT_RAGLAN, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(389, SenatePlus, "Senate +",
                      GI.GT_RAGLAN, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(390, Arizona, "Arizona",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(407, AuntMary, "Aunt Mary",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(420, DoubleDot, "Double Dot",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(434, SevenDevils, "Seven Devils",
                      GI.GT_RAGLAN, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(452, DoubleEasthaven, "Double Easthaven",
                      GI.GT_GYPSY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(453, TripleEasthaven, "Triple Easthaven",
                      GI.GT_GYPSY, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(470, MovingLeft, "Moving Left",
                      GI.GT_KLONDIKE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(471, Souter, "Souter",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(473, BigForty, "Big Forty",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(474, AliBaba, "Ali Baba",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(475, Cassim, "Cassim",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(479, Saratoga, "Saratoga",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(491, Whitehorse, "Whitehorse",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(518, Boost, "Boost",
                      GI.GT_KLONDIKE | GI.GT_ORIGINAL, 1, 2, GI.SL_BALANCED))
registerGame(GameInfo(522, ArticGarden, "Artic Garden",
                      GI.GT_RAGLAN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(532, GoldRush, "Gold Rush",
                      GI.GT_KLONDIKE, 1, 2, GI.SL_BALANCED))
registerGame(GameInfo(539, Usk, "Usk",
                      GI.GT_KLONDIKE, 1, 1, GI.SL_BALANCED))
registerGame(GameInfo(541, BatsfordAgain, "Batsford Again",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(572, GoldMine, "Gold Mine",
                      GI.GT_NUMERICA, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(585, LuckyThirteen, "Lucky Thirteen",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(586, LuckyPiles, "Lucky Piles",
                      GI.GT_FAN_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(601, AmericanCanister, "American Canister",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(602, BritishCanister, "British Canister",
                      GI.GT_BELEAGUERED_CASTLE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(607, Legion, "Legion",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(627, QueenVictoria, "Queen Victoria",
                      GI.GT_RAGLAN | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(630, BigBertha, "Big Bertha",
                      GI.GT_RAGLAN | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(633, Athena, "Athena",
                      GI.GT_KLONDIKE, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(634, Chinaman, "Chinaman",
                      GI.GT_KLONDIKE, 1, 1, GI.SL_BALANCED))
registerGame(GameInfo(651, EightByEight, "Eight by Eight",
                      GI.GT_KLONDIKE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(667, Kingsley, "Kingsley",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(669, Scarp, "Scarp",
                      GI.GT_GYPSY | GI.GT_ORIGINAL, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(726, EightSages, "Eight Sages",
                      GI.GT_KLONDIKE, 2, 1, GI.SL_MOSTLY_LUCK))

