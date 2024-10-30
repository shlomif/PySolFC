#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------

import os
import re
import tkinter
import tkinter.font

from pysollib.mfxutil import Image, ImageDraw, ImageOps, ImageTk, \
    get_default_resampling
from pysollib.settings import TITLE, WIN_SYSTEM


# ************************************************************************
# * window manager util
# ************************************************************************

def wm_withdraw(window):
    window.wm_withdraw()


def wm_deiconify(window):
    window.wm_deiconify()


def wm_map(window, maximized=0, fullscreen=0):
    if window.wm_state() != "iconic":
        if maximized and WIN_SYSTEM == "win32":
            window.wm_state("zoomed")
        else:
            wm_deiconify(window)
    window.attributes('-fullscreen', fullscreen)


__wm_get_geometry_re = re.compile(r"^(\d+)x(\d+)\+([\-]?\d+)\+([\-]?\d+)$")


def wm_get_geometry(window):
    g = window.wm_geometry()
    m = __wm_get_geometry_re.search(g)
    if not m:
        raise tkinter.TclError("invalid geometry "+str(g))
    lst = list(map(int, m.groups()))
    if window.wm_state() == "zoomed":
        # workaround as Tk returns the "unzoomed" origin
        lst[2] = lst[3] = 0
    return lst


# ************************************************************************
# * window util
# ************************************************************************

def setTransient(window, parent, relx=None, rely=None, expose=1):
    # Make an existing toplevel window transient for a parent.
    #
    # The window must exist but should not yet have been placed; in
    # other words, this should be called after creating all the
    # subwidget but before letting the user interact.

    # remain invisible while we figure out the geometry
    window.wm_withdraw()
    window.wm_group(parent)
    if parent and parent.wm_state() != "withdrawn":
        window.wm_transient(parent)
    # actualize geometry information
    window.update_idletasks()
    # show
    x, y = __getWidgetXY(window, parent, relx=relx, rely=rely)
    window.wm_geometry("+%d+%d" % (x, y))
    if expose:
        window.wm_deiconify()


def makeToplevel(parent, title=None):
    # Create a Toplevel window.
    #
    # This is a shortcut for a Toplevel() instantiation plus calls to
    # set the title and icon name of the window.
    window = tkinter.Toplevel(parent)  # , class_=TITLE)
    # window.wm_group(parent)
    # window.wm_command("")
    if WIN_SYSTEM == "x11":
        window.wm_command("/bin/true")
    # window.wm_protocol("WM_SAVE_YOURSELF", None)
    if title:
        window.wm_title(title)
        window.wm_iconname(title)
    return window


def make_help_toplevel(app, title=None):
    # Create an independent Toplevel window.
    from pysollib.winsystems import init_root_window
    window = tkinter.Toplevel(class_=TITLE)
    init_root_window(window, app)
    window.tkraise()
    return window


