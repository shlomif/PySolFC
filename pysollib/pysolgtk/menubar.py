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
from gtk import gdk

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
        self.progress = progress
        ##self.menus = None
        ##self.menu_items = None
        # create menus
        menubar = self.createMenubar()
        self.top.table.attach(menubar,
                              0, 1,                    0, 1,
                              gtk.EXPAND | gtk.FILL,   0,
                              0,                       0);
        menubar.show()


##         menubar, accel = self.createMenus()
##         # additional key bindings
##         ### FIXME
##         ###self.accel.add("Space", None, None, None, None)
##         # delete the old menubar
##         # set the menubar
##         ##~ accel.attach(self.top)
##         top.add_accel_group(accel)
##         w = menubar.get_widget('<main>')
##         self.top.vbox.pack_start(w, expand=FALSE, fill=FALSE)
##         self.top.vbox.reorder_child(w, 0)
##         self.__menubar = menubar
##         self.__accel = accel
##         self.menus = menubar


    #
    # create menubar
    #

    def m(self, *args):
        ##print args
        pass

    def createMenubar(self):

        entries = (
  ('New',     gtk.STOCK_NEW,     '_New', 'N', 'New game', self.mNewGame),
  ('Open',    gtk.STOCK_OPEN,    '_Open', '<control>O', 'Open a\nsaved game', self.mOpen),
  ('Restart', gtk.STOCK_REFRESH, '_Restart', '<control>G', 'Restart the\ncurrent game', self.mRestart),
  ('Save',    gtk.STOCK_SAVE,    '_Save', '<control>S', 'Save game', self.mSave),
  ('Undo',    gtk.STOCK_UNDO,    'Undo', 'Z', 'Undo', self.mUndo),
  ('Redo',    gtk.STOCK_REDO,    'Redo', 'R', 'Redo', self.mRedo),
  ('Autodrop',gtk.STOCK_JUMP_TO, '_Auto drop', 'A', 'Auto drop', self.mDrop),
  ('Stats',   gtk.STOCK_EXECUTE, 'Stats', None, 'Statistics', self.mStatus),
  ('Rules',   gtk.STOCK_HELP,    'Rules', None, 'Rules', self.mHelpRules),
  ('Quit',    gtk.STOCK_QUIT,    'Quit', '<control>Q', 'Quit PySol', self.mQuit),

  ("FileMenu",    None, "_File" ),
  ("SelectGame",  None, "Select _game"),
  ("EditMenu",    None, '_Edit'),
  ("GameMenu",    None, "_Game"),
  ("AssistMenu",  None, "_Assist"),
  ("OptionsMenu", None, "_Options"),
  ("HelpMenu",    None, "_Help"),

  ('SelectGameByNumber', None, "Select game by number...", None, None, self.mSelectGameById),
  ("SaveAs",    None, 'Save _as...', None, None, self.m),
  ("RedoAll",   None, 'Redo _all',   None, None, self.mRedoAll),
  ("DealCards", None, '_Deal cards', "D",  None, self.mDeal),
  ("Status",    None, 'S_tatus...',  "T",  None, self.mStatus),
  ("Hint",      None, '_Hint',       "H",  None, self.mHint),
  ("HighlightPiles", None, 'Highlight _piles', None, None, self.mHighlightPiles),
  ("Demo",         None, '_Demo',        "<control>D", None, self.mDemo),
  ("DemoAllGames", None, 'Demo (all games)', None,     None, self.mMixedDemo),
  ("Contents",     None, '_Contents',        'F1',     None, self.mHelp),
  ("About",        None, '_About PySol...', None,      None, self.mHelpAbout),
)

        toggle_entries = (
  ("Confirm",  None, '_Confirm', None, None, self.mOptConfirm),
  ("Autoplay", None, 'Auto_play', "P", None, self.mOptAutoDrop),
  ("AutomaticFaceUp", None,'_Automatic _face up', "F", None, self.mOptAutoFaceUp),
  ("HighlightMatchingCards", None, 'Highlight _matching cards', None, None, self.mOptEnableHighlightCards),
  ("CardShadow",      None, 'Card shadow',       None, None, self.mOptShadow),
  ("ShadeLegalMoves", None, 'Shade legal moves', None, None, self.mOptShade),

)

        ui_info = '''<ui>
  <menubar name='MenuBar'>

    <menu action='FileMenu'>
      <menuitem action='SelectGameByNumber'/>
      <menu action='SelectGame'/>
      <separator/>
      <menuitem action='Open'/>
      <menuitem action='Save'/>
      <menuitem action='SaveAs'/>
      <separator/>
      <menuitem action='Quit'/>
    </menu>

    <menu action='EditMenu'>
      <menuitem action='Undo'/>
      <menuitem action='Redo'/>
      <menuitem action='RedoAll'/>
      <separator/>
      <menuitem action='Restart'/>
    </menu>

    <menu action='GameMenu'>
      <menuitem action='DealCards'/>
      <menuitem action='Autodrop'/>
      <separator/>
      <menuitem action='Status'/>
    </menu>

    <menu action='AssistMenu'>
      <menuitem action='Hint'/>
      <menuitem action='HighlightPiles'/>
      <menuitem action='Demo'/>
      <menuitem action='DemoAllGames'/>
    </menu>

    <menu action='OptionsMenu'>
      <menuitem action='Confirm'/>
      <menuitem action='Autoplay'/>
      <menuitem action='AutomaticFaceUp'/>
      <menuitem action='HighlightMatchingCards'/>
      <menuitem action='CardShadow'/>
      <menuitem action='ShadeLegalMoves'/>
    </menu>

    <menu action='HelpMenu'>
      <menuitem action='Contents'/>
      <menuitem action='Rules'/>
      <menuitem action='About'/>
    </menu>

  </menubar>
</ui>
'''
        #
        ui_manager = gtk.UIManager()
        ui_manager_id = ui_manager.add_ui_from_string(ui_info)

        action_group = gtk.ActionGroup("PySolActions")
        action_group.add_actions(entries)
        action_group.add_toggle_actions(toggle_entries)

        ui_manager.insert_action_group(action_group, 0)
        self.top.add_accel_group(ui_manager.get_accel_group())
        self.top.ui_manager = ui_manager
        menubar = ui_manager.get_widget("/MenuBar")

        games = map(self.app.gdb.get, self.app.gdb.getGamesIdSortedByName())

        menu_item = ui_manager.get_widget("/MenuBar/FileMenu/SelectGame")
        menu_item.show()
        menu = gtk.Menu()
        menu_item.set_submenu(menu)
        self._addSelectAllGameSubMenu(games, menu, self.mSelectGame)

        return menubar


    def _createSubMenu(self, menu, label):
        menu_item = gtk.MenuItem(label)
        menu.add(menu_item)
        menu_item.show()
        submenu = gtk.Menu()
        menu_item.set_submenu(submenu)
        return submenu

    def _addSelectGameSubMenu(self, games, menu, command, group):
        for g in games:
            label = g.name
            menu_item = gtk.RadioMenuItem(group, label)
            group = menu_item
            menu.add(menu_item)
            menu_item.show()
            menu_item.connect('toggled', command, g.id)

    def _addSelectAllGameSubMenu(self, games, menu, command):
        cb_max = gdk.screen_height()/20
        n, d = 0, cb_max
        i = 0
        group = None
        while True:
            if self.progress: self.progress.update(step=1)
            i += 1
            if not games[n:n+d]:
                break
            m = min(n+d-1, len(games)-1)
            label = games[n].name[:3]+' - '+games[m].name[:3]
            submenu = self._createSubMenu(menu, label=label)
            group = self._addSelectGameSubMenu(games[n:n+d], submenu,
                                               command, group)
            n += d


