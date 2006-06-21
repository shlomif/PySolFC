##---------------------------------------------------------------------------##
##
## Ultrasol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Matthew Hohlfeld <hohlfeld@cs.ucsd.edu>
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

__all__ = []

# imports
import sys, types

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText


# /***********************************************************************
# //
# ************************************************************************/

class LarasGame_Hint(CautiousDefaultHint):
    pass


# /***********************************************************************
# //
# ************************************************************************/

class LarasGame_Talon(WasteTalonStack):
    # Deal a card to each of the RowStacks.  Then deal
    # cards to the talon.  Return number of cards dealt.
    def dealRow(self, rows=None, flip=1, reverse=0, frames=-1):
        game = self.game
        if rows is None:
            rows = game.s.rows
        old_state = game.enterState(game.S_DEAL)
        cards = self.dealToStacks(rows[:game.MAX_ROW], flip, reverse, frames)
        for i in range(game.DEAL_TO_TALON):
            if self.cards:
                game.moveMove(1, self, game.s.rows[-1], frames=frames)
                cards = cards + 1
        game.leaveState(old_state)
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

    def dealCards(self, sound=0):
        game = self.game
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
            return len(self.cards) or self.canDealCards()
        if self.round < self.max_rounds:
            num_cards = 0
            rows = list(game.s.rows)[:game.MAX_ROW]
            rows.reverse()
            for r in rows:
                while r.cards:
                    num_cards = num_cards + 1
                    if r.cards[-1].face_up:
                        game.flipMove(r)
                    game.moveMove(1, r, self, frames=0)
            assert len(self.cards) == num_cards
            if num_cards == 0:
                return 0
            game.nextRoundMove(self)
            game.dealToRows()
        if sound:
            game.stopSamples()
        return len(self.cards)

    def canDealCards(self):
        if self.game.demo and self.game.moves.index >= 400:
            return 0
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



class DojoujisGame_Talon(LarasGame_Talon):

    def getActiveRow(self):
        card = self.getCard()
        return card.rank + card.deck * 4



class DoubleKalisGame_Talon(LarasGame_Talon):

    def getActiveRow(self):
        card = self.getCard()
        return card.rank + card.deck * 12



class LarasGame_RowStack(OpenStack):
    def __init__(self, x, y, game, yoffset = 1, **cap):
        apply(OpenStack.__init__, (self, x, y, game), cap)
        self.CARD_YOFFSET = yoffset



class LarasGame_ReserveStack(OpenStack):
    pass



class BridgetsGame_Reserve(OpenStack):

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return from_stack in self.game.s.foundations and cards[0].suit == 4
        return from_stack in self.game.s.rows

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()



class LarasGame_Reserve(BridgetsGame_Reserve):

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return 0
        return from_stack in self.game.s.rows



# /***********************************************************************
# // Lara's Game
# ************************************************************************/

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
        if self.MAX_ROUNDS - 1:
            s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                                 x + l.XS / 2, y - l.YM,
                                                 anchor="center",
                                                 font=self.app.getFont("canvas_default"))
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
        self.updateStatus(moves=moves.index)
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
        self.updateStatus(moves = self.moves.index)
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
        self.updateStatus(moves = self.moves.index)
        self.updateMenus()

    def _restoreGameHook(self, game):
        self.active_row = game.loadinfo.active_row

    def _loadGameHook(self, p):
        self.loadinfo.addattr(active_row=0)    # register extra load var.
        self.loadinfo.active_row = p.load()

    def _saveGameHook(self, p):
        p.dump(self.active_row)



# /***********************************************************************
# // Relaxed Lara's Game
# ************************************************************************/

