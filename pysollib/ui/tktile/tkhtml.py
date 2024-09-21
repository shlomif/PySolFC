#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
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
# ---------------------------------------------------------------------------

import os
import sys
import tkinter

import pysollib.formatter
import pysollib.htmllib2 as htmllib
from pysollib.mfxutil import openURL
from pysollib.mygettext import _
from pysollib.settings import TITLE
from pysollib.ui.tktile.tkutil import bind, unbind_destroy

REMOTE_PROTOCOLS = ("ftp:", "gopher:", "http:", "https:", "mailto:", "news:",
                    "telnet:")

# ************************************************************************
# *
# ************************************************************************


class tkHTMLWriter(pysollib.formatter.NullWriter):
    def __init__(self, text, viewer, app):
        pysollib.formatter.NullWriter.__init__(self)

        self.text = text
        self.viewer = viewer

        if app:
            font = app.getFont("sans")
            fixed = app.getFont("fixed")
        else:
            font = ('helvetica', 12)
            fixed = ('courier', 12)
        size = font[1]
        sign = 1
        if size < 0:
            sign = -1
        self.fontmap = {
            "h1": (font[0], size + 12*sign, "bold"),
            "h2": (font[0], size + 8*sign, "bold"),
            "h3": (font[0], size + 6*sign, "bold"),
            "h4": (font[0], size + 4*sign, "bold"),
            "h5": (font[0], size + 2*sign, "bold"),
            "h6": (font[0], size + 1*sign, "bold"),
            "bold": (font[0], size, "bold"),
            "italic": (font[0], size, "italic"),
            "pre": fixed,
            "code": fixed,
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
        self.text.insert("insert", str(data))

    def anchor_bgn(self, href, name, type):
        if href:
            # self.text.update_idletasks()   # update display during parsing
            self.anchor = (href, name, type)
            self.anchor_mark = self.text.index("insert")

    def anchor_end(self):
        if self.anchor:
            url = self.anchor[0]
            tag = "href_" + url
            self.text.tag_add(tag, self.anchor_mark, "insert")
            from pysollib.options import calcCustomMouseButtonsBinding
            self.text.tag_bind(
                tag,
                calcCustomMouseButtonsBinding("<{mouse_button1}>"),
                self.createCallback(url))
            self.text.tag_bind(
                tag, "<Enter>", lambda e: self.anchor_enter(url))
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
            # print "end_font(%s)" % `self.font`
            self.text.tag_add(self.font, self.font_mark, "insert")
            self.font = None
        # start the new font
        if font:
            # print "start_font(%s)" % `font`
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
        # self.write(self.indent + data + " ")
        self.write(self.indent)
        if data == '*':  # <li>
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
        self.write("\n" * blankline)

    def send_line_break(self):
        self.write("\n")

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
        self.formatter.writer.viewer.showImage(
            src, alt, ismap, align, width, height)


class Base_HTMLViewer:
    def initBindings(self):
        w = self.parent
        bind(w, "WM_DELETE_WINDOW", self.destroy)
        bind(w, "<Escape>", self.destroy)
        bind(w, "<KeyPress-Prior>", self.page_up)
        bind(w, "<KeyPress-Next>", self.page_down)
        bind(w, "<KeyPress-Up>", self.unit_up)
        bind(w, "<KeyPress-Down>", self.unit_down)
        bind(w, "<KeyPress-Begin>", self.scroll_top)
        bind(w, "<KeyPress-Home>", self.scroll_top)
        bind(w, "<KeyPress-End>", self.scroll_bottom)
        bind(w, "<KeyPress-BackSpace>", self.goBack)

    def destroy(self, *event):
        unbind_destroy(self.parent)
        try:
            self.parent.wm_withdraw()
        except Exception:
            pass
        try:
            self.parent.destroy()
        except Exception:
            pass
        self.parent = None

    def _yview(self, *args):
        self.text.yview(*args)
        return 'break'

    def page_up(self, *event):
        return self._yview('scroll', -1, 'page')

    def page_down(self, *event):
        return self._yview('scroll', 1, 'page')

    def unit_up(self, *event):
        return self._yview('scroll', -1, 'unit')

    def unit_down(self, *event):
        return self._yview('scroll', 1, 'unit')

    def scroll_top(self, *event):
        return self._yview('moveto', 0)

    def scroll_bottom(self, *event):
        return self._yview('moveto', 1)

    # locate a file relative to the current self.url
    def basejoin(self, url, baseurl=None, relpath=1):
        if baseurl is None:
            baseurl = self.url
        if 0:
            import urllib.request
            import urllib.parse
            import urllib.error
            url = urllib.request.pathname2url(url)
            if relpath and self.url:
                url = urllib.basejoin(baseurl, url)
        else:
            url = os.path.normpath(url)
            if relpath and baseurl and not os.path.isabs(url):
                h1, t1 = os.path.split(url)
                h2, t2 = os.path.split(baseurl)
                if h1 != h2:
                    url = os.path.join(h2, h1, t1)
                url = os.path.normpath(url)
        return url

    def normurl(self, url, with_protocol=True):
        for p in REMOTE_PROTOCOLS:
            if url.startswith(p):
                break
        else:
            url = self.basejoin(url)
            if with_protocol:
                if os.name == 'nt':
                    url = url.replace('\\', '/')
                url = 'file://'+url
        return url

    def openfile(self, url):
        if url[-1:] == "/" or os.path.isdir(url):
            url = os.path.join(url, "index.html")
        url = os.path.normpath(url)

        def my_open(url):
            if sys.version_info > (3,):
                import codecs
                return codecs.open(url, encoding='utf-8')
            else:
                with open(url, "rb") as fh:
                    return fh
        return my_open(url), url

    def display(self, url, add=1, relpath=1, xview=0, yview=0):
        # for some reason we have to stop the PySol demo
        # (is this a multithread problem with tkinter ?)
        if self.app and self.app.game:
            self.app.game.stopDemo()
            # self.app.game._cancelDrag()
            # pass

        # ftp: and http: would work if we use urllib, but this widget is
        # far too limited to display anything but our documentation...
        for p in REMOTE_PROTOCOLS:
            if url.startswith(p):
                if not openURL(url):
                    self.errorDialog(_('''%(app)s HTML limitation:
The %(protocol)s protocol is not supported yet.

Please use your standard web browser
to open the following URL:
%(url)s
''') % {'app': TITLE, 'protocol': p, 'url': url})
                return

        # locate the file relative to the current url
        url = self.basejoin(url, relpath=relpath)

        # read the file
        try:
            file = None
            if 0:
                import urllib.request
                import urllib.parse
                import urllib.error
                file = urllib.request.urlopen(url)
            else:
                file, url = self.openfile(url)
            data = file.read()
            file.close()
            file = None
        except Exception as ex:
            if file:
                file.close()
            self.errorDialog(_("Unable to service request:\n") + url +
                             "\n\n" + str(ex))
            return
        except Exception:
            if file:
                file.close()
            self.errorDialog(_("Unable to service request:\n") + url)
            return

        self.url = url
        if self.home is None:
            self.home = self.url
        if add:
            self.addHistory(self.url, xview=xview, yview=yview)

        # print self.history.index, self.history.list
        if self.history.index > 1:
            self.backButton.config(state="normal")
        else:
            self.backButton.config(state="disabled")
        if self.history.index < len(self.history.list):
            self.forwardButton.config(state="normal")
        else:
            self.forwardButton.config(state="disabled")

        old_c1, old_c2 = self.defcursor, self.handcursor
        self.defcursor = self.handcursor = "watch"
        self.text.config(cursor=self.defcursor)
        self.text.update_idletasks()
        # self.frame.config(cursor=self.defcursor)
        # self.frame.update_idletasks()
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        # self.images = {}
        writer = tkHTMLWriter(self.text, self, self.app)
        fmt = pysollib.formatter.AbstractFormatter(writer)
        parser = tkHTMLParser(fmt)
        parser.feed(data)
        parser.close()
        self.text.config(state="disabled")
        if 0.0 <= xview <= 1.0:
            self.text.xview_moveto(xview)
        if 0.0 <= yview <= 1.0:
            self.text.yview_moveto(yview)
        self.parent.wm_title(parser.title)
        self.parent.wm_iconname(parser.title)
        self.defcursor, self.handcursor = old_c1, old_c2
        self.text.config(cursor=self.defcursor)
        # self.frame.config(cursor=self.defcursor)

    def addHistory(self, url, xview=0, yview=0):
        if url not in self.visited_urls:
            self.visited_urls.append(url)
        if self.history.index > 0:
            u, xv, yv = self.history.list[self.history.index-1]
            if u == url:
                self.updateHistoryXYView()
                return
        del self.history.list[self.history.index:]
        self.history.list.append((url, xview, yview))
        self.history.index = self.history.index + 1

    def updateHistoryXYView(self):
        if self.history.index > 0:
            url, xview, yview = self.history.list[self.history.index-1]
            xview = self.text.xview()[0]
            yview = self.text.yview()[0]
            self.history.list[self.history.index-1] = (url, xview, yview)

    def goBack(self, *event):
        if self.history.index > 1:
            self.updateHistoryXYView()
            self.history.index = self.history.index - 1
            url, xview, yview = self.history.list[self.history.index-1]
            self.display(url, add=0, relpath=0, xview=xview, yview=yview)

    def goForward(self, *event):
        if self.history.index < len(self.history.list):
            self.updateHistoryXYView()
            url, xview, yview = self.history.list[self.history.index]
            self.history.index = self.history.index + 1
            self.display(url, add=0, relpath=0, xview=xview, yview=yview)

    def goHome(self, *event):
        if self.home and self.home != self.url:
            self.updateHistoryXYView()
            self.display(self.home, relpath=0)

    def errorDialog(self, msg):
        self._calc_MfxMessageDialog()(
            self.parent, title="%(app)s HTML Problem" % {'app': TITLE},
            text=msg,
            # bitmap="warning", # FIXME: this interp don't have images
            strings=(_("&OK"),), default=0)

    def getImage(self, fn):
        if fn in self.images:
            return self.images[fn]
        try:
            img = tkinter.PhotoImage(master=self.parent, file=fn)
        except Exception:
            img = None
        self.images[fn] = img
        return img

    def showImage(self, src, alt, ismap, align, width, height):
        url = self.basejoin(src)
        img = self.getImage(url)
        if img:
            self.text.image_create(index="insert", image=img, padx=0, pady=0)
