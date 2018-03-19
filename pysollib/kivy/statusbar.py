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
import os
import sys

if __name__ == '__main__':
    d = os.path.abspath(os.path.join(sys.path[0], os.pardir, os.pardir))
    sys.path.append(d)
    import gettext
    gettext.install('pysol', d, unicode=True)

# PySol imports

# Toolkit imports
# from pysollib.settings import WIN_SYSTEM

# ************************************************************************
# *
# ************************************************************************
# statusbar not used.


class MfxStatusbar:
    def __init__(self, top, row, column, columnspan):
        pass

    def _createLabel(self, name, expand=False, width=0, tooltip=None):
        pass

    def show(self, on):
        pass

    def updateText(self, **kw):
        pass

    def config(self, a, b):
        pass


class PysolStatusbar(MfxStatusbar):
    def __init__(self, top):
        pass


class HelpStatusbar(MfxStatusbar):
    def __init__(self, top):
        MfxStatusbar.__init__(self, top, row=4, column=0, columnspan=3)
        # l = self._createLabel('info', expand=True)
        # l.config(justify='left', anchor='w', padx=8)


class HtmlStatusbar(MfxStatusbar):
    def __init__(self, top, row, column, columnspan):
        MfxStatusbar.__init__(self, top, row=row,
                              column=column, columnspan=columnspan)
        # l = self._createLabel('url', expand=True)
        # l.config(justify='left', anchor='w', padx=8)


# ************************************************************************
# *
# ************************************************************************
