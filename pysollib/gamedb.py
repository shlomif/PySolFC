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
import imp

# PySol imports
from mfxutil import Struct, print_err
from resource import CSI
import settings


# ************************************************************************
# * constants
# ************************************************************************

# GameInfo constants
class GI:
    # game category - these *must* match the cardset CSI.TYPE_xxx
    GC_FRENCH        = CSI.TYPE_FRENCH
    GC_HANAFUDA      = CSI.TYPE_HANAFUDA
    GC_TAROCK        = CSI.TYPE_TAROCK
    GC_MAHJONGG      = CSI.TYPE_MAHJONGG
    GC_HEXADECK      = CSI.TYPE_HEXADECK
    GC_MUGHAL_GANJIFA = CSI.TYPE_MUGHAL_GANJIFA
    GC_NAVAGRAHA_GANJIFA = CSI.TYPE_NAVAGRAHA_GANJIFA
    GC_DASHAVATARA_GANJIFA = CSI.TYPE_DASHAVATARA_GANJIFA
    GC_TRUMP_ONLY    = CSI.TYPE_TRUMP_ONLY

    # game type
    GT_1DECK_TYPE   = 0
    GT_2DECK_TYPE   = 1
    GT_3DECK_TYPE   = 2
    GT_4DECK_TYPE   = 3
    GT_BAKERS_DOZEN = 4
    GT_BELEAGUERED_CASTLE = 5
    GT_CANFIELD     = 6
    GT_DASHAVATARA_GANJIFA = 7
    GT_FAN_TYPE     = 8
    GT_FORTY_THIEVES = 9
    GT_FREECELL     = 10
    GT_GOLF         = 11
    GT_GYPSY        = 12
    GT_HANAFUDA     = 13
    GT_HEXADECK     = 14
    GT_KLONDIKE     = 15
    GT_MAHJONGG     = 16
    GT_MATRIX       = 17
    GT_MEMORY       = 18
    GT_MONTANA      = 19
    GT_MUGHAL_GANJIFA = 20
    GT_NAPOLEON     = 21
    GT_NAVAGRAHA_GANJIFA = 22
    GT_NUMERICA     = 23
    GT_PAIRING_TYPE = 24
    GT_POKER_TYPE   = 25
    GT_PUZZLE_TYPE  = 26
    GT_RAGLAN       = 27
    GT_ROW_TYPE     = 28
    GT_SIMPLE_TYPE  = 29
    GT_SPIDER       = 30
    GT_TAROCK       = 31
    GT_TERRACE      = 32
    GT_YUKON        = 33
    GT_SHISEN_SHO   = 34
    GT_CUSTOM       = 40
    # extra flags
    GT_BETA          = 1 << 12      # beta version of game driver
    GT_CHILDREN      = 1 << 13      # *not used*
    GT_CONTRIB       = 1 << 14      # contributed games under the GNU GPL
    GT_HIDDEN        = 1 << 15      # not visible in menus, but games can be loaded
    GT_OPEN          = 1 << 16
    GT_ORIGINAL      = 1 << 17
    GT_POPULAR       = 1 << 18      # *not used*
    GT_RELAXED       = 1 << 19
    GT_SCORE         = 1 << 20      # game has some type of scoring
    GT_SEPARATE_DECKS = 1 << 21
    GT_XORIGINAL     = 1 << 22      # original games by other people, not playable
    # skill level
    SL_LUCK         = 1
    SL_MOSTLY_LUCK  = 2
    SL_BALANCED     = 3
    SL_MOSTLY_SKILL = 4
    SL_SKILL        = 5
    #
    TYPE_NAMES = {
        GT_BAKERS_DOZEN:        n_("Baker's Dozen"),
        GT_BELEAGUERED_CASTLE:  n_("Beleaguered Castle"),
        GT_CANFIELD:            n_("Canfield"),
        GT_FAN_TYPE:            n_("Fan"),
        GT_FORTY_THIEVES:       n_("Forty Thieves"),
        GT_FREECELL:            n_("FreeCell"),
        GT_GOLF:                n_("Golf"),
        GT_GYPSY:               n_("Gypsy"),
        GT_KLONDIKE:            n_("Klondike"),
        GT_MONTANA:             n_("Montana"),
        GT_NAPOLEON:            n_("Napoleon"),
        GT_NUMERICA:            n_("Numerica"),
        GT_PAIRING_TYPE:        n_("Pairing"),
        GT_RAGLAN:              n_("Raglan"),
        GT_SIMPLE_TYPE:         n_("Simple games"),
        GT_SPIDER:              n_("Spider"),
        GT_TERRACE:             n_("Terrace"),
        GT_YUKON:               n_("Yukon"),
        GT_1DECK_TYPE:          n_("One-Deck games"),
        GT_2DECK_TYPE:          n_("Two-Deck games"),
        GT_3DECK_TYPE:          n_("Three-Deck games"),
        GT_4DECK_TYPE:          n_("Four-Deck games"),
    }

