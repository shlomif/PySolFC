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
import math, os, re, string, sys

import gtk
from gtk import gdk
TRUE, FALSE = True, False

# PySol imports
from pysollib.gamedb import GI
from pysollib.actions import PysolMenubarActions

# toolkit imports
from tkutil import setTransient
from tkutil import color_tk2gtk, color_gtk2tk
from selectcardset import SelectCardsetDialogWithPreview
from selectcardset import SelectCardsetByTypeDialogWithPreview


# /***********************************************************************
# // - create menubar
# // - update menubar
# // - menu actions
# ************************************************************************/

class PysolMenubar(PysolMenubarActions):
    def __init__(self, app, top, progress=None):
        PysolMenubarActions.__init__(self, app, top)
        self.menus = None
        self.menu_items = None
        # create menus
        menubar, accel = self.createMenus()
        # additional key bindings
        ### FIXME
        ###self.accel.add("Space", None, None, None, None)
        # delete the old menubar
        # set the menubar
        ##~ accel.attach(self.top)
        top.add_accel_group(accel)
        w = menubar.get_widget('<main>')
        self.top.vbox.pack_start(w, expand=FALSE, fill=FALSE)
        self.top.vbox.reorder_child(w, 0)
        self.__menubar = menubar
        self.__accel = accel
        self.menus = menubar


    #
    # create menubar
    #

    def m(self, *args):
        ##print args
        pass

    def _initItemFactory(self):
        self.menu_items = (
            ("/_File", None, None, 0, "<Branch>"),
            ("/File/<tearoff>", None, None, 0, "<Tearoff>"),
            ("/File/_New Game", "<control>N", self.mNewGame, 0, ""),
            ("/File/Select _game", None, None, 0, "<Branch>"),
        )

        #
        # /File/Select game
        #

        mi, radio = [], "<RadioItem>"
        games = self.app.gdb.getGamesIdSortedByName()
        i = 0
        path = "/File/Select game"
        columnbreak = 25
        n = 0
        mm = []
        t1 = t2 = None
        for id in games:
            if t1 is None:
                t1 = self.app.getGameMenuitemName(id)[:3]
            if n == columnbreak:
                t2 = self.app.getGameMenuitemName(id)[:3]
                pp = '%s/%s-%s' % (path, t1, t2)
                mi.append((pp, None, None, 0, '<Branch>'))
                for m in mm:
                    p = '%s/%s' % (pp, m[0])
                    mi.append((p, None, self.mSelectGame, m[1], radio))
                    if radio[0] == '<':
                        radio = re.sub('_', '', p)
                n = 0
                mm = []
                t1 = t2

            mm.append((self.app.getGameMenuitemName(id), id))
            n += 1

        t2 = self.app.getGameMenuitemName(id)[:3]
        pp = '%s/%s-%s' % (path, t1, t2)
        mi.append((pp, None, None, 0, '<Branch>'))
        for m in mm:
            p = '%s/%s' % (pp, m[0])
            mi.append((p, None, self.mSelectGame, m[1], radio))

        self.menu_items = self.menu_items + tuple(mi)
        self.tkopt.gameid.path = radio

        #
        #
        #

        self.menu_items = self.menu_items + (
            ("/File/Select game by number...", None, self.mSelectGameById, 0, ""),
            ("/File/<sep>", None, None, 0, "<Separator>"),
            ("/File/_Open", "<control>O", self.m, 0, ""),
            ("/File/_Save", "<control>S", self.mSave, 0, ""),
            ("/File/Save _as...", None, self.m, 0, ""),
            ("/File/<sep>", None, None, 0, "<Separator>"),
            ("/File/_Quit", "<control>Q", self.mQuit, 0, ""),
            ("/_Edit", None, None, 0, "<Branch>"),
            ("/Edit/<tearoff>", None, None, 0, "<Tearoff>"),
            ("/Edit/_Undo", "Z", self.mUndo, 0, ""),
            ("/Edit/_Redo", "R", self.mRedo, 0, ""),
            ("/Edit/Redo _all", None, self.mRedoAll, 0, ""),
            ("/Edit/<sep>", None, None, 0, "<Separator>"),
            ("/Edit/Restart _game", "<control>G", self.mRestart, 0, ""),
            ("/_Game", None, None, 0, "<Branch>"),
            ("/Game/<tearoff>", None, None, 0, "<Tearoff>"),
            ("/Game/_Deal cards", "D", self.mDeal, 0, ""),
            ("/Game/_Auto drop", "A", self.mDrop, 0, ""),
            ("/Game/<sep>", None, None, 0, "<Separator>"),
            ("/Game/S_tatus...", "T", self.mStatus, 0, ""),
            ("/_Assist", None, None, 0, "<Branch>"),
            ("/Assist/<tearoff>", None, None, 0, "<Tearoff>"),
            ("/Assist/_Hint", "H", self.mHint, 0, ""),
            ("/Assist/Highlight _piles", "Shift", self.mHighlightPiles, 0, ""),
            ("/Assist/<sep>", None, None, 0, "<Separator>"),
            ("/Assist/_Demo", "<control>D", self.mDemo, 0, ""),
            ("/Assist/Demo (all games)", "", self.mMixedDemo, 0, ""),
            ("/_Options", None, None, 0, "<Branch>"),
            ("/Options/<tearoff>", None, None, 0, "<Tearoff>"),
            ("/Options/_Confirm", None, self.mOptConfirm, 0, "<ToggleItem>"),
            ("/Options/Auto_play", "P", self.mOptAutoDrop, 0, "<ToggleItem>"),
            ("/Options/_Automatic _face up", "F", self.mOptAutoFaceUp, 0, "<ToggleItem>"),
            ("/Options/Highlight _matching cards", None, self.mOptEnableHighlightCards, 0, "<ToggleItem>"),
            ("/Options/<sep>", None, None, 0, "<Separator>"),
        )

        mi, radio = [], "<RadioItem>"
        path = "/Options/Cards_et"
        mi.append((path, None, None, 0, "<Branch>"))
        for i in range(self.app.cardset_manager.len()):
            columnbreak = i > 0 and (i % 25) == 0
            p = path + '/' + self.app.cardset_manager.get(i).name
            mi.append((p, None, self.mOptCardset, i, radio))
            if radio[0] == '<':
                radio = re.sub('_', '', p)
        self.menu_items = self.menu_items + tuple(mi)
