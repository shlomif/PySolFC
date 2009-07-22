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


# imports
import os, re, sys

import gtk
from gtk import gdk

# PySol imports
from pysollib.gamedb import GI
from pysollib.settings import TITLE

# toolkit imports
from tkutil import setTransient
from tkutil import color_tk2gtk, color_gtk2tk
from soundoptionsdialog import SoundOptionsDialog
from selectcardset import SelectCardsetDialogWithPreview
from selecttile import SelectTileDialogWithPreview
from selectgame import SelectGameDialogWithPreview
from findcarddialog import connect_game_find_card_dialog, destroy_find_card_dialog

def ltk2gtk(s):
    # label tk to gtk
    return _(s).replace('&', '_')


# ************************************************************************
# * - create menubar
# * - update menubar
# * - menu actions
# ************************************************************************

class PysolMenubarTk:
    def __init__(self, app, top, progress=None):
        self.progress = progress
        self._cb_max = gdk.screen_height()/24
        # create menus
        menubar = self.createMenubar()
        self.top.table.attach(menubar,
                              0, 3,                    0, 1,
                              gtk.EXPAND | gtk.FILL,   0,
                              0,                       0);
        menubar.show()

    def connectGame(self, game):
        self.game = game
        if game is None:
            return
        assert self.app is game.app
