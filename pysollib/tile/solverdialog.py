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

__all__ = [
    #'SolverDialog',
    'create_solver_dialog',
    'connect_game_solver_dialog',
    'destroy_solver_dialog',
    'reset_solver_dialog',
    ]

# imports
import ttk

# PySol imports
from pysollib.mygettext import _, n_
from pysollib.mfxutil import KwStruct

# Toolkit imports
from pysollib.tile.basetilemfxdialog import BaseTileMfxDialog
from tkwidget import PysolCombo
from pysollib.ui.tktile.solverdialog import BaseSolverDialog, solver_dialog, connect_game_solver_dialog, destroy_solver_dialog, reset_solver_dialog


# ************************************************************************
# *
# ************************************************************************

class SolverDialog(BaseSolverDialog, BaseTileMfxDialog):
    def _createGamesVar(self, frame, row):
        cb = PysolCombo(frame, values=tuple(self.gamenames),
                        selectcommand=self.gameSelected,
                        state='readonly', width=40)
        cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        return cb

    def _createPresetVar(self, frame, row):
        cb = PysolCombo(frame, values=tuple(self.presets), state='readonly')
        cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        cb.current(0)
        return cb
    def _createShowProgressButton(self, frame):
        return self._calcToolkit().Checkbutton(frame, variable=self.progress_var,
                            text=_('Show progress'))

    def initKw(self, kw):
        strings=[_('&Start'), _('&Play'), _('&New'), 'sep', _('&Close'),]
        kw = KwStruct(kw,
                      strings=strings,
                      default=0,
                      )
        return self._calc_MfxDialog().initKw(self, kw)

    def connectGame(self, game):
        name = self.app.getGameTitleName(game.id)
        if name in self.gamenames:
            self.start_button.config(state='normal')
            i = self.gamenames.index(name)
            self.games_var.current(i)
        else:
            self.start_button.config(state='disabled')
            self.games_var.current(0)
        self.play_button.config(state='disabled')



def create_solver_dialog(parent, game):
    global solver_dialog
    try:
        solver_dialog.top.wm_deiconify()
        solver_dialog.top.tkraise()
    except:
        ##traceback.print_exc()
        solver_dialog = SolverDialog(parent, game)

