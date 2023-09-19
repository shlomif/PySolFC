#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
# Copyright (C) 2016-2017 LB
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

# imports
import os
from time import time

# PySol imports
from pysollib.mygettext import _, n_
from pysollib.util import IMAGE_EXTENSIONS
from pysollib.winsystems import TkSettings

# ************************************************************************
# *
# ************************************************************************

from pysollib.kivy.LApp import LImage
from pysollib.kivy.LApp import LBase
from pysollib.kivy.toast import Toast
# from LApp import LMainWindow
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
# from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.image import Image as KivyImage

# ************************************************************************

from kivy.cache import Cache


class MyButton(ButtonBehavior, KivyImage, LBase):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        self.src = None
        if ('image' in kwargs):
            self.src = kwargs['image'].source
        self.command = None
        if ('command' in kwargs):
            self.command = kwargs['command']
        self.name = ""
        if ('name' in kwargs):
            self.name = kwargs['name']
        self.source = self.src
        self.allow_stretch = True
        self.shown = True

    def on_press(self):
        self.allow_stretch = False

    def on_release(self):
        self.allow_stretch = True
        if (self.command is not None):
            self.command()


class MyCheckButton(ButtonBehavior, KivyImage, LBase):
    def __init__(self, **kwargs):
        super(MyCheckButton, self).__init__(**kwargs)
        self.src = None
        if ('image' in kwargs):
            self.src = kwargs['image'].source
        self.command = None
        if ('command' in kwargs):
            self.command = kwargs['command']
        self.name = ""
        if ('name' in kwargs):
            self.name = kwargs['name']
        self.variable = None
        if ('variable' in kwargs):
            self.variable = kwargs['variable']
        self.win = None
        if ('win' in kwargs):
            self.win = kwargs['win']
        self.source = self.src
        self.allow_stretch = True
        self.checked = False
        self.shown = True

        # self.variable = self.win.app.menubar.tkopt.pause
        if self.variable:
            self.variable.bind(value=self.updateState)

    def updateState(self, obj, val):
        if (val):
            self.allow_stretch = False
        else:
            self.allow_stretch = True

    def isChecked(self):
        return self.checked

    def on_press(self):
        if self.win is None:
            return
        if self.win.app is None:
            return
        if self.win.app.game is None:
            return

        game = self.win.app.game
        if game.finished:
            return
        if game.demo:
            return

        # if self.win.app.menubar == None: return
        # mb = self.win.app.menubar

        if game.pause:
            self.allow_stretch = True
            self.checked = False
            if (self.command is not None):
                self.command()
        else:
            self.allow_stretch = False
            self.checked = True
            if (self.command is not None):
                self.command()

    def on_release(self):
        pass


class MyToastButton(ButtonBehavior, KivyImage, LBase):
    def __init__(self, **kwargs):
        super(MyToastButton, self).__init__(**kwargs)
        self.src = None
        if ('image' in kwargs):
            self.src = kwargs['image'].source
        self.command = None
        if ('command' in kwargs):
            self.command = kwargs['command']
        self.name = ""
        if ('name' in kwargs):
            self.name = kwargs['name']
        self.timeout = 0.0
        if ('timeout' in kwargs):
            self.timeout = kwargs['timeout']
        self.source = self.src
        self.allow_stretch = True
        self.shown = True
        self.start_time = 0.0

    def on_press(self):
        self.allow_stretch = False
        self.start_time = time()

    def on_release(self):
        self.allow_stretch = True
        delta = time()-self.start_time
        if (self.command is not None):
            if delta > self.timeout:
                self.command()
            else:
                mainApp = Cache.get('LAppCache', 'mainApp')
                toast = Toast(text=_("button released too early"))
                toast.show(parent=mainApp.baseWindow, duration=2.0)
                # print('too early released')


# ************************************************************************
# * Note: Applications should call show/hide after constructor.
# ************************************************************************


