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

from gamedb import registerGame, GameInfo, GI
from util import *
from stack import *
from game import Game
from layout import Layout
from hint import AbstractHint, DefaultHint, CautiousDefaultHint, Yukon_Hint

from wizardutil import WizardWidgets


# ************************************************************************
# *
# ************************************************************************

def get_settings(ss):
    s = {}
    for w in WizardWidgets:
        if isinstance(w, basestring):
            continue
        if w.var_name in ss:
            v = ss[w.var_name]
        else:
            v = w.default
        if w.widget == 'menu':
            v = dict(w.values_map)[v]
        s[w.var_name] = v
    return s


class CustomGame(Game):

    def createGame(self):

        s = get_settings(self.SETTINGS)
        ##from pprint import pprint; pprint(s)

        # foundations
        kw = {
            'dir': s['found_dir'],
            'base_rank': s['found_base_card'],
            'mod': 13,
            }
        # max_move
        if s['found_type'] not in (Spider_SS_Foundation,
                                   Spider_AC_Foundation,
                                   Spider_RK_Foundation,):
            kw['max_move'] = s['found_max_move']
        # suit
        if s['found_type'] in (Spider_SS_Foundation,
                               Spider_AC_Foundation,
                               Spider_RK_Foundation,):
            kw['suit'] = ANY_SUIT
        # fix dir and base_rank for Spider foundations
        if s['found_type'] in (Spider_SS_Foundation,
                               Spider_AC_Foundation,
                               Spider_RK_Foundation,):
            kw['dir'] = -kw['dir']
            if s['found_base_card'] == KING:
                kw['base_rank'] = ACE
            elif s['found_base_card'] == ACE:
                kw['base_rank'] = KING
        foundation = StackWrapper(s['found_type'], **kw)

        # talon
        kw = {
            'max_rounds': s['redeals'],
            }
        if s['redeals'] >= 0:
            kw['max_rounds'] += 1
        if s['talon'] is WasteTalonStack:
            kw['num_deal'] = s['deal_to_waste']
        talon = StackWrapper(s['talon'], **kw)

        # rows
        kw = {
            'base_rank': s['rows_base_card'],
            'dir':       s['rows_dir'],
            'max_move':  s['rows_max_move'],
            }
        if s['rows_wrap']:
            kw['mod'] = 13
        if s['rows_type'] in (UD_SS_RowStack, UD_AC_RowStack,
                              UD_RK_RowStack, UD_SC_RowStack):
            kw['max_move'] = 1
        # Super Move
        if s['rows_super_move'] and kw['max_move'] == 1:
            for s1, s2 in ((SS_RowStack, SuperMoveSS_RowStack),
                           (AC_RowStack, SuperMoveAC_RowStack),
                           (RK_RowStack, SuperMoveRK_RowStack),
                           (SC_RowStack, SuperMoveSC_RowStack),
                           (BO_RowStack, SuperMoveBO_RowStack)):
                if s['rows_type'] is s1:
                    s['rows_type'] = s2
                    kw['max_move'] = UNLIMITED_MOVES
                    break
        row = StackWrapper(s['rows_type'], **kw)

        # layout
        layout_kw = {
            'rows'     : s['rows_num'],
            'reserves' : s['reserves_num'],
            'waste'    : False,
            'texts'    : True,
            }
        playcards = 0
        if s['talon'] is InitialDealTalonStack:
            layout_kw['texts'] = False
            playcards = 12 + 52 * s['decks'] / s['rows_num']
        else:
            playcards = 12 + s['deal_face_down'] + s['deal_face_up']
        layout_kw['playcards'] = max(16, playcards)
        if s['talon'] in (DealRowRedealTalonStack,
                          SpiderTalonStack,
                          GroundsForADivorceTalonStack):
            layout_kw['playcards'] += 2 * s['decks']

        # reserves
        if s['reserves_num']:
            kw = {
                'max_cards': s['reserves_max_accept'],
                }
            if s['reserves_max_accept']:
                layout_kw['reserve_class'] = StackWrapper(ReserveStack, **kw)
            else:
                layout_kw['reserve_class'] = StackWrapper(OpenStack, **kw)
            if s['talon'] is DealReserveRedealTalonStack or \
               s['reserves_max_accept'] > 1 or s['deal_to_reserves'] > 1:
                layout_kw['reserve_texts'] = True

        # waste
        if s['talon'] is WasteTalonStack:
            layout_kw['waste'] = True
            layout_kw['waste_class'] = WasteStack

        Layout(self).createGame(layout_method    = s['layout'],
                                talon_class      = talon,
                                foundation_class = foundation,
                                row_class        = row,
                                **layout_kw
                                )

        # shuffle
        if s['talon_shuffle'] and s['talon'] in (WasteTalonStack,
                                                 DealRowRedealTalonStack):
            self.s.talon.dealCards = self.s.talon.shuffleAndDealCards

        # shallHighlightMatch
        for c, f in (
                ((Spider_AC_RowStack, Spider_SS_RowStack),
                 (self._shallHighlightMatch_RK,
                  self._shallHighlightMatch_RKW)),
                ((AC_RowStack, UD_AC_RowStack,
                  Yukon_AC_RowStack, SuperMoveAC_RowStack),
                 (self._shallHighlightMatch_AC,
                  self._shallHighlightMatch_ACW)),
                ((SS_RowStack, UD_SS_RowStack,
                  Yukon_SS_RowStack, SuperMoveSS_RowStack),
                 (self._shallHighlightMatch_SS,
                  self._shallHighlightMatch_SSW)),
                ((RK_RowStack, UD_RK_RowStack,
                  Yukon_RK_RowStack, SuperMoveRK_RowStack),
                 (self._shallHighlightMatch_RK,
                  self._shallHighlightMatch_RKW)),
                ((SC_RowStack, UD_SC_RowStack, SuperMoveSC_RowStack),
                 (self._shallHighlightMatch_SC,
                  self._shallHighlightMatch_SCW)),
                ((BO_RowStack, SuperMoveBO_RowStack),
                 (self._shallHighlightMatch_BO,
                  self._shallHighlightMatch_BOW)),
                ):
            if s['rows_type'] in c:
                if s['rows_wrap']:
                    self.shallHighlightMatch = f[1]
                else:
                    self.shallHighlightMatch = f[0]
                break

        # getQuickPlayScore
        if s['rows_type'] in (Spider_AC_RowStack,
                              Spider_SS_RowStack,):
            self.getQuickPlayScore = self._getSpiderQuickPlayScore

        # canDropCards
        if s['found_type'] in (Spider_SS_Foundation,
                               Spider_AC_Foundation,
                               Spider_RK_Foundation,):
            for stack in self.s.rows:
                stack.canDropCards = stack.spiderCanDropCards

        # acceptsCards
        if s['found_base_card'] == ANY_RANK and s['found_equal']:
            for stack in self.s.foundations:
                stack.acceptsCards = stack.varyAcceptsCards
                stack.getBaseCard = stack.varyGetBaseCard

        # getBottomImage
        if s['deal_face_down'] + s['deal_face_up'] == 0:
            for stack in self.s.rows:
                stack.getBottomImage = stack.getReserveBottomImage

        # Hint_Class
        # TODO
        if s['rows_type'] in (Yukon_SS_RowStack,
                              Yukon_AC_RowStack,
                              Yukon_RK_RowStack):
            self.Hint_Class = Yukon_Hint


    def _shuffleHook(self, cards):
        s = get_settings(self.SETTINGS)
        if not s['deal_found']:
            return cards
        if s['found_type'] in (Spider_SS_Foundation,
                               Spider_AC_Foundation,
                               Spider_RK_Foundation,):
            return cards
        base_card = s['found_base_card']
        if base_card == ANY_RANK:
            base_card = cards[0].rank
        # move base_card to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(
            cards,
            lambda c, rank=base_card: (c.rank == rank, c.suit))


    def startGame(self):

        s = get_settings(self.SETTINGS)
        anim_frames = -1

        def deal(rows, flip, frames, max_cards):
            if frames == 0:
                if len(self.s.talon.cards) <= min_cards or \
                       max_cards <= min_cards:
                    frames = anim_frames
                    self.startDealSample()
            if max_cards <= 0:
                return frames, 0
            max_cards -= self.s.talon.dealRowAvail(rows=rows, flip=flip,
                                                   frames=frames)
            return frames, max_cards

        frames = 0
        if isinstance(self.s.talon, InitialDealTalonStack):
            max_cards = 52 * s['decks']
        else:
            max_cards = s['deal_max_cards']

        min_cards = max(len(self.s.rows), 8)
        max_rows = s['deal_face_down'] + s['deal_face_up'] + s['deal_to_reserves']
        if max_rows <= 1:
            min_cards = max_cards

        # deal to foundations
        if s['deal_found']:
            frames, max_cards = deal(self.s.foundations,
                                     True, frames, max_cards)

        # deal to reserves
        n = s['deal_to_reserves']
        for i in range(n):
            frames, max_cards = deal(self.s.reserves[:max_cards],
                                     True, frames, max_cards)

        # deal to rows
        face_down = s['deal_face_down']
        max_rows = s['deal_face_down'] + s['deal_face_up']
        if s['deal_type'] == 'triangle':
            # triangle
            for i in range(1, len(self.s.rows)):
                if max_rows <= 1:
                    break
                flip = (face_down <= 0)
                mc = max_cards - len(self.s.rows)
                frames, max_cards = deal(self.s.rows[i:i+mc],
                                         flip, frames, max_cards)
                face_down -= 1
                max_rows -= 1

        else:
            # rectangle
            for i in range(max_rows-1):
                flip = (face_down <= 0)
                mc = max_cards - len(self.s.rows)
                frames, max_cards = deal(self.s.rows[:mc],
                                         flip, frames, max_cards)
                face_down -= 1

        if isinstance(self.s.talon, InitialDealTalonStack):
            while self.s.talon.cards:
                frames, max_cards = deal(self.s.rows, True, frames, max_cards)
        else:
            if max_rows > 0:
                deal(self.s.rows, True, frames, len(self.s.rows))

        # deal to waste
        if self.s.waste:
            if frames == 0:
                self.startDealSample()
            self.s.talon.dealCards()


def registerCustomGame(gameclass):

    s = get_settings(gameclass.SETTINGS)
    gameid = gameclass.SETTINGS['gameid']

    registerGame(GameInfo(gameid, gameclass, s['name'],
                          GI.GT_CUSTOM | GI.GT_ORIGINAL,
                          s['decks'], s['redeals'], s['skill_level']))

