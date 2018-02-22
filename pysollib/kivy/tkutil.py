#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------#

# kivy implementation:
# most of the code will not be used, but some important function have been
# emulated.

from __future__ import division

'''
__all__ = ['wm_withdraw',
           'wm_map',
           'setTransient',
           'makeToplevel',
           'make_help_toplevel',
           'bind',
           'unbind_destroy',
           'after',
           'after_idle',
           'after_cancel',
           # 'makeImage',
           'copyImage',
           'loadImage',
           # 'fillImage',
           'createImage',
           'shadowImage',
           'markImage',
           'createBottom',
           'get_text_width',
           ]
'''

# imports
import logging
from array import array

# PySol imports
# from pysollib.mfxutil import Image
from pysollib.kivy.LApp import LTopLevel0
from pysollib.kivy.LApp import LImage

# Kivy imports
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.graphics.texture import Texture

# ************************************************************************
# * window manager util
# ************************************************************************


def wm_withdraw(window):
    window.wm_withdraw()


def wm_map(window, maximized=0):
    return

# ************************************************************************
# * window util
# ************************************************************************


def setTransient(window, parent, relx=None, rely=None, expose=1):
    # Make an existing toplevel window transient for a parent.
    #
    # The window must exist but should not yet have been placed; in
    # other words, this should be called after creating all the
    # subwidget but before letting the user interact.

    # not used in kivy (highly tk specific).
    return


def makeToplevel(parent, title=None):
    print('tkutil: makeTopLevel')

    # Create a Toplevel window.
    #
    window = LTopLevel0(parent, title)
    # window = LTopLevelPopup(parent, title)
    return window.content


def make_help_toplevel(app, title=None):
    # Create an independent Toplevel window.

    window = app.top

    # from pysollib.winsystems import init_root_window
    # window = Tkinter.Tk(className=TITLE)
    # init_root_window(window, app)
    return window

# ************************************************************************
# * bind wrapper - Tkinter doesn't properly delete all bindings
# ************************************************************************


__mfx_bindings = {}
__mfx_wm_protocols = ("WM_DELETE_WINDOW", "WM_TAKE_FOCUS", "WM_SAVE_YOURSELF")


def bind(widget, sequence, func, add=None):

    # logging.info('tkutil: bind  %s %s %s %s '
    #              % (widget, sequence, func, add))

    # logging.info('tkutil: bind canvas = ' % str(widget.canvas))

    if hasattr(widget, 'bindings'):
        # logging.info('tkutil: bind  %s %s %s %s '
        #              % (sequence, widget, func, add))
        widget.bindings[sequence] = func
    else:
        # logging.info('tkutil: bind failed %s %s' % (sequence, widget))
        pass

    if (sequence == '<KeyPress-Left>'):
        return
    if (sequence == '<KeyPress-Right>'):
        return
    if (sequence == '<KeyPress-Prior>'):
        return
    if (sequence == '<KeyPress-Next>'):
        return
    if (sequence == '<KeyPress-Up>'):
        return
    if (sequence == '<KeyPress-Down>'):
        return
    if (sequence == '<KeyPress-Begin>'):
        return
    if (sequence == '<KeyPress-Home>'):
        return
    if (sequence == '<KeyPress-End>'):
        return
    if (sequence == '<KeyPress-Down>'):
        return

    if (sequence == '<4>'):
        return
    if (sequence == '<5>'):
        return

    if (sequence == '<1>'):
        return
    if (sequence == '<Motion>'):
        return
    if (sequence == '<ButtonRelease-1>'):
        return
    if (sequence == '<Control-1>'):
        return
    if (sequence == '<Shift-1>'):
        return
    if (sequence == '<Double-1>'):
        return
    if (sequence == '<3>'):
        return
    if (sequence == '<2>'):
        return
    if (sequence == '<Control-3>'):
        return
    if (sequence == '<Enter>'):
        return
    if (sequence == '<Leave>'):
        return
    if (sequence == '<Unmap>'):
        return
    if (sequence == '<Configure>'):
        return
    pass


def unbind_destroy(widget):
    # logging.info('tkutil: unbind  %s' % (widget))
    widget.bindings = []
    pass

# ************************************************************************
# * timer wrapper - Tkinter doesn't properly delete all commands
# ************************************************************************


def after(widget, ms, func, *args):
    print('tkutil: after(%s, %s, %s, %s)' % (widget, ms, func, args))
    if (ms == 'idle'):
        print('demo use')
        Clock.schedule_once(lambda dt: func(), 1.0)
    elif (isinstance(ms, int)):
        # print('ms: play timer (accounting)')
        # Clock.schedule_once(lambda dt: func(), float(ms)/1000.0)
        # makes not sense, drains battery!
        pass


def after_idle(widget, func, *args):
    print('tkutil: after_idle()')
    return after(widget, "idle", func, *args)


def after_cancel(t):
    print('tkutil: after_cancel()')
    pass


# ************************************************************************
# * image handling
# ************************************************************************


