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

__all__ = ['TclError',
           'MfxRoot']

# imports
import Tkinter
TclError = Tkinter.TclError

# PySol imports
from tkconst import EVENT_PROPAGATE


# ************************************************************************
# * Wrapper class for Tk.
# * Required so that a Game will get properly destroyed.
# ************************************************************************

class MfxRoot(Tkinter.Tk):
    def __init__(self, **kw):
        Tkinter.Tk.__init__(self, **kw)
        self.app = None
        self.wm_protocol('WM_DELETE_WINDOW', self.wmDeleteWindow)
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
