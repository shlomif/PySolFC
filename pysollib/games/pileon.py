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
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# * PileOn
# ************************************************************************

class PileOn_RowStack(RK_RowStack):
    getBottomImage = Stack._getReserveBottomImage

    def closeStack(self):
        if len(self.cards) == 4 and isRankSequence(self.cards, dir=0):
            if not self.game.moves.state == self.game.S_REDO:
                self.game.flipAllMove(self)

    def canFlipCard(self):
        return False


class PileOn(Game):
    Hint_Class = DefaultHint
    ##Hint_Class = CautiousDefaultHint
    TWIDTH = 4     
    NSTACKS = 15
    PLAYCARDS = 4

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (set size so that at least 4 cards are fully playable)
        #w = max(2*l.XS, l.XS+(self.PLAYCARDS-1)*l.XOFFSET+2*l.XM)
        w = l.XS+(self.PLAYCARDS-1)*l.XOFFSET+3*l.XOFFSET
        twidth, theight = self.TWIDTH, int((self.NSTACKS-1)/self.TWIDTH+1)
        self.setSize(l.XM+twidth*w, l.YM+theight*l.YS)

        # create stacks
        y = l.YM
        for i in range(theight):
            x = l.XM
            for j in range(twidth):
                if i*twidth+j >= self.NSTACKS:
                    break
                stack = PileOn_RowStack(x, y, self, dir=0, max_cards=self.PLAYCARDS)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                x = x + w
            y = y + l.YS
        x, y = self.width - l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        self.sg.openstacks = s.rows
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self):
        r = self.s.rows[:-2]
        for i in range(self.PLAYCARDS-1):
            self.s.talon.dealRow(rows=r, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=r)

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards and not cardsFaceDown(r.cards):
                return False
        return True

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank


class SmallPileOn(PileOn):
    TWIDTH = 3
    NSTACKS = 11
    PLAYCARDS = 4


## class PileOn2Decks(PileOn):
##     TWIDTH = 4
##     NSTACKS = 15
##     PLAYCARDS = 8
## registerGame(GameInfo(341, PileOn2Decks, "PileOn (2 decks)",
##                       GI.GT_2DECK_TYPE | GI.GT_OPEN,, 2, 0))


# ************************************************************************
# * Foursome
# * Quartets
# ************************************************************************

class Foursome(Game):
    Hint_Class = CautiousDefaultHint
    Talon_Class = DealRowTalonStack

    def createGame(self, rows=6, texts=True):
        l, s = Layout(self), self.s
        max_rows = max(8, rows)
        self.setSize(l.XM+max_rows*l.XS, l.YM+2*l.YS+13*l.YOFFSET)
        x, y = l.XM+l.XS*(max_rows-4)/2, l.YM
        for i in range(4):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        x = l.XM+(max_rows-1)*l.XS
        s.foundations.append(AbstractFoundationStack(x, y, self,
                             suit=ANY_SUIT, max_cards=52, max_accept=0))
        l.createText(s.foundations[0], 'nw')
        x, y = l.XM+l.XS*(max_rows-rows)/2, l.YM+l.YS
        for i in range(rows):
            s.rows.append(UD_AC_RowStack(x, y, self, mod=13))
            x += l.XS
        s.talon = self.Talon_Class(l.XM, l.YM, self)
        if texts:
            l.createText(s.talon, 'ne')
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.reserves)
        self.s.talon.dealRow()

    def fillStack(self, stack):
        if not self.s.reserves[0].cards:
            return
        rank = self.s.reserves[0].cards[0].rank
        for r in self.s.reserves[1:]:
            if not r.cards or r.cards[0].rank != rank:
                return
        old_state = self.enterState(self.S_FILL)
        self.playSample("droppair", priority=200)
        for r in self.s.reserves:
            self.moveMove(1, r, self.s.foundations[0], frames=4)
            self.flipMove(self.s.foundations[0])
        self.leaveState(old_state)


    shallHighlightMatch = Game._shallHighlightMatch_ACW


class Quartets(Foursome):
    Talon_Class = InitialDealTalonStack

    def createGame(self):
        Foursome.createGame(self, rows=8, texts=False)

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


# ************************************************************************
# * Four by Four
# ************************************************************************

