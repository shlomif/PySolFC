# Written by Shlomi Fish, under the MIT Expat License.

import unittest

from pysol_tests.common_mocks1 import MockApp, MockCanvas, MockTalon

import pysollib.stack
from pysollib.hint import FreeCellSolver_Hint, PySolHintLayoutImportError


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
    def _calc_hint(self, fn):
        """docstring for _calc_hint"""
        s_game = Mock_S_Game()
        h = FreeCellSolver_Hint(s_game, None)
        fh = open(fn, 'r+b')
        h.importFileHelper(fh, s_game)
        return h

    def _successful_import(self, fn, want_s, blurb):
        self.assertEqual(self._calc_hint(fn).calcBoardString(), want_s, blurb)

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

    def test_import_utf8_bom(self):
        return self._successful_import(
            'tests/unit/data/624-with-utf8-bom.board',
            '''FC: - - - -
KC 6H 4C QS 2D 4S AS
4H TH 2S JH 2H 9S AH
3S 6C 9H AD KH QD 7C
3C JS 5H KS TC 9C 8C
4D 9D 7S JC 5D TS
KD QC 5C QH 6S 3D
5S JD 8D 6D TD 8H
8S 7H 3H 2C AC 7D
''', 'import worked with utf-8 bom')

    def test_throw_error_on_duplicate_card(self):
        try:
            self._calc_hint('tests/unit/data/624-with-dup-card.board')
        except PySolHintLayoutImportError as err:
            self.assertEqual(err.msg, "Duplicate cards in input")
            self.assertEqual(err.cards, ["KC"])
            self.assertEqual(err.line_num, 1)
            self.assertEqual(err.format(), "Duplicate cards in input:\n\nKC")
            return
        self.fail("No exception thrown.")

    def test_throw_error_on_invalid_foundations_line(self):
        try:
            self._calc_hint(
                'tests/unit/data/624-invalid-foundations-line.board')
        except PySolHintLayoutImportError as err:
            self.assertEqual(err.msg, "Invalid Foundations line")
            self.assertEqual(err.cards, [])
            self.assertEqual(err.line_num, 1)
            return
        self.fail("No exception thrown.")

    def test_throw_error_on_missing_cards(self):
        try:
            self._calc_hint('tests/unit/data/624-missing-cards.board')
        except PySolHintLayoutImportError as err:
            self.assertEqual(err.msg, "Missing cards in input")
            self.assertEqual(err.cards, ["5H"])
            return
        self.fail("No exception thrown.")
