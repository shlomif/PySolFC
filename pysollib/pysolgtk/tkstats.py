## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
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
## Markus F.X.J. Oberhumer
## <markus.oberhumer@jk.uni-linz.ac.at>
## http://wildsau.idv.uni-linz.ac.at/mfx/pysol.html
##
##---------------------------------------------------------------------------##


# imports
import os, sys, time
import gtk, gobject, pango
import gtk.glade

# PySol imports
from pysollib.mfxutil import format_time
from pysollib.settings import TOP_TITLE
from pysollib.stats import PysolStatsFormatter

# Toolkit imports
from tkwidget import MfxDialog, MfxMessageDialog


glade_file = os.path.join(sys.path[0], 'data', 'pysolfc.glade')

open(glade_file)


# /***********************************************************************
# //
# ************************************************************************/

class StatsWriter(PysolStatsFormatter.StringWriter):
    def __init__(self, store):
        self.store = store

    def p(self, s):
        pass

    def pheader(self, s):
        pass

    def pstats(self, *args, **kwargs):
        gameid=kwargs.get('gameid', None)
        if gameid is None:
            # header
            return
        iter = self.store.append(None)
        self.store.set(iter,
                       0, args[0],
                       1, args[1],
                       2, args[2],
                       3, args[3],
                       4, args[4],
                       5, args[5],
                       6, args[6],
                       7, gameid)


class FullLogWriter(PysolStatsFormatter.StringWriter):
    def __init__(self, store):
        self.store = store

    def p(self, s):
        pass

    def pheader(self, s):
        pass

    def plog(self, gamename, gamenumber, date, status, gameid=-1, won=-1):
        if gameid < 0:
            # header
            return
        iter = self.store.append(None)
        self.store.set(iter,
                       0, gamename,
                       1, gamenumber,
                       2, date,
                       3, status,
                       4, gameid)


