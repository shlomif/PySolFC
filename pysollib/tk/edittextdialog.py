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

__all__ = ['EditTextDialog']

# imports
import os, sys, Tkinter

# PySol imports
from pysollib.mfxutil import destruct, kwdefault, KwStruct, Struct

# Toolkit imports
from tkwidget import MfxDialog

# /***********************************************************************
# //
# ************************************************************************/

class EditTextDialog(MfxDialog):

    def __init__(self, parent, title, text, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.text_w = Tkinter.Text(top_frame, bd=1, relief="sunken",
                                   wrap="word", width=64, height=16)
        self.text_w.pack(side='left', fill="both", expand=1)
        ###self.text_w.pack(side=Tkinter.TOP, padx=kw.padx, pady=kw.pady)
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
                      resizable=1,
                      separatorwidth=0,
                      )
        return MfxDialog.initKw(self, kw)

    def destroy(self):
        self.text = self.text_w.get("1.0", "end")
        MfxDialog.destroy(self)

    def wmDeleteWindow(self, *event):   # ignore
        pass

    def mCancel(self, *event):          # ignore <Escape>
        pass


