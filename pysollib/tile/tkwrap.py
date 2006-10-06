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

__all__ = ['TclError',
           'MfxCheckMenuItem',
           'MfxRadioMenuItem',
           'StringVar',
           'MfxRoot']

# imports
import os, sys, time, types
from Tkinter import TclError
import Tile as Tkinter

# PySol imports
from pysollib.mfxutil import destruct, Struct
from tkutil import after_idle
from tkconst import EVENT_HANDLED, EVENT_PROPAGATE

# /***********************************************************************
# // menubar
# ************************************************************************/

class MfxCheckMenuItem(Tkinter.BooleanVar):
    def __init__(self, menubar, path=None):
        Tkinter.BooleanVar.__init__(self)
    def set(self, value):
        if not value or value == "false": value = 0
        ##print value, type(value)
        ##assert type(value) is types.IntType and 0 <= value <= 1
        Tkinter.BooleanVar.set(self, value)


class MfxRadioMenuItem(Tkinter.IntVar):
    def __init__(self, menubar, path=None):
        Tkinter.IntVar.__init__(self)
    def set(self, value):
        ##assert type(value) is types.IntType and 0 <= value
        Tkinter.IntVar.set(self, value)


## BooleanVar = Tkinter.BooleanVar
## IntVar = Tkinter.IntVar

StringVar = Tkinter.StringVar


# /***********************************************************************
# // Wrapper class for Tk.
# // Required so that a Game will get properly destroyed.
# ************************************************************************/

class MfxRoot(Tkinter.Tk):
    def __init__(self, **kw):
        apply(Tkinter.Tk.__init__, (self,), kw)
##         self.tk.call("package", "require", "tile")
##         from pysollib.settings import TILE_THEME
##         if TILE_THEME:
##             ##self.tk.call('style', 'theme', 'use', TILE_THEME)
##             style = Tkinter.Style(self)
##             style.theme_use(TILE_THEME)
        self.app = None
        # for interruptible sleep
        #self.sleep_var = Tkinter.IntVar(self)
        #self.sleep_var.set(0)
        self.sleep_var = 0
        self.after_id = None
        ##self.bind('<ButtonPress>', self._sleepEvent, add=True)

    def connectApp(self, app):
        self.app = app

    # sometimes an update() is needed under Windows, whereas
    # under Unix an update_idletasks() would be enough...
    def busyUpdate(self):
        game = None
        if self.app: game = self.app.game
        if not game:
            self.update()
        else:
            old_busy = game.busy
            game.busy = 1
            if game.canvas:
                game.canvas.update()
            self.update()
            game.busy = old_busy

    def mainquit(self):
        self.after_idle(self.quit)

    def screenshot(self, filename):
        ##print 'MfxRoot.screenshot not yet implemented'
        pass

    def setCursor(self, cursor):
        if 0:
            ## FIXME: this causes ugly resizes !
            Tkinter.Tk.config(self, cursor=cursor)
        elif 0:
            ## and this is even worse
            ##print self.children
            for v in self.children.values():
                v.config(cursor=cursor)
        else:
            pass

    #
    # sleep
    #

    def sleep(self, seconds):
        #time.sleep(seconds)
        self.after(int(seconds*1000))
        return
        print 'sleep', seconds
        timeout = int(seconds*1000)
        self.sleep_var = 0
        while timeout > 0:
            self.update()
            self.update_idletasks()
            if self.sleep_var:
                break
            self.after(100)
            timeout -= 100
        print 'finish sleep'
        return
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(int(seconds*1000), self._sleepEvent)
        self.sleep_var.set(1)
        self.update()
        self.wait_variable(self.sleep_var)
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        print 'finish sleep'

    def _sleepEvent(self, *args):
        return
        print '_sleepEvent', args
        self.interruptSleep()
        return EVENT_PROPAGATE

    def interruptSleep(self):
        return
        print 'interruptSleep'
        self.update()
        self.update_idletasks()
        self.sleep_var = 1
        #self.sleep_var.set(0)
        #self.after_idle(self.sleep_var.set, 0)

    #
    #
    #

    def update(self):
        Tkinter.Tk.update(self)

    def wmDeleteWindow(self):
        if self.app and self.app.menubar:
            self.app.menubar.mQuit()
        else:
            ##self.after_idle(self.quit)
            pass
