#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
# Copyright (C) 2017 LB
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
# Note:
# Many classes or some methods of classes are dead code resulting from the tk
# implementation. If executed it would throw exceptions.
#
# Kivy Implementation used: MfxScrolledCanvas, MfxDialog (partly)

from __future__ import division

import logging

from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from pysollib.kivy.LApp import LBoxLayout
from pysollib.kivy.LApp import LScrollView
from pysollib.kivy.LApp import LTopLevel
from pysollib.kivy.LApp import LTopLevel0
from pysollib.kivy.LApp import get_menu_size_hint
from pysollib.kivy.LImage import LImage
from pysollib.kivy.tkcanvas import MfxCanvas
from pysollib.kivy.tkutil import bind, unbind_destroy
from pysollib.mfxutil import KwStruct, kwdefault
from pysollib.mygettext import _
from pysollib.settings import WIN_SYSTEM

# ************************************************************************
# * abstract base class for the dialogs in this module
# ************************************************************************


class MfxDialog:  # ex. _ToplevelDialog
    img = {}
    button_img = {}

    def __init__(self, parent, title="", resizable=False, default=-1):
        self.parent = parent
        self.status = 0
        self.button = default
        self.timer = None
        self.buttons = []
        self.accel_keys = {}
        self.window = LTopLevel0(parent, title=title)
        self.top = self.window.content

        def setSizeRule(obj, val):
            self.window.size_hint = get_menu_size_hint()
        self.parent.bind(size=setSizeRule)
        setSizeRule(0, 0)

    def wmDeleteWindow(self, *event):
        self.status = 1
        raise SystemExit
        # return EVENT_HANDLED

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
        # key = unicode(key, 'utf-8')
        key = key.lower()
        button = self.accel_keys.get(key)
        if button is not None:
            self.mDone(button)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      timeout=0, resizable=False,
                      text="", justify="center",
                      strings=(_("&OK"), ),
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
        a = LBoxLayout(orientation="vertical")
        b = LBoxLayout(orientation="vertical")
        return a, b


# ************************************************************************
# Needed Labels.

class MfxSimpleEntry:
    pass


class MfxToolTip:
    pass

# ************************************************************************
# * replacement for the tk_dialog script
# ************************************************************************
# Kivy implementation helpers.


class FLabel(Label):
    def __init__(self, **kw):
        super(FLabel, self).__init__(**kw)

        self.bind(size=self.onUpdate)
        self.bind(pos=self.onUpdate)
        self.bind(text=self.onUpdate)

    def onUpdate(self, instance, size):
        self.size_hint_y = None
        self.text_size = self.width, None
        self.texture_update()
        self.height = self.texture_size[1]


class FText(LScrollView):
    def __init__(self, **kw):
        super(FText, self).__init__(**kw)

        self.label = FLabel(**kw)
        self.add_widget(self.label)


class MfxMessageDialog(MfxDialog):
    def __init__(self, parent, title, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)

        if (kw.image):
            image = LImage(texture=kw.image.texture, size_hint=(1, 1))
            self.top.add_widget(image)

        label = FText(text=kw.text, halign='center')
        self.top.add_widget(label)

        # LB
        # nicht automatisch ein neues spiel laden.
        if (title == _("Game won")):
            self.status = 1
            # self.button = 0
        if (title == _("Game finished")):
            self.status = 1
            # self.button =

# ************************************************************************
# *
# ************************************************************************


class MfxExceptionDialog(MfxMessageDialog):
    def __init__(self, parent, ex, title=_("Error"), **kw):
        kw = KwStruct(kw, bitmap="error")
        text = kw.get("text", "")
        if not text.endswith("\n"):
            text = text + "\n"
        text = text + "\n"
        if isinstance(ex, EnvironmentError) and ex.filename is not None:
            t = "[Errno %s] %s:\n%s" % (
                ex.errno, ex.strerror, repr(ex.filename))
        else:
            t = str(ex)
        kw.text = text + t
        MfxMessageDialog.__init__(self, parent, title, **kw.getKw())


# ************************************************************************
# *
# ************************************************************************

