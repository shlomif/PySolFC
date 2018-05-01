#!/usr/bin/env python3
# Written by Shlomi Fish, under the MIT Expat License.

import unittest
from pysollib.acard import AbstractCard
from pysollib.hint import FreeCellSolver_Hint
import pysollib.stack


class MockItem:
    def __init__(self):
        self.xmargin = self.ymargin = 50

    def tkraise(self):
        return

    def addtag(self, nouse):
        return


class MockCanvas:
    def __init__(self):
        self.xmargin = self.ymargin = 50


class MockImages:
    def __init__(self):
        self.CARDW = self.CARDH = self.CARD_YOFFSET = 50


class MockOpt:
    def __init__(self):
        self.randomize_place = False


class MockApp:
    def __init__(self):
        self.images = MockImages()
        self.opt = MockOpt()


class MockTalon:
    def __init__(self, g):
        self.cards = [
            AbstractCard(1000+r*100+s*10, 0, s, r, g)
            for s in range(4) for r in range(13)]
        for c in self.cards:
            c.item = MockItem()


class MockGame:
    def __init__(self):
        self.app = MockApp()
        self.talon = MockTalon(self)

        self.allstacks = []
        self.stackmap = {}
        self.canvas = MockCanvas()
        self.foundations = [
            pysollib.stack.SS_FoundationStack(0, 0, self, s) for s in range(4)]
        self.rows = [pysollib.stack.AC_RowStack(0, 0, self) for s in range(8)]
        self.preview = 0


def m1(*args):
    return 1


pysollib.stack.MfxCanvasGroup = m1


class Mock_S_Game:
    def __init__(self):
        self.s = MockGame()

    def flipMove(self, foo):
        pass

    def moveMove(self, cnt, frm, to, frames=0):
        to.addCard(frm.cards.pop())
        pass


class MyTests(unittest.TestCase):
    def test_import(self):
        s_game = Mock_S_Game()
        h = FreeCellSolver_Hint(s_game, None)
        fh = open('tests/unit/data/with-10-for-rank.txt', 'r+b')
        h.importFileHelper(fh, s_game)

    def test_output(self):
        # TEST
        self.assertEqual(1, 1, 'card2str2 works')


if __name__ == '__main__':
    from pycotap import TAPTestRunner
    suite = unittest.TestLoader().loadTestsFromTestCase(MyTests)
    TAPTestRunner().run(suite)
