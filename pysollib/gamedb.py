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

from importlib import util

import pysollib.settings
from pysollib.mfxutil import Struct, print_err
from pysollib.mygettext import _, n_
from pysollib.resource import CSI


# ************************************************************************
# * constants
# ************************************************************************


# GameInfo constants
class GI:
    # game category - these *must* match the cardset CSI.TYPE_xxx
    GC_FRENCH = CSI.TYPE_FRENCH
    GC_HANAFUDA = CSI.TYPE_HANAFUDA
    GC_TAROCK = CSI.TYPE_TAROCK
    GC_MAHJONGG = CSI.TYPE_MAHJONGG
    GC_HEXADECK = CSI.TYPE_HEXADECK
    GC_MUGHAL_GANJIFA = CSI.TYPE_MUGHAL_GANJIFA
    GC_NAVAGRAHA_GANJIFA = CSI.TYPE_NAVAGRAHA_GANJIFA
    GC_DASHAVATARA_GANJIFA = CSI.TYPE_DASHAVATARA_GANJIFA
    GC_TRUMP_ONLY = CSI.TYPE_TRUMP_ONLY
    GC_MATCHING = CSI.TYPE_MATCHING
    GC_PUZZLE = CSI.TYPE_PUZZLE
    GC_ISHIDO = CSI.TYPE_ISHIDO

    NUM_CATEGORIES = CSI.TYPE_ISHIDO

    # game subcategory
    GS_NONE = CSI.SUBTYPE_NONE
    GS_JOKER_DECK = CSI.SUBTYPE_JOKER_DECK
    GS_3X3 = CSI.SUBTYPE_3X3
    GS_4X4 = CSI.SUBTYPE_4X4
    GS_5X5 = CSI.SUBTYPE_5X5
    GS_6X6 = CSI.SUBTYPE_6X6
    GS_7X7 = CSI.SUBTYPE_7X7
    GS_8X8 = CSI.SUBTYPE_8X8
    GS_9X9 = CSI.SUBTYPE_9X9
    GS_10X10 = CSI.SUBTYPE_10X10

    # game type
    GT_1DECK_TYPE = 0
    GT_2DECK_TYPE = 1
    GT_3DECK_TYPE = 2
    GT_4DECK_TYPE = 3
    GT_BAKERS_DOZEN = 4
    GT_BELEAGUERED_CASTLE = 5
    GT_CANFIELD = 6
    GT_CRIBBAGE_TYPE = 37
    GT_DASHAVATARA_GANJIFA = 7
    GT_FAN_TYPE = 8
    GT_FORTY_THIEVES = 9
    GT_FREECELL = 10
    GT_GOLF = 11
    GT_GYPSY = 12
    GT_HANAFUDA = 13
    GT_HANOI = 35
    GT_HEXADECK = 14
    GT_ISHIDO = 39
    GT_KLONDIKE = 15
    GT_LIGHTS_OUT = 38
    GT_MAHJONGG = 16
    GT_MATRIX = 17
    GT_MEMORY = 18
    GT_MONTANA = 19
    GT_MUGHAL_GANJIFA = 20
    GT_NAPOLEON = 21
    GT_NAVAGRAHA_GANJIFA = 22
    GT_NUMERICA = 23
    GT_PAIRING_TYPE = 24
    GT_PEGGED = 36
    GT_PICTURE_GALLERY = 41
    GT_POKER_TYPE = 25
    GT_PUZZLE_TYPE = 26
    GT_RAGLAN = 27
    GT_ROW_TYPE = 28
    GT_SAMEGAME = 42
    GT_SHISEN_SHO = 34
    GT_SIMPLE_TYPE = 29
    GT_SPIDER = 30
    GT_TAROCK = 31
    GT_TERRACE = 32
    GT_YUKON = 33

    GT_CUSTOM = 40

    # extra flags
    GT_BETA = 1 << 12      # beta version of game driver
    GT_CHILDREN = 1 << 13      # *not used*
    GT_CONTRIB = 1 << 14      # contributed games under the GNU GPL
    GT_HIDDEN = 1 << 15      # not visible in menus, but games can be loaded
    GT_OPEN = 1 << 16
    GT_ORIGINAL = 1 << 17
    GT_POPULAR = 1 << 18      # *not used*
    GT_RELAXED = 1 << 19
    GT_SCORE = 1 << 20      # game has some type of scoring
    GT_SEPARATE_DECKS = 1 << 21
    GT_XORIGINAL = 1 << 22      # original games by other people, not playable
    GT_STRIPPED = 1 << 23
    # skill level
    SL_LUCK = 1
    SL_MOSTLY_LUCK = 2
    SL_BALANCED = 3
    SL_MOSTLY_SKILL = 4
    SL_SKILL = 5
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
        GT_PICTURE_GALLERY:     n_("Picture Gallery"),
        GT_RAGLAN:              n_("Raglan"),
        GT_SIMPLE_TYPE:         n_("Simple games"),
        GT_SPIDER:              n_("Spider"),
        GT_TERRACE:             n_("Terrace"),
        GT_YUKON:               n_("Yukon"),
        GT_1DECK_TYPE:          n_("One-Deck games"),
        GT_2DECK_TYPE:          n_("Two-Deck games"),
        GT_3DECK_TYPE:          n_("Three-Deck games"),
        GT_4DECK_TYPE:          n_("Four-Deck games"),

        GT_MAHJONGG:            n_("Mahjongg"),
        GT_HANAFUDA:            n_("Hanafuda"),
        GT_MUGHAL_GANJIFA:      n_("Mughal Ganjifa"),
        GT_DASHAVATARA_GANJIFA: n_("Dashavatara Ganjifa"),

        GT_CRIBBAGE_TYPE:       n_("Cribbage"),
        GT_HEXADECK:            n_("Hex A Deck"),
        GT_ISHIDO:              n_("Ishido"),
        GT_LIGHTS_OUT:          n_("Lights Out"),
        GT_MATRIX:              n_("Matrix"),
        GT_MEMORY:              n_("Memory"),
        GT_PEGGED:              n_("Pegged"),
        GT_POKER_TYPE:          n_("Poker"),
        GT_PUZZLE_TYPE:         n_("Puzzle"),
        GT_SAMEGAME:            n_("Samegame"),
        GT_SHISEN_SHO:          n_("Shisen-Sho"),
        GT_TAROCK:              n_("Tarock"),
        GT_HANOI:               n_("Tower of Hanoi"),

        GT_CUSTOM:              n_("Custom"),
    }

    SKILL_LEVELS = {
        SL_LUCK: _('Luck only'),
        SL_MOSTLY_LUCK: _('Mostly luck'),
        SL_BALANCED: _('Balanced'),
        SL_MOSTLY_SKILL: _('Mostly skill'),
        SL_SKILL: _('Skill only'),
    }

    #      SELECT_GAME_BY_TYPE = []
    #      for gt, name in TYPE_NAMES.items():
    #          if not name.endswith('games'):
    #              name = name+n_(' type')
    #          SELECT_GAME_BY_TYPE.append(
    #              (name, lambda gi, gt=gt: gi.si.game_type == gt))
    #      SELECT_GAME_BY_TYPE = tuple(SELECT_GAME_BY_TYPE)

    def _gen_select(title, game_type):
        def _callback(gi, gt=game_type):
            return gi.si.game_type == gt
        return (title, _callback)

    SELECT_GAME_BY_TYPE = (
        _gen_select(title=n_("Baker's Dozen type"), game_type=GT_BAKERS_DOZEN),
        _gen_select(
            title=n_("Beleaguered Castle type"),
            game_type=GT_BELEAGUERED_CASTLE),
        _gen_select(title=n_("Canfield type"), game_type=GT_CANFIELD),
        _gen_select(title=n_("Fan type"), game_type=GT_FAN_TYPE),
        _gen_select(
            title=n_("Forty Thieves type"), game_type=GT_FORTY_THIEVES),
        _gen_select(title=n_("FreeCell type"), game_type=GT_FREECELL),
        _gen_select(title=n_("Golf type"), game_type=GT_GOLF),
        _gen_select(title=n_("Gypsy type"), game_type=GT_GYPSY),
        _gen_select(title=n_("Klondike type"), game_type=GT_KLONDIKE),
        _gen_select(title=n_("Montana type"), game_type=GT_MONTANA),
        _gen_select(title=n_("Napoleon type"), game_type=GT_NAPOLEON),
        _gen_select(title=n_("Numerica type"), game_type=GT_NUMERICA),
        _gen_select(title=n_("Pairing type"), game_type=GT_PAIRING_TYPE),
        _gen_select(title=n_("Picture Gallery type"),
                    game_type=GT_PICTURE_GALLERY),
        _gen_select(title=n_("Raglan type"), game_type=GT_RAGLAN),
        _gen_select(title=n_("Simple games"), game_type=GT_SIMPLE_TYPE),
        _gen_select(title=n_("Spider type"), game_type=GT_SPIDER),
        _gen_select(title=n_("Terrace type"), game_type=GT_TERRACE),
        _gen_select(title=n_("Yukon type"), game_type=GT_YUKON),
        _gen_select(title=n_("One-Deck games"), game_type=GT_1DECK_TYPE),
        _gen_select(title=n_("Two-Deck games"), game_type=GT_2DECK_TYPE),
        _gen_select(title=n_("Three-Deck games"), game_type=GT_3DECK_TYPE),
        _gen_select(title=n_("Four-Deck games"), game_type=GT_4DECK_TYPE),
    )

    SELECT_ORIGINAL_GAME_BY_TYPE = (
        (n_("French type"), lambda gi, gf=GT_ORIGINAL,
            gt=(
                GT_HANAFUDA,
                GT_HEXADECK, GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA,
                GT_DASHAVATARA_GANJIFA, GT_TAROCK,): gi.si.game_flags & gf and
            gi.si.game_type not in gt),
        (n_("Ganjifa type"), lambda gi, gf=GT_ORIGINAL,
            gt=(GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA,
                GT_DASHAVATARA_GANJIFA,): gi.si.game_flags & gf and
            gi.si.game_type in gt),
        (n_("Hanafuda type"), lambda gi, gf=GT_ORIGINAL, gt=GT_HANAFUDA:
            gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Hex A Deck type"), lambda gi, gf=GT_ORIGINAL, gt=GT_HEXADECK:
            gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Tarock type"), lambda gi, gf=GT_ORIGINAL, gt=GT_TAROCK:
            gi.si.game_flags & gf and gi.si.game_type == gt),
    )

    SELECT_CONTRIB_GAME_BY_TYPE = (
        (n_("French type"), lambda gi, gf=GT_CONTRIB,
            gt=(GT_HANAFUDA, GT_HEXADECK, GT_MUGHAL_GANJIFA,
                GT_NAVAGRAHA_GANJIFA, GT_DASHAVATARA_GANJIFA, GT_TAROCK,):
            gi.si.game_flags & gf and gi.si.game_type not in gt),
        (n_("Ganjifa type"), lambda gi, gf=GT_CONTRIB,
            gt=(GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA,
                GT_DASHAVATARA_GANJIFA,):
            gi.si.game_flags & gf and gi.si.game_type in gt),
        (n_("Hanafuda type"), lambda gi, gf=GT_CONTRIB, gt=GT_HANAFUDA:
            gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Hex A Deck type"), lambda gi, gf=GT_CONTRIB, gt=GT_HEXADECK:
            gi.si.game_flags & gf and gi.si.game_type == gt),
        (n_("Tarock type"), lambda gi, gf=GT_CONTRIB, gt=GT_TAROCK:
            gi.si.game_flags & gf and gi.si.game_type == gt),
    )

    SELECT_ORIENTAL_GAME_BY_TYPE = (
        (n_("Dashavatara Ganjifa type"), lambda gi, gt=GT_DASHAVATARA_GANJIFA:
            gi.si.game_type == gt),
        (n_("Ganjifa type"), lambda gi,
            gt=(GT_MUGHAL_GANJIFA, GT_NAVAGRAHA_GANJIFA,
                GT_DASHAVATARA_GANJIFA,): gi.si.game_type in gt),
        (n_("Hanafuda type"),
            lambda gi, gt=GT_HANAFUDA: gi.si.game_type == gt),
        (n_("Mughal Ganjifa type"),
            lambda gi, gt=GT_MUGHAL_GANJIFA: gi.si.game_type == gt),
        (n_("Navagraha Ganjifa type"),
            lambda gi, gt=GT_NAVAGRAHA_GANJIFA: gi.si.game_type == gt),
    )

    SELECT_SPECIAL_GAME_BY_TYPE = (
        (n_("Cribbage type"),
            lambda gi, gt=GT_CRIBBAGE_TYPE: gi.si.game_type == gt),
        (n_("Hex A Deck type"),
            lambda gi, gt=GT_HEXADECK: gi.si.game_type == gt),
        (n_("Ishido type"), lambda gi, gt=GT_ISHIDO: gi.si.game_type == gt),
        (n_("Lights Out type"),
            lambda gi, gt=GT_LIGHTS_OUT: gi.si.game_type == gt),
        (n_("Matrix type"), lambda gi, gt=GT_MATRIX: gi.si.game_type == gt),
        (n_("Memory type"), lambda gi, gt=GT_MEMORY: gi.si.game_type == gt),
        (n_("Pegged type"), lambda gi, gt=GT_PEGGED: gi.si.game_type == gt),
        (n_("Poker type"), lambda gi, gt=GT_POKER_TYPE: gi.si.game_type == gt),
        (n_("Puzzle type"),
            lambda gi, gt=GT_PUZZLE_TYPE: gi.si.game_type == gt),
        (n_("Samegame type"),
            lambda gi, gt=GT_SAMEGAME: gi.si.game_type == gt),
        (n_("Shisen-Sho type"),
            lambda gi, gt=GT_SHISEN_SHO: gi.si.game_type == gt),
        (n_("Tarock type"), lambda gi, gt=GT_TAROCK: gi.si.game_type == gt),
        (n_("Tower of Hanoi type"),
            lambda gi, gt=GT_HANOI: gi.si.game_type == gt),
    )

    # These obsolete gameids have been used in previous versions of
    # PySol and are no longer supported because of internal changes
    # (mainly rule changes or removed duplicate games). The game
    # has been assigned a new id.
    PROTECTED_GAMES = {
         22:  106,              # Double Canfield
         32:  901,              # La Belle Lucie (Midnight Oil)
         52:  903,              # Aces Up
         72:  115,              # Little Forty
         75:  126,              # Red and Black
         82:  901,              # La Belle Lucie (Midnight Oil)
         155: 5034,             # Mahjongg - Flying Dragon
         156: 5035,             # Mahjongg - Fortress Towers
         262: 105,              # Canfield
         283: 25,               # Gargantua/Jumbo
         902: 88,               # Trefoil
         904: 68,               # Lexington Harp
         237: 22231,            # Three Peaks
         297: 631,              # Alternation/Alternations
         526: 447,              # Australian/Outback Patience
         640: 566,              # Hypotenuse/Brazilian Patience

         # Lost Mahjongg Layouts
         5025: 5600, 5032: 5601, 5043: 5602, 5046: 5603, 5051: 5604,
         5061: 5605, 5062: 5606, 5066: 5607, 5085: 5608, 5093: 5609,
         5101: 5610, 5213: 5611, 5214: 5612, 5238: 5613, 5244: 5614,
         5501: 5615, 5502: 5616, 5503: 5617, 5504: 5618, 5505: 5619,
         5802: 5620, 5804: 5621, 5902: 5622, 5903: 5623
    }

    # For games by compatibility, note that missing games may actually
    # be present under alternate names.  This needs to be verified.
    # If such a game is found, the alternate name should be added if
    # possible, and the game recorded in the compatibility section
    # appropriately.
    #
    # Note that there are instances where another program's
    # implementation of a game uses different rules than PySol, or
    # has a different game with the same name.  These are marked
    # as missing.
    #
    # If a game is listed as missing from multiple collections below,
    # adding it should be a priority.

    GAMES_BY_COMPATIBILITY = (
        # Atari ST Patience game v2.13 (we have 10 out of 10 games)
        ("Atari ST Patience", (1, 3, 4, 7, 12, 14, 15, 16, 17, 39,)),

        #  Gnome AisleRiot 1.0.51 (we have 28 out of 32 games)
        #    still missing: Camelot, Clock, Thieves, Thirteen
        # ("Gnome AisleRiot 1.0.51", (
        #     2, 8, 11, 19, 27, 29, 33, 34, 35, 40,
        #     41, 42, 43, 58, 59, 92, 93, 94, 95, 96,
        #     100, 105, 111, 112, 113, 130, 200, 201,
        # )),
        #  Gnome AisleRiot 1.4.0.1 (we have XX out of XX games)
        # ("Gnome AisleRiot", (
        #     1, 2, 8, 11, 19, 27, 29, 33, 34, 35, 40,
        #     41, 42, 43, 58, 59, 92, 93, 94, 95, 96,
        #     100, 105, 111, 112, 113, 130, 200, 201,
        # )),
        # Gnome AisleRiot 2.2.0 (we have 65 out of 70 games)
        # Gnome AisleRiot 3.22.7
        #   still missing:
        #       Hamilton, Labyrinth, Treize, Wall
        ("Gnome AisleRiot", (
            1, 2, 8, 9, 11, 12, 13, 19, 24, 27, 29, 31, 33, 34, 35, 36,
            38, 40, 41, 42, 43, 45, 48, 58, 65, 67, 89, 91, 92, 93, 94,
            95, 96, 97, 100, 104, 105, 111, 112, 113, 130, 135, 139, 144,
            146, 147, 148, 200, 201, 206, 224, 225, 229, 230, 233, 257,
            258, 277, 280, 281, 282, 283, 284, 334, 384, 479, 495, 551,
            552, 553, 572, 593, 674, 700, 715, 716, 737, 772, 810, 819,
            824, 829, 859, 874, 906, 934, 22231,
        )),

        # Hoyle Card Games
        # still missing:
        #       Bowling (Schwader version), Euchre, Slide, Arcade games
        ("Hoyle Card Games", (
            2, 8, 9, 11, 13, 19, 24, 29, 31, 34, 36, 38, 42, 53, 57, 64,
            105, 112, 126, 133, 134, 135, 139, 147, 173, 222, 234, 235,
            256, 258, 296, 330, 398, 484, 619, 657, 737, 784, 800, 805,
            901, 903,
        )),

        #  KDE Patience 0.7.3 from KDE 1.1.2 (we have 6 out of 9 games)
        # ("KDE Patience 0.7.3", (2, 7, 8, 18, 256, 903,)),
        #  KDE Patience 2.0 from KDE 2.1.2 (we have 11 out of 13 games)
        # ("KDE Patience", (1, 2, 7, 8, 18, 19, 23, 50, 256, 261, 903,)),
        #  KDE Patience 2.0 from KDE 2.2beta1 (we have 12 out of 14 games)
        # ("KDE Patience", (1, 2, 7, 8, 18, 19, 23, 36, 50, 256, 261, 903,)),
        # KDE Patience 2.0 from KDE 3.1.1 (we have 15 out of 15 games)
        # ("KDE Patience", (1, 2, 7, 8, 18, 19, 23, 36, 50,
        #                256, 261, 277, 278, 279, 903,)),
        # Now KPatience - Calculation and Napoleon's Tomb have been removed.
        ("KPatience", (1, 2, 7, 8, 11, 18, 19, 23, 36, 50, 261, 278, 903,)),

        # Microsoft Solitaire (we have all 5 games)
        ("Microsoft Solitaire Collection", (2, 8, 11, 38, 22231,)),

        # Solitaire Royale
        # still missing: Pairs
        ("Solitaire Royale", (
            2, 36, 38, 105, 128, 176, 256, 328, 484, 835
        )),

        # Solitude for Windows
        # still missing:
        #       Bowling (Sackson version), Icicles
        ("Solitude for Windows", (
            2, 8, 11, 13, 19, 24, 25, 29, 30, 31, 33, 34, 36, 38, 42,
            43, 45, 48, 50, 53, 56, 57, 58, 62, 64, 67, 69, 71, 86, 87,
            88, 89, 95, 96, 97, 98, 100, 104, 105, 107, 109, 112, 125,
            128, 133, 134, 135, 139, 146, 147, 171, 172, 173, 221, 222,
            224, 228, 233, 234, 235, 256, 257, 258, 282, 314, 327, 330,
            355, 356, 398, 406, 414, 418, 434, 437, 484, 593, 715, 716,
            737, 751, 805, 830, 845, 847, 888, 901, 903, 970
        )),

        # XM Solitaire
        # NOTE: This collection has a lot of games with the same name as
        # established games but completely different rules, or more obscure
        # variations with more generic names.  As such rules/names may
        # conflict with other attempts to add games in the future, games
        # from XM Solitaire should be researched before being added to PySol.
        #
        # still missing:
        #       Agnes Three, Antares, Avenue, Baker's Fan, Baker's Spider,
        #       Bedeviled, Binding, Black Spider, California, Color Cell,
        #       Cornelius, Desert Fox, Double Antares, Double Antarctica,
        #       Double Arctica, Double Baker's Spider, Double Cascade,
        #       Double Majesty, Double Spidercells, Doublet Cell 5, Doubt,
        #       Dream Fan, Dumfries Cell, Falcon Wing, Fan Nine, Four By Ten,
        #       FreeCell AK, Gaps Alter, Gaps Diff, George V,
        #       Grandmother's Clock, In a Frame, Inverted FreeCell, Kings,
        #       Klondike FreeCell, La Cabane, La Double Entente,
        #       Little Gazette, Magic FreeCell, Mini Gaps, Montreal,
        #       Napoleon at Iena, Napoleon at Waterloo, Napoleon's Guards,
        #       Oasis, Opera, Ordered Suits, Osmotic FreeCell, Pair FreeCell,
        #       Pairs 2, Reserved Thirteens, Sept Piles 0, Short Solitaire,
        #       Simple Alternations, Smart Osmosis, Step By Step,
        #       Stripped FreeCell, Tarantula, Triple Dispute, Trusty Twenty,
        #       Two Ways 3, Up Or Down, Versailles, Vertical FreeCell,
        #       Wasp Baby, Yukon FreeCell
        ("XM Solitaire", (
            2, 8, 9, 13, 15, 18, 19, 20, 29, 30, 31, 34, 36, 38, 41, 42,
            45, 46, 50, 53, 54, 56, 57, 64, 77, 78, 86, 96, 97, 98, 105,
            110, 112, 124, 145, 173, 220, 222, 223, 224, 228, 231, 233,
            234, 235, 236, 257, 258, 264, 265, 267, 270, 271, 290, 291,
            292, 293, 303, 309, 314, 318, 320, 322, 324, 325, 336, 338,
            341, 359, 363, 364, 372, 376, 383, 384, 385, 386, 390, 391,
            393, 398, 405, 415, 416, 425, 451, 453, 461, 464, 466, 467,
            476, 480, 484, 511, 512, 513, 516, 561, 610, 613, 625, 629,
            631, 638, 641, 647, 650, 655, 678, 684, 702, 734, 751, 784,
            825, 829, 834, 837, 844, 862, 867, 880, 889, 901, 911, 933,
            941, 947, 953, 966
        )),

        # xpat2 1.06 (we have 14 out of 16 games)
        #   still missing: Michael's Fantasy, modCanfield
        ("xpat2", (
            1, 2, 8, 9, 11, 31, 54, 63, 89, 105, 901, 256, 345, 903,
        )),
    )

    GAMES_BY_INVENTORS = (
        ("Paul Alfille", (8,)),
        ("C.L. Baker", (45,)),
        ("Mark S. Ball", (909,)),
        ("David Bernazzani", (314, 830, 970,)),
        ("Gordon Bower", (763, 783, 852, 959,)),
        ("Art Cabral", (9,)),
        ("Richard A. Canfield", (105, 835,)),
        ("Lillian Davies and Christa Baran", (605,)),
        ("Ann Edwards", (869,)),
        ("Robert Harbin", (381,)),
        ("Robert Hogue", (22216, 22217, 22218, 22231,)),
        ("Erik den Hollander", (344, 544,)),
        ("Rick Holzgrafe", (756, 757,)),
        ("Charles Jewell", (220, 309, 894,)),
        ("Michael Keller", (592, 883,)),
        ("Fred Lunde", (459,)),
        ("Mark Masten", (811,)),
        ("Albert Morehead and Geoffrey Mott-Smith", (25, 42, 48, 173, 282,
                                                     303, 362, 547, 738,
                                                     845, 967, 968)),
        ("Toby Ord", (788,)),
        ("David Parlett", (64, 98, 294, 338, 654, 796, 812, 844)),
        ("Joe R.", (938, 960,)),
        ("Randy Rasa", (187, 188, 190, 191, 192,)),
        ("Gregg Seelhoff", (347,)),
        ("Adam Selene", (366,)),
        ("Jim Sizelove", (555001,)),
        ("Captain Jeffrey T. Spaulding", (400,)),
        ("John Stoneham", (201,)),
        ("Bryan Stout", (655,)),
        ("Bill Taylor", (349,)),
        ("Bram Tebbutt", (924,)),
        ("Katharine Turner", (931,)),
        ("Peter Voke", (876,)),
        ("Thomas Warfield", (189, 264, 300, 320, 336, 337, 359,
                             415, 427, 458, 495, 496, 497, 508,
                             800, 814, 820, 825, 889, 911, 926,
                             941, 966)),
        ("Mary Whitmore Jones", (421, 624,)),
        ("Jan Wolter", (917, 939, 946, 963,)),
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
                  50, 51, 903, 53, 54, 55, 56, 57, 58, 59,
                  60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                  70, 71, 115, 73, 74, 126, 76, 77, 78, 79,
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
        ("4.00", (5034, 5035, 157, 158, 159, 160, 161, 162, 163, 164)),
        ('4.10', tuple(range(5001, 5034)) + tuple(range(5036, 5103))),
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
        ("4.70", (237, 22231)),
        ('fc-0.5.0', (  # moved from Ultrasol
                      # 121, 122, 187, 188, 189, 190, 191, 192, 194, 197, 198,
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
                      22232, ) +
         tuple(range(5200, 5280)) + tuple(range(5401, 5415)) +
         tuple(range(5801, 5811)) + tuple(range(5901, 5906))),
        ('fc-0.8.0', tuple(range(263, 323))),  # exclude 297
        ('fc-0.9.0', tuple(range(323, 421))),
        ('fc-0.9.1', tuple(range(421, 441))),
        ('fc-0.9.2', tuple(range(441, 466))),
        ('fc-0.9.3', tuple(range(466, 661))),
        ('fc-0.9.4', tuple(range(661, 671))),
        ('fc-1.0',   tuple(range(671, 711))),
        ('fc-1.1',   tuple(range(711, 759))),
        ('fc-2.0',   tuple(range(11011, 11014)) + tuple(range(759, 767))),
        ('fc-2.1',   tuple(range(767, 774)) + (1900, 1901, 555001,)),
        ('fc-2.8',   (343001,)),
        ('fc-2.12',   tuple(range(774, 811)) + (16681,) +
         tuple(range(22217, 22219))),
        ('fc-2.14', tuple(range(811, 827))),
        ('fc-2.15', tuple(range(827, 855)) + tuple(range(22400, 22407))),
        ('fc-2.20', tuple(range(855, 897))),
        ('fc-2.21', tuple(range(897, 900)) + tuple(range(11014, 11017)) +
         tuple(range(13160, 13163)) + (16682,)),
        ('fc-3.0', tuple(range(906, 961)) + tuple(range(5415, 5419)) +
         tuple(range(5600, 5624)) + tuple(range(11017, 11020)) +
         tuple(range(13168, 13170)) + tuple(range(18000, 18005)) +
         tuple(range(19000, 19012)) + tuple(range(22303, 22311)) +
         tuple(range(22353, 22361))),
        ('dev', tuple(range(961, 971))),
    )

    # deprecated - the correct way is to or a GI.GT_XXX flag
    # in the registerGame() call
    _CHILDREN_GAMES = [16, 33, 55, 90, 91, 96, 97, 176, 328, 329, 862, 865,
                       886, 903, ]

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
        34,    # Beleaguered Castle
        36,    # Golf
        38,    # Pyramid
        53,    # Montana
        105,   # Canfield
        158,   # Imperial Trumps
        279,   # Kings
        901,   # La Belle Lucie
        903,   # Aces Up
        5034,  # Mahjongg Flying Dragon
        5401,  # Mahjongg Taipei
        12345,  # Oonsoo
        22231,  # Three Peaks
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
                 si={}, category=0, subcategory=GI.GS_NONE,
                 short_name=None, altnames=(),
                 suits=list(range(4)), ranks=list(range(13)), trumps=(),
                 rules_filename=None,
                 ):
        #
        def to_unicode(s):
            if isinstance(s, str):
                return s
            try:
                s = str(s, 'utf-8')
            except UnicodeDecodeError as err:
                print_err(err)
                s = str(s, 'utf-8', 'ignore')
            return s
        ncards = decks * (len(suits) * len(ranks) + len(trumps))
        game_flags = game_type & ~1023
        game_type = game_type & 1023
        name = to_unicode(name)
        en_name = name                  # for app.getGameRulesFilename
        if pysollib.settings.TRANSLATE_GAME_NAMES:
            name = _(name)
        if not short_name:
            short_name = name
        else:
            short_name = to_unicode(short_name)
            if pysollib.settings.TRANSLATE_GAME_NAMES:
                short_name = _(short_name)
        if isinstance(altnames, str):
            altnames = (altnames,)
        altnames = [to_unicode(n) for n in altnames]
        if pysollib.settings.TRANSLATE_GAME_NAMES:
            altnames = [_(n) for n in altnames]
        #
        if not (1 <= category <= GI.NUM_CATEGORIES):
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
            if decks % 4:
                raise GameInfoException(name+": invalid number of decks " +
                                        str(id))
        else:
            if not (1 <= decks <= 4):
                raise GameInfoException(
                    name+": invalid number of decks "+str(id))
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
                        category=category, subcategory=subcategory,
                        skill_level=skill_level,
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
        # print 'check game:', gi.id, gi.short_name.encode('utf-8')
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
        # print gi.id, gi.short_name.encode('utf-8')
        if not isinstance(gi, GameInfo):
            raise GameInfoException("wrong GameInfo class")
        if self.check_game and pysollib.settings.CHECK_GAMES:
            self._check_game(gi)
        # if 0 and gi.si.game_flags & GI.GT_XORIGINAL:
        #     return
        # print gi.id, gi.name
        gi.altnames = sorted(gi.altnames)
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
            self.registered_game_types[k] = \
                self.registered_game_types.get(k, 0) + 1
