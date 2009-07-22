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


# imports

# PySol imports
from settings import TITLE, PACKAGE_URL, TOOLKIT, VERSION
from pysoltk import make_help_toplevel
from pysoltk import MfxMessageDialog
from pysoltk import PysolAboutDialog
from pysoltk import HTMLViewer


# ************************************************************************
# *
# ************************************************************************

def help_about(app, timeout=0, sound=True):
    if sound:
        app.audio.playSample("about")
    t = _("A Python Solitaire Game Collection\n")
    if app.miscrandom.random() < 0.8:
        t = _("A World Domination Project\n")
    strings=(_("&Nice"), _("&Credits..."))
    if timeout:
        strings=(_("&Enjoy"),)
    version = _("Version %s") % VERSION
    d = PysolAboutDialog(app, app.top, title=_("About ") + TITLE,
                         timeout=timeout,
                         text=_('''PySol Fan Club edition
%s%s

Copyright (C) 1998 - 2003 Markus F.X.J. Oberhumer.
Copyright (C) 2003 Mt. Hood Playing Card Co.
Copyright (C) 2005 - 2009 Skomoroh.
All Rights Reserved.

PySol is free software distributed under the terms
of the GNU General Public License.

For more information about this application visit''') % (t, version),
                         url=PACKAGE_URL,
                         image=app.gimages.logos[2],
                         strings=strings, default=0,
                         separator=True)
    if d.status == 0 and d.button == 1:
        help_credits(app, sound=sound)
    return d.status


def help_credits(app, timeout=0, sound=True):
    if sound:
        app.audio.playSample("credits")
    t = ""
    if   TOOLKIT == "tk" : t = "Tcl/Tk"
    elif TOOLKIT == "gtk": t = "PyGTK"
    elif TOOLKIT == "kde": t = "pyKDE"
    elif TOOLKIT == "wx" : t = "wxPython"
    d = MfxMessageDialog(app.top, title=_("Credits"), timeout=timeout,
                         text=TITLE+_(''' credits go to:

Volker Weidner for getting me into Solitaire
Guido van Rossum for the initial example program
T. Kirk for lots of contributed games and cardsets
Carl Larsson for the background music
The Gnome AisleRiot team for parts of the documentation
Natascha

The Python, %s, SDL & Linux crews
for making this program possible''') % t,
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
        d = MfxMessageDialog(app.top, title=TITLE + _(" HTML Problem"),
                             text=_("Cannot find help document\n") + document,
                             bitmap="warning")
        return None
    ##print doc, help_html_index
    try:
        viewer = help_html_viewer
        #if viewer.parent.winfo_parent() != top._w:
        #    viewer.destroy()
        #    viewer = None
        viewer.updateHistoryXYView()
        viewer.display(doc, relpath=0)
    except:
        ##traceback.print_exc()
        top = make_help_toplevel(app, title=TITLE+_(" Help"))
        if top.winfo_screenwidth() < 800 or top.winfo_screenheight() < 600:
            #maximized = 1
            top.wm_minsize(300, 150)
        else:
            #maximized = 0
            top.wm_minsize(400, 200)
        viewer = HTMLViewer(top, app, help_html_index)
        viewer.display(doc)
    #wm_map(top, maximized=maximized)
    viewer.parent.wm_deiconify()
    viewer.parent.tkraise()
    help_html_viewer = viewer
    return viewer

def destroy_help_html():
    try:
        help_html_viewer.destroy()
    except:
        pass

