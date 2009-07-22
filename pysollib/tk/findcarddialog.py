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

__all__ = ['create_find_card_dialog',
           'connect_game_find_card_dialog',
           'destroy_find_card_dialog',
           ]

# imports
import os
import Tkinter
##import traceback

# PySol imports

# Toolkit imports
from tkutil import after, after_cancel
from tkutil import bind, unbind_destroy, makeImage
from tkcanvas import MfxCanvas, MfxCanvasGroup, MfxCanvasImage, MfxCanvasRectangle

from pysollib.settings import TITLE


# ************************************************************************
# *
# ************************************************************************

LARGE_EMBLEMS_SIZE = (38, 34)
SMALL_EMBLEMS_SIZE = (31, 21)

class FindCardDialog(Tkinter.Toplevel):
    CARD_IMAGES = {} # key: (rank, suit)

    def __init__(self, parent, game, dir, size='large'):
        Tkinter.Toplevel.__init__(self)
        title = TITLE + ' - ' + _('Find card')
        self.title(title)
        self.wm_resizable(False, False)
        #
        ##self.images_dir = dir
        if size == 'large':
            self.images_dir = os.path.join(dir, 'large')
            self.label_width, self.label_height = LARGE_EMBLEMS_SIZE
        else:
            self.images_dir = os.path.join(dir, 'small')
            self.label_width, self.label_height = SMALL_EMBLEMS_SIZE
        self.canvas = MfxCanvas(self, bg='white')
        ##self.canvas = MfxCanvas(self, bg='black')
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
        ##self.normal_timeout = 400    # in milliseconds
        self.normal_timeout = int(1000*game.app.opt.timeouts['highlight_samerank'])
        self.hidden_timeout = 200
        self.timer = None

    def createCardLabel(self, suit, rank, x0, y0):
        dx, dy = self.label_width, self.label_height
        dir = self.images_dir
        canvas = self.canvas
        group = MfxCanvasGroup(canvas)
        #
        im = FindCardDialog.CARD_IMAGES.get((rank, suit))
        if im is None:
            r = '%02d' % (rank+1)
            s = 'cshd'[suit]
            fn = os.path.join(dir, r+s+'.gif')
            im = makeImage(file=fn)
            FindCardDialog.CARD_IMAGES[(rank, suit)] = im
        cim = MfxCanvasImage(canvas, x0, y0, image=im, anchor='nw')
        cim.addtag(group)
        cim.lower()
        #
        rect_width = 4
        x1, y1 = x0+dx, y0+dy
        rect = MfxCanvasRectangle(self.canvas, x0+1, y0+1, x1-1, y1-1,
                                  width=rect_width,
                                  fill=None,
                                  outline='red',
                                  state='hidden'
                                  )
        rect.addtag(group)
        #
        bind(group, '<Enter>',
             lambda e, suit=suit, rank=rank, rect=rect:
                 self.enterEvent(suit, rank, rect, group))
        bind(group, '<Leave>',
             lambda e, suit=suit, rank=rank, rect=rect:
                 self.leaveEvent(suit, rank, rect, group))
        self.groups.append(group)

    def connectGame(self, game):
        self.canvas.delete('all')
        self.game = game
        suits = game.gameinfo.suits
        ranks = game.gameinfo.ranks
        dx, dy = self.label_width, self.label_height
        uniq_suits = []
        i = 0
        for suit in suits:
            if suit in uniq_suits:
                continue
            uniq_suits.append(suit)
            j = 0
            for rank in ranks:
                x, y = dx*j+2, dy*i+2
                self.createCardLabel(suit=suit, rank=rank, x0=x, y0=y)
                j += 1
            i += 1
        w, h = dx*j+2, dy*i+2
        self.canvas.config(width=w, height=h)
        self.wm_iconname(TITLE + " - " + game.getTitleName())
        self.wm_geometry('')            # cancel user-specified geometry

    def enterEvent(self, suit, rank, rect, group):
        ##print 'enterEvent', suit, rank, self.busy
        if self.busy: return
        if self.game.demo: return
        self.busy = True
        self.highlight_items = self.game.highlightCard(suit, rank)
        if not self.highlight_items:
            self.highlight_items = []
        if self.highlight_items:
            self.timer = after(self, self.normal_timeout, self.timeoutEvent)
        rect.config(state='normal')
        self.canvas.update_idletasks()
        self.busy = False

    def leaveEvent(self, suit, rank, rect, group):
        ##print 'leaveEvent', suit, rank, self.busy
        if self.busy: return
        self.busy = True
        if self.highlight_items:
            for i in self.highlight_items:
                i.delete()
            self.highlight_items = []
        if self.timer:
            after_cancel(self.timer)
            self.timer = None
        rect.config(state='hidden')
        if self.game.canvas:
            self.game.canvas.update_idletasks()
        self.canvas.update_idletasks()
        self.busy = False


    def timeoutEvent(self, *event):
        if self.highlight_items:
            state = self.highlight_items[0].cget('state')
            if state in ('', 'normal'):
                state = 'hidden'
                self.timer = after(self, self.hidden_timeout,
                                   self.timeoutEvent)
            else:
                state = 'normal'
                self.timer = after(self, self.normal_timeout,
                                   self.timeoutEvent)
            for item in self.highlight_items:
                item.config(state=state)

    def destroy(self, *args):
        for l in self.groups:
            unbind_destroy(l)
        unbind_destroy(self)
        if self.timer:
            after_cancel(self.timer)
            self.timer = None
        self.wm_withdraw()
        if self.highlight_items:
            for i in self.highlight_items:
                i.delete()
        Tkinter.Toplevel.destroy(self)



find_card_dialog = None

def create_find_card_dialog(parent, game, dir):
    global find_card_dialog
    try:
        find_card_dialog.wm_deiconify()
        find_card_dialog.tkraise()
    except:
        ##traceback.print_exc()
        find_card_dialog = FindCardDialog(parent, game, dir)

def connect_game_find_card_dialog(game):
    try:
        find_card_dialog.connectGame(game)
    except:
        pass

def destroy_find_card_dialog():
    global find_card_dialog
    try:
        find_card_dialog.destroy()
    except:
        ##traceback.print_exc()
        pass
    find_card_dialog = None


