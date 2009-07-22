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

__all__ = ['TimeoutsDialog']

# imports
import Tkinter

# PySol imports
from pysollib.mfxutil import KwStruct

# Toolkit imports
from tkwidget import MfxDialog

# ************************************************************************
# *
# ************************************************************************

class TimeoutsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        #self.createBitmaps(top_frame, kw)

        frame = Tkinter.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        self.demo_sleep_var = Tkinter.DoubleVar()
        self.demo_sleep_var.set(app.opt.timeouts['demo'])
        self.hint_sleep_var = Tkinter.DoubleVar()
        self.hint_sleep_var.set(app.opt.timeouts['hint'])
        self.raise_card_sleep_var = Tkinter.DoubleVar()
        self.raise_card_sleep_var.set(app.opt.timeouts['raise_card'])
        self.highlight_piles_sleep_var = Tkinter.DoubleVar()
        self.highlight_piles_sleep_var.set(app.opt.timeouts['highlight_piles'])
        self.highlight_cards_sleep_var = Tkinter.DoubleVar()
        self.highlight_cards_sleep_var.set(app.opt.timeouts['highlight_cards'])
        self.highlight_samerank_sleep_var = Tkinter.DoubleVar()
        self.highlight_samerank_sleep_var.set(app.opt.timeouts['highlight_samerank'])
        #
        #Tkinter.Label(frame, text='Set delays in seconds').grid(row=0, column=0, columnspan=2)
        row = 0
        for title, var in ((_('Demo:'), self.demo_sleep_var),
                           (_('Hint:'), self.hint_sleep_var),
                           (_('Raise card:'), self.raise_card_sleep_var),
                           (_('Highlight piles:'), self.highlight_piles_sleep_var),
                           (_('Highlight cards:'), self.highlight_cards_sleep_var),
                           (_('Highlight same rank:'), self.highlight_samerank_sleep_var),
                           ):
            Tkinter.Label(frame, text=title, anchor='w'
                          ).grid(row=row, column=0, sticky='we')
            widget = Tkinter.Scale(frame, from_=0.2, to=9.9,
                                   resolution=0.1, orient='horizontal',
                                   length="3i", variable=var, takefocus=0)
            widget.grid(row=row, column=1)
            row += 1
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)
        #
        self.demo_timeout = self.demo_sleep_var.get()
        self.hint_timeout = self.hint_sleep_var.get()
        self.raise_card_timeout = self.raise_card_sleep_var.get()
        self.highlight_piles_timeout = self.highlight_piles_sleep_var.get()
        self.highlight_cards_timeout = self.highlight_cards_sleep_var.get()
        self.highlight_samerank_timeout = self.highlight_samerank_sleep_var.get()

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")), default=0,
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)




