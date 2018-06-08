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

# PySol imports
# from pysollib.mfxutil import Image, ImageTk
from pysollib.kivy.LApp import LImage
from pysollib.kivy.LApp import LImage as Image
from pysollib.kivy.LApp import LImageItem
from pysollib.kivy.LApp import LColorToKivy
from pysollib.kivy.LApp import LText
from pysollib.kivy.LApp import LRectangle
from pysollib.kivy.LApp import LLine
from pysollib.kivy.LApp import LAnimationManager

# kivy imports
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import Rectangle

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
        # logging.info('MfxCanvasGroup: __init__() %s - %s' %
        #  (str(canvas), str(tag)))
        self.canvas = canvas
        self.bindings = {}
        self.stack = None

    def tkraise(self):
        pass

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


class MfxCanvasImage(object):
    def __init__(self, canvas, *args, **kwargs):

        # print ('MfxCanvasImage: %s | %s | %s' % (canvas, args, kwargs))

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

        super(MfxCanvasImage, self).__init__()
        self.canvas = canvas
        self.animation = None

        ed = kwargs['image']
        size = ed.size

        if type(ed) is LImageItem:
            aimage = ed
        else:
            if (ed.source is None):
                image = LImage(texture=ed.texture)
                image.size = [ed.getWidth(), ed.getHeight()]
                aimage = LImageItem(size=image.size, group=group)
                aimage.add_widget(image)
                size = image.size
            else:
                image = LImage(texture=ed.texture)
                # image = LImage(source=ed.source)
                image.size = [ed.getWidth(), ed.getHeight()]
                aimage = LImageItem(size=ed.size, group=group)
                aimage.add_widget(image)
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
        print('MfxCanvasImage: __del__(%s)' % self.image)
        self.canvas.clear_widgets([self.image])

    def config(self, **kw):
        pass

    def tkraise(self, aboveThis=None):
        # print('MfxCanvasImage: tkraise')
        abitm = None
        if aboveThis:
            abitm = aboveThis.widget
        if not self.animation:
            self.canvas.tag_raise(self.image, abitm)
        pass

    def addtag(self, tag):
        # print('MfxCanvasImage: addtag %s' % tag)
        self.group = tag
        if (self.image):
            self.image.group = tag
        pass

    def dtag(self, tag):
        # print('MfxCanvasImage: remtag %s' % tag)
        self.group = None
        if (self.image):
            self.image.group = None
        pass

    def delete(self):
        # print('MfxCanvasImage: delete()')
        self.canvas.clear_widgets([self.image])

    def move(self, dx, dy):
        # print ('MfxCanvasImage: move %s, %s' % (dx, dy))
        image = self.image
        dsize = image.coreSize
        dpos = (image.corePos[0] + dx, image.corePos[1] + dy)
        image.corePos = dpos
        if not self.animation:
            image.pos, image.size = self.canvas.CoreToKivy(dpos, dsize)

    def makeAnimStart(self):
        def animStart(anim, widget):
            # print('MfxCanvasImage: animStart')
            image = self.image
            self.canvas.tag_raise(image, None)
            pass
        return animStart

    def makeAnimEnd(self, dpos, dsize):
        def animEnd(anim, widget):
            # print('MfxCanvasImage: animEnd %s' % self)
            self.animation = False
            image = self.image
            image.pos, image.size = self.canvas.CoreToKivy(dpos, dsize)
            pass
        return animEnd

    def animatedMove(self, dx, dy, duration=0.2):
        # print ('MfxCanvasImage: animatedMove %s, %s' % (dx, dy))

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

        self.animation = True
        ssize = image.coreSize
        spos = (image.corePos[0], image.corePos[1])
        spos, ssize = self.canvas.CoreToKivy(spos, ssize)
        LAnimationManager.create(
            spos,
            image,
            x=pos[0], y=pos[1],
            duration=duration, transition=transition,
            bindS=self.makeAnimStart(),
            bindE=self.makeAnimEnd(dpos, dsize))

    # def moveTo(self, x, y):
    #    c = self.coords()
    #    self.move(x - int(c[0]), y - int(c[1]))

    def show(self):
        self.config(state='normal')

    def hide(self):
        self.config(state='hidden')


class MfxCanvasLine(object):
    def __init__(self, canvas, *args, **kwargs):
        print('MfxCanvasLine: %s %s' % (args, kwargs))

        self.canvas = canvas
        line = LLine(canvas, args, **kwargs)
        line.pos, line.size = canvas.CoreToKivy(line.corePos, line.coreSize)
        canvas.add_widget(line)
        self.canvas = canvas
        self.line = line
        self.widget = line

    def delete_deferred(self, seconds):
        print('MfxCanvasLine: delete_deferred(%s)' % seconds)
        Clock.schedule_once(lambda dt: self.delete(), seconds)

    def delete(self):
        print('MfxCanvasLine: delete()')
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

        print(
            'MfxCanvasText: %s | %s, %s, %s | %s'
            % (canvas, x, y, preview, kwargs))

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

    def config(self, **kw):
        print('MfxCanvasText: config %s' % kw)
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


