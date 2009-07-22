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

__all__ = []

# Imports
import sys
#from tkFont import Font
from gettext import ungettext

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText, MfxCanvasLine

from mahjongg import Mahjongg_RowStack, AbstractMahjonggGame, comp_cardset


# ************************************************************************
# *
# ************************************************************************

class Shisen_Hint(AbstractHint):
    TOP_MATCHING = False
    # FIXME: no intelligence whatsoever is implemented here
    def computeHints(self):
        game = self.game
        # get free stacks
        stacks = []
        for r in game.s.rows:
            if r.cards:
                stacks.append(r)
        # find matching tiles
        i = 0
        for r in stacks:
            for t in stacks[i+1:]:
                #if game.cardsMatch(r.cards[0], t.cards[0]):
                if r.acceptsCards(t, t.cards):
                    # simple scoring...
                    if self.TOP_MATCHING:
                        score = 2000 - r.rown - t.rown
                    else:
                        score = 1000 + r.rown + t.rown
                    self.addHint(score, 1, r, t)
            i += 1


class NotShisen_Hint(Shisen_Hint):
    TOP_MATCHING = True


# ************************************************************************
# * Shisen-Sho
# ************************************************************************


class Shisen_Foundation(AbstractFoundationStack):
    def __init__(self, x, y, game, suit=ANY_SUIT, **cap):
        kwdefault(cap, max_move=0, max_accept=0, max_cards=game.NCARDS)
        AbstractFoundationStack.__init__(self, x, y, game, suit, **cap)

    def acceptsCards(self, from_stack, cards):
        # We do not accept any cards - pairs will get
        # delivered by _dropPairMove() below.
        return 0

    def basicIsBlocked(self):
        return 1

    def initBindings(self):
        pass


