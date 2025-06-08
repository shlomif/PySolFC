import tkinter

from pysollib.mygettext import _
from pysollib.settings import TITLE
from pysollib.tile.tkwidget import PysolSpinbox
from pysollib.ui.tktile.tkconst import EVENT_HANDLED


class BaseSolverDialog:
    def _ToggleShowProgressButton(self, *args):
        self.app.opt.solver_show_progress = self.progress_var.get()

    def _getMaxIters(self):
        try:
            i = self.max_iters_var.get()
        except Exception:
            i = 100000
        return i

    def _OnAssignToMaxIters(self, *args):
        self.app.opt.solver_max_iterations = self._getMaxIters()

    def _OnAssignToPreset(self, *args):
        self.app.opt.solver_preset = self.preset_var.get()

    def __init__(self, parent, app, **kw):
        self.parent = parent
        self.app = app
        title = _('%(app)s - FreeCell Solver') % {'app': TITLE}
        kw = self.initKw(kw)
        self._calc_MfxDialog().__init__(
            self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        self.games = {}                 # key: gamename; value: gameid

        #
        frame = self._calcToolkit().Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=4, pady=4)
        frame.columnconfigure(1, weight=1)

        #
        row = 0
        self._calcToolkit().Label(
            frame, text=_('Game:'), anchor='w').grid(
            row=row, column=0, sticky='ew', padx=2, pady=2)
        games = app.getGamesForSolver()
        gamenames = ['']
        for id in games:
            name = app.getGameTitleName(id)
            gamenames.append(name)
            self.games[name] = id
        gamenames.sort()
        self.gamenames = gamenames
        self.games_var = self._createGamesVar(frame, row)

        #
        row += 1
        self._calcToolkit().Label(
            frame, text=_('Preset:'), anchor='w').grid(
            row=row, column=0, sticky='ew', padx=2, pady=2)
        presets = app.opt.solver_presets
        self.presets = presets
        self.preset_var = self._createPresetVar(frame, row)
        self.preset_var.set(self.app.opt.solver_preset)

        #
        row += 1
        self.max_iters_var = tkinter.IntVar()
        self.max_iters_var.set(self.app.opt.solver_max_iterations)
        self._calcToolkit().Label(
            frame, text=_('Max iterations:'), anchor='w').grid(
            row=row, column=0, sticky='ew', padx=2, pady=2)
        spin = PysolSpinbox(frame, from_=1000, to=10e6,
                            increment=1000, textvariable=self.max_iters_var,
                            fieldname=_('Max iterations:'))
        self.max_iters_var.trace('w', self._OnAssignToMaxIters)
        spin.grid(row=row, column=1, sticky='w', padx=2, pady=2)

        #
        row += 1
        self.progress_var = tkinter.BooleanVar()
        self.progress_var.set(self.app.opt.solver_show_progress)
        w = self._createShowProgressButton(frame)
        w.grid(row=row, column=0, columnspan=2, sticky='ew', padx=2, pady=2)
        w.config(command=self._ToggleShowProgressButton)

        #
        label_frame = self._calcToolkit().LabelFrame(
            top_frame, text=_('Progress'))
        label_frame.pack(expand=True, fill='both', padx=6, pady=2)
        # label_frame.columnconfigure(0, weight=1)
        label_frame.columnconfigure(1, weight=1)

        #
        frow = 0
        self._calcToolkit().Label(
            label_frame, text=_('Iteration:'), anchor='w').grid(
            row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = self._calcToolkit().Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.iter_label = lb
        frow += 1
        self._calcToolkit().Label(
            label_frame, text=_('Depth:'), anchor='w').grid(
            row=frow, column=0, sticky='ew', padx=4, pady=2)
        lb = self._calcToolkit().Label(label_frame, anchor='w')
        lb.grid(row=frow, column=1, sticky='ew', padx=4, pady=2)
        self.depth_label = lb
        frow += 1
        self._calcToolkit().Label(
            label_frame, text=_('Stored-States:'), anchor='w').grid(
            row=frow, column=0, sticky='ew', padx=4, pady=2)
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

    def _reset(self):
        self.play_button.config(state='disabled')
        self.setText(iter='', depth='', states='')
        self.result_label['text'] = ''
        self.top.update_idletasks()

    def reset(self):
        self.play_button.config(state='disabled')

    def startSolving(self):
        from pysollib.mygettext import ungettext

        self._reset()
        game = self.app.game
        solver = game.Solver_Class(game, self)  # create solver instance
        game.solver = solver
        preset = self.preset_var.get()
        max_iters = self._getMaxIters()
        progress = self.app.opt.solver_show_progress
        iters_step = self.app.opt.solver_iterations_output_step
        solver.config(preset=preset, max_iters=max_iters, progress=progress,
                      iters_step=iters_step)
        try:
            solver.computeHints()
        except RuntimeError:
            self.result_label['text'] = _('Solver not found in the PATH')
            return
        hints_len = len(solver.hints)-1
        if hints_len > 0:
            if solver.solver_state == 'intractable':
                t = ungettext('This game can be hinted in %d move.',
                              'This game can be hinted in %d moves.',
                              hints_len)
            else:
                t = ungettext('This game is solvable in %d move.',
                              'This game is solvable in %d moves.',
                              hints_len)
            t = t % hints_len
            self.result_label['text'] = t
            self.play_button.config(state='normal')
        else:
            self.result_label['text'] = \
                (_('I could not solve this game.')
                 if solver.solver_state == 'unsolved'
                 else _('Iterations count exceeded (Intractable)'))
            self.play_button.config(state='disabled')

    def startPlay(self):
        self.play_button.config(state='disabled')
        self.start_button.focus()
        if self.app.game.pause:
            self.app.menubar.mPause()
        self.app.top.tkraise()
        self.app.top.update_idletasks()
        self.app.top.update()
        self.app.top.after(200)
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


def connect_game_solver_dialog(game):
    try:
        solver_dialog.connectGame(game)
    except Exception:
        pass


def destroy_solver_dialog():
    global solver_dialog
    try:
        solver_dialog.destroy()
    except Exception:
        # traceback.print_exc()
        pass
    solver_dialog = None


def reset_solver_dialog():
    if solver_dialog:
        try:
            solver_dialog.reset()
        except Exception:
            # traceback.print_exc()
            pass
