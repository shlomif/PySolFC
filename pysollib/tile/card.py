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

__all__ = ['Card']

# imports

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
        self.item.config(state="hidden")
        self.hide_stack = stack
        ##print "hide:", self.id, self.item.coords()

    def unhide(self):
        if self.hide_stack is None:
            return 0
        ##print "unhide:", self.id, self.item.coords()
        self.item.config(state="normal")
        self.hide_stack = None
        return 1


# ************************************************************************
# * New implemetation since 2.10
# *
# * We use a single CanvasImage and call CanvasImage.config() to
# * turn the card.
# * This makes turning cards a little bit slower, but dragging cards
# * around is noticeable faster as the total number of images is
# * reduced by half.
# ************************************************************************

class _OneImageCard(_HideableCard):
    def __init__(self, id, deck, suit, rank, game, x=0, y=0):
        _HideableCard.__init__(self, id, deck, suit, rank, game, x=x, y=y)
        self._face_image = game.getCardFaceImage(deck, suit, rank)
        self._back_image = game.getCardBackImage(deck, suit, rank)
        self._shade_image = game.getCardShadeImage()
        self._active_image = self._back_image
        self.item = MfxCanvasImage(game.canvas, self.x, self.y, image=self._active_image, anchor="nw")
        self.shade_item = None
        ##self._setImage = self.item.config

    def _setImage(self, image):
        if image is not self._active_image:
            self.item.config(image=image)
            self._active_image = image

    def showFace(self, unhide=1):
        if not self.face_up:
            self._setImage(image=self._face_image)
            self.tkraise(unhide)
            self.face_up = 1

    def showBack(self, unhide=1):
        if self.face_up:
            self._setImage(image=self._back_image)
            self.tkraise(unhide)
            self.face_up = 0

    def updateCardBackground(self, image):
        self._back_image = image
        if not self.face_up:
            self._setImage(image=image)

    #
    # optimized by inlining
    #

    def moveBy(self, dx, dy):
        dx, dy = int(dx), int(dy)
        self.x = self.x + dx
        self.y = self.y + dy
        item = self.item
        item.canvas.tk.call(item.canvas._w, "move", item.id, dx, dy)



# ************************************************************************
# * New idea since 3.00
# *
# * Hide a card by configuring the canvas image to None.
# ************************************************************************

class _OneImageCardWithHideByConfig(_OneImageCard):
    def hide(self, stack):
        if stack is self.hide_stack:
            return
        self._setImage(image=None)
        self.hide_stack = stack

    def unhide(self):
        if self.hide_stack is None:
            return 0
        if self.face_up:
            self._setImage(image=self._face_image)
        else:
            self._setImage(image=self._back_image)
        self.hide_stack = None
        return 1

    #
    # much like in _OneImageCard
    #

    def showFace(self, unhide=1):
        if not self.face_up:
            if unhide:
                self._setImage(image=self._face_image)
            self.item.tkraise()
            self.face_up = 1

    def showBack(self, unhide=1):
        if self.face_up:
            if unhide:
                self._setImage(image=self._back_image)
            self.item.tkraise()
            self.face_up = 0

    def updateCardBackground(self, image):
        self._back_image = image
        if not self.face_up and not self.hide_stack:
            self._setImage(image=image)


# ************************************************************************
# * Old implemetation prior to 2.10
# *
# * The card consists of two CanvasImages. To show the card face up,
# * the face item is placed in front of the back. To show it face
# * down, this is reversed.
# ************************************************************************

class _TwoImageCard(_HideableCard):
    # Private instance variables:
    #   __face, __back -- the canvas items making up the card
    def __init__(self, id, deck, suit, rank, game, x=0, y=0):
        _HideableCard.__init__(self, id, deck, suit, rank, game, x=x, y=y)
        self.item = MfxCanvasGroup(game.canvas)
        self.__face = MfxCanvasImage(game.canvas, self.x, self.y, image=game.getCardFaceImage(deck, suit, rank), anchor="nw")
        self.__back = MfxCanvasImage(game.canvas, self.x, self.y, image=game.getCardBackImage(deck, suit, rank), anchor="nw")
        self.__face.addtag(self.item)
        self.__back.addtag(self.item)

    def showFace(self, unhide=1):
        if not self.face_up:
            self.__face.tkraise()
            self.tkraise(unhide)
            self.face_up = 1

    def showBack(self, unhide=1):
        if self.face_up:
            self.__back.tkraise()
            self.tkraise(unhide)
            self.face_up = 0

    def updateCardBackground(self, image):
        self.__back.config(image=image)


# ************************************************************************
# * New idea since 2.90
# *
# * The card consists of two CanvasImages. Instead of raising
# * one image above the other we move the inactive image out
# * of the visible canvas.
# ************************************************************************

class _TwoImageCardWithHideItem(_HideableCard):
    # Private instance variables:
    #   __face, __back -- the canvas items making up the card
    def __init__(self, id, deck, suit, rank, game, x=0, y=0):
        _HideableCard.__init__(self, id, deck, suit, rank, game, x=x, y=y)
        self.item = MfxCanvasGroup(game.canvas)
        self.__face = MfxCanvasImage(game.canvas, self.x, self.y + 11000, image=game.getCardFaceImage(deck, suit, rank), anchor="nw")
        self.__back = MfxCanvasImage(game.canvas, self.x, self.y, image=game.getCardBackImage(deck, suit, rank), anchor="nw")
        self.__face.addtag(self.item)
        self.__back.addtag(self.item)

    def showFace(self, unhide=1):
        if not self.face_up:
            self.__back.move(0, 10000)
            ##self.__face.tkraise()
            self.__face.move(0, -11000)
            self.tkraise(unhide)
            self.face_up = 1

    def showBack(self, unhide=1):
        if self.face_up:
            self.__face.move(0, 11000)
            ##self.__back.tkraise()
            self.__back.move(0, -10000)
            self.tkraise(unhide)
            self.face_up = 0

    def updateCardBackground(self, image):
        self.__back.config(image=image)



# choose the implementation
Card = _TwoImageCardWithHideItem
Card = _TwoImageCard
Card = _OneImageCardWithHideByConfig
Card = _OneImageCard

