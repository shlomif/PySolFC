#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
#
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

from __future__ import division

import logging
import math
import traceback

from kivy.animation import Animation
from kivy.app import App
from kivy.base import EventLoop
from kivy.base import stopTouchApp
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.graphics import Rectangle
from kivy.graphics import Triangle
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.actionbar import ActionButton
from kivy.uix.actionbar import ActionPrevious
from kivy.uix.actionbar import ActionView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.treeview import TreeViewNode
from kivy.uix.widget import Widget
from kivy.utils import platform

from pysollib.kivy.LBase import LBase
from pysollib.kivy.LTask import LTask, LTaskQ
from pysollib.kivy.androidperms import requestStoragePerm
from pysollib.kivy.androidrot import AndroidScreenRotation
from pysollib.kivy.tkconst import EVENT_HANDLED, EVENT_PROPAGATE
from pysollib.resource import CSI

if platform != 'android':
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# =============================================================================


def get_platform():
    return platform

# =============================================================================


def get_menu_size_hint():
    sh = (0.5, 1.0)
    if Window.size[0] < Window.size[1]:
        sh = (1.0, 1.0)
    return sh

# =============================================================================


def set_fullscreen(fullscreen=True):
    if get_platform() == 'android':
        from jnius import autoclass
    else:
        return

    SDLActivity = autoclass('org.libsdl.app.SDLActivity')
    SDLActivity.setWindowStyle(fullscreen)

# =============================================================================


def get_screen_ori():
    if get_platform() == 'android':
        from jnius import autoclass
        from jnius import cast
    else:
        return None

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)

    # Display = autoclass('android.view.Display')
    # WindowManager = autoclass('android.view.WindowManager')

    wm = currentActivity.getWindowManager()
    d = wm.getDefaultDisplay()

    so = None
    if d.getWidth() > d.getHeight():
        so = 'landscape'
    else:
        so = 'portrait'

    logging.info("LApp: ori = %s" % so)
    return so

# =============================================================================


class LPopCommander(LBase):
    def __init__(self, **kw):
        super(LPopCommander, self).__init__()
        self.pop_command = kw['pop_command']

    def pop(self):
        if self.pop_command is not None:
            self.pop_command(0)
            return True
        return False

# =============================================================================


class LAnimationTask(LTask, LBase):
    def __init__(self, spos, widget, **kw):
        super(LAnimationTask, self).__init__(widget.card)
        self.spos = spos
        self.widget = widget

        self.xdest = kw.get('x', 0.0)
        self.ydest = kw.get('y', 0.0)
        self.duration = kw.get('duration', 0.2)
        self.transition = kw.get('transition', 'in_out_quad')
        self.bindE = kw.get('bindE', None)
        self.bindS = kw.get('bindS', None)

        self.delay = self.duration / 3.0

        print(self.widget.card)

    def start(self):
        super(LAnimationTask, self).start()

        anim = Animation(
            x=self.xdest, y=self.ydest, duration=self.duration,
            transition=self.transition)

        if self.bindE is not None:
            anim.bind(on_complete=self.bindE)
        if self.bindS is not None:
            anim.bind(on_start=self.bindS)

        self.widget.pos = self.spos
        anim.bind(on_complete=self.stop)
        anim.start(self.widget)

    def updateDestPos(self, pos):
        self.xdest = pos[0]
        self.ydest = pos[1]

# =============================================================================


class LAnimationMgr(object):
    def __init__(self, **kw):
        super(LAnimationMgr, self).__init__()
        self.tasks = []
        self.callbacks = []
        self.taskQ = LTaskQ()

    def checkRunning(self):
        return len(self.tasks) > 0

    def addEndCallback(self, cb):
        self.callbacks.append(cb)

    def taskEnd(self, task, value):
        if value:
            # print('LAnimationMgr: taskEnd = %s %s' % (task, value))
            self.tasks.remove(task)
            if not self.checkRunning():
                # print('LAnimationMgr: taskEnd ->', len(self.callbacks), 'callbacks') # noqa
                for cb in self.callbacks:
                    cb()
                # print('LAnimationMgr: taskEnd -> callbacks done')
                self.callbacks = []

            # print('Clock.get_fps() ->', Clock.get_fps())

    def taskInsert(self, task):
        self.tasks.append(task)
        task.bind(done=self.taskEnd)
        Clock.schedule_once(lambda dt: self.taskQ.taskInsert(task), 0.016)


LAnimationManager = LAnimationMgr()

# =============================================================================


def LAfterAnimation(task, delay=0.0):
    def dotask():   # noqa
        Clock.schedule_once(lambda dt: task())
    def mkcb(task): # noqa
        def cb(dt):
            if LAnimationManager.checkRunning():
                LAnimationManager.addEndCallback(dotask)
            else:
                dotask()
        return cb
    Clock.schedule_once(mkcb(task), delay)

# =============================================================================


LSoundLoader = SoundLoader

# =============================================================================


class LBoxLayout(BoxLayout, LBase):
    def __init__(self, **kw):
        super(LBoxLayout, self).__init__(**kw)

    def winfo_screenwidth(self):
        return self.size[0]

    def winfo_screenheight(self):
        return self.size[1]

# =============================================================================


def addAnchorOffset(pos, size, anchor):
    # print ('MfxCanvas: anchor=%s' % (anchor))
    x = pos[0]
    y = pos[1]
    xa = 0
    ya = 0
    if anchor == "n":
        ya = -1
    elif anchor == "w":
        xa = -1
    elif anchor == "s":
        ya = 1
    elif anchor == "e":
        xa = 1
    elif anchor == "ne":
        ya = -1
        xa = 1
    elif anchor == "nw":
        ya = -1
        xa = -1
    elif anchor == "se":
        ya = 1
        xa = 1
    elif anchor == "sw":
        ya = 1
        xa = -1

    if xa == 0:
        x = x - size[0] / 2.0
    elif xa == 1:
        x = x - size[0]
    if ya == 0:
        y = y - size[1] / 2.0
    elif ya == 1:
        y = y - size[1]
    return (x, y)

# =============================================================================


def LColorToLuminance(color):
    kc = color
    if isinstance(color, str):
        kc = LColorToKivy(color)
    r = kc[0]
    g = kc[1]
    b = kc[2]
    Y = 0.2989*r + 0.5866*g + 0.1145*b
    return Y

# =============================================================================


def LTextureToLuminance(texture):
    b = texture.pixels
    s = 4
    n = len(b)/1000
    if n > 4:
        s = n - n % 4
    n = 0
    ll = 0
    for i in range(0, len(b), int(s)):
        rr = int.from_bytes(b[i:i+1], byteorder='big', signed=False) / 256.0  # noqa
        gg = int.from_bytes(b[i+1:i+2], byteorder='big', signed=False) / 256.0  # noqa
        bb = int.from_bytes(b[i+2:i+3], byteorder='big', signed=False) / 256.0  # noqa
        ll = ll + LColorToLuminance([rr, gg, bb, 1])
        n += 1
    return (ll/n)

# =============================================================================


def LColorToKivy(outline):
    if (outline[0] == '#'):
        outline = outline[1:]
    ou0 = float(int(outline[0:2], 16)) / 256.0
    ou1 = float(int(outline[2:4], 16)) / 256.0
    ou2 = float(int(outline[4:6], 16)) / 256.0
    ou3 = 1.0
    if len(outline) >= 8:
        ou3 = float(int(outline[6:8], 16)) / 256.0
    return ou0, ou1, ou2, ou3

