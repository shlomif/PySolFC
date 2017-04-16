# vim:ts=4:et:nowrap:fileencoding=utf-8
#

# imports
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout


#***********************************************************************
# Daddy Longlegs (by Jim Sizelove)
#***********************************************************************

class DaddyLonglegs(Game):
    Talon_Class = DealRowTalonStack
    RowStack_Class = StackWrapper(Yukon_SS_RowStack, dir=1, base_rank=ACE)

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s

        # set window
        self.setSize(l.XM + 6*l.XS, l.YM + 7*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = self.Talon_Class(x, y, self)
        l.createText(s.talon, "ss")
        x = x + 3*l.XS/2
        for i in range(4):
            s.rows.append(self.RowStack_Class(x, y, self))
            x = x + l.XS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        self.s.talon.dealRow()

    def isGameWon(self):
        if self.s.talon.cards:
            return 0
        for row in self.s.rows:
            if not isSameSuitSequence(row.cards, dir=1):
                return 0
        return 1


# register the game
registerGame(GameInfo(555001, DaddyLonglegs, "Daddy Longlegs",
                         GI.GT_SPIDER, 1, 0, GI.SL_MOSTLY_SKILL,
                         rules_filename="daddylonglegs.html"))
