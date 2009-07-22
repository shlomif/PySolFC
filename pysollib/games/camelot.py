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

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

from numerica import Numerica_Hint


# ************************************************************************
# * Camelot
# ************************************************************************

class Camelot_Hint(AbstractHint):

    def computeHints(self):
        game = self.game
        if game.is_fill:
            nhints = 0
            i = 0
            for r in game.s.rows:
                i += 1
                if not r.cards:
                    continue
                if r.cards[0].rank == 9:
                    self.addHint(5000, 1, r, game.s.foundations[0])
                    nhints += 1
                    continue
                for t in game.s.rows[i:]:
                    if t.acceptsCards(r, [r.cards[0]]):
                        self.addHint(5000, 1, r, t)
                        nhints += 1
            if nhints:
                return
        if game.s.talon.cards:
            for r in game.s.rows:
                if r.acceptsCards(game.s.talon, [game.s.talon.cards[-1]]):
                    self.addHint(5000, 1, game.s.talon, r)


class Camelot_RowStack(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if from_stack is self.game.s.talon:
            if len(self.cards) > 0:
                return False
            cr = cards[0].rank
            if cr == KING:
                return self.id in (0, 3, 12, 15)
            elif cr == QUEEN:
                return self.id in (1, 2, 13, 14)
            elif cr == JACK:
                return self.id in (4, 7, 8, 11)
            return True
        else:
            if len(self.cards) == 0:
                return False
            return self.cards[-1].rank + cards[0].rank == 8

    def canMoveCards(self, cards):
        if not self.game.is_fill:
            return False
        return cards[0].rank not in (KING, QUEEN, JACK)

    def clickHandler(self, event):
        game = self.game
        if game.is_fill and self.cards and self.cards[0].rank == 9:
            game.playSample("autodrop", priority=20)
            self.playMoveMove(1, game.s.foundations[0], sound=False)
            self.fillStack()
            return True
        return False

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if not to_stack is self.game.s.foundations[0]:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            ReserveStack.moveMove(self, ncards, to_stack, frames=frames, shadow=shadow)

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2|16)            # for undo
        if not game.demo:
            game.playSample("droppair", priority=200)
        game.moveMove(n, self, f, frames=frames, shadow=shadow)
        game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.fillStack()
        other_stack.fillStack()
        game.updateStackMove(game.s.talon, 1|16)            # for redo
        game.leaveState(old_state)


class Camelot_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        return True


class Camelot_Talon(OpenTalonStack):
    def fillStack(self):
        old_state = self.game.enterState(self.game.S_FILL)
        self.game.saveStateMove(2|16)            # for undo
        self.game.is_fill = self.game.isRowsFill()
        self.game.saveStateMove(1|16)            # for redo
        self.game.leaveState(old_state)
        OpenTalonStack.fillStack(self)


class Camelot(Game):

    Talon_Class = Camelot_Talon
    RowStack_Class = StackWrapper(Camelot_RowStack, max_move=0)
    Hint_Class = Camelot_Hint

    # game variables
    is_fill = False

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        # set window
        w = l.XS
        self.setSize(l.XM + w + 4*l.XS + w + l.XS, l.YM + 4*l.YS)
        # create stacks
        for i in range(4):
            for j in range(4):
                k = i+j*4
                x, y = l.XM + w + j*l.XS, l.YM + i*l.YS
                s.rows.append(self.RowStack_Class(x, y, self))
        x, y = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, 's')
        x, y = l.XM + w + 4*l.XS + w, l.YM
        s.foundations.append(Camelot_Foundation(x, y, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_accept=0, max_move=0, max_cards=52))
        l.createText(s.foundations[0], 's')
        # define stack-groups
        l.defaultStackGroups()
        return l

    #
    # game overrides
    #

    def startGame(self):
        self.is_fill = False
        self.s.talon.fillStack()


    def isGameWon(self):
        for i in (5, 6, 9, 10):
            if len(self.s.rows[i].cards) != 0:
                return False
        return len(self.s.talon.cards) == 0


    def isRowsFill(self):
        for i in range(16):
            if len(self.s.rows[i].cards) == 0:
                return False
        return True

    def _restoreGameHook(self, game):
        self.is_fill = game.loadinfo.is_fill

    def _loadGameHook(self, p):
        self.loadinfo.addattr(is_fill=p.load())

    def _saveGameHook(self, p):
        p.dump(self.is_fill)

    def getAutoStacks(self, event=None):
        return ((), (), ())

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.is_fill = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.is_fill]


# ************************************************************************
# * Sly Fox
# ************************************************************************