def makeImage(file=None, data=None, dither=None, alpha=None):
    kw = {}
    if data is None:
        assert file is not None
        kw["source"] = file
        # print('makeImage: source = %s' % file)
        # if (file=='/home/lb/PRG/Python/Kivy/pysolfc/data/images/redeal.gif'):
        #    y = self.yy
    else:
        assert data is not None
        kw["texture"] = data
        # ob das geht ?? - kommt das vor ?
        # yy = self.yy

    '''
    if 'source' in kw:
        logging.info ("makeImage: " + kw["source"])
    if 'texture' in kw:
        logging.info ("makeImage: " + str(kw["texture"]))
    '''

    return LImage(**kw)


loadImage = makeImage


def copyImage(image, x, y, width, height):

    # return Image(source=image.source)
    # return Image(texture=image.texture)
    return image


def fillTexture(texture, fill, outline=None, owidth=1):

    logging.info("fillImage: t=%s, f=%s o=%s, w=%s" %
                 (texture, fill, outline, owidth))
    # O.K. Kivy

    if not fill and not outline:
        return

    width = texture.width
    height = texture.height

    ox = round(owidth)
    ow = int(ox)    # muss int sein!
    if width <= 2 * ow or height <= 2 * ow:
        fill = fill or outline
        outline = None

    if not fill:
        fi0 = 0
        fi1 = 0
        fi2 = 0
        fi3 = 0
    else:
        # wir erwarten Werte als '#xxxxxx' (color Werte in Tk notation)
        # (optional mit transparenz)
        if (fill[0] == '#'):
            fill = fill[1:]
        fi0 = int(fill[0:2], 16)
        fi1 = int(fill[2:4], 16)
        fi2 = int(fill[4:6], 16)
        fi3 = 255
        if len(fill) >= 8:
            fi3 = int(fill[6:8], 16)

    if not outline:
        f = (fi0, fi1, fi2, fi3) * width
        f = (f, ) * height
        assert len(f) == height
        f = sum(f, ())
        assert len(f) == height * width * 4
        arr = array('B', f)
        texture.blit_buffer(arr, colorfmt='rgba', bufferfmt='ubyte')
    else:
        if (outline[0] == '#'):
            outline = outline[1:]
        ou0 = int(outline[0:2], 16)
        ou1 = int(outline[2:4], 16)
        ou2 = int(outline[4:6], 16)
        ou3 = 255
        if len(outline) >= 8:
            ou3 = int(outline[6:8], 16)

        l1 = (ou0, ou1, ou2, ou3, ) * width
        l2 = (ou0, ou1, ou2, ou3, ) * ow + (fi0, fi1, fi2, fi3, ) * \
            (width - 2 * ow) + (ou0, ou1, ou2, ou3, ) * ow
        f = (l1, ) * ow + (l2, ) * (height - 2 * ow) + (l1, ) * ow
        assert len(f) == height
        f = sum(f, ())
        assert len(f) == height * width * 4
        arr = array('B', f)
        texture.blit_buffer(arr, colorfmt='rgba', bufferfmt='ubyte')

    logging.info("fillImage: filled")


def createImage(width, height, fill, outline=None, outwidth=1):

    logging.info("createImage: w=%s, h=%s, f=%s, o=%s, ow=%s" %
                 (width, height, fill, outline, outwidth))

    # test stellungen:
    # if (fill==None):
    #   fill = '#00cc00'
    # if (outline==None):
    #   outline = '#ff00ff'
    if (fill is None and (outline is None or outline == '')):
        outline = '#fff000'
        outwidth = 1

    texture = Texture.create(size=(width, height), colorfmt='rgba')
    fillTexture(texture, fill, outline, outwidth)
    image = LImage(texture=texture)
    logging.info("createImage: LImage create %s" % image)
    return image


def shadowImage(image, color='#3896f8', factor=0.3):

    logging.info("shadowImage: ")
    # TBD.
    return None
    # Kivy nicht benötigt. aber - was tut das ?
    # wurde aufgerufen, als der erste König auf die Foundation
    # gezogen wurde. (möglicherweise eine Gewonnen! - Markierung).


def markImage(image):
    logging.info("markImage: ")
    return None


def createBottom(image, color='white', backfile=None):

    logging.info("createBottom: ")
    # TBD.
    # y = self.yy

    if not hasattr(image, '_pil_image'):
        return None

    # obviously not used.
    return None
    '''
    im = image._pil_image
    th = 1                              # thickness
    sh = Image.new('RGBA', im.size, color)
    out = Image.composite(sh, im, im)
    w, h = im.size
    size = (w - th * 2, h - th * 2)
    tmp = Image.new('RGBA', size, color)
    tmp.putalpha(60)
    mask = out.resize(size, Image.ANTIALIAS)
    out.paste(tmp, (th, th), mask)
    if backfile:
        back = Image.open(backfile).convert('RGBA')
        w0, h0 = back.size
        w1, h1 = im.size
        a = min(float(w1) / w0, float(h1) / h0)
        a = a * 0.9
        w0, h0 = int(w0 * a), int(h0 * a)
        back = back.resize((w0, h0), Image.ANTIALIAS)
        x, y = (w1 - w0) / 2, (h1 - h0) / 2
        out.paste(back, (x, y), back)
    return PIL_Image(image=out)
    '''

# ************************************************************************
# * font utils
# ************************************************************************


def get_text_width(text, font, root=None):

    logging.info("get_text_width: %s  %s" % (text, font))

    label = CoreLabel()
    label.text = text
    label.refresh()
    return label.content_width
    # return Font(root=root, font=font).measure(text)
