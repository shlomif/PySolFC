##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
##---------------------------------------------------------------------------##

from settings import TOOLKIT, USE_TILE

if TOOLKIT == 'tk':
    if USE_TILE:
        from tile.tkconst import *
        from tile.tkutil import *
        from tile.tkcanvas import *
        from tile.tkwrap import *
        from tile.tkwidget import *
        from tile.tkhtml import *
        from tile.edittextdialog import *
        from tile.tkstats import *
        from tile.playeroptionsdialog import *
        from tile.soundoptionsdialog import *
        from tile.timeoutsdialog import *
        from tile.colorsdialog import *
        from tile.fontsdialog import *
        from tile.findcarddialog import *
        from tile.gameinfodialog import *
        from tile.toolbar import *
        from tile.statusbar import *
        from tile.progressbar import *
        from tile.menubar import *
        from tile.card import *
        from tile.selectcardset import *
        from tile.selecttree import *
    else:
        from tk.tkconst import *
        from tk.tkutil import *
        from tk.tkcanvas import *
        from tk.tkwrap import *
        from tk.tkwidget import *
        from tk.tkhtml import *
        from tk.edittextdialog import *
        from tk.tkstats import *
        from tk.playeroptionsdialog import *
        from tk.soundoptionsdialog import *
        from tk.timeoutsdialog import *
        from tk.colorsdialog import *
        from tk.fontsdialog import *
        from tk.findcarddialog import *
        from tk.gameinfodialog import *
        from tk.toolbar import *
        from tk.statusbar import *
        from tk.progressbar import *
        from tk.menubar import *
        from tk.card import *
        from tk.selectcardset import *
        from tk.selecttree import *

else: # gtk
    from pysolgtk.tkconst import *
    from pysolgtk.tkutil import *
    from pysolgtk.tkcanvas import *
    from pysolgtk.tkwrap import *
    from pysolgtk.tkwidget import *
    from pysolgtk.tkhtml import *
    from pysolgtk.edittextdialog import *
    from pysolgtk.tkstats import *
    from pysolgtk.playeroptionsdialog import *
    from pysolgtk.soundoptionsdialog import *
    from pysolgtk.timeoutsdialog import *
    from pysolgtk.colorsdialog import *
    from pysolgtk.fontsdialog import *
    from pysolgtk.findcarddialog import *
    from pysolgtk.gameinfodialog import *
    from pysolgtk.toolbar import *
    from pysolgtk.statusbar import *
    from pysolgtk.progressbar import *
    from pysolgtk.menubar import *
    from pysolgtk.card import *
    from pysolgtk.selectcardset import *

