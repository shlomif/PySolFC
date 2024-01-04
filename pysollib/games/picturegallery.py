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
from pysollib.stack import \
        BasicRowStack, \
        DealRowTalonStack, \
        InvisibleStack, \
        RK_FoundationStack, \
        SS_FoundationStack, \
        SS_RowStack, \
        Stack, \
        StackWrapper, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ACE, KING, QUEEN

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
                rpile = r.cards[:(lr-lp)]   # remaining pile
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
        RK_FoundationStack.__init__(
            self, x, y, game, base_rank=ACE, dir=0, max_move=0,
            max_cards=(4 * game.gameinfo.decks))
        self.CARD_YOFFSET = min(30, self.game.app.images.CARD_YOFFSET + 10)

    def getBottomImage(self):
        return self.game.app.images.getLetter(ACE)

    def closeStack(self):
        if len(self.cards) == (4 * self.game.gameinfo.decks):
            if self.game.moves.state not in \
                    (self.game.S_REDO, self.game.S_RESTORE):
                self.game.flipAllMove(self)

    def canFlipCard(self):
        return False


class PictureGallery_TableauStack(SS_RowStack):
    max_accept = 1

    def __init__(self, x, y, game, base_rank, yoffset, dir=3, max_cards=4):
        SS_RowStack.__init__(
            self, x, y, game,
            base_rank=base_rank, dir=dir, max_cards=max_cards,
            max_accept=self.max_accept)
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
        StackWrapper(
            PictureGallery_TableauStack, base_rank=3, max_cards=4, dir=3),
        StackWrapper(
            PictureGallery_TableauStack, base_rank=2, max_cards=4, dir=3),
        StackWrapper(
            PictureGallery_TableauStack, base_rank=1, max_cards=4, dir=3),
        ]
    RowStack_Class = StackWrapper(PictureGallery_RowStack, max_accept=1)
    Talon_Class = DealRowTalonStack

    NORMAL_OFFSET = False

    #
    # game layout
    #

    def createGame(self, waste=False, numstacks=8):
        rows = len(self.TableauStack_Classes)
        # create layout
        l, s = Layout(self), self.s
        numtableau = (4 * self.gameinfo.decks)
        if not self.NORMAL_OFFSET:
            TABLEAU_YOFFSET = min(numtableau + 1, max(3, l.YOFFSET // 3))
        else:
            TABLEAU_YOFFSET = l.YOFFSET

        # set window
        th = l.YS + ((numtableau + 4) // rows - 1) * TABLEAU_YOFFSET
        if self.Foundation_Class is None and self.RowStack_Class is None:
            h = 0
        else:
            # (set piles so at least 2/3 of a card is visible with 10 cards)
            h = ((numtableau + 2) - 1) * l.YOFFSET + l.CH * 2 // 3
        self.setSize((numtableau + 2) * l.XS + l.XM, l.YM + 3 * th + l.YM + h)

        # create stacks
        s.addattr(tableaux=[])     # register extra stack variable
        x = l.XM + numtableau * l.XS + l.XS // 2
        y = l.YM + l.CH // 2
        if self.Foundation_Class is not None:
            s.foundations.append(self.Foundation_Class(x, y, self))
        y = l.YM
        for cl in self.TableauStack_Classes:
            x = l.XM
            for j in range(numtableau):
                s.tableaux.append(cl(x, y, self, yoffset=TABLEAU_YOFFSET))
                x = x + l.XS
            y = y + th
        if self.Foundation_Class is not None:
            self.setRegion(s.foundations, (x - l.CW // 2, -999, 999999,
                                           y - l.CH))
        x, y = l.XM, y + l.YM
        if self.RowStack_Class is not None:
            for i in range(numstacks):
                s.rows.append(self.RowStack_Class(x, y, self))
                x = x + l.XS
        # self.setRegion(s.rows, (-999, -999, x - l.CW // 2, 999999))
        x = l.XM + numstacks * l.XS + l.XS // 2
        y = self.height - l.YS
        if self.RowStack_Class is None and self.Foundation_Class is None:
            y = l.YM + l.YS + l.CH // 2
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, "se")
        if waste:
            y -= l.YS
            s.waste = WasteStack(x, y, self)
            l.createText(s.waste, "se")

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
        self._startAndDealRow()

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != (4 * self.gameinfo.decks):
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


class BigPictureGallery(PictureGallery):

    def createGame(self):
        PictureGallery.createGame(self, numstacks=12)


class HugePictureGallery(PictureGallery):

    def createGame(self):
        PictureGallery.createGame(self, numstacks=16)


# ************************************************************************
# * Great Wheel
# * Greater Wheel
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
        StackWrapper(
            PictureGallery_TableauStack, base_rank=2, max_cards=5, dir=2),
        StackWrapper(
            PictureGallery_TableauStack, base_rank=1, max_cards=6, dir=2),
        ]
    RowStack_Class = StackWrapper(GreatWheel_RowStack, max_accept=1)
    Talon_Class = StackWrapper(WasteTalonStack, max_rounds=1)

    def createGame(self):
        PictureGallery.createGame(self, waste=True, numstacks=8)

    def fillStack(self, stack):
        if stack is self.s.waste and not stack.cards:
            self.s.talon.dealCards()
        if self.s.talon.cards or self.s.waste.cards:
            if stack in self.s.rows and len(stack.cards) == 0:
                old_state = self.enterState(self.S_FILL)
                for i in range(2 + self.gameinfo.decks):
                    if not self.s.waste.cards:
                        self.s.talon.dealCards()
                    if self.s.waste.cards:
                        self.s.waste.moveMove(1, stack)
                self.leaveState(old_state)

    def startGame(self):
        for i in range(1 + self.gameinfo.decks):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()

    def isGameWon(self):
        if len(self.s.foundations[0].cards) != (4 * self.gameinfo.decks):
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


class GreaterWheel(GreatWheel):

    def createGame(self):
        PictureGallery.createGame(self, waste=True, numstacks=12)

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
            s.foundations.append(
                MountOlympus_Foundation(
                    x, y, self,
                    suit=i//2, base_rank=ACE, dir=2, max_move=0, max_cards=7))
            x += l.XS
        x, y = l.XM+l.XS, l.YM+l.YS
        for i in range(8):
            s.foundations.append(
                MountOlympus_Foundation(
                    x, y, self,
                    suit=i//2, base_rank=1, dir=2, max_move=0, max_cards=6))
            x += l.XS
        x, y = l.XM, l.YM+2*l.YS
        for i in range(9):
            s.rows.append(self.RowStack_Class(x, y, self, dir=-2))
            x += l.XS
        s.talon = DealRowTalonStack(l.XM, l.YM, self)
        l.createText(s.talon, 's')

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(
            cards,
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
# * Big Parade
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
        return PictureGallery_TableauStack.acceptsCards(
            self, from_stack, cards)

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

    def createGame(self, waste=False, numstacks=8):
        PictureGallery.createGame(self, waste=waste, numstacks=numstacks)
        self.s.internals.append(InvisibleStack(self))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.tableaux, frames=0)
        self.s.talon.dealRow()


class BigParade(RoyalParade):

    def createGame(self):
        RoyalParade.createGame(self, numstacks=12)


# ************************************************************************
# * Virginia Reel
# * Three Up
# * Blue Jacket
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
            if c.rank in (1, 2, 3) and c.rank not in ranks:
                ranks.append(c.rank)
                cards.remove(c)
                bottom_cards.append(c)
            if len(ranks) == 3:
                break
        bottom_cards.sort(key=lambda x: -x.rank)
        return cards+bottom_cards

    def startGame(self):
        numdeal = (4 * self.gameinfo.decks)
        self.s.talon.dealRow(rows=self.s.tableaux[0::numdeal], frames=0)
        self.startDealSample()
        for i in range(3):
            rows = self.s.tableaux[i*numdeal+1:i*numdeal+numdeal]
            self.s.talon.dealRow(rows=rows, frames=0)
        self.s.talon.dealRow()

    def fillStack(self, stack):
        pass


class ThreeUp(VirginiaReel):

    def createGame(self):
        VirginiaReel.createGame(self, numstacks=12)


class BlueJacket_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        return len(self.cards) == 0 and len(cards) == 1


class BlueJacket(VirginiaReel):
    RowStack_Class = StackWrapper(BlueJacket_RowStack, max_accept=1)


# ************************************************************************
# * Devil's Grip
# ************************************************************************

class DevilsGrip_TableauStack(RoyalParade_TableauStack):
    max_accept = 4

    def _canSwapPair(self, from_stack):
        if from_stack not in self.game.s.tableaux:
            return False
        if len(self.cards) == 0 or len(from_stack.cards) == 0:
            return False
        if self.cap.base_rank == from_stack.cap.base_rank:
            return False
        c0, c1 = from_stack.cards[0], self.cards[0]
        return (c0.rank != c1.rank and
                (c0.rank == self.cap.base_rank or
                 c1.rank == from_stack.cap.base_rank))

    def acceptsCards(self, from_stack, cards):
        if self._canSwapPair(from_stack):
            return True
        return SS_RowStack.acceptsCards(
            self, from_stack, cards)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(len(self.cards), self, swap, frames=0)
        game.moveMove(len(other_stack.cards), other_stack, self,
                      frames=frames, shadow=shadow)
        game.moveMove(len(swap.cards), swap, other_stack, frames=0)
        game.leaveState(old_state)


class DevilsGrip(RoyalParade):
    Foundation_Class = None
    RowStack_Class = None
    TableauStack_Classes = [
        StackWrapper(DevilsGrip_TableauStack,
                     base_rank=1, max_cards=4, dir=3),
        StackWrapper(DevilsGrip_TableauStack,
                     base_rank=2, max_cards=4, dir=3),
        StackWrapper(DevilsGrip_TableauStack,
                     base_rank=3, max_cards=4, dir=3),
        ]
    Talon_Class = StackWrapper(WasteTalonStack, max_rounds=1, num_deal=3)

    NORMAL_OFFSET = True

    def createGame(self):
        RoyalParade.createGame(self, waste=True, numstacks=8)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.tableaux, frames=0)
        self.s.talon.dealCards()

    def isGameWon(self):
        for stack in self.s.tableaux:
            if len(stack.cards) != 4 or \
                    stack.cards[0].rank != stack.cap.base_rank:
                return False
        return True

    def fillStack(self, stack):
        if not stack.cards and stack in self.s.tableaux:
            if self.s.waste.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.waste.moveMove(1, stack)
                self.leaveState(old_state)
            elif self.s.talon.cards:
                old_state = self.enterState(self.S_FILL)
                self.s.talon.moveMove(1, stack)
                self.leaveState(old_state)


# register the game
registerGame(GameInfo(7, PictureGallery, "Picture Gallery",
                      GI.GT_PICTURE_GALLERY, 2, 0, GI.SL_BALANCED,
                      altnames=("Die Bildgallerie", "Mod-3")))
registerGame(GameInfo(397, GreatWheel, "Great Wheel",
                      GI.GT_PICTURE_GALLERY | GI.GT_STRIPPED, 2, 0,
                      GI.SL_BALANCED, ranks=list(range(12))  # without Kings
                      ))
registerGame(GameInfo(398, MountOlympus, "Mount Olympus",
                      GI.GT_PICTURE_GALLERY, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(399, Zeus, "Zeus",
                      GI.GT_PICTURE_GALLERY, 2, 0, GI.SL_BALANCED))
registerGame(GameInfo(546, RoyalParade, "Royal Parade",
                      GI.GT_PICTURE_GALLERY, 2, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Hussars", "Financier")))
registerGame(GameInfo(547, VirginiaReel, "Virginia Reel",
                      GI.GT_PICTURE_GALLERY, 2, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(782, GreaterWheel, "Greater Wheel",
                      GI.GT_PICTURE_GALLERY | GI.GT_STRIPPED, 4, 0,
                      GI.SL_BALANCED, ranks=list(range(12))  # without Kings
                      ))
registerGame(GameInfo(803, BigParade, "Big Parade",
                      GI.GT_PICTURE_GALLERY, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(804, ThreeUp, "Three Up",
                      GI.GT_PICTURE_GALLERY, 3, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(927, BigPictureGallery, "Big Picture Gallery",
                      GI.GT_PICTURE_GALLERY, 3, 0, GI.SL_BALANCED))
registerGame(GameInfo(928, HugePictureGallery, "Huge Picture Gallery",
                      GI.GT_PICTURE_GALLERY, 4, 0, GI.SL_BALANCED))
registerGame(GameInfo(932, DevilsGrip, "Devil's Grip",
                      GI.GT_PICTURE_GALLERY | GI.GT_STRIPPED, 2, 0,
                      GI.SL_MOSTLY_LUCK,
                      ranks=list(range(1, 13))  # without Aces
                      ))
registerGame(GameInfo(944, BlueJacket, "Blue Jacket",
                      GI.GT_PICTURE_GALLERY, 2, 0, GI.SL_MOSTLY_SKILL))
