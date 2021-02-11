# Written by Juhani Numminen, under the MIT Expat License.

import unittest

from pysollib.cardsetparser import parse_cardset_config
from pysollib.resource import CSI, CardsetConfig


class CardsetParserTests(unittest.TestCase):

    def _assertCcEqual(self, a, b, msg=None):
        """Assert that CardsetConfig objects a and b have equal attributes."""
        return self.assertDictEqual(a.__dict__, b.__dict__, msg)

    def test_good_cardset(self):
        config_txt = """\
PySolFC solitaire cardset;4;.gif;1;52;7
123-dondorf;Dondorf
79 123 8
16 25 7 7
back01.gif
back01.gif
"""

        reference = CardsetConfig()
        reference.update(dict(
            version=4,
            ext='.gif',
            type=CSI.TYPE_FRENCH,
            ncards=52,
            styles=[7],
            ident='123-dondorf;Dondorf',
            name='Dondorf',
            CARDW=79,
            CARDH=123,
            CARDD=8,
            CARD_XOFFSET=16,
            CARD_YOFFSET=25,
            SHADOW_XOFFSET=7,
            SHADOW_YOFFSET=7,
            backindex=0,
            backnames=['back01.gif'],
            ))
        self._assertCcEqual(
            parse_cardset_config(config_txt.split('\n')),
            reference,
            'parse_cardset_config should parse well-formed v4 config.txt ' +
            'correctly')

    def test_reject_too_few_fields(self):
        config_txt = """\
PySolFC solitaire cardset;4;.gif;1;52
123-dondorf;Dondorf
79 123 8
16 25 7 7
back01.gif
back01.gif
"""
        self.assertIsNone(
            parse_cardset_config(config_txt.split('\n')),
            'parse_cardset_config should reject v4 config.txt with ' +
            'a missing field on the first line')
