# Written by Shlomi Fish, under the MIT Expat License.
import unittest

from pysollib.kpat_load_save import KpatXmlEmitter

from six.moves import cStringIO


class MyTests(unittest.TestCase):
    def test_emitter(self):
        f = cStringIO()
        e = KpatXmlEmitter(f)
        self.assertTrue(e)
        e.writeEmptyTag("foo", [("one", "val1"), ("two", "val2")])
        self.assertEqual(
            f.getvalue(),
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<foo one=\"val1\" two=\"val2\"/>\n")
        f = cStringIO()
        e = KpatXmlEmitter(f)
        self.assertTrue(e)
        e.writeStartTag("foo", [("one", "val1"), ("two", "val2")])
        e.writeEmptyTag("flutter", [])
        e.endTag()
        self.assertEqual(
            f.getvalue(),
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<foo one=\"val1\" two=\"val2\">\n"
            + "\t<flutter/>\n"
            + "</foo>\n")
