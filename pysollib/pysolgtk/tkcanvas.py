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


#
# This files tries to wrap a limited subset of the Tkinter canvas
# into GTK / Gnome.
#

#
# Some background information:
#
#   - Each card is a canvas group consisting of a background and foreground
#     image. Turning a card raises the respective image within that group.
#
#   - Each stack is a canvas group consisting of cards (i.e. a group of groups)
#
#   - Cards change stacks, and are bound to the main canvas when dragging
#     around.
#


# imports
import os, sys, types

import gobject, gtk
gdk = gtk.gdk
try:
    import gnomecanvas
except ImportError:
    import gnome.canvas as gnomecanvas

# toolkit imports
from tkutil import anchor_tk2gtk, loadImage, bind, create_pango_font_desc


# ************************************************************************
# * canvas items
# *
# * My first (obvious) approach was to subclass the GnomeCanvas*
# * classes, but this didn't work at all...
# *
# * Now I've resorted to delegation, but what are the Gnome canvas item
# * classes for then ?
# ************************************************************************

class _CanvasItem:

    def __init__(self, canvas):
        self.canvas = canvas
        canvas._all_items.append(self)
        self._is_hidden = False
        self._x, self._y = 0, 0
        self._group = None

    def addtag(self, group):
        ##print self, 'addtag'
        ##~ assert isinstance(group._item, CanvasGroup)
        self._item.reparent(group._item)
        if self._group == group:
            print 'addtag: new_group == old_group'
        self._group = group

    def dtag(self, group):
        ##print self, 'dtag'
        ##~ assert isinstance(group._item, CanvasGroup)
        ##self._item.reparent(self.canvas.root())
        pass

    def bind(self, sequence, func, add=None):
        bind(self._item, sequence, func, add)

    def bbox(self):
        ## FIXME
        return (0, 0, 0, 0)

    def delete(self):
        if self._item is not None:
            self._item.destroy()
            self._item = None

    def lower(self, positions=None):
        print 'lower', self, positions
        return # don't need?
##         if positions is None:
##             pass
##             ##self._item.lower_to_bottom()
##             ##self._item.get_property('parent').lower_to_bottom()
##         else:
##             print self, positions
##             self._item.lower(positions)

    def tkraise(self, positions=None):
        ##print 'tkraise', positions
        if positions is None:
            self._item.raise_to_top()
            self._item.get_property('parent').raise_to_top()
        else:
            #print self, 'tkraise', positions
            #self._item.raise_to_top()
            self._item.raise_to_top() #positions)

    def move(self, x, y):
        self._item.move(x, y)
        self._x, self._y = self._x+x, self._y+y

    def moveTo(self, x, y):
        self._item.move(x-self._x, y-self._y)
        self._x, self._y = x, y

    def show(self):
        if self._item:
            self._item.show()
        self._is_hidden = False
    def hide(self):
        if self._item:
            self._item.hide()
        self._is_hidden = True

    def connect(self, signal, func, args):
        #print '_CanvasItem.connect:', self, signal
        self._item.connect('event', func, args)



class MfxCanvasGroup(_CanvasItem):
    def __init__(self, canvas):
        _CanvasItem.__init__(self, canvas)
        self._item = canvas.root().add(gnomecanvas.CanvasGroup, x=0, y=0)


class MfxCanvasImage(_CanvasItem):
    def __init__(self, canvas, x, y, image, anchor=gtk.ANCHOR_NW, group=None):
        _CanvasItem.__init__(self, canvas)
        self._x, self._y = x, y
        if isinstance(anchor, str):
            anchor = anchor_tk2gtk(anchor)
        if group:
            self._group = group
            group = group._item
        else:
            group = canvas.root()
        self._item = group.add(gnomecanvas.CanvasPixbuf,
                               x=x, y=y,
                               pixbuf=image.pixbuf,
                               width=image.width(),
                               height=image.height(),
                               anchor=anchor)
        self._item.show()

    def config(self, image):
        ##~ assert isinstance(image.im, GdkImlib.Image)
        self._item.set(pixbuf=image.pixbuf)


