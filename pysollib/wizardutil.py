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

import os

from gamedb import GI, loadGame
from util import *
from stack import *
from layout import Layout
from wizardpresets import presets


# ************************************************************************
# *
# ************************************************************************

class WizSetting:
    def __init__(self, values_map, default, var_name,
                 label, widget='menu'):
        self.values_map = values_map
        self.default = default
        ##self.values_dict = dict(self.values_map)
        self.translation_map = {}       # for backward translation
        if widget == 'menu':
            self.values = []
            for k, v in self.values_map:
                self.values.append(k)
                self.translation_map[_(k)] = k
            assert self.default in self.values
        elif widget == 'preset':
            self.values = []
            for v in self.values_map:
                self.values.append(v)
                self.translation_map[_(v)] = v
            assert self.default in self.values
        else:
            self.values = self.values_map
        self.var_name = var_name
        self.label = label
        self.widget = widget
        self.variable = None            # Tk variable
        self.current_value = None


WizardPresets = WizSetting(
    values_map = presets.keys(),
    default = 'None',
    widget = 'preset',
    label = _('Initial setting:'),
    var_name = 'preset',
    )
GameName = WizSetting(
    values_map = (),
    default = _('My Game'),
    widget = 'entry',
    label = _('Name:'),
    var_name = 'name',
    )
SkillLevel = WizSetting(
    values_map = ((n_('Luck only'),    GI.SL_LUCK),
                  (n_('Mostly luck'),  GI.SL_MOSTLY_LUCK),
                  (n_('Balanced'),     GI.SL_BALANCED),
                  (n_('Mostly skill'), GI.SL_MOSTLY_SKILL),
                  (n_('Skill only'),   GI.SL_SKILL),
                  ),
    default = n_('Balanced'),
    label = _('Skill level:'),
    var_name = 'skill_level',
    )
NumDecks = WizSetting(
    values_map = ((n_('One'),   1),
                  (n_('Two'),   2),
                  (n_('Three'), 3),
                  (n_('Four'),  4)),
    default = n_('One'),
    label = _('Number of decks:'),
    var_name = 'decks',
    )
LayoutType = WizSetting(
    values_map = ((n_('FreeCell'), Layout.freeCellLayout),
                  (n_('Klondike'), Layout.klondikeLayout),
                  (n_('Gypsy'),    Layout.gypsyLayout),
                  (n_('Harp'),     Layout.harpLayout),
                  ),
    default = n_('FreeCell'),
    label = _('Layout:'),
    var_name = 'layout',
    )
TalonType = WizSetting(
    values_map = ((n_('Deal all cards at the beginning'), InitialDealTalonStack),
                  (n_('Deal to waste'),         WasteTalonStack),
                  (n_('Deal to tableau'),       DealRowRedealTalonStack),
                  (n_('Deal to reserves'),      DealReserveRedealTalonStack),
                  (n_('Spider'),                SpiderTalonStack),
                  (n_('Grounds for a Divorce'), GroundsForADivorceTalonStack),
                  ),
    default = n_('Deal all cards at the beginning'),
    label = _('Type:'),
    var_name = 'talon',
    )
Redeals = WizSetting(
    values_map = ((n_('No redeals'), 0),
                  (n_('One redeal'), 1),
                  (n_('Two redeals'), 2),
                  (n_('Three redeals'), 3),
                  (n_('Unlimited redeals'), -1),
                  ),
    default = n_('No redeals'),
    label = _('Number of redeals:'),
    var_name = 'redeals',
    )
DealToWaste = WizSetting(
    values_map = (1, 5),
    default = 1,
    widget = 'spin',
    label = _('# of cards dealt to the waste:'),
    var_name = 'deal_to_waste',
    )
TalonShuffle = WizSetting(
    values_map = (0, 1),
    default = 0,
    label = _('Shuffle during redeal:'),
    var_name = 'talon_shuffle',
    widget = 'check',
    )
FoundType = WizSetting(
    values_map = ((n_('Same suit'),              SS_FoundationStack),
                  (n_('Alternate color'),        AC_FoundationStack),
                  (n_('Same color'),             SC_FoundationStack),
                  (n_('Rank'),                   RK_FoundationStack),
                  (n_('Spider same suit'),       Spider_SS_Foundation),
                  (n_('Spider alternate color'), Spider_AC_Foundation),
                  (n_('Spider rank'),            Spider_RK_Foundation),
                  ),
    default = n_('Same suit'),
    label = _('Type:'),
    var_name = 'found_type',
    )
