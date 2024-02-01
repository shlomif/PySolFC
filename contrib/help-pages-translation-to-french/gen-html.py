#!/usr/bin/env python3

import builtins
import os
import sys

from pysollib.gamedb import GAME_DB
from pysollib.gamedb import GI
from pysollib.mfxutil import latin1_normalize
from pysollib.mygettext import fix_gettext
# outdir = '../html'
pysollib_dir = '../'


builtins._ = lambda x: x
builtins.n_ = lambda x: x

import pysollib.games  # noqa: E402,F402,I100,I202
import pysollib.games.mahjongg  # noqa: E402,F402
import pysollib.games.special  # noqa: E402,F401,F402

try:
    os.mkdir('html')
except Exception:
    pass

try:
    os.mkdir('html/rules')
except Exception:
    pass


def merge_dicts(x, y):
    ret = x.copy()
    ret.update(y)
    return ret


pysollib_path = os.path.join(sys.path[0], pysollib_dir)
sys.path[0] = os.path.normpath(pysollib_path)
# print sys.path

fix_gettext()

files = [
    ('credits.html', 'PySol Credits'),
    ('ganjifa.html', 'PySol - Règles générales du Ganjifa'),
    ('general_rules.html', 'PySol - Règles générales'),
    ('glossary.html', 'PySol - Glossaire'),
    ('hanafuda.html', 'PySol - Règles générales des jeux de cartes à fleurs'),
    ('hexadeck.html', 'PySol - Règles générales du jeu Hex A Deck'),
    ('howtoplay.html', 'Comment jouer à PySol'),
    ('index.html', 'PySol - une collection de jeux de solitaire'),
    ('install.html', 'PySol - Installation'),
    ('intro.html', 'PySol - Introduction'),
    ('license.html', 'Licence de PySol'),
    ('news.html', 'PySol - une collection de jeux de solitaire'),
    # ('rules_alternate.html', 'PySol - a Solitaire Game Collection'),
    # ('rules.html', 'PySol - a Solitaire Game Collection'),
    ]

rules_files = [
    # ('hanoipuzzle.html', ),
    ('mahjongg.html', 'PySol - Règles du Mahjongg'),
    ('matrix.html', 'PySol - Règles du Matrix'),
    ('pegged.html', 'PySol - Règles du Pegged'),
    ('shisensho.html', 'PySol - Règles du Shisen-Sho'),
    ('spider.html', 'PySol - Règles du Spider'),
    ('freecell.html', 'PySol - Règles du FreeCell'),
    ]
wikipedia_files = [
    ('houseinthewood.html', 'PySol - Règles de House in the Woods'),
    ('fourseasons.html', 'PySol - Règles du Four Seasons'),
    ]


def _fmt(fmt, params):
    return fmt % merge_dicts(params, {'logo_url': "images/pysollogo03.png",
                                      'logo_alt': "PySol FC Logo"})


main_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<html>
<head>
<title>%(title)s</title>
<meta name="license" content="GNU General Public License">
<meta http-equiv="content-type" content="text/html; charset=utf-8">
</head>
<body text="#000000" bgcolor="#F7F3FF" link="#0000FF" vlink="#660099"
alink="#FF0000">
<img src="%(logo_url)s" alt="%(logo_alt)s">
<br>
'''
main_footer = '''
<p>
<br>
%(back_to_index_link)s
</body>
</html>'''

rules_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<html>
<head>
<title>%(title)s</title>
<meta name="license" content="GNU General Public License">
<meta http-equiv="content-type" content="text/html; charset=utf-8">
</head>
<body text="#000000" bgcolor="#F7F3FF" link="#0000FF" vlink="#660099"
link="#FF0000">
<img src="../%(logo_url)s" alt="%(logo_alt)s">
<br>
'''
rules_footer = '''
<p>
%(footer)s
<br>
<a href="../glossary.html">Glossaire</a>
<br>
<a href="../general_rules.html">Règles générales</a>

<p>
<a href="../index.html">Sommaire</a>
</body>
</html>'''

