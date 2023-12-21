#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------#
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
# ---------------------------------------------------------------------------#
# imports
# import os
# import time

# Kivy
# from LApp import *
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.uix.label import Label
from kivy.uix.widget import Widget

# PySol imports
# Toolkit imports
# from pysollib.mfxutil import format_time
# from pysollib.mfxutil import kwdefault, KwStruct
# from pysollib.mygettext import _, n_
# from pysollib.pysoltk import MfxScrolledCanvas
# from pysollib.stats import PysolStatsFormatter, ProgressionFormatter
# from pysollib.util import *
# from tkutil import bind, unbind_destroy, loadImage
from pysollib.kivy.LImage import LImage
from pysollib.mfxutil import KwStruct
from pysollib.mygettext import _
from pysollib.pysoltk import MfxDialog, MfxMessageDialog
from pysollib.settings import TOP_TITLE

# FIXME - this file a quick hack and needs a rewrite

# Note almoust not used in the kivy implementation. Only a simple text
# is displayed, for single user Statisics. The code from tk implementation was
# kept as an examlple what could eventually be done once ....

# ************************************************************************
# *
# ************************************************************************


class LPieChart(Widget):
    def __init__(self, prnt, args, **kw):
        super(LPieChart, self).__init__(**kw)
        self.prnt = prnt

        # print('width   %s' % kw['width'])
        # print('outline %s' % kw['outline'])
        # print('fill    %s' % kw['fill'])

        # width = 10.0
        # if ('width' in kw):
        #     width = float(kw['width'])

        bcolor = '#ffa000a0'
        if ('outline') in kw:
            bcolor = kw['outline']
        if (not bcolor or len(bcolor) < 7):
            bcolor = '#ffa000a0'

        fcolor = '#00aaff20'
        if ('fill') in kw:
            fcolor = kw['fill']
        if (not fcolor or len(fcolor) < 7):
            fcolor = '#00aaff20'

        self.group = None
        if 'group' in kw:
            self.group = kw['group']

        self.center = (0.0, 0.0)
        if ('center') in kw:
            self.center = kw['center']

        self.radius = (0.0, 0.0)
        if ('radius') in kw:
            self.radius = kw['radius']

        self.fcolor = (0.9, 0.1, 0.3, 0.5)
        self.bind(size=self.updateCanvas)
        self.bind(pos=self.updateCanvas)

    def updateCanvas(self, instance, value):

        self.canvas.clear()
        with self.canvas:
            Color(self.fcolor[0], self.fcolor[1],
                  self.fcolor[2], self.fcolor[3])

            center = (self.pos[0] + self.size[0] / 2.0,
                      self.pos[1] + self.size[1] / 2.0)
            radius = (self.size[0] * 0.45)
            radius2 = (self.size[1] * 0.45)
            if (radius > radius2):
                radius = radius2

            # Rectangle(pos=pos, size=size)
            Line(circle=(center[0], center[1], radius), width=2.0, close=True)

            # kreis kann nicht gefüllt werden !!! - man sollte eine Funktion
            # haben die einen geschlossenen pfad füllt.
            # TBD.vertices/Mesh. versuchen, kreis annähern.

            # Color(self.bcolor[0], self.bcolor[1],
            #    self.bcolor[2], self.bcolor[3])
            # Line(points=poly, width=border)


# ************************************************************************
# *
# ************************************************************************


class SingleGame_StatsDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):
        self.app = app
        self.selected_game = None
        kw = self.initKw(kw)
        print('SingleGame_StatsDialog: p=%s, g=%s, kw=%s' %
              (player, gameid, kw))
        if isinstance(kw, KwStruct):
            print('kw=%s' % kw.getKw())

        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.top_frame = top_frame
        #
        self.player = player or _("Demo games")
        self.top.wm_minsize(200, 200)
        self.button = kw.default
        #
        # createChart = self.create3DBarChart
        # createChart = self.createPieChart
        # createChart = self.createSimpleChart
        #         if parent.winfo_screenwidth() < 800
        #            or parent.winfo_screenheight() < 600:
        #             createChart = self.createPieChart
        #             createChart = self.createSimpleChart
        #
        self.font = self.app.getFont("default")
