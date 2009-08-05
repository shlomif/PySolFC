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

# ************************************************************************
# *
# ************************************************************************

class PictureGallery_Hint(AbstractHint):
    def computeHints(self):
        game = self.game

        # 1) try if we can drop a card (i.e. an Ace)
        for r in game.sg.dropstacks:
            t, n = r.canDropCards(game.s.foundations)
            if t and n == 1:
                c = r.getCard()
                assert t is not r and c
                assert c.rank == ACE
                if r in game.s.tableaux:
                    base_score = 90000 + (4 - r.cap.base_rank)
                else:
                    base_score = 90000
                score = base_score + 100 * (self.K - c.rank)
                self.addHint(score, 1, r, t)

        # 2) try if we can move a card to the tableaux
        if not self.hints:
            for r in game.sg.dropstacks:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                if r in game.s.tableaux:
                    rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                    if rr.acceptsCards(None, pile):
                        # do not move a card that is already in correct place
                        continue
                    base_score = 80000 + (4 - r.cap.base_rank)
                else:
                    base_score = 80000
                # find a stack that would accept this card
                for t in game.s.tableaux:
                    if t is not r and t.acceptsCards(r, pile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 3) Try if we can move a card from the tableaux
        #    to a row stack. This can only happen if there are
        #    no more cards to deal.
        if not self.hints:
            for r in game.s.tableaux:
                pile = r.getPile()
                if not pile or len(pile) != 1:
                    continue
                rr = self.ClonedStack(r, stackcards=r.cards[:-1])
                if rr.acceptsCards(None, pile):
                    # do not move a card that is already in correct place
                    continue
                # find a stack that would accept this card
                for t in game.s.rows:
                    if t is not r and t.acceptsCards(r, pile):
                        score = 70000 + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 4) try if we can move a card within the row stacks
        if not self.hints:
            for r in game.s.rows:
                pile = r.getPile()
                if not pile:
                    continue
                lp = len(pile)
                lr = len(r.cards)
                assert 1 <= lp <= lr
                rpile = r.cards[ : (lr-lp) ]   # remaining pile
                if not pile or len(pile) != 1 or len(pile) == len(r.cards):
                    continue
                base_score = 60000
                # find a stack that would accept this card
                for t in game.s.rows:
                    if self.shallMovePile(r, t, pile, rpile):
                        score = base_score + 100 * (self.K - pile[0].rank)
                        self.addHint(score, 1, r, t)
                        break

        # 5) try if we can deal cards
        if self.level >= 2:
            if game.canDealCards():
                self.addHint(self.SCORE_DEAL, 0, game.s.talon, None)


# ************************************************************************
# * Picture Gallery
# ************************************************************************

# this Foundation only accepts Aces
class PictureGallery_Foundation(RK_FoundationStack):
    def __init__(self, x, y, game):
        RK_FoundationStack.__init__(self, x, y, game, base_rank=ACE, dir=0, max_move=0, max_cards=8)
        self.CARD_YOFFSET = min(30, self.game.app.images.CARD_YOFFSET + 10)

    def getBottomImage(self):
        return self.game.app.images.getLetter(ACE)

    def closeStack(self):
        if len(self.cards) == 8:
            if self.game.moves.state not in (self.game.S_REDO, self.game.S_RESTORE):
                self.game.flipAllMove(self)

    def canFlipCard(self):
        return False


class PictureGallery_TableauStack(SS_RowStack):
    def __init__(self, x, y, game, base_rank, yoffset, dir=3, max_cards=4):
        SS_RowStack.__init__(self, x, y, game,
            base_rank=base_rank, dir=dir, max_cards=max_cards, max_accept=1)
        self.CARD_YOFFSET = yoffset

    def acceptsCards(self, from_stack, cards):
        if not SS_RowStack.acceptsCards(self, from_stack, cards):
            return False
        # check that the base card is correct
        if self.cards and self.cards[0].rank != self.cap.base_rank:
            return False
        return True

    getBottomImage = Stack._getLetterImage


class PictureGallery_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        # check
        if self.cards or self.game.s.talon.cards:
            return False
        return True

    getBottomImage = Stack._getTalonBottomImage


# ************************************************************************
# *
# ************************************************************************

