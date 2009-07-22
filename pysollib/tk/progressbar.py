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

__all__ = ['PysolProgressBar']

# imports
import Tkinter

# Toolkit imports
from tkconst import EVENT_HANDLED
from tkutil import makeToplevel, setTransient


# ************************************************************************
# * a simple progress bar
# ************************************************************************

class PysolProgressBar:
    def __init__(self, app, parent, title=None, images=None, color="blue",
                 width=300, height=25, show_text=1, norm=1):
        self.parent = parent
        self.percent = 0
        self.top = makeToplevel(parent, title=title)
        self.top.wm_protocol("WM_DELETE_WINDOW", self.wmDeleteWindow)
        self.top.wm_group(parent)
        self.top.wm_resizable(False, False)
        self.frame = Tkinter.Frame(self.top, relief='flat', bd=0,
                                   takefocus=0)
        self.cframe = Tkinter.Frame(self.frame, relief='sunken', bd=1,
                                   takefocus=0)
        self.canvas = Tkinter.Canvas(self.cframe, width=width, height=height,
                                     takefocus=0, bd=0, highlightthickness=0)
        self.scale = self.canvas.create_rectangle(-10, -10, 0, height,
                                                  outline=color, fill=color)
        self.text = -1
        if show_text:
            self.text = self.canvas.create_text(0, 0, anchor=Tkinter.CENTER)
        self.cframe.grid_configure(column=0, row=0, sticky="ew")
        if images:
            self.f1 = Tkinter.Label(self.frame, image=images[0])
            self.f1.grid_configure(column=0, row=0, sticky="ew", ipadx=8, ipady=4)
            self.cframe.grid_configure(column=1, row=0, sticky="ew", padx=8)
            self.f2 = Tkinter.Label(self.frame, image=images[1])
            self.f2.grid_configure(column=2, row=0, sticky="ew", ipadx=8, ipady=4)
        self.top.config(cursor="watch")
        self.pack()
        if 1:
            setTransient(self.top, None, relx=0.5, rely=0.5)
        else:
            self.update(percent=0)
        self.norm = norm
        self.steps_sum = 0

    def wmDeleteWindow(self):
        return EVENT_HANDLED

    def destroy(self):
        if self.top is None:        # already destroyed
            return
        self.top.wm_withdraw()
        self.top.quit()
        self.top.destroy()
        self.top = None

    def pack(self, **kw):
        self.canvas.pack(fill=Tkinter.X, expand=False)
        self.frame.pack(**kw)

    def reset(self, percent=0):
        self.percent = percent

    def update(self, percent=None, step=1):
        self.steps_sum += step
        ##print self.steps_sum
        step = step/self.norm
        if self.top is None:        # already destroyed
            return
        if percent is None:
            self.percent = self.percent + step
        elif percent > self.percent:
            self.percent = percent
        else:
            return
        self.percent = min(100, max(0, self.percent))
        c = self.canvas
        width, height = c.winfo_reqwidth(), c.winfo_reqheight()
        c.coords(self.scale, -10, -10,
                 (self.percent * width ) / 100.0, height)
        if self.text >= 0:
            c.coords(self.text, width/2, height/2)
            c.itemconfig(self.text, text="%d %%" % int(round(self.percent)))
        c.update()


# ************************************************************************
# *
# ************************************************************************


class TestProgressBar:
    def __init__(self, parent):
        self.parent = parent
        self.progress = PysolProgressBar(None, parent, title="Progress", color="#008200")
        self.progress.pack(ipadx=10, ipady=10)
        self.progress.frame.after(1000, self.update)

    def update(self, event=None):
        if self.progress.percent >= 100:
            self.parent.after_idle(self.progress.destroy)
            return
        self.progress.update(step=1)
        self.progress.frame.after(30, self.update)

def progressbar_main(args):
    from tkutil import wm_withdraw
    tk = Tkinter.Tk()
    wm_withdraw(tk)
    pb = TestProgressBar(tk)
    tk.mainloop()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(progressbar_main(sys.argv))