class MfxCanvas(Widget):

    def __init__(self, wmain, *args, **kw):
        # super(MfxCanvas, self).__init__(**kw)
        super(MfxCanvas, self).__init__()

        # self.tags = {}   # bei basisklasse widget (ev. nur vorläufig)

        self.wmain = wmain
        print('MfxCanvas: wmain = %s' % self.wmain)

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

        # print('MfxCanvas: update_widget size=(%s, %s)' %
        #       (self.size[0], self.size[1]))

        # Update Skalierungsparameter

        oldscale = self.scale
        newscale = self.scalefactor()
        print('MfxCanvas: scale factor old= %s, new=%s' %
              (oldscale, newscale))
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

        self.canvas.before.clear()
        texture = None
        if self._bg_img:
            texture = self._bg_img.texture

            # Color only: Nur eine Hintergrundfarbe wird installiert.
        if texture is None:
            kc = LColorToKivy(self._bg_color)
            self.canvas.before.add(
                Color(kc[0], kc[1], kc[2], kc[3]))
            self.canvas.before.add(
                Rectangle(pos=self.pos, size=self.size))
            return

        # Image: Das Bild wird im Fenster expandiert.
        if self._stretch_bg_image:
            if self._save_aspect_bg_image == 0:
                self.canvas.before.add(
                    Rectangle(texture=texture, pos=self.pos, size=self.size))
            else:
                # TBD: gesucht: aspect erhaltende skalierung
                self.canvas.before.add(
                    Rectangle(texture=texture, pos=self.pos, size=self.size))
            return

            # Tiles: Die Kacheln werden im Fenster ausgelegt und minim
        # skaliert, damit sie genau passen.
        else:
            print('tiles !')
            stsize = (texture.size[0] * self.scale,
                      texture.size[1] * self.scale)
            stepsy = int(self.size[1] / stsize[1]) + 1
            stepsx = int(self.size[0] / stsize[0]) + 1

            scaley = 1.0 * self.size[1] / (stepsy * stsize[1])
            sy = scaley * stsize[1]
            scalex = 1.0 * self.size[0] / (stepsx * stsize[0])
            sx = scalex * stsize[0]
            tsize = (sx, sy)

            # print ('self.size = %s, %s' % (self.size[0], self.size[1]))
            # print ('sx, sy = %s, %s' % (stepsx, stepsy))
            for y in range(0, stepsy):
                py = y * sy
                for x in range(0, stepsx):
                    px = x * sx
                    tpos = (self.pos[0] + px, self.pos[1] + py)
                    self.canvas.before.add(
                        Rectangle(texture=texture, pos=tpos, size=tsize))

    def setBackgroundImage(self, event=None):

        print('setBackgroundImage', self._bg_img)

        if not self._bg_img:  # solid color
            return
        return 1

    # Funktionen, welche vom Core aufgerufen werden.

    def winfo_width(self):
        # return self.r_width
        cpos, csize = self.KivyToCoreP(self.pos, self.size, self.scale)
        print('MfxCanvas: winfo_width %s' % (csize[0]))
        return csize[0]

    def winfo_height(self):
        # return self.r_height
        cpos, csize = self.KivyToCoreP(self.pos, self.size, self.scale)
        print('MfxCanvas: winfo_height %s' % (csize[1]))
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
        # print('MfxCanvas: tag_raise, itm=%s, aboveThis=%s' % (itm, abitm))
        if (itm is not None):
            if (abitm is None):
                # print('MfxCanvas: tag_raise: to top')
                self.clear_widgets([itm])
                self.add_widget(itm)
            else:
                print('MfxCanvas: tag_raise: to specified position')
                ws = []
                for c in reversed(self.children):   # reversed!
                    if c != itm and c != abitm:
                        ws.append(c)
                    if c == itm:
                        ws.append(abitm)
                        ws.append(itm)    # (~shadow image!)
                self.clear_widgets()
                for w in ws:
                    self.add_widget(w)

    def tag_lower(self, id, belowThis=None):
        print('MfxCanvas: tag_lower(%s, %s)' % (id, belowThis))
        # y = self.yy  # kommt das vor ?
        pass

    #
    #
    #
    def setInitialSize(self, width, height):
        print('MfxCanvas: setInitialSize request %s/%s' % (width, height))
        print(
            'MfxCanvas: setInitialSize actual  %s/%s'
            % (self.size[0], self.size[1]))
        self.r_width = width
        self.r_height = height

        # ev. update anstossen
        self.update_widget(self.pos, self.size)

        # self.size[0] = width
        # self.size[1] = height
        return

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

    def setTextColor(self, color):
        print('MfxCanvas: setTextColor1 %s' % color)
        if color is None:
            c = self.cget("bg")
            if not isinstance(c, str) or c[0] != "#" or len(c) != 7:
                return
            v = []
            for i in (1, 3, 5):
                v.append(int(c[i:i + 2], 16))
            luminance = (0.212671 * v[0] + 0.715160 *
                         v[1] + 0.072169 * v[2]) / 255
            # print c, ":", v, "luminance", luminance
            color = ("#000000", "#ffffff")[luminance < 0.3]

        print('MfxCanvas: setTextColor2 %s' % color)
        if self._text_color != color:
            self._text_color = color

            # falls wir das wollen in kivy:
            # -> text_color als property deklarieren, und a.a.O binden.
            # for item in self._text_items:
            #    item.config(fill=self._text_color)

    def setTile(self, image, stretch=0, save_aspect=0):

        print('setTile: %s, %s' % (image, stretch))
        if image:
            try:
                # print ('setTile: image.open %s, %s' % (image, Image))
                bs = False
                if stretch > 0:
                    bs = True
                self._bg_img = Image(source=image, allow_stretch=bs)

                self._stretch_bg_image = stretch
                self._save_aspect_bg_image = save_aspect
                self.setBackgroundImage()
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
        print('MfxCanvas: config %s %s' % (cnf, kw))
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
