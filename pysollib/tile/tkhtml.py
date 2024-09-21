#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

import os
import sys
import tkinter

from pysollib.mfxutil import Struct
from pysollib.mygettext import _
from pysollib.ui.tktile.tkhtml import Base_HTMLViewer

from six.moves import tkinter_ttk as ttk

from .statusbar import HtmlStatusbar
from .tkwidget import MfxMessageDialog

if __name__ == '__main__':
    d = os.path.abspath(os.path.join(sys.path[0], '..', '..'))
    sys.path.append(d)
    import gettext
    gettext.install('pysol', d, unicode=True)

# ************************************************************************
# *
# ************************************************************************


class HTMLViewer(Base_HTMLViewer):
    symbols_fn = {}  # filenames, loaded in Application.loadImages3
    symbols_img = {}

    def _calc_MfxMessageDialog(self):
        return MfxMessageDialog

    def __init__(self, parent, app=None, home=None):
        self.parent = parent
        self.app = app
        self.home = home
        self.url = None
        self.history = Struct(
            list=[],
            index=0,
        )
        self.visited_urls = []
        # need to keep a reference because of garbage collection
        self.images = {}
        self.defcursor = parent["cursor"]
        # self.defcursor = 'xterm'
        self.handcursor = "hand2"

        frame = ttk.Frame(parent, width=640, height=440)
        frame.pack(expand=True, fill='both')
        frame.grid_propagate(False)

        # create buttons
        button_width = 8
        self.homeButton = ttk.Button(frame, text=_("Index"),
                                     width=button_width,
                                     command=self.goHome)
        self.homeButton.grid(row=0, column=0, sticky='w')
        self.backButton = ttk.Button(frame, text=_("Back"),
                                     width=button_width,
                                     command=self.goBack)
        self.backButton.grid(row=0, column=1, sticky='w')
        self.forwardButton = ttk.Button(frame, text=_("Forward"),
                                        width=button_width,
                                        command=self.goForward)
        self.forwardButton.grid(row=0, column=2, sticky='w')
        self.closeButton = ttk.Button(frame, text=_("Close"),
                                      width=button_width,
                                      command=self.destroy)
        self.closeButton.grid(row=0, column=3, sticky='e')

        # create text widget
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, columnspan=4,
                        sticky='nsew', padx=1, pady=1)
        vbar = ttk.Scrollbar(text_frame)
        vbar.pack(side='right', fill='y')
        self.text = tkinter.Text(text_frame,
                                 fg='black', bg='white',
                                 bd=1, relief='sunken',
                                 cursor=self.defcursor,
                                 wrap='word', padx=10)
        self.text.pack(side='left', fill='both', expand=True)
        self.text["yscrollcommand"] = vbar.set
        vbar["command"] = self.text.yview

        # statusbar
        self.statusbar = HtmlStatusbar(frame, row=2, column=0, columnspan=4)

        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(1, weight=1)

        # load images
        for name, fn in self.symbols_fn.items():
            self.symbols_img[name] = self.getImage(fn)

        self.initBindings()


# ************************************************************************
# *
# ************************************************************************


def tkhtml_main(args):
    try:
        url = args[1]
    except Exception:
        url = os.path.join(os.pardir, os.pardir, "data", "html", "index.html")
    top = tkinter.Tk()
    top.tk.call("package", "require", "tile")
    top.wm_minsize(400, 200)
    viewer = HTMLViewer(top)
    viewer.app = None
    viewer.display(url)
    top.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(tkhtml_main(sys.argv))
