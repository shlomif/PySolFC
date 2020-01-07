#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
# Copyright (C) 2020 qunka
# Modified by Shlomi Fish, 2020, while disclaiming all copyrights.
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

from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.games.bisley import Bisley
from pysollib.layout import Layout
from pysollib.stack import \
        InitialDealTalonStack, \
        SS_FoundationStack, \
        UD_SS_RowStack
from pysollib.util import KING, NO_RANK


# ************************************************************************
# * Bisley 13
# ************************************************************************

class Bisley13(Bisley):

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = 2*l.XM+9*l.XS, max(2*(l.YM+l.YS+8*l.YOFFSET), l.YM+5*l.YS)
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(7):
            s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS
        x, y = l.XM, l.YM+l.YS+8*l.YOFFSET
        for i in range(6):
            s.rows.append(UD_SS_RowStack(x, y, self, base_rank=NO_RANK))
            x += l.XS
        y = l.YM
        for i in range(4):
            x = l.XM+7*l.XS+l.XM
            s.foundations.append(SS_FoundationStack(x, y, self, i, max_move=0))
            x += l.XS
            s.foundations.append(SS_FoundationStack(x, y, self, i,
                                 base_rank=KING, max_move=0, dir=-1))
            y += l.YS

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        self._startDealNumRows(3)
        self.s.talon.dealRow(rows=self.s.rows[4:13])
        self.s.talon.dealRow(rows=self.s.foundations[::2])


# register the game
registerGame(GameInfo(343001, Bisley13, "Bisley 13",
                      GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0, GI.SL_MOSTLY_SKILL))
