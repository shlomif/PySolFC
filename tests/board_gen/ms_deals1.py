#!/usr/bin/python
#
# make_pysol_freecell_board.py - Program to generate the boards of
# PySol for input into Freecell Solver.
#
# Usage: make_pysol_freecell_board.py [board number] | fc-solve
#
# Or on non-UNIXes:
#
# python make_pysol_freecell_board.py [board number] | fc-solve
#
# This program is platform independent and will generate the same results
# on all architectures and operating systems.
#
# Based on the code by Markus Franz Xaver Johannes Oberhumer.
# Modified by Shlomi Fish, 2000
#
# Since much of the code here is ripped from the actual PySol code, this
# program is distributed under the GNU General Public License.
#
#
#
# vim:ts=4:et:nowrap
#
# ---------------------------------------------------------------------------##
#
# PySol -- a Python Solitaire game
#
# Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.
# If not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Markus F.X.J. Oberhumer
# <markus.oberhumer@jk.uni-linz.ac.at>
# http://wildsau.idv.uni-linz.ac.at/mfx/pysol.html
#
# ---------------------------------------------------------------------------##


# imports
import sys, os, re, string, time, types

sys.path.append("./tests/lib")
from TAP.Simple import plan, ok

# So the localpaths will be overrided.
sys.path.insert(0, ".")

from pysollib.pysolrandom import constructRandom, LCRandom31, random__str2long, random__long2str

# PySol imports

# /***********************************************************************
# // Abstract PySol Random number generator.
# //
# // We use a seed of type long in the range [0, MAX_SEED].
# ************************************************************************/

class Card:

    ACE = 1
    KING = 13

    def __init__(self, id, rank, suit, print_ts):
        self.id = id
        self.rank = rank
        self.suit = suit
        self.flipped = False
        self.print_ts = print_ts
        self.empty = False

    def is_king(self):
        return self.rank == self.KING

    def is_ace(self):
        return self.rank == self.ACE

    def rank_s(self):
        s = "0A23456789TJQK"[self.rank]
        if (not self.print_ts) and s == "T":
            s = "10"
        return s

    def suit_s(self):
        return "CSHD"[self.suit];

    def to_s(self):
        if self.empty:
            return "-"
        ret = ""
        ret = ret + self.rank_s()
        ret = ret + self.suit_s()
        if self.flipped:
            ret = "<" + ret + ">"

        return ret

    def found_s(self):
        return self.suit_s() + "-" + self.rank_s()

    def flip(self, flipped=True):
        new_card = Card(self.id, self.rank, self.suit, self.print_ts)
        new_card.flipped = flipped
        return new_card

    def is_empty(self):
        return self.empty

class Columns:

    def __init__(self, num):
        self.num = num
        cols = []
        for i in range(num):
            cols.append([])

        self.cols = cols

    def add(self, idx, card):
        self.cols[idx].append(card)

    def rev(self):
        self.cols.reverse()

    def output(self):
        s = ''
        for column in self.cols:
            s += column_to_string(column) + "\n"
        return s

class Board:
    def __init__(self, num_columns, with_freecells=False,
            with_talon=False, with_foundations=False):
        self.with_freecells = with_freecells
        self.with_talon = with_talon
        self.with_foundations = with_foundations
        self.columns = Columns(num_columns)
        if (self.with_freecells):
            self.freecells = []
        if (self.with_talon):
            self.talon = []
        if (self.with_foundations):
            self.foundations = map(lambda s:empty_card(),range(4))

    def reverse_cols(self):
        return self.columns.rev()

    def add(self, idx, card):
        return self.columns.add(idx, card)

    def print_freecells(self):
        return "FC: " + column_to_string(self.freecells)

    def print_talon(self):
        return "Talon: " + column_to_string(self.talon)

    def print_foundations(self):
        cells = []
        for f in [2,0,3,1]:
            if not self.foundations[f].is_empty():
                cells.append(self.foundations[f].found_s())

        if len(cells):
            return "Foundations:" + ("".join(map(lambda s: " "+s, cells)))

    def output(self):
        s = ''
        if (self.with_talon):
            s += self.print_talon() + "\n"
        if (self.with_foundations):
            s += self.print_foundations() + "\n"
        if (self.with_freecells):
            s += self.print_freecells() + "\n"
        s += self.columns.output()

        return s

    def add_freecell(self, card):
        if not self.with_freecells:
            raise AttributeError("Layout does not have freecells!")
        self.freecells.append(card)

    def add_talon(self, card):
        if not self.with_talon:
            raise AttributeError("Layout does not have a talon!")

        self.talon.append(card)

    def put_into_founds(self, card):
        if not self.with_foundations:
            raise AttributeError("Layout does not have foundations!")

        if ((self.foundations[card.suit].rank+1) == card.rank):
            self.foundations[card.suit] = card
            return True
        else:
            return False
        self.talon.append(card)


