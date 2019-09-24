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

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.properties import StringProperty

from pysollib.gamedb import GI
from pysollib.kivy.LApp import LMenu
from pysollib.kivy.LApp import LMenuItem
from pysollib.kivy.LApp import LScrollView
from pysollib.kivy.LApp import LTopLevel
from pysollib.kivy.LApp import LTreeNode
from pysollib.kivy.LApp import LTreeRoot
from pysollib.kivy.findcarddialog import destroy_find_card_dialog
from pysollib.kivy.selectcardset import SelectCardsetDialogWithPreview
from pysollib.kivy.selectgame import SelectGameDialog
from pysollib.kivy.solverdialog import connect_game_solver_dialog
from pysollib.kivy.tkconst import CURSOR_WATCH, EVENT_HANDLED, EVENT_PROPAGATE
from pysollib.kivy.tkconst import TOOLBAR_BUTTONS
from pysollib.kivy.tkutil import after_idle
from pysollib.kivy.tkutil import bind
from pysollib.mfxutil import Struct
from pysollib.mygettext import _
from pysollib.pysoltk import connect_game_find_card_dialog
from pysollib.settings import SELECT_GAME_MENU
from pysollib.settings import TITLE

# ************************************************************************
# * tk emuls:
# ************************************************************************


class TkVarObj(EventDispatcher):
    def __init(self):
        self.value = None

    def set(self, v):
        if v is None:
            if type(self.value) is str:
                v = ''
        self.value = v

    def get(self):
        return self.value


class BooleanVar(TkVarObj):
    value = BooleanProperty(False)


class IntVar(TkVarObj):
    value = NumericProperty(0)


class StringVar(TkVarObj):
    value = StringProperty('')

# ************************************************************************
# * Menu Dialogs
# ************************************************************************


class LMenuDialog(object):

    dialogCache = {}

    def make_pop_command(self, parent, title):
        def pop_command(event):
            print('event = %s' % event)
            parent.popWork(title)
        return pop_command

    def __init__(self, menubar, parent, title, app, **kw):
        super(LMenuDialog, self).__init__()

        self.menubar = menubar
        self.parent = parent
        self.app = app
        self.title = title
        self.window = None
        self.running = False
        self.persist = False
        if 'persist' in kw:
            self.persist = kw['persist']

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

        if self.persist:
            self.dialogCache[title] = window

        # Tree skelett.

        tv = self.tvroot = LTreeRoot(root_options=dict(text='EditTree'))
        tv.hide_root = True
        tv.size_hint = 1, None
        tv.bind(minimum_height=tv.setter('height'))

        # menupunkte aufbauen.

        self.buildTree(tv, None)

        # tree in einem Scrollwindow präsentieren.

        root = LScrollView(pos=(0, 0))
        root.add_widget(tv)
        self.window.content.add_widget(root)

    def buildTree(self, tree, node):
        print('buildTree base')
        # to implement in dervied class
        pass

# ************************************************************************


class MainMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['size_hint'] = (0.2, 1)
        kw['persist'] = True
        super(MainMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def make_game_command(self, command):
        def game_command():
            command()
            self.closeWindow(0)
        return game_command

    def buildTree(self, tv, node):
        rg = tv.add_node(
            LTreeNode(
                text=_("File"),
                command=self.make_game_command(self.menubar.mFileMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Games"),
                command=self.make_game_command(
                    self.menubar.mSelectGameDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Tools"),
                command=self.make_game_command(self.menubar.mEditMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Statistics"),
                command=self.make_game_command(self.menubar.mGameMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Assist"),
                command=self.make_game_command(
                    self.menubar.mAssistMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Options"),
                command=self.make_game_command(
                    self.menubar.mOptionsMenuDialog)))
        rg = tv.add_node(
            LTreeNode(
                text=_("Help"),
                command=self.make_game_command(self.menubar.mHelpMenuDialog)))
        del rg

# ************************************************************************


class FileMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['size_hint'] = (0.3, 1)
        super(FileMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def make_game_command(self, key, command):
        def game_command():
            command(key)
        return game_command

    def buildTree(self, tv, node):
        rg = tv.add_node(
            LTreeNode(text=_('Recent games')))
        # Recent Liste
        recids = self.app.opt.recent_gameid
        # recgames = []
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
                text=_('<Add>'), command=self.menubar.mAddFavor), rg)
            tv.add_node(LTreeNode(
                text=_('<Remove>'), command=self.menubar.mDelFavor), rg)

            # Recent Liste
            favids = self.app.opt.favorite_gameid
            # favgames = []
            for fid in favids:
                gi = self.app.getGameInfo(fid)
                if gi:
                    command = self.make_game_command(
                        fid, self.menubar._mSelectGame)
                    tv.add_node(
                        LTreeNode(text=gi.name, command=command), rg)

        tv.add_node(LTreeNode(
            text=_('Load'), command=self.menubar.mOpen))
        tv.add_node(LTreeNode(
            text=_('Save'), command=self.menubar.mSaveAs))

        tv.add_node(LTreeNode(
            text=_('Quit'), command=self.menubar.mHoldAndQuit))

# ************************************************************************


class EditMenuDialog(LMenuDialog):  # Tools

    def __init__(self, menubar, parent, title, app, **kw):
        kw['size_hint'] = (0.2, 1)
        kw['persist'] = True
        super(EditMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def make_auto_command(self, variable, command):
        def auto_command():
            variable.set(not variable.get())
            command()
        return auto_command

    def addCheckNode(self, tv, rg, title, auto_var, auto_com):
        command = self.make_auto_command(auto_var, auto_com)
        rg1 = tv.add_node(
            LTreeNode(text=title, command=command, variable=auto_var), rg)
        return rg1

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
            text='Solitaire &Wizard', command=self.menubar.mWizard))
        tv.add_node(LTreeNode(
                text='Edit current game', command=self.menubar.mWizardEdit))
        '''

# ************************************************************************


class GameMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['size_hint'] = (0.2, 1)
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
            command=self.make_command(101, self.menubar.mPlayerStats)), None)

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
        submenu = MfxMenu(menu, label=n_("D&emo statistics"))
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
        kw['size_hint'] = (0.2, 1)
        kw['persist'] = True
        super(AssistMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def buildTree(self, tv, node):
        tv.add_node(LTreeNode(
            text=_('Hint'), command=self.menubar.mHint))

        tv.add_node(LTreeNode(
            text=_('Highlight piles'), command=self.menubar.mHighlightPiles))

        # tv.add_node(LTreeNode(
        #   text='Find Card', command=self.menubar.mFindCard))

        tv.add_node(LTreeNode(
            text=_('Demo'), command=self.menubar.mDemo))

        # -------------------------------------------
        # TBD. How ?

        '''
        menu.add_command(
            label=n_("Demo (&all games)"), command=self.mMixedDemo)
        if USE_FREECELL_SOLVER:
            menu.add_command(label=n_("&Solver"), command=self.mSolver)
        else:
            menu.add_command(label=n_("&Solver"), state='disabled')
        menu.add_separator()
        menu.add_command(
            label=n_("&Piles description"),
            command=self.mStackDesk, accelerator="F2")
        '''

# ************************************************************************


class OptionsMenuDialog(LMenuDialog):

    def __init__(self, menubar, parent, title, app, **kw):
        kw['size_hint'] = (0.5, 1)
        kw['persist'] = True
        super(OptionsMenuDialog, self).__init__(
            menubar, parent, title, app, **kw)

    def make_auto_command(self, variable, command):
        def auto_command():
            variable.set(not variable.get())
            command()
        return auto_command

    def addCheckNode(self, tv, rg, title, auto_var, auto_com):
        command = self.make_auto_command(auto_var, auto_com)
        rg1 = tv.add_node(
            LTreeNode(text=title, command=command, variable=auto_var), rg)
        return rg1

    def make_val_command(self, variable, value, command):
        def val_command():
            variable.set(value)
            command()
        return val_command

    def make_vars_command(self, command, key):
        def vars_command():
            command(key)
        return vars_command

    def addRadioNode(self, tv, rg, title, auto_var, auto_val, auto_com):
        command = self.make_val_command(auto_var, auto_val, auto_com)
        rg1 = tv.add_node(
            LTreeNode(text=title,
                      command=command,
                      variable=auto_var, value=auto_val), rg)
        return rg1

    def buildTree(self, tv, node):

        # -------------------------------------------
        # Automatic play settings

        rg = tv.add_node(
            LTreeNode(text=_('Automatic play')))
        if rg:
            self.addCheckNode(tv, rg,
                              _('Auto face up'),
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
                              _('Highlight no matching'),
                              self.menubar.tkopt.highlight_not_matching,
                              self.menubar.mOptEnableHighlightNotMatching)

            # submenu.add_separator()

            self.addCheckNode(tv, rg,
                              _('Show removed tiles (in Mahjongg games)'),
                              self.menubar.tkopt.mahjongg_show_removed,
                              self.menubar.mOptMahjonggShowRemoved)

            self.addCheckNode(tv, rg,
                              _('Show hint arrow (in Shisen-Sho games)'),
                              self.menubar.tkopt.shisen_show_hint,
                              self.menubar.mOptShisenShowHint)

            # submenu.add_separator()

        '''
        # -------------------------------------------
        # Language options

        rg = tv.add_node(
            LTreeNode(text=_('Language')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('default'),
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
        '''

        # -------------------------------------------
        # Sound options

        rg = tv.add_node(
            LTreeNode(text=_('Sound')))
        if rg:
            self.addCheckNode(tv, rg,
                              _('Enable'),
                              self.menubar.tkopt.sound,
                              self.menubar.mOptSoundDialog)

            rg1 = tv.add_node(
                LTreeNode(text=_('Volume')), rg)
            if rg1:
                self.addRadioNode(tv, rg1,
                                  _('100%'),
                                  self.menubar.tkopt.sound_sample_volume, 100,
                                  self.menubar.mOptSoundSampleVol)
                self.addRadioNode(tv, rg1,
                                  _('75%'),
                                  self.menubar.tkopt.sound_sample_volume, 75,
                                  self.menubar.mOptSoundSampleVol)
                self.addRadioNode(tv, rg1,
                                  _('50%'),
                                  self.menubar.tkopt.sound_sample_volume, 50,
                                  self.menubar.mOptSoundSampleVol)
                self.addRadioNode(tv, rg1,
                                  _('25%'),
                                  self.menubar.tkopt.sound_sample_volume, 25,
                                  self.menubar.mOptSoundSampleVol)

            rg1 = tv.add_node(
                LTreeNode(text=_('Samples')), rg)
            if rg1:
                key = 'areyousure'
                self.addCheckNode(
                    tv, rg1,
                    _('are you sure'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'autodrop'
                self.addCheckNode(
                    tv, rg1,
                    _('auto drop'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'autoflip'
                self.addCheckNode(
                    tv, rg1,
                    _('auto flip'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'autopilotlost'
                self.addCheckNode(
                    tv, rg1,
                    _('auto pilot lost'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'autopilotwon'
                self.addCheckNode(
                    tv, rg1,
                    _('auto pilot won'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'deal'
                self.addCheckNode(
                    tv, rg1,
                    _('deal'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'dealwaste'
                self.addCheckNode(
                    tv, rg1,
                    _('deal waste'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'droppair'
                self.addCheckNode(
                    tv, rg1,
                    _('drop pair'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'drop'
                self.addCheckNode(
                    tv, rg1,
                    _('drop'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'flip'
                self.addCheckNode(
                    tv, rg1,
                    _('flip'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'move'
                self.addCheckNode(
                    tv, rg1,
                    _('move'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'nomove'
                self.addCheckNode(
                    tv, rg1,
                    _('no move'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'redo'
                self.addCheckNode(
                    tv, rg1,
                    _('redo'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'startdrag'
                self.addCheckNode(
                    tv, rg1,
                    _('start drag'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'turnwaste'
                self.addCheckNode(
                    tv, rg1,
                    _('turn waste'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'undo'
                self.addCheckNode(
                    tv, rg1,
                    _('undo'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'gamefinished'
                self.addCheckNode(
                    tv, rg1,
                    _('game finished'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'gamelost'
                self.addCheckNode(
                    tv, rg1,
                    _('game lost'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'gameperfect'
                self.addCheckNode(
                    tv, rg1,
                    _('game perfect'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))
                key = 'gamewon'
                self.addCheckNode(
                    tv, rg1,
                    _('game won'),
                    self.menubar.tkopt.sound_sample_vars[key],
                    self.make_vars_command(self.menubar.mOptSoundSample, key))

        # -------------------------------------------
        # Cardsets and card backside options

        rg = tv.add_node(
            LTreeNode(text=_('Cardsets')))
        if rg:
            self.menubar.tkopt.cardset.set(self.app.cardset.index)

            csm = self.app.cardset_manager
            # cnt = csm.len()
            i = 0
            while 1:
                cs = csm.get(i)
                if cs is None:
                    break
                rg1 = self.addRadioNode(tv, rg,
                                        cs.name,
                                        self.menubar.tkopt.cardset, i,
                                        self.menubar.mOptCardset)
                if rg1:
                    cbs = cs.backnames
                    self.menubar.tkopt.cardbacks[i] = IntVar()
                    self.menubar.tkopt.cardbacks[i].set(cs.backindex)

                    bcnt = len(cbs)
                    bi = 0
                    while 1:
                        if bi == bcnt:
                            break
                        cb = cbs[bi]
                        self.addRadioNode(
                            tv, rg1,
                            cb,
                            self.menubar.tkopt.cardbacks[i], bi,
                            self.make_vars_command(
                                self.menubar.mOptSetCardback, i))
                        bi += 1

                i += 1

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
                    _('Blue'),
                    self.menubar.tkopt.color_vars[key], '#0082df',
                    self.menubar.mOptTableColor)
                self.addRadioNode(
                    tv, rg1,
                    _('Green'),
                    self.menubar.tkopt.color_vars[key], '#008200',
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
                    _('Teal'),
                    self.menubar.tkopt.color_vars[key], '#008286',
                    self.menubar.mOptTableColor)

            rg1 = tv.add_node(
                LTreeNode(text=_('Tiles and Images')), rg)

            if rg1:
                tm = self.app.tabletile_manager
                # cnt = tm.len()
                i = 1
                while True:
                    ti = tm.get(i)
                    if ti is None:
                        break
                    self.addRadioNode(tv, rg1,
                                      ti.name,
                                      self.menubar.tkopt.tabletile, i,
                                      self.menubar.mOptTileSet)
                    i += 1

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

            # submenu.add_separator()

            self.addCheckNode(tv, rg,
                              _('Redeal animation'),
                              self.menubar.tkopt.redeal_animation,
                              self.menubar.mRedealAnimation)

            self.addCheckNode(tv, rg,
                              _('Winning animation'),
                              self.menubar.tkopt.win_animation,
                              self.menubar.mWinAnimation)

        # -------------------------------------------
        # Touch mode settings

        rg = tv.add_node(
            LTreeNode(text=_('Touch mode')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('Drag-and-Drop'),
                              self.menubar.tkopt.mouse_type, 'drag-n-drop',
                              self.menubar.mOptMouseType)

            self.addRadioNode(tv, rg,
                              _('Point-and-Click'),
                              self.menubar.tkopt.mouse_type, 'point-n-click',
                              self.menubar.mOptMouseType)

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

        # -------------------------------------------
        # Toolbar options

        rg = tv.add_node(
            LTreeNode(text=_('Toolbar')))
        if rg:
            self.addRadioNode(tv, rg,
                              _('Hide'),
                              self.menubar.tkopt.toolbar, 0,
                              self.menubar.mOptToolbar)

            # not supported: Top, Bottom
            # self.addRadioNode(tv, rg,
            #   'Top',
            #   self.menubar.tkopt.toolbar, 1,
            #   self.menubar.mOptToolbar)
            # self.addRadioNode(tv, rg,
            #   'Bottom',
            #   self.menubar.tkopt.toolbar, 2,
            #   self.menubar.mOptToolbar)

            self.addRadioNode(tv, rg,
                              _('Left'),
                              self.menubar.tkopt.toolbar, 3,
                              self.menubar.mOptToolbar)
            self.addRadioNode(tv, rg,
                              _('Right'),
                              self.menubar.tkopt.toolbar, 4,
                              self.menubar.mOptToolbar)

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
        # general options

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
                          self.menubar.mOptSplashscreen)

        self.addCheckNode(tv, None,
                          _('Winning splash'),
                          self.menubar.tkopt.display_win_message,
                          self.menubar.mWinDialog)


# ************************************************************************


class HelpMenuDialog(LMenuDialog):
    def __init__(self, menubar, parent, title, app, **kw):
        kw['size_hint'] = (0.3, 1)
        kw['persist'] = True
        super(HelpMenuDialog, self).__init__(menubar, parent, title, app, **kw)

    def make_help_command(self, command):
        def help_command():
            command()
            self.closeWindow(0)
        return help_command

    def buildTree(self, tv, node):
        tv.add_node(
            LTreeNode(
                text=_('Contents'),
                command=self.make_help_command(self.menubar.mHelp)))
        tv.add_node(
            LTreeNode(
                text=_('How to play'),
                command=self.make_help_command(self.menubar.mHelpHowToPlay)))
        tv.add_node(
            LTreeNode(
                text=_('Rules for this game'),
                command=self.make_help_command(self.menubar.mHelpRules)))
        tv.add_node(
            LTreeNode(
                text=_('License terms'),
                command=self.make_help_command(self.menubar.mHelpLicense)))
        tv.add_node(
            LTreeNode(
                text=_('About %s...') % TITLE,
                command=self.make_help_command(self.menubar.mHelpAbout)))

        # tv.add_node(LTreeNode(
        #   text='AboutKivy ...',
        #   command=self.makeHtmlCommand(self.menubar, "kivy.html")))

    def makeHtmlCommand(self, bar, htmlfile):
        def htmlCommand():
            bar.mHelpHtml(htmlfile)

        return htmlCommand


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


class PysolMenubarTk:
    def __init__(self, app, top, progress=None):
        self._createTkOpt()
        self._setOptions()
        # init columnbreak
#        self.__cb_max = int(self.top.winfo_screenheight()/23)
        self.__cb_max = 8
#         sh = self.top.winfo_screenheight()
#         self.__cb_max = 22
#         if sh >= 600: self.__cb_max = 27
#         if sh >= 768: self.__cb_max = 32
#         if sh >= 1024: self.__cb_max = 40
        self.progress = progress
        # create menus
        self.__menubar = None
        self.__menupath = {}
        self.__keybindings = {}
        self._createMenubar()
        self.top = top

        if self.progress:
            self.progress.update(step=1)

        # set the menubar
        # self.updateBackgroundImagesMenu()
        # self.top.config(menu=self.__menubar)

    def _createTkOpt(self):
        # structure to convert menu-options to Toolkit variables
        self.tkopt = Struct(
            gameid=IntVar(),
            gameid_popular=IntVar(),
            comment=BooleanVar(),
            autofaceup=BooleanVar(),
            autodrop=BooleanVar(),
            autodeal=BooleanVar(),
            quickplay=BooleanVar(),
            undo=BooleanVar(),
            bookmarks=BooleanVar(),
            hint=BooleanVar(),
            shuffle=BooleanVar(),
            highlight_piles=BooleanVar(),
            highlight_cards=BooleanVar(),
            highlight_samerank=BooleanVar(),
            highlight_not_matching=BooleanVar(),
            mahjongg_show_removed=BooleanVar(),
            shisen_show_hint=BooleanVar(),
            sound=BooleanVar(),
            sound_sample_volume=IntVar(),
            sound_music_volume=IntVar(),
            cardback=IntVar(),
            tabletile=IntVar(),
            animations=IntVar(),
            redeal_animation=BooleanVar(),
            win_animation=BooleanVar(),
            shadow=BooleanVar(),
            shade=BooleanVar(),
            shade_filled_stacks=BooleanVar(),
            shrink_face_down=BooleanVar(),
            toolbar=IntVar(),
            toolbar_style=StringVar(),
            toolbar_relief=StringVar(),
            toolbar_compound=StringVar(),
            toolbar_size=IntVar(),
            statusbar=BooleanVar(),
            num_cards=BooleanVar(),
            helpbar=BooleanVar(),
            save_games_geometry=BooleanVar(),
            splashscreen=BooleanVar(),
            demo_logo=BooleanVar(),
            mouse_type=StringVar(),
            mouse_undo=BooleanVar(),
            negative_bottom=BooleanVar(),
            display_win_message=BooleanVar(),
            pause=BooleanVar(),
            cardset=IntVar(),
            cardbacks={},
            toolbar_vars={},
            sound_sample_vars={},
            color_vars={},
            # language=StringVar(),
        )
        for w in TOOLBAR_BUTTONS:
            self.tkopt.toolbar_vars[w] = BooleanVar()
        for k in self.app.opt.sound_samples:
            self.tkopt.sound_sample_vars[k] = BooleanVar()
        for k in self.app.opt.colors:
            self.tkopt.color_vars[k] = StringVar()

    def _setOptions(self):
        tkopt, opt = self.tkopt, self.app.opt
        # set state of the menu items
        tkopt.autofaceup.set(opt.autofaceup)
        tkopt.autodrop.set(opt.autodrop)
        tkopt.autodeal.set(opt.autodeal)
        tkopt.quickplay.set(opt.quickplay)
        tkopt.undo.set(opt.undo)
        tkopt.hint.set(opt.hint)
        tkopt.shuffle.set(opt.shuffle)
        tkopt.bookmarks.set(opt.bookmarks)
        tkopt.highlight_piles.set(opt.highlight_piles)
        tkopt.highlight_cards.set(opt.highlight_cards)
        tkopt.highlight_samerank.set(opt.highlight_samerank)
        tkopt.highlight_not_matching.set(opt.highlight_not_matching)
        tkopt.shrink_face_down.set(opt.shrink_face_down)
        tkopt.shade_filled_stacks.set(opt.shade_filled_stacks)
        tkopt.mahjongg_show_removed.set(opt.mahjongg_show_removed)
        tkopt.shisen_show_hint.set(opt.shisen_show_hint)
        tkopt.sound.set(opt.sound)
        tkopt.sound_sample_volume.set(opt.sound_sample_volume)
        tkopt.sound_music_volume.set(opt.sound_music_volume)
        tkopt.cardback.set(self.app.cardset.backindex)
        tkopt.tabletile.set(self.app.tabletile_index)
        tkopt.animations.set(opt.animations)
        tkopt.redeal_animation.set(opt.redeal_animation)
        tkopt.win_animation.set(opt.win_animation)
        tkopt.shadow.set(opt.shadow)
        tkopt.shade.set(opt.shade)
        tkopt.toolbar.set(opt.toolbar)
        tkopt.toolbar_style.set(opt.toolbar_style)
        tkopt.toolbar_relief.set(opt.toolbar_relief)
        tkopt.toolbar_compound.set(opt.toolbar_compound)
        tkopt.toolbar_size.set(opt.toolbar_size)
        tkopt.toolbar_relief.set(opt.toolbar_relief)
        tkopt.statusbar.set(opt.statusbar)
        tkopt.num_cards.set(opt.num_cards)
        tkopt.helpbar.set(opt.helpbar)
        tkopt.save_games_geometry.set(opt.save_games_geometry)
        tkopt.demo_logo.set(opt.demo_logo)
        tkopt.splashscreen.set(opt.splashscreen)
        tkopt.mouse_type.set(opt.mouse_type)
        tkopt.mouse_undo.set(opt.mouse_undo)
        tkopt.negative_bottom.set(opt.negative_bottom)
        tkopt.display_win_message.set(opt.display_win_message)
        tkopt.cardset.set(self.app.cardset_manager.getSelected())
        # tkopt.language.set(opt.language)

        for w in TOOLBAR_BUTTONS:
            tkopt.toolbar_vars[w].set(opt.toolbar_vars.get(w, False))
        for k in self.app.opt.sound_samples:
            self.tkopt.sound_sample_vars[k].set(
                opt.sound_samples.get(k, False))
        for k in self.app.opt.colors:
            self.tkopt.color_vars[k].set(opt.colors.get(k, '#000000'))

    def connectGame(self, game):
        self.game = game
        if game is None:
            return
        assert self.app is game.app
        tkopt = self.tkopt
        # opt = self.app.opt
        tkopt.gameid.set(game.id)
        tkopt.gameid_popular.set(game.id)
        tkopt.comment.set(bool(game.gsaveinfo.comment))
        tkopt.pause.set(self.game.pause)
        if game.canFindCard():
            connect_game_find_card_dialog(game)
        else:
            destroy_find_card_dialog()
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
            variable.set(n)
            command()
        return gamesetter

    def _addSelectGameSubSubMenu(self, games, menu, command, variable,
                                 short_name=False):

        # cb = self.__cb_max
        for i in range(len(games)):
            gi = games[i]
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
        self._mSelectGame(self.tkopt.gameid.get())

    def mSelectGamePopular(self, *args):
        self._mSelectGame(self.tkopt.gameid_popular.get())

    def _mSelectGameDialog(self, d):
        if d.gameid != self.game.id:
            self.tkopt.gameid.set(d.gameid)
            self.tkopt.gameid_popular.set(d.gameid)
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
        print('updateBookmarkMenuState - fake')
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

    def _setCommentMenu(self, v):
        self.tkopt.comment.set(v)

    def _setPauseMenu(self, v):
        self.tkopt.pause.set(v)

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
            self.app.opt.favorite_gameid.append(gameid)
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
#        d = tkFileDialog.Open()
#        filename = d.show(filetypes=self.FILETYPES,
#                          defaultextension=self.DEFAULTEXTENSION,
#                          initialdir=idir, initialfile=ifile)
        filename = idir + "/" + ifile

        print('filename = %s' % filename)
        if filename:
            filename = os.path.normpath(filename)
            # filename = os.path.normcase(filename)
            if os.path.isfile(filename):
                self.game.loadGame(filename)

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
        # print self.game.filename, ifile
        # d = tkFileDialog.SaveAs()
        # filename = d.show(filetypes=self.FILETYPES,
        #                  defaultextension=self.DEFAULTEXTENSION,
        #                  initialdir=idir, initialfile=ifile)
        filename = idir + "/" + ifile
        if filename:
            filename = os.path.normpath(filename)
            # filename = os.path.normcase(filename)
            self.game.saveGame(filename)
            self.updateMenus()

    def mPause(self, *args):
        if not self.game:
            return
        if not self.game.pause:
            if self._cancelDrag():
                return
        self.game.doPause()
        self.tkopt.pause.set(self.game.pause)

    '''
    def mOptLanguage(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.language = self.tkopt.language.get()
    '''

    def mOptSoundDialog(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.sound = self.tkopt.sound.get()

    def mOptSoundSampleVol(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.sound_sample_volume = self.tkopt.sound_sample_volume.get()

    def mOptSoundMusicVol(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.sound_music_volume = self.tkopt.sound_music_volume.get()

    def mOptSoundSample(self, key, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.sound_samples[key] = \
            self.tkopt.sound_sample_vars[key].get()

    def mOptTableColor(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        nv = self.tkopt.color_vars['table'].get()
        ov = self.app.opt.colors['table']
        self.app.opt.colors['table'] = nv
        if ov != nv:
            self.app.top_bg = nv
            self.app.tabletile_index = 0
            self.app.setTile(0, force=True)
            self.tkopt.tabletile.set(0)

    def mOptTileSet(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        idx = self.tkopt.tabletile.get()
        if idx > 0 and idx != self.app.tabletile_index:
            self.app.setTile(idx)
            self.tkopt.color_vars['table'].set('#008285')

    def mOptAutoFaceUp(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.autofaceup = self.tkopt.autofaceup.get()
        if self.app.opt.autofaceup:
            self.game.autoPlay()

    def mOptAutoDrop(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.autodrop = self.tkopt.autodrop.get()
        if self.app.opt.autodrop:
            self.game.autoPlay()

    def mOptAutoDeal(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.autodeal = self.tkopt.autodeal.get()
        if self.app.opt.autodeal:
            self.game.autoPlay()

    def mOptQuickPlay(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.quickplay = self.tkopt.quickplay.get()

    def mOptEnableUndo(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.undo = self.tkopt.undo.get()
        self.game.updateMenus()

    def mOptEnableBookmarks(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.bookmarks = self.tkopt.bookmarks.get()
        self.game.updateMenus()

    def mOptEnableHint(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.hint = self.tkopt.hint.get()
        self.game.updateMenus()

    def mOptEnableShuffle(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shuffle = self.tkopt.shuffle.get()
        self.game.updateMenus()

    def mOptEnableHighlightPiles(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_piles = self.tkopt.highlight_piles.get()
        self.game.updateMenus()

    def mOptEnableHighlightCards(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_cards = self.tkopt.highlight_cards.get()
        self.game.updateMenus()

    def mOptEnableHighlightSameRank(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_samerank = self.tkopt.highlight_samerank.get()
        # self.game.updateMenus()

    def mOptEnableHighlightNotMatching(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_not_matching = \
            self.tkopt.highlight_not_matching.get()
        # self.game.updateMenus()

    def mOptAnimations(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.animations = self.tkopt.animations.get()

    def mRedealAnimation(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.redeal_animation = self.tkopt.redeal_animation.get()

    def mWinAnimation(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.win_animation = self.tkopt.win_animation.get()

    def mWinDialog(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.display_win_message = self.tkopt.display_win_message.get()

    def mOptShadow(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shadow = self.tkopt.shadow.get()

    def mOptShade(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shade = self.tkopt.shade.get()

    def mOptShrinkFaceDown(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shrink_face_down = self.tkopt.shrink_face_down.get()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShadeFilledStacks(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shade_filled_stacks = self.tkopt.shade_filled_stacks.get()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptMahjonggShowRemoved(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.mahjongg_show_removed = \
            self.tkopt.mahjongg_show_removed.get()
        # self.game.updateMenus()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShisenShowHint(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shisen_show_hint = self.tkopt.shisen_show_hint.get()
        # self.game.updateMenus()

    def mOptCardset(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        idx = self.tkopt.cardset.get()
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
        val = self.tkopt.cardbacks[key].get()
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
            self.app.canvas.update_idletasks()

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
        self.app.canvas.update_idletasks()
        self.tkopt.cardback.set(cs.backindex)

    def mOptCardback(self, *event):
        self._mOptCardback(self.tkopt.cardback.get())

    def mOptChangeCardback(self, *event):
        self._mOptCardback(self.app.cardset.backindex + 1)

    def mOptToolbar(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarSide(self.tkopt.toolbar.get())

    def mOptToolbarStyle(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarStyle(self.tkopt.toolbar_style.get())

    def mOptToolbarCompound(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarCompound(self.tkopt.toolbar_compound.get())

    def mOptToolbarSize(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarSize(self.tkopt.toolbar_size.get())

    def mOptToolbarRelief(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarRelief(self.tkopt.toolbar_relief.get())

    def mOptToolbarConfig(self, w):
        self.toolbarConfig(w, self.tkopt.toolbar_vars[w].get())

    def mOptStatusbar(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.app.statusbar:
            return
        side = self.tkopt.statusbar.get()
        self.app.opt.statusbar = side
        resize = not self.app.opt.save_games_geometry
        if self.app.statusbar.show(side, resize=resize):
            self.top.update_idletasks()

    def mOptNumCards(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.num_cards = self.tkopt.num_cards.get()

    def mOptHelpbar(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.app.helpbar:
            return
        show = self.tkopt.helpbar.get()
        self.app.opt.helpbar = show
        resize = not self.app.opt.save_games_geometry
        if self.app.helpbar.show(show, resize=resize):
            self.top.update_idletasks()

    def mOptSaveGamesGeometry(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.save_games_geometry = self.tkopt.save_games_geometry.get()

    def mOptDemoLogo(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.demo_logo = self.tkopt.demo_logo.get()

    def mOptSplashscreen(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.splashscreen = self.tkopt.splashscreen.get()

    def mOptMouseType(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.mouse_type = self.tkopt.mouse_type.get()

    def mOptMouseUndo(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.mouse_undo = self.tkopt.mouse_undo.get()

    def mOptNegativeBottom(self, *event):
        if self._cancelDrag():
            return
        self.app.opt.negative_bottom = self.tkopt.negative_bottom.get()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    #
    # toolbar support
    #

    def setToolbarSide(self, side):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar = side
        self.tkopt.toolbar.set(side)                    # update radiobutton
        resize = not self.app.opt.save_games_geometry
        if self.app.toolbar.show(side, resize=resize):
            self.top.update_idletasks()

    def setToolbarSize(self, size):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_size = size
        self.tkopt.toolbar_size.set(size)                # update radiobutton
        dir = self.app.getToolbarImagesDir()
        if self.app.toolbar.updateImages(dir, size):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_style = style
        # update radiobutton
        self.tkopt.toolbar_style.set(style)
        dir = self.app.getToolbarImagesDir()
        size = self.app.opt.toolbar_size
        if self.app.toolbar.updateImages(dir, size):
            # self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarCompound(self, compound):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_compound = compound
        self.tkopt.toolbar_compound.set(
            compound)          # update radiobutton
        if self.app.toolbar.setCompound(compound):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarRelief(self, relief):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_relief = relief
        self.tkopt.toolbar_relief.set(relief)           # update radiobutton
        self.app.toolbar.setRelief(relief)
        self.top.update_idletasks()

    def toolbarConfig(self, w, v):
        if self._cancelDrag(break_pause=False):
            return
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

            self.tkopt.gameid.set(gameid)
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
