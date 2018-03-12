#!/usr/bin/env python3
# Written by Shlomi Fish, under the MIT Expat License.

# imports
import unittest
from pysollib.mfxutil import latin1_normalize


class MyTests(unittest.TestCase):
    def test_output(self):
        self.assertEqual(latin1_normalize('HELLO%%good'), 'hellogood')


if __name__ == '__main__':
    from pycotap import TAPTestRunner
    suite = unittest.TestLoader().loadTestsFromTestCase(MyTests)
    TAPTestRunner().run(suite)
