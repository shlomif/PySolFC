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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import DefaultHint, FreeCellType_Hint, CautiousDefaultHint
from pysollib.hint import FreeCellSolverWrapper
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# *
# ************************************************************************

class DerKatzenschwanz_Hint(FreeCellType_Hint):
    def _getMovePileScore(self, score, color, r, t, pile, rpile):
        if len(rpile) == 0:
            # don't create empty row
            return -1, color
        return FreeCellType_Hint._getMovePileScore(self, score, color, r, t, pile, rpile)


# ************************************************************************
# *
# ************************************************************************

class DerKatzenschwanz(Game):
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=NO_RANK)
    Hint_Class = DerKatzenschwanz_Hint
    Solver_Class = FreeCellSolverWrapper(esf='none', sm='unlimited')

    #
    # game layout
    #

    def createGame(self, rows=9, reserves=8):
        # create layout
        l, s = Layout(self), self.s

        # set size
        maxrows = max(rows, reserves)
        self.setSize(l.XM + (maxrows+2)*l.XS, l.YM + 6*l.YS)

        #
        playcards = 4*l.YS / l.YOFFSET
        xoffset, yoffset = [], []
        for i in range(playcards):
            xoffset.append(0)
            yoffset.append(l.YOFFSET)
        for i in range(104-playcards):
            xoffset.append(l.XOFFSET)
            yoffset.append(0)

        # create stacks
        x, y = l.XM + (maxrows-reserves)*l.XS/2, l.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x = x + l.XS
        x, y = l.XM + (maxrows-rows)*l.XS/2, l.YM + l.YS
        self.setRegion(s.reserves, (-999, -999, 999999, y - l.CH / 2))
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = yoffset
            s.rows.append(stack)
            x = x + l.XS
        x, y = l.XM + maxrows*l.XS, l.YM
        for suit in range(4):
            for i in range(2):
                s.foundations.append(SS_FoundationStack(x+i*l.XS, y, self, suit=suit))
            y = y + l.YS
        self.setRegion(self.s.foundations, (x - l.CW / 2, -999, 999999, y), priority=1)
        s.talon = InitialDealTalonStack(self.width-3*l.XS/2, self.height-l.YS, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        i = 0
        while self.s.talon.cards:
            if self.s.talon.cards[-1].rank == KING:
                if self.s.rows[i].cards:
                    i = i + 1
            self.s.talon.dealRow(rows=[self.s.rows[i]], frames=4)

    shallHighlightMatch = Game._shallHighlightMatch_AC

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


# ************************************************************************
# *
# ************************************************************************

class DieSchlange(DerKatzenschwanz):

    RowStack_Class = StackWrapper(FreeCell_AC_RowStack, base_rank=NO_RANK)
    Solver_Class = FreeCellSolverWrapper(esf='none')

    def createGame(self):
        DerKatzenschwanz.createGame(self, rows=9, reserves=7)

    def startGame(self):
        self.startDealSample()
        i = 0
        while self.s.talon.cards:
            c = self.s.talon.cards[-1]
            if c.rank == ACE:
                to_stack = self.s.foundations[c.suit*2]
                if to_stack.cards:
                    to_stack = self.s.foundations[c.suit*2+1]
            else:
                if c.rank == KING and self.s.rows[i].cards:
                    i = i + 1
                to_stack = self.s.rows[i]
            self.s.talon.dealRow(rows=(to_stack,), frames=4)


# ************************************************************************
# * Kings
# ************************************************************************

class Kings(DerKatzenschwanz):

    RowStack_Class = StackWrapper(AC_RowStack, base_rank=NO_RANK)
    Solver_Class = FreeCellSolverWrapper(esf='none', sm='unlimited')

    def createGame(self):
        return DerKatzenschwanz.createGame(self, rows=8, reserves=8)

    def _shuffleHook(self, cards):
        for c in cards[:]:
            if c.rank == KING:
                cards.remove(c)
                break
        cards.append(c)
        return cards


# ************************************************************************
# * Retinue
# ************************************************************************

class Retinue(DieSchlange, Kings):

    RowStack_Class = StackWrapper(FreeCell_AC_RowStack, base_rank=NO_RANK)
    Solver_Class = FreeCellSolverWrapper(esf='none')

    def createGame(self):
        return DerKatzenschwanz.createGame(self, rows=8, reserves=8)
    def _shuffleHook(self, cards):
        return Kings._shuffleHook(self, cards)
    def startGame(self):
        return DieSchlange.startGame(self)


# ************************************************************************
# * Salic Law
# ************************************************************************

class SalicLaw_Hint(CautiousDefaultHint):

    # Score for dropping ncards from stack r to stack t.
    def _getDropCardScore(self, score, color, r, t, ncards):
        return score+len(r.cards), color


class SalicLaw_Talon(TalonStack):

    def dealCards(self, sound=False):
        if len(self.cards) == 0:
            return 0
        base_rank=self.game.ROW_BASE_RANK
        old_state = self.game.enterState(self.game.S_DEAL)
        rows = self.game.s.rows
        c = self.cards[-1]
        ri = len([r for r in rows if r.cards])
        if c.rank == base_rank:
            to_stack = rows[ri]
        else:
            to_stack = rows[ri-1]
        if sound and not self.game.demo:
            self.game.startDealSample()
        self.dealToStacks(stacks=[to_stack])
        if sound and not self.game.demo:
            self.game.stopSamples()
        return 1

# all Aces go to the Foundations
class SalicLaw_Talon_2(SalicLaw_Talon):
    def dealCards(self, sound=False):
        if len(self.cards) == 0:
            return 0
        if self.cards[-1].rank == ACE:
            for f in self.game.s.foundations:
                if not f.cards:
                    break
            if sound and not self.game.demo:
                self.game.startDealSample()
            self.dealToStacks(stacks=[f])
            if sound and not self.game.demo:
                self.game.stopSamples()
            return 1
        else:
            return SalicLaw_Talon.dealCards(self, sound=sound)


class SalicLaw_RowStack(OpenStack):
    def acceptsCards(self, from_stack, cards):
        if len(self.cards) == 1:
            return True
        return False
        return OpenStack.acceptsCards(self, from_stack, cards)


class SalicLaw_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack not in self.game.s.rows:
            return False
        row_id = self.id + 8
        return len(self.game.allstacks[row_id].cards) > 0


class SalicLaw(DerKatzenschwanz):

    Hint_Class = SalicLaw_Hint
    Solver_Class = None

    Talon_Class = SalicLaw_Talon_2
    Foundation_Classes = [
        StackWrapper(AbstractFoundationStack, max_cards=1, base_rank=QUEEN),
        StackWrapper(SalicLaw_Foundation, max_cards=11, base_rank=ACE),
        ]
    RowStack_Class = StackWrapper(SalicLaw_RowStack, min_cards=1,
                                  max_accept=UNLIMITED_ACCEPTS)

    ROW_BASE_RANK = KING

    #
    # game layout
    #

    def createGame(self): #, rows=9, reserves=8):
        # create layout
        l, s = Layout(self), self.s

        # set size
        self.setSize(l.XM+10*l.XS, l.YM+(5+len(self.Foundation_Classes))*l.YS)

        #
        playcards = 4*l.YS / l.YOFFSET
        xoffset, yoffset = [], []
        for i in range(playcards):
            xoffset.append(0)
            yoffset.append(l.YOFFSET)
        for i in range(104-playcards):
            xoffset.append(l.XOFFSET)
            yoffset.append(0)

        # create stacks
        y = l.YM
        for found_class in self.Foundation_Classes:
            x = l.XM
            for i in range(8):
                s.foundations.append(found_class(x, y, self,
                                                 suit=ANY_SUIT, max_move=0))
                x += l.XS
            y += l.YS

        x, y = l.XM, l.YM+l.YS*len(self.Foundation_Classes)
        self.setRegion(s.foundations, (-999, -999, 999999, y - l.XM / 2))
        for i in range(8):
            stack = self.RowStack_Class(x, y, self, max_move=1)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = yoffset
            s.rows.append(stack)
            x += l.XS
        s.talon = self.Talon_Class(l.XM+9*l.XS, l.YM, self)
        l.createText(s.talon, "s")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        for c in cards[:]:
            if c.rank == KING:
                cards.remove(c)
                break
        cards.append(c)
        cards = self._shuffleHookMoveToTop(cards,
                                           lambda c: (c.rank == QUEEN, None))
        return cards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(self.s.foundations[:8]) # deal Queens
        self.s.talon.dealRow(self.s.rows[:1]) # deal King

    def isGameWon(self):
        for s in self.s.foundations[8:]:
            if len(s.cards) != 11:
                return False
        return True


# ************************************************************************
# * Deep
# ************************************************************************

class Deep(DerKatzenschwanz):
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=ANY_RANK)
    Solver_Class = FreeCellSolverWrapper(sm='unlimited')

    def createGame(self):
        return DerKatzenschwanz.createGame(self, rows=8, reserves=8)

    def startGame(self):
        for i in range(12):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# ************************************************************************
