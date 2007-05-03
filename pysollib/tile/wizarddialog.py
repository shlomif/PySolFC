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

# Toolkit imports
from tkwidget import MfxDialog
from tkwidget import PysolScale


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
                notebook.add(frame, text=w)
                row = 0
                continue

            Label(frame, text=w.label).grid(row=row, column=0)

            if w.widget == 'entry':
                w.variable = var = StringVar()
                en = Entry(frame, textvariable=var)
                en.grid(row=row, column=1, sticky='ew')
            elif w.widget == 'menu':
                w.variable = var = StringVar()
                ##OptionMenu(frame, var, *w.values).grid(row=row, column=1)
                cb = Combobox(frame, values=tuple(w.values), textvariable=var,
                              state='readonly', width=20)
                cb.grid(row=row, column=1, sticky='ew', padx=2, pady=2)
            elif w.widget == 'spin':
                w.variable = var = IntVar()
                from_, to = w.values
                ##s = Spinbox(frame, textvariable=var, from_=from_, to=to)
                s = PysolScale(frame, from_=from_, to=to, resolution=1,
                               orient='horizontal',
                               variable=var)
                s.grid(row=row, column=1, sticky='ew')

            if w.current_value is None:
                var.set(w.default)
            else:
                var.set(w.current_value)

            row += 1


        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_('&OK'), _('&Cancel')),
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)



