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


__all__ = ['GameInfoDialog']

# imports
import os, sys
from Tkinter import *

# PySol imports
from pysollib.mfxutil import KwStruct
from pysollib.gamedb import GI

# Toolkit imports
from tkwidget import MfxDialog

# /***********************************************************************
# //
# ************************************************************************/

class GameInfoDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = Frame(top_frame)
        frame.pack(expand=YES, fill=BOTH, padx=5, pady=10)
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
        row = 0
        for n, t in (('Name:', gi.name),
                     ('Short name:', gi.short_name),
                     ('ID:', gi.id),
                     ('Alt names:', '\n'.join(gi.altnames)),
                     ('Decks:', gi.decks),
                     ('Cards:', gi.ncards),
                     ('Redeals:', redeals),
                     ('Category:', cat),
                     ('Type:', type),
                     ('Flags:', '\n'.join(flags)),
                     ('Rules filename:', gi.rules_filename),
                     ('Module:', game.__module__),
                     ('Class:', game.__class__.__name__),
                     ('Hint:', game.Hint_Class.__name__),
                     ):
            if t:
                Label(frame, text=n, anchor=W).grid(row=row, column=0, sticky=N+W)
                Label(frame, text=t, anchor=W, justify=LEFT).grid(row=row, column=1, sticky=N+W)
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
        Label(frame, text=title, anchor=W).grid(row=row, column=0, sticky=N+W)
        if isinstance(stacks, (list, tuple)):
            fs = {}
            for f in stacks:
                cn = f.__class__.__name__
                if fs.has_key(cn):
                    fs[cn] += 1
                else:
                    fs[cn] = 1
            t = '\n'.join(['%s (%d)' % (i[0], i[1]) for i in fs.items()])
        else:
            t = stacks.__class__.__name__
        Label(frame, text=t, anchor=W, justify=LEFT).grid(row=row, column=1, sticky=N+W)


    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),),
                      default=0,
                      separatorwidth=2,
                      )
        return MfxDialog.initKw(self, kw)
