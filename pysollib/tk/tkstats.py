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

__all__ = ['SingleGame_StatsDialog',
           'AllGames_StatsDialog',
           'FullLog_StatsDialog',
           'SessionLog_StatsDialog',
           'Status_StatsDialog',
           'Top_StatsDialog',
           'ProgressionDialog',
           ]

# imports
import os
import time
import Tkinter, tkFont

# PySol imports
from pysollib.mfxutil import kwdefault, KwStruct
from pysollib.mfxutil import format_time
##from pysollib.util import *
from pysollib.stats import PysolStatsFormatter, ProgressionFormatter
from pysollib.settings import TOP_TITLE

# Toolkit imports
from tkutil import bind, unbind_destroy, loadImage
from tkwidget import MfxDialog, MfxMessageDialog
from tkwidget import MfxScrolledCanvas


# FIXME - this file a quick hack and needs a rewrite

# ************************************************************************
# *
# ************************************************************************

class SingleGame_StatsDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):
        self.app = app
        self.selected_game = None
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.top_frame = top_frame
        self.createBitmaps(top_frame, kw)
        #
        self.player = player or _("Demo games")
        self.top.wm_minsize(200, 200)
        self.button = kw.default
        #
        ##createChart = self.create3DBarChart
        createChart = self.createPieChart
        ##createChart = self.createSimpleChart
##         if parent.winfo_screenwidth() < 800 or parent.winfo_screenheight() < 600:
##             createChart = self.createPieChart
##             createChart = self.createSimpleChart
        #
        self.font = self.app.getFont("default")
        self.tk_font = tkFont.Font(self.top, self.font)
        self.font_metrics = self.tk_font.metrics()
        self._calc_tabs()
        #
        won, lost = app.stats.getStats(player, gameid)
        createChart(app, won, lost, _("Total"))
        won, lost = app.stats.getSessionStats(player, gameid)
        createChart(app, won, lost, _("Current session"))
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    #
    # helpers
    #

    def _calc_tabs(self):
        #
        font = self.tk_font
        t0 = 160
        t = ''
        for i in (_("Won:"),
                  _("Lost:"),
                  _("Total:")):
            if len(i) > len(t):
                t = i
        t1 = font.measure(t)
##         t1 = max(font.measure(_("Won:")),
##                  font.measure(_("Lost:")),
##                  font.measure(_("Total:")))
        t1 += 10
        ##t2 = font.measure('99999')+10
        t2 = 45
        ##t3 = font.measure('100%')+10
        t3 = 45
        tx = (t0, t0+t1+t2, t0+t1+t2+t3)
        #
        ls = self.font_metrics['linespace']
        ls += 5
        ls = max(ls, 20)
        ty = (ls, 2*ls, 3*ls+15, 3*ls+25)
        #
        self.tab_x, self.tab_y = tx, ty

    def _getPwon(self, won, lost):
        pwon, plost = 0.0, 0.0
        if won + lost > 0:
            pwon = float(won) / (won + lost)
            pwon = min(max(pwon, 0.00001), 0.99999)
            plost = 1.0 - pwon
        return pwon, plost

    def _createChartInit(self, text):
        w, h = self.tab_x[-1]+20, self.tab_y[-1]+20
        c = Tkinter.Canvas(self.top_frame, width=w, height=h)
        c.pack(side='top', fill='both', expand=False, padx=20, pady=10)
        self.canvas = c
        ##self.fg = c.cget("insertbackground")
        self.fg = c.option_get('foreground', '') or c.cget("insertbackground")
        #
        c.create_rectangle(2, 7, w, h, fill="", outline="#7f7f7f")
        l = Tkinter.Label(c, text=text, font=self.font, bd=0, padx=3, pady=1)
        dy = int(self.font_metrics['ascent']) - 10
        dy = dy/2
        c.create_window(20, -dy, window=l, anchor="nw")

    def _createChartTexts(self, tx, ty, won, lost):
        c, tfont, fg = self.canvas, self.font, self.fg
        pwon, plost = self._getPwon(won, lost)
        #
        x = tx[0]
        dy = int(self.font_metrics['ascent']) - 10
        dy = dy/2
        c.create_text(x, ty[0]-dy, text=_("Won:"), anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[1]-dy, text=_("Lost:"), anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[2]-dy, text=_("Total:"), anchor="nw", font=tfont, fill=fg)
        x = tx[1] - 16
        c.create_text(x, ty[0]-dy, text="%d" % won, anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[1]-dy, text="%d" % lost, anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[2]-dy, text="%d" % (won + lost), anchor="ne", font=tfont, fill=fg)
        y = ty[2] - 11
        c.create_line(tx[0], y, x, y, fill=fg)
        if won + lost > 0:
            x = tx[2]
            pw = int(round(100.0 * pwon))
            c.create_text(x, ty[0]-dy, text="%d%%" % pw, anchor="ne", font=tfont, fill=fg)
            c.create_text(x, ty[1]-dy, text="%d%%" % (100-pw), anchor="ne", font=tfont, fill=fg)