# =============================================================================


def cardfactor(canvas):
    # heuristic to find some sort of 'fontsize' out of the cardset.
    # We take the original small cardsets as reference and calculate
    # a correction factor.

    def pyth(a, b):
        return math.sqrt(a*a+b*b)

    cardscale = 1.0
    try:
        cs = canvas.wmain.app.images.cs
        # print('Cardset:', cs)
        # print('Cardset:', cs.type)

        cardbase = pyth(73, 97)
        if cs.type == CSI.TYPE_FRENCH:
            cardbase = pyth(73, 97)
        elif cs.type == CSI.TYPE_HANAFUDA:
            cardbase = pyth(64, 102)
        elif cs.type == CSI.TYPE_MAHJONGG:
            cardbase = pyth(38, 54)
        elif cs.type == CSI.TYPE_TAROCK:
            cardbase = pyth(80, 80)
        elif cs.type == CSI.TYPE_HEXADECK:
            cardbase = pyth(50, 80)
        elif cs.type == CSI.TYPE_MUGHAL_GANJIFA:
            cardbase = pyth(80, 80)
        elif cs.type == CSI.TYPE_NAVAGRAHA_GANJIFA:
            cardbase = pyth(80, 80)
        elif cs.type == CSI.TYPE_DASHAVATARA_GANJIFA:
            cardbase = pyth(80, 80)
        elif cs.type == CSI.TYPE_TRUMP_ONLY:
            cardbase = pyth(35, 35)

        si = canvas.wmain.app.images.getSize()
        cardsize = pyth(si[0], si[1])
        cardscale = cardsize/cardbase
    except:	 # noqa: E722
        pass
    return cardscale

# =============================================================================


class LText(Widget, LBase):
    text = StringProperty('')

    def __init__(self, canvas, x, y, **kwargs):
        super(LText, self).__init__(**kwargs)
        # super(LText, self).__init__()

        if 'text' not in kwargs:
            kwargs['text'] = 'X'

        font = 'helvetica'
        fontsize = 18.0
        if 'font' in kwargs:
            font = kwargs['font'][0]
            fontsize = kwargs['font'][1]
            del kwargs['font']

        self.anchor = 'nw'
        if 'anchor' in kwargs:
            self.anchor = kwargs['anchor']

        self.text = kwargs['text']
        self.coreFontSize = fontsize
        self.coreFont = font

        # print('LText: font = %s, font_size = %s' % (font, fontsize))
        # print('LText: text = %s' % (self.text))

        kwargs['font'] = font
        kwargs['font_size'] = fontsize * cardfactor(canvas)

        class MyLabel(Label, LBase):
            pass

        self.label = MyLabel(**kwargs)
        self.label.texture_update()
        self.coreSize = self.label.texture_size
        self.corePos = (x, y)
        self.prnt = canvas

        # print('LText: corePos = %s, coreSize = %s'
        # % (self.corePos, self.coreSize))

        self.size = self.label.texture_size

        self.bind(size=self.updateCanvas)
        self.bind(pos=self.updateCanvas)
        self.bind(text=self.updateCanvas)

    def updateCanvas(self, inst, val):
        self.label.text = self.text
        self.label.texture_update()

        self.coreSize = self.label.texture_size
        cp = addAnchorOffset(self.corePos, self.coreSize, self.anchor)
        cs = self.coreSize

        pos, size = self.prnt.CoreToKivy(cp, cs)
        # print('LText: pos = %s, size = %s' % (pos, size))

        color = LColorToKivy(self.prnt._text_color)
        # print('LText: color = %s' % str(color))
        self.canvas.clear()
        with self.canvas:
            Color(color[0], color[1], color[2], color[3])
            Rectangle(texture=self.label.texture, pos=pos, size=size)

# =============================================================================


