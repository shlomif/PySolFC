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


__all__ = ['GameInfoDialog']

# imports
import Tkinter

# PySol imports
from pysollib.mfxutil import KwStruct
from pysollib.gamedb import GI

# Toolkit imports
from tkwidget import MfxDialog

# ************************************************************************
# *
# ************************************************************************

class GameInfoDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = Tkinter.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        game = app.game
        gi = game.gameinfo

        #
        if    gi.redeals == -2: redeals = 'VARIABLE'
        elif  gi.redeals == -1: redeals = 'UNLIMITED'
        else:                   redeals = str(gi.redeals)
        cat = '<none>'
        type = '<none>'
        flags = []
        for attr in dir(GI):
            if attr.startswith('GC_'):
                c = getattr(GI, attr)
                if gi.category == c:
                    cat = attr
            elif attr.startswith('GT_'):
                t = getattr(GI, attr)
                if t < (1<<12)-1:
                    if gi.si.game_type == t:
                        type = attr
                else:
                    if gi.si.game_flags & t:
                        flags.append(attr)
        #
        version = None
        for t in GI.GAMES_BY_PYSOL_VERSION:
            if gi.id in t[1]:
                version = t[0]
                break
        sl = {
            1: 'SL_LUCK',
            2: 'SL_MOSTLY_LUCK',
            3: 'SL_BALANCED',
            4: 'SL_MOSTLY_SKILL',
            5: 'SL_SKILL',
            }
        skill_level = sl.get(gi.skill_level)
        if game.Hint_Class is None:
            hint = None
        else:
            hint = game.Hint_Class.__name__
        row = 0
        for n, t in (('Name:', gi.name),
                     ('Short name:', gi.short_name),
                     ('ID:', gi.id),
                     ('Alt names:', '\n'.join(gi.altnames)),
                     ('PySol version:', version),
                     ('Decks:', gi.decks),
                     ('Cards:', gi.ncards),
                     ('Redeals:', redeals),
                     ('Category:', cat),
                     ('Type:', type),
                     ('Flags:', '\n'.join(flags)),
                     ('Skill level:', skill_level),
                     ('Rules filename:', gi.rules_filename),
                     ('Module:', game.__module__),
                     ('Class:', game.__class__.__name__),
                     ('Hint:', hint),
                     ):
            if t:
                Tkinter.Label(frame, text=n, anchor='w'
                              ).grid(row=row, column=0, sticky='nw')
                Tkinter.Label(frame, text=t, anchor='w', justify='left'
                              ).grid(row=row, column=1, sticky='nw')
                row += 1

        if game.s.talon:
            self.showStacks(frame, row, 'Talon:', game.s.talon)
            row += 1
        if game.s.waste:
            self.showStacks(frame, row, 'Waste:', game.s.waste)
            row += 1
        for t, s in (
            ('Foundations:', game.s.foundations,),
            ('Rows:',        game.s.rows,),
            ('Reserves:',    game.s.reserves,),
            ):
            if s:
                self.showStacks(frame, row, t, s)
                row += 1

        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def showStacks(self, frame, row, title, stacks):
        Tkinter.Label(frame, text=title, anchor='w'
                      ).grid(row=row, column=0, sticky='nw')
        if isinstance(stacks, (list, tuple)):
            fs = {}
            for f in stacks:
                cn = f.__class__.__name__
                if cn in fs:
                    fs[cn] += 1
                else:
                    fs[cn] = 1
            t = '\n'.join(['%s (%d)' % (i[0], i[1]) for i in fs.items()])
        else:
            t = stacks.__class__.__name__
        Tkinter.Label(frame, text=t, anchor='w', justify='left'
                      ).grid(row=row, column=1, sticky='nw')

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),),
                      default=0,
                      separator=True,
                      )
        return MfxDialog.initKw(self, kw)
