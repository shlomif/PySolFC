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
from pysollib.settings import TITLE
from pysollib.mfxutil import KwStruct

# Toolkit imports
from tkwidget import MfxDialog
from pysollib.ui.tktile.solverdialog import BaseSolverDialog, solver_dialog, connect_game_solver_dialog, destroy_solver_dialog, reset_solver_dialog


# ************************************************************************
# *
# ************************************************************************

class SolverDialog(BaseSolverDialog, MfxDialog):

    def _calcToolkit(self):
        return Tkinter

    def __init__(self, parent, app, **kw):
        self.parent = parent
        self.app = app
        title = TITLE+' - FreeCell Solver'
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.solving_methods = {
            'A*':                   'a-star',
            'Breadth-First Search': 'bfs',
            'Depth-First Search':   'soft-dfs', # default
            'A randomized DFS':     'random-dfs',
            ##'"Soft" DFS':           'soft-dfs',
            }
        self.games = {}                 # key: gamename; value: gameid

        #
        frame = self._calcToolkit().Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=4, pady=4)
        frame.columnconfigure(1, weight=1)

        #
        row = 0
        self._calcToolkit().Label(frame, text=_('Game:'), anchor='w'
                  ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        games = app.getGamesForSolver()
        gamenames = ['']
        for id in games:
            name = app.getGameTitleName(id)
            gamenames.append(name)
            self.games[name] = id
        gamenames.sort()
        self.gamenames = gamenames
        self.games_var = var = Tkinter.StringVar()
        om = Tkinter.OptionMenu(frame, var, command=self.gameSelected,
                                *gamenames)
        om.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        n = len(gamenames)
        cb_max = int(self.top.winfo_screenheight()/23)
        cb_max = n / (n/cb_max+1)
        for i in xrange(cb_max, n, cb_max):
            om['menu'].entryconfig(i, columnbreak=True)

        #
        row += 1
        self._calcToolkit().Label(frame, text=_('Preset:'), anchor='w'
                  ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        presets = app.opt.solver_presets
        self.presets = presets
        self.preset_var = var = Tkinter.StringVar()
        var.set('none')
        om = Tkinter.OptionMenu(frame, var, *presets)
        om.grid(row=row, column=1, sticky='ew', padx=2, pady=2)

        #
        row += 1
        self.max_iters_var = Tkinter.IntVar()
        self.max_iters_var.set(10e4)
        self._calcToolkit().Label(frame, text=_('Max iterations:'), anchor='w'
                  ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        spin = Tkinter.Spinbox(frame, bg='white', from_=1000, to=10e6,
                               increment=1000, textvariable=self.max_iters_var)
        spin.grid(row=row, column=1, sticky='w', padx=2, pady=2)

        #
        row += 1
        self.max_depth_var = Tkinter.IntVar()
        self.max_depth_var.set(1000)
        self._calcToolkit().Label(frame, text=_('Max depth:'), anchor='w'
                  ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        spin = Tkinter.Spinbox(frame, bg='white', from_=100, to=10000,
                               increment=100, textvariable=self.max_depth_var)
        spin.grid(row=row, column=1, sticky='w', padx=2, pady=2)

        #
        row += 1
        self.progress_var = Tkinter.BooleanVar()
        self.progress_var.set(True)
        w = self._createShowProgressButton(frame)
        w.grid(row=row, column=0, columnspan=2, sticky='ew', padx=2, pady=2)

        #
        label_frame = self._calcToolkit().LabelFrame(top_frame, text=_('Progress'))
        label_frame.pack(expand=True, fill='both', padx=6, pady=2)
        #label_frame.columnconfigure(0, weight=1)
        label_frame.columnconfigure(1, weight=1)

        #
        frow = 0
        self._calcToolkit().Label(label_frame, text=_('Iteration:'), anchor='w'
                  ).grid(row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = self._calcToolkit().Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.iter_label = lb
        frow += 1
        self._calcToolkit().Label(label_frame, text=_('Depth:'), anchor='w'
                  ).grid(row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = self._calcToolkit().Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.depth_label = lb
        frow += 1
        self._calcToolkit().Label(label_frame, text=_('Stored-States:'), anchor='w'
                  ).grid(row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = self._calcToolkit().Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.states_label = lb

        #
        lb = self._calcToolkit().Label(top_frame, anchor='w')
        lb.pack(expand=True, fill='x', padx=6, pady=4)
        self.result_label = lb

        #
        focus = self.createButtons(bottom_frame, kw)
        self.start_button = self.buttons[0]
        self.play_button = self.buttons[1]
        self._reset()
        self.connectGame(self.app.game)
        self.mainloop(focus, kw.timeout, transient=False)

    def _createShowProgressButton(self, frame):
        return self._calcToolkit().Checkbutton(frame, variable=self.progress_var,
                            text=_('Show progress'), anchor='w')

    def initKw(self, kw):
        strings=[_('&Start'), _('&Play'), _('&New'), _('&Close'),]
        kw = KwStruct(kw,
                      strings=strings,
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)

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

