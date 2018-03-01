#!/usr/bin/env pytho
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


# imports
import os
import time
import subprocess
import re
import sys
from io import BytesIO

# PySol imports
from pysollib.settings import DEBUG, FCS_COMMAND
from pysollib.mfxutil import destruct
from pysollib.util import KING

if sys.version_info > (3,):
    unicode = str

# ************************************************************************
# * HintInterface is an abstract class that defines the public
# * interface - it only consists of the constructor
# * and the getHints() method.
# *
# * The whole hint system is exclusively used by Game.getHints().
# ************************************************************************


class HintInterface:
    # level == 0: show hint (key `H')
    # level == 1: show hint and display score value (key `Ctrl-H')
    # level == 2: demo
    def __init__(self, game, level):
        pass

    # Compute all hints for the current position.
    # Subclass responsibility.
    #
    # Returns a list of "atomic hints" - an atomic hint is a 7-tuple
    # (score, pos, ncards, from_stack, to_stack, text_color, forced_move).
    #
    #    if ncards == 0: deal cards
    #    elif from_stack == to_stack: flip card
    #    else: move cards from from_stack to to_stack
    #
    #    score, pos and text_color are only for debugging.
    #    A forced_move is the next move that must be taken after this move
    #    in order to avoid endless loops during demo play.
    #
    # Deal and flip may only happen if self.level >= 2 (i.e. demo).
    #
    # See Game.showHint() for more information.
    def getHints(self, taken_hint=None):
        return []


# ************************************************************************
# * AbstractHint provides a useful framework for derived hint classes.
# *
# * Subclasses should override computeHints()
# ************************************************************************

