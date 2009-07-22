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
import ttk

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
        self.top.config(cursor="watch")
        #
        self.frame = ttk.Frame(self.top, relief='flat', borderwidth=0)
        self.progress = ttk.Progressbar(self.frame, maximum=100, length=250)
        ##style = ttk.Style(self.progress)
        ##style.configure('TProgressbar', background=color)
        if images:
            self.f1 = ttk.Label(self.frame, image=images[0])
            self.f1.pack(side='left', ipadx=8, ipady=4)
            self.progress.pack(side='left', expand=True, fill='x')
            self.f2 = ttk.Label(self.frame, image=images[1])
            self.f2.pack(side='left', ipadx=8, ipady=4)
        else:
            self.progress.pack(expand=True, fill='x')
        self.frame.pack(expand=True, fill='both')
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
        self.progress.config(value=self.percent)
        ##self.top.update_idletasks()
        self.top.update()


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


