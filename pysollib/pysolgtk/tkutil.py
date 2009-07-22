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
import sys, os, string, time

import gobject
import pango, gtk
from gtk import gdk


# ************************************************************************
# * window util
# ************************************************************************

def wm_withdraw(window):
    window.hide()

def wm_deiconify(window):
    window.present()

def wm_map(window, maximized=None):
    window.show()

def makeToplevel(parent, title=None, class_=None, gtkclass=gtk.Window):
    window = gtkclass()
    if not hasattr(window, 'table'):
        window.table = gtk.Table(1, 4, False)
        window.table.show()
        window.add(window.table)
    window.realize()        # needed for set_icon_name()
    if title:
        window.set_title(title)
        ##~ window.set_icon_name(title)
    if class_:
        ## window.set_wmclass(???)      ## FIXME
        pass
    return window


def setTransient(window, parent, relx=0.5, rely=0.3, expose=1):
    window.realize()
    ##~ grab_add(window)
    if parent:
        window.set_transient_for(parent)
    if expose:
        #window.unmap()          # Become visible at the desired location
        pass


# ************************************************************************
# * conversion util
# ************************************************************************

def anchor_tk2gtk(anchor):
    if isinstance(anchor, int):
        assert 0 <= anchor <= 8
        return anchor
    if isinstance(anchor, str):
        a = ['center', 'n', 'nw', 'ne', 's', 'sw', 'se', 'w', 'e']
        return a.index(string.lower(anchor))
    assert 0


def color_tk2gtk(col):
    r = string.atoi(col[1:3], 16) / 255.0
    g = string.atoi(col[3:5], 16) / 255.0
    b = string.atoi(col[5:7], 16) / 255.0
    return (r, g, b, 1.0)


def color_gtk2tk(col):
    r = int(round(col[0] * 255.0))
    g = int(round(col[1] * 255.0))
    b = int(round(col[2] * 255.0))
    return "#%02x%02x%02x" % (r, g, b)


# ************************************************************************
# * image util
# ************************************************************************


class _PysolPixmap:
    def __init__(self, file=None, pixbuf=None, width=0, height=0,
                 fill=None, outline=None):
        if file:
            self.pixbuf = gdk.pixbuf_new_from_file(file)
        elif pixbuf:
            self.pixbuf = pixbuf
        else:
            self.pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB,
                                     True, 8, width, height)
            if fill:
                c = gdk.color_parse(fill)
                c = '%02x%02x%02xffL' % (c.red, c.green, c.blue)
                self.pixbuf.fill(int(c, 16))
            else:
                self.pixbuf.fill(0)
            if outline:
                # FIXME
                pass
            

    def clone(self):
        pixbuf = self.pixbuf.copy()
        im = _PysolPixmap(pixbuf=pixbuf)
        return im

    def width(self):
        return self.pixbuf.get_width()

    def height(self):
        return self.pixbuf.get_height()

    def subsample(self, r):
        w, h = self.pixbuf.get_width(), self.pixbuf.get_height()
        w, h = int(float(w)/r), int(float(h)/r)
        pixbuf = self.pixbuf.scale_simple(w, h, gdk.INTERP_BILINEAR)
        im = _PysolPixmap(pixbuf=pixbuf)
        return im


def loadImage(file):
    return _PysolPixmap(file=file)

def copyImage(image, x, y, width, height):
    # FIXME
    return image.clone()

def createImage(width, height, fill, outline=None):
    # FIXME
    return _PysolPixmap(width=width, height=height, fill=fill, outline=outline)

def shadowImage(image):
    # FIXME
    return None

def markImage(image):
    # FIXME
    return image


# ************************************************************************
# * event wrapper
# * this really sucks, need something better...
# ************************************************************************

def _wrap_b1_press(e):
    return (e.type == gdk.BUTTON_PRESS and e.button == 1 and
            not (e.state & gdk.CONTROL_MASK) and
            not (e.state & gdk.SHIFT_MASK))

def _wrap_b1_double(e):
    return e.type == gdk._2BUTTON_PRESS and e.button == 1

def _wrap_b1_control(e):
    return e.type == gdk.BUTTON_PRESS and e.button == 1 and (e.state & gdk.CONTROL_MASK)

