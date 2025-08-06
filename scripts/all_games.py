#!/usr/bin/env python3
# -*- mode: python; coding: koi8-r; -*-
#

import builtins
import os
import sys
import time

# from pprint import pprint
import pysollib.games  # noqa: F401
import pysollib.games.mahjongg  # noqa: F401
import pysollib.games.special  # noqa: F401
from pysollib.gamedb import GAME_DB
from pysollib.gamedb import GI
from pysollib.mfxutil import latin1_normalize
from pysollib.mygettext import fix_gettext
from pysollib.resource import CSI

os.environ['LANG'] = 'C'
builtins.__dict__['_'] = lambda x: x
builtins.__dict__['n_'] = lambda x: x

pysollib_path = os.path.join(sys.path[0], '..')
sys.path[0] = os.path.normpath(pysollib_path)
rules_dir = os.path.normpath(os.path.join(pysollib_path, 'data/html/rules'))
# pprint(sys.path)
# print rules_dir
html_mode = None

fix_gettext()


def _get_game_rules_filename(n):
    if n.startswith('Mahjongg'):
        return 'mahjongg.html'
    return latin1_normalize(n) + '.html'


GAME_BY_TYPE = {
    GI.GT_BAKERS_DOZEN: "Baker's Dozen",
    GI.GT_BELEAGUERED_CASTLE: "Beleaguered Castle",
    GI.GT_CANFIELD: "Canfield",
    GI.GT_FAN_TYPE: "Fan",
    GI.GT_FORTY_THIEVES: "Forty Thieves",
    GI.GT_FREECELL: "FreeCell",
    GI.GT_GOLF: "Golf",
    GI.GT_GYPSY: "Gypsy",
    GI.GT_KLONDIKE: "Klondike",
    GI.GT_MONTANA: "Montana",
    GI.GT_NAPOLEON: "Napoleon",
    GI.GT_NUMERICA: "Numerica",
    GI.GT_PAIRING_TYPE: "Pairing",
    GI.GT_PICTURE_GALLERY: "Picture Gallery",
    GI.GT_RAGLAN: "Raglan",
    GI.GT_SIMPLE_TYPE: "Simple game",
    GI.GT_SPIDER: "Spider",
    GI.GT_TERRACE: "Terrace",
    GI.GT_YUKON: "Yukon",
    GI.GT_1DECK_TYPE: "One-Deck game",
    GI.GT_2DECK_TYPE: "Two-Deck game",
    GI.GT_3DECK_TYPE: "Three-Deck game",
    GI.GT_4DECK_TYPE: "Four-Deck game",

    GI.GT_LIGHTS_OUT: "Lights Out",
    GI.GT_MATRIX: "Matrix",
    GI.GT_MEMORY: "Memory",
    GI.GT_POKER_TYPE: "Poker",
    GI.GT_PUZZLE_TYPE: "Puzzle",
    GI.GT_TAROCK: "Tarock",
    GI.GT_HEXADECK: "Hex A Deck",
    GI.GT_HANAFUDA: "Hanafuda",
    GI.GT_DASHAVATARA_GANJIFA: "Dashavatara Ganjifa",
    GI.GT_MAHJONGG: "Mahjongg",
    GI.GT_MUGHAL_GANJIFA: "Mughal Ganjifa",
    GI.GT_SHISEN_SHO: "Shisen-Sho",
    GI.GT_HANOI: "Tower of Hanoi",
    GI.GT_PEGGED: "Pegged",
    GI.GT_CRIBBAGE_TYPE: "Cribbage",
    GI.GT_ISHIDO: "Ishido",
    GI.GT_SAMEGAME: "Samegame",
}


def by_category():
    games = GAME_DB.getGamesIdSortedById()
    games_by_cat = {}
    for id in games:
        gi = GAME_DB.get(id)
        gt = CSI.TYPE_NAME[gi.category]
        if gt in games_by_cat:
            games_by_cat[gt] += 1
        else:
            games_by_cat[gt] = 1
    games_by_cat_list = sorted(
        games_by_cat.items(), key=lambda x: x[1], reverse=True)
#     print '<table border="2"><tr><th>Name</th><th>Number</th></tr>'
#     for i in games_by_cat_list:
#         print '<tr><td>%s</td><td>%s</td></tr>' % i
#     print '</table>'
    print('<ul>')
    for i in games_by_cat_list:
        print('<li>%s (%s games)</li>' % i)
    print('</ul>')


def by_type():
    games = GAME_DB.getGamesIdSortedById()
    games_by_type = {}
    for id in games:
        gi = GAME_DB.get(id)
        if gi.si.game_type not in GAME_BY_TYPE:
            print(gi.si.game_type)
            continue
        gt = GAME_BY_TYPE[gi.si.game_type]
        if gt in games_by_type:
            games_by_type[gt] += 1
        else:
            games_by_type[gt] = 1
    games_by_type_list = sorted(games_by_type.items(), key=lambda x: x[0])
    #  print '<table border="2"><tr><th>Name</th><th>Number</th></tr>'
    #  for i in games_by_type_list:
    #      print '<tr><td>%s</td><td>%s</td></tr>' % i
    #  print '</table>'
    print('<ul>')
    for i in games_by_type_list:
        print('<li>%s (%s games)</li>' % i)
    print('</ul>')


