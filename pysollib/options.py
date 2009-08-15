#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##---------------------------------------------------------------------------##

# imports
import sys, os
import traceback

# PySol imports
from mfxutil import print_err
from resource import CSI
from configobj import configobj, validate
import settings

# Toolkit imports
from pysoltk import TOOLBAR_BUTTONS


# ************************************************************************
# * Options
# ************************************************************************


configspec = '''
[general]
player = string
confirm = boolean
update_player_stats = boolean
autofaceup = boolean
autodrop = boolean
autodeal = boolean
quickplay = boolean
shuffle = boolean
undo = boolean
bookmarks = boolean
hint = boolean
highlight_piles = boolean
highlight_cards = boolean
highlight_samerank = boolean
highlight_not_matching = boolean
mahjongg_show_removed = boolean
mahjongg_create_solvable = integer(0, 2)
shisen_show_hint = boolean
shisen_show_matching = boolean
animations = integer(0, 5)
redeal_animation = boolean
win_animation = boolean
flip_animation = boolean
compact_stacks = boolean
shadow = boolean
shade = boolean
shrink_face_down = boolean
shade_filled_stacks = boolean
demo_logo = boolean
tile_theme = string
default_tile_theme = string
toolbar = integer(0, 4)
toolbar_style = string
toolbar_relief = string
toolbar_compound = string
toolbar_size = integer(0, 1)
statusbar = boolean
statusbar_game_number = boolean
statusbar_stuck = boolean
num_cards = boolean
helpbar = boolean
num_recent_games = integer(10, 100)
last_gameid = integer
game_holded = integer
wm_maximized = boolean
splashscreen = boolean
mouse_type = string
mouse_undo = boolean
negative_bottom = boolean
randomize_place = boolean
save_cardsets = boolean
dragcursor = boolean
save_games_geometry = boolean
sound = boolean
sound_mode = integer(0, 1)
sound_sample_volume = integer(0, 128)
sound_sample_buffer_size = integer(1, 4)
tabletile_name = string
recent_gameid = int_list
favorite_gameid = int_list
visible_buttons = string_list
translate_game_names = boolean

[sound_samples]
move = boolean
autodrop = boolean
drop = boolean
nomove = boolean
gameperfect = boolean
deal = boolean
gamelost = boolean
autopilotwon = boolean
flip = boolean
undo = boolean
gamefinished = boolean
areyousure = boolean
startdrag = boolean
autoflip = boolean
autopilotlost = boolean
turnwaste = boolean
gamewon = boolean
droppair = boolean
redo = boolean
dealwaste = boolean

[fonts]
sans = list
small = list
fixed = list
canvas_default = list
canvas_small = list
canvas_fixed = list
canvas_large = list

[colors]
piles = string
text = string
table = string
hintarrow = string
cards_1 = string
cards_2 = string
samerank_1 = string
samerank_2 = string
not_matching = string

[timeouts]
highlight_samerank = float(0.2, 9.9)
raise_card = float(0.2, 9.9)
demo = float(0.2, 9.9)
highlight_cards = float(0.2, 9.9)
hint = float(0.2, 9.9)
highlight_piles = float(0.2, 9.9)

[cardsets]
0 = string_list(min=2, max=2)
1 = string_list(min=2, max=2)
2 = string_list(min=2, max=2)
3 = string_list(min=2, max=2)
4 = string_list(min=2, max=2)
5 = string_list(min=2, max=2)
6 = string_list(min=2, max=2)
7 = string_list(min=2, max=2)
8 = string_list(min=2, max=2)
9 = string_list(min=2, max=2)

'''.splitlines()