class FourByFour_Hint(DefaultHint):

    def _getMovePileScore(self, score, color, r, t, pile, rpile):
        self.bonus_color = color
        if len(t.cards) == 0:
            return 0, color
        return score + 1000 - len(r.cards), color

    def _getDropCardScore(self, score, color, r, t, ncards):
        # drop immediately
        return 93000, color


class FourByFour_Foundation(AbstractFoundationStack):

    def _getNumSameCards(self):
        decks = self.game.gameinfo.decks
        rank = self.cards[-1].rank
        n = 1
        for i in range(2, 4*decks+1):
            if len(self.cards) < i:
                break
            if self.cards[-i].rank != rank:
                break
            n += 1
        return n

    def _getDir(self):
        decks = self.game.gameinfo.decks
        if len(self.cards) < 4*decks:
            return 0
        if isRankSequence(self.cards[-4*decks:], dir=0):
            return 1
        return 0

    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        dir = self._getDir()
        return (self.cards[-1].rank+dir) % self.cap.mod == cards[0].rank

    def getHelp(self):
        return _('Foundation. Build up regardless of suit.')


class FourByFour(Game):
    Hint_Class = FourByFour_Hint

    def createGame(self):

        l, s = Layout(self), self.s
        self.setSize(l.XM+7*l.XS, l.YM+2*l.YS+20*l.YOFFSET)

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')

        x += 3.5*l.XS
        s.foundations.append(FourByFour_Foundation(x, y, self,
                             suit=ANY_SUIT, base_rank=ANY_RANK, max_cards=52,
                             max_accept=1, max_move=0, mod=13))
        stack = s.foundations[0]
        tx, ty, ta, tf = l.getTextAttr(stack, 'ne')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)

        x, y = l.XM+3*l.XS, l.YM+l.YS
        for i in range(4):
            stack = UD_RK_RowStack(x, y, self, mod=13)
            stack.getBottomImage = stack._getReserveBottomImage
            s.rows.append(stack)
            x += l.XS

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()

    def updateText(self):
        decks = self.gameinfo.decks
        if self.preview > 1:
            return
        f = self.s.foundations[0]
        if not f.cards:
            if f.cap.base_rank == ANY_RANK:
                t = ''
            else:
                r = RANKS[f.cap.base_rank]
                n = 4*decks
                t = '%s (%d)' % (r, n)
        elif len(f.cards) == 52*decks:
            t = ''
        else:
            n = f._getNumSameCards()
            n = 4*decks - n
            r = f.cards[-1].rank
            if n == 0:
                n = 4*decks
                r = (r+1) % f.cap.mod
            r = r % 13
            r = RANKS[r]
            t = '%s (%d)' % (r, n)
        f.texts.misc.config(text=t)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# ************************************************************************
# * Footling
# ************************************************************************

class Footling(FourByFour):
    Hint_Class = DefaultHint

    def createGame(self, rows=8, reserves=4, playcards=15):

        decks = self.gameinfo.decks

        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM+2*l.YS+playcards*l.YOFFSET)

        x, y = l.XM, l.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS

        x = self.width - 2*l.XS
        s.foundations.append(FourByFour_Foundation(x, y, self,
                             suit=ANY_SUIT, base_rank=ACE, max_cards=52*decks,
                             max_accept=1, max_move=0))
        stack = s.foundations[0]
        tx, ty, ta, tf = l.getTextAttr(stack, 'ne')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)

        x, y = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(AC_RowStack(x, y, self))
            x += l.XS

        x, y = l.XM, self.height-l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        l.defaultStackGroups()

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()

    shallHighlightMatch = Game._shallHighlightMatch_AC


class DoubleFootling(Footling):
    def createGame(self):
        Footling.createGame(self, rows=10, reserves=5, playcards=18)
    def startGame(self):
        for i in range(9):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


# register the game
registerGame(GameInfo(41, PileOn, "PileOn",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Fifteen Puzzle",) ))
registerGame(GameInfo(289, SmallPileOn, "Small PileOn",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL,
                      ranks=(0, 5, 6, 7, 8, 9, 10, 11, 12),
                      rules_filename = "pileon.html"))
registerGame(GameInfo(554, Foursome, "Foursome",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(555, Quartets, "Quartets",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(703, FourByFour, "Four by Four",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(740, Footling, "Footling",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(741, DoubleFootling, "Double Footling",
                      GI.GT_FREECELL | GI.GT_OPEN | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))


