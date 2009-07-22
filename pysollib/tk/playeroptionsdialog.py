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

__all__ = ['PlayerOptionsDialog']

# imports
import Tkinter

# PySol imports
from pysollib.mfxutil import KwStruct, Struct

# Toolkit imports
from tkwidget import MfxDialog
from tkutil import bind


# ************************************************************************
# *
# ************************************************************************

class SelectUserNameDialog(MfxDialog):
    def __init__(self, parent, title, usernames=[], **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        listbox = Tkinter.Listbox(top_frame)
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar = Tkinter.Scrollbar(top_frame)
        scrollbar.pack(side='right', fill='y')
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=listbox.yview)

        self.username = None
        self.listbox = listbox
        bind(listbox, '<<ListboxSelect>>', self.updateUserName)
        #
        for un in usernames:
            listbox.insert('end', un)
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

        #if listbox.curselection():
        #    self.username = listbox.get(listbox.curselection())

    def updateUserName(self, *args):
        self.username = self.listbox.get(self.listbox.curselection())

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")), default=0,
                      separator=False,
                      resizable=False,
                      padx=10, pady=10,
                      buttonpadx=10, buttonpady=5,
                      )
        return MfxDialog.initKw(self, kw)



class PlayerOptionsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        self.app = app
        #
        self.update_stats_var = Tkinter.BooleanVar()
        self.update_stats_var.set(app.opt.update_player_stats != 0)
        self.confirm_var = Tkinter.BooleanVar()
        self.confirm_var.set(app.opt.confirm != 0)
        self.win_animation_var = Tkinter.BooleanVar()
        self.win_animation_var.set(app.opt.win_animation != 0)
        #
        frame = Tkinter.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        widget = Tkinter.Label(frame, text=_("\nPlease enter your name"),
                               #justify='left', anchor='w',
                               takefocus=0)
        widget.grid(row=0, column=0, columnspan=2, sticky='ew', padx=0, pady=5)
        w = kw.get("e_width", 30)    # width in characters
        self.player_var = Tkinter.Entry(frame, exportselection=1, width=w)
        self.player_var.insert(0, app.opt.player)
        self.player_var.grid(row=1, column=0, sticky='ew', padx=0, pady=5)
        widget = Tkinter.Button(frame, text=_('Choose...'),
                                command=self.selectUserName)
        widget.grid(row=1, column=1, padx=5, pady=5)
        widget = Tkinter.Checkbutton(frame, variable=self.confirm_var,
                                     anchor='w', text=_("Confirm quit"))
        widget.grid(row=2, column=0, columnspan=2, sticky='ew', padx=0, pady=5)
        widget = Tkinter.Checkbutton(frame, variable=self.update_stats_var,
                                     anchor='w',
                                     text=_("Update statistics and logs"))
        widget.grid(row=3, column=0, columnspan=2, sticky='ew', padx=0, pady=5)
###        widget = Tkinter.Checkbutton(frame, variable=self.win_animation_var,
###                                     text="Win animation")
###        widget.pack(side='top', padx=kw.padx, pady=kw.pady)
        frame.columnconfigure(0, weight=1)
        #
        self.player = self.player_var.get()
        self.confirm = self.confirm_var.get()
        self.update_stats = self.update_stats_var.get()
        self.win_animation = self.win_animation_var.get()
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def selectUserName(self, *args):
        names = self.app.getAllUserNames()
        d = SelectUserNameDialog(self.top, _("Select name"), names)
        if d.status == 0 and d.button == 0 and d.username:
            self.player_var.delete(0, 'end')
            self.player_var.insert(0, d.username)

    def mDone(self, button):
        self.button = button
        self.player = self.player_var.get()
        self.confirm = self.confirm_var.get()
        self.update_stats = self.update_stats_var.get()
        self.win_animation = self.win_animation_var.get()
        raise SystemExit

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")), default=0,
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)


# ************************************************************************
# *
# ************************************************************************


def playeroptionsdialog_main(args):
    from tkutil import wm_withdraw
    opt = Struct(player="Test", update_player_stats=1)
    app = Struct(opt=opt)
    tk = Tkinter.Tk()
    wm_withdraw(tk)
    tk.update()
    d = PlayerOptionsDialog(tk, "Player options", app)
    print d.status, d.button, ":", d.player, d.update_stats
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(playeroptionsdialog_main(sys.argv))

