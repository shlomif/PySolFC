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
import sys, os, glob, operator, types
#import traceback

# PySol imports
from mfxutil import win32api
from mfxutil import Struct, KwStruct, EnvError, latin1_to_ascii
from version import VERSION
from settings import PACKAGE


# /***********************************************************************
# // Abstract
# ************************************************************************/

class Resource(Struct):
    def __init__(self, **kw):
        kw = KwStruct(kw,
            name = "",
            filename = "",
            basename = "",      # basename of filename
            absname = "",       # absolute filename
            # implicit
            index = -1,
            error = 0,          # error while loading this resource
        )
        apply(Struct.__init__, (self,), kw.getKw())

    def getSortKey(self):
        return latin1_to_ascii(self.name).lower()


class ResourceManager:
    def __init__(self):
        self._selected_key = -1
        self._objects = []
        self._objects_by_name = None
        self._objects_cache_name = {}
        self._objects_cache_filename = {}
        self._objects_cache_basename = {}
        self._objects_cache_absname = {}

    def getSelected(self):
        return self._selected_key

    def setSelected(self, index):
        assert -1 <= index < len(self._objects)
        self._selected_key = index

    def len(self):
        return len(self._objects)

    def register(self, obj):
        assert obj.index == -1
        assert obj.name and not self._objects_cache_name.has_key(obj.name)
        self._objects_cache_name[obj.name] = obj
        if obj.filename:
            obj.absname = os.path.abspath(obj.filename)
            obj.basename = os.path.basename(obj.filename)
            self._objects_cache_filename[obj.filename] = obj
            self._objects_cache_basename[obj.basename] = obj
            self._objects_cache_absname[obj.absname] = obj
        obj.index = len(self._objects)
        self._objects.append(obj)
        self._objects_by_name = None    # invalidate

    def get(self, index):
        if 0 <= index < len(self._objects):
            return self._objects[index]
        return None

    def getByName(self, key):
        return self._objects_cache_name.get(key)

    def getByBasename(self, key):
        return self._objects_cache_basename.get(key)

    def getAll(self):
        return tuple(self._objects)

    def getAllSortedByName(self):
        if self._objects_by_name is None:
            l = map(lambda obj: (obj.getSortKey(), obj), self._objects)
            l.sort()
            self._objects_by_name = tuple(map(lambda item: item[1], l))
        return self._objects_by_name

    #
    # static methods
    #

    def _addDir(self, result, dir):
        try:
            if dir:
                dir = os.path.normpath(dir)
                if dir and os.path.isdir(dir) and not dir in result:
                    result.append(dir)
        except EnvError, ex:
            pass

    def _addRegistryKey(self, result, hkey, subkey):
        k = None
        try:
            k = win32api.RegOpenKeyEx(hkey, subkey, 0, KEY_READ)
            nsubkeys, nvalues, t = win32api.RegQueryInfoKey(k)
            for i in range(nvalues):
                try:
                    key, value, vtype = win32api.RegEnumValue(k, i)
                except:
                    break
                if not key or not value:
                    continue
                if vtype == 1 and type(value) is types.StringType:
                    for d in value.split(os.pathsep):
                        self._addDir(result, d.strip())
        finally:
            if k is not None:
                try:
                    win32api.RegCloseKey(k)
                except:
                    pass

    def getSearchDirs(self, app, search, env=None):
        if type(search) is types.StringType:
            search = (search,)
        result = []
        if env:
            for d in os.environ.get(env, "").split(os.pathsep):
                self._addDir(result, d.strip())
        for dir in (app.dataloader.dir, app.dn.maint, app.dn.config):
            if not dir:
                continue
            dir = os.path.normpath(dir)
            if not dir or not os.path.isdir(dir):
                continue
            for s in search:
                try:
                    if s[-2:] == "-*":
                        d = os.path.normpath(os.path.join(dir, s[:-2]))
                        self._addDir(result, d)
                        globdirs = glob.glob(d + "-*")
                        globdirs.sort()
                        for d in globdirs:
                            self._addDir(result, d)
                    else:
                        self._addDir(result, os.path.join(dir, s))
                except EnvError, ex:
                    pass
        if app.debug >= 2:
            print "getSearchDirs", env, search, "->", result
        return result

    def getRegistryDirs(self, app, categories):
        if not win32api:
            return []
        #
        vendors = ("Markus Oberhumer", "",)
        versions = (VERSION, "",)
        if type(categories) is types.StringType:
            categories = (categories,)
        #
        result = []
        for version in versions:
            for vendor in vendors:
                for category in categories:
                    t = ("Software", vendor, PACKAGE, version, category)
                    t = filter(None, t)
                    subkey = '\\'.join(t)
                    ##print "getRegistryDirs subkey", subkey
                    for hkey in (HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE):
                        try:
                            self._addRegistryKey(result, hkey, subkey)
                        except:
                            pass
        #
        if app.debug >= 2:
            print "getRegistryDirs", category, "->", result
        return result


