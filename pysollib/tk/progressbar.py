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

__all__ = ['PysolProgressBar']

# imports
import os, sys, Tkinter

# Toolkit imports
from tkconst import EVENT_HANDLED, EVENT_PROPAGATE
from tkutil import makeToplevel, setTransient, wm_set_icon


# /***********************************************************************
# // a simple progress bar
# ************************************************************************/

class PysolProgressBar:
    def __init__(self, app, parent, title=None, images=None,
                 color="blue", width=300, height=25, show_text=1):
        self.parent = parent
        self.percent = 0
        self.top = makeToplevel(parent, title=title)
        self.top.wm_protocol("WM_DELETE_WINDOW", self.wmDeleteWindow)
        self.top.wm_group(parent)
        self.top.wm_resizable(0, 0)
        self.frame = Tkinter.Frame(self.top, relief=Tkinter.FLAT, bd=0,
                                   takefocus=0)
        self.cframe = Tkinter.Frame(self.frame, relief=Tkinter.SUNKEN, bd=1,
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
        if app:
            try:
                wm_set_icon(self.top, app.dataloader.findIcon())
            except: pass
        self.pack()
        if 1:
            setTransient(self.top, None, relx=0.5, rely=0.5)
        else:
            self.update(percent=0)

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
        self.canvas.pack(fill=Tkinter.X, expand=0)
        apply(self.frame.pack, (), kw)

    def reset(self, percent=0):
        self.percent = percent

    def update(self, percent=None, step=1):
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


# /***********************************************************************
# //
# ************************************************************************/


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


