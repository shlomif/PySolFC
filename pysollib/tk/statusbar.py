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

__all__ = ['PysolStatusbar',
           'HelpStatusbar']

# imports
import os, sys, Tkinter

if __name__ == '__main__':
    d = os.path.abspath(os.path.join(sys.path[0], os.pardir, os.pardir))
    sys.path.append(d)
    import gettext
    gettext.install('pysol', d, unicode=True)

# PySol imports

# Toolkit imports
from tkwidget import MfxTooltip
from pysollib.settings import WIN_SYSTEM


# ************************************************************************
# *
# ************************************************************************

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
        self._label_column = 0
        #
        self.padx = 1
        self.label_relief = 'sunken'
        self.frame = Tkinter.Frame(self.top, bd=1)
        self.frame.grid(row=self._row, column=self._column,
                        columnspan=self._columnspan, sticky='ew',
                        padx=1, pady=1)
        if WIN_SYSTEM == 'win32':
            self.frame.config(relief='raised')
            self.padx = 0
        if 0:
            self.frame.config(bd=0)
            self.label_relief = 'flat'
            self.padx = 0

    # util
    def _createLabel(self, name, expand=False, width=0, tooltip=None):
        label = Tkinter.Label(self.frame, width=width,
                              relief=self.label_relief, bd=1,
                              highlightbackground='black'
                              )
        label.grid(row=0, column=self._label_column,
                   sticky='nsew', padx=self.padx)
        if expand:
            self.frame.grid_columnconfigure(self._label_column,
                                            weight=1)
        self._label_column += 1
        setattr(self, name + '_label', label)
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
            label = getattr(self, k + '_label')
            text = unicode(v)
            width = label['width']
            if width and len(text) > width:
                label['width'] = len(text)
            label['text'] = text

    def config(self, name, show):
        label = getattr(self, name + '_label')
        if show:
            label.grid()
        else:
            label.grid_remove()

    def configLabel(self, name, **kw):
        label = getattr(self, name + '_label')
        label.config(**kw)

    def show(self, show=True, resize=False):
        if self._show == show:
            return False
        if resize:
            self.top.wm_geometry('')    # cancel user-specified geometry
        if not show:
            # hide
            self.frame.grid_forget()
        else:
            # show
            self.frame.grid(row=self._row, column=self._column,
                            columnspan=self._columnspan, sticky='ew')
        self._show = show
        return True

    def hide(self, resize=False):
        self.show(False, resize)

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
            ('stuck',       _("'You Are Stuck' indicator"), 3),
            ('time',        _('Playing time'),            10),
            ('moves',       _('Moves/Total moves'),       10),
            ('gamenumber',  _('Game number'),             26),
            ('stats',       _('Games played: won/lost'),  12),
            ):
            self._createLabel(n, tooltip=t, width=w)
        #
        l = self._createLabel('info', expand=True)
        ##l.config(text='', justify='left', anchor='w')
        l.config(padx=8)


class HelpStatusbar(MfxStatusbar):
    def __init__(self, top):
        MfxStatusbar.__init__(self, top, row=4, column=0, columnspan=3)
        l = self._createLabel('info', expand=True)
        l.config(justify='left', anchor='w', padx=8)


class HtmlStatusbar(MfxStatusbar):
    def __init__(self, top, row, column, columnspan):
        MfxStatusbar.__init__(self, top, row=row, column=column, columnspan=columnspan)
        l = self._createLabel('url', expand=True)
        l.config(justify='left', anchor='w', padx=8)


# ************************************************************************
# *
# ************************************************************************


class TestStatusbar(PysolStatusbar):
    def __init__(self, top, args):
        PysolStatusbar.__init__(self, top)
        # test some settings
        self.updateText(moves=999, gamenumber='#0123456789ABCDEF0123')
        self.updateText(info='Some info text.')

def statusbar_main(args):
    tk = Tkinter.Tk()
    statusbar = TestStatusbar(tk, args)
    tk.mainloop()
    return 0

if __name__ == '__main__':
    sys.exit(statusbar_main(sys.argv))