# /***********************************************************************
# // Cardset
# ************************************************************************/

# CardsetInfo constants
class CSI:
    # cardset size
    SIZE_TINY   = 1
    SIZE_SMALL  = 2
    SIZE_MEDIUM = 3
    SIZE_LARGE  = 4
    SIZE_XLARGE = 5

    # cardset types
    TYPE_FRENCH   = 1
    TYPE_HANAFUDA = 2
    TYPE_TAROCK   = 3
    TYPE_MAHJONGG = 4
    TYPE_HEXADECK = 5
    TYPE_MUGHAL_GANJIFA = 6
    TYPE_NAVAGRAHA_GANJIFA = 7
    TYPE_DASHAVATARA_GANJIFA = 8
    TYPE_TRUMP_ONLY = 9

    TYPE = {
        1:  "French type (52 cards)",
        2:  "Hanafuda type (48 cards)",
        3:  "Tarock type (78 cards)",
        4:  "Mahjongg type (42 tiles)",
        5:  "Hex A Deck type (68 cards)",
        6:  "Mughal Ganjifa type (96 cards)",
        7:  "Navagraha Ganjifa type (108 cards)",
        8:  "Dashavatara Ganjifa type (120 cards)",
        9:  "Trumps only type (variable cards)",
    }

    # cardset styles
    STYLE = {
        1:  "Adult",                #
        2:  "Animals",              #
        3:  "Anime",                #
        4:  "Art",                  #
        5:  "Cartoons",             #
        6:  "Children",             #
        7:  "Classic look",         #
        8:  "Collectors",           # scanned collectors cardsets
        9:  "Computers",            #
       10:  "Engines",              #
       11:  "Fantasy",              #
       30:  "Ganjifa",              #
       12:  "Hanafuda",             #
       29:  "Hex A Deck",           #
       13:  "Holiday",              #
       28:  "Mahjongg",             #
       14:  "Movies",               #
       31:  "Matrix",               #
       15:  "Music",                #
       16:  "Nature",               #
       17:  "Operating Systems",    # e.g. cards with Linux logos
       19:  "People",               # famous people
       20:  "Places",               #
       21:  "Plain",                #
       22:  "Products",             #
       18:  "Round cardsets",       #
       23:  "Science Fiction",      #
       24:  "Sports",               #
       27:  "Tarock",               #
       25:  "Vehicels",             #
       26:  "Video Games",          #
    }

    # cardset nationality (suit and rank symbols)
    NATIONALITY = {
        1021:  "Australia",         #
        1001:  "Austria",           #
        1019:  "Belgium",           #
        1010:  "Canada",            #
        1011:  "China",             #
        1012:  "Czech Republic",    #
        1013:  "Denmark",           #
        1003:  "England",           #
        1004:  "France",            #
        1006:  "Germany",           #
        1014:  "Great Britain",     #
        1015:  "Hungary",           #
        1020:  "India",             #
        1005:  "Italy",             #
        1016:  "Japan",             #
        1002:  "Netherlands",       #
        1007:  "Russia",            #
        1008:  "Spain",             #
        1017:  "Sweden",            #
        1009:  "Switzerland",       #
        1018:  "USA",               #
    }

    # cardset creation date
    DATE = {
        10:  "1000 - 1099",
        11:  "1100 - 1199",
        12:  "1200 - 1299",
        13:  "1300 - 1399",
        14:  "1400 - 1499",
        15:  "1500 - 1599",
        16:  "1600 - 1699",
        17:  "1700 - 1799",
        18:  "1800 - 1899",
        19:  "1900 - 1999",
        20:  "2000 - 2099",
        21:  "2100 - 2199",
        22:  "2200 - 2299",
    }

    #
    TYPE_NAME = {}

