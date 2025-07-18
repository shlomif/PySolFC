#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
#  Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
#  Copyright (C) 2003 Mt. Hood Playing Card Co.
#  Copyright (C) 2005-2009 Skomoroh
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

import locale
import os
import re
import sys
import time
import webbrowser
from pickle import Pickler, Unpickler

from pysollib.settings import PACKAGE, TOOLKIT

Image = ImageTk = ImageOps = ImageDraw = None
if TOOLKIT == 'tk':
    try:  # PIL
        from PIL import Image
        from PIL import ImageTk  # noqa: F401
        from PIL import ImageOps  # noqa: F401
        from PIL import ImageDraw  # noqa: F401
    except ImportError:
        Image = None
    else:
        # for py2exe
        from PIL import GifImagePlugin  # noqa: F401
        from PIL import PngImagePlugin  # noqa: F401
        from PIL import JpegImagePlugin  # noqa: F401
        from PIL import BmpImagePlugin  # noqa: F401
        from PIL import PpmImagePlugin  # noqa: F401
        Image._initialized = 2
USE_PIL = False
if TOOLKIT == 'tk' and Image:
    USE_PIL = True

# debug
# Image = None
# USE_PIL = False

# ************************************************************************
# * exceptions
# ************************************************************************


class SubclassResponsibility(Exception):
    pass


# ************************************************************************
# * misc. util
# ************************************************************************


def latin1_to_ascii(n):
    if sys.version_info > (3,):
        return n
    # return n
    n = n.encode('iso8859-1', 'replace')
    # FIXME: rewrite this for better speed
    return (n.replace("\xc4", "Ae")
             .replace("\xd6", "Oe")
             .replace("\xdc", "Ue")
             .replace("\xe4", "ae")
             .replace("\xf6", "oe")
             .replace("\xfc", "ue"))


def latin1_normalize(n):
    normal = re.sub(r"[^\w]", "", latin1_to_ascii(n).lower())
    # Some game names end in a +, and would have the same normalized
    # name as their counterpart.  This is a failsafe to avoid duplicate
    # name conflicts.  Though there is probably a better way to do this.
    if n.endswith("+"):
        normal += "plus"
    return normal


