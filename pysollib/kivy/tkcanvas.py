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

from __future__ import division

import logging
import math

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout

from pysollib.kivy.LApp import LAnimationManager
from pysollib.kivy.LApp import LColorToKivy
from pysollib.kivy.LApp import LImageItem
from pysollib.kivy.LApp import LLine
from pysollib.kivy.LApp import LRectangle
from pysollib.kivy.LApp import LText
from pysollib.kivy.LImage import LImage

# ************************************************************************
# * canvas items helpers
# ************************************************************************


def addAnchorOffset(pos, anchor, size):
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


def subAnchorOffset(pos, anchor, size):
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
        x = x + size[0] / 2.0
    elif xa == 1:
        x = x + size[0]
    if ya == 0:
        y = y + size[1] / 2.0
    elif ya == 1:
        y = y + size[1]
    return (x, y)

# ************************************************************************
# * canvas items
# ************************************************************************


class MfxCanvasGroup():
    def __init__(self, canvas, tag=None):
        # print(self, '__init__(', canvas, tag, ')')

        self.canvas = canvas
        self.bindings = {}
        self.stack = None

    def __str__(self):
        return f'<MfxCanvasGroup @ {hex(id(self))}>'

    def _imglist(self, group):
        ilst = []
        for w in group.canvas.children:
            if isinstance(w, LImageItem):
                if w.group == group:
                    ilst.append(w)
        return ilst

    def makeDeferredRaise(self, pos):
        def animCallback():
            self.tkraise(position=pos)
        return animCallback

    def tkraise(self, position=None):
        # print(self, ' tkraise(', position, ')')
        # Mainly used by Mahjongg game after a move.
        # import inspect
        # print('stack[1] = ',inspect.stack()[1].frame)
        # print('stack[2] = ',inspect.stack()[2].frame)

        if LAnimationManager.checkRunning():
            LAnimationManager.addEndCallback(
                self.makeDeferredRaise(position))
            return

        imgs = self._imglist(self)
        if len(imgs) == 0:
            return

        if position is not None:
            # add all images above specified position
            pimgs = self._imglist(position)
            if len(pimgs) == 0:
                return

            self.canvas.clear_widgets(imgs)
            k = self.canvas.children.index(pimgs[-1])
            for i in imgs:
                self.canvas.add_widget(i, index=k)
                k += 1
        else:
            # add all images to top
            self.canvas.clear_widgets(imgs)
            k = 0
            for i in imgs:
                self.canvas.add_widget(i, index=k)
                k += 1

    def makeDeferredLower(self, pos):
        def animCallback():
            self.lower(position=pos)
        return animCallback

    def lower(self, position=None):
        # print(self, ' lower(', position, ')')
        # import inspect
        # print('stack[1] = ',inspect.stack()[1].frame)
        # print('stack[2] = ',inspect.stack()[2].frame)

        if LAnimationManager.checkRunning():
            LAnimationManager.addEndCallback(
                self.makeDeferredLower(position))
            return

        imgs = self._imglist(self)
        if len(imgs) == 0:
            return

        if position is not None:
            # add below specified position
            pimgs = self._imglist(position)
            if len(pimgs) == 0:
                return

            self.canvas.clear_widgets(imgs)
            k = self.canvas.children.index(pimgs[0])  # the spec. item
            k += 1  # insert before
            for i in imgs:
                self.canvas.add_widget(i, index=k)
                k += 1
        else:
            # add all to bottom
            self.canvas.clear_widgets(imgs)
            k = len(self.canvas.children)-1  # the last item
            k += 1  # insert before
            for i in imgs:
                self.canvas.add_widget(i, index=k)
                k += 1

    def addtag(self, tag, option="withtag"):
        # logging.info('MfxCanvasGroup: addtag(%s, %s)' % (tag, option))
        # self.canvas.addtag(tag, option, self.id)
        pass

    def delete(self):
        # logging.info('MfxCanvasGroup: delete()')
        # del self.canvas.items[self.id]
        pass

    def gettags(self):
        # logging.info('MfxCanvasGroup: gettags()')
        # return self.canvas.tk.splitlist(self._do("gettags"))
        return None


