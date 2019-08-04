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


# imports
import re
import time

import pysol_cards

from pysollib.mfxutil import SubclassResponsibility
try:
    import random2
except ImportError:
    raise ImportError(
        "You need to install " +
        "https://pypi.python.org/pypi/random2 using pip or similar.")

assert ((pysol_cards.VERSION if 'VERSION' in pysol_cards.__dict__
         else (0, 0, 0)) >= (0, 8, 5))
from pysol_cards.random_base import RandomBase  # noqa: I100
from pysol_cards.random import match_ms_deal_prefix  # noqa: I100


# ************************************************************************
# * Abstract class for PySol Random number generator.
# *
# * We use a seed of type int in the range [0, MAX_SEED].
# ************************************************************************


class BasicRandom(RandomBase):
    def reset(self):
        raise SubclassResponsibility

    def _getRandomSeed(self):
        t = int(time.time() * 256.0)
        t = (t ^ (t >> 24)) % (self.MAX_SEED + 1)
        return t


# ************************************************************************
# * Mersenne Twister random number generator
# * uses the standard python module `random'
# ************************************************************************

class MTRandom(BasicRandom, random2.Random):

    def __init__(self, seed=None):
        if seed is None:
            seed = self._getRandomSeed()
        BasicRandom.__init__(self)
        random2.Random.__init__(self, seed)
        self.initial_seed = seed
        self.initial_state = self.getstate()
        self.origin = self.ORIGIN_UNKNOWN

    def reset(self):
        self.setstate(self.initial_state)


# ************************************************************************
# * Wichman-Hill random number generator
# * uses the standard python module `random'
# ************************************************************************

# class WHRandom(BasicRandom, random.WichmannHill):
#
#     def __init__(self, seed=None):
#         if seed is None:
#             seed = self._getRandomSeed()
#         BasicRandom.__init__(self)
#         random.WichmannHill.__init__(self, seed)
#         self.initial_seed = seed
#         self.initial_state = self.getstate()
#         self.origin = self.ORIGIN_UNKNOWN
#
#     def reset(self):
#         self.setstate(self.initial_state)

# ************************************************************************
# * Abstract class for LC Random number generators.
# ************************************************************************


class MFXRandom(BasicRandom):

    def __init__(self, seed=None):
        BasicRandom.__init__(self)
        if seed is None:
            seed = self._getRandomSeed()
        self.initial_seed = self.setSeed(seed)
        self.origin = self.ORIGIN_UNKNOWN

    def reset(self):
        self.seed = self.initial_seed

    def getSeed(self):
        return self.seed

    def setSeed(self, seed):
        seed = int(seed)
        if not (0 <= seed <= self.MAX_SEED):
            raise ValueError("seed out of range")
        self.seed = seed
        return seed

    def getstate(self):
        return self.seed

    def setstate(self, state):
        self.seed = state

    #
    # implementation
    #

    def choice(self, seq):
        return seq[int(self.random() * len(seq))]

    def randrange(self, a, b):
        return self.randint(a, b-1)


# ************************************************************************
# * Linear Congruential random generator
# *
# * Knuth, Donald.E., "The Art of Computer Programming,", Vol 2,
# * Seminumerical Algorithms, Third Edition, Addison-Wesley, 1998,
# * p. 106 (line 26) & p. 108
# ************************************************************************

class LCRandom64(MFXRandom):

    def random(self):
        self.seed = (self.seed*int('6364136223846793005') + 1) & self.MAX_SEED
        return ((self.seed >> 21) & 0x7fffffff) / 2147483648.0


MS_LONG_BIT = (1 << 1000)
CUSTOM_BIT = (1 << 999)


class CustomRandom(BasicRandom):
    def __init__(self):
        self.initial_seed = self.seed = MS_LONG_BIT | CUSTOM_BIT
        self.origin = self.ORIGIN_UNKNOWN
        self.setSeedAsStr('Custom')

    def reset(self):
        pass

    def shuffle(self, seq):
        pass

    def getstate(self):
        return self.seed

    def setstate(self, state):
        self.seed = state

# ************************************************************************
# * Linear Congruential random generator
# * In PySol this is only used for 0 <= seed <= 32000
# * for Windows FreeCell compatibility
# ************************************************************************


class LCRandom31(MFXRandom):
    MAX_SEED = int('0x1ffffffff', 0)          # 33 bits

    def increaseSeed(self, seed):
        ret = super(LCRandom31, self).increaseSeed(seed)
        return "ms{}".format(ret)

    def getSeedStr(self):
        return "ms" + str(self.initial_seed)

    def str(self, seed):
        if match_ms_deal_prefix("{}".format(seed)) is None:
            return "%05d" % int(seed)
        return seed

    def setSeed(self, seed):
        seed = int(seed)
        self.seed = seed
        if not (0 <= seed <= self.MAX_SEED):
            raise ValueError("seed out of range")
        self.seedx = (seed if (seed < int('0x100000000', 0)) else
                      (seed - int('0x100000000', 0)))
        return seed

    def _rando(self):
        self.seedx = (self.seedx*214013 + 2531011) & self.MAX_SEED
        return ((self.seedx >> 16) & 0x7fff)

    def _randp(self):
        self.seedx = (self.seedx*214013 + 2531011) & self.MAX_SEED
        return ((self.seedx >> 16) & 0xffff)

    def randint(self, a, b):
        if self.seed < 0x100000000:
            ret = self._rando()
            ret = (ret if (self.seed < 0x80000000) else (ret | 0x8000))
        else:
            ret = self._randp() + 1

        return a + (ret % (b+1-a))

    def reset(self):
        self.setSeed(self.seed)


# select
# PysolRandom = LCRandom64
# PysolRandom = WHRandom
PysolRandom = MTRandom


# ************************************************************************
# * PySol support code
# ************************************************************************


# construct Random from seed string
def constructRandom(s):
    if s == 'Custom':
        return CustomRandom()
    m = match_ms_deal_prefix(s)
    if m is not None:
        seed = m
        if 0 <= seed <= LCRandom31.MAX_SEED:
            ret = LCRandom31(seed)
            ret.setSeedAsStr(s)
            return ret
        else:
            raise ValueError("ms seed out of range")
    # cut off "L" from possible conversion to int
    s = re.sub(r"L$", "", str(s))
    s = re.sub(r"[\s\#\-\_\.\,]", "", s.lower())
    if not s:
        return None
    seed = int(s)
    if 0 <= seed < 32000:
        return LCRandom31(seed)
    return PysolRandom(seed)


def random__str2long(s):
    if s == 'Custom':
        return CUSTOM_BIT | MS_LONG_BIT
    m = match_ms_deal_prefix(s)
    if m is not None:
        return (m | MS_LONG_BIT)
    else:
        return int(s)


def random__long2str(l):
    if ((l & MS_LONG_BIT) != 0):
        if ((l & CUSTOM_BIT) != 0):
            return 'Custom'
        return "ms" + str(l & (~ MS_LONG_BIT))
    else:
        return str(l)


# test
if __name__ == '__main__':
    r = constructRandom('12345')
    print(r.randint(0, 100))
    print(r.random())
    print(type(r))
