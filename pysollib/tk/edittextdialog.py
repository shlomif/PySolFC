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

__all__ = ['EditTextDialog']

# imports
import Tkinter

# PySol imports
from pysollib.mfxutil import KwStruct

# Toolkit imports
from tkwidget import MfxDialog

# ************************************************************************
# *
# ************************************************************************

class EditTextDialog(MfxDialog):

    def __init__(self, parent, title, text, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.text_w = Tkinter.Text(top_frame, bd=1, relief="sunken",
                                   wrap="word", width=64, height=16)
        self.text_w.pack(side='left', fill="both", expand=True)
        ###self.text_w.pack(side='top', padx=kw.padx, pady=kw.pady)
        vbar = Tkinter.Scrollbar(top_frame)
        vbar.pack(side='right', fill='y')
        self.text_w["yscrollcommand"] = vbar.set
        vbar["command"] = self.text_w.yview
        #
        self.text = ""
        if text:
            self.text = text
            old_state = self.text_w["state"]
            self.text_w.config(state="normal")
            self.text_w.insert("insert", self.text)
            self.text_w.config(state=old_state)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.text_w
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")),
                      default=-1,
                      resizable=True,
                      separator=False,
                      )
        return MfxDialog.initKw(self, kw)

    def destroy(self):
        self.text = self.text_w.get("1.0", "end")
        MfxDialog.destroy(self)

    def wmDeleteWindow(self, *event):   # ignore
        pass

    def mCancel(self, *event):          # ignore <Escape>
        pass


