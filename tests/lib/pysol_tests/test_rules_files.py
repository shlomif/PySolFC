# -*- coding: utf-8 -*-
#
# Ensure every registered game has a rules HTML source file.
# Mirrors the lookup used by html-src/gen-html.py.

import os
import unittest

import pysollib.games  # noqa: F401
import pysollib.games.mahjongg  # noqa: F401
import pysollib.games.special  # noqa: F401
from pysollib.gamedb import GAME_DB
from pysollib.mfxutil import latin1_normalize


def _repo_root():
    # tests/lib/pysol_tests/this_file.py -> repo root
    here = os.path.dirname(__file__)
    return os.path.normpath(
        os.path.join(here, os.pardir, os.pardir, os.pardir)
    )


def _get_game_rules_filename(name):
    if name.startswith('Mahjongg'):
        return 'mahjongg.html'
    return latin1_normalize(name) + '.html'


def _resolve_rules_filename(gi):
    if gi.rules_filename:
        return gi.rules_filename
    return _get_game_rules_filename(gi.name)


class RulesFilesTests(unittest.TestCase):

    def test_every_game_has_rules_source(self):
        root = _repo_root()
        rules_dir = os.path.join(root, 'html-src', 'rules')
        wiki_dir = os.path.join(root, 'html-src', 'wikipedia')
        self.assertTrue(os.path.isdir(rules_dir),
                        'html-src/rules directory is missing')

        available = set(os.listdir(rules_dir))
        if os.path.isdir(wiki_dir):
            available.update(os.listdir(wiki_dir))

        missing = []
        for game_id in GAME_DB.getGamesIdSortedById():
            gi = GAME_DB.get(game_id)
            rules_fn = _resolve_rules_filename(gi)
            if rules_fn not in available:
                missing.append('%s (%s) -> %s' % (game_id, gi.name, rules_fn))

        self.assertEqual(
            missing, [],
            'Games missing rules HTML under html-src/rules or '
            'html-src/wikipedia:\n  ' + '\n  '.join(missing)
        )
