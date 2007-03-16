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
import sys, types

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

# /***********************************************************************
# //
# ************************************************************************/

class Golf_Hint(AbstractHint):
    # FIXME: this is very simple

    def computeHints(self):
        game = self.game
        # for each stack
        for r in game.sg.dropstacks:
            # try if we can drop a card to the Waste
            w, ncards = r.canDropCards(game.s.foundations)
            if not w:
                continue
            # this assertion must hold for Golf
            assert ncards == 1
            # clone the Waste (including the card that will be dropped) to
            # form our new foundations
            ww = (self.ClonedStack(w, stackcards=w.cards+[r.cards[-1]]), )
            # now search for a stack that would benefit from this card
            score, color = 10000 + r.id, None
            for t in game.sg.dropstacks:
                if not t.cards:
                    continue
                if t is r:
                    t = self.ClonedStack(r, stackcards=r.cards[:-1])
                if t.canFlipCard():
                    score = score + 100
                elif t.canDropCards(ww)[0]:
                    score = score + 100
            # add hint
            self.addHint(score, ncards, r, w, color)


# /***********************************************************************
# //
# ************************************************************************/

class Golf_Talon(WasteTalonStack):
    def canDealCards(self):
        if not WasteTalonStack.canDealCards(self):
            return 0
        return not self.game.isGameWon()


class Golf_Waste(WasteStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=0, max_accept=1)
        WasteStack.__init__(self, x, y, game, **cap)

    def acceptsCards(self, from_stack, cards):
        if not WasteStack.acceptsCards(self, from_stack, cards):
            return 0
        # check cards
        r1, r2 = self.cards[-1].rank, cards[0].rank
        if self.game.getStrictness() == 1:
            # nothing on a King
            if r1 == KING:
                return 0
        return (r1 + 1) % self.cap.mod == r2 or (r2 + 1) % self.cap.mod == r1


class Golf_RowStack(BasicRowStack):
    def clickHandler(self, event):
        return self.doubleclickHandler(event)
    def getHelp(self):
        return _('Tableau. No building.')


# /***********************************************************************
# // Golf
# ************************************************************************/

class Golf(Game):
    Waste_Class = Golf_Waste
    Hint_Class = Golf_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        playcards = 5
        w1, w2 = 8*l.XS+l.XM, 2*l.XS
        if w2 + 52*l.XOFFSET > w1:
            l.XOFFSET = int((w1 - w2) / 52)
        self.setSize(w1, l.YM+3*l.YS+(playcards-1)*l.YOFFSET+l.TEXT_HEIGHT)

        # create stacks
        x, y = l.XM + l.XS / 2, l.YM
        for i in range(7):
            s.rows.append(Golf_RowStack(x, y, self))
            x = x + l.XS
        x, y = l.XM, self.height - l.YS
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        l.createText(s.talon, "n")
        x = x + l.XS
        s.waste = self.Waste_Class(x, y, self)
        s.waste.CARD_XOFFSET = l.XOFFSET
        l.createText(s.waste, "n")
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        for r in self.s.rows:
            if r.cards:
                return 0
        return 1

    shallHighlightMatch = Game._shallHighlightMatch_RK

    def getHighlightPilesStacks(self):
        return ()

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return (self.sg.dropstacks, (), ())
        else:
            # rightclickHandler
            return (self.sg.dropstacks, self.sg.dropstacks, ())


# /***********************************************************************
# //
# ************************************************************************/

class DeadKingGolf(Golf):
    def getStrictness(self):
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if card1.rank == KING:
            return 0
        return Golf.shallHighlightMatch(self, stack1, card1, stack2, card2)


class RelaxedGolf(Golf):
    Waste_Class = StackWrapper(Golf_Waste, mod=13)

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# /***********************************************************************
# // Elevator - Relaxed Golf in a Pyramid layout
# ************************************************************************/

class Elevator_RowStack(Golf_RowStack):
    STEP = (1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6)

    def basicIsBlocked(self):
        r, step = self.game.s.rows, self.STEP
        i, n, l = self.id, 1, len(step)
        while i < l:
            i = i + step[i]
            n = n + 1
            for j in range(i, i+n):
                if r[j].cards:
                    return 1
        return 0


class Elevator(RelaxedGolf):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(9*l.XS+l.XM, 4*l.YS+l.YM)

        # create stacks
        for i in range(7):
            x = l.XM + (8-i) * l.XS / 2
            y = l.YM + i * l.YS / 2
            for j in range(i+1):
                s.rows.append(Elevator_RowStack(x, y, self))
                x = x + l.XS
        x, y = l.XM, l.YM
        s.talon = Golf_Talon(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = self.Waste_Class(x, y, self)
        l.createText(s.waste, "s")
        # the Waste is also our only Foundation in this game
        s.foundations.append(s.waste)

        # define stack-groups (non default)
        self.sg.openstacks = [s.waste]
        self.sg.talonstacks = [s.talon]
        self.sg.dropstacks = s.rows

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:21], flip=0)
        self.s.talon.dealRow(rows=self.s.rows[21:])
        self.s.talon.dealCards()          # deal first card to WasteStack

