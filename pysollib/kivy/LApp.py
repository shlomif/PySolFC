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
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.graphics import Rectangle
from kivy.graphics import Triangle
from kivy.properties import StringProperty
from kivy.uix.actionbar import ActionButton
from kivy.uix.actionbar import ActionPrevious
from kivy.uix.actionbar import ActionView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.widget import Widget
from kivy.utils import platform

# =============================================================================


def get_platform():
    return platform

# =============================================================================


def get_screen_ori():
    if get_platform() == 'android':
        from jnius import autoclass
        from jnius import cast
    else:
        logging.info("LApp: ori = unknown")
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
# kivy EventDispatcher passes keywords, that to not correspond to properties
# to the base classes. Finally they will reach 'object'. With python3 (but not
# python2) 'object' throws an exception 'takes no parameters' in that a
# situation. We therefore underlay a base class (right outside), which
# swallows up remaining keywords. Thus the keywords do not reach 'object' any
# more.


class LBase(object):
    def __init__(self, **kw):
        super(LBase, self).__init__()

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


class LAnimationMgr(object):
    def __init__(self, **kw):
        super(LAnimationMgr, self).__init__()
        self.animations = []
        self.widgets = {}

    def animEnd(self, anim, widget):
        # print('LAnimationMgr: animEnd = %s.%s' % (anim, widget))

        self.widgets[widget] = self.widgets[widget][1:]
        self.animations.remove(anim)
        if len(self.widgets[widget]) > 0:
            # start next animation on widget
            nanim = self.widgets[widget][0]
            self.animations.append(nanim)
            print('LAnimationMgr: animEnd, append = %s' % (nanim))
            nanim.start(widget)
        else:
            # no further animations for widget so stop
            del self.widgets[widget]

    def makeAnimStart(self, anim, spos, widget):
        def animStart(dt):
            widget.pos = spos
            # print('LAnimationMgr: animStart = %s ... %s' % (anim, dt))
            anim.start(widget)
        return animStart

    def checkRunning(self):
        return len(self.animations) > 0

    def create(self, spos, widget, **kw):
        x = 0.0
        y = 0.0
        duration = 0.2
        transition = 'in_out_quad'
        if 'x' in kw:
            x = kw['x']
        if 'y' in kw:
            y = kw['y']
        if 'duration' in kw:
            duration = kw['duration']
        if 'transition' in kw:
            transition = kw['transition']

        anim = Animation(x=x, y=y, duration=duration, transition=transition)
        anim.bind(on_complete=self.animEnd)
        if 'bindE' in kw:
            anim.bind(on_complete=kw['bindE'])
        if 'bindS' in kw:
            anim.bind(on_start=kw['bindS'])

        offset = duration / 3.0
        # offset = duration*1.2
        timedelay = offset * len(self.animations)
        # print('offset = %s'% offset)
        print('LAnimationMgr: timedelay = %s' % timedelay)

        if widget in self.widgets:
            # append additional animation to widget
            self.widgets[widget].append(anim)
        else:
            # setup first animation for widget
            self.animations.append(anim)
            self.widgets[widget] = [anim]
            Clock.schedule_once(self.makeAnimStart(
                anim, spos, widget), timedelay)


LAnimationManager = LAnimationMgr()

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


