# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Distributed under terms of the CC-BY-SA licence, see:
# https://stackoverflow.com/questions/22583035
# Thanks!


def svgPhotoImage(file_path_name):
    import Image
    import ImageTk
    import rsvg
    import cairo
    "Returns a ImageTk.PhotoImage object represeting the svg file"
    # Based on pygame.org/wiki/CairoPygame and http://bit.ly/1hnpYZY
    svg = rsvg.Handle(file=file_path_name)
    width, height = svg.get_dimension_data()[:2]
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    context = cairo.Context(surface)
    # context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
    svg.render_cairo(context)
    tk_image = ImageTk.PhotoImage('RGBA')
    image = Image.frombuffer('RGBA', (width, height), surface.get_data(),
                             'raw', 'BGRA', 0, 1)
    tk_image.paste(image)
    return tk_image
