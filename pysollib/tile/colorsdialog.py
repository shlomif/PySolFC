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

__all__ = ['ColorsDialog']

# imports
import Tkinter
import ttk
from tkColorChooser import askcolor

# PySol imports
from pysollib.mfxutil import KwStruct

# Toolkit imports
from tkwidget import MfxDialog

# ************************************************************************
# *
# ************************************************************************

class ColorsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = ttk.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        self.text_var = Tkinter.StringVar()
        self.text_var.set(app.opt.colors['text'])
        self.piles_var = Tkinter.StringVar()
        self.piles_var.set(app.opt.colors['piles'])
        self.cards_1_var = Tkinter.StringVar()
        self.cards_1_var.set(app.opt.colors['cards_1'])
        self.cards_2_var = Tkinter.StringVar()
        self.cards_2_var.set(app.opt.colors['cards_2'])
        self.samerank_1_var = Tkinter.StringVar()
        self.samerank_1_var.set(app.opt.colors['samerank_1'])
        self.samerank_2_var = Tkinter.StringVar()
        self.samerank_2_var.set(app.opt.colors['samerank_2'])
        self.hintarrow_var = Tkinter.StringVar()
        self.hintarrow_var.set(app.opt.colors['hintarrow'])
        self.not_matching_var = Tkinter.StringVar()
        self.not_matching_var.set(app.opt.colors['not_matching'])
        #
        row = 0
        for title, var in (
            (_('Text foreground:'),        self.text_var),
            (_('Highlight piles:'),        self.piles_var),
            (_('Highlight cards 1:'),      self.cards_1_var),
            (_('Highlight cards 2:'),      self.cards_2_var),
            (_('Highlight same rank 1:'),  self.samerank_1_var),
            (_('Highlight same rank 2:'),  self.samerank_2_var),
            (_('Hint arrow:'),             self.hintarrow_var),
            (_('Highlight not matching:'), self.not_matching_var),
            ):
            ttk.Label(frame, text=title, anchor='w',
                      ).grid(row=row, column=0, sticky='we')
            l = Tkinter.Label(frame, width=10, height=2,
                              bg=var.get(), textvariable=var)
            l.grid(row=row, column=1, padx=5)
            b = ttk.Button(frame, text=_('Change...'), width=10,
                           command=lambda l=l: self.selectColor(l))
            b.grid(row=row, column=2)
            row += 1
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)
        #
        self.text_color = self.text_var.get()
        self.piles_color = self.piles_var.get()
        self.cards_1_color = self.cards_1_var.get()
        self.cards_2_color = self.cards_2_var.get()
        self.samerank_1_color = self.samerank_1_var.get()
        self.samerank_2_color = self.samerank_2_var.get()
        self.hintarrow_color = self.hintarrow_var.get()
        self.not_matching_color = self.not_matching_var.get()

    def selectColor(self, label):
        try:
            c = askcolor(parent=self.top, initialcolor=label.cget('bg'),
                         title=_("Select color"))
        except:
            pass
        else:
            if c and c[1]:
                label.configure(bg=c[1])
                #label.configure(text=c[1]) # don't work
                label.setvar(label.cget('textvariable'), c[1])

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")),
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)