# * Faerie Queen
# ************************************************************************

class FaerieQueen_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if self.game.s.talon.cards:
            return False
        if len(self.cards) == 1:
            return True
        return RK_RowStack.acceptsCards(self, from_stack, cards)


class FaerieQueen(SalicLaw):

    Talon_Class = SalicLaw_Talon
    Foundation_Classes = [
        StackWrapper(RK_FoundationStack, max_move=0, max_cards=12)
        ]
    RowStack_Class = StackWrapper(FaerieQueen_RowStack, min_cards=1, max_move=1)

    def _shuffleHook(self, cards):
        for c in cards[:]:
            if c.rank == KING:
                cards.remove(c)
                break
        cards.append(c)
        return cards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(self.s.rows[:1]) # deal King

    def isGameWon(self):
        if self.s.talon.cards:
            return False
        for s in self.s.foundations:
            if len(s.cards) != 12:
                return False
        return True

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        return int(len(to_stack.cards) > 1)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Intrigue
# * Laggard Lady
# * Glencoe
# ************************************************************************

class Intrigue_RowStack(OpenStack):
    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        return len(self.game.s.talon.cards) == 0 and len(self.cards) == 1


class Intrigue(SalicLaw):

    Talon_Class = SalicLaw_Talon
    Foundation_Classes = [
        StackWrapper(RK_FoundationStack, base_rank=5, max_cards=6),
        StackWrapper(RK_FoundationStack, base_rank=4, max_cards=6, dir=-1, mod=13),
        ]
    RowStack_Class = StackWrapper(Intrigue_RowStack, max_accept=1, min_cards=1)

    ROW_BASE_RANK = QUEEN

    def _shuffleHook(self, cards):
        for c in cards[:]:
            if c.rank == QUEEN:
                cards.remove(c)
                break
        cards.append(c)
        return cards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(self.s.rows[:1]) # deal King

    def isGameWon(self):
        if self.s.talon.cards:
            return False
        for s in self.s.foundations:
            if len(s.cards) != 6:
                return False
        return True


