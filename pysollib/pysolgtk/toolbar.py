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
    def __init__(self, top, dir, relief=0):
        PysolToolbarActions.__init__(self)
        self.top = top
        self.dir = dir
        self.side = -1

        self.toolbar = gtk.Toolbar(ORIENTATION_HORIZONTAL, TOOLBAR_ICONS)
        self.bg = top.get_style().bg[STATE_NORMAL]

        self._createButton('new',     self.mNewGame, tooltip='New game')
        self._createButton('open',    self.mOpen   , tooltip='Open a \nsaved game')
        self._createSeparator()
        self._createButton('restart', self.mRestart, tooltip='Restart the \ncurrent game')
        self._createButton('save',    self.mSave,    tooltip='Save game')
        self._createSeparator()
        self._createButton('undo',    self.mUndo,    tooltip='Undo')
        self._createButton('redo',    self.mRedo,    tooltip='Redo')
        self._createButton('autodrop',self.mDrop,    tooltip='Auto drop')
        self._createSeparator()
        self._createButton('stats',   self.mStatus,  tooltip='Statistics')
        self._createButton('rules',   self.mHelpRules, tooltip='Rules')
        self._createSeparator()
        self._createButton('quit',    self.mQuit,     tooltip='Quit PySol')
        self._createSeparator()
        # no longer needed
        self.bg = None
        #
        top.vbox.pack_start(self.toolbar, FALSE, FALSE)


    # util
    def _createButton(self, name, command, padx=0, tooltip=None):
##         file = os.path.join(self.dir, name+".gif")
##         im = GdkImlib.Image(file)
##         im.render()
##         pixmap = im.make_pixmap()
##         if tooltip: tooltip = re.sub(r'\n', '', tooltip)

##append_item(text, tooltip_text, tooltip_private_text, icon, callback, user_data=None)

        button = self.toolbar.append_item(name, tooltip, "", None, command)
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
        mainquit()

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

