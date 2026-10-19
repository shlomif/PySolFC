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

import itertools
import random

# Rank of the hardest deduction a human has to use.
#  1 naked single
#  2 hidden single
#  3 naked pair
#  4 hidden pair
#  5 locked candidate (pointing pair or box-line)
#  6 naked triple
#  7 hidden triple
#  8 x-wing
#  9 swordfish
# 10 xy-wing
_MAX_RANK = 10

TECHNIQUE_NAMES = (
    "filled",
    "naked single",
    "hidden single",
    "naked pair",
    "hidden pair",
    "locked candidate",
    "naked triple",
    "hidden triple",
    "x-wing",
    "swordfish",
    "xy-wing",
)

# Inclusive band the re-roll is aiming at.
LEVEL_BANDS = {
    1: (2, 3),
    2: (2, 5),
    3: (4, 10),
    4: (8, 10),
}

# Dig cap, then how many fresh grids to try. The cap is the strongest
# technique a deleted clue may depend on. Caps of 3 and 5 never run
# a fish, which is what keeps an easy deal responsive.
_LEVEL_DIG = {
    1: (3, 1),
    2: (5, 1),
    3: (10, 2),
    4: (10, 3),
}

_DIGITS = 0x1FF
_BITS = tuple(1 << shift for shift in range(9))
_POP = tuple(bin(mask).count("1") for mask in range(512))


def _build_units():
    units = []
    for row in range(9):
        units.append(tuple(row * 9 + col for col in range(9)))
    for col in range(9):
        units.append(tuple(row * 9 + col for row in range(9)))
    for brow in range(3):
        for bcol in range(3):
            cells = []
            for drow in range(3):
                for dcol in range(3):
                    cells.append(
                        (brow * 3 + drow) * 9 + bcol * 3 + dcol)
            units.append(tuple(cells))
    return tuple(units)


