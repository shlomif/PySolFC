# Written by Shlomi Fish, under the MIT Expat License.

import unittest

<<<<<<< HEAD
from pysollib.game import GameDrag, GameStacks
=======
from pysollib.game import GameDrag
>>>>>>> f3d3517... add missing attribute.


class MyTests(unittest.TestCase):
    def test_shadows(self):
        d = GameDrag()
        d.shadows.append("test")
        self.assertTrue(len(d.shadows))
<<<<<<< HEAD

    def test_addattr(self):
        s = GameStacks()
        s.addattr(tableaux=[])
        s.tableaux.append("myval")
        self.assertEqual(s.tableaux, ["myval"])
=======
>>>>>>> f3d3517... add missing attribute.
