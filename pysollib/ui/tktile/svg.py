# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Distributed under terms of the CC-BY-SA licence, see:
# https://stackoverflow.com/questions/22583035
# Thanks!

import Image

import ImageTk

import cairo

import rsvg


class SVGManager:
    """docstring for SVGManager"""
    def __init__(self, filename):
        self.filename = filename
        self.svg = rsvg.Handle(filename)

    def render_fragment(self, id_):
        """docstring for render_"""
        width, height = self.svg.get_sub_dimension_data(id_)[:2]
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     int(width), int(height))
        context = cairo.Context(surface)
        self.svg.render_cairo_sub(context, id_)
        tk_image = ImageTk.PhotoImage('RGBA')
        image = Image.frombuffer('RGBA', (width, height), surface.get_data(),
                                 'raw', 'BGRA', 0, 1)
        tk_image.paste(image)
        return tk_image
