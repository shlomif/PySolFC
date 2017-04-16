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
import sys
import re
import time
import random
from pysollib.mfxutil import SubclassResponsibility


if sys.version_info > (3,):
    long = int

# ************************************************************************
# * Abstract class for PySol Random number generator.
# *
# * We use a seed of type long in the range [0, MAX_SEED].
# ************************************************************************


class BasicRandom:
    # MAX_SEED = 0L
    # MAX_SEED = 0xffffffffffffffffL  # 64 bits
    MAX_SEED = long('100000000000000000000')  # 20 digits

    ORIGIN_UNKNOWN = 0
    ORIGIN_RANDOM = 1
    ORIGIN_PREVIEW = 2         # random from preview
    ORIGIN_SELECTED = 3         # manually entered
    ORIGIN_NEXT_GAME = 4        # "Next game number"

    def __init__(self):
        self.seed_as_string = None

    def getSeedStr(self):
        return str(self.initial_seed)

    def __str__(self):
        return self.str(self.initial_seed)

    def str(self, seed):
        return '%020d' % seed

    def reset(self):
        raise SubclassResponsibility

    def copy(self):
        random = self.__class__(long(0))
        random.__dict__.update(self.__dict__)
        return random

    def increaseSeed(self, seed):
        if seed < self.MAX_SEED:
            return seed + long(1)
        return long(0)

    def _getRandomSeed(self):
        t = long(time.time() * 256.0)
        t = (t ^ (t >> 24)) % (self.MAX_SEED + long(1))
        return t

    def setSeedAsStr(self, new_s):
        self.seed_as_string = new_s

    def getSeedAsStr(self):
        if self.seed_as_string:
            return self.seed_as_string
        else:
            return str(self)


# ************************************************************************
# * Mersenne Twister random number generator
# * uses the standard python module `random'
# ************************************************************************

class MTRandom(BasicRandom, random.Random):

    def __init__(self, seed=None):
        if seed is None:
            seed = self._getRandomSeed()
        BasicRandom.__init__(self)
        random.Random.__init__(self, seed)
        self.initial_seed = seed
        self.initial_state = self.getstate()
        self.origin = self.ORIGIN_UNKNOWN

    def reset(self):
        self.setstate(self.initial_state)


# ************************************************************************
# * Wichman-Hill random number generator
# * uses the standard python module `random'
# ************************************************************************

class WHRandom(BasicRandom, random.WichmannHill):

    def __init__(self, seed=None):
        if seed is None:
            seed = self._getRandomSeed()
        BasicRandom.__init__(self)
        random.WichmannHill.__init__(self, seed)
        self.initial_seed = seed
        self.initial_state = self.getstate()
        self.origin = self.ORIGIN_UNKNOWN

    def reset(self):
        self.setstate(self.initial_state)

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
        seed = long(seed)
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

    # Get a random integer in the range [a, b] including both end points.
    def randint(self, a, b):
        return a + long(self.random() * (b+1-a))

    def randrange(self, a, b):
        return self.randint(a, b-1)

    def shuffle(self, seq):
        n = len(seq) - 1
        while n > 0:
            j = self.randint(0, n)
            seq[n], seq[j] = seq[j], seq[n]
            n -= 1


# ************************************************************************
# * Linear Congruential random generator
# *
# * Knuth, Donald.E., "The Art of Computer Programming,", Vol 2,
# * Seminumerical Algorithms, Third Edition, Addison-Wesley, 1998,
# * p. 106 (line 26) & p. 108
# ************************************************************************

class LCRandom64(MFXRandom):

    def random(self):
        self.seed = (self.seed*long('6364136223846793005') + 1) & self.MAX_SEED
        return ((self.seed >> 21) & 0x7fffffff) / 2147483648.0


# ************************************************************************
# * Linear Congruential random generator
# * In PySol this is only used for 0 <= seed <= 32000
# * for Windows FreeCell compatibility
# ************************************************************************

class LCRandom31(MFXRandom):
    MAX_SEED = long('0x1ffffffff', 0)          # 33 bits

    def getSeedStr(self):
        return "ms" + str(self.initial_seed)

    def str(self, seed):
        return "%05d" % int(seed)

    def setSeed(self, seed):
        seed = long(seed)
        self.seed = seed
        if not (0 <= seed <= self.MAX_SEED):
            raise ValueError("seed out of range")
        self.seedx = (seed if (seed < long('0x100000000', 0)) else
                      (seed - long('0x100000000', 0)))
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

    def shuffle(self, seq):
        n = len(seq) - 1
        while n > 0:
            j = self.randint(0, n)
            seq[n], seq[j] = seq[j], seq[n]
            n -= 1


# select
# PysolRandom = LCRandom64
# PysolRandom = WHRandom
PysolRandom = MTRandom


# ************************************************************************
# * PySol support code
# ************************************************************************

def _match_ms(s):
    """match an ms based seed string."""
    return re.match(r"ms([0-9]+)\n?\Z", s)


# construct Random from seed string
def constructRandom(s):
    m = _match_ms(s)
    if m:
        seed = long(m.group(1))
        if 0 <= seed <= LCRandom31.MAX_SEED:
            ret = LCRandom31(seed)
            ret.setSeedAsStr(s)
            return ret
        else:
            raise ValueError("ms seed out of range")
    # cut off "L" from possible conversion to long
    s = re.sub(r"L$", "", str(s))
    s = re.sub(r"[\s\#\-\_\.\,]", "", s.lower())
    if not s:
        return None
    seed = long(s)
    if 0 <= seed < 32000:
        return LCRandom31(seed)
    return PysolRandom(seed)


MS_LONG_BIT = (long(1) << 1000)


def random__str2long(s):
    m = _match_ms(s)
    if m:
        return (long(m.group(1)) | MS_LONG_BIT)
    else:
        return long(s)


def random__long2str(l):
    if ((l & MS_LONG_BIT) != 0):
        return "ms" + str(l & (~ MS_LONG_BIT))
    else:
        return str(l)


# test
if __name__ == '__main__':
    r = constructRandom('12345')
    print(r.randint(0, 100))
    print(r.random())
    print(type(r))
