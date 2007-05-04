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
from hint import AbstractHint, DefaultHint, CautiousDefaultHint
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
            if w.widget == 'menu':
                v = dict(w.values_map)[ss[w.var_name]]
            else:
                v = ss[w.var_name]
            s[w.var_name] = v
        ##from pprint import pprint; pprint(s)

        # foundations
        kw = {
            'dir': s['found_dir'],
            'base_rank': s['found_base_card'],
            }
        if s['found_type'] not in (Spider_SS_Foundation,
                                   Spider_AC_Foundation,):
            kw['max_move'] = s['found_max_move']
        else:
            kw['dir'] = -kw['dir']
            if s['found_base_card'] == KING:
                kw['base_rank'] = ACE
            elif s['found_base_card'] == ACE:
                kw['base_rank'] = KING
        if s['found_wrap']:
            kw['mod'] = 13
        foundation = StackWrapper(s['found_type'], **kw)

        # talon
        kw = {
            'max_rounds': s['redeals'],
            }
        if s['redeals'] >= 0:
            kw['max_rounds'] += 1
        talon = StackWrapper(s['talon'], **kw)

        # rows
        kw = {
            'base_rank': s['rows_base_card'],
            'dir':       s['rows_dir'],
            'max_move':  s['rows_max_move'],
            }
        if s['rows_wrap']:
            kw['mod'] = 13
        row = StackWrapper(s['rows_type'], **kw)

        # layout
        layout_kw = {'rows'     : s['rows_num'],
              'waste'    : False,
              'texts'    : True,
              }
        if s['talon'] is InitialDealTalonStack:
            layout_kw['texts'] = False
        layout_kw['playcards'] = 12+s['deal_to_rows']

        # reserves
        if s['reserves_num']:
            layout_kw['reserves'] = s['reserves_num']
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

        # shallHighlightMatch
        for c, f in (
                ((Spider_AC_RowStack, Spider_SS_RowStack),
                 (self._shallHighlightMatch_RK,
                  self._shallHighlightMatch_RKW)),
                ((AC_RowStack, UD_AC_RowStack),
                 (self._shallHighlightMatch_AC,
                  self._shallHighlightMatch_ACW)),
                ((SS_RowStack, UD_SS_RowStack),
                 (self._shallHighlightMatch_SS,
                  self._shallHighlightMatch_SSW)),
                ((RK_RowStack, UD_RK_RowStack),
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

        if s['found_base_card'] == ANY_RANK:
            for stack in self.s.foundations:
                stack.acceptsCards = stack.varyAcceptsCards
                stack.getBaseCard = stack.getVaryBaseCard


    def startGame(self):
        frames = 0

        # deal to reserves
        n = self.SETTINGS['deal_to_reserves']
        for i in range(n):
            self.s.talon.dealRowAvail(rows=self.s.reserves,
                                      flip=True, frames=frames)
            if frames == 0 and len(self.s.talon.cards) < 16:
                frames = -1
                self.startDealSample()

        # deal to rows
        flip = (self.SETTINGS['deal_faceup'] == 'All cards')
        max_rows = self.SETTINGS['deal_to_rows']
        if self.SETTINGS['deal_type'] == 'Triangle':
            # triangle
            for i in range(1, len(self.s.rows)):
                self.s.talon.dealRowAvail(rows=self.s.rows[i:],
                                          flip=flip, frames=frames)
                max_rows -= 1
                if max_rows == 1:
                    break
                if frames == 0 and len(self.s.talon.cards) < 16:
                    frames = -1
                    self.startDealSample()

        else:
            # rectangle
            for i in range(max_rows-1):
                self.s.talon.dealRowAvail(rows=self.s.rows,
                                          flip=flip, frames=frames)
                if frames == 0 and len(self.s.talon.cards) < 16:
                    frames = -1
                    self.startDealSample()
        if frames == 0:
            self.startDealSample()
        self.s.talon.dealRowAvail()
        if isinstance(self.s.talon, InitialDealTalonStack):
            while self.s.talon.cards:
                self.s.talon.dealRowAvail()

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
        if w.var_name == 'redeals':
            v = s['redeals']
            redeals = dict(w.values_map)[v]
        if w.var_name == 'skill_level':
            v = s['skill_level']
            skill_level = dict(w.values_map)[v]
    gameid = s['gameid']

    registerGame(GameInfo(gameid, gameclass, s['name'],
                          GI.GT_CUSTOM | GI.GT_ORIGINAL,
                          decks, redeals, skill_level))

