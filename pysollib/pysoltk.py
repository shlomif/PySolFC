#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

from pysollib.settings import TOOLKIT, USE_TILE

if TOOLKIT == 'tk':
    from pysollib.ui.tktile.tkconst import *
    from pysollib.ui.tktile.tkutil import *
    from pysollib.ui.tktile.card import *
    from pysollib.ui.tktile.tkcanvas import *
    from pysollib.ui.tktile.tkwrap import *
    from pysollib.ui.tktile.findcarddialog import *
    if USE_TILE:
        from pysollib.tile.tkwidget import *
        from pysollib.tile.tkhtml import *
        from pysollib.tile.edittextdialog import *
        from pysollib.tile.tkstats import *
        from pysollib.tile.playeroptionsdialog import *
        from pysollib.tile.soundoptionsdialog import *
        from pysollib.tile.timeoutsdialog import *
        from pysollib.tile.colorsdialog import *
        from pysollib.tile.fontsdialog import *
        from pysollib.tile.solverdialog import *
        from pysollib.tile.gameinfodialog import *
        from pysollib.tile.toolbar import *
        from pysollib.tile.statusbar import *
        from pysollib.tile.progressbar import *
        from pysollib.tile.menubar import *
        from pysollib.tile.selectcardset import *
        from pysollib.tile.selecttree import *
    else:
        from pysollib.tk.tkwidget import *
        from pysollib.tk.tkhtml import *
        from pysollib.tk.edittextdialog import *
        from pysollib.tk.tkstats import *
        from pysollib.tk.playeroptionsdialog import *
        from pysollib.tk.soundoptionsdialog import *
        from pysollib.tk.timeoutsdialog import *
        from pysollib.tk.colorsdialog import *
        from pysollib.tk.fontsdialog import *
        from pysollib.tk.solverdialog import *
        from pysollib.tk.gameinfodialog import *
        from pysollib.tk.toolbar import *
        from pysollib.tk.statusbar import *
        from pysollib.tk.progressbar import *
        from pysollib.tk.menubar import *
        from pysollib.tk.selectcardset import *
        from pysollib.tk.selecttree import *

else: # gtk
    from pysollib.pysolgtk.tkconst import *
    from pysollib.pysolgtk.tkutil import *
    from pysollib.pysolgtk.tkcanvas import *
    from pysollib.pysolgtk.tkwrap import *
    from pysollib.pysolgtk.tkwidget import *
    from pysollib.pysolgtk.tkhtml import *
    from pysollib.pysolgtk.edittextdialog import *
    from pysollib.pysolgtk.tkstats import *
    from pysollib.pysolgtk.playeroptionsdialog import *
    from pysollib.pysolgtk.soundoptionsdialog import *
    from pysollib.pysolgtk.timeoutsdialog import *
    from pysollib.pysolgtk.colorsdialog import *
    from pysollib.pysolgtk.fontsdialog import *
    from pysollib.pysolgtk.findcarddialog import *
    from pysollib.pysolgtk.solverdialog import *
    from pysollib.pysolgtk.gameinfodialog import *
    from pysollib.pysolgtk.toolbar import *
    from pysollib.pysolgtk.statusbar import *
    from pysollib.pysolgtk.progressbar import *
    from pysollib.pysolgtk.menubar import *
    from pysollib.pysolgtk.card import *
    from pysollib.pysolgtk.selectcardset import *

