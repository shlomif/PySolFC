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
from pysol_cards.random import random__str2int

from pysollib.settings import PACKAGE
from pysollib.settings import VERSION, VERSION_TUPLE


def pysolDumpGame(game_, p, bookmark=0):
    game_.updateTime()
    assert 0 <= bookmark <= 2
    p.dump(PACKAGE)
    p.dump(VERSION)
    p.dump(VERSION_TUPLE)
    p.dump(bookmark)
    p.dump(game_.GAME_VERSION)
    p.dump(game_.id)
    #
    p.dump(random__str2int(game_.random.getSeedStr()))
    p.dump(game_.random.getstate())
    #
    p.dump(len(game_.allstacks))
    for stack in game_.allstacks:
        p.dump(len(stack.cards))
        for card in stack.cards:
            p.dump(card.id)
            p.dump(card.face_up)
    p.dump(game_.s.talon.round)
    p.dump(game_.finished)
    if 0 <= bookmark <= 1:
        p.dump(game_.saveinfo)
        p.dump(game_.gsaveinfo)
    p.dump(game_.moves)
    p.dump(game_.snapshots)
    if 0 <= bookmark <= 1:
        if bookmark == 0:
            game_.gstats.saved += 1
        p.dump(game_.gstats)
        p.dump(game_.stats)
    game_._saveGameHook(p)
    p.dump("EOF")
