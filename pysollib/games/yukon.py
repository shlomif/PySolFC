#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
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
# ---------------------------------------------------------------------------##

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.games.spider import Spider_SS_Foundation
from pysollib.hint import Yukon_Hint
from pysollib.layout import Layout
from pysollib.mfxutil import kwdefault
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
    DealRowTalonStack, \
    InitialDealTalonStack, \
    OpenStack, \
    RedealTalonStack, \
    ReserveStack, \
    SS_FoundationStack, \
    StackWrapper, \
    WasteStack, \
    WasteTalonStack, \
    Yukon_AC_RowStack, \
    Yukon_BO_RowStack, \
    Yukon_SS_RowStack, \
    isAlternateColorSequence
from pysollib.util import ANY_SUIT, KING


# ************************************************************************
# * Yukon
# ************************************************************************

class Yukon(Game):
    Layout_Method = staticmethod(Layout.yukonLayout)
    Talon_Class = InitialDealTalonStack
    Foundation_Class = SS_FoundationStack
    RowStack_Class = StackWrapper(Yukon_AC_RowStack, base_rank=KING)
    Hint_Class = Yukon_Hint

    DIFF_SUITS = True

    def createGame(self, rows=7, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=rows, texts=0, playcards=25)
        self.Layout_Method(l, **layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = self.Talon_Class(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            if self.DIFF_SUITS:
                s.foundations.append(
                    self.Foundation_Class(
                        r.x, r.y, self, suit=r.suit, max_move=0))
            else:
                s.foundations.append(
                    self.Foundation_Class(
                        r.x, r.y, self, suit=ANY_SUIT, max_move=0))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()
        return l

    def startGame(self):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.rows[1:], flip=1, frames=0)
        self._startAndDealRow()

    def getHighlightPilesStacks(self):
        return ()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Russian Solitaire (like Yukon, but build down by suit)
# ************************************************************************

class RussianSolitaire(Yukon):
    RowStack_Class = StackWrapper(Yukon_SS_RowStack, base_rank=KING)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Moosehide (build down in any suit but the same)
# ************************************************************************

class Moosehide(Yukon):
    RowStack_Class = StackWrapper(Yukon_BO_RowStack, base_rank=KING)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit != card2.suit and
                abs(card1.rank-card2.rank) == 1)


# ************************************************************************
# * Odessa (just like Russian Solitaire, only a different initial
# * card layout)
# ************************************************************************

class Odessa(RussianSolitaire):
    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        self._dealNumRows(2)
        for i in range(2):
            self.s.talon.dealRow(rows=self.s.rows[1:6], frames=0)
        self._startAndDealRow()


# ************************************************************************
# * Grandfather
# ************************************************************************

class Grandfather_Talon(RedealTalonStack):
    def dealCards(self, sound=False):
        self.redealCards(sound=sound, shuffle=True)


class Grandfather(RussianSolitaire):
    Talon_Class = StackWrapper(Grandfather_Talon, max_rounds=3)

    def createGame(self):
        layout = Yukon.createGame(self)
        layout.createRoundText(self.s.talon, 'nn')

    def startGame(self):
        frames = 0
        sound = False
        for i,  j in ((1, 7), (1, 6), (2, 6), (2, 5), (3, 5), (3, 4)):
            if len(self.s.talon.cards) <= j-i:
                frames = -1
                sound = True
                self.startDealSample()
            self.s.talon.dealRowAvail(rows=self.s.rows[i:j],
                                      flip=0, frames=frames)
        if not sound:
            self.startDealSample()
        self.s.talon.dealRowAvail()
        for i in range(4):
            self.s.talon.dealRowAvail(rows=self.s.rows[1:])

    redealCards = startGame


# ************************************************************************
# * Alaska (like Russian Solitaire, but build up or down in suit)
# ************************************************************************

class Alaska_RowStack(Yukon_SS_RowStack):
    def _isYukonSequence(self, c1, c2):
        return (c1.suit == c2.suit and
                ((c1.rank + self.cap.dir) % self.cap.mod == c2.rank or
                 (c2.rank + self.cap.dir) % self.cap.mod == c1.rank))

    def getHelp(self):
        return _('Tableau. Build up or down by suit, can move any face-up '
                 'cards regardless of sequence.')


