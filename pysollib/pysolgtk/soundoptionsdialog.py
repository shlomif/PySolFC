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
import os, sys
import gtk
from gtk import glade

# PySol imports

# Toolkit imports
from tkwidget import MfxDialog


# ************************************************************************
# *
# ************************************************************************

class SoundOptionsDialog:
    def __init__(self, parent, title, app, **kw):
        saved_opt = app.opt.copy()

        glade_file = app.dataloader.findFile('pysolfc.glade')
        self.widgets_tree = gtk.glade.XML(glade_file)

        keys = [
            ('areyousure',    _('Are You Sure')),

            ('deal',          _('Deal')),
            ('dealwaste',     _('Deal waste')),

            ('turnwaste',     _('Turn waste')),
            ('startdrag',     _('Start drag')),

            ('drop',          _('Drop')),
            ('droppair',      _('Drop pair')),
            ('autodrop',      _('Auto drop')),

            ('flip',          _('Flip')),
            ('autoflip',      _('Auto flip')),
            ('move',          _('Move')),
            ('nomove',        _('No move')),

            ('undo',          _('Undo')),
            ('redo',          _('Redo')),

            ('autopilotlost', _('Autopilot lost')),
            ('autopilotwon',  _('Autopilot won')),

            ('gamefinished',  _('Game finished')),
            ('gamelost',      _('Game lost')),
            ('gamewon',       _('Game won')),
            ('gameperfect',   _('Perfect game')),
            ]

        table = self.widgets_tree.get_widget('samples_table')
        samples_checkbuttons = {}
        row = 0
        col = 0
        for n, t in keys:
            check = gtk.CheckButton(t)
            check.show()
            check.set_active(app.opt.sound_samples[n])
            samples_checkbuttons[n] = check
            table.attach(check,
                         col, col+1,              row, row+1,
                         gtk.FILL|gtk.EXPAND,     gtk.FILL,
                         4,                       4)
            if col == 1:
                col = 0
                row += 1
            else:
                col = 1

        w = self.widgets_tree.get_widget('enable_checkbutton')
        w.set_active(app.opt.sound)
        dic = {}
        for n in 'sample', 'music':
            def callback(w, n=n):
                sp = self.widgets_tree.get_widget(n+'_spinbutton')
                sc = self.widgets_tree.get_widget(n+'_scale')
                sp.set_value(sc.get_value())
            dic[n+'_scale_value_changed'] = callback
            def callback(w, n=n):
                sp = self.widgets_tree.get_widget(n+'_spinbutton')
                sc = self.widgets_tree.get_widget(n+'_scale')
                sc.set_value(sp.get_value())
            dic[n+'_spinbutton_value_changed'] = callback
        self.widgets_tree.signal_autoconnect(dic)
        w = self.widgets_tree.get_widget('sample_spinbutton')
        w.set_value(app.opt.sound_sample_volume)
        w = self.widgets_tree.get_widget('music_spinbutton')
        w.set_value(app.opt.sound_music_volume)

        self._translateLabels()

        dialog = self.widgets_tree.get_widget('sounds_dialog')
        dialog.set_title(title)
        dialog.set_transient_for(parent)

        while True:  # for `apply'
            response = dialog.run()
            if response in (gtk.RESPONSE_OK, gtk.RESPONSE_APPLY):
                w = self.widgets_tree.get_widget('enable_checkbutton')
                app.opt.sound = w.get_active()
                w = self.widgets_tree.get_widget('sample_spinbutton')
                app.opt.soun_sample_volume = w.get_value()
                w = self.widgets_tree.get_widget('music_spinbutton')
                app.opt.sound_music_volume = w.get_value()
                for n, t in keys:
                    w = samples_checkbuttons[n]
                    app.opt.sound_samples[n] = w.get_active()
            else:
                app.opt = saved_opt
            if app.audio:
                app.audio.updateSettings()
                if response == gtk.RESPONSE_APPLY:
                    app.audio.playSample('drop', priority=1000)
            if response != gtk.RESPONSE_APPLY:
                dialog.destroy()
                break


    def _translateLabels(self):
        for n in (
            'label76',
            'label77',
            'label78',
            ):
            w = self.widgets_tree.get_widget(n)
            w.set_text(_(w.get_text()))
        w = self.widgets_tree.get_widget('enable_checkbutton')
        w.set_label(_(w.get_label()))

