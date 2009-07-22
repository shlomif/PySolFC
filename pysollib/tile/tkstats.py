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
import Tkinter
import ttk
import tkFont

# PySol imports
from pysollib.mfxutil import KwStruct
from pysollib.mfxutil import format_time
##from pysollib.util import *
from pysollib.stats import PysolStatsFormatter, ProgressionFormatter
from pysollib.settings import TOP_TITLE

# Toolkit imports
from tkutil import bind, unbind_destroy, loadImage
from tkwidget import MfxDialog, MfxMessageDialog


# ************************************************************************
# *
# ************************************************************************

class StatsDialog(MfxDialog):
    SELECTED_TAB = 0

    def __init__(self, parent, title, app, player, gameid, **kw):

        kw = self.initKw(kw)
        title = _('Statistics')
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)

        self.font = app.getFont('default')
        self.tkfont = tkFont.Font(parent, self.font)
        self.font_metrics = self.tkfont.metrics()
        style = ttk.Style(parent)
        heading_font = style.lookup('Heading', 'font') # treeview heading
        self.heading_tkfont = tkFont.Font(parent, heading_font)

        self.selected_game = None

        top_frame, bottom_frame = self.createFrames(kw)
        notebook = ttk.Notebook(top_frame)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.notebook_tabs = []

        single_frame = SingleGameFrame(self, notebook, app, player, gameid)
        notebook.add(single_frame, text=_('Current game'))
        self.notebook_tabs.append(single_frame._w)

        all_frame = AllGamesFrame(self, notebook, app, player)
        notebook.add(all_frame, text=_('All games'))
        self.all_games_frame = all_frame
        self.notebook_tabs.append(all_frame._w)

        top_frame = TopFrame(self, notebook, app, player, gameid)
        notebook.add(top_frame, text=TOP_TITLE)
        self.notebook_tabs.append(top_frame._w)

        if player is not None:
            progr_frame = ProgressionFrame(self, notebook, app, player, gameid)
            notebook.add(progr_frame, text=_('Progression'))
            self.notebook_tabs.append(progr_frame._w)

        if StatsDialog.SELECTED_TAB < len(self.notebook_tabs):
            notebook.select(StatsDialog.SELECTED_TAB)
        bind(notebook, '<<NotebookTabChanged>>', self.tabChanged)
        ##notebook.enableTraversal()
        self.notebook = notebook

        focus = self.createButtons(bottom_frame, kw)
        self.tabChanged()               # configure buttons state
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=((_("&Play this game"), 401),
                               "sep", _("&OK"),
                               (_("&Reset..."), 500)),
                      default=0,
                      separator=False,
        )
        return MfxDialog.initKw(self, kw)

    def tabChanged(self, *args):
        w = self.notebook.select()
        run_button = self.buttons[0]
        indx = self.notebook_tabs.index(w)
        if indx == 1:                   # "All games"
            g = self.all_games_frame.getSelectedGame()
            if g is None:
                run_button.config(state='disabled')
            else:
                run_button.config(state='normal')
        else:
            run_button.config(state='disabled')
        reset_button = self.buttons[2]
        if indx in (0, 1):              # "Current game" or "All games"
            reset_button.config(state='normal')
        else:
            reset_button.config(state='disabled')


    def mDone(self, button):
        self.selected_game = self.all_games_frame.getSelectedGame()
        w = self.notebook.select()
        indx = self.notebook_tabs.index(w)
        StatsDialog.SELECTED_TAB = indx
        if button == 500:               # "Reset..."
            assert indx in (0, 1)
            if indx == 0:               # "Current game"
                button = 302
            else:                       # "All games"
                button = 301
        MfxDialog.mDone(self, button)


SingleGame_StatsDialog = AllGames_StatsDialog = Top_StatsDialog = ProgressionDialog = StatsDialog


# ************************************************************************
# *
# ************************************************************************

