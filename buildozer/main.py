#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#
# PySol -- a Python Solitaire game
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.
# If not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# ---------------------------------------------------------------------------

# Starter for kivy/android using buildozer: Needs an explizitly
# named main.py as startpoint.

import os
import sys
if '--kivy' not in sys.argv:
    sys.argv.append('--kivy')

runmain = True
if runmain:
    from pysollib.init import init
init()

if runmain:
    from pysollib.main import main

os.environ['KIVY_NO_CONSOLELOG'] = "No"
sys.exit(main(sys.argv))
