#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------

class AccessibleOutput:
    try:
        import accessible_output3.outputs.auto as accessible_output
    except ImportError:
        try:
            import accessible_output2.outputs.auto as accessible_output
        except ImportError:
            accessible_output = None

    def isSupported(self):
        if self.accessible_output is None:
            return False
        o = self.accessible_output.Auto()
        for output in o.outputs:
            if (output is not None and output.is_active() and
                    not output.name.startswith('sapi')):
                return True
        return False

    def speak(self, text):
        o = self.accessible_output.Auto()
        o.output(text)


class Speech:
    speechClass = AccessibleOutput()
    isEnabled = True

    def speak(self, text):
        if self.speechClass.isSupported():
            self.speechClass.speak(text)
