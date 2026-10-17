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
from pysollib.games.special.sudoku_gen import \
        SudokuGenerator, \
        clues_from_puzzle, \
        ranks_from_solution
from pysollib.hint import AbstractHint
from pysollib.layout import Layout
from pysollib.pysoltk import ANCHOR_NW, MfxCanvasImage
from pysollib.settings import TOOLKIT
from pysollib.stack import \
        InitialDealTalonStack, \
        InvisibleStack, \
        ReserveStack

# ************************************************************************
# * Sudoku stacks
# ************************************************************************


class Sudoku_RowStack(ReserveStack):

    def __init__(self, x, y, game, **cap):
        ReserveStack.__init__(self, x, y, game, **cap)
        self.locked = False

    def lock(self):
        # Given numbers are locked, so they cannot be changed.
        self.locked = True
        self.is_filled = True
        self._shadeLocked()

    def _shadeLocked(self):
        if not self.cards or self.items.shade_item:
            return
        if TOOLKIT == 'kivy':
            self.game.top.waitAnimation()
        card = self.cards[-1]
        img = self.game.app.images.getHighlightedCard(
            card.deck, card.suit, card.rank)
        if img is None:
            return
        self.items.shade_item = MfxCanvasImage(
            self.canvas, card.x, card.y,
            image=img, anchor=ANCHOR_NW, group=self.group)

    def resetGame(self):
        self.locked = False
        self.is_filled = False
        self.unshadeStack()
        ReserveStack.resetGame(self)

    def canMoveCards(self, cards):
        if self.locked:
            return False
        return ReserveStack.canMoveCards(self, cards)

    def acceptsCards(self, from_stack, cards):
        if self.locked or getattr(from_stack, "locked", False):
            return False
        if from_stack is self or len(cards) != 1 or not cards[0].face_up:
            return False
        if self.cards and not self.cards[-1].face_up:
            return False
        return self.game.ranksStayUnique(cards[0], from_stack, self)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game = self.game
        if to_stack in game.s.reserves:
            # Dropping on any reserve files the card with its own rank.
            to_stack = game.reserveFor(self.cards[-1])
            ReserveStack.moveMove(
                self, ncards, to_stack, frames=frames, shadow=shadow)
            return
        if to_stack.cards:
            self._swapPairMove(ncards, to_stack, frames=frames, shadow=shadow)
            return
        ReserveStack.moveMove(
            self, ncards, to_stack, frames=frames, shadow=shadow)

    def _swapPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        game.moveMove(n, self, swap, frames=0)
        game.moveMove(n, other_stack, self, frames=0)
        game.moveMove(n, swap, other_stack, frames=frames, shadow=shadow)
        game.leaveState(old_state)

    def rightclickHandler(self, event):
        return self.clickHandler(event)


class Sudoku_Reserve(ReserveStack):

    def acceptsCards(self, from_stack, cards):
        if getattr(from_stack, "locked", False):
            return False
        if from_stack is self or len(cards) != 1 or not cards[0].face_up:
            return False
        # Every reserve accepts every rank. The card is then filed
        # onto the pile of that rank, which may be this pile.
        home = self.game.reserveFor(cards[0])
        if home is from_stack:
            return False
        return len(home.cards) < home.cap.max_cards

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game = self.game
        if to_stack in game.s.rows:
            if to_stack.cards:
                self._replaceCell(to_stack, frames, shadow)
            else:
                ReserveStack.moveMove(
                    self, ncards, to_stack, frames=frames, shadow=shadow)
            return
        home = game.reserveFor(self.cards[-1])
        ReserveStack.moveMove(
            self, ncards, home, frames=frames, shadow=shadow)

    def _replaceCell(self, cell, frames, shadow):
        # Park the dragged card first. The cell's card may belong on
        # this same pile, and moving it home before the drag would bury
        # the card the player is holding.
        game = self.game
        old_state = game.enterState(game.S_FILL)
        swap = game.s.internals[0]
        home = game.reserveFor(cell.cards[-1])
        game.moveMove(1, self, swap, frames=0)
        game.moveMove(1, cell, home, frames=0)
        game.moveMove(1, swap, cell, frames=frames, shadow=shadow)
        game.leaveState(old_state)

    def rightclickHandler(self, event):
        return self.clickHandler(event)


# ************************************************************************
# * Hint
# ************************************************************************

