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

import logging
import os
from array import array

from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.graphics.texture import Texture

from pysollib.kivy.LApp import LTopLevel0

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


# ANM: werden ev. immer noch vom pysollib core benötigt/referenziert:
# (intern in kivy bitte nicht direkt benutzen).

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
    # print('tkutil: after(%s, %s, %s, %s)' % (widget, ms, func, args))
    if (ms == 'demo'):
        print('demo use')

        from pysollib.kivy.LApp import LAfterAnimation
        LAfterAnimation(func, 0.6)
        return

    elif (isinstance(ms, int)):
        # print('ms: play timer (accounting)')
        # Clock.schedule_once(lambda dt: func(), float(ms)/1000.0)
        # makes not sense, drains battery!
        pass


def after_idle(widget, func, *args):
    # NOTE: This is called from the core in demo mode only.
    # 'func' executes the next step in the game.
    return after(widget, "demo", func, *args)


def after_cancel(t):
    # print('tkutil: after_cancel()')
    pass


# ************************************************************************
# * image handling
# ************************************************************************
# Wrappers

LCoreImage = CoreImage  # noqa

class LImageInfo(object):   # noqa
    def __init__(self, arg):
        if type(arg) is Texture:
            self.filename = None
            self.source = None
            self.texture = arg
            self.size = self.texture.size
        if type(arg) is str:
            self.filename = arg
            self.source = arg
            self.texture = LCoreImage(arg).texture
            self.size = self.texture.size

    # pysol core needs that:

    def subsample(self, image):
        return self

    def width(self):
        return self.size[0]

    def height(self):
        return self.size[1]

    def getWidth(self):
        return self.size[0]

    def getHeight(self):
        return self.size[1]

# ************************************************************************
# Interface to core.


def makeImage(file=None, data=None, dither=None, alpha=None):
    if data is None:
        assert file is not None
        return LImageInfo(file)
    else:
        assert data is not None
        return LImageInfo(data)

loadImage = makeImage   # noqa - sorry flake8, aber das gehört zu oben dazu!


def copyImage(image, x, y, width, height):

    # wird das überhaupt aufgerufen - ja bei SubSampleImage.
    # aber: wo wird das gebraucht? - oder ist es eine altlast
    # welche gar keine Relevanz mehr hat ? (Kann auch None
    # zurückgeben, ohne dass etwas fehlt oder abstürzt).

    tregion = image.texture.get_region(x, y, width, height)
    return LImageInfo(tregion)


def fillTexture(texture, fill, outline=None, owidth=1):

    # logging.info("fillImage: t=%s, f=%s o=%s, w=%s" %
    #              (texture, fill, outline, owidth))
    # O.K. Kivy

    if not fill and not outline:
        return

    width = texture.width
    height = texture.height

    ox = round(owidth)
    ow = int(ox)  # muss int sein!
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

        l1 = (
            ou0,
            ou1,
            ou2,
            ou3,
        ) * width
        l2 = (ou0, ou1, ou2, ou3, ) * ow + (fi0, fi1, fi2, fi3, ) * \
            (width - 2 * ow) + (ou0, ou1, ou2, ou3, ) * ow
        f = (l1, ) * ow + (l2, ) * (height - 2 * ow) + (l1, ) * ow
        assert len(f) == height
        f = sum(f, ())
        assert len(f) == height * width * 4
        arr = array('B', f)
        texture.blit_buffer(arr, colorfmt='rgba', bufferfmt='ubyte')


def createImage(width, height, fill, outline=None, outwidth=1):

    logging.info("createImage: w=%s, h=%s, f=%s, o=%s, ow=%s" %
                 (width, height, fill, outline, outwidth))

    # test stellungen:
    # if (fill==None):
    #   fill = '#00cc00'
    # if (outline==None):
    #   outline = '#ff00ff'

    # if (fill is None and (outline is None or outline == '')):
    #     outline = '#fff000'
    #     outwidth = 1

    texture = Texture.create(size=(width, height), colorfmt='rgba')
    fillTexture(texture, fill, outline, outwidth)
    image = LImageInfo(texture)
    # logging.info("createImage: LImageInfo create %s" % image)
    return image