def cardmagnif(canvas, size):
    def pyth(s):
        return math.sqrt(s[0]*s[0]+s[1]*s[1])
    cs = canvas.wmain.app.images.getSize()
    csl = pyth(cs)
    sl = pyth(size)
    return csl/sl


class MfxCanvasImage(object):
    def __init__(self, canvas, *args, **kwargs):

        # print ('MfxCanvasImage: %s | %s | %s' % (canvas, args, kwargs))

        self.group = None
        group = None
        if 'group' in kwargs:
            group = kwargs['group']
            del kwargs['group']
        self._image = None
        if 'image' in kwargs:
            self._image = kwargs['image']
        self._anchor = None
        if 'anchor' in kwargs:
            self._anchor = kwargs['anchor']
        self.hint = None
        if 'hint' in kwargs:
            self.hint = kwargs['hint']

        # print ('MfxCanvasImage: group = %s ' % (group))
        # wir kommen üblicherweise aus Card.__init__(). und da ist keine
        # group (group wird über addtag gesetzt, sobald das image
        # in einem stack ist.)

        super(MfxCanvasImage, self).__init__()
        self.canvas = canvas
        self.redeal = False

        # animation mode support:
        self.animation = 0
        self.duration = 0.2
        self.deferred_raises = []
        self.animations = []

        ed = kwargs['image']
        size = ed.size

        if isinstance(ed, LImageItem):
            aimage = ed
        else:
            image = LImage(texture=ed.texture)
            if self.hint == "redeal_image":
                cm = cardmagnif(canvas, size)/1.9
                image.size = [cm*ed.getWidth(), cm*ed.getHeight()]
                self.redeal = True
                aimage = LImageItem(
                    size=ed.size, group=group, image_type=self.hint)
            else:
                image.size = [ed.getWidth(), ed.getHeight()]
                aimage = LImageItem(size=ed.size, group=group)

            aimage.add_widget(image)
            aimage.size = image.size
            size = image.size

        xy = addAnchorOffset(args, self._anchor, size)

        aimage.coreSize = (aimage.size[0], aimage.size[1])
        aimage.corePos = (xy[0], xy[1])

        aimage.pos, aimage.size = canvas.CoreToKivy(xy, aimage.size)
        self.canvas.add_widget(aimage)
        self.image = aimage
        self.widget = aimage

        if group:
            self.addtag(group)

    def __del__(self):
        # print('MfxCanvasImage: __del__(%s)' % self.image)
        self.canvas.clear_widgets([self.image])

    def __str__(self):
        return f'<MfxCanvasImage @ {hex(id(self))}>'

    def config(self, **kw):
        # print('MfxCanvasImage conifg:',kw)
        if "image" in kw:
            # print('is redeal image:',self.redeal)
            if self.redeal:
                image = self.image.children[0]
                image.texture = kw["image"].texture
                # print('redeal texture:',image.texture)
        pass

    def makeDeferredRaise(self, pos):
        def animCallback():
            self.canvas.tag_raise(self.image, pos)
        return animCallback

    def tkraise(self, aboveThis=None):

        abitm = None
        if aboveThis:
            abitm = aboveThis.widget

        # import inspect
        # print('stack[1] = ', inspect.stack()[1].frame)
        # print('stack[2] = ', inspect.stack()[2].frame)
        # print('stack[3] = ', inspect.stack()[3].frame)

        if self.animation > 0:
            # print('defer tkraise to animation', abitm)
            if len(self.deferred_raises) < self.animation:
                self.deferred_raises.append(self.makeDeferredRaise(abitm))
            return

        # print('direct tkraise', abitm)
        self.canvas.tag_raise(self.image, abitm)

    def addtag(self, tag):
        # print('MfxCanvasImage: addtag %s' % tag.stack)
        self.group = tag
        if (self.image):
            self.image.group = tag

    def dtag(self, tag):
        # print('MfxCanvasImage: remtag %s' % tag.stack)
        self.group = None
        if (self.image):
            self.image.group = None
        pass

    def delete(self):
        # print('MfxCanvasImage: delete()')
        self.canvas.clear_widgets([self.image])

    def move(self, dx, dy):
        # print('MfxCanvasImage: move %s, %s' % (dx, dy))
        image = self.image
        dsize = image.coreSize
        dpos = (image.corePos[0] + dx, image.corePos[1] + dy)
        image.corePos = dpos
        if self.animation == 0:
            image.pos, image.size = self.canvas.CoreToKivy(dpos, dsize)
        else:
            pos, size = self.canvas.CoreToKivy(dpos, dsize)
            self.animations[self.animation-1].updateDestPos(pos)

    def makeAnimStart(self):
        def animStart(anim, widget):
            # print('MfxCanvasImage: animStart %s' % self)

            # raise to top if reqested for this move
            if self.deferred_raises:
                self.deferred_raises[0]()
                self.deferred_raises = self.deferred_raises[1:]

            # update z-order (for some specials)
            while 1:
                from pysollib.games.grandfathersclock import Clock_RowStack
                specials = [Clock_RowStack, ]

                if self.group is None: break            # noqa
                stack = self.group.stack
                if stack is None: break                 # noqa
                if type(stack) not in specials: break   # noqa

                cards = self.group.stack.cards
                card = self.image.card
                if card is None: break                  # noqa
                if card == cards[-1]: break             # noqa
                i = cards.index(card) + 1

                # print('stack =', self.group.stack)
                # print('cards:', [c.__str__() for c in cards])
                # print('card =', card)
                # print('***** adjust z-reordering:',card,'before',cards[i])

                def lower_z(dt):
                    self.canvas.tag_lower(card.item.image, cards[i].item.image)

                Clock.schedule_once(lower_z, self.duration/2.0)
                break

        return animStart

    def makeAnimEnd(self, dpos, dsize):
        def animEnd(anim, widget):
            # print('MfxCanvasImage: animEnd %s' % self)

            if self.animation > 0:
                self.animation -= 1
                self.animations = self.animations[1:]

            if self.animation == 0:
                # just for the case, keep in sync:
                self.deferred_raises = []
                self.animations = []

            # print('MfxCanvasImage: animEnd moved to %s, %s' % (dpos[0], dpos[1])) # noqa
        return animEnd

    def animatedMove(self, dx, dy, duration=0.2):
        # print('MfxCanvasImage: animatedMove %s, %s' % (dx, dy))
        # import inspect
        # for insi in range(1,9):
        #     print('stack[insi] = ', inspect.stack()[insi].frame)

        image = self.image
        dsize = image.coreSize
        dpos = (image.corePos[0] + dx, image.corePos[1] + dy)
        pos, size = self.canvas.CoreToKivy(dpos, dsize)
        transition1 = 'out_expo'
        # transition2 = 'out_cubic'
        # transition3 = 'out_quad'
        # transition4 = 'out_quint'
        # transition5 = 'out_sine'
        transition6 = 'in_out_quad'
        # transition7 = 'in_bounce'
        # transition8 = 'in_elastic'
        transition = transition6
        if self.canvas.wmain.app.game.demo:
            transition = transition1

        self.duration = duration
        ssize = image.coreSize
        spos = (image.corePos[0], image.corePos[1])
        spos, ssize = self.canvas.CoreToKivy(spos, ssize)

        from pysollib.kivy.LApp import LAnimationTask
        task = LAnimationTask(
            spos,
            image,
            x=pos[0], y=pos[1],
            duration=duration, transition=transition,
            bindS=self.makeAnimStart(),
            bindE=self.makeAnimEnd(dpos, dsize))
        self.animations.append(task)
        self.animation += 1
        LAnimationManager.taskInsert(task)

    def show(self):
        self.config(state='normal')

    def hide(self):
        self.config(state='hidden')


