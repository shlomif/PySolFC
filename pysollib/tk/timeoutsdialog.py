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

__all__ = ['TimeoutsDialog']

# imports
import os, sys
from Tkinter import *

# PySol imports
from pysollib.mfxutil import destruct, kwdefault, KwStruct, Struct

# Toolkit imports
from tkconst import EVENT_HANDLED, EVENT_PROPAGATE
from tkwidget import _ToplevelDialog, MfxDialog

# /***********************************************************************
# //
# ************************************************************************/

class TimeoutsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        _ToplevelDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        #self.createBitmaps(top_frame, kw)

        frame = Frame(top_frame)
        frame.pack(expand=YES, fill=BOTH, padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        self.demo_sleep_var = DoubleVar()
        self.demo_sleep_var.set(app.opt.demo_sleep)
        self.hint_sleep_var = DoubleVar()
        self.hint_sleep_var.set(app.opt.hint_sleep)
        self.raise_card_sleep_var = DoubleVar()
        self.raise_card_sleep_var.set(app.opt.raise_card_sleep)
        self.highlight_piles_sleep_var = DoubleVar()
        self.highlight_piles_sleep_var.set(app.opt.highlight_piles_sleep)
        self.highlight_cards_sleep_var = DoubleVar()
        self.highlight_cards_sleep_var.set(app.opt.highlight_cards_sleep)
        self.highlight_samerank_sleep_var = DoubleVar()
        self.highlight_samerank_sleep_var.set(app.opt.highlight_samerank_sleep)
        #
        #Label(frame, text='Set delays in seconds').grid(row=0, column=0, columnspan=2)
        row = 0
        for title, var in ((_('Demo:'), self.demo_sleep_var),
                           (_('Hint:'), self.hint_sleep_var),
                           (_('Raise card:'), self.raise_card_sleep_var),
                           (_('Highlight piles:'), self.highlight_piles_sleep_var),
                           (_('Highlight cards:'), self.highlight_cards_sleep_var),
                           (_('Highlight same rank:'), self.highlight_samerank_sleep_var),
                           ):
            Label(frame, text=title, anchor=W).grid(row=row, column=0, sticky=W+E)
            widget = Scale(frame, from_=0.2, to=9.9,
                           resolution=0.1, orient=HORIZONTAL,
                           length="3i",
                           variable=var, takefocus=0)
            widget.grid(row=row, column=1)
            row += 1
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)
        #
        self.demo_sleep = self.demo_sleep_var.get()
        self.hint_sleep = self.hint_sleep_var.get()
        self.raise_card_sleep = self.raise_card_sleep_var.get()
        self.highlight_piles_sleep = self.highlight_piles_sleep_var.get()
        self.highlight_cards_sleep = self.highlight_cards_sleep_var.get()
        self.highlight_samerank_sleep = self.highlight_samerank_sleep_var.get()

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("OK"), _("Cancel")), default=0,
                      separatorwidth=0,
                      )
        return MfxDialog.initKw(self, kw)




