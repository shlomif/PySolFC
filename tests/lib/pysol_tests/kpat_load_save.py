# Written by Shlomi Fish, under the MIT Expat License.
import unittest

from pysollib.kpat_load_save import KpatEmitter

from six.moves import cStringIO


class MyTests(unittest.TestCase):
    def test_emitter(self):
        f = cStringIO()
        e = KpatEmitter(f)
        self.assertTrue(e)
        e.writeEmptyTag("foo", [("one", "val1"), ("two", "val2")])
        self.assertEqual(
            f.getvalue(),
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<foo one=\"val1\" two=\"val2\"/>\n")
