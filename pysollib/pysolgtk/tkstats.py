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


# imports
import os, sys, time
import gtk, gobject, pango
import gtk.glade

# PySol imports
from pysollib.mfxutil import format_time
from pysollib.settings import TOP_TITLE, PACKAGE
from pysollib.stats import PysolStatsFormatter

# Toolkit imports
from tkwidget import MfxDialog, MfxMessageDialog

gettext = _


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
                       0, gettext(args[0]),
                       1, args[1],
                       2, args[2],
                       3, args[3],
                       4, args[4],
                       5, args[5],
                       6, args[6],
                       7, gameid)


class LogWriter(PysolStatsFormatter.StringWriter):
    MAX_ROWS = 10000

    def __init__(self, store):
        self.store = store
        self._num_rows = 0

    def p(self, s):
        pass

    def pheader(self, s):
        pass

    def plog(self, gamename, gamenumber, date, status, gameid=-1, won=-1):
        if gameid < 0:
            # header
            return
        if self._num_rows > self.MAX_ROWS:
            return
        iter = self.store.append(None)
        self.store.set(iter,
                       0, gettext(gamename),
                       1, gamenumber,
                       2, date,
                       3, status,
                       4, gameid)
        self._num_rows += 1


class Game_StatsDialog:

    def __init__(self, parent, header, app, player, gameid):
        #
        self.app = app
        self.player = player
        self.gameid = gameid
        self.games = {}
        self.games_id = [] # sorted by name
        #
        formatter = PysolStatsFormatter(self.app)
        glade_file = app.dataloader.findFile('pysolfc.glade')
        #
        games = app.gdb.getGamesIdSortedByName()
        n = 0
        current = 0
        for id in games:
            won, lost = self.app.stats.getStats(self.player, id)
            if won+lost > 0 or id == gameid:
                gi = app.gdb.get(id)
                if id == gameid:
                    current = n
                self.games[n] = gi
                self.games_id.append(id)
                n += 1
        #
        self.widgets_tree = gtk.glade.XML(glade_file)
        #
        table = self.widgets_tree.get_widget('current_game_table')
        combo = self._createGameCombo(table, 1, 0, self._currentComboChanged)
        # total
        self._createText('total')
        drawing = self.widgets_tree.get_widget('total_drawingarea')
        drawing.connect('expose_event', self._drawingExposeEvent, 'total')
        # current session
        self._createText('session')
        drawing = self.widgets_tree.get_widget('session_drawingarea')
        drawing.connect('expose_event', self._drawingExposeEvent, 'session')
        # top 10
        table = self.widgets_tree.get_widget('top_10_table')
        combo = self._createGameCombo(table, 1, 0, self._top10ComboChanged)
        self._createTop()
        self._updateTop(gameid)
        # all games stat
        store = self._createStatsList()
        writer = StatsWriter(store)
        formatter.writeStats(writer, player, header, sort_by='name')
        # full log
        store = self._createLogList('full_log_treeview')
        writer = LogWriter(store)
        formatter.writeFullLog(writer, player, header)
        # session log
        store = self._createLogList('session_log_treeview')
        writer = LogWriter(store)
        formatter.writeSessionLog(writer, player, header)
        #
        self._translateLabels()
        dialog = self.widgets_tree.get_widget('stats_dialog')
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.set_transient_for(parent)
        dialog.resize(500, 340)
        dialog.set_title(PACKAGE+' - '+_("Statistics"))
        #
        dialog.run()
        self.status = -1
        dialog.destroy()


    def _translateLabels(self):
        # mnemonic
        for n in (
            'label0',
            'label1',
            'label2',
            'label3',
            'label4',
            'label15',
            'label16',
            'label17',
            'label18',
            ):
            w = self.widgets_tree.get_widget(n)
            w.set_text_with_mnemonic(gettext(w.get_label()))
        # simple
        for n in (
            'label5',
            'label6',
            'label7',
            'label14'
            ):
            w = self.widgets_tree.get_widget(n)
            w.set_text(gettext(w.get_text()))
        # markup
        for n in (
            'label8',
            'label9',
            'label10',
            'label11',
            'label12',
            'label13',
            'label19',
            'label20',
            'label21',
            'label22',
            'label23',
            'label24',
            ):
            w = self.widgets_tree.get_widget(n)
            s = gettext(w.get_label())
            w.set_markup('<b>%s</b>' % s)


    def _createGameCombo(self, table, x, y, callback):
        combo = gtk.combo_box_new_text()
        combo.show()
        table.attach(combo,
                     x, x+1,                y, y+1,
                     gtk.FILL|gtk.EXPAND,   0,
                     4,                     4)
        #
        n = 0
        current = 0
        for id in self.games_id:
            gi = self.app.gdb.get(id)
            combo.append_text(gettext(gi.name))
            if id == self.gameid:
                current = n
            n += 1
        combo.set_active(current)
        combo.connect('changed', callback) #self._comboChanged)


    def _currentComboChanged(self, w):
        gi = self.games[w.get_active()]
        self.gameid = gi.id
        self._createText('total')
        drawing = self.widgets_tree.get_widget('total_drawingarea')
        self._createChart(drawing, 'total')
        self._createText('session')
        drawing = self.widgets_tree.get_widget('session_drawingarea')
        self._createChart(drawing, 'session')


    def _top10ComboChanged(self, w):
        gi = self.games[w.get_active()]
        self._updateTop(gi.id)


    def _createText(self, name):
        if name == 'total':
            won, lost = self.app.stats.getStats(self.player, self.gameid)
        else:
            won, lost = self.app.stats.getSessionStats(self.player, self.gameid)
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


    def _drawingExposeEvent(self, drawing, e, frame):
        self._createChart(drawing, frame)


    def _createChart(self, drawing, frame):
        if frame == 'total':
            won, lost = self.app.stats.getStats(self.player, self.gameid)
        else:
            won, lost = self.app.stats.getSessionStats(self.player, self.gameid)
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
            gc.set_foreground(colormap.alloc_color('#008000'))
            win.draw_arc(gc, True, x, y+dy, w, h, s*64, ewon*64)
            gc.set_foreground(colormap.alloc_color('black'))
            win.draw_arc(gc, False, x, y+dy, w, h, s*64, ewon*64)
            gc.set_foreground(colormap.alloc_color('#800000'))
            win.draw_arc(gc, True, x, y+dy, w, h, (s+ewon)*64, elost*64)
            gc.set_foreground(colormap.alloc_color('black'))
            win.draw_arc(gc, False, x, y+dy, w, h, (s+ewon)*64, elost*64)
            gc.set_foreground(colormap.alloc_color('#00ff00'))
            win.draw_arc(gc, True, x, y, w, h, s*64, ewon*64)
            gc.set_foreground(colormap.alloc_color('black'))
            win.draw_arc(gc, False, x, y, w, h, s*64, ewon*64)
            gc.set_foreground(colormap.alloc_color('#ff0000'))
            win.draw_arc(gc, True, x, y, w, h, (s+ewon)*64, elost*64)
            gc.set_foreground(colormap.alloc_color('black'))
            win.draw_arc(gc, False, x, y, w, h, (s+ewon)*64, elost*64)
        else:
            gc.set_foreground(colormap.alloc_color('#808080'))
            win.draw_arc(gc, True, x, y+dy, w, h, 0, 360*64)
            gc.set_foreground(colormap.alloc_color('black'))
            win.draw_arc(gc, False, x, y+dy, w, h, 0, 360*64)
            gc.set_foreground(colormap.alloc_color('#f0f0f0'))
            win.draw_arc(gc, True, x, y, w, h, 0, 360*64)
            gc.set_foreground(colormap.alloc_color('black'))
            win.draw_arc(gc, False, x, y, w, h, 0, 360*64)
            gc.set_foreground(colormap.alloc_color('#a0a0a0'))
            pangolayout = drawing.create_pango_layout(_('No games'))
            ext = pangolayout.get_extents()
            tw, th = ext[1][2]/pango.SCALE, ext[1][3]/pango.SCALE
            win.draw_layout(gc, x+w/2-tw/2, y+h/2-th/2, pangolayout)


    def _createTop(self):
        for n in ('top_10_time_treeview',
                  'top_10_moves_treeview',
                  'top_10_total_moves_treeview'):
            self._createTopList(n)


    def _updateTop(self, gameid):
        if (not self.app.stats.games_stats.has_key(self.player) or
            not self.app.stats.games_stats[self.player].has_key(gameid) or
            not self.app.stats.games_stats[self.player][gameid].time_result.top):
            return

        s = self.app.stats.games_stats[self.player][gameid]

        label = self.widgets_tree.get_widget('playing_time_minimum_label')
        label.set_text(format_time(s.time_result.min))
        label = self.widgets_tree.get_widget('playing_time_maximum_label')
        label.set_text(format_time(s.time_result.max))
        label = self.widgets_tree.get_widget('playing_time_average_label')
        label.set_text(format_time(s.time_result.average))

        label = self.widgets_tree.get_widget('moves_minimum_label')
        label.set_text(str(s.moves_result.min))
        label = self.widgets_tree.get_widget('moves_maximum_label')
        label.set_text(str(s.moves_result.max))
        label = self.widgets_tree.get_widget('moves_average_label')
        label.set_text(str(round(s.moves_result.average, 2)))

        label = self.widgets_tree.get_widget('total_moves_minimum_label')
        label.set_text(str(s.total_moves_result.min))
        label = self.widgets_tree.get_widget('total_moves_maximum_label')
        label.set_text(str(s.total_moves_result.max))
        label = self.widgets_tree.get_widget('total_moves_average_label')
        label.set_text(str(round(s.total_moves_result.average, 2)))

        for n, ss in (
            ('top_10_time_treeview',        s.time_result.top),
            ('top_10_moves_treeview',       s.moves_result.top),
            ('top_10_total_moves_treeview', s.total_moves_result.top)):
            self._updateTopList(n, ss)


    def _createTopList(self, tv_name):
        treeview = self.widgets_tree.get_widget(tv_name)
        store = gtk.ListStore(gobject.TYPE_INT,    # N
                              gobject.TYPE_STRING, # number
                              gobject.TYPE_STRING, # started at
                              gobject.TYPE_STRING, # result
                              gobject.TYPE_STRING, # result
                              )
        treeview.set_model(store)
        n = 0
        for label in (
            _('N'),
            _('Game number'),
            _('Started at'),
            _('Result'),
            ):
            column = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=n)
            column.set_resizable(True)
            ##column.set_sort_column_id(n)
            treeview.append_column(column)
            n += 1


    def _updateTopList(self, tv_name, top):
        treeview = self.widgets_tree.get_widget(tv_name)
        store = treeview.get_model()
        store.clear()
        row = 1
        for i in top:
            t = time.strftime('%Y-%m-%d %H:%M',
                              time.localtime(i.game_start_time))
            if isinstance(i.value, float):
                # time
                r = format_time(i.value)
            else:
                # moves
                r = str(i.value)
            iter = store.append(None)
            store.set(iter, 0, row, 1, i.game_number, 2, t, 3, r)
            row += 1


    def _createStatsList(self):
        treeview = self.widgets_tree.get_widget('all_games_treeview')
        n = 0
        for label in (
            _('Game'),
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
        sortable.set_sort_func(4, self._cmpPlayingTime)
        sortable.set_sort_func(5, self._cmpMoves)
        sortable.set_sort_func(6, self._cmpPercent)
        treeview.set_model(sortable)
        treeview.set_rules_hint(True)
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
        treeview.set_rules_hint(True)
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
AllGames_StatsDialog = Game_StatsDialog
FullLog_StatsDialog = Game_StatsDialog
SessionLog_StatsDialog = Game_StatsDialog
Top_StatsDialog = Game_StatsDialog


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
        date = time.strftime('%Y-%m-%d %H:%M',
                             time.localtime(game.gstats.start_time))
        MfxMessageDialog.__init__(
            self, parent, title=_('Game status'),
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
                     (_('&Statistics...'), 101), ),
            image=game.app.gimages.logos[3],
            image_side='left', image_padx=20,
            padx=20,
            )