class AbstractHint(HintInterface):
    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.score_flatten_value = 0
        if self.level == 0:
            self.score_flatten_value = 10000
        # temporaries within getHints()
        self.bonus_color = None
        #
        self.__clones = []
        self.reset()

    def __del__(self):
        self.reset()

    def reset(self):
        self.hints = []
        self.max_score = 0
        self.__destructClones()
        self.solver_state = 'not_started'

    #
    # stack cloning
    #

    # Create a shallow copy of a stack.
    class AClonedStack:
        def __init__(self, stack, stackcards):
            # copy class identity
            self.__class__ = stack.__class__
            # copy model data (reference copy)
            stack.copyModel(self)
            # set new cards (shallow copy of the card list)
            self.cards = stackcards[:]

    def ClonedStack(self, stack, stackcards):
        s = self.AClonedStack(stack, stackcards)
        self.__clones.append(s)
        return s

    def __destructClones(self):
        for s in self.__clones:
            s.__class__ = self.AClonedStack     # restore orignal class
            destruct(s)
        self.__clones = []

    # When computing hints for level 0, the scores are flattened
    # (rounded down) to a multiple of score_flatten_value.
    #
    # The idea is that hints will appear equal within a certain score range
    # so that the player will not get confused by the demo-intelligence.
    #
    # Pressing `Ctrl-H' (level 1) will preserve the score.

    def addHint(self, score, ncards, from_stack,
                to_stack, text_color=None, forced_move=None):
        if score < 0:
            return
        self.max_score = max(self.max_score, score)
        # add an atomic hint
        if self.score_flatten_value > 0:
            score = (score // self.score_flatten_value) * \
                    self.score_flatten_value
        if text_color is None:
            text_color = self.BLACK
        assert forced_move is None or len(forced_move) == 7
        # pos is used for preserving the original sort order on equal scores
        pos = -len(self.hints)
        ah = (int(score), pos, ncards, from_stack, to_stack,
              text_color, forced_move)
        self.hints.append(ah)

    # clean up and return hints sorted by score
    def _returnHints(self):
        hints = self.hints
        self.reset()
        hints.sort()
        hints.reverse()
        return hints

    #
    # getHints() default implementation:
    #   - handle forced moves
    #   - try to flip face-down cards
    #   - call computeHints() to do something useful
    #   - try to deal cards
    #   - clean up and return hints sorted by score
    #

    # Default scores for flip and deal moves.
    SCORE_FLIP = 100000         # 0..100000
    SCORE_DEAL = 0              # 0..100000

    def getHints(self, taken_hint=None):
        # 0) setup
        self.reset()
        game = self.game
        # 1) forced moves of the prev. taken hint have absolute priority
        if taken_hint and taken_hint[6]:
            return [taken_hint[6]]
        # 2) try if we can flip a card
        if self.level >= 2:
            for r in game.allstacks:
                if r.canFlipCard():
                    self.addHint(self.SCORE_FLIP, 1, r, r)
                    if self.SCORE_FLIP >= 90000:
                        return self._returnHints()
        # 3) ask subclass to do something useful
        self.computeHints()
        # 4) try if we can deal cards
        if self.level >= 2:
            if game.canDealCards():
                self.addHint(self.SCORE_DEAL, 0, game.s.talon, None)
        return self._returnHints()

    # subclass
    def computeHints(self):
        pass

    #
    # utility shallMovePile()
    #

    # we move the pile if it is accepted by the target stack
    def _defaultShallMovePile(self, from_stack, to_stack, pile, rpile):
        if from_stack is to_stack or not \
                to_stack.acceptsCards(from_stack, pile):
            return 0
        return 1

    # same, but check for loops
    def _cautiousShallMovePile(self, from_stack, to_stack, pile, rpile):
        if from_stack is to_stack or not \
                to_stack.acceptsCards(from_stack, pile):
            return 0
        #
        if len(rpile) == 0:
            return 1
        # now check for loops
        rr = self.ClonedStack(from_stack, stackcards=rpile)
        if rr.acceptsCards(to_stack, pile):
            # the pile we are going to move could be moved back -
            # this is dangerous as we can create endless loops...
            return 0
        return 1

    # same, but only check for loops only when in demo mode
    def _cautiousDemoShallMovePile(self, from_stack, to_stack, pile, rpile):
        if from_stack is to_stack or not \
                to_stack.acceptsCards(from_stack, pile):
            return 0
        if self.level >= 2:
            #
            if len(rpile) == 0:
                return 1
            # now check for loops
            rr = self.ClonedStack(from_stack, stackcards=rpile)
            if rr.acceptsCards(to_stack, pile):
                # the pile we are going to move could be moved back -
                # this is dangerous as we can create endless loops...
                return 0
        return 1

    shallMovePile = _defaultShallMovePile

    #
    # other utility methods
    #

    def _canDropAllCards(self, from_stack, stacks, stackcards):
        assert from_stack not in stacks
        return 0
        # FIXME: this does not account for cards which are dropped herein
        #         cards = pile[:]
        #         cards.reverse()
        #         for card in cards:
        #             for s in stacks:
        #                 if s is not from_stack:
        #                     if s.acceptsCards(from_stack, [card]):
        #                         break
        #             else:
        #                 return 0
        #         return 1

    #
    # misc. constants
    #

    # score value so that the scores look nicer
    K = KING + 1
    # text_color that will display the score (for debug with level 1)
    BLACK = "black"
    RED = "red"
    BLUE = "blue"


# ************************************************************************
# *
# ************************************************************************

class DefaultHint(AbstractHint):

    # The DefaultHint is optimized for Klondike type games
    # and also deals quite ok with other simple variants.
    #
    # But it completely lacks any specific strategy about game
    # types like Forty Thieves, FreeCell, Golf, Spider, ...
    #
    # BTW, we do not cheat !

    #
    # bonus scoring used in _getXxxScore() below - subclass overrideable
    #

    def _preferHighRankMoves(self):
        return 0

    # Basic bonus for moving a card.
    # Bonus must be in range 0..999

    BONUS_DROP_CARD = 300        # 0..400
    BONUS_SAME_SUIT_MOVE = 200        # 0..400
    BONUS_NORMAL_MOVE = 100        # 0..400

    def _getMoveCardBonus(self, r, t, pile, rpile):
        assert pile
        bonus = 0
        if rpile:
            rr = self.ClonedStack(r, stackcards=rpile)
            if (rr.canDropCards(self.game.s.foundations))[0]:
                # the card below the pile can be dropped
                bonus = self.BONUS_DROP_CARD
        if t.cards and t.cards[-1].suit == pile[0].suit:
            # simple heuristics - prefer moving high-rank cards
            bonus += self.BONUS_SAME_SUIT_MOVE + (1 + pile[0].rank)
        elif self._preferHighRankMoves():
            # simple heuristics - prefer moving high-rank cards
            bonus += self.BONUS_NORMAL_MOVE + (1 + pile[0].rank)
        elif rpile:
            # simple heuristics - prefer low-rank cards in rpile
            bonus += self.BONUS_NORMAL_MOVE + (self.K - rpile[-1].rank)
        else:
            # simple heuristics - prefer moving high-rank cards
            bonus += self.BONUS_NORMAL_MOVE + (1 + pile[0].rank)
        return bonus

    # Special bonus for facing up a card after the current move.
    # Bonus must be in range 0..9000

    BONUS_FLIP_CARD = 1500        # 0..9000

    def _getFlipSpecialBonus(self, r, t, pile, rpile):
        assert pile and rpile
        # The card below the pile can be flipped
        # (do not cheat and look at it !)
        # default: prefer a short rpile
        bonus = max(self.BONUS_FLIP_CARD - len(rpile), 0)
        return bonus

    # Special bonus for moving a pile from stack r to stack t.
    # Bonus must be in range 0..9000

    BONUS_CREATE_EMPTY_ROW = 9000        # 0..9000
    BONUS_CAN_DROP_ALL_CARDS = 4000        # 0..4000
    BONUS_CAN_CREATE_EMPTY_ROW = 2000        # 0..4000

    def _getMoveSpecialBonus(self, r, t, pile, rpile):
        # check if we will create an empty row
        if not rpile:
            return self.BONUS_CREATE_EMPTY_ROW
        # check if the card below the pile can be flipped
        if not rpile[-1].face_up:
            return self._getFlipSpecialBonus(r, t, pile, rpile)
        # check if all the cards below our pile could be dropped
        if self._canDropAllCards(r, self.game.s.foundations, stackcards=rpile):
            # we can drop the whole remaining pile
            # (and will create an empty row in the next move)
            # print "BONUS_CAN_DROP_ALL_CARDS", r, pile, rpile
            self.bonus_color = self.RED
            return self.BONUS_CAN_DROP_ALL_CARDS + \
                self.BONUS_CAN_CREATE_EMPTY_ROW
        # check if the cards below our pile are a whole row
        if r.canMoveCards(rpile):
            # could we move the remaining pile ?
            for x in self.game.s.rows:
                # note: we allow x == r here, because the pile
                #       (currently at the top of r) will be
                #       available in the next move
                if x is t or not x.cards:
                    continue
                if x.acceptsCards(r, rpile):
                    # we can create an empty row in the next move
                    # print "BONUS_CAN_CREATE_EMPTY_ROW", r, x, pile, rpile
                    self.bonus_color = self.BLUE
                    return self.BONUS_CAN_CREATE_EMPTY_ROW
        return 0

    #
    # scoring used in getHints() - subclass overrideable
    #

    # Score for moving a pile from stack r to stack t.
    # Increased score should be in range 0..9999
    def _getMovePileScore(self, score, color, r, t, pile, rpile):
        assert pile
        self.bonus_color = color
        b1 = self._getMoveSpecialBonus(r, t, pile, rpile)
        assert 0 <= b1 <= 9000
        b2 = self._getMoveCardBonus(r, t, pile, rpile)
        assert 0 <= b2 <= 999
        return score + b1 + b2, self.bonus_color

    # Score for moving a pile (usually a single card) from the WasteStack.
    def _getMoveWasteScore(self, score, color, r, t, pile, rpile):
        assert pile
        self.bonus_color = color
        score = 30000
        if t.cards:
            score = 31000
        b2 = self._getMoveCardBonus(r, t, pile, rpile)
        assert 0 <= b2 <= 999
        return score + b2, self.bonus_color

    # Score for dropping ncards from stack r to stack t.
    def _getDropCardScore(self, score, color, r, t, ncards):
        assert t is not r
        if ncards > 1:
            # drop immediately (Spider)
            return 93000, color
        pile = r.cards
        c = pile[-1]
        # compute distance to t.cap.base_rank - compare Stack.getRankDir()
        if t.cap.base_rank < 0:
            d = len(t.cards)
        else:
            d = (c.rank - t.cap.base_rank) % t.cap.mod
            if d > t.cap.mod // 2:
                d = d - t.cap.mod
        if abs(d) <= 1:
            # drop Ace and 2 immediately
            score = 92000
        elif r in self.game.sg.talonstacks:
            score = 25000              # less than _getMoveWasteScore()
        elif len(pile) == 1:
            # score = 50000
            score = 91000
        elif self._canDropAllCards(
                r, self.game.s.foundations, stackcards=pile[:-1]):
            score = 90000
            color = self.RED
        else:
            # don't drop this card too eagerly - we may need it
            # for pile moving
            score = 50000
        score += (self.K - c.rank)
        return score, color

    #
    # compute hints - main hint intelligence
    #

    def computeHints(self):
        game = self.game

        # 1) check Tableau piles
        self.step010(game.sg.dropstacks, game.s.rows)

        # 2) try if we can move part of a pile within the RowStacks
        #    so that we can drop a card afterwards
        if not self.hints and self.level >= 1:
            self.step020(game.s.rows, game.s.foundations)

        # 3) try if we should move a card from a Foundation to a RowStack
        if not self.hints and self.level >= 1:
            self.step030(game.s.foundations, game.s.rows, game.sg.dropstacks)

        # 4) try if we can move a card from a RowStack to a ReserveStack
        if not self.hints or self.level == 0:
            self.step040(game.s.rows, game.sg.reservestacks)

        # 5) try if we should move a card from a ReserveStack to a RowStack
        if not self.hints or self.level == 0:
            self.step050(game.sg.reservestacks, game.s.rows)

        # Don't be too clever and give up ;-)

    #
    # implementation of the hint steps
    #

    # 1) check Tableau piles

    def step010(self, dropstacks, rows):
        # for each stack
        for r in dropstacks:
            # 1a) try if we can drop cards
            t, ncards = r.canDropCards(self.game.s.foundations)
            if t:
                score, color = 0, None
                score, color = self._getDropCardScore(
                    score, color, r, t, ncards)
                self.addHint(score, ncards, r, t, color)
                if score >= 90000 and self.level >= 1:
                    break
            # 1b) try if we can move cards to one of the RowStacks
            for pile in self.step010b_getPiles(r):
                if pile:
                    self.step010_movePile(r, pile, rows)

    def step010b_getPiles(self, stack):
        # return all moveable piles for this stack, longest one first
        return (stack.getPile(), )

    def step010_movePile(self, r, pile, rows):
        lp = len(pile)
        lr = len(r.cards)
        assert 1 <= lp <= lr
        rpile = r.cards[: (lr-lp)]   # remaining pile

        empty_row_seen = 0
        r_is_waste = r in self.game.sg.talonstacks

        for t in rows:
            score, color = 0, None
            if not self.shallMovePile(r, t, pile, rpile):
                continue
            if r_is_waste:
                # moving a card from the WasteStack
                score, color = self._getMoveWasteScore(
                    score, color, r, t, pile, rpile)
            else:
                if not t.cards:
                    # the target stack is empty
                    if lp == lr:
                        # do not move a whole stack from row to row
                        continue
                    if empty_row_seen:
                        # only make one hint for moving to an empty stack
                        # (in case we have multiple empty stacks)
                        continue
                    score = 60000
                    empty_row_seen = 1
                else:
                    # the target stack is not empty
                    score = 80000
                score, color = self._getMovePileScore(
                    score, color, r, t, pile, rpile)
            self.addHint(score, lp, r, t, color)

    # 2) try if we can move part of a pile within the RowStacks
    #    so that we can drop a card afterwards
    #    score: 40000 .. 59999

    step020_getPiles = step010b_getPiles

    def step020(self, rows, foundations):
        for r in rows:
            for pile in self.step020_getPiles(r):
                if not pile or len(pile) < 2:
                    continue
                # is there a card in our pile that could be dropped ?
                drop_info = []
                i = 0
                for c in pile:
                    rr = self.ClonedStack(r, stackcards=[c])
                    stack, ncards = rr.canDropCards(foundations)
                    if stack and stack is not r:
                        assert ncards == 1
                        drop_info.append((c, stack, ncards, i))
                    i = i + 1
                # now try to make a move so that the drop-card will get free
                for di in drop_info:
                    c = di[0]
                    sub_pile = pile[di[3]+1:]
                    # print "trying drop move", c, pile, sub_pile
                    # assert r.canMoveCards(sub_pile)
                    if not r.canMoveCards(sub_pile):
                        continue
                    for t in rows:
                        if t is r or not t.acceptsCards(r, sub_pile):
                            continue
                        # print "drop move", r, t, sub_pile
                        score = 40000
                        score = score + 1000 + (self.K - r.getCard().rank)
                        # force the drop (to avoid loops)
                        force = (999999, 0, di[2], r, di[1], self.BLUE, None)
                        self.addHint(
                                score, len(sub_pile), r, t,
                                self.RED, forced_move=force)

    # 3) try if we should move a card from a Foundation to a RowStack
    #    score: 20000 .. 29999

    def step030(self, foundations, rows, dropstacks):
        for s in foundations:
            card = s.getCard()
            if not card or not s.canMoveCards([card]):
                continue
            # search a RowStack that would accept the card
            for t in rows:
                if t is s or not t.acceptsCards(s, [card]):
                    continue
                tt = self.ClonedStack(t, stackcards=t.cards+[card])
                # search a Stack that would benefit from this card
                for r in dropstacks:
                    if r is t:
                        continue
                    pile = r.getPile()
                    if not pile:
                        continue
                    if not tt.acceptsCards(r, pile):
                        continue
                    # compute remaining pile in r
                    rpile = r.cards[:(len(r.cards)-len(pile))]
                    rr = self.ClonedStack(r, stackcards=rpile)
                    if rr.acceptsCards(t, pile):
                        # the pile we are going to move from r to t
                        # could be moved back from t ro r - this is
                        # dangerous as we can create loops...
                        continue
                    score = 20000 + card.rank
                    # print score, s, t, r, pile, rpile
                    # force the move from r to t (to avoid loops)
                    force = (999999, 0, len(pile), r, t, self.BLUE, None)
                    self.addHint(score, 1, s, t, self.BLUE, forced_move=force)

    # 4) try if we can move a card from a RowStack to a ReserveStack
    #    score: 10000 .. 19999

    def step040(self, rows, reservestacks):
        if not reservestacks:
            return
        for r in rows:
            card = r.getCard()
            if not card or not r.canMoveCards([card]):
                continue
            pile = [card]
            # compute remaining pile in r
            rpile = r.cards[:(len(r.cards)-len(pile))]
            rr = self.ClonedStack(r, stackcards=rpile)
            for t in reservestacks:
                if t is r or not t.acceptsCards(r, pile):
                    continue
                if rr.acceptsCards(t, pile):
                    # the pile we are going to move from r to t
                    # could be moved back from t ro r - this is
                    # dangerous as we can create loops...
                    continue
                score = 10000
                score, color = self._getMovePileScore(
                    score, None, r, t, pile, rpile)
                self.addHint(score, len(pile), r, t, color)
                break

    # 5) try if we should move a card from a ReserveStack to a RowStack

    def step050(self, reservestacks, rows):
        if not reservestacks:
            return
        # FIXME


# ************************************************************************
# *
# ************************************************************************

class CautiousDefaultHint(DefaultHint):
    shallMovePile = DefaultHint._cautiousShallMovePile
    # shallMovePile = DefaultHint._cautiousDemoShallMovePile

    def _preferHighRankMoves(self):
        return 1


# ************************************************************************
# * now some default hints for the various game types
# ************************************************************************

# DefaultHint is optimized for Klondike type games anyway
class KlondikeType_Hint(DefaultHint):
    pass


# this works for Yukon, but not too well for Russian Solitaire
class YukonType_Hint(CautiousDefaultHint):
    def step010b_getPiles(self, stack):
        # return all moveable piles for this stack, longest one first
        p = stack.getPile()
        piles = []
        while p:
            piles.append(p)
            p = p[1:]       # note: we need a fresh shallow copy
        return piles


class Yukon_Hint(YukonType_Hint):
    BONUS_FLIP_CARD = 9000
    BONUS_CREATE_EMPTY_ROW = 100

    # FIXME: this is only a rough approximation and doesn't seem to help
    #        for Russian Solitaire
    def _getMovePileScore(self, score, color, r, t, pile, rpile):
        s, color = YukonType_Hint._getMovePileScore(
            self, score, color, r, t, pile, rpile)
        bonus = s - score
        assert 0 <= bonus <= 9999
        # We must take care when moving piles that we won't block cards,
        # i.e. if there is a card in pile which would be needed
        # for a card in stack t.
        tpile = t.getPile()
        if tpile:
            for cr in pile:
                rr = self.ClonedStack(r, stackcards=[cr])
                for ct in tpile:
                    if rr.acceptsCards(t, [ct]):
                        d = bonus // 1000
                        bonus = (d * 1000) + bonus % 100
                        break
        return score + bonus, color


# FIXME
class FreeCellType_Hint(CautiousDefaultHint):
    pass


class GolfType_Hint(DefaultHint):
    pass


class SpiderType_Hint(DefaultHint):
    pass


# ************************************************************************
# * FreeCell-Solver
# ************************************************************************

class Base_Solver_Hint:
    def __init__(self, game, dialog, **game_type):
        self.game = game
        self.dialog = dialog
        self.game_type = game_type
        self.options = {
            'max_iters': 10000,
            'progress': False,
            'preset': None,
            }
        self.hints = []
        self.hints_index = 0

        # correct cards rank if foundations.base_rank != 0 (Penguin, Opus)
        if 'base_rank' in game_type:    # (Simple Simon)
            self.base_rank = game_type['base_rank']
        else:
            self.base_rank = game.s.foundations[0].cap.base_rank
        # print 'game_type:', game_type
        # print 'base_rank:', self.base_rank

    def config(self, **kw):
        self.options.update(kw)

    def _card2str_format(self, fmt, card):
        # row and reserves
        rank = (card.rank-self.base_rank) % 13
        return fmt % {'R': "A23456789TJQK"[rank], 'S': "CSHD"[card.suit]}

    def card2str1(self, card):
        # row and reserves
        return self._card2str_format('%(R)s%(S)s', card)

    def card2str2(self, card):
        # foundations
        return self._card2str_format('%(S)-s%(R)s', card)

# hard solvable: Freecell #47038300998351211829 (65539 iters)

    def getHints(self, taken_hint=None):
        if taken_hint and taken_hint[6]:
            return [taken_hint[6]]
        h = self.hints[self.hints_index]
        # print 'getHints', taken_hint, h
        if h is None:
            return None
        ncards, src, dest = h
        thint = None
        if len(src.cards) > ncards and not src.cards[-ncards-1].face_up:
            # flip card
            thint = (999999, 0, 1, src, src, None, None)
        if dest is None:                 # foundation
            cards = src.cards[-ncards:]
            for f in self.game.s.foundations:
                if f.acceptsCards(src, cards):
                    dest = f
                    break
        assert dest
        hint = (999999, 0, ncards, src, dest, None, thint)
        self.hints_index += 1
        # print hint
        return [hint]

    def colonPrefixMatch(self, prefix, s):
        m = re.match(prefix + ': (\d+)', s)
        if m:
            self._v = int(m.group(1))
            return True
        else:
            self._v = None
            return False

    def run_solver(self, command, board):
        if DEBUG:
            print(command)
        kw = {'shell': True,
              'stdin': subprocess.PIPE,
              'stdout': subprocess.PIPE,
              'stderr': subprocess.PIPE}
        if os.name != 'nt':
            kw['close_fds'] = True
        p = subprocess.Popen(command, **kw)
        bytes_board = board
        if sys.version_info > (3,):
            bytes_board = bytes(board, 'utf-8')
        pout, perr = p.communicate(bytes_board)
        if p.returncode in (127, 1):
            # Linux and Windows return codes for "command not found" error
            raise RuntimeError('Solver exited with {}'.format(p.returncode))
        return BytesIO(pout), BytesIO(perr)


class FreeCellSolver_Hint(Base_Solver_Hint):
    def _determineIfSolverState(self, line):
        if re.search('^(?:Iterations count exceeded)', line):
            self.solver_state = 'intractable'
            return True
        elif re.search('^(?:I could not solve this game)', line):
            self.solver_state = 'unsolved'
            return True
        else:
            return False

    def _isSimpleSimon(self):
        game_type = self.game_type
        return ('preset' in game_type and
                game_type['preset'] == 'simple_simon')

    def _addBoardLine(self, l):
        self.board += l + '\n'
        return

    def _addPrefixLine(self, prefix, b):
        if b:
            self._addBoardLine(prefix + b)
        return

    def importFile(solver, fh, s_game, self):
        s_game.endGame()
        s_game.newGame(
            shuffle=True,
            dealer=lambda: solver.importFileHelper(fh, s_game))

    def importFileHelper(solver, fh, s_game):
        game = s_game.s
        stack_idx = 0

        RANKS_S = "A23456789TJQK"
        RANKS0_S = '0' + RANKS_S
        RANKS_RE = '[' + RANKS_S + ']'
        SUITS_S = "CSHD"
        SUITS_RE = '[' + SUITS_S + ']'
        CARD_RE = r'(?:' + RANKS_RE + SUITS_RE + ')'

        def cards():
            return game.talon.cards

        def put(target, suit, rank):
            ret = [i for i, c in enumerate(cards())
                   if c.suit == suit and c.rank == rank]
            assert len(ret) == 1
            ret = ret[0]
            game.talon.cards = \
                cards()[0:ret] + cards()[(ret+1):] + [cards()[ret]]
            s_game.flipMove(game.talon)
            s_game.moveMove(1, game.talon, target, frames=0)

        def put_str(target, str_):
            put(target, SUITS_S.index(str_[1]), RANKS_S.index(str_[0]))

        def my_find_re(RE, m):
            s = m.group(1)
            assert re.match(r'^\s*(?:' + RE + r')?(?:\s+' + RE + r')*\s*$', s)
            return re.findall(r'\b' + RE + r'\b', s)

        for line_p in fh:
            line = line_p.rstrip('\r\n')
            m = re.match(r'^(?:Foundations:|Founds?:)\s*(.*)', line)
            if m:
                for gm in my_find_re(
                        r'(' + SUITS_RE + r')-([' + RANKS0_S + r'])', m):
                    for foundat in game.foundations:
                        suit = foundat.cap.suit
                        if SUITS_S[suit] == gm[0]:
                            for r in range(RANKS0_S.index(gm[1])):
                                put(foundat, suit, r)
                            break
                continue
            m = re.match(r'^(?:FC:|Freecells:)\s*(.*)', line)
            if m:
                g = my_find_re(r'(' + CARD_RE + r'|\-)', m)
                while len(g) < len(game.reserves):
                    g.append('-')
                for i, gm in enumerate(g):
                    str_ = gm
                    if str_ != '-':
                        put_str(game.reserves[i], str_)
                continue
            m = re.match(r'^:?\s*(.*)', line)
            assert m
            for str_ in my_find_re(r'(' + CARD_RE + r')', m):
                put_str(game.rows[stack_idx], str_)

            stack_idx += 1
        assert len(cards()) == 0

    def calcBoardString(self):
        game = self.game
        self.board = ''
        is_simple_simon = self._isSimpleSimon()
        #
        #
        b = ''
        for s in game.s.foundations:
            if s.cards:
                b += ' ' + self.card2str2(
                    s.cards[0 if is_simple_simon else -1])
        self._addPrefixLine('Founds:', b)

        b = ''
        for s in game.s.reserves:
            b += ' ' + (self.card2str1(s.cards[-1]) if s.cards else '-')
        self._addPrefixLine('FC:', b)

        for s in game.s.rows:
            b = ''
            for c in s.cards:
                cs = self.card2str1(c)
                if not c.face_up:
                    cs = '<%s>' % cs
                b += cs + ' '
            self._addBoardLine(b.strip())

        return self.board

    def computeHints(self):
        game = self.game
        game_type = self.game_type
        progress = self.options['progress']

        board = self.calcBoardString()
        #
        if DEBUG:
            print('--------------------\n', board, '--------------------')
        #
        args = []
        # args += ['-sam', '-p', '-opt', '--display-10-as-t']
        args += ['-m', '-p', '-opt', '-sel']
        if progress:
            args += ['--iter-output']
            if DEBUG:
                args += ['-s']
        if self.options['preset'] and self.options['preset'] != 'none':
            args += ['--load-config', self.options['preset']]
        args += ['--max-iters', self.options['max_iters'],
                 '--decks-num', game.gameinfo.decks,
                 '--stacks-num', len(game.s.rows),
                 '--freecells-num', len(game.s.reserves),
                 ]
        #
        if 'preset' in game_type:
            args += ['--preset', game_type['preset']]
        if 'sbb' in game_type:
            args += ['--sequences-are-built-by', game_type['sbb']]
        if 'sm' in game_type:
            args += ['--sequence-move', game_type['sm']]
        if 'esf' in game_type:
            args += ['--empty-stacks-filled-by', game_type['esf']]

        command = FCS_COMMAND+' '+' '.join([str(i) for i in args])
        pout, perr = self.run_solver(command, board)
        #
        stack_types = {
            'the': game.s.foundations,
            'stack': game.s.rows,
            'freecell': game.s.reserves,
            }
        if DEBUG:
            start_time = time.time()
        if progress:
            # iteration output
            iter_ = 0
            depth = 0
            states = 0

            for sbytes in pout:
                s = unicode(sbytes, encoding='utf-8')
                if DEBUG >= 5:
                    print(s)

                if self.colonPrefixMatch('Iteration', s):
                    iter_ = self._v
                elif self.colonPrefixMatch('Depth', s):
                    depth = self._v
                elif self.colonPrefixMatch('Stored-States', s):
                    states = self._v
                    if iter_ % 100 == 0:
                        self.dialog.setText(iter=iter_, depth=depth,
                                            states=states)
                elif re.search('^(?:-=-=)', s):
                    break
                elif self._determineIfSolverState(s):
                    break
            self.dialog.setText(iter=iter_, depth=depth, states=states)

        hints = []
        for sbytes in pout:
            s = unicode(sbytes, encoding='utf-8')
            if DEBUG:
                print(s)
            if self._determineIfSolverState(s):
                next
            m = re.match('Total number of states checked is (\d+)\.', s)
            if m:
                iter_ = int(m.group(1))
                self.dialog.setText(iter=iter_)

            m = re.match('This scan generated (\d+) states\.', s)

            if m:
                states = int(m.group(1))
                self.dialog.setText(states=states)

            m = re.match('Move (.*)', s)
            if not m:
                continue

            move_s = m.group(1)

            m = re.match(
                'the sequence on top of Stack (\d+) to the foundations',
                move_s)

            if m:
                ncards = 13
                st = stack_types['stack']
                sn = int(m.group(1))
                src = st[sn]
                dest = None
            else:
                m = re.match(
                    '(?P<ncards>a card|(?P<count>\d+) cards) '
                    'from (?P<source_type>stack|freecell) '
                    '(?P<source_idx>\d+) to '
                    '(?P<dest>the foundations|(?P<dest_type>freecell|stack) '
                    '(?P<dest_idx>\d+))\s*', move_s)

                if not m:
                    continue

                ncards = m.group('ncards')
                if ncards == 'a card':
                    ncards = 1
                else:
                    ncards = int(m.group('count'))

                st = stack_types[m.group('source_type')]
                sn = int(m.group('source_idx'))
                src = st[sn]            # source stack

                dest_s = m.group('dest')
                if dest_s == 'the foundations':
                    # to foundation
                    dest = None
                else:
                    # to rows or reserves
                    dt = stack_types[m.group('dest_type')]
                    dn = int(m.group('dest_idx'))
                    dest = dt[dn]

            hints.append([ncards, src, dest])
            # print src, dest, ncards

        #
        if DEBUG:
            print('time:', time.time()-start_time)
        # print perr.read(),

        self.hints = hints
        if len(hints) > 0:
            self.solver_state = 'solved'
        self.hints.append(None)         # XXX

        # print self.hints

        pout.close()
        perr.close()


class BlackHoleSolver_Hint(Base_Solver_Hint):
    BLACK_HOLE_SOLVER_COMMAND = 'black-hole-solve'

    def calcBoardString(self):
        board = ''
        cards = self.game.s.foundations[0].cards
        s = '-'
        if (len(cards) > 0):
            s = self.card2str1(cards[-1])
        board += 'Foundations: ' + s + '\n'

        for s in self.game.s.rows:
            b = ''
            for c in s.cards:
                cs = self.card2str1(c)
                if not c.face_up:
                    cs = '<%s>' % cs
                b += cs + ' '
            board += b.strip() + '\n'

        return board

    def computeHints(self):
        game = self.game
        game_type = self.game_type

        board = self.calcBoardString()
        #
        if DEBUG:
            print('--------------------\n', board, '--------------------')
        #
        args = []
        # args += ['-sam', '-p', '-opt', '--display-10-as-t']
        args += ['--game', game_type['preset'], '--rank-reach-prune']
        args += ['--max-iters', self.options['max_iters']]
        #

        command = self.BLACK_HOLE_SOLVER_COMMAND + ' ' + \
            ' '.join([str(i) for i in args])
        pout, perr = self.run_solver(command, board)
        #
        if DEBUG:
            start_time = time.time()

        result = ''
        # iteration output
        iter_ = 0
        depth = 0
        states = 0

        for sbytes in pout:
            s = unicode(sbytes, encoding='utf-8')
            if DEBUG >= 5:
                print(s)

            m = re.search('^(Intractable!|Unsolved!|Solved!)', s.rstrip())
            if m:
                result = m.group(1)
                break
        self.dialog.setText(iter=iter_, depth=depth, states=states)

        if (result == 'Intractable!'):
            self.solver_state = 'intractable'
            return
        if (result == 'Unsolved!'):
            self.solver_state = 'unsolved'
            return

        self.solver_state = 'solved'

        hints = []
        for sbytes in pout:
            s = unicode(sbytes, encoding='utf-8')
            if DEBUG:
                print(s)
            m = re.match('Total number of states checked is (\d+)\.', s)
            if m:
                iter_ = int(m.group(1))
                self.dialog.setText(iter=iter_)
                continue

            m = re.match('This scan generated (\d+) states\.', s)

            if m:
                states = int(m.group(1))
                self.dialog.setText(states=states)
                continue

            m = re.match(
                'Move a card from stack ([0-9]+) to the foundations', s)
            if not m:
                continue

            found_stack_idx = int(m.group(1))
            ncards = 1
            st = game.s.rows
            sn = found_stack_idx
            src = st[sn]            # source stack
            dest = None

            hints.append([ncards, src, dest])
            # print src, dest, ncards

        #
        if DEBUG:
            print('time:', time.time()-start_time)
        # print perr.read(),

        self.hints = hints
        self.hints.append(None)         # XXX

        # print self.hints

        pout.close()
        perr.close()


class FreeCellSolverWrapper:

    def __init__(self, **game_type):
        self.game_type = game_type

    def __call__(self, game, dialog):
        hint = FreeCellSolver_Hint(game, dialog, **self.game_type)
        return hint


class BlackHoleSolverWrapper:

    def __init__(self, **game_type):
        self.game_type = game_type

    def __call__(self, game, dialog):
        hint = BlackHoleSolver_Hint(game, dialog, **self.game_type)
        return hint