wikipedia_header = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<html>
<head>
<title>%(title)s</title>
<meta name="license" content="GNU General Public License">
<meta http-equiv="content-type" content="text/html; charset=utf-8">
</head>
<body text="#000000" bgcolor="#F7F3FF" link="#0000FF" vlink="#660099"
alink="#FF0000">
<img src="../%(logo_url)s" alt="%(logo_alt)s">
<br>
'''


def getGameRulesFilename(n):
    if n.startswith('Mahjongg'):
        return 'mahjongg.html'
    return latin1_normalize(n) + '.html'


def gen_main_html():
    for infile, title in files:
        outfile = open(os.path.join('html', infile), 'w')
        print(_fmt(main_header, {'title': title}), file=outfile)
        with open(infile, 'r') as file:
            print(file.read(), file=outfile)
        s = '<a href="index.html">Sommaire</a>'
        if infile == 'index.html':
            s = ''
        print(_fmt(main_footer, {'back_to_index_link': s}), file=outfile)
        outfile.close()


def gen_rules_html():
    # ls = glob(os.path.join('rules', '*.html'))
    rules_ls = os.listdir('rules')
    rules_ls.sort()
    wikipedia_ls = os.listdir('wikipedia')
    wikipedia_ls.sort()

    games = GAME_DB.getGamesIdSortedByName()
    rules_list = []
    files_list = []
    for fn, tt in rules_files:
        rules_list.append(('rules', fn, tt, ''))
        files_list.append(fn)
    for fn, tt in wikipedia_files:
        rules_list.append(('wikipedia', fn, tt, ''))
        files_list.append(fn)
    altnames = []

    # open file of list of all rules
    out_rules = open(os.path.join('html', 'rules.html'), 'w')
    print(_fmt(
        main_header,
        {'title': 'PySol - une collection de jeux de solitaire'}),
        file=out_rules)
    with open('rules.html', 'r') as file:
        print(file.read(), file=out_rules)

    for id in games:
        # create list of rules

        gi = GAME_DB.get(id)

        rules_fn = gi.rules_filename
        if not rules_fn:
            rules_fn = getGameRulesFilename(gi.name)

        if rules_fn in files_list:
            continue

        if rules_fn in rules_ls:
            rules_dir = 'rules'
        elif rules_fn in wikipedia_ls:
            rules_dir = 'wikipedia'
        else:
            print('missing rules for %s (file: %s)'
                  % (gi.name, rules_fn))
            continue

        # print '>>>', rules_fn

        title = 'PySol - Règles pour ' + gi.name
        s = ''
        if gi.si.game_type == GI.GT_HANAFUDA:
            s = '<a href="../hanafuda.html">' + \
                'Règles générales des jeux de cartes à fleurs</a>'
        elif gi.si.game_type == GI.GT_DASHAVATARA_GANJIFA:
            s = '<a href="../ganjifa.html">A-propos du Ganjifa</a>'
        elif gi.si.game_type == GI.GT_HEXADECK:
            s = '<a href="../hexadeck.html">' + \
                'Règles générales du jeu Hex A Deck</a>'
        elif gi.si.game_type == GI.GT_MUGHAL_GANJIFA:
            s = '<a href="../ganjifa.html">A-propos du Ganjifa</a>'
            # print '***', gi.name, '***'

        rules_list.append((rules_dir, rules_fn, title, s))
        files_list.append(rules_fn)
        # rules_list.append((rules_fn, gi.name))
        print('<li><a href="rules/%s">%s</a>'
              % (rules_fn, gi.name), file=out_rules)
        for n in gi.altnames:
            altnames.append((n, rules_fn))

    print('</ul>\n' + _fmt(main_footer,
          {'back_to_index_link':
           '<a href="index.html">Sommaire</a>'}),
          file=out_rules)

    out_rules.close()

    # create file of altnames
    out_rules_alt = open(os.path.join('html', 'rules_alternate.html'), 'w')
    print(_fmt(
        main_header, {'title': 'PySol - une collection de jeux de solitaire'}),
        file=out_rules_alt)
    with open('rules_alternate.html', 'r') as file:
        print(file.read(), file=out_rules_alt)
    altnames.sort()
    for name, fn in altnames:
        print('<li> <a href="rules/%s">%s</a>'
              % (fn, name), file=out_rules_alt)
    print('</ul>\n' + _fmt(main_footer,
          {'back_to_index_link':
           '<a href="index.html">Sommaire</a>'}),
          file=out_rules_alt)
    out_rules_alt.close()

    # create rules
    for dir, filename, title, footer in rules_list:
        outfile = open(
            os.path.join('html', 'rules', filename), 'w', encoding='utf-8')
        if dir == 'rules':
            print(_fmt(rules_header, {'title': title}), file=outfile)
        else:  # d == 'wikipedia'
            print(_fmt(wikipedia_header, {'title': title}), file=outfile)
        with open(os.path.join(dir, filename), 'r', encoding='utf-8') as file:
            print(file.read(), file=outfile)
        print(_fmt(rules_footer, {'footer': footer}), file=outfile)
        outfile.close()


gen_main_html()
gen_rules_html()