class PictureGallery(Game):
    Hint_Class = PictureGallery_Hint

    Foundation_Class = PictureGallery_Foundation
    TableauStack_Classes = [
        StackWrapper(PictureGallery_TableauStack, base_rank=3, max_cards=4, dir=3),
        StackWrapper(PictureGallery_TableauStack, base_rank=2, max_cards=4, dir=3),
        StackWrapper(PictureGallery_TableauStack, base_rank=1, max_cards=4, dir=3),
        ]
    RowStack_Class = StackWrapper(PictureGallery_RowStack, max_accept=1)
    Talon_Class = DealRowTalonStack

    #
    # game layout
    #

    def createGame(self, waste=False):
        rows = len(self.TableauStack_Classes)
        # create layout
        l, s = Layout(self), self.s
        TABLEAU_YOFFSET = min(9, max(3, l.YOFFSET / 3))

        # set window
        th = l.YS + (12/rows-1) * TABLEAU_YOFFSET
        # (set piles so that at least 2/3 of a card is visible with 10 cards)
        h = (10-1)*l.YOFFSET + l.CH*2/3
        self.setSize(10*l.XS+l.XM, l.YM + 3*th + l.YM + h)

        # create stacks
        s.addattr(tableaux=[])     # register extra stack variable
        x = l.XM + 8 * l.XS + l.XS / 2
        y = l.YM + l.CH / 2
        s.foundations.append(self.Foundation_Class(x, y, self))
        y = l.YM
        for cl in self.TableauStack_Classes:
            x = l.XM
            for j in range(8):
                s.tableaux.append(cl(x, y, self, yoffset=TABLEAU_YOFFSET))
                x = x + l.XS
            y = y + th
        x, y = l.XM, y + l.YM
        for i in range(8):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS
        ##self.setRegion(s.rows, (-999, -999, x - l.CW / 2, 999999))
        x = l.XM + 8 * l.XS + l.XS / 2
        y = self.height - l.YS
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, "se")
        if waste:
            y -= l.YS
            s.waste = WasteStack(x, y, self)
            l.createText(s.waste, "se")
        self.setRegion(s.foundations, (x - l.CW / 2, -999, 999999, y - l.CH))

        # define stack-groups
        if waste:
            ws = [s.waste]
        else:
            ws = []
        self.sg.openstacks = s.foundations + s.tableaux + s.rows + ws
        self.sg.talonstacks = [s.talon] + ws
        self.sg.dropstacks = s.tableaux + s.rows + ws


    #
    # game overrides
    #

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.tableaux, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != 8:
            return False
        for stack in self.s.tableaux:
            if len(stack.cards) != 4:
                return False
        return True

    def fillStack(self, stack):
        if self.s.talon.cards:
            if stack in self.s.rows and len(stack.cards) == 0:
                self.s.talon.dealRow(rows=[stack])

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if card1.rank == ACE or card2.rank == ACE:
            return False
        return (card1.suit == card2.suit and
                (card1.rank + 3 == card2.rank or card2.rank + 3 == card1.rank))

    def getHighlightPilesStacks(self):
        return ()



# ************************************************************************
# * Great Wheel
# ************************************************************************

class GreatWheel_Hint(PictureGallery_Hint):
    shallMovePile = PictureGallery_Hint._cautiousShallMovePile


class GreatWheel_Foundation(PictureGallery_Foundation):
    def acceptsCards(self, from_stack, cards):
        if not PictureGallery_Foundation.acceptsCards(self, from_stack, cards):
            return False
        if self.cards and self.cards[-1].color == cards[0].color:
            return False
        return True


class GreatWheel_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if self.game.s.talon.cards:
            return False
        if not self.cards:
            return True
        c1, c2 = self.cards[-1], cards[0]
        return c1.suit == c2.suit and c1.rank == c2.rank+1

    getBottomImage = Stack._getTalonBottomImage


class GreatWheel(PictureGallery):

    Hint_Class = GreatWheel_Hint
    Foundation_Class = GreatWheel_Foundation
    TableauStack_Classes = [
        StackWrapper(PictureGallery_TableauStack, base_rank=2, max_cards=5, dir=2),
        StackWrapper(PictureGallery_TableauStack, base_rank=1, max_cards=6, dir=2),
        ]
    RowStack_Class = StackWrapper(GreatWheel_RowStack, max_accept=1)
    Talon_Class = StackWrapper(WasteTalonStack, max_rounds=1)

    def createGame(self):
        PictureGallery.createGame(self, waste=True)

    def fillStack(self, stack):
        if stack is self.s.waste and not stack.cards :
            self.s.talon.dealCards()
        if self.s.talon.cards or self.s.waste.cards:
            if stack in self.s.rows and len(stack.cards) == 0:
                old_state = self.enterState(self.S_FILL)
                for i in range(4):
                    if not self.s.waste.cards:
                        self.s.talon.dealCards()
                    if self.s.waste.cards:
                        self.s.waste.moveMove(1, stack)
                self.leaveState(old_state)

    def startGame(self):
        self.startDealSample()
        for i in range(4):
            self.s.talon.dealRow()
        self.s.talon.dealCards()


    def isGameWon(self):
        if len(self.s.foundations[0].cards) != 8:
            return False
        if self.s.talon.cards or self.s.waste.cards:
            return False
        for stack in self.s.rows:
            if stack.cards:
                return False
        return True


    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        if card1.rank == ACE or card2.rank == ACE:
            return False
        return (card1.suit == card2.suit and
                (card1.rank + 2 == card2.rank or card2.rank + 2 == card1.rank))

# ************************************************************************
# * Mount Olympus
# * Zeus
# ************************************************************************

class MountOlympus_Foundation(SS_FoundationStack):
    def getHelp(self):
        return 'Build up in suit by twos.'


class MountOlympus_RowStack(SS_RowStack):
    def getHelp(self):
        return 'Build down in suit by twos.'


