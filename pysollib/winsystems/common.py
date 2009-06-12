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

from pysollib.settings import TITLE
from pysollib.settings import VERSION
from pysollib.settings import TOOLKIT, USE_TILE
from pysollib.settings import DEBUG
from pysollib.mfxutil import print_err
if USE_TILE:
    from pysollib.tile import ttk


def init_tile(app, top):
    # load available themes
    d = os.path.join(app.dataloader.dir, 'themes')
    if os.path.isdir(d):
        top.tk.eval('global auto_path; lappend auto_path {%s}' % d)
        for t in os.listdir(d):
            if os.path.exists(os.path.join(d, t, 'pkgIndex.tcl')):
                try:
                    top.tk.eval('package require ttk::theme::'+t)
                    #print 'load theme:', t
                except:
                    traceback.print_exc()
                    pass


def set_theme(app, top, theme):
    # set theme
    style = ttk.Style(top)
    try:
        style.theme_use(theme)
    except:
        print_err(_('invalid theme name: ') + theme)
        style.theme_use(app.opt.default_tile_theme)


def get_font_name(font):
    # create font name
    # i.e. "helvetica 12" -> ("helvetica", 12, "roman", "normal")
    from tkFont import Font
    font_name = None
    try:
        f = Font(font=font)
    except:
        print_err(_('invalid font name: ') + font)
        if DEBUG:
            traceback.print_exc()
    else:
        fa = f.actual()
        font_name = (fa['family'],
                     fa['size'],
                     fa['slant'],
                     fa['weight'])
    return font_name


def base_init_root_window(root, app):
    #root.wm_group(root)
    root.wm_title(TITLE + ' ' + VERSION)
    root.wm_iconname(TITLE + ' ' + VERSION)
    # set minsize
    sw, sh, sd = (root.winfo_screenwidth(),
                  root.winfo_screenheight(),
                  root.winfo_screendepth())
    if sw < 640 or sh < 480:
        root.wm_minsize(400, 300)
    else:
        root.wm_minsize(520, 360)

    if TOOLKIT == 'gtk':
        pass
    elif USE_TILE:
        theme = app.opt.tile_theme
        init_tile(app, root)
        set_theme(app, root, theme)
    else:
        pass


class BaseTkSettings:
    canvas_padding = (0, 0)
    horizontal_toolbar_padding = (0, 0)
    vertical_toolbar_padding = (0, 1)
    toolbar_button_padding = (2, 2)
    toolbar_label_padding = (4, 4)
    if USE_TILE:
        toolbar_relief = 'flat'
        toolbar_borderwidth = 0
    else:
        toolbar_relief = 'raised'
        toolbar_button_relief = 'flat'
        toolbar_separator_relief = 'sunken'
        toolbar_borderwidth = 1
        toolbar_button_borderwidth = 1