class PysolAboutDialog(object):

    # Die einzige Instanz.
    AboutDialog = None

    def onClick(self, event):
        print('LTopLevel: onClick')
        PysolAboutDialog.AboutDialog.parent.popWork('AboutDialog')
        PysolAboutDialog.AboutDialog.running = False

    def __init__(self, app, parent, title, **kw):
        logging.info('PysolAboutDialog:')
        super(PysolAboutDialog, self).__init__()

        self._url = kw['url']
        logging.info('PysolAboutDialog: txt=%s' % title)

        text = kw['text']
        text = text + '\n' + self._url
        logging.info('PysolAboutDialog: txt=%s' % text)

        text = text + '\n\n' + 'Adaptation to Kivy/Android\n' + \
            ' Copyright (C) (2016-24) LB'

        self.parent = parent
        self.app = app
        self.window = None
        self.running = False
        self.status = 1  # -> von help.py so benötigt
        self.button = 0  # -> von help.py so benötigt

        # bestehenden Dialog rezyklieren.

        logging.info('PysolAboutDialog: 1')
        onlyone = PysolAboutDialog.AboutDialog
        if (onlyone and onlyone.running):
            return
        if (onlyone):
            onlyone.parent.pushWork('AboutDialog', onlyone.window)
            onlyone.running = True
            return

        # neuen Dialog aufbauen.

        window = LTopLevel(parent, title, size_hint=(1.0, 1.0))
        window.titleline.bind(on_press=self.onClick)
        self.parent.pushWork('AboutDialog', window)
        self.window = window
        self.running = True
        PysolAboutDialog.AboutDialog = self

        if kw['image']:
            image = LImage(texture=kw['image'].texture)
            image.size_hint = (1, 0.8)
            al = AnchorLayout()
            al.add_widget(image)
            al.size_hint = (1, 0.3)
            window.content.add_widget(al)

        label = FText(text=text, halign='center', size_hint=(1, 1))
        window.content.add_widget(label)


# ************************************************************************
# * a simple tooltip
# ************************************************************************
# ToolTip - not used in Kivy - would not run without adaptations.


'''
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
        timediff = time.time() - MfxTooltip.last_leave_time
        if timediff < self.leave_timeout / 1000.:
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
#         if isinstance(self.widget, (Tkinter.Button, Tkinter.Checkbutton)):
#             if self.widget["state"] == 'disabled':
#                 return
        # x = self.widget.winfo_rootx()
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
        self.cancel_timer = after(
            self.widget, self.cancel_timeout, self._leave)
        # self.tooltip.tkraise()
'''

# ************************************************************************
# * A canvas widget with scrollbars and some useful bindings.
# ************************************************************************
# Kivy implementation of MfxScrolledCanvas.

from kivy.uix.scatterlayout import Scatter        # noqa
from kivy.uix.stencilview import StencilView      # noqa
from kivy.graphics.transformation import Matrix   # noqa


