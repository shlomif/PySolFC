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
import os, re, sys, types
import gtk, gobject

# PySol imports

# Toolkit imports


# ************************************************************************
# *
# ************************************************************************

class PysolTreeView:

    _expanded_rows = []
    _selected_row = None
    _vadjustment_position = None

    def __init__(self, parent, store, **kw):
        #
        sw = gtk.ScrolledWindow()
        self.scrolledwindow = sw
        sw.show()
        self.sw_vadjustment = sw.get_vadjustment()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #
        treeview = gtk.TreeView(store)
        self.treeview = treeview
        treeview.show()
        sw.add(treeview)
        treeview.set_rules_hint(True)
        treeview.set_headers_visible(False)
        renderer = gtk.CellRendererText()
        renderer.set_property('xalign', 0.0)
        column = gtk.TreeViewColumn('Column Name', renderer, text=0)
        column.set_clickable(True)
        treeview.append_column(column)
        selection = treeview.get_selection()
        selection.connect('changed', parent.showSelected)
        treeview.connect('unrealize', self._unrealizeEvent)

        self._restoreSettings()


    def _unrealizeEvent(self, w):
        self._saveSettings()


    def _saveSettings(self):
        self._saveExpandedRows()
        selection = self.treeview.get_selection()
        model, path = selection.get_selected_rows()
        if path:
            PysolTreeView._selected_row = path[0]
        PysolTreeView._vadjustment_position = self.sw_vadjustment.get_value()

    def _restoreSettings(self):
        self._loadExpandedRows()
        if self._selected_row:
            selection = self.treeview.get_selection()
            ##selection.select_path(self._selected_row)
            ##selection.unselect_all()
            gobject.idle_add(selection.select_path, self._selected_row)
        if self._vadjustment_position is not None:
            ##self.sw_vadjustment.set_value(self._vadjustment_position)
            gobject.idle_add(self.sw_vadjustment.set_value,
                             self._vadjustment_position)


    def _saveExpandedRows(self):
        treeview = self.treeview
        PysolTreeView._expanded_rows = []
        treeview.map_expanded_rows(
            lambda tv, path, self=self:
                PysolTreeView._expanded_rows.append(path))

    def _loadExpandedRows(self):
        for path in self._expanded_rows:
            self.treeview.expand_to_path(path)


    def getSelected(self):
        selection = self.treeview.get_selection()
        model, path = selection.get_selected_rows()
        if not path:
            return None
        iter = model.get_iter(path[0])
        index = model.get_value(iter, 1)
        return index


    def unselectAll(self):
        selection = self.treeview.get_selection()
        selection.unselect_all()








