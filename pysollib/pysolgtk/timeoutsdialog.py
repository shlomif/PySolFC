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

__all__ = ['TimeoutsDialog']

# imports
## import os, sys
import gtk, gobject, pango
import gtk.glade


# ************************************************************************
# *
# ************************************************************************

class TimeoutsDialog:

    def __init__(self, parent, title, app, **kw):

        glade_file = app.dataloader.findFile('pysolfc.glade')
        self.widgets_tree = gtk.glade.XML(glade_file)

        keys = (
            'demo',
            'hint',
            'raise_card',
            'highlight_piles',
            'highlight_cards',
            'highlight_samerank',
            )

        dic = {}
        for n in keys:
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

        for n in keys:
            v = app.opt.timeouts[n]
            w = self.widgets_tree.get_widget(n+'_spinbutton')
            w.set_value(v)
            w = self.widgets_tree.get_widget(n+'_scale')
            w.set_value(v)

        self._translateLabels()

        dialog = self.widgets_tree.get_widget('timeouts_dialog')
        dialog.set_title(title)
        dialog.set_transient_for(parent)

        self.status = -1
        self.button = -1
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.status = 0
            self.button = 0
        for n in keys:
            w = self.widgets_tree.get_widget(n+'_spinbutton')
            setattr(self, n+'_timeout', w.get_value())

        dialog.destroy()

    def _translateLabels(self):
        for n in (
            'label25',
            'label26',
            'label27',
            'label28',
            'label29',
            'label30',
            ):
            w = self.widgets_tree.get_widget(n)
            w.set_text(_(w.get_text()))

