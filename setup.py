#!/usr/bin/env python
# -*- mode: python; -*-

import os
from distutils.core import setup
from pysollib.settings import FC_VERSION as VERSION
from pysollib.settings import PACKAGE_URL
if os.name == 'nt':
    import py2exe

if os.name == 'posix':
    data_dir = 'share/PySolFC'
elif os.name == 'nt':
    data_dir = 'data'
else:
    data_dir = 'data'

ddirs = [
    'html',
    'images',
    'sound',
    'tiles',
    'toolbar',
    'themes',
    'tcl',
    ]
for s in file('MANIFEST.in'):
    if s.startswith('graft data/cardset-'):
        ddirs.append(s[11:].strip())

data_files = []

for d in ddirs:
    for root, dirs, files in os.walk(os.path.join('data', d)):
        if root.find('.svn') >= 0:
            continue
        if files:
            #files = map(lambda f: os.path.join(root, f), files)
            files = [os.path.join(root, f) for f in files]
            data_files.append((os.path.join(data_dir, root[5:]), files))

if os.name == 'posix':
    data_files.append(('share/pixmaps', ['data/pysol.xbm', 'data/pysol.xpm']))
    for l in ('ru', 'ru_RU'):
        data_files.append(('share/locale/%s/LC_MESSAGES' % l,
                           ['locale/%s/LC_MESSAGES/pysol.mo' % l]))
    data_files.append((data_dir, ['data/pysolfc.glade']))

##from pprint import pprint; pprint(data_files)
##import sys; sys.exit()

long_description = '''\
PySol is a solitaire card game. Its features include support for many
different games, very nice look and feel, multiple cardsets and
backgrounds, unlimited undo & redo, load & save games, player
statistics, hint system, demo games, support for user written plug-ins,
integrated HTML help browser, and it\'s free Open Source software. 
'''

kw = {
    'name'         : 'PySolFC',
    'version'      : VERSION,
    'url'          : PACKAGE_URL,
    'author'       : 'Skomoroh',
    'author_email' : 'skomoroh@gmail.com',
    'description'  : 'PySol - a solitaire game collection',
    'long_description' : long_description,
    'license'      : 'GPL',
    'scripts'      : ['pysol.py'],
    'packages'     : ['pysollib',
                      'pysollib.configobj',
                      'pysollib.macosx',
                      'pysollib.winsystems',
                      'pysollib.tk',
                      'pysollib.tile',
                      'pysollib.pysolgtk',
                      'pysollib.games',
                      'pysollib.games.special',
                      'pysollib.games.ultra',
                      'pysollib.games.mahjongg'],
    'data_files'   : data_files,
    }
    
if os.name == 'nt':
    kw['windows'] = [{'script': 'pysol.py',
                      'icon_resources': [(1, 'data/pysol.ico')], }]
    kw['packages'].remove('pysollib.pysolgtk')

setup(**kw)
