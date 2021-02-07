# Written by Shlomi Fish, under the MIT Expat License.

import unittest

from pysollib.acard import AbstractCard


class MyTests(unittest.TestCase):
    def test_cards(self):
        card1 = AbstractCard(1001, 0, 1, 2, 3001)
        # TEST
        self.assertEqual(card1.color, 0, 'card1.color is sane.')

        # TEST
        self.assertEqual(card1.rank, 2, 'card1.rank')

        card2 = AbstractCard(1001, 0, 3, 7, 3001)
        # TEST
        self.assertEqual(card2.color, 1, 'card2.color is sane.')

        # TEST
        self.assertEqual(card2.rank, 7, 'card2.rank')