class MfxCanvasLine(object):
    def __init__(self, canvas, *args, **kwargs):
        # print('MfxCanvasLine: %s %s' % (args, kwargs))

        self.canvas = canvas
        line = LLine(canvas, args, **kwargs)
        line.pos, line.size = canvas.CoreToKivy(line.corePos, line.coreSize)
        canvas.add_widget(line)
        self.canvas = canvas
        self.line = line
        self.widget = line

    def delete_deferred(self, seconds):
        # print('MfxCanvasLine: delete_deferred(%s)' % seconds)
        from kivy.animation import Animation
        z = 0
        t = 'in_expo'
        anim = Animation(opacity=z, t=t, d=seconds/1.5)
        anim.start(self.line)
        Clock.schedule_once(lambda dt: self.delete(), seconds)

    def delete(self):
        # print('MfxCanvasLine: delete()')
        self.canvas.clear_widgets([self.line])


class MfxCanvasRectangle(object):
    def __init__(self, canvas, *args, **kwargs):

        # logging.info('MfxCanvasRectangle: %s %s' % (args, kwargs))

        rect = LRectangle(canvas, args, **kwargs)
        rect.pos, rect.size = canvas.CoreToKivy(rect.corePos, rect.coreSize)
        canvas.add_widget(rect)
        self.canvas = canvas
        self.rect = rect
        self.widget = rect

    def delete(self):
        # print('MfxCanvasRectangle: delete()')
        self.canvas.clear_widgets([self.rect])

    def __del__(self):
        # print('MfxCanvasRectangle: __del__()')
        self.delete()

    def delete_deferred_step(self, seconds):
        # print ('MfxCanvasRectangle: delete_deferred_step(%s)' % seconds)
        Clock.schedule_once(lambda dt: self.delete(), seconds)

    def delete_deferred(self, seconds):
        # self.canvas.canvas.ask_update()
        # print ('MfxCanvasRectangle: delete_deferred(%s)' % seconds)
        Clock.schedule_once(
            lambda dt: self.delete_deferred_step(seconds), 0.05)

    def addtag(self, tag):
        logging.info('MfxCanvasRectangle: addtag(%s) - fake' % tag)
        pass

    def tkraise(self, aboveThis=None):
        # logging.info('MfxCanvasRectangle: tkraise(%s) - fake' % item)
        abitm = None
        if aboveThis:
            abitm = aboveThis.widget
        self.canvas.tag_raise(self.rect, abitm)
        pass