def __getWidgetXY(widget, parent, relx=None, rely=None,
                  w_width=None, w_height=None):
    if w_width is None:
        w_width = widget.winfo_reqwidth()
    if w_height is None:
        w_height = widget.winfo_reqheight()
    s_width = widget.winfo_screenwidth()
    s_height = widget.winfo_screenheight()
    m_x = m_y = 0
    m_width, m_height = s_width, s_height
    if parent and parent.winfo_ismapped():
        # print parent.wm_geometry()
        # print parent.winfo_geometry(), parent.winfo_x(), parent.winfo_y(), \
        #   parent.winfo_rootx(), parent.winfo_rooty(), parent.winfo_vrootx(),\
        #   parent.winfo_vrooty()
        m_x = m_y = None
        if WIN_SYSTEM == "win32":
            try:
                m_width, m_height, m_x, m_y = wm_get_geometry(parent)
            except Exception:
                pass
        if m_x is None:
            m_x = parent.winfo_x()
            m_y = parent.winfo_y()
            m_width = parent.winfo_width()
            m_height = parent.winfo_height()
            if relx is None:
                relx = 0.5
            if rely is None:
                rely = 0.3
        else:
            if relx is None:
                relx = 0.5
            if rely is None:
                rely = 0.5
        m_x = max(m_x, 0)
        m_y = max(m_y, 0)
    else:
        if relx is None:
            relx = 0.5
        if rely is None:
            rely = 0.3
    x = m_x + int((m_width - w_width) * relx)
    y = m_y + int((m_height - w_height) * rely)
    # print x, y, w_width, w_height, m_x, m_y, m_width, m_height
    # make sure the widget is fully on screen
    if x < 0:
        x = 0
    elif x + w_width + 32 > s_width:
        x = max(0, (s_width - w_width) // 2)
    if y < 0:
        y = 0
    elif y + w_height + 32 > s_height:
        y = max(0, (s_height - w_height) // 2)
    return x, y


# ************************************************************************
# * bind wrapper - tkinter doesn't properly delete all bindings
# ************************************************************************

__mfx_bindings = {}
__mfx_wm_protocols = ("WM_DELETE_WINDOW", "WM_TAKE_FOCUS", "WM_SAVE_YOURSELF")


def bind(widget, sequence, func, add=None):
    # assert callable(func) # XXX: removed in py3k
    if sequence in __mfx_wm_protocols:
        funcid = widget._register(func)
        widget.tk.call("wm", "protocol", widget._w, sequence, funcid)
    elif add is None:
        funcid = widget.bind(sequence, func)
    else:
        # add = add and "+" or ""
        funcid = widget.bind(sequence, func, add)
    k = id(widget)
    if k in __mfx_bindings:
        __mfx_bindings[k].append((sequence, funcid))
    else:
        __mfx_bindings[k] = [(sequence, funcid)]


def unbind_destroy(widget):
    if widget is None:
        return
    k = id(widget)
    if k in __mfx_bindings:
        for sequence, funcid in __mfx_bindings[k]:
            # print widget, sequence, funcid
            try:
                if sequence in __mfx_wm_protocols:
                    widget.tk.call("wm", "protocol", widget._w, sequence, "")
                    # widget.deletecommand(funcid)
                else:
                    widget.unbind(sequence, funcid)
            except tkinter.TclError:
                pass
        del __mfx_bindings[k]
    # for k in __mfx_bindings.keys(): print __mfx_bindings[k]
    # print len(__mfx_bindings.keys())


# ************************************************************************
# * timer wrapper - tkinter doesn't properly delete all commands
# ************************************************************************

def after(widget, ms, func, *args):
    timer = widget.after(ms, func, *args)
    command = widget._tclCommands[-1]
    return (timer, command, widget)


def after_idle(widget, func, *args):
    return after(widget, "idle", func, *args)


def after_cancel(t):
    if t is not None:
        t[2].after_cancel(t[0])
        try:
            t[2].deletecommand(t[1])
        except tkinter.TclError:
            pass


# ************************************************************************
# * image handling
# ************************************************************************

if Image:
    class PIL_Image(ImageTk.PhotoImage):
        def __init__(self, file=None, image=None, pil_image_orig=None):

            if file:
                image = Image.open(file).convert('RGBA')

                basename = os.path.basename(file)
                file_name = os.path.splitext(basename)[0]

                findsum = findfile(file_name)

                if findsum != -3:  # -1 for every check
                    image = masking(image)

                    image.filename = file_name

            ImageTk.PhotoImage.__init__(self, image)
            self._pil_image = image
            if pil_image_orig:
                self._pil_image_orig = pil_image_orig
            else:
                self._pil_image_orig = image

        def subsample(self, r):
            im = self._pil_image
            w, h = im.size
            w, h = int(float(w)/r), int(float(h)/r)

            im = im.resize((w, h))

            try:
                findsum = findfile(self._pil_image_orig.filename)
                if findsum != -3:  # -1 for every check
                    im = masking(im)
            except Exception:
                pass  # placeholder
                #  im = masking(im)  # now don't mask images with no name

            im = PIL_Image(image=im)
            return im

        def resize(self, xf, yf, resample=-1):

            if resample == -1:
                resample = get_default_resampling()

            w, h = self._pil_image_orig.size
            w0, h0 = int(w*xf), int(h*yf)

            im = self._pil_image_orig.resize((w0, h0), resample)

            try:
                findsum = findfile(self._pil_image_orig.filename)
                if findsum != -3:  # -1 for every check
                    im = masking(im)
            except Exception:
                pass  # placeholder
                #  im = masking(im)  # now don't mask images with no name

            return PIL_Image(image=im, pil_image_orig=self._pil_image_orig)


def masking(image):

    # eliminates the 0 in alphachannel
    # because PhotoImage and Rezising
    # have problems with it

    image = image.convert("RGBA")  # make sure it has alphachannel
    mask = image.copy()
    # important alpha must be bigger than 0
    mask.putalpha(1)
    mask.paste(image, (0, 0), image)
    image = mask.copy()

    return image


def findfile(file_name):

    find1 = file_name.find("bottom")
    find2 = file_name.find("shad")
    find3 = file_name.find("l0")
    # find4 = file_name.find("back")

    findsum = find1 + find2 + find3

    return findsum


def makeImage(file=None, data=None, dither=None, alpha=None):
    kw = {}
    if data is None:
        assert file is not None
        kw["file"] = file
    else:
        # assert data is not None
        kw["data"] = data
    if Image:
        # use PIL
        if file:
            im = PIL_Image(file)
            return im
        # fromstring(mode, size, data, decoder_name='raw', *args)
        else:
            return tkinter.PhotoImage(data=data)
    return tkinter.PhotoImage(**kw)


loadImage = makeImage


def copyImage(image, x, y, width, height):
    if Image:
        if isinstance(image, PIL_Image):
            return ImageTk.PhotoImage(
                image._pil_image.crop((x, y, x+width, y+height)))
    dest = tkinter.PhotoImage(width=width, height=height)
    assert dest.width() == width
    assert dest.height() == height
    dest.blank()
    image.tk.call(dest, "copy", image.name, "-from", x, y, x+width, y+height)
    assert dest.width() == width
    assert dest.height() == height
    return dest


def fillImage(image, fill, outline=None):
    if not fill and not outline:
        return
    width = image.width()
    height = image.height()
    ow = 1                              # outline width
    if width <= 2*ow or height <= 2*ow:
        fill = fill or outline
        outline = None
    if not outline:
        f = (fill,) * width
        f = (f,) * height
        assert len(f) == height
        image.put(f)
    elif not fill:
        l1 = ((outline,) * width,)
        for y in range(0, ow):
            image.put(l1, (0, y))
        for y in range(height-ow, height):
            image.put(l1, (0, y))
        p = ((outline,) * ow,)
        for y in range(ow, height-ow):
            image.put(p, (0, y))
            image.put(p, (width-ow, y))
    else:
        l1 = (outline,) * width
        l2 = (outline,) * ow + (fill,) * (width-2*ow) + (outline,) * ow
        f = (l1,) * ow + (l2,) * (height-2*ow) + (l1,) * ow
        assert len(f) == height
        image.put(f)


def createImage(width, height, fill, outline=None):
    image = tkinter.PhotoImage(width=width, height=height)
    assert image.width() == width
    assert image.height() == height
    image.blank()
    fillImage(image, fill, outline)
    return image


def createImagePIL(width, height, fill, outline=None):
    if not fill:
        image = Image.new('RGBA', (width, height))
    else:
        image = Image.new('RGBA', (width, height), color=fill)
    if outline is not None:
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, width - 1, height - 1], fill=None,
                       outline=outline, width=1)

    return PIL_Image(image=image)


