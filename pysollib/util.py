#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

# imports
import os
try:
    import site
except Exception:
    class Dummy:
        def __init__(self):
            self.PREFIXES = []
    site = Dummy()
import sys

# PySol imports
from pysollib.mfxutil import Image
from pysollib.mygettext import _
from pysollib.settings import DATA_DIRS, TOOLKIT

# ************************************************************************
# * constants
# ************************************************************************

# Suits values are 0-3. This maps to colors 0-1.
SUITS = (_("Club"), _("Spade"), _("Heart"), _("Diamond"))
COLORS = (_("black"), _("red"))

# Card ranks are 0-12.  We also define symbolic names for the picture cards.
RANKS = (_("Ace"), "2", "3", "4", "5", "6", "7", "8", "9", "10",
         _("Jack"), _("Queen"), _("King"))
ACE = 0
JACK = 10
QUEEN = 11
KING = 12

# Special values for Stack.cap:
ANY_SUIT = -1
ANY_COLOR = -1
ANY_RANK = -1
NO_SUIT = 999999            # no card can ever match this suit
NO_COLOR = 999999           # no card can ever match this color
NO_RANK = 999999            # no card can ever match this rank
UNLIMITED_MOVES = 999999    # for max_move
UNLIMITED_ACCEPTS = 999999  # for max_accept
UNLIMITED_CARDS = 999999    # for max_cards
#
NO_REDEAL = 0
UNLIMITED_REDEALS = -1
VARIABLE_REDEALS = -2

CARDSET = _("cardset")

IMAGE_EXTENSIONS = (".gif", ".ppm", ".png")
if 1 and os.name == "nt":
    IMAGE_EXTENSIONS = (".png", ".gif", ".ppm", ".jpg",)
    pass

if Image:
    IMAGE_EXTENSIONS = (".png", ".gif", ".jpg", ".ppm", ".bmp")

if TOOLKIT == 'kivy':
    IMAGE_EXTENSIONS = (".png", ".bmp", ".ppm", ".jpg", ".tiff")

# ************************************************************************
# * DataLoader
# ************************************************************************


class DataLoader:
    def __init__(self, argv0, filenames, path=[]):
        self.dir = None
        if isinstance(filenames, str):
            filenames = (filenames,)
        assert isinstance(filenames, (tuple, list))
        # init path
        path = path[:]
        head, tail = os.path.split(argv0)
        if not head:
            head = os.curdir
        # dir where placed startup script
        path.append(head)
        path.append(os.path.join(head, "data"))
        path.append(os.path.join(head, os.pardir, "data"))
        # dir where placed pysol package
        path.append(os.path.join(sys.path[0], "data"))
        path.append(os.path.join(sys.path[0], "pysollib", "data"))
        # from settings.py
        path.extend(DATA_DIRS)
        # py2app compatibility, see
        # https://github.com/shlomif/PySolFC/issues/100
        _prefixes = []
        try:
            _prefixes = site.PREFIXES
        except Exception:
            _prefixes = []
        # itz 2018-10-21 in case of venv installation
        # (or even homedir installation), path[0] will be quite wrong.
        # Just directly use the location where setup.py puts the data.
        for pref in _prefixes:
            path.append(os.path.join(pref, 'share', 'PySolFC'))
        # check path for valid directories
        self.path = []
        for p in path:
            if not p:
                continue
            np = os.path.abspath(p)
            if np and (np not in self.path) and os.path.isdir(np):
                self.path.append(np)
        # now try to find all filenames along path
        for p in self.path:
            if all(os.path.isfile(os.path.join(p, fn)) for fn in filenames):
                self.dir = p
                break
        else:
            raise OSError(str(argv0)+": DataLoader could not find " +
                          str(filenames))

    def __findFile(self, func, filename, subdirs=None, do_raise=1):
        if subdirs is None:
            subdirs = ("",)
        elif isinstance(subdirs, str):
            subdirs = (subdirs,)
        for dir in subdirs:
            f = os.path.join(self.dir, dir, filename)
            f = os.path.normpath(f)
            if func(f):
                return f
        if do_raise:
            raise OSError("DataLoader could not find "+filename+" in " +
                          self.dir+" "+str(subdirs))
        return None

    def findFile(self, filename, subdirs=None):
        return self.__findFile(os.path.isfile, filename, subdirs)

    def findImage(self, filename, subdirs=None):
        for ext in IMAGE_EXTENSIONS:
            f = self.__findFile(os.path.isfile, filename+ext, subdirs, 0)
            if f:
                return f
        raise OSError("DataLoader could not find image "+filename +
                      " in "+self.dir+" "+str(subdirs))

    def findAllIconSizes(self, filename='pysol.png'):
        try:
            icondir = self.findDir(os.path.join('images', 'icons'))
            icons = [os.path.join(icondir, subdir, filename) for subdir in
                     os.listdir(icondir)]
        except OSError:
            try:
                # pysol06.png is known to have transparent borders around it
                # which is unsuitable for a window icon
                icon_blacklist = ('pysol06.png',)
                miscdir = self.findDir(os.path.join('images', 'misc'))
                icons = [os.path.join(miscdir, f) for f in os.listdir(miscdir)
                         if f not in icon_blacklist]
            except OSError:
                icons = []
        return filter(os.path.isfile, icons)

    def findDir(self, filename, subdirs=None):
        return self.__findFile(os.path.isdir, filename, subdirs)
