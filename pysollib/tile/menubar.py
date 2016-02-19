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

__all__ = ['PysolMenubarTk']

# imports
import math, os, sys, re
import Tkinter
import ttk
import traceback
import tkFileDialog

# PySol imports
from pysollib.mygettext import _, n_
from pysollib.mfxutil import Struct, kwdefault
from pysollib.mfxutil import Image, USE_PIL
from pysollib.util import CARDSET
from pysollib.settings import TITLE, WIN_SYSTEM
from pysollib.settings import SELECT_GAME_MENU
from pysollib.settings import USE_FREECELL_SOLVER
from pysollib.settings import DEBUG
from pysollib.gamedb import GI

# toolkit imports
from pysollib.ui.tktile.tkconst import EVENT_HANDLED, EVENT_PROPAGATE, CURSOR_WATCH, COMPOUNDS
from pysollib.ui.tktile.tkutil import bind, after_idle
from tkwidget import MfxMessageDialog
from selectgame import SelectGameDialog, SelectGameDialogWithPreview
from soundoptionsdialog import SoundOptionsDialog
from selectcardset import SelectCardsetDialogWithPreview
from selecttile import SelectTileDialogWithPreview
from findcarddialog import connect_game_find_card_dialog, destroy_find_card_dialog
from solverdialog import connect_game_solver_dialog

from pysollib.ui.tktile.tkconst import TOOLBAR_BUTTONS

from pysollib.ui.tktile.menubar import createToolbarMenu, MfxMenubar, MfxMenu, PysolMenubarTkCommon
# ************************************************************************
# * - create menubar
# * - update menubar
# * - menu actions
# ************************************************************************