class SingleGameFrame(ttk.Frame):
    def __init__(self, dialog, parent, app, player, gameid, **kw):
        ttk.Frame.__init__(self, parent)

        self.oval_width = 120
        self.oval_height = 60

        left_label = ttk.Label(self, image=app.gimages.logos[5])
        left_label.pack(side='left', expand=True, fill='both')
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side='right', expand=True)

        self.dialog = dialog
        self.app = app
        self.parent = parent
        self.player = player or _("Demo games")
        #
        self._calc_tabs()
        #
        won, lost = app.stats.getStats(player, gameid)
        self.createPieChart(app, won, lost, _("Total"))
        won, lost = app.stats.getSessionStats(player, gameid)
        self.createPieChart(app, won, lost, _("Current session"))
        #

    #
    # helpers
    #

    def _calc_tabs(self):
        #
        font = self.dialog.tkfont
        t0 = self.oval_width+70
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
        tx = (t0, t0+t1+t2, t0+t1+t2+t3, t0+t1+t2+t3+20)
        #
        ls = self.dialog.font_metrics['linespace']
        ls += 5
        #ls = max(ls, 20)
        ty = (5, 5+ls, 5+2*ls+15, max(85, 5+3*ls+15))
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
        frame = ttk.LabelFrame(self.right_frame, text=text)
        frame.pack(side='top', fill='both', expand=False, padx=20, pady=10)
        style = ttk.Style(self.parent)
        fg = style.lookup('.', 'foreground') or None # use default if fg == ''
        bg = style.lookup('.', 'background') or None
        self.fg = fg
        #
        w, h = self.tab_x[-1], max(self.tab_y[-1], self.oval_height+40)
        c = Tkinter.Canvas(frame, width=w, height=h,
                           bg=bg, highlightthickness=0)
        c.pack(fill='both', expand=True)
        self.canvas = c

    def _createChartTexts(self, tx, ty, won, lost):
        c, tfont, fg = self.canvas, self.dialog.font, self.fg
        pwon, plost = self._getPwon(won, lost)
        #
        x = tx[0]
        dy = int(self.dialog.font_metrics['ascent']) - 10
        dy = dy/2
        c.create_text(x, ty[0]-dy, text=_("Won:"),
                      anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[1]-dy, text=_("Lost:"),
                      anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[2]-dy, text=_("Total:"),
                      anchor="nw", font=tfont, fill=fg)
        x = tx[1] - 16
        c.create_text(x, ty[0]-dy, text="%d" % won,
                      anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[1]-dy, text="%d" % lost,
                      anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[2]-dy, text="%d" % (won + lost),
                      anchor="ne", font=tfont, fill=fg)
        y = ty[2] - 11
        c.create_line(tx[0], y, x, y, fill=fg)
        if won + lost > 0:
            x = tx[2]
            pw = int(round(100.0 * pwon))
            c.create_text(x, ty[0]-dy, text="%d%%" % pw,
                          anchor="ne", font=tfont, fill=fg)
            c.create_text(x, ty[1]-dy, text="%d%%" % (100-pw),
                          anchor="ne", font=tfont, fill=fg)


    def createPieChart(self, app, won, lost, text):
        #c, tfont, fg = self._createChartInit(frame, 300, 100, text)
        #
        self._createChartInit(text)
        c, tfont, fg = self.canvas, self.dialog.font, self.fg
        pwon, plost = self._getPwon(won, lost)
        #
        #tx = (160, 250, 280)
        #ty = (21, 41, 75)
        #
        tx, ty = self.tab_x, self.tab_y
        x0, y0 = 20, 10                 # base coords
        w = self.oval_width
        h = self.oval_height
        d = 9                           # delta
        if won + lost > 0:
            ##s, ewon, elost = 90.0, -360.0 * pwon, -360.0 * plost
            s, ewon, elost = 0.0, 360.0 * pwon, 360.0 * plost
            c.create_arc(x0, y0+d, x0+w, y0+h+d, fill="#007f00",
                         start=s, extent=ewon)
            c.create_arc(x0, y0+d, x0+w, y0+h+d, fill="#7f0000",
                         start=s+ewon, extent=elost)
            c.create_arc(x0, y0,   x0+w, y0+h,   fill="#00ff00",
                         start=s, extent=ewon)
            c.create_arc(x0, y0,   x0+w, y0+h,   fill="#ff0000",
                         start=s+ewon, extent=elost)
            x, y = tx[0] - 25, ty[0]
            c.create_rectangle(x, y, x+10, y+10, fill="#00ff00")
            y = ty[1]
            c.create_rectangle(x, y, x+10, y+10, fill="#ff0000")
        else:
            c.create_oval(x0, y0+d, x0+w, y0+h+d, fill="#7f7f7f")
            c.create_oval(x0, y0,   x0+w, y0+h,   fill="#f0f0f0")
            c.create_text(x0+w/2, y0+h/2, text=_("No games"),
                          anchor="center", font=tfont, fill="#bfbfbf")
        #
        self._createChartTexts(tx, ty, won, lost)


