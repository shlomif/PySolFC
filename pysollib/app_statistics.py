#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
#  Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
#  Copyright (C) 2003 Mt. Hood Playing Card Co.
#  Copyright (C) 2005-2009 Skomoroh
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

from pysollib.app_stat import GameStat
from pysollib.settings import VERSION_TUPLE


class Statistics:
    def __init__(self):
        self.version_tuple = VERSION_TUPLE
        self.saved = 0
        # a dictionary of dictionaries of GameStat (keys: player and gameid)
        self.games_stats = {}
        # a dictionary of lists of tuples (key: player)
        self.prev_games = {}
        self.all_prev_games = {}
        self.session_games = {}
        # some simple balance scores (key: gameid)
        self.total_balance = {}     # a dictionary of integers
        self.session_balance = {}   # reset per session
        self.gameid_balance = 0     # reset when changing the gameid

    def new(self):
        return Statistics()

    #
    # player & demo statistics
    #

    def resetStats(self, player, gameid):
        self.__resetPrevGames(player, self.prev_games, gameid)
        self.__resetPrevGames(player, self.session_games, gameid)
        if player not in self.games_stats:
            return
        if gameid == 0:
            # remove all games
            try:
                del self.games_stats[player]
            except KeyError:
                pass
        else:
            try:
                del self.games_stats[player][gameid]
            except KeyError:
                pass

    def __resetPrevGames(self, player, games, gameid):
        if player not in games:
            return
        if gameid == 0:
            del games[player]
        else:
            games[player] = [g for g in games[player] if g[0] != gameid]

    def deleteGameStats(self, gameid):
        for player in self.games_stats:
            try:
                del self.games_stats[player][gameid]
            except KeyError:
                pass
        for player in self.prev_games:
            self.prev_games[player] = \
                [g for g in self.prev_games[player] if g[0] != gameid]
        for player in self.session_games:
            self.session_games[player] = \
                [g for g in self.session_games[player] if g[0] != gameid]

    def getStats(self, player, gameid):
        # returned (won, lost)
        return self.getFullStats(player, gameid)[:2]

    def getFullStats(self, player, gameid):
        # returned (won, lost, playing time, moves)
        stats = self.games_stats
        if player in stats and gameid in stats[player]:
            s = self.games_stats[player][gameid]
            return (s.num_won+s.num_perfect,
                    s.num_lost,
                    s.time_result.average,
                    s.moves_result.average,)
        return (0, 0, 0, 0)

    def getSessionStats(self, player, gameid):
        games = self.session_games.get(player, [])
        games = [g for g in games if g[0] == gameid]
        won = len([g for g in games if g[2] > 0])
        lost = len([g for g in games if g[2] == 0])
        return won, lost

    def updateStats(self, player, game, status):
        ret = None
        log = (game.id, game.getGameNumber(format=0), status,
               game.gstats.start_time, game.gstats.total_elapsed_time,
               VERSION_TUPLE, game.getGameScore(), game.getGameScoreCasino(),
               game.GAME_VERSION)
        # full log
        if status >= 0:
            if player not in self.prev_games:
                self.prev_games[player] = []
            self.prev_games[player].append(log)
            if player not in self.all_prev_games:
                self.all_prev_games[player] = []
            self.all_prev_games[player].append(log)
            ret = self.updateGameStat(player, game, status)
        # session log
        if player not in self.session_games:
            self.session_games[player] = []
        self.session_games[player].append(log)
        return ret

    def updateGameStat(self, player, game, status):
        #
        if player not in self.games_stats:
            self.games_stats[player] = {}
        if game.id not in self.games_stats[player]:
            game_stat = GameStat(game.id)
            self.games_stats[player][game.id] = game_stat
        else:
            game_stat = self.games_stats[player][game.id]
        if 'all' not in self.games_stats[player]:
            all_games_stat = GameStat('all')
            self.games_stats[player]['all'] = all_games_stat
        else:
            all_games_stat = self.games_stats[player]['all']
        all_games_stat.update(game, status)
        return game_stat.update(game, status)

#      def __setstate__(self, state):      # for backward compatible
#          if 'gameid' not in state:
#              self.gameid = None
#          self.__dict__.update(state)
