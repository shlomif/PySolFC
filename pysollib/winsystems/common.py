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

from pysollib.settings import PACKAGE, VERSION
from pysollib.settings import TOOLKIT, USE_TILE
from pysollib.settings import DEBUG
from pysollib.tile import Tile


def init_tile(app, top, theme):
    top.tk.call("package", "require", "tile")
    # load available themes
    d = os.path.join(app.dataloader.dir, 'themes')
    if os.path.isdir(d):
        top.tk.call('lappend', 'auto_path', d)
        for t in os.listdir(d):
            if os.path.exists(os.path.join(d, t, 'pkgIndex.tcl')):
                try:
                    top.tk.call('package', 'require', 'tile::theme::'+t)
                    #print 'load theme:', t
                except:
                    traceback.print_exc()
                    pass

def set_theme(app, top, theme):
    # set theme
    style = Tile.Style(top)
    all_themes = style.theme_names()
    if theme not in all_themes:
        print >> sys.stderr, 'WARNING: invalid theme name:', theme
        theme = app.opt.default_tile_theme
    style.theme_use(theme)


def get_font_name(font):
    # create font name
    # i.e. "helvetica 12" -> ("helvetica", 12, "roman", "normal")
    from tkFont import Font
    font_name = None
    try:
        f = Font(font=font)
    except:
        print >> sys.stderr, 'invalid font name:', font
        if DEBUG:
            traceback.print_exc()
    else:
        fa = f.actual()
        font_name = (fa['family'],
                     fa['size'],
                     fa['slant'],
                     fa['weight'])
    return font_name


class baseInitRootWindow:
    def __init__(self, root, app):
        #root.wm_group(root)
        root.wm_title(PACKAGE + ' ' + VERSION)
        root.wm_iconname(PACKAGE + ' ' + VERSION)
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
            init_tile(app, root, theme)
            set_theme(app, root, theme)
        else:
            pass

class BaseTkSettings:
    canvas_padding = (0, 0)
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


