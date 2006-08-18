## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
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
## <markus.oberhumer@jk.uni-linz.ac.at>
## http://wildsau.idv.uni-linz.ac.at/mfx/pysol.html
##
##---------------------------------------------------------------------------##


# imports
import os, sys, time, types

import gtk
from gtk import gdk

# PySol imports
## from pysollib.images import Images

# Toolkit imports
from tkutil import makeToplevel, loadImage


# /***********************************************************************
# //
# ************************************************************************/

class TclError:
    pass

def makeHelpToplevel(parent, title=None, class_=None):
    return makeToplevel(parent, title=title, class_=class_, gtkclass=_MfxToplevel)


class MfxCheckMenuItem:
    def __init__(self, menubar, path=None):
        self.menubar = menubar
        self.path = path
        self.value = None
    def get(self):
        ##print 'MfxCheckMenuItem.get:', self.path
        if self.path is None: return 0
        w = self.menubar.menus.get_widget(self.path)
        return w.active
    def set(self, value):
        ##print 'MfxCheckMenuItem.set:', value, self.path
        if self.path is None: return
        if not value or value == 'false': value = 0
        assert type(value) is types.IntType and 0 <= value <= 1
        self.value = value
        w = self.menubar.menus.get_widget(self.path)
        w.set_active(value)
        #print self.path, value, w, w.active


class MfxRadioMenuItem(MfxCheckMenuItem):
    def get(self):
        ##print 'MfxRadioMenuItem.get:', self.path, self.value
        if self.path is None: return 0
        w = self.menubar.menus.get_widget(self.path)
        #from pprint import pprint
        #pprint(dir(w))
        #print 'widget:', w
        #print w.active
        #print w.__dict__
        return self.value
    def set(self, value):
        ##print 'MfxRadioMenuItem.set:', value, self.path
        if self.path is None: return
        if not value or value == 'false': value = 0
        assert type(value) is types.IntType and 0 <= value
        self.value = value
        #w = self.menubar.menus.get_widget(self.path)
        #w.set_active(value)
        #print self.path, value #, w, w.active


class StringVar:
    def set(self, v):
        pass


# /***********************************************************************
# // A toplevel window.
# ************************************************************************/

class _MfxToplevel(gtk.Window):
    def __init__(self, *args, **kw):
        gtk.Window.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        ##~ self.style = self.get_style().copy()
        ##~ self.set_style(self.style)
        #self.vbox = gtk.VBox()
        #self.vbox.show()
        #self.add(self.vbox)
        self.table = gtk.Table(3, 5, False)
        self.add(self.table)
        self.table.show()
        self.realize()

    def cget(self, attr):
        if attr == 'cursor':
            # FIXME
            return gdk.LEFT_PTR
            return self.get_window().get_cursor(v)
        elif attr in ("background", "bg"):
            c = self.style.bg[gtk.STATE_NORMAL]
            c = '#%02x%02x%02x' % (c.red/256, c.green/256, c.blue/256)
            return c
        print "Toplevel cget:", attr
        ##~ raise AttributeError, attr
        return None

    def configure(self, **kw):
        height, width = -1, -1
        for k, v in kw.items():
            if k in ("background", "bg"):
                ##print "Toplevel configure: bg"
                ##~ c = self.get_colormap().alloc_color(v)
                ##~ self.style.bg[gtk.STATE_NORMAL] = c
                ##~ self.set_style(self.style)
                ##~ self.queue_draw()
                pass
            elif k == "cursor":
                self.setCursor(v)
            elif k == "height":
                height = v
            elif k == "width":
                width = v
            else:
                print "Toplevel configure:", k, v
                raise AttributeError, k
        if height > 0 and width > 0:
            ##print 'configure: size:', width, height
            ## FIXME
            #self.set_default_size(width, height)
            #self.set_size_request(width, height)
            #self.set_geometry_hints(base_width=width, base_height=height)
            pass


    config = configure

    def mainloop(self):
        gtk.main()      # the global function

    def mainquit(self):
        gtk.main_quit()      # the global function

    def screenshot(self, filename):
        pass

    def setCursor(self, cursor):
        self.get_window().set_cursor(cursor_new(v))

    def tk_setPalette(self, *args):
        # FIXME ?
        pass

    def update(self):
        self.update_idletasks()

    def update_idletasks(self):
        ##print '_MfxToplevel.update_idletasks'
        while gtk.events_pending():
            gtk.main_iteration(True)

    def winfo_ismapped(self):
        # FIXME
        return 1

    def winfo_screenwidth(self):
        return gdk.screen_width()

    def winfo_screenheight(self):
        return gdk.screen_height()

    def winfo_screendepth(self):
        ##print 'winfo_screendepth', self.window.get_geometry()
        return self.window.get_geometry()[-1]

    def wm_command(self, *args):
        # FIXME
        pass

    def wm_deiconify(self):
        self.present()

    def wm_geometry(self, newGeometry=None):
        ##print 'wm_geometry', newGeometry
        if not newGeometry:
            pass
            ##self.reshow_with_initial_size()
            ##self.resize(1, 1)
        else:
            pass
            ##w, h = newGeometry
            ##self.resize(w, h)



    def wm_group(self, pathName=None):
        # FIXME
        pass

    def wm_iconbitmap(self, name):
        if name and name[0] == '@' and name[-4:] == '.xbm':
            name = name[1:-4] + '.xpm'
            bg = self.get_style().bg[gtk.STATE_NORMAL]
            pixmap, mask = create_pixmap_from_xpm(self, bg, name)
            self.set_icon(pixmap, mask)

    def wm_iconname(self, name):
        pass
        ##~ self.set_icon_name(name)

    def wm_minsize(self, width, height):
        pass
        ##~ self.set_geometry_hints(min_width=width, min_height=height)

    def wm_protocol(self, name=None, func=None):
        if name == 'WM_DELETE_WINDOW':
            self.connect("delete_event", func)
        else:
            raise AttributeError, name

    def wm_title(self, title):
        self.set_title(title)

    def tkraise(self):
        self.present()

    def option_add(self, *args):
        ##print self, 'option_add'
        pass

    def option_get(self, *args):
        ##print self, 'option_get'
        return None

    def grid_columnconfigure(self, *args, **kw):
        ##print self, 'grid_columnconfigure'
        pass

    def grid_rowconfigure(self, *args, **kw):
        ##print self, 'grid_rowconfigure'
        pass

    def interruptSleep(self, *args, **kw):
        ##print self, 'interruptSleep'
        pass

    def wm_state(self):
        ##print self, 'wm_state'
        pass



# /***********************************************************************
# // The root toplevel window of an application.
# ************************************************************************/

class MfxRoot(_MfxToplevel):
    def __init__(self, **kw):
        apply(_MfxToplevel.__init__, (self,), kw)
        self.app = None

    def connectApp(self, app):
        self.app = app

    # sometimes an update() is needed under Windows, whereas
    # under Unix an update_idletask() would be enough...
    def busyUpdate(self):
        game = None
        if self.app: game = self.app.game
        if not game:
            self.update()
        elif not game.busy:
            game.busy = 1
            self.update()
            game.busy = 0

    # FIXME - make sleep interruptible
    def sleep(self, seconds):
        gdk.window_process_all_updates()
        time.sleep(seconds)

    def wmDeleteWindow(self, *args):
        if self.app and self.app.menubar:
            self.app.menubar.mQuit()
        else:
            ##self.after_idle(self.quit)
            pass
        return True