##     def _createChart3DBar(self, canvas, perc, x, y, p, col):
##         if perc < 0.005:
##             return
##         # translate and scale
##         p = list(p[:])
##         for i in (0, 1, 2, 3):
##             p[i] = (x + p[i][0], y + p[i][1])
##             j = i + 4
##             dx = int(round(p[j][0] * perc))
##             dy = int(round(p[j][1] * perc))
##             p[j] = (p[i][0] + dx, p[i][1] + dy)
##         # draw rects
##         def draw_rect(a, b, c, d, col, canvas=canvas, p=p):
##             points = (p[a][0], p[a][1], p[b][0], p[b][1],
##                       p[c][0], p[c][1], p[d][0], p[d][1])
##             canvas.create_polygon(points, fill=col)
##         draw_rect(0, 1, 5, 4, col[0])
##         draw_rect(1, 2, 6, 5, col[1])
##         draw_rect(4, 5, 6, 7, col[2])
##         # draw lines
##         def draw_line(a, b, canvas=canvas, p=p):
##             ##print a, b, p[a], p[b]
##             canvas.create_line(p[a][0], p[a][1], p[b][0], p[b][1])
##         draw_line(0, 1)
##         draw_line(1, 2)
##         draw_line(0, 4)
##         draw_line(1, 5)
##         draw_line(2, 6)
##         ###draw_line(3, 7)     ## test
##         draw_line(4, 5)
##         draw_line(5, 6)
##         draw_line(6, 7)
##         draw_line(7, 4)


    #
    # charts
    #

##     def createSimpleChart(self, app, won, lost, text):
##         #c, tfont, fg = self._createChartInit(frame, 300, 100, text)
##         self._createChartInit(300, 100, text)
##         c, tfont, fg = self.canvas, self.font, self.fg
##         #
##         tx = (90, 180, 210)
##         ty = (21, 41, 75)
##         self._createChartTexts(tx, ty, won, lost)

##     def create3DBarChart(self, app, won, lost, text):
##         image = app.gimages.stats[0]
##         iw, ih = image.width(), image.height()
##         #c, tfont, fg = self._createChartInit(frame, iw+160, ih, text)
##         self._createChartInit(iw+160, ih, text)
##         c, tfont, fg = self.canvas, self.font, self.fg
##         pwon, plost = self._getPwon(won, lost)
##         #
##         tx = (iw+20, iw+110, iw+140)
##         yy = ih/2 ## + 7
##         ty = (yy+21-46, yy+41-46, yy+75-46)
##         #
##         c.create_image(0, 7, image=image, anchor="nw")
##         #
##         p = ((0, 0), (44, 6), (62, -9), (20, -14),
##              (-3, -118), (-1, -120), (-1, -114), (-4, -112))
##         col = ("#00ff00", "#008200", "#00c300")
##         self._createChart3DBar(c, pwon,  102, 145+7, p, col)
##         p = ((0, 0), (49, 6), (61, -10), (15, -15),
##              (1, -123), (3, -126), (4, -120), (1, -118))
##         col = ("#ff0000", "#860400", "#c70400")
##         self._createChart3DBar(c, plost, 216, 159+7, p, col)
##         #
##         self._createChartTexts(tx, ty, won, lost)
##         c.create_text(tx[0], ty[0]-48, text=self.player, anchor="nw", font=tfont, fill=fg)

    def createPieChart(self, app, won, lost, text):
        #c, tfont, fg = self._createChartInit(frame, 300, 100, text)
        #
        self._createChartInit(text)
        c, tfont, fg = self.canvas, self.font, self.fg
        pwon, plost = self._getPwon(won, lost)
        #
        #tx = (160, 250, 280)
        #ty = (21, 41, 75)
        #
        tx, ty = self.tab_x, self.tab_y
        if won + lost > 0:
            ##s, ewon, elost = 90.0, -360.0 * pwon, -360.0 * plost
            s, ewon, elost = 0.0, 360.0 * pwon, 360.0 * plost
            c.create_arc(20, 25+9, 110, 75+9,  fill="#007f00", start=s, extent=ewon)
            c.create_arc(20, 25+9, 110, 75+9,  fill="#7f0000", start=s+ewon, extent=elost)
            c.create_arc(20, 25,   110, 75,    fill="#00ff00", start=s, extent=ewon)
            c.create_arc(20, 25,   110, 75,    fill="#ff0000", start=s+ewon, extent=elost)
            x, y = tx[0] - 25, ty[0]
            c.create_rectangle(x, y, x+10, y+10, fill="#00ff00")
            y = ty[1]
            c.create_rectangle(x, y, x+10, y+10, fill="#ff0000")
        else:
            c.create_oval(20, 25+10, 110, 75+10, fill="#7f7f7f")
            c.create_oval(20, 25,    110, 75,    fill="#f0f0f0")
            c.create_text(65, 50, text=_("No games"), anchor="center", font=tfont, fill="#bfbfbf")
        #
        self._createChartTexts(tx, ty, won, lost)

    #
    #
    #

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),
                               (_("&All games..."), 102),
                               (TOP_TITLE+"...", 105),
                               (_("&Reset..."), 302)), default=0,
                      image=self.app.gimages.logos[5],
                      padx=10, pady=10,
        )
        return MfxDialog.initKw(self, kw)