class PysolMenubarTk(PysolMenubarTkCommon):
    def __init__(self, app, top, progress=None):
        PysolMenubarTkCommon.__init__(self, app, top, progress)

    def _setOptions(self):
        PysolMenubarTkCommon._setOptions(self)
        tkopt, opt = self.tkopt, self.app.opt
        tkopt.theme.set(opt.tile_theme)

    def _connect_game_find_card_dialog(self, game):
        return connect_game_find_card_dialog(game)

    def _destroy_find_card_dialog(self):
        return destroy_find_card_dialog()

    def _connect_game_solver_dialog(self, game):
        return connect_game_solver_dialog(game)
    #
    # create the menubar
    #


    def mSelectCardsetDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        key = self.app.nextgame.cardset.index
        cs = self.app.selectCardset(_("Select ")+CARDSET, key)
        if not cs:
            return
        self.app.nextgame.cardset = cs
        self._cancelDrag()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def _mOptCardback(self, index):
        if self._cancelDrag(break_pause=False): return
        cs = self.app.cardset
        old_index = cs.backindex
        cs.updateCardback(backindex=index)
        if cs.backindex == old_index:
            return
        self.app.updateCardset(self.game.id)
        image = self.app.images.getBack(update=True)
        for card in self.game.cards:
            card.updateCardBackground(image=image)
        self.app.canvas.update_idletasks()
        self.tkopt.cardback.set(cs.backindex)

    def mOptCardback(self, *event):
        self._mOptCardback(self.tkopt.cardback.get())

    def mOptChangeCardback(self, *event):
        self._mOptCardback(self.app.cardset.backindex + 1)

    def mOptChangeTableTile(self, *event):
        if self._cancelDrag(break_pause=False): return
        n = self.app.tabletile_manager.len()
        if n >= 2:
            i = (self.tkopt.tabletile.get() + 1) % n
            if self.app.setTile(i):
                self.tkopt.tabletile.set(i)

    def mSelectTileDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        key = self.app.tabletile_index
        if key <= 0:
            key = self.app.opt.colors['table'] ##.lower()
        d = SelectTileDialogWithPreview(self.top, app=self.app,
                                        title=_("Select table background"),
                                        manager=self.app.tabletile_manager,
                                        key=key)
        if d.status == 0 and d.button == 0:
            if isinstance(d.key, str):
                tile = self.app.tabletile_manager.get(0)
                tile.color = d.key
                if self.app.setTile(0):
                    self.tkopt.tabletile.set(0)
            elif d.key > 0 and d.key != self.app.tabletile_index:
                if self.app.setTile(d.key):
                    self.tkopt.tabletile.set(d.key)

    def mOptToolbar(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarSide(self.tkopt.toolbar.get())

    def mOptToolbarStyle(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarStyle(self.tkopt.toolbar_style.get())

    def mOptToolbarCompound(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarCompound(self.tkopt.toolbar_compound.get())

    def mOptToolbarSize(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarSize(self.tkopt.toolbar_size.get())

    def mOptToolbarConfig(self, w):
        self.toolbarConfig(w, self.tkopt.toolbar_vars[w].get())

    def mOptStatusbar(self, *event):
        if self._cancelDrag(break_pause=False): return
        if not self.app.statusbar: return
        side = self.tkopt.statusbar.get()
        self.app.opt.statusbar = side
        resize = not self.app.opt.save_games_geometry
        if self.app.statusbar.show(side, resize=resize):
            self.top.update_idletasks()

    def mOptNumCards(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.num_cards = self.tkopt.num_cards.get()

    def mOptHelpbar(self, *event):
        if self._cancelDrag(break_pause=False): return
        if not self.app.helpbar: return
        show = self.tkopt.helpbar.get()
        self.app.opt.helpbar = show
        resize = not self.app.opt.save_games_geometry
        if self.app.helpbar.show(show, resize=resize):
            self.top.update_idletasks()

    def mOptSaveGamesGeometry(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.save_games_geometry = self.tkopt.save_games_geometry.get()

    def mOptDemoLogo(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.demo_logo = self.tkopt.demo_logo.get()

    def mOptSplashscreen(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.splashscreen = self.tkopt.splashscreen.get()

    def mOptMouseType(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.mouse_type = self.tkopt.mouse_type.get()

    def mOptMouseUndo(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.mouse_undo = self.tkopt.mouse_undo.get()

    def mOptNegativeBottom(self, *event):
        if self._cancelDrag(): return
        self.app.opt.negative_bottom = self.tkopt.negative_bottom.get()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)


    #
    # toolbar support
    #

    def setToolbarSide(self, side):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar = side
        self.tkopt.toolbar.set(side)                    # update radiobutton
        resize = not self.app.opt.save_games_geometry
        if self.app.toolbar.show(side, resize=resize):
            self.top.update_idletasks()

    def setToolbarSize(self, size):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_size = size
        self.tkopt.toolbar_size.set(size)                # update radiobutton
        dir = self.app.getToolbarImagesDir()
        if self.app.toolbar.updateImages(dir, size):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarStyle(self, style):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_style = style
        self.tkopt.toolbar_style.set(style)                # update radiobutton
        dir = self.app.getToolbarImagesDir()
        size = self.app.opt.toolbar_size
        if self.app.toolbar.updateImages(dir, size):
            ##self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarCompound(self, compound):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_compound = compound
        self.tkopt.toolbar_compound.set(compound)          # update radiobutton
        if self.app.toolbar.setCompound(compound):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def toolbarConfig(self, w, v):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_vars[w] = v
        self.app.toolbar.config(w, v)
        self.top.update_idletasks()

    #
    # stacks descriptions
    #

    def mStackDesk(self, *event):
        if self.game.stackdesc_list:
            self.game.deleteStackDesc()
        else:
            if self._cancelDrag(break_pause=True): return
            self.game.showStackDesc()

    #
    # Tile (ttk)
    #

    def mOptTheme(self, *event):
        theme = self.tkopt.theme.get()
        self.app.opt.tile_theme = theme
        d = MfxMessageDialog(self.top, title=_("Change theme"),
                      text=_("""\
This settings will take effect
the next time you restart """)+TITLE,
                      bitmap="warning",
                      default=0, strings=(_("&OK"),))

    def createThemesMenu(self, menu):
        submenu = MfxMenu(menu, label=n_("Set t&heme"))
        all_themes = list(ttk.Style(self.top).theme_names())
        all_themes.sort()
        #
        tn = {
            'default':     n_('Default'),
            'classic':     n_('Classic'),
            'alt':         n_('Revitalized'),
            'winnative':   n_('Windows native'),
            'xpnative':    n_('XP Native'),
            'aqua':        n_('Aqua'),
            }
        for t in all_themes:
            try:
                n = tn[t]
            except KeyError:
                n = t.capitalize()
            submenu.add_radiobutton(label=n, variable=self.tkopt.theme,
                                    value=t, command=self.mOptTheme)

    def wizardDialog(self, edit=False):
        from pysollib.wizardutil import write_game, reset_wizard
        from wizarddialog import WizardDialog

        if edit:
            reset_wizard(self.game)
        else:
            reset_wizard(None)
        d = WizardDialog(self.top, _('Solitaire Wizard'), self.app)
        if d.status == 0 and d.button == 0:
            try:
                if edit:
                    gameid = write_game(self.app, game=self.game)
                else:
                    gameid = write_game(self.app)
            except Exception, err:
                if DEBUG:
                    traceback.print_exc()
                d = MfxMessageDialog(self.top, title=_('Save game error'),
                                     text=_('''
Error while saving game.

%s
''') % str(err),
                                     bitmap='error')
                return

            if SELECT_GAME_MENU:
                menu = self.menupath[".menubar.select.customgames"][2]
                select_func = lambda gi: gi.si.game_type == GI.GT_CUSTOM
                games = map(self.app.gdb.get,
                            self.app.gdb.getGamesIdSortedByName())
                games = filter(select_func, games)
                self.updateGamesMenu(menu, games)

            self.tkopt.gameid.set(gameid)
            self._mSelectGame(gameid, force=True)


    def mWizard(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.wizardDialog()

    def mWizardEdit(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.wizardDialog(edit=True)

