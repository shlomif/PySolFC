#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------
"""
a couple of classes for implementing partial tabbed-page like behaviour
"""

import tkinter

MYRIDGE, MYRAISED = tkinter.RAISED, tkinter.RIDGE
# MYRIDGE, MYRAISED = tkinter.RIDGE, tkinter.RAISED


class InvalidTabPage(Exception):
    pass


class AlreadyExists(Exception):
    pass


class PageTab(tkinter.Frame):
    """
    a 'page tab' like framed button
    """
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent, borderwidth=2, relief=MYRIDGE)
        self.button = tkinter.Radiobutton(
            self, padx=5, pady=5, takefocus=0,
            indicatoron=tkinter.FALSE, highlightthickness=0,
            borderwidth=0, selectcolor=self.cget('bg'))
        self.button.pack()


class TabPageSet(tkinter.Frame):
    """
    a set of 'pages' with TabButtons for controlling their display
    """
    def __init__(self, parent, pageNames=[], **kw):
        """
        pageNames - a list of strings, each string will be the dictionary key
        to a page's data, and the name displayed on the page's tab. Should be
        specified in desired page order. The first page will be the default
        and first active page.
        """
        tkinter.Frame.__init__(self, parent, kw)
        self.grid_location(0, 0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.tabBar = tkinter.Frame(self)
        self.tabBar.grid(row=0, column=0, sticky=tkinter.EW)
        self.activePage = tkinter.StringVar(self)
        self.defaultPage = ''
        self.pages = {}
        for name in pageNames:
            self.AddPage(name)

    def ChangePage(self, pageName=None):
        if pageName:
            if pageName in self.pages.keys():
                self.activePage.set(pageName)
            else:
                raise InvalidTabPage('Invalid TabPage Name')
        # pop up the active 'tab' only
        for page in self.pages.keys():
            self.pages[page]['tab'].config(relief=MYRIDGE)
        self.pages[self.GetActivePage()]['tab'].config(relief=MYRAISED)
        # switch page
        self.pages[self.GetActivePage()]['page'].lift()

    def GetActivePage(self):
        return self.activePage.get()

    def AddPage(self, pageName):
        if pageName in self.pages.keys():
            raise AlreadyExists('TabPage Name Already Exists')
        self.pages[pageName] = {
            'tab': PageTab(self.tabBar),
            'page': tkinter.Frame(self, borderwidth=2, relief=tkinter.RAISED)
            }
        self.pages[pageName]['tab'].button.config(
            text=pageName,
            command=self.ChangePage,
            variable=self.activePage,
            value=pageName
            )
        self.pages[pageName]['tab'].pack(side=tkinter.LEFT)
        self.pages[pageName]['page'].grid(row=1, column=0, sticky=tkinter.NSEW)
        if len(self.pages) == 1:  # adding first page
            self.defaultPage = pageName
            self.activePage.set(self.defaultPage)
            self.ChangePage()

    def RemovePage(self, pageName):
        if pageName not in self.pages.keys():
            raise InvalidTabPage('Invalid TabPage Name')
        self.pages[pageName]['tab'].pack_forget()
        self.pages[pageName]['page'].grid_forget()
        self.pages[pageName]['tab'].destroy()
        self.pages[pageName]['page'].destroy()
        del (self.pages[pageName])
        # handle removing last remaining, or default, or active page
        if not self.pages:  # removed last remaining page
            self.defaultPage = ''
            return
        if pageName == self.defaultPage:  # set a new default page
            self.defaultPage = \
                self.tabBar.winfo_children()[0].button.cget('text')
        if pageName == self.GetActivePage():  # set a new active page
            self.activePage.set(self.defaultPage)
        self.ChangePage()


if __name__ == '__main__':
    # test dialog
    root = tkinter.Tk()
    tabPage = TabPageSet(root, pageNames=['Foobar', 'Baz'])
    tabPage.pack(expand=tkinter.TRUE, fill=tkinter.BOTH)
    tkinter.Label(tabPage.pages['Foobar']['page'], text='Foo', pady=20).pack()
    tkinter.Label(tabPage.pages['Foobar']['page'], text='Bar', pady=20).pack()
    tkinter.Label(tabPage.pages['Baz']['page'], text='Baz').pack()
    entryPgName = tkinter.Entry(root)
    buttonAdd = tkinter.Button(
        root, text='Add Page',
        command=lambda: tabPage.AddPage(entryPgName.get()))
    buttonRemove = tkinter.Button(
        root, text='Remove Page',
        command=lambda: tabPage.RemovePage(entryPgName.get()))
    labelPgName = tkinter.Label(root, text='name of page to add/remove:')
    buttonAdd.pack(padx=5, pady=5)
    buttonRemove.pack(padx=5, pady=5)
    labelPgName.pack(padx=5)
    entryPgName.pack(padx=5)
    tabPage.ChangePage()
    root.mainloop()