##     def _initItemFactory(self):
##         self.menu_items = (
##             ("/_File", None, None, 0, "<Branch>"),
##             ("/File/<tearoff>", None, None, 0, "<Tearoff>"),
##             ("/File/_New Game", "<control>N", self.mNewGame, 0, ""),
##             ("/File/Select _game", None, None, 0, "<Branch>"),
##         )

##         #
##         # /File/Select game
##         #

##         mi, radio = [], "<RadioItem>"
##         games = self.app.gdb.getGamesIdSortedByName()
##         i = 0
##         path = "/File/Select game"
##         columnbreak = 25
##         n = 0
##         mm = []
##         t1 = t2 = None
##         for id in games:
##             if t1 is None:
##                 t1 = self.app.getGameMenuitemName(id)[:3]
##             if n == columnbreak:
##                 t2 = self.app.getGameMenuitemName(id)[:3]
##                 pp = '%s/%s-%s' % (path, t1, t2)
##                 mi.append((pp, None, None, 0, '<Branch>'))
##                 for m in mm:
##                     p = '%s/%s' % (pp, m[0])
##                     mi.append((p, None, self.mSelectGame, m[1], radio))
##                     if radio[0] == '<':
##                         radio = re.sub('_', '', p)
##                 n = 0
##                 mm = []
##                 t1 = t2

##             mm.append((self.app.getGameMenuitemName(id), id))
##             n += 1

##         t2 = self.app.getGameMenuitemName(id)[:3]
##         pp = '%s/%s-%s' % (path, t1, t2)
##         mi.append((pp, None, None, 0, '<Branch>'))
##         for m in mm:
##             p = '%s/%s' % (pp, m[0])
##             mi.append((p, None, self.mSelectGame, m[1], radio))

##         self.menu_items = self.menu_items + tuple(mi)
##         self.tkopt.gameid.path = radio

##         #
##         #
##         #