# ************************************************************************
# *
# ************************************************************************

class TreeFormatter(PysolStatsFormatter):
    MAX_ROWS = 10000

    def __init__(self, app, tree, parent_window, font, w, h):
        self.app = app
        self.tree = tree
        self.parent_window = parent_window
        self.tkfont = font
        self.gameid = None
        self.gamenumber = None
        self._tabs = None
        self.w = w
        self.h = h

    def _calc_tabs(self, arg):
        if self.parent_window.tree_tabs:
            self._tabs = self.parent_window.tree_tabs
            return
        tw = 20*self.w
        ##tw = 160
        self._tabs = [tw]
        measure = self.tkfont.measure
        for t in arg[1:]:
            tw = measure(t)+8
            self._tabs.append(tw)
        self._tabs.append(10)
        self.parent_window.tree_tabs = self._tabs

    def createHeader(self, player, header):
        i = 0
        for column in ('#0',) + self.parent_window.COLUMNS:
            text = header[i]
            anchor = i == 0 and 'nw' or 'ne'
            self.tree.heading(column, text=text,
                command=lambda par=self.parent_window, col=column: par.headerClick(col))
            self.tree.column(column, width=16)
            i += 1

    def resizeHeader(self, player, header, tree_width=0):
        if self._tabs is not None:
            return
        self._calc_tabs(header)
        # set first column width
        if tree_width != 0:
            tab = tree_width - sum(self._tabs[1:])
            tab = min(tree_width, self._tabs[0])
        else:
            tab = self._tabs[0]
        self.tree.column('#0', width=tab)
        # other column
        i = 1
        for column in self.parent_window.COLUMNS:
            tab = self._tabs[i]
            self.tree.column(column, width=tab)
            i += 1

    def writeStats(self, player, sort_by='name'):
        header = self.getStatHeader()
        tree_width = self.tree.winfo_width()
        self.resizeHeader(player, header, tree_width)

        for result in self.getStatResults(player, sort_by):
            # result == [name, won+lost, won, lost, time, moves, perc, id]
            t1, t2, t3, t4, t5, t6, t7, t8 = result
            id = self.tree.insert("", "end", text=t1,
                                  values=(t2, t3, t4, t5, t6, t7))
            self.parent_window.tree_items.append(id)
            self.parent_window.games[id] = t8

        total, played, won, lost, time_, moves, perc = self.getStatSummary()
        text = _("Total (%d out of %d games)") % (played, total)
        id = self.tree.insert("", "end", text=text,
                              values=(won+lost, won, lost, time_, moves, perc))
        self.parent_window.tree_items.append(id)
        return 1

    def writeLog(self, player, prev_games):
        if not player or not prev_games:
            return 0
        num_rows = 0
        for result in self.getLogResults(player, prev_games):
            t1, t2, t3, t4, t5, t6 = result
            id = self.tree.insert("", "end", text=t1, values=(t2, t3, t4))
            self.parent_window.tree_items.append(id)
            num_rows += 1
            if num_rows > self.MAX_ROWS:
                break
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

