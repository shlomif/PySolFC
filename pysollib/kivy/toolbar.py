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

# PySol imports
from pysollib.mygettext import _, n_
from pysollib.settings import TITLE
from pysollib.util import IMAGE_EXTENSIONS
from pysollib.winsystems import TkSettings

# ************************************************************************
# *
# ************************************************************************


class AbstractToolbarButton:
    def __init__(self, parent, toolbar, toolbar_name, position):
        self.toolbar = toolbar
        self.toolbar_name = toolbar_name
        self.position = position
        self.visible = False

    def show(self, orient, force=False):
        if self.visible and not force:
            return
        self.visible = True
        padx, pady = 2, 2
        if orient == 'horizontal':
            self.grid(row=0,
                      column=self.position,
                      ipadx=padx, ipady=pady,
                      sticky='nsew')
        else:
            self.grid(row=self.position,
                      column=0,
                      ipadx=padx, ipady=pady,
                      sticky='nsew')

    def hide(self):
        if not self.visible:
            return
        self.visible = False
        self.grid_forget()

# ************************************************************************


if True:
    from pysollib.kivy.LApp import LImage
    from pysollib.kivy.LApp import LBase
    # from LApp import LMainWindow
    from kivy.uix.boxlayout import BoxLayout
    # from kivy.uix.button import Button
    from kivy.uix.behaviors import ButtonBehavior
    # from kivy.uix.behaviors import ToggleButtonBehavior
    from kivy.uix.image import Image as KivyImage

# ************************************************************************


class MyButton(ButtonBehavior, KivyImage, LBase):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        # super(MyButton, self).__init__()
        self.src = None
        if ('image' in kwargs):
            self.src = kwargs['image'].source
        self.command = None
        if ('command' in kwargs):
            self.command = kwargs['command']
        self.source = self.src
        self.allow_stretch = True

    def on_press(self):
        self.allow_stretch = False

    def on_release(self):
        self.allow_stretch = True
        if (self.command is not None):
            self.command()


class MyCheckButton(ButtonBehavior, KivyImage, LBase):
    def __init__(self, **kwargs):
        super(MyCheckButton, self).__init__(**kwargs)
        # super(MyCheckButton, self).__init__()
        self.src = None
        if ('image' in kwargs):
            self.src = kwargs['image'].source
        self.command = None
        if ('command' in kwargs):
            self.command = kwargs['command']
        self.variable = None
        if ('variable' in kwargs):
            self.variable = kwargs['variable']
        self.win = None
        if ('win' in kwargs):
            self.win = kwargs['win']
        self.source = self.src
        self.allow_stretch = True
        self.checked = False

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
        self.size_hint = (0.05, 1.0)
        # self.size_hint=(None, 1.0)
        # self.width = 50
        self.win = top
        self.menubar = menubar
        self.dir = dir
        self.win.setTool(self, 3)

        for label, f, t in (
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
            (n_("Pause"),    self.mPause,     _("Pause game")),
            (None,           None,            None),
            # (n_("Statistics"), self.mPlayerStats, _("View statistics")),
            (n_("Rules"),    self.mHelpRules, _("Rules for this game")),
            (None,           None,            None),
            (n_("Quit"),     self.mHoldAndQuit,      _("Quit ") + TITLE),
        ):
            if label is None:
                # sep = self._createSeparator()
                # sep.bind("<1>", self.clickHandler)
                # sep.bind("<3>", self.rightclickHandler)
                pass
            elif label == 'Pause':
                self._createButton(label, f, check=True, tooltip=t)
            else:
                self._createButton(label, f, tooltip=t)

            # hier gibt es noch ein 'player label' mit contextmenu, wo
            # der spielername gewählt und die spielstatistik etc.
            # angezeigt werden könnte (TBD):
            '''
        sep = self._createFlatSeparator()
        sep.bind("<1>", self.clickHandler)
        sep.bind("<3>", self.rightclickHandler)
        self._createLabel("player", label=n_('Player'),
                          tooltip=_("Player options"))
        #
        self.player_label.bind("<1>", self.mOptPlayerOptions)
        # self.player_label.bind("<3>", self.mOptPlayerOptions)
        self.popup = MfxMenu(master=None, label=n_('Toolbar'), tearoff=0)
        createToolbarMenu(menubar, self.popup)
        self.frame.bind("<1>", self.clickHandler)
        self.frame.bind("<3>", self.rightclickHandler)
        #
        self.setCompound(compound, force=True)
            '''

    def show(self, on, **kw):
        side = self.menubar.tkopt.toolbar.get()
        self.win.setTool(None, side)
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
        print('PysolToolbarTk: config %s, %s' % (w, v))
        # y = self.yy
        pass

    # Lokale.

    def _loadImage(self, name):
        file = os.path.join(self.dir, name)
        image = None
        for ext in IMAGE_EXTENSIONS:
            file = os.path.join(self.dir, name + ext)
            if os.path.isfile(file):
                image = LImage(source=file)
                # print('_loadImage: file=%s' % file)
                # image = Tkinter.PhotoImage(file=file)
                break
        return image

    def _createButton(self, label, command, check=False, tooltip=None):
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
        }
        # print ('toolbar:  print %s' % self.win)
        # print ('toolbar:  print %s' % self.win.app)
        kw['win'] = self.win
        if image:
            kw['image'] = image
        if check:
            kw['offrelief'] = button_relief
            kw['indicatoron'] = False
            kw['selectcolor'] = ''

            button = MyCheckButton(**kw)
        else:
            button = MyButton(**kw)

        # button.show(orient=self.orient)
        setattr(self, name + "_image", image)
        setattr(self, name + "_button", button)
        # self._widgets.append(button)
        self.add_widget(button)

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
