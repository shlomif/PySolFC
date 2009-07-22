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

__all__ = ['FontsDialog']

# imports
import Tkinter
import ttk
import tkFont

# PySol imports
from pysollib.mfxutil import KwStruct

# Toolkit imports
from tkwidget import MfxDialog
from tkutil import bind
from tkwidget import PysolScale


# ************************************************************************
# *
# ************************************************************************

class FontChooserDialog(MfxDialog):
    def __init__(self, parent, title, init_font, **kw):
        ##print init_font
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        self.font_family = 'Helvetica'
        self.font_size =  12
        self.font_weight = 'normal'
        self.font_slant = 'roman'

        if init_font is not None:
            assert 2 <= len(init_font) <= 4
            assert isinstance(init_font[1], int)
            self.font_family, self.font_size = init_font[:2]
            if len(init_font) > 2:
                if init_font[2] in ['bold', 'normal']:
                    self.font_weight = init_font[2]
                elif init_font[2] in ['italic', 'roman']:
                    self.font_slant = init_font[2]
                else:
                    raise ValueError('invalid font style: '+init_font[2])
                if len(init_font) > 3:
                    if init_font[3] in ['bold', 'normal']:
                        self.font_weight = init_font[3]
                    elif init_font[2] in ['italic', 'roman']:
                        self.font_slant = init_font[3]
                    else:
                        raise ValueError('invalid font style: '+init_font[3])

        #self.family_var = Tkinter.StringVar()
        self.weight_var = Tkinter.BooleanVar()
        self.weight_var.set(self.font_weight == 'bold')
        self.slant_var = Tkinter.BooleanVar()
        self.slant_var.set(self.font_slant == 'italic')
        self.size_var = Tkinter.IntVar()
        self.size_var.set(self.font_size)
        #
        frame = ttk.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        frame.columnconfigure(0, weight=1)
        #frame.rowconfigure(1, weight=1)
        self.entry = ttk.Entry(frame)
        self.entry.grid(row=0, column=0, columnspan=2, sticky='news')
        self.entry.insert('end', _('abcdefghABCDEFGH'))
        self.list_box = Tkinter.Listbox(frame, width=36, exportselection=False)
        sb = ttk.Scrollbar(frame)
        self.list_box.configure(yscrollcommand=sb.set)
        sb.configure(command=self.list_box.yview)
        self.list_box.grid(row=1, column=0, sticky='news') # rowspan=4
        sb.grid(row=1, column=1, sticky='ns')
        bind(self.list_box, '<<ListboxSelect>>', self.fontupdate)
        ##self.list_box.focus()
        cb1 = ttk.Checkbutton(frame, text=_('Bold'),
                              command=self.fontupdate,
                              variable=self.weight_var)
        cb1.grid(row=2, column=0, columnspan=2, sticky='we')
        cb2 = ttk.Checkbutton(frame, text=_('Italic'),
                              command=self.fontupdate,
                              variable=self.slant_var)
        cb2.grid(row=3, column=0, columnspan=2, sticky='we')

        sc = PysolScale(frame, from_=6, to=40, resolution=1,
                        label=_('Size:'), orient='horizontal',
                        command=self.fontupdate, variable=self.size_var)
        sc.grid(row=4, column=0, columnspan=2, sticky='news')
        #
        font_families = list(tkFont.families())
        font_families.sort()
        selected = -1
        n = 0
        self.list_box.insert('end', *font_families)
        for font in font_families:
            if font.lower() == self.font_family.lower():
                selected = n
                break
            n += 1
        if selected >= 0:
            self.list_box.select_set(selected)
            self.list_box.see(selected)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

        self.font = (self.font_family, self.font_size,
                     self.font_slant, self.font_weight)

    def fontupdate(self, *args):
        if self.list_box.curselection():
            self.font_family = self.list_box.get(self.list_box.curselection())
        self.font_weight = self.weight_var.get() and 'bold' or 'normal'
        self.font_slant = self.slant_var.get() and 'italic' or 'roman'
        self.font_size = self.size_var.get()
        self.entry.configure(font=(self.font_family, self.font_size,
                                   self.font_slant, self.font_weight))

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")),
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)

# ************************************************************************
# *
# ************************************************************************

class FontsDialog(MfxDialog):
    def __init__(self, parent, title, app, **kw):
        kw = self.initKw(kw)
        MfxDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)

        frame = ttk.Frame(top_frame)
        frame.pack(expand=True, fill='both', padx=5, pady=10)
        frame.columnconfigure(0, weight=1)

        self.fonts = {}
        row = 0
        for fn, title in (##('default',        _('Default')),
                          ('sans',           _('HTML: ')),
                          ('small',          _('Small: ')),
                          ('fixed',          _('Fixed: ')),
                          ('canvas_default', _('Tableau default: ')),
                          ('canvas_fixed',   _('Tableau fixed: ')),
                          ('canvas_large',   _('Tableau large: ')),
                          ('canvas_small',   _('Tableau small: ')),
                          ):
            font = app.opt.fonts[fn]
            self.fonts[fn] = font
            ttk.Label(frame, text=title, anchor='w'
                      ).grid(row=row, column=0, sticky='we')
            if font:
                title = ' '.join([str(i) for i in font if i not in ('roman', 'normal')])
            elif font is None:
                title = 'Default'
            l = ttk.Label(frame, font=font, text=title)
            l.grid(row=row, column=1, padx=8)
            b = ttk.Button(frame, text=_('Change...'), width=10,
                           command=lambda l=l, fn=fn: self.selectFont(l, fn))
            b.grid(row=row, column=2)
            row += 1
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)


    def selectFont(self, label, fn):
        d = FontChooserDialog(self.top, _('Select font'), self.fonts[fn])
        if d.status == 0 and d.button == 0:
            self.fonts[fn] = d.font
            title = ' '.join([str(i) for i in d.font if i not in ('roman', 'normal')])
            label.configure(font=d.font, text=title)


    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_('&OK'), _('&Cancel')),
                      default=0,
                      )
        return MfxDialog.initKw(self, kw)




