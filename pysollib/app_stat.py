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


from pysollib.app_stat_result import GameStatResult


class GameStat:
    def __init__(self, id):
        self.gameid = id
        #
        self.num_total = 0
        # self.num_not_won = 0
        self.num_lost = 0
        self.num_won = 0
        self.num_perfect = 0
        #
        self.time_result = GameStatResult()
        self.moves_result = GameStatResult()
        self.total_moves_result = GameStatResult()
        self.score_result = GameStatResult()
        self.score_casino_result = GameStatResult()

    def update(self, game, status):
        #
        game_number = game.getGameNumber(format=0)
        game_start_time = game.gstats.start_time
        # update number of games
        # status:
        # -1 - NOT WON (not played)
        # 0 - LOST
        # 1 - WON
        # 2 - PERFECT
        self.num_total += 1
        assert status in (0, 1, 2)
        if status == 0:
            self.num_lost += 1
            return
        if status == 1:
            self.num_won += 1
        else:  # status == 2
            self.num_perfect += 1

        score = game.getGameScore()
        # print 'GameScore:', score
        score_p = None
        if score is not None:
            score_p = self.score_result.update(
                game.id, score, game_number, game_start_time)
        score = game.getGameScoreCasino()
        # print 'GameScoreCasino:', score
        score_casino_p = None
        if score is not None:
            score_casino_p = self.score_casino_result.update(
                game.id, score, game_number, game_start_time)

        if status == 0:
            return

        game.updateTime()
        time_p = self.time_result.update(
            game.id, game.stats.elapsed_time, game_number, game_start_time)
        moves_p = self.moves_result.update(
            game.id, game.moves.index, game_number, game_start_time)
        total_moves_p = self.total_moves_result.update(
            game.id, game.stats.total_moves, game_number, game_start_time)

        return time_p, moves_p, total_moves_p, score_p, score_casino_p