class LImage(KivyImage, LBase):

    def __init__(self, **kwargs):
        super(LImage, self).__init__(**kwargs)
        self.size = self.texture.size
        self.silent = False
        self.allow_stretch = True
        # self.keep_ratio = 0
        # self.size_hint = (1.0/9.0, 1.0/4.0)
        self.size_hint = (1.0, 1.0)
        # self.mipmap = True     # funktioniert nicht.

        self.corePos = None
        self.coreSize = None

        # logging.info('LImage: __init__() %s' % kwargs)

    def getHeight(self):
        return self.size[1]

    def getWidth(self):
        return self.size[0]

    def subsample(self, r):
        ''
        return LImage(texture=self.texture)
        '''
        if (self.source!=None):
            # logging.info("LImage: subsample, %d, %s " % (r , self.source))
            return LImage(source=self.source)
        elif (self.texture!=None):
            # logging.info("LImage: subsample, %d (texture) " % r)
            return LImage(texture=self.texture)
        '''
        return self

    def on_touch_down(self, touch):
        if self.silent:
            return False

        # print('LImage: touch_down on %s' % str(touch.pos))
        if self.collide_point(*touch.pos):
            if (self.source is not None):
                print('LImage match %s' % self.source)
            else:
                print('LImage match with texture')
            return True
        return False

    def on_touch_up(self, touch):
        if self.silent:
            return False

        # print('LImage: touch_up on %s' % str(touch.pos))
        if self.collide_point(*touch.pos):
            if (self.source is not None):
                print('LImage match %s' % self.source)
            else:
                print('LImage match with texture')
            return True
        return False

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
        kwargs['font_size'] = fontsize

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

        lwidth = 10
        fill = '#ee3344'
        ashape = ()
        arrow = 'none'

        self.prnt = canvas
        xmin = 100000
        ymin = 100000
        xmax = -100000
        ymax = -100000
        self.corePoly = []
        if isinstance(args[0], list):
            kww = args[1]
            if ('width' in kww):
                lwidth = kww['width']
            self.lwidth = lwidth
            if ('fill' in kww):
                fill = kww['fill']
            self.fill = fill
            if ('arrowshape' in kw):
                ashape = kw['arrowshape']
            self.ashape = ashape
            if ('arrow' in kw):
                arrow = kw['arrow']
            self.arrow = arrow

            pts = args[0]
            ipts = iter(pts)
            for x, y in zip(ipts, ipts):
                print('%s.%s' % (x, y))
                self.corePoly.append(x)
                self.corePoly.append(y)
                if x < xmin:
                    xmin = x
                if x > xmax:
                    xmax = x
                if y < ymin:
                    ymin = y
                if y > ymax:
                    ymax = y
        else:
            if ('width' in kw):
                lwidth = kw['width']
            self.lwidth = lwidth
            if ('fill' in kw):
                fill = kw['fill']
            self.fill = fill
            if ('arrowshape' in kw):
                ashape = kw['arrowshape']
            self.ashape = ashape
            if ('arrow' in kw):
                arrow = kw['arrow']
            self.arrow = arrow

            for i in range(0, 2):
                x = args[2 * i]
                y = args[2 * i + 1]
                self.corePoly.append(x)
                self.corePoly.append(y)
                if x < xmin:
                    xmin = x
                if x > xmax:
                    xmax = x
                if y < ymin:
                    ymin = y
                if y > ymax:
                    ymax = y

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

        width = 10.0
        if ('width' in kw):
            width = float(kw['width'])

        bcolor = '#ffa000a0'
        if ('outline') in kw:
            bcolor = kw['outline']
        if (not bcolor or len(bcolor) < 7):
            bcolor = '#ffa000a0'

        fcolor = '#00aaff20'
        if ('fill') in kw:
            fcolor = kw['fill']
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

        dmy, brd = self.prnt.CoreToKivy(
            (0.0, 0.0), (self.border, self.border))
        border = brd[1]

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