class MfxCanvasText(object):
    def __init__(self, canvas, x, y, preview=-1, **kwargs):

        if preview < 0:
            preview = canvas.preview
        if preview > 1:
            return
        if "fill" not in kwargs:
            kwargs["fill"] = canvas._text_color
        if 'group' in kwargs:
            del kwargs['group']

        super(MfxCanvasText, self).__init__()

        label = LText(canvas, x, y, **kwargs)
        label.pos, label.size = canvas.CoreToKivy(
            label.corePos, label.coreSize)
        canvas.add_widget(label)
        self.canvas = canvas
        self.label = label
        self.widget = label
        self.canvas.bind(_text_color=self.setColor)

    def setColor(self, w, c):
        self.label.label.color = LColorToKivy(c)

    def config(self, **kw):
        # print('MfxCanvasText: config %s' % kw)
        if ('text' in kw):
            self.label.text = kw['text']

    def tkraise(self, aboveThis=None):
        abitm = None
        if aboveThis:
            abitm = aboveThis.widget
        self.canvas.tag_raise(self.label, abitm)
        pass

    def bbox(self):
        # Dimensionen als 2x2 array zurückgeben.
        # (aufruf z.B. bei games/special/poker.py und bei Memory!)
        label = self.label
        canvas = self.canvas
        pos = label.pos
        size = label.size
        pos, size = canvas.KivyToCore(pos, size)
        ret = [[pos[0], pos[1]], [pos[0] + size[0], pos[1] + size[1]]]
        return ret

    def addtag(self, tag):
        pass

# ************************************************************************
# * canvas
# ************************************************************************


