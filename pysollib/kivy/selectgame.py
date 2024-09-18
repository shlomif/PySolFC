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

from collections import UserList

from kivy.clock import Clock

from pysollib.gamedb import GI
from pysollib.kivy.LApp import LScrollView
from pysollib.kivy.LApp import LTopLevel
from pysollib.kivy.LApp import LTreeNode
from pysollib.kivy.LApp import LTreeRoot
from pysollib.kivy.LApp import get_menu_size_hint
from pysollib.kivy.selecttree import SelectDialogTreeData
from pysollib.kivy.selecttree import SelectDialogTreeLeaf, SelectDialogTreeNode
from pysollib.mygettext import _


# ************************************************************************
# * Nodes
# ************************************************************************


class SelectGameLeaf(SelectDialogTreeLeaf):
    def getContents(self):
        return None


class SelectGameNode(SelectDialogTreeNode):
    def _getContents(self):
        contents = []
        if isinstance(self.select_func, UserList):
            # key/value pairs
            for id, name in self.select_func:
                if id and name:
                    node = SelectGameLeaf(self.tree, self, name, key=id)
                    contents.append(node)
        else:
            for gi in self.tree.all_games_gi:
                if gi and self.select_func is None:
                    # All games
                    # name = '%s (%s)' % (gi.name, CSI.TYPE_NAME[gi.category])
                    name = gi.name
                    node = SelectGameLeaf(self.tree, self, name, key=gi.id)
                    contents.append(node)
                elif gi and self.select_func(gi):
                    name = gi.name
                    node = SelectGameLeaf(self.tree, self, name, key=gi.id)
                    contents.append(node)
        return contents or self.tree.no_games


# ************************************************************************
# * Tree database
# ************************************************************************

class SelectGameData(SelectDialogTreeData):
    def __init__(self, app):
        SelectDialogTreeData.__init__(self)

        # originale.
        self.all_games_gi = list(
            map(app.gdb.get, app.gdb.getGamesIdSortedByName()))
        self.no_games = [SelectGameLeaf(None, None, _("(no games)"), None), ]
        #
        s_by_type = s_oriental = s_special = None
        s_original = s_contrib = s_mahjongg = None
        g = []
        for data in (GI.SELECT_GAME_BY_TYPE,
                     GI.SELECT_ORIENTAL_GAME_BY_TYPE,
                     GI.SELECT_SPECIAL_GAME_BY_TYPE,
                     GI.SELECT_ORIGINAL_GAME_BY_TYPE,
                     GI.SELECT_CONTRIB_GAME_BY_TYPE,
                     ):
            gg = []
            for name, select_func in data:
                filtered = filter(select_func, self.all_games_gi)
                if name is None or not filtered or len(list(filtered)) == 0:
                    continue
                node = SelectGameNode(None, _(name), select_func)
                if node:
                    gg.append(node)
            g.append(gg)

        def select_mahjongg_game(gi): return gi.si.game_type == GI.GT_MAHJONGG
        gg = None
        if filter(select_mahjongg_game, self.all_games_gi):
            gg = SelectGameNode(None, _("Mahjongg Games"),
                                select_mahjongg_game)
        g.append(gg)
        if g[0]:
            s_by_type = SelectGameNode(None, _("French Games"),
                                       tuple(g[0]), expanded=1)
        if g[1]:
            s_oriental = SelectGameNode(None, _("Oriental Games"),
                                        tuple(g[1]))
        if g[2]:
            s_special = SelectGameNode(None, _("Special Games"),
                                       tuple(g[2]))
        if g[3]:
            s_original = SelectGameNode(None, _("Original Games"),
                                        tuple(g[3]))
