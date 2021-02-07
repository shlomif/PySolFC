# Written by Shlomi Fish, under the MIT Expat License.

import unittest

from pysollib.game import GameDrag, GameStacks


class MyTests(unittest.TestCase):
    def test_shadows(self):
        d = GameDrag()
        d.shadows.append("test")
        self.assertTrue(len(d.shadows))

    def test_addattr(self):
        s = GameStacks()
        s.addattr(tableaux=[])
        s.tableaux.append("myval")
        self.assertEqual(s.tableaux, ["myval"])
