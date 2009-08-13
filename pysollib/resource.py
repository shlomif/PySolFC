#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##---------------------------------------------------------------------------##


# imports
import os, glob, traceback

# PySol imports
from mfxutil import Struct, KwStruct
from settings import DEBUG


# ************************************************************************
# * Abstract
# ************************************************************************

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
        Struct.__init__(self, **kw.getKw())

    def getSortKey(self):
        return self.name.lower()
        #return latin1_to_ascii(self.name).lower()


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
        assert obj.name and obj.name not in self._objects_cache_name
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
            l = [(obj.getSortKey(), obj) for obj in self._objects]
            l.sort()
            self._objects_by_name = tuple([item[1] for item in l])
        return self._objects_by_name

    #
    # static methods
    #

    def _addDir(self, result, dir):
        try:
            if dir:
                dir = os.path.normpath(dir)
                if dir and os.path.isdir(dir) and dir not in result:
                    result.append(dir)
        except EnvironmentError, ex:
            pass

    def getSearchDirs(self, app, search, env=None):
        if isinstance(search, str):
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
                except EnvironmentError, ex:
                    traceback.print_exc()
                    pass
        if DEBUG >= 6:
            print "getSearchDirs", env, search, "->", result
        return result


# ************************************************************************
# * Cardset
# ************************************************************************

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
        1:  _("French type (52 cards)"),
        2:  _("Hanafuda type (48 cards)"),
        3:  _("Tarock type (78 cards)"),
        4:  _("Mahjongg type (42 tiles)"),
        5:  _("Hex A Deck type (68 cards)"),
        6:  _("Mughal Ganjifa type (96 cards)"),
        7:  _("Navagraha Ganjifa type (108 cards)"),
        8:  _("Dashavatara Ganjifa type (120 cards)"),
        9:  _("Trumps only type (variable cards)"),
    }

    TYPE_NAME = {
        1:  _("French"),
        2:  _("Hanafuda"),
        3:  _("Tarock"),
        4:  _("Mahjongg"),
        5:  _("Hex A Deck"),
        6:  _("Mughal Ganjifa"),
        7:  _("Navagraha Ganjifa"),
        8:  _("Dashavatara Ganjifa"),
        9:  _("Trumps only"),
    }

    TYPE_ID = {
        1: "french",
        2: "hanafuda",
        3: "tarock",
        4: "mahjongg",
        5: "hex-a-deck",
        6: "mughal-ganjifa",
        7: "navagraha-ganjifa",
        8: "dashavatara-ganjifa",
        9: "trumps-only",
    }

    # cardset styles
    STYLE = {
        1:  _("Adult"),                #
        2:  _("Animals"),              #
        3:  _("Anime"),                #
        4:  _("Art"),                  #
        5:  _("Cartoons"),             #
        6:  _("Children"),             #
        7:  _("Classic look"),         #
        8:  _("Collectors"),           # scanned collectors cardsets
        9:  _("Computers"),            #
       10:  _("Engines"),              #
       11:  _("Fantasy"),              #
       30:  _("Ganjifa"),              #
       12:  _("Hanafuda"),             #
       29:  _("Hex A Deck"),           #
       13:  _("Holiday"),              #
       28:  _("Mahjongg"),             #
       14:  _("Movies"),               #
       31:  _("Matrix"),               #
       15:  _("Music"),                #
       16:  _("Nature"),               #
       17:  _("Operating Systems"),    # e.g. cards with Linux logos
       19:  _("People"),               # famous people
       20:  _("Places"),               #
       21:  _("Plain"),                #
       22:  _("Products"),             #
       18:  _("Round cardsets"),       #
       23:  _("Science Fiction"),      #
       24:  _("Sports"),               #
       27:  _("Tarock"),               #
       25:  _("Vehicels"),             #
       26:  _("Video Games"),          #
    }

    # cardset nationality (suit and rank symbols)
    NATIONALITY = {
        1021:  _("Australia"),         #
        1001:  _("Austria"),           #
        1019:  _("Belgium"),           #
        1010:  _("Canada"),            #
        1011:  _("China"),             #
        1012:  _("Czech Republic"),    #
        1013:  _("Denmark"),           #
        1003:  _("England"),           #
        1004:  _("France"),            #
        1006:  _("Germany"),           #
        1014:  _("Great Britain"),     #
        1015:  _("Hungary"),           #
        1020:  _("India"),             #
        1005:  _("Italy"),             #
        1016:  _("Japan"),             #
        1002:  _("Netherlands"),       #
        1007:  _("Russia"),            #
        1008:  _("Spain"),             #
        1017:  _("Sweden"),            #
        1009:  _("Switzerland"),       #
        1018:  _("USA"),               #
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
        kw = KwStruct(config.__dict__, **kw)
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
        Resource.__init__(self, **kw.getKw())

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
        if isinstance(backname, basestring):
            if backname in self.backnames:
                backindex = self.backnames.index(backname)
        if isinstance(backindex, int):
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
        if s not in CSI.TYPE:
            return 0
        cs.si.type = s
        if s == CSI.TYPE_FRENCH:
            cs.ranks = range(13)
            cs.suits = "cshd"
        elif s == CSI.TYPE_HANAFUDA:
            cs.nbottoms = 15
            cs.ranks = range(4)
            cs.suits = "abcdefghijkl"
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
        cs.si.styles = tuple([s for s in keys if s in CSI.STYLE])
        for s in cs.si.styles:
            self.registered_styles[s] = self.registered_styles.get(s, 0) + 1
        cs.si.nationalities = tuple([s for s in keys if s in CSI.NATIONALITY])
        for s in cs.si.nationalities:
            self.registered_nationalities[s] = self.registered_nationalities.get(s, 0) + 1
        keys = (cs.year / 100,)
        cs.si.dates = tuple([s for s in keys if s in CSI.DATE])
        for s in cs.si.dates:
            self.registered_dates[s] = self.registered_dates.get(s, 0) + 1
        #
        s = cs.si.type
        self.registered_types[s] = self.registered_types.get(s, 0) + 1
        s = cs.si.size
        self.registered_sizes[s] = self.registered_sizes.get(s, 0) + 1
        cs.updateCardback()
        ResourceManager.register(self, cs)


# ************************************************************************
# * Tile
# ************************************************************************

class Tile(Resource):
    def __init__(self, **kw):
        kw['color'] = None
        kw['stretch'] = 0
        kw['save_aspect'] = 0
        Resource.__init__(self, **kw)


class TileManager(ResourceManager):
    pass


# ************************************************************************
# * Sample
# ************************************************************************

class Sample(Resource):
    def __init__(self, **kw):
        kw['volume'] = -1
        Resource.__init__(self, **kw)


class SampleManager(ResourceManager):
    pass


# ************************************************************************
# * Music
# ************************************************************************

class Music(Sample):
    pass


class MusicManager(SampleManager):
    pass