class Game_StatsDialog:

    def __init__(self, parent, header, app, player, gameid):
        #
        self.app = app
        
        formatter = PysolStatsFormatter(self.app)
        #
        self.widgets_tree = gtk.glade.XML(glade_file)
        #game_name_combo = self.widgets_tree.get_widget('game_name_combo')
        #model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        #game_name_combo.set_model(model)
        #game_name_combo.set_text_column(0)
        stats_dialog = self.widgets_tree.get_widget('stats_dialog')
        stats_dialog.set_title('Game Statistics')
        stats_dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        # total
        won, lost = app.stats.getStats(player, gameid)
        self._createText('total', won, lost)
        drawing = self.widgets_tree.get_widget('total_drawingarea')
        drawing.connect('expose_event', self._createChart, won, lost)
        # current session
        won, lost = app.stats.getSessionStats(player, gameid)
        self._createText('current', won, lost)
        drawing = self.widgets_tree.get_widget('session_drawingarea')
        drawing.connect('expose_event', self._createChart, won, lost)
        #
        store = self._createStatsList()
        writer = StatsWriter(store)
        formatter.writeStats(writer, player, header, sort_by='name')
        #
        store = self._createLogList('full_log_treeview')
        writer = FullLogWriter(store)
        formatter.writeFullLog(writer, player, header)
        #
        store = self._createLogList('session_log_treeview')
        writer = FullLogWriter(store)
        formatter.writeSessionLog(writer, player, header)
        #
        stats_dialog.set_transient_for(parent)
        stats_dialog.resize(400, 300)

        stats_dialog.run()
        self.status = -1
        stats_dialog.destroy()


    def _createText(self, name, won, lost):
        pwon, plost = self._getPwon(won, lost)
        label = self.widgets_tree.get_widget(name+'_num_won_label')
        label.set_text(str(won))
        label = self.widgets_tree.get_widget(name+'_num_lost_label')
        label.set_text(str(lost))
        label = self.widgets_tree.get_widget(name+'_percent_won_label')
        label.set_text(str(int(round(pwon*100)))+'%')
        label = self.widgets_tree.get_widget(name+'_percent_lost_label')
        label.set_text(str(int(round(plost*100)))+'%')
        label = self.widgets_tree.get_widget(name+'_num_total_label')
        label.set_text(str(won+lost))


    def _createChart(self, drawing, e, won, lost):
        pwon, plost = self._getPwon(won, lost)
        s, ewon, elost = 0, int(360.0*pwon), int(360.0*plost)

        win = drawing.window
        colormap = drawing.get_colormap()
        gc = win.new_gc()
        gc.set_colormap(colormap)

        alloc = drawing.allocation
        width, height = alloc.width, alloc.height
        w, h = 90, 50
        ##x, y = 10, 10
        x, y = (width-w)/2, (height-h)/2
        dy = 9
        y = y-dy/2

        if won+lost > 0:
            gc.set_rgb_fg_color(colormap.alloc_color('#007f00'))
            win.draw_arc(gc, True, x, y+dy, w, h, s*64, ewon*64)
            gc.set_rgb_fg_color(colormap.alloc_color('#7f0000'))
            win.draw_arc(gc, True, x, y+dy, w, h, (s+ewon)*64, elost*64)
            gc.set_rgb_fg_color(colormap.alloc_color('#00ff00'))
            win.draw_arc(gc, True, x, y, w, h, s*64, ewon*64)
            gc.set_rgb_fg_color(colormap.alloc_color('#ff0000'))
            win.draw_arc(gc, True, x, y, w, h, (s+ewon)*64, elost*64)
        else:
            gc.set_rgb_fg_color(colormap.alloc_color('#7f7f7f'))
            win.draw_arc(gc, True, x, y+dy, w, h, 0, 360*64)
            gc.set_rgb_fg_color(colormap.alloc_color('#f0f0f0'))
            win.draw_arc(gc, True, x, y, w, h, 0, 360*64)
            gc.set_rgb_fg_color(colormap.alloc_color('#bfbfbf'))
            pangolayout = drawing.create_pango_layout('No games')
            ext = pangolayout.get_extents()
            tw, th = ext[1][2]/pango.SCALE, ext[1][3]/pango.SCALE
            win.draw_layout(
                gc,
                x+w/2-tw/2, y+h/2-th/2,
                pangolayout)


    def _createStatsList(self):
        treeview = self.widgets_tree.get_widget('all_games_treeview')
        n = 0
        for label in (
            '',
            _('Played'),
            _('Won'),
            _('Lost'),
            _('Playing time'),
            _('Moves'),
            _('% won'),
            ):
            column = gtk.TreeViewColumn(label, gtk.CellRendererText(),
                                        text=n)
            column.set_resizable(True)
            column.set_sort_column_id(n)
            treeview.append_column(column)
            n += 1
        #
        store = gtk.ListStore(gobject.TYPE_STRING, # name
                              gobject.TYPE_INT,    # played
                              gobject.TYPE_INT,    # won
                              gobject.TYPE_INT,    # lost
                              gobject.TYPE_STRING, # playing time
                              gobject.TYPE_STRING, # moves
                              gobject.TYPE_STRING, # % won
                              gobject.TYPE_INT,    # gameid
                              )
        sortable = gtk.TreeModelSort(store)
        treeview.set_model(sortable)
        sortable.set_sort_func(4, self._cmpPlayingTime)
        sortable.set_sort_func(5, self._cmpMoves)
        sortable.set_sort_func(6, self._cmpPercent)
        return store


    def _createLogList(self, name):
        #
        treeview = self.widgets_tree.get_widget(name)
        n = 0
        for label in (
            _('Game'),
            _('Game number'),
            _('Started at'),
            _('Status'),
            ):
            column = gtk.TreeViewColumn(label, gtk.CellRendererText(),
                                        text=n)
            column.set_resizable(True)
            column.set_sort_column_id(n)
            treeview.append_column(column)
            n += 1
        #
        store = gtk.ListStore(gobject.TYPE_STRING, # game name
                              gobject.TYPE_STRING, # game number
                              gobject.TYPE_STRING, # started at
                              gobject.TYPE_STRING, # status
                              gobject.TYPE_INT,    # gameid
                              )
        treeview.set_model(store)
        return store


    def _getPwon(self, won, lost):
        pwon, plost = 0.0, 0.0
        if won + lost > 0:
            pwon = float(won) / (won + lost)
            pwon = min(max(pwon, 0.00001), 0.99999)
            plost = 1.0 - pwon
        return pwon, plost


    def _cmpPlayingTime(self, store, iter1, iter2):
        val1 = store.get_value(iter1, 4)
        val2 = store.get_value(iter2, 4)
        t1 = map(int, val1.split(':'))
        t2 = map(int, val2.split(':'))
        return cmp(len(t1), len(t2)) or cmp(t1, t2)

    def _cmpMoves(self, store, iter1, iter2):
        val1 = store.get_value(iter1, 5)
        val2 = store.get_value(iter2, 5)
        return cmp(float(val1), float(val2))

    def _cmpPercent(self, store, iter1, iter2):
        val1 = store.get_value(iter1, 6)
        val2 = store.get_value(iter2, 6)
        return cmp(float(val1), float(val2))


