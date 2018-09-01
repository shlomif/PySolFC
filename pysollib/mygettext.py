import gettext
import sys
import six


def n_(x):
    return x


def fix_gettext():
    def ugettext(message):
        # unicoded gettext
        if not isinstance(message, six.text_type):
            message = six.text_type(message, 'utf-8')
        domain = gettext._current_domain
        try:
            t = gettext.translation(domain,
                                    gettext._localedirs.get(domain, None))
        except IOError:
            return message
        if sys.version_info >= (3, 0):
            return t.gettext(message)
        else:
            return t.ugettext(message)

    gettext.ugettext = ugettext

    def ungettext(msgid1, msgid2, n):
        # unicoded ngettext
        if not isinstance(msgid1, six.text_type):
            msgid1 = six.text_type(msgid1, 'utf-8')
        if not isinstance(msgid2, six.text_type):
            msgid2 = six.text_type(msgid2, 'utf-8')
        domain = gettext._current_domain
        try:
            t = gettext.translation(domain,
                                    gettext._localedirs.get(domain, None))
        except IOError:
            if n == 1:
                return msgid1
            else:
                return msgid2
        if sys.version_info >= (3, 0):
            return t.ngettext(msgid1, msgid2, n)
        else:
            return t.ungettext(msgid1, msgid2, n)
    gettext.ungettext = ungettext


fix_gettext()
_ = gettext.ugettext
