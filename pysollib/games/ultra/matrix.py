##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 by T. Kirk
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
##---------------------------------------------------------------------------##

__all__ = []

# Imports
import sys, math

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText, MfxCanvasImage, bind, ANCHOR_NW

from pysollib.games.special.pegged import Pegged_RowStack, WasteTalonStack, \
     Pegged, PeggedCross1, PeggedCross2, Pegged6x6, Pegged7x7


## Matrix_RowStack
## NewTower_RowStack
## RockHopper_RowStack
## ThreePeaks_TalonStack
## ThreePeaks_RowStack
## Matrix3
## Matrix4
## Matrix5
## Matrix6
## Matrix7
## Matrix8
## Matrix9
## Matrix10
## Matrix20
## NewTowerofHanoi
## RockHopper
## RockHopperCross1
## RockHopperCross2
## RockHopper6x6
## RockHopper7x7
## ThreePeaks
## ThreePeaksNoScore
## LeGrandeTeton


# /***********************************************************************
# // Matrix Row Stack
# ************************************************************************/

class Matrix_RowStack(OpenStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1, max_cards=1,
                    base_rank=ANY_RANK)
        apply(OpenStack.__init__, (self, x, y, game), cap)

    def acceptsCards(self, from_stack, cards):
        return OpenStack.acceptsCards(self, from_stack, cards)

    def canFlipCard(self):
        return 0

    def canDropCards(self, stacks):
        return (None, 0)

    def cancelDrag(self, event=None):
        if event is None:
            self._stopDrag()

    def _findCard(self, event):
        # we need to override this because the shade may be hiding
        # the tile (from Tk's stacking view)
        return len(self.cards) - 1

    def initBindings(self):
        bind(self.group, "<1>", self._Stack__clickEventHandler)
        bind(self.group, "<Control-1>", self._Stack__controlclickEventHandler)

    def getBottomImage(self):
        return None

    def blockMap(self):
        ncards = self.game.gameinfo.ncards
        id, sqrt = self.id, int(math.sqrt(ncards))
        line, row, column = int(id / sqrt), [], []
        for r in self.game.s.rows[line * sqrt:sqrt + line * sqrt]:
            row.append(r.id)
        while id >= sqrt:
            id = id - sqrt
        while id < ncards:
            column.append(id)
            id = id + sqrt
        return [row, column]

    def basicIsBlocked(self):
        stack_map = self.blockMap()
        for j in range(2):
            for i in range(len(stack_map[j])):
                if not self.game.s.rows[stack_map[j][i]].cards:
                    return 0
        return 1

    def clickHandler(self, event):
        game = self.game
        row = game.s.rows
        if not self.cards or game.drag.stack is self or self.basicIsBlocked():
            return 1
        stack_map = self.blockMap()
        for j in range(2):
            dir = 1
            for i in range(len(stack_map[j])):
                to_stack = row[stack_map[j][i]]
                if to_stack is self:
                    dir = -1
                if not to_stack.cards:
                    self._stopDrag()
                    step = 1
                    from_stack = row[stack_map[j][i + dir]]
                    while not from_stack is self:
                        from_stack.playMoveMove(1, to_stack, frames = 0, sound = 1)
                        to_stack = from_stack
                        step = step + 1
                        from_stack = row[stack_map[j][i + dir * step]]
                    self.playMoveMove(1, to_stack, frames = 0, sound = 1)
                    return 1
        return 1



# /***********************************************************************
# // New Tower Row Stack
# ************************************************************************/

