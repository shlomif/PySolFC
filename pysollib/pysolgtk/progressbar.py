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
from gtk import gdk

# Toolkit imports
from tkutil import makeToplevel, setTransient


# ************************************************************************
# * a simple progress bar
# ************************************************************************

class PysolProgressBar:
    def __init__(self, app, parent, title=None, images=None,
                 color='blue', bg='#c0c0c0',
                 height=25, show_text=1, norm=1):
        self.parent = parent
        self.percent = 0
        self.steps_sum = 0
        self.norm = norm
        self.top = makeToplevel(parent, title=title)
        self.top.set_position(gtk.WIN_POS_CENTER)
        self.top.set_resizable(False)
        self.top.connect("delete_event", self.wmDeleteWindow)

        # hbox
        hbox = gtk.HBox(spacing=5)
        hbox.set_border_width(10)
        hbox.show()
        self.top.table.attach(hbox,
                              0, 1, 0, 1,
                              0,    0,
                              0,    0)
        # hbox-1: image
        if images and images[0]:
            im = gtk.Image()
            im.set_from_pixbuf(images[0].pixbuf)
            hbox.pack_start(im, expand=False, fill=False)
            im.show()
            im.set_property('xpad', 10)
            im.set_property('ypad', 5)
        # hbox-2:vbox
        vbox = gtk.VBox()
        vbox.show()
        hbox.pack_start(vbox, False, False)
        # hbox-2:vbox:pbar
        self.pbar = gtk.ProgressBar()
        self.pbar.show()
        vbox.pack_start(self.pbar, True, False)
        self.pbar.realize()
        ##~ self.pbar.set_show_text(show_text)
        self.pbar.set_text(str(show_text)+'%')
        w, h = self.pbar.size_request()
        self.pbar.set_size_request(max(w, 300), max(h, height))
        # hbox-3:image
        if images and images[1]:
            im = gtk.Image()
            im.set_from_pixbuf(images[1].pixbuf)
            hbox.pack_end(im, expand=False)
            im.show()
            im.set_property('xpad', 10)
            im.set_property('ypad', 5)
        # set icon
##         if app:
##             try:
##                 name = app.dataloader.findFile('pysol.xpm')
##                 bg = self.top.get_style().bg[gtk.STATE_NORMAL]
##                 pixmap, mask = create_pixmap_from_xpm(self.top, bg, name)
##                 self.top.set_icon(pixmap, mask)
##             except: pass
        setTransient(self.top, parent)
        self.top.show()
        self.top.window.set_cursor(gdk.Cursor(gdk.WATCH))
        self.update(percent=0)

    def destroy(self):
        self.top.destroy()

    def pack(self):
        pass

    def update(self, percent=None, step=1):
        ##self.steps_sum += step
        ##print self.steps_sum, self.norm
        step = step/self.norm
        if percent is None:
            self.percent += step
        elif percent > self.percent:
            self.percent = percent
        percent = int(self.percent)
        percent = min(100, max(0, percent))
        self.pbar.set_fraction(percent / 100.0)
        self.pbar.set_text(str(percent)+'%')
        self.update_idletasks()

    def reset(self, percent=0):
        self.percent = percent

    def update_idletasks(self):
        while gtk.events_pending():
            gtk.main_iteration()

    def wmDeleteWindow(self, *args):
        return True


# ************************************************************************
# *
# ************************************************************************

#%ifndef BUNDLE

class TestProgressBar:
    def __init__(self, parent, images=None):
        self.parent = parent
        self.progress = PysolProgressBar(None, parent, title="Progress",
                                         images=images, color='#008200')
        self.progress.pack()
        self.func = [ self.update, 0 ]
        self.func[1] = timeout_add(30, self.func[0])

    def update(self, *args):
        if self.progress.percent >= 100:
            self.progress.destroy()
            mainquit()
            return False
        self.progress.update(step=1)
        return True

def progressbar_main(args):
    root = gtk.Window()
    root.connect("destroy", mainquit)
    root.connect("delete_event", mainquit)
    images = None
    if 1:
        from tkwrap import loadImage
        im = loadImage(os.path.join(os.pardir, os.pardir, 'data', 'images', 'jokers', 'joker07_40_774.gif'))
        images = (im, im)
    pb = TestProgressBar(root, images=images)
    main()
    return 0

if __name__ == '__main__':
    sys.exit(progressbar_main(sys.argv))

#%endif

