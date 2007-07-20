#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-
#

import sys, os, re, time
from pprint import pprint

os.environ['LANG'] = 'C'
import __builtin__
__builtin__.__dict__['_'] = lambda x: x
__builtin__.__dict__['n_'] = lambda x: x

pysollib_path = os.path.join(sys.path[0], '..')
sys.path[0] = os.path.normpath(pysollib_path)
rules_dir = os.path.normpath(os.path.join(pysollib_path, 'data/html/rules'))
#pprint(sys.path)
#print rules_dir

from pysollib.init import fix_gettext
fix_gettext()

import pysollib.games
import pysollib.games.special
import pysollib.games.ultra
import pysollib.games.mahjongg

from pysollib.gamedb import GAME_DB
from pysollib.gamedb import GI
from pysollib.mfxutil import latin1_to_ascii
from pysollib.resource import CSI

def getGameRulesFilename(n):
    if n.startswith('Mahjongg'): return 'mahjongg.html'
    ##n = re.sub(r"[\[\(].*$", "", n)
    n = latin1_to_ascii(n)
    n = re.sub(r"[^\w]", "", n)
    n = n.lower() + ".html"
    return n

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
    GI.GT_RAGLAN: "Raglan",
    GI.GT_SIMPLE_TYPE: "Simple game",
    GI.GT_SPIDER: "Spider",
    GI.GT_TERRACE: "Terrace",
    GI.GT_YUKON: "Yukon",
    GI.GT_1DECK_TYPE: "One-Deck game",
    GI.GT_2DECK_TYPE: "Two-Deck game",
    GI.GT_3DECK_TYPE: "Three-Deck game",
    GI.GT_4DECK_TYPE: "Four-Deck game",

    GI.GT_MATRIX: "Matrix",
    GI.GT_MEMORY: "Memory",
    GI.GT_POKER_TYPE: "Poker",
    GI.GT_PUZZLE_TYPE: "Puzzle",
    GI.GT_TAROCK: "Tarock",
    GI.GT_HEXADECK: "Hex A Deck",
    GI.GT_HANAFUDA: "Hanafuda",
    GI.GT_DASHAVATARA_GANJIFA: "Dashavatara Ganjifa",
    GI.GT_MAHJONGG: "Mahjongg",
    GI.GT_MUGHAL_GANJIFA:"Mughal Ganjifa",
    GI.GT_SHISEN_SHO:"Shisen-Sho",

}

def by_category():
    games = GAME_DB.getGamesIdSortedById()
    games_by_cat = {}
    for id in games:
        gi = GAME_DB.get(id)
        gt = CSI.TYPE_NAME[gi.category]
        if games_by_cat.has_key(gt):
            games_by_cat[gt] += 1
        else:
            games_by_cat[gt] = 1
    games_by_cat_list = [(i, j) for i, j in games_by_cat.items()]
    games_by_cat_list.sort(lambda i, j: cmp(j[1], i[1]))
##     print '<table border="2"><tr><th>Name</th><th>Number</th></tr>'
##     for i in games_by_cat_list:
##         print '<tr><td>%s</td><td>%s</td></tr>' % i
##     print '</table>'
    print '<ul>'
    for i in games_by_cat_list:
        print '<li>%s (%s games)</li>' % i
    print '</ul>'
    return

def by_type():
    games = GAME_DB.getGamesIdSortedById()
    games_by_type = {}
    for id in games:
        gi = GAME_DB.get(id)
        if not GAME_BY_TYPE.has_key(gi.si.game_type):
            print gi.si.game_type
            continue
        gt = GAME_BY_TYPE[gi.si.game_type]
        if games_by_type.has_key(gt):
            games_by_type[gt] += 1
        else:
            games_by_type[gt] = 1
    games_by_type_list = games_by_type.items()
    games_by_type_list.sort(lambda i, j: cmp(i[0], j[0]))
##     print '<table border="2"><tr><th>Name</th><th>Number</th></tr>'
##     for i in games_by_type_list:
##         print '<tr><td>%s</td><td>%s</td></tr>' % i
##     print '</table>'
    print '<ul>'
    for i in games_by_type_list:
        print '<li>%s (%s games)</li>' % i
    print '</ul>'
    return