class NewTower_RowStack(Matrix_RowStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1, max_cards=99,
                  base_rank=ANY_RANK)
        apply(OpenStack.__init__, (self, x, y, game), cap)
        self.CARD_YOFFSET = -max(self.game.app.images.CARD_YOFFSET, 20)

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return 0
        if self.cards:
            return self.cards[-1].rank > cards[0].rank
        return 1

    def getBottomImage(self):
        # None doesn't recognize clicks.
        return self.game.app.images.getLetter(0)

    def basicIsBlocked(self):
        return 0

    def clickHandler(self, event):
        game = self.game
        drag = game.drag
        from_stack = drag.stack
        if from_stack is self:
            # remove selection
            self._stopDrag()
            return 1
        # possible move
        if from_stack:
            if self.acceptsCards(from_stack, from_stack.cards[-1:]):
                self._stopDrag()
                # this code actually moves the tiles
                from_stack.playMoveMove(1, self, frames=3, sound=0)
                return 1
        drag.stack = self
        # move or create the shade image (see stack.py, _updateShade)
        if drag.shade_img:
            img = drag.shade_img
            img.dtag(drag.shade_stack.group)
            img.moveTo(self.x, self.y)
        elif self.cards:
            img = game.app.images.getShade()
            if img is None:
                return 1
            img = MfxCanvasImage(game.canvas, self.x,
                                 self.y + self.CARD_YOFFSET[0] * (len(self.cards) - 1),
                                 image=img, anchor=ANCHOR_NW)
            drag.shade_img = img
        if self.cards:
            img.tkraise(self.cards[-1].item)
            img.addtag(self.group)
        drag.shade_stack = self
        return 1



# /***********************************************************************
# // Rock Hopper Row Stack
# ************************************************************************/

class RockHopper_RowStack(Pegged_RowStack):

    def canFlipCard(self):
        return 0

    def cancelDrag(self, event=None):
        if event is None:
            self._stopDrag()

    def _findCard(self, event):
        # we need to override this because the shade may be hiding
        # the tile (from Tk's stacking view)
        return len(self.cards) - 1

    def initBindings(self):
        bind(self.group, "<1>", self._Stack__clickEventHandler)
        bind(self.group, "<Control-1>", self._Stack__controlclickEventHandler)

    def getBottomImage(self):
        # None doesn't recognize clicks.
        return self.game.app.images.getReserveBottom()

    def clickHandler(self, event):
        game = self.game
        drag = game.drag
        from_stack = drag.stack
        if from_stack is self:
            # remove selection
            self._stopDrag()
            return 1
        # possible move
        if from_stack and not self.cards and self._getMiddleStack(from_stack) is not None:
            self._stopDrag()
            # this code actually moves the tiles
            from_stack.moveMove(1, self, frames=3)
            return 1
        drag.stack = self
        # move or create the shade image (see stack.py, _updateShade)
        if drag.shade_img and self.cards:
            img = drag.shade_img
            img.dtag(drag.shade_stack.group)
            img.moveTo(self.x, self.y)
        elif self.cards:
            img = game.app.images.getShade()
            if img is None:
                return 1
            img = MfxCanvasImage(game.canvas, self.x, self.y,
                                 image=img, anchor=ANCHOR_NW)
            drag.shade_img = img
        if self.cards:
            img.tkraise(self.cards[-1].item)
            img.addtag(self.group)
        drag.shade_stack = self
        return 1



# /***********************************************************************
# // Matrix Game
# ************************************************************************/

