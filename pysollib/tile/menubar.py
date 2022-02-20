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

from pysollib.mygettext import _, n_
from pysollib.settings import TITLE
from pysollib.ui.tktile.findcarddialog import connect_game_find_card_dialog
from pysollib.ui.tktile.findcarddialog import destroy_find_card_dialog
from pysollib.ui.tktile.menubar import MfxMenu, PysolMenubarTkCommon
from pysollib.ui.tktile.solverdialog import connect_game_solver_dialog
from pysollib.util import CARDSET

from six.moves import tkinter_ttk as ttk

from .selectgame import SelectGameDialog, SelectGameDialogWithPreview
from .selecttile import SelectTileDialogWithPreview
from .soundoptionsdialog import SoundOptionsDialog
from .tkwidget import MfxMessageDialog

# ************************************************************************
# * - create menubar
# * - update menubar
# * - menu actions
# ************************************************************************


class PysolMenubarTk(PysolMenubarTkCommon):
    def __init__(self, app, top, progress=None):
        PysolMenubarTkCommon.__init__(self, app, top, progress)

    def _setOptions(self):
        PysolMenubarTkCommon._setOptions(self)
        tkopt, opt = self.tkopt, self.app.opt
        tkopt.theme.set(opt.tile_theme)

    def _connect_game_find_card_dialog(self, game):
        return connect_game_find_card_dialog(game)

    def _destroy_find_card_dialog(self):
        return destroy_find_card_dialog()

    def _connect_game_solver_dialog(self, game):
        return connect_game_solver_dialog(game)

    def _calcWizardDialog(self):
        from .wizarddialog import WizardDialog
        return WizardDialog

    def _calcSelectGameDialog(self):
        return SelectGameDialog

    def _calcSelectGameDialogWithPreview(self):
        return SelectGameDialogWithPreview

    def _calcSoundOptionsDialog(self):
        return SoundOptionsDialog

    def _calcSelectTileDialogWithPreview(self):
        return SelectTileDialogWithPreview

    def _calc_MfxMessageDialog(self):
        return MfxMessageDialog

    #
    # create the menubar
    #

    def mSelectCardsetDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        key = self.app.nextgame.cardset.index
        cs = self.app.selectCardset(_("Select ")+CARDSET, key)
        if not cs:
            return
        self.app.nextgame.cardset = cs
        self._cancelDrag()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)
        self.updateMenus()

    #
    # Tile (ttk)
    #

    def mOptTheme(self, *event):
        theme = self.tkopt.theme.get()
        self.app.opt.tile_theme = theme
        self._calc_MfxMessageDialog()(
            self.top, title=_("Change theme"),
            text=_("""\
These settings will take effect
the next time you restart %(app)s""") % {'app': TITLE},
            bitmap="warning",
            default=0, strings=(_("&OK"),))

    def createThemesMenu(self, menu):
        submenu = MfxMenu(menu, label=n_("Set t&heme"))

        try:
            from ttkthemes import themed_style
            style_path = themed_style.ThemedStyle(self.top)
        except ImportError:
            style_path = ttk.Style(self.top)
        all_themes = list(style_path.theme_names())

        all_themes.sort()
        #
        tn = {
            'alt':         n_('Alt/Revitalized'),
            'itft1':       n_('ITFT1'),
            'scidblue':    n_('Scid Blue'),
            'scidgreen':   n_('Scid Green'),
            'scidgrey':    n_('Scid Grey'),
            'scidmint':    n_('Scid Mint'),
            'scidpink':    n_('Scid Pink'),
            'scidpurple':  n_('Scid Purple'),
            'scidsand':    n_('Scid Sand'),
            'winnative':   n_('Windows Native'),
            'winxpblue':   n_('Windows XP Blue'),
            'xpnative':    n_('XP Native'),
            }
        for t in all_themes:
            try:
                n = tn[t]
            except KeyError:
                n = t.capitalize()
            submenu.add_radiobutton(label=n, variable=self.tkopt.theme,
                                    value=t, command=self.mOptTheme)
