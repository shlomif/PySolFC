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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

# /***********************************************************************
# //
# ************************************************************************/

class Bristol_Hint(CautiousDefaultHint):
    # FIXME: demo is not too clever in this game

    BONUS_CREATE_EMPTY_ROW     = 0           # 0..9000
    BONUS_CAN_DROP_ALL_CARDS   = 0           # 0..4000
    BONUS_CAN_CREATE_EMPTY_ROW = 0           # 0..4000

    # Score for moving a pile from stack r to stack t.
    # Increased score must be in range 0..9999
    def _getMovePileScore(self, score, color, r, t, pile, rpile):
        # prefer reserves
        if not r in self.game.s.reserves:
            score = score - 10000
            # an empty pile doesn't gain anything
            if len(pile) == len(r.cards):
                return -1, color
        return CautiousDefaultHint._getMovePileScore(self, score, color, r, t, pile, rpile)


# /***********************************************************************
# // Bristol
# ************************************************************************/

class Bristol_Talon(TalonStack):
    def dealCards(self, sound=0):
        return self.dealRowAvail(rows=self.game.s.reserves, sound=sound)


class Bristol(Game):
    Layout_Method = Layout.klondikeLayout
    Hint_Class = Bristol_Hint

    #
    # game layout
    #

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 10*l.XS, l.YM + 5*l.YS)

        # create stacks
        x, y, = l.XM + 3*l.XS, l.YM
        for i in range(4):
            s.foundations.append(RK_FoundationStack(x, y, self, max_move=0))
            x = x + l.XS
        for i in range(2):
            y = l.YM + (i*2+3)*l.YS/2
            for j in range(4):
                x = l.XM + (j*5)*l.XS/2
                stack = RK_RowStack(x, y, self,  base_rank=NO_RANK, max_move=1)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
        x, y, = l.XM + 3*l.XS, l.YM + 4*l.YS
        s.talon = Bristol_Talon(x, y, self)
        l.createText(s.talon, "sw")
        for i in range(3):
            x = x + l.XS
            s.reserves.append(ReserveStack(x, y, self, max_accept=0, max_cards=UNLIMITED_CARDS))

        # define stack-groups
        self.sg.openstacks = s.foundations + s.rows
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows + s.reserves

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move Kings to bottom of each stack
        i, n = 0, len(self.s.rows)
        kings = []
        for c in cards[:24]:    # search the first 24 cards only
            if c.rank == KING:
                kings.append(i)
            i = i + 1
        for i in kings:
            j = i % n           # j = card index of rowstack bottom
            while j < i:
                if cards[j].rank != KING:
                    cards[j], cards[i] = cards[i], cards[j]
                    break
                j = j + n
        cards.reverse()
        return cards

    def startGame(self):
        r = self.s.rows
        for i in range(2):
            self.s.talon.dealRow(rows=r, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=r)
        self.s.talon.dealCards()          # deal first cards to Reserves


# /***********************************************************************
# // Belvedere
# ************************************************************************/

class Belvedere(Bristol):
    def _shuffleHook(self, cards):
        # remove 1 Ace
        for c in cards:
            if c.rank == 0:
                cards.remove(c)
                break
        # move Kings to bottom
        cards = Bristol._shuffleHook(self, cards)
        # re-insert Ace
        return cards[:-24] + [c] + cards[-24:]

    def startGame(self):
        r = self.s.rows
        for i in range(2):
            self.s.talon.dealRow(rows=r, frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=r)
        assert self.s.talon.cards[-1].rank == ACE
        self.s.talon.dealRow(rows=self.s.foundations[:1])
        self.s.talon.dealCards()          # deal first cards to Reserves


# /***********************************************************************
# // Dover
# ************************************************************************/

class Dover_RowStack(RK_RowStack):

    def acceptsCards(self, from_stack, cards):
        if not self.cards and from_stack in self.game.s.reserves:
            return True
        return RK_RowStack.acceptsCards(self, from_stack, cards)