class MfxCanvasLine(_CanvasItem):
    def __init__(self, canvas, *points, **kw):
        _CanvasItem.__init__(self, canvas)
        kwargs = {}
        if 'arrow' in kw:
            if kw['arrow'] == 'first':
                kwargs['first_arrowhead'] = True
            elif kw['arrow'] == 'last':
                kwargs['last_arrowhead'] = True
            elif kw['arrow'] == 'both':
                kwargs['first_arrowhead'] = True
                kwargs['last_arrowhead'] = True
        if 'fill' in kw:
            kwargs['fill_color'] = kw['fill']
        if 'width' in kw:
            kwargs['width_units'] = float(kw['width'])
        if 'arrowshape' in kw:
            kwargs['arrow_shape_a'] = kw['arrowshape'][0]
            kwargs['arrow_shape_b'] = kw['arrowshape'][1]
            kwargs['arrow_shape_c'] = kw['arrowshape'][2]
        if 'group' in kw:
            self._group = kw['group']
            group = kw['group']._item
        else:
            group = canvas.root()
        self._item = group.add(gnomecanvas.CanvasLine,
                               points=points, **kwargs)
        self._item.show()


class MfxCanvasRectangle(_CanvasItem):
    def __init__(self, canvas, x1, y1, x2, y2,
                 width=0, fill=None, outline=None, group=None):
        _CanvasItem.__init__(self, canvas)
        self._x, self._y = x1, y1
        kw = {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2}
        if width:   kw['width_pixels']  = width
        if fill:    kw['fill_color']    = fill
        if outline: kw['outline_color'] = outline
        if group:
            self._group = group
            group = group._item
        else:
            group = canvas.root()
        self._item = group.add(gnomecanvas.CanvasRect, **kw)
        self._item.show()


class MfxCanvasText(_CanvasItem):
    def __init__(self, canvas, x, y, anchor=gtk.ANCHOR_NW, preview=-1, **kw):
        _CanvasItem.__init__(self, canvas)
        self._x, self._y = x, y
        if preview < 0:
            preview = canvas.preview
        if preview > 1:
            self._item = None
            return
        anchor = anchor_tk2gtk(anchor)
        if 'group' in kw:
            self._group = kw['group']
            group = kw['group']._item
            del kw['group']
        else:
            group = canvas.root()
        self._item = group.add(gnomecanvas.CanvasText,
                               x=x, y=y, anchor=anchor)
        if 'fill' not in kw:
            kw['fill'] = canvas._text_color
        for k, v in kw.items():
            self[k] = v
        ##~ self.text_format = None
        canvas._text_items.append(self)
        self._item.show()

    def __setitem__(self, key, value):
        if key == 'fill':
            self._item.set(fill_color=value)
        elif key == 'font':
            ##print 'set font:', value
            font_desc = create_pango_font_desc(value)
            self._item.set(font_desc=font_desc)
        elif key == 'text':
            self._item.set(text=value)
        else:
            raise AttributeError, key

    def config(self, **kw):
        for k, v in kw.items():
            self[k] = v

    def __getitem__(self, key):
        if key == 'text':
            return self._item.get_property('text')
        else:
            raise AttributeError, key
    cget = __getitem__


# ************************************************************************
# * canvas
# ************************************************************************