def _wrap_b1_shift(e):
    return e.type == gdk.BUTTON_PRESS and e.button == 1 and (e.state & gdk.SHIFT_MASK)

def _wrap_b2_press(e):
    return e.type == gdk.BUTTON_PRESS and e.button == 2

def _wrap_b3_press(e):
    return (e.type == gdk.BUTTON_PRESS and e.button == 3 and
            not (e.state & gdk.CONTROL_MASK) and
            not (e.state & gdk.SHIFT_MASK))

def _wrap_b3_control(e):
    return e.type == gdk.BUTTON_PRESS and e.button == 3 and (e.state & gdk.CONTROL_MASK)

def _wrap_b1_motion(e):
    return e.type == gdk.MOTION_NOTIFY and (e.state & gdk.BUTTON_PRESS_MASK)

def _wrap_b1_release(e):
    return e.type == gdk.BUTTON_RELEASE and e.button == 1

def _wrap_key_press(e, key):
    return e.type == gdk.KEY_PRESS and e.key == key

def _wrap_enter(e):
    return e.type == gdk.ENTER_NOTIFY

def _wrap_leave(e):
    return e.type == gdk.LEAVE_NOTIFY

_wrap_handlers = {
    '<1>':                  (_wrap_b1_press,   'button-press-event'),
    '<ButtonPress-1>':      (_wrap_b1_press,   'button-press-event'),
    '<Double-1>':           (_wrap_b1_double,  'button-press-event'),
    '<Control-1>':          (_wrap_b1_control, 'button-press-event'),
    '<Shift-1>':            (_wrap_b1_shift,   'button-press-event'),
    '<2>':                  (_wrap_b2_press,   'button-press-event'),
    '<ButtonPress-2>':      (_wrap_b2_press,   'button-press-event'),
    '<3>':                  (_wrap_b3_press,   'button-press-event'),
    '<ButtonPress-3>':      (_wrap_b3_press,   'button-press-event'),
    '<Control-3>':          (_wrap_b3_control, 'button-press-event'),
    '<Motion>':             (_wrap_b1_motion,  'motion-notify-event'),
    '<ButtonRelease-1>':    (_wrap_b1_release, 'button-release-event'),
    '<Enter>':              (_wrap_enter,      'enter-notify-event'),
    '<Leave>':              (_wrap_leave,      'leave-notify-event'),
}
## for c in " " + string.letters:
##     seq = "<" + c + ">"
##     if not _wrap_handlers.has_key(seq):
##         _wrap_handlers[seq] = lambda e, key=c: _wrap_key_press(e, key)
## import pprint; pprint.pprint(_wrap_handlers)

## NOT BOUND: <Unmap>


__bindings = {}

def _wrap_event(widget, event, l):
    for wrap, func in l:
        if wrap(event):
            #print "event:", wrap, func, event
            return func(event)
    return 0


def bind(widget, sequence, func, add=None):
    wrap = _wrap_handlers.get(sequence)
    if not wrap:
        ##print "NOT BOUND:", sequence
        return
    wrap, signal = wrap
    #
    k = id(widget)
    if k in __bindings:
        __bindings[k].append((wrap, func))
    else:
        l = [(wrap, func)]
        widget.connect(signal, _wrap_event, l)
        __bindings[k] = l


def unbind_destroy(widget):
    k = id(widget)
    if k in __bindings:
        ## FIXME
        del __bindings[k]


# ************************************************************************
# * timer wrapper
# ************************************************************************

def after(widget, ms, func, *args):
    timer = gobject.timeout_add(ms, func, *args)
    return timer

def after_idle(widget, func, *args):
    gobject.idle_add(func, *args)
    return None

def after_cancel(t):
    if t is not None:
        gobject.source_remove(t)


# ************************************************************************
# * font
# ************************************************************************

def create_pango_font_desc(font):
    font_desc = pango.FontDescription(font[0]+' '+str(font[1]))
    if 'italic' in font:
        font_desc.set_style(pango.STYLE_ITALIC)
    if 'bold' in font:
        font_desc.set_weight(pango.WEIGHT_BOLD)
    return font_desc


def get_text_width(text, font=None, root=None):
    if root:
        pango_font_desc = create_pango_font_desc(font)
        pangolayout = root.create_pango_layout(text)
        width = pangolayout.get_pixel_extents()[1][2]
        return width
    return 0

