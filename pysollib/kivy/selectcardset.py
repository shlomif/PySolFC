#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
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
# ---------------------------------------------------------------------------#


# imports
# import os

# PySol imports
from pysollib.mygettext import _
# from pysollib.resource import CSI
from pysollib.mfxutil import kwdefault

# Toolkit imports
from tkwidget import MfxDialog
# from tkcanvas import MfxCanvas, MfxCanvasImage
# from tkutil import loadImage

# ************************************************************************
# * Dialog
# ************************************************************************
# not used with kivy. dummy def.


class SelectCardsetDialogWithPreview(MfxDialog):
    _cardset_store = None

    def __init__(self, parent, title, app, manager, key=None, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, **kw)
        #
        if key is None:
            key = manager.getSelected()
        self.app = app
        self.manager = manager
        self.key = key
        self.preview_key = -1
        self.all_keys = []
        self.status = -1

    def getSelected(self):
        return None

    def showSelected(self, w):
        pass

    def updatePreview(self, key):
        pass

    def initKw(self, kw):
        kwdefault(kw,
                  strings=(_("&Load"), _("&Cancel"), _("&Info..."), ),
                  default=1,
                  resizable=1,
                  padx=10, pady=10,
                  width=600, height=400,
                  )
        return MfxDialog.initKw(self, kw)

    def createInfo(self):
        pass

    def done(self, button):
        pass