##     SELECT_GAME_BY_TYPE = []
##     for gt, name in TYPE_NAMES.items():
##         if not name.endswith('games'):
##             name = name+n_(' type')
##         SELECT_GAME_BY_TYPE.append(
##             (name, lambda gi, gt=gt: gi.si.game_type == gt))
##     SELECT_GAME_BY_TYPE = tuple(SELECT_GAME_BY_TYPE)

    SELECT_GAME_BY_TYPE = (
        (n_("Baker's Dozen type"),lambda gi, gt=GT_BAKERS_DOZEN: gi.si.game_type == gt),
        (n_("Beleaguered Castle type"),lambda gi, gt=GT_BELEAGUERED_CASTLE: gi.si.game_type == gt),
        (n_("Canfield type"), lambda gi, gt=GT_CANFIELD: gi.si.game_type == gt),
        (n_("Fan type"),      lambda gi, gt=GT_FAN_TYPE: gi.si.game_type == gt),
        (n_("Forty Thieves type"),lambda gi, gt=GT_FORTY_THIEVES: gi.si.game_type == gt),
        (n_("FreeCell type"), lambda gi, gt=GT_FREECELL: gi.si.game_type == gt),
        (n_("Golf type"),     lambda gi, gt=GT_GOLF: gi.si.game_type == gt),
        (n_("Gypsy type"),    lambda gi, gt=GT_GYPSY: gi.si.game_type == gt),
        (n_("Klondike type"), lambda gi, gt=GT_KLONDIKE: gi.si.game_type == gt),
        (n_("Montana type"),  lambda gi, gt=GT_MONTANA: gi.si.game_type == gt),
        (n_("Napoleon type"), lambda gi, gt=GT_NAPOLEON: gi.si.game_type == gt),
        (n_("Numerica type"), lambda gi, gt=GT_NUMERICA: gi.si.game_type == gt),
        (n_("Pairing type"),  lambda gi, gt=GT_PAIRING_TYPE: gi.si.game_type == gt),
        (n_("Raglan type"),   lambda gi, gt=GT_RAGLAN: gi.si.game_type == gt),
        (n_("Simple games"),  lambda gi, gt=GT_SIMPLE_TYPE: gi.si.game_type == gt),
        (n_("Spider type"),   lambda gi, gt=GT_SPIDER: gi.si.game_type == gt),
        (n_("Terrace type"),  lambda gi, gt=GT_TERRACE: gi.si.game_type == gt),
        (n_("Yukon type"),    lambda gi, gt=GT_YUKON: gi.si.game_type == gt),
        (n_("One-Deck games"),lambda gi, gt=GT_1DECK_TYPE: gi.si.game_type == gt),
        (n_("Two-Deck games"),lambda gi, gt=GT_2DECK_TYPE: gi.si.game_type == gt),
        (n_("Three-Deck games"),lambda gi, gt=GT_3DECK_TYPE: gi.si.game_type == gt),
        (n_("Four-Deck games"),lambda gi, gt=GT_4DECK_TYPE: gi.si.game_type == gt),
    )

    SELECT_ORIGINAL_GAME_BY_TYPE = (
        (n_("French type"),         lambda gi, gf=GT_ORIGINAL, gt=(GT_HANAFUDA, GT_HEXADECK, GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA, GT_DASHAVATARA_GANJIFA, GT_TAROCK,): gi.si.game_flags & gf and gi.si.game_type not in gt),
        (n_("Ganjifa type"),        lambda gi, gf=GT_ORIGINAL, gt=(GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA, GT_DASHAVATARA_GANJIFA,): gi.si.game_flags & gf and gi.si.game_type in gt),
        (n_("Hanafuda type"),       lambda gi, gf=GT_ORIGINAL, gt=GT_HANAFUDA: gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Hex A Deck type"),     lambda gi, gf=GT_ORIGINAL, gt=GT_HEXADECK: gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Tarock type"),         lambda gi, gf=GT_ORIGINAL, gt=GT_TAROCK: gi.si.game_flags & gf and gi.si.game_type == gt),
    )

    SELECT_CONTRIB_GAME_BY_TYPE = (
        (n_("French type"),         lambda gi, gf=GT_CONTRIB, gt=(GT_HANAFUDA, GT_HEXADECK, GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA, GT_DASHAVATARA_GANJIFA, GT_TAROCK,): gi.si.game_flags & gf and gi.si.game_type not in gt),
        (n_("Ganjifa type"),        lambda gi, gf=GT_CONTRIB, gt=(GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA, GT_DASHAVATARA_GANJIFA,): gi.si.game_flags & gf and gi.si.game_type in gt),
        (n_("Hanafuda type"),       lambda gi, gf=GT_CONTRIB, gt=GT_HANAFUDA: gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Hex A Deck type"),     lambda gi, gf=GT_CONTRIB, gt=GT_HEXADECK: gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Tarock type"),         lambda gi, gf=GT_CONTRIB, gt=GT_TAROCK: gi.si.game_flags & gf and gi.si.game_type == gt),
    )

    SELECT_ORIENTAL_GAME_BY_TYPE = (
        (n_("Dashavatara Ganjifa type"), lambda gi, gt=GT_DASHAVATARA_GANJIFA: gi.si.game_type == gt),
        (n_("Ganjifa type"),        lambda gi, gt=(GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA, GT_DASHAVATARA_GANJIFA,): gi.si.game_type in gt),
        (n_("Hanafuda type"),       lambda gi, gt=GT_HANAFUDA: gi.si.game_type == gt),
        (n_("Mughal Ganjifa type"), lambda gi, gt=GT_MUGHAL_GANJIFA: gi.si.game_type == gt),
        (n_("Navagraha Ganjifa type"), lambda gi, gt=GT_NAVAGRAHA_GANJIFA: gi.si.game_type == gt),
    )

    SELECT_SPECIAL_GAME_BY_TYPE = (
        (n_("Shisen-Sho"),      lambda gi, gt=GT_SHISEN_SHO: gi.si.game_type == gt),
        (n_("Hex A Deck type"), lambda gi, gt=GT_HEXADECK: gi.si.game_type == gt),
        (n_("Matrix type"),     lambda gi, gt=GT_MATRIX: gi.si.game_type == gt),
        (n_("Memory type"),     lambda gi, gt=GT_MEMORY: gi.si.game_type == gt),
        (n_("Poker type"),      lambda gi, gt=GT_POKER_TYPE: gi.si.game_type == gt),
        (n_("Puzzle type"),     lambda gi, gt=GT_PUZZLE_TYPE: gi.si.game_type == gt),
        (n_("Tarock type"),     lambda gi, gt=GT_TAROCK: gi.si.game_type == gt),
    )



    # These obsolete gameids have been used in previous versions of
    # PySol and are no longer supported because of internal changes
    # (mainly rule changes). The game has been assigned a new id.
    PROTECTED_GAMES = {
         22:  106,              # Double Canfield
         32:  901,              # La Belle Lucie (Midnight Oil)
         52:  903,              # Aces Up
         72:  115,              # Little Forty
         75:  126,              # Red and Black
         82:  901,              # La Belle Lucie (Midnight Oil)
##        155: 5034,              # Mahjongg - Flying Dragon
##        156: 5035,              # Mahjongg - Fortress Towers
        262:  105,              # Canfield
        902:   88,              # Trefoil
        904:   68,              # Lexington Harp
        297:  631,              # Alternation/Alternations
    }

    GAMES_BY_COMPATIBILITY = (
        # Atari ST Patience game v2.13 (we have 10 out of 10 games)
        ("Atari ST Patience", (1, 3, 4, 7, 12, 14, 15, 16, 17, 39,)),

        ## Gnome AisleRiot 1.0.51 (we have 28 out of 32 games)
        ##   still missing: Camelot, Clock, Thieves, Thirteen
        ##("Gnome AisleRiot 1.0.51", (
        ##    2, 8, 11, 19, 27, 29, 33, 34, 35, 40,
        ##    41, 42, 43, 58, 59, 92, 93, 94, 95, 96,
        ##    100, 105, 111, 112, 113, 130, 200, 201,
        ##)),
        ## Gnome AisleRiot 1.4.0.1 (we have XX out of XX games)
        ##("Gnome AisleRiot", (
        ##    1, 2, 8, 11, 19, 27, 29, 33, 34, 35, 40,
        ##    41, 42, 43, 58, 59, 92, 93, 94, 95, 96,
        ##    100, 105, 111, 112, 113, 130, 200, 201,
        ##)),
        # Gnome AisleRiot 2.2.0 (we have 61 out of 70 games)
        #   still missing:
        #         Gay gordons, Helsinki,
        #         Isabel, Labyrinth, Quatorze, Thieves,
        #         Treize, Valentine, Yeld.
        ("Gnome AisleRiot", (
            1, 2, 8, 9, 11, 12, 19, 24, 27, 29, 31, 33, 34, 35, 36, 40,
            41, 42, 43, 45, 48, 58, 59, 67, 89, 91, 92, 93, 94, 95, 96,
            100, 105, 111, 112, 113, 130, 139, 144, 146, 147, 148, 200,
            201, 206, 224, 225, 229, 230, 233, 257, 258, 280, 281, 282,
            283, 284, 551, 552, 553, 737,
        )),

        ## KDE Patience 0.7.3 from KDE 1.1.2 (we have 6 out of 9 games)
        ##("KDE Patience 0.7.3", (2, 7, 8, 18, 256, 903,)),
        ## KDE Patience 2.0 from KDE 2.1.2 (we have 11 out of 13 games)
        ##("KDE Patience", (1, 2, 7, 8, 18, 19, 23, 50, 256, 261, 903,)),
        ## KDE Patience 2.0 from KDE 2.2beta1 (we have 12 out of 14 games)
        ##("KDE Patience", (1, 2, 7, 8, 18, 19, 23, 36, 50, 256, 261, 903,)),
        # KDE Patience 2.0 from KDE 3.1.1 (we have 15 out of 15 games)
        ("KDE Patience", (1, 2, 7, 8, 18, 19, 23, 36, 50,
                          256, 261, 277, 278, 279, 903,)),

        # xpat2 1.06 (we have 14 out of 16 games)
        #   still missing: Michael's Fantasy, modCanfield
        ("xpat2", (
            1, 2, 8, 9, 11, 31, 54, 63, 89, 105, 901, 256, 345, 903,
        )),
    )

    GAMES_BY_INVENTORS = (
        ("Paul Alfille", (8,)),
        ("C.L. Baker", (45,)),
        ("David Bernazzani", (314,)),
        ("Gordon Bower", (763,)),
        ("Art Cabral", (9,)),
        ("Robert Harbin", (381,)),
        ("Robert Hogue", (22216,)),
        ("Charles Jewell", (220, 309,)),
        ("Michael Keller", (592,)),
        ("Fred Lunde", (459,)),
        ("Albert Morehead and Geoffrey Mott-Smith", (25, 42, 48, 173, 282,
                                                     303, 362, 547, 738)),
        ("David Parlett", (64, 98, 294, 338, 654, 674,)),
        ("Randy Rasa", (187, 190, 191, 192,)),
        ("Captain Jeffrey T. Spaulding", (400,)),
        ("Adam Selene", (366,)),
        ("John Stoneham", (201,)),
        ("Bryan Stout", (655,)),
        ("Bill Taylor", (349,)),
        ("Thomas Warfield", (189, 264, 300, 320, 336, 337, 359,
                             415, 427, 458, 495, 496, 497, 508,)),
        )

    GAMES_BY_PYSOL_VERSION = (
        ("1.00", (1, 2, 3, 4)),
        ("1.01", (5, 6)),
        ("1.02", (7, 8, 9)),
        ("1.03", (10, 11, 12, 13)),
        ("1.10", (14,)),
        ("1.11", (15, 16, 17)),
        ("2.00", (256, 257)),
        ("2.01", (258, 259, 260, 261)),
        ("2.02", (105,)),
        ("2.90", (18, 19, 20, 21, 106, 23, 24, 25, 26, 27,
                  28, 29, 30, 31, 901, 33, 34, 35, 36)),
        ("2.99", (37,)),
        ("3.00", (38, 39,
                  40, 41, 42, 43,     45, 46, 47, 48, 49,
                  50, 51,903, 53, 54, 55, 56, 57, 58, 59,
                  60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                  70, 71,115, 73, 74,126, 76, 77, 78, 79,
                  80, 81,     83, 84, 85, 86, 87, 88, 89,
                  90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                  100, 101, 102, 103, 104, 107, 108,)),
        ("3.10", (109, 110, 111, 112, 113, 114, 116, 117, 118, 119,
                  120, 121, 122, 123, 124, 125, 127)),
        ("3.20", (128, 129, 130, 131, 132, 133, 134, 135, 136, 137,
                  138, 139, 140, 141, 142,
                  12345, 12346, 12347, 12348, 12349, 12350, 12351, 12352)),
        ("3.21", (143, 144)),
        ("3.30", (145, 146, 147, 148, 149, 150, 151)),
        ("3.40", (152, 153, 154)),
        ("4.00", (          157, 158, 159, 160, 161, 162, 163, 164)),
        ("4.20", (165, 166, 167, 168, 169, 170, 171, 172, 173, 174,
                  175, 176, 177, 178)),
        ("4.30", (179, 180, 181, 182, 183, 184)),
        ("4.41", (185, 186, 187, 188, 189, 190, 191, 192, 193, 194,
                  195, 196, 197, 198, 199)),
        ("4.60", (200, 201, 202, 203, 204, 205,
                  206, 207, 208, 209,
                  210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
                  220, 221, 222, 223, 224, 225, 226, 227, 228, 229,
                  230, 231, 232, 233, 234, 235, 236)),
        ("4.70", (237,)),
        ('fc-0.5.0', ( # moved from Ultrasol
                      #121, 122, 187, 188, 189, 190, 191, 192, 194, 197, 198,
                      5301, 5302, 9011, 11001, 11002, 11003, 11004, 11005,
                      11006, 12353, 12354, 12355, 12356, 12357, 12358, 12359,
                      12360, 12361, 12362, 12363, 12364, 12365, 12366, 12367,
                      12368, 12369, 12370, 12371, 12372, 12373, 12374, 12375,
                      12376, 12377, 12378, 12379, 12380, 12381, 12382, 12383,
                      12384, 12385, 13001, 13002, 13003, 13004, 13005, 13006,
                      13007, 13008, 13009, 13010, 13011, 13012, 13013, 13014,
                      13163, 13164, 13165, 13166, 13167, 14401, 14402, 14403,
                      14404, 14405, 14406, 14407, 14408, 14409, 14410, 14411,
                      14412, 14413, 15406, 15407, 15408, 15409, 15410, 15411,
                      15412, 15413, 15414, 15415, 15416, 15417, 15418, 15419,
                      15420, 15421, 15422, 16000, 16001, 16002, 16003, 16004,
                      16666, 16667, 16668, 16669, 16670, 16671, 16672, 16673,
                      16674, 16675, 16676, 16677, 16678, 16679, 16680, 22216,
                      22223, 22224, 22225, 22226, 22227, 22228, 22229, 22230,
                      22231, 22232,)),
        ('fc-0.8.0', tuple(range(263, 323))), # exclude 297
        ('fc-0.9.0', tuple(range(323, 421))),
        ('fc-0.9.1', tuple(range(421, 441))),
        ('fc-0.9.2', tuple(range(441, 466))),
        ('fc-0.9.3', tuple(range(466, 661))),
        ('fc-0.9.4', tuple(range(661, 671))),
        ('fc-1.0',   tuple(range(671, 711))),
        ('fc-1.1',   tuple(range(711, 759))),
        ('fc-2.0',   tuple(range(11011, 11014)) + tuple(range(759, 767)) ),
    )

    # deprecated - the correct way is to or a GI.GT_XXX flag
    # in the registerGame() call
    _CHILDREN_GAMES = [16, 33, 55, 90, 91, 96, 97, 176, 903,]

    _OPEN_GAMES = []

    _POPULAR_GAMES = [
        1,     # Gypsy
        2,     # Klondike
        7,     # Picture Galary
        8,     # FreeCell
        9,     # Seahaven Towers
        11,    # Spider
        12,    # Braid
        13,    # Forty Thieves
        14,    # Grounds for a Divorce
        19,    # Yukon
        31,    # Baker's Dozen
        36,    # Golf
        38,    # Pyramid
        105,   # Canfield
        158,   # Imperial Trumps
        279,   # Kings
        903,   # Ace Up
        5034,  # Mahjongg Flying Dragon
        5401,  # Mahjongg Taipei
        12345, # Oonsoo
    ]