class AllGamesFrame(ttk.Frame):

    COLUMNS = ('played', 'won', 'lost', 'time', 'moves', 'percent')

    def __init__(self, dialog, parent, app, player, **kw):
        ttk.Frame.__init__(self, parent)
        #
        self.dialog = dialog
        self.app = app
        self.CHAR_H = self.dialog.font_metrics['linespace']
        self.CHAR_W = self.dialog.tkfont.measure('M')
        #
        self.player = player
        self.sort_by = 'name'
        self.tree_items = []
        self.tree_tabs = None
        self.games = {}                 # tree_itemid: gameid
        #
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        vsb = ttk.Scrollbar(frame)
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree = ttk.Treeview(frame, columns=self.COLUMNS,
                                 selectmode='browse')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.config(yscrollcommand=vsb.set)
        vsb.config(command=self.tree.yview)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        hsb = ttk.Scrollbar(frame, orient='horizontal')
        hsb.grid(row=1, column=0, sticky='ew')
        self.tree.config(xscrollcommand=hsb.set)
        hsb.config(command=self.tree.xview)
        bind(self.tree, '<<TreeviewSelect>>', self.treeviewSelected)
        #
        self.formatter = TreeFormatter(self.app, self.tree, self,
                                       self.dialog.heading_tkfont,
                                       self.CHAR_W, self.CHAR_H)
        self.createHeader(player)
        bind(self.tree, '<Map>', self.mapEvent)

    def getSelectedGame(self):
        sel = self.tree.selection()
        if sel and len(sel) == 1:
            if sel[0] in self.games:
                return self.games[sel[0]]
        return None

    def treeviewSelected(self, *args):
        sel = self.tree.selection()
        run_button = self.dialog.buttons[0]
        if sel and len(sel) == 1:
            if sel[0] not in self.games: # "Total"
                run_button.config(state='disabled')
            else:
                run_button.config(state='normal')
        else:
            run_button.config(state='disabled')

    def mapEvent(self, *args):
        if not self.tree_items:
            self.fillTreeview(self.player)

    def headerClick(self, column):
        if column == '#0':
            sort_by = 'name'
        else:
            sort_by = column
        if self.sort_by == sort_by: return
        self.sort_by = sort_by
        self.fillTreeview(self.player)

    def createHeader(self, player):
        header = self.formatter.getStatHeader()
        self.formatter.createHeader(player, header)

    def fillTreeview(self, player):
        if self.tree_items:
            self.tree.delete(tuple(self.tree_items))
            self.tree_items = []
        self.formatter.writeStats(player, sort_by=self.sort_by)
        if self.dialog.buttons:
            run_button = self.dialog.buttons[0]
            run_button.config(state='disabled')


# ************************************************************************
# *
# ************************************************************************

class LogDialog(MfxDialog):
    SELECTED_TAB = 0

    def __init__(self, parent, title, app, player, **kw):

        self.font = app.getFont('default')
        self.tkfont = tkFont.Font(parent, self.font)
        style = ttk.Style(parent)
        heading_font = style.lookup('Heading', 'font') # treeview heading
        self.heading_tkfont = tkFont.Font(parent, heading_font)
        self.font_metrics = self.tkfont.metrics()

        self.CHAR_H = self.font_metrics['linespace']
        self.CHAR_W = self.tkfont.measure('M')

        kw = self.initKw(kw)
        title = _('Log')
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)

        ##self.selected_game = None

        top_frame, bottom_frame = self.createFrames(kw)
        notebook = ttk.Notebook(top_frame)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.notebook_tabs = []

        full_frame = FullLogFrame(self, notebook, app, player)
        notebook.add(full_frame, text=_('Full log'))
        self.notebook_tabs.append(full_frame._w)

        session_frame = SessionLogFrame(self, notebook, app, player)
        notebook.add(session_frame, text=_('Session log'))
        self.notebook_tabs.append(session_frame._w)

        notebook.select(LogDialog.SELECTED_TAB)
