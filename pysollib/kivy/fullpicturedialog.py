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

import math

from kivy.uix.stacklayout import StackLayout

from pysollib.kivy.LApp import LTopLevel0
from pysollib.kivy.LImage import LImage
from pysollib.mygettext import _

# ************************************************************************
# *
# ************************************************************************


class ImageStacker(StackLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.dx = 1
        self.dy = 1
        self.asp = 1  # width/height.

    def set_matrix(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def set_aspect(self, asp):
        self.asp = asp  # width/height.

    def on_size(self, instance, value):
        hint_x = 1.0 / self.dx
        hint_y = 1.0 / self.dx
        vasp = value[0]/value[1]
        # adjust width or height
        if vasp < self.asp:
            hint_y = hint_y * vasp / self.asp
        else:
            hint_x = hint_x * self.asp / vasp
        # apply to all images
        for i in self.children:
            i.size_hint = (hint_x, hint_y)


class FullPictureDialog(object):
    def __init__(self, parent, title, game, **kw):

        self.game = game
        self.top = LTopLevel0(parent, title)
        self.frame = self.top.content

        self.images = game.app.subsampled_images
        dx, dy = self.images.CARDW, self.images.CARDH

        cards = self.game.gameinfo.trumps
        cols = int(math.ceil(math.sqrt(len(cards))))

        self.stp = ImageStacker()
        self.stp.set_aspect(dx/dy)
        self.stp.set_matrix(cols, cols)
        for card in cards:
            image = LImage(texture=self.images._card[card].texture)
            self.stp.add_widget(image)

        self.frame.add_widget(self.stp)


def create_full_picture_dialog(parent, game):
    pd = FullPictureDialog(parent, _("Full picture"), game)  # noqa
    '''
    global full_picture_dialog
    try:
        full_picture_dialog.wm_deiconify()
        full_picture_dialog.tkraise()
    except Exception:
        # traceback.print_exc()
        full_picture_dialog = FullPictureDialog(parent, game)
    '''


def connect_game_full_picture_dialog(game):
    pass
    '''
    try:
        full_picture_dialog.connectGame(game)
    except Exception:
        pass
    '''


def raise_full_picture_dialog(game):
    pass


def unraise_full_picture_dialog():
    pass


def destroy_full_picture_dialog():
    pass
    '''
    global full_picture_dialog
    try:
        full_picture_dialog.destroy()
    except Exception:
        # traceback.print_exc()
        pass
    full_picture_dialog = None
    '''


'''
'''
