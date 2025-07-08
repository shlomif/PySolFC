#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
#  Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
#  Copyright (C) 2003 Mt. Hood Playing Card Co.
#  Copyright (C) 2005-2009 Skomoroh
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

# imports
import getopt
import os
import sys
import traceback

from pysollib.app import Application
from pysollib.gamedb import GAME_DB
from pysollib.mfxutil import print_err
from pysollib.mygettext import _
from pysollib.pysolaudio import AbstractAudioClient
from pysollib.pysolaudio import KivyAudioClient, OSSAudioClient
from pysollib.pysolaudio import PyGameAudioClient, Win32AudioClient
from pysollib.pysolaudio import PysolSoundServerModuleClient
from pysollib.pysolaudio import pysolsoundserver
from pysollib.pysoltk import MfxMessageDialog
from pysollib.pysoltk import MfxRoot
from pysollib.pysoltk import PysolProgressBar
from pysollib.pysoltk import loadImage
from pysollib.resource import Tile
from pysollib.settings import SOUND_MOD, TITLE, TOOLKIT
from pysollib.util import DataLoader
from pysollib.winsystems import init_root_window

# ************************************************************************
# *
# ************************************************************************

if TOOLKIT == 'kivy':
    from pysollib.mfxutil import getprefdir
    from pysollib.settings import PACKAGE

    def fatal_no_cardsets(app):
        app.wm_withdraw()
        MfxMessageDialog(app.top, title=_("%s installation error") % TITLE,
                         text=_('''No cardsets were found!!!

Cardsets should be installed into:
%(dir)s

Please check your %(app)s installation.
''') % {'dir': getprefdir(PACKAGE) + '/cardsets/', 'app': TITLE},
            bitmap="error", strings=(_("&Quit"),))
else:
    def fatal_no_cardsets(app):
        app.wm_withdraw()
        MfxMessageDialog(app.top, title=_("%s installation error") % TITLE,
                         text=_('''No cardsets were found!!!

Main data directory is:
%(dir)s

Please check your %(app)s installation.
''') % {'dir': app.dataloader.dir, 'app': TITLE},
                     bitmap="error", strings=(_("&Quit"),))


# ************************************************************************
# *
# ************************************************************************

def parse_option(argv):
    prog_name = argv[0]
    try:
        optlist, args = getopt.getopt(argv[1:], "g:i:hD:",
                                      ["deal=", "game=", "gameid=",
                                       "random-game",
                                       "french-only",
                                       "noplugins",
                                       "nosound",
                                       "sound-mod=",
                                       "help"])
    except getopt.GetoptError as err:
        print_err(str(err) + "\n" + _("try %s --help for more information") %
                  prog_name, 0)
        return None
    opts = {"help": False,
            "deal": None,
            "game": None,
            "gameid": None,
            "random-game": False,
            "french-only": False,
            "noplugins": False,
            "nosound": False,
            "sound-mod": None,
            }
    for i in optlist:
        if i[0] in ("-h", "--help"):
            opts["help"] = True
        elif i[0] == "--deal":
            opts["deal"] = i[1]
        elif i[0] in ("-g", "--game"):
            opts["game"] = i[1]
        elif i[0] in ("-i", "--gameid"):
            opts["gameid"] = i[1]
        elif i[0] == "--random-game":
            opts["random-game"] = True
        elif i[0] == "--french-only":
            opts["french-only"] = True
        elif i[0] == "--noplugins":
            opts["noplugins"] = True
        elif i[0] == "--nosound":
            opts["nosound"] = True
        elif i[0] == "--sound-mod":
            assert i[1] in ('pss', 'pygame', 'oss', 'win')
            opts["sound-mod"] = i[1]

    if opts["help"]:
        print(_("""Usage: %s [OPTIONS] [FILE]
  -g    --game=GAMENAME        start game GAMENAME
  -i    --gameid=GAMEID        start game with ID GAMEID
        --deal=DEAL            start game deal by number DEAL
        --random-game          start a random game
        --french-only          disable non-french games
        --sound-mod=MOD        use a certain sound module
        --nosound              disable sound support
        --noplugins            disable loading plugins
  -h    --help                 display this help and exit

  FILE - file name of a saved game
  MOD - one of following: pss(default), pygame, oss, win
""") % prog_name)
        return None

    if len(args) > 1:
        print_err(
            _("too many files\ntry %s --help for more information") %
            prog_name, 0)
        return None
    filename = args and args[0] or None
    if filename and not os.path.isfile(filename):
        print_err(
            _("invalid file name\ntry %s --help for more information") %
            prog_name, 0)
        return None
    return opts, filename