class PysolToolbarTk(BoxLayout):
    def __init__(
            self,
            top,
            menubar,
            dir,
            size=0,
            relief='flat',
            compound='none'):

        super(PysolToolbarTk, self).__init__(orientation='vertical')
        self.size_hint = (0.06, 1.0)
        # self.size_hint=(None, 1.0)
        # self.width = 50
        self.win = top
        self.menubar = menubar
        self.dir = dir
        self.win.setTool(self, 3)
        self.buttons = []

        # This is called only once after program start. Configurations
        # have to take place elsewhere.

        bl = []
        bl.append((n_("New"),      self.mNewGame,   _("New game")))
        bl.append((n_("Restart"),  self.mRestart,   _("Restart the\ncurrent game")))  # noqa
        bl.append((n_("Undo"),     self.mUndo,      _("Undo last move")))  # noqa
        bl.append((n_("Redo"),     self.mRedo,      _("Redo last move")))
        bl.append((n_("Autodrop"), self.mDrop,      _("Auto drop cards")))
        bl.append((n_("Shuffle"),  self.mShuffle,   _("Shuffle tiles")))
        bl.append((n_("Hint"),     self.mHint,      _("Hint")))
        bl.append((n_("Pause"),    self.mPause,     _("Pause game")))
        bl.append((n_("Rules"),    self.mHelpRules, _("Rules for this game")))

        '''
        for label, f, t in [
            (n_("New"),      self.mNewGame,   _("New game")),
            (n_("Restart"),  self.mRestart,   _("Restart the\ncurrent game")),
            (None,           None,            None),
            # (n_("Open"),     self.mOpen,      _("Open a\nsaved game")),
            # (n_("Save"),     self.mSave,      _("Save game")),
            (None,           None,            None),
            (n_("Undo"),     self.mUndo,      _("Undo last move")),
            (n_("Redo"),     self.mRedo,      _("Redo last move")),
            (n_("Autodrop"), self.mDrop,      _("Auto drop cards")),
            (n_("Shuffle"),  self.mShuffle,   _("Shuffle tiles")),
            (n_("Hint"),     self.mHint,      _("Hint")),
            (n_("Pause"),    self.mPause,     _("Pause game")),
            (None,           None,            None),
            # (n_("Statistics"), self.mPlayerStats, _("View statistics")),
            (n_("Rules"),    self.mHelpRules, _("Rules for this game")),
            (None,           None,            None),
            (n_("Quit"),     self.mHoldAndQuit,      _("Quit %s") % TITLE),
        ]:
        '''

        for label, f, t in bl:
            if label is None:
                # We dont have separators in kivy version.
                pass
            elif label == 'Pause':
                button = self._createButton(label, f, check=True, tooltip=t)
                self.buttons.append(button)
            elif label in ["New", "Restart"]:
                button = self._createButton(label, f, check=False, tooltip=t, timeout=1.0)  # noqa
                self.buttons.append(button)
            else:
                button = self._createButton(label, f, check=False, tooltip=t)
                self.buttons.append(button)

    def show(self, on, **kw):
        side = self.menubar.tkopt.toolbar.get()
        self.win.setTool(None, side)
        print('******** toolbar show', on, side, kw)
        return False

    def mHoldAndQuit(self, *args):
        if not self._busy():
            self.menubar.mHoldAndQuit()
        return 1

    def getSize(self):
        return 0

    def updateText(self, **kw):
        pass

    def config(self, w, v):
        print('********************* PysolToolbarTk: config %s, %s' % (w, v))

        # This is the position, where the toolbar can be configured.

        chgd = False
        for b in self.buttons:
            if b.name == w:
                ov = b.shown
                if v != ov:
                    b.shown = v
                    chgd = True

        if chgd:
            self.clear_widgets()
            for b in self.buttons:
                if b.shown:
                    self.add_widget(b)

    # Lokale.

    def _loadImage(self, name):
        file = os.path.join(self.dir, name)
        image = None
        for ext in IMAGE_EXTENSIONS:
            file = os.path.join(self.dir, name + ext)
            if os.path.isfile(file):
                image = LImage(source=file)
                # print('_loadImage: file=%s' % file)
                break
        return image

    def _createButton(self, label, command, check=False, tooltip=None, timeout=0.0):  # noqa
        name = label.lower()
        image = self._loadImage(name)
        # position = len(self._widgets)
        button_relief = TkSettings.toolbar_button_relief
        bd = TkSettings.toolbar_button_borderwidth
        padx, pady = TkSettings.toolbar_button_padding
        kw = {
            'toolbar': self,
            'toolbar_name': name,
            'command': command,
            'takefocus': 0,
            'text': _(label),
            'bd': bd,
            'relief': button_relief,
            'padx': padx,
            'pady': pady,
            'overrelief': 'raised',
            'timeout': timeout
        }
        # print ('toolbar:  print %s' % self.win)
        # print ('toolbar:  print %s' % self.win.app)
        kw['win'] = self.win
        if image:
            kw['image'] = image
        if name:
            kw['name'] = name
        if check:
            kw['offrelief'] = button_relief
            kw['indicatoron'] = False
            kw['selectcolor'] = ''

            button = MyCheckButton(**kw)
        elif timeout > 0.0:
            button = MyToastButton(**kw)
        else:
            button = MyButton(**kw)

        # TBD: tooltip ev. auf basis einer statuszeile implementieren
        # if tooltip:
        #   b = MfxTooltip(button)
        #   self._tooltips.append(b)
        #   b.setText(tooltip)
        return button

    def _busy(self):
        # if not self.side or not self.game or not self.menubar:
        #   return 1
        if not self.game or not self.menubar:
            return 1
        print('_busy:')
        self.game.stopDemo()
        self.game.interruptSleep()
        return self.game.busy