def create_csi_type_name():
    for id, type in CSI.TYPE.items():
        i = type.find('type')
        if i > 0:
            CSI.TYPE_NAME[id] = type[:i-1]
        else:
            CSI.TYPE_NAME[id] = type

if not CSI.TYPE_NAME:
    create_csi_type_name()


class CardsetConfig(Struct):
    # see config.txt and _readCardsetConfig()
    def __init__(self):
        Struct.__init__(self,
            # line[0]
            version = 1,
            ext = ".gif",
            type = CSI.TYPE_FRENCH,
            ncards = -1,
            styles = [],
            year = 0,
            # line[1]
            ident = "",
            name = "",
            # line[2]
            CARDW = 0,
            CARDH = 0,
            CARDD = 0,
            # line[3]
            CARD_XOFFSET = 0,
            CARD_YOFFSET = 0,
            SHADOW_XOFFSET = 0,
            SHADOW_YOFFSET = 0,
            # line[4]
            backindex = 0,
            # line[5]
            backnames = (),
            # other
            CARD_DX = 0,        # relative pos of real card image within Card
            CARD_DY = 0,
        )


class Cardset(Resource):
    def __init__(self, **kw):
        # start with all fields from CardsetConfig
        config = CardsetConfig()
        kw = apply(KwStruct, (config.__dict__,), kw)
        # si is the SelectionInfo struct that will be queried by
        # the "select cardset" dialogs. It can be freely modified.
        si = Struct(type=0, size=0, styles=[], nationalities=[], dates=[])
        kw = KwStruct(kw,
            # essentials
            ranks = (),
            suits = (),
            trumps = (),
            nbottoms = 7,
            nletters = 4,
            nshadows = 1 + 13,
            # selection criterias
            si = si,
            # implicit
            backname = None,
            dir = "",
        )
        apply(Resource.__init__, (self,), kw.getKw())

    def getFaceCardNames(self):
        names = []
        for suit in self.suits:
            for rank in self.ranks:
                names.append("%02d%s" % (rank + 1, suit))
        for trump in self.trumps:
            names.append("%02d%s" % (trump + 1, "z"))
        assert len(names) == self.ncards
        return names

    def getPreviewCardNames(self):
        names = self.getFaceCardNames()
        pnames = []
        ranks, suits = self.ranks, self.suits
        lr, ls = len(ranks), len(suits)
        if lr == 0 or ls == 0:     # TYPE_TRUMP_ONLY
            return names[:16], 4
        if lr >= 4:
            ls = min(ls, 4)
        low_ranks, high_ranks = 1, 3
        ###if self.type == 3: high_ranks = 4
        for rank in range(0, low_ranks) + range(lr-high_ranks, lr):
            for suit in range(ls):
                index = suit * len(self.ranks) + rank
                pnames.append(names[index % len(names)])
        return pnames, ls

    def updateCardback(self, backname=None, backindex=None):
        # update default back
        if type(backname) is types.StringType:
            if backname in self.backnames:
                backindex = self.backnames.index(backname)
        if type(backindex) is types.IntType:
            self.backindex = backindex % len(self.backnames)
        self.backname = self.backnames[self.backindex]