# ************************************************************************
# *
# ************************************************************************


def pysol_init(app, args):

    # init commandline options (undocumented)
    opts = parse_option(args)
    if not opts:
        return 1
        sys.exit(1)
    opts, filename = opts
    if filename:
        app.commandline.loadgame = filename
    app.commandline.deal = opts['deal']
    app.commandline.game = opts['game']
    if opts['gameid'] is not None:
        try:
            app.commandline.gameid = int(opts['gameid'])
        except ValueError:
            print_err(_('invalid game id: ') + opts['gameid'])

    # try to create the config directory
    for d in (
        app.dn.config,
        app.dn.savegames,
        app.dn.boards,
        os.path.join(app.dn.config, "music"),
        # os.path.join(app.dn.config, "screenshots"),
        os.path.join(app.dn.config, "tiles"),
        os.path.join(app.dn.config, "tiles", "stretch"),
        os.path.join(app.dn.config, "tiles", "save-aspect"),
        os.path.join(app.dn.config, "tiles", "stretch-4k"),
        os.path.join(app.dn.config, "tiles", "save-aspect-4k"),
        os.path.join(app.dn.config, "cardsets"),
        os.path.join(app.dn.config, "plugins"),
            ):
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except Exception:
                traceback.print_exc()

    # init DataLoader
    f = os.path.join("html", "license.html")
    app.dataloader = DataLoader(args[0], f)

    # init toolkit 1)
    top = MfxRoot(className=TITLE)
    app.top = top
    app.top_bg = top.cget("bg")
    app.top_cursor = top.cget("cursor")

    # load options
    try:
        app.loadOptions()
    except Exception:
        traceback.print_exc()

    # init toolkit 2)
    init_root_window(top, app)

    # prepare the progress bar
    app.loadImages1()
    if not app.progress_images:
        app.progress_images = (loadImage(app.gimages.logos[0]),
                               loadImage(app.gimages.logos[1]))
    app.wm_withdraw()

    # create the progress bar
    title = _("Welcome to %s") % TITLE
    color = app.opt.colors['table']
    if app.tabletile_index > 0:
        color = "#008200"
    app.intro.progress = PysolProgressBar(app, top, title=title, color=color,
                                          images=app.progress_images, norm=2.0)
    app.intro.progress.update(step=1)

    # init games database
    def progressCallback(*args):
        app.intro.progress.update(step=1)
    GAME_DB.setCallback(progressCallback)
    import pysollib.games
    if not opts['french-only']:
        import pysollib.games.mahjongg
        import pysollib.games.special
        pysollib.games.special.no_use()

    # try to load plugins
    if not opts["noplugins"]:
        for dir in (os.path.join(app.dataloader.dir, "games"),
                    os.path.join(app.dataloader.dir, "plugins"),
                    app.dn.plugins):
            try:
                app.loadPlugins(dir)
            except Exception:
                pass
    GAME_DB.setCallback(None)

    # init audio 1)
    app.audio = None
    sounds = {'pss':     PysolSoundServerModuleClient,
              'pygame':  PyGameAudioClient,
              'oss':     OSSAudioClient,
              'win':     Win32AudioClient}
    if TOOLKIT == 'kivy':
        sounds['kivy'] = KivyAudioClient
    if opts["nosound"] or SOUND_MOD == 'none':
        app.audio = AbstractAudioClient()
    elif opts['sound-mod']:
        c = sounds[opts['sound-mod']]
        app.audio = c()
    elif SOUND_MOD == 'auto':
        snd = []
        snd.append(PyGameAudioClient)
        if TOOLKIT == 'kivy':
            snd.append(KivyAudioClient)
        if pysolsoundserver:
            snd.append(PysolSoundServerModuleClient)
        snd.append(OSSAudioClient)
        snd.append(Win32AudioClient)
        snd.append(AbstractAudioClient)
        for c in snd:
            try:
                app.audio = c()
                app.audio.startServer()
                app.audio.connectServer(app)
            except Exception:
                pass
            else:
                # success
                break
    else:
        c = sounds[SOUND_MOD]
        app.audio = c()
        app.audio.startServer()
        app.audio.connectServer(app)

    # update sound_mode
    if isinstance(app.audio, PysolSoundServerModuleClient):
        app.opt.sound_mode = 1
    else:
        app.opt.sound_mode = 0

    # check games
    if len(app.gdb.getGamesIdSortedByName()) == 0:
        app.wm_withdraw()
        app.intro.progress.destroy()
        d = MfxMessageDialog(top, title=_("%s installation error") % TITLE,
                             text=_('''
No games were found!!!

Main data directory is:
%(dir)s

Please check your %(app)s installation.
''') % {'dir': app.dataloader.dir, 'app': TITLE},
                             bitmap="error", strings=(_("&Quit"),))
        return 1

    if opts['random-game']:
        app.commandline.gameid = app.getRandomGameId()

    # init cardsets
    app.initCardsets()
    cardset = None
    c = app.opt.cardset.get(0).get(0)
    if c:
        cardset = app.cardset_manager.getByName(c[0])
        if cardset and c[1]:
            cardset.updateCardback(backname=c[1])
    if app.cardset_manager.len() == 0:
        fatal_no_cardsets(app)
        return 3
    missing = app.cardset_manager.identify_missing_cardsets()
    if len(missing) > 0:
        error_text = \
            _('''PySol cannot find cardsets of the following types:''')
        error_text += "\n\n"
        for missingtype in missing:
            error_text += missingtype + "\n"
        error_text += _('''
This may make games that use those types of cardsets unplayable. Please
ensure that your Cardsets package is up to date.''')
        MfxMessageDialog(top, title=_("Cardset error"), text=error_text,
                         bitmap="error")
    if not cardset:
        MfxMessageDialog(top, title=_("Cardset error"),
                         text=_('''
The cardset "%(cs)s" was not found.

Please ensure that this cardset has been installed, and that your
Cardsets package is up to date.
''') % {'cs': c[0]},
                         bitmap="error")
        cardset = app.cardset_manager.getByName("Standard")
        if not cardset:
            cardset = app.cardset_manager.get(0)
            if not cardset:
                fatal_no_cardsets(app)
                return 3

    # init tiles
    manager = app.tabletile_manager
    tile = Tile()
    tile.color = app.opt.colors['table']
    tile.name = "None"
    tile.filename = None
    manager.register(tile)
    app.initTiles()
    if app.opt.tabletile_name:  # and top.winfo_screendepth() > 8:
        for tile in manager.getAll():
            # The basename is checked in addition to the tile name
            # this is to support differences in the table tile format
            # from older PySol versions.
            if (app.opt.tabletile_name == tile.name or
                    (os.path.splitext(app.opt.tabletile_name)[0] ==
                     os.path.splitext(tile.basename)[0])):
                app.tabletile_index = tile.index
                break

    # init samples and music resources
    app.initSamples()
    app.initMusic()

    # init audio 2)
    if not app.audio.CAN_PLAY_SOUND:
        app.opt.sound = 0
    app.audio.updateSettings()
    # start up the background music
    if app.audio.CAN_PLAY_MUSIC:
        music = app.music_manager.getAll()
        if music:
            app.music_playlist = list(music)[:]
            app.miscrandom.shuffle(app.music_playlist)
            # Cancelling because otherwise people complain
            # that the music order is not random.
            SHOULD_PUT_bye_for_now_FIRST = False
            if SHOULD_PUT_bye_for_now_FIRST:
                for m in app.music_playlist:
                    if m.name.lower() == "bye_for_now":
                        app.music_playlist.remove(m)
                        app.music_playlist.insert(0, m)
                        break
            app.audio.playContinuousMusic(app.music_playlist)

    # prepare other images
    app.loadImages2()
    app.loadImages3()
    app.loadImages4()

    startgameid = app.opt.last_gameid

    if app.commandline.loadgame:
        pass
    elif app.commandline.game is not None:
        gameid = app.gdb.getGameByName(app.commandline.game)
        if gameid is None:
            print_err(_("can't find game: %(game)s") % {
                'game': app.commandline.game})
            sys.exit(-1)
        else:
            startgameid = gameid
    elif app.commandline.gameid is not None:
        startgameid = app.commandline.gameid

    progress = app.intro.progress
    # load cardset
    if startgameid != app.opt.last_gameid and app.opt.game_holded == 0:
        success = app.requestCompatibleCardsetType(startgameid,
                                                   progress=progress)
    else:
        success = app.loadCardset(cardset, progress=progress, id=startgameid)
    if not success and not cardset:
        for cardset in app.cardset_manager.getAll():
            progress.reset()

            if app.loadCardset(cardset, progress=progress,
                               id=startgameid):
                break
        else:
            fatal_no_cardsets(app)
            return 3

    # ok
    return 0


# ************************************************************************
# * main
# ************************************************************************


if TOOLKIT == 'kivy':
    from pysollib.kivy.LApp import LApp
    import logging

    def main(args=None):
        logging.basicConfig(level=logging.INFO)
        LApp(args).run()

else:

    def main(args=None):
        # create the application
        app = Application()
        r = pysol_init(app, args)
        if r != 0:
            return r
        # let's go - enter the mainloop
        app.mainloop()