class Options:
    GENERAL_OPTIONS = [
        ('player', 'str'),
        ('confirm', 'bool'),
        ('update_player_stats', 'bool'),
        ('autofaceup', 'bool'),
        ('autodrop', 'bool'),
        ('autodeal', 'bool'),
        ('quickplay', 'bool'),
        ('shuffle', 'bool'),
        ('undo', 'bool'),
        ('bookmarks', 'bool'),
        ('hint', 'bool'),
        ('highlight_piles', 'bool'),
        ('highlight_cards', 'bool'),
        ('highlight_samerank', 'bool'),
        ('highlight_not_matching', 'bool'),
        ('mahjongg_show_removed', 'bool'),
        ('mahjongg_create_solvable', 'int'),
        ('shisen_show_hint', 'bool'),
        ('shisen_show_matching', 'bool'),
        ('animations', 'int'),
        ('redeal_animation', 'bool'),
        ('win_animation', 'bool'),
        ('flip_animation', 'bool'),
        ('compact_stacks', 'bool'),
        ('shadow', 'bool'),
        ('shade', 'bool'),
        ('shrink_face_down', 'bool'),
        ('shade_filled_stacks', 'bool'),
        ('demo_logo', 'bool'),
        ('tile_theme', 'str'),
        ('default_tile_theme', 'str'),
        ('toolbar', 'int'),
        ('toolbar_style', 'str'),
        ('toolbar_relief', 'str'),
        ('toolbar_compound', 'str'),
        ('toolbar_size', 'int'),
        ('statusbar', 'bool'),
        ('statusbar_game_number', 'bool'),
        ('statusbar_stuck', 'bool'),
        ('num_cards', 'bool'),
        ('helpbar', 'bool'),
        ('num_recent_games', 'int'),
        ('last_gameid', 'int'),
        ('game_holded', 'int'),
        ('wm_maximized', 'bool'),
        ('splashscreen', 'bool'),
        ('mouse_type', 'str'),
        ('mouse_undo', 'bool'),
        ('negative_bottom', 'bool'),
        ('randomize_place', 'bool'),
        ('save_cardsets', 'bool'),
        ('dragcursor', 'bool'),
        ('save_games_geometry', 'bool'),
        ('sound', 'bool'),
        ('sound_mode', 'int'),
        ('sound_sample_volume', 'int'),
        ('sound_music_volume', 'int'),
        ('sound_sample_buffer_size', 'int'),
        ('tabletile_name', 'str'),
        ('translate_game_names', 'bool'),
        #('toolbar_vars', 'list'),
        #('recent_gameid', 'list'),
        #('favorite_gameid', 'list'),
        ]


    def __init__(self):
        self._config = None             # configobj.ConfigObj instance
        self._config_encoding = 'utf-8'

        self.version_tuple = settings.VERSION_TUPLE # XXX
        self.saved = 0                  # XXX
        # options menu:
        self.player = _("Unknown")
        self.confirm = True
        self.update_player_stats = True
        self.autofaceup = True
        self.autodrop = False
        self.autodeal = True
        self.quickplay = True
        self.shuffle = True
        self.undo = True
        self.bookmarks = True
        self.hint = True
        self.highlight_piles = True
        self.highlight_cards = True
        self.highlight_samerank = True
        self.highlight_not_matching = True
        self.mahjongg_show_removed = False
        self.mahjongg_create_solvable = 2 # 0 - none, 1 - easy, 2 - hard
        self.shisen_show_hint = True
        self.shisen_show_matching = False
        self.animations = 3             # default to Medium
        self.redeal_animation = True
        self.win_animation = True
        self.flip_animation = True
        self.compact_stacks = True
        self.shadow = True
        self.shade = True
        self.shrink_face_down = True
        self.shade_filled_stacks = True
        self.demo_logo = True
        self.tile_theme = 'default'
        self.default_tile_theme = 'default'
        self.toolbar = 1       # 0 == hide, 1,2,3,4 == top, bottom, lef, right
        ##self.toolbar_style = 'default'
        self.toolbar_style = 'bluecurve'
        self.toolbar_relief = 'flat'
        self.toolbar_compound = 'none'  # icons only
        self.toolbar_size = 0
        self.toolbar_vars = {}
        for w in TOOLBAR_BUTTONS:
            self.toolbar_vars[w] = True # show all buttons
        self.statusbar = True
        self.statusbar_game_number = False # show game number in statusbar
        self.statusbar_stuck = False       # show stuck indicator
        self.num_cards = False
        self.helpbar = False
        self.splashscreen = True
        self.mouse_type = 'drag-n-drop' # or 'sticky-mouse' or 'point-n-click'
        self.mouse_undo = False         # use mouse for undo/redo
        self.negative_bottom = True
        self.translate_game_names = True
        # sound
        self.sound = True
        self.sound_mode = 1
        self.sound_sample_volume = 80
        self.sound_music_volume = 100
        self.sound_sample_buffer_size = 1 # 1 - 4 (1024 - 4096 bytes)
        self.sound_samples = {
            'areyousure'    : True,
            'autodrop'      : True,
            'autoflip'      : True,
            'autopilotlost' : True,
            'autopilotwon'  : True,
            'deal'          : True,
            'dealwaste'     : True,
            'droppair'      : True,
            'drop'          : True,
            #'extra'         : True,
            'flip'          : True,
            'move'          : True,
            'nomove'        : True,
            'redo'          : True,
            'startdrag'     : True,
            'turnwaste'     : True,
            'undo'          : True,
            'gamefinished'  : False,
            'gamelost'      : False,
            'gameperfect'   : False,
            'gamewon'       : False,
            }
        # fonts
        self.fonts = {
            "default"        : None,
            #"default"        : ("helvetica", 12),
            "sans"           : ("times",     12), # for html
            "fixed"          : ("courier",   12), # for html & log
            "small"          : ("helvetica", 12),
            "canvas_default" : ("helvetica", 12),
            #"canvas_card"    : ("helvetica", 12),
            "canvas_fixed"   : ("courier",   12),
            "canvas_large"   : ("helvetica", 16),
            "canvas_small"   : ("helvetica", 10),
            }
        # colors
        self.colors = {
            'table':        '#008200',
            'text':         '#ffffff',
            'piles':        '#ffc000',
            'cards_1':      '#ffc000',
            'cards_2':      '#0000ff',
            'samerank_1':   '#ffc000',
            'samerank_2':   '#0000ff',
            'hintarrow':    '#303030',
            'not_matching': '#ff0000',
            }
        # delays
        self.timeouts = {
            'hint':               1.0,
            'demo':               1.0,
            'raise_card':         1.0,
            'highlight_piles':    1.0,
            'highlight_cards':    1.0,
            'highlight_samerank': 1.0,
            }
        # additional startup information
        self.num_recent_games = 15
        self.recent_gameid = []
        self.favorite_gameid = []
        self.last_gameid = 0            # last game played
        self.game_holded = 0            # gameid or 0
        self.wm_maximized = 0
        self.save_games_geometry = False
        self.games_geometry = {} # saved games geometry (gameid: (width, height))
        #
        self.randomize_place = False
        self.save_cardsets = True
        self.dragcursor = True

    def setDefaults(self, top=None):
        WIN_SYSTEM = settings.WIN_SYSTEM
        # toolbar
        #if WIN_SYSTEM == 'win32':
        #    self.toolbar_style = 'crystal'
        # fonts
        if WIN_SYSTEM == 'win32':
            self.fonts["sans"] = ("times new roman", 12)
            self.fonts["fixed"] = ("courier new", 10)
        elif WIN_SYSTEM == 'x11':
            self.fonts["sans"] = ("helvetica", -12)
        # tile theme
        if WIN_SYSTEM == 'win32':
            self.tile_theme = self.default_tile_theme = 'winnative'
            if sys.getwindowsversion() >= (5, 1): # xp
                self.tile_theme = 'xpnative'
        elif WIN_SYSTEM == 'x11':
            self.tile_theme = 'clam'
            self.default_tile_theme = 'default'
        elif WIN_SYSTEM == 'aqua':
            self.tile_theme = self.default_tile_theme = 'aqua'
        #
        sw, sh, sd = 0, 0, 8
        if top:
            sw, sh, sd = (top.winfo_screenwidth(),
                          top.winfo_screenheight(),
                          top.winfo_screendepth())
        # bg
        if sd > 8:
            self.tabletile_name = "Nostalgy.gif" # basename
        else:
            self.tabletile_name = None
        # cardsets
        c = "Standard"
        if sw < 800 or sh < 600:
            c = "2000"
        #if sw > 1024 and sh > 768:
        #    c = 'Dondorf'
        self.cardset = {
            # game_type:        (cardset_name, back_file)
            0:                  (c, ""),
            CSI.TYPE_FRENCH:    (c, ""),
            CSI.TYPE_HANAFUDA:  ("Kintengu", ""),
            CSI.TYPE_MAHJONGG:  ("Crystal Mahjongg", ""),
            CSI.TYPE_TAROCK:    ("Vienna 2K", ""),
            CSI.TYPE_HEXADECK:  ("Hex A Deck", ""),
            CSI.TYPE_MUGHAL_GANJIFA: ("Mughal Ganjifa", ""),
            ##CSI.TYPE_NAVAGRAHA_GANJIFA: ("Navagraha Ganjifa", ""),
            CSI.TYPE_NAVAGRAHA_GANJIFA: ("Dashavatara Ganjifa", ""),
            CSI.TYPE_DASHAVATARA_GANJIFA: ("Dashavatara Ganjifa", ""),
            CSI.TYPE_TRUMP_ONLY: ("Matrix", ""),
        }

    # not changeable options
    def setConstants(self):
        if 'shuffle' not in self.toolbar_vars:
            # new in v.1.1
            self.toolbar_vars['shuffle'] = True
        if isinstance(self.mahjongg_create_solvable, bool):
            # changed in v.1.1
            self.mahjongg_create_solvable = 2
        pass

    def copy(self):
        opt = Options()
        opt.__dict__.update(self.__dict__)
        opt.setConstants()
        return opt

    def save(self, filename):
        config = self._config

        # general
        for key, t in self.GENERAL_OPTIONS:
            val = getattr(self, key)
            if isinstance(val, str):
                val = unicode(val, 'utf-8')
            config['general'][key] = val

        config['general']['recent_gameid'] = self.recent_gameid
        config['general']['favorite_gameid'] = self.favorite_gameid
        visible_buttons = [b for b in self.toolbar_vars
                           if self.toolbar_vars[b]]
        config['general']['visible_buttons'] = visible_buttons

        # sound_samples
        config['sound_samples'] = self.sound_samples

        # fonts
        for key, val in self.fonts.items():
            if key == 'default':
                continue
            if val is None:
                continue
            config['fonts'][key] = val

        # colors
        config['colors'] = self.colors

        # timeouts
        config['timeouts'] = self.timeouts

        # cardsets
        for key, val in self.cardset.items():
            config['cardsets'][str(key)] = val

        # games_geometry
        config['games_geometry'].clear()
        for key, val in self.games_geometry.items():
            config['games_geometry'][str(key)] = val

        config.write()
        ##config.write(sys.stdout); print


    def _getOption(self, section, key, t):
        config = self._config
        try:
            if config[section][key] is None:
                # invalid value
                return None
            if t == 'bool':
                val = config[section].as_bool(key)
            elif t == 'int':
                val = config[section].as_int(key)
            elif t == 'float':
                val = config[section].as_float(key)
            elif t == 'list':
                val = config[section][key]
                assert isinstance(val, (list, tuple))
            else: # str
                val = config[section][key]
        except KeyError:
            val = None
        except:
            print_err('load option error: %s: %s' % (section, key))
            traceback.print_exc()
            val = None
        return val

    def load(self, filename):

        # create ConfigObj instance
        try:
            config = configobj.ConfigObj(filename,
                                         configspec=configspec,
                                         encoding=self._config_encoding)
        except configobj.ParseError:
            traceback.print_exc()
            config = configobj.ConfigObj(configspec=configspec,
                                         encoding=self._config_encoding)
        self._config = config

        # create sections
        for section in (
            'general',
            'sound_samples',
            'fonts',
            'colors',
            'timeouts',
            'cardsets',
            'games_geometry',
            ):
            if section not in config:
                config[section] = {}

        # add initial comment
        if not os.path.exists(filename):
            config.initial_comment = ['-*- coding: %s -*-' %
                                      self._config_encoding]
            return

        # validation
        vdt = validate.Validator()
        res = config.validate(vdt)
        ##from pprint import pprint; pprint(res)
        if res is not True:
            for section, data in res.items():
                if data is True:
                    continue
                for key, value in data.items():
                    if value is False:
                        print_err('config file: validation error: '
                                  'section: "%s", key: "%s"' % (section, key))
                        config[section][key] = None


        # general
        for key, t in self.GENERAL_OPTIONS:
            val = self._getOption('general', key, t)
            if val == 'None':
                setattr(self, key, None)
            elif val is not None:
                setattr(self, key, val)

        settings.TRANSLATE_GAME_NAMES = self.translate_game_names

        recent_gameid = self._getOption('general', 'recent_gameid', 'list')
        if recent_gameid is not None:
            try:
                self.recent_gameid = [int(i) for i in recent_gameid]
            except:
                traceback.print_exc()

        favorite_gameid = self._getOption('general', 'favorite_gameid', 'list')
        if favorite_gameid is not None:
            try:
                self.favorite_gameid = [int(i) for i in favorite_gameid]
            except:
                traceback.print_exc()

        visible_buttons = self._getOption('general', 'visible_buttons', 'list')
        if visible_buttons is not None:
            for key in TOOLBAR_BUTTONS:
                self.toolbar_vars[key] = (key in visible_buttons)

        # sound_samples
        for key in self.sound_samples:
            val = self._getOption('sound_samples', key, 'bool')
            if val is not None:
                self.sound_samples[key] = val

        # fonts
        for key in self.fonts:
            if key == 'default':
                continue
            val = self._getOption('fonts', key, 'str')
            if val is not None:
                try:
                    val[1] = int(val[1])
                except:
                    traceback.print_exc()
                else:
                    val = tuple(val)
                    self.fonts[key] = val

        # colors
        for key in self.colors:
            val = self._getOption('colors', key, 'str')
            if val is not None:
                self.colors[key] = val

        # timeouts
        for key in self.timeouts:
            val = self._getOption('timeouts', key, 'float')
            if val is not None:
                self.timeouts[key] = val

        # cardsets
        for key in self.cardset:
            val = self._getOption('cardsets', str(key), 'list')
            if val is not None:
                try:
                    self.cardset[int(key)] = val
                except:
                    traceback.print_exc()

        # games_geometry
        for key, val in config['games_geometry'].items():
            try:
                val = [int(i) for i in val]
                assert len(val) == 2
                self.games_geometry[int(key)] = val
            except:
                traceback.print_exc()


