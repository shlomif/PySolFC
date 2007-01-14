## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##


# imports
import os, time, types

try:
    from cPickle import Pickler, Unpickler, UnpicklingError
except ImportError:
    from pickle import Pickler, Unpickler, UnpicklingError

try:
    import thread
except:
    thread = None

from settings import TOOLKIT
Image = ImageTk = ImageOps = None
if TOOLKIT == 'tk':
    try: # PIL
        import Image
    except ImportError:
        pass
    else:
        import ImageTk
        import ImageOps
        # for py2exe
        import GifImagePlugin
        import PngImagePlugin
        import JpegImagePlugin
        import BmpImagePlugin
        import PpmImagePlugin
        Image._initialized=2

if os.name == "mac":
    # macfs module is deprecated, consider using Carbon.File or Carbon.Folder
    import macfs, MACFS

# /***********************************************************************
# // exceptions
# ************************************************************************/

# work around a Mac problem
##EnvError = EnvironmentError
EnvError = (IOError, OSError, os.error,)


class SubclassResponsibility(Exception):
    pass


# /***********************************************************************
# // misc. util
# ************************************************************************/


def latin1_to_ascii(n):
    #return n
    n = n.encode('iso8859-1', 'replace')
    ## FIXME: rewrite this for better speed
    n = (n.replace("\xc4", "Ae")
         .replace("\xd6", "Oe")
         .replace("\xdc", "Ue")
         .replace("\xe4", "ae")
         .replace("\xf6", "oe")
         .replace("\xfc", "ue"))
    return n

## import htmlentitydefs
## htmlentitydefs_i = {}
## def latin1_to_html(n):
##     global htmlentitydefs_i
##     if not htmlentitydefs_i:
##         for k, v in htmlentitydefs.entitydefs.items():
##             htmlentitydefs_i[v] = "&" + k + ";"
##     s, g = "", htmlentitydefs_i.get
##     for c in n:
##         s = s + g(c, c)
##     return s


## def hexify(s):
##     return "%02x"*len(s) % tuple(map(ord, s))


def format_time(t):
    ##print 'format_time:', t
    if t <= 0: return "0:00"
    if t < 3600: return "%d:%02d" % (t / 60, t % 60)
    return "%d:%02d:%02d" % (t / 3600, (t % 3600) / 60, t % 60)


# /***********************************************************************
# // misc. portab stuff
# ************************************************************************/

def getusername():
    if os.name == "nt":
        return win32_getusername()
    user = os.environ.get("USER","").strip()
    if not user:
        user = os.environ.get("LOGNAME","").strip()
    return user


def gethomedir():
    if os.name == "nt":
        return win32_gethomedir()
    home = os.environ.get("HOME", "").strip()
    if not home or not os.path.isdir(home):
        home = os.curdir
    return os.path.abspath(home)


def getprefdir(package, home=None):
    if os.name == "nt":
        return win32_getprefdir(package)
    if os.name == "mac":
        vrefnum, dirid = macfs.FindFolder(MACFS.kOnSystemDisk, MACFS.kPreferencesFolderType, 0)
        fss = macfs.FSSpec((vrefnum, dirid, ":" + "PySolFC"))
        return fss.as_pathname()
    if home is None:
        home = gethomedir()
    return os.path.join(home, ".PySolFC")


# high resolution clock() and sleep()
uclock = time.clock
usleep = time.sleep
if os.name == "posix":
    uclock = time.time

# /***********************************************************************
# // MSWin util
# ************************************************************************/

def win32_getusername():
    user = os.environ.get('USERNAME','').strip()
    return user

def win32_getprefdir(package):
    hd = win32_gethomedir()
    return os.path.join(hd, 'PySolFC')

def win32_gethomedir():
    # %USERPROFILE%, %APPDATA%
    hd = os.environ.get('APPDATA')
    if hd:
        return hd
    hd = os.path.expanduser('~')
    if hd == '~': # win9x
        return os.path.abspath('/')
    return hd

# /***********************************************************************
# // memory util
# ************************************************************************/

def destruct(obj):
    # assist in breaking circular references
    if obj is not None:
        assert isinstance(obj, types.InstanceType)
        for k in obj.__dict__.keys():
            obj.__dict__[k] = None
            ##del obj.__dict__[k]


# /***********************************************************************
# //
# ************************************************************************/

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
        for key in kw.keys():
            if hasattr(self, key):
                raise AttributeError(key)
        self.__dict__.update(kw)

    def update(self, dict):
        for key in dict.keys():
            if key not in self.__dict__:
                raise AttributeError(key)
        self.__dict__.update(dict)

    def clear(self):
        for key in self.__dict__.keys():
            if isinstance(key, list):
                self.__dict__[key] = []
            elif isinstance(key, tuple):
                self.__dict__[key] = ()
            elif isinstance(key, dict):
                self.__dict__[key] = {}
            else:
                self.__dict__[key] = None

    def copy(self):
        c = Struct()
        c.__class__ = self.__class__
        c.__dict__.update(self.__dict__)
        return c


# /***********************************************************************
# // keyword argument util
# ************************************************************************/

# update keyword arguments with default arguments
def kwdefault(kw, **defaults):
    for k, v in defaults.items():
        if k not in kw:
            kw[k] = v


class KwStruct:
    def __init__(self, kw={}, **defaults):
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


# /***********************************************************************
# // pickling support
# ************************************************************************/

def pickle(obj, filename, binmode=0):
    f = None
    try:
        f = open(filename, "wb")
        p = Pickler(f, binmode)
        p.dump(obj)
        f.close(); f = None
        ##print "Pickled", filename
    finally:
        if f: f.close()


def unpickle(filename):
    f, obj = None, None
    try:
        f = open(filename, "rb")
        p = Unpickler(f)
        x = p.load()
        f.close(); f = None
        obj = x
        ##print "Unpickled", filename
    finally:
        if f: f.close()
    return obj


# /***********************************************************************
# //
# ************************************************************************/

def openURL(url):
    try:
        import webbrowser
        webbrowser.open(url)
        return 1
    except ImportError:                 # FIXME
        return 0


