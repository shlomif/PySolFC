#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
#  Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
#  Copyright (C) 2003 Mt. Hood Playing Card Co.
#  Copyright (C) 2005-2009 Skomoroh
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

import re

from pysollib.mfxutil import print_err
from pysollib.resource import Cardset, CardsetConfig


def read_cardset_config(dirname, filename):
    """Parse a cardset config file and produce a Cardset object.

    This function returns None if any errors occurred.
    """
    with open(filename, "rt") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    if not lines[0].startswith("PySol"):
        return None
    config = parse_cardset_config(lines)
    if not config:
        print_err('invalid cardset: %s' % filename)
        return None
    cs = Cardset()
    cs.dir = dirname
    cs.update(config.__dict__)
    return cs


def parse_cardset_config(line):
    def perr(line_no, field=None, msg=''):
        if field:
            print_err('cannot parse cardset config: line #%d, field #%d: %s'
                      % (line_no, field, msg))
        else:
            print_err('cannot parse cardset config: line #%d: %s'
                      % (line_no, msg))

    cs = CardsetConfig()
    if len(line) < 6:
        perr(1, msg='not enough lines in file')
        return None
    # line[0]: magic identifier, possible version information
    fields = [f.strip() for f in line[0].split(';')]
    if len(fields) >= 2:
        m = re.search(r"^(\d+)$", fields[1])
        if m:
            cs.version = int(m.group(1))
    if cs.version >= 3:
        if len(fields) < 5:
            perr(1, msg='not enough fields')
            return None
        cs.ext = fields[2]
        m = re.search(r"^(\d+)$", fields[3])
        if not m:
            perr(1, 3, 'not integer')
            return None
        cs.type = int(m.group(1))
        m = re.search(r"^(\d+)$", fields[4])
        if not m:
            perr(1, 4, 'not integer')
            return None
        cs.ncards = int(m.group(1))
    if cs.version >= 4:
        if len(fields) < 6:
            perr(1, msg='not enough fields')
            return None
        styles = fields[5].split(",")
        for s in styles:
            m = re.search(r"^\s*(\d+)\s*$", s)
            if not m:
                perr(1, 5, 'not integer')
                return None
            s = int(m.group(1))
            if s not in cs.styles:
                cs.styles.append(s)
    if cs.version >= 5:
        if len(fields) < 7:
            perr(1, msg='not enough fields')
            return None
        m = re.search(r"^(\d+)$", fields[6])
        if not m:
            perr(1, 6, 'not integer')
            return None
        cs.year = int(m.group(1))
    if len(cs.ext) < 2 or cs.ext[0] != ".":
        perr(1, msg='specifies an invalid file extension')
        return None
    # line[1]: identifier/name
    if not line[1]:
        perr(2, msg='unexpected empty line')
        return None
    cs.ident = line[1]
    m = re.search(r"^(.*;)?([^;]+)$", cs.ident)
    if not m:
        perr(2, msg='invalid format')
        return None
    cs.name = m.group(2).strip()
    # line[2]: CARDW, CARDH, CARDD
    m = re.search(r"^(\d+)\s+(\d+)\s+(\d+)", line[2])
    if not m:
        perr(3, msg='invalid format')
        return None
    cs.CARDW, cs.CARDH, cs.CARDD = \
        int(m.group(1)), int(m.group(2)), int(m.group(3))
    # line[3]: CARD_UP_YOFFSET, CARD_DOWN_YOFFSET,
    # SHADOW_XOFFSET, SHADOW_YOFFSET
    m = re.search(r"^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line[3])
    if not m:
        perr(4, msg='invalid format')
        return None
    cs.CARD_XOFFSET = int(m.group(1))
    cs.CARD_YOFFSET = int(m.group(2))
    cs.SHADOW_XOFFSET = int(m.group(3))
    cs.SHADOW_YOFFSET = int(m.group(4))
    # line[4]: default background
    back = line[4]
    if not back:
        perr(5, msg='unexpected empty line')
        return None
    # line[5]: all available backgrounds
    cs.backnames = [f.strip() for f in line[5].split(';')]
    if back in cs.backnames:
        cs.backindex = cs.backnames.index(back)
    else:
        cs.backnames.insert(0, back)
        cs.backindex = 0

    # if cs.type != 1: print cs.type, cs.name
    return cs
