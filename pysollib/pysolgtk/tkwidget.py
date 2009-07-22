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


# imports
import os, sys

import gtk
gdk = gtk.gdk

# PySol imports

# Toolkit imports
from tkutil import makeToplevel, setTransient, wm_withdraw

from pysollib.mfxutil import kwdefault, KwStruct, openURL


# ************************************************************************
# *
# ************************************************************************

class _MyDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self)
        self.connect("destroy", self.quit)
        self.connect("delete_event", self.quit)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def quit(self, *args):
        self.status = 0
        self.hide()
        self.destroy()
        gtk.main_quit()


class MfxDialog(_MyDialog):
    img = {}
    button_img = {}
    def __init__(self, parent, title='',
                 timeout=0,
                 resizable=0,
                 width=-1, height=-1,
                 text='', justify='center',
                 strings=("OK",), default=0,
                 separator=False,
                 padx=20, pady=20,
                 bitmap=None, bitmap_side='left',
                 bitmap_padx=20, bitmap_pady=20,
                 image=None, image_side='left',
                 image_padx=10, image_pady=20,
                 **kw):
        _MyDialog.__init__(self)
        self.status = 1
        self.button = -1
        self.buttons = []

        modal=True
        if modal:
            setTransient(self, parent)

        # settings
        if width > 0 or height > 0:
            self.set_size_request(width, height)
            #self.window.resize(width, height)
        self.set_title(title)
        #
        self.connect('key-press-event', self._keyPressEvent)


    def createBox(self, widget_class=gtk.HBox):
        box = widget_class(spacing=5)
        box.set_border_width(5)
        self.vbox.pack_start(box)
        box.show()
        return box, self.action_area

    createHBox = createBox

    def createVBox(self):
        return self.createBox(widget_class=gtk.VBox)

    def createTable(self):
        # FIXME
        return self.createBox(widget_class=gtk.Table)

    def createBitmaps(self, box, kw):
        if kw['bitmap']:
            stock = {"info":     gtk.STOCK_DIALOG_INFO,
                     "error":    gtk.STOCK_DIALOG_ERROR,
                     "warning":  gtk.STOCK_DIALOG_WARNING,
                     "question": gtk.STOCK_DIALOG_QUESTION} [kw['bitmap']]
            im = gtk.image_new_from_stock(stock, gtk.ICON_SIZE_DIALOG)
            box.pack_start(im)
            im.set_property('xpad', kw['bitmap_padx'])
            im.set_property('ypad', kw['bitmap_pady'])
            im.show()
        elif kw['image']:
            im = gtk.Image()
            im.set_from_pixbuf(kw['image'].pixbuf)
            if kw['image_side'] == 'left':
                box.pack_start(im)
            else:
                box.pack_end(im)
            im.set_property('xpad', kw['image_padx'])
            im.set_property('ypad', kw['image_pady'])
            im.show()

    def createButtons(self, box, kw):
        strings, default = kw['strings'], kw['default']
        for i in range(len(strings)):
            text = strings[i]
            if not text:
                continue
            if isinstance(text, (list, tuple)):
                text, index = text
            else: # str
                index = i
            text = text.replace('&', '_')
            b = gtk.Button(text)
            b.set_property('can-default', True)
            if index == default:
                b.grab_focus()
                #b.grab_default()
            b.set_data("user_data", index)
            b.connect("clicked", self.done)
            box.pack_start(b)
            b.show()
            self.buttons.append(b)

    def initKw(self, kw):
        kwdefault(kw,
                  timeout=0, resizable=0,
                  text="", justify="center",
                  strings=(_("&OK"),),
                  default=0,
                  width=0,
                  padx=20, pady=20,
                  bitmap=None, bitmap_side="left",
                  bitmap_padx=10, bitmap_pady=20,
                  image=None, image_side="left",
                  image_padx=10, image_pady=20,
                  )
##         # default to separator if more than one button
##         sw = len(kw.strings) > 1
##         kwdefault(kw.__dict__, separator=sw)
        return kw

    def done(self, button):
        self.status = 0
        self.button = button.get_data("user_data")
        self.quit()

    def _keyPressEvent(self, w, e):
        if gdk.keyval_name(e.keyval) == 'Escape':
            self.quit()


class MfxMessageDialog(MfxDialog):
    def __init__(self, parent, title, **kw):
        ##print 'MfxMessageDialog', kw
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, **kw)

        top_box, bottom_box = self.createBox()
        self.createBitmaps(top_box, kw)

        label = gtk.Label(kw['text'])
        label.set_justify(gtk.JUSTIFY_CENTER)
        label.set_property('xpad', kw['padx'])
        label.set_property('ypad', kw['pady'])
        top_box.pack_start(label)

        self.createButtons(bottom_box, kw)

        label.show()
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        ##self.set_position(gtk.WIN_POS_CENTER)

        self.show_all()
        gtk.main()

    def initKw(self, kw):
        #if kw.has_key('bitmap'):
        #    kwdefault(kw, width=250, height=150)
        return MfxDialog.initKw(self, kw)


# ************************************************************************
# *
# ************************************************************************

class PysolAboutDialog(MfxDialog):
    def __init__(self, app, parent, title, **kw):
        self._url = kw['url']
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, **kw)

        top_box, bottom_box = self.createBox()
        self.createBitmaps(top_box, kw)

        box = gtk.VBox()
        box.set_property('border-width', 20)
        top_box.pack_start(box)

        label = gtk.Label(kw['text'])
        label.set_justify(gtk.JUSTIFY_CENTER)
        box.pack_start(label)

        url_label = gtk.Label()
        url_label.set_justify(gtk.JUSTIFY_CENTER)
        url_label.set_markup(
            '<span foreground="blue" underline="single">%s</span>' % kw['url'])

        event_box = gtk.EventBox()
        box.pack_start(event_box)
        event_box.connect('button-press-event', self._urlClicked)
        event_box.add(url_label)

        self.createButtons(bottom_box, kw)

        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        ##self.set_position(gtk.WIN_POS_CENTER)

        self.show_all()
        event_box.window.set_cursor(gdk.Cursor(gdk.HAND2))
        gtk.main()

    def initKw(self, kw):
        #if kw.has_key('bitmap'):
        #    kwdefault(kw, width=250, height=150)
        return MfxDialog.initKw(self, kw)

    def _urlClicked(self, *args):
        openURL(self._url)


# ************************************************************************
# *
# ************************************************************************

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
        MfxDialog.__init__(self, parent, title, **kw.__dict__)


# ************************************************************************
# *
# ************************************************************************

class MfxSimpleEntry(_MyDialog):
    def __init__(self, parent, title, label, value, resizable=0, **kw):
        _MyDialog.__init__(self)
        self.button = 0
        self.status = 1
        self.value = value
        self.init(parent, label, True)
        self.entry.set_text(str(value))
        self.set_title(title)
        self.show()
        gtk.main()

    def init(self, parent,  message="", modal=True):
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
        button.connect("clicked", self.done)
        button.set_flags(gtk.CAN_DEFAULT)
        self.action_area.pack_start(button)
        button.show()
        button.grab_default()
        button = gtk.Button("Cancel")
        button.connect("clicked", self.quit)
        button.set_flags(gtk.CAN_DEFAULT)
        self.action_area.pack_start(button)
        button.show()

    def done(self, button):
        self.status = 0
        self.value = self.entry.get_text()
        self.quit()


        



class SelectDialogTreeData:
    pass