# ************************************************************************
# *
# ************************************************************************

class CanvasFormatter(PysolStatsFormatter):
    def __init__(self, app, canvas, parent_window, font, w, h):
        self.app = app
        self.canvas = canvas
        self.parent_window = parent_window
        ##self.fg = canvas.cget("insertbackground")
        self.fg = canvas.option_get('foreground', '') or canvas.cget("insertbackground")
        self.font = font
        self.w = w
        self.h = h
        #self.x = self.y = 0
        self.gameid = None
        self.gamenumber = None
        self.canvas.config(yscrollincrement=h)
        self._tabs = None

    def _addItem(self, id):
        self.canvas.dialog.nodes[id] = (self.gameid, self.gamenumber)

    def _calc_tabs(self, arg):
        tw = 15*self.w
        ##tw = 160
        self._tabs = [tw]
        font = tkFont.Font(self.canvas, self.font)
        for t in arg[1:]:
            tw = font.measure(t)+20
            self._tabs.append(tw)
        self._tabs.append(10)

    def pstats(self, y, args, gameid=None):
        x = 1
        t1, t2, t3, t4, t5, t6, t7 = args
        self.gameid = gameid
        if gameid is None:              # header
            self.gameid = 'header'
        for var, text, anchor, tab in (
            ('name',    t1, 'nw', self._tabs[0]+self._tabs[1]),
            ('played',  t2, 'ne', self._tabs[2]),
            ('won',     t3, 'ne', self._tabs[3]),
            ('lost',    t4, 'ne', self._tabs[4]),
            ('time',    t5, 'ne', self._tabs[5]),
            ('moves',   t6, 'ne', self._tabs[6]),
            ('percent', t7, 'ne', self._tabs[7]), ):
            self.gamenumber = None
            if gameid is None:          # header
                self.gamenumber=var
            id = self.canvas.create_text(x, y, text=text, anchor=anchor,
                                         font=self.font, fill=self.fg)
            self._addItem(id)
            x += tab
        self.pstats_perc(x, y, t7)

    def pstats_perc(self, x, y, t):
        if not (t and "0" <= t[0] <= "9"):
            return
        perc = int(round(float(str(t))))
        if perc < 1:
            return
        rx, ry, rw, rh = x, y+1, 2 + 8*10, self.h-5
        if 1:
            w = int(round(rw*perc/100.0))
            if 1 and w < 1:
                return
            if w > 0:
                w = max(3, w)
                w = min(rw - 2, w)
                id = self.canvas.create_rectangle(rx, ry, rx+w, ry+rh, width=1,
                                                  fill="#00ff00", outline="#000000")
            if w < rw:
                id = self.canvas.create_rectangle(rx+w, ry, rx+rw, ry+rh, width=1,
                                                  fill="#ff0000", outline="#000000")
            return
        ##fill = "#ffffff"
        ##fill = self.canvas["bg"]
        fill = None
        id = self.canvas.create_rectangle(rx, ry, rx+rw, ry+rh, width=1,
                                          fill=fill, outline="#808080")
        if 1:
            rx, rw = rx + 1, rw - 1
            ry, rh = ry + 1, rh - 1
            w = int(round(rw*perc/100.0))
            if w > 0:
                id = self.canvas.create_rectangle(rx, ry, rx+w, ry+rh, width=0,
                                                  fill="#00ff00", outline="")
            if w < rw:
                id = self.canvas.create_rectangle(rx+w, ry, rx+rw, ry+rh, width=0,
                                                  fill="#ff0000", outline="")
            return
        p = 1.0
        ix = rx + 2
        for i in (1, 11, 21, 31, 41, 51, 61, 71, 81, 91):
            if perc < i:
                break
            ##c = "#ff8040"
            r, g, b = 255, 128*p, 64*p
            c = "#%02x%02x%02x" % (int(r), int(g), int(b))
            id = self.canvas.create_rectangle(ix, ry+2, ix+6, ry+rh-2, width=0,
                                              fill=c, outline=c)
            ix = ix + 8
            p = max(0.0, p - 0.1)

    def writeStats(self, player, sort_by='name'):
        header = self.getStatHeader()
        y = 0
        if self._tabs is None:
            self._calc_tabs(header)
        self.pstats(y, header)
        #
        y += 2*self.h
        for result in self.getStatResults(player, sort_by):
            gameid = result.pop()
            self.pstats(y, result, gameid)
            y += self.h
        #
        y += self.h
        total, played, won, lost, time_, moves, perc = self.getStatSummary()
        s = _("Total (%d out of %d games)") % (played, total)
        self.pstats(y, (s, won+lost, won, lost, time_, moves, perc))

    def writeLog(self, player, prev_games):
        y = 0
        header = self.getLogHeader()
        t1, t2, t3, t4 = header
        s = "%-25s %-20s  %-17s  %s" % header
        id = self.canvas.create_text(1, y, text=s, anchor="nw",
                                     font=self.font, fill=self.fg)
        self._addItem(id)
        y += 2*self.h
        if not player or not prev_games:
            return 0
        for result in self.getLogResults(player, prev_games):
            s = "%-25s %-20s  %-17s  %s" % tuple(result[:4])
            id = self.canvas.create_text(1, y, text=s, anchor="nw",
                                         font=self.font, fill=self.fg)
            y += self.h
        return 1

    def writeFullLog(self, player):
        prev_games = self.app.stats.prev_games.get(player)
        return self.writeLog(player, prev_games)

    def writeSessionLog(self, player):
        prev_games = self.app.stats.session_games.get(player)
        return self.writeLog(player, prev_games)