FoundBaseCard = WizSetting(
    values_map = ((n_('Ace'),  ACE),
                  (n_('King'), KING),
                  (n_('Any'),  ANY_RANK),
                  ),
    default = n_('Ace'),
    label = _('Base card:'),
    var_name = 'found_base_card',
    )
FoundDir = WizSetting(
    values_map = ((n_('Up'), 1), (n_('Down'), -1)),
    default = n_('Up'),
    label = _('Direction:'),
    var_name = 'found_dir',
    )
FoundMaxMove = WizSetting(
    values_map = ((n_('None'), 0,), (n_('Top card'), 1)),
    default = n_('Top card'),
    label = _('Move:'),
    var_name = 'found_max_move',
    )
FoundEqual = WizSetting(
    values_map = (0, 1),
    default = 1,
    label = _('First card sets base cards:'),
    var_name = 'found_equal',
    widget = 'check',
    )
RowsNum = WizSetting(
    values_map = (1, 20),
    default = 8,
    widget = 'spin',
    label = _('Number of tableau piles:'),
    var_name = 'rows_num',
    )
RowsType = WizSetting(
    values_map = ((n_('Same suit'),                     SS_RowStack),
                  (n_('Alternate color'),               AC_RowStack),
                  (n_('Same color'),                    SC_RowStack),
                  (n_('Rank'),                          RK_RowStack),
                  (n_('Any suit but the same'),         BO_RowStack),

                  (n_('Up or down by same suit'),       UD_SS_RowStack),
                  (n_('Up or down by alternate color'), UD_AC_RowStack),
                  (n_('Up or down by rank'),            UD_RK_RowStack),
                  (n_('Up or down by same color'),      UD_SC_RowStack),

                  (n_('Spider same suit'),              Spider_SS_RowStack),
                  (n_('Spider alternate color'),        Spider_AC_RowStack),

                  (n_('Yukon same suit'),               Yukon_SS_RowStack),
                  (n_('Yukon alternate color'),         Yukon_AC_RowStack),
                  (n_('Yukon rank'),                    Yukon_RK_RowStack),
                  ),
    default = n_('Alternate color'),
    label = _('Type:'),
    var_name = 'rows_type',
    )
RowsBaseCard = WizSetting(
    values_map = ((n_('Ace'),  ACE),
                  (n_('King'), KING),
                  (n_('Any'),  ANY_RANK),
                  (n_('None'), NO_RANK),
                  ),
    default = n_('Any'),
    label = _('Base card:'),
    var_name = 'rows_base_card',
    )
RowsDir = WizSetting(
    values_map = ((n_('Up'), 1), (n_('Down'), -1)),
    default = n_('Down'),
    label = _('Direction:'),
    var_name = 'rows_dir',
    )
RowsMaxMove = WizSetting(
    values_map = ((n_('Top card'), 1), (n_('Sequence'), UNLIMITED_MOVES)),
    default = n_('Sequence'),
    label = _('Move:'),
    var_name = 'rows_max_move',
    )
RowsWrap = WizSetting(
    values_map = (0, 1),
    default = 0,
    label = _('Wrapping:'),
    var_name = 'rows_wrap',
    widget = 'check',
    )
RowsSuperMove = WizSetting(
    values_map = (0, 1),
    default = 0,
    label = _('Use "Super Move" feature:'),
    var_name = 'rows_super_move',
    widget = 'check',
    )
ReservesNum = WizSetting(
    values_map = (0, 20),
    default = 4,
    widget = 'spin',
    label = _('Number of reserves:'),
    var_name = 'reserves_num',
    )
ReservesMaxAccept = WizSetting(
    values_map = (0, 20),
    default = 1,
    widget = 'spin',
    label = _('Max # of accepted cards:'),
    var_name = 'reserves_max_accept',
    )
DealType = WizSetting(
    values_map = ((n_('Triangle'),  'triangle'),
                  (n_('Rectangle'), 'rectangle'),
                  ),
    default = n_('Rectangle'),
    label = _('Type:'),
    var_name = 'deal_type',
    )
