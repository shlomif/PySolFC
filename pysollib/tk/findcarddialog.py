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

__all__ = ['create_find_card_dialog',
           'connect_game_find_card_dialog',
           'destroy_find_card_dialog',
           ]

# imports
import os
import Tkinter
import traceback

# PySol imports

# Toolkit imports
from tkutil import after, after_cancel
from tkutil import bind, unbind_destroy, makeImage
from tkcanvas import MfxCanvas, MfxCanvasGroup, MfxCanvasImage, MfxCanvasRectangle


# /***********************************************************************
# //
# ************************************************************************/

class FindCardDialog(Tkinter.Toplevel):
    SUIT_IMAGES = {} # key: (suit, color)
    RANK_IMAGES = {} # key: (rank, color)

    def __init__(self, parent, game, dir):
        Tkinter.Toplevel.__init__(self)
        self.title(_('Find card'))
        self.wm_resizable(0, 0)
        #
        self.images_dir = dir
        self.label_width, self.label_height = 38, 34
        self.canvas = MfxCanvas(self, bg='white')
        self.canvas.pack(expand=True, fill='both')
        #
        self.groups = []
        self.highlight_items = None
        self.connectGame(game)
        #
        bind(self, "WM_DELETE_WINDOW", self.destroy)
        bind(self, "<Escape>", self.destroy)
        #
        ##self.normal_timeout = 400    # in milliseconds
        self.normal_timeout = int(1000*game.app.opt.highlight_samerank_sleep)
        self.hidden_timeout = 200
        self.timer = None

    def createCardLabel(self, suit, rank, x0, y0):
        dx, dy = self.label_width, self.label_height
        dir = self.images_dir
        canvas = self.canvas
        group = MfxCanvasGroup(canvas)
        s = 'cshd'[suit]
        if suit >= 2: c = 'red'
        else:         c = 'black'
        rect_width = 4
        x1, y1 = x0+dx-rect_width, y0+dy-rect_width
        rect = MfxCanvasRectangle(self.canvas, x0, y0, x1, y1,
                                  width=rect_width,
                                  fill='white', outline='white')
        rect.addtag(group)
        #
        fn = os.path.join(dir, c+'-'+str(rank)+'.gif')
        rim = FindCardDialog.RANK_IMAGES.get((rank, c))
        if not rim:
            rim = makeImage(file=fn)
            FindCardDialog.RANK_IMAGES[(rank, c)] = rim
        fn = os.path.join(dir, s+'.gif')
        sim = FindCardDialog.SUIT_IMAGES.get((suit, c))
        if not sim:
            sim = makeImage(file=fn)
            FindCardDialog.SUIT_IMAGES[(suit, c)] = sim
        #
        x0 = x0+(dx-rim.width()-sim.width())/2
        x0, y0 = x0-1, y0-2
        x, y = x0, y0+(dy-rim.height())/2
        im = MfxCanvasImage(canvas, x, y, image=rim, anchor='nw')
        im.addtag(group)
        x, y = x0+rim.width(), y0+(dy-sim.height())/2
        im = MfxCanvasImage(canvas, x, y, image=sim, anchor='nw')
        im.addtag(group)
        bind(group, '<Enter>',
             lambda e, suit=suit, rank=rank, rect=rect:
                 self.enterEvent(suit, rank, rect))
        bind(group, '<Leave>',
             lambda e, suit=suit, rank=rank, rect=rect:
                 self.leaveEvent(suit, rank, rect))
        self.groups.append(group)

    def connectGame(self, game):
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
        w, h = dx*j, dy*i
        self.canvas.config(width=w, height=h)

    def enterEvent(self, suit, rank, rect):
        #print 'enterEvent', suit, rank
        self.highlight_items = self.game.highlightCard(suit, rank)
        if not self.highlight_items:
            self.highlight_items = []
        rect.config(outline='red')
        if self.highlight_items:
            self.timer = after(self, self.normal_timeout, self.timeoutEvent)

    def leaveEvent(self, suit, rank, rect):
        #print 'leaveEvent', suit, rank
        if self.highlight_items:
            for i in self.highlight_items:
                i.delete()
        rect.config(outline='white')
        #self.game.canvas.update_idletasks()
        #self.canvas.update_idletasks()
        if self.timer:
            after_cancel(self.timer)
            self.timer = None

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
        Tkinter.Toplevel.destroy(self)



find_card_dialog = None

def create_find_card_dialog(parent, game, dir):
    global find_card_dialog
    try:
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