def shadowImage(image, color='#3896f8', factor=0.3):
    if not hasattr(image, '_pil_image'):
        return None
    im = image._pil_image
    # use an alpha image
    sh = Image.new('RGBA', im.size, color)
    sh.putalpha(100)
    out = Image.composite(sh, im, im)
    return PIL_Image(image=out)


def markImage(image):
    assert Image
    if 1:                               # shadow
        color, factor = '#6ae400', 0.3
        sh = Image.new('RGBA', image.size, color)
        tmp = Image.blend(image, sh, factor)
    else:                               # negate
        tmp = ImageOps.invert(image.convert('RGB'))
    out = Image.composite(tmp, image, image)
    return out


def _createBottomImage(image, color='white', backfile=None):
    th = 1                              # thickness
    sh = Image.new('RGBA', image.size, color)
    out = Image.composite(sh, image, image)
    w, h = image.size
    size = (w-th*2, h-th*2)
    tmp = Image.new('RGBA', size, color)
    tmp.putalpha(60)

    resampling = get_default_resampling()

    mask = out.resize(size, resampling)
    out.paste(tmp, (th, th), mask)
    if backfile:
        back = Image.open(backfile).convert('RGBA')
        w0, h0 = back.size
        w1, h1 = w, h
        a = min(float(w1)/w0, float(h1)/h0)
        a = a*0.9
        w0, h0 = int(w0*a), int(h0*a)
        back = back.resize((w0, h0), resampling)
        x, y = (w1 - w0) // 2, (h1 - h0) // 2
        out.paste(back, (x, y), back)
    return out


def createBottom(maskimage, color='white', backfile=None):
    if not hasattr(maskimage, '_pil_image'):
        return None
    maskimage = maskimage._pil_image
    out = _createBottomImage(maskimage, color, backfile)

    return PIL_Image(image=out)


def resizeBottom(image, maskimage, color='white', backfile=None):
    maskimage = maskimage._pil_image
    out = _createBottomImage(maskimage, color, backfile)
    image['image'] = out


# ************************************************************************
# * font utils
# ************************************************************************

def get_text_width(text, font, root=None):
    return tkinter.font.Font(root=root, font=font).measure(text)
