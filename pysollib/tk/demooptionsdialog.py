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

__all__ = ['DemoOptionsDialog']

# imports
import os, sys, Tkinter

# PySol imports
from pysollib.mfxutil import destruct, kwdefault, KwStruct, Struct

# Toolkit imports
from tkconst import EVENT_HANDLED, EVENT_PROPAGATE
from tkwidget import _ToplevelDialog, MfxDialog

# /***********************************************************************
# //
# ************************************************************************/

class DemoOptionsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        _ToplevelDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.demo_logo_var = Tkinter.BooleanVar()
        self.demo_logo_var.set(app.opt.demo_logo != 0)
        self.demo_score_var = Tkinter.BooleanVar()
        self.demo_score_var.set(app.opt.demo_score != 0)
        self.demo_sleep_var = Tkinter.DoubleVar()
        self.demo_sleep_var.set(app.opt.demo_sleep)
        widget = Tkinter.Checkbutton(top_frame, variable=self.demo_logo_var,
                                     text=_("Display floating Demo logo"))
        widget.pack(side=Tkinter.TOP, padx=kw.padx, pady=kw.pady)
        widget = Tkinter.Checkbutton(top_frame, variable=self.demo_score_var,
                                     text=_("Show score in statusbar"))
        widget.pack(side=Tkinter.TOP, padx=kw.padx, pady=kw.pady)
        widget = Tkinter.Scale(top_frame, from_=0.2, to=9.9,
                               resolution=0.1, orient=Tkinter.HORIZONTAL,
                               length="3i", label=_("Set demo delay in seconds"),
                               variable=self.demo_sleep_var, takefocus=0)
        widget.pack(side=Tkinter.TOP, padx=kw.padx, pady=kw.pady)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)
        #
        self.demo_logo = self.demo_logo_var.get()
        self.demo_score = self.demo_score_var.get()
        self.demo_sleep = self.demo_sleep_var.get()


    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("OK"), _("Cancel")), default=0,
                      separatorwidth = 0,
                      )
        return MfxDialog.initKw(self, kw)


# /***********************************************************************
# //
# ************************************************************************/


def demooptionsdialog_main(args):
    from tkutil import wm_withdraw
    opt = Struct(demo_logo=1, demo_sleep=1.5)
    app = Struct(opt=opt)
    tk = Tkinter.Tk()
    wm_withdraw(tk)
    tk.update()
    d = DemoOptionsDialog(tk, "Demo options", app)
    print d.status, d.button, ":", d.demo_logo, d.demo_sleep
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(demooptionsdialog_main(sys.argv))

