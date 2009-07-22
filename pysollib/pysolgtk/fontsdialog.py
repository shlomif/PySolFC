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

__all__ = ['FontsDialog']

# imports
## import os, sys
## import types
import gtk, gobject, pango
import gtk.glade

# PySol imports
from tkutil import create_pango_font_desc


# ************************************************************************
# *
# ************************************************************************

class FontsDialog:

    def __init__(self, parent, title, app, **kw):
        glade_file = app.dataloader.findFile('pysolfc.glade')
        self.widgets_tree = gtk.glade.XML(glade_file)

        keys = (
            'sans',
            'small',
            'fixed',
            'canvas_default',
            'canvas_fixed',
            'canvas_large',
            'canvas_small',
            )

        for n in keys:
            font = app.opt.fonts[n]
            self._setFont(n, font)
            button = self.widgets_tree.get_widget(n+'_button')
            button.connect('clicked', self._changeFont, n)

        self._translateLabels()

        dialog = self.widgets_tree.get_widget('fonts_dialog')
        self.dialog = dialog
        dialog.set_title(title)
        dialog.set_transient_for(parent)

        self.status = -1
        self.button = -1
        self.fonts = {}
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.status = 0
            self.button = 0
            for n in keys:
                label = self.widgets_tree.get_widget(n+'_label')
                font = label.get_data('user_data')
                self.fonts[n] = font

        dialog.destroy()


    def _setFont(self, name, font):
        label = self.widgets_tree.get_widget(name+'_label')
        font_desc = create_pango_font_desc(font)
        label.modify_font(font_desc)
        text = ' '.join([str(i) for i in font if i not in ('roman', 'normal')])
        label.set_text(text)
        label.set_data('user_data', font)


    def _changeFont(self, w, name):
        label = self.widgets_tree.get_widget(name+'_label')
        font = label.get_data('user_data')
        dialog = gtk.FontSelectionDialog(_('Select color'))
        dialog.set_transient_for(self.dialog)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        font_name = font[0]
        bi = []
        if 'bold' in font:
            bi.append('bold')
        if 'italic' in font:
            bi.append('italic')
        if bi:
            bi = ' '.join(bi)
            font_name += ', '+bi
        font_name += ' '+str(font[1])
        dialog.fontsel.set_font_name(font_name)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            font = dialog.fontsel.get_font_name()
            fd = pango.FontDescription(font)
            family = fd.get_family()
            size = fd.get_size()/pango.SCALE
            style = (fd.get_style() == pango.STYLE_NORMAL
                     and 'roman' or 'italic')
            weight = (fd.get_weight() == pango.WEIGHT_NORMAL
                      and 'normal' or 'bold')
            font = (family, size, style, weight)
            self._setFont(name, font)

        dialog.destroy()


    def _translateLabels(self):
        for n in (
            'label54',
            'label55',
            'label56',
            'label57',
            'label58',
            'label59',
            'label60',
            'label69',
            'label70',
            'label71',
            'label72',
            'label73',
            'label74',
            'label75',
            ):
            w = self.widgets_tree.get_widget(n)
            w.set_text(_(w.get_text()))