def createImagePIL(width, height, fill, outline=None, outwidth=1):
    # Is this needed for Kivy?
    createImage(width, height, fill, outline=outline, outwidth=outwidth)
    # wird nur mit USE_PIL benutzt: nicht relevant. Der code wird mit
    # Kivy nie durchlaufen.


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


def _createImageMask(texture, color):

    col = 0
    if (color == 'black'):
        col = 0
    if (color == 'white'):
        col = 255

    g = texture.pixels
    arr = array('B', g)

    for mx in range(int(len(arr) / 4)):
        m = 4 * mx
        if arr[m + 3] < 128:
            arr[m + 3] = 0
            arr[m] = arr[m + 1] = arr[m + 2] = 0
        else:
            arr[m + 3] = 32
            arr[m] = arr[m + 1] = arr[m + 2] = col

    mask = Texture.create(size=texture.size, colorfmt='rgba')
    mask.blit_buffer(arr, colorfmt='rgba', bufferfmt='ubyte')
    return mask


def _scaleTextureToSize(texture, size):

    width = size[0]
    height = size[1]

    g = texture.pixels
    ag = array('B', g)
    gw, gh = texture.size

    # print('size:',width,height)
    # print('texture size:',gw,gh)

    bb = array('B', [0 for x in range(width * height * 4)])
    # print ('bb length: ',len(bb))
    # print ('gg length: ',gw*gh*4)

    scalex = width / gw
    scaley = height / gh

    # scale, x und y offset bestimmen.

    scale = scaley
    if (scalex < scaley):
        scale = scalex

    offx = (width - gw * scale) / 2
    offy = (height - gh * scale) / 2

    # print ('scale: ',scalex,'/',scaley,' -> ',scale)
    # print ('offs: ',offx,'/',offy)

    for bi in range(height):
        bline = bi * width
        if (bi >= offy) and (bi < (height - offy)):
            # transfer
            ai = gh - int((bi - offy) / scale) - 1
            aline = ai * gw
            for bk in range(width):
                bpos = (bline + bk) * 4
                if (bk >= offx) and (bk < (width - offx)):
                    # transfer
                    ak = int((bk - offx) / scale)
                    apos = (aline + ak) * 4
                    bb[bpos] = ag[apos]
                    bb[bpos + 1] = ag[apos + 1]
                    bb[bpos + 2] = ag[apos + 2]
                    bb[bpos + 3] = ag[apos + 3]
                else:
                    # transparent
                    bb[bpos + 3] = 0
        else:
            # transparent
            for bk in range(width):
                bb[(bline + bk) * 4 + 3] = 0

    stext = Texture.create(size=(width, height), colorfmt='rgba')
    stext.blit_buffer(bb, colorfmt='rgba', bufferfmt='ubyte')
    return stext


def _pasteTextureTo(texture, totexture):

    g = texture.pixels
    ag = array('B', g)
    gw, gh = texture.size

    t = totexture.pixels
    at = array('B', t)
    tw, th = totexture.size

    if (tw != gw) or (th != gh):
        return

    for i in range(int(len(ag) / 4)):
        i4 = i * 4
        if ag[i4 + 3] > 128:
            at[i4] = ag[i4]
            at[i4 + 1] = ag[i4 + 1]
            at[i4 + 2] = ag[i4 + 2]
            at[i4 + 3] = ag[i4 + 3]

    stext = Texture.create(size=(tw, th), colorfmt='rgba')
    stext.blit_buffer(at, colorfmt='rgba', bufferfmt='ubyte')
    return stext


def createBottom(image, color='white', backfile=None):

    backfilebase = None
    if backfile is not None:
        backfilebase = os.path.basename(backfile)

    logging.info("createBottom: %s | %s" % (color, backfilebase))
    # print('createBottom:',image)

    # th = 1                              # thickness
    # size = (w - th * 2, h - th * 2)
    # original: zeichnet noch eine outline um die karte - können wir nicht.

    tmp0 = _createImageMask(image.texture, color)
    if backfile:
        tmp1 = LCoreImage(backfile)
        txtre = _scaleTextureToSize(tmp1.texture, image.texture.size)
        tmp = _pasteTextureTo(txtre, tmp0)
    else:
        tmp = tmp0

    img = LImageInfo(tmp)
    img.size = (image.getWidth(), image.getHeight())
    return img
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
