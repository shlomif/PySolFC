# Written by Shlomi Fish, under the MIT Expat License.
import unittest

from pysollib.kpat_load_save import KpatEmitter

from six.moves import cStringIO


class MyTests(unittest.TestCase):
    def test_emitter(self):
        f = cStringIO()
        e = KpatEmitter(f)
        self.assertTrue(e)
