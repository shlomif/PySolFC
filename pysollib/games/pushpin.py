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
from pysollib.hint import AbstractHint
from pysollib.layout import Layout
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        AbstractFoundationStack, \
        DealRowTalonStack, \
        ReserveStack, \
        Stack
from pysollib.util import ANY_RANK, ANY_SUIT, RANKS, SUITS_PL


class PushPin_Hint(AbstractHint):

    def computeHints(self):
        game = self.game
        rows = game.s.rows
        for i in range(len(rows)-3):
            r = rows[i+1]
            if not rows[i+2].cards:
                break
            if r._checkPair(i, i+2):
                self.addHint(5000, 1, r, game.s.foundations[0])
            if not rows[i+3].cards:
                break
            if r._checkPair(i, i+3):
                self.addHint(5000, 1, r, rows[i+2])


class PushPin_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        return True


class PushPin_Talon(DealRowTalonStack):
    def dealCards(self, sound=False):
        for r in self.game.s.rows:
            if not r.cards:
                return self.dealRowAvail(rows=[r], sound=sound)
        return self.dealRowAvail(rows=[self.game.s.rows[0]], sound=sound)
    getBottomImage = Stack._getNoneBottomImage


class PushPin_RowStack(ReserveStack):

    def _checkPair(self, ps, ns):
        if ps < 0 or ns > 51:
            return False
        rows = self.game.allstacks
        pc, nc = rows[ps].cards, rows[ns].cards
        if pc and nc:
            if pc[0].suit == nc[0].suit or pc[0].rank == nc[0].rank:
                return True
        return False

    def clickHandler(self, event):
        ps, ns = self.id - 1, self.id + 1
        if self._checkPair(ps, ns):
            if not self.game.demo:
                self.game.playSample("autodrop", priority=20)
            self.playMoveMove(1, self.game.s.foundations[0], sound=False)
            return True
        return False

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return False
        if abs(self.id - from_stack.id) != 1:
            return False
        ps = min(self.id, from_stack.id)-1
        ns = ps + 3
        return self._checkPair(ps, ns)

    def fillStack(self):
        self.game.fillEmptyStacks()

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if to_stack is not self.game.s.foundations[0]:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            ReserveStack.moveMove(
                self, ncards, to_stack, frames=frames, shadow=shadow)

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2 | 16)            # for undo
        if not game.demo:
            game.playSample("droppair", priority=200)
        game.moveMove(n, self, f, frames=frames, shadow=shadow)
        game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.fillStack()
        game.updateStackMove(game.s.talon, 1 | 16)            # for redo
        game.leaveState(old_state)

    getBottomImage = Stack._getBlankBottomImage


class PushPin(Game):

    Hint_Class = PushPin_Hint
    RowStack_Class = PushPin_RowStack

    Comment = False

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        pad = 1
        if self.Comment:
            pad = 5

        # set window
        xx, yy = 9, 6
        w, h = l.XM + xx * l.XS, (l.YM * pad) + yy * l.YS
        self.setSize(w, h)

        # create stacks
        for i in range(yy):
            for j in range(xx):
                n = j+xx*i
                if n < 1:
                    continue
                if n > 52:
                    break
                k = j
                if i % 2:
                    k = xx-j-1
                x, y = l.XM + k*l.XS, (l.YM * pad) + i * l.YS
                s.rows.append(self.RowStack_Class(x, y, self))
        s.talon = PushPin_Talon(l.XM, l.YM * pad, self)
        if self.Comment:
            self.texts.base_rank = \
                MfxCanvasText(self.canvas, l.XM, l.YM, anchor="nw",
                              font=self.app.getFont("canvas_default"))
        s.foundations.append(PushPin_Foundation(l.XM, h-l.YS, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_accept=0, max_move=0, max_cards=52))

        # define stack-groups
        l.defaultStackGroups()
        return l

    def startGame(self):
        self.startDealSample()
        if self.app.opt.accordion_deal_all:
            self.s.talon.dealRow(rows=self.s.rows[:47], frames=0)
            self.s.talon.dealRow(rows=self.s.rows[47:52])
        else:
            self.s.talon.dealRow(rows=self.s.rows[:3])

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 50

    def _fillOne(self):
        rows = self.s.rows
        i = 0
        for r in rows:
            if not r.cards:
                break
            i += 1
        j = i
        for r in rows[i:]:
            if r.cards:
                break
            j += 1
        else:
            return 0
        self.moveMove(1, rows[j], rows[i], frames=2, shadow=0)
        return 1

    def fillEmptyStacks(self):
        if not self.demo:
            self.startDealSample()
        old_state = self.enterState(self.S_FILL)
        while True:
            if not self._fillOne():
                break
        self.leaveState(old_state)
        if not self.demo:
            self.stopSamples()

    def getAutoStacks(self, event=None):
        return ((), (), ())