class SlyFox_Foundation(SS_FoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return False
        if from_stack in self.game.s.rows:
            if len(self.game.s.talon.cards) == 0:
                return True
            return self.game.num_dealled <= 0
        return True


class SlyFox_Talon(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        old_state = self.game.enterState(self.game.S_FILL)
        self.game.saveStateMove(2|16)            # for undo
        if old_state == self.game.S_PLAY and to_stack in self.game.s.rows:
            n = self.game.num_dealled
            if n < 0: n = 0
            self.game.num_dealled = (n+1)%20
        self.game.saveStateMove(1|16)            # for redo
        self.game.leaveState(old_state)
        OpenTalonStack.moveMove(self, ncards, to_stack, frames, shadow)


class SlyFox_RowStack(ReserveStack):
    def acceptsCards(self, from_stack, cards):
        if not ReserveStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack is self.game.s.talon


class SlyFox(Game):
    Hint_Class = Numerica_Hint

    num_dealled = -1

    def createGame(self):
        l, s = Layout(self), self.s
        self.setSize(l.XM+9*l.XS, l.YM+4*l.YS)

        x, y = l.XM, l.YM
        s.talon = SlyFox_Talon(x, y, self)
        s.waste = s.talon
        l.createText(s.talon, 'ne')
        tx, ty, ta, tf = l.getTextAttr(s.talon, "ss")
        font = self.app.getFont("canvas_default")
        self.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)

        y = l.YM
        for i in range(4):
            x = l.XM+1.5*l.XS
            for j in range(5):
                stack = SlyFox_RowStack(x, y, self, max_cards=UNLIMITED_CARDS)
                stack.CARD_YOFFSET = 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        x, y = self.width-2*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SlyFox_Foundation(x, y, self, suit=i))
            s.foundations.append(SlyFox_Foundation(x+l.XS, y, self, suit=i,
                                                   base_rank=KING, dir=-1))
            y += l.YS

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
           lambda c: (c.rank in (ACE, KING) and c.deck == 0, (c.suit, c.rank)))

    def startGame(self):
        self.num_dealled = -1
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.fillStack()

    def _restoreGameHook(self, game):
        self.num_dealled = game.loadinfo.num_dealled

    def _loadGameHook(self, p):
        self.loadinfo.addattr(num_dealled=p.load())

    def _saveGameHook(self, p):
        p.dump(self.num_dealled)

    def setState(self, state):
        # restore saved vars (from undo/redo)
        self.num_dealled = state[0]

    def getState(self):
        # save vars (for undo/redo)
        return [self.num_dealled]


    def fillStack(self, stack):
        if self.num_dealled == -1 and stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            self.s.talon.moveMove(1, stack)
            self.leaveState(old_state)


    def updateText(self):
        if self.preview > 1:
            return
        n = self.num_dealled
        if n < 0: n = 0
        text=str(n)+'/20'
        self.texts.misc.config(text=text)


class OpenSlyFox(SlyFox):

    def createGame(self):
        playcards = 6

        l, s = Layout(self), self.s
        self.setSize(l.XM+10*l.XS, l.YM+3*l.YS+2*playcards*l.YOFFSET+l.TEXT_HEIGHT)

        x, y = l.XM, l.YM
        s.talon = SlyFox_Talon(x, y, self)
        s.waste = s.talon
        l.createText(s.talon, 'ne')
        tx, ty, ta, tf = l.getTextAttr(s.talon, "ss")
        font = self.app.getFont("canvas_default")
        self.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)

        x += 2*l.XS
        for i in range(4):
            s.foundations.append(SlyFox_Foundation(x, y, self, suit=i))
            s.foundations.append(SlyFox_Foundation(x+4*l.XS, y, self, suit=i,
                                                   base_rank=KING, dir=-1))
            x += l.XS
        y = l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(2):
            x = l.XM
            for j in range(10):
                stack = SlyFox_RowStack(x, y, self, max_cards=UNLIMITED_CARDS)
                s.rows.append(stack)
                stack.CARD_YOFFSET = l.YOFFSET
                x += l.XS
            y += l.YS+playcards*l.YOFFSET

        l.defaultStackGroups()


# ************************************************************************
# * Princess Patience
# ************************************************************************

class PrincessPatience_RowStack(SS_RowStack):

    def canMoveCards(self, cards):
        if not SS_RowStack.canMoveCards(self, cards):
            return False
        ##index = list(self.game.s.rows).index(self) # don't work in demo-mode with cloned stack
        index = self.id
        col = index % 4
        row = index / 4
        if index < 16: # left
            for i in range(col+1, 4):
                r = self.game.s.rows[row*4+i]
                if r.cards:
                    return False
        else: # right
            for i in range(0, col):
                r = self.game.s.rows[row*4+i]
                if r.cards:
                    return False
        return True

    def acceptsCards(self, from_stack, cards):
        if not SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return from_stack is self.game.s.waste
        return True


class PrincessPatience(Game):
    Hint_Class = CautiousDefaultHint
    RowStack_Class = PrincessPatience_RowStack

    def createGame(self, max_rounds=1):

        l, s = Layout(self), self.s
        self.setSize(l.XM+11*l.XS, l.YM+5*l.YS)

        y = l.YM
        for i in range(4):
            x = l.XM
            for j in range(4):
                stack = self.RowStack_Class(x, y, self, max_move=1)
                s.rows.append(stack)
                stack.CARD_YOFFSET = 0
                x += l.XS
            y += l.YS
        y = l.YM
        for i in range(4):
            x = l.XM+7*l.XS
            for j in range(4):
                stack = self.RowStack_Class(x, y, self, max_move=1)
                s.rows.append(stack)
                stack.CARD_YOFFSET = 0
                x += l.XS
            y += l.YS

        x, y = l.XM+4.5*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            s.foundations.append(SS_FoundationStack(x+l.XS, y, self, suit=i))
            y += l.YS

        x, y = l.XM+4.5*l.XS, self.height-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds)
        l.createText(s.talon, 'sw')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'se')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    shallHighlightMatch = Game._shallHighlightMatch_SS


