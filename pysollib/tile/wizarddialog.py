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

__all__ = ['WizardDialog']


# imports
import Tkinter
import ttk

# PySol imports
from pysollib.mfxutil import KwStruct
from pysollib.wizardutil import WizardWidgets
from pysollib.wizardpresets import presets

# Toolkit imports
from tkwidget import MfxDialog
from tkwidget import PysolScale, PysolCombo


# ************************************************************************
# *
# ************************************************************************

class WizardDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = ttk.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        notebook = ttk.Notebook(frame)
        notebook.pack(expand=True, fill='both')

        for w in WizardWidgets:
            if isinstance(w, basestring):
                frame = ttk.Frame(notebook)
                notebook.add(frame, text=w, sticky='nsew', padding=5)
                frame.columnconfigure(1, weight=1)
                row = 0
                continue

            ttk.Label(frame, text=w.label).grid(row=row, column=0)

            if w.widget == 'preset':
                if w.variable is None:
                    w.variable = Tkinter.StringVar()
                values = [_(v) for v in w.values]
                default = _(w.default)
                values.remove(default)
                values.sort()
                values.insert(0, default)
                callback = lambda e, w=w: self.presetSelected(e, w)
                cb = PysolCombo(frame, values=tuple(values),
                                textvariable=w.variable,
                                exportselection=False,
                                selectcommand=callback,
                                state='readonly', width=32)
                cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            elif w.widget == 'entry':
                if w.variable is None:
                    w.variable = Tkinter.StringVar()
                en = ttk.Entry(frame, textvariable=w.variable)
                en.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            elif w.widget == 'menu':
                if w.variable is None:
                    w.variable = Tkinter.StringVar()
                values = [_(v) for v in w.values]
                cb = PysolCombo(frame, values=tuple(values),
                                textvariable=w.variable,
                                exportselection=False,
                                state='readonly', width=32)
                cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            elif w.widget == 'spin':
                if w.variable is None:
                    w.variable = Tkinter.IntVar()
                else:
                    # delete all trace callbacks
                    for mod, cbname in w.variable.trace_vinfo():
                        w.variable.trace_vdelete(mod, cbname)
                from_, to = w.values
                ##s = Spinbox(frame, textvariable=w.variable, from_=from_, to=to)
                s = PysolScale(frame, from_=from_, to=to, resolution=1,
                               orient='horizontal',
                               variable=w.variable)
                s.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            elif w.widget == 'check':
                if w.variable is None:
                    w.variable = Tkinter.BooleanVar()
                ch = ttk.Checkbutton(frame, variable=w.variable,
                                     takefocus=False)
                ch.grid(row=row, column=1, sticky='ew', padx=2, pady=2)

            if w.current_value is None:
                v = w.default
            else:
                v = w.current_value
            if w.widget in ('menu', 'preset'):
                v = _(v)
            w.variable.set(v)

            row += 1

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


    def presetSelected(self, e, w):
        n = e.widget.get()
        n = w.translation_map[n]
        p = presets[n]
        for w in WizardWidgets:
            if isinstance(w, basestring):
                continue
            if w.var_name in p:
                v = p[w.var_name]
            else:
                v = w.default
            if w.widget in ('menu', 'preset', 'entry'):
                v = _(v)
            w.variable.set(v)


    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_('&OK'), _('&Cancel')),
                      default=0,
                      separator=False,
                      )
        return MfxDialog.initKw(self, kw)



