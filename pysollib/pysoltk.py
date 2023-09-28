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
    from pysollib.ui.tktile.tkconst import *  # noqa: F401,F403
    from pysollib.ui.tktile.tkutil import *  # noqa: F401,F403
    from pysollib.ui.tktile.card import *  # noqa: F401,F403
    from pysollib.ui.tktile.tkcanvas import *  # noqa: F401,F403
    from pysollib.ui.tktile.tkwrap import *  # noqa: F401,F403
    from pysollib.ui.tktile.findcarddialog import *  # noqa: F401,F403
    from pysollib.ui.tktile.fullpicturedialog import *  # noqa: F401,F403
    if USE_TILE:
        from pysollib.tile.tkwidget import *  # noqa: F401,F403
        from pysollib.tile.tkhtml import *  # noqa: F401,F403
        from pysollib.tile.edittextdialog import *  # noqa: F401,F403
        from pysollib.tile.tkstats import *  # noqa: F401,F403
        from pysollib.tile.playeroptionsdialog import *  # noqa: F401,F403
        from pysollib.tile.soundoptionsdialog import *  # noqa: F401,F403
        from pysollib.tile.timeoutsdialog import *  # noqa: F401,F403
        from pysollib.tile.colorsdialog import *  # noqa: F401,F403
        from pysollib.tile.fontsdialog import *  # noqa: F401,F403
        from pysollib.tile.solverdialog import *  # noqa: F401,F403
        from pysollib.tile.gameinfodialog import *  # noqa: F401,F403
        from pysollib.tile.toolbar import *  # noqa: F401,F403
        from pysollib.tile.statusbar import *  # noqa: F401,F403
        from pysollib.tile.progressbar import *  # noqa: F401,F403
        from pysollib.tile.menubar import *  # noqa: F401,F403
        from pysollib.tile.selectcardset import *  # noqa: F401,F403
        from pysollib.tile.selecttree import *  # noqa: F401,F403
    else:
        from pysollib.tk.tkwidget import *  # noqa: F401,F403
        from pysollib.tk.tkhtml import *  # noqa: F401,F403
        from pysollib.tk.edittextdialog import *  # noqa: F401,F403
        from pysollib.tk.tkstats import *  # noqa: F401,F403
        from pysollib.tk.playeroptionsdialog import *  # noqa: F401,F403
        from pysollib.tk.soundoptionsdialog import *  # noqa: F401,F403
        from pysollib.tk.timeoutsdialog import *  # noqa: F401,F403
        from pysollib.tk.colorsdialog import *  # noqa: F401,F403
        from pysollib.tk.fontsdialog import *  # noqa: F401,F403
        from pysollib.tk.solverdialog import *  # noqa: F401,F403
        from pysollib.tk.gameinfodialog import *  # noqa: F401,F403
        from pysollib.tk.toolbar import *  # noqa: F401,F403
        from pysollib.tk.statusbar import *  # noqa: F401,F403
        from pysollib.tk.progressbar import *  # noqa: F401,F403
        from pysollib.tk.menubar import *  # noqa: F401,F403
        from pysollib.tk.selectcardset import *  # noqa: F401,F403
        from pysollib.tk.selecttree import *  # noqa: F401,F403

elif TOOLKIT == 'kivy':
    from pysollib.kivy.tkconst import *  # noqa: F401,F403
    from pysollib.kivy.tkutil import *  # noqa: F401,F403
    from pysollib.kivy.card import *  # noqa: F401,F403
    from pysollib.kivy.tkcanvas import *  # noqa: F401,F403
    from pysollib.kivy.tkwrap import *  # noqa: F401,F403
    from pysollib.kivy.findcarddialog import *  # noqa: F401,F403
    from pysollib.kivy.fullpicturedialog import *  # noqa: F401,F403
    from pysollib.kivy.tkwidget import *  # noqa: F401,F403
    from pysollib.kivy.tkhtml import *  # noqa: F401,F403
    from pysollib.kivy.edittextdialog import *  # noqa: F401,F403
    from pysollib.kivy.tkstats import *  # noqa: F401,F403
    from pysollib.kivy.playeroptionsdialog import *  # noqa: F401,F403
    # from pysollib.kivy.soundoptionsdialog import *  # noqa: F401,F403
    from pysollib.kivy.timeoutsdialog import *  # noqa: F401,F403
    from pysollib.kivy.colorsdialog import *  # noqa: F401,F403
    from pysollib.kivy.fontsdialog import *  # noqa: F401,F403
    from pysollib.kivy.solverdialog import *  # noqa: F401,F403
    from pysollib.kivy.gameinfodialog import *  # noqa: F401,F403
    from pysollib.kivy.toolbar import *  # noqa: F401,F403
    from pysollib.kivy.statusbar import *  # noqa: F401,F403
    from pysollib.kivy.progressbar import *  # noqa: F401,F403
    from pysollib.kivy.menubar import *  # noqa: F401,F403
    from pysollib.kivy.selectcardset import *  # noqa: F401,F403
    from pysollib.kivy.selecttree import *  # noqa: F401,F403

else:  # gtk
    from pysollib.pysolgtk.tkconst import *  # noqa: F401,F403
    from pysollib.pysolgtk.tkutil import *  # noqa: F401,F403
    from pysollib.pysolgtk.tkcanvas import *  # noqa: F401,F403
    from pysollib.pysolgtk.tkwrap import *  # noqa: F401,F403
    from pysollib.pysolgtk.tkwidget import *  # noqa: F401,F403
    from pysollib.pysolgtk.tkhtml import *  # noqa: F401,F403
    from pysollib.pysolgtk.edittextdialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.tkstats import *  # noqa: F401,F403
    from pysollib.pysolgtk.playeroptionsdialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.soundoptionsdialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.timeoutsdialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.colorsdialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.fontsdialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.findcarddialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.fullpicturedialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.solverdialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.gameinfodialog import *  # noqa: F401,F403
    from pysollib.pysolgtk.toolbar import *  # noqa: F401,F403
    from pysollib.pysolgtk.statusbar import *  # noqa: F401,F403
    from pysollib.pysolgtk.progressbar import *  # noqa: F401,F403
    from pysollib.pysolgtk.menubar import *  # noqa: F401,F403
    from pysollib.pysolgtk.card import *  # noqa: F401,F403
    from pysollib.pysolgtk.selectcardset import *  # noqa: F401,F403
