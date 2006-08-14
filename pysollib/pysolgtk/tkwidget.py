## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
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
## <markus.oberhumer@jk.uni-linz.ac.at>
## http://wildsau.idv.uni-linz.ac.at/mfx/pysol.html
##
##---------------------------------------------------------------------------##


# imports
import os, sys

import gtk
TRUE, FALSE = True, False

# PySol imports

# Toolkit imports
from tkutil import makeToplevel, setTransient, wm_withdraw


# /***********************************************************************
# //
# ************************************************************************/

class _MyDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self)
        self.style = self.get_style().copy()
        self.set_style(self.style)
        self.connect("destroy", self.quit)
        self.connect("delete_event", self.quit)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def quit(self, *args):
        self.hide()
        self.destroy()
        gtk.main_quit()


class MfxDialog(_MyDialog):
    def __init__(self, parent, title='',
                 timeout=0,
                 resizable=0,
                 text='', justify='center',
                 strings=("OK",), default=0,
                 width=0, separatorwidth=0,
                 font=None,
                 buttonfont=None,
                 padx='20', pady='20',
                 bitmap=None, bitmap_side='left',
                 bitmap_padx=20, bitmap_pady=20,
                 image=None, image_side='left',
                 image_padx=10, image_pady=20):
        _MyDialog.__init__(self)
        self.status = 1
        self.button = -1
        bitmap = None
        self.init(parent, text, strings, default, bitmap, TRUE)
        #font = "Times-14"
##         if font:
##             self.style.font = load_font(font)
##             self.set_style(self.style)
        self.set_title(title)
        self.show()
        gtk.main()

    def init(self, parent, message="", buttons=(), default=-1,
             pixmap=None, modal=TRUE):
        if modal:
            setTransient(self, parent)
        hbox = gtk.HBox(spacing=5)
        hbox.set_border_width(5)
        self.vbox.pack_start(hbox)
        hbox.show()
##         if pixmap:
##             self.realize()
##             pixmap = gtk.Pixmap(self, pixmap)
##             hbox.pack_start(pixmap, expand=FALSE)
##             pixmap.show()
        label = gtk.Label(message)
        hbox.pack_start(label)
        label.show()
        for i in range(len(buttons)):
            text = buttons[i]
            b = gtk.Button(text)
            b.set_flags(gtk.CAN_DEFAULT)
            if i == default:
                b.grab_focus()
                b.grab_default()
            b.set_data("user_data", i)
            b.connect("clicked", self.click)
            self.action_area.pack_start(b)
            b.show()
        self.ret = None

    def click(self, button):
        self.status = 0
        self.button = button.get_data("user_data")
        self.quit()


MfxMessageDialog = MfxDialog


# /***********************************************************************
# //
# ************************************************************************/

class MfxExceptionDialog(MfxDialog):
    def __init__(self, parent, ex, title="Error", **kw):
        kw = KwStruct(kw, bitmap="error")
        text = str(kw.get("text", ""))
        if text and text[-1] != "\n":
            text = text + "\n"
        text = text + "\n"
        if isinstance(ex, EnvironmentError) and ex.filename is not None:
            t = '[Errno %s] %s:\n%s' % (ex.errno, ex.strerror, repr(ex.filename))
        else:
            t = str(ex)
        kw.text = text + t
        apply(MfxDialog.__init__, (self, parent, title), kw.__dict__)


# /***********************************************************************
# //
# ************************************************************************/

class MfxSimpleSlider(_MyDialog):
    def __init__(self, parent, title,
                 label, value, from_, to, resolution,
                 resizable=0):
        self.button = 0
        self.status = 1
        self.value = value


# /***********************************************************************
# //
# ************************************************************************/

class MfxSimpleEntry(_MyDialog):
    def __init__(self, parent, title, label, value, resizable=0, **kw):
        _MyDialog.__init__(self)
        self.button = 0
        self.status = 1
        self.value = value
        self.init(parent, label, TRUE)
        self.entry.set_text(str(value))
        self.set_title(title)
        self.show()
        gtk.main()

    def init(self, parent,  message="", modal=TRUE):
        if modal:
            setTransient(self, parent)
        box = gtk.VBox(spacing=10)
        box.set_border_width(10)
        self.vbox.pack_start(box)
        box.show()
        if message:
            label = gtk.Label(message)
            box.pack_start(label)
            label.show()
        self.entry = gtk.Entry()
        box.pack_start(self.entry)
        self.entry.show()
        self.entry.grab_focus()
        button = gtk.Button("OK")
        button.connect("clicked", self.click)
        button.set_flags(CAN_DEFAULT)
        self.action_area.pack_start(button)
        button.show()
        button.grab_default()
        button = gtk.Button("Cancel")
        button.connect("clicked", self.quit)
        button.set_flags(CAN_DEFAULT)
        self.action_area.pack_start(button)
        button.show()

    def click(self, button):
        self.status = 0
        self.value = self.entry.get_text()
        self.quit()


        



class SelectDialogTreeData:
    pass

