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

__all__ = ['HTMLViewer']

# imports
import os, sys, re, types
import htmllib, formatter
import traceback

import gtk, pango, gobject
from gtk import gdk

if __name__ == '__main__':
    d = os.path.abspath(os.path.join(sys.path[0], '..', '..'))
    sys.path.append(d)
    import gettext
    gettext.install('pysol', d, unicode=True)

# PySol imports
from pysollib.mfxutil import Struct, openURL
from pysollib.settings import TITLE

# Toolkit imports
from tkutil import bind, unbind_destroy, loadImage
from tkwidget import MfxMessageDialog


REMOTE_PROTOCOLS = ('ftp:', 'gopher:', 'http:', 'mailto:', 'news:', 'telnet:')


# ************************************************************************
# *
# ************************************************************************

class tkHTMLWriter(formatter.NullWriter):
    def __init__(self, text, viewer, app):
        formatter.NullWriter.__init__(self)

        self.text = text      # gtk.TextBuffer
        self.viewer = viewer  # HTMLViewer

        self.anchor = None
        self.anchor_mark = None

        self.font = None
        self.font_mark = None
        self.indent = ''


    def write(self, data):
        data = unicode(data)
        self.text.insert(self.text.get_end_iter(), data, len(data))

    def anchor_bgn(self, href, name, type):
        if href:
            ##self.text.update_idletasks()   # update display during parsing
            self.anchor = (href, name, type)
            self.anchor_mark = self.text.get_end_iter().get_offset()

    def anchor_end(self):
        if self.anchor:
            href = self.anchor[0]
            tag_name = 'href_' + href
            if tag_name in self.viewer.anchor_tags:
                tag = self.viewer.anchor_tags[tag_name][0]
            else:
                tag = self.text.create_tag(tag_name, foreground='blue',
                                           underline=pango.UNDERLINE_SINGLE)
                self.viewer.anchor_tags[tag_name] = (tag, href)
                tag.connect('event', self.viewer.anchor_event, href)
            u = self.viewer.normurl(href, with_protocol=False)
            if u in self.viewer.visited_urls:
                tag.set_property('foreground', '#660099')
            start = self.text.get_iter_at_offset(self.anchor_mark)
            end = self.text.get_end_iter()
            ##print 'apply_tag href >>', start.get_offset(), end.get_offset()
            self.text.apply_tag(tag, start, end)

            self.anchor = None

    def new_font(self, font):
        # end the current font
        if self.font:
            ##print 'end_font(%s)' % `self.font`
            start = self.text.get_iter_at_offset(self.font_mark)
            end = self.text.get_end_iter()
            ##print 'apply_tag font >>', start.get_offset(), end.get_offset()
            self.text.apply_tag_by_name(self.font, start, end)
            self.font = None
        # start the new font
        if font:
            ##print 'start_font(%s)' % `font`
            self.font_mark = self.text.get_end_iter().get_offset()
            if font[0] in self.viewer.fontmap:
                self.font = font[0]
            elif font[3]:
                self.font = 'pre'
            elif font[2]:
                self.font = 'bold'
            elif font[1]:
                self.font = 'italic'
            else:
                self.font = None

    def new_margin(self, margin, level):
        self.indent = '    ' * level

    def send_label_data(self, data):
        ##self.write(self.indent + data + ' ')
        self.write(self.indent)
        if data == '*': # <li>
            img = self.viewer.symbols_img.get('disk')
            if img:
                self.text.insert_pixbuf(self.text.get_end_iter(), img)
            else:
                self.write('*') ##unichr(0x2022)
        else:
            self.write(data)
        self.write(' ')

    def send_paragraph(self, blankline):
        self.write('\n' * blankline)

    def send_line_break(self):
        self.write('\n')

    def send_hor_rule(self, *args):
        ##~ width = int(int(self.text['width']) * 0.9)
        width = 70
        self.write('_' * width)
        self.write('\n')

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


# ************************************************************************
# *
# ************************************************************************