class LaggardLady_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        c = cards[0]
        if c.rank in (4, 5):
            i = list(self.game.s.foundations).index(self) % 8
            r = self.game.s.rows[i]
            if not r.cards:
                return False
        return True

class LaggardLady(Intrigue):
    Foundation_Classes = [
        StackWrapper(LaggardLady_Foundation, base_rank=5, max_cards=6),
        StackWrapper(LaggardLady_Foundation, base_rank=4, max_cards=6, dir=-1, mod=13),
        ]


class Glencoe_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        c = cards[0]
        if c.rank in (4, 5):
            i = list(self.game.s.foundations).index(self) % 8
            r = self.game.s.rows[i]
            if not r.cards:
                return False
            return c.suit == r.cards[0].suit
        return True

class Glencoe(Intrigue):
    Foundation_Classes = [
        StackWrapper(Glencoe_Foundation, base_rank=5, max_cards=6),
        StackWrapper(Glencoe_Foundation, base_rank=4, max_cards=6, dir=-1, mod=13),
        ]


# ************************************************************************
# * Step-Up
# ************************************************************************

class StepUp_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.reserves:
            return True
        for r in self.game.s.reserves:
            if not r.cards:
                return True
        return False

class StepUp_Talon(WasteTalonStack):
    def canDealCards(self):
        if not WasteTalonStack.canDealCards(self):
            return False
        for r in self.game.s.reserves:
            if not r.cards:
                return False
        return True

class StepUp_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if (from_stack in self.game.s.reserves or
            from_stack in self.game.s.foundations):
            return False
        return True


