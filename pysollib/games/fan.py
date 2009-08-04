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
from pysollib.hint import FreeCellSolverWrapper
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# *
# ************************************************************************

class Fan_Hint(CautiousDefaultHint):
    # FIXME: demo is not too clever in this game
    pass


# ************************************************************************
# * Fan
# ************************************************************************

class Fan(Game):
    Talon_Class = InitialDealTalonStack
    Foundation_Classes = [SS_FoundationStack]
    ReserveStack_Class = ReserveStack
    RowStack_Class = KingSS_RowStack
    Hint_Class = Fan_Hint

    #
    # game layout
    #

    def createGame(self, rows=(5,5,5,3), playcards=9, reserves=0, texts=False):
        # create layout
        l, s = Layout(self), self.s

        # set window
        # (set size so that at least 9 cards are fully playable)
        w = max(2*l.XS, l.XS+(playcards-1)*l.XOFFSET)
        w = min(3*l.XS, w)
        w = (w + 1) & ~1
        ##print 2*l.XS, w
        self.setSize(l.XM + max(rows)*w, l.YM + (1+len(rows))*l.YS)

        # create stacks
        decks = self.gameinfo.decks
        if reserves:
            x, y = l.XM, l.YM
            for r in range(reserves):
                s.reserves.append(self.ReserveStack_Class(x, y, self))
                x += l.XS
            x = (self.width - decks*4*l.XS) # - 2*l.XS) / 2
            dx = l.XS
        else:
            dx = (self.width - decks*4*l.XS)/(decks*4+1)
            x, y = l.XM + dx, l.YM
            dx += l.XS
        for fnd_cls in self.Foundation_Classes:
            for i in range(4):
                s.foundations.append(fnd_cls(x, y, self, suit=i))
                x += dx
        for i in range(len(rows)):
            x, y = l.XM, y + l.YS
            for j in range(rows[i]):
                stack = self.RowStack_Class(x, y, self, max_move=1, max_accept=1)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                x += w
        x, y = self.width - l.XS, self.height - l.YS
        s.talon = self.Talon_Class(x, y, self)
        if texts:
            l.createRoundText(s.talon, 'nn')

        # define stack-groups
        l.defaultStackGroups()
        return l

    #
    # game overrides
    #

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(rows=self.s.rows[:17], frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_SS

    def getHighlightPilesStacks(self):
        return ()


class FanGame(Fan):
    Solver_Class = FreeCellSolverWrapper(preset='fan')


# ************************************************************************
# * Scotch Patience
# ************************************************************************

class ScotchPatience(Fan):
    Foundation_Classes = [AC_FoundationStack]
    RowStack_Class = StackWrapper(RK_RowStack, base_rank=NO_RANK)
    def createGame(self):
        Fan.createGame(self, playcards=8)
    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Shamrocks
# * Shamrocks II
# ************************************************************************

class Shamrocks(Fan):
    RowStack_Class = StackWrapper(UD_RK_RowStack, base_rank=NO_RANK, max_cards=3)
    def createGame(self):
        Fan.createGame(self, playcards=4)
    shallHighlightMatch = Game._shallHighlightMatch_RK

class ShamrocksII(Shamrocks):
    def _shuffleHook(self, cards):
        # move Kings to bottom of each stack
        i, n = 0, 17
        kings = []
        for c in cards:
            if c.rank == KING:
                kings.append(i)
            i += 1
        for i in kings:
            if i == 51:
                continue
            j = i % n
            while j < i:
                if cards[j].rank != KING:
                    cards[i], cards[j] = cards[j], cards[i]
                    break
                j += n
        cards.reverse()
        return cards


# ************************************************************************
# * La Belle Lucie (Midnight Oil)
# ************************************************************************

class LaBelleLucie_Talon(TalonStack):
    def canDealCards(self):
        return self.round != self.max_rounds and not self.game.isGameWon()

    def dealCards(self, sound=False):
        n = self.redealCards1()
        if n == 0:
            return 0
        self.redealCards2()
        if sound:
            self.game.startDealSample()
        self.redealCards3()
        if sound:
            self.game.stopSamples()
        return n

    # redeal step 1) - collect all cards, move them to the Talon
    def redealCards1(self):
        assert len(self.cards) == 0
        num_cards = 0
        for r in self.game.s.rows:
            if r.cards:
                num_cards = num_cards + len(r.cards)
                self.game.moveMove(len(r.cards), r, self, frames=0)
        assert len(self.cards) == num_cards
        return num_cards

    # redeal step 2) - shuffle
    def redealCards2(self):
        assert self.round != self.max_rounds
        assert self.cards
        self.game.shuffleStackMove(self)
        self.game.nextRoundMove(self)

    # redeal step 3) - redeal cards to stacks
    def redealCards3(self, face_up=1):
        # deal 3 cards to each row, and 1-3 cards to last row
        to_stacks = self.game.s.rows
        n = min(len(self.cards), 3*len(to_stacks))
        for i in range(3):
            j = (n/3, (n+1)/3, (n+2)/3) [i]
            frames = (0, 0, 4) [i]
            for r in to_stacks[:j]:
                if self.cards[-1].face_up != face_up:
                    self.game.flipMove(self)
                self.game.moveMove(1, self, r, frames=frames)


class LaBelleLucie(Fan):
    Talon_Class = StackWrapper(LaBelleLucie_Talon, max_rounds=3)
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=NO_RANK)
    def createGame(self):
        return Fan.createGame(self, texts=True)