def all_games(sort_by='id'):
    #rules_dir = 'rules'
    print '''<table border="2">
<tr><th>ID</th><th>Name</th><th>Alternate names</th><th>Type</th></tr>
'''

    if sort_by == 'id':
        get_games_func = GAME_DB.getGamesIdSortedById
    else:
        get_games_func = GAME_DB.getGamesIdSortedByName

    for id in get_games_func():
        gi = GAME_DB.get(id)
        if not gi.rules_filename:
            rules_fn = getGameRulesFilename(gi.name)
        else:
            rules_fn = gi.rules_filename
        gt = CSI.TYPE_NAME[gi.category]
        if gt == 'French':
            gt = 'French (%s)' % GAME_BY_TYPE[gi.si.game_type]
        name = gi.name.encode('utf-8')
        altnames = '<br>'.join(gi.altnames).encode('utf-8')
        fn = os.path.join(rules_dir, rules_fn)
        if 1 and os.path.exists(fn):
            print '''<tr><td>%s</td><td>
<a href="%s" title="Rules for this game">%s</a>
</td><td>%s</td><td>%s</td></tr>
''' % (id, fn, name, altnames, gt)
        else:
            print '''<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
''' % (id, name, altnames, gt)
    print '</table>'

def create_html(sort_by):
    print '''<html>
<head>
  <title>PySolFC - List of solitaire games</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
'''
    print '<b>Total games: %d</b>' % len(GAME_DB.getGamesIdSortedById())
    print '<h2>Categories</h2>'
    by_category()
    print '<h2>Types</h2>'
    by_type()
    #print '<h2>All games</h2>'
    all_games(sort_by)
    print '</body></html>'


def get_text():
    #get_games_func = GAME_DB.getGamesIdSortedById
    get_games_func = GAME_DB.getGamesIdSortedByName

    games_list = {} # for unique
    for id in get_games_func():
        gi = GAME_DB.get(id)
        games_list[gi.name] = ''
        if gi.name != gi.short_name:
            games_list[gi.short_name] = ''
        for n in gi.altnames:
            games_list[n] = ''
    games_list = games_list.keys()
    games_list.sort()
    print '''\
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

''' % (time.asctime(), sys.argv[0])
    for g in games_list:
        print 'msgid "%s"\nmsgstr ""\n' % g.encode('utf-8')

def old_plain_text():
    #get_games_func = GAME_DB.getGamesIdSortedById
    get_games_func = GAME_DB.getGamesIdSortedByName
    games_list = {} # for unique
    for id in get_games_func():
        gi = GAME_DB.get(id)
        games_list[gi.name] = ''
        #if gi.name != gi.short_name:
        #    games_list[gi.short_name] = ''
        for n in gi.altnames:
            games_list[n] = ''
    games_list = games_list.keys()
    games_list.sort()
    for g in games_list:
        print g.encode('utf-8')

def plain_text():
    get_games_func = GAME_DB.getGamesIdSortedByName
    for id in get_games_func():
        gi = GAME_DB.get(id)
        if gi.category == GI.GC_FRENCH:
            ##print str(gi.gameclass)
            ##gc = gi.gameclass
            ##h = gc.Hint_Class is None and 'None' or gc.Hint_Class.__name__
            ##print gi.name.encode('utf-8'), h
            print gi.name.encode('utf-8')
            for n in gi.altnames:
                print n.encode('utf-8')
            ##name = gi.name.lower()
            ##name = re.sub('\W', '', name)
            ##print id, name #, gi.si.game_type, gi.si.game_type == GI.GC_FRENCH


##
if len(sys.argv) < 2 or sys.argv[1] == 'html':
    sort_by = 'id'
    if len(sys.argv) > 2:
        sort_by = sys.argv[2]
    if len(sys.argv) > 3:
        rules_dir = sys.argv[3]
    create_html(sort_by)
elif sys.argv[1] == 'gettext':
    get_text()
elif sys.argv[1] == 'text':
    plain_text()
else:
    sys.exit('invalid argument')



