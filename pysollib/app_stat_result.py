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

from pysollib.mfxutil import Struct
from pysollib.settings import TOP_SIZE


class GameStatResult:
    def __init__(self):
        self.min = 0
        self.max = 0
        self.top = []
        self.num = 0
        self.total = 0  # sum of all values
        self.average = 0

    def update(self, gameid, value, game_number, game_start_time):
        # update min & max
        if not self.min or value < self.min:
            self.min = value
        if not self.max or value > self.max:
            self.max = value
        # calculate position & update top
        position = None
        n = 0
        for i in self.top:
            if value < i.value:
                position = n+1
                v = Struct(gameid=gameid,
                           value=value,
                           game_number=game_number,
                           game_start_time=game_start_time)
                self.top.insert(n, v)
                del self.top[TOP_SIZE:]
                break
            n += 1
        if not position and len(self.top) < TOP_SIZE:
            v = Struct(gameid=gameid,
                       value=value,
                       game_number=game_number,
                       game_start_time=game_start_time)
            self.top.append(v)
            position = len(self.top)
        # update average
        self.total += value
        self.num += 1
        self.average = float(self.total)/self.num
        return position
