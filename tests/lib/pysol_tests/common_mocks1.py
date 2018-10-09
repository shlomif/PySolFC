#! /usr/bin/env python MockItem
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.

from pysollib.acard import AbstractCard
import pysollib.stack

"""

"""


class MockItem:
    def __init__(self):
        pass

    def tkraise(self):
        return

    def addtag(self, nouse):
        return


class MockCanvas:
    def __init__(self):
        self.xmargin = self.ymargin = 50


class MockImages:
    def __init__(self):
        self.CARDW = self.CARDH = self.CARD_YOFFSET = 50


class MockOpt:
    def __init__(self):
        self.randomize_place = False


class MockApp:
    def __init__(self):
        self.images = MockImages()
        self.opt = MockOpt()


class MockTalon:
    def __init__(self, g):
        self.cards = [
            AbstractCard(1000+r*100+s*10, 0, s, r, g)
            for s in range(4) for r in range(13)]
        for c in self.cards:
            c.item = MockItem()


def _empty_override(*args):
    return True


pysollib.stack.MfxCanvasGroup = _empty_override
