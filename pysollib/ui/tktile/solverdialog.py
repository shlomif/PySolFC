class BaseSolverDialog:

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
        from gettext import ungettext

        self._reset()
        game = self.app.game
        solver = game.Solver_Class(game, self) # create solver instance
        game.solver = solver
        preset = self.preset_var.get()
        max_iters = self.max_iters_var.get()
        max_depth = self.max_depth_var.get()
        progress = self.progress_var.get()
        solver.config(preset=preset, max_iters=max_iters,
                      max_depth=max_depth, progress=progress)
        solver.computeHints()
        hints_len = len(solver.hints)-1
        if hints_len > 0:
            t = ungettext('This game is solveable in %d move.',
                          'This game is solveable in %d moves.',
                          hints_len) % hints_len
            self.result_label['text'] = t
            self.play_button.config(state='normal')
        else:
            self.result_label['text'] = (_('I could not solve this game.') if solver.solver_state == 'unsolved' else _('Iterations count exceeded (Intractable)'))
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