##         bind(notebook, '<<NotebookTabChanged>>', self.tabChanged)

        self.notebook = notebook

        focus = self.createButtons(bottom_frame, kw)
        ##self.tabChanged()               # configure buttons state
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),
                               (_("&Save to file"), 500)),
                      default=0,
                      width=76*self.CHAR_W,
                      separator=False,
                      )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        ##self.selected_game = self.all_games_frame.getSelectedGame()
        w = self.notebook.select()
        indx = self.notebook_tabs.index(w)
        LogDialog.SELECTED_TAB = indx
        if button == 500:               # "Save to file"
            assert indx in (0, 1)
            if indx == 0:               # "Full log"
                button = 203
            else:                       # "Session log"
                button = 204
        MfxDialog.mDone(self, button)

FullLog_StatsDialog = SessionLog_StatsDialog = LogDialog


# ************************************************************************
# *
# ************************************************************************

class FullLogFrame(AllGamesFrame):

    COLUMNS = ('gamenumber', 'date', 'status')

    def __init__(self, dialog, parent, app, player, **kw):
        AllGamesFrame.__init__(self, dialog, parent, app, player, **kw)
        header = ('', '99999999999999999999', '9999-99-99  99:99',
                  'XXXXXXXXXXXX')
        self.formatter.resizeHeader(player, header)

    def createHeader(self, player):
        header = self.formatter.getLogHeader()
        self.formatter.createHeader(player, header)

    def fillTreeview(self, player):
        if self.tree_items:
            return
        self.formatter.writeFullLog(player)

    def treeviewSelected(self, *args):
        pass
    def headerClick(self, column):
        pass


class SessionLogFrame(FullLogFrame):
    def fillTreeview(self, player):
        if self.tree_items:
            return
        self.formatter.writeSessionLog(player)


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
        MfxMessageDialog.__init__(
            self, parent, title=_("Game status"),
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
            strings=((_("&Statistics..."), 101),
                     'sep',
                     _("&OK")),
            image=game.app.gimages.logos[3],
            image_side="left", image_padx=20,
            padx=20,
            )


# ************************************************************************
# *
# ************************************************************************

