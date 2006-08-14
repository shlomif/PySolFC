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
import os, re, sys

import gtk
TRUE, FALSE = True, False

# PySol imports

from pysollib.actions import PysolToolbarActions



# /***********************************************************************
# //
# ************************************************************************/

class PysolToolbar(PysolToolbarActions):
    def __init__(self, top, dir, size=0, relief=0, compound=None):

        PysolToolbarActions.__init__(self)
        self.top = top
        self.dir = dir
        self.side = -1

        self.toolbar = gtk.Toolbar(gtk.ORIENTATION_HORIZONTAL,
                                   gtk.TOOLBAR_ICONS)

        #self.bg = top.get_style().bg[gtk.STATE_NORMAL]
        ui_info = '''
<ui>
  <toolbar  name='ToolBar'>
    <toolitem action='New'/>
    <toolitem action='Restart'/>
    <separator/>
    <toolitem action='Open'/>
    <toolitem action='Save'/>
    <separator/>
    <toolitem action='Undo'/>
    <toolitem action='Redo'/>
    <toolitem action='Autodrop'/>
    <separator/>
    <toolitem action='Stats'/>
    <toolitem action='Rules'/>
    <separator/>
    <toolitem action='Quit'/>
  </toolbar>
</ui>
'''
        ui_manager = self.top.ui_manager # created in menubar.py
        ui_manager_id = ui_manager.add_ui_from_string(ui_info)

        toolbar = ui_manager.get_widget("/ToolBar")
        toolbar.set_tooltips(True)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.show()

        top.table.attach(toolbar,
                         0, 1,                   1, 2,
                         gtk.EXPAND | gtk.FILL,  0,
                         0,                      0)
        toolbar.show()



        # no longer needed
        self.bg = None
        #



    # util
    def _createButton(self, name, command, padx=0, stock=None, tooltip=None):
        ##button = self.toolbar.append_item(name, tooltip, "", stock, command)
        ##button = self.toolbar.insert_stock(stock, tooltip, '', command, None, -1)
        image = gtk.Image()
        image.set_from_stock(stock, gtk.ICON_SIZE_SMALL_TOOLBAR)

        button = gtk.ToolButton(None, name)
        button.set_tooltip(tooltip)
        #button.set_relief(gtk.RELIEF_NONE)
        #button.connect('activate', command)
        self.toolbar.insert(button, -1)
        setattr(self, name + "_button", button)


    def _createLabel(self, name, padx=0, side='IGNORE', tooltip=None):
        ## FIXME: append_widget
        pass

    def _createSeparator(self):
        self.toolbar.append_space()


    #
    # wrappers
    #

    def _busy(self):
        return not (self.side and self.game and not self.game.busy and self.menubar)

    def destroy(self):
        self.toolbar.destroy()

    def getSide(self):
        return self.side

    def getSize(self):
        return 0

    def hide(self, resize=1):
        self.show(None, resize)

    def show(self, side=1, resize=1):
        self.side = side
        if side:
            self.toolbar.show()
        else:
            self.toolbar.hide()


    #
    # public methods
    #

    def setCursor(self, cursor):
        if self.side:
            # FIXME
            pass

    def setRelief(self, relief):
        # FIXME
        pass

    def updateText(self, **kw):
        # FIXME
        pass


# /***********************************************************************
# //
# ************************************************************************/

#%ifndef BUNDLE

class TestToolbar(PysolToolbar):
    def __init__(self, top, args):
        from util import DataLoader
        dir = "kde-large"
        dir = "gnome-large"
        if len(args) > 1: dir = args[1]
        dir = os.path.join(os.pardir, os.pardir, "data", "toolbar", dir)
        ##print dataloader.dir
        PysolToolbar.__init__(self, top, dir)
        # test some settings
        self.updateText(player="Player\nPySol")
        self.undo_button.set_state(STATE_INSENSITIVE)
    def mQuit(self, *args):
        gtk.main_quit()

def toolbar_main(args):
    from tkwrap import MfxRoot
    root = MfxRoot()
    root.connect("destroy", mainquit)
    root.connect("delete_event", mainquit)
    toolbar = TestToolbar(root, args)
    root.show_all()
    mainloop()
    return 0

if __name__ == '__main__':
    sys.exit(toolbar_main(sys.argv))

#%endif