# ************************************************************************
# * Super Flower Garden
# ************************************************************************

class SuperFlowerGarden(LaBelleLucie):
    RowStack_Class = StackWrapper(RK_RowStack, base_rank=NO_RANK)
    shallHighlightMatch = Game._shallHighlightMatch_RK


# ************************************************************************
# * Three Shuffles and a Draw
# ************************************************************************

class ThreeShufflesAndADraw_RowStack(SS_RowStack):
    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game, r = self.game, self.game.s.reserves[0]
        if to_stack is not r:
            SS_RowStack.moveMove(self, ncards, to_stack, frames=frames, shadow=shadow)
            return
        f = self._canDrawCard()
        assert f and game.draw_done == 0 and ncards == 1
        # 1) top card from self to reserve
        game.updateStackMove(r, 2|16)       # update view for undo
        game.moveMove(1, self, r, frames=frames, shadow=shadow)
        game.updateStackMove(r, 3|64)       # update model
        game.updateStackMove(r, 1|16)       # update view for redo
        # 2) second card from self to foundation/row
        if 1 or not game.demo:
            game.playSample("drop", priority=200)
        if frames == 0:
            frames = -1
        game.moveMove(1, self, f, frames=frames, shadow=shadow)
        # 3) from reserve back to self
        #    (need S_FILL because the move is normally not valid)
        old_state = game.enterState(game.S_FILL)
        game.moveMove(1, r, self, frames=frames, shadow=shadow)
        game.leaveState(old_state)

    def _canDrawCard(self):
        if len(self.cards) >= 2:
            pile = self.cards[-2:-1]
            for s in self.game.s.foundations + self.game.s.rows:
                if s is not self and s.acceptsCards(self, pile):
                    return s
        return None


class ThreeShufflesAndADraw_ReserveStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        if not from_stack in self.game.s.rows:
            return False
        if self.game.draw_done or not from_stack._canDrawCard():
            return False
        return True

    def updateModel(self, undo, flags):
        assert undo == self.game.draw_done
        self.game.draw_done = not self.game.draw_done

    def updateText(self):
        if self.game.preview > 1 or self.texts.misc is None:
            return
        t = (_("X"), _("Draw")) [self.game.draw_done == 0]
        self.texts.misc.config(text=t)

    def prepareView(self):
        ReserveStack.prepareView(self)
        if not self.is_visible or self.game.preview > 1:
            return
        images = self.game.app.images
        x, y = self.x + images.CARDW/2, self.y + images.CARDH/2
        self.texts.misc = MfxCanvasText(self.game.canvas, x, y,
                                        anchor="center",
                                        font=self.game.app.getFont("canvas_default"))


