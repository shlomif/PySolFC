#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##---------------------------------------------------------------------------##

import sys, os, traceback

import Tkinter
import tkFont

from pysollib.settings import TITLE
from pysollib.settings import TOOLKIT, USE_TILE
if USE_TILE:
    from pysollib.tile import ttk

from common import base_init_root_window, BaseTkSettings, get_font_name


# ************************************************************************
# * Init root window
# ************************************************************************

def init_root_window(root, app):

    base_init_root_window(root, app)

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
                root.tk.evalfile(f)
            except:
                traceback.print_exc()
        f = 'clrpick8.5.tcl'
        f = os.path.join(app.dataloader.dir, 'tcl', f)
        if os.path.exists(f):
            try:
                root.tk.evalfile(f)
            except:
                traceback.print_exc()
        f = 'fsdialog8.5.tcl'
        f = os.path.join(app.dataloader.dir, 'tcl', f)
        if os.path.exists(f):
            try:
                root.tk.evalfile(f)
            except:
                traceback.print_exc()
            else:
                import tkFileDialog
                tkFileDialog.Open.command = 'ttk::getOpenFile'
                tkFileDialog.SaveAs.command = 'ttk::getSaveFile'
                tkFileDialog.Directory.command = 'ttk::chooseDirectory'

        style = ttk.Style(root)
        color = style.lookup('.', 'background')
        if color:
            root.tk_setPalette(color)

        root.option_add('*Menu.borderWidth', 1, 60)
        root.option_add('*Menu.activeBorderWidth', 1, 60)
        color = style.lookup('.', 'background', ['active'])
        if color:
            root.option_add('*Menu.activeBackground', color, 60)

        root.option_add('*Listbox.background', 'white', 60)
        root.option_add('*Listbox.foreground', 'black', 60)
        root.option_add('*Text.background', 'white', 60)
        root.option_add('*Text.foreground', 'black', 60)
        root.option_add('*selectForeground', 'white', 60)
        root.option_add('*selectBackground', '#0a5f89', 60)
        root.option_add('*inactiveSelectBackground', '#0a5f89', 60) # Tk-8.5

        color = style.lookup('TEntry', 'selectbackground', ['focus'])
        if color:
            root.option_add('*selectBackground', color, 60)
            root.option_add('*inactiveSelectBackground', color, 60)
        color = style.lookup('TEntry', 'selectforeground', ['focus'])
        if color:
            root.option_add('*selectForeground', color, 60)

        root.option_add('*selectBorderWidth', 0, 60)

        font = root.option_get('font', TITLE)
        if font:
            # use font from xrdb
            fn = get_font_name(font)
            if fn:
                ##root.option_add('*font', font)
                style.configure('.', font=font)
                app.opt.fonts['default'] = fn
                # treeview heading
                f = root.tk.splitlist(root.tk.call('font', 'actual', fn))
                root.tk.call('font', 'configure', 'TkHeadingFont', *f)
        else:
            # use font from ttk settings
            font = style.lookup('.', 'font')
            if font:
                fn = get_font_name(font)
                if fn:
                    root.option_add('*font', font)
                    app.opt.fonts['default'] = fn
        if app.opt.tile_theme == 'clam':
            style.configure('TLabelframe', labeloutside=False,
                            labelmargins=(8, 0, 8, 0))

    #
    else:
        root.option_add('*Entry.background', 'white', 60)
        root.option_add('*Entry.foreground', 'black', 60)
        root.option_add('*Listbox.background', 'white', 60)
        root.option_add('*Listbox.foreground', 'black', 60)
        root.option_add('*Text.background', 'white', 60)
        root.option_add('*Text.foreground', 'black', 60)
        root.option_add('*selectForeground', 'white', 60)
        root.option_add('*selectBackground', '#0a5f89', 60)
        root.option_add('*inactiveSelectBackground', '#0a5f89', 60) # Tk-8.5
        root.option_add('*selectBorderWidth', 0, 60)
        ##root.option_add('*borderWidth', '1', 50)
        ##root.option_add('*Button.borderWidth', '1', 50)
        root.option_add('*Scrollbar.elementBorderWidth', 1, 60)
        root.option_add('*Scrollbar.borderWidth', 1, 60)
        root.option_add('*Menu.borderWidth', 1, 60)
        root.option_add('*Menu.activeBorderWidth', 1, 60)
        #root.option_add('*Button.HighlightBackground', '#595d59')
        #root.option_add('*Button.HighlightThickness', '1')
        font = root.option_get('font', TITLE)
        if font:
            fn = get_font_name(font)
            app.opt.fonts['default'] = fn
        else:
            root.option_add('*font', 'helvetica 12', 60)
            app.opt.fonts['default'] = ('helvetica', 12,
                                        'roman', 'normal')



class TkSettings(BaseTkSettings):
    pass