# ************************************************************************
# *
# ************************************************************************

class AllGames_StatsDialogScrolledCanvas(MfxScrolledCanvas):
    pass


class AllGames_StatsDialog(MfxDialog):

    YVIEW = 0
    FONT_TYPE = "default"

    def __init__(self, parent, title, app, player, **kw):
        lines = 25
        #if parent and parent.winfo_screenheight() < 600:
        #    lines = 20
        #
        self.font = app.getFont(self.FONT_TYPE)
        font = tkFont.Font(parent, self.font)
        self.font_metrics = font.metrics()
        self.CHAR_H = self.font_metrics['linespace']
        self.CHAR_W = font.measure('M')
        self.app = app
        #
        self.player = player
        self.title = title
        self.sort_by = 'name'
        self.selected_game = None
        #
        kwdefault(kw, width=self.CHAR_W*64, height=lines*self.CHAR_H)
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.top.wm_minsize(200, 200)
        self.button = kw.default
        #
        self.sc = AllGames_StatsDialogScrolledCanvas(top_frame,
                                       width=kw.width, height=kw.height)
        self.sc.pack(fill='both', expand=True, padx=kw.padx, pady=kw.pady)
        #
        self.nodes = {}
        self.canvas = self.sc.canvas
        self.canvas.dialog = self
        bind(self.canvas, "<1>", self.singleClick)
        self.fillCanvas(player, title)
        bbox = self.canvas.bbox("all")
        ##print bbox
        ##self.canvas.config(scrollregion=bbox)
        dx, dy = 4, 0
        self.canvas.config(scrollregion=(-dx,-dy,bbox[2]+dx,bbox[3]+dy))
        self.canvas.xview_moveto(-dx)
        self.canvas.yview_moveto(self.YVIEW)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),
                               (_("&Save to file"), 202),
                               (_("&Reset all..."), 301),),
                      default=0,
                      resizable=True,
                      padx=10, pady=10,
                      #width=900,
        )
        return MfxDialog.initKw(self, kw)

    def destroy(self):
        self.app = None
        self.canvas.dialog = None
        self.nodes = {}
        self.sc.destroy()
        MfxDialog.destroy(self)

    def rearrange(self, sort_by):
        if self.sort_by == sort_by: return
        self.sort_by = sort_by
        self.fillCanvas(self.player, self.title)

    def singleClick(self, event=None):
        id = self.canvas.find_withtag('current')
        if not id:
            return
        ##print 'singleClick:', id, self.nodes.get(id[0])
        gameid, gamenumber = self.nodes.get(id[0], (None, None))
        if gameid == 'header':
            if self.sort_by == gamenumber: return
            self.sort_by = gamenumber
            self.fillCanvas(self.player, self.title)
            return
        ## FIXME / TODO
        return
        if gameid and gamenumber:
            print gameid, gamenumber
        elif gameid:
            print gameid

    #
    #
    #

    def fillCanvas(self, player, header):
        self.canvas.delete('all')
        self.nodes = {}
        writer = CanvasFormatter(self.app, self.canvas, self,
                              self.font, self.CHAR_W, self.CHAR_H)
        writer.writeStats(player, self.sort_by)


