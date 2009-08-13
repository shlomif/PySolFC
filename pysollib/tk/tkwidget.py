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

__all__ = ['MfxDialog',
           'MfxMessageDialog',
           'MfxExceptionDialog',
           'MfxSimpleEntry',
           'PysolAboutDialog',
           'MfxTooltip',
           'MfxScrolledCanvas',
           'StackDesc',
           ]

# imports
import time
import Tkinter
import tkFont
import traceback

# PySol imports
from pysollib.mfxutil import destruct, kwdefault, KwStruct, openURL
from pysollib.settings import WIN_SYSTEM

# Toolkit imports
from tkutil import after, after_cancel
from tkutil import bind, unbind_destroy
from tkutil import makeToplevel, setTransient
from tkcanvas import MfxCanvas


# ************************************************************************
# * abstract base class for the dialogs in this module
# ************************************************************************

class MfxDialog: # ex. _ToplevelDialog
    img = {}
    button_img = {}
    def __init__(self, parent, title="", resizable=False, default=-1):
        self.parent = parent
        self.status = 0
        self.button = default
        self.timer = None
        self.buttons = []
        self.accel_keys = {}
        self.top = makeToplevel(parent, title=title)
        self.top.wm_resizable(resizable, resizable)
        ##w, h = self.top.winfo_screenwidth(), self.top.winfo_screenheight()
        ##self.top.wm_maxsize(w-4, h-32)
        bind(self.top, "WM_DELETE_WINDOW", self.wmDeleteWindow)
        #

    def mainloop(self, focus=None, timeout=0, transient=True):
        bind(self.top, "<Escape>", self.mCancel)
        bind(self.top, '<Alt-Key>', self.altKeyEvent) # for accelerators
        if focus is not None:
            focus.focus()
        if transient:
            setTransient(self.top, self.parent)
            try:
                self.top.grab_set()
            except Tkinter.TclError:
                if traceback: traceback.print_exc()
                pass
            if timeout > 0:
                self.timer = after(self.top, timeout, self.mTimeout)
            try: self.top.mainloop()
            except SystemExit:
                pass
            self.destroy()

    def destroy(self):
        after_cancel(self.timer)
        unbind_destroy(self.top)
        try:
            self.top.wm_withdraw()
        except:
            if traceback: traceback.print_exc()
            pass
        try:
            self.top.destroy()
        except:
            if traceback: traceback.print_exc()
            pass
        #destruct(self.top)
        if 1 and self.parent: # ???
            try:
                ##self.parent.update_idletasks()
                # FIXME: why do we need this under Windows ?
                if hasattr(self.parent, "busyUpdate"):
                    self.parent.busyUpdate()
                else:
                    self.parent.update()
            except:
                if traceback: traceback.print_exc()
                pass
        self.top = None
        self.parent = None

    def wmDeleteWindow(self, *event):
        self.status = 1
        raise SystemExit
        ##return EVENT_HANDLED

    def mCancel(self, *event):
        self.status = 1
        raise SystemExit

    def mTimeout(self, *event):
        self.status = 2
        raise SystemExit

    def mDone(self, button):
        self.button = button
        raise SystemExit

    def altKeyEvent(self, event):
        key = event.char
        key = unicode(key, 'utf-8')
        key = key.lower()
        button = self.accel_keys.get(key)
        if button is not None:
            self.mDone(button)


    def initKw(self, kw):
        kw = KwStruct(kw,
                      timeout=0, resizable=False,
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
        # default to separator if more than one button
        sep = len(kw.strings) > 1
        kwdefault(kw.__dict__, separator=sep)
        return kw

    def createFrames(self, kw):
        bottom_frame = Tkinter.Frame(self.top)
        bottom_frame.pack(side='bottom', fill='both', expand=False,
                          ipadx=3, ipady=3)
        if kw.separator:
            separator = Tkinter.Frame(self.top, relief="sunken",
                    height=2, width=2, borderwidth=1)
            separator.pack(side='bottom', fill='x')
        top_frame = Tkinter.Frame(self.top)
        top_frame.pack(side='top', fill='both', expand=True)
        return top_frame, bottom_frame

    def createBitmaps(self, frame, kw):
        if kw.bitmap: ## in ("error", "info", "question", "warning")
            img = self.img.get(kw.bitmap)
            b = Tkinter.Label(frame, image=img)
            b.pack(side=kw.bitmap_side, padx=kw.bitmap_padx, pady=kw.bitmap_pady)
        elif kw.image:
            b = Tkinter.Label(frame, image=kw.image)
            b.pack(side=kw.image_side, padx=kw.image_padx, pady=kw.image_pady)

    def createButtons(self, frame, kw):
        button = -1
        column = 0
        padx, pady = kw.get("buttonpadx", 10), kw.get("buttonpady", 10)
        focus = None
        max_len = 0
        for s in kw.strings:
            if isinstance(s, tuple):
                s = s[0]
            if s:
                #if os.name == 'posix':
                #    s = s.replace('...', '.')
                s = s.replace('&', '')
                max_len = max(max_len, len(s))
            ##print s, len(s)
        if   max_len > 12 and WIN_SYSTEM == 'x11': button_width = max_len
        elif max_len > 9 : button_width = max_len+1
        elif max_len > 6 : button_width = max_len+2
        else             : button_width = 8
        #print 'button_width =', button_width
        #
        #
        for s in kw.strings:
            xbutton = button = button + 1
            if isinstance(s, tuple):
                assert len(s) == 2
                button = int(s[1])
                s = s[0]
            if s is None:
                continue
            accel_indx = s.find('&')
            s = s.replace('&', '')
            if button < 0:
                b = Tkinter.Button(frame, text=s, state="disabled")
                button = xbutton
            else:
                b = Tkinter.Button(frame, text=s, default="normal",
                                   command=(lambda self=self, button=button: self.mDone(button)))
                if button == kw.default:
                    focus = b
                    focus.config(default="active")
            self.buttons.append(b)
            #
            b.config(width=button_width)
            if accel_indx >= 0:
                # key accelerator
                b.config(underline=accel_indx)
                key = s[accel_indx]
                self.accel_keys[key.lower()] = button
            #
##             img = None
##             if self.button_img:
##                 img = self.button_img.get(s)
##             b.config(compound='left', image=img)
            column += 1
            b.grid(column=column, row=0, sticky="ns", padx=padx, pady=pady)
        if focus is not None:
            l = (lambda event=None, self=self, button=kw.default: self.mDone(button))
            bind(self.top, "<Return>", l)
            bind(self.top, "<KP_Enter>", l)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(99, weight=1)
        return focus


# ************************************************************************
# * replacement for the tk_dialog script
# ************************************************************************

class MfxMessageDialog(MfxDialog):
    def __init__(self, parent, title, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.button = kw.default
        msg = Tkinter.Label(top_frame, text=kw.text, justify=kw.justify,
                            width=kw.width)
        msg.pack(fill='both', expand=True, padx=kw.padx, pady=kw.pady)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


# ************************************************************************
# *
# ************************************************************************

class MfxExceptionDialog(MfxMessageDialog):
    def __init__(self, parent, ex, title="Error", **kw):
        kw = KwStruct(kw, bitmap="error")
        text = kw.get("text", "")
        if not text.endswith("\n"):
            text = text + "\n"
        text = text + "\n"
        if isinstance(ex, EnvironmentError) and ex.filename is not None:
            t = "[Errno %s] %s:\n%s" % (ex.errno, ex.strerror, repr(ex.filename))
        else:
            t = str(ex)
        kw.text = text + unicode(t, errors='replace')
        MfxMessageDialog.__init__(self, parent, title, **kw.getKw())


# ************************************************************************
# *
# ************************************************************************

class PysolAboutDialog(MfxMessageDialog):
    def __init__(self, app, parent, title, **kw):
        self._url = kw['url']
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.button = kw.default
        frame = Tkinter.Frame(top_frame)
        frame.pack(fill='both', expand=True, padx=kw.padx, pady=kw.pady)
        msg = Tkinter.Label(frame, text=kw.text, justify=kw.justify,
                            width=kw.width)
        msg.pack(fill='both', expand=True)

        font = tkFont.Font(parent, app.getFont('default'))
        font.configure(underline=True)
        url_label = Tkinter.Label(frame, text=kw.url, font=font,
                                  foreground='blue', cursor='hand2')
        url_label.pack()
        url_label.bind('<1>', self._urlClicked)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def _urlClicked(self, event):
        openURL(self._url)


# ************************************************************************
# *
# ************************************************************************

class MfxSimpleEntry(MfxDialog):
    def __init__(self, parent, title, label, value, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.value = value
        if label:
            label = Tkinter.Label(top_frame, text=label, takefocus=0)
            label.pack(pady=5)
        w = kw.get("e_width", 0)    # width in characters
        self.var = Tkinter.Entry(top_frame, exportselection=1, width=w)
        self.var.insert(0, value)
        self.var.pack(side='top', padx=kw.padx, pady=kw.pady)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.var
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")), default=0,
                      separator=False,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        self.button = button
        self.value = self.var.get()
        raise SystemExit


# ************************************************************************
# * a simple tooltip
# ************************************************************************

class MfxTooltip:
    last_leave_time = 0

    def __init__(self, widget):
        # private vars
        self.widget = widget
        self.text = None
        self.timer = None
        self.cancel_timer = None
        self.tooltip = None
        self.label = None
        self.bindings = []
        self.bindings.append(self.widget.bind("<Enter>", self._enter))
        self.bindings.append(self.widget.bind("<Leave>", self._leave))
        self.bindings.append(self.widget.bind("<ButtonPress>", self._leave))
        # user overrideable settings
        self.timeout = 800                    # milliseconds
        self.cancel_timeout = 5000
        self.leave_timeout = 400
        self.relief = 'solid'
        self.justify = 'left'
        self.fg = "#000000"
        self.bg = "#ffffe0"
        self.xoffset = 0
        self.yoffset = 4

    def setText(self, text):
        self.text = text

    def _unbind(self):
        if self.bindings and self.widget:
            self.widget.unbind("<Enter>", self.bindings[0])
            self.widget.unbind("<Leave>", self.bindings[1])
            self.widget.unbind("<ButtonPress>", self.bindings[2])
            self.bindings = []

    def destroy(self):
        self._unbind()
        self._leave()

    def _enter(self, *event):
        after_cancel(self.timer)
        after_cancel(self.cancel_timer)
        self.cancel_timer = None
        if time.time() - MfxTooltip.last_leave_time < self.leave_timeout/1000.:
            self._showTip()
        else:
            self.timer = after(self.widget, self.timeout, self._showTip)

    def _leave(self, *event):
        after_cancel(self.timer)
        after_cancel(self.cancel_timer)
        self.timer = self.cancel_timer = None
        if self.tooltip:
            self.label.destroy()
            destruct(self.label)
            self.label = None
            self.tooltip.destroy()
            destruct(self.tooltip)
            self.tooltip = None
            MfxTooltip.last_leave_time = time.time()

    def _showTip(self):
        self.timer = None
        if self.tooltip or not self.text:
            return
##         if isinstance(self.widget, (Tkinter.Button, Tkinter.Checkbutton)):
##             if self.widget["state"] == 'disabled':
##                 return
        ##x = self.widget.winfo_rootx()
        x = self.widget.winfo_pointerx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        x += self.xoffset
        y += self.yoffset
        self.tooltip = Tkinter.Toplevel()
        self.tooltip.wm_iconify()
        self.tooltip.wm_overrideredirect(1)
        self.tooltip.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.label = Tkinter.Label(self.tooltip, text=self.text,
                                   relief=self.relief, justify=self.justify,
                                   fg=self.fg, bg=self.bg, bd=1, takefocus=0)
        self.label.pack(ipadx=1, ipady=1)
        self.tooltip.wm_geometry("%+d%+d" % (x, y))
        self.tooltip.wm_deiconify()
        self.cancel_timer = after(self.widget, self.cancel_timeout, self._leave)
        ##self.tooltip.tkraise()


# ************************************************************************
# * A canvas widget with scrollbars and some useful bindings.
# ************************************************************************

class MfxScrolledCanvas:
    def __init__(self, parent, hbar=True, vbar=True, propagate=False, **kw):
        kwdefault(kw, highlightthickness=0, bd=1, relief='sunken')
        self.parent = parent
        self.createFrame(kw)
        self.canvas = None
        self.hbar = None
        self.vbar = None
        self.hbar_show = False
        self.vbar_show = False
        self.createCanvas(kw)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_propagate(propagate)
        if hbar:
            self.createHbar()
            self.bindHbar()
        if vbar:
            self.createVbar()
            self.bindVbar()
        ###self.canvas.focus_set()

    #
    #
    #

    def destroy(self):
        self.unbind_all()
        self.canvas.destroy()
        self.frame.destroy()

    def pack(self, **kw):
        self.frame.pack(**kw)

    def grid(self, **kw):
        self.frame.grid(**kw)

    #
    #
    #

    def setTile(self, app, i, force=False):
        tile = app.tabletile_manager.get(i)
        if tile is None or tile.error:
            return False
        ##print i, tile
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
        #
        if not self.canvas.setTile(tile.filename, tile.stretch, tile.save_aspect):
            tile.error = True
            return False

        if i == 0:
            self.canvas.config(bg=tile.color)
            ##app.top.config(bg=tile.color)
        else:
            self.canvas.config(bg=app.top_bg)
            ##app.top.config(bg=app.top_bg)

        self.canvas.setTextColor(app.opt.colors['text'])

        return True

    #
    #
    #

    def unbind_all(self):
        unbind_destroy(self.hbar)
        unbind_destroy(self.vbar)
        unbind_destroy(self.canvas)
        unbind_destroy(self.frame)

    def createFrame(self, kw):
        width = kw.get("width")
        height = kw.get("height")
        self.frame = Tkinter.Frame(self.parent, width=width, height=height)
    def createCanvas(self, kw):
        bd = kw['bd']
        kw['bd'] = 0
        relief = kw['relief']
        del kw['relief']
        frame = Tkinter.Frame(self.frame, bd=bd, relief=relief)
        frame.grid(row=0, column=0, sticky="news")
        self.canvas = MfxCanvas(frame, **kw)
        self.canvas.pack(expand=True, fill='both')
    def createHbar(self):
        self.hbar = Tkinter.Scrollbar(self.frame, takefocus=0,
                                      orient="horizontal")
        self.canvas["xscrollcommand"] = self._setHbar
        self.hbar["command"] = self.canvas.xview
        self.hbar.grid(row=1, column=0, sticky="we")
        self.hbar.grid_remove()
    def createVbar(self):
        self.vbar = Tkinter.Scrollbar(self.frame, takefocus=0)
        self.canvas["yscrollcommand"] = self._setVbar
        self.vbar["command"] = self.canvas.yview
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.vbar.grid_remove()
    def bindHbar(self, w=None):
        if w is None:
            w = self.canvas
        bind(w, "<KeyPress-Left>", self.unit_left)
        bind(w, "<KeyPress-Right>", self.unit_right)
    def bindVbar(self, w=None):
        if w is None:
            w = self.canvas
        bind(w, "<KeyPress-Prior>", self.page_up)
        bind(w, "<KeyPress-Next>", self.page_down)
        bind(w, "<KeyPress-Up>", self.unit_up)
        bind(w, "<KeyPress-Down>", self.unit_down)
        bind(w, "<KeyPress-Begin>", self.scroll_top)
        bind(w, "<KeyPress-Home>", self.scroll_top)
        bind(w, "<KeyPress-End>", self.scroll_bottom)
        # mousewheel support
        if WIN_SYSTEM == 'x11':
            bind(w, '<4>', self.mouse_wheel_up)
            bind(w, '<5>', self.mouse_wheel_down)
        # don't work on Linux
        #bind(w, '<MouseWheel>', self.mouse_wheel)

    def mouse_wheel(self, *args):
        print 'MfxScrolledCanvas.mouse_wheel', args

    def _setHbar(self, first, last):
        if self.canvas.busy:
            return
        sb = self.hbar
        if float(first) <= 0 and float(last) >= 1:
            sb.grid_remove()
            self.hbar_show = False
        else:
            if self.canvas.winfo_ismapped():
                sb.grid()
                self.hbar_show = True
        sb.set(first, last)
    def _setVbar(self, first, last):
        if self.canvas.busy:
            return
        sb = self.vbar
        if float(first) <= 0 and float(last) >= 1:
            sb.grid_remove()
            self.vbar_show = False
        else:
            if self.canvas.winfo_ismapped():
                sb.grid()
                self.vbar_show = True
        sb.set(first, last)

    def _xview(self, *args):
        if self.hbar_show: self.canvas.xview(*args)
        return 'break'
    def _yview(self, *args):
        if self.vbar_show: self.canvas.yview(*args)
        return 'break'

    def page_up(self, *event):
        return self._yview('scroll', -1, 'page')
    def page_down(self, *event):
        return self._yview('scroll', 1, 'page')
    def unit_up(self, *event):
        return self._yview('scroll', -1, 'unit')
    def unit_down(self, *event):
        return self._yview('scroll', 1, 'unit')
    def mouse_wheel_up(self, *event):
        return self._yview('scroll', -5, 'unit')
    def mouse_wheel_down(self, *event):
        return self._yview('scroll', 5, 'unit')
    def page_left(self, *event):
        return self._xview('scroll', -1, 'page')
    def page_right(self, *event):
        return self._xview('scroll', 1, 'page')
    def unit_left(self, *event):
        return self._xview('scroll', -1, 'unit')
    def unit_right(self, *event):
        return self._xview('scroll', 1, 'unit')
    def scroll_top(self, *event):
        return self._yview('moveto', 0)
    def scroll_bottom(self, *event):
        return self._yview('moveto', 1)


# ************************************************************************
# *
# ************************************************************************

class StackDesc:

    def __init__(self, game, stack):
        self.game = game
        self.stack = stack
        self.canvas = game.canvas
        self.bindings = []

        font = game.app.getFont('canvas_small')
        ##print self.app.cardset.CARDW, self.app.images.CARDW
        cardw = game.app.images.CARDW
        x, y = stack.x+cardw/2, stack.y
        text = stack.getHelp()+'\n'+stack.getBaseCard()
        text = text.strip()
        if text:
            frame = Tkinter.Frame(self.canvas)
            self.frame = frame
            label = Tkinter.Message(frame, font=font, text=text,
                                    width=cardw-8, relief='solid',
                                    fg='#000000', bg='#ffffe0', bd=1)
            label.pack()
            self.label = label
            self.id = self.canvas.create_window(x, y, window=frame, anchor='n')
            self.bindings.append(label.bind('<ButtonPress>', self._buttonPressEvent))
            ##self.bindings.append(label.bind('<Enter>', self._enterEvent))
        else:
            self.id = None

    def _buttonPressEvent(self, *event):
        ##self.game.deleteStackDesc()
        self.frame.tkraise()

    def _enterEvent(self, *event):
        self.frame.tkraise()

    def delete(self):
        if self.id:
            self.canvas.delete(self.id)
            for b in self.bindings:
                self.label.unbind('<ButtonPress>', b)