class ThreeShufflesAndADraw(LaBelleLucie):
    RowStack_Class = StackWrapper(ThreeShufflesAndADraw_RowStack, base_rank=NO_RANK)

    def createGame(self):
        l = LaBelleLucie.createGame(self)
        s = self.s
        # add a reserve stack
        x, y = s.rows[3].x, s.rows[-1].y
        s.reserves.append(ThreeShufflesAndADraw_ReserveStack(x, y, self))
        # redefine the stack-groups
        l.defaultStackGroups()
        # extra settings
        self.draw_done = 0

    def startGame(self):
        self.draw_done = 0
        self.s.reserves[0].updateText()
        LaBelleLucie.startGame(self)

    def _restoreGameHook(self, game):
        self.draw_done = game.loadinfo.draw_done

    def _loadGameHook(self, p):
        self.loadinfo.addattr(draw_done=p.load())

    def _saveGameHook(self, p):
        p.dump(self.draw_done)


# ************************************************************************
# * Trefoil
# ************************************************************************

class Trefoil(LaBelleLucie):
    GAME_VERSION = 2
    Foundation_Classes = [StackWrapper(SS_FoundationStack, min_cards=1)]

    def createGame(self):
        return Fan.createGame(self, rows=(5,5,5,1), texts=True)

    def _shuffleHook(self, cards):
        # move Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)


# ************************************************************************
# * Intelligence
# ************************************************************************

class Intelligence_Talon(LaBelleLucie_Talon):
    # all Aces go to Foundations
    dealToStacks = TalonStack.dealToStacksOrFoundations

    # redeal step 1) - collect all cards, move them to the Talon (face down)
    def redealCards1(self):
        assert len(self.cards) == 0
        r = self.game.s.reserves[0]
        num_cards = len(r.cards)
        if num_cards > 0:
            self.game.moveMove(len(r.cards), r, self, frames=0)
        for r in self.game.s.rows:
            num_cards = num_cards + len(r.cards)
            while r.cards:
                self.game.moveMove(1, r, self, frames=0)
                self.game.flipMove(self)
        assert len(self.cards) == num_cards
        return num_cards

    # redeal step 3) - redeal cards to stacks
    def redealCards3(self, face_up=1):
        for r in self.game.s.rows:
            while len(r.cards) < 3:
                self.dealToStacks([r], frames=4)
                if not self.cards:
                    return
        # move all remaining cards to the reserve
        self.game.moveMove(len(self.cards), self, self.game.s.reserves[0], frames=0)


# up or down in suit
class Intelligence_RowStack(UD_SS_RowStack):
    def fillStack(self):
        if not self.cards:
            r = self.game.s.reserves[0]
            if r.cards:
                r.dealRow((self,self,self), sound=True)


class Intelligence_ReserveStack(ReserveStack, DealRow_StackMethods):
    # all Aces go to Foundations (used in r.dealRow() above)
    dealToStacks = DealRow_StackMethods.dealToStacksOrFoundations

    def canFlipCard(self):
        return False


class Intelligence(Fan):

    Foundation_Classes = [SS_FoundationStack, SS_FoundationStack]
    Talon_Class = StackWrapper(Intelligence_Talon, max_rounds=3)
    RowStack_Class = StackWrapper(Intelligence_RowStack, base_rank=NO_RANK)

    def createGame(self, rows=(5,5,5,3)):
        l = Fan.createGame(self, rows)
        s = self.s
        # add a reserve stack
        x, y = s.talon.x - l.XS, s.talon.y
        s.reserves.append(Intelligence_ReserveStack(x, y, self, max_move=0, max_accept=0, max_cards=UNLIMITED_CARDS))
        l.createText(s.reserves[0], "sw")
        l.createRoundText(s.talon, 'nn')
        # redefine the stack-groups
        l.defaultStackGroups()

    def startGame(self):
        talon = self.s.talon
        for i in range(2):
            talon.dealRow(frames=0)
        self.startDealSample()
        talon.dealRow()
        # move all remaining cards to the reserve
        self.moveMove(len(talon.cards), talon, self.s.reserves[0], frames=0)


class IntelligencePlus(Intelligence):
    def createGame(self):
        Intelligence.createGame(self, rows=(5,5,5,4))


# ************************************************************************
# * House in the Wood
# * House on the Hill
# *   (2 decks variants of Fan)
# ************************************************************************

class HouseInTheWood(Fan):
    Foundation_Classes = [SS_FoundationStack, SS_FoundationStack]
    RowStack_Class = StackWrapper(UD_SS_RowStack, base_rank=NO_RANK)

    def createGame(self):
        Fan.createGame(self, rows=(6,6,6,6,6,5))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.rows[:34], frames=0)
        self.s.talon.dealRow(rows=self.s.rows[:35], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:35])


