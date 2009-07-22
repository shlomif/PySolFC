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
from random import randint

# PySol imports
from mfxutil import SubclassResponsibility

# ************************************************************************
# *
# ************************************************************************

class AbstractCard:
    # A playing card.
    #
    # A card doesn't record to which stack it belongs; only the stack
    # records this (it turns out that we always know this from the
    # context, and this saves a ``double update'' with potential for
    # inconsistencies).
    #
    # Public methods:
    #
    # moveTo(x, y) -- move the card to an absolute position
    # moveBy(dx, dy) -- move the card by a relative offset
    # tkraise() -- raise the card to the top of its stack
    # showFace(), showBack() -- turn the card face up or down & raise it
    #
    # Public read-only instance variables:
    #
    # suit, rank, color -- the card's suit, rank and color
    # face_up -- true when the card is shown face up, else false
    #
    # Semi-public read-only instance variables:
    #
    # item -- the CanvasItem representing the card
    # x, y -- the position of the card's top left corner
    #

    def __init__(self, id, deck, suit, rank, game, x=0, y=0):
        # The card is created at position (x, y), with its face down.
        # Adding it to a stack will position it according to that
        # stack's rules.
        self.id = id
        self.deck = deck
        self.suit = suit
        self.color = suit / 2
        self.rank = rank
        self.game = game
        self.x = x
        self.y = y
        self.item = None
        self.face_up = 0
        # To improve display speed, we hide cards (except 2 top cards).
        self.hide_stack = None

    def __str__(self):
        # Return a string for debug print statements.
        return "Card(%d, %d, %d, %d)" % (self.id, self.deck, self.suit, self.rank)

    def isHidden(self):
        return self.hide_stack is not None

    def moveTo(self, x, y):
        ##print 'moveTo', x, y
        # Move the card to absolute position (x, y).
        dx, dy = 0, 0
        if self.game.app.opt.randomize_place:
            d = 1
            dx, dy = randint(-d, d), randint(-d, d)
        self.moveBy(x - self.x + dx, y - self.y + dy)

    def moveBy(self, dx, dy):
        # Move the card by (dx, dy).
        dx, dy = int(dx), int(dy)
        if dx or dy:
            self.x = self.x + dx
            self.y = self.y + dy
            ##print "moveBy:", self.id, dx, dy, self.item.coords()
            self.item.move(dx, dy)

    def tkraise(self, unhide=1):
        # Raise the card above all other objects in its group (i.e. stack).
        if unhide:
            self.unhide()
        self.item.tkraise()


    #
    # abstract methods
    #

    def hide(self, stack):
        pass

    def unhide(self):
        pass

    def setSelected(self, s, group=None):
        pass

    def showFace(self, unhide=1):
        # Turn the card's face up.
        raise SubclassResponsibility

    def showBack(self, unhide=1):
        # Turn the card's face down.
        raise SubclassResponsibility

    def updateCardBackground(self, image):
        raise SubclassResponsibility


    def close(self):
        pass

    def unclose(self):
        pass