##        self.tkopt.cardset.path = radio

        self.menu_items = self.menu_items + (
            ("/Options/Table color...", None, self.mOptTableColor, 0, ""),
        )

        mi, radio = [], "<RadioItem>"
        path = "/Options/_Animations"
        mi.append((path, None, None, 0, "<Branch>"))
        i = 0
        for k in ("_None", "_Fast", "_Timer based"):
            p = path + '/' + k
            mi.append((p, None, self.mOptAnimations, i, radio))
            if radio[0] == '<':
                radio = re.sub('_', '', p)
            i = i + 1
        self.menu_items = self.menu_items + tuple(mi)
        self.tkopt.animations.path = radio

        self.menu_items = self.menu_items + (
            ("/Options/Card shadow", None, self.mOptShadow, 0, "<ToggleItem>"),
            ("/Options/Shade legal moves", None, self.mOptShade, 0, "<ToggleItem>"),
            ("/Options/<sep>", None, None, 0, "<Separator>"),
            ("/Options/_Hint options...", None, self.mOptHintOptions, 0, ""),
            ("/Options/_Demo options...", None, self.mOptDemoOptions, 0, ""),
            ("/_Help", None, None, 0, "<LastBranch>"),
            ("/Help/<tearoff>", None, None, 0, "<Tearoff>"),
            ("/Help/_Contents", "F1", self.mHelp, 0, ""),
            ("/Help/_Rules", None, self.mHelpRules, 0, ""),
            ("/Help/<sep>", None, None, 0, "<Separator>"),
            ("/Help/_About PySol...", None, self.mHelpAbout, 0, ""),
        )


    def createMenus(self):
        if not self.menu_items:
            self._initItemFactory()
        accel = gtk.AccelGroup()
        item_factory = gtk.ItemFactory(gtk.MenuBar, '<main>', accel)
        item_factory.create_items(self.menu_items)
        return item_factory, accel


    #
    # menu updates
    #

    def setMenuState(self, state, path):
        return
        w = self.__menubar.get_widget(path)
        w.set_sensitive(state)

    def setToolbarState(self, state, path):
        ##~ w = getattr(self.app.toolbar, path + "_button")
        ##~ w.set_sensitive(state)
        pass


    #
    # menu actions
    #

    def mOpen(self, *args):
        pass

    def mSaveAs(self, *event):
        pass

    def mOptCardset(self, *args):
        pass

    def mOptTableColor(self, *args):
        win = gtk.ColorSelectionDialog("Select table color")
        win.help_button.destroy()
        win.set_position(gtk.WIN_POS_MOUSE)
        win.colorsel.set_current_color(gdk.color_parse(self.app.opt.table_color))
        
        ##win.colorsel.set_update_policy(UPDATE_CONTINUOUS)
        def delete_event(widget, *event):
            widget.destroy()
        def ok_button_clicked(_button, self=self, win=win):
            c = win.colorsel.get_current_color()
            c = '#%02x%02x%02x' % (c.red/256, c.green/256, c.blue/256)
            win.destroy()
            self.app.opt.table_color = c
            self.game.canvas.config(bg=self.app.opt.table_color)
            self.top.config(bg=self.app.opt.table_color)
        win.connect("delete_event", delete_event)
        win.ok_button.connect("clicked", ok_button_clicked)
        win.cancel_button.connect("clicked", win.destroy)
        setTransient(win, self.top)
        win.show()

    def mOptConfirm(self, *args):
        pass

    def mOptHintOptions(self, *args):
        pass

    def mOptDemoOptions(self, *args):
        pass

    def updateFavoriteGamesMenu(self, *args):
        pass

##     def mSelectGame(self, gameid, menuitem):
##         if menuitem.get_active():
##             self._mSelectGame(gameid)