class Matrix3(Game):

    #
    # Game layout
    #

    def createGame(self):
        l, s = Layout(self), self.s
        grid = math.sqrt(self.gameinfo.ncards)
        assert grid == int(grid)
        grid = int(grid)

        # Set window size
        w, h = l.XM * 2 + l.CW * grid, l.YM * 2 + l.CH * grid
        self.setSize(w, h)

        # Create rows
        for j in range(grid):
            x, y = l.XM, l.YM + l.CH * j
            for i in range(grid):
                s.rows.append(Matrix_RowStack(x, y, self))
                x = x + l.CW

        # Create talon
        x, y = l.XM - l.XS, l.YM
        s.talon = InitialDealTalonStack(x, y, self)

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game extras
    #

    def shuffle(self):
        cards = list(self.cards)[:]
        cards.reverse()
        for card in cards:
            self.s.talon.addCard(card, update=0)
            card.showBack(unhide=0)

    def scramble(self):
        if self.gstats.restarted:
            self.random.reset()
        ncards, randint = self.gameinfo.ncards, self.random.randint
        r = self.s.rows[ncards - int(math.sqrt(ncards))]
        rc, stackmap = 1, r.blockMap()
        for i in range(randint(max(200, ncards * 4), max(300, ncards * 5))):
            r.clickHandler(r)
            r = self.s.rows[stackmap[rc][randint(0, len(stackmap[0]) - 1)]]
            rc, stackmap = (rc + 1) % 2, r.blockMap()

    #
    # Game over rides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        self.s.talon.dealRow(rows=self.s.rows[:self.gameinfo.ncards - 1],
                             flip=1, frames=3)
        self.scramble()
        self.startDealSample()

    def isGameWon(self):
        if self.busy:
            return 0
        s = self.s.rows
        l = len(s) - 1
        for r in s[:l]:
            if not r.cards or not r.cards[0].rank == r.id:
                return 0
        self.s.talon.dealRow(rows=s[l:], flip=1, frames=3)
        return 1

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1 == card2.rank)
                or (card1.rank - 1 == card2.rank))



# /***********************************************************************
# // Size variations
# ************************************************************************/

class Matrix4(Matrix3):

    pass

class Matrix5(Matrix3):

    pass

class Matrix6(Matrix3):

    pass

class Matrix7(Matrix3):

    pass

class Matrix8(Matrix3):

    pass

class Matrix9(Matrix3):

    pass

class Matrix10(Matrix3):

    pass

class Matrix20(Matrix3):

    pass


# /***********************************************************************
# // Rock Hopper
# ************************************************************************/

class RockHopper(Pegged):
    STACK = RockHopper_RowStack

class RockHopperCross1(PeggedCross1):
    STACK = RockHopper_RowStack

class RockHopperCross2(PeggedCross2):
    STACK = RockHopper_RowStack

class RockHopper6x6(Pegged6x6):
    STACK = RockHopper_RowStack

class RockHopper7x7(Pegged7x7):
    STACK = RockHopper_RowStack



# /***********************************************************************
# // Register a Matrix game
# ************************************************************************/

def r(id, gameclass, short_name):
    name = short_name
    ncards = int(name[:2]) * int(name[:2])
    gi = GameInfo(id, gameclass, name,
                GI.GT_MATRIX, 1, 0,
                category=GI.GC_TRUMP_ONLY, short_name=short_name,
                suits=(), ranks=(), trumps=range(ncards),
                si = {"decks": 1, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "matrix.html"
    registerGame(gi)
    return gi

r(22223, Matrix3, " 3x3 Matrix")
r(22224, Matrix4, " 4x4 Matrix")
r(22225, Matrix5, " 5x5 Matrix")
r(22226, Matrix6, " 6x6 Matrix")
r(22227, Matrix7, " 7x7 Matrix")
r(22228, Matrix8, " 8x8 Matrix")
r(22229, Matrix9, " 9x9 Matrix")
r(22230, Matrix10, "10x10 Matrix")
#r(22240, Matrix20, "20x20 Matrix")

del r

def r(id, gameclass, short_name):
    name = short_name
    ncards = 0
    for n in gameclass.ROWS:
        ncards = ncards + n
    gi = GameInfo(id, gameclass, name, GI.GT_MATRIX, 1, 0,
                  category=GI.GC_TRUMP_ONLY, short_name=short_name,
                  suits=(), ranks=(), trumps=range(ncards),
                  si={"decks": 1, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "pegged.html"
    registerGame(gi)
    return gi

r(22221, RockHopper, "Rock Hopper")
r(22220, RockHopperCross1, "Rock Hopper Cross 1")
r(22219, RockHopperCross2, "Rock Hopper Cross 2")
r(22218, RockHopper6x6, "Rock Hopper 6x6")
r(22217, RockHopper7x7, "Rock Hopper 7x7")

del r