# /***********************************************************************
# //
# ************************************************************************/

SingleGame_StatsDialog = Game_StatsDialog

class AllGames_StatsDialog(MfxDialog):
    pass

class FullLog_StatsDialog(AllGames_StatsDialog):
    pass

class SessionLog_StatsDialog(FullLog_StatsDialog):
    pass


# /***********************************************************************
# //
# ************************************************************************/

class Status_StatsDialog(MfxMessageDialog): #MfxDialog
    def __init__(self, parent, game):
        stats, gstats = game.stats, game.gstats
        w1 = w2 = ''
        n = 0
        for s in game.s.foundations:
            n = n + len(s.cards)
        w1 = (_('Highlight piles: ') + str(stats.highlight_piles) + '\n' +
              _('Highlight cards: ') + str(stats.highlight_cards) + '\n' +
              _('Highlight same rank: ') + str(stats.highlight_samerank) + '\n')
        if game.s.talon:
            if game.gameinfo.redeals != 0:
                w2 = w2 + _('\nRedeals: ') + str(game.s.talon.round - 1)
            w2 = w2 + _('\nCards in Talon: ') + str(len(game.s.talon.cards))
        if game.s.waste and game.s.waste not in game.s.foundations:
            w2 = w2 + _('\nCards in Waste: ') + str(len(game.s.waste.cards))
        if game.s.foundations:
            w2 = w2 + _('\nCards in Foundations: ') + str(n)
        #
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime(game.gstats.start_time))
        MfxMessageDialog.__init__(self, parent, title=_('Game status'),
                                  text=game.getTitleName() + '\n' +
                                  game.getGameNumber(format=1) + '\n' +
                                  _('Playing time: ') + game.getTime() + '\n' +
                                  _('Started at: ') + date + '\n\n'+
                                  _('Moves: ') + str(game.moves.index) + '\n' +
                                  _('Undo moves: ') + str(stats.undo_moves) + '\n' +
                                  _('Bookmark moves: ') + str(gstats.goto_bookmark_moves) + '\n' +
                                  _('Demo moves: ') + str(stats.demo_moves) + '\n' +
                                  _('Total player moves: ') + str(stats.player_moves) + '\n' +
                                  _('Total moves in this game: ') + str(stats.total_moves) + '\n' +
                                  _('Hints: ') + str(stats.hints) + '\n' +
                                  '\n' +
                                  w1 + w2,
                                  strings=(_('&OK'),
                                           (_('&Statistics...'), 101),
                                           (TOP_TITLE+'...', 105), ),
                                  image=game.app.gimages.logos[3],
                                  image_side='left', image_padx=20,
                                  padx=20,
                                  )



class Top_StatsDialog(MfxDialog):
    pass


