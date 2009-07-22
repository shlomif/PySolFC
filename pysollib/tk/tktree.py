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
import os
import Tkinter

# Toolkit imports
from tkutil import bind
from tkwidget import MfxScrolledCanvas


# ************************************************************************
# *
# ************************************************************************

class MfxTreeBaseNode:
    def __init__(self, tree, parent_node, text, key):
        self.tree = tree
        self.parent_node = parent_node
        self.text = text
        self.key = key
        # state
        self.selected = 0
        self.subnodes = None
        # canvas item ids
        self.symbol_id = None
        self.text_id = None
        self.textrect_id = None

    def registerKey(self):
        if self.key is not None:
            l = self.tree.keys.get(self.key, [])
            l.append(self)
            self.tree.keys[self.key] = l

    def whoami(self):
        if self.parent_node is None:
            return (self.text, )
        else:
            return self.parent_node.whoami() + (self.text, )

    def draw(self, x, y, lastx=None, lasty=None):
        canvas, style = self.tree.canvas, self.tree.style
        topleftx = x + style.distx
        toplefty = y - style.height / 2 #+++
        # draw the horizontal line
        if lastx is not None:
            canvas.create_line(x, y, topleftx, y, stipple=style.linestyle, fill=style.linecolor)
        # draw myself - ugly, ugly...
        self.selected = 0
        self.symbol_id = -1
        self.drawSymbol(topleftx, toplefty)
        linestart = style.distx + style.width + 5
        self.text_id = -1
        self.drawText(x + linestart, y)
        return x, y, x, y + style.disty

    #
    #
    #

    def drawText(self, x, y):
        canvas, style = self.tree.canvas, self.tree.style
        if self.selected:
            fg, bg = style.text_selected_fg, style.text_selected_bg
        else:
            fg, bg = style.text_normal_fg, style.text_normal_bg
        #
        if self.tree.nodes.get(self.text_id) is self:
            canvas.itemconfig(self.text_id, fill=fg)
        else:
            # note: I don't use Label + canvas.create_window here
            #   because it doesn't propagate events to the canvas
            #   and has some other re-display annoyances
            ##print 'style.font:', style.font
            self.text_id = canvas.create_text(x+1, y, text=self.text,
                                              anchor="w", justify="left",
                                              font=style.font,
                                              fill=fg)
            self.tree.nodes[self.text_id] = self
        #
        if self.tree.nodes.get(self.textrect_id) is self:
            try:
                # _tkinter.TclError: unknown option "-fill" ???
                canvas.itemconfig(self.textrect_id, fill=bg)
            except Tkinter.TclError:
                pass
        elif self.selected:
            b = canvas.bbox(self.text_id)
            self.textrect_id = canvas.create_rectangle(b[0]-1, b[1]-1, b[2]+1, b[3]+1,
                                                       fill=bg, outline="")
            canvas.tag_lower(self.textrect_id, self.text_id)
            self.tree.nodes[self.textrect_id] = self

    def updateText(self):
        if self.tree.nodes.get(self.text_id) is self:
            self.drawText(-1, -1)

    #
    #
    #

    def drawSymbol(self, x, y, **kw):
        canvas, style = self.tree.canvas, self.tree.style
        color = kw.get("color")
        if color is None:
            if self.selected:
                color = "darkgreen"
            else:
                color = "green"
        # note: rectangle outline is one pixel
        if self.tree.nodes.get(self.symbol_id) is self:
            canvas.itemconfig(self.symbol_id, fill=color)
        else:
            self.symbol_id = canvas.create_rectangle(
                x+1, y+1, x + style.width, y + style.height, fill=color)
            self.tree.nodes[self.symbol_id] = self

    def updateSymbol(self):
        if self.tree.nodes.get(self.symbol_id) is self:
            self.drawSymbol(-1, -1)


# ************************************************************************
# * Terminal and non-terminal nodes
# ************************************************************************

