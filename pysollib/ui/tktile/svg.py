# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Distributed under terms of the CC-BY-SA licence, see:
# https://stackoverflow.com/questions/22583035
# Thanks!

import cairo

from gi.repository import Rsvg

from pysollib.mfxutil import Image, ImageTk


class SVGManager:
    """docstring for SVGManager"""
    def __init__(self, filename):
        self.filename = filename
        self.svg = Rsvg.Handle().new_from_file(filename)

    def render_fragment(self, id_, width, height):
        id__ = '#' + id_
        """docstring for render_"""
        dims = self.svg.get_dimensions_sub(id__)[1]
        width_, height_ = dims.width, dims.height
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     int(width_), int(height_))
        context = cairo.Context(surface)
        self.svg.render_cairo_sub(context, id__)
        tk_image = ImageTk.PhotoImage('RGBA')
        image = Image.frombuffer('RGBA', (width_, height_),
                                 bytes(surface.get_data()),
                                 'raw', 'BGRA', 0, 1)
        return image.crop((0, 0, width, height))
        tk_image = ImageTk.PhotoImage(image.crop((0, 0, width, height)))
        return tk_image