class Alaska(RussianSolitaire):
    RowStack_Class = StackWrapper(Alaska_RowStack, base_rank=KING)


# ************************************************************************
# * Roslin (like Yukon, but build up or down by alternate color)
# ************************************************************************

class Roslin_RowStack(Yukon_AC_RowStack):
    def _isYukonSequence(self, c1, c2):
        return (c1.color != c2.color and
                ((c1.rank + self.cap.dir) % self.cap.mod == c2.rank or
                 (c2.rank + self.cap.dir) % self.cap.mod == c1.rank))

    def getHelp(self):
        return _('Tableau. Build up or down by alternate color, can move '
                 'any face-up cards regardless of sequence.')


class Roslin(Yukon):
    RowStack_Class = StackWrapper(Roslin_RowStack, base_rank=KING)


# ************************************************************************
# * Chinese Discipline
# * Chinese Solitaire
# ************************************************************************

class ChineseDiscipline(Yukon):
    Layout_Method = staticmethod(Layout.klondikeLayout)
    Talon_Class = DealRowTalonStack

    def createGame(self):
        return Yukon.createGame(self, waste=0, texts=1)

    def startGame(self):
        for i in (3, 3, 3, 4, 5, 6):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=1, frames=0)
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self._startAndDealRow()


class ChineseSolitaire(ChineseDiscipline):
    RowStack_Class = Yukon_AC_RowStack      # anything on an empty space


# ************************************************************************
# * Queenie
# ************************************************************************

class Queenie(Yukon):
    Layout_Method = staticmethod(Layout.klondikeLayout)
    Talon_Class = DealRowTalonStack

    def createGame(self):
        return Yukon.createGame(self, waste=0, texts=1)

    def startGame(self, flip=1, reverse=1):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(
                rows=self.s.rows[i:], flip=flip, frames=0, reverse=reverse)
        self.startDealSample()
        self.s.talon.dealRow(reverse=reverse)


# ************************************************************************
# * Rushdike (like Queenie, but built down by suit)
# ************************************************************************

class Rushdike(RussianSolitaire):
    Layout_Method = staticmethod(Layout.klondikeLayout)
    Talon_Class = DealRowTalonStack

    def createGame(self):
        return RussianSolitaire.createGame(self, waste=0, texts=1)

    def startGame(self, flip=0, reverse=1):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(
                rows=self.s.rows[i:], flip=flip, frames=0, reverse=reverse)
        self.startDealSample()
        self.s.talon.dealRow(reverse=reverse)


# ************************************************************************
# * Russian Point (Rushdike in a different layout)
# ************************************************************************

class RussianPoint(Rushdike):
    def startGame(self):
        r = self.s.rows
        for i in (1, 1, 2, 2, 3, 3):
            self.s.talon.dealRow(rows=r[i:len(r)-i], flip=0, frames=0)
        self._startAndDealRow()


# ************************************************************************
# * Abacus
# ************************************************************************

class Abacus_Foundation(SS_FoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, base_rank=suit, mod=13, dir=suit+1, max_move=0)
        SS_FoundationStack.__init__(self, x, y, game, suit, **cap)


class Abacus_RowStack(Yukon_SS_RowStack):
    def _isYukonSequence(self, c1, c2):
        dir, mod = -(c1.suit + 1), 13
        return c1.suit == c2.suit and (c1.rank + dir) % mod == c2.rank


class Abacus(Rushdike):
    Foundation_Class = Abacus_Foundation
    RowStack_Class = Abacus_RowStack

    def createGame(self):
        layout = Rushdike.createGame(self)
        help = (_('''\
Club:    A 2 3 4 5 6 7 8 9 T J Q K
Spade:   2 4 6 8 T Q A 3 5 7 9 J K
Heart:   3 6 9 Q 2 5 8 J A 4 7 T K
Diamond: 4 8 Q 3 7 J 2 6 T A 5 9 K'''))
        self.texts.help = MfxCanvasText(self.canvas,
                                        layout.XM, self.height - layout.YM,
                                        text=help,
                                        anchor="sw",
                                        font=self.app.getFont("canvas_fixed"))

    def _shuffleHook(self, cards):
        # move Twos to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(
            cards, lambda c: (c.id in (0, 14, 28, 42), c.suit))

    def startGame(self, flip=1, reverse=1):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(
                rows=self.s.rows[i:], flip=flip, frames=0, reverse=reverse)
        self.startDealSample()
        self.s.talon.dealRow(reverse=reverse)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        dir, mod = -(card1.suit + 1), 13
        return (card1.suit == card2.suit and
                ((card1.rank + dir) % mod == card2.rank or
                 (card2.rank + dir) % mod == card1.rank))


