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
  ('new',     gtk.STOCK_NEW,     '_New', 'N', 'New game', self.mNewGame),
  ('open',    gtk.STOCK_OPEN,    '_Open', '<control>O', 'Open a\nsaved game', self.mOpen),
  ('restart', gtk.STOCK_REFRESH, '_Restart', '<control>G', 'Restart the\ncurrent game', self.mRestart),
  ('save',    gtk.STOCK_SAVE,    '_Save', '<control>S', 'Save game', self.mSave),
  ('undo',    gtk.STOCK_UNDO,    'Undo', 'Z', 'Undo', self.mUndo),
  ('redo',    gtk.STOCK_REDO,    'Redo', 'R', 'Redo', self.mRedo),
  ('autodrop',gtk.STOCK_JUMP_TO, '_Auto drop', 'A', 'Auto drop', self.mDrop),
  ('stats',   gtk.STOCK_HOME,    'Stats', None, 'Statistics', self.mStatus),
  ('rules',   gtk.STOCK_HELP,    'Rules', 'F1', 'Rules', self.mHelpRules),
  ('quit',    gtk.STOCK_QUIT,    'Quit', '<control>Q', 'Quit PySol', self.mQuit),

  ('file',          None, '_File' ),
  ('selectgame',    None, 'Select _game'),
  ('edit',          None, '_Edit'),
  ('game',          None, '_Game'),
  ('assist',        None, '_Assist'),
  ('options',       None, '_Options'),
  ("automaticplay", None, "_Automatic play"),

  ('animations', None, '_Animations'),
  ('help',       None, '_Help'),

  ('selectgamebynumber', None, 'Select game by number...', None, None, self.mSelectGameById),
  ('saveas',    None, 'Save _as...', None, None, self.m),
  ('redoall',   None, 'Redo _all',   None, None, self.mRedoAll),
  ('dealcards', None, '_Deal cards', 'D',  None, self.mDeal),
  ('status',    None, 'S_tatus...',  'T',  None, self.mStatus),
  ('hint',      None, '_Hint',       'H',  None, self.mHint),
  ('highlightpiles', None, 'Highlight _piles', None, None, self.mHighlightPiles),
  ('demo',         None,'_Demo',     '<control>D',None,self.mDemo),
  ('demoallgames', None,'Demo (all games)',  None,None,self.mMixedDemo),
  ('playeroptions',None,'_Player options...',None,None,self.mOptPlayerOptions),
  ('tabletile',    None,'Table t_ile...',    None,None,self.mOptTableTile),
  ('contents',     None,'_Contents','<control>F1',None,self.mHelp),
  ('aboutpysol',   None,'_About PySol...',   None,None,self.mHelpAbout),
)

        #
        toggle_entries = (
  ('pause', gtk.STOCK_STOP, '_Pause', 'P', 'Pause game', self.mPause),
  ('optautodrop', None, 'A_uto drop',    None, None, self.mOptAutoDrop),
  ('autofaceup',  None, 'Auto _face up', None, None, self.mOptAutoFaceUp),
  ("autodeal",    None, "Auto _deal",    None, None, self.mOptAutoDeal),
  ("quickplay",   None, '_Quick play',   None, None, self.mOptQuickPlay),

  ('highlightmatchingcards', None, 'Highlight _matching cards', None, None, self.mOptEnableHighlightCards),
  ('cardshadow',      None, 'Card shadow',       None, None, self.mOptShadow),
  ('shadelegalmoves', None, 'Shade legal moves', None, None, self.mOptShade),

)

        #
        animations_entries = (
            ('animationnone',     None, '_None',        None, None, 0),
            ('animationfast',     None, '_Fast',        None, None, 1),
            ('animationtimer',    None, '_Timer based', None, None, 2),
            ('animationslow',     None, '_Slow',        None, None, 3),
            ('animationveryslow', None, '_Very slow',   None, None, 4),
        )
        #
        ui_info = '''<ui>
  <menubar name='menubar'>

    <menu action='file'>
      <menuitem action='selectgamebynumber'/>
      <menu action='selectgame'/>
      <separator/>
      <menuitem action='open'/>
      <menuitem action='save'/>
      <menuitem action='saveas'/>
      <separator/>
      <menuitem action='quit'/>
    </menu>

    <menu action='edit'>
      <menuitem action='undo'/>
      <menuitem action='redo'/>
      <menuitem action='redoall'/>
      <separator/>
      <menuitem action='restart'/>
    </menu>

    <menu action='game'>
      <menuitem action='dealcards'/>
      <menuitem action='autodrop'/>
      <menuitem action='pause'/>
      <separator/>
      <menuitem action='status'/>
    </menu>

    <menu action='assist'>
      <menuitem action='hint'/>
      <menuitem action='highlightpiles'/>
      <menuitem action='demo'/>
      <menuitem action='demoallgames'/>
    </menu>

    <menu action='options'>
      <menuitem action='playeroptions'/>
      <menu action='automaticplay'>
        <menuitem action='autofaceup'/>
        <menuitem action='autodrop'/>
        <menuitem action='autodeal'/>
        <separator/>
        <menuitem action='quickplay'/>
      </menu>
      <menuitem action='highlightmatchingcards'/>
      <separator/>
      <menuitem action='tabletile'/>
      <menu action='animations'>
        <menuitem action='animationnone'/>
        <menuitem action='animationtimer'/>
        <menuitem action='animationfast'/>
        <menuitem action='animationslow'/>
        <menuitem action='animationveryslow'/>
      </menu>
      <menuitem action='cardshadow'/>
      <menuitem action='shadelegalmoves'/>
    </menu>

    <menu action='help'>
      <menuitem action='contents'/>
      <menuitem action='rules'/>
      <menuitem action='aboutpysol'/>
    </menu>

  </menubar>
</ui>
'''
        #
        ui_manager = gtk.UIManager()
        ui_manager_id = ui_manager.add_ui_from_string(ui_info)

        action_group = gtk.ActionGroup('PySolActions')
        action_group.add_actions(entries)
        action_group.add_toggle_actions(toggle_entries)
        action_group.add_radio_actions(animations_entries,
                                       self.app.opt.animations,
                                       self.mOptAnimations)

        ui_manager.insert_action_group(action_group, 0)
        self.top.add_accel_group(ui_manager.get_accel_group())
        self.top.ui_manager = ui_manager
        menubar = ui_manager.get_widget('/menubar')

        games = map(self.app.gdb.get, self.app.gdb.getGamesIdSortedByName())

        menu_item = ui_manager.get_widget('/menubar/file/selectgame')
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
        cb_max = gdk.screen_height()/24
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

## WARNING: setMenuState: not found: /menubar/file/holdandquit
## WARNING: setMenuState: not found: /menubar/assist/findcard
    def setMenuState(self, state, path):
        path_map = {'help.rulesforthisgame': '/menubar/help/rules',}
        if path_map.has_key(path):
            path = path_map[path]
        else:
            path = '/menubar/'+path.replace('.', '/')
        menuitem = self.top.ui_manager.get_widget(path)
        if not menuitem:
            ##print 'WARNING: setMenuState: not found:', path
            return
        menuitem.set_sensitive(state)



    def setToolbarState(self, state, path):
        path = '/toolbar/'+path
        button = self.top.ui_manager.get_widget(path)
        if not button:
            print 'WARNING: setToolbarState: not found:', path
        else:
            button.set_sensitive(state)


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
                                        title=_('Select table background'),
                                        manager=self.app.tabletile_manager,
                                        key=key)
        if d.status == 0 and d.button in (0, 1):
            if type(d.key) is str:
                self._mOptTableColor(d.key)
            elif d.key > 0 and d.key != self.app.tabletile_index:
                self._mOptTableTile(d.key)


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