class LScatterFrame(Scatter):
    def __init__(self, inner, **kw):
        super(LScatterFrame, self).__init__(**kw)
        self.inner = inner
        self.add_widget(inner)
        self.bind(pos=self._updatepos)
        self.bind(size=self._updatesize)
        self.do_rotation = False
        self.scale_min = 1.0
        self.scale_max = 2.2
        self.lock_pos = None
        self.lock_chk = None
        self.offset = None
        self.tkopt = None

    def set_scale(self,zoom):
        scale = zoom[0]
        self.transform = Matrix().scale(scale,scale,1)
        xoff = zoom[1]
        yoff = zoom[2]
        self.offset = (xoff,yoff)

    def _change_command(self,inst,val):
        if self.lock_pos is None:
            self.set_scale(val)

    def _update(self):
        # initialisation
        if self.tkopt is None:
            app = self.inner.wmain.app
            tkopt = None
            if app is not None: tkopt = app.menubar.tkopt
            if tkopt is not None:
                self.tkopt = tkopt
                self.set_scale(tkopt.table_zoom.value)
                print("table_zoom",tkopt.table_zoom.value)
                tkopt.table_zoom.bind(value=self._change_command)

        # update
        if self.lock_pos is None:
            self.lock_pos = "locked"
            if self.offset is not None:
                dx = round(self.offset[0] * (self.bbox[1][0] - self.size[0]))
                dy = round(self.offset[1] * (self.bbox[1][1] - self.size[1]))
                self.pos = (self.parent.pos[0]-dx,self.parent.pos[1]-dy)
                if self.lock_chk is None:
                    Clock.schedule_once(lambda dt: self.chk_bnd()) # noqa
            self.lock_pos = None
            # print("_update",self.pos,self.size)

    def _updatesize(self,instance,value):
        self.inner.size = self.size
        self._update()

    def _updatepos(self,instance,value):
        self._update()

    def collide_point(self,x,y):
        px,py = self.parent.pos
        sx,sy = self.parent.size
        return px <= x < px + sx and py <= y < py + sy

    def on_touch_down(self, touch):
        ret = False
        x,y = touch.pos
        if self.collide_point(x,y):
            if touch.is_double_tap:
                # Do not use the event handling of scatter because scatter
                # does not allow to propagate an unhandled double tap back
                # to parent (it grabs the touch unseen if not
                # handled by a child!).
                touch.push()
                touch.apply_transform_2d(self.to_local)
                ret = self.inner.on_touch_down(touch)
                touch.pop()
            else:
                ret = super(LScatterFrame, self).on_touch_down(touch)
        return ret

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            return super(LScatterFrame, self).on_touch_up(touch)

        x,y = touch.pos
        if self.collide_point(x,y):
            return super(LScatterFrame, self).on_touch_up(touch)
        return False

    def on_touch_move(self, touch):
        ret = False
        self.lock_pos = "locked"
        ret = super(LScatterFrame, self).on_touch_move(touch)
        self.lock_pos = None
        return ret

    def on_transform_with_touch(self,touch):
        self.chk_bnd()

    def chk_bnd(self):
        # Keep the game on the screen.

        # check and set lock
        if self.lock_chk is not None: return
        self.lock_chk = "locked"

        # limiting parameters:
        pos,size = self.bbox
        w,h = size
        x,y = pos
        px,py = self.parent.pos
        sx,sy = self.parent.size

        # calculate correction matrix and apply
        tm = Matrix()
        if (x>px):
            tm = tm.multiply(Matrix().translate(px-x,0,0))
        if (y>py):
            tm = tm.multiply(Matrix().translate(0,py-y,0))
        if ((x+w) <= (px+sx)):
            tm = tm.multiply(Matrix().translate(px+sx-x-w,0,0))
        if ((y+h) <= (py+sy)):
            tm = tm.multiply(Matrix().translate(0,py+sy-y-h,0))
        self.apply_transform(tm)

        # save current offset.
        self.offset = None
        offx = self.parent.pos[0] - self.pos[0]
        offy = self.parent.pos[1] - self.pos[1]
        offmx = float(self.bbox[1][0] - self.size[0])
        offmy = float(self.bbox[1][1] - self.size[1])
        if (offmx>0 and offmy>0):
            self.offset = (offx/offmx,offy/offmy)

        # update persistent zoom parameters
        zoom = self.bbox[1][0]/float(self.size[0])
        if self.offset is not None:
            zoominfo = [zoom, self.offset[0], self.offset[1]]
        else:
            zoominfo = [zoom, 0.0, 0.0]
        self.tkopt.table_zoom.value = zoominfo

        # remove lock
        self.lock_chk = None


class LScrollFrame(BoxLayout,StencilView):
    def __init__(self, **kw):
        super(LScrollFrame, self).__init__(orientation="vertical", **kw)