#         if g[4]:
#           s_contrib = SelectGameNode(None, "Contributed Games", tuple(g[4]))
        if g[5]:
            s_mahjongg = g[5]
        #
        # all games sorted (in pieces).
        s_all_games, gg = None, []
        agames = self.all_games_gi
        n, d = 0, 17
        i = 0
        while True:
            # columnbreak = i > 0 and (i % d) == 0
            i += 1
            if not agames[n:n + d]:
                break
            m = min(n + d - 1, len(agames) - 1)
            label = agames[n].name[:4] + ' - ' + agames[m].name[:4]
            # print('label = %s' % label)

            ggg = []
            for ag in agames[n:n + d]:
                # print('game, id = %s, %s' % (ag.name, ag.id))
                ggg.append((ag.id, ag.name + ' (' + str(ag.id) + ')'))

            gg.append(SelectGameNode(None, label, UserList(ggg)))
            n += d
        if 1 and gg:
            s_all_games = SelectGameNode(None, _("All Games"), tuple(gg))
        #
        s_by_compatibility, gg = None, []
        for name, games in GI.GAMES_BY_COMPATIBILITY:
            def select_func(gi, games=games):
                return gi.id in games
            if name is None or not list(filter(
                    select_func, self.all_games_gi)):
                continue
            gg.append(SelectGameNode(None, name, select_func))
        if 1 and gg:
            s_by_compatibility = SelectGameNode(None, _("by Compatibility"),
                                                tuple(gg))
            pass
        #
        s_by_pysol_version, gg = None, []
        for name, games in GI.GAMES_BY_PYSOL_VERSION:
            def select_func(gi, games=games):
                return gi.id in games
            if name is None or not list(filter(
                    select_func, self.all_games_gi)):
                continue
            name = _("New games in v. %(version)s") % {'version': name}
            gg.append(SelectGameNode(None, name, select_func))
        if 1 and gg:
            s_by_pysol_version = SelectGameNode(None, _("by PySol version"),
                                                tuple(gg))
        #
        s_by_inventors, gg = None, []
        for name, games in GI.GAMES_BY_INVENTORS:
            def select_func(gi, games=games):
                return gi.id in games
            if name is None or not list(filter(
                    select_func, self.all_games_gi)):
                continue
            gg.append(SelectGameNode(None, name, select_func))
        if 1 and gg:
            s_by_inventors = SelectGameNode(None, _("by Inventors"),
                                            tuple(gg))
        #
        ul_alternate_names = UserList(
            list(app.gdb.getGamesTuplesSortedByAlternateName()))
        #
        self.rootnodes = [_f for _f in (
            # SelectGameNode(None, _("All Games"), None),
            SelectGameNode(None, _("Popular Games"),
                           lambda gi: gi.si.game_flags & GI.GT_POPULAR),
            s_mahjongg,
            s_oriental,
            s_special,
            # SelectGameNode(None, _("Custom Games"),
            #               lambda gi: gi.si.game_type == GI.GT_CUSTOM),
            SelectGameNode(None, _("Alternate Names"), ul_alternate_names),
            s_by_type,
            s_all_games,
            SelectGameNode(None, _('by Skill Level'), (
                SelectGameNode(None, _('Luck only'),
                           lambda gi: gi.skill_level == GI.SL_LUCK),
                SelectGameNode(None, _('Mostly luck'),
                           lambda gi: gi.skill_level == GI.SL_MOSTLY_LUCK),
                SelectGameNode(None, _('Balanced'),
                           lambda gi: gi.skill_level == GI.SL_BALANCED),
                SelectGameNode(None, _('Mostly skill'),
                           lambda gi: gi.skill_level == GI.SL_MOSTLY_SKILL),
                SelectGameNode(None, _('Skill only'),
                           lambda gi: gi.skill_level == GI.SL_SKILL),
            )),
            SelectGameNode(None, _("by Game Feature"), (
                SelectGameNode(None, _("by Number of Cards"), (
                    SelectGameNode(None, _("32 cards"),
                                   lambda gi: gi.si.ncards == 32),
                    SelectGameNode(None, _("48 cards"),
                                   lambda gi: gi.si.ncards == 48),
                    SelectGameNode(None, _("52 cards"),
                                   lambda gi: gi.si.ncards == 52),
                    SelectGameNode(None, _("64 cards"),
                                   lambda gi: gi.si.ncards == 64),
                    SelectGameNode(None, _("78 cards"),
                                   lambda gi: gi.si.ncards == 78),
                    SelectGameNode(None, _("104 cards"),
                                   lambda gi: gi.si.ncards == 104),
                    SelectGameNode(None, _("144 cards"),
                                   lambda gi: gi.si.ncards == 144),
                    SelectGameNode(None, _("Other number"),
                                   lambda gi: gi.si.ncards not in
                                   (32, 48, 52, 64, 78, 104, 144)),
                )),
                SelectGameNode(None, _("by Number of Decks"), (
                    SelectGameNode(None, _("1 deck games"),
                                   lambda gi: gi.si.decks == 1),
                    SelectGameNode(None, _("2 deck games"),
                                   lambda gi: gi.si.decks == 2),
                    SelectGameNode(None, _("3 deck games"),
                                   lambda gi: gi.si.decks == 3),
                    SelectGameNode(None, _("4 deck games"),
                                   lambda gi: gi.si.decks == 4),
                )),
                SelectGameNode(None, _("by Number of Redeals"), (
                    SelectGameNode(None, _("No redeal"),
                               lambda gi: gi.si.redeals == 0),
                    SelectGameNode(None, _("1 redeal"),
                               lambda gi: gi.si.redeals == 1),
                    SelectGameNode(None, _("2 redeals"),
                               lambda gi: gi.si.redeals == 2),
                    SelectGameNode(None, _("3 redeals"),
                               lambda gi: gi.si.redeals == 3),
                    SelectGameNode(None, _("Unlimited redeals"),
                               lambda gi: gi.si.redeals == -1),
                    SelectGameNode(None, _("Variable redeals"),
                               lambda gi: gi.si.redeals == -2),
                    SelectGameNode(None, _("Other number of redeals"),
                               lambda gi: gi.si.redeals not in
                               (-2, -1, 0, 1, 2, 3)),
                )),
                s_by_compatibility,
            )),
            s_by_pysol_version,
            s_by_inventors,
            SelectGameNode(None, _("Other Categories"), (
                SelectGameNode(None, _("Games for Children (very easy)"),
                               lambda gi: gi.si.game_flags & GI.GT_CHILDREN),
                SelectGameNode(None, _("Games with Scoring"),
                               lambda gi: gi.si.game_flags & GI.GT_SCORE),
                SelectGameNode(None, _("Games with Stripped Decks"),
                               lambda gi: gi.si.game_flags & GI.GT_STRIPPED),
                SelectGameNode(None, _("Games with Separate Decks"),
                           lambda gi: gi.si.game_flags & GI.GT_SEPARATE_DECKS),
                SelectGameNode(None, _("Games with Jokers"),
                               lambda gi: gi.category == GI.GC_FRENCH and
                               gi.subcategory == GI.GS_JOKER_DECK),
                SelectGameNode(None, _("Open Games (all cards visible)"),
                               lambda gi: gi.si.game_flags & GI.GT_OPEN),
                SelectGameNode(None, _("Relaxed Variants"),
                               lambda gi: gi.si.game_flags & GI.GT_RELAXED),
            )),
            s_original,
            s_contrib,
        ) if _f]