# ************************************************************************
# * core games database
# ************************************************************************

class GameInfoException(Exception):
    pass


class GameInfo(Struct):
    def __init__(self, id, gameclass, name,
                 game_type, decks, redeals,
                 skill_level=None,
                 # keyword arguments:
                 si={}, category=0,
                 short_name=None, altnames=(),
                 suits=range(4), ranks=range(13), trumps=(),
                 rules_filename=None,
                 ):
        #
        def to_unicode(s):
            if isinstance(s, unicode):
                return s
            try:
                s = unicode(s, 'utf-8')
            except UnicodeDecodeError, err:
                print_err(err)
                s = unicode(s, 'utf-8', 'ignore')
            return s
        ncards = decks * (len(suits) * len(ranks) + len(trumps))
        game_flags = game_type & ~1023
        game_type = game_type & 1023
        name = to_unicode(name)
        en_name = name                  # for app.getGameRulesFilename
        if settings.TRANSLATE_GAME_NAMES:
            name = _(name)
        if not short_name:
            short_name = name
        else:
            short_name = to_unicode(short_name)
            if settings.TRANSLATE_GAME_NAMES:
                short_name = _(short_name)
        if isinstance(altnames, basestring):
            altnames = (altnames,)
        altnames = [to_unicode(n) for n in altnames]
        if settings.TRANSLATE_GAME_NAMES:
            altnames = [_(n) for n in altnames]
        #
        if not (1 <= category <= 9):
            if game_type == GI.GT_HANAFUDA:
                category = GI.GC_HANAFUDA
            elif game_type == GI.GT_TAROCK:
                category = GI.GC_TAROCK
            elif game_type == GI.GT_MAHJONGG:
                category = GI.GC_MAHJONGG
            elif game_type == GI.GT_HEXADECK:
                category = GI.GC_HEXADECK
            elif game_type == GI.GT_MUGHAL_GANJIFA:
                category = GI.GC_MUGHAL_GANJIFA
            elif game_type == GI.GT_NAVAGRAHA_GANJIFA:
                category = GI.GC_NAVAGRAHA_GANJIFA
            elif game_type == GI.GT_DASHAVATARA_GANJIFA:
                category = GI.GC_DASHAVATARA_GANJIFA
            else:
                category = GI.GC_FRENCH
        #
        if not (1 <= id <= 999999):
            raise GameInfoException(name+": invalid game ID "+str(id))
        if category == GI.GC_MAHJONGG:
            if decks%4:
                raise GameInfoException(name+": invalid number of decks "+str(id))
        else:
            if not (1 <= decks <= 4):
                raise GameInfoException(name+": invalid number of decks "+str(id))
        if not name:
            raise GameInfoException(name+": invalid game name")
        if GI.PROTECTED_GAMES.get(id):
            raise GameInfoException(name+": protected game ID "+str(id))
        #
        for f, l in ((GI.GT_CHILDREN, GI._CHILDREN_GAMES),
                     (GI.GT_OPEN, GI._OPEN_GAMES),
                     (GI.GT_POPULAR, GI._POPULAR_GAMES)):
            if (game_flags & f) and (id not in l):
                l.append(id)
            elif not (game_flags & f) and (id in l):
                game_flags = game_flags | f
        # si is the SelectionInfo struct that will be queried by
        # the "select game" dialogs. It can be freely modified.
        gi_si = Struct(game_type=game_type, game_flags=game_flags,
                       decks=decks, redeals=redeals, ncards=ncards)
        gi_si.update(si)
        #
        Struct.__init__(self, id=id, gameclass=gameclass,
                        name=name, short_name=short_name,
                        altnames=tuple(altnames), en_name=en_name,
                        decks=decks, redeals=redeals, ncards=ncards,
                        category=category, skill_level=skill_level,
                        suits=tuple(suits), ranks=tuple(ranks),
                        trumps=tuple(trumps),
                        si=gi_si, rules_filename=rules_filename)


