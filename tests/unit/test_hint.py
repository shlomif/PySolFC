# Written by Shlomi Fish, under the MIT Expat License.

import unittest

from pysollib.acard import AbstractCard
from pysollib.hint import Base_Solver_Hint


class MyTests(unittest.TestCase):
    def test_output(self):
        card = AbstractCard(1001, 0, 3, 7, 3001)
        h = Base_Solver_Hint(None, None, base_rank=0)

        got = h.card2str2(card)
        # TEST
        self.assertEqual(got, 'D-8', 'card2str2 works')
        # diag('got == ' + got)

        got = h.card2str1(card)
        # TEST
        self.assertEqual(got, '8D', 'card2str2 works')
        # diag('got == ' + got)