class Escalator(Elevator):
    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Black Hole
# ************************************************************************/

class BlackHole_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # check the rank
        if self.cards:
            r1, r2 = self.cards[-1].rank, cards[0].rank
            return (r1 + 1) % self.cap.mod == r2 or (r2 + 1) % self.cap.mod == r1
        return 1
    def getHelp(self):
        return _('Foundation. Build up or down regardless of suit.')


class BlackHole_RowStack(ReserveStack):
    def clickHandler(self, event):
        return self.doubleclickHandler(event)
    def getHelp(self):
        return _('Tableau. No building.')


class BlackHole(Game):
    RowStack_Class = StackWrapper(BlackHole_RowStack, max_accept=0, max_cards=3)
    Hint_Class = Golf_Hint

    #
    # game layout
    #

    def createGame(self, playcards=5):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w = max(2*l.XS, l.XS+(playcards-1)*l.XOFFSET)
        self.setSize(l.XM + 5*w, l.YM + 4*l.YS)

        # create stacks
        y = l.YM
        for i in range(5):
            x = l.XM + i*w
            s.rows.append(self.RowStack_Class(x, y, self))
        for i in range(2):
            y = y + l.YS
            for j in (0, 1, 3, 4):
                x = l.XM + j*w
                s.rows.append(self.RowStack_Class(x, y, self))
        y = y + l.YS
        for i in range(4):
            x = l.XM + i*w
            s.rows.append(self.RowStack_Class(x, y, self))
        for r in s.rows:
            r.CARD_XOFFSET = l.XOFFSET
            r.CARD_YOFFSET = 0
        x, y = l.XM + 2*w, l.YM + 3*l.YS/2
        s.foundations.append(BlackHole_Foundation(x, y, self, suit=ANY_SUIT,
                             dir=0, mod=13, max_move=0, max_cards=52))
        l.createText(s.foundations[0], "s")
        x, y = l.XM + 4*w, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # move Ace to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.id == 13, c.suit), 1)

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return ((), (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return ((), self.sg.dropstacks, self.sg.dropstacks)



# /***********************************************************************
# // Four Leaf Clovers
# ************************************************************************/

class FourLeafClovers_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # check the rank
        if self.cards:
            r1, r2 = self.cards[-1].rank, cards[0].rank
            return (r1 + 1) % self.cap.mod == r2
        return 1
    def getHelp(self):
        return _('Foundation. Build up regardless of suit.')


class FourLeafClovers(Game):

    Hint_Class = CautiousDefaultHint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        h = l.YS + 6*l.YOFFSET
        self.setSize(l.XM + 7*l.XS, l.YM + 2*h)

        # create stacks
        y = l.YM
        for i in range(7):
            x = l.XM + i*l.XS
            s.rows.append(UD_RK_RowStack(x, y, self, mod=13, base_rank=NO_RANK))
        y = l.YM+h
        for i in range(6):
            x = l.XM + i*l.XS
            s.rows.append(UD_RK_RowStack(x, y, self, mod=13, base_rank=NO_RANK))

        s.foundations.append(FourLeafClovers_Foundation(l.XM+6*l.XS, self.height-l.YS, self, ANY_SUIT, dir=0, mod=13, max_move=0, max_cards=52))
        x, y = l.XM + 7*l.XS, self.height - l.YS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_RKW


# /***********************************************************************
# // All in a Row
# ************************************************************************/

class AllInARow(BlackHole):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        h = l.YM+l.YS+4*l.YOFFSET
        self.setSize(l.XM+7*l.XS, 3*l.YM+2*h+l.YS)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(7):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        x, y = l.XM, l.YM+h
        for i in range(6):
            s.rows.append(self.RowStack_Class(x, y, self))
            x += l.XS
        for r in s.rows:
            r.CARD_XOFFSET, r.CARD_YOFFSET = 0, l.YOFFSET

        x, y = l.XM, self.height-l.YS
        stack = BlackHole_Foundation(x, y, self, ANY_SUIT, dir=0, mod=13, max_move=0, max_cards=52, base_rank=ANY_RANK)
        s.foundations.append(stack)
        stack.CARD_XOFFSET, stack.CARD_YOFFSET = (self.width-l.XS)/51, 0
        l.createText(stack, 'n')
        x = self.width-l.XS
        s.talon = InitialDealTalonStack(x, y, self)

        # define stack-groups
        l.defaultStackGroups()


    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


# /***********************************************************************
# // Robert
# ************************************************************************/

class Robert(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+4*l.XS, l.YM+2*l.YS)
        x, y = l.XM+3*l.XS/2, l.YM
        s.foundations.append(BlackHole_Foundation(x, y, self, ANY_SUIT, dir=0, mod=13, max_move=0, max_cards=52))
        x, y = l.XM+l.XS, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 'sw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()


# /***********************************************************************
# // Diamond Mine
# ************************************************************************/

DIAMOND = 3

class DiamondMine_RowStack(RK_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if cards[0].suit == DIAMOND:
            return False
        if self.cards:
            return self.cards[-1].suit != DIAMOND
        return True


class DiamondMine(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+13*l.XS, l.YM+2*l.YS+15*l.YOFFSET)

        x, y = l.XM+6*l.XS, l.YM
        s.foundations.append(SS_FoundationStack(x, y, self,
                             base_rank=ANY_RANK, suit=DIAMOND, mod=13))
        x, y = l.XM, l.YM+l.YS
        for i in range(13):
            s.rows.append(DiamondMine_RowStack(x, y, self))
            x += l.XS
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        l.defaultAll()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != 13:
            return False
        for s in self.s.rows:
            if len(s.cards) == 0:
                continue
            if len(s.cards) != 13:
                return False
            if not isSameSuitSequence(s.cards):
                return False
        return True

    shallHighlightMatch = Game._shallHighlightMatch_RK


# /***********************************************************************
# // Dolphin
# ************************************************************************/

class Dolphin(Game):

    def createGame(self, rows=8, reserves=4, playcards=6):
        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM+3*l.YS+playcards*l.YOFFSET)

        dx = (self.width-l.XM-(reserves+1)*l.XS)/3
        x, y = l.XM+dx, l.YM
        for i in range(reserves):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS
        x += dx
        max_cards = 52*self.gameinfo.decks
        s.foundations.append(RK_FoundationStack(x, y, self,
                             base_rank=ANY_RANK, mod=13, max_cards=max_cards))
        x, y = l.XM, l.YM+l.YS
        for i in range(rows):
            s.rows.append(BasicRowStack(x, y, self))
            x += l.XS
        s.talon = InitialDealTalonStack(l.XM, self.height-l.YS, self)

        l.defaultAll()

    def startGame(self):
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


class DoubleDolphin(Dolphin):

    def createGame(self):
        Dolphin.createGame(self, rows=10, reserves=5, playcards=10)

    def startGame(self):
        for i in range(9):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRowAvail()


# /***********************************************************************
# // Waterfall
# ************************************************************************/

class Waterfall_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return False
        c1 = cards[0]
        if not self.cards:
            return c1.rank == ACE and c1.suit == 0
        c2 = self.cards[-1]
        if c2.rank == KING:
            suit = (c2.suit+1) % 4
            rank = ACE
        else:
            suit = c2.suit
            rank = c2.rank+1
        return c1.suit == suit and c1.rank == rank


class Waterfall(Game):

    def createGame(self):
        rows = 8
        l, s = Layout(self), self.s
        self.setSize(l.XM+rows*l.XS, l.YM+2*l.YS+20*l.YOFFSET)

        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self))
            x += l.XS
        x, y = l.XM+(rows-1)*l.XS/2, self.height-l.YS
        s.foundations.append(Waterfall_Foundation(x, y, self, suit=ANY_SUIT,
                                                  max_cards=104))
        stack = s.foundations[0]
        tx, ty, ta, tf = l.getTextAttr(stack, 'se')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)
        x, y = self.width-l.XS, self.height-l.YS
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, 'sw')

        l.defaultStackGroups()

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def updateText(self):
        if self.preview > 1:
            return
        f = self.s.foundations[0]
        if len(f.cards) == 104:
            t = ''
        elif len(f.cards) == 0:
            t = SUITS[0]
        else:
            c = f.cards[-1]
            if c.rank == KING:
                suit = (c.suit+1) % 4
            else:
                suit = c.suit
            t = SUITS[suit]
        f.texts.misc.config(text=t)

    shallHighlightMatch = Game._shallHighlightMatch_RK


