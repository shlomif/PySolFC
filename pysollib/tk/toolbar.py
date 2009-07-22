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

__all__ = ['PysolToolbarTk']

# imports
import os
import Tkinter

# PySol imports
from pysollib.mfxutil import destruct
from pysollib.mfxutil import Image, ImageTk
from pysollib.util import IMAGE_EXTENSIONS
from pysollib.settings import TITLE
from pysollib.winsystems import TkSettings

# Toolkit imports
from tkconst import EVENT_HANDLED
from tkwidget import MfxTooltip
from menubar import createToolbarMenu, MfxMenu


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
        if not self.visible: return
        self.visible = False
        self.grid_forget()


class ToolbarCheckbutton(AbstractToolbarButton, Tkinter.Checkbutton):
    def __init__(self, parent, toolbar, toolbar_name, position, **kwargs):
        Tkinter.Checkbutton.__init__(self, parent, kwargs)
        AbstractToolbarButton.__init__(self, parent, toolbar, toolbar_name, position)


class ToolbarButton(AbstractToolbarButton, Tkinter.Button):
    def __init__(self, parent, toolbar, toolbar_name, position, **kwargs):
        Tkinter.Button.__init__(self, parent, kwargs)
        AbstractToolbarButton.__init__(self, parent, toolbar, toolbar_name, position)


class ToolbarSeparator(Tkinter.Frame):
    def __init__(self, parent, toolbar, position, **kwargs):
        Tkinter.Frame.__init__(self, parent, kwargs)
        self.toolbar = toolbar
        self.position = position
        self.visible = False
    def show(self, orient, force=False):
        if self.visible and not force:
            return
        self.visible = True
        width = 4
        height = 4
        padx = 6
        pady = 6
        if orient == 'horizontal':
            self.config(width=width, height=height)
            self.grid(row=0,
                      column=self.position,
                      padx=padx, pady=pady,
                      sticky='ns')
        else:
            self.config(width=height, height=width)
            self.grid(row=self.position,
                      column=0,
                      padx=pady, pady=padx,
                      sticky='ew')
    def hide(self):
        if not self.visible: return
        self.visible = False
        self.grid_forget()

class ToolbarFlatSeparator(ToolbarSeparator):
    pass

class ToolbarLabel(Tkinter.Message):
    def __init__(self, parent, toolbar, toolbar_name, position, **kwargs):
        Tkinter.Message.__init__(self, parent, kwargs)
        self.toolbar = toolbar
        self.toolbar_name = toolbar_name
        self.position = position
        self.visible = False
    def show(self, orient, force=False):
        if self.visible and not force:
            return
        self.visible = True
        padx, pady = TkSettings.toolbar_label_padding
        if orient == 'horizontal':
            self.grid(row=0,
                      column=self.position,
                      padx=padx, pady=pady,
                      sticky='nsew')
        else:
            self.grid(row=self.position,
                      column=0,
                      padx=padx, pady=pady,
                      sticky='nsew')
    def hide(self):
        if not self.visible: return
        self.visible = False
        self.grid_forget()


# ************************************************************************
# * Note: Applications should call show/hide after constructor.
# ************************************************************************

