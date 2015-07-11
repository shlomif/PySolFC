#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-

import gettext

def n_(x):
    return x

def fix_gettext():
    def ugettext(message):
        # unicoded gettext
        if not isinstance(message, str):
            message = str(message, 'utf-8')
        domain = gettext._current_domain
        try:
            t = gettext.translation(domain,
                                    gettext._localedirs.get(domain, None))
        except IOError:
            return message
        return t.ugettext(message)
    gettext.ugettext = ugettext
    def ungettext(msgid1, msgid2, n):
        # unicoded ngettext
        if not isinstance(msgid1, str):
            msgid1 = str(msgid1, 'utf-8')
        if not isinstance(msgid2, str):
            msgid2 = str(msgid2, 'utf-8')
        domain = gettext._current_domain
        try:
            t = gettext.translation(domain,
                                    gettext._localedirs.get(domain, None))
        except IOError:
            if n == 1:
                return msgid1
            else:
                return msgid2
        return t.ungettext(msgid1, msgid2, n)
    gettext.ungettext = ungettext

fix_gettext()
_ = gettext.ugettext
