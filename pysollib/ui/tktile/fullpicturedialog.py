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

from pysollib.mygettext import _
from pysollib.settings import TITLE
from pysollib.ui.tktile.tkcanvas import MfxCanvas, MfxCanvasGroup
from pysollib.ui.tktile.tkcanvas import MfxCanvasImage
from pysollib.ui.tktile.tkutil import bind, unbind_destroy

from six.moves import tkinter


class FullPictureDialog(tkinter.Toplevel):
    CARD_IMAGES = {}  # key: (type, rank, suit)

    def __init__(self, parent, game):
        tkinter.Toplevel.__init__(self)
        title = TITLE + ' - ' + _('Full picture')
        self.title(title)
        self.wm_resizable(False, False)
        self.cardsettype = ''
        self.images = {}
        self.label_width = 0
        self.label_height = 0

        # if size == 'large':
        #     self.images_dir = os.path.join(dir, 'large', cs_type)
        #     self.label_width, self.label_height = LARGE_EMBLEMS_SIZE
        # else:
        #     self.images_dir = os.path.join(dir, 'small')
        #     self.label_width, self.label_height = SMALL_EMBLEMS_SIZE

        self.canvas = MfxCanvas(self, bg='white')
        # self.canvas = MfxCanvas(self, bg='black')
        self.canvas.pack(expand=True, fill='both')
        #
        self.groups = []
        self.highlight_items = None
        self.busy = False
        self.connectGame(game)
        #
        bind(self, "WM_DELETE_WINDOW", self.destroy)
        bind(self, "<Escape>", self.destroy)
        #

    def createCardLabel(self, suit, rank, x0, y0):
        canvas = self.canvas
        group = MfxCanvasGroup(canvas)
        #
        im = self.images.getFace(0, 0, rank)
        FullPictureDialog.CARD_IMAGES[rank] = im
        cim = MfxCanvasImage(canvas, x0, y0, image=im, anchor='nw')
        cim.addtag(group)
        cim.lower()

        self.groups.append(group)

    def connectGame(self, game):
        self.images = game.app.subsampled_images
        #
        # self.images_dir = dir
        self.label_width = self.images.CARDW
        self.label_height = self.images.CARDH
        self.cardsettype = game.gameinfo.subcategory
        #
        # self.images_dir = dir
        self.canvas.delete('all')
        self.game = game
        cards = game.gameinfo.trumps

        dx, dy = self.label_width, self.label_height
        i = 0
        k = 0

        for card in cards:
            x, y = dx * k + 2, dy * i + 2
            self.createCardLabel(suit=0, rank=card, x0=x, y0=y)
            k += 1
            if k >= self.cardsettype:
                k = 0
                i += 1
        if k > 0:
            i += 1

        w, h = dx*self.cardsettype+2, dy*i+2
        self.canvas.config(width=w, height=h)
        self.wm_iconname(TITLE + " - " + game.getTitleName())
        self.wm_geometry('')            # cancel user-specified geometry

    def destroy(self, *args):
        for group in self.groups:
            unbind_destroy(group)
        unbind_destroy(self)
        self.wm_withdraw()
        tkinter.Toplevel.destroy(self)


full_picture_dialog = None


def create_full_picture_dialog(parent, game):
    global full_picture_dialog
    try:
        full_picture_dialog.wm_deiconify()
        full_picture_dialog.tkraise()
    except Exception:
        # traceback.print_exc()
        full_picture_dialog = FullPictureDialog(parent, game)


def connect_game_full_picture_dialog(game):
    try:
        full_picture_dialog.connectGame(game)
    except Exception:
        pass


def destroy_full_picture_dialog():
    global full_picture_dialog
    try:
        full_picture_dialog.destroy()
    except Exception:
        # traceback.print_exc()
        pass
    full_picture_dialog = None
