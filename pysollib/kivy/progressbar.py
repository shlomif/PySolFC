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

from kivy.uix.popup import Popup

# ************************************************************************
# * a simple progress bar
# ************************************************************************
# not really supportable with kivy. dummy def.


class PysolProgressBar(Popup):
    def __init__(self, app, parent, title=None, images=None, color="blue",
                 width=300, height=25, show_text=1, norm=1):
        self.percent = 100

    def update(self, **kw):
        return

    def destroy(self):
        return

    def reset(self, percent=0):
        return