class MountOlympus(Game):
    RowStack_Class = MountOlympus_RowStack

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM+9*l.XS, l.YM+3*l.YS+12*l.YOFFSET)

        # create stacks
        x, y = l.XM+l.XS, l.YM
        for i in range(8):
            s.foundations.append(MountOlympus_Foundation(x, y, self,
                                 suit=i/2, base_rank=ACE, dir=2, max_move=0, max_cards=7))
            x += l.XS
        x, y = l.XM+l.XS, l.YM+l.YS
        for i in range(8):
            s.foundations.append(MountOlympus_Foundation(x, y, self,
                                 suit=i/2, base_rank=1, dir=2, max_move=0, max_cards=6))
            x += l.XS
        x, y = l.XM, l.YM+2*l.YS
        for i in range(9):
            s.rows.append(self.RowStack_Class(x, y, self, dir=-2))
            x += l.XS
        s.talon=DealRowTalonStack(l.XM, l.YM, self)
        l.createText(s.talon, 's')

        # define stack-groups
        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
            lambda c: (c.rank in (ACE, 1),  (c.rank, c.suit)))


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealRow()


    def fillStack(self, stack):
        if self.s.talon.cards:
            if stack in self.s.rows and len(stack.cards) == 0:
                self.s.talon.dealRow(rows=[stack])


    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 2 == card2.rank or card2.rank + 2 == card1.rank))


class Zeus_RowStack(MountOlympus_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not MountOlympus_RowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return cards[0].rank in (QUEEN, KING)
        return True

class Zeus(MountOlympus):
    RowStack_Class = Zeus_RowStack
    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        for i in range(4):
            self.s.talon.dealRow()


# ************************************************************************
# * Royal Parade
# ************************************************************************


class RoyalParade_TableauStack(PictureGallery_TableauStack):

    def _canSwapPair(self, from_stack):
        if from_stack not in self.game.s.tableaux:
            return False
        if len(self.cards) != 1 or len(from_stack.cards) != 1:
            return False
        c0, c1 = from_stack.cards[0], self.cards[0]
        return (c0.rank == self.cap.base_rank and
                c1.rank == from_stack.cap.base_rank)

    def acceptsCards(self, from_stack, cards):
        if self._canSwapPair(from_stack):
            return True
        return PictureGallery_TableauStack.acceptsCards(self, from_stack, cards)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if self._canSwapPair(to_stack):
            self._swapPairMove(ncards, to_stack, frames=-1, shadow=0)
        else:
            PictureGallery_TableauStack.moveMove(self, ncards, to_stack,
                                                 frames=frames, shadow=shadow)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=frames, shadow=shadow)
        game.moveMove(n, swap, other_stack, frames=0)
        game.leaveState(old_state)


class RoyalParade(PictureGallery):
    Talon_Class = DealRowTalonStack
    TableauStack_Classes = [
        StackWrapper(RoyalParade_TableauStack,
                     base_rank=1, max_cards=4, dir=3),
        StackWrapper(RoyalParade_TableauStack,
                     base_rank=2, max_cards=4, dir=3),
        StackWrapper(RoyalParade_TableauStack,
                     base_rank=3, max_cards=4, dir=3),
        ]
    RowStack_Class = StackWrapper(BasicRowStack, max_accept=0)

    def createGame(self):
        PictureGallery.createGame(self)
        self.s.internals.append(InvisibleStack(self))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.tableaux)
        self.s.talon.dealRow()


# ************************************************************************
# * Virginia Reel
# ************************************************************************

class VirginiaReel_Talon(DealRowTalonStack):

    def canDealCards(self):
        if not DealRowTalonStack.canDealCards(self):
            return False
        for s in self.game.s.tableaux:
            if not s.cards:
                return False
        return True


class VirginiaReel(RoyalParade):
    Talon_Class = VirginiaReel_Talon

    def _shuffleHook(self, cards):
        bottom_cards = []
        ranks = []
        for c in cards[:]:
            if c.rank in (1,2,3) and c.rank not in ranks:
                ranks.append(c.rank)
                cards.remove(c)
                bottom_cards.append(c)
            if len(ranks) == 3:
                break
        bottom_cards.sort(lambda a, b: cmp(b.rank, a.rank))
        return cards+bottom_cards

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.tableaux[0::8], frames=0)
        self.startDealSample()
        for i in range(3):
            rows = self.s.tableaux[i*8+1:i*8+8]
            self.s.talon.dealRow(rows=rows)
        self.s.talon.dealRow()

    def fillStack(self, stack):
        pass



# register the game
registerGame(GameInfo(7, PictureGallery, "Picture Gallery",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED,
                      altnames=("Die Bildgallerie", "Mod-3") ))
registerGame(GameInfo(397, GreatWheel, "Great Wheel",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED,
                      ranks=range(12) # without Kings
                      ))
registerGame(GameInfo(398, MountOlympus, "Mount Olympus",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(399, Zeus, "Zeus",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(546, RoyalParade, "Royal Parade",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL,
                      rules_filename='virginiareel.html'))
registerGame(GameInfo(547, VirginiaReel, "Virginia Reel",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_MOSTLY_SKILL))