# ************************************************************************
# * Double Yukon
# * Double Russian Solitaire
# ************************************************************************

class DoubleYukon(Yukon):
    def createGame(self):
        Yukon.createGame(self, rows=10)

    def startGame(self):
        for i in range(1, len(self.s.rows)-1):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        # self.s.talon.dealRow(rows=self.s.rows, flip=0, frames=0)
        for i in range(5):
            self.s.talon.dealRow(flip=1, frames=0)
        self._startAndDealRow()


class DoubleRussianSolitaire(DoubleYukon):
    RowStack_Class = StackWrapper(Yukon_SS_RowStack, base_rank=KING)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Triple Yukon
# * Triple Russian Solitaire
# ************************************************************************

class TripleYukon(Yukon):
    def createGame(self):
        Yukon.createGame(self, rows=13, playcards=34)

    def startGame(self):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        for i in range(5):
            self.s.talon.dealRow(rows=self.s.rows, flip=1, frames=0)
        self._startAndDealRow()


class TripleRussianSolitaire(TripleYukon):
    RowStack_Class = StackWrapper(Yukon_SS_RowStack, base_rank=KING)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Quadruple Yukon
# ************************************************************************

class QuadrupleYukon(Yukon):
    def createGame(self):
        Yukon.createGame(self, rows=16, playcards=34)

    def startGame(self):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self.s.talon.dealRow(rows=self.s.rows[1:13], flip=1, frames=0)
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.rows[1:], flip=1, frames=0)
        self._startAndDealRow()


# ************************************************************************
# * Ten Across
# ************************************************************************

class TenAcross(Yukon):

    Foundation_Class = Spider_SS_Foundation
    RowStack_Class = StackWrapper(Yukon_SS_RowStack, base_rank=KING)
    Layout_Method = staticmethod(Layout.freeCellLayout)

    #
    # game layout
    #

    def createGame(self, **layout):
        # create layout
        lay, s = Layout(self), self.s
        kwdefault(layout, rows=10, reserves=2, texts=0)
        self.Layout_Method(lay, **layout)
        self.setSize(lay.size[0], lay.size[1])
        # create stacks
        s.talon = InitialDealTalonStack(lay.s.talon.x, lay.s.talon.y, self)
        for r in lay.s.foundations:
            self.s.foundations.append(
                self.Foundation_Class(r.x, r.y, self, suit=r.suit))
        for r in lay.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        for r in lay.s.reserves:
            self.s.reserves.append(ReserveStack(r.x, r.y, self))
        # default
        lay.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        n = 1
        for i in range(4):
            self.s.talon.dealRow(rows=self.s.rows[:n], frames=0)
            self.s.talon.dealRow(rows=self.s.rows[n:-n], frames=0, flip=0)
            self.s.talon.dealRow(rows=self.s.rows[-n:], frames=0)
            n += 1
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Panopticon
# ************************************************************************

class Panopticon(TenAcross):

    Foundation_Class = SS_FoundationStack

    def createGame(self):
        TenAcross.createGame(self, rows=8, reserves=4)

    def startGame(self):
        self.s.talon.dealRow(frames=0, flip=0)
        n = 1
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.rows[:n], frames=0)
            self.s.talon.dealRow(rows=self.s.rows[n:-n], frames=0, flip=0)
            self.s.talon.dealRow(rows=self.s.rows[-n:], frames=0)
            n += 1
        self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.reserves)


# ************************************************************************
# * Australian Patience
# * Tasmanian Patience
# * Canberra
# * Raw Prawn
# * Bim Bom
# ************************************************************************