#              if not gi.si.game_type == GI.GT_MAHJONGG:
#                  for v, k in GI.GAMES_BY_PYSOL_VERSION:
#                      if gi.id in k: break
#                  else:
#                      print gi.id
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
        # return self.__all_games
        return list(self.__games.values())

    def getGamesIdSortedById(self):
        if self.__games_by_id is None:
            lst = list(self.__games.keys())
            lst.sort()
            self.__games_by_id = tuple(lst)
        return self.__games_by_id

    def getGamesIdSortedByName(self):
        if self.__games_by_name is None:
            l1, l2, l3 = [], [], []
            for id, gi in self.__games.items():
                name = gi.name .lower()
                l1.append((name, id))
                if gi.name != gi.short_name:
                    name = gi.short_name.lower()
                l2.append((name, id))
                for n in gi.altnames:
                    name = n.lower()
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


def hideGame(game):
    game.gameinfo.si.game_type = GI.GT_HIDDEN
    registerGame(game.gameinfo)


def loadGame(modname, filename, check_game=False):
    # print "load game", modname, filename
    GAME_DB.check_game = check_game
    GAME_DB.current_filename = filename
    spec = util.spec_from_file_location(modname, filename)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # execfile(filename, globals(), globals())
    GAME_DB.current_filename = None
