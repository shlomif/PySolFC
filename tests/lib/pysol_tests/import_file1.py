# Written by Shlomi Fish, under the MIT Expat License.

import unittest
from pysollib.acard import AbstractCard
from pysollib.hint import FreeCellSolver_Hint
import pysollib.stack


class MockItem:
    def __init__(self):
        pass

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
        self.reserves = [
            pysollib.stack.AC_RowStack(0, 0, self) for s in range(4)]
        self.preview = 0


def _empty_override(*args):
    return True


pysollib.stack.MfxCanvasGroup = _empty_override


class Mock_S_Game:
    def __init__(self):
        self.s = MockGame()

    def flipMove(self, foo):
        pass

    def moveMove(self, cnt, frm, to, frames=0):
        c = frm.cards.pop()
        c.face_up = True
        to.addCard(c)
        pass


class MyTests(unittest.TestCase):
    def _successful_import(self, fn, want_s, blurb):
        s_game = Mock_S_Game()
        h = FreeCellSolver_Hint(s_game, None)
        fh = open(fn, 'r+b')
        h.importFileHelper(fh, s_game)
        self.assertEqual(h.calcBoardString(), want_s, blurb)

    def test_import(self):
        return self._successful_import('tests/unit/data/with-10-for-rank.txt',
                                       '''FC: - - - -
4C 2C 9C 8C QS 4S 2H
5H QH 3C AC 3H 4H QD
QC 9S 6H 9H 3S KS 3D
5D 2S JC 5C JH 6D AS
2D KD TH TC TD 8D
7H JS KH TS KC 7C
AH 5S 6S AD 8H JD
7S 6C 7D 4D 8S 9D
''', 'import worked with "10"s as ranks')

    def test_import_2(self):
        return self._successful_import('tests/unit/data/624.board',
                                       '''FC: - - - -
KC 6H 4C QS 2D 4S AS
4H TH 2S JH 2H 9S AH
3S 6C 9H AD KH QD 7C
3C JS 5H KS TC 9C 8C
4D 9D 7S JC 5D TS
KD QC 5C QH 6S 3D
5S JD 8D 6D TD 8H
8S 7H 3H 2C AC 7D
''', 'import worked with Ts')


def mymain():
    from pycotap import TAPTestRunner
    suite = unittest.TestLoader().loadTestsFromTestCase(MyTests)
    TAPTestRunner().run(suite)