# ************************************************************************
# * Grandmamma's Patience
# ************************************************************************

class GrandmammasPatience_Talon(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler
    doubleclickHandler = OpenStack.doubleclickHandler


class GrandmammasPatience_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack not in self.game.s.rows


class GrandmammasPatience(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        h0 = l.YS+4*l.YOFFSET
        self.setSize(l.XM+11*l.XS, l.YM+2*l.YS+2*h0)
        self.base_rank = ANY_RANK

        x, y = l.XM, l.YM
        s.talon = GrandmammasPatience_Talon(x, y, self)
        l.createText(s.talon, 'ne')

        x, y = self.width-4*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 dir=-1, mod=13, max_move=0, base_rank=ANY_RANK))
            x += l.XS
        stack = s.foundations[0]
        tx, ty, ta, tf = l.getTextAttr(stack, "sw")
        font = self.app.getFont("canvas_default")
        stack.texts.misc = MfxCanvasText(self.canvas, tx, ty,
                                        anchor=ta, font=font)
        x, y = self.width-4*l.XS, self.height-l.YS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 mod=13, max_move=0, base_rank=ANY_RANK))
            x += l.XS
        stack = s.foundations[4]
        tx, ty, ta, tf = l.getTextAttr(stack, "sw")
        font = self.app.getFont("canvas_default")
        stack.texts.misc = MfxCanvasText(self.canvas,
                                        tx, ty, anchor=ta, font=font)

        y = l.YM+l.YS
        for i in range(2):
            x = l.XM
            for j in range(11):
                s.rows.append(GrandmammasPatience_RowStack(x, y, self,
                              max_accept=1, max_cards=2))
                x += l.XS
            y += h0

        x, y = l.XM, self.height-l.YS
        for i in range(4):
            s.reserves.append(ReserveStack(x, y, self))
            x += l.XS

        l.defaultStackGroups()
        self.sg.dropstacks.append(s.talon)


    def startGame(self):
        c = self.s.talon.cards[-1]
        self.base_rank = c.rank
        to_stack = self.s.foundations[c.suit]
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, to_stack, frames=0)
        for s in self.s.foundations[:4]:
            s.cap.base_rank = c.rank
        for s in self.s.foundations[4:]:
            s.cap.base_rank = (c.rank+1)%13
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.fillStack()


    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)

    def updateText(self):
        if self.preview > 1:
            return
        base_rank = self.base_rank
        if base_rank == ANY_RANK:
            t1 = t2 = ''
        else:
            t1 = RANKS[base_rank]+_(" Descending")
            t2 = RANKS[(base_rank+1)%13]+_(" Ascending")
        self.s.foundations[0].texts.misc.config(text=t1)
        self.s.foundations[4].texts.misc.config(text=t2)


    def _restoreGameHook(self, game):
        self.base_rank = game.loadinfo.base_rank
        for s in self.s.foundations[:4]:
            s.cap.base_rank = self.base_rank
        for s in self.s.foundations[4:]:
            s.cap.base_rank = (self.base_rank+1)%13

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_rank=None)    # register extra load var.
        self.loadinfo.base_rank = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_rank)



# ************************************************************************
# * Double Line
# ************************************************************************

class DoubleLine_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # this stack accepts any one card from the Waste pile
        return from_stack is self.game.s.waste

    def getHelp(self):
        return _('Tableau. Build regardless of rank and suit.')


class DoubleLine(Game):

    def createGame(self):

        l, s = Layout(self), self.s
        h0 = l.YS+3*l.YOFFSET
        self.setSize(l.XM+10*l.XS, l.YM+l.YS+l.TEXT_HEIGHT+2*h0)

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')

        x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i%4))
            x += l.XS
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i,
                                 base_rank=KING, dir=-1))
            x += l.XS

        y = l.YM+l.YS+l.TEXT_HEIGHT
        for i in range(2):
            x = l.XM
            for j in range(10):
                s.rows.append(DoubleLine_RowStack(x, y, self, max_cards=2,
                              max_move=1, max_accept=1, base_rank=NO_RANK))
                x += l.XS
            y += h0

        l.defaultStackGroups()

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)


# register the game
registerGame(GameInfo(280, Camelot, "Camelot",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_BALANCED))
registerGame(GameInfo(610, SlyFox, "Sly Fox",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(614, OpenSlyFox, "Open Sly Fox",
                      GI.GT_NUMERICA | GI.GT_ORIGINAL, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(623, PrincessPatience, "Princess Patience",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(622, GrandmammasPatience, "Grandmamma's Patience",
                      GI.GT_NUMERICA, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(702, DoubleLine, "Double Line",
                      GI.GT_NUMERICA, 2, 0, GI.SL_BALANCED))


