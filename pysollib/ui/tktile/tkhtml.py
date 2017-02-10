#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##---------------------------------------------------------------------------##

import htmllib, formatter

REMOTE_PROTOCOLS = ("ftp:", "gopher:", "http:", "mailto:", "news:", "telnet:")

# ************************************************************************
# *
# ************************************************************************

class tkHTMLWriter(formatter.NullWriter):
    def __init__(self, text, viewer, app):
        formatter.NullWriter.__init__(self)

        self.text = text
        self.viewer = viewer

        ##
        if app:
            font = app.getFont("sans")
            fixed = app.getFont("fixed")
        else:
            font = ('helvetica', 12)
            fixed = ('courier', 12)
        size = font[1]
        sign = 1
        if size < 0: sign = -1
        self.fontmap = {
            "h1"      : (font[0], size + 12*sign, "bold"),
            "h2"      : (font[0], size +  8*sign, "bold"),
            "h3"      : (font[0], size +  6*sign, "bold"),
            "h4"      : (font[0], size +  4*sign, "bold"),
            "h5"      : (font[0], size +  2*sign, "bold"),
            "h6"      : (font[0], size +  1*sign, "bold"),
            "bold"    : (font[0], size, "bold"),
            "italic"  : (font[0], size, "italic"),
            "pre"     : fixed,
        }

        self.text.config(cursor=self.viewer.defcursor, font=font)
        for f in self.fontmap.keys():
            self.text.tag_config(f, font=self.fontmap[f])

        self.anchor = None
        self.anchor_mark = None
        self.font = None
        self.font_mark = None
        self.indent = ""

    def createCallback(self, href):
        class Functor:
            def __init__(self, viewer, arg):
                self.viewer = viewer
                self.arg = arg
            def __call__(self, *args):
                self.viewer.updateHistoryXYView()
                return self.viewer.display(self.arg)
        return Functor(self.viewer, href)

    def write(self, data):
        self.text.insert("insert", data)

    def anchor_bgn(self, href, name, type):
        if href:
            ##self.text.update_idletasks()   # update display during parsing
            self.anchor = (href, name, type)
            self.anchor_mark = self.text.index("insert")

    def anchor_end(self):
        if self.anchor:
            url = self.anchor[0]
            tag = "href_" + url
            self.text.tag_add(tag, self.anchor_mark, "insert")
            self.text.tag_bind(tag, "<1>", self.createCallback(url))
            self.text.tag_bind(tag, "<Enter>", lambda e: self.anchor_enter(url))
            self.text.tag_bind(tag, "<Leave>", self.anchor_leave)
            fg = 'blue'
            u = self.viewer.normurl(url, with_protocol=False)
            if u in self.viewer.visited_urls:
                fg = '#660099'
            self.text.tag_config(tag, foreground=fg, underline=1)
            self.anchor = None

    def anchor_enter(self, url):
        url = self.viewer.normurl(url)
        self.viewer.statusbar.updateText(url=url)
        self.text.config(cursor=self.viewer.handcursor)

    def anchor_leave(self, *args):
        self.viewer.statusbar.updateText(url='')
        self.text.config(cursor=self.viewer.defcursor)

    def new_font(self, font):
        # end the current font
        if self.font:
            ##print "end_font(%s)" % `self.font`
            self.text.tag_add(self.font, self.font_mark, "insert")
            self.font = None
        # start the new font
        if font:
            ##print "start_font(%s)" % `font`
            self.font_mark = self.text.index("insert")
            if font[0] in self.fontmap:
                self.font = font[0]
            elif font[3]:
                self.font = "pre"
            elif font[2]:
                self.font = "bold"
            elif font[1]:
                self.font = "italic"
            else:
                self.font = None

    def new_margin(self, margin, level):
        self.indent = "    " * level

    def send_label_data(self, data):
        ##self.write(self.indent + data + " ")
        self.write(self.indent)
        if data == '*': # <li>
            img = self.viewer.symbols_img.get('disk')
            if img:
                self.text.image_create(index='insert', image=img,
                                       padx=0, pady=0)
            else:
                self.write('*')
        else:
            self.write(data)
        self.write(' ')

    def send_paragraph(self, blankline):
        self.write('\n' * blankline)

    def send_line_break(self):
        self.write('\n')

    def send_hor_rule(self, *args):
        width = int(int(self.text["width"]) * 0.9)
        self.write("_" * width)
        self.write("\n")

    def send_literal_data(self, data):
        self.write(data)

    def send_flowing_data(self, data):
        self.write(data)


# ************************************************************************
# *
# ************************************************************************

class tkHTMLParser(htmllib.HTMLParser):
    def anchor_bgn(self, href, name, type):
        self.formatter.flush_softspace()
        htmllib.HTMLParser.anchor_bgn(self, href, name, type)
        self.formatter.writer.anchor_bgn(href, name, type)

    def anchor_end(self):
        if self.anchor:
            self.anchor = None
        self.formatter.writer.anchor_end()

    def do_dt(self, attrs):
        self.formatter.end_paragraph(1)
        self.ddpop()

    def handle_image(self, src, alt, ismap, align, width, height):
        self.formatter.writer.viewer.showImage(src, alt, ismap, align, width, height)