class _TopDialog(MfxDialog):
    def __init__(self, parent, title, app, gameid, top, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        cnf = {'master': top_frame,
               'padding': (4, 1),
               }
        frame = ttk.Frame(**cnf)
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        frame.columnconfigure(0, weight=1)
        cnf['master'] = frame
        cnf['text'] = _('N')
        l = ttk.Label(**cnf)
        l.grid(row=0, column=0, sticky='ew')
        if gameid == 'all':
            cnf['text'] = _('Game')
            l = ttk.Label(**cnf)
            l.grid(row=0, column=1, sticky='ew')
        cnf['text'] = _('Game number')
        l = ttk.Label(**cnf)
        l.grid(row=0, column=2, sticky='ew')
        cnf['text'] = _('Started at')
        l = ttk.Label(**cnf)
        l.grid(row=0, column=3, sticky='ew')
        cnf['text'] = _('Result')
        l = ttk.Label(**cnf)
        l.grid(row=0, column=4, sticky='ew')

        row = 1
        for i in top:
            # N
            cnf['text'] = str(row)
            l = ttk.Label(**cnf)
            l.grid(row=row, column=0, sticky='ew')
            if gameid == 'all':
                name = app.getGameTitleName(i.gameid)
                if name is None:
                    name = _("** UNKNOWN %d **") % i.gameid
                cnf['text'] = name
                l = ttk.Label(**cnf)
                l.grid(row=row, column=1, sticky='ew')
            # Game number
            cnf['text'] = '#'+str(i.game_number)
            l = ttk.Label(**cnf)
            l.grid(row=row, column=2, sticky='ew')
            # Start time
            t = time.strftime('%Y-%m-%d %H:%M', time.localtime(i.game_start_time))
            cnf['text'] = t
            l = ttk.Label(**cnf)
            l.grid(row=row, column=3, sticky='ew')
            # Result
            if isinstance(i.value, float):
                # time
                s = format_time(i.value)
            else:
                # moves
                s = str(i.value)
            cnf['text'] = s
            l = ttk.Label(**cnf)
            l.grid(row=row, column=4, sticky='ew')
            row += 1

        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


    def initKw(self, kw):
        kw = KwStruct(kw, strings=(_('&OK'),), default=0, separator=True)
        return MfxDialog.initKw(self, kw)


class TopFrame(ttk.Frame):
    def __init__(self, dialog, parent, app, player, gameid):
        ttk.Frame.__init__(self, parent)

        self.app = app
        self.dialog = dialog

        left_label = ttk.Label(self, image=app.gimages.logos[5])
        left_label.pack(side='left', expand=True, fill='both')

        frame = ttk.LabelFrame(self, text=_('Current game'),
                               padding=(10,5,10,10))
        frame.pack(side='top', expand=True, fill='x', padx=10, pady=10)
        ##frame.columnconfigure(0, weight=1)
        if not self.createTopFrame(frame, player, gameid):
            ttk.Label(frame, text=_('No TOP for this game')
                      ).pack(padx=10, pady=10)

        frame = ttk.LabelFrame(self, text=_('All games'),
                               padding=(10,5,10,10))
        frame.pack(side='top', expand=True, fill='x', padx=10, pady=10)
        ##frame.columnconfigure(0, weight=1)
        if not self.createTopFrame(frame, player, 'all'):
            ttk.Label(frame, text=_('No TOP for all games')
                      ).pack(padx=10, pady=10)

    def createTopFrame(self, frame, player, gameid):
        app = self.app

        if (player not in app.stats.games_stats or
            gameid not in app.stats.games_stats[player] or
            not app.stats.games_stats[player][gameid].time_result.top):
            return False

        ttk.Label(frame, text=_('Minimum')
                  ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame, text=_('Maximum')
                  ).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(frame, text=_('Average')
                  ).grid(row=0, column=3, padx=5, pady=5)
        ##ttk.Label(frame, text=_('Total')).grid(row=0, column=4)

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
            ttk.Label(frame, text=l
                      ).grid(row=row, column=0, padx=5, pady=5)
            ttk.Label(frame, text=str(min)
                      ).grid(row=row, column=1, padx=5, pady=5)
            ttk.Label(frame, text=str(max)
                      ).grid(row=row, column=2, padx=5, pady=5)
            ttk.Label(frame, text=str(avr)
                      ).grid(row=row, column=3, padx=5, pady=5)
            ##ttk.Label(frame, text=str(tot)).grid(row=row, column=4)
            def command(gameid=gameid, top=top):
                self.showTop(gameid, top)
            b = ttk.Button(frame, text=TOP_TITLE+' ...',
                           width=10, command=command)
            b.grid(row=row, column=5)
            row += 1
        return True

    def showTop(self, gameid, top):
        d = _TopDialog(self.dialog.top, TOP_TITLE, self.app, gameid, top)


# ************************************************************************
# *
# ************************************************************************

class ProgressionFrame(ttk.Frame):

    def __init__(self, dialog, parent, app, player, gameid, **kw):
        ttk.Frame.__init__(self, parent)

        self.mapped = False

        self.dialog = dialog
        self.app = app
        self.player = player
        self.gameid = gameid
        self.items = []
        self.formatter = ProgressionFormatter(app, player, gameid)

        frame = ttk.Frame(self)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        # constants
        w = dialog.tkfont.measure('M') * 42
        w = max(w, 500)
        w = min(w, 600)
        self.canvas_width, self.canvas_height = w, 250
        if parent.winfo_screenwidth() < 800 or \
               parent.winfo_screenheight() < 600:
            self.canvas_width, self.canvas_height = 400, 200
        self.xmargin, self.ymargin = 10, 10
        self.graph_dx, self.graph_dy = 10, 10
        self.played_color = '#ff7ee9'
        self.won_color = '#00dc28'
        self.percent_color = 'blue'
        # create canvas
        self.canvas = canvas = Tkinter.Canvas(frame, bg='#dfe8ff', bd=0,
                                              highlightthickness=1,
                                              highlightbackground='black',
                                              width=self.canvas_width,
                                              height=self.canvas_height)
        canvas.pack(side='left', padx=5)

        # right frame
        right_frame = ttk.Frame(frame)
        right_frame.pack(side='left', fill='x', padx=5)
        self.all_games_variable = var = Tkinter.StringVar()
        var.set('all')
        b = ttk.Radiobutton(right_frame, text=_('All games'),
                            variable=var, value='all',
                            command=self.updateGraph)
        b.pack(fill='x', expand=True, padx=3, pady=1)
        b = ttk.Radiobutton(right_frame, text=_('Current game'),
                            variable=var, value='current',
                            command=self.updateGraph)
        b.pack(fill='x', expand=True, padx=3, pady=1)
        label_frame = ttk.LabelFrame(right_frame, text=_('Statistics for'))
        label_frame.pack(side='top', fill='x', pady=10)
        self.variable = var = Tkinter.StringVar()
        var.set('week')
        for v, t in (
            ('week',  _('Last 7 days')),
            ('month', _('Last month')),
            ('year',  _('Last year')),
            ('all',   _('All time')),
            ):
            b = ttk.Radiobutton(label_frame, text=t, variable=var,
                                value=v, command=self.updateGraph)
            b.pack(fill='x', expand=True, padx=3, pady=1)
        label_frame = ttk.LabelFrame(right_frame, text=_('Show graphs'))
        label_frame.pack(side='top', fill='x')
        self.played_graph_var = Tkinter.BooleanVar()
        self.played_graph_var.set(True)
        b = ttk.Checkbutton(label_frame, text=_('Played'),
                            command=self.updateGraph,
                            variable=self.played_graph_var)
        b.pack(fill='x', expand=True, padx=3, pady=1)
        self.won_graph_var = Tkinter.BooleanVar()
        self.won_graph_var.set(True)
        b = ttk.Checkbutton(label_frame, text=_('Won'),
                            command=self.updateGraph,
                            variable=self.won_graph_var)
        b.pack(fill='x', expand=True, padx=3, pady=1)
        self.percent_graph_var = Tkinter.BooleanVar()
        self.percent_graph_var.set(True)
        b = ttk.Checkbutton(label_frame, text=_('% won'),
                            command=self.updateGraph,
                            variable=self.percent_graph_var)
        b.pack(fill='x', expand=True, padx=3, pady=1)

        #self.createGraph()
        bind(canvas, '<Map>', self.createGraph)


    def createGraph(self, event):
        if self.mapped:
            return
        self.mapped = True

        canvas = self.canvas

        self.text_height = self.dialog.font_metrics['linespace']
        measure = self.dialog.tkfont.measure
        self.text_width_1 = measure('XX.XX')
        self.text_width_2 = measure('XX.XX.XX')

        dir = os.path.join('images', 'stats')
        try:
            fn = self.app.dataloader.findImage('progression', dir)
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

        self.updateGraph()


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
        xx = -100                       # coord. of prev. text
        for res in result:
            text = res[0]
            text_width = 0
            if text is not None:
                if len(text) == 5:      # day.month
                    text_width = self.text_width_1
                else:                   # day.month.year
                    text_width = self.text_width_2
            if text is not None and x > xx+text_width+4:
                ##id = canvas.create_line(x, y0, x, y0-5, width=3)
                ##self.items.append(id)
                id = canvas.create_line(x, y0, x, y1, stipple='gray50')
                self.items.append(id)
                id = canvas.create_text(x, y0+td, anchor='n', text=text)
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