class MfxScrolledCanvas(object):
    def __init__(self, parent, hbar=True, vbar=True, propagate=False, **kw):
        kwdefault(kw, highlightthickness=0, bd=1, relief='sunken')
        self.parent = parent

        # workarea = parent.getWork()
        print('MfxScrolledCanvas: parent=%s' % (parent))

        super(MfxScrolledCanvas, self).__init__()
        self.createFrame(kw)
        self.canvas = None
        # do_scroll_x = None
        # do_scroll_y = None
        # self.hbar = None
        # self.vbar = None
        self.hbar_show = False
        self.vbar_show = False
        self.createCanvas(kw)
        # self.frame.grid_rowconfigure(0, weight=1)
        # self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_propagate(propagate)
        if hbar:
            self.createHbar()
            self.bindHbar()
        if vbar:
            self.createVbar()
            self.bindVbar()
        # self.canvas.focus_set()

    def destroy(self):
        logging.info('MfxRoot: destroy')
        self.unbind_all()
        self.canvas.destroy()
        self.frame.destroy()

    def pack(self, **kw):
        pass
        # self.frame.pack(**kw)

    def grid(self, **kw):
        pass
        # self.frame.grid(**kw)

    #
    #
    #

    def setTile(self, app, i, scale_method, force=False):
        logging.info('MfxRoot: setTitle app=%s' % app)

        tile = app.tabletile_manager.get(i)

        print('setTile: (tile) %s, index=%s' % (tile, i))

        if tile is None or tile.error:
            return False

        # print i, tile
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
        print('setTile2: %s, %s' % (tile.filename, tile.color))

        if not self.canvas.setTile(
                tile.filename, tile.stretch, tile.save_aspect):
            tile.error = True
            return False

        print(
            'MfxScrolledCanvas: tile.color, app.top_bg %s, %s'
            % (tile.color, app.top_bg))
        if i == 0:
            if force:
                tile.color = app.opt.colors['table']
            self.canvas.config(bg=tile.color)
        else:
            if isinstance(app.top_bg, str):
                self.canvas.config(bg=app.top_bg)

        self.canvas.setTextColor(app.opt.colors['text'])
        return True
    #
    #
    #

    def deleteAllItems(self):
        logging.info('MfxRoot: deleteAllItems')
        # self.parent.getWork()
        # self.parent.popWork()
        # self.frame.clear_widgets()
        self.canvas.clear_widgets()

    def update_idletasks(self):
        logging.info('MfxRoot: update_idletasks')
        Clock.schedule_once(lambda x: self.canvas.canvas.ask_update)

    def unbind_all(self):
        unbind_destroy(self.hbar)
        unbind_destroy(self.vbar)
        unbind_destroy(self.canvas)
        unbind_destroy(self.frame)

    def createFrame(self, kw):
        logging.info('MfxRoot: createFrame')
        # width = kw.get("width")
        # height = kw.get("height")
        print('createFrame: kw=%s' % kw)
        # self.frame = Tkinter.Frame(self.parent, width=width, height=height)

        self.frame = LScrollFrame(size_hint=(1, 1))

        print("createFrame: self.parent %s" % str(self.frame))

    def createCanvas(self, kw):
        logging.info('MfxRoot: createCanvas')
        kw['bd'] = 0
        del kw['relief']
        self.canvas = MfxCanvas(self.parent, **kw)
        scatter = LScatterFrame(self.canvas)
        self.frame.add_widget(scatter)
        self.parent.pushWork('playground', self.frame)

    def createHbar(self):
        pass
        '''
        self.hbar = Tkinter.Scrollbar(self.frame, takefocus=0,
                                      orient="horizontal")
        self.canvas["xscrollcommand"] = self._setHbar
        self.hbar["command"] = self.canvas.xview
        self.hbar.grid(row=1, column=0, sticky="we")
        self.hbar.grid_remove()
        '''

    def createVbar(self):
        pass
        '''
        self.vbar = Tkinter.Scrollbar(self.frame, takefocus=0)
        self.canvas["yscrollcommand"] = self._setVbar
        self.vbar["command"] = self.canvas.yview
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.vbar.grid_remove()
        '''

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
        # bind(w, '<MouseWheel>', self.mouse_wheel)

    def mouse_wheel(self, *args):
        pass

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
        if self.hbar_show:
            self.canvas.xview(*args)
        return 'break'

    def _yview(self, *args):
        if self.vbar_show:
            self.canvas.yview(*args)
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
# not used witch kivy. would not nun as it refers TkInter.
