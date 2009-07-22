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

__all__ = ['ColorsDialog']

# imports
## import os, sys
import gtk, gobject, pango
import gtk.glade
from gtk import gdk


# ************************************************************************
# *
# ************************************************************************

class ColorsDialog:

    def __init__(self, parent, title, app, **kw):

        glade_file = app.dataloader.findFile('pysolfc.glade')
        self.widgets_tree = gtk.glade.XML(glade_file)

        keys = (
            'text',
            'piles',
            'cards_1',
            'cards_2',
            'samerank_1',
            'samerank_2',
            'hintarrow',
            'not_matching',
            )
        for n in keys:
            self._setColor(n, app.opt.colors[n])
            button = self.widgets_tree.get_widget(n+'_button')
            button.connect('clicked', self._changeColor, n)

        self._translateLabels()

        dialog = self.widgets_tree.get_widget('colors_dialog')
        self.dialog = dialog
        dialog.set_title(title)
        dialog.set_transient_for(parent)

        self.status = -1
        self.button = -1
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.status = 0
            self.button = 0
            for n in keys:
                w = self.widgets_tree.get_widget(n+'_label')
                c = w.get_data('user_data')
                setattr(self, n+'_color', c)

        dialog.destroy()


    def _setColor(self, name, color):
        label = self.widgets_tree.get_widget(name+'_label')
        eventbox = self.widgets_tree.get_widget(name+'_eventbox')
        eventbox.modify_bg(gtk.STATE_NORMAL, gdk.color_parse(color))
        label.set_data('user_data', color)
        label.set_text(color)


    def _changeColor(self, w, name):
        label = self.widgets_tree.get_widget(name+'_label')
        color = label.get_data('user_data')
        dialog = gtk.ColorSelectionDialog(_('Select color'))
        dialog.help_button.destroy()
        dialog.set_transient_for(self.dialog)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.colorsel.set_current_color(gdk.color_parse(color))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            c = dialog.colorsel.get_current_color()
            c = '#%02x%02x%02x' % (c.red/256, c.green/256, c.blue/256)
            self._setColor(name, c)
        dialog.destroy()


    def _translateLabels(self):
        for n in (
            'label31',
            'label32',
            'label33',
            'label34',
            'label35',
            'label36',
            'label37',
            'label46',
            'label47',
            'label48',
            'label49',
            'label50',
            'label51',
            'label52',
            'label53',
            'label79',
            ):
            w = self.widgets_tree.get_widget(n)
            w.set_text(_(w.get_text()))

