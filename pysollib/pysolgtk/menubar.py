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
from pysollib.settings import PACKAGE

# toolkit imports
from tkutil import setTransient
from tkutil import color_tk2gtk, color_gtk2tk
from selectcardset import SelectCardsetDialogWithPreview
from selecttile import SelectTileDialogWithPreview

from selectgame import SelectGameDialogWithPreview

gettext = _


def ltk2gtk(s):
    return gettext(s).replace('&', '_')


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

            ### toolbar
            ('newgame', gtk.STOCK_NEW,
             ltk2gtk('&New game'), 'N',
             ltk2gtk('New game'),
             self.mNewGame),
            ('open', gtk.STOCK_OPEN,
             ltk2gtk('&Open...'), '<control>O',
             ltk2gtk('Open a\nsaved game'),
             self.mOpen),
            ('restart', gtk.STOCK_REFRESH,
             ltk2gtk('&Restart'), '<control>G',
             ltk2gtk('Restart the\ncurrent game'),
             self.mRestart),
            ('save', gtk.STOCK_SAVE,
             ltk2gtk('&Save'), '<control>S',
             ltk2gtk('Save game'),
             self.mSave),
            ('undo', gtk.STOCK_UNDO,
             ltk2gtk('&Undo'), 'Z',
             ltk2gtk('Undo'),
             self.mUndo),
            ('redo', gtk.STOCK_REDO,
             ltk2gtk('&Redo'), 'R',
             ltk2gtk('Redo'),
             self.mRedo),
            ('autodrop', gtk.STOCK_JUMP_TO,
             ltk2gtk('&Auto drop'), 'A',
             ltk2gtk('Auto drop'),
             self.mDrop),
            ('stats', gtk.STOCK_INDEX,
             ltk2gtk('Stats'), None,
             ltk2gtk('Statistics'),
             self.mStatus),
            ('rules', gtk.STOCK_HELP,
             ltk2gtk('Rules'), 'F1',
             ltk2gtk('Rules'),
             self.mHelpRules),
            ('quit', gtk.STOCK_QUIT,
             ltk2gtk('&Quit'), '<control>Q',
             ltk2gtk('Quit PySol'),
             self.mQuit),

            ### menus
            ('file',          None, ltk2gtk('&File')),
            ('selectgame',    None, ltk2gtk('Select &game')),
            ('edit',          None, ltk2gtk('&Edit')),
            ('game',          None, ltk2gtk('&Game')),
            ('assist',        None, ltk2gtk('&Assist')),
            ('options',       None, ltk2gtk('&Options')),
            ('assistlevel',   None, ltk2gtk("Assist &level")),
            ("automaticplay", None, ltk2gtk("&Automatic play")),
            ('animations',    None, ltk2gtk('A&nimations')),
            ('help',          None, ltk2gtk('&Help')),

            ### menuitems
            ('playablepreview', None,
             ltk2gtk('Playable pre&view...'), 'V',
             None, self.mSelectGameDialogWithPreview),
            ('selectgamebynumber', None,
             ltk2gtk('Select game by nu&mber...'), None,
             None, self.mSelectGameById),
            ('saveas', None,
             ltk2gtk('Save &as...'), None,
             None, self.m),
            ('redoall', None,
             ltk2gtk('Redo &all'), None,
             None, self.mRedoAll),
            ('dealcards', None,
             ltk2gtk('&Deal cards'), 'D',
             None, self.mDeal),
            ('status', None,
             ltk2gtk('S&tatus...'),  'T',
             None, self.mStatus),
            ('hint', None,
             ltk2gtk('&Hint'), 'H',
             None, self.mHint),
            ('highlightpiles', None,
             ltk2gtk('Highlight p&iles'), None,
             None, self.mHighlightPiles),
            ('demo', None,
             ltk2gtk('&Demo'), '<control>D',
             None,self.mDemo),
            ('demoallgames', None,
             ltk2gtk('Demo (&all games)'), None,
             None,self.mMixedDemo),
            ('playeroptions', None,
             ltk2gtk('&Player options...'), None,
             None,self.mOptPlayerOptions),
            ('tabletile', None,
             ltk2gtk('Table t&ile...'), None,
             None,self.mOptTableTile),
            ('cardset', None,
             ltk2gtk('Cards&et...'), '<control>E',
             None, self.mSelectCardsetDialog),
            ('contents', None,
             ltk2gtk('&Contents'), '<control>F1',
             None, self.mHelp),
            ('aboutpysol', None,
             ltk2gtk('&About ')+PACKAGE+'...',
             None,None,self.mHelpAbout),
            ('updateall', None,
             'Redraw Game', '<control>L',
             None,
             self.updateAll),
            )

        #
        toggle_entries = [
            ('pause',                              # name
             gtk.STOCK_STOP, ltk2gtk('&Pause'),    # stock, label
             'P', ltk2gtk('Pause game'),           # accelerator, tooltip
             self.mPause,                          # callback
             False,                                # initial value
             ), ]
        for label, name, opt_name in (
            ('A&uto drop',       'optautodrop', 'autodrop'),
            ('Auto &face up',               '', 'autofaceup'),
            ('Auto &deal',                  '', 'autodeal'),
            ('&Quick play',                 '', 'quickplay'),
            ('Enable &undo',                '', 'undo'),
            ('Enable &bookmarks'   ,        '', 'bookmarks'),
            ('Enable &hint',                '', 'hint'),
            ('Enable highlight p&iles',     '', 'highlight_piles'),
            ('Enable highlight &cards',     '', 'highlight_cards'),
            ('Enable highlight same &rank', '', 'highlight_samerank'),
            ('Highlight &no matching',      '', 'highlight_not_matching'),
            ('Card shado&w',                '', 'shadow'),
            ('Shade &legal moves',          '', 'shade'),
            ):
            if not name:
                name = re.sub(r"[^0-9a-zA-Z]", "", label).lower()
            toggle_entries.append(
                (name,
                 None, ltk2gtk(label),
                 None, None,
                 lambda w, opt_name=opt_name: self.mOptToggle(w, opt_name),
                 getattr(self.app.opt, opt_name)))

        #
        animations_entries = (
          ('animationnone',     None, ltk2gtk('&None'),        None, None, 0),
          ('animationfast',     None, ltk2gtk('&Fast'),        None, None, 1),
          ('animationtimer',    None, ltk2gtk('&Timer based'), None, None, 2),
          ('animationslow',     None, ltk2gtk('&Slow'),        None, None, 3),
          ('animationveryslow', None, ltk2gtk('&Very slow'),   None, None, 4),
          )
        #
        ui_info = '''<ui>
  <menubar name='menubar'>

    <menu action='file'>
      <menuitem action='newgame'/>
      <menuitem action='selectgamebynumber'/>
      <menuitem action='playablepreview'/>
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
      <separator/>
      <menuitem action='updateall'/>
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
        <menuitem action='optautodrop'/>
        <menuitem action='autodeal'/>
        <separator/>
        <menuitem action='quickplay'/>
      </menu>
      <menu action='assistlevel'>
        <menuitem action='enableundo'/>
        <menuitem action='enablebookmarks'/>
        <menuitem action='enablehint'/>
        <menuitem action='enablehighlightpiles'/>
        <menuitem action='enablehighlightcards'/>
        <menuitem action='enablehighlightsamerank'/>
        <menuitem action='highlightnomatching'/>
      </menu>
      <separator/>
      <menuitem action='tabletile'/>
      <menuitem action='cardset'/>
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
            label = gettext(label)
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
            n1, n2 = games[n].name, games[m].name
            n1, n2 = gettext(n1), gettext(n2)
            label = n1[:3]+' - '+n2[:3]
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
        path_map = {
            'help.rulesforthisgame': '/menubar/help/rules',
            'options.automaticplay.autodrop': '/menubar/options/automaticplay/optautodrop'
            }
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

    def _createFileChooser(self, title, action, idir, ifile):
        d = gtk.FileChooserDialog(title, self.top, action,
                                  (gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT,
                                   gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        d.set_current_folder(idir)
        if ifile:
            d.set_current_name(ifile)

        filter = gtk.FileFilter()
        filter.set_name('PySol files')
        filter.add_pattern('*.pso')
        d.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name('All files')
        filter.add_pattern('*')
        d.add_filter(filter)

        resp = d.run()
        if resp == gtk.RESPONSE_ACCEPT:
            filename = d.get_filename()
        else:
            filename = None
        d.destroy()
        return filename


    def mOpen(self, *args):
        if self._cancelDrag(break_pause=False): return
        filename = self.game.filename
        if filename:
            idir, ifile = os.path.split(os.path.normpath(filename))
        else:
            idir, ifile = "", ""
        if not idir:
            idir = self.app.dn.savegames
        filename = self._createFileChooser(_('Open Game'),
                                           gtk.FILE_CHOOSER_ACTION_OPEN,
                                           idir, '')
        if filename:
            ##filename = os.path.normpath(filename)
            ##filename = os.path.normcase(filename)
            if os.path.isfile(filename):
                self.game.loadGame(filename)


    def mSaveAs(self, *event):
        if self._cancelDrag(break_pause=False): return
        if not self.menustate.save_as:
            return
        filename = self.game.filename
        if not filename:
            filename = self.app.getGameSaveName(self.game.id)
            if os.name == "posix":
                filename = filename + "-" + self.game.getGameNumber(format=0)
            elif os.path.supports_unicode_filenames: # new in python 2.3
                filename = filename + "-" + self.game.getGameNumber(format=0)
            else:
                filename = filename + "-01"
            filename = filename + '.pso'
        idir, ifile = os.path.split(os.path.normpath(filename))
        if not idir:
            idir = self.app.dn.savegames
        ##print self.game.filename, ifile
        filename = self._createFileChooser(_('Save Game'),
                                           gtk.FILE_CHOOSER_ACTION_SAVE,
                                           idir, ifile)
        if filename:
            ##filename = os.path.normpath(filename)
            ##filename = os.path.normcase(filename)
            self.game.saveGame(filename)
            self.updateMenus()



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


    def mSelectGameDialogWithPreview(self, *event):
        if self._cancelDrag(break_pause=False): return
##         self.game.setCursor(cursor=CURSOR_WATCH)
        bookmark = None
##         if 0:
##             # use a bookmark for our preview game
##             if self.game.setBookmark(-2, confirm=0):
##                 bookmark = self.game.gsaveinfo.bookmarks[-2][0]
##                 del self.game.gsaveinfo.bookmarks[-2]
        ##~ after_idle(self.top, self.__restoreCursor)
        d = SelectGameDialogWithPreview(self.top, title=_("Select game"),
                                        app=self.app, gameid=self.game.id,
                                        bookmark=bookmark)
        return self._mSelectGameDialog(d)

    def _mSelectGameDialog(self, d):
        if d.status == 0 and d.button == 0 and d.gameid != self.game.id:
            ##~ self.tkopt.gameid.set(d.gameid)
            ##~ self.tkopt.gameid_popular.set(d.gameid)
            if 0:
                self._mSelectGame(d.gameid, random=d.random)
            else:
                # don't ask areYouSure()
                self._cancelDrag()
                self.game.endGame()
                self.game.quitGame(d.gameid, random=d.random)


    def mSelectCardsetDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        key = self.app.nextgame.cardset.index
        d = SelectCardsetDialogWithPreview(self.top, title=_("Select cardset"),
                app=self.app, manager=self.app.cardset_manager, key=key)
        cs = self.app.cardset_manager.get(d.key)
        if cs is None or d.key == self.app.cardset.index:
            return
        if d.status == 0 and d.button in (0, 1) and d.key >= 0:
            self.app.nextgame.cardset = cs
            if d.button == 0:
                self._cancelDrag()
                self.game.endGame(bookmark=1)
                self.game.quitGame(bookmark=1)
                self.app.opt.games_geometry = {} # clear saved games geometry


    def mOptToggle(self, w, opt):
        ##print 'mOptToggle:', opt, w.get_active()
        if self._cancelDrag(break_pause=False): return
        self.app.opt.__dict__[opt] = w.get_active()


    def updateAll(self, *event):
        self.app.canvas.updateAll()