class Shisen_RowStack(Mahjongg_RowStack):

    def basicIsBlocked(self):
        return 0

    def acceptsCards(self, from_stack, cards):
        if not self.game.cardsMatch(self.cards[0], cards[-1]):
            return 0

        cols, rows = self.game.L
        game_cols = self.game.cols
        x1, y1 = self.coln+1, self.rown+1
        x2, y2 = from_stack.coln+1, from_stack.rown+1
        dx, dy = x2 - x1, y2 - y1

        a = []
        for i in xrange(cols+2):
            a.append([5]*(rows+2))

        def can_move(x, y, nx, ny, direct, d, direct_chng_cnt):
            if nx == x2 and ny == y2:
                return 1
            if nx < 0 or ny < 0 or nx > cols+1 or ny > rows+1:
                return 0
            if nx in (0, cols+1) or ny in (0, rows+1) \
                   or not game_cols[nx-1][ny-1].cards:
                if direct_chng_cnt == 0:
                    return 1
                elif direct_chng_cnt == 1:
                    if direct != d:
                        if d == 1 and dy > 0:
                            return 1
                        elif d == 2 and dy < 0:
                            return 1
                        elif d == 3 and dx > 0:
                            return 1
                        elif d == 4 and dx < 0:
                            return 1
                    else:
                        return 1
                elif direct_chng_cnt == 2:
                    if direct != d:
                        if d in (1, 2) and x == x2:
                            return 1
                        elif y == y2:
                            return 1
                    else:
                        if d == 1 and y < y2:
                            return 1
                        elif d == 2 and y > y2:
                            return 1
                        elif d == 3 and x < x2:
                            return 1
                        elif d == 4 and x > x2:
                            return 1
                elif direct_chng_cnt == 3:
                    if direct == d:
                        return 1

            return 0

        res_path = [None]
        def do_accepts(x, y, direct, direct_chng_cnt, path):
            #if direct_chng_cnt > 3:
            #    return
            if a[x][y] < direct_chng_cnt:
                return
            #if res_path[0]:
            #    return
            a[x][y] = direct_chng_cnt
            if x == x2 and y == y2:
                res_path[0] = path
                return

            if can_move(x, y, x, y+1, direct, 1, direct_chng_cnt): #### 1
                #dcc = direct == 1 and direct_chng_cnt or direct_chng_cnt+1
                p = path[:]
                if direct == 1:
                    dcc = direct_chng_cnt
                else:
                    dcc = direct_chng_cnt+1
                    p.append((x, y))
                do_accepts(x, y+1, 1, dcc, p)
            if can_move(x, y, x, y-1, direct, 2, direct_chng_cnt): #### 2
                #dcc = direct == 2 and direct_chng_cnt or direct_chng_cnt+1
                p = path[:]
                if direct == 2:
                    dcc = direct_chng_cnt
                else:
                    dcc = direct_chng_cnt+1
                    p.append((x, y))
                do_accepts(x, y-1, 2, dcc, p)
            if can_move(x, y, x+1, y, direct, 3, direct_chng_cnt): #### 3
                #dcc = direct == 3 and direct_chng_cnt or direct_chng_cnt+1
                p = path[:]
                if direct == 3:
                    dcc = direct_chng_cnt
                else:
                    dcc = direct_chng_cnt+1
                    p.append((x, y))
                do_accepts(x+1, y, 3, dcc, p)
            if can_move(x, y, x-1, y, direct, 4, direct_chng_cnt): #### 4
                #dcc = direct == 4 and direct_chng_cnt or direct_chng_cnt+1
                p = path[:]
                if direct == 4:
                    dcc = direct_chng_cnt
                else:
                    dcc = direct_chng_cnt+1
                    p.append((x, y))
                do_accepts(x-1, y, 4, dcc, p)

        do_accepts(x1, y1, 0, 0, [])
        #from pprint import pprint
        #pprint(a)

        if a[x2][y2] > 3:
            return None

        res_path = res_path[0]
        res_path.append((x2, y2))
        #print res_path
        return res_path


    def fillStack(self):
        self.game.fillStack(self)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        assert ncards == 1 and to_stack in self.game.s.rows
        if to_stack.cards:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            Mahjongg_RowStack.moveMove(self, ncards, to_stack, frames=frames, shadow=shadow)

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2|16)            # for undo
        if not game.demo:
            if game.app.opt.shisen_show_hint:
                self.drawArrow(other_stack, game.app.opt.timeouts['hint'])
            game.playSample("droppair", priority=200)
        #
        game.moveMove(n, self, f, frames=frames, shadow=shadow)
        game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.fillStack()
        other_stack.fillStack()
        game.updateStackMove(game.s.talon, 1|16)            # for redo
        game.leaveState(old_state)


    def drawArrow(self, other_stack, sleep):
        game = self.game
        path = self.acceptsCards(other_stack, [other_stack.cards[-1]])
        #print path
        x0, y0 = game.XMARGIN, game.YMARGIN
        #print x0, y0
        images = game.app.images
        cs = game.app.cardset
        if cs.version >= 6:
            cardw = images.CARDW-cs.SHADOW_XOFFSET
            cardh = images.CARDH-cs.SHADOW_YOFFSET
        else:
            cardw = images.CARDW
            cardh = images.CARDH
        coords = []
        dx, dy = game._delta_x, game._delta_y
        for x, y in path:
            if x == 0:
                coords.append(6)
            elif x == game.L[0]+1:
                coords.append(x0+cardw*(x-1)+10+dx)
            else:
                coords.append(x0+cardw/2+cardw*(x-1)+dx)
            if y == 0:
                coords.append(6)
            elif y == game.L[1]+1:
                coords.append(y0+cardh*(y-1)+6)
            else:
                coords.append(y0+cardh/2+cardh*(y-1))
        #print coords
        ##s1 = min(cardw/2, cardh/2, 30)
        ##w = min(s1/3, 7)
        ##s2 = min(w, 10)
        w = 7
        arrow = MfxCanvasLine(game.canvas,
                              coords,
                              {'width': w,
                               'fill': game.app.opt.colors['hintarrow'],
                               ##'arrow': 'last',
                               ##'arrowshape': (s1, s1, s2)
                               }
                              )
        game.canvas.update_idletasks()
        game.sleep(sleep)
        if arrow is not None:
            arrow.delete()
        game.canvas.update_idletasks()