class LImageItem(BoxLayout, LBase):
    def __init__(self, **kw):
        super(LImageItem, self).__init__(**kw)
        self.game = None
        self.card = None
        self.group = None
        if 'game' in kw:
            self.game = kw['game']
        if 'card' in kw:
            self.card = kw['card']
        if 'group' in kw:
            self.group = kw['group']
        self.dragstart = None
        # ev. noch globales cache für stacks->game und cards->stack
        # einrichten. Aber: stacks hängt vom jeweiligen spiel ab.

    def send_event_pressed_1(self, event):
        if self.group and '<1>' in self.group.bindings:
            self.group.bindings['<1>'](event)

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):

            for c in self.children:
                # print('child at %s' % c)
                if (c.on_touch_down(touch) and self.game):
                    for stack in self.game.allstacks:
                        for i in range(len(stack.cards)):
                            if stack.cards[i] == self.card:
                                print('LCardImage: stack = %s' % stack)
                                print('LCardImage: touch = %s' % str(touch))
                                print('grab')
                                # grab the touch!
                                touch.grab(self)
                                ppos, psize = self.game.canvas.KivyToCore(
                                    touch.pos, self.size)
                                event = LEvent()
                                event.x = ppos[0]
                                event.y = ppos[1]
                                self.dragstart = touch.pos
                                event.cardid = i
                                self.send_event_pressed_1(event)
                                return True

            if self.group is not None:
                print('LCardImage: self=%s group=%s' % (self, self.group))
                if '<1>' in self.group.bindings:
                    ppos, psize = self.group.canvas.KivyToCore(
                        touch.pos, self.size)
                    event = LEvent()
                    event.x = ppos[0]
                    event.y = ppos[1]
                    self.group.bindings['<1>'](event)
                    return True

            if self.card is None:
                return False
            if self.game is None:
                return False

        # print('LCardImage: touch_down on %s' % str(touch.pos))
        return False

    def send_event_released_1(self, event):
        if self.group and '<ButtonRelease-1>' in self.group.bindings:
            self.group.bindings['<ButtonRelease-1>'](event)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # release my grabbed touch!
            print('ungrab')
            touch.ungrab(self)
            return True

        if self.collide_point(*touch.pos):

            for c in self.children:
                # print('child at %s' % c)

                if (c.on_touch_up(touch) and self.game):
                    for stack in self.game.allstacks:
                        for i in range(len(stack.cards)):
                            if stack.cards[i] == self.card:
                                print('LCardImage: stack = %s' % stack)
                                ppos, psize = self.game.canvas.KivyToCore(
                                    touch.pos, self.size)
                                event = LEvent()
                                event.x = ppos[0]
                                event.y = ppos[1]
                                event.cardid = i
                                self.send_event_released_1(event)
                                return True

            if self.group is not None:
                print('LCardImage: self=%s group=%s' % (self, self.group))
                if '<ButtonRelease-1>' in self.group.bindings:
                    ppos, psize = self.group.canvas.KivyToCore(
                        touch.pos, self.size)
                    event = LEvent()
                    event.x = ppos[0]
                    event.y = ppos[1]
                    self.group.bindings['<ButtonRelease-1>'](event)
                    return True

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
            for i in range(len(stack.cards)):
                if stack.cards[i] == self.card:
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
            self.onVarChange(self.variable, self.variable.get())

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
        if type(value) is bool:
            self.setCheck(value)
        if type(value) is int:
            self.setVal(value)
        if type(value) is str:
            self.setVal(value)
        # if type(value) is unicode:
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
            self.text = u'    ' + self.title
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

        # beispiel zu canvas (hintergrund)
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

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_press(self):
        print('press')

    def on_release(self):
        print('release')

# =============================================================================


class LTopLevel0(BoxLayout, LBase):
    def __init__(self, top, title=None, **kw):
        self.main = top
        super(LTopLevel0, self).__init__(
            orientation="vertical", **kw)

        # self.canvas.add(Color(0, 1, 0, 0.4))
        # self.canvas.add(Rectangle(pos=(100, 100), size=(100, 100)))

        self.size_hint = (0.5, 1.0)
        '''
        self.titleline = BoxLayout(
            orientation="horizontal", size_hint=[1.0, 0.15], **kw)
        self.button = Button(text="X", size_hint=[0.15, 1.0], **kw)
        if not title:
            title = '<>'
        self.title = Label(text=title, **kw)
        self.titleline.add_widget(self.title)
        self.titleline.add_widget(self.button)
        '''
        self.titleline = LTopLine(text=title, size_hint=[1.0, 0.15])
        self.title = title

        # self.content = BoxLayout(orientation="vertical", **kw)
        self.content = LTopLevelContent(orientation="vertical", **kw)
        self.add_widget(self.titleline)
        self.add_widget(self.content)
        '''
        self.button.bind(on_press=self.onClick)
        '''
        self.titleline.bind(on_press=self.onClick)
        self.main.pushWork(self.title, self)

    def onClick(self, event):
        print('LTopLevel: onClick')
        self.main.popWork(self.title)

