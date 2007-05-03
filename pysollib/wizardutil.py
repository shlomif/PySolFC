##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
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
##---------------------------------------------------------------------------##

import sys, os

from gamedb import GI, loadGame
from util import *
from stack import *
#from game import Game
from layout import Layout
#from hint import AbstractHint, DefaultHint, CautiousDefaultHint
#from pysoltk import MfxCanvasText

gettext = _
n_ = lambda x: x

# /***********************************************************************
# //
# ************************************************************************/

class WizSetting:
    def __init__(self, values_map, default, var_name,
                 label, widget='menu'):
        self.values_map = values_map
        self.default = gettext(default)
        ##self.values_dict = dict(self.values_map)
        self.translate_map = {}
        ##self.values = [i[0] for i in self.values_map]
        if widget == 'menu':
            self.values = []
            for k, v in self.values_map:
                t = gettext(k)
                self.values.append(t)
                self.translate_map[t] = k
            assert self.default in self.values
        else:
            self.values = self.values_map
        self.var_name = var_name
        self.label = label
        self.widget = widget
        self.variable = None            # Tk variable
        self.current_value = None


GameName = WizSetting(
    values_map = (),
    default = 'My Game',
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
    values_map = ((n_('Initial dealing'), InitialDealTalonStack),
                  (n_('Deal to waste'),   WasteTalonStack),
                  (n_('Deal to rows'),    DealRowTalonStack),
                  ),
    default = n_('Initial dealing'),
    label = _('Type of talon:'),
    var_name = 'talon',
    )
Redeals = WizSetting(
    values_map = ((n_('No redeals'), 0),
                  (n_('One redeal'), 1),
                  (n_('Two redeals'), 2),
                  (n_('Unlimited redeals'), -1),
                  ),
    default = n_('No redeals'),
    label = _('Number of redeals:'),
    var_name = 'redeals',
    )
FoundType = WizSetting(
    values_map = ((n_('Same suit'),       SS_FoundationStack),
                  (n_('Alternate color'), AC_FoundationStack),
                  (n_('Same color'),      SC_FoundationStack),
                  (n_('Rank'),            RK_FoundationStack),
                  ),
    default = n_('Same suit'),
    label = _('Type:'),
    var_name = 'found_type',
    )
FoundBaseCard = WizSetting(
    values_map = ((n_('Ace'), ACE), (n_('King'), KING)),
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
FoundWrap = WizSetting(
    values_map = ((n_('Yes'), True), (n_('No'), False)),
    default = n_('No'),
    label = _('Wrapping:'),
    var_name = 'found_wrap',
    )
FoundMaxMove = WizSetting(
    values_map = ((n_('No move'), 0,), (n_('One card'), 1)),
    default = n_('One card'),
    label = _('Max move cards:'),
    var_name = 'found_max_move',
    )
RowsNum = WizSetting(
    values_map = (1, 20),
    default = 8,
    widget = 'spin',
    label = _('Number of rows:'),
    var_name = 'rows_num',
    )
RowsType = WizSetting(
    values_map = ((n_('Same suit'),             SS_RowStack),
                  (n_('Alternate color'),       AC_RowStack),
                  (n_('Same color'),            SC_RowStack),
                  (n_('Rank'),                  RK_RowStack),
                  (n_('Any suit but the same'), BO_RowStack),
                  ),
    default = n_('Alternate color'),
    label = _('Type:'),
    var_name = 'rows_type',
    )
RowsBaseCard = WizSetting(
    values_map = ((n_('Ace'),  ACE),
                  (n_('King'), KING),
                  (n_('Any'),  ANY_RANK),
                  (n_('No'),   NO_RANK),
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
RowsWrap = WizSetting(
    values_map = ((n_('Yes'), True), (n_('No'), False)),
    default = n_('No'),
    label = _('Wrapping:'),
    var_name = 'rows_wrap',
    )
RowsMaxMove = WizSetting(
    values_map = ((n_('One card'), 1), (n_('Unlimited'), UNLIMITED_MOVES)),
    default = n_('Unlimited'),
    label = _('Max move cards:'),
    var_name = 'rows_max_move',
    )
ReservesNum = WizSetting(
    values_map = (0, 20),
    default = 4,
    widget = 'spin',
    label = _('Number of reserves:'),
    var_name = 'reserves_num',
    )
ReservesType = WizSetting(
    values_map = ((n_('FreeCell'), ReserveStack),
                  (n_('Reserve'),  OpenStack),
                  ),
    default = n_('FreeCell'),
    label = n_('Type of reserves:'),
    var_name = 'reserves_type',
    )
DealType = WizSetting(
    values_map = ((n_('Triangle'),  'triangle'),
                  (n_('Rectangle'), 'rectangle'),
                  ),
    default = n_('Rectangle'),
    label = _('Type:'),
    var_name = 'deal_type',
    )
DealFaceUp = WizSetting(
    values_map = ((n_('Top cards'), 'top'), (n_('All cards'), 'all')),
    default = n_('All cards'),
    label = _('Face-up:'),
    var_name = 'deal_faceup',
    )
DealMaxRows = WizSetting(
    values_map = (0, 20),
    default = 7,
    widget = 'spin',
    label = _('Deal to rows:'),
    var_name = 'deal_to_rows',
    )
DealToReseves = WizSetting(
    values_map = (0, 20),
    default = 0,
    widget = 'spin',
    label = _('Deal ro reserves:'),
    var_name = 'deal_to_reserves',
    )

WizardWidgets = (
    _('General'),
    GameName,
    SkillLevel,
    NumDecks,
    LayoutType,
    _('Talon'),
    TalonType,
    Redeals,
    _('Foundations'),
    FoundType,
    FoundBaseCard,
    FoundDir,
    FoundWrap,
    FoundMaxMove,
    _('Tableau'),
    RowsNum,
    RowsType,
    RowsBaseCard,
    RowsDir,
    RowsWrap,
    RowsMaxMove,
    _('Reserves'),
    ReservesNum,
    ReservesType,
    _('Initial dealing'),
    DealType,
    DealFaceUp,
    DealMaxRows,
    DealToReseves,
    )


def write_game(app, game=None):

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
        fn = game.SETTINGS['file']
        fn = os.path.join(app.dn.plugins, fn)
        mn = game.__module__
        gameid = game.SETTINGS['gameid']
        n = gameid-200000
        check_game = False

    ##print '===>', fn
    fd = open(fn, 'w')

    fd.write('''\
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
        if w.widget == 'menu':
            v = w.translate_map[v]
        if isinstance(v, int):
            fd.write("        '%s': %i,\n" % (w.var_name, v))
        else:
            fd.write("        '%s': '%s',\n" % (w.var_name, v))
    fd.write("        'gameid': %i,\n" % gameid)
    fd.write("        'file': '%s',\n" % os.path.split(fn)[1])

    fd.write('''\
        }

registerCustomGame(MyCustomGame)
''')
    fd.close()

    loadGame(mn, fn, check_game=check_game)

    return gameid

def reset_wizard(game):
    s = game.SETTINGS
    for w in WizardWidgets:
        if isinstance(w, basestring):
            continue
        v = s[w.var_name]
        if w.widget == 'menu':
            v = gettext(v)
        w.current_value = v


