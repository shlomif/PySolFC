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

class Calculation_Hint(DefaultHint):
    # FIXME: demo logic is a complete nonsense
    def _getMoveWasteScore(self, score, color, r, t, pile, rpile):
        assert r is self.game.s.waste and len(pile) == 1
        score = 30000
        if len(t.cards) == 0:
            score = score - (KING - r.cards[0].rank) * 1000
        elif t.cards[-1].rank < r.cards[0].rank:
            score = 10000 + t.cards[-1].rank - len(t.cards)
        elif t.cards[-1].rank == r.cards[0].rank:
            score = 20000
        else:
            score = score - (t.cards[-1].rank - r.cards[0].rank) * 1000
        return score, color


# /***********************************************************************
# //
# ************************************************************************/

class BetsyRoss_Foundation(RK_FoundationStack):
    def updateText(self):
        if self.game.preview > 1:
            return
        if self.texts.misc:
            if len(self.cards) == 0:
                rank = self.cap.base_rank
                self.texts.misc.config(text=RANKS[rank])
            elif len(self.cards) == self.cap.max_cards:
                self.texts.misc.config(text="")
            else:
                rank = (self.cards[-1].rank + self.cap.dir) % self.cap.mod
                self.texts.misc.config(text=RANKS[rank])


class Calculation_Foundation(BetsyRoss_Foundation):
    def getBottomImage(self):
        return self.game.app.images.getLetter(self.cap.base_rank)


class Calculation_RowStack(BasicRowStack):
    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return 0
        # this stack accepts any one card from the Waste pile
        return from_stack is self.game.s.waste and len(cards) == 1

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()

    def getHelp(self):
        return _('Row. Build regardless of rank and suit.')


# /***********************************************************************
# // Calculation
# ************************************************************************/

class Calculation(Game):
    Hint_Class = Calculation_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, TEXT_HEIGHT=40), self.s

        # set window
        # (piles up to 20 cards are playable in default window size)
        h = max(2*l.YS, 20*l.YOFFSET)
        self.setSize(5.5*l.XS+l.XM+200, l.YM + l.YS + l.TEXT_HEIGHT + h)

        # create stacks
        x0 = l.XM + l.XS * 3 / 2
        x, y = x0, l.YM
        for i in range(4):
            stack = Calculation_Foundation(x, y, self, base_rank=i, mod=13, dir=i+1)
            s.foundations.append(stack)
            stack.texts.misc = MfxCanvasText(self.canvas,
                                             x + l.CW / 2, y + l.YS,
                                             anchor="n",
                                             font=self.app.getFont("canvas_default"))
            x = x + l.XS
        help = (_('''\
1: 2 3 4 5 6 7 8 9 T J Q K
2: 4 6 8 T Q A 3 5 7 9 J K
3: 6 9 Q 2 5 8 J A 4 7 T K
4: 8 Q 3 7 J 2 6 T A 5 9 K'''))
        self.texts.help = MfxCanvasText(self.canvas, x + l.XM, y + l.CH / 2, text=help,
                                        anchor="w", font=self.app.getFont("canvas_fixed"))
        x = x0
        y = l.YM + l.YS + l.TEXT_HEIGHT
        for i in range(4):
            s.rows.append(Calculation_RowStack(x, y, self, max_move=1, max_accept=1))
            x = x + l.XS
        self.setRegion(s.rows, (-999, y, 999999, 999999))
        x = l.XM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "nn")
        y = y + l.YS
        s.waste = WasteStack(x, y, self, max_cards=1)

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # prepare first cards
        topcards = [ None ] * 4
        for c in cards[:]:
            if c.rank <= 3 and topcards[c.rank] is None:
                topcards[c.rank] = c
                cards.remove(c)
        topcards.reverse()
        return cards + topcards

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        self.s.talon.dealCards()          # deal first card to WasteStack

    def getHighlightPilesStacks(self):
        return ()


# /***********************************************************************
# // Hopscotch
# ************************************************************************/

class Hopscotch(Calculation):
    def _shuffleHook(self, cards):
        # prepare first cards
        topcards = [ None ] * 4
        for c in cards[:]:
            if c.suit == 0 and c.rank <= 3 and topcards[c.rank] is None:
                topcards[c.rank] = c
                cards.remove(c)
        topcards.reverse()
        return cards + topcards


# /***********************************************************************
# // Betsy Ross
# ************************************************************************/

class BetsyRoss(Calculation):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self, TEXT_HEIGHT=40), self.s

        # set window
        self.setSize(5.5*l.XS+l.XM+200, l.YM + l.YS + l.TEXT_HEIGHT + 3*l.YS)

        # create stacks
        x0 = l.XM + l.XS * 3 / 2
        x, y = x0, l.YM
        for i in range(4):
            stack = BetsyRoss_Foundation(x, y, self, base_rank=i,
                                         max_cards=1, max_move=0, max_accept=0)
            s.foundations.append(stack)
            x = x + l.XS
        x = x0
        y = l.YM + l.YS + l.TEXT_HEIGHT
        for i in range(4):
            stack = BetsyRoss_Foundation(x, y, self, base_rank=2*i+1, mod=13, dir=i+1,
                                        max_cards=12, max_move=0)
            stack.texts.misc = MfxCanvasText(self.canvas, x + l.CW / 2, y - l.YM,
                                             anchor="s", font=self.app.getFont("canvas_default"))
            s.foundations.append(stack)
            x = x + l.XS
        help = (_('''\
1: 2 3 4 5 6 7 8 9 T J Q K
2: 4 6 8 T Q A 3 5 7 9 J K
3: 6 9 Q 2 5 8 J A 4 7 T K
4: 8 Q 3 7 J 2 6 T A 5 9 K'''))
        self.texts.help = MfxCanvasText(self.canvas, x + l.XM, y + l.CH / 2, text=help,
                                        anchor="w", font=self.app.getFont("canvas_fixed"))
        x = l.XM
        s.talon = WasteTalonStack(x, y, self, max_rounds=3)
        l.createText(s.talon, "nn")
        y = y + l.YS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "ss")

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def _shuffleHook(self, cards):
        # prepare first cards
        topcards = [ None ] * 8
        for c in cards[:]:
            if c.rank <= 3 and topcards[c.rank] is None:
                topcards[c.rank] = c
                cards.remove(c)
            elif c.rank in (1, 3, 5, 7):
                i = 4 + (c.rank - 1) / 2
                if topcards[i] is None:
                    topcards[i] = c
                    cards.remove(c)
        topcards.reverse()
        return cards + topcards


# register the game
registerGame(GameInfo(256, Calculation, "Calculation",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL,
                      altnames=("Progression",) ))
registerGame(GameInfo(94, Hopscotch, "Hopscotch",
                      GI.GT_1DECK_TYPE, 1, 0, GI.SL_MOSTLY_SKILL))
registerGame(GameInfo(134, BetsyRoss, "Betsy Ross",
                      GI.GT_1DECK_TYPE, 1, 2, GI.SL_MOSTLY_LUCK,
                      altnames=("Fairest", "Four Kings", "Musical Patience",
                                "Quadruple Alliance", "Plus Belle") ))