class RoyalMarriage(PushPin):
    def _shuffleHook(self, cards):
        qi, ki = -1, -1
        for i, c in enumerate(cards):
            if c.suit == 2 and c.rank == 11:
                qi = i
            if c.suit == 2 and c.rank == 12:
                ki = i
            if qi >= 0 and ki >= 0:
                break
        q, k = cards[qi], cards[ki]
        del cards[max(qi, ki)]
        del cards[min(qi, ki)]
        cards.insert(0, k)
        cards.append(q)
        return cards


# ************************************************************************
# * Bayan (ex. Accordion)
# ************************************************************************

class Accordion_Hint(AbstractHint):
    VAL1 = 1
    VAL2 = 3

    def computeHints(self):
        game = self.game
        rows = game.s.rows
        for i in range(len(rows)-3):
            r1, r2 = rows[i], rows[i + self.VAL1]
            if r1.cards and r2.cards:
                c1, c2 = r1.cards[0], r2.cards[0]
                if c1.rank == c2.rank or c1.suit == c2.suit:
                    if r2.acceptsCards(r1, [c1]):
                        self.addHint(5000, 1, r1, r2)
                    if r1.acceptsCards(r2, [c2]):
                        self.addHint(5000, 1, r2, r1)
            r1, r2 = rows[i], rows[i + self.VAL2]
            if r1.cards and r2.cards:
                c1, c2 = r1.cards[0], r2.cards[0]
                if c1.rank == c2.rank or c1.suit == c2.suit:
                    if r2.acceptsCards(r1, [c1]):
                        self.addHint(6000, 1, r1, r2)
                    if r1.acceptsCards(r2, [c2]):
                        self.addHint(6000, 1, r2, r1)


class Accordion_RowStack(PushPin_RowStack):
    ALLOWED_JUMPS = (1, 3)

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return False
        if abs(self.id - from_stack.id) not in self.ALLOWED_JUMPS:
            return False
        c1, c2 = self.cards[-1], cards[0]
        if c1.rank == c2.rank:
            return True
        return c1.suit == c2.suit

    clickHandler = ReserveStack.clickHandler


class Accordion(PushPin):
    Hint_Class = Accordion_Hint
    RowStack_Class = Accordion_RowStack

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 52

# ************************************************************************
# * Accordion (fixed)
# ************************************************************************


class Accordion2_RowStack(Accordion_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not Accordion_RowStack.acceptsCards(self, from_stack, cards):
            return False
        # accepts only from right stack
        return self.id < from_stack.id

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2 | 16)            # for undo

        game.moveMove(ncards, to_stack, f, frames=frames, shadow=shadow)
        game.moveMove(ncards, self, to_stack, frames=frames, shadow=shadow)
        self.fillStack()

        game.updateStackMove(game.s.talon, 1 | 16)            # for redo
        game.leaveState(old_state)


class Accordion2(Accordion):
    RowStack_Class = Accordion2_RowStack

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 51

# ************************************************************************
# * Relaxed Accordion
# ************************************************************************


class RelaxedAccordion_RowStack(Accordion2_RowStack):
    acceptsCards = Accordion_RowStack.acceptsCards


class RelaxedAccordion(Accordion2):
    RowStack_Class = RelaxedAccordion_RowStack

# ************************************************************************
# * 23 Skidoo
# ************************************************************************


class TwoThreeSkidoo_Hint(Accordion_Hint):
    VAL1 = 2
    VAL2 = 3


class TwoThreeSkidoo_RowStack(Accordion2_RowStack):
    ALLOWED_JUMPS = (2, 3)


class TwoThreeSkidoo(Accordion2):
    RowStack_Class = TwoThreeSkidoo_RowStack
    Hint_Class = TwoThreeSkidoo_Hint

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 50

# ************************************************************************
# * Accordion's Revenge
# ************************************************************************


class AccordionsRevenge(Accordion2):
    Comment = True

    def createGame(self):
        self.finalrank = -1
        self.finalsuit = -1

        Accordion2.createGame(self)

    def startGame(self):
        self.finalrank = -1
        self.finalsuit = -1
        self.updateText()

        Accordion2.startGame(self)

        while (self.finalrank == -1 or self.finalsuit == -1 or
               (self.finalrank == self.s.rows[0].cards[0].rank and
                self.finalsuit == self.s.rows[0].cards[0].suit) or
               (self.finalrank == self.s.rows[1].cards[0].rank and
                self.finalsuit == self.s.rows[1].cards[0].suit)):
            self.finalsuit = self.random.choice(self.gameinfo.suits)
            self.finalrank = self.random.choice(self.gameinfo.ranks)

    def isGameWon(self):
        return (len(self.s.foundations[0].cards) == 51 and
                self.s.rows[0].cards[0].rank == self.finalrank and
                self.s.rows[0].cards[0].suit == self.finalsuit)

    def _restoreGameHook(self, game):
        self.finalrank = game.loadinfo.dval.get('Rank')
        self.finalsuit = game.loadinfo.dval.get('Suit')

    def _loadGameHook(self, p):
        self.loadinfo.addattr(dval=p.load())

    def _saveGameHook(self, p):
        dval = {'Rank': self.finalrank, 'Suit': self.finalsuit}
        p.dump(dval)

    def updateText(self):
        if self.preview > 1:
            return
        if self.finalrank != -1 and self.finalsuit != -1:
            self.texts.base_rank.config(text=self.parseGameInfo())

    def parseGameInfo(self):
        return _("Goal card: ") + RANKS[self.finalrank] + \
            ' - ' + SUITS_PL[self.finalsuit]

