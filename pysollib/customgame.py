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

from gamedb import registerGame, GameInfo, GI
from util import *
from stack import *
from game import Game
from layout import Layout
from hint import AbstractHint, DefaultHint, CautiousDefaultHint, Yukon_Hint
#from pysoltk import MfxCanvasText

from wizardutil import WizardWidgets


# /***********************************************************************
# //
# ************************************************************************/

class CustomGame(Game):

    def createGame(self):

        ss = self.SETTINGS
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
        ##from pprint import pprint; pprint(s)

        # foundations
        kw = {
            'dir': s['found_dir'],
            'base_rank': s['found_base_card'],
            'mod': 13,
            }
        # max_move
        if s['found_type'] not in (Spider_SS_Foundation,
                                   Spider_AC_Foundation,):
            kw['max_move'] = s['found_max_move']
        # suit
        if s['found_type'] in (Spider_SS_Foundation,
                               Spider_AC_Foundation,):
            kw['suit'] = ANY_SUIT
        # fix dir and base_rank for Spider foundations
        if s['found_type'] in (Spider_SS_Foundation,
                               Spider_AC_Foundation,):
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
        row = StackWrapper(s['rows_type'], **kw)

        # layout
        layout_kw = {
            'rows'     : s['rows_num'],
            'reserves' : s['reserves_num'],
            'waste'    : False,
            'texts'    : True,
            }
        if s['talon'] is InitialDealTalonStack:
            layout_kw['texts'] = False
        layout_kw['playcards'] = max(16, 12+s['deal_face_down']+s['deal_face_up'])

        # reserves
        if s['reserves_num']:
            kw = {
                'max_accept': s['reserves_max_accept'],
                }
            if s['reserves_max_accept']:
                layout_kw['reserve_class'] = StackWrapper(ReserveStack, **kw)
            else:
                layout_kw['reserve_class'] = StackWrapper(OpenStack, **kw)

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
                ((AC_RowStack, UD_AC_RowStack, Yukon_AC_RowStack),
                 (self._shallHighlightMatch_AC,
                  self._shallHighlightMatch_ACW)),
                ((SS_RowStack, UD_SS_RowStack, Yukon_SS_RowStack),
                 (self._shallHighlightMatch_SS,
                  self._shallHighlightMatch_SSW)),
                ((RK_RowStack, UD_RK_RowStack, Yukon_RK_RowStack),
                 (self._shallHighlightMatch_RK,
                  self._shallHighlightMatch_RKW)),
                ((SC_RowStack, UD_SC_RowStack),
                 (self._shallHighlightMatch_SC,
                  self._shallHighlightMatch_SCW)),
                ((BO_RowStack,),
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
        if s['rows_type'] in (Spider_AC_RowStack, Spider_SS_RowStack):
            self.getQuickPlayScore = self._getSpiderQuickPlayScore

        # canDropCards
        if s['found_type'] in (Spider_SS_Foundation,
                               Spider_AC_Foundation,):
            for stack in self.s.rows:
                stack.canDropCards = stack.spiderCanDropCards

        # acceptsCards
        if s['found_base_card'] == ANY_RANK and s['found_equal']:
            for stack in self.s.foundations:
                stack.acceptsCards = stack.varyAcceptsCards
                stack.getBaseCard = stack.varyGetBaseCard

        # Hint_Class
        # TODO
        if s['rows_type'] in (Yukon_SS_RowStack,
                              Yukon_AC_RowStack,
                              Yukon_RK_RowStack):
            self.Hint_Class = Yukon_Hint


    def startGame(self):

        def deal(rows, flip, frames, max_cards):
            if max_cards <= 0:
                return 0
            return self.s.talon.dealRowAvail(rows=rows, flip=flip,
                                             frames=frames)

        frames = 0
        s = self.SETTINGS
        max_cards = s['deal_max_cards'] - len(self.s.rows)
        if self.s.waste:
            max_cards -= 1
        anim_frames = -1

        # deal to reserves
        n = s['deal_to_reserves']
        for i in range(n):
            max_cards -= deal(self.s.reserves[:max_cards],
                              True, frames, max_cards)
            if frames == 0 and len(self.s.talon.cards) < 16:
                frames = anim_frames
                self.startDealSample()

        # deal to rows
        face_down = s['deal_face_down']
        max_rows = s['deal_face_down'] + s['deal_face_up']
        if s['deal_type'] == 'Triangle':
            # triangle
            for i in range(1, len(self.s.rows)):
                flip = (face_down <= 0)
                max_cards -= deal(self.s.rows[i:i+max_cards],
                                  flip, frames, max_cards)
                face_down -= 1
                max_rows -= 1
                if max_rows == 1:
                    break
                if frames == 0 and len(self.s.talon.cards) < 16:
                    frames = anim_frames
                    self.startDealSample()

        else:
            # rectangle
            for i in range(max_rows-1):
                flip = (face_down <= 0)
                max_cards -= deal(self.s.rows[:max_cards],
                                  flip, frames, max_cards)
                face_down -= 1
                if frames == 0 and len(self.s.talon.cards) < 16:
                    frames = anim_frames
                    self.startDealSample()
        if frames == 0:
            self.startDealSample()
        self.s.talon.dealRowAvail(frames=anim_frames)
        if isinstance(self.s.talon, InitialDealTalonStack):
            while self.s.talon.cards:
                self.s.talon.dealRowAvail(frames=anim_frames)

        # deal to waste
        if self.s.waste:
            self.s.talon.dealCards()



def registerCustomGame(gameclass):

    s = gameclass.SETTINGS
    for w in WizardWidgets:
        if isinstance(w, basestring):
            continue
        if w.var_name == 'decks':
            v = s['decks']
            decks = dict(w.values_map)[v]
        elif w.var_name == 'redeals':
            v = s['redeals']
            redeals = dict(w.values_map)[v]
        elif w.var_name == 'skill_level':
            v = s['skill_level']
            skill_level = dict(w.values_map)[v]
    gameid = s['gameid']

    registerGame(GameInfo(gameid, gameclass, s['name'],
                          GI.GT_CUSTOM | GI.GT_ORIGINAL,
                          decks, redeals, skill_level))