def empty_card():
    ret = Card(0,0,0,1)
    ret.empty = True
    return ret

def createCards(num_decks, print_ts):
    cards = []
    for deck in range(num_decks):
        id = 0
        for suit in range(4):
            for rank in range(13):
                cards.append(Card(id, rank+1, suit, print_ts))
                id = id + 1
    return cards

def column_to_list_of_strings(col):
    return map( lambda c: c.to_s(), col)

def column_to_string(col):
    return " ".join(column_to_list_of_strings(col))

def flip_card(card_str, flip):
    if flip:
        return "<" + card_str + ">"
    else:
        return card_str


def shuffle(orig_cards, rand):
    shuffled_cards = list(orig_cards)
    if isinstance(rand, LCRandom31) and len(shuffled_cards) == 52:
        # FreeCell mode
        fcards = []
        for i in range(13):
            for j in (0, 39, 26, 13):
                fcards.append(shuffled_cards[i + j])
        shuffled_cards = fcards
    # rand.shuffle works in place
    rand.shuffle(shuffled_cards)
    return shuffled_cards

class Game:
    REVERSE_MAP = \
        {
                "freecell":
                [ "freecell", "forecell", "bakers_game",
        "ko_bakers_game", "kings_only_bakers_game", "relaxed_freecell",
        "eight_off" ],
                "der_katz":
                [ "der_katz", "der_katzenschwantz", "die_schlange"],
                "seahaven":
                [ "seahaven_towers", "seahaven", "relaxed_seahaven", "relaxed_seahaven_towers" ],
                "bakers_dozen" : None,
                "gypsy" : None,
                "klondike" : [ "klondike", "klondike_by_threes", "casino_klondike", "small_harp", "thumb_and_pouch", "vegas_klondike", "whitehead" ],
                "simple_simon" : None,
                "yukon" : None,
                "beleaguered_castle" : [ "beleaguered_castle", "streets_and_alleys", "citadel" ],
                "fan" : None,
                "black_hole" : None,
                "all_in_a_row" : None,
        }

    def __init__(self, game_id, rand, print_ts):
        mymap = {}
        for k in self.REVERSE_MAP.keys():
            if self.REVERSE_MAP[k] is None:
                mymap[k] = k
            else:
                for alias in self.REVERSE_MAP[k]:
                    mymap[alias] = k
        self.games_map = mymap
        self.game_id = game_id
        self.print_ts = print_ts
        self.rand = rand

    def print_layout(self):
        game_class = self.lookup()

        if not game_class:
            raise ValueError("Unknown game type " + self.game_id + "\n")

        self.deal()

        getattr(self, game_class)()

        return self.board.output()

    def lookup(self):
        return self.games_map[self.game_id];

    def is_two_decks(self):
        return self.game_id in ("der_katz", "der_katzenschwantz", "die_schlange", "gypsy")

    def get_num_decks(self):
        if self.is_two_decks():
            return 2
        else:
            return 1

    def deal(self):
        orig_cards = createCards(self.get_num_decks(), self.print_ts)

        orig_cards = shuffle(orig_cards, self.rand)

        cards = orig_cards
        cards.reverse()

        self.cards = cards
        self.card_idx = 0
        return True

    def __iter__(self):
        return self

    def no_more_cards(self):
        return self.card_idx >= len(self.cards)

    def next(self):
        if self.no_more_cards():
            raise StopIteration
        c = self.cards[self.card_idx]
        self.card_idx = self.card_idx + 1
        return c

    def new_cards(self, cards):
        self.cards = cards
        self.card_idx = 0

    def add(self, idx, card):
        return self.board.add(idx, card)

    def add_freecell(self, card):
        return self.board.add_freecell(card)

    def cyclical_deal(game, num_cards, num_cols, flipped=False):
        for i in range(num_cards):
            game.add(i%num_cols, game.next().flip(flipped=flipped))
        return i

    def add_all_to_talon(game):
        for card in game:
            game.board.add_talon(card)

    ### These are the games variants:
    ### Each one is a callback.
    def der_katz(game):
        if (game.game_id == "die_schlange"):
            return "Foundations: H-A S-A D-A C-A H-A S-A D-A C-A"

        game.board = Board(9)
        col_idx = 0

        for card in game:
            if card.is_king():
                col_idx = col_idx + 1
            if not ((game.game_id == "die_schlange") and (card.rank == 1)):
                game.add(col_idx, card)

    def freecell(game):
        is_fc = (game.game_id in ('forecell', 'eight_off'))

        game.board = Board(8, with_freecells=is_fc)

        if is_fc:
            game.cyclical_deal(48, 8)
            for card in game:
                game.add_freecell(card)
                if game.game_id == "eight_off":
                    game.add_freecell(empty_card())
        else:
            game.cyclical_deal(52, 8)

    def seahaven(game):
        game.board = Board(10, with_freecells=True)

        game.add_freecell(empty_card())

        game.cyclical_deal(50, 10)

        for card in game:
            game.add_freecell(card)

    def bakers_dozen(game):
        i, n = 0, 13
        kings = []
        cards = game.cards
        cards.reverse()
        for c in cards:
            if c.is_king():
                kings.append(i)
            i = i + 1
        for i in kings:
            j = i % n
            while j < i:
                if not cards[j].is_king():
                    cards[i], cards[j] = cards[j], cards[i]
                    break
                j = j + n

        game.new_cards(cards)

        game.board = Board(13)

        game.cyclical_deal(52, 13)

    def gypsy(game):
        num_cols = 8
        game.board = Board(num_cols, with_talon=True)

        game.cyclical_deal(num_cols*2, num_cols, flipped=True)
        game.cyclical_deal(num_cols, num_cols, flipped=False)

        game.add_all_to_talon()

    def klondike(game):
        num_cols = 7
        game.board = Board(num_cols, with_talon=True)

        for r in range(1,num_cols):
            for s in range(num_cols-r):
                game.add(s, game.next().flip())

        game.cyclical_deal(num_cols, num_cols)

        game.add_all_to_talon()

        if not (game.game_id == "small_harp"):
            game.board.reverse_cols()

    def simple_simon(game):
        game.board = Board(10)

        num_cards = 9

        while num_cards >= 3:
            for s in range(num_cards):
                game.add(s, game.next())
            num_cards = num_cards - 1

        for s in range(10):
            game.add(s, game.next())

    def fan(game):
        game.board = Board(18)

        game.cyclical_deal(52-1, 17)

        game.add(17, game.next())

    def _shuffleHookMoveSorter(self, cards, func, ncards):
        # note that we reverse the cards, so that smaller sort_orders
        # will be nearer to the top of the Talon
        sitems, i = [], len(cards)
        for c in cards[:]:
            select, sort_order = func(c)
            if select:
                cards.remove(c)
                sitems.append((sort_order, i, c))
                if len(sitems) >= ncards:
                    break
            i = i - 1
        sitems.sort()
        sitems.reverse()
        scards = map(lambda item: item[2], sitems)
        return cards, scards

    def _shuffleHookMoveToBottom(self, cards, func, ncards=999999):
        # move cards to bottom of the Talon (i.e. last cards to be dealt)
        cards, scards = self._shuffleHookMoveSorter(cards, func, ncards)
        ret = scards + cards
        return ret

    def _shuffleHookMoveToTop(self, cards, func, ncards=999999):
        # move cards to top of the Talon (i.e. last cards to be dealt)
        cards, scards = self._shuffleHookMoveSorter(cards, func, ncards)
        return cards + scards

    def black_hole(game):
        game.board = Board(17)

        # move Ace to bottom of the Talon (i.e. last cards to be dealt)
        game.cards = game._shuffleHookMoveToBottom(game.cards, lambda c: (c.id == 13, c.suit), 1)
        game.next()
        game.cyclical_deal(52-1, 17)

        return "Foundations: AS"

    def all_in_a_row(game):
        game.board = Board(13)

        # move Ace to bottom of the Talon (i.e. last cards to be dealt)
        game.cards = game._shuffleHookMoveToTop(game.cards, lambda c: (c.id == 13, c.suit), 1)
        game.cyclical_deal(52, 13)
        return "Foundations: -"

    def beleaguered_castle(game):
        aces_up = game.game_id in ("beleaguered_castle", "citadel")

        game.board = Board(8, with_foundations=True)

        if aces_up:
            new_cards = []

            for c in game:
                if c.is_ace():
                    game.board.put_into_founds(c)
                else:
                    new_cards.append(c)

            game.new_cards(new_cards)


        for i in range(6):
            for s in range(8):
                c = game.next()
                if (game.game_id == "citadel") and game.board.put_into_founds(c):
                    # Already dealt with this card
                    True
                else:
                    game.add(s, c)
            if game.no_more_cards():
                break

        if (game.game_id == "streets_and_alleys"):
            game.cyclical_deal(4, 4)

    def yukon(game):
        num_cols = 7
        game.board = Board(num_cols)

        for i in range(1, num_cols):
            for j in range(i, num_cols):
                game.add(j, game.next().flip())

        for i in range(4):
            for j in range(1,num_cols):
                game.add(j, game.next())

        game.cyclical_deal(num_cols, num_cols)

