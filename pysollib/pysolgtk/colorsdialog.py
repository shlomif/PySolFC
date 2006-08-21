##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
##---------------------------------------------------------------------------##

__all__ = ['ColorsDialog']

# imports
## import os, sys
import gtk, gobject, pango
import gtk.glade
from gtk import gdk

# PySol imports

# Toolkit imports


gettext = _

# /***********************************************************************
# //
# ************************************************************************/

class ColorsDialog:

## self.app.opt.table_text_color = d.table_text_color
## self.app.opt.table_text_color_value = d.table_text_color_value
## ##self.app.opt.table_color = d.table_color
## self.app.opt.highlight_piles_colors = d.highlight_piles_colors
## self.app.opt.highlight_cards_colors = d.highlight_cards_colors
## self.app.opt.highlight_samerank_colors = d.highlight_samerank_colors
## self.app.opt.hintarrow_color = d.hintarrow_color
## self.app.opt.highlight_not_matching_color = d.highlight_not_matching_color

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
            label = self.widgets_tree.get_widget(n+'_label')
            self._setColor(label, app.opt.colors[n])
            button = self.widgets_tree.get_widget(n+'_button')
            button.connect('clicked', self._changeColor, n, label)
        checkbutton = self.widgets_tree.get_widget('use_default_checkbutton')
        checkbutton.set_active(not app.opt.use_default_text_color)

        self._translateLabels()

        dialog = self.widgets_tree.get_widget('colors_dialog')
        self.dialog = dialog
        dialog.set_title(title)
        dialog.set_transient_for(parent)
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

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
            self.use_default_color = not checkbutton.get_active()

        dialog.destroy()


    def _setColor(self, label, color):
        c = gdk.color_parse(color)
        al = pango.AttrList()
        al.insert(pango.AttrBackground(c.red, c.green, c.blue, 0, 10))
        label.set_attributes(al)
        label.set_data('user_data', color)


    def _changeColor(self, w, name, label):
        print '_changeColor', name
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
            self._setColor(label, c)
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
            ):
            w = self.widgets_tree.get_widget(n)
            w.set_text(gettext(w.get_text()))