# ************************************************************************
# * Canvas that shows the tree
# ************************************************************************
'''
class SelectGameTreeWithPreview(SelectDialogTreeCanvas):
    data = None


class SelectGameTree(SelectGameTreeWithPreview):
    def singleClick(self, event=None):
        self.doubleClick(event)
'''
# ************************************************************************
# * Kivy support
# ************************************************************************


class LGameRoot(LTreeRoot):
    def __init__(self, gametree, gameview, **kw):
        super(LGameRoot, self).__init__(**kw)
        self.gametree = gametree
        self.gameview = gameview
        self.kw = kw


class LGameNode(LTreeNode):
    def __init__(self, gamenode, gameview, **kw):

        self.lastpos = None
        self.gamenode = gamenode
        self.gameview = gameview
        super(LGameNode, self).__init__(**kw)

        self.coreFont = self.font_size
        # self.scaleFont(self.gameview.size[1])
        # self.gameview.bind(size=self.scaleFontCB)

        self.command = None
        if 'command' in kw:
            self.command = kw['command']
        self.bind(on_release=self.on_released)

    # font skalierung.

    def scaleFont(self, value):
        self.font_size = int(self.coreFont * value / 550.0)

    def scaleFontCB(self, instance, value):
        self.scaleFont(value[1])

    # benutzer interaktion.

    def on_released(self, v):
        if self.gamenode.key:
            if self.command:
                # print('game number = %s' % self.gamenode.key)
                Clock.schedule_once(self.commandCB, 0.1)
        else:
            # verzögert aufrufen, wegen user feedback.
            Clock.schedule_once(self.toggleCB, 0.1)
    '''
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            if self.lastpos==None:
                self.lastpos = touch.pos
                print('touch.pos %s' % str(touch.pos))
                return

            print ('touch move on %s - %s' % (self.text, touch.profile))
            print('touch.pos(2) %s' % str(touch.pos))
            # tbd: nur wenn horizontal move !
            if (touch.pos[0]+2) < self.lastpos[0]:
                Clock.schedule_once(self.collapseParentCB, 0.1)
        pass
    '''

    def commandCB(self, d):
        self.command(self.gamenode.key)

    def toggleCB(self, d):
        self.parent.toggle_node(self)

    '''
    def collapseParentCB(self, d):
        if self.parent:
            if self.parent_node.is_open:
                self.parent.toggle_node(self.parent_node)
            self.lastpos = None
    '''
