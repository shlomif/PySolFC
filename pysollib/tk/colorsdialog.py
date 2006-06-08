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

__all__ = ['ColorsDialog']

# imports
import os, sys
from Tkinter import *
from tkColorChooser import askcolor

# PySol imports
from pysollib.mfxutil import destruct, kwdefault, KwStruct, Struct

# Toolkit imports
from tkconst import EVENT_HANDLED, EVENT_PROPAGATE
from tkwidget import MfxDialog

# /***********************************************************************
# //
# ************************************************************************/

class ColorsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = Frame(top_frame)
        frame.pack(expand=YES, fill=BOTH, padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        self.table_text_color_var = BooleanVar()
        self.table_text_color_var.set(app.opt.table_text_color)
        self.table_text_color_value_var = StringVar()
        self.table_text_color_value_var.set(app.opt.table_text_color_value)
        ##self.table_color_var = StringVar()
        ##self.table_color_var.set(app.opt.table_color)
        self.highlight_piles_colors_var = StringVar()
        self.highlight_piles_colors_var.set(app.opt.highlight_piles_colors[1])
        self.highlight_cards_colors_1_var = StringVar()
        self.highlight_cards_colors_1_var.set(app.opt.highlight_cards_colors[1])
        self.highlight_cards_colors_2_var = StringVar()
        self.highlight_cards_colors_2_var.set(app.opt.highlight_cards_colors[3])
        self.highlight_samerank_colors_1_var = StringVar()
        self.highlight_samerank_colors_1_var.set(app.opt.highlight_samerank_colors[1])
        self.highlight_samerank_colors_2_var = StringVar()
        self.highlight_samerank_colors_2_var.set(app.opt.highlight_samerank_colors[3])
        self.hintarrow_color_var = StringVar()
        self.hintarrow_color_var.set(app.opt.hintarrow_color)
        self.highlight_not_matching_color_var = StringVar()
        self.highlight_not_matching_color_var.set(app.opt.highlight_not_matching_color)
        #
        c = Checkbutton(frame, variable=self.table_text_color_var,
                        text=_("Text foreground:"), anchor=W)
        c.grid(row=0, column=0, sticky=W+E)
        l = Label(frame, width=10, height=2,
                  bg=self.table_text_color_value_var.get(),
                  textvariable=self.table_text_color_value_var)
        l.grid(row=0, column=1, padx=5)
        b = Button(frame, text=_('Change...'), width=10,
                   command=lambda l=l: self.selectColor(l))
        b.grid(row=0, column=2)
        row = 1
        for title, var in (
            ##('Table:', self.table_color_var),
            (_('Highlight piles:'), self.highlight_piles_colors_var),
            (_('Highlight cards 1:'), self.highlight_cards_colors_1_var),
            (_('Highlight cards 2:'), self.highlight_cards_colors_2_var),
            (_('Highlight same rank 1:'), self.highlight_samerank_colors_1_var),
            (_('Highlight same rank 2:'), self.highlight_samerank_colors_2_var),
            (_('Hint arrow:'), self.hintarrow_color_var),
            (_('Highlight not matching:'), self.highlight_not_matching_color_var),
            ):
            Label(frame, text=title, anchor=W).grid(row=row, column=0, sticky=W+E)
            l = Label(frame, width=10, height=2,
                      bg=var.get(), textvariable=var)
            l.grid(row=row, column=1, padx=5)
            b = Button(frame, text=_('Change...'), width=10,
                       command=lambda l=l: self.selectColor(l))
            b.grid(row=row, column=2)
            row += 1
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)
        #
        self.table_text_color = self.table_text_color_var.get()
        self.table_text_color_value = self.table_text_color_value_var.get()
        ##self.table_color = self.table_color_var.get()
        self.highlight_piles_colors = (None,
                                       self.highlight_piles_colors_var.get())
        self.highlight_cards_colors = (None,
                                       self.highlight_cards_colors_1_var.get(),
                                       None,
                                       self.highlight_cards_colors_2_var.get())
        self.highlight_samerank_colors = (None,
                                          self.highlight_samerank_colors_1_var.get(),
                                          None,
                                          self.highlight_samerank_colors_2_var.get())
        self.hintarrow_color = self.hintarrow_color_var.get()
        self.highlight_not_matching_color = self.highlight_not_matching_color_var.get()

    def selectColor(self, label):
        c = askcolor(master=self.top, initialcolor=label.cget('bg'),
                     title=_("Select color"))
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