# =============================================================================


class LTopLevel(BoxLayout, LBase):
    def __init__(self, parent, title=None, **kw):
        self.mainwindow = parent
        super(LTopLevel, self).__init__(
            orientation="vertical", **kw)

        if ('size_hint' not in kw):
            self.size_hint = (0.5, 1.0)
        else:
            del kw['size_hint']
        self.titleline = LTopLine(text=title, size_hint=(1.0, 0.10))

        self.content = LTopLevelContent(orientation="vertical", **kw)
        self.add_widget(self.titleline)
        self.add_widget(self.content)

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

        kw['app_icon'] = 'data/images/misc/pysol01.png'
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
            if (type(c) is LMenuItem):
                # print ('LMenu: to delete child %s' % c)
                items.append(c)
            elif (type(c) is LMenu):
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
        # print('LMenuItem: setCommand')
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
        logging.info("LTkBase: update_idletasks")
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
        logging.info('LTkBase: interruptSleep')
        self.update_idletasks()
        # self.sleep_var = 1
        return

    def mainquit(self):
        logging.info('LTkBase: mainquit')
        lapp = App.get_running_app()
        lapp.mainloop.send(None)    # Spielprozess verlassen
        return

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

    def waitCondition(self, condition):
        logging.info('LTkBase: wait condition start')
        while condition():
            self.in_loop = True
            EventLoop.idle()
            self.in_loop = False
        logging.info('LTkBase: wait condition end')

    def waitAnimation(self):
        self.waitCondition(LAnimationManager.checkRunning)

    def tkraise(self):
        pass

    def winfo_ismapped(self):
        return True
        # ???

# =============================================================================


class LStack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, key, item):
        self.items.append((key, item))

    def pop(self, key):
        for i in range(len(self.items)):
            t = self.items[i]
            if (t[0] == key):
                self.items.pop(i)
                return t[1]
        return None

    def peek(self, key):
        for i in range(len(self.items)):
            t = self.items[i]
            if (t[0] == key):
                return t
        return None

    def size(self):
        return len(self.items)

# =============================================================================


