#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

import os
import sys
import traceback

import configobj

import pysollib.settings
from pysollib.mfxutil import USE_PIL, \
    get_default_resampling, print_err
from pysollib.mygettext import _
from pysollib.mygettext import myGettext
from pysollib.pysoltk import STATUSBAR_ITEMS, TOOLBAR_BUTTONS, TOOLKIT
from pysollib.resource import CSI

import validate

# ************************************************************************
# * Options
# ************************************************************************

_global_settings = {
    'mouse_button1': 1,
    'mouse_button2': 2,
    'mouse_button3': 3,
}


def calcCustomMouseButtonsBinding(binding_format):
    assert _global_settings['mouse_button1']
    return binding_format.format(
        mouse_button1=_global_settings['mouse_button1'],
        mouse_button2=_global_settings['mouse_button2'],
        mouse_button3=_global_settings['mouse_button3'],
    )


configspec = '''
[general]
last_version = list
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
free_hint = boolean
highlight_piles = boolean
highlight_cards = boolean
highlight_samerank = boolean
highlight_not_matching = boolean
peek_facedown = boolean
stuck_notification = boolean
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
demo_logo_style = string
pause_text_style = string
redeal_icon_style = string
dialog_icon_style = string
tree_icon_style = string
button_icon_style = string
tile_theme = string
default_tile_theme = string
toolbar = integer(0, 4)
toolbar_land = integer(0, 4)
toolbar_port = integer(0, 4)
toolbar_style = string
toolbar_relief = string
toolbar_compound = string
toolbar_size = integer(0, 2)
statusbar = boolean
num_recent_games = integer(10, 100)
last_gameid = integer
game_holded = integer
wm_maximized = boolean
wm_fullscreen = boolean
splashscreen = boolean
date_format = string
mouse_type = string
mouse_undo = boolean
negative_bottom = boolean
randomize_place = boolean
use_cardset_bottoms = boolean
dragcursor = boolean
save_games_geometry = boolean
game_geometry = int_list(min=2, max=2)
topmost_dialogs = boolean
sound = boolean
sound_mode = integer(0, 1)
sound_sample_volume = integer(0, 128)
sound_sample_buffer_size = integer(1, 4)
music = boolean
tabletile_name = string
tabletile_scale_method = integer
center_layout = boolean
recent_gameid = int_list
favorite_gameid = int_list
visible_buttons = string_list
visible_status = string_list
translate_game_names = boolean
solver_presets = string_list
solver_show_progress = boolean
solver_max_iterations = integer
solver_iterations_output_step = integer
solver_preset = string
display_win_message = boolean
language = string
table_zoom = list

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
edge = boolean
extra = boolean

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
keyboard_sel = string

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
1_1 = string_list(min=2, max=2)
2 = string_list(min=2, max=2)
3 = string_list(min=2, max=2)
4 = string_list(min=2, max=2)
5 = string_list(min=2, max=2)
6 = string_list(min=2, max=2)
7 = string_list(min=2, max=2)
8 = string_list(min=2, max=2)
9 = string_list(min=2, max=2)
10 = string_list(min=2, max=2)
11_3 = string_list(min=2, max=2)
11_4 = string_list(min=2, max=2)
11_5 = string_list(min=2, max=2)
11_6 = string_list(min=2, max=2)
11_7 = string_list(min=2, max=2)
11_8 = string_list(min=2, max=2)
11_9 = string_list(min=2, max=2)
11_10 = string_list(min=2, max=2)
12 = string_list(min=2, max=2)
scale_cards = boolean
scale_x = float
scale_y = float
auto_scale = boolean
preview_scale = boolean
spread_stacks = boolean
preserve_aspect_ratio = boolean
resampling = integer(0, 10)
'''.splitlines()


