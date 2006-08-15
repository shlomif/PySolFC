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
from selecttile import SelectTileDialogWithPreview


# /***********************************************************************
# // - create menubar
# // - update menubar
# // - menu actions
# ************************************************************************/

class PysolMenubar(PysolMenubarActions):
    def __init__(self, app, top, progress=None):
        PysolMenubarActions.__init__(self, app, top)
        self.progress = progress
        # create menus
        menubar = self.createMenubar()
        self.top.table.attach(menubar,
                              0, 1,                    0, 1,
                              gtk.EXPAND | gtk.FILL,   0,
                              0,                       0);
        menubar.show()


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

  ("FileMenu",       None, "_File" ),
  ("SelectGame",     None, "Select _game"),
  ("EditMenu",       None, '_Edit'),
  ("GameMenu",       None, "_Game"),
  ("AssistMenu",     None, "_Assist"),
  ("OptionsMenu",    None, "_Options"),
  ('AnimationsMenu', None, '_Animations'),
  ("HelpMenu",       None, "_Help"),

  ('SelectGameByNumber', None, "Select game by number...", None, None, self.mSelectGameById),
  ("SaveAs",    None, 'Save _as...', None, None, self.m),
  ("RedoAll",   None, 'Redo _all',   None, None, self.mRedoAll),
  ("DealCards", None, '_Deal cards', "D",  None, self.mDeal),
  ("Status",    None, 'S_tatus...',  "T",  None, self.mStatus),
  ("Hint",      None, '_Hint',       "H",  None, self.mHint),
  ("HighlightPiles", None, 'Highlight _piles', None, None, self.mHighlightPiles),
  ("Demo",         None, '_Demo',     "<control>D", None, self.mDemo),
  ("DemoAllGames", None, 'Demo (all games)', None,  None, self.mMixedDemo),
  ("TableTile",   None, "Table t_ile...",   None,  None, self.mOptTableTile),
  ("Contents",     None, '_Contents',        'F1',  None, self.mHelp),
  ("About",        None, '_About PySol...',  None,  None, self.mHelpAbout),
)
        #
        toggle_entries = (
  ("Confirm",  None, '_Confirm', None, None, self.mOptConfirm),
  ("Autoplay", None, 'Auto_play', "P", None, self.mOptAutoDrop),
  ("AutomaticFaceUp", None,'_Automatic _face up', "F", None, self.mOptAutoFaceUp),
  ("HighlightMatchingCards", None, 'Highlight _matching cards', None, None, self.mOptEnableHighlightCards),
  ("CardShadow",      None, 'Card shadow',       None, None, self.mOptShadow),
  ("ShadeLegalMoves", None, 'Shade legal moves', None, None, self.mOptShade),

)
        #
        animations_entries = (
            ("AnimationNone",     None, "_None",        None, None, 0),
            ("AnimationFast",     None, "_Fast",        None, None, 1),
            ("AnimationTimer",    None, "_Timer based", None, None, 2),
            ("AnimationSlow",     None, "_Slow",        None, None, 3),
            ("AnimationVerySlow", None, "_Very slow",   None, None, 4),
        )
        #
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
      <separator/>
      <menuitem action='TableTile'/>
      <menu action='AnimationsMenu'>
        <menuitem action='AnimationNone'/>
        <menuitem action='AnimationFast'/>
        <menuitem action='AnimationTimer'/>
        <menuitem action='AnimationSlow'/>
        <menuitem action='AnimationVerySlow'/>
      </menu>
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
        action_group.add_radio_actions(animations_entries,
                                       self.app.opt.animations,
                                       self.mOptAnimations)

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

    def mOptTableTile(self, *args):
        if self._cancelDrag(break_pause=False): return
        key = self.app.tabletile_index
        if key <= 0:
            key = self.app.opt.table_color.lower()
        d = SelectTileDialogWithPreview(self.top, app=self.app,
                                        title=_("Select table background"),
                                        manager=self.app.tabletile_manager,
                                        key=key)
        if d.status == 0 and d.button in (0, 1):
            if type(d.key) is str:
                self._mOptTableColor(d.key)
            elif d.key > 0 and d.key != self.app.tabletile_index:
                self._mOptTableTile(d.key)


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

    def mOptAnimations(self, a1, a2):
        ##print a1.get_current_value(), a2.get_current_value()
        self.app.opt.animations = a1.get_current_value()


    def _mOptTableTile(self, i):
        self.app.setTile(i)

    def _mOptTableColor(self, color):
        tile = self.app.tabletile_manager.get(0)
        tile.color = color
        self.app.setTile(0)

