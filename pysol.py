#!/usr/bin/env python
# ---------------------------------------------------------------------------##
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
# ---------------------------------------------------------------------------##

# import pychecker.checker
import sys

# Initialise basics and read command line and settings.
from pysollib.init import init
init()

# Setup and Load the main process modules.
# IMPORTANT: The set of modules to load depends on the settings
# and command line options. Therfore import of pysollib.main
# HAS TO BE after call to init().
# See docs/README.SOURCE.
# Flake8 test would complain here E402, so disabled

from pysollib.main import main  # noqa: E402

# Execute it.
# import profile
# profile.run("main(sys.argv)")
sys.exit(main(sys.argv))
