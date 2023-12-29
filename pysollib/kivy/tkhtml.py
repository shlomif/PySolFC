#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
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
# ---------------------------------------------------------------------------#

import os
import sys

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import pysollib.formatter
import pysollib.htmllib2 as htmllib
from pysollib.kivy.LApp import LPopCommander
from pysollib.kivy.LApp import LScrollView
from pysollib.kivy.LApp import LTopLevel
from pysollib.kivy.LApp import get_platform
from pysollib.mfxutil import Struct, openURL
from pysollib.mygettext import _
from pysollib.pysoltk import MfxMessageDialog
from pysollib.settings import TITLE

REMOTE_PROTOCOLS = ("ftp:", "gopher:", "http:", "https:", "mailto:", "news:",
                    "telnet:")

# ************************************************************************
# *
# ************************************************************************


if get_platform() == 'android':
    from jnius import autoclass
    from jnius import cast

    def startAndroidBrowser(www):
        # init java classes
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        # String = autoclass('java.lang.String') # get the Java object

        # prepare activity
        # PythonActivity.mActivity is the instance of the current Activity
        # BUT, startActivity is a method from the Activity class, not from our
        # PythonActivity.
        # We need to cast our class into an activity and use it
        currentActivity = cast(
            'android.app.Activity', PythonActivity.mActivity)

        # create the intent
        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.setDataAndType(Uri.parse(www), "application/xhtml+xml")

        # start activity
        currentActivity.startActivity(intent)

# ************************************************************************
# *
# ************************************************************************


def cmp2(a, b):
    """python 3 replacement for python 2 cmp function"""
    return (a > b) - (a < b)


class tkHTMLWriter(pysollib.formatter.NullWriter):
    def __init__(self, text, viewer, app):
        pysollib.formatter.NullWriter.__init__(self)

        self.text = text
        self.viewer = viewer

        #
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
            "h1": (font[0], size + 12 * sign, "bold"),
            "h2": (font[0], size + 8 * sign, "bold"),
            "h3": (font[0], size + 6 * sign, "bold"),
            "h4": (font[0], size + 4 * sign, "bold"),
            "h5": (font[0], size + 2 * sign, "bold"),
            "h6": (font[0], size + 1 * sign, "bold"),
            "bold": (font[0], size, "bold"),
            "italic": (font[0], size, "italic"),
            "pre": fixed,
        }

        self.text.config(cursor=self.viewer.defcursor, font=font)
        for f in self.fontmap.keys():
            self.text.tag_config(f, font=self.fontmap[f])

        self.anchor = None
        self.anchor_mark = None
        self.font = None
        self.font_mark = None
        self.indent = ""
        self.text.label.bind(on_ref_press=self.refpress)

    '''
    def createCallback(self, href):
        class Functor:
            def __init__(self, viewer, arg):
                self.viewer = viewer
                self.arg = arg

            def __call__(self, *args):
                self.viewer.updateHistoryXYView()
                return self.viewer.display(self.arg)
        return Functor(self.viewer, href)
    '''

    def write(self, data):
        # print('writer: write %s' % data)
        self.text.insert("insert", data)

    def anchor_bgn(self, href, name, type):
        # print('writer: anchor_bgn %s - %s' % (href, name))
        if href:
            # self.text.update_idletasks()   # update display during parsing
            self.anchor = (href, name, type)
            self.anchor_mark = self.text.index("insert")
            self.write('[ref=' + href + ']')

            url = self.anchor[0]
            fg = '0000cc'
            u = self.viewer.normurl(url, with_protocol=False)
            if u in self.viewer.visited_urls:
                fg = '660099'
            self.write('[color=' + fg + '][i]')
            # self.text.tag_config(tag, foreground=fg, underline=1)

    def refpress(self, instance, value):
        # print('writer: refpress %s, %s' % (instance, value))
        pass

    def anchor_end(self):
        # print('writer: anchor_end')
        if self.anchor:

            self.anchor = None
            self.write('[/i][/color]')
            self.write('[/ref]')

    def anchor_enter(self, url):
        url = self.viewer.normurl(url)
        self.viewer.statusbar.updateText(url=url)
        self.text.config(cursor=self.viewer.handcursor)

    def anchor_leave(self, *args):
        self.viewer.statusbar.updateText(url='')
        self.text.config(cursor=self.viewer.defcursor)

    def new_font(self, font):
        # print('writer: new_font %s' % str(font))
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
        # print('writer: new_margin %s, %s' % (margin, level))
        self.indent = "    " * level

    def send_label_data(self, data):
        # print('writer: send_label_data %s' % (data))
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
        # print('writer: send_paragraph %s' % (blankline))
        self.write('\n' * blankline)

    def send_line_break(self):
        # print('writer: send_break')
        self.write('\n')

    def send_hor_rule(self, *args):
        if (args):
            pass
            # print('writer: send_hor_rule %s' % (args))
        # width = int(int(self.text["width"]) * 0.9)
        width = 20
        self.write("_" * width)
        self.write("\n")

    def send_literal_data(self, data):
        # print('writer: send_literal_data %s' % (data))
        self.write(data)

    def send_flowing_data(self, data):
        # print('writer: send_flowing_data %s' % (data))
        self.write(data)