class Sudoku_Hint(AbstractHint):
    # Highest priority is removing incorrect digits.  Then, we prioritize
    # easier, more obvious numbers.  We do not include options from the
    # solution that have multiple possible numbers, as the hints will
    # cycle, revealing the solution.  If the puzzle is correctly designed,
    # there should always be one hint.

    def _legalRanks(self, cell):
        ranks = []
        for reserve in self.game.s.reserves:
            if not reserve.cards:
                continue
            card = reserve.cards[-1]
            if cell.acceptsCards(reserve, [card]):
                ranks.append(card.rank)
        return ranks

    def computeHints(self):
        game = self.game
        solution = game.solution
        if not solution:
            return
        for i, cell in enumerate(game.s.rows):
            if cell.locked or not cell.cards:
                continue
            if cell.cards[-1].rank == solution[i]:
                continue
            home = game.reserveFor(cell.cards[-1])
            pile = cell.cards[-1:]
            if home.acceptsCards(cell, pile):
                self.addHint(100000, 1, cell, home)
        if self.hints:
            return
        legal = {}
        for i, cell in enumerate(game.s.rows):
            if cell.cards:
                continue
            legal[i] = self._legalRanks(cell)
        naked = set()
        for i, ranks in legal.items():
            if len(ranks) == 1 and ranks[0] == solution[i]:
                naked.add(i)
                self.addHint(
                    90000, 1, game.reserve_by_rank[ranks[0]],
                    game.s.rows[i])
        index_of = {cell: i for i, cell in enumerate(game.s.rows)}
        # First sighting wins, and rows are listed before columns
        # and boxes, so a row scan is the simpler of two homes.
        hidden = {}
        for gi, group in enumerate(game.sudoku_rows):
            homes = {}
            for cell in group:
                i = index_of[cell]
                for rank in legal.get(i, ()):
                    homes.setdefault(rank, []).append(i)
            for rank, cells in homes.items():
                if len(cells) != 1:
                    continue
                i = cells[0]
                if i in naked or i in hidden or solution[i] != rank:
                    continue
                hidden[i] = (len(legal[i]), gi, rank)
        # Player hints flatten to multiples of 10000, so each extra
        # legal rank has to cost a whole step. Two ranks score 80000.
        order = sorted(
            hidden, key=lambda i: (hidden[i][0], hidden[i][1], i))
        for i in order:
            n_ranks, rank = hidden[i][0], hidden[i][2]
            self.addHint(
                10000 * (10 - n_ranks), 1,
                game.reserve_by_rank[rank], game.s.rows[i])


# ************************************************************************
# * Sudoku Game
# ************************************************************************