class HouseOnTheHill(HouseInTheWood):
    Foundation_Classes = [SS_FoundationStack,
                          StackWrapper(SS_FoundationStack, base_rank=KING, dir=-1)]


# ************************************************************************
# * Clover Leaf
# ************************************************************************

class CloverLeaf_RowStack(UD_SS_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not UD_SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return cards[0].rank in (ACE, KING)
        return True
    def _getBaseCard(self):
        return _('Base card - Ace or King.')


class CloverLeaf(Game):

    Hint_Class = Fan_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        playcards = 7
        w, h = l.XM+l.XS+4*(l.XS+(playcards-1)*l.XOFFSET), l.YM+4*l.YS
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(2):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            y += l.YS
        for i in range(2):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i+2,
                                                    base_rank=KING, dir=-1))
            y += l.YS

        x = l.XM+l.XS
        for i in range(4):
            y = l.YM
            for j in range(4):
                stack = CloverLeaf_RowStack(x, y, self,
                                            max_move=1, max_accept=1)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                y += l.YS
            x += l.XS+(playcards-1)*l.XOFFSET

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToBottom(cards,
                   lambda c: ((c.rank == ACE and c.suit in (0,1)) or
                              (c.rank == KING and c.suit in (2,3)),
                              c.suit))

    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Free Fan
# ************************************************************************

class FreeFan(Fan):
    RowStack_Class = FullStackWrapper(SuperMoveSS_RowStack, base_rank=KING)
    Solver_Class = FreeCellSolverWrapper(esf='kings', sbb='suit')
    def createGame(self):
        Fan.createGame(self, reserves=2, playcards=8)


# ************************************************************************
# * Box Fan
# ************************************************************************

class BoxFan(Fan):

    RowStack_Class = KingAC_RowStack
    Solver_Class = FreeCellSolverWrapper(esf='kings')

    def createGame(self):
        Fan.createGame(self, rows=(4,4,4,4))

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    def _shuffleHook(self, cards):
        # move Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards, lambda c: (c.rank == 0, c.suit))

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Troika
# ************************************************************************

class Troika(Fan):

    RowStack_Class = StackWrapper(RK_RowStack, dir=0,
                                  base_rank=NO_RANK, max_cards=3)

    def createGame(self):
        Fan.createGame(self, rows=(6, 6, 6), playcards=4)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank

    def startGame(self, ncards=3):
        self.startDealSample()
        for r in self.s.rows:
            for i in range(ncards):
                if not self.s.talon.cards:
                    break
                c = self.s.talon.cards[-1]
                t = r
                if c.rank == ACE:
                    t = self.s.foundations[c.suit]
                self.s.talon.dealRow(rows=[t], frames=4)


class Quads_RowStack(RK_RowStack):
    getBottomImage = Stack._getReserveBottomImage

class Quads(Troika):
    RowStack_Class = FullStackWrapper(Quads_RowStack, dir=0,
                                  ##base_rank=NO_RANK,
                                  max_cards=4)
    def createGame(self):
        Fan.createGame(self, rows=(5, 5, 3), playcards=5)

    def startGame(self):
        Troika.startGame(self, ncards=4)

class QuadsPlus(Quads):
    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(3):
            self.s.talon.dealRow(rows=self.s.rows[:-1], frames=0)
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:-1])


# ************************************************************************
# * Fascination Fan
# ************************************************************************

class FascinationFan_Talon(RedealTalonStack):
    def dealCards(self, sound=False):
        RedealTalonStack.redealCards(self, shuffle=True, sound=sound)