# ************************************************************************
# *
# ************************************************************************


class tkHTMLParser(htmllib.HTMLParser):
    def anchor_bgn(self, href, name, type):
        self.formatter.flush_softspace()
        htmllib.HTMLParser.anchor_bgn(self, href, name, type)
        self.formatter.writer.anchor_bgn(href, name, type)

    def close(self):
        # print('tkHTMLParser1: close()')
        self.formatter.writer.text.applyBuffer()
        # label = self.formatter.writer.text.label
        # print('tkHTMLParser: label.refs %s' % str(label.refs))
        # print ('tkHTMLParser: label.refs %s' % str(Label.refs))

        # print('tkHTMLParser2: close()')
        htmllib.HTMLParser.close(self)

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

# ************************************************************************
# *
# ************************************************************************


class HTMLButton(Button):
    def __init__(self, **kw):
        super(HTMLButton, self).__init__(**kw)

    def config(self, **kw):
        pass


class HTMLLabel(Label):
    def __init__(self, **kw):
        super(HTMLLabel, self).__init__(**kw)

        self.bind(size=self.onUpdate)
        self.bind(pos=self.onUpdate)
        self.bind(text=self.onUpdate)

    def onUpdate(self, instance, size):
        self.size_hint_y = None
        self.text_size = self.width, None
        self.texture_update()
        self.height = self.texture_size[1]


class HTMLText(LScrollView, LPopCommander):
    def __init__(self, **kw):
        super(HTMLText, self).__init__(**kw)

        self.viewer = kw['viewer']
        # self.scroll_timeout = 250
        # self.scroll_distance = 20
        self.do_scroll_x = False

        self.multiLabel = True
        if self.multiLabel:
            self.label = BoxLayout(orientation='vertical', size_hint=(1, None))
        else:
            self.label = HTMLLabel(text='', markup=True)
            self.label.bind(on_ref_press=self.viewer.refpress)
        self.tags = {}
        self.textbuffer = ''
        self.add_widget(self.label)

    def applyBuffer(self):
        if self.multiLabel:
            splittedText = self.textbuffer.split('\n')
            self.textbuffer = ''
            self.label.clear_widgets()

            def add_label(si, ei):
                lt = '\n'.join(splittedText[si:ei])
                if lt == '':
                    lt = ' '
                label = HTMLLabel(text=lt, markup=True)
                label.bind(on_ref_press=self.viewer.refpress)
                label.bind(size=self.on_size)
                self.label.add_widget(label)

            index = 0
            sindex = 0
            limit = 1000
            summe = 0
            for k in splittedText:
                l = len(k)  # noqa
                s = summe + l
                index += 1
                if s > limit:
                    add_label(sindex, index)
                    sindex = index
                    summe = l
                else:
                    summe = s
            add_label(sindex, index)
        else:
            self.label.text = self.textbuffer

    def on_size(self, o, s):
        y = 0
        for c in self.label.children:
            y += c.size[1]
        self.label.size[1] = y

    def config(self, **kw):
        # print('config: %s' % kw)
        pass

    def update_idletasks(self):
        pass

    def delete(self, val, val1):
        pass

    def insert(self, cmd, data):
        # print('insert text: %s' % data)
        self.textbuffer = self.textbuffer + data
        # self.label.text = self.textbuffer
        pass

    def index(self, cmd):
        # print('index: %s' % cmd)
        # was sollen wir hier zuruckgeben ?
        return 0

    def tag_add(self, font, fontmark, cmd):
        # print('tag_add: %s, %s, %s' % (font, fontmark, cmd))
        pass

    def tag_config(self, tag, **kw):
        # print('tag_config: %s, %s' % (tag, kw))
        # self.tags[tag] = kw

        # for t, k in self.tags:
        #    print('tagslist: %s, %s' % (t, k))

        pass

    def xview_moveto(self, xview):
        # print('xview_moveto: %s' % xview)
        pass

    def yview_moveto(self, yview):
        # print('yview_moveto: %s' % yview)
        pass