class Sudoku(Game):
    Hint_Class = Sudoku_Hint
    RANK_COPIES = 11
    LEVEL = 2

    #
    # Game layout
    #

    def createGame(self):
        self.shownCards = tuple()
        self.solution = None
        self.reserve_by_rank = {}

        l, s = Layout(self), self.s
        grid = 9

        # Set window size
        w, h = l.XM * 2 + l.CW * (grid + 1), l.YM * 2 + l.CH * (grid + 2.5)
        self.setSize(w, h)

        # Create rows
        for j in range(grid):
            x, y = l.XM, l.YM + l.CH * j
            if j > 2:
                y += l.CW / 2
            if j > 5:
                y += l.CW / 2
            for i in range(grid):
                s.rows.append(Sudoku_RowStack(x, y, self))
                x += l.CW
                if i in (2, 5):
                    x += l.CW / 2

        # Nine rows, nine columns, and nine 3x3 boxes. A won game is
        # every one of these holding nine different ranks.
        self._indexSudokuGroups()

        x, y = l.XM + (l.CW / 2), l.YM + l.CH * 10.5

        for j in range(9):
            stack = Sudoku_Reserve(
                x, y, self, max_cards=self.RANK_COPIES, max_accept=1)
            s.reserves.append(stack)
            x += l.CW

        # Create talon
        x, y = -2 * l.XS, 0               # invisible
        s.talon = InitialDealTalonStack(x, y, self)

        s.internals.append(InvisibleStack(self))

        # Define stack groups
        l.defaultStackGroups()

    #
    # Game extras
    #

    def _indexSudokuGroups(self):
        r = self.s.rows
        grid = 9
        box = 3
        groups = []
        for j in range(grid):
            groups.append(tuple(r[j * grid:(j + 1) * grid]))
        for i in range(grid):
            groups.append(tuple(r[i + j * grid] for j in range(grid)))
        for br in range(box):
            for bc in range(box):
                cells = []
                for dr in range(box):
                    for dc in range(box):
                        cells.append(
                            r[(br * box + dr) * grid + bc * box + dc])
                groups.append(tuple(cells))
        self.sudoku_rows = groups
        self.stack_groups = {}
        for group in groups:
            for stack in group:
                self.stack_groups.setdefault(stack, []).append(group)

    def reserveFor(self, card):
        return self.reserve_by_rank[card.rank]

    def ranksStayUnique(self, card, from_stack, to_stack):
        # Resulting row, column, and box may not hold the rank twice.
        # A swap puts the displaced card on the source cell; a drop
        # from a reserve takes the displaced card off the grid.
        if to_stack not in self.s.rows:
            return True
        changes = {to_stack: card}
        if from_stack in self.s.rows:
            if to_stack.cards:
                changes[from_stack] = to_stack.cards[-1]
            else:
                changes[from_stack] = None
        seen = set()
        for stack in changes:
            for group in self.stack_groups[stack]:
                if id(group) in seen:
                    continue
                seen.add(id(group))
                ranks = []
                for cell in group:
                    if cell in changes:
                        placed = changes[cell]
                    elif cell.cards:
                        placed = cell.cards[0]
                    else:
                        placed = None
                    if placed is not None:
                        ranks.append(placed.rank)
                if len(ranks) != len(set(ranks)):
                    return False
        return True

    def isCompleteRow(self, row):
        ranks = []
        for stack in row:
            if not stack.cards:
                return False
            ranks.append(stack.cards[0].rank)
        return len(set(ranks)) == len(ranks)

    def _shuffleHook(self, cards):
        cards.sort(key=lambda c: -c.rank)
        return cards

    #
    # Game over rides
    #

    def startGame(self):
        self.startDealSample()
        n = self.gameinfo.ncards // len(self.s.reserves)
        for reserve in self.s.reserves:
            self.s.talon.dealRow(rows=[reserve] * n, frames=0)
        self._bindReserves()
        self._dealClues()

    def _bindReserves(self):
        self.reserve_by_rank = {}
        for reserve in self.s.reserves:
            reserve.home_rank = reserve.cards[-1].rank
            self.reserve_by_rank[reserve.home_rank] = reserve

    def _dealClues(self):
        # Same game number, same puzzle: generation continues the
        # deal RNG after the deck has been ordered by rank.
        puzzle, solution = SudokuGenerator(
            self.random).generate_puzzle(self.LEVEL)
        self.solution = ranks_from_solution(solution)
        for index, rank in clues_from_puzzle(puzzle):
            cell = self.s.rows[index]
            self.moveMove(1, self.reserve_by_rank[rank], cell, frames=0)
            cell.lock()

    def _restoreGameHook(self, game):
        dval = game.loadinfo.dval
        self.solution = dval['solution']
        self.reserve_by_rank = {}
        for reserve, rank in zip(self.s.reserves, dval['home_ranks']):
            reserve.home_rank = rank
            self.reserve_by_rank[rank] = reserve
        for stack, flag in zip(self.s.rows, dval['locked']):
            if flag:
                stack.lock()

    def _loadGameHook(self, p):
        self.loadinfo.addattr(dval=p.load())

    def _saveGameHook(self, p):
        p.dump({
            'solution': self.solution,
            'locked': [int(stack.locked) for stack in self.s.rows],
            'home_ranks': [stack.home_rank for stack in self.s.reserves],
        })

    def parseCard(self, card):
        return str(card.rank + 1)

    def isGameWon(self):
        for row in self.sudoku_rows:
            if not self.isCompleteRow(row):
                return False
        return True


# ************************************************************************
# * Register a Sudoku game
# ************************************************************************

def r(id, short_name, level):
    name = short_name
    ranks = list(range(0, 9))
    copies = Sudoku.RANK_COPIES
    ncards = copies * len(ranks)
    # The level integer is the difficulty the generator reads.
    gameclass = type(
        "SudokuLevel%d" % level, (Sudoku,), {"LEVEL": level})
    gi = GameInfo(
        id, gameclass, name,
        GI.GT_SUDOKU, 1, 0, GI.SL_SKILL,
        category=GI.GC_TRUMP_ONLY, short_name=short_name,
        suits=(), ranks=(), trumps=ranks * copies,
        si={"decks": 1, "ncards": ncards})
    gi.ncards = ncards
    gi.rules_filename = "sudoku.html"
    registerGame(gi)
    return gi


r(21001, "Sudoku (Level 1)", 1)
r(21002, "Sudoku (Level 2)", 2)
r(21003, "Sudoku (Level 3)", 3)
r(21004, "Sudoku (Level 4)", 4)

del r
