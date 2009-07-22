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

# imports

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# ************************************************************************
# *
# ************************************************************************

class LarasGame_Hint(CautiousDefaultHint):
    pass


# ************************************************************************
# *
# ************************************************************************

class LarasGame_Talon(WasteTalonStack):
    # Deal a card to each of the RowStacks.  Then deal
    # cards to the talon.  Return number of cards dealt.
    def dealRow(self, rows=None, flip=1, reverse=0, frames=-1, sound=False):
        game = self.game
        if rows is None:
            rows = game.s.rows
        old_state = game.enterState(game.S_DEAL)
        cards = self.dealToStacks(rows[:game.MAX_ROW], flip, reverse, frames)
        if sound and frames and self.game.app.opt.animations:
            self.game.startDealSample()
        for i in range(game.DEAL_TO_TALON):
            if self.cards:
                game.moveMove(1, self, game.s.rows[-1], frames=frames)
                cards = cards + 1
        game.leaveState(old_state)
        if sound:
            self.game.stopSamples()
        return cards

    def dealToStacks(self, stacks, flip=1, reverse=0, frames=-1):
        game = self.game
        i, move = 0, game.moveMove
        for r in stacks:
            if not self.cards:
                return 0
            assert not self.getCard().face_up
            assert r is not self
            if flip:
                game.flipMove(self)
            move(1, self, r, frames=frames)
            # Dealing has extra rules in this game type:
            # If card rank == card location then add one card to talon
            # If card rank == ACE then add two cards to talon
            # If card rank == JACK, or higher then add one card to talon
            # After all the rows have been dealt, deal cards to talon in self.dealRow
            rank = r.getCard().rank
            if rank == i:       # Is the rank == position?
                if not self.cards:
                    return 0
                move(1, self, game.s.rows[-1], frames=frames)
            i = i + 1
            if rank == 0:       # Is this an Ace?
                for j in range(2):
                    if not self.cards:
                        return 0
                    move(1, self, game.s.rows[-1], frames=frames)
            if rank >= 10:      # Is it a Jack or better?
                if not self.cards:
                    return 0
                move(1, self, game.s.rows[-1], frames=frames)
        return len(stacks)

    def dealCards(self, sound=False):
        game = self.game
        if sound and self.game.app.opt.animations:
            self.game.startDealSample()
        for r in game.s.reserves[:20]:
            while r.cards:
                game.moveMove(1, r, game.s.rows[game.active_row], frames=3, shadow=0)
        if self.cards:
            game.active_row = self.getActiveRow()
            game.flipMove(self)
            game.moveMove(1, self, game.s.reserves[0], frames=4, shadow=0)
            ncards = len(game.s.rows[game.active_row].cards)
            if ncards >= 20:
                # We have encountered an extreme situation.
                # In some game type variations it's possible
                # to have up to 28 cards on a row stack.
                # We'll have to double up on some of the reserves.
                for i in range(ncards - 19):
                    game.moveMove(1, game.s.rows[game.active_row],
                                        game.s.reserves[19 - i], frames=4, shadow=0)
                    ncards = len(game.s.rows[game.active_row].cards)
                assert ncards <= 19
            for i in range(ncards):
                game.moveMove(1, game.s.rows[game.active_row],
                                game.s.reserves[ncards - i], frames=4, shadow=0)
            num_cards = len(self.cards) or self.canDealCards()
        else: # not self.cards
            if self.round < self.max_rounds:
                ncards = 0
                rows = list(game.s.rows)[:game.MAX_ROW]
                rows.reverse()
                for r in rows:
                    while r.cards:
                        ncards += 1
                        if r.cards[-1].face_up:
                            game.flipMove(r)
                        game.moveMove(1, r, self, frames=0)
                assert len(self.cards) == ncards
                if ncards != 0:
                    game.nextRoundMove(self)
                    game.dealToRows()
            num_cards = len(self.cards)
        if sound:
            game.stopSamples()
        return num_cards

    def canDealCards(self):
        if self.game.demo and self.game.moves.index >= 400:
            return False
        return (self.cards or (self.round < self.max_rounds and not self.game.isGameWon()))

    def updateText(self):
        if self.game.preview > 1:
            return
        WasteTalonStack.updateText(self, update_rounds=0)
        if not self.max_rounds - 1:
            return
        t = _("Round %d") % self.round
        self.texts.rounds.config(text=t)

    def getActiveRow(self):
        return self.getCard().rank


class LarasGame_RowStack(OpenStack):
    def __init__(self, x, y, game, yoffset = 1, **cap):
        OpenStack.__init__(self, x, y, game, **cap)
        self.CARD_YOFFSET = yoffset


