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

import gtk
from gtk import gdk
import gnome.canvas
TRUE, FALSE = True, False

# toolkit imports
from tkutil import anchor_tk2gtk, loadImage, bind

# /***********************************************************************
# // canvas items
# //
# // My first (obvious) approach was to subclass the GnomeCanvas*
# // classes, but this didn't work at all...
# //
# // Now I've resorted to delegation, but what are the Gnome canvas item
# // classes for then ?
# ************************************************************************/

class _CanvasItem:
    def __init__(self, canvas):
        self.canvas = canvas
    def addtag(self, group):
        ##~ assert isinstance(group._item, CanvasGroup)
        self._item.reparent(group._item)
    def bind(self, sequence, func, add=None):
        bind(self._item, sequence, func, add)
    def bbox(self):
        ## FIXME
        return (0, 0, 0, 0)
    def dtag(self, group):
        ##~ assert isinstance(group._item, CanvasGroup)
        self._item.reparent(self.canvas.root())
    def delete(self):
        if self._item is not None:
            self._item.destroy()
            self._item = None
    def hide(self):
        self._item.hide()
    def lower(self, positions=None):
        ##print "lower", self._item, positions
        if positions is None:
            self._item.lower_to_bottom()
        else:
            ##~ assert type(positions) is types.IntType and positions > 0
            ##~ self._item.lower(positions)
            pass
    def move(self, x, y):
        self._item.move(x, y)
    def show(self):
        self._item.show()
    def tkraise(self, positions=None):
        ##print "tkraise", self._item, positions
        if positions is None:
            self._item.raise_to_top()
        else:
            ##~ assert type(positions) is types.IntType and positions > 0
            ##~ self._item.raise_(positions)
            pass


class MfxCanvasGroup(_CanvasItem):
    def __init__(self, canvas):
        _CanvasItem.__init__(self, canvas)
        self._item = canvas.root().add(gnome.canvas.CanvasGroup, x=0, y=0)



class MfxCanvasImage(_CanvasItem):
    def __init__(self, canvas, x, y, image, anchor=gtk.ANCHOR_NW):
        _CanvasItem.__init__(self, canvas)
        anchor = anchor_tk2gtk(anchor)
        self._item = canvas.root().add(gnome.canvas.CanvasPixbuf,
                                       x=x, y=y,
                                       pixbuf=image.pixbuf,
                                       width=image.width(),
                                       height=image.height(),
                                       anchor=anchor)

    def config(self, image):
        ##~ assert isinstance(image.im, GdkImlib.Image)
        self._item.set(pixbuf=image.pixbuf)


class MfxCanvasLine(_CanvasItem):
    def __init__(self, canvas, x1, y1, x2, y2, width, fill, arrow, arrowshape):
        _CanvasItem.__init__(self, canvas)
        # FIXME
        self._item = None


class MfxCanvasRectangle(_CanvasItem):
    def __init__(self, canvas, x1, y1, x2, y2, width, fill, outline):
        self._item = canvas.root().add('rect', x1=x1, y1=y1, x2=x2, y2=y2,
                                       width_pixels=width, outline_color=outline)
        if fill is not None:
            self._item.set(fill_color=fill)


class MfxCanvasText(_CanvasItem):
    def __init__(self, canvas, x, y, anchor=gtk.ANCHOR_NW, preview=-1, **kw):
        if preview < 0:
            preview = canvas.preview
        if preview > 1:
            return
        anchor = anchor_tk2gtk(anchor)
        self._item = canvas.root().add(gnome.canvas.CanvasText,
                                       x=x, y=y, anchor=anchor)
        if not kw.has_key('fill'):
            kw['fill'] = canvas._text_color
        for k, v in kw.items():
            self[k] = v
        self.text_format = None
        canvas._text_items.append(self)

    def __setitem__(self, key, value):
        if key == 'fill':
            self._item.set(fill_color=value)
        elif key == 'font':
            self._item.set(font=value)
        elif key == 'text':
            self._item.set(text=value)
        else:
            raise AttributeError, key

    def config(self, **kw):
        for k, v in kw.items():
            self[k] = v

    def __getitem__(self, key):
        if key == 'text':
            # FIXME
            return ""
        else:
            raise AttributeError, key
    cget = __getitem__


