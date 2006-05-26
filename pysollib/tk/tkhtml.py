## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = ['tkHTMLViewer']

# imports
import os, sys, re, string, types
import htmllib, formatter
import Tkinter

# PySol imports
from pysollib.mfxutil import Struct, openURL
from pysollib.settings import PACKAGE

# Toolkit imports
from tkutil import bind, unbind_destroy, loadImage
from tkwidget import MfxDialog
from statusbar import HtmlStatusbar


REMOTE_PROTOCOLS = ("ftp:", "gopher:", "http:", "mailto:", "news:", "telnet:")


# /***********************************************************************
# //
# ************************************************************************/

class MfxScrolledText(Tkinter.Text):
    def __init__(self, parent=None, **cnf):
        fcnf = {}
        for k in cnf.keys():
            if type(k) is types.ClassType or k == "name":
                fcnf[k] = cnf[k]
                del cnf[k]
        if cnf.has_key("bg"):
            fcnf["bg"] = cnf["bg"]
        self.frame = apply(Tkinter.Frame, (parent,), fcnf)
        self.vbar = Tkinter.Scrollbar(self.frame, name="vbar")
        self.vbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        cnf["name"] = "text"
        apply(Tkinter.Text.__init__, (self, self.frame), cnf)
        self.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
        self["yscrollcommand"] = self.vbar.set
        self.vbar["command"] = self.yview

        # FIXME: copy Pack methods of self.frame -- this is a hack!
        for m in Tkinter.Pack.__dict__.keys():
            if m[0] != "_" and m != "config" and m != "configure":
                ##print m, getattr(self.frame, m)
                setattr(self, m, getattr(self.frame, m))

        self.frame["highlightthickness"] = 0
        self.vbar["highlightthickness"] = 0
        ##print self.__dict__

    # XXX these are missing in Tkinter.py
    def xview_moveto(self, fraction):
        return self.tk.call(self._w, "xview", "moveto", fraction)
    def xview_scroll(self, number, what):
        return self.tk.call(self._w, "xview", "scroll", number, what)
    def yview_moveto(self, fraction):
        return self.tk.call(self._w, "yview", "moveto", fraction)
    def yview_scroll(self, number, what):
        return self.tk.call(self._w, "yview", "scroll", number, what)


class MfxReadonlyScrolledText(MfxScrolledText):
    def __init__(self, parent=None, **cnf):
        apply(MfxScrolledText.__init__, (self, parent), cnf)
        self.config(state="disabled", insertofftime=0)
        self.frame.config(takefocus=0)
        self.config(takefocus=0)
        self.vbar.config(takefocus=0)


# /***********************************************************************
# //
# ************************************************************************/

class tkHTMLWriter(formatter.DumbWriter):
    def __init__(self, text, viewer, app):
        formatter.DumbWriter.__init__(self, self, maxcol=9999)

        self.text = text
        self.viewer = viewer

        ##
        font = app.getFont("sans")
        size = font[1]
        fixed = app.getFont("fixed")
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
        ## FIXME
        ##if self.col == 0 and self.atbreak == 0:
        ##    self.text.insert("insert", self.indent)
        self.text.insert("insert", data)

    def __write(self, data):
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
            self.text.tag_config(tag, foreground="blue", underline=1)
            self.anchor = None

    def anchor_enter(self, url):
        for p in REMOTE_PROTOCOLS:
            if url.startswith(p):
                break
        else:
            url = 'file://'+self.viewer.basejoin(url)
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
            if self.fontmap.has_key(font[0]):
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
        self.__write(self.indent + data + " ")

    def send_paragraph(self, blankline):
        if self.col > 0:
            self.__write("\n")
        if blankline > 0:
            self.__write("\n" * blankline)
        self.col = 0
        self.atbreak = 0

    def send_hor_rule(self, *args):
        width = int(int(self.text["width"]) * 0.9)
        self.__write("_" * width)
        self.__write("\n")
        self.col = 0
        self.atbreak = 0


# /***********************************************************************
# //
# ************************************************************************/

class tkHTMLParser(htmllib.HTMLParser):
    def anchor_bgn(self, href, name, type):
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


# /***********************************************************************
# //
# ************************************************************************/