class MfxCanvas(gnomecanvas.Canvas):
    def __init__(self, top, bg=None, highlightthickness=0):
        self.preview = 0
        # Tkinter compat
        self.items = {}
        self._all_items = []
        self._text_items = []
        self._hidden_items = []
        self._width, self._height = -1, -1
        self._tile = None
        # private
        self.__tileimage = None
        self.__tiles = []
        self.__topimage = None
        # friend MfxCanvasText
        self._text_color = '#000000'
        #
        gnomecanvas.Canvas.__init__(self)
        c = top.style.bg[gtk.STATE_NORMAL]
        c = '#%02x%02x%02x' % (c.red/256, c.green/256, c.blue/256)
        self.top_bg = c
        if bg is not None:
            self.modify_bg(gtk.STATE_NORMAL, gdk.color_parse(bg))

        #
        self.top = top
        self.xmargin, self.ymargin = 0, 0

        self.connect('size-allocate', self._sizeAllocate)
        ##self.connect('destroy', self.destroyEvent)


    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def _sizeAllocate(self, w, rect):
        ##print '_sizeAllocate', rect.x, rect.y, rect.width, rect.height
        if self._width > 0:
            w = self._width
            h = min(self._height, rect.height)
            self.set_scroll_region(0,0,w,h)
        if self._tile and self._tile.filename:
            self._setTile()

    def bind(self, sequence=None, func=None, add=None):
        assert add is None
        # FIXME
        print 'TkCanvas bind:', sequence
        return

    def cget(self, attr):
        if attr == 'cursor':
            # FIXME
            return gdk.LEFT_PTR
            return self.get_window().get_cursor(v)
        elif attr == 'width':
            return self.get_size()[0]
        elif attr == 'height':
            return self.get_size()[1]
        print 'TkCanvas cget:', attr
        raise AttributeError, attr

    def xview(self):
        w, h = self.get_size()
        dx, dy = self.world_to_window(0, 0)
        return -float(dx)/w, 1.0
    def yview(self):
        w, h = self.get_size()
        dx, dy = self.world_to_window(0, 0)
        return -float(dy)/h, 1.0

    def winfo_width(self):
        return self.get_size()[0]
    def winfo_height(self):
        return self.get_size()[1]

    def configure(self, **kw):
        height, width = -1, -1
        for k, v in kw.items():
            if k in ('background', 'bg'):
                self.modify_bg(gtk.STATE_NORMAL, gdk.color_parse(v))
            elif k == 'cursor':
                if not self.window:
                    self.realize()
                if v == '':
                    v = gdk.LEFT_PTR
                self.window.set_cursor(gdk.Cursor(v))
            elif k == 'height':
                height = v
            elif k == 'width':
                width = v
            else:
                print 'TkCanvas', k, v
                raise AttributeError, k
        if height > 0 and width > 0:
            self.set_size_request(width, height)

    config = configure

    # PySol extension
    # delete all CanvasItems, but keep the background and top tiles
    def deleteAllItems(self):
        for i in self._all_items:
            if i._item:
                i._item.destroy()
            ##i._item = None
        self._all_items = []

    def hideAllItems(self):
        self._hidden_items = []
        for i in self._all_items:
            if not i._is_hidden:
                i.hide()
                self._hidden_items.append(i)

    def showAllItems(self):
        for i in self._hidden_items:
            i.show()
        self._hidden_items = []

    # PySol extension
    def findCard(self, stack, event):
        # FIXME
        ##w = self.get_item_at(event.x, event.y)
        ##print w
        return stack._findCardXY(event.x, event.y)

    def pack(self, **kw):
        self.show()

    # PySol extension
    def setTextColor(self, color):
        if self._text_color != color:
            self._text_color = color
            for item in self._text_items:
                item._item.set(fill_color=self._text_color)

    # PySol extension - set a tiled background image
    def setTile(self, app, i, force=False):
        ##print 'setTile:', i
        tile = app.tabletile_manager.get(i)
        if tile is None or tile.error:
            return False
        if i == 0:
            assert tile.color
            assert tile.filename is None
        else:
            assert tile.color is None
            assert tile.filename
            assert tile.basename
        if not force:
            if (i == app.tabletile_index and
                tile.color == app.opt.colors['table']):
                return False
            if self._tile is tile:
                return False
        #
        self._tile = tile
        if i == 0:
            self.setBackgroundImage(None)
            self.configure(bg=tile.color)
            ##app.top.config(bg=tile.color)
        else:
            self._setTile()
            self.configure(bg=self.top_bg)

        self.setTextColor(app.opt.colors['text'])

        return True


    ### FIXME: should use style.bg_pixmap ????
    def _setTile(self):
        if not self._tile:
            return
        ##print '_setTile:', self.get_size(), self._tile.filename
        #
        filename = self._tile.filename
        stretch = self._tile.stretch

        if not filename:
            return False
        if not self.window: # not realized yet
            self.realize()
            ##return False

        gobject.idle_add(self.setBackgroundImage, filename, stretch)


    def setBackgroundImage(self, filename, stretch=False):
        ##print 'setBackgroundImage', filename
        if filename is None:
            if self.__tileimage:
                self.__tileimage.destroy()
                self.__tileimage = None
            return

        width, height = self.get_size()
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        w, h = pixbuf.get_width(), pixbuf.get_height()
        dx, dy = self.world_to_window(0, 0)
        dx, dy = int(dx), int(dy)

        if self.__tileimage:
            self.__tileimage.destroy()
            self.__tileimage = None

        if stretch:
            bg_pixbuf = pixbuf.scale_simple(width, height, gdk.INTERP_BILINEAR)
        else:
            bg_pixbuf = gdk.Pixbuf(pixbuf.get_colorspace(),
                                   pixbuf.get_has_alpha(),
                                   pixbuf.get_bits_per_sample(),
                                   width, height)
            y = 0
            while y < height:
                x = 0
                while x < width:
                    ww = min(w, width-x)
                    hh = min(h, height-y)
                    pixbuf.copy_area(0, 0, ww, hh, bg_pixbuf, x, y)
                    x += w
                y += h

        w = self.root().add(gnomecanvas.CanvasPixbuf,
                            pixbuf=bg_pixbuf, x=0-dx, y=0-dy)
        w.lower_to_bottom()
        self.__tileimage = w


    def setTopImage(self, image, cw=0, ch=0):
        if self.__topimage:
            self.__topimage.destroy()
            self.__topimage = None
        if not image:
            return
        if isinstance(image, str):
            pixbuf = gtk.gdk.pixbuf_new_from_file(image)
        else:
            pixbuf = image.pixbuf
        w, h = self.get_size()
        iw, ih = pixbuf.get_width(), pixbuf.get_height()
        x, y = (w-iw)/2, (h-ih)/2
        dx, dy = self.world_to_window(0, 0)
        dx, dy = int(dx), int(dy)
        self.__topimage = self.root().add(gnomecanvas.CanvasPixbuf,
                                          pixbuf=pixbuf, x=x-dx, y=y-dy)


    def update_idletasks(self):
        ##print 'MfxCanvas.update_idletasks'
        #gdk.window_process_all_updates()
        #self.show_now()
        # FIXME
        ##if self.__topimage:
        ##    self.__topimage.raise_to_top()
        self.update_now()
        pass

    def updateAll(self):
        print 'Canvas - updateAll', 
        for i in self._all_items:
            i._item.hide()
        self.update_now()
        n = 0
        for i in self._all_items:
            i._item.show()
            print n, i
            n += 1
        self.update_now()
        #self.window.invalidate_rect((0, 0, 400, 400), True)


    def grid(self, *args, **kw):
        self.top.table.attach(self,
            1, 2,                   2, 3,
            gtk.EXPAND | gtk.FILL,  gtk.EXPAND | gtk.FILL | gtk.SHRINK,
            0,                      0)
        self.show()


    def setInitialSize(self, width, height):
        ##print 'setInitialSize:', width, height
        self._width, self._height = width, height
        self.set_size_request(width, height)
        #self.set_size(width, height)
        #self.queue_resize()


    def destroyEvent(self, w):
        #print 'MfxCanvas.destroyEvent'
        self.hide()
##         self.deleteAllItems()
##         if self.__topimage:
##             self.__topimage.destroy()
##             self.__topimage = None



class MfxScrolledCanvas(MfxCanvas):
    def __init__(self, parent, hbar=2, vbar=2, **kw):
        MfxCanvas.__init__(self, parent)
        self.canvas = self