class MfxCanvas(LImage):
    _text_color = StringProperty("#000000")

    def __str__(self):
        return f'<MfxCanvas @ {hex(id(self))}>'

    def __init__(self, wmain, *args, **kw):
        super(MfxCanvas, self).__init__(background=True)

        # print('MfxCanvas: __init__()')
        # self.tags = {}   # bei basisklasse widget (ev. nur vorläufig)

        self.wmain = wmain
        # print('MfxCanvas: wmain = %s' % self.wmain)

        # Tkinter.Canvas.__init__(self, *args, **kw)
        self.preview = 0
        self.busy = False
        self._text_color = '#000000'
        self._bg_color = '#00ffff'
        self._stretch_bg_image = 0
        self._save_aspect_bg_image = 0
        #
        self.xmargin, self.ymargin = 0.0, 0.0
        self.topImage = None

        # Skalierung
        # self.lastsize = (self.size[0], self.size[1])
        # self.lastpos = (self.pos[0], self.pos[1])

        self.scale = 1.2
        self.r_width = None
        self.r_height = None

        self.bindings = {}
        self.bind(pos=self.pos_update_widget)
        self.bind(size=self.size_update_widget)

    def KivyToCoreP(self, pos, size, scale):
        cpos = pos
        cpos = (cpos[0] - self.pos[0], self.pos[1] +
                self.size[1] - cpos[1] - size[1])
        cpos = (1.0 * cpos[0] / scale, 1.0 * cpos[1] / scale)
        csize = (1.0 * size[0] / scale, 1.0 * size[1] / scale)
        return cpos, csize

    def CoreToKivyP(self, cpos, csize, scale):
        size = (1.0 * csize[0] * scale, 1.0 * csize[1] * scale)
        pos = (1.0 * cpos[0] * scale, 1.0 * cpos[1] * scale)
        pos = (self.pos[0] + pos[0], self.pos[1] +
               self.size[1] - pos[1] - size[1])
        return pos, size

    def KivyToCore(self, pos, size=(0.0, 0.0)):
        return self.KivyToCoreP(pos, size, self.scale)

    def CoreToKivy(self, cpos, csize=(0.0, 0.0)):
        return self.CoreToKivyP(cpos, csize, self.scale)

    def move(self, itm, dx, dy):
        # print ('MfxCanvas: move %s %s %s' % (itm, dx, dy))
        scale = self.scale
        dx = scale * dx
        dy = scale * dy
        itm.pos = (itm.pos[0] + dx, itm.pos[1] - dy)

    def scalefactor(self):
        if self.r_width is None:
            return self.scale
        if self.r_height is None:
            return self.scale

        # TBD (idee).
        # Hier ev. einen 2ten Modus zulassen, welche das Spielfeld
        # knapp auf die vorhandenen Karten/Anzeigeelemente bemisst.
        # Zur Optimierung der Sichtbarkeit auf kleinen Geräten.
        # Könnte z.B. über Doppelklick umgeschaltet werden. (Die
        # Skalierung müsste dann allerding nach jedem Zug dem ev.
        # veränderten Feld angepasst werden.)

        wid = self.size[0]
        hei = self.size[1]
        scfx = wid / self.r_width
        scfy = hei / self.r_height

        scf = scfx
        if (scfx < scfy):
            # print('scale factor by x = %s' % (scfx))
            scf = scfx
        else:
            # print('scale factor by y = %s' % (scfy))
            scf = scfy

        return scf

    def pos_update_widget(self, posorobj, size):
        # print('MfxCanvas: pos_update_widget size=(%s, %s)' %
        #       (self.size[0], self.size[1]))
        self.update_widget(posorobj, size)

    def size_update_widget(self, posorobj, size):
        # print('MfxCanvas: size_update_widget size=(%s, %s)' %
        #       (self.size[0], self.size[1]))
        self.update_widget(posorobj, size)

    def update_widget(self, posorobj, size):
        def psize(s):
            return "({:1.2f}, {:1.2f})".format(s[0], s[1])

        # logging.info('MfxCanvas: update_widget to: '+psize(size))

        # print('MfxCanvas: update_widget size=(%s, %s)' %
        #       (self.size[0], self.size[1]))

        # Update Skalierungsparameter

        # oldscale = self.scale
        newscale = self.scalefactor()
        # logging.info('MfxCanvas: scale factor: {:1.2f})'.format(newscale))
        self.scale = newscale

        # Anpassung Skalierung.

        for c in self.children:
            if not hasattr(c, 'corePos'):
                continue
            if not hasattr(c, 'coreSize'):
                continue

            bpos = c.corePos
            bsiz = c.coreSize
            if bpos and bsiz:
                npos, nsiz = self.CoreToKivy(bpos, bsiz)
                c.pos = npos
                c.size = nsiz

        # Hintergrund update.

        kc = LColorToKivy(self._bg_color)
        texture = None
        if self._bg_img:
            texture = self._bg_img.texture

        self.texture = texture
        if texture is None:
            self.setColor(kc)
        else:
            self.setColor([1,1,1,1]) # noqa
            if self._stretch_bg_image:
                if self._save_aspect_bg_image == 0:
                    self.fit_mode = "fill"
                else:
                    self.fit_mode = "cover"
            else:
                self.fit_mode = "tiling"

    # Funktionen, welche vom Core aufgerufen werden.

    def winfo_width(self):
        # return self.r_width
        cpos, csize = self.KivyToCoreP(self.pos, self.size, self.scale)
        # print('MfxCanvas: winfo_width %s' % (csize[0]))
        return csize[0]

    def winfo_height(self):
        # return self.r_height
        cpos, csize = self.KivyToCoreP(self.pos, self.size, self.scale)
        # print('MfxCanvas: winfo_height %s' % (csize[1]))
        return csize[1]

    def cget(self, f):
        print('MfxCanvas: cget %s -> %s, %s' % (f, self.pos, self.size))
        cpos, csize = self.KivyToCoreP(self.pos, self.size, self.scale)
        if f == 'width':
            print('MfxCanvas: cget %s -> x=%s' % (f, cpos[0]))
            return cpos[0]
        if f == 'height':
            print('MfxCanvas: cget %s -> y=%s' % (f, cpos[1]))
            return cpos[1]
        # if f=='bg':
        #    return background-color
        print('MfxCanvas: cget unsupported token')
        return 1

    def xview(self):
        print('MfxCanvas: xview')
        return [1, 1]
        pass

    def yview(self):
        print('MfxCanvas: yview')
        return [1, 1]
        pass

    #
    # top-image support
    #
    def tag_raise(self, itm, abitm=None):
        # print('MfxCanvas: tag_raise(%s, %s)' % (itm, abitm))

        def findTop(itm):
            t = type(itm)
            for c in self.children:
                if isinstance(c, t):
                    return self.children.index(c)
            return 0

        if (itm is not None):
            if (abitm is None):
                self.remove_widget(itm)
                self.add_widget(itm, index=findTop(itm))
            else:
                self.remove_widget(itm)
                k = self.children.index(abitm)
                self.add_widget(itm, index=k)

    def tag_lower(self, itm, belowThis=None):
        # print('MfxCanvas: tag_lower(%s, %s)' % (itm, belowThis))

        if (itm is not None):
            if (belowThis is None):
                self.remove_widget(itm)
                k = len(self.children)
                self.add_widget(itm, index=k)
            else:
                self.remove_widget(itm)
                k = self.children.index(belowThis)
                k += 1
                self.add_widget(itm, index=k)

    def setInitialSize(self, width, height):
        self.r_width = width
        self.r_height = height
        self.update_widget(self.pos, self.size)

    # delete all CanvasItems, but keep the background and top tiles
    def deleteAllItems(self):
        print('MfxCanvas: deleteAllItems')
        self.clear_widgets()
        pass

    def findCard(self, stack, event):
        print('MfxCanvas: findCard(%s, %s)' % (stack, event))
        if (event.cardid > -1):
            return event.cardid

        print('MfxCanvas: findCard no cardid')
        return -1

    def findImagesByType(self, image_type):
        images = []
        for c in self.children:
            if isinstance(c, LImageItem):
                if c.get_image_type() == image_type:
                    images.append(c)
        return images

    def setTextColor(self, color):
        # print('MfxCanvas: setTextColor')
        # color is ignored: it sets a predefined (option settable)
        # color. We do not support that. Instead of this wie examine
        # the background and set the color accordingly.
        if self._bg_img is not None:
            from pysollib.kivy.LApp import LTextureToLuminance
            lumi = LTextureToLuminance(self._bg_img.texture)
        else:
            from pysollib.kivy.LApp import LColorToLuminance
            lumi = LColorToLuminance(self._bg_color)

        self._text_color = ("#000000", "#ffffff")[lumi < 0.4]
        # print('average luminance =', lumi)

    def setTile(self, image, stretch=0, save_aspect=0):

        # print('setTile: %s, %s, %s' % (image, stretch, save_aspect))
        if image:
            try:
                from pysollib.kivy.tkutil import LImageInfo
                self._bg_img = LImageInfo(image)
                self._stretch_bg_image = stretch
                self._save_aspect_bg_image = save_aspect
                self.update_widget(self.pos, self.size)
            except Exception:
                return 0
        else:
            # print ('setTile: no image!')
            self._bg_img = None
            self.update_widget(self.pos, self.size)
        return 1

    def setTopImage(self, image, cw=0, ch=0):
        print('MfxCanvas: setTopImage %s' % image)

        if self.topImage:
            self.clear_widgets([self.topImage])
            self.topImage = None

        if image:
            tex = LImage(texture=image.texture)
            tex.size_hint = (0.4, 0.4)
            lay = AnchorLayout(anchor_y='bottom')
            lay.size = self.size
            lay.add_widget(tex)

            self.topImage = lay
            self.add_widget(self.topImage)

        return 1
    #
    # Pause support
    #

    def hideAllItems(self):
        print('MfxCanvas: hideAllItems')
        # TBD
        # Wir lassen das. Das TopImage deckt alles ab. Spielen ist
        # nicht möglich.
        pass

    def showAllItems(self):
        print('MfxCanvas: showAllItems')
        # TBD
        # Brauchts darum auch nicht.
        pass

    # Erweiterungen fuer Tk Canvas (prüfen was noch nötig!!).

    def itemconfig(self, tagOrId, cnf=None, **kw):
        """Configure resources of an item TAGORID.

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method without arguments.
        """
        print(
            'MfxCanvas: itemconfigure tagOrId=%s, cnf=%s, kw=%s'
            % (tagOrId, cnf, kw))

        if 'image' in cnf:
            # tagOrId ist ein Image oder ein CardImage
            # self.clear_widgets([cnf['image']])
            # self.add_widget(cnf['image'])
            # y = self.yy
            pass
        if 'text' in cnf:
            # tagOrId ist das Label.
            tagOrId.text = cnf['text']
            pass

    def config(self, cnf={}, **kw):
        # print('MfxCanvas: config %s %s' % (cnf, kw))
        if ('cursor' in kw):
            pass
        if ('width' in kw):
            self.size[0] = kw['width']
        if ('height' in kw):
            self.size[1] = kw['height']
        if ('bg' in kw):
            self._bg_color = kw['bg']
            self.update_widget(self.pos, self.size)

    def dtag(self, tag, b=None):
        # print ('Canvas: dtag %s %s' % (tag, b))
        # if (tag in self.tags):
        #  if (self.tags[tag]==b):
        #    del self.tags[tag]
        pass

    def addtag(self, tag, b, c):
        # print ('Canvas: addtag %s %s %s' % (tag, b, c))
        # self.tags[c] = tag
        # self.tags.append(tag)
        pass

    def delete(self, tag):
        # print ('MfxCanvas: delete tag=%s' % tag)
        # y = self.yy
        pass

    def update_idletasks(self):
        print('MfxCanvas: update_idletasks')
        self.wmain.update_idletasks()