class HTMLViewer:
    symbols_fn = {}  # filenames, loaded in Application.loadImages3
    symbols_img = {}

    def make_pop_command(self, parent, title):
        def pop_command(event):
            if self.history.index > 1:
                self.goBack(event)
                return None
            del self.history.list
            self.history.index = 0
            parent.popWork(title)
        return pop_command

    def make_close_command(self, parent, title):
        def close_command(event):
            del self.history.list
            self.history.index = 0
            parent.popWork(title)
        return close_command

    def refpress(self, instance, value):
        # print('writer: refpress %s, %s' % (instance, value))
        self.updateHistoryXYView()
        return self.display(value)

    def __init__(self, parent, app=None, home=None):
        self.parent = parent
        self.app = app
        self.home = home
        self.url = None
        self.history = Struct(
            list=[],
            index=0,
        )
        self.visited_urls = []
        self.images = {}
        # need to keep a reference because of garbage collection
        self.defcursor = "default"
        # self.defcursor = parent["cursor"]
        # self.defcursor = 'xterm'
        self.handcursor = "hand2"

        self.title = _("Browser")
        self.window = None
        self.running = False

        # prüfen ob noch aktiv.

        if parent.workStack.peek(self.title) is not None:
            parent.popWork(self.title)

        pc = self.make_pop_command(parent, self.title)
        cc = self.make_close_command(parent, self.title)

        # create new dialog.

        window = LTopLevel(app.top, self.title, size_hint=(2.0, 1.0))
        window.titleline.bind(on_press=cc)
        self.parent.pushWork(self.title, window)
        self.window = window
        self.running = True

        content = BoxLayout(orientation='vertical')

        # create button line

        buttonline = BoxLayout(
            orientation='horizontal', size_hint=(None, 0.07))

        self.backButton = HTMLButton(text=_("Back"), on_release=self.goBack)
        self.homeButton = HTMLButton(text=_("Index"), on_release=self.goHome)
        self.forwardButton = HTMLButton(
            text=_("Forward"), on_release=self.goForward)
        # self.closeButton = HTMLButton(text=_("Close"), on_release=cc)
        # -> use title bar as usual.

        buttonline.add_widget(self.backButton)
        buttonline.add_widget(self.homeButton)
        buttonline.add_widget(self.forwardButton)
        # buttonline.add_widget(self.closeButton)
        self.buttonline = buttonline

        # create text widget

        self.text = HTMLText(
            pop_command=pc, text="hallo", size_hint=(None, 1.0), viewer=self)

        # add content: first text, buttonline at bottom.

        content.add_widget(self.text)
        content.add_widget(buttonline)
        self.window.content.add_widget(content)
        self.window.bind(size=self.on_size)

        # load images ?
        for name, fn in self.symbols_fn.items():
            self.symbols_img[name] = self.getImage(fn)

    def on_size(self, o, s):
        self.text.size = s
        self.buttonline.size = s

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
            import urllib
            url = urllib.pathname2url(url)
            if relpath and self.url:
                url = urllib.basejoin(baseurl, url)
        else:
            url = os.path.normpath(url)
            if relpath and baseurl and not os.path.isabs(url):
                h1, t1 = os.path.split(url)
                h2, t2 = os.path.split(baseurl)
                if cmp2(h1, h2) != 0:
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
                url = 'file://' + url
        return url

    def openfile(self, url):
        if url[-1:] == "/" or os.path.isdir(url):
            url = os.path.join(url, "index.html")
        url = os.path.normpath(url)
        if sys.version_info > (3,):
            import codecs
            return codecs.open(url, encoding='utf-8'), url
        return open(url, "rb"), url

    def display(self, url, add=1, relpath=1, xview=0, yview=0):
        # for some reason we have to stop the PySol demo
        # (is this a multithread problem with Tkinter ?)
        if self.app and self.app.game:
            self.app.game.stopDemo()
            # self.app.game._cancelDrag()
            # pass

        # this is a workaround for android: Small devices cannot
        # render the whole text into a label ... and Android does not
        # allow local files be displayed in the local browser. The
        # simplest way is to take it from the original web site.
        '''
        if get_platform() == 'android':
            if os.path.basename(url) == 'license.html':
                url = 'https://www.gnu.org/licenses/gpl-3.0-standalone.html'
        '''

        # ftp: and http: would work if we use urllib, but this widget is
        # far too limited to display anything but our documentation...
        for p in REMOTE_PROTOCOLS:
            if url.startswith(p):
                plat = get_platform()
                if plat == 'android':
                    print("Open url: %s (TBD)" % url)
                    startAndroidBrowser(url)
                elif not openURL(url):
                    return

        # locate the file relative to the current url
        url = self.basejoin(url, relpath=relpath)

        # read the file
        try:
            file = None
            if 0:
                import urllib
                file = urllib.urlopen(url)
            else:
                file, url = self.openfile(url)
            data = file.read()
            file.close()
            file = None
        except Exception:
            print("Open url(1) - Exception: %s" % url)
            if file:
                file.close()

            '''
            self.errorDialog(_("Unable to service request:\n") + url)
            '''
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
        self.text.textbuffer = ''
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
        # self.parent.wm_title(parser.title)
        self.window.titleline.text = parser.title
        self.parent.wm_iconname(parser.title)
        self.defcursor, self.handcursor = old_c1, old_c2
        self.text.config(cursor=self.defcursor)

    def addHistory(self, url, xview=0, yview=0):
        if url not in self.visited_urls:
            self.visited_urls.append(url)
        if self.history.index > 0:
            u, xv, yv = self.history.list[self.history.index - 1]
            if cmp2(u, url) == 0:
                self.updateHistoryXYView()
                return
        del self.history.list[self.history.index:]
        self.history.list.append((url, xview, yview))
        self.history.index = self.history.index + 1

    def updateHistoryXYView(self):
        if self.history.index > 0:
            url, xview, yview = self.history.list[self.history.index - 1]
            self.history.list[self.history.index - 1] = (url, xview, yview)

    def goBack(self, *event):
        if self.history.index > 1:
            self.updateHistoryXYView()
            self.history.index = self.history.index - 1
            url, xview, yview = self.history.list[self.history.index - 1]
            self.display(url, add=0, relpath=0, xview=xview, yview=yview)

    def goForward(self, *event):
        if self.history.index < len(self.history.list):
            self.updateHistoryXYView()
            url, xview, yview = self.history.list[self.history.index]
            self.history.index = self.history.index + 1
            self.display(url, add=0, relpath=0, xview=xview, yview=yview)

    def goHome(self, *event):
        if self.home and cmp2(self.home, self.url) != 0:
            self.updateHistoryXYView()
            self.display(self.home, relpath=0)

    def errorDialog(self, msg):
        MfxMessageDialog(self.parent,
                         title=_("%s HTML Problem") % TITLE,
                         text=msg,
                         # bitmap="warning"
                         # FIXME: this interp don't have images
                         strings=(_("&OK"), ), default=0)

    def getImage(self, fn):
        if fn in self.images:
            return self.images[fn]
        else:
            return None

    def showImage(self, src, alt, ismap, align, width, height):
        url = self.basejoin(src)
        img = self.getImage(url)
        if img:
            self.text.image_create(index="insert", image=img, padx=0, pady=0)


# ************************************************************************
# *
# ************************************************************************

''