# ************************************************************************
# *
# ************************************************************************

class FullLog_StatsDialog(AllGames_StatsDialog):
    YVIEW = 1
    FONT_TYPE = "fixed"

    def fillCanvas(self, player, header):
        writer = CanvasFormatter(self.app, self.canvas, self,
                                 self.font, self.CHAR_W, self.CHAR_H)
        writer.writeFullLog(player)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), (_("Session &log..."), 104), (_("&Save to file"), 203)), default=0,
                      width=76*self.CHAR_W,
                      )
        return AllGames_StatsDialog.initKw(self, kw)


class SessionLog_StatsDialog(FullLog_StatsDialog):
    def fillCanvas(self, player, header):
        a = PysolStatsFormatter()
        writer = CanvasFormatter(self.app, self.canvas, self,
                                 self.font, self.CHAR_W, self.CHAR_H)
        writer.writeSessionLog(player)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), (_("&Full log..."), 103), (_("&Save to file"), 204)), default=0,
                      )
        return FullLog_StatsDialog.initKw(self, kw)

# ************************************************************************
# *
# ************************************************************************

class Status_StatsDialog(MfxMessageDialog):
    def __init__(self, parent, game):
        stats, gstats = game.stats, game.gstats
        w1 = w2 = ""
        n = 0
        for s in game.s.foundations:
            n = n + len(s.cards)
        w1 = (_("Highlight piles: ") + str(stats.highlight_piles) + "\n" +
              _("Highlight cards: ") + str(stats.highlight_cards) + "\n" +
              _("Highlight same rank: ") + str(stats.highlight_samerank) + "\n")
        if game.s.talon:
            if game.gameinfo.redeals != 0:
                w2 = w2 + _("\nRedeals: ") + str(game.s.talon.round - 1)
            w2 = w2 + _("\nCards in Talon: ") + str(len(game.s.talon.cards))
        if game.s.waste and game.s.waste not in game.s.foundations:
            w2 = w2 + _("\nCards in Waste: ") + str(len(game.s.waste.cards))
        if game.s.foundations:
            w2 = w2 + _("\nCards in Foundations: ") + str(n)
        #
        date = time.strftime("%Y-%m-%d %H:%M", time.localtime(game.gstats.start_time))
        MfxMessageDialog.__init__(self, parent, title=_("Game status"),
                                  text=game.getTitleName() + "\n" +
                                  game.getGameNumber(format=1) + "\n" +
                                  _("Playing time: ") + game.getTime() + "\n" +
                                  _("Started at: ") + date + "\n\n"+
                                  _("Moves: ") + str(game.moves.index) + "\n" +
                                  _("Undo moves: ") + str(stats.undo_moves) + "\n" +
                                  _("Bookmark moves: ") + str(gstats.goto_bookmark_moves) + "\n" +
                                  _("Demo moves: ") + str(stats.demo_moves) + "\n" +
                                  _("Total player moves: ") + str(stats.player_moves) + "\n" +
                                  _("Total moves in this game: ") + str(stats.total_moves) + "\n" +
                                  _("Hints: ") + str(stats.hints) + "\n" +
                                  "\n" +
                                  w1 + w2,
                                  strings=(_("&OK"),
                                           (_("&Statistics..."), 101),
                                           (TOP_TITLE+"...", 105), ),
                                  image=game.app.gimages.logos[3],
                                  image_side="left", image_padx=20,
                                  padx=20,
                                  )

# ************************************************************************
# *
# ************************************************************************

