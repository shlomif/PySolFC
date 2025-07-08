#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-
# =============================================================================
# Copyright (C) 2017-2023 LB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# =============================================================================

import math
# import inspect

from kivy.core.image import Image as CoreImage
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.widget import Widget

from pysollib.kivy.LBase import LBase

# =============================================================================


class LImage(Widget, LBase):
    CONTAIN = 0
    FILL = 1
    COVER = 2
    SCALE_DOWN = 3
    TILING = 4
    fit_mode = StringProperty("contain")
    texture = ObjectProperty(None, allownone=True)

    def make_scale_down(self, s, p):
        r = self.rect
        t = self.texture.size
        if (t[0] > s[0]) or (t[1] > s[1]):
            self.make_contain(s, p)
        else:
            r.size = t
            r.pos = (p[0]+(s[0]-t[0])/2.0, p[1]+(s[1]-t[1])/2.0)

    def make_fill(self, s, p):
        self.rect.size = s
        self.rect.pos = p

    def make_contain(self, s, p):
        taspect = self.texture.size[0]/self.texture.size[1]
        waspect = s[0]/s[1]
        r = self.rect
        if waspect < taspect:
            s1 = s[1]*waspect/taspect
            r.size = (s[0], s1)
            r.pos = (p[0], p[1]+(s[1]-s1)/2.0)
        else:
            s0 = s[0]/waspect*taspect
            r.size = (s0, s[1])
            r.pos = (p[0]+(s[0]-s0)/2.0, p[1])

    def make_cover(self, s, p):
        aspect = self.texture.size[0]/self.texture.size[1]
        waspect = self.size[0]/self.size[1]

        # 'clamp_to_edge','repeat','mirrored_repeat'
        self.texture.wrap = 'repeat'

        # set rect size/pos to window
        self.rect.size = s
        self.rect.pos = p

        # evaluate original texture coords ?
        u = uu = self.tex_u  # noqa
        v = vv = self.tex_v  # noqa
        w = ww = self.tex_w
        h = hh = self.tex_h

        # in order to center the image in the window
        # modify texture coords
        if waspect < aspect:
            w = ww/aspect*waspect  # noqa
            u = 0.5 - w/2.0        # noqa
        else:
            h = hh*aspect/waspect  # noqa
            v = 0.5 - h/2.0        # noqa

        # and update them.
        tc = ( u, v, u + w, v, u + w, v + h, u, v + h )   # noqa
        self.rect.tex_coords = tc

    def make_tiling(self, s, p):
        # set rect size/pos to window
        self.rect.size = s
        self.rect.pos = p

        # number of repetitions
        t = self.texture
        t.wrap = 'repeat'
        stepsy = self.size[1] / t.size[1]
        stepsx = self.size[0] / t.size[0]

        # set coord parameters.
        w = self.tex_w * stepsx
        h = self.tex_h * stepsy
        u = self.tex_u
        v = stepsy - math.floor(stepsy)
        self.rect.tex_coords = ( u, v, u + w, v, u + w, v + h, u, v + h )  # noqa

    def make_format(self, size, pos):
        if hasattr(self, "rect"):
            if self.texture is None:
                self.rect.size = size
                self.rect.pos = pos
            elif self.fit_num == self.CONTAIN:
                self.make_contain(size, pos)
            elif self.fit_num == self.FILL:
                self.make_fill(size, pos)
            elif self.fit_num == self.COVER:
                self.make_cover(size, pos)
            elif self.fit_num == self.SCALE_DOWN:
                self.make_scale_down(size, pos)
            elif self.fit_num == self.TILING:
                self.make_tiling(size, pos)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # NOTE:
        # properties self.texture and self.fit_mode are
        # already set here from the super call either to its
        # default value or set from evaluaion of a matching kwargs
        # entry.
        '''
        print('LImage __init__: ',self)
        print('stack[1] = ',inspect.stack()[1].frame)
        print('stack[2] = ',inspect.stack()[2].frame)
        print('texture=',self.texture)
        print('fit_mode=',self.fit_mode)
        '''
        self.corePos = None
        self.coreSize = None
        self.source = None
        if "source" in kwargs:
            self.source = kwargs["source"]
            image = CoreImage(self.source)
            self.texture = image.texture

        # update fit_num from fit_mode (needs self.fit_num defined)
        self.fit_num = self.FILL
        self.fit_num_update(self.fit_mode)

        # setup canvas.
        self.background = False
        if "background" in kwargs:
            self.background = kwargs["background"]

        if self.background:
            with self.canvas.before:
                self.color = Color(1.0,1.0,1.0,1.0)  # noqa
                self.rect = Rectangle(texture=self.texture)
        else:
            with self.canvas:
                self.color = Color(1.0,1.0,1.0,1.0)  # noqa
                self.rect = Rectangle(texture=self.texture)

        # save original tex_coords (needs self.rect defined)
        self.tex_coord_update(self.texture)

        # initial size is the natural size of the image.
        if self.texture is not None:
            self.size = self.texture.size

    def tex_coord_update(self, texture):
        if hasattr(self,  "rect"):
            self.rect.texture = texture
            self.tex_u = self.rect.tex_coords[0]
            self.tex_v = self.rect.tex_coords[1]
            self.tex_w = self.rect.tex_coords[2] - self.tex_u
            self.tex_h = self.rect.tex_coords[5] - self.tex_v

    def fit_num_update(self, fit_mode):
        if hasattr(self, "fit_num"):
            if fit_mode == "contain":
                self.fit_num = self.CONTAIN
            if fit_mode == "fill":
                self.fit_num = self.FILL
            if fit_mode == "cover":
                self.fit_num = self.COVER
            if fit_mode == "scale-down":
                self.fit_num = self.SCALE_DOWN
            if fit_mode == "scale_down":
                self.fit_num = self.SCALE_DOWN
            if fit_mode == "tiling":
                self.fit_num = self.TILING

    def on_size(self, a, s):
        self.make_format(s, self.pos)

    def on_pos(self, a, p):
        self.make_format(self.size, p)

    def on_fit_mode(self, a, m):
        # print('on_fit_mode', m)
        self.fit_num_update(self.fit_mode)
        self.make_format(self.size, self.pos)

    def on_texture(self, a, texture):
        # print('on_texture', texture)
        self.tex_coord_update(self.texture)
        self.make_format(self.size, self.pos)

    def setColor(self, color):
        self.color.rgba = color

    def getHeight(self):
        return self.size[1]

    def getWidth(self):
        return self.size[0]

    def subsample(self, r):
        return LImage(texture=self.texture)

# =============================================================================