def all_games(sort_by='id'):
    # rules_dir = 'rules'
    print('''<table><thead>
<tr><th>ID</th><th>Name</th><th>Alternate names</th><th>Type</th></tr>
</thead>
<tbody>
''')

    if sort_by == 'id':
        get_games_func = GAME_DB.getGamesIdSortedById
    else:
        get_games_func = GAME_DB.getGamesIdSortedByName

    for id in get_games_func():
        gi = GAME_DB.get(id)
        if not gi.rules_filename:
            rules_fn = _get_game_rules_filename(gi.name)
        else:
            rules_fn = gi.rules_filename
        gt = CSI.TYPE_NAME[gi.category]
        if gt == 'French':
            gt = 'French (%s)' % GAME_BY_TYPE[gi.si.game_type]
        name = gi.name
        altnames = '<br/>'.join(gi.altnames)
        fn = os.path.join(rules_dir, rules_fn)
        if os.path.exists(fn):
            print('''<tr>
<td>%s</td>
<td> <a href="%s" title="Rules for this game">%s</a> </td>
<td>%s</td>
<td>%s</td>
</tr>
''' % (id, fn, name, altnames, gt))
        else:
            print('''<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>
''' % (id, name, altnames, gt))
    print('</tbody></table>')


def create_html(sort_by):
    if html_mode != 'bare':
        print('''<!DOCTYPE html><html lang="en-US">
<head>
  <title>PySolFC - List of solitaire games</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head>
<body>
''')
    print('<strong>Total games: %d</strong>' %
          len(GAME_DB.getGamesIdSortedById()))
    print('<section>')
    print('<h2>Categories</h2>')
    by_category()
    print('</section>')
    print('<section>')
    print('<h2>Types</h2>')
    by_type()
    print('</section>')
    # print '<h2>All games</h2>'
    print('<section>')
    print('<h2>The games</h2>')
    all_games(sort_by)
    print('</section>')
    if html_mode != 'bare':
        print('</body></html>')


def get_text():
    # get_games_func = GAME_DB.getGamesIdSortedById
    get_games_func = GAME_DB.getGamesIdSortedByName

    games_list = {}  # for unique
    for id in get_games_func():
        gi = GAME_DB.get(id)
        games_list[gi.name] = ''
        if gi.name != gi.short_name:
            games_list[gi.short_name] = ''
        for n in gi.altnames:
            games_list[n] = ''
    games_list = sorted(games_list.keys())
    print('''\
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PySol 0.0.1\\n"
"POT-Creation-Date: %s\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=CHARSET\\n"
"Content-Transfer-Encoding: ENCODING\\n"
"Generated-By: %s 0.1\\n"

''' % (time.asctime(), sys.argv[0]))
    for g in games_list:
        print('msgid "%s"\nmsgstr ""\n' % g)


def old_plain_text():
    # get_games_func = GAME_DB.getGamesIdSortedById
    get_games_func = GAME_DB.getGamesIdSortedByName
    games_list = {}  # for unique
    for id in get_games_func():
        gi = GAME_DB.get(id)
        games_list[gi.name] = ''
        # if gi.name != gi.short_name:
        #    games_list[gi.short_name] = ''
        for n in gi.altnames:
            games_list[n] = ''
    games_list = sorted(games_list.keys())
    for g in games_list:
        print(g)


def plain_text():
    get_games_func = GAME_DB.getGamesIdSortedByName
    for id in get_games_func():
        gi = GAME_DB.get(id)
        if gi.category == GI.GC_FRENCH:
            # print str(gi.gameclass)
            # gc = gi.gameclass
            # h = gc.Hint_Class is None and 'None' or gc.Hint_Class.__name__
            # print gi.name.encode('utf-8'), h
            print(gi.name)
            for n in gi.altnames:
                print(n)
            # name = gi.name.lower()
            # name = re.sub('\W', '', name)
            # print id, name #, gi.si.game_type,
            #       gi.si.game_type == GI.GC_FRENCH


if len(sys.argv) < 2 or sys.argv[1] == 'html':
    sort_by = 'id'
    if len(sys.argv) > 2:
        sort_by = sys.argv[2]
    if len(sys.argv) > 3:
        rules_dir = sys.argv[3]
    if len(sys.argv) > 4:
        html_mode = sys.argv[4]
    create_html(sort_by)
elif sys.argv[1] == 'gettext':
    get_text()
elif sys.argv[1] == 'text':
    plain_text()
else:
    sys.exit('invalid argument')
