#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.

"""

"""


class NewStruct(object):
    """docstring for NewStruct"""
    def copy(self):
        ret = self.__class__()
        ret.__dict__.update(self.__dict__)
        return ret