class Options:
    GENERAL_OPTIONS = [
        ('last_version', 'list'),
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
        ('free_hint', 'bool'),
        ('highlight_piles', 'bool'),
        ('highlight_cards', 'bool'),
        ('highlight_samerank', 'bool'),
        ('highlight_not_matching', 'bool'),
        ('peek_facedown', 'bool'),
        ('stuck_notification', 'bool'),
        ('mahjongg_show_removed', 'bool'),
        ('mahjongg_create_solvable', 'int'),
        ('shisen_show_hint', 'bool'),
        ('shisen_show_matching', 'bool'),
        ('accordion_deal_all', 'bool'),
        ('pegged_auto_remove', 'bool'),
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
        ('demo_logo_style', 'str'),
        ('pause_text_style', 'str'),
        ('redeal_icon_style', 'str'),
        ('dialog_icon_style', 'str'),
        ('tree_icon_style', 'str'),
        ('button_icon_style', 'str'),
        ('tile_theme', 'str'),
        ('default_tile_theme', 'str'),
        ('toolbar', 'int'),
        ('toolbar_land', 'int'),
        ('toolbar_port', 'int'),
        ('toolbar_style', 'str'),
        ('toolbar_relief', 'str'),
        ('toolbar_compound', 'str'),
        ('toolbar_size', 'int'),
        ('statusbar', 'bool'),
        # ('statusbar_game_number', 'bool'),
        # ('statusbar_stuck', 'bool'),
        # ('num_cards', 'bool'),
        # ('helpbar', 'bool'),
        ('num_recent_games', 'int'),
        ('last_gameid', 'int'),
        ('game_holded', 'int'),
        ('wm_maximized', 'bool'),
        ('wm_fullscreen', 'bool'),
        ('splashscreen', 'bool'),
        ('date_format', 'str'),
        ('mouse_type', 'str'),
        ('mouse_undo', 'bool'),
        ('negative_bottom', 'bool'),
        ('randomize_place', 'bool'),
        ('use_cardset_bottoms', 'bool'),
        # ('save_cardsets', 'bool'),
        ('dragcursor', 'bool'),
        ('save_games_geometry', 'bool'),
        ('topmost_dialogs', 'bool'),
        ('sound', 'bool'),
        ('sound_mode', 'int'),
        ('sound_sample_volume', 'int'),
        ('sound_music_volume', 'int'),
        ('sound_sample_buffer_size', 'int'),
        ('music', 'bool'),
        ('tabletile_name', 'str'),
        ('tabletile_scale_method', 'int'),
        ('center_layout', 'bool'),
        ('translate_game_names', 'bool'),
        ('solver_presets', 'list'),
        ('solver_show_progress', 'bool'),
        ('solver_max_iterations', 'int'),
        ('solver_iterations_output_step', 'int'),
        ('solver_preset', 'string'),
        ('mouse_button1', 'int'),
        ('mouse_button2', 'int'),
        ('mouse_button3', 'int'),
        # ('toolbar_vars', 'list'),
        # ('recent_gameid', 'list'),
        # ('favorite_gameid', 'list'),
        ('display_win_message', 'bool'),
        ('language', 'str'),
        # ('table_zoom', 'list'),
        ('fontscale', 'str'),
        # ('fontsizefactor', 'float'),
        ]

    def __init__(self):
        self._config = None             # configobj.ConfigObj instance
        self._config_encoding = 'utf-8'

        self.version_tuple = pysollib.settings.VERSION_TUPLE  # XXX
        self.saved = 0                  # XXX

        self.last_version = (2, 20, 1)
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
        self.free_hint = False
        self.highlight_piles = True
        self.highlight_cards = True
        self.highlight_samerank = True
        self.highlight_not_matching = True
        self.peek_facedown = False
        self.stuck_notification = False
        self.mahjongg_show_removed = False
        self.mahjongg_create_solvable = 2  # 0 - none, 1 - easy, 2 - hard
        self.accordion_deal_all = True
        self.pegged_auto_remove = True
        if TOOLKIT == 'kivy':
            self.mahjongg_create_solvable = 1  # 0 - none, 1 - easy, 2 - hard
        self.shisen_show_hint = True
        self.shisen_show_matching = False
        self.animations = 3             # default to Medium
        self.redeal_animation = True
        self.win_animation = True
        if TOOLKIT == 'kivy':
            self.redeal_animation = False
            self.win_animation = False
        self.flip_animation = True
        self.compact_stacks = True
        self.shadow = True
        self.shade = True
        self.shrink_face_down = True
        self.shade_filled_stacks = True
        self.demo_logo = True
        self.demo_logo_style = 'komika'
        self.pause_text_style = 'komika'
        self.redeal_icon_style = 'modern'
        self.dialog_icon_style = 'remix'
        self.tree_icon_style = 'remix'
        self.button_icon_style = 'none'
        self.tile_theme = 'default'
        self.default_tile_theme = 'default'
        self.toolbar = 1       # 0 == hide, 1,2,3,4 == top, bottom, left, right
        # used with 'kivy' version in addition:
        self.toolbar_land = 4  # (landscape)
        self.toolbar_port = 2  # (portrait)
        # 0 == hide,
        # 1,2,3,4 == top, bottom, left, right
        # self.toolbar_style = 'default'
        self.toolbar_style = 'remix'
        self.toolbar_relief = 'flat'
        self.toolbar_compound = 'none'  # icons only
        self.toolbar_size = 0
        self.toolbar_vars = {}
        for w in TOOLBAR_BUTTONS:
            self.toolbar_vars[w] = True  # show all buttons
        self.statusbar_vars = {}
        for w, x in STATUSBAR_ITEMS:
            self.statusbar_vars[w] = True
        self.statusbar = True
        # self.statusbar_game_number = False  # show game number in statusbar
        # self.statusbar_stuck = False        # show stuck indicator
        # self.num_cards = False
        # self.helpbar = False
        self.splashscreen = True
        self.date_format = '%m-%d'
        self.mouse_button1 = 1
        self.mouse_button2 = 2
        self.mouse_button3 = 3
        # mouse_type:  'drag-n-drop' or 'sticky-mouse' or 'point-n-click'
        if TOOLKIT == 'kivy':
            self.mouse_type = 'point-n-click'
        else:
            self.mouse_type = 'drag-n-drop'
        self.mouse_undo = False         # use mouse for undo/redo
        self.negative_bottom = True
        self.translate_game_names = True
        self.display_win_message = True
        self.language = ''
        self.table_zoom = [1.0, 0.0, 0.0]
        self.fontscale = 'default'        # (kivy,  platform defaults)
        # self.fontsizefactor = 1.0
        # sound
        self.sound = True
        self.sound_mode = 1
        self.sound_sample_volume = 75
        self.sound_music_volume = 100
        self.sound_sample_buffer_size = 1  # 1 - 4 (1024 - 4096 bytes)
        self.music = True
        self.sound_samples = {
            'areyousure': True,
            'autodrop': True,
            'autoflip': True,
            'autopilotlost': True,
            'autopilotwon': True,
            'deal': True,
            'dealwaste': True,
            'droppair': True,
            'drop': True,
            'edge': True,
            'extra': True,
            'flip': True,
            'move': True,
            'nomove': True,
            'redo': True,
            'startdrag': True,
            'turnwaste': True,
            'undo': True,
            'gamefinished': False,
            'gamelost': False,
            'gameperfect': False,
            'gamewon': False,
            }
        # fonts
        self.fonts = {
            "default": None,
            # "default": ("helvetica", 12),
            "sans": ("times",     12),  # for html
            "fixed": ("courier",   12),  # for html & log
            "small": ("helvetica", 12),
            "canvas_default": ("helvetica", 12),
            # "canvas_card": ("helvetica", 12),
            "canvas_fixed": ("courier",   12),
            "canvas_large": ("helvetica", 16),
            "canvas_small": ("helvetica", 10),
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
            'keyboard_sel': '#bf40bf',
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
        if TOOLKIT == 'kivy':
            self.favorite_gameid = [2, 7, 8, 19, 140, 116, 152, 176, 181,
                                    194, 207, 706, 721, 756, 903, 5034,
                                    11004, 14405, 14410, 15411, 22225]
        self.last_gameid = 0            # last game played
        self.game_holded = 0            # gameid or 0
        self.wm_maximized = 1
        self.wm_fullscreen = 0
        self.save_games_geometry = False
        self.topmost_dialogs = True
        # saved games geometry (gameid: (width, height))
        self.games_geometry = {}
        self.game_geometry = (0, 0)  # game geometry before exit
        self.offsets = {}           # cards offsets
        #
        self.randomize_place = False
        self.use_cardset_bottoms = False
        # self.save_cardsets = True
        self.dragcursor = True
        #
        self.scale_cards = False
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.auto_scale = True
        self.preview_scale = True
        self.spread_stacks = False
        self.center_layout = True
        self.preserve_aspect_ratio = True
        self.tabletile_scale_method = 0
        self.resampling = 0
        if USE_PIL:
            self.resampling = int(get_default_resampling())

        # solver
        self.solver_presets = [
            'none',
            'abra-kadabra',
            'blue-yonder',
            'conspiracy-theory',
            'cookie-monster',
            'cool-jives',
            'crooked-nose',
            'fools-gold',
            'good-intentions',
            'hello-world',
            'john-galt-line',
            'looking-glass',
            'one-big-family',
            'rin-tin-tin',
            'slick-rock',
            'the-last-mohican',
            'video-editing',
            'yellow-brick-road',
            ]
        self.solver_show_progress = True
        self.solver_max_iterations = 100000
        self.solver_iterations_output_step = 100
        self.solver_preset = 'video-editing'

    def setDefaults(self, top=None):
        WIN_SYSTEM = pysollib.settings.WIN_SYSTEM
        # toolbar
        # if WIN_SYSTEM == 'win32':
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
            if sys.getwindowsversion() >= (5, 1):  # xp
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
            self.tabletile_name = "Felt Green"  # name
        else:
            self.tabletile_name = None
        # cardsets
        c = "Standard"
        m = "Crystal Mahjongg"
        if sw < 800 or sh < 600:
            c = "2000"
        if TOOLKIT == 'kivy':
            c = "Standard"
            m = "Gnome Mahjongg 1"

        # if sw > 1024 and sh > 768:
        #    c = 'Dondorf'
        if USE_PIL:
            self.cardset = {
                0:                  {0: ("Neo", "")},
                CSI.TYPE_FRENCH:    {0: ("Neo", ""), 1: ("Neo", "")},
                CSI.TYPE_HANAFUDA:  {0: ("Louie Mantia Hanafuda", "")},
                CSI.TYPE_MAHJONGG:  {0: ("Uni Mahjongg", "")},
                CSI.TYPE_TAROCK:    {0: ("Neo Tarock", "")},
                CSI.TYPE_HEXADECK:  {0: ("Neo Hex", "")},
                CSI.TYPE_MUGHAL_GANJIFA: {0: ("Mughal Ganjifa XL", "")},
                # CSI.TYPE_NAVAGRAHA_GANJIFA: {0: ("Navagraha Ganjifa", "")},
                CSI.TYPE_NAVAGRAHA_GANJIFA:
                    {0: ("Dashavatara Ganjifa XL", "")},
                CSI.TYPE_DASHAVATARA_GANJIFA:
                    {0: ("Dashavatara Ganjifa XL", "")},
                CSI.TYPE_TRUMP_ONLY: {0: ("Next Matrix", "")},
                CSI.TYPE_MATCHING: {0: ("Neo", "")},
                CSI.TYPE_PUZZLE: {3: ("Dojouji Ukiyo E (3x3)", ""),
                                  4: ("Knave of Hearts (4x4)", ""),
                                  5: ("Victoria Falls (5x5)", ""),
                                  6: ("Hokusai Ukiyo E (6x6)", ""),
                                  7: ("Blaren (7x7)", ""),
                                  8: ("Mid Winter's Eve (8x8)", ""),
                                  9: ("The Card Players (9x9)", ""),
                                  10: ("Players Trumps (10x10)", "")},
                CSI.TYPE_ISHIDO: {0: ("Simple Ishido XL", "")},
            }
        else:
            self.cardset = {
                # game_type:        (cardset_name, back_file)
                0:                  {0: (c, "")},
                CSI.TYPE_FRENCH:    {0: (c, ""), 1: (c, "")},
                CSI.TYPE_HANAFUDA:  {0: ("Kintengu", "")},
                CSI.TYPE_MAHJONGG:  {0: (m, "")},
                CSI.TYPE_TAROCK:    {0: ("Vienna 2K", "")},
                CSI.TYPE_HEXADECK:  {0: ("Hex A Deck", "")},
                CSI.TYPE_MUGHAL_GANJIFA: {0: ("Mughal Ganjifa", "")},
                # CSI.TYPE_NAVAGRAHA_GANJIFA: {0: ("Navagraha Ganjifa", "")},
                CSI.TYPE_NAVAGRAHA_GANJIFA: {0: ("Dashavatara Ganjifa", "")},
                CSI.TYPE_DASHAVATARA_GANJIFA: {0: ("Dashavatara Ganjifa", "")},
                CSI.TYPE_TRUMP_ONLY: {0: ("Matrix", "")},
                CSI.TYPE_MATCHING: {0: (c, "")},
                CSI.TYPE_PUZZLE: {3: ("Dojouji Ukiyo E (3x3)", ""),
                                  4: ("Knave of Hearts (4x4)", ""),
                                  5: ("Victoria Falls (5x5)", ""),
                                  6: ("Hokusai Ukiyo E (6x6)", ""),
                                  7: ("Blaren (7x7)", ""),
                                  8: ("Mid Winter's Eve (8x8)", ""),
                                  9: ("The Card Players (9x9)", ""),
                                  10: ("Players Trumps (10x10)", "")},
                CSI.TYPE_ISHIDO: {0: ("Simple Ishido", "")},
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

        self.last_version = self.version_tuple

        # general
        for key, t in self.GENERAL_OPTIONS:
            val = getattr(self, key)
            if isinstance(val, str):
                if sys.version_info < (3,):
                    val = str(val, 'utf-8')
            config['general'][key] = val

        config['general']['recent_gameid'] = self.recent_gameid
        config['general']['favorite_gameid'] = self.favorite_gameid
        config['general']['table_zoom'] = self.table_zoom
        visible_buttons = [b for b in self.toolbar_vars
                           if self.toolbar_vars[b]]
        config['general']['visible_buttons'] = visible_buttons
        visible_status = [b for b in self.statusbar_vars
                          if self.statusbar_vars[b]]
        config['general']['visible_status'] = visible_status
        if 'none' in config['general']['solver_presets']:
            config['general']['solver_presets'].remove('none')

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
            for key2, val2 in val.items():
                if key2 > 0:
                    config['cardsets'][str(key) + "_" + str(key2)] = val2
                else:
                    config['cardsets'][str(key)] = val2
        for key in ('scale_cards', 'scale_x', 'scale_y',
                    'auto_scale', 'preview_scale', 'spread_stacks',
                    'preserve_aspect_ratio', 'resampling'):
            config['cardsets'][key] = getattr(self, key)

        # games_geometry
        config['games_geometry'].clear()
        for key, val in self.games_geometry.items():
            config['games_geometry'][str(key)] = val
        config['general']['game_geometry'] = self.game_geometry

        # offsets
        for key, val in self.offsets.items():
            config['offsets'][key] = val

        config.write()
        # config.write(sys.stdout); print

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
            else:  # str
                val = config[section][key]
        except KeyError:
            val = None
        except Exception:
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
            'offsets',
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
        # from pprint import pprint; pprint(res)
        if isinstance(res, dict):
            for section, data in res.items():
                if data is True:
                    continue
                for key, value in data.items():
                    if value is False:
                        config[section][key] = None

        # general
        for key, t in self.GENERAL_OPTIONS:
            val = self._getOption('general', key, t)
            if val == 'None':
                setattr(self, key, None)
            elif val is not None:
                setattr(self, key, val)

        pysollib.settings.TRANSLATE_GAME_NAMES = self.translate_game_names

        recent_gameid = self._getOption('general', 'recent_gameid', 'list')
        if recent_gameid is not None:
            try:
                self.recent_gameid = [int(i) for i in recent_gameid]
            except Exception:
                traceback.print_exc()

        favorite_gameid = self._getOption('general', 'favorite_gameid', 'list')
        if favorite_gameid is not None:
            try:
                self.favorite_gameid = [int(i) for i in favorite_gameid]
            except Exception:
                traceback.print_exc()

        table_zoom = self._getOption('general', 'table_zoom', 'list')
        if table_zoom is not None:
            try:
                self.table_zoom = [float(i) for i in table_zoom]
            except Exception:
                traceback.print_exc()

        visible_buttons = self._getOption('general', 'visible_buttons', 'list')
        if visible_buttons is not None:
            for key in TOOLBAR_BUTTONS:
                self.toolbar_vars[key] = (key in visible_buttons)
        visible_status = self._getOption('general', 'visible_status', 'list')
        if visible_status is not None:
            for key, label in STATUSBAR_ITEMS:
                self.statusbar_vars[key] = (key in visible_status)

        myGettext.language = self.language

        # solver
        solver_presets = self._getOption('general', 'solver_presets', 'list')
        if solver_presets is not None:
            if 'none' not in solver_presets:
                solver_presets.insert(0, 'none')
            self.solver_presets = solver_presets

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
                except Exception:
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
            for key2 in self.cardset[key]:
                if key2 > 0:
                    val = self._getOption('cardsets',
                                          str(key) + "_" + str(key2), 'list')
                else:
                    val = self._getOption('cardsets', str(key), 'list')
                if val is not None:
                    try:
                        self.cardset[int(key)][int(key2)] = val
                    except Exception:
                        traceback.print_exc()
        for key, t in (('scale_cards', 'bool'),
                       ('scale_x', 'float'),
                       ('scale_y', 'float'),
                       ('auto_scale', 'bool'),
                       ('preview_scale', 'bool'),
                       ('spread_stacks', 'bool'),
                       ('preserve_aspect_ratio', 'bool'),
                       ('resampling', 'int')):
            val = self._getOption('cardsets', key, t)
            if val is not None:
                setattr(self, key, val)

        # games_geometry
        for key, val in config['games_geometry'].items():
            try:
                val = [int(i) for i in val]
                assert len(val) == 2
                self.games_geometry[int(key)] = val
            except Exception:
                traceback.print_exc()
        game_geometry = self._getOption('general', 'game_geometry', 'list')
        if game_geometry is not None:
            try:
                self.game_geometry = tuple(int(i) for i in game_geometry)
            except Exception:
                traceback.print_exc()

        # cards offsets
        for key, val in config['offsets'].items():
            try:
                val = [int(i) for i in val]
                assert len(val) == 2
                self.offsets[key] = val
            except Exception:
                traceback.print_exc()

        # mouse buttons swap
        def _positive(button):
            return max([button, 1])
        _global_settings['mouse_button1'] = _positive(self.mouse_button1)
        _global_settings['mouse_button2'] = _positive(self.mouse_button2)
        _global_settings['mouse_button3'] = _positive(self.mouse_button3)

    def calcCustomMouseButtonsBinding(self, binding_format):
        """docstring for calcCustomMouseButtonsBinding"""
        def _positive(button):
            return max([button, 1])
        return binding_format.format(
            mouse_button1=_positive(self.mouse_button1),
            mouse_button2=_positive(self.mouse_button2),
            mouse_button3=_positive(self.mouse_button3),
        )
