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

import sys, os, traceback

import Tkinter
import tkFont

from pysollib.settings import PACKAGE
from pysollib.settings import TOOLKIT, USE_TILE
from pysollib.tile import Tile

from common import baseInitRootWindow, BaseTkSettings, get_font_name


# /***********************************************************************
# // Init root window
# ************************************************************************/

class initRootWindow(baseInitRootWindow):
    def __init__(self, root, app):
        baseInitRootWindow.__init__(self, root, app)

##         if TOOLKIT == 'tk':
##             window.wm_iconbitmap("@"+filename)
##             window.wm_iconmask("@"+filename)

        ##root.self.wm_maxsize(9999, 9999) # unlimited
        if TOOLKIT == 'gtk':
            pass
        elif USE_TILE:
            f = os.path.join(app.dataloader.dir, 'tcl', 'menu8.4.tcl')
            if os.path.exists(f):
                try:
                    root.tk.call('source', f)
                except:
                    traceback.print_exc()
            f = os.path.join(app.dataloader.dir, 'tcl', 'clrpick.tcl')
            if os.path.exists(f):
                try:
                    root.tk.call('source', f)
                except:
                    traceback.print_exc()
            f = os.path.join(app.dataloader.dir, 'tcl', 'fsdialog.tcl')
            if os.path.exists(f):
                try:
                    root.tk.call('source', f)
                except:
                    traceback.print_exc()
                else:
                    import tkFileDialog
                    tkFileDialog.Open.command = 'ttk::getOpenFile'
                    tkFileDialog.SaveAs.command = 'ttk::getSaveFile'
                    tkFileDialog.Directory.command = 'ttk::chooseDirectory'

            style = Tile.Style(root)
            color = style.lookup('.', 'background')
            if color:
                root.tk_setPalette(color)

            root.option_add('*Menu.borderWidth', 1, 60)
            root.option_add('*Menu.activeBorderWidth', 1, 60)
            color = style.lookup('.', 'background', 'active')
            if color:
                root.option_add('*Menu.activeBackground', color, 60)

            root.option_add('*Listbox.background', 'white', 60)
            root.option_add('*Listbox.foreground', 'black', 60)
            root.option_add('*Listbox*selectBackground', '#0a5f89', 60)
            root.option_add('*Listbox*selectForeground', 'white', 60)

            font = root.option_get('font', PACKAGE)
            if font:
                # use font from xrdb
                fn = get_font_name(font)
                if fn:
                    root.option_add('*font', font)
                    style.configure('.', font=font)
                    app.opt.fonts['default'] = fn
                    # treeview heading
                    f = root.tk.splitlist(root.tk.call('font', 'actual', fn))
                    root.tk.call('font', 'configure', 'TkHeadingFont', *f)
            else:
                # use font from Tile settings
                font = style.lookup('.', 'font')
                if font:
                    fn = get_font_name(font)
                    if fn:
                        root.option_add('*font', font)
                        app.opt.fonts['default'] = fn
            if app.opt.tile_theme in ('clam', 'clearlooks'):
                root.wm_minsize(550, 360)
                style.configure('TLabelframe', labeloutside=False,
                                labelmargins=(8, 0, 8, 0))

        #
        else:
            root.option_add('*Entry.background', 'white', 60)
            root.option_add('*Entry.foreground', 'black', 60)
            root.option_add('*Listbox.background', 'white', 60)
            root.option_add('*Listbox.foreground', 'black', 60)
            root.option_add('*Listbox*selectBackground', '#0a5f89', 60)
            root.option_add('*Listbox*selectForeground', 'white', 60)
            ##root.option_add('*borderWidth', '1', 50)
            ##root.option_add('*Button.borderWidth', '1', 50)
            root.option_add('*Scrollbar.elementBorderWidth', 1, 60)
            root.option_add('*Scrollbar.borderWidth', 1, 60)
            root.option_add('*Menu.borderWidth', 1, 60)
            root.option_add('*Menu.activeBorderWidth', 1, 60)
            #root.option_add('*Button.HighlightBackground', '#595d59')
            #root.option_add('*Button.HighlightThickness', '1')
            root.option_add('*font', 'helvetica 12', 60)



class TkSettings(BaseTkSettings):
    pass


