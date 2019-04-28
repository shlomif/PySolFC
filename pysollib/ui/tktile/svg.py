# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Distributed under terms of the CC-BY-SA licence, see:
# https://stackoverflow.com/questions/22583035
# Thanks!

try:
    from PySide2.QtGui import QPixmap  # noqa: F401
    from PySolFC_KCard import MyKCardDeck
except BaseException:
    def MyKCardDeck():
        return None

# import cairo
# from gi import require_version
# require_version('Rsvg', '2.0')
# from gi.repository import Rsvg  # noqa: E402

from pysollib.mfxutil import Image  # noqa: E402


class SVGManager:
    """docstring for SVGManager"""
    def __init__(self, filename):
        self.filename = filename
        # self.svg = Rsvg.Handle().new_from_file(filename)
        self.d = MyKCardDeck()

    # Taken from https://stackoverflow.com/questions/44471795
    # Under MIT License - thanks.
    def pixbuf2image(self, pxb):
        """ Convert GdkPixbuf.Pixbuf to PIL image """
        data = pxb.get_pixels()
        w = pxb.get_width()
        h = pxb.get_height()
        stride = pxb.get_rowstride()
        mode = "RGB"
        if pxb.get_has_alpha():
            mode = "RGBA"
        img = Image.frombytes(mode, (w, h), data, "raw", mode, stride)
        return img

    def render_fragment(self, rank, suit, width, height):
        if not self.d:
            return None
        image = Image.fromqpixmap(
            self.d.get_card_pixmap(
                rank + 1 + {'c': 0, 'd': 1, 'h': 2, 's': 3}[suit]*0x100))
        if 0:
            id__ = '#' + "queen_heart"
            """docstring for render_"""
            dims = self.svg.get_dimensions_sub(id__)[1]
            width_, height_ = dims.width, dims.height
            pix = self.svg.get_pixbuf_sub(id__)
            if False:
                import cairo
                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                             int(width_), int(height_))
                context = cairo.Context(surface)
                # context.scale(width_, height_)
                assert self.svg.render_cairo_sub(context, id__)
                buf = bytes(surface.get_data())
                image = Image.frombuffer('RGBA', (width_, height_), buf,
                                         'raw', 'BGRA', 0, 1)
            image = self.pixbuf2image(pix)
        return image.resize((width, height))
