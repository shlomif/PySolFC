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

try:
    import pysol_cards
except ImportError:
    import sys
    sys.stderr.write(
        "Please install pysol_cards.py from \"PyPI\"\r\n" +
        "(e.g: using \"python3 -m pip install " +
        "--user --upgrade pysol_cards\"\r\n")
    sys.exit(1)
assert getattr(pysol_cards, 'VERSION', (0, 0, 0)) >= (0, 8, 17), (
    "Newer version of https://pypi.org/project/pysol-cards is required.")
import pysol_cards.random  # noqa: E402,I100
import pysol_cards.random_base  # noqa: E402,I100
from pysol_cards.random import LCRandom31  # noqa: E402,I100
from pysol_cards.random import match_ms_deal_prefix  # noqa: E402,I100
from pysol_cards.random import CUSTOM_BIT, MS_LONG_BIT  # noqa: E402,I100


class CustomRandom(pysol_cards.random_base.RandomBase):
    def __init__(self, seed=None):
        self.initial_seed = self.seed = MS_LONG_BIT | CUSTOM_BIT
        self.origin = self.ORIGIN_UNKNOWN
        self.setSeedAsStr('Custom')

    def reset(self):
        pass

    def shuffle(self, seq):
        pass


PysolRandom = pysol_cards.random.MTRandom


# ************************************************************************
# * PySol support code
# ************************************************************************


# construct Random from seed string
def construct_random(s):
    if s == 'Custom':
        return CustomRandom()
    m = match_ms_deal_prefix(s)
    if m is not None:
        seed = m
        if 0 <= seed <= LCRandom31.MAX_SEED:
            ret = LCRandom31(seed)
            # ret.setSeedAsStr(s)
            return ret
        raise ValueError("ms seed out of range")
    # cut off "L" from possible conversion to int
    s = re.sub(r"L$", "", str(s))
    s = re.sub(r"[\s\#\-\_\.\,]", "", s.lower())
    if not s:
        return None
    seed = int(s)
    if 0 <= seed < 32000:
        return LCRandom31(seed)
    # print("MTRandom", seed)
    ret = pysol_cards.random.MTRandom(seed)
    return ret