class FascinationFan(Fan):
    Talon_Class = StackWrapper(FascinationFan_Talon, max_rounds=7)
    #Talon_Class = StackWrapper(LaBelleLucie_Talon, max_rounds=7)
    RowStack_Class = StackWrapper(AC_RowStack, base_rank=NO_RANK)

    def createGame(self):
        Fan.createGame(self, texts=True)

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(rows=self.s.rows[:17], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def redealCards(self):
        r0 = r1 = len(self.s.talon.cards)/3
        m = len(self.s.talon.cards)%3
        if m >= 1: r1 += 1
        self.s.talon.dealRow(rows=self.s.rows[:r0], flip=0, frames=4)
        self.s.talon.dealRow(rows=self.s.rows[:r1], flip=0, frames=4)
        self.s.talon.dealRowAvail(frames=4)

    shallHighlightMatch = Game._shallHighlightMatch_AC


# ************************************************************************
# * Crescent
# ************************************************************************

class Crescent_Talon(RedealTalonStack):

    def dealCards(self, sound=False):
        old_state = self.game.enterState(self.game.S_DEAL)
        ncards = 0
        intern1, intern2 = self.game.s.internals
        if sound and self.game.app.opt.animations:
            self.game.startDealSample()
        for r in self.game.s.rows:
            if len(r.cards) <= 1:
                continue
            ncards += len(r.cards)
            # move cards to internal stacks
            while len(r.cards) != 1:
                self.game.moveMove(1, r, intern1, frames=4)
            self.game.moveMove(1, r, intern2, frames=4)
            # move back
            while intern1.cards:
                self.game.moveMove(1, intern1, r, frames=4)
            self.game.moveMove(1, intern2, r, frames=4)
        self.game.nextRoundMove(self)
        if sound:
            self.game.stopSamples()
        self.game.leaveState(old_state)
        return ncards


class Crescent(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):
        l, s = Layout(self), self.s
        playcards = 10
        w0 = l.XS+(playcards-1)*l.XOFFSET
        w, h = l.XM+max(4*w0, 9*l.XS), l.YM+5*l.YS
        self.setSize(w, h)
        x, y = l.XM, l.YM
        s.talon = Crescent_Talon(x, y, self, max_rounds=4)
        l.createRoundText(s.talon, 'ne')
        x, y = w-8*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                                    base_rank=KING, dir=-1))
            x += l.XS
        y = l.YM+l.YS
        for i in range(4):
            x = l.XM
            for j in range(4):
                stack = UD_SS_RowStack(x, y, self, base_rank=NO_RANK, mod=13)
                s.rows.append(stack)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                x += w0
            y += l.YS
        self.s.internals.append(InvisibleStack(self))
        self.s.internals.append(InvisibleStack(self))

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank in (ACE, KING) and c.deck == 0,
                              (c.rank, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(5):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_SSW


# ************************************************************************
# * School
# ************************************************************************

class School(Fan):

    Talon_Class = StackWrapper(LaBelleLucie_Talon, max_rounds=3)
    RowStack_Class = StackWrapper(RK_RowStack, dir=0, base_rank=NO_RANK)

    def createGame(self):
        Fan.createGame(self, rows=(4, 4, 4, 4), playcards=10, texts=True)

    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealRow(rows=self.s.foundations)

    def _shuffleHook(self, cards):
        # move Aces to bottom of the Talon (i.e. last cards to be dealt)
        return self._shuffleHookMoveToBottom(cards,
                                             lambda c: (c.rank == ACE, c.suit))

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank


# ************************************************************************
# * Forest Glade
# ************************************************************************

class ForestGlade_Talon(DealRowRedealTalonStack):

    def _redeal(self, rows=None, frames=0):
        # move all cards to the talon
        num_cards = 0
        if rows is None:
            rows = self.game.s.rows
        for r in rows:
            for i in range(len(r.cards)):
                num_cards += 1
                self.game.moveMove(1, r, self, frames=frames, shadow=0)
                if self.cards[-1].face_up:
                    self.game.flipMove(self)
        return num_cards

    def canDealCards(self):
        if self.round == self.max_rounds:
            if not self.cards:
                return False
            for r in self.game.s.rows:
                if not r.cards:
                    return True
            return False
        return True

    def dealCards(self, sound=False):
        rows = [r for r in self.game.s.rows if not r.cards]
        if not rows or not self.cards:
            if sound and self.game.app.opt.animations:
                self.game.startDealSample()
            # move all cards to the talon
            ncards = self._redeal(frames=4)
            # shuffle
            self.game.shuffleStackMove(self)
            # deal
            if self.cards:
                for r in self.game.s.rows:
                    for i in range(3):
                        if not self.cards:
                            break
                        ncards += self.dealRowAvail(rows=[r], frames=4)
            #
            self.game.nextRoundMove(self)
            if sound:
                self.game.stopSamples()
            return ncards
        #
        if sound and self.game.app.opt.animations:
            self.game.startDealSample()
        ncards = 0
        for r in rows:
            for i in range(3):
                if not self.cards:
                    break
                ncards += self.dealRowAvail(rows=[r], sound=False)
        if sound:
            self.game.stopSamples()
        return ncards


class ForestGlade(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s
        playcards = 7
        w0 = l.XS+(playcards-1)*l.XOFFSET
        w, h = l.XM + 3*w0 + 4*l.XS, l.YM+6*l.YS
        self.setSize(w, h)

        x1, x2 = l.XM, self.width - 2*l.XS
        for i in range(2):
            y = l.YM
            for j in range(4):
                s.foundations.append(SS_FoundationStack(x1, y, self,
                                     suit=j, dir=2, max_cards=7))
                s.foundations.append(SS_FoundationStack(x2, y, self,
                                     base_rank=1, suit=j, dir=2, max_cards=6))
                y += l.YS
            x1 += l.XS
            x2 += l.XS

        x, y = l.XM + 3*l.XS, l.YM
        for i in (0, 1):
            stack = SS_RowStack(x, y, self, max_move=1, base_rank=KING)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.rows.append(stack)
            x += w0
        y = l.YM+l.YS
        for i in range(4):
            x = l.XM + 2*l.XS
            for j in range(3):
                stack = SS_RowStack(x, y, self, max_move=1, base_rank=KING)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
                s.rows.append(stack)
                x += w0
            y += l.YS
        x, y = l.XM + 3*l.XS, l.YM + 5*l.YS
        for i in (0, 1):
            stack = SS_RowStack(x, y, self, max_move=1, base_rank=KING)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.rows.append(stack)
            x += w0

        x, y = l.XM, self.height - l.YS
        s.talon = ForestGlade_Talon(x, y, self, max_rounds=3)
        l.createText(s.talon, 'ne')
        l.createRoundText(s.talon, 'se')

        l.defaultStackGroups()


    def startGame(self):
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    shallHighlightMatch = Game._shallHighlightMatch_SS



# register the game
registerGame(GameInfo(56, FanGame, "Fan",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(87, ScotchPatience, "Scotch Patience",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(57, Shamrocks, "Shamrocks",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(901, LaBelleLucie, "La Belle Lucie",      # was: 32, 82
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL,
                      altnames=("Fair Lucy", "Midnight Oil") ))
registerGame(GameInfo(132, SuperFlowerGarden, "Super Flower Garden",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(128, ThreeShufflesAndADraw, "Three Shuffles and a Draw",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(88, Trefoil, "Trefoil",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(227, Intelligence, "Intelligence",
                      GI.GT_FAN_TYPE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(340, IntelligencePlus, "Intelligence +",
                      GI.GT_FAN_TYPE, 2, 2, GI.SL_BALANCED))
registerGame(GameInfo(268, HouseInTheWood, "House in the Wood",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(317, HouseOnTheHill, "House on the Hill",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 2, 0, GI.SL_MOSTLY_SKILL,
                      rules_filename='houseinthewood.html'))
registerGame(GameInfo(320, CloverLeaf, "Clover Leaf",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(347, FreeFan, "Free Fan",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(385, BoxFan, "Box Fan",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(516, Troika, "Troika",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(517, Quads, "Quads",
                      GI.GT_FAN_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(625, FascinationFan, "Fascination Fan",
                      GI.GT_FAN_TYPE, 1, 6, GI.SL_BALANCED,
                      altnames=('Demon Fan',) ))
registerGame(GameInfo(647, Crescent, "Crescent",
                      GI.GT_FAN_TYPE, 2, 3, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(714, ShamrocksII, "Shamrocks II",
                      GI.GT_FAN_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(719, School, "School",
                      GI.GT_FAN_TYPE, 1, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(739, ForestGlade, "Forest Glade",
                      GI.GT_FAN_TYPE, 2, 2, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(767, QuadsPlus, "Quads +",
                      GI.GT_FAN_TYPE | GI.GT_OPEN | GI.GT_ORIGINAL, 1, 0, GI.SL_MOSTLY_SKILL))

