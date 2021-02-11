# Written by Shlomi Fish, under the MIT Expat License.

import unittest

import pysollib.stack
from pysollib.acard import AbstractCard
from pysollib.games.spider import ScorpionTail_RowStack
from pysollib.games.spider import Scorpion_RowStack
from pysollib.games.spider import Spider_RowStack

from .common_mocks import MockApp, MockCanvas, MockItem, MockTalon


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


class Mock_S_Game:  # noqa: N801
    def __init__(self):
        self.s = MockGame()

    def flipMove(self, foo):  # noqa: N802
        pass

    def moveMove(self, cnt, frm, to, frames=0):  # noqa: N802
        c = frm.cards.pop()
        c.face_up = True
        to.addCard(c)
        pass


class ScorpionTests(unittest.TestCase):
    def _calc_scorpion_stack(self, is_scorpion_tail):
        g = MockGame()
        stack = (ScorpionTail_RowStack
                 if is_scorpion_tail
                 else Scorpion_RowStack)(0, 0, g)
        for s, r in [(2, 5), (3, 7), (2, 7), (2, 0), (2, 3), (2, 4), (1, 4)]:
            c = AbstractCard(1000+r*100+s*10, 0, s, r, g)
            c.face_up = True
            c.item = MockItem()
            stack.addCard(c)
        return stack

    def test_canMoveCards(self):  # noqa: N802
        for is_scorpion_tail in [False, True]:
            stack = self._calc_scorpion_stack(is_scorpion_tail)
            stack.canMoveCards(stack.cards[6:])
            self.assertTrue(stack)

    def test_canMoveCards_non_top(self):  # noqa: N802
        for is_scorpion_tail in [False, True]:
            stack = self._calc_scorpion_stack(is_scorpion_tail)
            self.assertTrue(stack.canMoveCards(stack.cards[4:]))
            self.assertTrue(stack)

    def _calc_spider_stack(self):
        g = MockGame()
        stack = Spider_RowStack(0, 0, g)
        for s, r in [(2, 5), (3, 7), (2, 7), (2, 0), (2, 3), (2, 5), (1, 4)]:
            c = AbstractCard(1000+r*100+s*10, 0, s, r, g)
            c.face_up = True
            c.item = MockItem()
            stack.addCard(c)
        return stack

    def test_Spider_canMoveCards_non_top(self):  # noqa: N802
        stack = self._calc_spider_stack()
        self.assertFalse(stack.canMoveCards(stack.cards[5:]))
        self.assertTrue(stack)
