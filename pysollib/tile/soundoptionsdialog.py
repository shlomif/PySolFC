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

__all__ = ['SoundOptionsDialog']

# imports
import os
import Tkinter
import ttk

# PySol imports
from pysollib.mfxutil import KwStruct
from pysollib.settings import TITLE
from pysollib.pysolaudio import pysolsoundserver

# Toolkit imports
from tkconst import EVENT_HANDLED
from tkwidget import MfxDialog, MfxMessageDialog
from tkwidget import PysolScale


# ************************************************************************
# *
# ************************************************************************

class SoundOptionsDialog(MfxDialog):

    def __init__(self, parent, title, app, **kw):
        self.app = app
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.saved_opt = app.opt.copy()
        self.sound = Tkinter.BooleanVar()
        self.sound.set(app.opt.sound != 0)
        self.sound_mode = Tkinter.BooleanVar()
        self.sound_mode.set(app.opt.sound_mode != 0)
        self.sample_volume = Tkinter.IntVar()
        self.sample_volume.set(app.opt.sound_sample_volume)
        self.music_volume = Tkinter.IntVar()
        self.music_volume.set(app.opt.sound_music_volume)
        self.samples = [
            ('areyousure',    _('Are You Sure'),   Tkinter.BooleanVar()),

            ('deal',          _('Deal'),           Tkinter.BooleanVar()),
            ('dealwaste',     _('Deal waste'),     Tkinter.BooleanVar()),

            ('turnwaste',     _('Turn waste'),     Tkinter.BooleanVar()),
            ('startdrag',     _('Start drag'),     Tkinter.BooleanVar()),

            ('drop',          _('Drop'),           Tkinter.BooleanVar()),
            ('droppair',      _('Drop pair'),      Tkinter.BooleanVar()),
            ('autodrop',      _('Auto drop'),      Tkinter.BooleanVar()),

            ('flip',          _('Flip'),           Tkinter.BooleanVar()),
            ('autoflip',      _('Auto flip'),      Tkinter.BooleanVar()),
            ('move',          _('Move'),           Tkinter.BooleanVar()),
            ('nomove',        _('No move'),        Tkinter.BooleanVar()),

            ('undo',          _('Undo'),           Tkinter.BooleanVar()),
            ('redo',          _('Redo'),           Tkinter.BooleanVar()),

            ('autopilotlost', _('Autopilot lost'), Tkinter.BooleanVar()),
            ('autopilotwon',  _('Autopilot won'),  Tkinter.BooleanVar()),

            ('gamefinished',  _('Game finished'),  Tkinter.BooleanVar()),
            ('gamelost',      _('Game lost'),      Tkinter.BooleanVar()),
            ('gamewon',       _('Game won'),       Tkinter.BooleanVar()),
            ('gameperfect',   _('Perfect game'),   Tkinter.BooleanVar()),
            ]

        #
        frame = ttk.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=5)
        frame.columnconfigure(1, weight=1)
        #
        row = 0
        w = ttk.Checkbutton(frame, variable=self.sound,
                            text=_("Sound enabled"))
        w.grid(row=row, column=0, columnspan=2, sticky='ew')
        #
        if os.name == "nt" and pysolsoundserver:
            row += 1
            w = ttk.Checkbutton(frame, variable=self.sound_mode,
                                text=_("Use DirectX for sound playing"),
                                command=self.mOptSoundDirectX)
            w.grid(row=row, column=0, columnspan=2, sticky='ew')
        #
        if app.audio.CAN_PLAY_MUSIC: # and app.startup_opt.sound_mode > 0:
            row += 1
            ttk.Label(frame, text=_('Sample volume:'), anchor='w'
                      ).grid(row=row, column=0, sticky='ew')
            w = PysolScale(frame, from_=0, to=128, resolution=1,
                           orient='horizontal', takefocus=0,
                           length="3i", #label=_('Sample volume'),
                           variable=self.sample_volume)
            w.grid(row=row, column=1, sticky='w', padx=5)
            row += 1
            ttk.Label(frame, text=_('Music volume:'), anchor='w'
                      ).grid(row=row, column=0, sticky='ew')
            w = PysolScale(frame, from_=0, to=128, resolution=1,
                           orient='horizontal', takefocus=0,
                           length="3i", #label=_('Music volume'),
                           variable=self.music_volume)
            w.grid(row=row, column=1, sticky='w', padx=5)

        else:
            # remove "Apply" button
            kw.strings[1] = None
        #
        frame = ttk.LabelFrame(top_frame, text=_('Enable samples'))
        frame.pack(expand=True, fill='both', padx=5, pady=5)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        #
        row = 0
        col = 0
        for n, t, v in self.samples:
            v.set(app.opt.sound_samples[n])
            w = ttk.Checkbutton(frame, text=t, variable=v)
            w.grid(row=row, column=col, sticky='ew', padx=3, pady=1)
            if col == 1:
                col = 0
                row += 1
            else:
                col = 1
        #
        top_frame.columnconfigure(1, weight=1)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        strings=[_("&OK"), _("&Apply"), _("&Cancel"),]
        kw = KwStruct(kw,
                      strings=strings,
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        if button == 0 or button == 1:
            self.app.opt.sound = self.sound.get()
            self.app.opt.sound_mode = int(self.sound_mode.get())
            self.app.opt.sound_sample_volume = self.sample_volume.get()
            self.app.opt.sound_music_volume = self.music_volume.get()
            for n, t, v in self.samples:
                self.app.opt.sound_samples[n] = v.get()
        elif button == 2:
            self.app.opt = self.saved_opt
        if self.app.audio:
            self.app.audio.updateSettings()
            if button == 1:
                self.app.audio.playSample("drop", priority=1000)
        if button == 1:
            return EVENT_HANDLED
        return MfxDialog.mDone(self, button)

    def mCancel(self, *event):
        return self.mDone(2)

    def wmDeleteWindow(self, *event):
        return self.mDone(0)

    def mOptSoundDirectX(self, *event):
        ##print self.sound_mode.get()
        d = MfxMessageDialog(self.top, title=_("Sound preferences info"),
                      text=_("""\
Changing DirectX settings will take effect
the next time you restart """)+TITLE,
                      bitmap="warning",
                      default=0, strings=(_("&OK"),))

