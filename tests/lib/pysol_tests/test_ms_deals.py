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
import unittest

from pysol_cards.cards import CardRenderer
from pysol_cards.deal_game import Game
from pysol_cards.random import random__int2str, random__str2int
from pysol_cards.random_base import RandomBase

# So the localpaths will be overrided.
from pysollib.pysolrandom import construct_random

# PySol imports

# /***********************************************************************
# // Abstract PySol Random number generator.
# //
# // We use a seed of type long in the range [0, MAX_SEED].
# ************************************************************************/


ren = CardRenderer(True)


class MsDealsTests(unittest.TestCase):
    def _cmp_board(self, got_s, expected_s, blurb):
        if not self.assertEqual(got_s, expected_s, blurb):
            return False
        return True

    def test_main(self):

        def test_24(blurb):
            game = Game("freecell", 24, RandomBase.DEALS_PYSOLFC)
            got_s = game.calc_layout_string(ren)
            self.assertEqual(got_s, '''4C 2C 9C 8C QS 4S 2H
5H QH 3C AC 3H 4H QD
QC 9S 6H 9H 3S KS 3D
5D 2S JC 5C JH 6D AS
2D KD TH TC TD 8D
7H JS KH TS KC 7C
AH 5S 6S AD 8H JD
7S 6C 7D 4D 8S 9D
''', blurb)

        # TEST
        test_24('Deal 24')

        game = Game("freecell", 123456, RandomBase.DEALS_MS)
        # TEST
        got_s = game.calc_layout_string(ren)
        self.assertEqual(got_s, '''QD TC AS KC AH KH 6H
6D TD 8D TH 7C 2H 9C
AC AD 5C 5H 8C 9H 9D
JS 8S 4D 4C 2S 7D 3C
7H 7S 9S 2C JC 5S
5D 3S 3D 3H KD JH
6C QS 4S 2D KS TS
JD QH 6S 4H QC 8H
''', 'Microsoft Deal 123456')

        game = Game("freecell", 123456, True)
        # TEST
        self._cmp_board(game.calc_layout_string(ren), '''3D 6C AS TS QC 8D 4D
2D TC 4H JD TD 2H 5C
2C 8S AH KD KH 5S 7C
9C 8C QH 3C 5D 9S QD
AC 9D 7H 6D KS JH
6H TH 8H QS 7D JC
4C 2S 3S 6S 5H 3H
KC JS 9H 4S 7S AD
''', 'PySolFC deal No. 123456')

        rand = construct_random('ms3000000000')
        self.assertEqual(rand.getSeedAsStr(), 'ms3000000000')
        game = Game("freecell", 3000000000, RandomBase.DEALS_MS)
        # TEST
        self._cmp_board(game.calc_layout_string(ren), '''8D TS JS TD JH JD JC
4D QS TH AD 4S TC 3C
9H KH QH 4C 5C KD AS
9D 5D 8S 4H KS 6S 9S
6H 2S 7H 3D KC 2C
9C 7C QC 7S QD 7D
6C 3H 8H AC 6D 3S
8C AH 2H 5H 2D 5S
''', 'Microsoft Deal #3E9 - long seed.')

        rand = construct_random('ms6000000000')
        game = Game("freecell", 6000000000, RandomBase.DEALS_MS)
        # TEST
        got_s = game.calc_layout_string(ren)
        self.assertEqual(got_s, '''2D 2C QS 8D KD 8C 4C
3D AH 2H 4H TS 6H QD
4D JS AD 6S JH JC JD
KH 3H KS AS TC 5D AC
TD 7C 9C 7H 3C 3S
QH 9H 9D 5S 7S 6C
5C 5H 2S KC 9S 4S
6D QC 8S TH 7D 8H
''', 'Microsoft Deal #6E9 - extra long seed.')

        inp = 'ms12345678'
        got = random__int2str(random__str2int(inp))

        # TEST
        self.assertEqual(got, inp, 'long2str ms roundtrip.')

        inp = '246007891097'
        got = random__int2str(random__str2int(inp))

        # TEST
        self.assertEqual(got, inp, 'long2str PySolFC roundtrip.')

        proto_inp = '246007891097'
        inp = random__str2int(proto_inp)
        got = random__str2int(random__int2str(inp))

        # TEST
        self.assertEqual(got, inp, 'str2long PySolFC roundtrip.')

        rand = construct_random('ms100000')
        seed = rand.increaseSeed(rand.initial_seed)
        seed = rand.str(seed)
        # TEST
        self.assertEqual(seed, 'ms100001', 'increaseSeed for ms deals')
        rand = construct_random(seed)
        game = Game("freecell", int(seed[2:]), RandomBase.DEALS_MS)
        # TEST
        self._cmp_board(game.calc_layout_string(ren), '''5S AH 4H TD 4S JD JS
3C 8C 4C AC JC AS QS
7C QH 2D QD 8S 9D AD
KS 7S 5H 3H TS 3S 5D
9S 7H KC TH 8D 6S
5C KD 9H 2H 2S 6D
9C JH 8H 3D 4D QC
KH 6H 6C TC 2C 7D
''', 'ms100001')

        seed = 24000024
        rand = construct_random(str(seed))
        expected0 = rand.randint(0, 100)
        expected1 = rand.randint(0, 100)
        rand.reset()
        got0 = rand.randint(0, 100)
        got1 = rand.randint(0, 100)
        # TEST
        self.assertEqual(
            [got0, got1, ],
            [expected0, expected1, ],
            "same results after reset()",)
