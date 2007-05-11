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

__all__ = [
    #'SolverDialog',
    'create_solver_dialog',
    'connect_game_solver_dialog',
    'destroy_solver_dialog',
    'reset_solver_dialog',
    ]

# imports
import os, sys
import Tile as Tkinter
import traceback

# PySol imports
from pysollib.mfxutil import destruct, kwdefault, KwStruct, Struct
from pysollib.settings import PACKAGE

# Toolkit imports
from tkconst import EVENT_HANDLED, EVENT_PROPAGATE
from tkwidget import MfxDialog
from tkwidget import PysolScale
from tkutil import bind, unbind_destroy


# /***********************************************************************
# //
# ************************************************************************/

class SolverDialog(MfxDialog):

    def __init__(self, parent, app, **kw):
        self.parent = parent
        self.app = app
        title = PACKAGE+' - FreeCell Solver'
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
        frame = Tkinter.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=4, pady=4)
        frame.columnconfigure(1, weight=1)

        #
        row = 0
        Tkinter.Label(frame, text=_('Game:'), anchor='w'
                      ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        games = app.getGamesForSolver()
        gamenames = ['']
        for id in games:
            name = app.getGameTitleName(id)
            name = _(name)
            gamenames.append(name)
            self.games[name] = id
        gamenames.sort()
        self.gamenames = gamenames
        cb = Tkinter.Combobox(frame, values=tuple(gamenames),
                              state='readonly', width=40)
        cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        bind(cb, '<<ComboboxSelected>>', self.gameSelected)
        self.games_var = cb

        #
        row += 1
        Tkinter.Label(frame, text=_('Solving method:'), anchor='w'
                      ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        ##sm = self.solving_methods.values()
        ##sm.sort()
        sm = ['A*',
              'Breadth-First Search',
              'Depth-First Search',
              'A randomized DFS',
              ##'"Soft" DFS'
              ]
        cb = Tkinter.Combobox(frame, values=tuple(sm), state='readonly')
        cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        cb.current(sm.index('Depth-First Search'))
        self.solving_method_var = cb

        #
        row += 1
        Tkinter.Label(frame, text=_('Preset:'), anchor='w'
                      ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        presets = [
            'none',
            'abra-kadabra',
            'cool-jives',
            'crooked-nose',
            'fools-gold',
            'good-intentions',
            'hello-world',
            'john-galt-line',
            'rin-tin-tin',
            'yellow-brick-road',
            ]
        self.presets = presets
        cb = Tkinter.Combobox(frame, values=tuple(presets), state='readonly')
        cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
        cb.current(0)
        self.preset_var = cb

        #
        row += 1
        self.max_iters_var = Tkinter.IntVar()
        self.max_iters_var.set(10e4)
        Tkinter.Label(frame, text=_('Max iterations:'), anchor='w'
                      ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        spin = Tkinter.Spinbox(frame, bg='white', from_=1000, to=10e6,
                               increment=1000, textvariable=self.max_iters_var)
        spin.grid(row=row, column=1, sticky='w', padx=2, pady=2)

        #
        row += 1
        self.max_depth_var = Tkinter.IntVar()
        self.max_depth_var.set(1000)
        Tkinter.Label(frame, text=_('Max depth:'), anchor='w'
                      ).grid(row=row, column=0, sticky='ew', padx=2, pady=2)
        spin = Tkinter.Spinbox(frame, bg='white', from_=100, to=10000,
                               increment=100, textvariable=self.max_depth_var)
        spin.grid(row=row, column=1, sticky='w', padx=2, pady=2)

        #
        row += 1
        self.progress_var = Tkinter.BooleanVar()
        self.progress_var.set(True)
        w = Tkinter.Checkbutton(frame, variable=self.progress_var,
                                text=_('Show progress'))
        w.grid(row=row, column=0, columnspan=2, sticky='ew', padx=2, pady=2)

        #
        label_frame = Tkinter.LabelFrame(top_frame, text=_('Progress'))
        label_frame.pack(expand=True, fill='both', padx=6, pady=2)
        #label_frame.columnconfigure(0, weight=1)
        label_frame.columnconfigure(1, weight=1)

        #
        frow = 0
        Tkinter.Label(label_frame, text=_('Iteration:'), anchor='w'
                      ).grid(row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = Tkinter.Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.iter_label = lb
        frow += 1
        Tkinter.Label(label_frame, text=_('Depth:'), anchor='w'
                      ).grid(row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = Tkinter.Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.depth_label = lb
        frow += 1
        Tkinter.Label(label_frame, text=_('Stored-States:'), anchor='w'
                      ).grid(row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = Tkinter.Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.states_label = lb

        #
        lb = Tkinter.Label(top_frame, anchor='w')
        lb.pack(expand=True, fill='x', padx=6, pady=4)
        self.result_label = lb

        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout, transient=False)

        self.start_button = self.buttons[0]
        self.play_button = self.buttons[1]

        #
        self._reset()
        self.connectGame(self.app.game)

    def initKw(self, kw):
        strings=[_('&Start'), _('&Play'), _('&New'), 'sep', _('&Close'),]
        kw = KwStruct(kw,
                      strings=strings,
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        if button == 0:
            self.startSolving()
        elif button == 1:
            self.startPlay()
        elif button == 2:
            self.app.menubar.mNewGame()
        elif button == 3:
            global solver_dialog
            solver_dialog = None
            self.destroy()
        return EVENT_HANDLED

    def mCancel(self, *event):
        return self.mDone(3)

    def wmDeleteWindow(self, *event):
        return self.mDone(3)

    def gameSelected(self, *event):
        name = self.games_var.get()
        if not name:
            return
        id = self.games[name]
        self.app.menubar._mSelectGame(id)

    def connectGame(self, game):
        name = self.app.getGameTitleName(game.id)
        name = _(name)
        if name in self.gamenames:
            self.start_button.config(state='normal')
            i = self.gamenames.index(name)
            self.games_var.current(i)
        else:
            self.start_button.config(state='disabled')
            self.games_var.current(0)
        self.play_button.config(state='disabled')

    def _reset(self):
        self.play_button.config(state='disabled')
        self.setText(iter='', depth='', states='')
        self.result_label['text'] = ''
        self.top.update_idletasks()

    def reset(self):
        self.play_button.config(state='disabled')

    def startSolving(self):
        self._reset()
        game = self.app.game
        solver = game.Solver_Class(game, self) # create solver instance
        game.solver = solver
        method = self.solving_method_var.get()
        method = self.solving_methods[method]
        preset = self.preset_var.get()
        max_iters = self.max_iters_var.get()
        max_depth = self.max_depth_var.get()
        progress = self.progress_var.get()
        solver.config(method=method, preset=preset,  max_iters=max_iters,
                      max_depth=max_depth, progress=progress)
        solver.computeHints()
        hints_len = len(solver.hints)-1
        if hints_len > 0:
            self.result_label['text'] = _('This game is solveable in %s moves.') % hints_len
            self.play_button.config(state='normal')
        else:
            self.result_label['text'] = _('I could not solve this game.')
            self.play_button.config(state='disabled')

    def startPlay(self):
        self.play_button.config(state='disabled')
        self.app.top.tkraise()
        self.app.top.update_idletasks()
        self.app.top.update()
        self.app.game.startDemo(level=3)

    def setText(self, **kw):
        if 'iter' in kw:
            self.iter_label['text'] = kw['iter']
        if 'depth' in kw:
            self.depth_label['text'] = kw['depth']
        if 'states' in kw:
            self.states_label['text'] = kw['states']
        self.top.update_idletasks()



solver_dialog = None

def create_solver_dialog(parent, game):
    global solver_dialog
    try:
        solver_dialog.top.wm_deiconify()
        solver_dialog.top.tkraise()
    except:
        ##traceback.print_exc()
        solver_dialog = SolverDialog(parent, game)

def connect_game_solver_dialog(game):
    try:
        solver_dialog.connectGame(game)
    except:
        pass

def destroy_solver_dialog():
    global solver_dialog
    try:
        solver_dialog.destroy()
    except:
        ##traceback.print_exc()
        pass
    solver_dialog = None


def reset_solver_dialog():
    if solver_dialog:
        try:
            solver_dialog.reset()
        except:
            ##traceback.print_exc()
            pass