# /***********************************************************************
# // Vague
# ************************************************************************/

class Vague_RowStack(BasicRowStack):
    clickHandler = BasicRowStack.doubleclickHandler


class Vague(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+6*l.XS, l.YM+4*l.YS)

        x, y = l.XM, l.YM
        s.talon = TalonStack(x, y, self)
        l.createText(s.talon, 'ne')

        x, y = l.XM+2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 base_rank=ANY_RANK, mod=13))
            x += l.XS

        y = l.YM+l.YS
        for i in range(3):
            x = l.XM
            for j in range(6):
                s.rows.append(Vague_RowStack(x, y, self))
                x += l.XS
            y += l.YS

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.flipMove()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                if not self.s.talon.cards[-1].face_up:
                    self.s.talon.flipMove()
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    def getAutoStacks(self, event=None):
        if event is None:
            # disable auto drop - this would ruin the whole gameplay
            return ((), (), self.sg.dropstacks)
        else:
            # rightclickHandler
            return ((), self.sg.dropstacks, self.sg.dropstacks)


# /***********************************************************************
# // Devil's Solitaire
# ************************************************************************/

class DevilsSolitaire_Foundation(RK_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not RK_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if self.cards:
            return True
        if self.game.s.reserves[0].cards:
            c = self.game.s.reserves[0].cards[-1]
            return (c.rank+1) % 13 == cards[-1].rank
        return True


class DevilsSolitaire_WasteStack(WasteStack):
    clickHandler = WasteStack.doubleclickHandler


class DevilsSolitaire(Game):

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+3*l.YS+7*l.YOFFSET+2*l.TEXT_HEIGHT)

        x, y = l.XM+4*l.XS, l.YM
        stack = DevilsSolitaire_Foundation(x, y, self,
                             suit=ANY_SUIT, base_rank=ANY_RANK, mod=13)
        tx, ty, ta, tf = l.getTextAttr(stack, 'nw')
        font = self.app.getFont('canvas_default')
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                         anchor=ta, font=font)
        s.foundations.append(stack)

        x, y = self.width-l.XS, l.YM
        stack = AbstractFoundationStack(x, y, self,
                             suit=ANY_SUIT, max_move=0, max_cards=104,
                             max_accept=0, base_rank=ANY_RANK)
        l.createText(stack, 'nw')
        s.foundations.append(stack)

        x, y = l.XM, l.YM+l.YS
        for i in range(4):
            s.rows.append(Vague_RowStack(x, y, self))
            x += l.XS
        x += l.XS
        for i in range(4):
            s.rows.append(Vague_RowStack(x, y, self))
            x += l.XS

        x, y = l.XM+4*l.XS, l.YM+l.YS
        stack = OpenStack(x, y, self)
        stack.CARD_YOFFSET = l.YOFFSET
        s.reserves.append(stack)

        x, y = l.XM+4.5*l.XS, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, 'n')
        tx, ty, ta, tf = l.getTextAttr(s.talon, 'nn')
        font = self.app.getFont('canvas_default')
        s.talon.texts.rounds = MfxCanvasText(self.canvas, tx, ty-l.TEXT_MARGIN,
                                             anchor=ta, font=font)

        x -= l.XS
        s.waste = DevilsSolitaire_WasteStack(x, y, self)
        l.createText(s.waste, 'n')

        l.defaultStackGroups()


    def startGame(self):
        for i in range(8):
            self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        old_state = self.enterState(self.S_FILL)
        if stack in self.s.rows and not stack.cards:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
        f0 = self.s.foundations[0]
        if len(f0.cards) == 12:
            self.moveMove(1, self.s.reserves[0], f0, frames=4)
            f1 = self.s.foundations[1]
            for i in range(13):
                self.moveMove(1, f0, f1, frames=4)
        self.leaveState(old_state)

    def updateText(self):
        if self.preview > 1:
            return
        f = self.s.foundations[0]
        r = self.s.reserves[0]
        if not r.cards:
            t = ''
        else:
            c = r.cards[-1]
            t = RANKS[(c.rank+1) % 13]
        f.texts.misc.config(text=t)