class GameManager:
    def __init__(self):
        self.__selected_key = -1
        self.__games = {}
        self.__gamenames = {}
        self.__games_by_id = None
        self.__games_by_name = None
        self.__games_by_short_name = None
        self.__games_by_altname = None
        self.__all_games = {}           # includes hidden games
        self.__all_gamenames = {}       # includes hidden games
        self.__games_for_solver = []
        self.check_game = True
        self.current_filename = None
        self.registered_game_types = {}
        self.callback = None            # update progress-bar (see main.py)
        self._num_games = 0             # for callback only

    def setCallback(self, func):
        self.callback = func

    def getSelected(self):
        return self.__selected_key

    def setSelected(self, gameid):
        assert gameid in self.__all_games
        self.__selected_key = gameid

    def get(self, key):
        return self.__all_games.get(key)

    def _check_game(self, gi):
        ##print 'check game:', gi.id, gi.short_name.encode('utf-8')
        if gi.id in self.__all_games:
            raise GameInfoException("duplicate game ID %s: %s and %s" %
                                    (gi.id, str(gi.gameclass),
                                     str(self.__all_games[gi.id].gameclass)))
        if gi.name in self.__all_gamenames:
            gameclass = self.__all_gamenames[gi.name].gameclass
            raise GameInfoException("duplicate game name %s: %s and %s" %
                                    (gi.name, str(gi.gameclass),
                                     str(gameclass)))
        if 1:
            for id, game in self.__all_games.items():
                if gi.gameclass is game.gameclass:
                    raise GameInfoException(
                        "duplicate game class %s: %s and %s" %
                        (gi.id, str(gi.gameclass), str(game.gameclass)))
        for n in gi.altnames:
            if n in self.__all_gamenames:
                raise GameInfoException("duplicate game altname %s: %s" %
                                        (gi.id, n))

    def register(self, gi):
        ##print gi.id, gi.short_name.encode('utf-8')
        if not isinstance(gi, GameInfo):
            raise GameInfoException("wrong GameInfo class")
        if self.check_game and settings.CHECK_GAMES:
            self._check_game(gi)
        ##if 0 and gi.si.game_flags & GI.GT_XORIGINAL:
        ##    return
        ##print gi.id, gi.name
        self.__all_games[gi.id] = gi
        self.__all_gamenames[gi.name] = gi
        for n in gi.altnames:
            self.__all_gamenames[n] = gi
        if not (gi.si.game_flags & GI.GT_HIDDEN):
            self.__games[gi.id] = gi
            self.__gamenames[gi.name] = gi
            for n in gi.altnames:
                self.__gamenames[n] = gi
            # invalidate sorted lists
            self.__games_by_id = None
            self.__games_by_name = None
            # update registry
            k = gi.si.game_type
            self.registered_game_types[k] = self.registered_game_types.get(k, 0) + 1