class AbstractShisenGame(AbstractMahjonggGame):
    Hint_Class = NotShisen_Hint #Shisen_Hint
    RowStack_Class = Shisen_RowStack

    #NCARDS = 144
    GRAVITY = True

    def createGame(self):
        cols, rows = self.L
        assert cols*rows == self.NCARDS

        # start layout
        l, s = Layout(self), self.s
        ##dx, dy = 3, -3

        cs = self.app.cardset
        if cs.version >= 6:
            dx = l.XOFFSET
            dy = -l.YOFFSET
            d_x = cs.SHADOW_XOFFSET
            d_y = cs.SHADOW_YOFFSET
            self._delta_x, self._delta_y = dx, -dy
        else:
            dx = 3
            dy = -3
            d_x = 0
            d_y = 0
            self._delta_x, self._delta_y = 0, 0

        font = self.app.getFont("canvas_default")

        # width of self.texts.info
        #ti_width = Font(self.canvas, font).measure(_('Remaining'))
        ti_width = 80

        # set window size
        dxx, dyy = abs(dx), abs(dy)
        cardw, cardh = l.CW - d_x, l.CH - d_y
        w = l.XM+dxx + cols*cardw+d_x + l.XM+ti_width+l.XM
        h = l.YM+dyy + rows*cardh+d_y + l.YM
        self.setSize(w, h)
        self.XMARGIN = l.XM+dxx
        self.YMARGIN = l.YM+dyy

        # set game extras
        self.check_dist = l.CW*l.CW + l.CH*l.CH     # see _getClosestStack()

        #
        self.cols = [[] for i in xrange(cols)]
        cl = range(cols)
        if dx > 0:
            cl.reverse()
        for col in cl:
            for row in xrange(rows):
                x = l.XM + dxx + col * cardw
                y = l.YM + dyy + row * cardh
                stack = self.RowStack_Class(x, y, self)
                stack.CARD_XOFFSET = 0
                stack.CARD_YOFFSET = 0
                stack.coln, stack.rown = col, row
                s.rows.append(stack)
                self.cols[col].append(stack)
        #from pprint import pprint
        #pprint(self.cols)

        # create other stacks
        y = l.YM + dyy
        s.foundations.append(Shisen_Foundation(-l.XS-self.canvas.xmargin,
                                               y, self))
        self.texts.info = MfxCanvasText(self.canvas,
                                        self.width - l.XM - ti_width, y,
                                        anchor="nw", font=font)
        # the Talon is invisble
        s.talon = InitialDealTalonStack(-l.XS-self.canvas.xmargin,
                                        self.height-dyy, self)

        # Define stack groups
        l.defaultStackGroups()

    def fillStack(self, stack):
        if not self.GRAVITY: return
        to_stack = stack
        for from_stack in self.cols[stack.coln][stack.rown+1::-1]:
            if not from_stack.cards:
                continue
            self.moveMove(1, from_stack, to_stack, frames=0)
            to_stack = from_stack

    def updateText(self):
        if self.preview > 1 or self.texts.info is None:
            return

        if self.app.opt.shisen_show_matching:
            # find matching tiles
            stacks = self.s.rows
            f, i = 0, 0
            for r in stacks:
                i = i + 1
                if not r.cards:
                    continue
                for t in stacks[i:]:
                    if not t.cards:
                        continue
                    if r.acceptsCards(t, t.cards):
                        f += 1
            if f == 0:
                f = _('No Free\nMatching\nPairs')
            else:
                f = ungettext('%d Free\nMatching\nPair',
                              '%d Free\nMatching\nPairs',
                              f) % f
        else:
            f = ''

        t = len(self.s.foundations[0].cards)
        r1 = ungettext('%d\nTile\nRemoved\n\n',
                       '%d\nTiles\nRemoved\n\n',
                       t) % t
        r2 = ungettext('%d\nTile\nRemaining\n\n',
                       '%d\nTiles\nRemaining\n\n',
                       self.NCARDS - t) % (self.NCARDS - t)

        t = r1 + r2 + f
        self.texts.info.config(text = t)


    def drawHintArrow(self, from_stack, to_stack, ncards, sleep):
        from_stack.drawArrow(to_stack, sleep)


    def _shuffleHook(self, cards):
        return cards

    def canShuffle(self):
        return False