##         self.menu_items = self.menu_items + (
##             ("/File/Select game by number...", None, self.mSelectGameById, 0, ""),
##             ("/File/<sep>", None, None, 0, "<Separator>"),
##             ("/File/_Open", "<control>O", self.m, 0, ""),
##             ("/File/_Save", "<control>S", self.mSave, 0, ""),
##             ("/File/Save _as...", None, self.m, 0, ""),
##             ("/File/<sep>", None, None, 0, "<Separator>"),
##             ("/File/_Quit", "<control>Q", self.mQuit, 0, ""),
##             ("/_Edit", None, None, 0, "<Branch>"),
##             ("/Edit/<tearoff>", None, None, 0, "<Tearoff>"),
##             ("/Edit/_Undo", "Z", self.mUndo, 0, ""),
##             ("/Edit/_Redo", "R", self.mRedo, 0, ""),
##             ("/Edit/Redo _all", None, self.mRedoAll, 0, ""),
##             ("/Edit/<sep>", None, None, 0, "<Separator>"),
##             ("/Edit/Restart _game", "<control>G", self.mRestart, 0, ""),
##             ("/_Game", None, None, 0, "<Branch>"),
##             ("/Game/<tearoff>", None, None, 0, "<Tearoff>"),
##             ("/Game/_Deal cards", "D", self.mDeal, 0, ""),
##             ("/Game/_Auto drop", "A", self.mDrop, 0, ""),
##             ("/Game/<sep>", None, None, 0, "<Separator>"),
##             ("/Game/S_tatus...", "T", self.mStatus, 0, ""),
##             ("/_Assist", None, None, 0, "<Branch>"),
##             ("/Assist/<tearoff>", None, None, 0, "<Tearoff>"),
##             ("/Assist/_Hint", "H", self.mHint, 0, ""),
##             ("/Assist/Highlight _piles", "Shift", self.mHighlightPiles, 0, ""),
##             ("/Assist/<sep>", None, None, 0, "<Separator>"),
##             ("/Assist/_Demo", "<control>D", self.mDemo, 0, ""),
##             ("/Assist/Demo (all games)", "", self.mMixedDemo, 0, ""),
##             ("/_Options", None, None, 0, "<Branch>"),
##             ("/Options/<tearoff>", None, None, 0, "<Tearoff>"),
##             ("/Options/_Confirm", None, self.mOptConfirm, 0, "<ToggleItem>"),
##             ("/Options/Auto_play", "P", self.mOptAutoDrop, 0, "<ToggleItem>"),
##             ("/Options/_Automatic _face up", "F", self.mOptAutoFaceUp, 0, "<ToggleItem>"),
##             ("/Options/Highlight _matching cards", None, self.mOptEnableHighlightCards, 0, "<ToggleItem>"),
##             ("/Options/<sep>", None, None, 0, "<Separator>"),
##         )

##         mi, radio = [], "<RadioItem>"
##         path = "/Options/Cards_et"
##         mi.append((path, None, None, 0, "<Branch>"))
##         for i in range(self.app.cardset_manager.len()):
##             columnbreak = i > 0 and (i % 25) == 0
##             p = path + '/' + self.app.cardset_manager.get(i).name
##             mi.append((p, None, self.mOptCardset, i, radio))
##             if radio[0] == '<':
##                 radio = re.sub('_', '', p)
##         self.menu_items = self.menu_items + tuple(mi)
## ##        self.tkopt.cardset.path = radio

##         self.menu_items = self.menu_items + (
##             ("/Options/Table color...", None, self.mOptTableColor, 0, ""),
##         )

##         mi, radio = [], "<RadioItem>"
##         path = "/Options/_Animations"
##         mi.append((path, None, None, 0, "<Branch>"))
##         i = 0
##         for k in ("_None", "_Fast", "_Timer based"):
##             p = path + '/' + k
##             mi.append((p, None, self.mOptAnimations, i, radio))
##             if radio[0] == '<':
##                 radio = re.sub('_', '', p)
##             i = i + 1
##         self.menu_items = self.menu_items + tuple(mi)
##         self.tkopt.animations.path = radio

##         self.menu_items = self.menu_items + (
##             ("/Options/Card shadow", None, self.mOptShadow, 0, "<ToggleItem>"),
##             ("/Options/Shade legal moves", None, self.mOptShade, 0, "<ToggleItem>"),
##             ("/Options/<sep>", None, None, 0, "<Separator>"),
##             ("/Options/_Hint options...", None, self.mOptHintOptions, 0, ""),
##             ("/Options/_Demo options...", None, self.mOptDemoOptions, 0, ""),
##             ("/_Help", None, None, 0, "<LastBranch>"),
##             ("/Help/<tearoff>", None, None, 0, "<Tearoff>"),
##             ("/Help/_Contents", "F1", self.mHelp, 0, ""),
##             ("/Help/_Rules", None, self.mHelpRules, 0, ""),
##             ("/Help/<sep>", None, None, 0, "<Separator>"),
##             ("/Help/_About PySol...", None, self.mHelpAbout, 0, ""),
##         )


    def createMenus(self):
        return self._initUI()

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

    def mSelectGame(self, menu_item, game_id):
        if menu_item.get_active():
            self._mSelectGame(game_id)