class MfxTreeLeaf(MfxTreeBaseNode):
    def drawText(self, x, y):
        if self.text_id < 0:
            self.registerKey()
        MfxTreeBaseNode.drawText(self, x, y)


class MfxTreeNode(MfxTreeBaseNode):
    def __init__(self, tree, parent_node, text, key, expanded=0):
        MfxTreeBaseNode.__init__(self, tree, parent_node, text, key)
        self.expanded = expanded

    def drawChildren(self, x, y, lastx, lasty):
        # get subnodes
        self.subnodes = self.tree.getContents(self)
        # draw subnodes
        lx, ly = lastx, lasty
        nx, ny = x, y
        for node in self.subnodes:
            # update tree
            node.tree = self.tree
            # draw node
            lx, ly, nx, ny = node.draw(nx, ny, lx, ly)
        # draw the vertical line
        if self.subnodes:
            style = self.tree.style
            dy = (style.disty-style.width)/2
            y = y-style.disty/2-dy
            self.tree.canvas.create_line(x, y, nx, ly,
                                         stipple=style.linestyle,
                                         fill=style.linecolor)
        return ny


    def draw(self, x, y, ilastx=None, ilasty=None):
        # draw myself
        lx, ly, nx, ny = MfxTreeBaseNode.draw(self, x, y, ilastx, ilasty)
        if self.expanded:
            style = self.tree.style
            childx = nx + style.distx + style.width / 2
            childy = ny
            clastx = nx + style.distx + style.width / 2
            clasty = ly + style.height /2
            ny = self.drawChildren(childx, childy, clastx, clasty)
        return lx, ly, x, ny

    #
    #
    #

    def drawSymbol(self, x, y, **kw):
        color = kw.get("color")
        if color is None:
            if self.expanded:
                color = "red"
            else:
                color = "pink"
        MfxTreeBaseNode.drawSymbol(self, x, y, color=color)


# ************************************************************************
# *
# ************************************************************************