class CardsetManager(ResourceManager):
    def __init__(self):
        ResourceManager.__init__(self)
        self.registered_types = {}
        self.registered_sizes = {}
        self.registered_styles = {}
        self.registered_nationalities = {}
        self.registered_dates = {}

    def _check(self, cs):
        s = cs.type
        if not CSI.TYPE.has_key(s):
            return 0
        cs.si.type = s
        if s == CSI.TYPE_FRENCH:
            cs.ranks = range(13)
            cs.suits = "cshd"
        elif s == CSI.TYPE_HANAFUDA:
            cs.ranks = range(12)
            cs.suits = "cshd"
        elif s == CSI.TYPE_TAROCK:
            cs.nbottoms = 8
            cs.ranks = range(14)
            cs.suits = "cshd"
            cs.trumps = range(22)
        elif s == CSI.TYPE_MAHJONGG:
            cs.ranks = range(10)
            cs.suits = "abc"
            cs.trumps = range(12)
            #
            cs.nbottoms = 0
            cs.nletters = 0
            cs.nshadows = 0
        elif s == CSI.TYPE_HEXADECK:
            cs.nbottoms = 8
            cs.ranks = range(16)
            cs.suits = "cshd"
            cs.trumps = range(4)
        elif s == CSI.TYPE_MUGHAL_GANJIFA:
            cs.nbottoms = 11
            cs.ranks = range(12)
            cs.suits = "abcdefgh"
        elif s == CSI.TYPE_NAVAGRAHA_GANJIFA:
            #???return 0                            ## FIXME
            cs.nbottoms = 12
            cs.ranks = range(12)
            cs.suits = "abcdefghi"
        elif s == CSI.TYPE_DASHAVATARA_GANJIFA:
            cs.nbottoms = 13
            cs.ranks = range(12)
            cs.suits = "abcdefghij"
        elif s == CSI.TYPE_TRUMP_ONLY:
            #???return 0                            ## FIXME
            #cs.nbottoms = 7
            #cs.ranks = ()
            #cs.suits = ""
            #cs.trumps = range(cs.ncards)
            cs.nbottoms = 1
            cs.nletters = 0
            cs.nshadows = 0
            cs.ranks = ()
            cs.suits = ""
            cs.trumps = range(cs.ncards)

        else:
            return 0
        return 1

    def register(self, cs):
        if not self._check(cs):
            return
        cs.ncards = len(cs.ranks) * len(cs.suits) + len(cs.trumps)
        cs.name = cs.name[:25]
        if not (1 <= cs.si.size <= 5):
            CW, CH = cs.CARDW, cs.CARDH
            if CW <= 55 and CH <= 72:
                cs.si.size = CSI.SIZE_TINY
            elif CW <= 60 and CH <= 85:
                cs.si.size = CSI.SIZE_SMALL
            elif CW <= 75 and CH <= 105:
                cs.si.size = CSI.SIZE_MEDIUM
            elif CW <= 90 and CH <= 125:
                cs.si.size = CSI.SIZE_LARGE
            else:
                cs.si.size = CSI.SIZE_XLARGE
        #
        keys = cs.styles[:]
        cs.si.styles = tuple(filter(lambda s: CSI.STYLE.has_key(s), keys))
        for s in cs.si.styles:
            self.registered_styles[s] = self.registered_styles.get(s, 0) + 1
        cs.si.nationalities = tuple(filter(lambda s: CSI.NATIONALITY.has_key(s), keys))
        for s in cs.si.nationalities:
            self.registered_nationalities[s] = self.registered_nationalities.get(s, 0) + 1
        keys = (cs.year / 100,)
        cs.si.dates = tuple(filter(lambda s: CSI.DATE.has_key(s), keys))
        for s in cs.si.dates:
            self.registered_dates[s] = self.registered_dates.get(s, 0) + 1
        #
        s = cs.si.type
        self.registered_types[s] = self.registered_types.get(s, 0) + 1
        s = cs.si.size
        self.registered_sizes[s] = self.registered_sizes.get(s, 0) + 1
        cs.updateCardback()
        ResourceManager.register(self, cs)


# /***********************************************************************
# // Tile
# ************************************************************************/

class Tile(Resource):
    def __init__(self, **kw):
        kw = KwStruct(kw,
                      color = None,
                      text_color = "#000000",
                      stretch = 0,
                      )
        apply(Resource.__init__, (self,), kw.getKw())


class TileManager(ResourceManager):
    pass


# /***********************************************************************
# // Sample
# ************************************************************************/

class Sample(Resource):
    def __init__(self, **kw):
        kw = KwStruct(kw,
            volume = -1,
        )
        apply(Resource.__init__, (self,), kw.getKw())


class SampleManager(ResourceManager):
    pass


# /***********************************************************************
# // Music
# ************************************************************************/

class Music(Sample):
    pass


class MusicManager(SampleManager):
    pass