class PysolToolbarTk:

    def __init__(self, top, menubar, dir,
                 size=0, relief='flat', compound='none'):
        self.top = top
        self.menubar = menubar
        #self._setRelief(relief)
        self.side = -1
        self._tooltips = []
        self._widgets = []
        self.dir = dir
        self.size = size
        self.compound = compound
        self.orient = 'horizontal'
        self.button_pad = 2
        #
        self.frame = Tkinter.Frame(top, relief=TkSettings.toolbar_relief,
                                   bd=TkSettings.toolbar_borderwidth)
        #
        for l, f, t in (
            (n_("New"),      self.mNewGame,   _("New game")),
            (n_("Restart"),  self.mRestart,   _("Restart the\ncurrent game")),
            (None,           None,            None),
            (n_("Open"),     self.mOpen,      _("Open a\nsaved game")),
            (n_("Save"),     self.mSave,      _("Save game")),
            (None,           None,            None),
            (n_("Undo"),     self.mUndo,      _("Undo last move")),
            (n_("Redo"),     self.mRedo,      _("Redo last move")),
            (n_("Autodrop"), self.mDrop,      _("Auto drop cards")),
            (n_("Shuffle"),  self.mShuffle,   _("Shuffle tiles")),
            (n_("Pause"),    self.mPause,     _("Pause game")),
            (None,           None,            None),
            (n_("Statistics"), self.mPlayerStats, _("View statistics")),
            (n_("Rules"),    self.mHelpRules, _("Rules for this game")),
            (None,           None,            None),
            (n_("Quit"),     self.mQuit,      _("Quit ")+TITLE),
            ):
            if l is None:
                sep = self._createSeparator()
                sep.bind("<1>", self.clickHandler)
                sep.bind("<3>", self.rightclickHandler)
            elif l == 'Pause':
                self._createButton(l, f, check=True, tooltip=t)
            else:
                self._createButton(l, f, tooltip=t)
        self.pause_button.config(variable=menubar.tkopt.pause)

        sep = self._createFlatSeparator()
        sep.bind("<1>", self.clickHandler)
        sep.bind("<3>", self.rightclickHandler)
        self._createLabel("player", label=n_('Player'),
                          tooltip=_("Player options"))
        #
        self.player_label.bind("<1>",self.mOptPlayerOptions)
        ##self.player_label.bind("<3>",self.mOptPlayerOptions)
        self.popup = MfxMenu(master=None, label=n_('Toolbar'), tearoff=0)
        createToolbarMenu(menubar, self.popup)
        self.frame.bind("<1>", self.clickHandler)
        self.frame.bind("<3>", self.rightclickHandler)
        #
        self.setCompound(compound, force=True)

    def config(self, w, v):
        if w == 'player':
            # label
            if v:
                self.player_label.show(orient=self.orient)
            else:
                self.player_label.hide()
        else:
            # button
            widget = getattr(self, w+'_button')
            position = widget.position
            if v:
                widget.show(orient=self.orient)
            else:
                widget.hide()
        #
        prev_visible = None
        last_visible = None
        for w in self._widgets:
            if w.__class__ is ToolbarSeparator:
                if prev_visible is None or prev_visible.__class__ is ToolbarSeparator:
                    w.hide()
                else:
                    w.show(orient=self.orient)
            elif w.__class__ is ToolbarFlatSeparator:
                if prev_visible.__class__ is ToolbarSeparator:
                    prev_visible.hide()
            if w.visible:
                prev_visible = w
                if not isinstance(w, ToolbarLabel):
                    last_visible = w
        if isinstance(last_visible, ToolbarSeparator):
            last_visible.hide()

    # util
    def _loadImage(self, name):
        file = os.path.join(self.dir, name)
        image = None
        for ext in IMAGE_EXTENSIONS:
            file = os.path.join(self.dir, name+ext)
            if os.path.isfile(file):
                if Image:
                    image = ImageTk.PhotoImage(Image.open(file))
                else:
                    image = Tkinter.PhotoImage(file=file)
                break
        return image

    def _createSeparator(self):
        position=len(self._widgets)
        sep = ToolbarSeparator(self.frame,
                               position=position,
                               toolbar=self,
                               bd=1,
                               highlightthickness=1,
                               width=4,
                               takefocus=0,
                               relief=TkSettings.toolbar_separator_relief)
        sep.show(orient=self.orient)
        self._widgets.append(sep)
        return sep

    def _createFlatSeparator(self):
        position=len(self._widgets)
        sep = ToolbarFlatSeparator(self.frame,
                                   position=position,
                                   toolbar=self,
                                   bd=1,
                                   highlightthickness=1,
                                   width=5,
                                   takefocus=0,
                                   relief='flat')
        sep.show(orient=self.orient)
        self.frame.rowconfigure(position, weight=1)
        self.frame.columnconfigure(position, weight=1)
        self._widgets.append(sep)
        return sep

    def _createButton(self, label, command, check=False, tooltip=None):
        name = label.lower()
        image = self._loadImage(name)
        position = len(self._widgets)
        button_relief = TkSettings.toolbar_button_relief
        bd = TkSettings.toolbar_button_borderwidth
        padx, pady = TkSettings.toolbar_button_padding
        kw = {
            'position'     : position,
            'toolbar'      : self,
            'toolbar_name' : name,
            'command'      : command,
            'takefocus'    : 0,
            'text'         : _(label),
            'bd'           : bd,
            'relief'       : button_relief,
            'padx'         : padx,
            'pady'         : pady,
            'overrelief'   : 'raised',
            }
        if image:
            kw['image'] = image
        if check:
            kw['offrelief'] = button_relief
            kw['indicatoron'] = False
            kw['selectcolor'] = ''
            button = ToolbarCheckbutton(self.frame, **kw)
        else:
            button = ToolbarButton(self.frame, **kw)
        button.show(orient=self.orient)
        setattr(self, name + "_image", image)
        setattr(self, name + "_button", button)
        self._widgets.append(button)
        if tooltip:
            b = MfxTooltip(button)
            self._tooltips.append(b)
            b.setText(tooltip)
        return button

    def _createLabel(self, name, label=None, tooltip=None):
        aspect = (400, 300) [self.getSize() != 0]
        position = len(self._widgets)
        label = ToolbarLabel(self.frame,
                             position=position,
                             toolbar=self,
                             toolbar_name=name,
                             relief="ridge",
                             justify="center",
                             aspect=aspect)
        label.show(orient=self.orient)
        setattr(self, name + "_label", label)
        self._widgets.append(label)
        if tooltip:
            b = MfxTooltip(label)
            self._tooltips.append(b)
            b.setText(tooltip)
        return label

    def _busy(self):
        if not self.side or not self.game or not self.menubar:
            return 1
        self.game.stopDemo()
        self.game.interruptSleep()
        return self.game.busy


    #
    # public methods
    #

    def show(self, side=1, resize=1):
        if self.side == side:
            return 0
        if resize:
            self.top.wm_geometry("")    # cancel user-specified geometry
        if not side:
            # hide
            self.frame.grid_forget()
        else:
            # show
            pack_func = self.frame.grid_configure

            if side == 1:
                # top
                pack_func(row=0, column=1, sticky='ew')
            elif side == 2:
                # bottom
                pack_func(row=2, column=1, sticky='ew')
            elif side == 3:
                # left
                pack_func(row=1, column=0, sticky='ns')
            else:
                # right
                pack_func(row=1, column=2, sticky='ns')
            # set orient
            orient = side in (1, 2) and 'horizontal' or 'vertical'
            self._setOrient(orient)
        self.side = side
        return 1

    def hide(self, resize=1):
        self.show(0, resize)

    def destroy(self):
        for w in self._tooltips:
            if w: w.destroy()
        self._tooltips = []
        for w in self._widgets:
            if w: w.destroy()
        self._widgets = []

    def setCursor(self, cursor):
        if self.side:
            self.frame.config(cursor=cursor)
            self.frame.update_idletasks()

    def updateText(self, **kw):
        for name in kw.keys():
            label = getattr(self, name + "_label")
            label["text"] = kw[name]

    def updateImages(self, dir, size):
        if dir == self.dir and size == self.size:
            return 0
        if not os.path.isdir(dir):
            return 0
        old_dir, old_size = self.dir, self.size
        self.dir, self.size = dir, size
        data = []
        try:
            for w in self._widgets:
                if not isinstance(w, (ToolbarButton, ToolbarCheckbutton)):
                    continue
                name = w.toolbar_name
                image = self._loadImage(name)
                data.append((name, w, image))
        except:
            self.dir, self.size = old_dir, old_size
            return 0
        l = self.player_label
        aspect = (400, 300) [size != 0]
        l.config(aspect=aspect)
        for name, w, image in data:
            w.config(image=image)
            setattr(self, name + "_image", image)
        self.setCompound(self.compound, force=True)
        return 1

    def setCompound(self, compound, force=False):
        if not force and self.compound == compound:
            return False
        for w in self._widgets:
            if not isinstance(w, (ToolbarButton, ToolbarCheckbutton)):
                continue
            if compound == 'text':
                w.config(compound='none', image='')
            else:
                image = getattr(self, w.toolbar_name+'_image')
                w.config(compound=compound, image=image)
        self.compound = compound
        return True

    def _setOrient(self, orient='horizontal', force=False):
        if not force and self.orient == orient:
            return False
        for w in self._widgets:
            if w.visible:
                w.show(orient=orient, force=True)
        self.orient = orient
        return True

    #
    # Mouse event handlers
    #

    def clickHandler(self, event):
        if self._busy(): return EVENT_HANDLED
        return EVENT_HANDLED

    def rightclickHandler(self, event):
        if self._busy(): return EVENT_HANDLED
        if self.popup:
            ##print event.x, event.y, event.x_root, event.y_root, event.__dict__
            self.popup.tk_popup(event.x_root, event.y_root)
        return EVENT_HANDLED

    def middleclickHandler(self, event):
        if self._busy(): return EVENT_HANDLED
        if 1 <= self.side <= 2:
            self.menubar.setToolbarSide(3 - self.side)
        return EVENT_HANDLED

    def getSize(self):
        if self.compound == 'text':
            return 0
        size = self.size
        comp = int(self.compound in ('top', 'bottom'))
        return int((size+comp) != 0)