class tkHTMLViewer:
    def __init__(self, parent):
        self.parent = parent
        self.home = None
        self.url = None
        self.history = Struct(
            list = [],
            index = 0,
        )
        self.images = {}    # need to keep a reference because of garbage collection
        self.defcursor = parent["cursor"]
        self.handcursor = "hand2"

        # create buttons
        button_width = 8
        self.homeButton = Tkinter.Button(parent, text=_("Index"),
                                         width=button_width,
                                         command=self.goHome)
        self.homeButton.grid(row=0, column=0, sticky='w')
        self.backButton = Tkinter.Button(parent, text=_("Back"),
                                         width=button_width,
                                         command=self.goBack)
        self.backButton.grid(row=0, column=1, sticky='w')
        self.forwardButton = Tkinter.Button(parent, text=_("Forward"),
                                            width=button_width,
                                            command=self.goForward)
        self.forwardButton.grid(row=0, column=2, sticky='w')
        self.closeButton = Tkinter.Button(parent, text=_("Close"),
                                          width=button_width,
                                          command=self.destroy)
        self.closeButton.grid(row=0, column=3, sticky='e')

        # create text widget
        text_frame = Tkinter.Frame(parent)
        text_frame.grid(row=1, column=0, columnspan=4, sticky='nsew')
        self.text = MfxReadonlyScrolledText(text_frame,
                                            fg="#000000", bg="#f7f3ff",
                                            cursor=self.defcursor,
                                            wrap="word", padx=20, pady=20)
        self.text.pack(side="top", fill="both", expand=1)

        # statusbar
        self.statusbar = HtmlStatusbar(parent, row=2, column=0, columnspan=4)

        parent.columnconfigure(2, weight=1)
        parent.rowconfigure(1, weight=1)

        self.initBindings()

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
        except: pass
        try:
            self.parent.destroy()
        except: pass
        self.parent = None

    def page_up(self, *event):
        self.text.yview_scroll(-1, "page")
        return "break"
    def page_down(self, *event):
        self.text.yview_scroll(1, "page")
        return "break"
    def unit_up(self, *event):
        self.text.yview_scroll(-1, "unit")
        return "break"
    def unit_down(self, *event):
        self.text.yview_scroll(1, "unit")
        return "break"
    def scroll_top(self, *event):
        self.text.yview_moveto(0)
        return "break"
    def scroll_bottom(self, *event):
        self.text.yview_moveto(1)
        return "break"

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
                if cmp(h1, h2) != 0:
                    url = os.path.join(h2, h1, t1)
                url = os.path.normpath(url)
        return url

    def openfile(self, url):
        if url[-1:] == "/" or os.path.isdir(url):
            url = os.path.join(url, "index.html")
        url = os.path.normpath(url)
        return open(url, "rb"), url

    def display(self, url, add=1, relpath=1, xview=0, yview=0):
        # for some reason we have to stop the PySol demo
        # (is this a multithread problem with Tkinter ?)
        if self.__dict__.get("app"):
            if self.app and self.app.game:
                self.app.game.stopDemo()
                ##self.app.game._cancelDrag()

        # ftp: and http: would work if we use urllib, but this widget is
        # far too limited to display anything but our documentation...
        for p in REMOTE_PROTOCOLS:
            if url.startswith(p):
                if not openURL(url):
                    self.errorDialog(PACKAGE + _(''' HTML limitation:
The %s protocol is not supported yet.

Please use your standard web browser
to open the following URL:
%s
''') % (p, url))
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
        except Exception, ex:
            if file: file.close()
            self.errorDialog(_("Unable to service request:\n") + url + "\n\n" + str(ex))
            return
        except:
            if file: file.close()
            self.errorDialog(_("Unable to service request:\n") + url)
            return

        self.url = url
        if self.home is None:
            self.home = self.url
        if add:
            self.addHistory(self.url, xview=xview, yview=yview)

        ##print self.history.index, self.history.list
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
        ##self.frame.config(cursor=self.defcursor)
        ##self.frame.update_idletasks()
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        ##self.images = {}
        writer = tkHTMLWriter(self.text, self, self.app)
        fmt = formatter.AbstractFormatter(writer)
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
        ##self.frame.config(cursor=self.defcursor)

    def addHistory(self, url, xview=0, yview=0):
        if self.history.index > 0:
            u, xv, yv = self.history.list[self.history.index-1]
            if cmp(u, url) == 0:
                self.updateHistoryXYView()
                return
        del self.history.list[self.history.index : ]
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
        if self.home and cmp(self.home, self.url) != 0:
            self.updateHistoryXYView()
            self.display(self.home, relpath=0)

    def errorDialog(self, msg):
        d = MfxDialog(self.parent, title=PACKAGE+" HTML Problem",
                      text=msg, bitmap="warning",
                      strings=(_("OK"),), default=0)

    def showImage(self, src, alt, ismap, align, width, height):
        url = self.basejoin(src)
        ##print url, ":", src, alt, ismap, align, width, height
        if self.images.has_key(url):
            img = self.images[url]
        else:
            try:
                img = Tkinter.PhotoImage(master=self.parent, file=url)
            except:
                img = None
            self.images[url] = img
        ##print url, img
        if img:
            padx, pady = 10, 10
            padx, pady = 0, 20
            if align.lower() == "left":
                padx = 0
            self.text.image_create(index="insert", image=img, padx=padx, pady=pady)



# /***********************************************************************
# //
# ************************************************************************/


def tkhtml_main(args):
    try:
        url = args[1]
    except:
        url = os.path.join(os.pardir, os.pardir, "data", "html", "index.html")
    top = Tkinter.Tk()
    top.wm_minsize(400, 200)
    viewer = tkHTMLViewer(top)
    viewer.display(url)
    top.mainloop()
    return 0

if __name__ == "__main__":
    sys.exit(tkhtml_main(sys.argv))


