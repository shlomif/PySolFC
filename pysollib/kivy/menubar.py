#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
# Copyright (C) 2017 LB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------#

import math
import os
import re

from kivy.cache import Cache
from kivy.clock import Clock
from kivy.core.window import Window

from pysollib.gamedb import GI
from pysollib.kivy.LApp import LMenu
from pysollib.kivy.LApp import LMenuItem
from pysollib.kivy.LApp import LScrollView
from pysollib.kivy.LApp import LTopLevel
from pysollib.kivy.LApp import LTreeNode
from pysollib.kivy.LApp import LTreeRoot
from pysollib.kivy.LApp import LTreeSliderNode
from pysollib.kivy.LObjWrap import LBoolWrap
from pysollib.kivy.LObjWrap import LListWrap
from pysollib.kivy.LObjWrap import LNumWrap
from pysollib.kivy.LObjWrap import LStringWrap
from pysollib.kivy.androidrot import AndroidScreenRotation
from pysollib.kivy.findcarddialog import destroy_find_card_dialog
from pysollib.kivy.fullpicturedialog import destroy_full_picture_dialog
from pysollib.kivy.selectcardset import SelectCardsetDialogWithPreview
from pysollib.kivy.selectgame import SelectGameDialog
from pysollib.kivy.solverdialog import connect_game_solver_dialog
from pysollib.kivy.tkconst import CURSOR_WATCH, EVENT_HANDLED, EVENT_PROPAGATE
from pysollib.kivy.tkconst import TOOLBAR_BUTTONS
from pysollib.kivy.tkutil import after_idle
from pysollib.kivy.tkutil import bind
from pysollib.kivy.toast import Toast
from pysollib.mfxutil import Struct
from pysollib.mygettext import _
from pysollib.pysoltk import MfxMessageDialog
from pysollib.pysoltk import connect_game_find_card_dialog
from pysollib.pysoltk import connect_game_full_picture_dialog
from pysollib.settings import SELECT_GAME_MENU
from pysollib.settings import TITLE

# ************************************************************************
# * Common base
# ************************************************************************


class LMenuBase(object):
    def __init__(self, menubar, parent, title, app):
        self.menubar = menubar
        self.parent = parent
        self.app = app
        self.title = title

    def make_pop_command(self, parent, title):
        def pop_command(event):
            parent.popWork(title)
        return pop_command

    def closeWindow(self, event):
        self.parent.popWork(self.title)

    def auto_close(self, command):
        def auto_close_command():
            if command is not None:
                command()
            self.closeWindow(0)
        return auto_close_command

    def make_toggle_command(self, variable, command):
        def auto_command():
            variable.value = not variable.value
            if command is not None:
                command()
        return auto_command

    def make_val_command(self, variable, value, command):
        def val_command():
            variable.value = value
            if command is not None:
                command()
        return val_command

    def make_vars_command(self, command, key):
        def vars_command():
            command(key)
        return vars_command

    def make_game_command(self, key, command):
        def game_command():
            self.closeWindow(0)
            command(key)
        return game_command

    def make_command(self, command):
        def _command():
            self.closeWindow(0)
            if command is not None:
                command()
        return _command

    def addCheckNode(self, tv, rg, title, auto_var, auto_com):
        command = self.make_toggle_command(auto_var, auto_com)
        rg1 = tv.add_node(
            LTreeNode(text=title, command=command, variable=auto_var), rg)
        return rg1

    def addRadioNode(self, tv, rg, title, auto_var, auto_val, auto_com):
        command = self.make_val_command(auto_var, auto_val, auto_com)
        rg1 = tv.add_node(
            LTreeNode(text=title,
                      command=command,
                      variable=auto_var, value=auto_val), rg)
        return rg1

    def addSliderNode(self, tv, rg, auto_var, auto_setup):
        rg1 = tv.add_node(
            LTreeSliderNode(variable=auto_var, setup=auto_setup), rg)
        return rg1

# ************************************************************************
# * Tree Generators
# ************************************************************************


class LTreeGenerator(LMenuBase):
    def __init__(self, menubar, parent, title, app):
        super(LTreeGenerator, self).__init__(menubar, parent, title, app)

    def generate(self):
        tv = LTreeRoot(root_options={'text': 'EditTree'})
        tv.hide_root = True
        tv.size_hint = 1, None
        tv.bind(minimum_height=tv.setter('height'))

        gen = self.buildTree(tv, None)

        def process(dt):
            try:
                gen.send(None)
                Clock.schedule_once(process, 0.2)
            except StopIteration:
                print('generator: all jobs done')
                pass

        Clock.schedule_once(process, 0.2)
        return tv

    def buildTree(self, tv, node):
        print('buildTree generator function not implemented')
        # needs at least on 'yield' statement
        # not reentrant: do not recurse !
        # implement it in a dervied class
        yield

# ************************************************************************
# * Menu Dialogs
# ************************************************************************


class LMenuDialog(LMenuBase):

    dialogCache = {}

    def __init__(self, menubar, parent, title, app, **kw):
        super(LMenuDialog, self).__init__(menubar, parent, title, app)

        self.window = None
        self.running = False
        self.persist = False
        if 'persist' in kw:
            self.persist = kw['persist']
        self.tvroot = None
        if 'tv' in kw:
            self.tvroot = kw['tv']

        # prüfen ob noch aktiv - toggle.

        if parent.workStack.peek(title) is not None:
            parent.popWork(title)
            return

        if self.persist and title in self.dialogCache:
            parent.pushWork(title, self.dialogCache[title])
            return

        pc = self.closeWindow = self.make_pop_command(parent, title)

        # neuen Dialog aufbauen.

        window = LTopLevel(parent, title, **kw)
        window.titleline.bind(on_press=pc)
        self.parent.pushWork(title, window)
        self.window = window
        self.running = True

        from pysollib.kivy.LApp import get_menu_size_hint

        def updrule(obj, val):
            self.window.size_hint = get_menu_size_hint()
        updrule(0, 0)
        self.parent.bind(size=updrule)

        if self.persist:
            self.dialogCache[title] = window

        # Tree construct or assign.

        if self.tvroot is None:
            tv = self.initTree()
            self.buildTree(tv, None)
        else:
            tv = self.tvroot

        # show the tree in a scroll window

        root = LScrollView(pos=(0, 0))
        root.add_widget(tv)
        self.window.content.add_widget(root)

    def initTree(self):
        tv = self.tvroot = LTreeRoot(root_options={'text': 'EditTree'})
        tv.hide_root = True
        tv.size_hint = 1, None
        tv.bind(minimum_height=tv.setter('height'))
        return tv

    def buildTree(self, tree, node):
        # to implement in dervied class if needed
        pass

# ************************************************************************


class MainMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['persist'] = True
        super(MainMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

        # print('MainMenuDialog starting')

    def buildTree(self, tv, node):
        rg = tv.add_node(
            LTreeNode(
                text=_("File"),
                command=self.auto_close(self.menubar.mFileMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Games"),
                command=self.auto_close(
                    self.menubar.mSelectGameDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Tools"),
                command=self.auto_close(self.menubar.mEditMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Statistics"),
                command=self.auto_close(self.menubar.mGameMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Assist"),
                command=self.auto_close(
                    self.menubar.mAssistMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Options"),
                command=self.auto_close(
                    self.menubar.mOptionsMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Help"),
                command=self.auto_close(self.menubar.mHelpMenuDialog)))
        del rg

# ************************************************************************


class FileMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        super(FileMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def make_favid_list(self, tv, rg):
        favids = self.app.opt.favorite_gameid
        for fid in favids:
            gi = self.app.getGameInfo(fid)
            if gi:
                command = self.make_game_command(
                    fid, self.menubar._mSelectGame)
                tv.add_node(
                    LTreeNode(text=gi.name, command=command), rg)

    def remove_favid_list(self, tv, rg):
        delist = []
        for n in rg.nodes:
            if n.text not in [_('<Add>'), _('<Remove>')]:
                delist.append(n)
        for m in delist:
            tv.remove_node(m)

    def change_favid_list(self, command, *args):
        def doit():
            command()
            self.remove_favid_list(args[0], args[1])
            self.make_favid_list(args[0], args[1])
        return doit

    def buildTree(self, tv, node):
        rg = tv.add_node(
            LTreeNode(text=_('Recent games')))
        recids = self.app.opt.recent_gameid
        for rid in recids:
            gi = self.app.getGameInfo(rid)
            if gi:
                command = self.make_game_command(
                    rid, self.menubar._mSelectGame)
                tv.add_node(
                    LTreeNode(text=gi.name, command=command), rg)

        rg = tv.add_node(
            LTreeNode(text=_('Favorite games')))
        if rg:
            tv.add_node(LTreeNode(
                text=_('<Add>'),
                command=self.change_favid_list(
                    self.menubar.mAddFavor, tv, rg)), rg)
            tv.add_node(LTreeNode(
                text=_('<Remove>'),
                command=self.change_favid_list(
                    self.menubar.mDelFavor, tv, rg)), rg)

            self.make_favid_list(tv, rg)

        tv.add_node(LTreeNode(
            text=_('Random game'),
            command=self.make_command(self.menubar.mSelectRandomGame)))
        tv.add_node(LTreeNode(
            text=_('Load'), command=self.make_command(self.menubar.mOpen)))
        tv.add_node(LTreeNode(
            text=_('Save'), command=self.make_command(self.menubar.mSaveAs)))

        tv.add_node(LTreeNode(
            text=_('Quit'), command=self.menubar.mHoldAndQuit))

# ************************************************************************


class EditMenuDialog(LMenuDialog):  # Tools

    def __init__(self, menubar, parent, title, app, **kw):
        kw['persist'] = True
        super(EditMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def buildTree(self, tv, node):
        tv.add_node(LTreeNode(
            text=_('New game'), command=self.menubar.mNewGame))
        tv.add_node(LTreeNode(
            text=_('Restart game'), command=self.menubar.mRestart))

        tv.add_node(LTreeNode(
            text=_('Undo'), command=self.menubar.mUndo))
        tv.add_node(LTreeNode(
            text=_('Redo'), command=self.menubar.mRedo))
        tv.add_node(LTreeNode(
            text=_('Redo all'), command=self.menubar.mRedoAll))

        tv.add_node(LTreeNode(
            text=_('Auto drop'), command=self.menubar.mDrop))
        tv.add_node(LTreeNode(
            text=_('Shuffle tiles'), command=self.menubar.mShuffle))
        tv.add_node(LTreeNode(
            text=_('Deal cards'), command=self.menubar.mDeal))
        tv.add_node(LTreeNode(
            text=_('Reset zoom'),
            command=self.auto_close(self.menubar.mResetZoom)))

        self.addCheckNode(tv, None,
                          _('Pause'),
                          self.menubar.tkopt.pause,
                          self.menubar.mPause)

        tv.add_node(LTreeNode(
            text=_('Load game'), command=self.menubar.mOpen))
        tv.add_node(LTreeNode(
            text=_('Save game'), command=self.menubar.mSaveAs))

        tv.add_node(LTreeNode(
            text=_('Help'), command=self.menubar.mHelpRules))

        # -------------------------------------------
        # TBD ?
        '''
        menu.add_separator()
        submenu = MfxMenu(menu, label=n_("&Set bookmark"))
        for i in range(9):
            label = _("Bookmark %d") % (i + 1)
            submenu.add_command(
                label=label, command=lambda i=i: self.mSetBookmark(i))
        submenu = MfxMenu(menu, label=n_("Go&to bookmark"))
        for i in range(9):
            label = _("Bookmark %d") % (i + 1)
            acc = m + "%d" % (i + 1)
            submenu.add_command(
                label=label,
                command=lambda i=i: self.mGotoBookmark(i),
                accelerator=acc)
        menu.add_command(
            label=n_("&Clear bookmarks"), command=self.mClearBookmarks)
        menu.add_separator()
        '''
        # und solitär wizard (-> custom games).
        '''
        tv.add_node(LTreeNode(
            text='Solitaire &Wizard...', command=self.menubar.mWizard))
        tv.add_node(LTreeNode(
                text='Edit current game', command=self.menubar.mWizardEdit))
        '''

# ************************************************************************


class GameMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['persist'] = True
        super(GameMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def make_command(self, key, command):
        def stats_command():
            kw = {}
            kw['mode'] = key
            command(**kw)
        return stats_command

    def buildTree(self, tv, node):
        tv.add_node(LTreeNode(
            text=_('Current game...'),
            command=self.auto_close(
                self.make_command(101, self.menubar.mPlayerStats))), None)

        # tv.add_node(LTreeNode(
        #   text='All games ...',
        #   command=self.make_command(102, self.menubar.mPlayerStats)), None)

    # -------------------------------------------
    # TBD ? - just to remember original tk code.
    '''
        menu.add_command(
            label=n_("S&tatus..."),
            command=lambda x: self.mPlayerStats(mode=100), accelerator=m+"Y")
        menu.add_checkbutton(
            label=n_("&Comments..."), variable=self.tkopt.comment,
            command=self.mEditGameComment)
    '''
    '''
        menu.add_separator()
        submenu = MfxMenu(menu, label=n_("&Statistics"))
        submenu.add_command(
            label=n_("Current game..."),
            command=lambda x: self.mPlayerStats(mode=101))
        submenu.add_command(
            label=n_("All games..."),
            command=lambda x: self.mPlayerStats(mode=102))
        submenu.add_separator()
        submenu.add_command(
            label=n_("Session log..."),
            command=lambda x: self.mPlayerStats(mode=104))
        submenu.add_command(
            label=n_("Full log..."),
            command=lambda x: self.mPlayerStats(mode=103))
        submenu.add_separator()
        submenu.add_command(
            label=TOP_TITLE+"...",
            command=lambda x: self.mPlayerStats(mode=105),
            accelerator=m+"T")
        submenu.add_command(
            label=n_("Progression..."),
            command=lambda x: self.mPlayerStats(mode=107))
        submenu = MfxMenu(menu, label=n_("D&emo statistics..."))
        submenu.add_command(
            label=n_("Current game..."),
            command=lambda x: self.mPlayerStats(mode=1101))
        submenu.add_command(
            label=n_("All games..."),
            command=lambda x: self.mPlayerStats(mode=1102))
    '''

# ************************************************************************


class AssistMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['persist'] = True
        super(AssistMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def buildTree(self, tv, node):
        tv.add_node(LTreeNode(
            text=_('Hint'), command=self.menubar.mHint))

        tv.add_node(LTreeNode(
            text=_('Highlight piles'), command=self.menubar.mHighlightPiles))

        tv.add_node(LTreeNode(
            text=_('Show full picture...'),
            command=self.auto_close(self.menubar.mFullPicture)))

        # tv.add_node(LTreeNode(
        #   text='Find Card', command=self.menubar.mFindCard))

        tv.add_node(LTreeNode(
            text=_('Demo'), command=self.auto_close(self.menubar.mDemo)))

        # -------------------------------------------
        # TBD. How ?

        '''
        menu.add_command(
            label=n_("Demo (&all games)"), command=self.mMixedDemo)
        if USE_FREECELL_SOLVER:
            menu.add_command(label=n_("&Solver..."), command=self.mSolver)
        else:
            menu.add_command(label=n_("&Solver..."), state='disabled')
        menu.add_separator()
        menu.add_command(
            label=n_("&Piles description"),
            command=self.mStackDesk, accelerator="F2")
        '''

# ************************************************************************


class LOptionsMenuGenerator(LTreeGenerator):
    def __init__(self, menubar, parent, title, app):
        super(LOptionsMenuGenerator, self).__init__(
            menubar, parent, title, app)

    def buildTree(self, tv, node):
        # -------------------------------------------
        # Automatic play settings

        rg = tv.add_node(
            LTreeNode(text=_('Automatic play')))
        if rg:
            self.addCheckNode(tv, rg,
                              _('Auto face-up'),
                              self.menubar.tkopt.autofaceup,
                              self.menubar.mOptAutoFaceUp)

            self.addCheckNode(tv, rg,
                              _('Auto drop'),
                              self.menubar.tkopt.autodrop,
                              self.menubar.mOptAutoDrop)

            self.addCheckNode(tv, rg,
                              _('Auto deal'),
                              self.menubar.tkopt.autodeal,
                              self.menubar.mOptAutoDeal)

            # submenu.add_separator()

            self.addCheckNode(tv, rg,
                              _('Quick play'),
                              self.menubar.tkopt.quickplay,
                              self.menubar.mOptQuickPlay)

        yield
        # -------------------------------------------
        # Player assistance

        rg = tv.add_node(
            LTreeNode(text=_('Assist level')))
        if rg:
            self.addCheckNode(tv, rg,
                              _('Enable undo'),
                              self.menubar.tkopt.undo,
                              self.menubar.mOptEnableUndo)

            self.addCheckNode(tv, rg,
                              _('Enable bookmarks'),
                              self.menubar.tkopt.bookmarks,
                              self.menubar.mOptEnableBookmarks)

            self.addCheckNode(tv, rg,
                              _('Enable hint'),
                              self.menubar.tkopt.hint,
                              self.menubar.mOptEnableHint)

            self.addCheckNode(tv, rg,
                              _('Enable shuffle'),
                              self.menubar.tkopt.shuffle,
                              self.menubar.mOptEnableShuffle)

            self.addCheckNode(tv, rg,
                              _('Free hints'),
                              self.menubar.tkopt.free_hint,
                              self.menubar.mOptFreeHints)

            self.addCheckNode(tv, rg,
                              _('Enable highlight piles'),
                              self.menubar.tkopt.highlight_piles,
                              self.menubar.mOptEnableHighlightPiles)

            self.addCheckNode(tv, rg,
                              _('Enable highlight cards'),
                              self.menubar.tkopt.highlight_cards,
                              self.menubar.mOptEnableHighlightCards)

            self.addCheckNode(tv, rg,
                              _('Enable highlight same rank'),
                              self.menubar.tkopt.highlight_samerank,
                              self.menubar.mOptEnableHighlightSameRank)

            self.addCheckNode(tv, rg,
                              _('Enable face-down peek'),
                              self.menubar.tkopt.peek_facedown,
                              self.menubar.mOptEnablePeekFacedown)

            self.addCheckNode(tv, rg,
                              _('Highlight no matching'),
                              self.menubar.tkopt.highlight_not_matching,
                              self.menubar.mOptEnableHighlightNotMatching)

            self.addCheckNode(tv, rg,
                              _('Stuck notification'),
                              self.menubar.tkopt.stuck_notification,
                              self.menubar.mOptEnableStuckNotification)

            # submenu.add_separator()

            self.addCheckNode(tv, rg,
                              _('Show removed tiles (in Mahjongg games)'),
                              self.menubar.tkopt.mahjongg_show_removed,
                              self.menubar.mOptMahjonggShowRemoved)

            self.addCheckNode(tv, rg,
                              _('Show hint arrow (in Shisen-Sho games)'),
                              self.menubar.tkopt.shisen_show_hint,
                              self.menubar.mOptShisenShowHint)

            self.addCheckNode(tv, rg,
                              _('Deal all cards (in Accordion type games)'),
                              self.menubar.tkopt.accordion_deal_all,
                              self.menubar.mOptAccordionDealAll)

            self.addCheckNode(tv, rg,
                              _('Auto-remove first card (in Pegged games)'),
                              self.menubar.tkopt.accordion_deal_all,
                              self.menubar.mOptPeggedAutoRemove)

            # submenu.add_separator()

        yield
        # -------------------------------------------
        # Language options

        rg = tv.add_node(
            LTreeNode(text=_('Language')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('Default'),
                              self.menubar.tkopt.language, '',
                              self.menubar.mOptLanguage)
            self.addRadioNode(tv, rg,
                              _('English'),
                              self.menubar.tkopt.language, 'en',
                              self.menubar.mOptLanguage)
            self.addRadioNode(tv, rg,
                              _('German'),
                              self.menubar.tkopt.language, 'de',
                              self.menubar.mOptLanguage)
            self.addRadioNode(tv, rg,
                              _('Italian'),
                              self.menubar.tkopt.language, 'it',
                              self.menubar.mOptLanguage)
            self.addRadioNode(tv, rg,
                              _('Polish'),
                              self.menubar.tkopt.language, 'pl',
                              self.menubar.mOptLanguage)
            self.addRadioNode(tv, rg,
                              _('Russian'),
                              self.menubar.tkopt.language, 'ru',
                              self.menubar.mOptLanguage)

        yield
        # -------------------------------------------
        # Sound options

        rg = tv.add_node(
            LTreeNode(text=_('Sound')))
        if rg:
            self.addCheckNode(tv, rg,
                              _('Enable'),
                              self.menubar.tkopt.sound, None)

            rg1 = tv.add_node(
                LTreeNode(text=_('Volume')), rg)
            if rg1:
                self.addRadioNode(tv, rg1,
                                  _('100%'),
                                  self.menubar.tkopt.sound_sample_volume, 100,
                                  None)
                self.addRadioNode(tv, rg1,
                                  _('75%'),
                                  self.menubar.tkopt.sound_sample_volume, 75,
                                  None)
                self.addRadioNode(tv, rg1,
                                  _('50%'),
                                  self.menubar.tkopt.sound_sample_volume, 50,
                                  None)
                self.addRadioNode(tv, rg1,
                                  _('25%'),
                                  self.menubar.tkopt.sound_sample_volume, 25,
                                  None)

            rg1 = tv.add_node(
                LTreeNode(text=_('Samples')), rg)
            if rg1:
                key = 'areyousure'
                self.addCheckNode(
                    tv, rg1,
                    _('are you sure'),
                    self.menubar.tkopt.sound_areyousure, None)
                key = 'autodrop'
                self.addCheckNode(
                    tv, rg1,
                    _('auto drop'),
                    self.menubar.tkopt.sound_autodrop, None)
                key = 'autoflip'
                self.addCheckNode(
                    tv, rg1,
                    _('auto flip'),
                    self.menubar.tkopt.sound_autoflip, None)
                key = 'autopilotlost'
                self.addCheckNode(
                    tv, rg1,
                    _('auto pilot lost'),
                    self.menubar.tkopt.sound_autopilotlost, None)
                key = 'autopilotwon'
                self.addCheckNode(
                    tv, rg1,
                    _('auto pilot won'),
                    self.menubar.tkopt.sound_autopilotwon, None)
                key = 'deal'
                self.addCheckNode(
                    tv, rg1,
                    _('deal'),
                    self.menubar.tkopt.sound_deal, None)
                key = 'dealwaste'
                self.addCheckNode(
                    tv, rg1,
                    _('deal waste'),
                    self.menubar.tkopt.sound_dealwaste, None)
                key = 'droppair'
                self.addCheckNode(
                    tv, rg1,
                    _('drop pair'),
                    self.menubar.tkopt.sound_droppair, None)
                key = 'drop'
                self.addCheckNode(
                    tv, rg1,
                    _('drop'),
                    self.menubar.tkopt.sound_drop, None)
                key = 'flip'
                self.addCheckNode(
                    tv, rg1,
                    _('flip'),
                    self.menubar.tkopt.sound_flip, None)
                key = 'move'
                self.addCheckNode(
                    tv, rg1,
                    _('move'),
                    self.menubar.tkopt.sound_move, None)
                key = 'nomove'
                self.addCheckNode(
                    tv, rg1,
                    _('no move'),
                    self.menubar.tkopt.sound_nomove, None)
                key = 'redo'
                self.addCheckNode(
                    tv, rg1,
                    _('redo'),
                    self.menubar.tkopt.sound_redo, None)
                key = 'startdrag'
                self.addCheckNode(
                    tv, rg1,
                    _('start drag'),
                    self.menubar.tkopt.sound_startdrag, None)
                key = 'turnwaste'
                self.addCheckNode(
                    tv, rg1,
                    _('turn waste'),
                    self.menubar.tkopt.sound_turnwaste, None)
                key = 'undo'
                self.addCheckNode(
                    tv, rg1,
                    _('undo'),
                    self.menubar.tkopt.sound_undo, None)
                key = 'gamefinished'
                self.addCheckNode(
                    tv, rg1,
                    _('game finished'),
                    self.menubar.tkopt.sound_gamefinished, None)
                key = 'gamelost'
                self.addCheckNode(
                    tv, rg1,
                    _('game lost'),
                    self.menubar.tkopt.sound_gamelost, None)
                key = 'gameperfect'
                self.addCheckNode(
                    tv, rg1,
                    _('game perfect'),
                    self.menubar.tkopt.sound_gameperfect, None)
                key = 'gamewon'
                self.addCheckNode(
                    tv, rg1,
                    _('game won'),
                    self.menubar.tkopt.sound_gamewon, None)
                key = 'extra'
                self.addCheckNode(
                    tv, rg1,
                    _('Other'),
                    self.menubar.tkopt.sound_extra, None)

        yield
        # -------------------------------------------
        # Cardsets and card backside options

        from pysollib.resource import CSI

        rg = tv.add_node(
            LTreeNode(text=_('Cardsets')))
        if rg:
            self.menubar.tkopt.cardset.value = self.app.cardset.index

            csm = self.app.cardset_manager
            cdict = {}
            i = 0
            while 1:
                cardset = csm.get(i)
                if cardset is None: break  # noqa
                t = cardset.type
                if t not in cdict.keys(): cdict[t] = []  # noqa
                cdict[t].append((i, cardset))
                i += 1

            for k in sorted(cdict.keys()):
                name = CSI.TYPE_NAME[k]
                csl = cdict[k]
                rg1 = tv.add_node(LTreeNode(text=name), rg)

                for cst in csl:
                    i = cst[0]
                    cs = cst[1]
                    rg2 = self.addRadioNode(
                        tv,rg1,cs.name,self.menubar.tkopt.cardset, # noqa
                        i,self.menubar.mOptCardset)                # noqa

                    if rg2:
                        cbs = cs.backnames
                        self.menubar.tkopt.cardbacks[i] = LNumWrap(None)
                        self.menubar.tkopt.cardbacks[i].value = cs.backindex

                        bcnt = len(cbs)
                        bi = 0
                        while 1:
                            if bi == bcnt: break  # noqa
                            cb = cbs[bi]
                            self.addRadioNode(tv,rg2,cb,             # noqa
                                self.menubar.tkopt.cardbacks[i],bi,  # noqa
                                self.make_vars_command(              # noqa
                                    self.menubar.mOptSetCardback, i))
                            bi += 1
        yield
        # -------------------------------------------
        # Table background settings

        rg = tv.add_node(
            LTreeNode(text=_('Table')))
        if rg:
            rg1 = tv.add_node(
                LTreeNode(text=_('Solid colors')), rg)
            if rg1:
                key = 'table'
                self.addRadioNode(
                    tv, rg1,
                    _('Azure'),
                    self.menubar.tkopt.color_vars[key], '#0082df',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Black'),
                    self.menubar.tkopt.color_vars[key], '#000000',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Blue'),
                    self.menubar.tkopt.color_vars[key], '#0000ff',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Bright Green'),
                    self.menubar.tkopt.color_vars[key], '#00ff00',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Brown'),
                    self.menubar.tkopt.color_vars[key], '#684700',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Cyan'),
                    self.menubar.tkopt.color_vars[key], '#00ffff',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Grey'),
                    self.menubar.tkopt.color_vars[key], '#888888',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Green'),
                    self.menubar.tkopt.color_vars[key], '#008200',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Magenta'),
                    self.menubar.tkopt.color_vars[key], '#ff00ff',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Navy'),
                    self.menubar.tkopt.color_vars[key], '#000086',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Olive'),
                    self.menubar.tkopt.color_vars[key], '#868200',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Orange'),
                    self.menubar.tkopt.color_vars[key], '#f79600',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Pink'),
                    self.menubar.tkopt.color_vars[key], '#ff92fc',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Purple'),
                    self.menubar.tkopt.color_vars[key], '#8300ff',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Red'),
                    self.menubar.tkopt.color_vars[key], '#ff0000',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Teal'),
                    self.menubar.tkopt.color_vars[key], '#008286',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('White'),
                    self.menubar.tkopt.color_vars[key], '#ffffff',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Yellow'),
                    self.menubar.tkopt.color_vars[key], '#ffff00',
                    self.menubar.mOptTableColor)

            rg1 = tv.add_node(
                LTreeNode(text=_('Tiles')), rg)
            rg2 = tv.add_node(
                LTreeNode(text=_('Images')), rg)

            if rg1 or rg2:
                tm = self.app.tabletile_manager
                # cnt = tm.len()
                i = 1
                while True:
                    ti = tm.get(i)

                    if ti is None:
                        break
                    if ti.save_aspect == 0 and ti.stretch == 0 and rg1:
                        self.addRadioNode(tv, rg1,
                                          ti.name,
                                          self.menubar.tkopt.tabletile, i,
                                          self.menubar.mOptTileSet)
                    if (ti.save_aspect == 1 or ti.stretch == 1) and rg2:
                        self.addRadioNode(tv, rg2,
                                          ti.name,
                                          self.menubar.tkopt.tabletile, i,
                                          self.menubar.mOptTileSet)
                    i += 1

        yield
        # -------------------------------------------
        # Card view options

        rg = tv.add_node(
            LTreeNode(text=_('Card view')))
        if rg:
            self.addCheckNode(tv, rg,
                              _('Card shadow'),
                              self.menubar.tkopt.shadow,
                              self.menubar.mOptShadow)

            self.addCheckNode(tv, rg,
                              _('Shade legal moves'),
                              self.menubar.tkopt.shade,
                              self.menubar.mOptShade)

            self.addCheckNode(tv, rg,
                              _('Negative cards bottom'),
                              self.menubar.tkopt.negative_bottom,
                              self.menubar.mOptNegativeBottom)

            self.addCheckNode(tv, rg,
                              _('Shrink face-down cards'),
                              self.menubar.tkopt.shrink_face_down,
                              self.menubar.mOptShrinkFaceDown)

            self.addCheckNode(tv, rg,
                              _('Shade filled stacks'),
                              self.menubar.tkopt.shade_filled_stacks,
                              self.menubar.mOptShadeFilledStacks)

        yield
        # -------------------------------------------
        # Animation settins

        rg = tv.add_node(
            LTreeNode(text=_('Animations')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('None'),
                              self.menubar.tkopt.animations, 0,
                              self.menubar.mOptAnimations)

            self.addRadioNode(tv, rg,
                              _('Very fast'),
                              self.menubar.tkopt.animations, 1,
                              self.menubar.mOptAnimations)

            self.addRadioNode(tv, rg,
                              _('Fast'),
                              self.menubar.tkopt.animations, 2,
                              self.menubar.mOptAnimations)

            self.addRadioNode(tv, rg,
                              _('Medium'),
                              self.menubar.tkopt.animations, 3,
                              self.menubar.mOptAnimations)

            self.addRadioNode(tv, rg,
                              _('Slow'),
                              self.menubar.tkopt.animations, 4,
                              self.menubar.mOptAnimations)

            self.addRadioNode(tv, rg,
                              _('Very slow'),
                              self.menubar.tkopt.animations, 5,
                              self.menubar.mOptAnimations)

            # NOTE: All the following animation features only work on the
            # desktop and only if pillow is installed. So its useless to
            # present them here.
            '''
            self.addCheckNode(tv, rg,
                              _('Redeal animation'),
                              self.menubar.tkopt.redeal_animation,
                              self.menubar.mRedealAnimation)
            self.addCheckNode(tv, rg,
                              _('Winning animation'),
                              self.menubar.tkopt.win_animation,
                              self.menubar.mWinAnimation)
            self.addCheckNode(tv, rg,
                              _('Flip animation'),
                              self.menubar.tkopt.flip_animation,
                              None)
            '''

        yield
        # -------------------------------------------
        # Touch mode settings

        rg = tv.add_node(
            LTreeNode(text=_('Touch mode')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('Drag-and-Drop'),
                              self.menubar.tkopt.mouse_type, 'drag-n-drop',
                              None)

            self.addRadioNode(tv, rg,
                              _('Point-and-Click'),
                              self.menubar.tkopt.mouse_type, 'point-n-click',
                              None)

            # sinnlos mit touch-device:
            # self.addRadioNode(tv, rg,
            #   'Sticky mouse',
            #   self.menubar.tkopt.mouse_type, u'sticky-mouse',
            #   self.menubar.mOptMouseType)

            # submenu.add_separator()

            # sinnlos mit touch-device:
            # self.addCheckNode(tv, rg,
            #   'Use mouse for undo/redo',
            #   self.menubar.tkopt.mouse_undo,
            #   self.menubar.mOptMouseUndo)

        # submenu.add_separator()

        # -------------------------------------------
        # TBD ?

        '''
        menu.add_command(label=n_("&Fonts..."), command=self.mOptFonts)
        menu.add_command(label=n_("&Colors..."), command=self.mOptColors)
        menu.add_command(label=n_("Time&outs..."), command=self.mOptTimeouts)
        menu.add_separator()
        '''

        yield
        # -------------------------------------------
        # Toolbar options

        rg = tv.add_node(
            LTreeNode(text=_('Toolbar')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('Hide'),
                              self.menubar.tkopt.toolbar, 0,
                              self.menubar.setToolbarPos)

            self.addRadioNode(tv, rg,
                              _('Top'),
                              self.menubar.tkopt.toolbar, 1,
                              self.menubar.setToolbarPos)
            self.addRadioNode(tv, rg,
                              _('Bottom'),
                              self.menubar.tkopt.toolbar, 2,
                              self.menubar.setToolbarPos)
            self.addRadioNode(tv, rg,
                              _('Left'),
                              self.menubar.tkopt.toolbar, 3,
                              self.menubar.setToolbarPos)
            self.addRadioNode(tv, rg,
                              _('Right'),
                              self.menubar.tkopt.toolbar, 4,
                              self.menubar.setToolbarPos)

            rg1 = tv.add_node(
                LTreeNode(text=_('Visible buttons')), rg)
            if rg1:
                for w in TOOLBAR_BUTTONS:
                    w0 = w[0].upper()
                    ww = w[1:]
                    self.addCheckNode(tv, rg1,
                        _(w0+ww),  # noqa
                        self.menubar.tkopt.toolbar_vars[w],
                        self.make_vars_command(self.menubar.mOptToolbarConfig, w))  # noqa

        # -------------------------------------------
        # Statusbar - not implemented

        '''
        submenu = MfxMenu(menu, label=n_("Stat&usbar"))
        submenu.add_checkbutton(
             label=n_("Show &statusbar"),
             variable=self.tkopt.statusbar,
             command=self.mOptStatusbar)
        submenu.add_checkbutton(
            label=n_("Show &number of cards"),
            variable=self.tkopt.num_cards,
            command=self.mOptNumCards)
        submenu.add_checkbutton(
            label=n_("Show &help bar"),
            variable=self.tkopt.helpbar,
            command=self.mOptHelpbar)
        '''
        # -------------------------------------------
        # Other graphics settings

        rg = tv.add_node(
            LTreeNode(text=_('Other graphics')))
        data_dir = os.path.join(self.app.dataloader.dir, 'images', 'demo')
        dl = tv.add_node(
            LTreeNode(text=_('Demo logo')), rg)
        styledirs = os.listdir(data_dir)
        styledirs.append("none")
        styledirs.sort()
        for f in styledirs:
            d = os.path.join(data_dir, f)
            if (os.path.isdir(d) and os.path.exists(os.path.join(d))) \
                    or f == "none":
                name = f.replace('_', ' ').capitalize()
                self.addRadioNode(tv, dl,
                                  _(name),
                                  self.menubar.tkopt.demo_logo_style, f,
                                  self.menubar.mOptDemoLogoStyle)

        data_dir = os.path.join(self.app.dataloader.dir, 'images', 'pause')
        dl = tv.add_node(
            LTreeNode(text=_('Pause text')), rg)
        styledirs = os.listdir(data_dir)
        styledirs.sort()
        for f in styledirs:
            d = os.path.join(data_dir, f)
            if os.path.isdir(d) and os.path.exists(os.path.join(d)):
                name = f.replace('_', ' ').capitalize()
                self.addRadioNode(tv, dl,
                                  _(name),
                                  self.menubar.tkopt.pause_text_style, f,
                                  self.menubar.mOptPauseTextStyle)

        data_dir = os.path.join(self.app.dataloader.dir, 'images',
                                'redealicons')
        dl = tv.add_node(
            LTreeNode(text=_('Redeal icons')), rg)
        styledirs = os.listdir(data_dir)
        styledirs.sort()
        for f in styledirs:
            d = os.path.join(data_dir, f)
            if os.path.isdir(d) and os.path.exists(os.path.join(d)):
                name = f.replace('_', ' ').capitalize()
                self.addRadioNode(tv, dl,
                                  _(name),
                                  self.menubar.tkopt.redeal_icon_style, f,
                                  self.menubar.mOptRedealIconStyle)

        # -------------------------------------------
        # general options

        rg = tv.add_node(
            LTreeNode(text=_('Font size')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('default'),
                              self.menubar.tkopt.fontscale, 'default',
                              None)
            self.addRadioNode(tv, rg,
                              _('tiny'),
                              self.menubar.tkopt.fontscale, 'tiny',
                              None)
            self.addRadioNode(tv, rg,
                              _('small'),
                              self.menubar.tkopt.fontscale, 'small',
                              None)
            self.addRadioNode(tv, rg,
                              _('normal'),
                              self.menubar.tkopt.fontscale, 'normal',
                              None)
            self.addRadioNode(tv, rg,
                              _('large'),
                              self.menubar.tkopt.fontscale, 'large',
                              None)
            self.addRadioNode(tv, rg,
                              _('huge'),
                              self.menubar.tkopt.fontscale, 'huge',
                              None)
            '''
            self.addSliderNode(tv, rg, self.menubar.tkopt.fontsizefactor,
                               (0.7, 2.0, 0.1))
            '''

        # self.addCheckNode(tv, None,
        #   'Save games geometry',
        #   self.menubar.tkopt.save_games_geometry,
        #   self.menubar.mOptSaveGamesGeometry)

        # self.addCheckNode(tv, None,
        #   'Demo logo',
        #   self.menubar.tkopt.demo_logo,
        #   self.menubar.mOptDemoLogo)

        self.addCheckNode(tv, None,
                          _('Startup splash screen'),
                          self.menubar.tkopt.splashscreen,
                          None)

        self.addCheckNode(tv, None,
                          _('Winning splash'),
                          self.menubar.tkopt.display_win_message,
                          None)

# ************************************************************************


class OptionsMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['persist'] = True
        super(OptionsMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def initTree(self):
        og = LOptionsMenuGenerator(
            self.menubar, self.parent, title=_("Options"), app=self.app)
        tv = og.generate()
        return tv

# ************************************************************************


class HelpMenuDialog(LMenuDialog):
    def __init__(self, menubar, parent, title, app, **kw):
        kw['persist'] = True
        super(HelpMenuDialog, self).__init__(menubar, parent, title, app, **kw)

    def buildTree(self, tv, node):
        tv.add_node(
            LTreeNode(
                text=_('Contents'),
                command=self.auto_close(self.menubar.mHelp)))
        tv.add_node(
            LTreeNode(
                text=_('How to use PySol'),
                command=self.auto_close(self.menubar.mHelpHowToPlay)))
        tv.add_node(
            LTreeNode(
                text=_('Rules for this game'),
                command=self.auto_close(self.menubar.mHelpRules)))
        tv.add_node(
            LTreeNode(
                text=_('License terms'),
                command=self.auto_close(self.menubar.mHelpLicense)))
        tv.add_node(
            LTreeNode(
                text=_('About %s...') % TITLE,
                command=self.auto_close(self.menubar.mHelpAbout)))

        # tv.add_node(LTreeNode(
        #   text='AboutKivy ...',
        #   command=self.makeHtmlCommand(self.menubar, "kivy.html")))
    '''
    def makeHtmlCommand(self, bar, htmlfile):
        def htmlCommand():
            bar.mHelpHtml(htmlfile)
        return htmlCommand
    '''

# ************************************************************************
# *
# ************************************************************************


class EmulTkMenu(object):

    def __init__(self, master, **kw):

        self.name = kw["name"]
        self.n = 0
        self._w = None
        if (self.name):
            if master._w == '.':
                self._w = '.' + self.name
            else:
                self._w = master._w + '.' + self.name
        else:
            self.name = "<>"

    def labeltoname(self, label):
        name = re.sub(r"[^0-9a-zA-Z]", "", label).lower()
        label = _(label)
        underline = label.find('&')
        if underline >= 0:
            label = label.replace('&', '')
        return name, label, underline

    def add_cascade(self, cnf={}, **kw):
        self.add('cascade', cnf or kw)
        pass

    def add(self, itemType, cnf={}):
        label = cnf.get("label")
        if label:
            name = cnf.get('name')
            if name:
                name, label, underline = self.labeltoname(label)
                cnf["underline"] = cnf.get("underline", underline)
                cnf["label"] = label
                if name and self.addPath:
                    path = str(self._w) + "." + name
                    self.addPath(path, self, self.n, cnf.get("menu"))

    def cget(self, key):
        return key

# ************************************************************************


class MfxMenubar(EmulTkMenu):
    addPath = None

    def __init__(self, master, **kw):
        super(MfxMenubar, self).__init__(master, **kw)
        topmenu = self.name == 'menubar'

        self.menu = LMenu(not topmenu, text=self.name)
        if topmenu:
            master.setMenu(self.menu)

# ************************************************************************
# * - create menubar
# * - update menubar
# * - menu actions
# ************************************************************************


class DictObjMap(object):
    def __init__(self, val):
        self.__dict__ = val


class PysolMenubarTk:
    def __init__(self, app, top, progress=None):
        print('PysolMenubarTk: __init__()')
        self.top = top
        self.app = app

        self._createTkOpt()
        self._setOptions()

        self.__cb_max = 8
        self.progress = progress

        # create menus
        self.__menubar = None
        self.__menupath = {}
        self.__keybindings = {}
        self._createMenubar()

        if self.progress:
            self.progress.update(step=1)

    def unlockScreenRotation(self, obj, val):
        AndroidScreenRotation.unlock(toaster=False)
        print('unlock screen rotation')

    def setFontScale(self, obj, val):
        from kivy.metrics import Metrics
        vals = {
            'tiny':   0.833,
            'small':  1.0,
            'normal': 1.2,
            'large':  1.44,
            'huge':   1.728
        }
        if val == 'default':
            Metrics.reset_metrics()
        else:
            Metrics.fontscale = vals[val]
    '''
    def setFontSize(self, obj, val):
        from kivy.metrics import Metrics
        Metrics.fontscale = val
    '''

    def _createTkOpt(self):
        opt = self.app.opt

        # fake options
        self.tabletile_index = self.app.tabletile_index
        self.cardback = self.app.cardset.backindex
        self.cardset = self.app.cardset_manager.getSelected()
        self.pause = False
        if self.game:
            self.pause = self.game.pause
        self.gameid = 0
        self.gameid_popular = 0

        # map dicts to Obj
        self.sound_samples = DictObjMap(opt.sound_samples)
        self.tbv = DictObjMap(opt.toolbar_vars)
        self.cvo = DictObjMap(opt.colors)

        # option mappings.
        self.tkopt = Struct(
            # automation
            autofaceup=LBoolWrap(opt, "autofaceup"),
            autodrop=LBoolWrap(opt, "autodrop"),
            autodeal=LBoolWrap(opt, "autodeal"),
            quickplay=LBoolWrap(opt, "quickplay"),
            # support
            undo=LBoolWrap(opt, "undo"),
            hint=LBoolWrap(opt, "hint"),
            free_hint=LBoolWrap(opt, "free_hint"),
            shuffle=LBoolWrap(opt, "shuffle"),
            bookmarks=LBoolWrap(opt, "bookmarks"),
            highlight_piles=LBoolWrap(opt, "highlight_piles"),
            highlight_cards=LBoolWrap(opt, "highlight_cards"),
            highlight_samerank=LBoolWrap(opt, "highlight_samerank"),
            peek_facedown=LBoolWrap(opt, "peek_facedown"),
            highlight_not_matching=LBoolWrap(opt, "highlight_not_matching"),
            stuck_notification=LBoolWrap(opt, "stuck_notification"),
            mahjongg_show_removed=LBoolWrap(opt, "mahjongg_show_removed"),
            shisen_show_hint=LBoolWrap(opt, "shisen_show_hint"),
            accordion_deal_all=LBoolWrap(opt, "accordion_deal_all"),
            pegged_auto_remove=LBoolWrap(opt, "pegged_auto_remove"),
            # sound
            sound=LBoolWrap(opt, "sound"),
            sound_sample_volume=LNumWrap(opt, "sound_sample_volume"),
            sound_music_volume=LNumWrap(opt, "sound_music_volume"),
            # sound samples
            sound_areyousure=LBoolWrap(self.sound_samples, 'areyousure'),
            sound_autodrop=LBoolWrap(self.sound_samples, 'autodrop'),
            sound_autoflip=LBoolWrap(self.sound_samples, 'autoflip'),
            sound_autopilotlost=LBoolWrap(self.sound_samples, 'autopilotlost'),
            sound_autopilotwon=LBoolWrap(self.sound_samples, 'autopilotwon'),
            sound_deal=LBoolWrap(self.sound_samples, 'deal'),
            sound_dealwaste=LBoolWrap(self.sound_samples, 'dealwaste'),
            sound_droppair=LBoolWrap(self.sound_samples, 'droppair'),
            sound_drop=LBoolWrap(self.sound_samples, 'drop'),
            sound_extra=LBoolWrap(self.sound_samples, 'extra'),
            sound_flip=LBoolWrap(self.sound_samples, 'flip'),
            sound_move=LBoolWrap(self.sound_samples, 'move'),
            sound_nomove=LBoolWrap(self.sound_samples, 'nomove'),
            sound_redo=LBoolWrap(self.sound_samples, 'redo'),
            sound_startdrag=LBoolWrap(self.sound_samples, 'startdrag'),
            sound_turnwaste=LBoolWrap(self.sound_samples, 'turnwaste'),
            sound_undo=LBoolWrap(self.sound_samples, 'undo'),
            sound_gamefinished=LBoolWrap(self.sound_samples, 'gamefinished'),
            sound_gamelost=LBoolWrap(self.sound_samples, 'gamelost'),
            sound_gameperfect=LBoolWrap(self.sound_samples, 'gameperfect'),
            sound_gamewon=LBoolWrap(self.sound_samples, 'gamewon'),
            # animation
            animations=LNumWrap(opt, "animations"),
            redeal_animation=LBoolWrap(opt, "redeal_animation"),
            win_animation=LBoolWrap(opt, "win_animation"),
            flip_animation=LBoolWrap(opt, "flip_animation"),
            # toolbar
            toolbar=LNumWrap(opt, "toolbar"),
            toolbar_land=LNumWrap(opt, "toolbar_land", self.mOptToolbar),
            toolbar_port=LNumWrap(opt, "toolbar_port", self.mOptToolbar),
            toolbar_style=LStringWrap(opt, "toolbar_style"),
            toolbar_relief=LStringWrap(opt, "toolbar_relief"),
            toolbar_compound=LStringWrap(opt, "toolbar_compound"),
            toolbar_size=LNumWrap(opt, "toolbar_size"),
            toolbar_vars={},
            # card dsiplay and text style settings
            demo_logo=LBoolWrap(opt, "demo_logo"),
            demo_logo_style=LStringWrap(opt, "demo_logo_style"),
            pause_text_style=LStringWrap(opt, "pause_text_style"),
            redeal_icon_style=LStringWrap(opt, "redeal_icon_style"),
            mouse_type=LStringWrap(opt, "mouse_type"),
            mouse_undo=LBoolWrap(opt, "mouse_undo"),
            shade_filled_stacks=LBoolWrap(opt, "shade_filled_stacks"),
            shrink_face_down=LBoolWrap(opt, "shrink_face_down"),
            negative_bottom=LBoolWrap(opt, "negative_bottom"),
            shadow=LBoolWrap(opt, "shadow"),
            shade=LBoolWrap(opt, "shade"),
            # colors
            color_vars={},
            tabletile=LNumWrap(self, "tabletile_index"),
            # other
            splashscreen=LBoolWrap(opt, "splashscreen"),
            display_win_message=LBoolWrap(opt, "display_win_message"),
            language=LStringWrap(opt, "language"),
            save_games_geometry=LBoolWrap(opt, "save_games_geometry"),
            pause=LBoolWrap(self, "pause"),
            table_zoom=LListWrap(opt, "table_zoom"),
            fontscale=LStringWrap(opt, "fontscale", self.setFontScale),
            # fontsizefactor=LNumWrap(opt, "fontsizefactor", self.setFontSize),
            # cards
            cardset=LNumWrap(self, "cardset"),
            cardback=LNumWrap(self, "cardback"),
            cardbacks={},
            # statusbar (not implemented)
            statusbar=LBoolWrap(opt, "statusbar"),
            # num_cards=BooleanVar(),
            # helpbar=BooleanVar(),
            # game
            gameid=LNumWrap(self, "gameid", self.unlockScreenRotation),
            gameid_popular=LNumWrap(self, "gameid_popular"),
        )
        for w in TOOLBAR_BUTTONS:
            self.tkopt.toolbar_vars[w] = LBoolWrap(self.tbv, w)
        for k in self.app.opt.colors:
            self.tkopt.color_vars[k] = LStringWrap(self.cvo, k)

    def _setOptions(self):
        self.tkopt.save_games_geometry.value = False
        self.getToolbarPos(None, Window.size)
        self.setFontScale(None, self.tkopt.fontscale.value)
        # self.setFontSize(None, self.tkopt.fontsizefactor.value)
        Window.bind(size=self.getToolbarPos)

    def getToolbarPos(self, obj, size):
        if (size[0] > size[1]):
            self.tkopt.toolbar.value = self.tkopt.toolbar_land.value
        else:
            self.tkopt.toolbar.value = self.tkopt.toolbar_port.value

    def setToolbarPos(self, *args):
        if (Window.size[0] > Window.size[1]):
            self.tkopt.toolbar_land.value = self.tkopt.toolbar.value
        else:
            self.tkopt.toolbar_port.value = self.tkopt.toolbar.value

    def connectGame(self, game):
        self.game = game
        if game is None:
            return
        assert self.app is game.app
        tkopt = self.tkopt
        # opt = self.app.opt
        tkopt.gameid.value = game.id
        tkopt.gameid_popular.value = game.id
        tkopt.pause.value = self.game.pause
        if game.canFindCard():
            connect_game_find_card_dialog(game)
        else:
            destroy_find_card_dialog()
        if game.canShowFullPicture():
            connect_game_full_picture_dialog(game)
        else:
            destroy_full_picture_dialog()
        connect_game_solver_dialog(game)

    # create a GTK-like path
    def _addPath(self, path, menu, index, submenu):
        # print ('MfxMenubar: _addPath %s, %s' % (path, menu))
        # y = self.yy
        if path not in self.__menupath:
            # print path, menu, index, submenu
            self.__menupath[path] = (menu, index, submenu)

    def _getEnabledState(self, enabled):
        print('_getEnabledState: %s' % enabled)
        if enabled:
            return "normal"
        return "disabled"

    def updateProgress(self):
        if self.progress:
            self.progress.update(step=1)

    #
    # create the menubar
    #

    def _createMenubar(self):
        MfxMenubar.addPath = self._addPath
        kw = {"name": "menubar"}
        self.__menubar = MfxMenubar(self.top, **kw)

        # init keybindings
        bind(self.top, "<KeyPress>", self._keyPressHandler)

        # LMainMenuDialog()
        LMenuItem(self.__menubar.menu,
                  text=_("Menu"), command=self.mMainMenuDialog)

        MfxMenubar.addPath = None

    #
    # key binding utility
    #

    def _bindKey(self, modifier, key, func):
        #         if 0 and not modifier and len(key) == 1:
        #             self.__keybindings[key.lower()] = func
        #             self.__keybindings[key.upper()] = func
        #             return
        if not modifier and len(key) == 1:
            # ignore Ctrl/Shift/Alt
            # but don't ignore NumLock (state == 16)
            def lfunc(e, func=func):
                return e.state in (0, 16) and func(e)
            func = lfunc
            # func = lambda e, func=func: e.state in (0, 16) and func(e)
        sequence = "<" + modifier + "KeyPress-" + key + ">"
        bind(self.top, sequence, func)
        if len(key) == 1 and key != key.upper():
            key = key.upper()
            sequence = "<" + modifier + "KeyPress-" + key + ">"
            bind(self.top, sequence, func)

    def _keyPressHandler(self, event):
        r = EVENT_PROPAGATE
        if event and self.game:
            # print event.__dict__
            if self.game.demo:
                # stop the demo by setting self.game.demo.keypress
                if event.char:    # ignore Ctrl/Shift/etc.
                    self.game.demo.keypress = event.char
                    r = EVENT_HANDLED
#             func = self.__keybindings.get(event.char)
#             if func and (event.state & ~2) == 0:
#                 func(event)
#                 r = EVENT_HANDLED
        return r

    #
    # Select Game menu creation
    #
    '''
    def _addSelectGameMenu(self, menu):
        games = map(self.app.gdb.get, self.app.gdb.getGamesIdSortedByName())
        m = "Ctrl-"
        if sys.platform == "darwin":
            m = "Cmd-"
        menu.add_command(label=n_("All &games..."), accelerator=m + "W",
                         command=self.mSelectGameDialog)

    def _addSelectGameSubMenu(self, games, menu, select_data,
                              command, variable):
        # print select_data
        need_sep = 0
        for label, select_func in select_data:
            if label is None:
                need_sep = 1
                continue
            g = filter(select_func, games)
            if not g:
                continue
            if need_sep:
                menu.add_separator()
                need_sep = 0
            submenu = MfxMenu(menu, label=label)
            self._addSelectGameSubSubMenu(g, submenu, command, variable)

    def _getNumGames(self, games, select_data):
        ngames = 0
        for label, select_func in select_data:
            ngames += len(filter(select_func, games))
        return ngames

    def _addSelectMahjonggGameSubMenu(self, games, menu, command, variable):
        def select_func(gi): return gi.si.game_type == GI.GT_MAHJONGG
        mahjongg_games = filter(select_func, games)
        if len(mahjongg_games) == 0:
            return
        #
        menu = MfxMenu(menu, label=n_("&Mahjongg games"))

        def add_menu(games, c0, c1, menu=menu,
                     variable=variable, command=command):
            if not games:
                return
            label = c0 + ' - ' + c1
            if c0 == c1:
                label = c0
            submenu = MfxMenu(menu, label=label, name=None)
            self._addSelectGameSubSubMenu(games, submenu, command,
                                          variable, short_name=True)

        games = {}
        for gi in mahjongg_games:
            c = gi.short_name.strip()[0]
            if c in games:
                games[c].append(gi)
            else:
                games[c] = [gi]
        games = games.items()
        games.sort()
        g0 = []
        c0 = c1 = games[0][0]
        for c, g1 in games:
            if len(g0) + len(g1) >= self.__cb_max:
                add_menu(g0, c0, c1)
                g0 = g1
                c0 = c1 = c
            else:
                g0 += g1
                c1 = c
        add_menu(g0, c0, c1)

    def _addSelectPopularGameSubMenu(self, games, menu, command, variable):
        def select_func(gi): return gi.si.game_flags & GI.GT_POPULAR
        if len(filter(select_func, games)) == 0:
            return
        data = (n_("&Popular games"), select_func)
        self._addSelectGameSubMenu(games, menu, (data, ),
                                   self.mSelectGamePopular,
                                   self.tkopt.gameid_popular)

    def _addSelectFrenchGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&French games"))
        self._addSelectGameSubMenu(games, submenu, GI.SELECT_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectOrientalGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_ORIENTAL_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&Oriental games"))
        self._addSelectGameSubMenu(games, submenu,
                                   GI.SELECT_ORIENTAL_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectSpecialGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_ORIENTAL_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&Special games"))
        self._addSelectGameSubMenu(games, submenu,
                                   GI.SELECT_SPECIAL_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectCustomGameSubMenu(self, games, menu, command, variable):
        submenu = MfxMenu(menu, label=n_("&Custom games"))

        def select_func(gi): return gi.si.game_type == GI.GT_CUSTOM
        games = filter(select_func, games)
        self.updateGamesMenu(submenu, games)
    '''

    def _addSelectAllGameSubMenu(self, games, menu, command, variable):
        # LB
        # herausgenommen: zu aufwendig !
        return
        '''
        menu = MfxMenu(menu, label=n_("&All games by name"))
        n, d = 0, self.__cb_max
        i = 0
        while True:
            if self.progress:
                self.progress.update(step=1)
            columnbreak = i > 0 and (i % d) == 0
            i += 1
            if not games[n:n + d]:
                break
            m = min(n + d - 1, len(games) - 1)
            label = games[n].name[:3] + ' - ' + games[m].name[:3]

            submenu = MfxMenu(menu, label=label, name=None)
            self._addSelectGameSubSubMenu(games[n:n + d], submenu,
                                          command, variable)
            n += d
            # if columnbreak:
            #    menu.entryconfigure(i, columnbreak=columnbreak)
        '''

    # Eine 'closure' in Python? - voila!
    def make_gamesetter(self, n, variable, command):
        def gamesetter(x):
            variable.value = n
            command()
        return gamesetter

    def _addSelectGameSubSubMenu(self, games, menu, command, variable,
                                 short_name=False):

        # cb = self.__cb_max
        for gi in games:
            # columnbreak = i > 0 and (i % cb) == 0
            if short_name:
                label = gi.short_name
            else:
                label = gi.name

            # optimized by inlining

            # geht nicht mehr 'optimiert' mit kivy
            # die Funktionalität des tk.calls kann mit hilfe
            # einer 'closure' rekonstruiert werden (s.o).
            # LB

            gsetter = self.make_gamesetter(gi.id, variable, command)
            menu.add_command(label=label, command=gsetter)

            # menu.tk.call((menu._w, 'add', 'radiobutton') +
            #             menu._options({'command': command,
            #                            'variable': variable,
            #                            'columnbreak': columnbreak,
            #                            'value': gi.id,
            #                            'label': label}))

    def updateGamesMenu(self, menu, games):

        def cmp2(a, b):
            """python 3 replacement for python 2 cmp function"""
            return (a > b) - (a < b)

        menu.delete(0, 'last')

        if len(games) == 0:
            menu.add_radiobutton(label=_('<none>'), name=None,
                                 state='disabled')
        elif len(games) > self.__cb_max * 4:
            games.sort(lambda a, b: cmp2(a.name, b.name))
            self._addSelectAllGameSubMenu(games, menu,
                                          command=self.mSelectGame,
                                          variable=self.tkopt.gameid)
        else:
            self._addSelectGameSubSubMenu(games, menu,
                                          command=self.mSelectGame,
                                          variable=self.tkopt.gameid)

    def mMainMenuDialog(self, *event):
        MainMenuDialog(self, self.top, title=_("Main Menu"), app=self.app)
        return EVENT_HANDLED

    def mFileMenuDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        FileMenuDialog(self, self.top, title=_("File Menu"), app=self.app)
        return EVENT_HANDLED

    def mEditMenuDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        EditMenuDialog(self, self.top, title=_("Tools"), app=self.app)
        return EVENT_HANDLED

    def mGameMenuDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        GameMenuDialog(self, self.top, title=_("Statistics"), app=self.app)
        return EVENT_HANDLED

    def mAssistMenuDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        AssistMenuDialog(self, self.top, title=_("Assists"), app=self.app)
        return EVENT_HANDLED

    def mOptionsMenuDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)

        OptionsMenuDialog(self, self.top, title=_("Options"), app=self.app)
        return EVENT_HANDLED

    def mHelpMenuDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        HelpMenuDialog(self, self.top, title=_("Help"), app=self.app)
        return EVENT_HANDLED
    #
    # Select Game menu actions
    #

    def mSelectGame(self, *args):
        print('mSelectGame %s' % self)
        self._mSelectGame(self.tkopt.gameid.value)

    def mSelectGamePopular(self, *args):
        self._mSelectGame(self.tkopt.gameid_popular.value)

    def _mSelectGameDialog(self, d):
        if d.gameid != self.game.id:
            self.tkopt.gameid.value = d.gameid
            self.tkopt.gameid_popular.value = d.gameid
            self._cancelDrag()
            self.game.endGame()
            self.game.quitGame(d.gameid, random=d.random)
        return EVENT_HANDLED

    def __restoreCursor(self, *event):
        self.game.setCursor(cursor=self.app.top_cursor)

    def mSelectGameDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        d = SelectGameDialog(self.top, title=_("Select game"),
                             app=self.app, gameid=self.game.id)
        return self._mSelectGameDialog(d)

    #
    # menubar overrides
    #

    def updateFavoriteGamesMenu(self):
        return

        # TBD ?
        '''
        gameids = self.app.opt.favorite_gameid

        print('favorite_gameids = %s' % gameids)

        submenu = self.__menupath[".menubar.file.favoritegames"][2]
        games = []
        for id in gameids:
            gi = self.app.getGameInfo(id)
            if gi:
                games.append(gi)
        self.updateGamesMenu(submenu, games)

        # das folgende ist nur das enable/disable des add/remove buttons.
        # geht mit kivy nicht so.

#        state = self._getEnabledState
#        in_favor = self.app.game.id in gameids

# menu, index, submenu = self.__menupath[".menubar.file.addtofavorites"]
# menu.entryconfig(index, state=state(not in_favor))

# menu, index, submenu = self.__menupath[".menubar.file.removefromfavorites"]
# menu.entryconfig(index, state=state(in_favor))
        '''

    def updateRecentGamesMenu(self, gameids):
        return

        # TBD ?
        '''
        submenu = self.__menupath[".menubar.file.recentgames"][2]
        games = []
        for id in gameids:
            gi = self.app.getGameInfo(id)
            if gi:
                games.append(gi)
        self.updateGamesMenu(submenu, games)
        '''

    def updateBookmarkMenuState(self):
        # LB:
        # print('updateBookmarkMenuState - fake')
        return

        state = self._getEnabledState
        mp1 = self.__menupath.get(".menubar.edit.setbookmark")
        mp2 = self.__menupath.get(".menubar.edit.gotobookmark")
        mp3 = self.__menupath.get(".menubar.edit.clearbookmarks")
        if mp1 is None or mp2 is None or mp3 is None:
            return
        x = self.app.opt.bookmarks and self.game.canSetBookmark()
        #
        menu, index, submenu = mp1
        for i in range(9):
            submenu.entryconfig(i, state=state(x))
        menu.entryconfig(index, state=state(x))
        #
        menu, index, submenu = mp2
        ms = 0
        for i in range(9):
            s = self.game.gsaveinfo.bookmarks.get(i) is not None
            submenu.entryconfig(i, state=state(s and x))
            ms = ms or s
        menu.entryconfig(index, state=state(ms and x))
        #
        menu, index, submenu = mp3
        menu.entryconfig(index, state=state(ms and x))

    def updateBackgroundImagesMenu(self):
        # LB:
        print('updateBackgroundImagesMenu - fake')
        return

        mp = self.__menupath.get(".menubar.options.cardbackground")
        # delete all entries
        submenu = mp[2]
        submenu.delete(0, "last")
        # insert new cardbacks
        mbacks = self.app.images.getCardbacks()
        cb = int(math.ceil(math.sqrt(len(mbacks))))
        for i in range(len(mbacks)):
            columnbreak = i > 0 and (i % cb) == 0
            submenu.add_radiobutton(
                    label=mbacks[i].name,
                    image=mbacks[i].menu_image,
                    variable=self.tkopt.cardback,
                    value=i,
                    command=self.mOptCardback,
                    columnbreak=columnbreak,
                    indicatoron=0,
                    hidemargin=0)
    #
    # menu updates
    #

    def setMenuState(self, state, path):
        # LB: not used
        return

    def setToolbarState(self, state, path):
        # LB: not used
        return

    def _setPauseMenu(self, v):
        self.tkopt.pause.value = v

    #
    # menu actions
    #

    DEFAULTEXTENSION = ".pso"
    # TRANSLATORS: Usually, 'PySol files'
    FILETYPES = ((_("%s files") % TITLE, "*" + DEFAULTEXTENSION),
                 (_("All files"), "*"))

    def mAddFavor(self, *event):
        gameid = self.app.game.id
        if gameid not in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.insert(0, gameid)
            self.updateFavoriteGamesMenu()

    def mDelFavor(self, *event):
        gameid = self.app.game.id
        if gameid in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.remove(gameid)
            self.updateFavoriteGamesMenu()

    def mOpen(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        # filename = self.game.filename
        filename = "lastgame.pso"
        if filename:
            idir, ifile = os.path.split(os.path.normpath(filename))
        else:
            idir, ifile = "", ""
        if not idir:
            idir = self.app.dn.savegames
#        d = tkinter.filedialog.Open()
#        filename = d.show(filetypes=self.FILETYPES,
#                          defaultextension=self.DEFAULTEXTENSION,
#                          initialdir=idir, initialfile=ifile)
        filename = idir + "/" + ifile

        print('filename = %s' % filename)
        if filename:
            filename = os.path.normpath(filename)
            if os.path.isfile(filename):
                baseWindow = Cache.get('LAppCache', 'baseWindow')
                text = _("loading game from:")+filename
                toast = Toast(text=text)
                toast.show(parent=baseWindow, duration=4.0)
                Clock.schedule_once(lambda dt: self.game.loadGame(filename), 1.0) # noqa

    def mSaveAs(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.menustate.save_as:
            return
        # filename = self.game.filename
        filename = "lastgame.pso"
        if not filename:
            filename = self.app.getGameSaveName(self.game.id)
            if os.name == "posix":
                filename = filename + "-" + self.game.getGameNumber(format=0)
            elif os.path.supports_unicode_filenames:  # new in python 2.3
                filename = filename + "-" + self.game.getGameNumber(format=0)
            else:
                filename = filename + "-01"
            filename = filename + self.DEFAULTEXTENSION
        idir, ifile = os.path.split(os.path.normpath(filename))
        if not idir:
            idir = self.app.dn.savegames

        filename = idir + "/" + ifile
        if filename:
            filename = os.path.normpath(filename)
            # filename = os.path.normcase(filename)
            if self.game.saveGame(filename):
                baseWindow = Cache.get('LAppCache', 'baseWindow')
                text = _("game saved to:")+filename
                toast = Toast(text=text)
                toast.show(parent=baseWindow, duration=5.0)
            self.updateMenus()

    def mResetZoom(self, *args):
        self.tkopt.table_zoom.value = [1.0, 0.0, 0.0]

    def mPause(self, *args):
        if not self.game:
            return
        if not self.game.pause:
            if self._cancelDrag():
                return
        self.game.doPause()
        self.tkopt.pause.value = self.game.pause

    def mOptLanguage(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        MfxMessageDialog(
           self.app.top, title=_("Note"),
           text=_("""\
These settings will take effect
the next time you restart the %(app)s""") % {'app': TITLE})

    def mAppSetTile(self, idx, force=False):
        self.app.setTile(idx, force=force)
        # setTile() may change option values (?):
        # app.opt.tabletile_scale_method:  not manaaged here -> o.k.
        # app.opt.tabletile_name:          not managed here -> o.k.
        # app.tabletile_index:             managed here, is set to idx, no change occurs.  # noqa
        # app.opt.colors['table']:         managed as color_vars, complex, (proved: no change)  # noqa
        # print('**********', self.app.opt.colors['table'])
        # print('**********', self.tkopt.color_vars['table'].value)

    def mOptTableColor(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.tkopt.tabletile.value = 0  # (0 denotes color instead of a tile)
        nv = self.tkopt.color_vars['table'].value
        self.app.top_bg = nv
        self.mAppSetTile(0, force=True)

    def mOptTileSet(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        idx = self.tkopt.tabletile.value
        if idx > 0 and idx != self.app.tabletile_index:
            self.mAppSetTile(idx)
            # set color out of known colors
            # (its to remove the check flag from the menu):
            self.tkopt.color_vars['table'].value = '#008285'

    def mOptAutoFaceUp(self, *args):
        if self._cancelDrag():
            return
        if self.app.opt.autofaceup:
            self.game.autoPlay()

    def mOptAutoDrop(self, *args):
        if self._cancelDrag():
            return
        if self.app.opt.autodrop:
            self.game.autoPlay()

    def mOptAutoDeal(self, *args):
        if self._cancelDrag():
            return
        if self.app.opt.autodeal:
            self.game.autoPlay()

    def mOptQuickPlay(self, *args):
        if self._cancelDrag(break_pause=False):
            return

    def mOptEnableUndo(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.updateMenus()

    def mOptEnableBookmarks(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.updateMenus()

    def mOptEnableHint(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.updateMenus()

    def mOptFreeHints(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.updateMenus()

    def mOptEnableShuffle(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.updateMenus()

    def mOptEnableHighlightPiles(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.updateMenus()

    def mOptEnableHighlightCards(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.updateMenus()

    def mOptEnableHighlightSameRank(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        # self.game.updateMenus()

    def mOptEnablePeekFacedown(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        # self.game.updateMenus()

    def mOptEnableHighlightNotMatching(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        # self.game.updateMenus()

    def mOptEnableStuckNotification(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        # self.game.updateMenus()

    def mOptAnimations(self, *args):
        if self._cancelDrag(break_pause=False):
            return

    def mRedealAnimation(self, *args):
        if self._cancelDrag(break_pause=False):
            return

    def mWinAnimation(self, *args):
        if self._cancelDrag(break_pause=False):
            return

    def mOptShadow(self, *args):
        if self._cancelDrag(break_pause=False):
            return

    def mOptShade(self, *args):
        if self._cancelDrag(break_pause=False):
            return

    def mOptShrinkFaceDown(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShadeFilledStacks(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptMahjonggShowRemoved(self, *args):
        if self._cancelDrag():
            return
        # self.game.updateMenus()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShisenShowHint(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        # self.game.updateMenus()

    def mOptAccordionDealAll(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        # self.game.updateMenus()

    def mOptPeggedAutoRemove(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        # self.game.updateMenus()

    def mOptCardset(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        idx = self.tkopt.cardset.value
        cs = self.app.cardset_manager.get(idx)
        if cs is None or idx == self.app.cardset.index:
            return
        if idx >= 0:
            self.app.nextgame.cardset = cs
            self._cancelDrag()
            self.game.endGame(bookmark=1)
            self.game.quitGame(bookmark=1)

    def mSelectCardsetDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        # strings, default = ("&OK", "&Load", "&Cancel"), 0
        strings, default = (None, _("&Load"), _("&Cancel"), ), 1
        # if os.name == "posix":
        strings, default = (None, _("&Load"), _(
            "&Cancel"), _("&Info..."), ), 1
        key = self.app.nextgame.cardset.index
        d = SelectCardsetDialogWithPreview(
                self.top, title=_("Select cardset"),
                app=self.app, manager=self.app.cardset_manager, key=key,
                strings=strings, default=default)

        cs = self.app.cardset_manager.get(d.key)
        if cs is None or d.key == self.app.cardset.index:
            return
        if d.status == 0 and d.button in (0, 1) and d.key >= 0:
            self.app.nextgame.cardset = cs
            if d.button == 1:
                self._cancelDrag()
                self.game.endGame(bookmark=1)
                self.game.quitGame(bookmark=1)

    def mOptSetCardback(self, key, *event):
        val = self.tkopt.cardbacks[key].value
        cs = self.app.cardset_manager.get(key)
        cs.updateCardback(backindex=val)
        # ANM: wir können den Background nur für das aktuell
        # selektierte Cardset wirklich ändern. Nur dieses wird
        # wird in den Optionen gespeichert.
        if (cs == self.app.cardset):
            self.app.updateCardset(self.game.id)
            self.app.cardset.backindex = val
            image = self.app.images.getBack(update=True)
            for card in self.game.cards:
                card.updateCardBackground(image=image)

    def _mOptCardback(self, index):
        if self._cancelDrag(break_pause=False):
            return
        cs = self.app.cardset
        old_index = cs.backindex
        cs.updateCardback(backindex=index)
        if cs.backindex == old_index:
            return
        self.app.updateCardset(self.game.id)
        image = self.app.images.getBack(update=True)
        for card in self.game.cards:
            card.updateCardBackground(image=image)
        self.tkopt.cardback.value = cs.backindex

    def mOptCardback(self, *event):
        self._mOptCardback(self.tkopt.cardback.value)

    def mOptChangeCardback(self, *event):
        self._mOptCardback(self.app.cardset.backindex + 1)

    def mOptToolbar(self, *event):
        self.app.toolbar.show()

    def mOptToolbarStyle(self, *event):
        self.setToolbarStyle(self.tkopt.toolbar_style.value)

    def mOptToolbarCompound(self, *event):
        self.setToolbarCompound(self.tkopt.toolbar_compound.value)

    def mOptToolbarSize(self, *event):
        self.setToolbarSize(self.tkopt.toolbar_size.value)

    def mOptToolbarRelief(self, *event):
        self.setToolbarRelief(self.tkopt.toolbar_relief.value)

    def mOptToolbarConfig(self, w):
        self.toolbarConfig(w, self.tkopt.toolbar_vars[w].value)

    def mOptDemoLogoStyle(self, *event):
        self.setDemoLogoStyle()

    def mOptPauseTextStyle(self, *event):
        self.setPauseTextStyle()

    def mOptRedealIconStyle(self, *event):
        self.setRedealIconStyle()

    def mOptStatusbar(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.app.statusbar:
            return
        side = self.tkopt.statusbar.value  # noqa
        resize = not self.app.opt.save_games_geometry  # noqa

    def mOptSaveGamesGeometry(self, *event):
        if self._cancelDrag(break_pause=False):
            return

    def mOptDemoLogo(self, *event):
        if self._cancelDrag(break_pause=False):
            return

    def mOptNegativeBottom(self, *event):
        if self._cancelDrag():
            return
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    #
    # toolbar support
    #

    def setToolbarSize(self, size):
        if self._cancelDrag(break_pause=False):
            return
        dir = self.app.getToolbarImagesDir()
        if self.app.toolbar.updateImages(dir, size):
            self.game.updateStatus(player=self.app.opt.player)

    def setToolbarStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        dir = self.app.getToolbarImagesDir()
        size = self.app.opt.toolbar_size
        self.app.toolbar.updateImages(dir, size)

    def setToolbarCompound(self, compound):
        if self._cancelDrag(break_pause=False):
            return
        if self.app.toolbar.setCompound(compound):
            self.game.updateStatus(player=self.app.opt.player)

    def setToolbarRelief(self, relief):
        if self._cancelDrag(break_pause=False):
            return
        self.app.toolbar.setRelief(relief)

    def toolbarConfig(self, w, v):
        if self._cancelDrag(break_pause=False):
            return

    #
    # other graphics
    #

    def setDemoLogoStyle(self, style=None):
        if self._cancelDrag(break_pause=False):
            return
        if self.tkopt.demo_logo_style.value == "none":
            self.tkopt.demo_logo.value = False
        else:
            self.tkopt.demo_logo.value = True
            self.app.loadImages2()
            self.app.loadImages4()

    def setDialogIconStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.loadImages1()
        self.app.loadImages4()

    def setPauseTextStyle(self, style=None):
        if self._cancelDrag(break_pause=False):
            return
        self.app.loadImages2()
        self.app.loadImages4()
        if self.tkopt.pause.value:
            self.app.game.displayPauseImage()

    def setRedealIconStyle(self, style=None):
        if self._cancelDrag(break_pause=False):
            return
        self.app.loadImages2()
        self.app.loadImages4()
        try:
            images = self.app.game.canvas.findImagesByType("redeal_image")
            for i in images:
                i.group.stack.updateRedealImage()
        except:  # noqa
            pass

    #
    # stacks descriptions
    #

    def mStackDesk(self, *event):
        if self.game.stackdesc_list:
            self.game.deleteStackDesc()
        else:
            if self._cancelDrag(break_pause=True):
                return
            self.game.showStackDesc()

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
            except Exception:
                return
            if SELECT_GAME_MENU:
                menu = self.__menupath[".menubar.select.customgames"][2]

                def select_func(gi): return gi.si.game_type == GI.GT_CUSTOM
                games = map(self.app.gdb.get,
                            self.app.gdb.getGamesIdSortedByName())
                games = filter(select_func, games)
                self.updateGamesMenu(menu, games)

            self.tkopt.gameid.value = gameid
            self._mSelectGame(gameid, force=True)

    def mWizard(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.wizardDialog()

    def mWizardEdit(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.wizardDialog(edit=True)


'''
'''