class Dover(Bristol):

    Talon_Class = Bristol_Talon
    Foundation_Class = StackWrapper(SS_FoundationStack, max_move=0)
    RowStack_Class = StackWrapper(Dover_RowStack, base_rank=NO_RANK, max_move=1)
    ReserveStack_Class = StackWrapper(ReserveStack, max_accept=0, max_cards=UNLIMITED_CARDS)

    def createGame(self, rows=8, text=False):
        # create layout
        l, s = Layout(self), self.s

        # set window
        max_rows = max(rows, self.gameinfo.decks*4)
        w, h = 2*l.XM+l.XS+max_rows*l.XS, l.YM+l.TEXT_HEIGHT+5*l.YS
        self.setSize(w, h)

        # create stacks
        x, y, = 2*l.XM+l.XS+l.XS*(max_rows-self.gameinfo.decks*4), l.YM
        for j in range(self.gameinfo.decks):
            for i in range(4):
                s.foundations.append(self.Foundation_Class(x, y, self, suit=i))
                x += l.XS
        if text:
            x, y = l.XM+8*l.XS, l.YM
            tx, ty, ta, tf = l.getTextAttr(None, "s")
            tx, ty = x+tx+l.XM, y+ty
            font = self.app.getFont("canvas_default")
            self.texts.info = MfxCanvasText(self.canvas, tx, ty, anchor=ta, font=font)

        x, y = 2*l.XM+(max_rows-rows)*l.XS, l.YM+l.YS
        if text:
            y += l.TEXT_HEIGHT
        for i in range(rows):
            x += l.XS
            stack = self.RowStack_Class(x, y, self)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, l.YOFFSET
            s.rows.append(stack)
        x, y, = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, "s")
        y += l.TEXT_HEIGHT
        for i in range(3):
            y += l.YS
            s.reserves.append(self.ReserveStack_Class(x, y, self))

        # define stack-groups
        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return cards


# /***********************************************************************
# // New York
# ************************************************************************/

class NewYork_Hint(CautiousDefaultHint):
    def computeHints(self):
        CautiousDefaultHint.computeHints(self)
        if self.hints:
            return
        if not self.game.s.talon.cards:
            return
        c = self.game.s.talon.cards[-1].rank - self.game.base_card.rank
        if c < 0: c += 13
        if 0 <= c <= 3:
            r = self.game.s.reserves[0]
        elif 4 <= c <= 7:
            r = self.game.s.reserves[1]
        else:
            r = self.game.s.reserves[2]
        self.addHint(5000, 1, self.game.s.talon, r)


class NewYork_Talon(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler


class NewYork_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack is self.game.s.talon


class NewYork_RowStack(AC_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not AC_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return (from_stack is self.game.s.talon or
                    from_stack in self.game.s.reserves)
        return True


class NewYork(Dover):

    Hint_Class = NewYork_Hint
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, max_move=0)
    Talon_Class = NewYork_Talon
    RowStack_Class = StackWrapper(NewYork_RowStack, base_rank=ANY_RANK, mod=13, max_move=1)
    ReserveStack_Class = StackWrapper(NewYork_ReserveStack, max_accept=1, max_cards=UNLIMITED_CARDS, mod=13)

    def createGame(self):
        # extra settings
        self.base_card = None
        Dover.createGame(self, text=True)
        self.sg.dropstacks.append(self.s.talon)

    def updateText(self):
        if self.preview > 1:
            return
        if not self.base_card:
            t = ""
        else:
            t = RANKS[self.base_card.rank]
        self.texts.info.config(text=t)

    def startGame(self):
        self.startDealSample()
        self.base_card = None
        self.updateText()
        # deal base_card to Foundations, update foundations cap.base_rank
        self.base_card = self.s.talon.getCard()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        n = self.base_card.suit
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, self.s.foundations[n])
        ##self.updateText()
        self.s.talon.dealRow()
        self.s.talon.fillStack()

    shallHighlightMatch = Game._shallHighlightMatch_ACW

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


# /***********************************************************************
# // Spike
# ************************************************************************/

class Spike(Dover):

    Foundation_Class = SS_FoundationStack
    RowStack_Class = KingAC_RowStack

    def createGame(self):
        Dover.createGame(self, rows=7)

    def startGame(self):
        for i in range(1, 7):
            self.s.talon.dealRow(rows=self.s.rows[i:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_AC


# /***********************************************************************
# // Gotham
# ************************************************************************/

class Gotham_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return (from_stack is self.game.s.talon or
                    from_stack in self.game.s.reserves)
        return True

class Gotham(NewYork):
    RowStack_Class = StackWrapper(Gotham_RowStack, base_rank=ANY_RANK, mod=13)
    def startGame(self):
        self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(frames=0)
        NewYork.startGame(self)


# register the game
registerGame(GameInfo(42, Bristol, "Bristol",
                      GI.GT_FAN_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(214, Belvedere, "Belvedere",
                      GI.GT_FAN_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(266, Dover, "Dover",
                      GI.GT_FAN_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(425, NewYork, "New York",
                      GI.GT_FAN_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(468, Spike, "Spike",
                      GI.GT_KLONDIKE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(519, Gotham, "Gotham",
                      GI.GT_FAN_TYPE, 2, 0, GI.SL_BALANCED))