def shlomif_main(args):

    plan(8)

    rand = constructRandom('24')
    game = Game("freecell", rand, True)
    # TEST
    got_s = game.print_layout()
    ok (got_s == '''4C 2C 9C 8C QS 4S 2H
5H QH 3C AC 3H 4H QD
QC 9S 6H 9H 3S KS 3D
5D 2S JC 5C JH 6D AS
2D KD TH TC TD 8D
7H JS KH TS KC 7C
AH 5S 6S AD 8H JD
7S 6C 7D 4D 8S 9D
''',
    'Deal 24',
);

    rand = constructRandom('ms123456')
    game = Game("freecell", rand, True)
    # TEST
    got_s = game.print_layout()
    ok (got_s == '''QD TC AS KC AH KH 6H
6D TD 8D TH 7C 2H 9C
AC AD 5C 5H 8C 9H 9D
JS 8S 4D 4C 2S 7D 3C
7H 7S 9S 2C JC 5S
5D 3S 3D 3H KD JH
6C QS 4S 2D KS TS
JD QH 6S 4H QC 8H
''',
    'Microsoft Deal 123456',
);

    rand = constructRandom('123456')
    game = Game("freecell", rand, True)
    # TEST
    got_s = game.print_layout()
    ok (got_s == '''3D 6C AS TS QC 8D 4D
2D TC 4H JD TD 2H 5C
2C 8S AH KD KH 5S 7C
9C 8C QH 3C 5D 9S QD
AC 9D 7H 6D KS JH
6H TH 8H QS 7D JC
4C 2S 3S 6S 5H 3H
KC JS 9H 4S 7S AD
''',
    'PySolFC deal No. 123456',
);

    rand = constructRandom('ms3000000000')
    game = Game("freecell", rand, True)
    # TEST
    got_s = game.print_layout()
    ok (got_s == '''8D TS JS TD JH JD JC
4D QS TH AD 4S TC 3C
9H KH QH 4C 5C KD AS
9D 5D 8S 4H KS 6S 9S
6H 2S 7H 3D KC 2C
9C 7C QC 7S QD 7D
6C 3H 8H AC 6D 3S
8C AH 2H 5H 2D 5S
''',
    'Microsoft Deal #3E9 - long seed.',
);

    rand = constructRandom('ms6000000000')
    game = Game("freecell", rand, True)
    # TEST
    got_s = game.print_layout()
    ok (got_s == '''2D 2C QS 8D KD 8C 4C
3D AH 2H 4H TS 6H QD
4D JS AD 6S JH JC JD
KH 3H KS AS TC 5D AC
TD 7C 9C 7H 3C 3S
QH 9H 9D 5S 7S 6C
5C 5H 2S KC 9S 4S
6D QC 8S TH 7D 8H
''',
    'Microsoft Deal #6E9 - extra long seed.',
);

    inp = 'ms12345678'
    got = random__long2str(random__str2long(inp))

    # TEST
    ok (got == inp, 'long2str ms roundtrip.')

    inp = '246007891097'
    got = random__long2str(random__str2long(inp))

    # TEST
    ok (got == inp, 'long2str PySolFC roundtrip.')

    proto_inp = '246007891097'
    inp = random__str2long(proto_inp)
    got = random__str2long(random__long2str(inp))

    # TEST
    ok (got == inp, 'str2long PySolFC roundtrip.')

if __name__ == "__main__":
    sys.exit(shlomif_main(sys.argv))