class RelaxedLarasGame(LarasGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 1
    DEAL_TO_TALON = 3
    MAX_ROUNDS = 2


# /***********************************************************************
# // Double Lara's Game
# ************************************************************************/

class DoubleLarasGame(RelaxedLarasGame):
    Reserve_Cards = 2
    MAX_ROUNDS = 3

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 26


# /***********************************************************************
# // Katrina's Game
# ************************************************************************/

class KatrinasGame(LarasGame):
    DEAL_TO_TALON = 3
    MAX_ROUNDS = 2
    ROW_LENGTH = 5
    MAX_ROW = 22

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 14 + 8 * (i == 4)

    def Mod(self, i):
        return 14 + 8 * (i == 4)

    def Base_Rank(self, i, j):
        return (13 + 8 * (i == 4)) * (not j)

    def Deal_Rows(self, i):
        return 14 + 8 * (i % 2)

    def Base_Suit(self, i, j):
        return i

    #
    # Game overrides
    #

    def getCardFaceImage(self, deck, suit, rank):
        return self.app.images.getFace(deck, suit, rank)


# /***********************************************************************
# // Relaxed Katrina's Game
# ************************************************************************/

class RelaxedKatrinasGame(KatrinasGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 2


# /***********************************************************************
# // Double Katrina's Game
# ************************************************************************/

class DoubleKatrinasGame(RelaxedKatrinasGame):
    Reserve_Cards = 3
    MAX_ROUNDS = 3

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 28 + 16 * (i == 4)


# /***********************************************************************
# // Bridget's Game
# // In memory of Bridget Bishop
# // Hanged as a witch on June 10, 1692
# // Salem Massachusetts, U. S. A.
# // and the nineteen other women
# // and men who followed her
# ************************************************************************/

class BridgetsGame(LarasGame):
    Reserve_Class = BridgetsGame_Reserve
    Reserve_Cards = 2
    MAX_ROUNDS = 2
    ROW_LENGTH = 5
    MAX_ROW = 16

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 16 - 12 * (i == 4)

    def Mod(self, i):
        return 16 - 12 * (i == 4)

    def Base_Rank(self, i, j):
        return (15 - 12 * (i == 4)) * (not j)

    def Deal_Rows(self, i):
        return 16

    def Base_Suit(self, i, j):
        return i


# /***********************************************************************
# // Double Bridget's Game
# ************************************************************************/

class DoubleBridgetsGame(BridgetsGame):
    Reserve_Cards = 3
    MAX_ROUNDS = 3

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 32 - 24 * (i == 4)


# /***********************************************************************
# // Fatimeh's Game
# ************************************************************************/

class FatimehsGame(LarasGame):
    DEAL_TO_TALON = 5
    MAX_ROUNDS = 3
    MAX_ROW = 12
    DIR = (1, 1)

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 12

    def Mod(self, i):
        return 12

    def Base_Rank(self, i, j):
        return 0

    def Deal_Rows(self, i):
        return 12

    def Base_Suit(self, i, j):
        return i + j * 4


# /***********************************************************************
# // Relaxed Fatimeh's Game
# ************************************************************************/

class RelaxedFatimehsGame(FatimehsGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 2


# /***********************************************************************
# // Kali's Game
# ************************************************************************/

class KalisGame(FatimehsGame):
    DEAL_TO_TALON = 6
    ROW_LENGTH = 5

    #
    # Game extras
    #

    def Base_Suit(self, i, j):
        return i + j * 5


# /***********************************************************************
# // Relaxed Kali's Game
# ************************************************************************/

class RelaxedKalisGame(KalisGame):
    Reserve_Class = LarasGame_Reserve
    Reserve_Cards = 2


# /***********************************************************************
# // Double Kali's Game
# ************************************************************************/

class DoubleKalisGame(RelaxedKalisGame):
    Talon_Class = DoubleKalisGame_Talon
    Reserve_Cards = 4
    MAX_ROUNDS = 4
    MAX_ROW = 24

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 24

    def Deal_Rows(self, i):
        return 24


# /***********************************************************************
# // Dojouji's Game
# ************************************************************************/

class DojoujisGame(LarasGame):
    Talon_Class = DojoujisGame_Talon
    ROW_LENGTH = 6
    MAX_ROW = 8
    DIR = (-1, -1)

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 8

    def Mod(self, i):
        return 4

    def Base_Rank(self, i, j):
        return 3

    def Deal_Rows(self, i):
        return 8

    def Base_Suit(self, i, j):
        return i + j * 6



# /***********************************************************************
# // Double Dojouji's Game
# ************************************************************************/

class DoubleDojoujisGame(DojoujisGame):
    MAX_ROW = 16

    #
    # Game extras
    #

    def Max_Cards(self, i):
        return 16

    def Deal_Rows(self, i):
        return 16



# register the game
registerGame(GameInfo(37, LarasGame, "Lara's Game",
                      GI.GT_2DECK_TYPE, 2, 0, GI.SL_BALANCED))

registerGame(GameInfo(13001, KatrinasGame, "Katrina's Game",
                      GI.GT_TAROCK, 2, 1, GI.SL_BALANCED,
                      ranks = range(14), trumps = range(22)))

registerGame(GameInfo(13002, BridgetsGame, "Bridget's Game",
                      GI.GT_HEXADECK, 2, 1, GI.SL_BALANCED,
                      ranks = range(16), trumps = range(4)))

registerGame(GameInfo(13003, FatimehsGame, "Fatimeh's Game",
                      GI.GT_MUGHAL_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(8), ranks = range(12)))

registerGame(GameInfo(13004, KalisGame, "Kali's Game",
                      GI.GT_DASHAVATARA_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(10), ranks = range(12)))

registerGame(GameInfo(13005, DojoujisGame, "Dojouji's Game",
                      GI.GT_HANAFUDA, 2, 0, GI.SL_BALANCED,
                      suits = range(12), ranks = range(4)))

registerGame(GameInfo(13006, RelaxedLarasGame, "Lara's Game Relaxed",
                      GI.GT_2DECK_TYPE, 2, 1, GI.SL_BALANCED))

registerGame(GameInfo(13007, DoubleLarasGame, "Lara's Game Doubled",
                      GI.GT_2DECK_TYPE, 4, 2, GI.SL_BALANCED))

registerGame(GameInfo(13008, RelaxedKatrinasGame, "Katrina's Game Relaxed",
                      GI.GT_TAROCK, 2, 1, GI.SL_BALANCED,
                      ranks = range(14), trumps = range(22)))

registerGame(GameInfo(13009, DoubleKatrinasGame, "Katrina's Game Doubled",
                      GI.GT_TAROCK, 4, 2, GI.SL_BALANCED,
                      ranks = range(14), trumps = range(22)))

registerGame(GameInfo(13010, DoubleBridgetsGame, "Bridget's Game Doubled",
                      GI.GT_HEXADECK, 4, 2, GI.SL_BALANCED,
                      ranks = range(16), trumps = range(4)))

registerGame(GameInfo(13011, RelaxedKalisGame, "Kali's Game Relaxed",
                      GI.GT_DASHAVATARA_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(10), ranks = range(12)))

registerGame(GameInfo(13012, DoubleKalisGame, "Kali's Game Doubled",
                      GI.GT_DASHAVATARA_GANJIFA, 2, 3, GI.SL_BALANCED,
                      suits = range(10), ranks = range(12)))

registerGame(GameInfo(13013, RelaxedFatimehsGame, "Fatimeh's Game Relaxed",
                      GI.GT_MUGHAL_GANJIFA, 1, 2, GI.SL_BALANCED,
                      suits = range(8), ranks = range(12)))

registerGame(GameInfo(13014, DoubleDojoujisGame, "Dojouji's Game Doubled",
                      GI.GT_HANAFUDA, 4, 0, GI.SL_BALANCED,
                      suits = range(12), ranks = range(4)))
