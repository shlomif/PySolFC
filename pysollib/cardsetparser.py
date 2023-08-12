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

from pysollib.mfxutil import print_err
from pysollib.resource import Cardset, CardsetConfig


def _perr(line_no, field=None, msg=''):
    if field:
        print_err('cannot parse cardset config: line #%d, field #%d: %s'
                  % (line_no, field, msg))
    else:
        print_err('cannot parse cardset config: line #%d: %s' % (line_no, msg))


def read_cardset_config(dirname, filename):
    """Parse a cardset config file and produce a Cardset object.

    This function returns None if any errors occurred.
    """
    with open(filename, "rt") as f:
        lines_list = f.readlines()
    lines_list = [line.strip() for line in lines_list]
    if not lines_list[0].startswith("PySol"):
        return None
    config = parse_cardset_config(lines_list)
    if not config:
        print_err('invalid cardset: %s' % filename)
        return None
    cs = Cardset()
    cs.dir = dirname
    cs.update(config.__dict__)
    return cs


def parse_cardset_config(lines_list):
    cs = CardsetConfig()
    if len(lines_list) < 6:
        _perr(1, msg='not enough lines in file')
        return None
    # lines_list[0]: magic identifier, possible version information
    fields = [f.strip() for f in lines_list[0].split(';')]
    if len(fields) >= 2:
        try:
            cs.version = int(fields[1])
        except ValueError:
            # version 1 is implied
            cs.version = 1
    if cs.version >= 3:
        if len(fields) < 5:
            _perr(1, msg='not enough fields')
            return None
        cs.ext = fields[2]
        try:
            cs.type = int(fields[3])
        except ValueError:
            _perr(1, 3, 'not integer')
            return None
        try:
            cs.ncards = int(fields[4])
        except ValueError:
            _perr(1, 4, 'not integer')
            return None
    if cs.version >= 4:
        if len(fields) < 6:
            _perr(1, msg='not enough fields')
            return None
        try:
            styles = (int(s.strip()) for s in fields[5].split(","))
            cs.styles = list(set(styles))
        except ValueError:
            _perr(1, 5, 'not integer')
            return None
    if cs.version >= 5:
        if len(fields) < 7:
            _perr(1, msg='not enough fields')
            return None
        try:
            cs.year = int(fields[6])
        except ValueError:
            _perr(1, 6, 'not integer')
            return None
    if cs.version >= 7:
        if len(fields) < 9:
            _perr(1, msg='not enough fields')
            return None
        try:
            cs.subtype = int(fields[7])
        except ValueError:
            _perr(1, 7, 'not integer')
            return None
        try:
            cs.mahjongg3d = bool(fields[8])
        except ValueError:
            _perr(1, 8, 'not boolean')
            return None
    if len(cs.ext) < 2 or cs.ext[0] != ".":
        _perr(1, msg='specifies an invalid file extension')
        return None
    # lines_list[1]: identifier/name
    if not lines_list[1]:
        _perr(2, msg='unexpected empty line')
        return None
    cs.ident = lines_list[1]
    split_ident = cs.ident.split(';')
    if len(split_ident) == 1:
        cs.name = cs.ident
    elif len(split_ident) == 2:
        cs.name = split_ident[1].strip()
    else:
        _perr(2, msg='invalid format')
        return None
    # lines_list[2]: CARDW, CARDH, CARDD
    try:
        cs.CARDW, cs.CARDH, cs.CARDD = (int(x) for x in lines_list[2].split())
    except ValueError:
        _perr(3, msg='invalid format')
        return None
    # lines_list[3]: CARD_UP_YOFFSET, CARD_DOWN_YOFFSET,
    # SHADOW_XOFFSET, SHADOW_YOFFSET
    try:
        (cs.CARD_XOFFSET, cs.CARD_YOFFSET,
         cs.SHADOW_XOFFSET, cs.SHADOW_YOFFSET) = \
             (int(x) for x in lines_list[3].split())
    except ValueError:
        _perr(4, msg='invalid format')
        return None
    # lines_list[4]: default background
    back = lines_list[4]
    if not back:
        _perr(5, msg='unexpected empty line')
        return None
    # lines_list[5]: all available backgrounds
    cs.backnames = [f.strip() for f in lines_list[5].split(';')]
    if back in cs.backnames:
        cs.backindex = cs.backnames.index(back)
    else:
        cs.backnames.insert(0, back)
        cs.backindex = 0

    # if cs.type != 1: print cs.type, cs.name
    return cs
