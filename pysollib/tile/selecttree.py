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

__all__ = ['SelectDialogTreeData']

# Toolkit imports
from tktree import MfxTreeLeaf, MfxTreeNode, MfxTreeInCanvas

from pysollib.ui.tktile.selecttree import BaseSelectDialogTreeLeaf, BaseSelectDialogTreeNode, SelectDialogTreeData, BaseSelectDialogTreeCanvas

# ************************************************************************
# * Nodes
# ************************************************************************

class SelectDiagCommon:
    def _calc_MfxTreeNode(self):
        return MfxTreeNode
    def _calc_MfxTreeInCanvas(self):
        return MfxTreeInCanvas
    def _calc_MfxTreeLeaf(self):
        return MfxTreeLeaf

class SelectDialogTreeLeaf(SelectDiagCommon, BaseSelectDialogTreeLeaf, MfxTreeLeaf):
    pass

class SelectDialogTreeNode(SelectDiagCommon, BaseSelectDialogTreeNode, MfxTreeNode):
    pass

# ************************************************************************
# * Canvas that shows the tree (left side)
# ************************************************************************

class SelectDialogTreeCanvas(SelectDiagCommon, BaseSelectDialogTreeCanvas, MfxTreeInCanvas):
    pass