class AustralianPatience(RussianSolitaire):

    RowStack_Class = StackWrapper(Yukon_SS_RowStack, base_rank=KING)

    def createGame(self, rows=7, max_rounds=1, num_deal=1):
        l, s = Layout(self), self.s
        Layout.klondikeLayout(l, rows=rows, waste=1)
        self.setSize(l.size[0], l.size[1])
        s.talon = WasteTalonStack(l.s.talon.x, l.s.talon.y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for r in l.s.foundations:
            s.foundations.append(
                SS_FoundationStack(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        l.defaultAll()

    def startGame(self):
        self._startDealNumRowsAndDealRowAndCards(3)


class TasmanianPatience(AustralianPatience):
    def createGame(self):
        AustralianPatience.createGame(self, max_rounds=-1, num_deal=3)


class Canberra(AustralianPatience):
    def createGame(self):
        AustralianPatience.createGame(self, max_rounds=2)


class RawPrawn(AustralianPatience):
    RowStack_Class = Yukon_SS_RowStack


class BimBom(AustralianPatience):
    RowStack_Class = Yukon_SS_RowStack

    def createGame(self):
        AustralianPatience.createGame(self, rows=8)

    def startGame(self):
        self._startDealNumRowsAndDealRowAndCards(4)


# ************************************************************************
# * Geoffrey
# ************************************************************************

class Geoffrey(Yukon):
    Layout_Method = staticmethod(Layout.klondikeLayout)
    RowStack_Class = StackWrapper(Yukon_SS_RowStack, base_rank=KING)

    def createGame(self):
        Yukon.createGame(self, rows=8, waste=0)

    def startGame(self):
        for i in (4, 4, 4, 4, 8):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=1, frames=0)
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.rows[:4])

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Queensland
# ************************************************************************

class Queensland(Yukon):
    Layout_Method = staticmethod(Layout.klondikeLayout)
    RowStack_Class = Yukon_SS_RowStack

    def createGame(self):
        Yukon.createGame(self, waste=0)

    def startGame(self):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self._startDealNumRows(3)
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Russian Spider
# * Double Russian Spider
# ************************************************************************

class RussianSpider_RowStack(Yukon_SS_RowStack):  # Spider_SS_RowStack
    def canDropCards(self, stacks):
        if len(self.cards) < 13:
            return (None, 0)
        cards = self.cards[-13:]
        for s in stacks:
            if s is not self and s.acceptsCards(self, cards):
                return (s, 13)
        return (None, 0)


class RussianSpider(RussianSolitaire):
    RowStack_Class = StackWrapper(RussianSpider_RowStack, base_rank=KING)
    Foundation_Class = Spider_SS_Foundation

    DIFF_SUITS = False


class DoubleRussianSpider(RussianSpider, DoubleRussianSolitaire):
    def createGame(self):
        Yukon.createGame(self, rows=10)

    def startGame(self):
        DoubleRussianSolitaire.startGame(self)


# ************************************************************************
# * Kiev
# * Dnieper
# * Sevastopol
# ************************************************************************

class Kiev(RussianSpider):
    RowStack_Class = RussianSpider_RowStack
    Layout_Method = staticmethod(Layout.klondikeLayout)
    Talon_Class = DealRowTalonStack

    def createGame(self):
        return Yukon.createGame(self, waste=0, texts=1)

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        self._startAndDealRow()


class Dnieper(Kiev):
    RowStack_Class = StackWrapper(RussianSpider_RowStack, mod=13)


class Sevastopol(Kiev):

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(flip=0, frames=0)
        r = self.s.rows
        rows = (r[1], r[3], r[5])
        self.s.talon.dealRow(rows=rows, flip=0, frames=0)
        self._startAndDealRow()


# ************************************************************************
# * Brisbane
# ************************************************************************

class Brisbane_RowStack(Yukon_AC_RowStack):
    def _isYukonSequence(self, c1, c2):
        return (c1.rank + self.cap.dir) % self.cap.mod == c2.rank

    def getHelp(self):
        return _('Tableau. Build down regardless of suit, can move any '
                 'face-up cards regardless of sequence.')


class Brisbane(Yukon):
    RowStack_Class = Brisbane_RowStack

    def startGame(self):
        for i in range(1, len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self._startDealNumRows(3)
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    def getHighlightPilesStacks(self):
        return ()

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Hawaiian
# ************************************************************************

class Hawaiian(Game):
    Hint_Class = Yukon_Hint

    def createGame(self, rows=10, playcards=20):
        l, s = Layout(self), self.s
        self.setSize(l.XM+max(rows, 8)*l.XS,
                     l.YM+2*l.YS+playcards*l.YOFFSET)
        x, y = l.XM, l.YM
        stack = OpenStack(x, y, self, max_move=1, max_accept=0)
        s.reserves.append(stack)
        l.createText(stack, 'ne')
        x, y = self.width-8*l.XS, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i//2))
            x += l.XS
        x, y = self.width-rows*l.XS, l.YM+l.YS
        for i in range(rows):
            s.rows.append(Yukon_AC_RowStack(x, y, self))
            x += l.XS
        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        l.defaultStackGroups()

    def startGame(self):
        for i in range(104-5*10):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self._startDealNumRowsAndDealSingleRow(4)

    def getHighlightPilesStacks(self):
        return ()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Wave
# ************************************************************************

class WaveTalon(DealRowTalonStack):
    def dealCards(self, sound=False):
        if sound and self.game.app.opt.animations:
            self.game.startDealSample()
        n = self.dealRowAvail(flip=0, sound=False)
        n += self.dealRowAvail(sound=False)
        if sound:
            self.game.stopSamples()
        return n


class Wave(Game):
    Hint_Class = Yukon_Hint

    def createGame(self, rows=8):
        l, s = Layout(self), self.s
        l.klondikeLayout(rows=rows, waste=0, playcards=25)
        self.setSize(l.size[0], l.size[1])
        s.talon = WaveTalon(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(SS_FoundationStack(r.x, r.y, self,
                                                    suit=r.suit))
        for r in l.s.rows:
            s.rows.append(Yukon_AC_RowStack(r.x, r.y, self))
        l.defaultAll()

    def startGame(self):
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0, flip=0)
        self._startAndDealRow()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Yukon Kings
# ************************************************************************

class YukonKings(Yukon):

    def createGame(self, playcards=25):
        l, s = Layout(self), self.s
        self.setSize(l.XM + (7 * l.XS),
                     l.YM + l.YS + playcards * l.YOFFSET)

        x, y = l.XM, l.YM
        for i in range(7):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS

        x, y = l.XM, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        l.defaultStackGroups()

    def isGameWon(self):
        cardsPlayed = False
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isAlternateColorSequence(s.cards):
                    return False
                cardsPlayed = True
        if not cardsPlayed:
            return False
        return True


# ************************************************************************
# * Yukon Cells
# * Russian Cell
# * Yukonic Plague
# ************************************************************************

class YukonCells(Yukon):
    Reserve_Stack = ReserveStack

    RESERVES = 2
    RESERVE_TEXT = False

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        ROWS = 7

        # set size so that at least 2//3 of a card is visible with 20 cards
        h = l.CH * 2 // 27 * l.YOFFSET
        h = l.YM + max(h, 5 * l.YS)

        # create rows
        x, y = l.XM, l.YM

        w1, w2 = (7 * (l.XS + l.XM)), (2 * l.XS)
        if w2 + 13 * l.XOFFSET > w1:
            l.XOFFSET = int((w1 - w2) / 13)

        x2 = x * 3
        for i in range(self.RESERVES):
            reserve = self.Reserve_Stack(x2, y, self)
            reserve.CARD_XOFFSET = l.XOFFSET
            if self.RESERVE_TEXT:
                l.createText(reserve, "sw")
            s.reserves.append(reserve)
            x2 += l.XS

        y += l.YS
        for i in range(ROWS):
            self.s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS

        # Don't know why this is necessary for the Yukon layout.
        # But we should probably figure out how to get this to work
        # like other games.
        self.setRegion(self.s.rows + self.s.reserves,
                       (-999, -999, x - l.CW // 2, 999999))

        # create foundations
        y = l.YM
        for suit in range(4):
            self.s.foundations.append(self.Foundation_Class(
                x, y, self, suit=suit, max_move=0))
            y += l.YS

        x, y = l.XM, h - l.YS
        self.s.talon = self.Talon_Class(x, y, self)

        # set window
        self.setSize(l.XM + 8 * l.XS, h)
        l.defaultAll()


class RussianCell(YukonCells):
    RowStack_Class = StackWrapper(Yukon_SS_RowStack, base_rank=KING)

    shallHighlightMatch = Game._shallHighlightMatch_SS


class YukonicPlague(YukonCells):
    Reserve_Stack = OpenStack

    RESERVES = 1
    RESERVE_TEXT = True

    def startGame(self):
        for i in range(13):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(2):
            self.s.talon.dealRow(rows=self.s.rows[1:7], flip=0, frames=0)
        for i in range(5):
            self.s.talon.dealRow(rows=self.s.rows[i + 1:7], flip=1, frames=0)
        self._startAndDealRow()


# register the game
registerGame(GameInfo(19, Yukon, "Yukon",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(20, RussianSolitaire, "Russian Solitaire",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(27, Odessa, "Odessa",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(278, Grandfather, "Tvete's Grandfather",
                      GI.GT_YUKON, 1, 2, GI.SL_BALANCED))
registerGame(GameInfo(186, Alaska, "Alaska",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(187, ChineseDiscipline, "Chinese Discipline",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(188, ChineseSolitaire, "Chinese Solitaire",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(189, Queenie, "Queenie",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(190, Rushdike, "Rushdike",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(191, RussianPoint, "Russian Point",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(192, Abacus, "Abacus",
                      GI.GT_YUKON | GI.GT_XORIGINAL, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(271, DoubleYukon, "Double Yukon",
                      GI.GT_YUKON, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(272, TripleYukon, "Triple Yukon",
                      GI.GT_YUKON, 3, 0, GI.SL_BALANCED))
registerGame(GameInfo(284, TenAcross, "Ten Across",
                      GI.GT_YUKON, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(285, Panopticon, "Panopticon",
                      GI.GT_YUKON | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(339, Moosehide, "Moosehide",
                      GI.GT_YUKON, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(387, Roslin, "Roslin",
                      GI.GT_YUKON, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Roslyn",)))
registerGame(GameInfo(447, AustralianPatience, "Australian Patience",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED,
                      altnames=('Outback Patience',)))
registerGame(GameInfo(450, RawPrawn, "Raw Prawn",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(456, BimBom, "Bim Bom",
                      GI.GT_YUKON | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(466, DoubleRussianSolitaire, "Double Russian Solitaire",
                      GI.GT_YUKON, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(488, TripleRussianSolitaire, "Triple Russian Solitaire",
                      GI.GT_YUKON, 3, 0, GI.SL_BALANCED))
registerGame(GameInfo(492, Geoffrey, "Geoffrey",
                      GI.GT_YUKON, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(525, Queensland, "Queensland",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(530, RussianSpider, "Russian Spider",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED,
                      altnames=('Ukrainian Solitaire',)))
registerGame(GameInfo(531, DoubleRussianSpider, "Double Russian Spider",
                      GI.GT_SPIDER | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(603, Brisbane, "Brisbane",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(707, Hawaiian, "Hawaiian",
                      GI.GT_YUKON | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(732, Wave, "Wave",
                      GI.GT_YUKON | GI.GT_ORIGINAL, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(826, YukonicPlague, "Yukonic Plague",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(857, TasmanianPatience, "Tasmanian Patience",
                      GI.GT_YUKON, 1, -1, GI.SL_BALANCED))
registerGame(GameInfo(897, Kiev, "Kiev",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED,
                      altnames=('Kyiv',)))
registerGame(GameInfo(914, Canberra, "Canberra",
                      GI.GT_YUKON, 1, 1, GI.SL_BALANCED))
registerGame(GameInfo(919, Dnieper, "Dnieper",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED,
                      altnames=('Dnipro',)))
registerGame(GameInfo(925, YukonCells, "Yukon Cells",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(936, YukonKings, "Yukon Kings",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(942, QuadrupleYukon, "Quadruple Yukon",
                      GI.GT_YUKON, 4, 0, GI.SL_BALANCED))
registerGame(GameInfo(963, Sevastopol, "Sevastopol",
                      GI.GT_SPIDER, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(964, RussianCell, "Russian Cell",
                      GI.GT_YUKON, 1, 0, GI.SL_BALANCED))
