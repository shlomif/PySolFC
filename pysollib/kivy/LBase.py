#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-
# =============================================================================
# Copyright (C) 2017-2023 LB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# =============================================================================
# noqa
# kivy EventDispatcher passes keywords, that to not correspond to properties
# to the base classes. Finally they will reach 'object'. With python3 (but not
# python2) 'object' throws an exception 'takes no parameters' in that a
# situation. We therefore underlay a base class (right outside), which
# swallows up remaining keywords. Thus the keywords do not reach 'object' any
# more.

class LBase(object):
    def __init__(self, **kw):
        super(LBase, self).__init__()

# =============================================================================