DealFaceDown = WizSetting(
    values_map = (0, 20),
    default = 0,
    widget = 'spin',
    label = _('# of face-down cards dealt to the tableau pile:'),
    var_name = 'deal_face_down',
    )
DealFaceUp = WizSetting(
    values_map = (0, 20),
    default = 8,
    widget = 'spin',
    label = _('# of face-up cards dealt to the tableau pile:'),
    var_name = 'deal_face_up',
    )
DealToReseves = WizSetting(
    values_map = (0, 208),
    default = 0,
    widget = 'spin',
    label = _('# of cards dealt to the reserve:'),
    var_name = 'deal_to_reserves',
    )
DealMaxCards = WizSetting(
    values_map = (0, 208),
    default = 52,
    widget = 'spin',
    label = _('Max # of dealt cards:'),
    var_name = 'deal_max_cards',
    )
DealToFound = WizSetting(
    values_map = (0, 1),
    default = 0,
    label = _('Deal first cards to the foundations:'),
    var_name = 'deal_found',
    widget = 'check',
    )

WizardWidgets = (
    _('General'),
    WizardPresets,
    GameName,
    SkillLevel,
    NumDecks,
    LayoutType,
    _('Talon'),
    TalonType,
    Redeals,
    DealToWaste,
    TalonShuffle,
    _('Foundations'),
    FoundType,
    FoundBaseCard,
    FoundDir,
    FoundMaxMove,
    FoundEqual,
    _('Tableau'),
    RowsNum,
    RowsType,
    RowsBaseCard,
    RowsDir,
    RowsMaxMove,
    RowsWrap,
    RowsSuperMove,
    _('Reserves'),
    ReservesNum,
    ReservesMaxAccept,
    _('Opening deal'),
    DealType,
    DealFaceDown,
    DealFaceUp,
    DealToReseves,
    DealMaxCards,
    DealToFound,
    )


def write_game(app, game=None):
    import customgame                   # for py2exe

    if game is None:
        # new game
        d = app.dn.plugins
        ls = os.listdir(d)
        n = 1
        while True:
            fn = os.path.join(d, 'customgame%d.py' % n) # file name
            mn = 'customgame%d' % n         # module name
            gameid = 200000+n
            if not os.path.exists(fn):
                break
            n += 1
        check_game = True
    else:
        # edit current game
        fn = game.MODULE_FILENAME
        mn = game.__module__
        gameid = game.SETTINGS['gameid']
        check_game = False

    ##print '===>', fn
    fd = open(fn, 'w')

    fd.write('''\
## -*- coding: utf-8 -*-
## THIS FILE WAS GENERATED AUTOMATICALLY BY SOLITAIRE WIZARD
## DO NOT EDIT

from pysollib.customgame import CustomGame, registerCustomGame

class MyCustomGame(CustomGame):
    WIZARD_VERSION = 1
    SETTINGS = {
''')

    for w in WizardWidgets:
        if isinstance(w, basestring):
            continue
        v = w.variable.get()
        if w.widget in ('menu', 'preset'):
            v = w.translation_map[v]
        if v == w.default:
            # save only unique values
            continue
        if isinstance(v, int):
            fd.write("        '%s': %i,\n" % (w.var_name, v))
        else:
            if w.var_name == 'name':
                # escape
                v = v.replace('\\', '\\\\')
                v = v.replace("'", "\\'")
                if isinstance(v, unicode):
                    v = v.encode('utf-8')
                if not v:
                    v = 'Invalid Game Name'
            fd.write("        '%s': '%s',\n" % (w.var_name, v))
    fd.write("        'gameid': %i,\n" % gameid)

    fd.write('''\
        }

registerCustomGame(MyCustomGame)
''')
    fd.close()

    loadGame(mn, fn, check_game=check_game)

    return gameid

def reset_wizard(game):
    for w in WizardWidgets:
        if isinstance(w, basestring):
            continue
        if game is None:
            # set to default
            v = w.default
        else:
            # set from current game
            if w.var_name in game.SETTINGS:
                v = game.SETTINGS[w.var_name]
            else:
                v = w.default
        w.current_value = v