class _TopDialog(MfxDialog):
    def __init__(self, parent, title, top, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        cnf = {'master': top_frame,
               'highlightthickness': 1,
               'highlightbackground': 'black',
               }
        frame = Tkinter.Frame(**cnf)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        cnf['master'] = frame
        cnf['text'] = _('N')
        l = Tkinter.Label(**cnf)
        l.grid(row=0, column=0, sticky='ew')
        cnf['text'] = _('Game number')
        l = Tkinter.Label(**cnf)
        l.grid(row=0, column=1, sticky='ew')
        cnf['text'] = _('Started at')
        l = Tkinter.Label(**cnf)
        l.grid(row=0, column=2, sticky='ew')
        cnf['text'] = _('Result')
        l = Tkinter.Label(**cnf)
        l.grid(row=0, column=3, sticky='ew')

        row = 1
        for i in top:
            # N
            cnf['text'] = str(row)
            l = Tkinter.Label(**cnf)
            l.grid(row=row, column=0, sticky='ew')
            # Game number
            cnf['text'] = '#'+str(i.game_number)
            l = Tkinter.Label(**cnf)
            l.grid(row=row, column=1, sticky='ew')
            # Start time
            t = time.strftime('%Y-%m-%d %H:%M', time.localtime(i.game_start_time))
            cnf['text'] = t
            l = Tkinter.Label(**cnf)
            l.grid(row=row, column=2, sticky='ew')
            # Result
            if isinstance(i.value, float):
                # time
                s = format_time(i.value)
            else:
                # moves
                s = str(i.value)
            cnf['text'] = s
            l = Tkinter.Label(**cnf)
            l.grid(row=row, column=3, sticky='ew')
            row += 1

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


    def initKw(self, kw):
        kw = KwStruct(kw, strings=(_('&OK'),), default=0, separator=True)
        return MfxDialog.initKw(self, kw)


class Top_StatsDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):
        self.app = app
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = Tkinter.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        frame.columnconfigure(0, weight=1)

        if (player in app.stats.games_stats and
            gameid in app.stats.games_stats[player] and
            app.stats.games_stats[player][gameid].time_result.top):

            Tkinter.Label(frame, text=_('Minimum')).grid(row=0, column=1)
            Tkinter.Label(frame, text=_('Maximum')).grid(row=0, column=2)
            Tkinter.Label(frame, text=_('Average')).grid(row=0, column=3)
            ##Tkinter.Label(frame, text=_('Total')).grid(row=0, column=4)

            s = app.stats.games_stats[player][gameid]
            row = 1
            ll = [
                (_('Playing time:'),
                 format_time(s.time_result.min),
                 format_time(s.time_result.max),
                 format_time(s.time_result.average),
                 format_time(s.time_result.total),
                 s.time_result.top,
                 ),
                (_('Moves:'),
                 s.moves_result.min,
                 s.moves_result.max,
                 round(s.moves_result.average, 2),
                 s.moves_result.total,
                 s.moves_result.top,
                 ),
                (_('Total moves:'),
                 s.total_moves_result.min,
                 s.total_moves_result.max,
                 round(s.total_moves_result.average, 2),
                 s.total_moves_result.total,
                 s.total_moves_result.top,
                 ),
                ]
##             if s.score_result.min:
##                 ll.append(('Score:',
##                            s.score_result.min,
##                            s.score_result.max,
##                            round(s.score_result.average, 2),
##                            s.score_result.top,
##                            ))
##             if s.score_casino_result.min:
##                 ll.append(('Casino Score:',
##                            s.score_casino_result.min,
##                            s.score_casino_result.max,
##                            round(s.score_casino_result.average, 2), ))
            for l, min, max, avr, tot, top in ll:
                Tkinter.Label(frame, text=l).grid(row=row, column=0)
                Tkinter.Label(frame, text=str(min)).grid(row=row, column=1)
                Tkinter.Label(frame, text=str(max)).grid(row=row, column=2)
                Tkinter.Label(frame, text=str(avr)).grid(row=row, column=3)
                ##Tkinter.Label(frame, text=str(tot)).grid(row=row, column=4)
                b = Tkinter.Button(frame, text=TOP_TITLE+' ...', width=10,
                                   command=lambda top=top: self.showTop(top))
                b.grid(row=row, column=5)
                row += 1
        else:
            Tkinter.Label(frame, text=_('No TOP for this game')).pack()

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def showTop(self, top):
        #print top
        d = _TopDialog(self.top, TOP_TITLE, top)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_('&OK'),),
                      default=0,
                      image=self.app.gimages.logos[4],
                      separator=True,
                      )
        return MfxDialog.initKw(self, kw)


# ************************************************************************
# *
# ************************************************************************

class ProgressionDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):

        font_name = app.getFont('default')
        font = tkFont.Font(parent, font_name)
        tkfont = tkFont.Font(parent, font)
        font_metrics = font.metrics()
        measure = tkfont.measure
        self.text_height = font_metrics['linespace']
        self.text_width = measure('XX.XX.XX')

        self.items = []
        self.formatter = ProgressionFormatter(app, player, gameid)

        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = Tkinter.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        # constants
        self.canvas_width, self.canvas_height = 600, 250
        if parent.winfo_screenwidth() < 800 or \
               parent.winfo_screenheight() < 600:
            self.canvas_width, self.canvas_height = 400, 200
        self.xmargin, self.ymargin = 10, 10
        self.graph_dx, self.graph_dy = 10, 10
        self.played_color = '#ff7ee9'
        self.won_color = '#00dc28'
        self.percent_color = 'blue'
        # create canvas
        self.canvas = canvas = Tkinter.Canvas(frame, bg='#dfe8ff',
                                              highlightthickness=1,
                                              highlightbackground='black',
                                              width=self.canvas_width,
                                              height=self.canvas_height)
        canvas.pack(side='left', padx=5)
        #
        dir = os.path.join('images', 'stats')
        try:
            fn = app.dataloader.findImage('progression', dir)
            self.bg_image = loadImage(fn)
            canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
        except:
            pass
        #
        tw = max(measure(_('Games/day')),
                 measure(_('Games/week')),
                 measure(_('% won')))
        self.left_margin = self.xmargin+tw/2
        self.right_margin = self.xmargin+tw/2
        self.top_margin = 15+self.text_height
        self.bottom_margin = 15+self.text_height+10+self.text_height
        #
        x0, y0 = self.left_margin, self.canvas_height-self.bottom_margin
        x1, y1 = self.canvas_width-self.right_margin, self.top_margin
        canvas.create_rectangle(x0, y0, x1, y1, fill='white')
        # horizontal axis
        canvas.create_line(x0, y0, x1, y0, width=3)

        # left vertical axis
        canvas.create_line(x0, y0, x0, y1, width=3)
        t = _('Games/day')
        self.games_text_id = canvas.create_text(x0-4, y1-4, anchor='s', text=t)

        # right vertical axis
        canvas.create_line(x1, y0, x1, y1, width=3)
        canvas.create_text(x1+4, y1-4, anchor='s', text=_('% won'))

        # caption
        d = self.text_height
        x, y = self.xmargin, self.canvas_height-self.ymargin
        id = canvas.create_rectangle(x, y, x+d, y-d, outline='black',
                                     fill=self.played_color)
        x += d+5
        canvas.create_text(x, y, anchor='sw', text=_('Played'))
        x += measure(_('Played'))+20
        id = canvas.create_rectangle(x, y, x+d, y-d, outline='black',
                                     fill=self.won_color)
        x += d+5
        canvas.create_text(x, y, anchor='sw', text=_('Won'))
        x += measure(_('Won'))+20
        id = canvas.create_rectangle(x, y, x+d, y-d, outline='black',
                                     fill=self.percent_color)
        x += d+5
        canvas.create_text(x, y, anchor='sw', text=_('% won'))

        # right frame
        right_frame = Tkinter.Frame(frame)
        right_frame.pack(side='left', fill='x', padx=5)
        self.all_games_variable = var = Tkinter.StringVar()
        var.set('all')
        b = Tkinter.Radiobutton(right_frame, text=_('All games'),
                                variable=var, value='all',
                                command=self.updateGraph,
                                justify='left', anchor='w'
                                )
        b.pack(fill='x', expand=True, padx=3, pady=1)
        b = Tkinter.Radiobutton(right_frame, text=_('Current game'),
                                variable=var, value='current',
                                command=self.updateGraph,
                                justify='left', anchor='w'
                                )
        b.pack(fill='x', expand=True, padx=3, pady=1)
        label_frame = Tkinter.LabelFrame(right_frame, text=_('Statistics for'))
        label_frame.pack(side='top', fill='x', pady=10)
        self.variable = var = Tkinter.StringVar()
        var.set('week')
        for v, t in (
            ('week',  _('Last 7 days')),
            ('month', _('Last month')),
            ('year',  _('Last year')),
            ('all',   _('All time')),
            ):
            b = Tkinter.Radiobutton(label_frame, text=t, variable=var, value=v,
                                    command=self.updateGraph,
                                    justify='left', anchor='w'
                                    )
            b.pack(fill='x', expand=True, padx=3, pady=1)
        label_frame = Tkinter.LabelFrame(right_frame, text=_('Show graphs'))
        label_frame.pack(side='top', fill='x')
        self.played_graph_var = Tkinter.BooleanVar()
        self.played_graph_var.set(True)
        b = Tkinter.Checkbutton(label_frame, text=_('Played'),
                                command=self.updateGraph,
                                variable=self.played_graph_var,
                                justify='left', anchor='w'
                                )
        b.pack(fill='x', expand=True, padx=3, pady=1)
        self.won_graph_var = Tkinter.BooleanVar()
        self.won_graph_var.set(True)
        b = Tkinter.Checkbutton(label_frame, text=_('Won'),
                                command=self.updateGraph,
                                variable=self.won_graph_var,
                                justify='left', anchor='w'
                                )
        b.pack(fill='x', expand=True, padx=3, pady=1)
        self.percent_graph_var = Tkinter.BooleanVar()
        self.percent_graph_var.set(True)
        b = Tkinter.Checkbutton(label_frame, text=_('% won'),
                                command=self.updateGraph,
                                variable=self.percent_graph_var,
                                justify='left', anchor='w'
                                )
        b.pack(fill='x', expand=True, padx=3, pady=1)

        self.updateGraph()

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


    def initKw(self, kw):
        kw = KwStruct(kw, strings=(_('&OK'),), default=0, separator=True)
        return MfxDialog.initKw(self, kw)


    def updateGraph(self, *args):
        interval = self.variable.get()
        canvas = self.canvas
        if self.items:
            canvas.delete(*self.items)
        self.items = []

        all_games = (self.all_games_variable.get() == 'all')
        result = self.formatter.getResults(interval, all_games)

        if interval in ('week', 'month'):
            t = _('Games/day')
        else:
            t = _('Games/week')
        canvas.itemconfig(self.games_text_id, text=t)

        graph_width = self.canvas_width-self.left_margin-self.right_margin
        graph_height = self.canvas_height-self.top_margin-self.bottom_margin
        dx = (graph_width-2*self.graph_dx)/(len(result)-1)
        graph_dx = (graph_width-(len(result)-1)*dx)/2
        dy = (graph_height-self.graph_dy)/5
        x0, y0 = self.left_margin, self.canvas_height-self.bottom_margin
        x1, y1 = self.canvas_width-self.right_margin, self.top_margin
        td = self.text_height/2

        # vertical scale
        x = x0+graph_dx
        xx = -100
        for res in result:
            if res[0] is not None and x > xx+self.text_width+4:
                ##id = canvas.create_line(x, y0, x, y0-5, width=3)
                ##self.items.append(id)
                id = canvas.create_line(x, y0, x, y1, stipple='gray50')
                self.items.append(id)
                id = canvas.create_text(x, y0+td, anchor='n', text=res[0])
                self.items.append(id)
                xx = x
            else:
                id = canvas.create_line(x, y0, x, y0-3, width=1)
                self.items.append(id)
            x += dx

        # horizontal scale
        max_games = max([i[1] for i in result])
        games_delta = max_games/5+1
        percent = 0
        games = 0
        for y in range(y0, y1, -dy):
            if y != y0:
                id = canvas.create_line(x0, y, x1, y, stipple='gray50')
                self.items.append(id)
            id = canvas.create_text(x0-td, y, anchor='e', text=str(games))
            self.items.append(id)
            id = canvas.create_text(x1+td, y, anchor='w', text=str(percent))
            self.items.append(id)
            games += games_delta
            percent += 20

        # draw result
        games_resolution = float(dy)/games_delta
        percent_resolution = float(dy)/20
        played_coords = []
        won_coords = []
        percent_coords = []
        x = x0+graph_dx
        for res in result:
            played, won = res[1], res[2]
            y = y0 - int(games_resolution*played)
            played_coords += [x,y]
            y = y0 - int(games_resolution*won)
            won_coords += [x,y]
            if played > 0:
                percent = int(100.*won/played)
            else:
                percent = 0
            y = y0 - int(percent_resolution*percent)
            percent_coords += [x,y]
            x += dx
        if self.played_graph_var.get():
            id = canvas.create_line(fill=self.played_color, width=3,
                                    *played_coords)
            self.items.append(id)
        if self.won_graph_var.get():
            id = canvas.create_line(fill=self.won_color, width=3,
                                    *won_coords)
            self.items.append(id)
        if self.percent_graph_var.get():
            id = canvas.create_line(fill=self.percent_color, width=3,
                                    *percent_coords)
            self.items.append(id)

