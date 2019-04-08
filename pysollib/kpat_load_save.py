#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Shlomi Fish <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.

"""

"""


class KpatXmlEmitter:
    """docstring for KpatXmlEmitter"""
    def _ind_out(self, text):
        """docstring for _out"""
        self._out("\t" * self._indent)
        self._out(text)

    def _out(self, text):
        """docstring for _out"""
        self.f.write(text)

    def __init__(self, f):
        self.f = f
        self._out("""<?xml version="1.0" encoding="UTF-8"?>\n""")
        self._tags = []
        self._indent = 0

    def _genericTag(self, suf, name, attrs):
        self._ind_out(
            "<" + name + "".join([" "+k+"=\""+v+"\"" for k, v in attrs])
            + suf + ">\n")

    def writeEmptyTag(self, name, attrs):
        self._genericTag("/", name, attrs)

    def writeStartTag(self, name, attrs):
        self._genericTag("", name, attrs)
        self._tags.append({'name': name})
        self._indent += 1

    def endTag(self):
        """docstring for endTag"""
        self._indent -= 1
        self._ind_out("</{}>\n".format(self._tags.pop()['name']))