##         tkopt, opt = self.tkopt, self.app.opt
##         tkopt.gameid.set(game.id)
##         tkopt.gameid_popular.set(game.id)
##         tkopt.comment.set(bool(game.gsaveinfo.comment))
        if game.canFindCard():
            connect_game_find_card_dialog(game)
        else:
            destroy_find_card_dialog()

    #
    # create menubar
    #

    def m(self, *args):
        ##print args
        pass

    def createMenubar(self):

        entries = (

            ### toolbar
            ('newgame', gtk.STOCK_NEW,            # action name, stock
             ltk2gtk('&New game'), 'N',           # label, accelerator
             ltk2gtk('New game'),                 # tooltip
             self.mNewGame),                      # callback
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
            ('shuffle', gtk.STOCK_EXECUTE,
             ltk2gtk('Shuffle tiles'), 'F',
             ltk2gtk('Shuffle tiles'),
             self.mShuffle),
            ('autodrop', gtk.STOCK_JUMP_TO,
             ltk2gtk('&Auto drop'), 'A',
             ltk2gtk('Auto drop'),
             self.mDrop),
            ('stats', gtk.STOCK_INDEX,
             ltk2gtk('&Statistics'), None,
             ltk2gtk('Statistics'),
             lambda w, self=self: self.mPlayerStats(mode=101)),
            ('rules', gtk.STOCK_HELP,
             ltk2gtk('&Rules'), 'F1',
             ltk2gtk('Rules'),
             self.mHelpRules),
            ('quit', gtk.STOCK_QUIT,
             ltk2gtk('&Quit'), '<control>Q',
             ltk2gtk('Quit PySol'),
             self.mQuit),

            ### menus
            ('file',           None, ltk2gtk('&File')),
            ('recentgames',    None, ltk2gtk('R&ecent games')),
            ('favoritegames',  None, ltk2gtk('Fa&vorite games')),
            ('select',         None, ltk2gtk('&Select')),
            ('edit',           None, ltk2gtk('&Edit')),
            ('game',           None, ltk2gtk('&Game')),
            ('assist',         None, ltk2gtk('&Assist')),
            ('options',        None, ltk2gtk('&Options')),
            ('assistlevel',    None, ltk2gtk('Assist &level')),
            ('automaticplay',  None, ltk2gtk('&Automatic play')),
            ('animations',     None, ltk2gtk('A&nimations')),
            ('mouse',          None, ltk2gtk('&Mouse')),
            ('cardview',       None, ltk2gtk('Card &view')),
            ('toolbar',        None, ltk2gtk('&Toolbar')),
            ('statusbar',      None, ltk2gtk('Stat&usbar')),
            ('help',           None, ltk2gtk('&Help')),

            ### menuitems
            ('playablepreview', None,
             ltk2gtk('Playable pre&view...'), 'V',
             None, self.mSelectGameDialogWithPreview),
            ('selectgamebynumber', None,
             ltk2gtk('Select game by nu&mber...'), None,
             None, self.mSelectGameById),
            ('addtofavorites', None,
             ltk2gtk('A&dd to favorites'), None,
             None, self.mAddFavor),
            ('removefromfavorites', None,
             ltk2gtk('R&emove from favorites'), None,
             None, self.mDelFavor),
            ('saveas', None,
             ltk2gtk('Save &as...'), None,
             None, self.mSaveAs),
            ('holdandquit', None,
             ltk2gtk('&Hold and quit'), None,
             None, self.mHoldAndQuit),
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
            ('sound', None,
             ltk2gtk('&Sound...'), None,
             None, self.mOptSoundDialog),
            ('cardset', None,
             ltk2gtk('Cards&et...'), '<control>E',
             None, self.mSelectCardsetDialog),
            ('tabletile', None,
             ltk2gtk('Table t&ile...'), None,
             None, self.mOptTableTile),
            ('fonts', None,
             ltk2gtk('&Fonts...'), None,
             None, self.mOptFonts),
            ('colors', None,
             ltk2gtk('&Colors...'), None,
             None, self.mOptColors),
            ('timeouts', None,
             ltk2gtk('Time&outs...'), None,
             None, self.mOptTimeouts),
            ('contents', None,
             ltk2gtk('&Contents'), '<control>F1',
             None, self.mHelp),
            ('aboutpysol', None,
             ltk2gtk('&About ')+TITLE+'...',
             None,None,self.mHelpAbout),
            ('updateall', None,
             'Redraw Game', '<control>L',
             None,
             self.updateAll),
            )

        #
        toggle_entries = [
            ('pause', gtk.STOCK_STOP,            # action, stock
             ltk2gtk('&Pause'), 'P',             # label, accelerator
             ltk2gtk('Pause game'),              # tooltip
             self.mPause,                        # callback
             False,                              # initial value
             ),
            ('negativecardsbottom', None,
             ltk2gtk('&Negative cards bottom'), None, None,
             self.mOptNegativeBottom,
             self.app.opt.negative_bottom,
             ),
            ('showstatusbar', None,
             ltk2gtk('Show &statusbar'), None, None,
             self.mOptStatusbar,
             self.app.opt.statusbar,
             ),
            ]
        for label, action, opt_name, update_game in (
            ('A&uto drop',   'optautodrop', 'autodrop',               False),
            ('Auto &face up',           '', 'autofaceup',             False),
            ('Auto &deal',              '', 'autodeal',               False),
            ('&Quick play',             '', 'quickplay',              False),
            ('Enable &undo',            '', 'undo',                   False),
            ('Enable &bookmarks',       '', 'bookmarks',              False),
            ('Enable &hint',            '', 'hint',                   False),
            ('Enable highlight p&iles', '', 'highlight_piles',        False),
            ('Enable highlight &cards', '', 'highlight_cards',        False),
            ('Enable highlight same &rank', '', 'highlight_samerank', False),
            ('Highlight &no matching',  '', 'highlight_not_matching', False),
            ('Card shado&w',            '', 'shadow',                 False),
            ('Shade &legal moves',      '', 'shade',                  False),
            ('Shrink face-down cards',  '', 'shrink_face_down',       True),
            ('Shade &filled stacks',    '', 'shade_filled_stacks',    True),
            ('Show &number of cards',   '', 'num_cards',              False),
            ('Use mouse for undo/redo', '', 'mouse_undo',             False),
            ('&Demo logo',              '', 'demo_logo',              False),
            ('Startup splash sc&reen',  '', 'splashscreen',           False),
            ('&Show removed tiles (in Mahjongg games)', '', 'mahjongg_show_removed', True),
            ('Show hint &arrow (in Shisen-Sho games)', '', 'shisen_show_hint', False),
            ):
            if not action:
                action = re.sub(r'[^0-9a-zA-Z]', '', label).lower()
            toggle_entries.append(
                (action,
                 None, ltk2gtk(label),
                 None, None,
                 lambda w, o=opt_name, u=update_game: self.mOptToggle(w, o, u),
                 getattr(self.app.opt, opt_name)))

        #
        animations_entries = (
          ('animationnone',     None, ltk2gtk('&None'),        None, None, 0),
          ('animationveryfast', None, ltk2gtk('&Very fast'),   None, None, 1),
          ('animationfast',     None, ltk2gtk('&Fast'),        None, None, 2),
          ('animationmedium',   None, ltk2gtk('&Medium'),      None, None, 3),
          ('animationslow',     None, ltk2gtk('&Slow'),        None, None, 4),
          ('animationveryslow', None, ltk2gtk('V&ery slow'),   None, None, 5),
          )
        mouse_entries = (
          ('draganddrop',   None, ltk2gtk('&Drag-and-Drop'),   None, None, 0),
          ('pointandclick', None, ltk2gtk('&Point-and-Click'), None, None, 1),
          ('stickymouse',   None, ltk2gtk('&Sticky mouse'),    None, None, 2),
          )
        toolbar_side_entries = (
            ('toolbarhide',     None, ltk2gtk('Hide'),         None, None, 0),
            ('toolbartop',      None, ltk2gtk('Top'),          None, None, 1),
            ('toolbarbottom',   None, ltk2gtk('Bottom'),       None, None, 2),
            ('toolbarleft',     None, ltk2gtk('Left'),         None, None, 3),
            ('toolbarright',    None, ltk2gtk('Right'),        None, None, 4),
            )

        #
        ui_info = '''<ui>
  <menubar name='menubar'>

    <menu action='file'>
      <menuitem action='newgame'/>
      <menuitem action='selectgamebynumber'/>
      <menu action='recentgames'/>
      <menu action='favoritegames'/>
      <menuitem action='addtofavorites'/>
      <menuitem action='removefromfavorites'/>
      <separator/>
      <menuitem action='open'/>
      <menuitem action='save'/>
      <menuitem action='saveas'/>
      <separator/>
      <menuitem action='holdandquit'/>
      <menuitem action='quit'/>
      <menuitem action='quit'/>
    </menu>

    <menu action='select'>
      <menuitem action='playablepreview'/>
      <separator/>
    </menu>

    <menu action='edit'>
      <menuitem action='undo'/>
      <menuitem action='redo'/>
      <menuitem action='redoall'/>
      <separator/>
      <menuitem action='restart'/>
      <!--
      <separator/>
      <menuitem action='updateall'/>
      -->
    </menu>

    <menu action='game'>
      <menuitem action='dealcards'/>
      <menuitem action='autodrop'/>
      <menuitem action='pause'/>
      <separator/>
      <menuitem action='status'/>
      <menuitem action='stats'/>
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
        <separator/>
        <menuitem action='showremovedtilesinmahjongggames'/>
        <menuitem action='showhintarrowinshisenshogames'/>
      </menu>
      <separator/>
      <menuitem action='sound'/>
      <menuitem action='cardset'/>
      <menuitem action='tabletile'/>
      <menu action='animations'>
        <menuitem action='animationnone'/>
        <menuitem action='animationveryfast'/>
        <menuitem action='animationfast'/>
        <menuitem action='animationmedium'/>
        <menuitem action='animationslow'/>
        <menuitem action='animationveryslow'/>
      </menu>
      <menu action='cardview'>
        <menuitem action='cardshadow'/>
        <menuitem action='shadelegalmoves'/>
        <menuitem action='negativecardsbottom'/>
        <menuitem action='shrinkfacedowncards'/>
        <menuitem action='shadefilledstacks'/>
      </menu>
      <menu action='mouse'>
        <menuitem action='draganddrop'/>
        <menuitem action='pointandclick'/>
        <menuitem action='stickymouse'/>
        <separator/>
        <menuitem action='usemouseforundoredo'/>
      </menu>
      <separator/>
      <menuitem action='fonts'/>
      <menuitem action='colors'/>
      <menuitem action='timeouts'/>
      <separator/>
      <menuitem action='demologo'/>
      <menuitem action='startupsplashscreen'/>
      <menu action='toolbar'>
        <menuitem action='toolbarhide'/>
        <menuitem action='toolbartop'/>
        <menuitem action='toolbarbottom'/>
        <menuitem action='toolbarleft'/>
        <menuitem action='toolbarright'/>
      </menu>
      <menu action='statusbar'>
        <menuitem action='showstatusbar'/>
        <menuitem action='shownumberofcards'/>
      </menu>
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
        t = ['drag-n-drop', 'point-n-click', 'sticky-mouse'].index(self.app.opt.mouse_type)
        action_group.add_radio_actions(mouse_entries,
                                       t,
                                       self.mOptMouseType)
        action_group.add_radio_actions(toolbar_side_entries,
                                       self.app.opt.toolbar,
                                       self.mOptToolbar)

        ui_manager.insert_action_group(action_group, 0)
        self.top.add_accel_group(ui_manager.get_accel_group())
        self.top.ui_manager = ui_manager

        #ui_manager.get_widget('/menubar/file/recentgames').show()
        #ui_manager.get_widget('/menubar/file/favoritegames').show()

        games = map(self.app.gdb.get, self.app.gdb.getGamesIdSortedByName())
        menu = ui_manager.get_widget('/menubar/select').get_submenu()
        self._createSelectMenu(games, menu)

        if not self.app.audio.CAN_PLAY_SOUND:
            item = ui_manager.get_widget('/menubar/options/sound')
            item.set_sensitive(False)

        menubar = ui_manager.get_widget('/menubar')
        return menubar


    #
    # Select Game menu creation
    #

    def _getNumGames(self, games, select_data):
        ngames = 0
        for label, select_func in select_data:
            ngames += len(filter(select_func, games))
        return ngames

    def _createSubMenu(self, menu, label):
        menu_item = gtk.MenuItem(label)
        menu.add(menu_item)
        menu_item.show()
        submenu = gtk.Menu()
        menu_item.set_submenu(submenu)
        return submenu

    def _addGamesMenuItem(self, menu, gi, short_name=False):
        if not gi: return
        if short_name:
            label = gi.short_name
        else:
            label = gi.name
        menu_item = gtk.MenuItem(label)
        menu_item.set_data('user_data', gi.id)
        menu_item.connect('activate', self.mSelectGame)
        menu.add(menu_item)
        menu_item.show()

    def _addGamesSubMenu(self, games, menu, short_name=False):
        for gi in games:
            self._addGamesMenuItem(menu, gi, short_name=short_name)

    def _addAllGamesMenu(self, games, menu):
        menu = self._createSubMenu(menu, label=ltk2gtk('&All games by name'))
        n, d = 0, self._cb_max
        i = 0
        while True:
            if self.progress: self.progress.update(step=1)
            i += 1
            if not games[n:n+d]:
                break
            m = min(n+d-1, len(games)-1)
            n1, n2 = games[n].name, games[m].name
            label = n1[:3]+' - '+n2[:3]
            submenu = self._createSubMenu(menu, label=label)
            self._addGamesSubMenu(games[n:n+d], submenu)
            n += d

    def _addSelectedGamesSubMenu(self, games, menu, select_data):
        for label, select_func in select_data:
            g = filter(select_func, games)
            if not g:
                continue
            submenu = self._createSubMenu(menu, label=label)
            self._addGamesSubMenu(g, submenu)

    def _addPopularGamesMenu(self, games, menu):
        select_func = lambda gi: gi.si.game_flags & GI.GT_POPULAR
        if len(filter(select_func, games)) == 0:
            return
        data = (ltk2gtk('&Popular games'), select_func)
        self._addSelectedGamesSubMenu(games, menu, (data, ))

    def _addGamesByType(self, games, menu, label, data):
        if self._getNumGames(games, data) == 0:
            return
        submenu = self._createSubMenu(menu, label=label)
        self._addSelectedGamesSubMenu(games, submenu, data)

    def _addMahjonggGamesMenu(self, games, menu):
        select_func = lambda gi: gi.si.game_type == GI.GT_MAHJONGG
        mahjongg_games = filter(select_func, games)
        if len(mahjongg_games) == 0:
            return
        menu = self._createSubMenu(menu, label=ltk2gtk('&Mahjongg games'))
        #
        def add_menu(games, c0, c1, menu=menu):
            if not games:
                return
            label = c0 + ' - ' + c1
            if c0 == c1:
                label = c0
            submenu = self._createSubMenu(menu, label=label)
            self._addGamesSubMenu(games, submenu, short_name=True)
        #
        games = {}
        for gi in mahjongg_games:
            c = gi.short_name.strip()[0]
            if c in games:
                games[c].append(gi)
            else:
                games[c] = [gi]
        games = games.items()
        games.sort()
        #
        g0 = []
        c0 = c1 = games[0][0]
        for c, g1 in games:
            if len(g0)+len(g1) >= self._cb_max:
                add_menu(g0, c0, c1)
                g0 = g1
                c0 = c1 = c
            else:
                g0 += g1
                c1 = c
        add_menu(g0, c0, c1)


    def _createSelectMenu(self, games, menu):
        assert isinstance(menu, gtk.Menu)
        self._addPopularGamesMenu(games, menu)
        for l, d in (
            (ltk2gtk('&French games'),   GI.SELECT_GAME_BY_TYPE),
            (ltk2gtk('&Oriental games'), GI.SELECT_ORIENTAL_GAME_BY_TYPE),
            (ltk2gtk('&Special games'),  GI.SELECT_SPECIAL_GAME_BY_TYPE),
            ):
            self._addGamesByType(games, menu, l, d)
        self._addMahjonggGamesMenu(games, menu)
        sep = gtk.SeparatorMenuItem()
        menu.add(sep)
        self._addAllGamesMenu(games, menu)


    #
    # menu updates
    #

## WARNING: setMenuState: not found: /menubar/assist/findcard
    def setMenuState(self, state, path):
        path_map = {
            'help.rulesforthisgame': '/menubar/help/rules',
            'options.automaticplay.autodrop': '/menubar/options/automaticplay/optautodrop'
            }
        if path in path_map:
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

    def mAddFavor(self, w):
        gameid = self.app.game.id
        if gameid not in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.append(gameid)
            self.updateFavoriteGamesMenu()

    def mDelFavor(self, w):
        gameid = self.app.game.id
        if gameid in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.remove(gameid)
            self.updateFavoriteGamesMenu()

    def updateFavoriteGamesMenu(self):
        games = self.app.opt.favorite_gameid
        self._updateGamesMenu('/menubar/file/favoritegames', games)
        in_favor = self.app.game.id in games
        item = self.top.ui_manager.get_widget('/menubar/file/addtofavorites')
        item.set_sensitive(not in_favor)
        item = self.top.ui_manager.get_widget('/menubar/file/removefromfavorites')
        item.set_sensitive(in_favor)

    def updateRecentGamesMenu(self, games):
        self._updateGamesMenu('/menubar/file/recentgames', games)

    def updateBookmarkMenuState(self):
        # FIXME
        pass

    def _updateGamesMenu(self, path, games):
        item = self.top.ui_manager.get_widget(path)
        item.show()
        menu = item.get_submenu()
        menu.show()
        #
        menu_games = []
        def checkFavor(item):
            gameid = item.get_data('user_data')
            if gameid in games:
                menu_games.append(gameid)
            else:
                menu.remove(item)
        menu.foreach(checkFavor)
        #
        for gameid in games:
            if gameid not in menu_games:
                gi = self.app.getGameInfo(gameid)
                self._addGamesMenuItem(menu, gi)
        if not games:
            item = gtk.MenuItem(_('Empty'))
            item.show()
            item.set_sensitive(False)
            menu.add(item)


    def _createFileChooser(self, title, action, idir, ifile, stock):
        d = gtk.FileChooserDialog(title, self.top, action,
                                  (stock, gtk.RESPONSE_ACCEPT,
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
            idir, ifile = '', ''
        if not idir:
            idir = self.app.dn.savegames
        filename = self._createFileChooser(_('Open Game'),
                                           gtk.FILE_CHOOSER_ACTION_OPEN,
                                           idir, '',
                                           gtk.STOCK_OPEN)
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
            if os.name == 'posix':
                filename = filename + '-' + self.game.getGameNumber(format=0)
            elif os.path.supports_unicode_filenames: # new in python 2.3
                filename = filename + '-' + self.game.getGameNumber(format=0)
            else:
                filename = filename + '-01'
            filename = filename + '.pso'
        idir, ifile = os.path.split(os.path.normpath(filename))
        if not idir:
            idir = self.app.dn.savegames
        ##print self.game.filename, ifile
        filename = self._createFileChooser(_('Save Game'),
                                           gtk.FILE_CHOOSER_ACTION_SAVE,
                                           idir, ifile,
                                           gtk.STOCK_SAVE)
        if filename:
            ##filename = os.path.normpath(filename)
            ##filename = os.path.normcase(filename)
            self.game.saveGame(filename)
            self.updateMenus()


    def mSelectGame(self, menu_item):
        game_id = menu_item.get_data('user_data')
        self._mSelectGame(game_id)


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
        d = SelectGameDialogWithPreview(self.top, title=_('Select game'),
                                        app=self.app, gameid=self.game.id,
                                        bookmark=bookmark)
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

    def mPause(self, *args):
        if not self.game.pause:
            if self._cancelDrag(): return
        self.game.doPause()

    def mOptSoundDialog(self, *args):
        if self._cancelDrag(break_pause=False): return
        d = SoundOptionsDialog(self.top, _('Sound settings'), self.app)


    def mOptTableTile(self, *args):
        if self._cancelDrag(break_pause=False): return
        key = self.app.tabletile_index
        if key <= 0:
            key = self.app.opt.colors['table']
        d = SelectTileDialogWithPreview(self.top, app=self.app,
                                        title=_('Select table background'),
                                        manager=self.app.tabletile_manager,
                                        key=key)
        if d.status == 0 and d.button in (0, 1):
            if isinstance(d.key, str):
                tile = self.app.tabletile_manager.get(0)
                tile.color = d.key
                self.app.setTile(0)
            elif d.key > 0 and d.key != self.app.tabletile_index:
                self.app.setTile(d.key)


    def mSelectCardsetDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        key = self.app.nextgame.cardset.index
        d = SelectCardsetDialogWithPreview(self.top, title=_('Select cardset'),
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


    def mOptToggle(self, w, opt_name, update_game):
        ##print 'mOptToggle:', opt, w.get_active()
        if self._cancelDrag(break_pause=False): return
        self.app.opt.__dict__[opt_name] = w.get_active()
        if update_game:
            self.game.endGame(bookmark=1)
            self.game.quitGame(bookmark=1)

    def mOptNegativeBottom(self, w):
        if self._cancelDrag(): return
        self.app.opt.negative_bottom = w.get_active()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)


    def mOptAnimations(self, w1, w2):
        self.app.opt.animations = w1.get_current_value()


    def mOptMouseType(self, w1, w2):
        v = w1.get_current_value()
        t = ('drag-n-drop', 'point-n-click', 'sticky-mouse')[v]
        self.app.opt.mouse_type = t


    def mOptToolbar(self, w1, w2):
        if self._cancelDrag(break_pause=False): return
        side = w1.get_current_value()
        self.app.opt.toolbar = side
        if self.app.toolbar.show(side, resize=1):
            self.top.update_idletasks()


    def mOptStatusbar(self, w):
        if self._cancelDrag(break_pause=False): return
        if not self.app.statusbar: return
        side = w.get_active()
        self.app.opt.statusbar = side
        resize = not self.app.opt.save_games_geometry
        if self.app.statusbar.show(side, resize=resize):
            self.top.update_idletasks()


    def updateAll(self, *event):
        self.app.canvas.updateAll()


    def _setCommentMenu(self, v):
        # FIXME
        pass

    def _setPauseMenu(self, v):
        # FIXME
        pass

    def mStatus(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.mPlayerStats(mode=100)

