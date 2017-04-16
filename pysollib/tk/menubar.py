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

__all__ = ['PysolMenubarTk']

# imports
import Tkinter

# PySol imports
from pysollib.mygettext import _, n_
from pysollib.mfxutil import USE_PIL
from pysollib.util import CARDSET

# toolkit imports
from pysollib.ui.tktile.tkconst import EVENT_HANDLED, EVENT_PROPAGATE, CURSOR_WATCH, COMPOUNDS
from pysollib.ui.tktile.tkutil import bind, after_idle
from tkwidget import MfxMessageDialog
from selectgame import SelectGameDialog, SelectGameDialogWithPreview
from soundoptionsdialog import SoundOptionsDialog
from selectcardset import SelectCardsetDialogWithPreview
from selecttile import SelectTileDialogWithPreview
from pysollib.ui.tktile.findcarddialog import connect_game_find_card_dialog, destroy_find_card_dialog
from solverdialog import connect_game_solver_dialog

from pysollib.ui.tktile.menubar import PysolMenubarTkCommon
# ************************************************************************
# * - create menubar
# * - update menubar
# * - menu actions
# ************************************************************************

class PysolMenubarTk(PysolMenubarTkCommon):
    def __init__(self, app, top, progress=None):
        PysolMenubarTkCommon.__init__(self, app, top, progress)

    def _connect_game_find_card_dialog(self, game):
        return connect_game_find_card_dialog(game)

    def _destroy_find_card_dialog(self):
        return destroy_find_card_dialog()

    def _connect_game_solver_dialog(self, game):
        return connect_game_solver_dialog(game)

    def _calcWizardDialog(self):
        from wizarddialog import WizardDialog
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

    def createThemesMenu(self, menu):
        return


    def mSelectCardsetDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        ##strings, default = ("&OK", "&Load", "&Cancel"), 0
        strings, default = (None, _("&Load"), _("&Cancel"),), 1
        strings, default = (None, _("&Load"), _("&Cancel"), _("&Info..."),), 1
        t = CARDSET
        key = self.app.nextgame.cardset.index
        d = SelectCardsetDialogWithPreview(self.top, title=_("Select ")+t,
                app=self.app, manager=self.app.cardset_manager, key=key,
                strings=strings, default=default)
        cs = self.app.cardset_manager.get(d.key)
        if d.status != 0 or d.button != 1 or cs is None:
            return
        if USE_PIL:
            changed = (self.app.opt.scale_x,
                       self.app.opt.scale_y,
                       self.app.opt.auto_scale,
                       self.app.opt.preserve_aspect_ratio) != d.scale_values
        else:
            changed = False
        if d.key == self.app.cardset.index and not changed:
            return
        if d.key >= 0:
            self.app.nextgame.cardset = cs
            if USE_PIL:
                (self.app.opt.scale_x,
                 self.app.opt.scale_y,
                 self.app.opt.auto_scale,
                 self.app.opt.preserve_aspect_ratio) = d.scale_values
                if not self.app.opt.auto_scale:
                    self.app.images.resize(self.app.opt.scale_x,
                                           self.app.opt.scale_y)
            self._cancelDrag()
            self.game.endGame(bookmark=1)
            self.game.quitGame(bookmark=1)



    def setToolbarRelief(self, relief):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_relief = relief
        self.tkopt.toolbar_relief.set(relief)           # update radiobutton
        self.app.toolbar.setRelief(relief)
        self.top.update_idletasks()


