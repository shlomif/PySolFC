## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
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


# imports
import sys, re, time
import random
from mfxutil import SubclassResponsibility


# /***********************************************************************
# // system based random (need python >= 2.3)
# ************************************************************************/

class SysRandom(random.Random):
    #MAX_SEED = 0L
    #MAX_SEED = 0xffffffffffffffffL  # 64 bits
    MAX_SEED = 100000000000000000000L # 20 digits

    ORIGIN_UNKNOWN  = 0
    ORIGIN_RANDOM   = 1
    ORIGIN_PREVIEW  = 2         # random from preview
    ORIGIN_SELECTED = 3         # manually entered
    ORIGIN_NEXT_GAME = 4        # "Next game number"

    def __init__(self, seed=None):
        if seed is None:
            seed = self._getRandomSeed()
        random.Random.__init__(self, seed)
        self.initial_seed = seed
        self.initial_state = self.getstate()
        self.origin = self.ORIGIN_UNKNOWN

    def __str__(self):
        return self.str(self.initial_seed)

    def str(self, seed):
        return '%020d' % seed

    def reset(self):
        self.setstate(self.initial_state)

    def copy(self):
        random = self.__class__(0L)
        random.__dict__.update(self.__dict__)
        return random

    def increaseSeed(self, seed):
        if seed < self.MAX_SEED:
            return seed + 1L
        return 0L

    def _getRandomSeed(self):
        t = long(time.time() * 256.0)
        t = (t ^ (t >> 24)) % (self.MAX_SEED + 1L)
        return t


# /***********************************************************************
# // Abstract PySol Random number generator.
# //
# // We use a seed of type long in the range [0, MAX_SEED].
# ************************************************************************/

class MFXRandom:
    MAX_SEED = 0L

    ORIGIN_UNKNOWN  = 0
    ORIGIN_RANDOM   = 1
    ORIGIN_PREVIEW  = 2         # random from preview
    ORIGIN_SELECTED = 3         # manually entered
    ORIGIN_NEXT_GAME = 4        # "Next game number"

    def __init__(self, seed=None):
        if seed is None:
            seed = self._getRandomSeed()
        self.initial_seed = self.setSeed(seed)
        self.origin = self.ORIGIN_UNKNOWN

    def __str__(self):
        return self.str(self.initial_seed)

    def reset(self):
        self.seed = self.initial_seed

    def getSeed(self):
        return self.seed

    def setSeed(self, seed):
        seed = self._convertSeed(seed)
        if not isinstance(seed, long):
            raise TypeError, "seeds must be longs"
        if not (0L <= seed <= self.MAX_SEED):
            raise ValueError, "seed out of range"
        self.seed = seed
        return seed

    def getstate(self):
        return self.seed

    def setstate(self, state):
        self.seed = state

    def copy(self):
        random = self.__class__(0L)
        random.__dict__.update(self.__dict__)
        return random

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

    #
    # subclass responsibility
    #

    # Get the next random number in the range [0.0, 1.0).
    def random(self):
        raise SubclassResponsibility

    #
    # subclass overrideable
    #

    def _convertSeed(self, seed):
        return long(seed)

    def increaseSeed(self, seed):
        if seed < self.MAX_SEED:
            return seed + 1L
        return 0L

    def _getRandomSeed(self):
        t = long(time.time() * 256.0)
        t = (t ^ (t >> 24)) % (self.MAX_SEED + 1L)
        return t

    #
    # shuffle
    #   see: Knuth, Vol. 2, Chapter 3.4.2, Algorithm P
    #   see: FAQ of sci.crypt: "How do I shuffle cards ?"
    #

    def shuffle(self, seq):
        n = len(seq) - 1
        while n > 0:
            j = self.randint(0, n)
            seq[n], seq[j] = seq[j], seq[n]
            n = n - 1


# /***********************************************************************
# // Linear Congruential random generator
# //
# // Knuth, Donald.E., "The Art of Computer Programming,", Vol 2,
# // Seminumerical Algorithms, Third Edition, Addison-Wesley, 1998,
# // p. 106 (line 26) & p. 108
# ************************************************************************/

class LCRandom64(MFXRandom):
    MAX_SEED = 0xffffffffffffffffL  # 64 bits

    def str(self, seed):
        s = repr(long(seed))
        if s[-1:] == "L":
            s = s[:-1]
        s = "0"*(20-len(s)) + s
        return s

    def random(self):
        self.seed = (self.seed*6364136223846793005L + 1L) & self.MAX_SEED
        return ((self.seed >> 21) & 0x7fffffffL) / 2147483648.0


# /***********************************************************************
# // Linear Congruential random generator
# // In PySol this is only used for 0 <= seed <= 32000.
# ************************************************************************/

class LCRandom31(MFXRandom):
    MAX_SEED = 0x7fffffffL          # 31 bits

    def str(self, seed):
        return "%05d" % int(seed)

    def random(self):
        self.seed = (self.seed*214013L + 2531011L) & self.MAX_SEED
        return (self.seed >> 16) / 32768.0

    def randint(self, a, b):
        self.seed = (self.seed*214013L + 2531011L) & self.MAX_SEED
        return a + (int(self.seed >> 16) % (b+1-a))


# select
if sys.version_info >= (2,3):
    PysolRandom = SysRandom
else:
    PysolRandom = LCRandom64


# /***********************************************************************
# // PySol support code
# ************************************************************************/

# construct Random from seed string
def constructRandom(s):
    s = re.sub(r"L$", "", str(s))   # cut off "L" from possible conversion to long
    s = re.sub(r"[\s\#\-\_\.\,]", "", s.lower())
    if not s:
        return None
    seed = long(s)
    if 0 <= seed <= 32000:
        return LCRandom31(seed)
    return PysolRandom(seed)

# test
if __name__ == '__main__':
    _, r = constructRandom('12345')
    print r.randint(0, 100)
    print r.random()
    print type(r)


