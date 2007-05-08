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

__all__ = ['WizardDialog']


# imports
from Tile import *

# PySol imports
from pysollib.mfxutil import destruct, kwdefault, KwStruct, Struct
from pysollib.wizardutil import WizardWidgets
from pysollib.wizardpresets import presets

# Toolkit imports
from tkwidget import MfxDialog
from tkwidget import PysolScale


gettext = _

# /***********************************************************************
# //
# ************************************************************************/

class WizardDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        notebook = Notebook(frame)
        notebook.pack(expand=True, fill='both')

        for w in WizardWidgets:
            if isinstance(w, basestring):
                frame = Frame(notebook)
                notebook.add(frame, text=w, sticky='nsew', padding=5)
                frame.columnconfigure(1, weight=1)
                row = 0
                continue

            Label(frame, text=w.label).grid(row=row, column=0)

            if w.widget == 'preset':
                if w.variable is None:
                    w.variable = StringVar()
                values = [gettext(v) for v in w.values]
                default = gettext(w.default)
                values.remove(default)
                values.sort()
                values.insert(0, default)
                cb = Combobox(frame, values=tuple(values),
                              textvariable=w.variable,
                              state='readonly', width=32)
                cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
                callback = lambda e, w=w: self.presetSelected(e, w)
                cb.bind('<<ComboboxSelected>>', callback)
            elif w.widget == 'entry':
                if w.variable is None:
                    w.variable = StringVar()
                en = Entry(frame, textvariable=w.variable)
                en.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            elif w.widget == 'menu':
                if w.variable is None:
                    w.variable = StringVar()
                values = [gettext(v) for v in w.values]
                cb = Combobox(frame, values=tuple(values),
                              textvariable=w.variable,
                              state='readonly', width=32)
                cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            elif w.widget == 'spin':
                if w.variable is None:
                    w.variable = IntVar()
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
                    w.variable = BooleanVar()
                ch = Checkbutton(frame, variable=w.variable, takefocus=False)
                ch.grid(row=row, column=1, sticky='ew', padx=2, pady=2)

            if w.current_value is None:
                w.variable.set(gettext(w.default))
            else:
                w.variable.set(gettext(w.current_value))

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
            if w.widget in ('menu', 'preset'):
                v = gettext(v)
            w.variable.set(v)


    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_('&OK'), _('&Cancel')),
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)