class LEvent(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.cardid = -1
        self.char = False
        pass

# =============================================================================


class LLine(Widget, LBase):
    def __init__(self, canvas, args, **kw):
        super(LLine, self).__init__(**kw)

        print('kw = %s%s' % (args, kw))

        default_lwidth = 10
        default_fill = '#ee3344'
        default_ashape = ()
        default_arrow = 'none'

        self.prnt = canvas
        xmin = 100000
        ymin = 100000
        xmax = -100000
        ymax = -100000
        self.corePoly = []
        if isinstance(args[0], list):
            kww = args[1]
            self.lwidth = kww.get('width', default_lwidth)
            self.fill = kww.get('fill', default_fill)
            self.ashape = kw.get('arrowshape', default_ashape)
            self.arrow = kw.get('arrow', default_arrow)

            pts = args[0]
            ipts = iter(pts)
            for x, y in zip(ipts, ipts):
                print('%s.%s' % (x, y))
                self.corePoly.append(x)
                self.corePoly.append(y)
                xmin = min(xmin, x)
                xmax = max(xmax, x)
                ymin = min(ymin, y)
                ymax = max(ymax, y)
        else:
            self.lwidth = kw.get('width', default_lwidth)
            self.fill = kw.get('fill', default_fill)
            self.ashape = kw.get('arrowshape', default_ashape)
            self.arrow = kw.get('arrow', default_arrow)

            for i in range(0, 2):
                x = args[2 * i]
                y = args[2 * i + 1]
                self.corePoly.append(x)
                self.corePoly.append(y)
                xmin = min(xmin, x)
                xmax = max(xmax, x)
                ymin = min(ymin, y)
                ymax = max(ymax, y)

        print('width = %s' % self.lwidth)
        print('color = %s' % self.fill)
        print('arrow = %s' % self.arrow)
        print('ashape = %s' % str(self.ashape))

        self.alist = []
        if self.arrow == 'last':
            self.alist.append(self.corePoly[-2])
            self.alist.append(self.corePoly[-1])
            self.alist.append(self.corePoly[-4])
            self.alist.append(self.corePoly[-3])
        elif self.arrow != 'none':
            self.alist.append(self.corePoly[0])
            self.alist.append(self.corePoly[1])
            self.alist.append(self.corePoly[2])
            self.alist.append(self.corePoly[3])

        self.corePos = (xmin, ymin)
        self.coreSize = (xmax - xmin, ymax - ymin)
        self.pos = self.corePos
        self.size = self.coreSize

        self.bcolor = LColorToKivy(self.fill)

        self.bind(size=self.updateCanvas)
        self.bind(pos=self.updateCanvas)

    def updateCanvas(self, instance, value):
        # size = self.size
        # pos = self.pos

        # Linie:
        poly = None
        poly = []
        dmy, sxy = self.prnt.CoreToKivy(
            (0.0, 0.0), (self.lwidth, self.lwidth))
        wpoly = sxy[1]
        ipts = iter(self.corePoly)
        for x, y in zip(ipts, ipts):
            print('%s.%s' % (x, y))
            xy, dmy = self.prnt.CoreToKivy((x, y))
            poly.append(xy[0])
            poly.append(xy[1])

        def rot(x, y, a):
            x1 = x * math.cos(a) + y * math.sin(a)
            y1 = y * math.cos(a) - x * math.sin(a)
            return (x1, y1)

        # Pfeil:
        PI = 3.1415926
        atrio = None
        atrio = []
        if (len(self.ashape) > 2):
            dx = (self.alist[0] - self.alist[2])
            dy = (self.alist[1] - self.alist[3])
            if (dx == 0.0):
                if (dy > 0.0):
                    ang = -PI / 2.0
                else:
                    ang = PI / 2.0
            else:
                ang = math.atan(dy / dx)
            if (dx > 0.0):
                ang = ang + PI

            # (kante, winkel?)
            x = self.ashape[0] * math.cos(self.ashape[1] * PI / 360.0)
            y = 2.0 * self.ashape[0] * math.sin(self.ashape[1] * PI / 360.0)
            # (länge, breite?)
            # x = self.ashape[0]
            # y = self.ashape[1]
            o = self.ashape[2]
            axy, dmy = self.prnt.CoreToKivy((self.alist[0], self.alist[1]))
            dmy, asxy = self.prnt.CoreToKivy((0, 0), (x, y))
            dmy, aoff = self.prnt.CoreToKivy((0, 0), (o, o))
            print('asxy=%s' % str(asxy))

            x1, y1 = rot(-aoff[0], 0.0, ang)
            atrio.append(x1 + axy[0])
            atrio.append(y1 + axy[1])
            x1, y1 = rot(asxy[0] - aoff[0], asxy[1], ang)
            atrio.append(x1 + axy[0])
            atrio.append(y1 + axy[1])
            x1, y1 = rot(asxy[0] - aoff[0], -asxy[1], ang)
            atrio.append(x1 + axy[0])
            atrio.append(y1 + axy[1])

        self.canvas.clear()
        with self.canvas:
            Color(self.bcolor[0], self.bcolor[1],
                  self.bcolor[2], self.bcolor[3])
            Line(points=poly, width=wpoly, cap='none', joint='bevel')
            if (len(atrio) > 2):
                Triangle(points=atrio)

# =============================================================================


class LRectangle(Widget, LBase):
    def __init__(self, prnt, args, **kw):
        super(LRectangle, self).__init__(**kw)
        self.prnt = prnt

        # print('width   %s' % kw['width'])
        # print('outline %s' % kw['outline'])
        # print('fill    %s' % kw['fill'])

        width = float(kw.get('width', 10.0))

        bcolor = kw.get('outline', '#ffa000a0')
        if (not bcolor or len(bcolor) < 7):
            bcolor = '#ffa000a0'

        fcolor = kw.get('fill', '#00aaff20')
        if (not fcolor or len(fcolor) < 7):
            fcolor = '#00aaff20'

        self.group = None
        if 'group' in kw:
            self.group = kw['group']

        xmin = float(args[0])
        ymin = float(args[1])
        xmax = float(args[2])
        ymax = float(args[3])

        # print ('LRectangle: min = %s.%s' % (xmin, ymin))
        # print ('LRectangle: max = %s.%s' % (xmax, ymax))
        # print ('LRectangle: border = %s' % (width))

        self.border = width
        self.fcolor = LColorToKivy(fcolor)
        self.bcolor = LColorToKivy(bcolor)

        self.corePos = (xmin, ymin)
        self.coreSize = (xmax - xmin, ymax - ymin)
        self.pos = self.corePos
        self.size = self.coreSize
        self.topleft = (xmin + width / 2.0, ymin + width / 2.0)
        self.bottomright = (xmax - width / 2.0, ymax - width / 2.0)
        self.poly = None

        self.bind(size=self.updateCanvas)
        self.bind(pos=self.updateCanvas)

    def updateCanvas(self, instance, value):
        # print('LRectangle: updateCanvas')

        pos, size = self.prnt.CoreToKivy(self.corePos, self.coreSize)
        bpos, dmy = self.prnt.CoreToKivy(self.topleft)
        tpos, dmy = self.prnt.CoreToKivy(self.bottomright)

        poly = [bpos[0], bpos[1],
                tpos[0], bpos[1],
                tpos[0], tpos[1],
                bpos[0], tpos[1],
                bpos[0], bpos[1]]

        cf = cardfactor(self.prnt)
        dmy, brd = self.prnt.CoreToKivy(
            (0.0, 0.0), (self.border, self.border))
        border = brd[1] * cf

        self.canvas.clear()
        with self.canvas:
            Color(self.fcolor[0], self.fcolor[1],
                  self.fcolor[2], self.fcolor[3])
            Rectangle(pos=pos, size=size)
            Color(self.bcolor[0], self.bcolor[1],
                  self.bcolor[2], self.bcolor[3])
            Line(points=poly, width=border)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.group is not None:
                logging.info('LRectangle: self=%s group=%s' %
                             (self, self.group))
                if '<1>' in self.group.bindings:
                    # logging.info('LRectangle: size=%s' % (self.size))
                    ppos, psize = self.group.canvas.KivyToCore(touch.pos)
                    event = LEvent()
                    event.x = ppos[0]
                    event.y = ppos[1]
                    if touch.is_double_tap:
                        self.group.bindings['<Double-1>'](event)
                    else:
                        self.group.bindings['<1>'](event)
                    return True
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.group is not None:
                logging.info('LRectangle: self=%s group=%s' %
                             (self, self.group))
                if '<ButtonRelease-1>' in self.group.bindings:
                    ppos, psize = self.group.canvas.KivyToCore(touch.pos)
                    event = LEvent()
                    event.x = ppos[0]
                    event.y = ppos[1]
                    self.group.bindings['<ButtonRelease-1>'](event)
                    return True
        return False

# =============================================================================
# Represents a Card as Kivy Window. Will contain an LImage item as child.
# Images are managed in cards.py according to the cards state. Processes
# Events/Action on the card or other images, as LImage is designed to not
# process events. Should not take more than one child (LImage) at a time.


class LImageItem(BoxLayout, LBase):
    def __init__(self, **kw):
        super(LImageItem, self).__init__(**kw)
        self.game = None
        self.card = None
        self.group = None
        self.image_type = "undefined"
        if 'game' in kw:
            self.game = kw['game']
        if 'card' in kw:
            self.card = kw['card']
            self.image_type = "card"
        if 'group' in kw:
            self.group = kw['group']
        if 'image_type' in kw:
            self.image_type = kw['image_type']

        self.dragstart = None
        # ev. noch globales cache für stacks->game und cards->stack
        # einrichten. Aber: stacks hängt vom jeweiligen spiel ab.

    def __str__(self):
        return f'<LImageItem @ {hex(id(self))}>'

    def get_image_type(self):
        return self.image_type

    '''
    NOTE:
    The following code binds kivy events to tk-like (?) events used
    in common code. There are several problems
    - EVENT_HANDLED and EVENT_PROPAGATE constants are defined separately in
      different ui implementations, but are used in common code (stack.py,
      game/__init__.py, many game implementations: (241 functions!))
    - EVENT_PROPAGATE is defined to 'None', which is highly unspecific.
      (conditions would evaluate to False, empty returns of event function
      implicitly return EVENT_PROPAGATE).
    - Most events return EVENT_HANDLED even if they did not change anything
      in current situations. I would expect specifically for stack base cards
      that they return HANDLE_PROPAGATE if nothing happened.
    - stack __defaultclickhandler__ returns EVENT_HANDLED in any case so some
      code here is obsolete or for future.
    - A pragmatic way to handle this: If an empty stack is still empty
      after the click then we propagate otherwise not.
    LB241111.
    '''

    def send_event_pressed_n(self, event, n):
        r = EVENT_PROPAGATE
        if self.group and n in self.group.bindings:
            r = self.group.bindings[n](event)
        return r

    def send_event_pressed(self, touch, event):

        r = EVENT_PROPAGATE
        if touch.is_double_tap:
            r = self.send_event_pressed_n(event, '<Double-1>')
        else:
            button = 'left'
            if 'button' in touch.profile:
                button = touch.button
            if button == 'left':
                r = self.send_event_pressed_n(event, '<1>')
            if button == 'middle':
                r = self.send_event_pressed_n(event, '<2>')
            if button == 'right':
                r = self.send_event_pressed_n(event, '<3>')
        return r

    def on_touch_down(self, touch):

        # print('LCardImage: size = %s' % self.size)
        if self.collide_point(*touch.pos):

            if (self.game):
                for stack in self.game.allstacks:
                    for i, cur_card in enumerate(stack.cards):
                        if cur_card == self.card:
                            print('LCardImage: stack = %s' % stack)
                            print('LCardImage: touch = %s' % str(touch))
                            ppos, psize = self.game.canvas.KivyToCore(
                                touch.pos, self.size)
                            event = LEvent()
                            event.x = ppos[0]
                            event.y = ppos[1]
                            self.dragstart = touch.pos
                            event.cardid = i
                            r = self.send_event_pressed(touch, event)
                            if r == EVENT_HANDLED:
                                AndroidScreenRotation.lock(toaster=False)
                                print('grab')
                                touch.grab(self)
                                return True
                            return False

            if self.group is not None:
                print('LCardImage: self=%s group=%s' % (self, self.group))
                if '<1>' in self.group.bindings:
                    ppos, psize = self.group.canvas.KivyToCore(
                        touch.pos, self.size)
                    event = LEvent()
                    event.x = ppos[0]
                    event.y = ppos[1]
                    r = self.group.bindings['<1>'](event)
                    if r == EVENT_HANDLED:
                        if len(self.group.stack.cards) > 0:
                            return True
                    return False

            if self.card is None:
                return False
            if self.game is None:
                return False

        # print('LCardImage: touch_down on %s' % str(touch.pos))
        return False

    def send_event_released_1(self, event):
        r = EVENT_PROPAGATE
        if self.group and '<ButtonRelease-1>' in self.group.bindings:
            r = self.group.bindings['<ButtonRelease-1>'](event)
        return r

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # ungrab. this stops move events after a drag.
            print('ungrab')
            touch.ungrab(self)
            return True

        if self.collide_point(*touch.pos):

            if (self.game):
                for stack in self.game.allstacks:
                    for i, cur_card in enumerate(stack.cards):
                        if cur_card == self.card:
                            print('LCardImage: stack = %s' % stack)
                            ppos, psize = self.game.canvas.KivyToCore(
                                touch.pos, self.size)
                            event = LEvent()
                            event.x = ppos[0]
                            event.y = ppos[1]
                            event.cardid = i
                            r = self.send_event_released_1(event)
                            if r == EVENT_HANDLED:
                                return True
                            return False

            if self.group is not None:
                print('LCardImage: self=%s group=%s' % (self, self.group))
                if '<ButtonRelease-1>' in self.group.bindings:
                    ppos, psize = self.group.canvas.KivyToCore(
                        touch.pos, self.size)
                    event = LEvent()
                    event.x = ppos[0]
                    event.y = ppos[1]
                    r = self.group.bindings['<ButtonRelease-1>'](event)
                    if r == EVENT_HANDLED:
                        if len(self.group.stack.cards) > 0:
                            return True
                    return False

            if self.card is None:
                return False
            if self.game is None:
                return False

        # print('LCardImage: touch_up on %s' % str(touch.pos))
        return False

    def on_touch_move(self, touch):
        # behandeln nur wenn grabbed
        if touch.grab_current is not self:
            return False
        if 'pos' not in touch.profile:
            return False

        print('LCardImage: touch_move on %s' % str(touch.pos))

        for stack in self.game.allstacks:
            for i, cur_card in enumerate(stack.cards):
                if cur_card == self.card:
                    print('LCardImage: stack = %s/%s' % (stack, touch))
                    ppos, psize = self.game.canvas.KivyToCore(
                        touch.pos, self.size)
                    event = LEvent()
                    event.x = ppos[0]
                    event.y = ppos[1]
                    event.cardid = i
                    stack._motionEventHandler(event)
                    return True

        # print('LCardImage: touch_move on %s' % str(touch.pos))
        return False

# =============================================================================
# Treeview


class LTreeRoot(TreeView, LBase):
    def __init__(self, **kw):
        super(LTreeRoot, self).__init__(**kw)
        self.kw = kw

    def closeLastNode(self):
        ret = False
        lastopen = None
        for ti in reversed(self.children):
            if isinstance(ti, LTreeNode):
                if ti.is_open:
                    lastopen = ti

        if lastopen is not None:
            self.toggle_node(lastopen)
            self.select_node(lastopen)
            ret = True

        return ret

class LTreeSliderNode(Slider, TreeViewNode, LBase):

    def __init__(self, **kw):
        self.variable = None
        if 'variable' in kw:
            self.variable = kw['variable']
            del kw['variable']
        if 'setup' in kw:
            self.min  = kw['setup'][0]
            self.max  = kw['setup'][1]
            self.step = kw['setup'][2]
            del kw['setup']

        super(LTreeSliderNode, self).__init__(markup=True, **kw)
        self.value = self.variable.value
        self.height = '24sp'
        self.background_width = '12sp'
        self.background_height = '12sp'
        self.cursor_height = '12sp'
        self.cursor_width = '12sp'

    def on_value(self,obj,val):
        print (val)
        self.variable.value = val


class LTreeNode(ButtonBehavior, TreeViewLabel, LBase):

    # def __init__(self, gameview, **kw):
    def __init__(self, **kw):
        self.command = None
        if 'command' in kw:
            self.command = kw['command']
        self.variable = None
        if 'variable' in kw:
            self.variable = kw['variable']
        if 'value' in kw:
            self.value = kw['value']
        if ('text' in kw):
            self.title = kw['text']

        super(LTreeNode, self).__init__(markup=True, **kw)

        if self.variable:
            self.variable.bind(value=self.onVarChange)
            self.onVarChange(self.variable, self.variable.value)

        # self.gameview = gameview
        self.coreFont = self.font_size
        # self.scaleFont(self.gameview.size[1])
        # self.gameview.bind(size=self.scaleFontCB)
        # nicht skalieren!

        self.bind(on_release=self.on_released)
        self.bind(is_selected=self.onSelect)
        self.bind(is_open=self.onOpen)

    def onVarChange(self, instance, value):
        # print('LTreeNode: onVarChange(%s, %s, %s)'
        # % (instance, value, type(value)))
        if isinstance(value, bool):
            self.setCheck(value)
        elif isinstance(value, int):
            self.setVal(value)
        elif isinstance(value, str):
            self.setVal(value)
        # if isinstance(value), unicode):
        #     self.setVal(value)

    def setCheck(self, value):
        # print('LTreeNode: setCheck(%s)' % value)
        if value:
            # self.text = '+ '+self.title
            self.text = '[b]+[/b] ' + self.title
        else:
            self.text = '- ' + self.title
        self.texture_update()

    def setVal(self, value):
        # print('LTreeNode: setVal(%s)' % value)
        if value == self.value:
            # fs = str(int(self.font_size+2))
            # print ('%s.%s' % (self.font_size, fs))
            # self.text = '[size='+fs+'][b]'+self.title+'[/b][/size]'
            # self.text = 'o '+self.title
            self.text = '[b]o[/b] ' + self.title
            # self.text = u'\u25cf '+self.title  # unicode filled circle
        else:
            self.text = self.title
            self.text = '    ' + self.title
            # self.text = u'\u25cb  '+self.title # unicode open circle
        self.texture_update()

    # font skalierung.

    def scaleFont(self, value):
        self.font_size = int(self.coreFont * value / 550.0)

    def scaleFontCB(self, instance, value):
        self.scaleFont(value[1])

    # benutzer interaktion.

    def onSelect(self, instance, val):
        if val:
            print('select %s' % self.title)
        else:
            print('deselect %s' % self.title)
        pass

    def collapseChildren(self, deep=False):

        def cc(p, n):
            for c in n.nodes:
                if c.is_open:
                    cc(p, c)
                    p.toggle_node(c)

        p = self.parent
        if p and isinstance(p, LTreeRoot):
            for n in self.nodes:
                if n.is_open:
                    # n.collapseChildren()   # ginge nur mit LTreeNode!
                    if deep:
                        cc(p, n)            # geht mit allen TreeViewNode
                    p.toggle_node(n)

    def collapseSiblings(self, deep=True):

        def cc(p, n):
            for c in n.nodes:
                if c.is_open:
                    cc(p, c)
                    p.toggle_node(c)

        p = self.parent
        if p and isinstance(p, LTreeRoot):
            # print('expand: LTreeRoot')
            for n in p.root.nodes:
                # print('expand: -> check %s' % n.title)
                if n != self and n.is_open and n.level >= self.level:
                    # print('expand: -> close %s' % n.title)
                    if deep:
                        cc(p, n)
                    p.toggle_node(n)

            pn = self.parent_node
            if pn and isinstance(pn, LTreeNode):
                # print('expand: LTreeNode')
                for n in pn.nodes:
                    # print('expand: -> check %s' % n.title)
                    if n != self and n.is_open and n.level >= self.level:
                        # print('expand: -> close %s' % n.title)
                        if deep:
                            cc(p, n)
                        p.toggle_node(n)

    def onOpen(self, instance, val):
        if val:
            # print('expand %s, %s' % (self.level, self.title))
            self.collapseSiblings(deep=False)
        else:
            # print('collapse %s, %s' % (self.level, self.title))
            pass

    def on_released(self, v):
        if self.command:
            Clock.schedule_once(self.commandCB, 0.1)
        else:
            Clock.schedule_once(self.toggleCB, 0.1)

    def commandCB(self, d):
        self.command()

    def toggleCB(self, d):
        # hier könnte der knoten ev. auch neu aufgebaut werden ?!
        self.parent.toggle_node(self)

# =============================================================================


class LTopLevelContent(BoxLayout, LBase):
    def __init__(self, **kw):
        super(LTopLevelContent, self).__init__(**kw)

        # Macht die Hintergrundfarbe der TopLevel (Dialog-) Fenster.
        with self.canvas.before:
            Color(0.45, 0.5, 0.5, 1.0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def wm_minsize(self, w, h):
        pass

# =============================================================================


class LTopLine(ButtonBehavior, Label, LBase):

    def __init__(self, **kw):
        super(LTopLine, self).__init__(**kw)
        with self.canvas.before:
            Color(0.45, 0.3, 0.3, 1.0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        self.maxlines = 0
        self.halign = 'center'
        self.valign = 'center'

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_size(self, o, s):
        self.text_size = s

    def on_press(self):
        print('press')

    def on_release(self):
        print('release')

# =============================================================================


class LTopLevelBase(BoxLayout, LBase):
    def __init__(self, title='', **kw):
        super(LTopLevelBase, self).__init__(orientation="vertical", **kw)
        self.title = title
        self.titleline = LTopLine(text=title, size_hint=[1.0, 0.15])
        self.content = LTopLevelContent(orientation="vertical", **kw)
        self.add_widget(self.titleline)
        self.add_widget(self.content)

# =============================================================================


class LTopLevel0(LTopLevelBase, LBase):
    def __init__(self, top, title='', **kw):
        super(LTopLevel0, self).__init__(title=title, **kw)

        self.main = top
        self.titleline.bind(on_press=self.onClick)
        self.main.pushWork(self.title, self)

    def onClick(self, event):
        print('LTopLevel: onClick')
        self.main.popWork(self.title)

# =============================================================================


class LTopLevel(LTopLevelBase, LBase):
    def __init__(self, parent, title='', **kw):
        super(LTopLevel, self).__init__(title=title, **kw)
        self.mainwindow = parent

    def processAndroidBack(self):
        ret = False
        # try to collapse the last open tree node
        # the treeview will be located inside of a scrollview
        # (-> menubar.py)
        for c in self.content.children:
            # print("childitem: %s" % str(c))
            if isinstance(c, LScrollView):
                for t in reversed(c.children):
                    # print("  childitem: %s" % str(t))
                    if isinstance(t, LTreeRoot):
                        ret = t.closeLastNode()
            if isinstance(c, BoxLayout):
                for t in reversed(c.children):
                    # print("  childitem: %s" % str(t))
                    if isinstance(t, LPopCommander):
                        ret = t.pop()
                    pass
        return ret

# =============================================================================


class LMenuBar(BoxLayout, LBase):
    def __init__(self, **kw):
        super(LMenuBar, self).__init__(**kw)
        self.menu = None
        self.size_hint = (1.0, 0.08)

    def setMenu(self, menu):
        print('LMenuBar: setMenu %s, %s' % (self, menu))

        # Letztes Menu entfernen
        last = self.menu
        if (last is not None):
            self.remove_widget(last)
            self.menu = None

        # Neues Menu einfügen
        if (menu is not None):
            self.add_widget(menu)
            self.menu = menu
            menu.setBar(self)

    def getMenu(self):
        return self.menu

# =============================================================================


class LMenu(ActionView, LBase):
    def __init__(self, prev, **kw):
        super(LMenu, self).__init__(**kw)

        class MyActionPrev(ActionPrevious, LBase):
            pass

        kw['app_icon'] = 'data/images/icons/48x48/pysol.png'
        kw['with_previous'] = prev
        kw['size_hint'] = (.01, 1)
        self.ap = MyActionPrev(**kw)
        self.add_widget(self.ap)
        self.bar = None
        self.uppermenu = None

    def addItem(self, mi):
        # print ('LMenu: addItem '+str(mi)+' '+str(self.bar))
        mi.setBar(self.bar)
        self.add_widget(mi)

    def setBar(self, bar):
        # print ('LMenu: setBar %s, %s' % (self, bar))
        self.bar = bar

    def prev(self, menu):
        # print ('LMenu: prev = %s' % menu)
        self.uppermenu = menu
        self.ap.bind(on_release=self.upper)
        pass

    def upper(self, event):
        print('upper')
        self.bar.setMenu(self.uppermenu)

    def delete(self, pos, mode):
        # print ('LMenu(%s): delete(%s, %s)' % (self, pos, mode))

        items = []
        menues = []
        for c in self.children:
            if isinstance(c, LMenuItem):
                # print ('LMenu: to delete child %s' % c)
                items.append(c)
            elif isinstance(c, LMenu):
                # print ('LMenu: to delete child %s' % c)
                menues.append(c)
            else:
                # print ('LMenu: unknown child %s' % c)
                pass

        for c in items:
            # print ('LMenu: delete child %s' % c)
            self.clear_widgets([c])
        for c in menues:
            # print ('LMenu: delete child %s' % c)
            self.clear_widgets([c])
            c.delete(pos, mode)

    # def __str__(self):
    #   return hex(id(self))

# =============================================================================


class LMenuItem(ActionButton, LBase):

    def __init__(self, menu, **kw):
        super(LMenuItem, self).__init__(**kw)
        # super(LMenuItem, self).__init__()
        self.bar = None
        self.submenu = None
        self.menu = menu
        self.menu.addItem(self)
        self.minimum_width = '200sp'
        if 'command' in kw:
            self.setCommand(kw['command'])
        if 'submenu' in kw:
            self.setSubMenu(kw['submenu'])

    def setBar(self, bar):
        # print ('LMenuItem: setBar %s, %s' % (self, bar))
        self.bar = bar

    def onClick(self, event):
        # print('LMenuItem: onClick')
        # print('LMenuItem: submenu vorh: '+str(self.submenu))
        self.bar.setMenu(self.submenu)
        return True

    def setSubMenu(self, submenu):
        # print('LMenuItem: setSubMenu')
        self.submenu = submenu
        # print('LMenuItem: setSubMenu: '+str(self.submenu))
        self.submenu.prev(self.menu)
        self.submenu.setBar(self.bar)
        self.bind(on_release=self.onClick)
        pass

    def setCommand(self, cmd):
        print('LMenuItem: setCommand')
        self.bind(on_release=cmd)

    # def __str__(self):
    #   return hex(id(self))

# =============================================================================


class LScrollView(ScrollView, LBase):
    def __init__(self, **kw):
        super(LScrollView, self).__init__(**kw)
        self.delayDown = False
        self.touch = None

    def delayReset(self, dt):
        if not self.delayDown:
            return
        self.delayDown = False
        ScrollView.on_touch_down(self, self.touch)

    # Scroll ist original viel zu flink auf den Touchgeräten.
    # Wir versuchen das hier etwas abzuschwächen.

    def on_touch_down(self, touch):
        self.delayDown = True
        self.touch = touch
        Clock.schedule_once(self.delayReset, 0.15)

    def on_touch_up(self, touch):
        if self.delayDown:
            ScrollView.on_touch_down(self, self.touch)
        self.delayDown = False
        return ScrollView.on_touch_up(self, touch)

    def on_touch_move(self, touch):
        return ScrollView.on_touch_move(self, touch)

# =============================================================================


class LWorkWindow(Widget):
    def __init__(self):
        super(LWorkWindow, self).__init__()

        # beispiel zu canvas (hintergrund)
        with self.canvas.before:
            Color(0, 1, 1, 0.4)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        print('LWorkWindow: touch_down on %s' % str(touch.pos))
        # return True

# =============================================================================
# TkBase:
# When using (introducing) new methods of the main tk window in the tk-version
# please check if that method is catched here. And provide appropriate
# implementation if needed. Otherwise the android version will crash.
# LB241029.


class LTkBase:
    # Tk Emulation needs.
    def __init__(self):
        self.title = "default title"
        self.icontitle = "default title"
        logging.info("LTkBase: __init__()")
        self.sleeping = False
        self.in_loop = False
        self.screenSize = (1000, 1000)

    def cget(self, strg):
        return False

    def wm_title(self, strg):
        self.title = strg
        logging.info("LTkBase: wm_title %s" % strg)
        if (self.app):
            # self.app.top.topLine.text = strg
            self.app.top.getMenu().ap.title = strg

    def wm_iconname(self, strg):
        self.icontitle = strg
        logging.info("LTkBase: wm_iconname %s" % strg)

    def eval_screen_dim(self, size):
        self.screenSize = size
        if get_platform() == 'android':
            from jnius import autoclass
            from jnius import cast
        else:
            return

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        currentActivity = cast(
            'android.app.Activity', PythonActivity.mActivity)
        wm = currentActivity.getWindowManager()
        d = wm.getDefaultDisplay()

        self.screenSize = (d.getWidth(), d.getHeight())

    def winfo_screenwidth(self):
        logging.info("LTkBase: winfo_screenwidth %s" % str(self.size[0]))
        return self.size[0]

    def winfo_screenheight(self):
        logging.info("LTkBase: winfo_screenheight %s" % str(self.size[1]))
        return self.size[1]

    def winfo_screendepth(self):
        return 32

    def wm_minsize(self, x, y):
        pass

    def option_add(self, a, b, c):
        pass

    def option_get(self, a, b):
        return 0

    def wm_withdraw(self):
        logging.info("LTkBase: wm_withdraw")
        pass

    def busyUpdate(self):
        print('LTkBase: busyUpdate()')
        pass

    def grid_columnconfigure(self, a, weight):
        pass

    def grid_rowconfigure(self, a, weight):
        pass

    def connectApp(self, app):
        logging.info("LTkBase: connectApp %s" % str(app))
        self.app = app
        pass

    def wm_geometry(self, val):
        logging.info("LTkBase: wm_geometry %s" % str(val))
        pass

    def update_idletasks(self):
        # logging.info("LTkBase: update_idletasks")
        try:
            if len(EventLoop.event_listeners) > 0:
                self.in_loop = True
                EventLoop.idle()
                self.in_loop = False
            else:
                logging.info("LTkBase: update_idletasks: terminating")
        except Exception:
            self.in_loop = False
            logging.info("LTkBase: update_idletasks: exception")

    def wm_state(self):
        return ""

    def wm_deiconify(self):
        pass

    def mainloop(self):
        logging.info("LTkBase: mainloop")
        pass

    def quit(self):
        logging.info("LTkBase: quit")
        stopTouchApp()

    def interruptSleep(self):
        # logging.info('LTkBase: interruptSleep')
        self.update_idletasks()
        # self.sleep_var = 1

    def mainquit(self):
        logging.info('LTkBase: mainquit')
        lapp = App.get_running_app()
        lapp.mainloop.send(None)    # Spielprozess verlassen

    def onWakeUp(self, dt):
        self.sleeping = False

    def sleep(self, seconds):
        logging.info('LTkBase: sleep %s seconds' % seconds)
        self.sleeping = True
        Clock.schedule_once(self.onWakeUp, seconds)
        while self.sleeping:
            # time.sleep(0.05)
            self.in_loop = True
            EventLoop.idle()
            self.in_loop = False

    def waitCondition(self, condition, swallow=False, pickup=False):
        # logging.info('LTkBase: wait condition start')
        while condition():
            self.in_loop = True
            if swallow:  # eat picked input up
                for provider in EventLoop.input_providers:
                    provider.update(dispatch_fn=lambda *x: None)
            EventLoop.idle()
            if pickup:  # pick input from os
                if EventLoop.window:
                    EventLoop.window.mainloop()
            self.in_loop = False
        # logging.info('LTkBase: wait condition end')

    def waitAnimation(self, swallow=False, pickup=False):
        self.waitCondition(LAnimationManager.checkRunning,
                           swallow=swallow,
                           pickup=pickup)

    def tkraise(self):
        pass

    def winfo_ismapped(self):
        return True
        # ???

    def attributes(self, *args):
        pass

# =============================================================================


class LStack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, key, item):
        self.items.append((key, item))

    def pop(self, key):
        for i, t in enumerate(self.items):
            if (t[0] == key):
                self.items.pop(i)
                return t[1]
        return None

    def peek(self, key):
        for t in self.items:
            if (t[0] == key):
                return t
        return None

    def size(self):
        return len(self.items)

# =============================================================================


class LMainWindow(BoxLayout, LTkBase):

    longPress = NumericProperty(0)

    def __init__(self, **kw):
        super(LMainWindow, self).__init__(orientation='vertical')
        LTkBase.__init__(self)
        self.menuArea = LMenuBar()
        self.workContainer = LBoxLayout(orientation='horizontal')
        self.workContainerO = LBoxLayout(orientation='horizontal')
        self.workContainer1 = LBoxLayout(orientation='vertical')
        self.workArea = None
        self.toolBar = None
        self.toolBarPos = 0
        self.bindings = {}
        self._w = '.'

        self.add_widget(self.menuArea)
        self.add_widget(self.workContainerO)
        self.workContainerO.add_widget(self.workContainer)

        self.workStack = LStack()
        self.app = None

        '''
        from kivy.graphics import opengl_utils
        print('OPENGL support:')
        print(opengl_utils.gl_get_extensions())
        '''

        # self.touches = []

        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.pos = (0, 0)
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_motion(self, m):
        print('on_motion', m)
        pass

    # Events.

    def on_touch_down(self, touch):
        ret = False
        if super().on_touch_down(touch):
            return True

        # print(dir(touch))

        # multitouch detection
        '''
        #print("MainWindow touch_down",touch.ox,touch.oy)
        #print("MainWindow touch_down",touch.sx,touch.sy)
        #print("MainWindow touch_down",touch.px,touch.py)
        self.touches.append(touch)
        print("touches cnt = ",len(self.touches))
        '''
        # multiclick detection

        if touch.is_double_tap:
            # print('Touch is a double tap !')
            # print(' - interval is', touch.double_tap_time)
            # print(' - distance betw. previous is', touch.double_tap_distance)
            AndroidScreenRotation.unlock()
        '''
        if touch.is_triple_tap:
            print('Touch is a triple tap !')
            AndroidScreenRotation.unlock()
        '''

        # (Eventloop reentrancy check)
        if self.in_loop:
            return ret

        # (demo mode stop - nur auf spielfläche)
        if '<KeyPress>' in self.bindings:
            pgs = self.workStack.peek('playground')
            if pgs:
                pg = pgs[1]
                if pg.collide_point(*touch.pos):
                    event = LEvent()
                    event.char = True
                    self.bindings['<KeyPress>'](event)

        # standard notifikation:
        for c in self.children:
            ret = c.on_touch_down(touch)
            if ret:
                break
        return ret

    def on_touch_up(self, touch):
        ret = False
        if super().on_touch_up(touch):
            return True

        # long press only on playground.
        pgs = self.workStack.peek('playground')
        if pgs:
            pg = pgs[1]
            if pg.collide_point(*touch.pos):
                if (touch.time_end-touch.time_start) > 2.5:
                    self.longPress = touch.time_end

        # standard notifikation:
        for c in self.children:
            ret = c.on_touch_up(touch)
            if ret:
                break

        # multitouch support
        '''
        self.touches = [xx for xx in self.touches if xx != touch]
        print("touches cnt = ",len(self.touches))
        '''
        return ret

    def on_longPress(self, instance, timestamp):
        print('longPressed at {time}'.format(time=timestamp))

    # Menubar:

    def setMenu(self, menu):
        self.menuArea.setMenu(menu)

    def getMenu(self):
        return self.menuArea.getMenu()

    # Toolbar:

    def setTool(self, toolbar, pos=0):
        if (toolbar is not None):
            self.toolBar = toolbar
        self.toolBarPos = pos
        self.rebuildContainer()

    # Workarea:

    def removeContainer(self):
        self.workContainer.clear_widgets()
        self.workContainerO.clear_widgets()
        self.workContainer1.clear_widgets()

    def buildContainer(self):
        # (hbox)
        if self.toolBar is not None and self.toolBarPos == 3:
            self.workContainerO.add_widget(self.toolBar)
        self.workContainerO.add_widget(self.workContainer1)
        if self.toolBar is not None and self.toolBarPos == 4:
            self.workContainerO.add_widget(self.toolBar)
        # (vbox)
        if self.toolBar is not None and self.toolBarPos == 1:
            self.workContainer1.add_widget(self.toolBar)
        self.workContainer1.add_widget(self.workContainer)
        if self.toolBar is not None and self.toolBarPos == 2:
            self.workContainer1.add_widget(self.toolBar)
        # (workcontainer)
        for w in self.workStack.items:
            self.workContainer.add_widget(w[1])

    def rebuildContainer(self):
        LAfterAnimation(self.removeContainer)
        LAfterAnimation(self.buildContainer)

    def pushWork(self, key, widget):
        if (widget):
            self.workStack.push(key, widget)
            self.rebuildContainer()

    def popWork(self, key):
        w = None
        if self.workStack.size() > 0:
            w = self.workStack.pop(key)
            self.rebuildContainer()
        return w

    def setWork(self, key, widget):
        self.pushWork(key, widget)

    def getWork(self, key):
        return self.workStack.peek(key)

    def processAndroidBack(self):
        ret = False
        # try to close currently open popup windows, one by one
        r = range(len(self.workStack.items))
        rr = reversed(r)
        for i in rr:
            t = self.workStack.items[i]
            # print("stackkey:  %s" % str(t[0]))
            # print("stackitem: %s" % str(t[1]))
            if t[0] == 'playground':
                pass
            else:
                if isinstance(t[1], LTopLevel):
                    ret = t[1].processAndroidBack()
                if not ret:
                    self.popWork(t[0])
                    ret = True
            if ret:
                break
        return ret

# =============================================================================


class LApp(App):

    # Handling of android return key
    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            # Back key of Android.
            lapp = App.get_running_app()
            app = lapp.app
            if app is None:
                return False  # delegate

            # redirect to mainwindow to close popups, tree nodes
            # and html pages.
            if (self.mainWindow.processAndroidBack()):
                return True  # consumed

            # redirect to game to undo last step
            app.menubar.mUndo()
            return True     # consumed
        return False    # delegate

    def __init__(self, args):
        super(LApp, self).__init__()
        self.args = args
        self.title = "PySolFC"
        self.baseWindow = FloatLayout()

    def build(self):
        class MyLabel(Label, LBase):
            def __init__(self, **kw):
                super(MyLabel, self).__init__(**kw)
                with self.canvas.before:
                    Color(0.05, 0.05, 0.05, 1)
                    self.rect = Rectangle(pos=self.pos, size=self.size)
                self.bind(pos=self.update_rect)
                self.bind(size=self.update_rect)

            def update_rect(self, *args):
                self.rect.pos = self.pos
                self.rect.size = self.size

        # self.startLabel = MyLabel(text="PySolFC", color=[0.9,0.9,0.9,1]) # noqa
        # self.baseWindow.add_widget(self.startLabel)

        return self.baseWindow

    def app_start(self, *args):
        logging.info("LApp: app_start")
        logging.info('top = %s' % str(self.baseWindow))

        self.mainWindow = LMainWindow()
        Cache.register('LAppCache', limit=10)
        Cache.append('LAppCache', 'baseWindow', self.baseWindow, timeout=0)
        Cache.append('LAppCache', 'mainWindow', self.mainWindow, timeout=0)
        Cache.append('LAppCache', 'mainApp', self, timeout=0)
        self.startCode = 0
        Window.bind(on_keyboard=self.key_input)

        from pysollib.app import Application
        from pysollib.main import pysol_init

        self.app = app = Application()
        app.top = self.baseWindow
        self.startCode = pysol_init(app, self.args)
        if self.startCode > 0:
            logging.info("LApp: on_start fails")
            return

        self.mainloop = self.app.mainproc()  # Einrichten
        logging.info("LApp: mainproc initialised sending start signal")
        self.mainloop.send(None)             # Spielprozess starten
        logging.info("LApp: app_start processed, returned to kivy mainloop")

        self.baseWindow.add_widget(self.mainWindow,index=1) # noqa
        self.baseWindow.opacity = 0
        anim = Animation(opacity=1,duration=0.7) # noqa
        Clock.schedule_once(lambda dt: anim.start(self.baseWindow),0.3) # noqa
        Clock.schedule_once(lambda dt: set_fullscreen(True),0.0) # noqa

    def on_start(self):
        logging.info("LApp: on_start")

        # Window.update_viewport()
        # There is still a black screen gap between android splash
        # and displayed app window. But seems to depend on the device
        # used. There are actual discussions running on that. Some
        # suggest its a SDL2 issue.

        debug = False
        if debug:
            # Investigation of the black screen gap on start.
            # For testing we introduce a button. The app will start
            # when the button is pressed.

            # It gets more and more clear that the black screen is
            # screen refresh problem. only arising, when in buildozer.spec
            # fullscreen = 1 is set.
            # Without fullscreen, Initialisation works perfectly and
            # the start button is displayed right after the splash has been
            # removed.
            # In fullscreen mode the button is still there but not
            # visible. It can be pressed to start the app.
            # When the (black) device is rotated the button is displayed
            # because this initiates a screen refresh.
            # In the SDLActivity there are interface functions available.
            # One of these allows to switch between normal and fullscreen.
            # If this function is used, then the complete behaviour of
            # fullscreen is much better. Fullscreen is stable
            # this way and does not switch back occasionally.

            # The result of that investigation is:
            # - App will now be built with fullscreen = 0 in buildozer.spec
            # - Fullscreen is switched on at runtime after the app has fully
            #   started using the SDLActivity command.

            from kivy.uix.button import Button
            self.mybutton = Button(text='startbutton')
            def addbutton(dt):  # noqa
                self.baseWindow.add_widget(self.mybutton)
            def delaystart(*args): # noqa
                self.baseWindow.remove_widget(self.mybutton)
                Clock.schedule_once(self.app_start, 0.5)
            self.mybutton.bind(on_press=delaystart)
            Clock.schedule_once(addbutton, 1.5)
        else:
            Clock.schedule_once(self.app_start, 0.0)
            # self.app_start(0)

        # Android: Request missing android permissions.
        requestStoragePerm()
        logging.info("LApp: on_start processed")

        # NOTE: The Kivy Eventloop starts after this call
        # to process input and events. (NOT EARLIER!). This is
        # also the point, where the android splash screen will be
        # removed.

    def on_stop(self):
        # Achtung wird u.U. 2 mal aufgerufen !!!
        logging.info("LApp: on_stop")
        if self.startCode > 0:
            return
        # lapp: erweiterte klasse dieser (mit pysolfc app members).
        lapp = App.get_running_app()
        lapp.app.menubar.mHoldAndQuit()

    def on_pause(self):
        logging.info("LApp: on_pause")
        # return True: wenn wir wirklich in pause gehen. Dann wird auch
        # resume aufgerufen falls die app wieder aktiviert wird.
        # return False: app wird gestoppt (on_stop wird aufgerufen)
        if self.startCode > 0:
            return False

        pauseSupport = True
        # True ist die bessere Variante.

        lapp = App.get_running_app()
        app = lapp.app
        if app is None:
            return

        logging.info("LApp: on_pause - pause on")
        # set pause
        if not app.game.pause:
            app.game.doPause()

        logging.info("LApp: on_pause - savegame")
        # save game
        try:
            app.game.gstats.holded = 1
            app.game._saveGame(app.fn.holdgame)
            app.opt.game_holded = app.game.id
            app.opt.last_gameid = app.game.id
        except Exception:
            traceback.print_exc()
            pass
        # save options
        try:
            app.saveOptions()
        except Exception:
            traceback.print_exc()
            pass
        # save statistics
        try:
            app.saveStatistics()
        except Exception:
            traceback.print_exc()
            pass
        logging.info("LApp: on_pause - gamesaved")

        logging.info("LApp: on_pause, Window.size=%s" % str(Window.size))

        return pauseSupport

    def on_resume(self):
        logging.info("LApp: on_resume")

        lapp = App.get_running_app()
        app = lapp.app
        if app is None:
            return

        AndroidScreenRotation.unlock(toaster=False)

        so = get_screen_ori()
        go = so  # flake8: F841 nonsense!
        so = go
        logging.info("LApp: on_resume, Window.size=%s" % str(Window.size))
        # ANM:
        # kivy.core.window.Window hat hier u.U. eine falsche dimension
        # und unterscheidet sich vom display (-> in get_screen_ori).
        # Eine korrektur der Parameter von Window kann hier wie skizziert
        # durchgeführt werden und führt auch zu den korrekten 'on_size'
        # Notifikationen. Allerdings wird später (nach diesem Aufruf)
        # eine weitere Notifikation erhalten, welche das Fenster u.U.
        # wieder falsch aufstellt. (woher kommt die und warum ist sie
        # oft falsch ?)

        # Gelegentlich beobachtet: Schwarzer Bilschirm nach resume. Und
        # das bleibt dann so auf ewig. Aber die app läuft stabil. Die
        # einzige Interaktion mit der App ist über die Android buttons
        # für hintrgrund und resume. Diese funktioneren gemäss logcat
        # einwandfrei. Daher versuchen wir ... um den graphik context
        # wieder zu aktivieren/auszurichten:

        # gemäss einer neueren Antwort auf kivy issue 3671 gehört auch
        # update-viewport zu den nützlichen massnahmen.

        Clock.schedule_once(lambda dt: Window.update_viewport(),0.0) # noqa
        Clock.schedule_once(lambda dt: self.mainWindow.rebuildContainer(), 0.5)
        Clock.schedule_once(lambda dt: set_fullscreen(True),1.0) # noqa

        # Pause modus abschalten nach resume:
        if app.game.pause:
            Clock.schedule_once(self.makeEndPauseCmd(app), 3.0)

    def makeEndPauseCmd(self, app):
        def endPauseCmd(dt):
            if app.game.pause:
                logging.info("LApp: on_resume - pause off")
                app.game.doPause()
        return endPauseCmd