# ************************************************************************
# * Dialog
# ************************************************************************


class SelectGameDialog(object):

    # Dialog, einmal erzeugt, wird rezykliert.
    SingleInstance = None

    def onClick(self, event):
        print('LTopLevel: onClick')
        SelectGameDialog.SingleInstance.parent.popWork('SelectGame')

    def selectCmd(self, gameid):
        self.app.menubar._mSelectGame(gameid)

    def __init__(self, parent, title, app, gameid, **kw):
        super(SelectGameDialog, self).__init__()

        self.parent = parent
        self.app = app
        self.gameid = gameid
        self.random = None
        self.window = None

        # bestehenden Dialog rezyklieren.

        si = SelectGameDialog.SingleInstance
        if si and si.parent.workStack.peek('SelectGame') is not None:
            parent.popWork('SelectGame')
            return
        if (si):
            si.parent.pushWork('SelectGame', si.window)
            return

        # neuen Dialog aufbauen.

        self.window = window = LTopLevel(parent, title)
        self.window.titleline.bind(on_press=self.onClick)

        self.parent.pushWork('SelectGame', self.window)
        SelectGameDialog.SingleInstance = self

        def updrule(obj, val):
            self.window.size_hint = get_menu_size_hint()
        updrule(0, 0)
        self.parent.bind(size=updrule)

        # Asynchron laden.

        def loaderCB(treeview, node):

            # Beispielcode aus doku:
            #
            # for name in ('Item 1', 'Item 2'):
            #   yield TreeViewLabel(text=name, parent=node)
            #
            # LGameNode ist ein Button. Es stellt sich heraus, dass
            # wir (ev. darum) parent=node NICHT setzen dürfen, da das
            # sonst zum versuchten doppelten einfügen des gleichen
            # widget im tree führt.

            if node:
                if not hasattr(node, "gamenode"):
                    # (das löst ein problem mit dem root knoten),
                    return

            v = treeview.gameview
            if node:
                n = node.gamenode
                n.tree = treeview.gametree

                nodes = n.getContents()
                if type(nodes) is list:
                    # Blaetter
                    for node in nodes:
                        # print ('**game=%s' % node.text)
                        yield LGameNode(
                            node, v, text=node.text,
                            is_leaf=True,
                            command=self.selectCmd)

                if type(nodes) is tuple:
                    # Knoten
                    for nn in nodes:
                        # print ('**node=%s' % nn.text)
                        newnode = LGameNode(
                            nn, v, text=nn.text, is_leaf=False)
                        yield newnode

                    print('all nodes done')
            else:
                # Knoten
                nodes = treeview.gametree.rootnodes[:]
                for n in nodes:
                    newnode = LGameNode(n, v, text=n.text, is_leaf=False)
                    # print ('**node=%s' % newnode)
                    yield newnode

        # treeview aufsetzen.

        tree = SelectGameData(app)
        tv = self.tvroot = LGameRoot(
            tree,
            self.app.canvas,
            root_options=dict(text='Tree One'))
        tv.size_hint = (1, None)
        tv.hide_root = True
        tv.load_func = loaderCB
        tv.bind(minimum_height=tv.setter('height'))

        # tree in einem Scrollwindow präsentieren.

        root = LScrollView(pos=(0, 0))
        root.add_widget(tv)
        window.content.add_widget(root)

# ************************************************************************