class MfxTreeInCanvas(MfxScrolledCanvas):
    class Style:
        def __init__(self):
            self.distx = 16
            self.disty = 18
            self.width = 16         # width of symbol
            self.height = 16        # height of symbol
            self.originx = 0
            self.originy = 0
            self.text_normal_fg = "black"
            self.text_normal_bg = "white"
            self.text_selected_fg = "white"
            self.text_selected_bg = "#00008b"       # "darkblue"
            self.font = None
            self.linestyle = "gray50"
            self.linecolor = "black"

    def __init__(self, parent, rootnodes, **kw):
        bg = kw["bg"] = kw.get("bg") or parent.cget("bg")
        kw['bd'] = 0
        MfxScrolledCanvas.__init__(self, parent, **kw)
        #
        self.rootnodes = rootnodes
        self.updateNodesWithTree(self.rootnodes, self)
        self.selection_key = None
        self.nodes = {}
        self.keys = {}
        #
        self.style = self.Style()
        ##self.style.text_normal_fg = self.canvas.cget("insertbackground")
        self.style.text_normal_fg = self.canvas.option_get('foreground', '') or self.canvas.cget("insertbackground")
        self.style.text_normal_bg = bg
        #
        bind(self.canvas, "<ButtonPress-1>", self.singleClick)
        bind(self.canvas, "<Double-Button-1>", self.doubleClick)
        ##bind(self.canvas, "<ButtonRelease-1>", xxx)
        self.pack(fill='both', expand=True)

    def destroy(self):
        for node in self.keys.get(self.selection_key, []):
            node.selected = 0
        MfxScrolledCanvas.destroy(self)

    def findNode(self, event=None):
        id = self.canvas.find_withtag('current')
        if id:
            return self.nodes.get(id[0])
        return None

    #
    # draw nodes
    #

    def draw(self):
        nx, ny = self.style.originx, self.style.originy
        # Account for initial offsets, see topleft[xy] in BaseNode.draw().
        # We do this so that our bounding box always starts at (0,0)
        # and the yscrollincrement works nicely.
        nx = nx - self.style.distx
        ny = ny + self.style.height / 2
        for node in self.rootnodes:
            # update tree
            node.tree = self
            # draw
            try:
                lx, ly, nx, ny = node.draw(nx, ny, None, None)
            except Tkinter.TclError:
                # FIXME: Tk bug ???
                raise
        # set scroll region
        bbox = self.canvas.bbox("all")
        ##self.canvas.config(scrollregion=bbox)
        self.canvas.config(scrollregion=(0,0,bbox[2],bbox[3]))
        self.canvas.config(yscrollincrement=self.style.disty)

    def clear(self):
        self.nodes = {}
        self.keys = {}
        self.canvas.delete("all")

    def redraw(self):
        oldcur = self.canvas["cursor"]
        self.canvas["cursor"] = "watch"
        self.canvas.update_idletasks()
        self.clear()
        self.draw()
        self.updateSelection(self.selection_key)
        self.canvas["cursor"] = oldcur

    #
    #
    #

    def getContents(self, node):
        # Overload this, supposed to return a list of subnodes of node.
        pass

    def singleClick(self, event=None):
        # Overload this if you want to know when a node is clicked on.
        pass

    def doubleClick(self, event=None):
        # Overload this if you want to know when a node is d-clicked on.
        self.singleClick(event)

    #
    #
    #

    def updateSelection(self, key):
        l1 = self.keys.get(self.selection_key, [])
        l2 = self.keys.get(key, [])
        for node in l1:
            if node.selected and node not in l2:
                node.selected = 0
                node.updateSymbol()
                node.updateText()
        for node in l2:
            if not node.selected:
                node.selected = 1
                node.updateSymbol()
                node.updateText()
        self.selection_key = key

    def updateNodesWithTree(self, nodes, tree):
        for node in nodes:
            node.tree = tree
            if node.subnodes:
                self.updateNodesWithTree(node.subnodes, tree)


# ************************************************************************
# *
# ************************************************************************


class DirectoryBrowser(MfxTreeInCanvas):
    def __init__(self, parent, dirs):
        nodes = []
        if isinstance(dirs, str):
            dirs = (dirs,)
        for dir in dirs:
            self.addNode(nodes, None, dir, dir)
        # note: best results if height is a multiple of style.disty
        MfxTreeInCanvas.__init__(self, parent, nodes, height=25*18)
        self.draw()

    def addNode(self, list, node, filename, text):
        try:
            if os.path.isdir(filename):
                list.append(MfxTreeNode(self, node, text, key=filename))
            else:
                list.append(MfxTreeLeaf(self, node, text, key=filename))
        except EnvironmentError:
            pass

    def getContents(self, node):
        # use cached values
        if node.subnodes is not None:
            return node.subnodes
        #
        dir = node.key
        print "Getting %s" % dir
        try:
            filenames = os.listdir(dir)
            filenames.sort()
        except EnvironmentError:
            return ()
        contents = []
        for filename in filenames:
            self.addNode(contents, node, os.path.join(dir, filename), filename)
        ##print "gotten"
        return contents

    def singleClick(self, event=None):
        node = self.findNode(event)
        if not node:
            return
        print "Clicked node %s %s" % (node.text, node.key)
        if isinstance(node, MfxTreeLeaf):
            self.updateSelection(key=node.key)
        elif isinstance(node, MfxTreeNode):
            node.expanded = not node.expanded
            self.redraw()
        return "break"


if __name__ == "__main__":
    tk = Tkinter.Tk()
    if os.name == "nt":
        app = DirectoryBrowser(tk, ("c:\\", "c:\\windows"))
    else:
        app = DirectoryBrowser(tk, ("/", "/home"))
    tk.mainloop()


