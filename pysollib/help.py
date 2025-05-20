#!/usr/bin/env python
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

# PySol imports
from pysollib.mygettext import _
from pysollib.pysoltk import HTMLViewer
from pysollib.pysoltk import MfxMessageDialog
from pysollib.pysoltk import PysolAboutDialog
from pysollib.pysoltk import make_help_toplevel
from pysollib.settings import PACKAGE_URL, TITLE, TOOLKIT, VERSION


# ************************************************************************
# *
# ************************************************************************

def help_about(app, timeout=0, sound=True):
    if sound:
        app.audio.playSample("about")
    t = _("A Python Solitaire Game Collection")
    if app.miscrandom.random() < 0.8:
        t = _("A World Domination Project")
    strings = (_("&Nice"), _("&Credits"))
    if timeout:
        strings = (_("&Enjoy"),)
    version = _("Version %s") % VERSION
    d = PysolAboutDialog(app, app.top, title=_("About %s") % TITLE,
                         timeout=timeout,
                         text=_('''PySol Fan Club edition
%(description)s
%(versioninfo)s

Copyright (C) 1998 - 2003 Markus F.X.J. Oberhumer.
Copyright (C) 2003 Mt. Hood Playing Card Co.
Copyright (C) 2005 - 2009 Skomoroh.
Copyright (C) 2020 - 2025 PySolFC.
All Rights Reserved.

PySol is free software distributed under the terms
of the GNU General Public License.

For more information about this application visit''') %
                         {'description': t, 'versioninfo': version},
                         url=PACKAGE_URL,
                         image=app.gimages.logos[2],
                         strings=strings, default=0,
                         separator=True)
    if d.status == 0 and d.button == 1:
        viewer = help_html(app, "credits.html", "html")
        viewer.parent.after(2, viewer.parent.focus_force)
        # help_credits(app, sound=sound)
    return d.status


def help_credits(app, timeout=0, sound=True):
    if sound:
        app.audio.playSample("credits")
    t = ""
    if TOOLKIT == "tk":
        t = "Tcl/Tk"
    elif TOOLKIT == "gtk":
        t = "PyGTK"
    elif TOOLKIT == "kde":
        t = "pyKDE"
    elif TOOLKIT == "wx":
        t = "wxPython"
    elif TOOLKIT == "kivy":
        t = "kivy"
    d = MfxMessageDialog(
        app.top, title=_("Credits"), timeout=timeout,
        text=_('''%(app)s credits go to:

Volker Weidner for getting me into Solitaire
Guido van Rossum for the initial example program
T. Kirk for lots of contributed games and cardsets
Carl Larsson for the background music
The Gnome AisleRiot team for parts of the documentation
Natascha

The Python, %(gui_library)s, SDL & Linux crews
for making this program possible''') % {'app': TITLE, 'gui_library': t},
        image=app.gimages.logos[3], image_side="right",
        separator=True)
    return d.status


# ************************************************************************
# *
# ************************************************************************

help_html_viewer = None
help_html_index = None


def help_html(app, document, dir_, top=None):
    global help_html_viewer, help_html_index
    if not document:
        return None
    if top is None:
        top = app.top
    try:
        doc = app.dataloader.findFile(document, dir_)
        if help_html_index is None:
            document, dir_ = "index.html", "html"
            help_html_index = app.dataloader.findFile(document, dir_)
    except EnvironmentError:
        MfxMessageDialog(app.top, title=_("%s HTML Problem") % TITLE,
                         text=_("Cannot find help document\n%s") % document,
                         bitmap="warning")
        return None
    # print doc, help_html_index
    try:
        viewer = help_html_viewer
        # if viewer.parent.winfo_parent() != top._w:
        #    viewer.destroy()
        #    viewer = None
        viewer.updateHistoryXYView()
        viewer.display(doc, relpath=0)
    except Exception:
        # traceback.print_exc()
        top = make_help_toplevel(app, title=_("%s Help") % TITLE)

        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        h = int(sh * .8)
        w = min(650, int(sw * .8))
        if TOOLKIT == "tk":
            th = int(top.winfo_rooty() - top.winfo_y())
            top.wm_minsize(w, min(200, h))
            top.geometry("%dx%d+%d+%d" % (w, h, (sw - w) / 2,
                                          ((sh - h) / 2) - th))

        viewer = HTMLViewer(top, app, help_html_index)
        viewer.display(doc)
    # wm_map(top, maximized=maximized)
    viewer.parent.wm_deiconify()
    viewer.parent.tkraise()
    help_html_viewer = viewer
    raise_help_html(app.game)
    return viewer


def raise_help_html(game):
    try:
        if game.app.opt.topmost_dialogs:
            help_html_viewer.parent.tkraise()
            help_html_viewer.parent.attributes("-topmost", True)
        else:
            help_html_viewer.parent.attributes("-topmost", False)
    except Exception:
        pass


def unraise_help_html():
    try:
        help_html_viewer.parent.attributes("-topmost", False)
    except Exception:
        pass


def destroy_help_html():
    try:
        help_html_viewer.destroy()
    except Exception:
        pass
