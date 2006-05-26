## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
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
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = ['PysolStatusbar',
           'HelpStatusbar']

# imports
import os, sys, Tkinter

# PySol imports
from pysollib.mfxutil import destruct

# Toolkit imports
from tkwidget import MfxTooltip

# /***********************************************************************
# //
# ************************************************************************/

class MfxStatusbar:
    def __init__(self, top, row, column, columnspan):
        self.top = top
        self._show = True
        self._widgets = []
        self._tooltips = []
        #
        self._row = row
        self._column = column
        self._columnspan = columnspan
        self.padx = 0
        self.pady = 0
        #
        self.frame = Tkinter.Frame(self.top, bd=1, relief='raised')
        self.frame.grid(row=self._row, column=self._column,
                        columnspan=self._columnspan, sticky='ew')

    # util
    def _createLabel(self, name,
                     text="", relief='sunken',
                     side='left', fill='none',
                     padx=-1, expand=0, width=0,
                     tooltip=None):
        if padx < 0: padx = self.padx
        label = Tkinter.Label(self.frame, text=text,
                              width=width, relief=relief)
        label.pack(side=side, fill=fill, padx=padx, expand=expand)
        setattr(self, name + "_label", label)
        self._widgets.append(label)
        if tooltip:
            b = MfxTooltip(label)
            self._tooltips.append(b)
            b.setText(tooltip)
        return label


    #
    # public methods
    #

    def updateText(self, **kw):
        for k, v in kw.items():
            label = getattr(self, k + "_label")
            #label["text"] = str(v)
            label["text"] = unicode(v)

    def configLabel(self, name, **kw):
        label = getattr(self, name + "_label")
        apply(label.config, (), kw)

    def show(self, show=True, resize=False):
        if self._show == show:
            return False
        if resize:
            self.top.wm_geometry("")    # cancel user-specified geometry
        if not show:
            # hide
            self.frame.grid_forget()
        else:
            # show
            self.frame.grid(row=self._row, column=self._column,
                            columnspan=self._columnspan, sticky='ew')
        self._show = show
        return True

    def hide(self, resize=0):
        self.show(None, resize)

    def destroy(self):
        for w in self._tooltips:
            if w: w.destroy()
        self._tooltips = []
        for w in self._widgets:
            if w: w.destroy()
        self._widgets = []


class PysolStatusbar(MfxStatusbar):
    def __init__(self, top):
        MfxStatusbar.__init__(self, top, row=3, column=0, columnspan=3)
        #
        for n, t, w in (
            ("time",        _("Playing time"),            10),
            ("moves",       _('Moves/Total moves'),       10),
            ("gamenumber",  _("Game number"),             26),
            ("stats",       _("Games played: won/lost"),  12),
            ):
            self._createLabel(n, tooltip=t, width=w)
        #
        l = self._createLabel("info", fill='both', expand=1)
        ##l.config(text="", justify="left", anchor='w')
        l.config(padx=8)


class HelpStatusbar(MfxStatusbar):
    def __init__(self, top):
        MfxStatusbar.__init__(self, top, row=4, column=0, columnspan=3)
        l = self._createLabel("info", fill='both', expand=1)
        l.config(text="", justify="left", anchor='w', padx=8)


class HtmlStatusbar(MfxStatusbar):
    def __init__(self, top, row, column, columnspan):
        MfxStatusbar.__init__(self, top,
                              row=row, column=column, columnspan=columnspan)
        l = self._createLabel("url", fill='both', expand=1)
        l.config(text="", justify="left", anchor='w', padx=8)


# /***********************************************************************
# //
# ************************************************************************/


class TestStatusbar(PysolStatusbar):
    def __init__(self, top, args):
        PysolStatusbar.__init__(self, top)
        # test some settings
        self.updateText(moves=999, gamenumber="#0123456789ABCDEF0123")
        self.updateText(info="Some info text.")

def statusbar_main(args):
    tk = Tkinter.Tk()
    statusbar = TestStatusbar(tk, args)
    tk.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(statusbar_main(sys.argv))


