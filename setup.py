#!/usr/bin/env python
# -*- mode: python; -*-

import os

from pysollib.settings import PACKAGE_URL
from pysollib.settings import VERSION

from setuptools import setup

if os.name == 'nt':
    import py2exe  # noqa: F401


def get_data_files(source, destination):
    """Iterates over all files under the given tree, to install them to the
    destination using the data_files keyword of setuptools.setup."""
    for path, _, files in os.walk(source):
        files = [os.path.join(path, f) for f in files]
        path = path.replace(source, destination, 1)
        yield (path, files)


if os.name == 'posix':
    data_dir = 'share/PySolFC'
    locale_dir = 'share/locale'
else:
    data_dir = 'data'
    locale_dir = 'locale'

ddirs = [
    'html',
    'images',
    'sound',
    'tiles',
    'toolbar',
    'themes',
    'tcl',
    ]
for s in open('MANIFEST.in'):
    if s.startswith('graft data/cardset-'):
        ddirs.append(s[11:].strip())

data_files = []

for d in ddirs:
    data_files += get_data_files(os.path.join('data', d),
                                 os.path.join(data_dir, d))

data_files += get_data_files('locale', locale_dir)

if os.name == 'posix':
    for size in os.listdir('data/images/icons'):
        data_files.append(('share/icons/hicolor/%s/apps' % size,
                           ['data/images/icons/%s/pysol.png' % size]))
    data_files.append((data_dir, ['data/pysolfc.glade']))
    data_files.append(('share/applications', ['data/pysol.desktop']))

# from pprint import pprint; pprint(data_files)
# import sys; sys.exit()

long_description = '''\
PySolFC is a collection of more than 1000 solitaire card games.
Its features include modern look and feel (uses Tile widget set), multiple
cardsets and tableau backgrounds, sound, unlimited undo, player statistics,
a hint system, demo games, a solitaire wizard, support for user written
plug-ins, an integrated HTML help browser, and lots of documentation.
'''

kw = {
    'name': 'PySolFC',
    'version': VERSION,
    'url': PACKAGE_URL,
    'author': 'Skomoroh',
    'author_email': 'skomoroh@gmail.com',
    'description': 'a Python solitaire game collection',
    'install_requires': [
        'attrs',
        'configobj',
        'pycotap',
        'pysol_cards',
        'random2',
        'six',
    ],
    'long_description': long_description,
    'license': 'GPL',
    'scripts': ['pysol.py'],
    'packages': ['pysollib',
                 'pysollib.macosx',
                 'pysollib.winsystems',
                 'pysollib.tk',
                 'pysollib.tile',
                 'pysollib.pysolgtk',
                 'pysollib.ui',
                 'pysollib.ui.tktile',
                 'pysollib.kivy',
                 'pysollib.game',
                 'pysollib.games',
                 'pysollib.games.special',
                 'pysollib.games.ultra',
                 'pysollib.games.mahjongg'],
    'data_files': data_files,
    }

if os.name == 'nt':
    kw['windows'] = [{'script': 'pysol.py',
                      'icon_resources': [(1, 'data/pysol.ico')], }]
    kw['packages'].remove('pysollib.pysolgtk')

setup(**kw)
