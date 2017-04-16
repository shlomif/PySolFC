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
import Tkinter

# PySol imports
from pysollib.mygettext import _, n_
from pysollib.mfxutil import KwStruct

# Toolkit imports
from pysollib.tk.basetkmfxdialog import BaseTkMfxDialog
from pysollib.ui.tktile.solverdialog import BaseSolverDialog, solver_dialog, connect_game_solver_dialog, destroy_solver_dialog, reset_solver_dialog


# ************************************************************************
# *
# ************************************************************************

class SolverDialog(BaseSolverDialog, BaseTkMfxDialog):
    def _createGamesVar(self, frame, row):
        var = Tkinter.StringVar()
        om = Tkinter.OptionMenu(frame, var, command=self.gameSelected,
                                *(self.gamenames))
        om.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        n = len(gamenames)
        cb_max = int(self.top.winfo_screenheight()/23)
        cb_max = n / (n/cb_max+1)
        for i in xrange(cb_max, n, cb_max):
            om['menu'].entryconfig(i, columnbreak=True)
        return var

    def _createPresetVar(self, frame, row):
        var = Tkinter.StringVar()
        var.set('none')
        om = Tkinter.OptionMenu(frame, var, *(self.presets))
        om.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        return var

    def _createShowProgressButton(self, frame):
        return self._calcToolkit().Checkbutton(frame, variable=self.progress_var,
                            text=_('Show progress'), anchor='w')

    def initKw(self, kw):
        strings=[_('&Start'), _('&Play'), _('&New'), _('&Close'),]
        kw = KwStruct(kw,
                      strings=strings,
                      default=0,
                      )
        return self._calc_MfxDialog().initKw(self, kw)

    def connectGame(self, game):
        name = self.app.getGameTitleName(game.id)
        if name in self.gamenames:
            self.start_button.config(state='normal')
            self.games_var.set(name)
        else:
            self.start_button.config(state='disabled')
            self.games_var.set('')
        self.play_button.config(state='disabled')



def create_solver_dialog(parent, game):
    global solver_dialog
    try:
        solver_dialog.top.wm_deiconify()
        solver_dialog.top.tkraise()
    except:
        ##traceback.print_exc()
        solver_dialog = SolverDialog(parent, game)

