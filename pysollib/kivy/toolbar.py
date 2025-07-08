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

from kivy.cache import Cache
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

# PySol kivy imports
from pysollib.kivy.LBase import LBase
from pysollib.kivy.LImage import LImage
from pysollib.kivy.toast import Toast

# PySol imports
from pysollib.mygettext import _, n_  # noqa
from pysollib.util import IMAGE_EXTENSIONS
from pysollib.winsystems import TkSettings

# ************************************************************************


class MyButtonBase(ButtonBehavior, LImage, LBase):
    shown = BooleanProperty(True)
    enabled = BooleanProperty(True)
    config = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.src = None
        if ('image' in kwargs):
            self.src = kwargs['image'].source
        self.command = None
        if ('command' in kwargs):
            self.command = kwargs['command']
        self.name = ""
        if ('name' in kwargs):
            self.name = kwargs['name']

        image = CoreImage(self.src)
        self.texture = image.texture
        self.fit_mode = "contain"

    def set_enabled(self, instance, value):
        # print ('** set enabled (',self.name ,') called', value)
        self.enabled = value

    def set_config(self, instance, value):
        # print ('** set config (',self.name ,') called', value)
        self.config = value


class MyButton(MyButtonBase):
    def on_press(self):
        self.fit_mode = "scale-down"

    def on_release(self):
        self.fit_mode = "contain"
        if (self.command is not None):
            self.command()


class MyCheckButton(MyButtonBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.variable = None
        if ('variable' in kwargs):
            self.variable = kwargs['variable']
        self.win = None
        if ('win' in kwargs):
            self.win = kwargs['win']
        self.checked = False

        # self.variable = self.win.app.menubar.tkopt.pause
        if self.variable:
            self.variable.bind(value=self.updateState)

    def updateState(self, obj, val):
        if (val):
            self.fit_mode = "scale-down"
        else:
            self.fit_mode = "contain"

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
            self.fit_mode = "contain"
            self.checked = False
            if (self.command is not None):
                self.command()
        else:
            self.fit_mode = "scale-down"
            self.checked = True
            if (self.command is not None):
                self.command()

    def on_release(self):
        pass


class MyToastButton(MyButtonBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timeout = 2.0
        if ('timeout' in kwargs):
            self.timeout = kwargs['timeout']

    def exec_command(self):
        if (self.command is not None):
            self.command()

    def on_press(self):
        self.fit_mode = "scale-down"
        text = ""
        if self.name == "new":
            text = _("New game")
        if self.name == "restart":
            text = _("Restart game")
        toast = Toast(text=text+" ?")
        toast.show(parent=Cache.get('LAppCache', 'mainApp').baseWindow,
                   duration=self.timeout,
                   hook=self.exec_command)

    def on_release(self):
        self.fit_mode = "contain"


class MyWaitButton(MyButtonBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timeout = 1.0
        if ('timeout' in kwargs):
            self.timeout = kwargs['timeout']
        self.eventId = None
        self.wait_toast = None
        self.ok = False

    def make_toast(self, text):
        mainApp = Cache.get('LAppCache', 'mainApp')
        self.wait_toast = Toast(text=text)
        self.wait_toast.popup(mainApp.baseWindow, offset=(0,-0.2))  # noqa

    def clear_toast(self):
        if self.wait_toast is not None:
            self.wait_toast.stop()
            self.wait_toast = None

    def okstart(self, *args):
        self.make_toast(_("ok to release"))

    def holdend(self, *args):
        self.clear_toast()
        self.eventId = None
        self.ok = True
        Clock.schedule_once(self.okstart, 0.1)

    def on_press(self):
        self.fit_mode = "scale-down"
        self.eventId = Clock.schedule_once(self.holdend, self.timeout)
        self.make_toast(_("hold on ..."))

    def on_release(self):
        self.fit_mode = "contain"
        if self.eventId is not None:
            Clock.unschedule(self.eventId)
        self.clear_toast()
        if self.ok:
            if (self.command is not None):
                self.command()
        self.ok = False

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

        super().__init__(orientation='vertical')
        self.size_hint = (0.06, 1.0)
        # self.size_hint=(None, 1.0)
        # self.width = 50
        self.win = top
        self.menubar = menubar
        self.dir = dir
        self.win.setTool(self, 3)
        self.buttons = []
        self.buttond = {}

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

        # Build all the buttions.

        for label, f, t in bl:
            if label is None:
                button = None
                # We dont have separators in kivy version.
            elif label == 'Pause':
                button = self._createButton(label, f, check=True, tooltip=t)
                self.buttons.append(button)
            elif label in ["New", "Restart"]:
                button = self._createButton(label, f, check=False, tooltip=t, timeout=3.0)  # noqa
                self.buttons.append(button)
            else:
                button = self._createButton(label, f, check=False, tooltip=t)
                self.buttons.append(button)

            if button is not None:
                # print('button name: ', button.name)
                self.buttond[button.name] = button

        self.redraw()
        Window.bind(size=self.doResize)

    def doResize(self, *args):
        self.show(True)

    def show(self, on=0, **kw):

        landscape = Window.width/Window.height > 1.0
        if landscape:
            side = self.menubar.tkopt.toolbar_land.value
        else:
            side = self.menubar.tkopt.toolbar_port.value

        self.win.setTool(None, side)

        # size_hint dependent on screen orientation:
        if side in [1, 2]:
            self.orientation = "horizontal"
            if landscape:
                self.size_hint = (1.0, 0.09)
            else:
                self.size_hint = (1.0, 0.06)
        else:
            self.orientation = "vertical"
            if landscape:
                self.size_hint = (0.06, 1.0)
            else:
                self.size_hint = (0.09, 1.0)
        return False

    def mHoldAndQuit(self, *args):
        if not self._busy():
            self.menubar.mHoldAndQuit()
        return 1

    def getSize(self):
        return 0

    def updateText(self, **kw):
        pass

    def redraw(self):
        self.clear_widgets()
        for b in self.buttons:
            # print(b.name,b.config,b.shown,b.enabled)
            if b.shown and b.enabled and b.config:
                self.add_widget(b)

    def changed_state(self, instance, value):
        self.redraw()

    def config(self, w, v):
        if w == 'shuffle':
            self.buttond['shuffle'].shown = v
            self.buttond['autodrop'].shown = not v

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

        # config settings (button.config bindings)

        opt = self.menubar.tkopt.toolbar_vars[name]
        button.config = opt.value
        opt.bind(value=button.set_config)

        # support settings (button.enabled bindings)
        try:
            oname = name
            if name == 'redo':
                # no separate option for redo, goes with undo.
                oname = 'undo'
            opt = getattr(self.menubar.tkopt, oname)

            # specialisation (differently used options):
            # - autodrop button has no own option. option 'autodrop' is used
            #   for the different effect of fully automatic dropping!
            # - pause button sets and clears the pause option, not vice versa!
            #   it is an option that only exists internaly (not saved).

            if oname not in ['autodrop', 'pause']:
                button.enabled = opt.value
                # print('** ', oname, '(enabled) = ', opt.value)
                opt.bind(value=button.set_enabled)

            button.bind(enabled=self.changed_state)
            button.bind(shown=self.changed_state)
        except:  # noqa
            # print('exception: button enable settings',name)
            pass

        button.bind(config=self.changed_state)

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
        # print('_busy:')
        self.game.stopDemo()
        self.game.interruptSleep()
        return self.game.busy
