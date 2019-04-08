#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.

"""

"""


class KpatEmitter:
    """docstring for KpatEmitter"""
    def _out(self, text):
        """docstring for _out"""
        self.f.write(text)

    def __init__(self, f):
        self.f = f
        self._out("""<?xml version="1.0" encoding="UTF-8"?>\n""")

    def writeEmptyTag(self, name, attrs):
        self._out(
            "<" + name + "".join([" "+x[0]+"=\""+x[1]+"\"" for x in attrs])
            + "/>\n")