class HTMLViewer:
    symbols_fn = {}  # filenames, loaded in Application.loadImages3
    symbols_img = {}

    def __init__(self, parent, app=None, home=None):
        self.parent = parent
        self.app = app
        self.home = home
        self.url = None
        self.history = Struct(
            list = [],
            index = 0,
        )
        self.visited_urls = []
        self.images = {}
        self.anchor_tags = {}

        # create buttons
        button_width = 8
        vbox = gtk.VBox()
        parent.table.attach(vbox,
            0, 1,                   0, 1,
            gtk.EXPAND | gtk.FILL,  gtk.EXPAND | gtk.FILL | gtk.SHRINK,
            0,                      0)

        buttons_box = gtk.HBox()
        vbox.pack_start(buttons_box, fill=True, expand=False)
        for name, label, callback in (
            ('homeButton',    _('Index'),   self.goHome),
            ('backButton',    _('Back'),    self.goBack),
            ('forwardButton', _('Forward'), self.goForward),
            ('closeButton',   _('Close'),   self.destroy) ):
            button = gtk.Button(label)
            button.show()
            button.connect('clicked', callback)
            buttons_box.pack_start(button, fill=True, expand=False)
            button.set_property('can-focus', False)
            setattr(self, name, button)

        # create text widget
        self.textview = gtk.TextView()
        self.textview.show()
        self.textview.set_left_margin(10)
        self.textview.set_right_margin(10)
        self.textview.set_cursor_visible(False)
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.textbuffer = self.textview.get_buffer()

        sw = gtk.ScrolledWindow()
        sw.set_property('hscrollbar-policy', gtk.POLICY_AUTOMATIC)
        sw.set_property('vscrollbar-policy', gtk.POLICY_AUTOMATIC)
        sw.set_property('border-width', 0)
        sw.add(self.textview)
        sw.show()
        vbox.pack_start(sw, fill=True, expand=True)
        self.vadjustment = sw.get_vadjustment()
        self.hadjustment = sw.get_hadjustment()

        # statusbar
        self.statusbar = gtk.Statusbar()
        self.statusbar.show()
        vbox.pack_start(self.statusbar, fill=True, expand=False)

        # load images
        for name, fn in self.symbols_fn.items():
            self.symbols_img[name] = self.getImage(fn)

        # bindings
        parent.connect('key-press-event', self.key_press_event)
        parent.connect('destroy', self.destroy)
        self.textview.connect('motion-notify-event', self.motion_notify_event)
        self.textview.connect('leave-notify-event', self.leave_event)
        self.textview.connect('enter-notify-event', self.motion_notify_event)

        self._changed_cursor = False

        self.createFontMap()

        # cursor
        self.defcursor = gdk.XTERM
        self.handcursor = gdk.HAND2
        ##self.textview.realize()
        ##window = self.textview.get_window(gtk.TEXT_WINDOW_TEXT)
        ##window.set_cursor(gdk.Cursor(self.defcursor))

        parent.set_default_size(600, 440)
        parent.show_all()
        gobject.idle_add(gtk.main)


    def motion_notify_event(self, widget, event):
        x, y, _ = widget.window.get_pointer()
        x, y = widget.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, x, y)
        tags = widget.get_iter_at_location(x, y).get_tags()
        is_over_anchor = False
        for tag, href in self.anchor_tags.values():
            if tag in tags:
                is_over_anchor = True
                break
        if is_over_anchor:
            if not self._changed_cursor:
                ##print 'set cursor hand'
                window = widget.get_window(gtk.TEXT_WINDOW_TEXT)
                window.set_cursor(gdk.Cursor(self.handcursor))
                self._changed_cursor = True
            self.statusbar.pop(0)
            href = url = self.normurl(href)
            self.statusbar.push(0, href)
        else:
            if self._changed_cursor:
                ##print 'set cursor xterm'
                window = widget.get_window(gtk.TEXT_WINDOW_TEXT)
                window.set_cursor(gdk.Cursor(self.defcursor))
                self._changed_cursor = False
            self.statusbar.pop(0)
        return False

    def leave_event(self, widget, event):
        if self._changed_cursor:
            ##print 'set cursor xterm'
            window = widget.get_window(gtk.TEXT_WINDOW_TEXT)
            window.set_cursor(gdk.Cursor(self.defcursor))
            self._changed_cursor = False
        self.statusbar.pop(0)

    def anchor_event(self, tag, textview, event, iter, href):
        #print 'anchor_event:', args
        if event.type == gdk.BUTTON_PRESS and event.button == 1:
            self.updateHistoryXYView()
            self.display(href)
            return True
        return False

    def key_press_event(self, w, e):
        if gdk.keyval_name(e.keyval) == 'Escape':
            self.destroy()


    def createFontMap(self):
        try: ## if app
            default_font = self.app.getFont('sans')
            fixed_font = self.app.getFont('fixed')
        except:
            traceback.print_exc()
            default_font = ('times new roman', 12)
            fixed_font = ('courier', 12)
        size = default_font[1]
        sign = 1
        if size < 0: sign = -1
        self.fontmap = {
            'h1'      : (default_font[0], size + 12*sign, 'bold'),
            'h2'      : (default_font[0], size +  8*sign, 'bold'),
            'h3'      : (default_font[0], size +  6*sign, 'bold'),
            'h4'      : (default_font[0], size +  4*sign, 'bold'),
            'h5'      : (default_font[0], size +  2*sign, 'bold'),
            'h6'      : (default_font[0], size +  1*sign, 'bold'),
            'bold'    : (default_font[0], size,           'bold'),
        }

        for tag_name in self.fontmap.keys():
            font = self.fontmap[tag_name]
            font = font[0]+' '+str(font[1])
            tag = self.textbuffer.create_tag(tag_name, font=font)
            tag.set_property('weight', pango.WEIGHT_BOLD)

        font = font[0]+' '+str(font[1])
        tag = self.textbuffer.create_tag('italic', style=pango.STYLE_ITALIC)
        self.fontmap['italic'] = (font[0], size, 'italic')
        font = fixed_font[0]+' '+str(fixed_font[1])
        self.textbuffer.create_tag('pre', font=font)
        self.fontmap['pre'] = fixed_font
        # set default font
        fd = pango.FontDescription(default_font[0]+' '+str(default_font[1]))
        if 'bold' in default_font:
            fd.set_weight(pango.WEIGHT_BOLD)
        if 'italic' in default_font:
            fd.set_style(pango.STYLE_ITALIC)
        self.textview.modify_font(fd)

    def destroy(self, *event):
        self.parent.destroy()
        self.parent = None

    def get_position(self):
        pos = self.hadjustment.get_value(), self.vadjustment.get_value()
        return pos

    def set_position(self, pos):
        def callback(pos, hadj, vadj):
            hadj.set_value(pos[0])
            vadj.set_value(pos[1])
        gobject.idle_add(callback, pos, self.hadjustment, self.vadjustment)

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
        if url[-1:] == '/' or os.path.isdir(url):
            url = os.path.join(url, 'index.html')
        url = os.path.normpath(url)
        return open(url, 'rb'), url

    def display(self, url, add=1, relpath=1, position=(0,0)):
        ##print 'display:', url, position
        # for some reason we have to stop the PySol demo
        # (is this a multithread problem with Tkinter ?)
        try:
            ##self.app.game.stopDemo()
            ##self.app.game._cancelDrag()
            pass
        except:
            pass

        # ftp: and http: would work if we use urllib, but this widget is
        # far too limited to display anything but our documentation...
        for p in REMOTE_PROTOCOLS:
            if url.startswith(p):
                if not openURL(url):
                    self.errorDialog(TITLE + _('''HTML limitation:
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
            self.errorDialog(_('Unable to service request:\n') + url + '\n\n' + str(ex))
            return
        except:
            if file: file.close()
            self.errorDialog(_('Unable to service request:\n') + url)
            return

        self.url = url
        if self.home is None:
            self.home = self.url
        if add:
            self.addHistory(self.url, position=position)

        ##print self.history.index, self.history.list
        if self.history.index > 1:
            self.backButton.set_sensitive(True)
        else:
            self.backButton.set_sensitive(False)
        if self.history.index < len(self.history.list):
            self.forwardButton.set_sensitive(True)
        else:
            self.forwardButton.set_sensitive(False)

        start, end = self.textbuffer.get_bounds()
        self.textbuffer.delete(start, end)

        writer = tkHTMLWriter(self.textbuffer, self, self.app)
        fmt = formatter.AbstractFormatter(writer)
        parser = tkHTMLParser(fmt)
        parser.feed(data)
        parser.close()

        self.set_position(position)

        self.parent.set_title(parser.title)


    def addHistory(self, url, position=(0,0)):
        if url not in self.visited_urls:
            self.visited_urls.append(url)
        if self.history.index > 0:
            u, pos = self.history.list[self.history.index-1]
            if u == url:
                self.updateHistoryXYView()
                return
        del self.history.list[self.history.index : ]
        self.history.list.append((url, position))
        self.history.index = self.history.index + 1

    def updateHistoryXYView(self):
        if self.history.index > 0:
            url, position = self.history.list[self.history.index-1]
            position = self.get_position()
            self.history.list[self.history.index-1] = (url, position)

    def goBack(self, *event):
        if self.history.index > 1:
            self.updateHistoryXYView()
            self.history.index = self.history.index - 1
            url, position = self.history.list[self.history.index-1]
            self.display(url, add=0, relpath=0, position=position)

    def goForward(self, *event):
        if self.history.index < len(self.history.list):
            self.updateHistoryXYView()
            url, position = self.history.list[self.history.index]
            self.history.index = self.history.index + 1
            self.display(url, add=0, relpath=0, position=position)

    def goHome(self, *event):
        if self.home and self.home != self.url:
            self.updateHistoryXYView()
            self.display(self.home, relpath=0)

    def errorDialog(self, msg):
        d = MfxMessageDialog(self.parent, title=TITLE+' HTML Problem',
                             text=msg, bitmap='warning',
                             strings=(_('&OK'),), default=0)

    def getImage(self, fn):
        if fn in self.images:
            return self.images[fn]
        try:
            img = gdk.pixbuf_new_from_file(fn)
        except:
            img = None
        self.images[fn] = img
        return img

    def showImage(self, src, alt, ismap, align, width, height):
        url = self.basejoin(src)
        img = self.getImage(url)
        if img:
            iter = self.textbuffer.get_end_iter()
            self.textbuffer.insert_pixbuf(iter, img)



# ************************************************************************
# *
# ************************************************************************


def tkhtml_main(args):
    try:
        url = args[1]
    except:
        url = os.path.join(os.pardir, os.pardir, 'data', 'html', 'index.html')
    top = gtk.Window()
    table = gtk.Table()
    table.show()
    top.add(table)
    top.table = table
    viewer = HTMLViewer(top)
    viewer.app = None
    viewer.display(url)
    top.connect('destroy', lambda w: gtk.main_quit())
    gtk.main()
    return 0

if __name__ == '__main__':
    sys.exit(tkhtml_main(sys.argv))


