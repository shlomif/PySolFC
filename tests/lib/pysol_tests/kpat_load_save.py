# Written by Shlomi Fish, under the MIT Expat License.
import unittest

from pysollib.acard import AbstractCard
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

        f = cStringIO()
        e = KpatXmlEmitter(f)
        self.assertTrue(e)
        e.writeStartTag("foo", [("one", "val1"), ("two", "val2")])
        e.writeStartTag("rar", [("z", "zval"), ("a", "aval")])
        e.writeEmptyTag("flutter", [])
        e.endTag()
        e.endTag()
        self.assertEqual(
            f.getvalue(),
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<foo one=\"val1\" two=\"val2\">\n"
            + "\t<rar z=\"zval\" a=\"aval\">\n"
            + "\t\t<flutter/>\n"
            + "\t</rar>\n"
            + "</foo>\n")

    def test_write_card(self):
        f = cStringIO()
        e = KpatXmlEmitter(f)
        self.assertTrue(e)
        e.writeCard(card=AbstractCard(1001, 0, 0, 0, 3001), turn="face-up")
        self.assertEqual(
            f.getvalue(),
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<card id=\"1001\" suit=\"clubs\" " +
            "rank=\"ace\" turn=\"face-up\"/>\n"
        )

    def test_write_card2(self):
        f = cStringIO()
        e = KpatXmlEmitter(f)
        self.assertTrue(e)
        e.writeCard(card=AbstractCard(1002, 0, 1, 1, 3001), turn="face-up")
        self.assertEqual(
            f.getvalue(),
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<card id=\"1002\" suit=\"spades\" " +
            "rank=\"two\" turn=\"face-up\"/>\n"
        )