class LMainWindow(BoxLayout, LTkBase):
    def __init__(self, **kw):
        super(LMainWindow, self).__init__(orientation='vertical')
        LTkBase.__init__(self)
        self.menuArea = LMenuBar()
        self.workContainer = LBoxLayout(orientation='horizontal')
        self.workContainerO = LBoxLayout(orientation='horizontal')
        self.workArea = None
        self.toolBar = None
        self.toolBarPos = 0
        self.bindings = {}
        self._w = '.'
        self.topLine = Button(
            size_hint=(1.0, 0.01),
            background_down='atlas:'
                            '//data/images/defaulttheme/action_item_down',
            background_normal='atlas:'
                              '//data/images/defaulttheme/action_item',
            border=(0, 0, 0, 0))
        self.topLine1 = Label(size_hint=(1.0, 0.01))

        self.add_widget(self.topLine)
        self.add_widget(self.menuArea)
        self.add_widget(self.topLine1)
        self.add_widget(self.workContainerO)
        self.workContainerO.add_widget(self.workContainer)
        # self.add_widget(Button(size_hint = (1.0, 0.01)))

        self.workStack = LStack()
        self.app = None

        # self.touches = []

        # beispiel zu canvas (hintergrund)
        # with self.canvas.before:
        #   Color(0, 1, 0.7, 0.5)
        #   self.rect = Rectangle(pos=self.pos, size=self.size)
        # self.bind(pos=self.update_rect)
        # self.bind(size=self.update_rect)

    # def update_rect(self, *args):
    #   self.rect.pos = self.pos
    #   self.rect.size = self.size

    def on_motion(self, m):
        print('on_motion', m)
        pass

    # Events.

    def on_touch_down(self, touch):
        ret = False

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
        '''
        if touch.is_double_tap:
            # print('Touch is a double tap !')
            # print(' - interval is', touch.double_tap_time)
            # print(' - distance betw. previous is', touch.double_tap_distance)
            # test the functions of Android back key
            ret = self.processAndroidBack()
            if (ret):
                return ret
        '''
        '''
        if touch.is_triple_tap:
            print('Touch is a triple tap !')
            print(' - interval is', touch.triple_tap_time)
            print(' - distance between previous is', touch.triple_tap_distance)
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

    def buildContainer(self):
        if self.toolBar is not None and self.toolBarPos == 3:
            self.workContainerO.add_widget(self.toolBar)
        self.workContainerO.add_widget(self.workContainer)
        if self.toolBar is not None and self.toolBarPos == 4:
            self.workContainerO.add_widget(self.toolBar)
        for w in self.workStack.items:
            self.workContainer.add_widget(w[1])

    def rebuildContainer(self):
        self.removeContainer()
        self.buildContainer()

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
        else:
            return False    # delegate

    def __init__(self):
        super(LApp, self).__init__()

        # Config.set('input', 'multitouchscreen1', 'tuio,0.0.0.0:3333')

        self.mainWindow = LMainWindow()
        logging.info('top = %s' % str(self.mainWindow))
        Cache.register('LAppCache', limit=10)
        Cache.append('LAppCache', 'mainWindow', self.mainWindow, timeout=0)
        Cache.append('LAppCache', 'mainApp', self, timeout=0)
        self.startCode = 0

    # Es gibt hier offensichtlich nur einen Bilschirm mit Höhe und Breite.
    # Alles andere stellt das Betriebssystem zur Verfügung. Wir wissen auch
    # nicht, wie das Gerät gerade orientiert ist, ist nicht unsere Sache.
    # Alles was wir tun können ist Höhe und Breite zu verfolgen, sobald wir
    # dazu informiert werden. (Android informiert leider nicht immer, wenn
    # es nötig wäre).
    # Update:
    # Nachdem im Manifest nun steht 'configChange=...|screenSize' bekommen
    # wir auch nach dem on_resume ein Signal.

    def delayedRebuild(self, dt):
        logging.info("LApp: delayedRebuild")
        self.mainWindow.rebuildContainer()

    def makeDelayedRebuild(self):
        def delayedRebuild(dt):
            # Clock.schedule_once(self.delayedRebuild, 0.01)
            Clock.schedule_once(self.delayedRebuild, 0.5)
        return delayedRebuild

    def doSize(self, obj, val):
        mval = self.mainWindow.size
        logging.info("LApp: size changed %s - %s (%s)" % (obj, val, mval))
        # Clock.schedule_once(self.delayedRebuild, 0.01)
        Clock.schedule_once(self.makeDelayedRebuild(), 0.01)
        # self.mainWindow.rebuildContainer()
        pass

    def on_start(self):
        logging.info('mw = %s,  w = %s' % (self.mainWindow, Window))

        Window.bind(on_keyboard=self.key_input)
        Window.bind(size=self.doSize)

        if self.startCode > 0:
            logging.info("LApp: on_start fails")
            return

        logging.info("LApp: on_start")
        self.mainloop = self.app.mainproc()  # Einrichten
        self.mainloop.send(None)                # Spielprozess starten
        logging.info("LApp: on_start processed")

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
        # save comments
        try:
            app.saveComments()
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

        if app.game.pause:
            Clock.schedule_once(self.makeEndPauseCmd(app), 3.0)

    def makeEndPauseCmd(self, app):
        def endPauseCmd(dt):
            if app.game.pause:
                logging.info("LApp: on_resume - pause off")
                app.game.doPause()
        return endPauseCmd
