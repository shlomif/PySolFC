##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
##---------------------------------------------------------------------------##

import sys, os, locale
import traceback
import gettext

import settings

# /***********************************************************************
# // init
# ************************************************************************/

def fix_gettext():
    def ugettext(message):
        # unicoded gettext
        if not isinstance(message, unicode):
            message = unicode(message, 'utf-8')
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
        if not isinstance(msgid1, unicode):
            msgid1 = unicode(msgid1, 'utf-8')
        if not isinstance(msgid2, unicode):
            msgid2 = unicode(msgid2, 'utf-8')
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


def init():
    fix_gettext()

    if os.name == 'nt' and 'LANG' not in os.environ:
        try:
            l = locale.getdefaultlocale()
            os.environ['LANG'] = l[0]
        except:
            pass
    ##locale.setlocale(locale.LC_ALL, '')

    ## install gettext
    ##locale_dir = 'locale'
    locale_dir = None
    if os.path.isdir(sys.path[0]):
        d = os.path.join(sys.path[0], 'locale')
    else:
        # i.e. library.zip
        d = os.path.join(os.path.dirname(sys.path[0]), 'locale')
    if os.path.exists(d) and os.path.isdir(d):
        locale_dir = d
    ##if locale_dir: locale_dir = os.path.normpath(locale_dir)
    #gettext.install('pysol', locale_dir, unicode=True) # ngettext don't work
    gettext.bindtextdomain('pysol', locale_dir)
    gettext.textdomain('pysol')
    import __builtin__
    __builtin__._ = gettext.ugettext    # use unicode
    __builtin__.n_ = lambda x: x

    ## debug
    if 'PYSOL_CHECK_GAMES' in os.environ or 'PYSOL_DEBUG' in os.environ:
        settings.CHECK_GAMES = True
        print 'PySol debugging: set CHECK_GAMES to True'
    if 'PYSOL_DEBUG' in os.environ:
        try:
            settings.DEBUG = int(os.environ['PYSOL_DEBUG'])
        except:
            settings.DEBUG = 1
        print 'PySol debugging: set DEBUG to', settings.DEBUG

    ## init toolkit
    if '--gtk' in sys.argv:
        settings.TOOLKIT = 'gtk'
        sys.argv.remove('--gtk')
    elif '--tk' in sys.argv:
        settings.TOOLKIT = 'tk'
        settings.USE_TILE = False
        sys.argv.remove('--tk')
    elif '--tile' in sys.argv:
        settings.TOOLKIT = 'tk'
        settings.USE_TILE = True
        sys.argv.remove('--tile')
    if settings.TOOLKIT == 'tk':
        import Tkinter
        root = Tkinter.Tk(className=settings.TITLE)
        root.withdraw()
        if Tkinter.TkVersion < 8.4:
            # we need unicode support
            sys.exit("%s needs Tcl/Tk 8.4 or better (you have %s)" %
                     (settings.TITLE, str(Tkinter.TkVersion)))
        settings.WIN_SYSTEM = root.tk.call('tk', 'windowingsystem')
        if settings.WIN_SYSTEM == 'aqua':
            # TkAqua displays the console automatically in application
            # bundles, so we hide it here.
            from macosx.appSupport import hideTkConsole
            hideTkConsole(root)
        #
        if settings.USE_TILE == 'auto':
            # check Tile
            settings.USE_TILE = False
            try:
                root.tk.eval('package require tile 0.7.8')
            except Tkinter.TclError:
                pass
            else:
                settings.USE_TILE = True
        # "can't invoke event <<ThemeChanged>>: application has been destroyed"
        #root.destroy()
        Tkinter._default_root = None

    # check FreeCell-Solver
    settings.USE_FREECELL_SOLVER = False
    if os.name == 'nt':
        if sys.path[0] and not os.path.isdir(sys.path[0]): # i.e. library.zip
            d = os.path.dirname(sys.path[0])
            os.chdir(d)                 # for read presets
            fcs_command = os.path.join('freecell-solver', 'fc-solve.exe')
            settings.FCS_COMMAND = fcs_command
            ##f = os.path.join(d, 'freecell-solver', 'presetrc')
            ##os.environ['FREECELL_SOLVER_PRESETRC'] = f # defined in prefix.h
    if os.name in ('posix', 'nt'):
        try:
            pin, pout, perr = os.popen3(settings.FCS_COMMAND+' --help')
            if pout.readline().startswith('fc-solve'):
                settings.USE_FREECELL_SOLVER = True
            del pin, pout, perr
            if os.name == 'posix':
                os.wait()               # kill zombi
        except:
            ##traceback.print_exc()
            pass
    os.environ['FREECELL_SOLVER_QUIET'] = '1'

    # run app without games menus (more fast start)
    if '--no-games-menu' in sys.argv:
        sys.argv.remove('--no-games-menu')
        settings.SELECT_GAME_MENU = False