class LarasGame_ReserveStack(OpenStack):
    pass


class LarasGame_Reserve(OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return False
        return from_stack in self.game.s.rows

    getBottomImage = Stack._getReserveBottomImage


# ************************************************************************
# * Lara's Game
# ************************************************************************

class LarasGame(Game):
    Hint_Class = LarasGame_Hint
    Talon_Class = LarasGame_Talon
    Reserve_Class = None
    DEAL_TO_TALON = 2
    MAX_ROUNDS = 1
    ROW_LENGTH = 4
    MAX_ROW = 13
    DIR = (-1, 1)

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s
        ROW_LENGTH = self.ROW_LENGTH

        # set window
        w, h = l.XM + l.XS * (ROW_LENGTH + 5), l.YM + l.YS * (ROW_LENGTH + (ROW_LENGTH != 6))
        self.setSize(w, h)

        # extra settings
        self.active_row = None

        # Create foundations
        x, y = l.XM, l.YM
        for j in range(2):
            for i in range(ROW_LENGTH):
                s.foundations.append(SS_FoundationStack(x, y, self, self.Base_Suit(i, j),
                                    max_cards = self.Max_Cards(i), mod = self.Mod(i),
                                    dir = self.DIR[j], base_rank = self.Base_Rank(i, j)))
                y = y + l.YS * (not j)
                x = x + l.XS * j
            x, y = x + l.XS * 2, l.YM

        # Create rows
        x, y = l.XM + l.XS, y + l.YS
        for i in range(self.MAX_ROW):
            s.rows.append(LarasGame_RowStack(x, y, self))
            x = x + l.XS
            if i == ROW_LENGTH or i == ROW_LENGTH * 2 + 1 or i == ROW_LENGTH * 3 + 2:
                x, y = l.XM + l.XS, y + l.YS

        # Create reserves
        x, y = l.XM + l.XS * (ROW_LENGTH == 6), l.YM + l.YS * (ROW_LENGTH - (ROW_LENGTH == 6))
        for i in range(20):
            s.reserves.append(LarasGame_ReserveStack(x, y, self, max_cards=2))
            x = x + l.XS * (i < (ROW_LENGTH + 4)) - l.XS * (i == (ROW_LENGTH + 9))
            y = y - l.YS * (i > (ROW_LENGTH + 3) and i < (ROW_LENGTH + 9)) + l.YS * (i > (ROW_LENGTH + 9))

        # Create talon
        x, y = l.XM + l.XS * (ROW_LENGTH + 2), h - l.YM - l.YS * 3
        s.talon = self.Talon_Class(x, y, self, max_rounds=self.MAX_ROUNDS)
        l.createText(s.talon, "s")
        if self.MAX_ROUNDS > 1:
            l.createRoundText(s.talon, 'nn')
        y = h - l.YS * 2
        s.rows.append(LarasGame_RowStack(x, y, self, yoffset=0))

        # Define stack-groups (not default)
        self.sg.openstacks = s.foundations + s.rows[:self.MAX_ROW]
        self.sg.talonstacks = [s.talon] + s.rows[-1:]
        self.sg.dropstacks = s.rows[:self.MAX_ROW] + s.reserves

        # Create relaxed reserve
        if self.Reserve_Class != None:
            x, y = l.XM + l.XS * (ROW_LENGTH + 2), l.YM + l.YS * .5
            s.reserves.append(self.Reserve_Class(x, y, self,
                            max_accept=1, max_cards=self.Reserve_Cards))
        self.sg.openstacks = self.sg.openstacks + s.reserves[19:]
        self.sg.dropstacks = self.sg.dropstacks + s.reserves[19:]
        self.setRegion(s.reserves[19:], (x - l.XM / 2, 0, 99999, 99999))

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 13

    def Mod(self, i):
        return 13

    def Base_Rank(self, i, j):
        return 12 * (not j)

    def Deal_Rows(self, i):
        return 13

    def Base_Suit(self, i, j):
        return i

    #
    # game overrides
    #

    def startGame(self):
        assert len(self.s.talon.cards) == self.gameinfo.ncards
        self.dealToRows()

    def dealToRows(self):
        frames, ncards = 0, len(self.s.talon.cards)
        for i in range(8):
            if not self.s.talon.cards:
                break
            if i == 4 or len(self.s.talon.cards) <= ncards / 2:
                self.startDealSample()
                frames = 4
            self.s.talon.dealRow(rows=self.s.rows[:self.Deal_Rows(i)], frames=frames)
        self.moveMove(len(self.s.rows[-1].cards), self.s.rows[-1], self.s.talon, frames=0)
        self.active_row = None

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        i, j = (stack1 in self.s.foundations), (stack2 in self.s.foundations)
        if not (i or j): return 0
        if i: stack = stack1
        else: stack = stack2
        i = 0
        for f in self.s.foundations:
            if f == stack: break
            i = i + 1 % self.ROW_LENGTH
        return (card1.suit == card2.suit and
                ((card1.rank + 1) % self.Mod(i) == card2.rank
                or (card1.rank - 1) % self.Mod(i) == card2.rank))

    def getHighlightPilesStacks(self):
        return ()

    # Finish the current move.
    # Append current active_row to moves.current.
    # Append moves.current to moves.history.
    def finishMove(self):
        moves, stats = self.moves, self.stats
        if not moves.current:
            return 0
        # invalidate hints
        self.hints.list = None
        # resize (i.e. possibly shorten list from previous undos)
        if not moves.index == 0:
            m = moves.history[len(moves.history) - 1]
        del moves.history[moves.index : ]
        # update stats
        if self.demo:
            stats.demo_moves = stats.demo_moves + 1
            if moves.index == 0:
                stats.player_moves = 0  # clear all player moves
        else:
            stats.player_moves = stats.player_moves + 1
            if moves.index == 0:
                stats.demo_moves = 0    # clear all demo moves
        stats.total_moves = stats.total_moves + 1
        # add current move to history (which is a list of lists)
        moves.current.append(self.active_row)
        moves.history.append(moves.current)
        moves.index = moves.index + 1
        assert moves.index == len(moves.history)
        moves.current = []
        self.updateText()
        self.updateStatus(moves=(moves.index, self.stats.total_moves))
        self.updateMenus()
        return 1

    def undo(self):
        assert self.canUndo()
        assert self.moves.state == self.S_PLAY and self.moves.current == []
        assert 0 <= self.moves.index <= len(self.moves.history)
        if self.moves.index == 0:
            return
        self.moves.index = self.moves.index - 1
        m = self.moves.history[self.moves.index]
        m = m[:len(m) - 1]
        m.reverse()
        self.moves.state = self.S_UNDO
        for atomic_move in m:
            atomic_move.undo(self)
        self.moves.state = self.S_PLAY
        m = self.moves.history[max(0, self.moves.index - 1)]
        self.active_row = m[len(m) - 1]
        self.stats.undo_moves = self.stats.undo_moves + 1
        self.stats.total_moves = self.stats.total_moves + 1
        self.hints.list = None
        self.updateText()
        self.updateStatus(moves=(self.moves.index, self.stats.total_moves))
        self.updateMenus()

    def redo(self):
        assert self.canRedo()
        assert self.moves.state == self.S_PLAY and self.moves.current == []
        assert 0 <= self.moves.index <= len(self.moves.history)
        if self.moves.index == len(self.moves.history):
            return
        m = self.moves.history[self.moves.index]
        self.moves.index = self.moves.index + 1
        self.active_row = m[len(m) - 1]
        m = m[:len(m) - 1]
        self.moves.state = self.S_REDO
        for atomic_move in m:
            atomic_move.redo(self)
        self.moves.state = self.S_PLAY
        self.stats.redo_moves = self.stats.redo_moves + 1
        self.stats.total_moves = self.stats.total_moves + 1
        self.hints.list = None
        self.updateText()
        self.updateStatus(moves=(self.moves.index, self.stats.total_moves))
        self.updateMenus()

    def _restoreGameHook(self, game):
        self.active_row = game.loadinfo.active_row

    def _loadGameHook(self, p):
        self.loadinfo.addattr(active_row=0)    # register extra load var.
        self.loadinfo.active_row = p.load()

    def _saveGameHook(self, p):
        p.dump(self.active_row)



# ************************************************************************
# * Relaxed Lara's Game
# ************************************************************************

class RelaxedLarasGame(LarasGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 1
    DEAL_TO_TALON = 3
    MAX_ROUNDS = 2


# ************************************************************************
# * Double Lara's Game
# ************************************************************************

class DoubleLarasGame(RelaxedLarasGame):
    Reserve_Cards = 2
    MAX_ROUNDS = 3
    def Max_Cards(self, i):
        return 26


# register the game

registerGame(GameInfo(37, LarasGame, "Lara's Game",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED,
                      altnames=("Thirteen Packs",) ))
registerGame(GameInfo(13006, RelaxedLarasGame, "Lara's Game Relaxed",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_BALANCED))
registerGame(GameInfo(13007, DoubleLarasGame, "Lara's Game Doubled",
                      GI.GT_2DECK_TYPE, 4, 2, GI.SL_BALANCED))