_UNITS = _build_units()
_BOXES = _UNITS[18:]
_BOX = []
for _cell in range(81):
    _BOX.append((_cell // 9 // 3) * 3 + (_cell % 9 // 3))
_BOX = tuple(_BOX)


def _build_peers():
    peers = [set() for _cell in range(81)]
    for unit in _UNITS:
        for cell in unit:
            peers[cell].update(unit)
            peers[cell].discard(cell)
    return tuple(tuple(sorted(group)) for group in peers)


_PEERS = _build_peers()
_PEER_MASK = []
for _group in _PEERS:
    _mask = 0
    for _peer in _group:
        _mask |= 1 << _peer
    _PEER_MASK.append(_mask)
_PEER_MASK = tuple(_PEER_MASK)


class _Conflict(Exception):
    pass


def band_for_level(level):
    return LEVEL_BANDS.get(int(level), LEVEL_BANDS[2])


def _fit(rating, lo, hi):
    # Higher is a better match for the band. A miss that is a little
    # too hard beats a miss that is still easy.
    if rating is None:
        return (-1, 0)
    if lo <= rating <= hi:
        return (2, 0)
    if rating > hi:
        return (1, hi - rating)
    return (0, rating)


def _clue_count(puzzle):
    return sum(1 for row in puzzle for value in row if value)


def _as_board(value):
    return [value[row * 9:(row + 1) * 9] for row in range(9)]


class _Grid(object):
    # Candidates are 9-bit masks, bit 0 standing for digit 1.
    # Logic steps are tried from easiest to hardest, and restarted
    # after every success, so the recorded rank is forced rather
    # than an artifact of applying a hard step too early.

    def __init__(self, board):
        self.value = [0] * 81
        self.cand = [0] * 81
        self.empty = 0
        self.ok = True
        used_row = [0] * 9
        used_col = [0] * 9
        used_box = [0] * 9
        for cell in range(81):
            digit = board[cell // 9][cell % 9]
            if not digit:
                continue
            if not 1 <= digit <= 9:
                self.ok = False
                return
            bit = 1 << (digit - 1)
            row = cell // 9
            col = cell % 9
            box = _BOX[cell]
            if (used_row[row] | used_col[col] | used_box[box]) & bit:
                self.ok = False
                return
            self.value[cell] = digit
            used_row[row] |= bit
            used_col[col] |= bit
            used_box[box] |= bit
        for cell in range(81):
            if self.value[cell]:
                continue
            row = cell // 9
            col = cell % 9
            mask = _DIGITS & ~(
                used_row[row] | used_col[col] | used_box[_BOX[cell]])
            if mask == 0:
                self.ok = False
                return
            self.cand[cell] = mask
            self.empty += 1

    def analyze(self, limit):
        if not self.ok:
            return 0, False
        score = 0
        try:
            while self.empty:
                step = self._step(limit)
                if step == 0:
                    break
                if step > score:
                    score = step
        except _Conflict:
            return score, False
        return score, self.empty == 0

    def placements_within(self, limit):
        if not self.ok:
            return []
        hardest = 0
        try:
            while self.empty:
                before = self.value[:]
                step = self._step(limit)
                if not step:
                    return []
                if step > hardest:
                    hardest = step
                placed = []
                for cell in range(81):
                    if self.value[cell] and not before[cell]:
                        placed.append(
                            (cell, self.value[cell], hardest))
                if placed:
                    return placed
        except _Conflict:
            return []
        return []

    def _step(self, limit):
        # Techniques above the cap are not tried. A removal the cap
        # cannot solve is rejected, and easy deals never pay for a
        # fish or a wing.
        if self._naked_singles():
            return 1
        if limit < 2:
            return 0
        if self._hidden_singles():
            return 2
        if limit < 3:
            return 0
        if self._naked_subset(2):
            return 3
        if limit < 4:
            return 0
        if self._hidden_subset(2):
            return 4
        if limit < 5:
            return 0
        if self._pointing():
            return 5
        if self._claiming():
            return 5
        if limit < 6:
            return 0
        if self._naked_subset(3):
            return 6
        if limit < 7:
            return 0
        if self._hidden_subset(3):
            return 7
        if limit < 8:
            return 0
        if self._fish(2):
            return 8
        if limit < 9:
            return 0
        if self._fish(3):
            return 9
        if limit < 10:
            return 0
        if self._xywing():
            return 10
        return 0

    def _place(self, cell, bit):
        if self.value[cell]:
            if self.value[cell] != bit.bit_length():
                raise _Conflict()
            return False
        if not (self.cand[cell] & bit):
            raise _Conflict()
        self.value[cell] = bit.bit_length()
        self.cand[cell] = 0
        self.empty -= 1
        for peer in _PEERS[cell]:
            if self.cand[peer] & bit:
                self.cand[peer] &= ~bit
                if self.cand[peer] == 0:
                    raise _Conflict()
        return True

    def _clear(self, cell, bits):
        if self.cand[cell] & bits:
            self.cand[cell] &= ~bits
            if self.cand[cell] == 0:
                raise _Conflict()
            return True
        return False

    def _keep(self, cell, allow):
        if self.cand[cell] & ~allow:
            self.cand[cell] &= allow
            if self.cand[cell] == 0:
                raise _Conflict()
            return True
        return False

    def _naked_singles(self):
        moved = False
        for cell in range(81):
            mask = self.cand[cell]
            if mask and mask & (mask - 1) == 0:
                self._place(cell, mask)
                moved = True
        return moved

    def _hidden_singles(self):
        # One pass over a unit builds a cell-bit per digit. A digit
        # whose bit is a single cell is a hidden single. Placing the
        # unit's singles invalidates later units, so rescan after.
        cand = self.cand
        for unit in _UNITS:
            pos = [0] * 9
            seen = 0
            for index, cell in enumerate(unit):
                mask = cand[cell]
                if not mask:
                    continue
                seen |= mask
                digit = 0
                bits = mask
                while bits:
                    if bits & 1:
                        pos[digit] |= 1 << index
                    bits >>= 1
                    digit += 1
            found = []
            digit = 0
            bits = seen
            while bits:
                if bits & 1:
                    where = pos[digit]
                    if where and where & (where - 1) == 0:
                        found.append(
                            (unit[where.bit_length() - 1], 1 << digit))
                bits >>= 1
                digit += 1
            moved = False
            for cell, bit in found:
                if self.cand[cell] & bit:
                    self._place(cell, bit)
                    moved = True
            if moved:
                return True
        return False

    def _naked_subset(self, size):
        changed = False
        for unit in _UNITS:
            opts = []
            for cell in unit:
                count = _POP[self.cand[cell]] if self.cand[cell] else 0
                if 0 < count <= size:
                    opts.append(cell)
            if len(opts) < size:
                continue
            for group in itertools.combinations(opts, size):
                union = 0
                for cell in group:
                    union |= self.cand[cell]
                if _POP[union] != size:
                    continue
                for cell in unit:
                    if cell in group:
                        continue
                    if self._clear(cell, union):
                        changed = True
        return changed

    def _hidden_subset(self, size):
        changed = False
        cand = self.cand
        for unit in _UNITS:
            pos = [0] * 9
            for index, cell in enumerate(unit):
                mask = cand[cell]
                digit = 0
                bits = mask
                while bits:
                    if bits & 1:
                        pos[digit] |= 1 << index
                    bits >>= 1
                    digit += 1
            if size == 2:
                changed = self._hidden_pairs(unit, pos) or changed
            else:
                changed = self._hidden_triples(unit, pos) or changed
        return changed

    def _hidden_pairs(self, unit, pos):
        changed = False
        for left in range(9):
            if not pos[left]:
                continue
            for right in range(left + 1, 9):
                if not pos[right]:
                    continue
                cover = pos[left] | pos[right]
                if _POP[cover] != 2:
                    continue
                allow = (1 << left) | (1 << right)
                if self._restrict(unit, cover, allow):
                    changed = True
        return changed

    def _hidden_triples(self, unit, pos):
        changed = False
        for left in range(9):
            if not pos[left]:
                continue
            for mid in range(left + 1, 9):
                if not pos[mid]:
                    continue
                for right in range(mid + 1, 9):
                    if not pos[right]:
                        continue
                    cover = pos[left] | pos[mid] | pos[right]
                    if _POP[cover] != 3:
                        continue
                    allow = (1 << left) | (1 << mid) | (1 << right)
                    if self._restrict(unit, cover, allow):
                        changed = True
        return changed

    def _restrict(self, unit, cover, allow):
        changed = False
        bits = cover
        while bits:
            low = bits & -bits
            bits -= low
            if self._keep(unit[low.bit_length() - 1], allow):
                changed = True
        return changed

    def _pointing(self):
        # A digit confined to one row of a box cannot sit elsewhere
        # in that row. Same for a column.
        changed = False
        for box, unit in enumerate(_BOXES):
            for bit in _BITS:
                count = 0
                row0 = -1
                col0 = -1
                same_row = True
                same_col = True
                for cell in unit:
                    if not (self.cand[cell] & bit):
                        continue
                    row = cell // 9
                    col = cell % 9
                    if count == 0:
                        row0 = row
                        col0 = col
                    else:
                        if row != row0:
                            same_row = False
                        if col != col0:
                            same_col = False
                    count += 1
                if count < 2:
                    continue
                if same_row:
                    base = row0 * 9
                    for col in range(9):
                        cell = base + col
                        if _BOX[cell] != box and self._clear(cell, bit):
                            changed = True
                if same_col:
                    for row in range(9):
                        cell = row * 9 + col0
                        if _BOX[cell] != box and self._clear(cell, bit):
                            changed = True
        return changed

    def _claiming(self):
        # A digit confined to one box along a line cannot sit in the
        # rest of that box.
        changed = False
        for unit_index in range(18):
            unit = _UNITS[unit_index]
            by_row = unit_index < 9
            for bit in _BITS:
                count = 0
                box0 = -1
                same_box = True
                for cell in unit:
                    if not (self.cand[cell] & bit):
                        continue
                    box = _BOX[cell]
                    if count == 0:
                        box0 = box
                    elif box != box0:
                        same_box = False
                    count += 1
                if count < 2 or not same_box:
                    continue
                for cell in _BOXES[box0]:
                    if by_row:
                        outside = cell // 9 != unit_index
                    else:
                        outside = cell % 9 != unit_index - 9
                    if outside and self._clear(cell, bit):
                        changed = True
        return changed

    def _fish(self, size):
        # size 2 is an x-wing, size 3 a swordfish. Cross positions
        # are a bit mask so the scan does not build a list per line.
        changed = False
        cand = self.cand
        for bit in _BITS:
            if self._fish_axis(cand, bit, size, True):
                changed = True
            if self._fish_axis(cand, bit, size, False):
                changed = True
        return changed

    def _fish_axis(self, cand, bit, size, by_row):
        masks = []
        ids = []
        for index in range(9):
            mask = 0
            for cross in range(9):
                if by_row:
                    cell = index * 9 + cross
                else:
                    cell = cross * 9 + index
                if cand[cell] & bit:
                    mask |= 1 << cross
            count = _POP[mask]
            if 2 <= count <= size:
                masks.append(mask)
                ids.append(index)
        width = len(masks)
        if width < size:
            return False
        changed = False
        if size == 2:
            for left in range(width):
                for right in range(left + 1, width):
                    cover = masks[left] | masks[right]
                    if _POP[cover] != 2:
                        continue
                    base = (1 << ids[left]) | (1 << ids[right])
                    if self._elim_fish(bit, cover, base, by_row):
                        changed = True
            return changed
        for left in range(width):
            for mid in range(left + 1, width):
                for right in range(mid + 1, width):
                    cover = masks[left] | masks[mid] | masks[right]
                    if _POP[cover] != 3:
                        continue
                    base = (
                        (1 << ids[left]) | (1 << ids[mid])
                        | (1 << ids[right]))
                    if self._elim_fish(bit, cover, base, by_row):
                        changed = True
        return changed

    def _elim_fish(self, bit, cover, base, by_row):
        changed = False
        bits = cover
        while bits:
            low = bits & -bits
            bits -= low
            cross = low.bit_length() - 1
            for index in range(9):
                if base & (1 << index):
                    continue
                if by_row:
                    cell = index * 9 + cross
                else:
                    cell = cross * 9 + index
                if self._clear(cell, bit):
                    changed = True
        return changed

    def _xywing(self):
        # Pivot XY, wings XZ and YZ. A cell that sees both wings
        # cannot be Z.
        changed = False
        pivots = [
            cell for cell in range(81) if _POP[self.cand[cell]] == 2]
        for pivot in pivots:
            xy = self.cand[pivot]
            wings = []
            for cell in _PEERS[pivot]:
                mask = self.cand[cell]
                if _POP[mask] != 2:
                    continue
                shared = mask & xy
                outside = mask & ~xy
                if _POP[shared] == 1 and _POP[outside] == 1:
                    wings.append(cell)
            pairs = itertools.combinations(wings, 2)
            for left, right in pairs:
                left_mask = self.cand[left]
                right_mask = self.cand[right]
                if (left_mask & ~xy) != (right_mask & ~xy):
                    continue
                if (left_mask & xy) == (right_mask & xy):
                    continue
                zee = left_mask & ~xy
                both = _PEER_MASK[left] & _PEER_MASK[right]
                while both:
                    bit = both & -both
                    both -= bit
                    cell = bit.bit_length() - 1
                    if cell != pivot and self._clear(cell, zee):
                        changed = True
        return changed

    def count_solutions(self, limit):
        # Independent of the technique solver. Minimum-remaining-
        # values plus naked-single propagation. `limit` stops the
        # walk once a second solution is enough to reject a grid.
        nodes = [0]

        def restore(saved):
            for cell, old_value, old_cand in saved:
                self.value[cell] = old_value
                self.cand[cell] = old_cand

        def assume(cell, bit):
            saved = []
            seen = set()

            def remember(index):
                if index not in seen:
                    seen.add(index)
                    saved.append(
                        (index, self.value[index], self.cand[index]))

            stack = [(cell, bit)]
            while stack:
                index, forced = stack.pop()
                digit = forced.bit_length()
                if self.value[index]:
                    if self.value[index] != digit:
                        restore(saved)
                        return None
                    continue
                if not (self.cand[index] & forced):
                    restore(saved)
                    return None
                remember(index)
                self.value[index] = digit
                self.cand[index] = 0
                for peer in _PEERS[index]:
                    if self.value[peer] or not (self.cand[peer] & forced):
                        continue
                    reduced = self.cand[peer] & ~forced
                    if reduced == 0:
                        restore(saved)
                        return None
                    remember(peer)
                    self.cand[peer] = reduced
                    if reduced & (reduced - 1) == 0:
                        stack.append((peer, reduced))
            return saved

        def search():
            nodes[0] += 1
            if nodes[0] > 250000:
                raise RuntimeError("sudoku search node cap")
            best = -1
            best_n = 10
            best_mask = 0
            for index in range(81):
                if self.value[index]:
                    continue
                mask = self.cand[index]
                count = _POP[mask]
                if count < best_n:
                    best = index
                    best_n = count
                    best_mask = mask
                    if count == 0:
                        return 0
            if best < 0:
                return 1
            found = 0
            mask = best_mask
            while mask and found < limit:
                bit = mask & -mask
                mask -= bit
                saved = assume(best, bit)
                if saved is not None:
                    found += search()
                    restore(saved)
                    if found >= limit:
                        return found
            return found

        if not self.ok:
            return 0
        return search()


def solve_puzzle(puzzle):
    grid = _Grid(puzzle)
    if not grid.ok:
        return 0, False, None
    rating, solved = grid.analyze(_MAX_RANK)
    if not solved:
        return rating, False, None
    return rating, True, _as_board(grid.value)


def next_forced(puzzle, level):
    # The first digits the level's own techniques can place. An
    # elimination that does not fill a cell is followed until one
    # does, so a pair is reported as the digit it frees.
    cap = _LEVEL_DIG.get(int(level), _LEVEL_DIG[2])[0]
    return _Grid(puzzle).placements_within(cap)


def rate_puzzle(puzzle):
    rating, solved, _board = solve_puzzle(puzzle)
    return rating, solved


def count_grid(board, limit=2):
    return _Grid(board).count_solutions(limit)


def clues_from_puzzle(puzzle):
    # Generator digits are 1-9. Card ranks are 0-8. Zero is an empty cell.
    clues = []
    for row in range(9):
        for col in range(9):
            value = puzzle[row][col]
            if value:
                clues.append((row * 9 + col, value - 1))
    return clues


def ranks_from_solution(solution):
    return [solution[row][col] - 1
            for row in range(9) for col in range(9)]


class SudokuGenerator:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.grid = [[0 for _col in range(9)] for _row in range(9)]

    def is_valid(self, board, row, col, num):
        if num in board[row]:
            return False
        if num in [board[index][col] for index in range(9)]:
            return False
        box_x = (col // 3) * 3
        box_y = (row // 3) * 3
        for brow in range(box_y, box_y + 3):
            for bcol in range(box_x, box_x + 3):
                if board[brow][bcol] == num:
                    return False
        return True

    def fill_grid(self):
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    numbers = list(range(1, 10))
                    self.rng.shuffle(numbers)
                    for num in numbers:
                        if self.is_valid(self.grid, row, col, num):
                            self.grid[row][col] = num
                            if self.fill_grid():
                                return True
                            self.grid[row][col] = 0
                    return False
        return True

    def count_solutions(self, board):
        return count_grid(board)

    def _measure(self, puzzle, solution, limit):
        grid = _Grid(puzzle)
        rating, solved = grid.analyze(limit)
        if not solved:
            return None
        for row in range(9):
            if grid.value[row * 9:(row + 1) * 9] != solution[row]:
                return None
        return rating

    def _accept(self, puzzle, solution, limit):
        # A grid that still falls to singles never needs the fish.
        if limit > 2:
            easy = self._measure(puzzle, solution, 2)
            if easy is not None:
                return easy
        return self._measure(puzzle, solution, limit)

    def _dig(self, puzzle, solution, limit, lo):
        # One pass. A second pass only rechecks clues that already
        # failed, and once the cap includes a fish those rejects are
        # most of the deal time.
        cells = [(row, col) for row in range(9) for col in range(9)]
        self.rng.shuffle(cells)
        rating = 0
        for row, col in cells:
            if puzzle[row][col] == 0:
                continue
            puzzle[row][col] = 0
            trial = self._accept(puzzle, solution, limit)
            if trial is None:
                puzzle[row][col] = solution[row][col]
                continue
            rating = trial
            # Once a hard pattern is required, more deletions are
            # optional. Stop so the deal does not keep searching.
            if limit >= 8 and rating >= lo:
                return rating
        return rating

    def generate_puzzle(self, level=2):
        lo, hi = band_for_level(level)
        cap, attempts = _LEVEL_DIG.get(int(level), _LEVEL_DIG[2])
        best = None
        for _attempt in range(attempts):
            self.grid = [[0 for _col in range(9)] for _row in range(9)]
            if not self.fill_grid():
                continue
            solution = [row[:] for row in self.grid]
            puzzle = [row[:] for row in solution]
            rating = self._dig(puzzle, solution, cap, lo)
            choice = (_fit(rating, lo, hi), -_clue_count(puzzle))
            snapshot = [row[:] for row in puzzle]
            if best is None or choice > best[0]:
                best = (choice, snapshot, solution, rating)
            if lo <= rating <= hi:
                break
        if best is None:
            raise RuntimeError("could not fill a sudoku grid")
        _choice, puzzle, solution, _rating = best
        self.grid = puzzle
        return puzzle, solution

    @staticmethod
    def print_board(board):
        for row in range(9):
            if row % 3 == 0 and row != 0:
                print("- " * 11)
            row_str = ""
            for col in range(9):
                if col % 3 == 0 and col != 0:
                    row_str += "| "
                val = board[row][col]
                row_str += "%s " % (val if val else ".")
            print(row_str.strip())