##             if not gi.si.game_type == GI.GT_MAHJONGG:
##                 for v, k in GI.GAMES_BY_PYSOL_VERSION:
##                     if gi.id in k: break
##                 else:
##                     print gi.id
            if hasattr(gi.gameclass, 'Solver_Class') and \
               gi.gameclass.Solver_Class is not None:
                self.__games_for_solver.append(gi.id)
        if self.current_filename is not None:
            gi.gameclass.MODULE_FILENAME = self.current_filename

        if self.callback and self._num_games % 10 == 0:
            self.callback()
        self._num_games += 1

    #
    # access games database - we do not expose hidden games
    #

    def getAllGames(self):
        ##return self.__all_games
        return self.__games.values()

    def getGamesIdSortedById(self):
        if self.__games_by_id is None:
            l = self.__games.keys()
            l.sort()
            self.__games_by_id = tuple(l)
        return self.__games_by_id

    def getGamesIdSortedByName(self):
        if self.__games_by_name is None:
            l1, l2, l3  = [], [], []
            for id, gi in self.__games.items():
                name = gi.name #.lower()
                l1.append((name, id))
                if gi.name != gi.short_name:
                    name = gi.short_name #.lower()
                l2.append((name, id))
                for n in gi.altnames:
                    name = n #.lower()
                    l3.append((name, id, n))
            l1.sort()
            l2.sort()
            l3.sort()
            self.__games_by_name = tuple([i[1] for i in l1])
            self.__games_by_short_name = tuple([i[1] for i in l2])
            self.__games_by_altname = tuple([i[1:] for i in l3])
        return self.__games_by_name

    def getGamesIdSortedByShortName(self):
        if self.__games_by_name is None:
            self.getGamesIdSortedByName()
        return self.__games_by_short_name

    # note: this contains tuples as entries
    def getGamesTuplesSortedByAlternateName(self):
        if self.__games_by_name is None:
            self.getGamesIdSortedByName()
        return self.__games_by_altname

    # find game by name
    def getGameByName(self, name):
        gi = self.__all_gamenames.get(name)
        if gi:
            return gi.id
        return None

    def getGamesForSolver(self):
        return self.__games_for_solver


# ************************************************************************
# *
# ************************************************************************

# the global game database (the single instance of class GameManager)
GAME_DB = GameManager()


def registerGame(gameinfo):
    GAME_DB.register(gameinfo)
    return gameinfo


def loadGame(modname, filename, check_game=False):
    ##print "load game", modname, filename
    GAME_DB.check_game = check_game
    GAME_DB.current_filename = filename
    module = imp.load_source(modname, filename)
    ##execfile(filename, globals(), globals())
    GAME_DB.current_filename = None

