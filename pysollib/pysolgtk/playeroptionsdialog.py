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

__all__ = ['PlayerOptionsDialog']

# imports
import gobject, gtk

# PySol imports

# Toolkit imports
from tkwidget import MfxDialog
from pysollib.mfxutil import kwdefault


# ************************************************************************
# *
# ************************************************************************

class PlayerOptionsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, **kw)
        #
        top_box, bottom_box = self.createVBox()
        #
        label = gtk.Label('Please enter your name')
        label.show()
        top_box.pack_start(label)
        self.player_entry = gtk.Entry()
        self.player_entry.show()
        top_box.pack_start(self.player_entry, expand=False)
        completion = gtk.EntryCompletion()
        self.player_entry.set_completion(completion)
        model = gtk.ListStore(gobject.TYPE_STRING)
        for name in app.getAllUserNames():
            iter = model.append()
            model.set(iter, 0, name)
        completion.set_model(model)
        completion.set_text_column(0)
        self.player_entry.set_text(app.opt.player)
        #
        self.confirm_quit_check = gtk.CheckButton(_('Confirm quit'))
        self.confirm_quit_check.show()
        top_box.pack_start(self.confirm_quit_check)
        self.confirm_quit_check.set_active(app.opt.confirm != 0)
        #
        self.update_stats_check = gtk.CheckButton(_('Update statistics and logs'))
        self.update_stats_check.show()
        top_box.pack_start(self.update_stats_check)
        self.update_stats_check.set_active(app.opt.update_player_stats != 0)
        #
        self.createButtons(bottom_box, kw)
        self.show_all()
        gtk.main()


    def initKw(self, kw):
        kwdefault(kw,
                  strings=(_('&OK'), _('&Cancel'),),
                  default=0,
                  #resizable=1,
                  padx=10, pady=10,
                  #width=600, height=400,
                  ##~ buttonpadx=10, buttonpady=5,
                  )
        return MfxDialog.initKw(self, kw)


    def done(self, button):
        self.button = button.get_data('user_data')
        self.player = self.player_entry.get_text()
        self.confirm = self.confirm_quit_check.get_active()
        self.update_stats = self.update_stats_check.get_active()
        self.win_animation = False
        self.quit()