def format_time(t):
    # print 'format_time:', t
    if t <= 0:
        return "0:00"
    if t < 3600:
        return "%d:%02d" % (t // 60, t % 60)
    return "%d:%02d:%02d" % (t // 3600, (t % 3600) // 60, t % 60)


def get_default_resampling():
    if not USE_PIL:
        return 0
    if hasattr(Image, "ANTIALIAS"):
        return Image.ANTIALIAS
    if hasattr(Image, "LANCZOS"):
        return Image.LANCZOS
    return Image.NEAREST


def print_err(s, level=1):
    if level == 0:
        ss = PACKAGE+': ERROR:'
    elif level == 1:
        ss = PACKAGE+': WARNING:'
    elif level == 2:
        ss = PACKAGE+': DEBUG WARNING:'
    try:
        print(ss, s, file=sys.stderr)
    except Exception:
        print(ss, s.encode(locale.getpreferredencoding()), file=sys.stderr)
    sys.stderr.flush()


# ************************************************************************
# * misc. portab stuff
# ************************************************************************

def getusername():
    if os.name == "nt":
        return win32_getusername()
    user = os.environ.get("USER", "").strip()
    if not user:
        user = os.environ.get("LOGNAME", "").strip()
    return user


def getprefdir(package):

    if (TOOLKIT == 'kivy'):
        from pysollib.kivy.LApp import get_platform
        plat = get_platform()
        if plat == 'android':
            from pysollib.kivy.androidperms import getStoragePerm
            from android.storage import primary_external_storage_path
            from android.storage import app_storage_path
            if getStoragePerm():
                os.environ['HOME'] = primary_external_storage_path()
            else:
                os.environ['HOME'] = app_storage_path()

    if os.name == "nt":
        return win32_getprefdir(package)
    home = os.environ.get("HOME", "").strip()
    if not home or not os.path.isdir(home):
        home = os.curdir
    return os.path.join(home, ".PySolFC")


# high resolution clock() and sleep()
try:
    uclock = time.perf_counter
except Exception:
    uclock = time.clock

usleep = time.sleep
if os.name == "posix":
    uclock = time.time

# ************************************************************************
# * MSWin util
# ************************************************************************


def win32_getusername():
    user = os.environ.get('USERNAME', '').strip()
    try:
        user = str(user, locale.getpreferredencoding())
    except Exception:
        user = ''
    return user


def win32_getprefdir(package):
    portprefdir = 'config'      # portable varsion
    if os.path.isdir(portprefdir):
        return portprefdir
    # %USERPROFILE%, %APPDATA%
    hd = os.environ.get('APPDATA')
    if not hd:
        hd = os.path.expanduser('~')
        if hd == '~':  # win9x
            hd = os.path.abspath('/windows/Application Data')
            if not os.path.exists(hd):
                hd = os.path.abspath('/')
    return os.path.join(hd, 'PySolFC')


# ************************************************************************
# * memory util
# ************************************************************************

def destruct(obj):
    if TOOLKIT == 'kivy':
        return

    # assist in breaking circular references
    if obj is not None:
        for k in obj.__dict__.keys():
            obj.__dict__[k] = None
            # del obj.__dict__[k]


# ************************************************************************
# *
# ************************************************************************

class Struct:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __str__(self):
        return str(self.__dict__)

    def __setattr__(self, key, value):
        if key not in self.__dict__:
            raise AttributeError(key)
        self.__dict__[key] = value

    def addattr(self, **kw):
        for key in kw:
            if hasattr(self, key):
                raise AttributeError(key)
        self.__dict__.update(kw)

    def update(self, dict):
        for key in dict.keys():
            if key not in self.__dict__:
                raise AttributeError(key)
        self.__dict__.update(dict)

    def clear(self):
        for key in self.__dict__:
            if isinstance(key, list):
                self.__dict__[key] = []
            elif isinstance(key, tuple):
                self.__dict__[key] = ()
            elif isinstance(key, dict):
                self.__dict__[key] = {}
            else:
                self.__dict__[key] = None

    def copy(self):
        c = self.__class__()
        c.__dict__.update(self.__dict__)
        return c


# ************************************************************************
# * keyword argument util
# ************************************************************************

# update keyword arguments with default arguments
def kwdefault(kw, **defaults):
    for k, v in defaults.items():
        if k not in kw:
            kw[k] = v


class KwStruct:
    def __init__(self, kw=None, **defaults):
        if kw is None:
            kw = {}
        if isinstance(kw, KwStruct):
            kw = kw.__dict__
        if isinstance(defaults, KwStruct):
            defaults = defaults.__dict__
        if defaults:
            kw = kw.copy()
            for k, v in defaults.items():
                if k not in kw:
                    kw[k] = v
        self.__dict__.update(kw)

    def __setattr__(self, key, value):
        if key not in self.__dict__:
            raise AttributeError(key)
        self.__dict__[key] = value

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def getKw(self):
        return self.__dict__


# ************************************************************************
# * pickling support
# ************************************************************************

def pickle(obj, filename, protocol=0):
    try:
        with open(filename, "wb") as fh:
            Pickler(fh, protocol).dump(obj)
        # print "Pickled", filename
    finally:
        pass


def unpickle(filename):
    obj = None
    try:
        with open(filename, "rb") as fh:
            x = Unpickler(fh).load()
        obj = x
        # print "Unpickled", filename
    finally:
        pass
    return obj


# ************************************************************************
# *
# ************************************************************************

def openURL(url):
    try:
        webbrowser.open(url)
    except OSError:                  # raised on windows if link is unreadable
        pass
    except Exception:
        return False
    return True