class StepUp(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+13*l.XS, l.YM+7*l.YS)
        self.base_rank = ANY_RANK

        x, y = l.XM+2.5*l.XS, l.YM
        for i in range(8):
            s.foundations.append(StepUp_Foundation(x, y, self,
                                 suit=i%4, mod=13, base_rank=ANY_RANK))
            x += l.XS
        tx, ty, ta, tf = l.getTextAttr(s.foundations[0], "sw")
        font = self.app.getFont("canvas_default")
        self.texts.info = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)

        x, y = l.XM, l.YM+l.YS
        for i in range(13):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        x, y = l.XM+2*l.XS, l.YM+2*l.YS
        for i in range(9):
            s.rows.append(StepUp_RowStack(x, y, self, max_move=1, mod=13))
            x += l.XS

        x, y = l.XM, l.YM+2.5*l.YS
        s.talon = StepUp_Talon(x, y, self, max_rounds=1)
        l.createText(s.talon, 'se')
        y += l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        l.defaultStackGroups()


    def startGame(self):
        c = self.s.talon.cards[-1]
        self.base_rank = c.rank
        self.s.talon.flipMove()
        self.s.talon.moveMove(1, self.s.foundations[c.suit], frames=0)
        for s in self.s.foundations:
            s.cap.base_rank = c.rank
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def updateText(self):
        if self.preview > 1:
            return
        base_rank = self.base_rank
        if base_rank == ANY_RANK:
            t = ''
        else:
            t = RANKS[base_rank]
        self.texts.info.config(text=t)

    def _restoreGameHook(self, game):
        self.base_rank = game.loadinfo.base_rank
        for s in self.s.foundations:
            s.cap.base_rank = self.base_rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_rank=None)    # register extra load var.
        self.loadinfo.base_rank = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_rank)

    shallHighlightMatch = Game._shallHighlightMatch_ACW


# ************************************************************************
# * Kentish
# ************************************************************************

class Kentish(Kings):
    Solver_Class = FreeCellSolverWrapper(sbb='rank', sm='unlimited')

    def createGame(self, rows=8):
        # create layout
        l, s = Layout(self), self.s

        # set size
        self.setSize(l.XM + (rows+2)*l.XS, l.YM + 5*l.YS)

        #
        playcards = 4*l.YS / l.YOFFSET
        xoffset, yoffset = [], []
        for i in range(playcards):
            xoffset.append(0)
            yoffset.append(l.YOFFSET)
        for i in range(104-playcards):
            xoffset.append(l.XOFFSET)
            yoffset.append(0)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(rows):
            stack = RK_RowStack(x, y, self)
            stack.CARD_XOFFSET = xoffset
            stack.CARD_YOFFSET = yoffset
            s.rows.append(stack)
            x += l.XS
        x, y = l.XM + rows*l.XS, l.YM
        for suit in range(4):
            for i in range(2):
                s.foundations.append(RK_FoundationStack(x+i*l.XS, y, self,
                                                        suit=suit))
            y += l.YS
        self.setRegion(self.s.foundations,
                       (x - l.CW / 2, -999, 999999, y), priority=1)
        x, y = self.width-3*l.XS/2, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        for c in cards[:]:
            if c.rank == ACE:
                cards.remove(c)
                break
        cards.insert(0, c)
        return cards

    def startGame(self):
        self.startDealSample()
        i = 0
        while self.s.talon.cards:
            r = self.s.talon.cards[-1].rank
            self.s.talon.dealRow(rows=[self.s.rows[i]], frames=4)
            if r == ACE:
                i += 1

    shallHighlightMatch = Game._shallHighlightMatch_RK



# register the game
registerGame(GameInfo(141, DerKatzenschwanz, "Cat's Tail",
                      GI.GT_FREECELL | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Der Katzenschwanz",) ))
registerGame(GameInfo(142, DieSchlange, "Snake",
                      GI.GT_FREECELL | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Die Schlange",) ))
registerGame(GameInfo(279, Kings, "Kings",
                      GI.GT_FREECELL | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(286, Retinue, "Retinue",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(299, SalicLaw, "Salic Law",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(442, Deep, "Deep",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(523, Intrigue, "Intrigue",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(611, FaerieQueen, "Faerie Queen",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(612, Glencoe, "Glencoe",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED,
                      rules_filename="intrigue.html"))
registerGame(GameInfo(616, LaggardLady, "Laggard Lady",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED,
                      rules_filename="intrigue.html"))
registerGame(GameInfo(624, StepUp, "Step-Up",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(766, Kentish, "Kentish",
                      GI.GT_2DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))



