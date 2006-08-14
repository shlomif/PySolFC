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
import sys, os, string, time, types

import gtk
from gtk import gdk
TRUE, FALSE = True, False



# /***********************************************************************
# // window util
# ************************************************************************/

def wm_withdraw(window):
    ##window.unmap()
    pass

def wm_deiconify(window):
    window.show_all()

def wm_map(window, maximized=None):
    window.show_all()

def wm_set_icon(window, icon):
    pass

def makeToplevel(parent, title=None, class_=None, gtkclass=gtk.Window):
    window = gtkclass()
    ##~ window.style = window.get_style().copy()
    ##~ window.set_style(window.style)
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


# /***********************************************************************
# // conversion util
# ************************************************************************/

def anchor_tk2gtk(anchor):
    if type(anchor) is types.IntType:
        assert 0 <= anchor <= 8
        return anchor
    if type(anchor) is types.StringType:
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


# /***********************************************************************
# // image util
# ************************************************************************/



class _PysolPixmap:
    def __init__(self, file=None):
        if file:
            self.pixbuf = gdk.pixbuf_new_from_file(file)
        else:
            self.pixbuf = gdk.Pixbuf()

    def clone(self):
        return self.pixbuf.copy()

    def width(self):
        return self.pixbuf.get_width()

    def height(self):
        return self.pixbuf.get_height()

    def subsample(self, x, y=None):
        ## FIXME
        return None


def loadImage(file):
    return _PysolPixmap(file=file)

def copyImage(image, x, y, width, height):
    return image

def createImage(width, height, fill, outline=None):
    return _PysolPixmap()


# /***********************************************************************
# // event wrapper
# // this really sucks, need something better...
# ************************************************************************/

def _wrap_b1_press(e):
    return e.type == gdk.BUTTON_PRESS and e.button == 1

def _wrap_b2_press(e):
    return e.type == gdk.BUTTON_PRESS and e.button == 2

def _wrap_b3_press(e):
    return e.type == gdk.BUTTON_PRESS and e.button == 3

def _wrap_b1_motion(e):
    return e.type == gdk.MOTION_NOTIFY and (e.state & gdk.BUTTON_PRESS_MASK)

def _wrap_b1_release(e):
    return e.type == gdk.BUTTON_RELEASE and e.button == 1

def _wrap_key_press(e, key):
    return e.type == gdk.KEY_PRESS and e.key == key


_wrap_handlers = {
    '<1>':                      _wrap_b1_press,
    '<ButtonPress-1>':          _wrap_b1_press,
    '<2>':                      _wrap_b2_press,
    '<ButtonPress-2>':          _wrap_b2_press,
    '<3>':                      _wrap_b3_press,
    '<ButtonPress-3>':          _wrap_b3_press,
    '<Motion>':                 _wrap_b1_motion,
    '<ButtonRelease-1>':        _wrap_b1_release,
}
for c in " " + string.letters:
    seq = "<" + c + ">"
    if not _wrap_handlers.has_key(seq):
        _wrap_handlers[seq] = lambda e, key=c: _wrap_key_press(e, key)
#print _wrap_handlers



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
    # HACK for MfxCanvasItem
    if hasattr(widget, '_item'):
        widget = widget._item
    #
    k = id(widget)
    if __bindings.has_key(k):
        __bindings[k].append((wrap, func))
    else:
        l = [(wrap, func)]
        widget.connect('event', _wrap_event, l)
        __bindings[k] = l


def unbind_destroy(widget):
    k = id(widget)
    if __bindings.has_key(k):
        ## FIXME
        del __bindings[k]


# /***********************************************************************
# // timer wrapper
# ************************************************************************/

def after(widget, ms, func, *args):
    ## FIXME
    return None

def after_idle(widget, func, *args):
    ## FIXME
    return None

def after_cancel(t):
    if t is not None:
        ## FIXME
        pass


# /***********************************************************************
# // font
# ************************************************************************/

getFont_cache = {}

def getFont(name, cardw=0):
    key = (name, cardw)
    font = getFont_cache.get(key)
    if font:
        return font
    # default
    ### FIXME
    font = "Helvetica-14"
    font = "-adobe-helvetica-medium-r-normal--*-100-*-*-*-*-*-*"
    getFont_cache[key] = font
    return font


def getTextWidth(text, font=None, root=None):
    return 10
