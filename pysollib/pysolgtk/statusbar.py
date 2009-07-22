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

# PySol imports


# ************************************************************************
# *
# ************************************************************************

class BasicStatusbar:
    def __init__(self, top, row, column, columnspan):
        self.top = top
        self._widgets = []
        self.hbox = gtk.HBox()
        top.table.attach(self.hbox,
                         column, column+columnspan,   row, row+1,
                         gtk.EXPAND | gtk.FILL,       0,
                         0,                           0)


    def createLabel(self, name, fill=False, expand=False,
                    tooltip=None, grip=False, width=0):
        label = gtk.Statusbar()
        self.hbox.pack_start(label, fill=fill, expand=expand)
        label.show()
        if not grip:
            label.set_has_resize_grip(False)
        setattr(self, name + "_label", label)
        label.set_size_request(width*7, -1)
        lb = label.get_children()[0].get_children()[0]
        lb.set_alignment(0.5, 0.0)
        self._widgets.append(label)
        ##label.push(0, '')
##         if tooltip:
##             tt = gtk.Tooltips()
##             tt.set_tip(label, tooltip, '')
##             tt.enable()


    def updateText(self, **kw):
        for k, v in kw.items():
            label = getattr(self, k + "_label")
            label.pop(0)
            label.push(0, unicode(v))

    def config(self, name, show):
        # FIXME
        pass

    def configLabel(self, name, **kw):
        label = getattr(self, name + "_label")
        # FIXME kw['fg']
        label.pop(0)
        label.push(0, unicode(kw['text']))


    def show(self, show=True, resize=False):
        if show:
            self.hbox.show()
        else:
            self.hbox.hide()
        return True

    def hide(self, resize=False):
        self.show(False, resize)
        return True


    def destroy(self):
        pass


# ************************************************************************
# *
# ************************************************************************
class PysolStatusbar(BasicStatusbar):
    def __init__(self, top):
        BasicStatusbar.__init__(self, top, row=4, column=0, columnspan=3)
        #
        for n, t, w in (
            ("time",        _("Playing time"),            10),
            ("moves",       _('Moves/Total moves'),       10),
            ("gamenumber",  _("Game number"),             26),
            ("stats",       _("Games played: won/lost"),  12),
            ):
            self.createLabel(n, width=w, tooltip=t)
        #
        l = self.createLabel("info", fill=True, expand=True, grip=True)



class HelpStatusbar(BasicStatusbar):
    def __init__(self, top):
        BasicStatusbar.__init__(self, top, row=5, column=0, columnspan=3)
        self.createLabel("info", fill=True, expand=True)