# /***********************************************************************
# // canvas
# ************************************************************************/

class MfxCanvas(gnome.canvas.Canvas):
    def __init__(self, top, bg=None, highlightthickness=0):
        self.preview = 0
        # Tkinter compat
        self.items = {}
        # private
        self.__tileimage = None
        self.__tiles = []
        # friend MfxCanvasText
        self._text_color = '#000000'
        self._text_items = []
        #
        gnome.canvas.Canvas.__init__(self)
        self.style = self.get_style().copy()
        if bg is not None:
            c = self.get_colormap().alloc(bg)
            self.style.bg[gtk.STATE_NORMAL] = c
        self.set_style(self.style)
        self.set_scroll_region(0, 0, gdk.screen_width(), gdk.screen_height())
        top.vbox.pack_start(self)
        ##
        self.top = top
        self.xmargin, self.ymargin = 0, 0

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def bind(self, sequence=None, func=None, add=None):
        assert add is None
        # FIXME
        print "TkCanvas bind:", sequence
        return

    def cget(self, attr):
        if attr == 'cursor':
            # FIXME
            return gdk.LEFT_PTR
            return self.get_window().get_cursor(v)
        print "TkCanvas cget:", attr
        raise AttributeError, attr

    def configure(self, **kw):
        height, width = -1, -1
        for k, v in kw.items():
            if k == "background" or k == "bg":
                print 'configure: bg:', v
                c = self.get_colormap().alloc_color(v)
                self.style.bg[gtk.STATE_NORMAL] = c
                ##~ self.set_style(self.style)
                self.queue_draw()
            elif k == "cursor":
                ##~ w = self.window
                ##~ if w:
                ##~     w.set_cursor(cursor_new(v))
                pass
            elif k == "height":
                height = v
            elif k == "width":
                width = v
            else:
                print "TkCanvas", k, v
                raise AttributeError, k
        if height > 0 and width > 0:
            self.set_size_request(width, height)
            #self.queue_draw()
            #self.queue_resize()
            #self.show()
            #pass

    config = configure

    # PySol extension
    # delete all CanvasItems, but keep the background and top tiles
    def deleteAllItems(self):
        ## FIXME
        pass

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
                item.set(fill_color=_self.text_color)

    # PySol extension - set a tiled background image
    def setTile(self, app, i, force=False):
        ##print 'setTile'
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
            if i == app.tabletile_index and tile.color == app.opt.table_color:
                return False
        #
        if not self._setTile(tile.filename, tile.stretch):
            tile.error = True
            return False

        if i == 0:
            self.configure(bg=tile.color)
            ##app.top.config(bg=tile.color)
            color = None
        else:
            self.configure(bg=app.top_bg)
            ##app.top.config(bg=app.top_bg)
            color = tile.text_color

        if app.opt.table_text_color:
            self.setTextColor(app.opt.table_text_color_value)
        else:
            self.setTextColor(color)

        return True


    ### FIXME: should use style.bg_pixmap ????
    def _setTile(self, image, stretch=False):
        try:
            if image and type(image) is types.StringType:
                image = loadImage(image)
        except:
             return 0
        for item in self.__tiles:
            item.destroy()
        self.__tiles = []
        # must keep a reference to the image, otherwise Python will
        # garbage collect it...
        self.__tileimage = image
        if image is None:
            return 1
        iw, ih = image.width(), image.height()
        sw = max(self.winfo_screenwidth(), 1024)
        sh = max(self.winfo_screenheight(), 768)
        for x in range(0, sw - 1, iw):
            for y in range(0, sh - 1, ih):
                item = self.root().add('image', x=x, y=y, width=iw, height=ih,
                                       image=image.im._im,
                                       anchor=gtk.ANCHOR_NW)
                item.lower_to_bottom()
                self.__tiles.append(item)
        return 1

    def setTopImage(self, image, cw=0, ch=0):
        ## FIXME
        pass

    def update_idletasks(self):
        self.update_now()

    def grid(self, *args, **kw):
        pass

    def setInitialSize(self, width, height):
        self.set_size_request(width, height)
        if self.window:
            self.window.resize(width, height)