# register the game
registerGame(GameInfo(36, Golf, "Golf",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(259, DeadKingGolf, "Dead King Golf",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(260, RelaxedGolf, "Relaxed Golf",
                      GI.GT_GOLF | GI.GT_RELAXED, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(40, Elevator, "Elevator",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED,
                      altnames=("Egyptian Solitaire", "Pyramid Golf") ))
registerGame(GameInfo(98, BlackHole, "Black Hole",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(267, FourLeafClovers, "Four Leaf Clovers",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(281, Escalator, "Escalator",
                      GI.GT_GOLF, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(405, AllInARow, "All in a Row",
                      GI.GT_GOLF | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(432, Robert, "Robert",
                      GI.GT_GOLF, 1, 2, GI.SL_LUCK))
registerGame(GameInfo(551, DiamondMine, "Diamond Mine",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(661, Dolphin, "Dolphin",
                      GI.GT_GOLF | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(662, DoubleDolphin, "Double Dolphin",
                      GI.GT_GOLF | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(709, Waterfall, "Waterfall",
                      GI.GT_2DECK_TYPE | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(720, Vague, "Vague",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_LUCK))
registerGame(GameInfo(723, DevilsSolitaire, "Devil's Solitaire",
                      GI.GT_2DECK_TYPE, 2, 2, GI.SL_BALANCED))

