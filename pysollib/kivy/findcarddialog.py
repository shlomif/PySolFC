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

# imports
# import os
# import traceback

# PySol imports

# Toolkit imports
# from tkutil import after, after_cancel
# from tkutil import bind, unbind_destroy, makeImage
# from tkcanvas import MfxCanvas, MfxCanvasGroup
# from tkcanvas import MfxCanvasImage, MfxCanvasRectangle

# from pysollib.settings import TITLE

# ************************************************************************
# *
# ************************************************************************

LARGE_EMBLEMS_SIZE = (38, 34)
SMALL_EMBLEMS_SIZE = (31, 21)


find_card_dialog = None


def create_find_card_dialog(parent, game, dir):
    pass
    '''
    global find_card_dialog
    try:
        find_card_dialog.wm_deiconify()
        find_card_dialog.tkraise()
    except:
        # traceback.print_exc()
        find_card_dialog = FindCardDialog(parent, game, dir)
    '''


def connect_game_find_card_dialog(game):
    pass
    '''
    try:
        find_card_dialog.connectGame(game)
    except:
        pass
    '''


def raise_find_card_dialog(game):
    pass


def unraise_find_card_dialog():
    pass


def destroy_find_card_dialog():
    pass
    '''
    global find_card_dialog
    try:
        find_card_dialog.destroy()
    except:
        # traceback.print_exc()
        pass
    find_card_dialog = None
    '''


'''
'''