# ************************************************************************
# * Decade
# ************************************************************************


# Hint should reveal a valid move, but some intelligence should be added.
class Decade_Hint(AbstractHint):

    def computeHints(self):
        game = self.game
        rows = game.s.rows
        for i, row_i in enumerate(rows):
            for j in range(i + 1, len(rows)):
                total = 0
                count = 0
                for k in range(i, j):
                    if self.game.s.rows[k].cards:
                        total += min(self.game.s.rows[k].cards[0].rank + 1, 10)
                        count += 1
                if total in [10, 20, 30] and count > 1:
                    self.addHint(5000, 1, row_i, rows[j - 1])


class Decade_RowStack(PushPin_RowStack):

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return False
        firstcard = min(self.id, from_stack.id)
        lastcard = max(self.id, from_stack.id) + 1

        total = 0
        for x in range(firstcard, lastcard):
            total += min(self.game.s.rows[x].cards[0].rank + 1, 10)

        return total in [10, 20, 30]

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2 | 16)  # for undo
        if not game.demo:
            game.playSample("droppair", priority=200)

        firstcard = min(self.id, other_stack.id)
        lastcard = max(self.id, other_stack.id) + 1

        for x in range(firstcard, lastcard):
            game.moveMove(n, self.game.s.rows[x], f,
                          frames=frames, shadow=shadow)

        self.fillStack()
        game.updateStackMove(game.s.talon, 1 | 16)  # for redo
        game.leaveState(old_state)

    clickHandler = ReserveStack.clickHandler


class Decade(PushPin):
    Hint_Class = Decade_Hint
    RowStack_Class = Decade_RowStack

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 52


# ************************************************************************
# * Seven Up
# ************************************************************************


# Hint should reveal a valid move, but some intelligence should be added.
class SevenUp_Hint(AbstractHint):

    def computeHints(self):
        rows = self.game.s.rows
        for i, row in enumerate(rows):
            if row.cards and row.cards[0].rank == 6:
                self.addHint(5000, 1, row, self.game.s.foundations[0])
            for j in range(i + 1, len(rows)):
                cards_in_between = [
                    rows[k].cards[0].rank + 1
                    for k in range(i, j)
                    if rows[k].cards
                ]
                count = len(cards_in_between)
                total = sum(cards_in_between)
                if total % 7 == 0 and 1 < count <= 4:
                    self.addHint(5000, 1, row, rows[j - 1])


class SevenUp_RowStack(Decade_RowStack):

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return False
        firstcard = min(self.id, from_stack.id)
        lastcard = max(self.id, from_stack.id) + 1

        total = 0
        numcards = 0
        for x in range(firstcard, lastcard):
            total += self.game.s.rows[x].cards[0].rank + 1
            numcards += 1

        return numcards <= 4 and total % 7 == 0

    def _dropSevenClickHandler(self, event):
        if not self.cards:
            return 0
        c = self.cards[-1]
        if c.face_up and c.rank == 6:
            self.game.playSample("autodrop", priority=20)
            self.playMoveMove(1, self.game.s.foundations[0], sound=False)
            return 1
        return 0

    def clickHandler(self, event):
        if self._dropSevenClickHandler(event):
            return 1
        return Decade_RowStack.clickHandler(self, event)


class SevenUp(Decade):
    Hint_Class = SevenUp_Hint
    RowStack_Class = SevenUp_RowStack


registerGame(GameInfo(287, PushPin, "Push Pin",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK,
                      altnames=('Queens')))
registerGame(GameInfo(288, RoyalMarriage, "Royal Marriage",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK,
                      altnames=('Betrothal', 'Coquette')))
registerGame(GameInfo(656, Accordion, "Bayan",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(772, Accordion2, "Accordion",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_SKILL,
                      altnames=('Idle Year', 'Methuselah', 'Tower of Babel',
                                'One Away Three Away', 'One-Handed')))
registerGame(GameInfo(773, RelaxedAccordion, "Relaxed Accordion",
                      GI.GT_1DECK_TYPE | GI.GT_RELAXED, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(811, AccordionsRevenge, "Accordion's Revenge",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(816, Decade, "Decade",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_SKILL,
                      altnames=('Ten Twenty Thirty')))
registerGame(GameInfo(883, TwoThreeSkidoo, "23 Skidoo",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_SKILL))
registerGame(GameInfo(918, SevenUp, "Seven Up",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_SKILL,
                      altnames=('Seventh Wonder', 'The Magic Seven')))
