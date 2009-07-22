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


# imports
import gtk

# PySol imports
from pysollib.acard import AbstractCard

# Toolkit imports
from tkcanvas import MfxCanvasGroup, MfxCanvasImage


# ************************************************************************
# *
# ************************************************************************

class _HideableCard(AbstractCard):
    def hide(self, stack):
        if stack is self.hide_stack:
            return
        self.item.hide()
        self.hide_stack = stack

    def unhide(self):
        if self.hide_stack is None:
            return 0
        self.item.show()
        self.hide_stack = None
        return 1


# ************************************************************************
# *
# ************************************************************************

class _OneImageCard(_HideableCard):
    def __init__(self, id, deck, suit, rank, game, x=0, y=0):
        _HideableCard.__init__(self, id, deck, suit, rank, game, x=x, y=y)
        images = game.app.images
        self.__face_image = images.getFace(deck, suit, rank)
        self.__back_image = images.getBack()
        self.__image = MfxCanvasImage(game.canvas, self.x, self.y,
                                      image=self.__back_image,
                                      anchor=gtk.ANCHOR_NW)
        if 0:
            # using a group for a single image doesn't gain much
            self.item = MfxCanvasGroup(game.canvas)
            self.__image.addtag(self.item)
        else:
            self.item = self.__image

    def showFace(self, unhide=1):
        if not self.face_up:
            self.__image.config(image=self.__face_image)
            self.tkraise(unhide)
            self.face_up = 1

    def showBack(self, unhide=1):
        if self.face_up:
            self.__image.config(image=self.__back_image)
            self.tkraise(unhide)
            self.face_up = 0

    def updateCardBackground(self, image):
        self.__back_image = image
        if not self.face_up:
            self.__image.config(image=image)


# ************************************************************************
# *
# ************************************************************************

class _TwoImageCard(_HideableCard):
    def __init__(self, id, deck, suit, rank, game, x=0, y=0):
        _HideableCard.__init__(self, id, deck, suit, rank, game, x=x, y=y)
        images = game.app.images
        self.item = MfxCanvasGroup(game.canvas)
        self.__face = MfxCanvasImage(game.canvas, self.x, self.y,
                                     image=images.getFace(deck, suit, rank),
                                     anchor='nw')
        self.__back = MfxCanvasImage(game.canvas, self.x, self.y,
                                     image=images.getBack(),
                                     anchor='nw')
        self.__face.addtag(self.item)
        self.__back.addtag(self.item)
        self.__face.hide()

    def showFace(self, unhide=1):
        if not self.face_up:
            self.__back.hide()
            self.__face.show()
            ##self.tkraise(unhide)
            self.face_up = 1

    def showBack(self, unhide=1):
        if self.face_up:
            self.__face.hide()
            self.__back.show()
            ##self.tkraise(unhide)
            self.face_up = 0

    def updateCardBackground(self, image):
        self.__back.config(image=image)



# choose the implementation
Card = _TwoImageCard
#Card = _OneImageCard # FIXME: this implementation lost any cards (bug?)