#        self.tk_font = tkFont.Font(self.top, self.font)
#        self.font_metrics = self.tk_font.metrics()
        self._calc_tabs()

        if (kw.image):
            image = LImage(texture=kw.image.texture, size_hint=(1, 1))
            self.top.add_widget(image)

        #
        won, lost = app.stats.getStats(player, gameid)
        pwon, plost = self._getPwon(won, lost)

        print('Stats(p): won=%s, lost=%s' % (won, lost))

        text1 = _('Total:\n' +
                  '   won: %(won)s ... %(percentwon)s%%\n' +
                  '   lost: %(lost)s ... %(percentlost)s%%\n\n') % dict(
            won=won, percentwon=int(round(100.0 * pwon)),
            lost=lost, percentlost=int(round(100.0 * plost)))

#        createChart(app, won, lost, _("Total"))
        won, lost = app.stats.getSessionStats(player, gameid)
        pwon, plost = self._getPwon(won, lost)

        print('Stats(s): won=%s, lost=%s' % (won, lost))

        text2 = _('Current Session:\n' +
                  '   won: %(won)s ... %(percentwon)s%%\n' +
                  '   lost: %(lost)s ... %(percentlost)s%%\n') % dict(
            won=won, percentwon=(round(100.0 * pwon)),
            lost=lost, percentlost=int(round(100.0 * plost)))
        # text2 = 'Current Session:\n   won=%s, lost=%s\n' % (won, lost)

#        createChart(app, won, lost, _("Current session"))

        self.top.add_widget(Label(text=text1 + text2))

        # self.top.add_widget(Button(text='reset', size_hint=(1, 0.15)))
        #
#        focus = self.createButtons(bottom_frame, kw)
#        self.mainloop(focus, kw.timeout)

    #
    # helpers
    #

    def _calc_tabs(self):
        return

    def _getPwon(self, won, lost):
        pwon, plost = 0.0, 0.0
        if won + lost > 0:
            pwon = float(won) / float(won + lost)
            pwon = min(max(pwon, 0.00001), 0.99999)
            plost = 1.0 - float(pwon)
        return pwon, plost

    def _createChartTexts(self, tx, ty, won, lost):
        c, tfont, fg = self.canvas, self.font, self.fg
        pwon, plost = self._getPwon(won, lost)
        #
        x = tx[0]
        dy = int(self.font_metrics['ascent']) - 10
        dy = dy / 2
        c.create_text(x, ty[0] - dy, text=_("Won:"),
                      anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[1] - dy, text=_("Lost:"),
                      anchor="nw", font=tfont, fill=fg)
        c.create_text(x, ty[2] - dy, text=_("Total:"),
                      anchor="nw", font=tfont, fill=fg)
        x = tx[1] - 16
        c.create_text(x, ty[0] - dy, text="%d" %
                      won, anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[1] - dy, text="%d" %
                      lost, anchor="ne", font=tfont, fill=fg)
        c.create_text(x, ty[2] - dy, text="%d" %
                      (won + lost), anchor="ne", font=tfont, fill=fg)
        y = ty[2] - 11
        c.create_line(tx[0], y, x, y, fill=fg)
        if won + lost > 0:
            x = tx[2]
            pw = int(round(100.0 * pwon))
            c.create_text(x, ty[0] - dy, text="%d%%" %
                          pw, anchor="ne", font=tfont, fill=fg)
            c.create_text(x, ty[1] - dy, text="%d%%" %
                          (100 - pw), anchor="ne", font=tfont, fill=fg)

    #
    # charts
    #

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"),
                               (_("&All games..."), 102),
                               (TOP_TITLE + "...", 105),
                               (_("&Reset..."), 302)), default=0,
                      image=self.app.gimages.logos[5],
                      padx=10, pady=10,
                      )
        return MfxDialog.initKw(self, kw)

# ************************************************************************
# *
# ************************************************************************


class AllGames_StatsDialog(MfxDialog):

    YVIEW = 0
    FONT_TYPE = "default"

    def __init__(self, parent, title, app, player, **kw):
        self.status = 0
        print('AllGames_StatsDialog')
        pass

# ************************************************************************
# *
# ************************************************************************


class FullLog_StatsDialog(AllGames_StatsDialog):
    pass


class SessionLog_StatsDialog(FullLog_StatsDialog):
    pass

# ************************************************************************
# *
# ************************************************************************


class Status_StatsDialog(MfxMessageDialog):
    def __init__(self, parent, game):
        self.status = 0
        pass

# ************************************************************************
# *
# ************************************************************************


class Top_StatsDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):
        pass

# ************************************************************************
# *
# ************************************************************************


class ProgressionDialog(MfxDialog):
    def __init__(self, parent, title, app, player, gameid, **kw):
        pass
