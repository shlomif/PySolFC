# Written by Shlomi Fish, under the MIT Expat License.

import unittest

from pysollib.game import GameDrag


class MyTests(unittest.TestCase):
    def test_shadows(self):
        d = GameDrag()
        d.shadows.append("test")
        self.assertTrue(len(d.shadows))