class Shisen_18x8(AbstractShisenGame):
    L = (18, 8)

class Shisen_14x6(AbstractShisenGame):
    L = (14, 6)
    NCARDS = 84

class Shisen_24x12(AbstractShisenGame):
    L = (24, 12)
    NCARDS = 288

class Shisen_18x8_NoGravity(AbstractShisenGame):
    L = (18, 8)
    GRAVITY = False

class Shisen_14x6_NoGravity(AbstractShisenGame):
    L = (14, 6)
    NCARDS = 84
    GRAVITY = False

class Shisen_24x12_NoGravity(AbstractShisenGame):
    L = (24, 12)
    NCARDS = 288
    GRAVITY = False


# ************************************************************************
# * Not Shisen-Sho
# ************************************************************************

class NotShisen_RowStack(Shisen_RowStack):
    def acceptsCards(self, from_stack, cards):
        if not self.game.cardsMatch(self.cards[0], cards[-1]):
            return 0
        if self.coln != from_stack.coln and self.rown != from_stack.rown:
            return 0
        return [(self.coln+1, self.rown+1),
                (from_stack.coln+1, from_stack.rown+1)]


class NotShisen_14x6(AbstractShisenGame):
    Hint_Class = NotShisen_Hint
    RowStack_Class = NotShisen_RowStack
    L = (14, 6)
    NCARDS = 84

class NotShisen_18x8(AbstractShisenGame):
    Hint_Class = NotShisen_Hint
    RowStack_Class = NotShisen_RowStack
    L = (18, 8)

class NotShisen_24x12(AbstractShisenGame):
    Hint_Class = NotShisen_Hint
    RowStack_Class = NotShisen_RowStack
    L = (24, 12)
    NCARDS = 288


# ************************************************************************
# * register a Shisen-Sho type game
# ************************************************************************

def r(id, gameclass, name, rules_filename="shisensho.html"):
    decks, ranks, trumps = comp_cardset(gameclass.NCARDS)
    gi = GameInfo(id, gameclass, name,
                  GI.GT_SHISEN_SHO, 4*decks, 0, GI.SL_MOSTLY_SKILL,
                  category=GI.GC_MAHJONGG, short_name=name,
                  suits=range(3), ranks=range(ranks), trumps=range(trumps),
                  si={"decks": decks, "ncards": gameclass.NCARDS})
    gi.ncards = gameclass.NCARDS
    gi.rules_filename = rules_filename
    registerGame(gi)
    return gi

r(11001, Shisen_14x6, "Shisen-Sho 14x6")
r(11002, Shisen_18x8, "Shisen-Sho 18x8")
r(11003, Shisen_24x12, "Shisen-Sho 24x12")
r(11004, Shisen_14x6_NoGravity, "Shisen-Sho (No Gravity) 14x6")
r(11005, Shisen_18x8_NoGravity, "Shisen-Sho (No Gravity) 18x8")
r(11006, Shisen_24x12_NoGravity, "Shisen-Sho (No Gravity) 24x12")
r(11011, NotShisen_14x6, "Not Shisen-Sho 14x6", "notshisensho.html")
r(11012, NotShisen_18x8, "Not Shisen-Sho 18x8", "notshisensho.html")
r(11013, NotShisen_24x12, "Not Shisen-Sho 24x12", "notshisensho.html")


del r
