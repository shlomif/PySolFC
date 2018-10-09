# Written by Shlomi Fish, under the MIT Expat License.

import unittest
from pysollib.acard import AbstractCard
import pysollib.stack
from pysollib.games.spider import Scorpion_RowStack
from pysol_tests.common_mocks1 import MockApp, MockCanvas, MockItem, MockTalon


class MockGame:
    def __init__(self):
        self.app = MockApp()
        self.talon = MockTalon(self)

        self.allstacks = []
        self.stackmap = {}
        self.canvas = MockCanvas()
        self.foundations = [
            pysollib.stack.SS_FoundationStack(0, 0, self, s) for s in range(4)]
        self.rows = [pysollib.stack.Yukon_SS_RowStack(0, 0, self)
                     for s in range(8)]
        self.reserves = [
            pysollib.stack.Yukon_SS_RowStack(0, 0, self) for s in range(4)]
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
    def test_import(self):
        g = MockGame()
        stack = Scorpion_RowStack(0, 0, g)
        cards = [
            AbstractCard(1000+r*100+s*10, 0, s, r, g)
            for s, r in [(2, 5), (3, 7), (2, 7), (2, 0),
                         (2, 3), (2, 4), (1, 4)]
            ]
        for c in cards:
            c.face_up = True
            c.item = MockItem()
            stack.addCard(c)
        stack.canMoveCards(stack.cards[6:])
        self.assertTrue(stack)
