import math
import os
import platform
import re
import sys
import tkinter

from pysollib.gamedb import GI
from pysollib.hint import PySolHintLayoutImportError
from pysollib.mfxutil import Image, USE_PIL
from pysollib.mfxutil import Struct, kwdefault
from pysollib.mygettext import _, n_
from pysollib.settings import SELECT_GAME_MENU
from pysollib.settings import TITLE, WIN_SYSTEM
from pysollib.settings import USE_FREECELL_SOLVER
from pysollib.ui.tktile.tkconst import COMPOUNDS, CURSOR_WATCH, EVENT_HANDLED
from pysollib.ui.tktile.tkconst import EVENT_PROPAGATE
from pysollib.ui.tktile.tkconst import STATUSBAR_ITEMS, TOOLBAR_BUTTONS
from pysollib.ui.tktile.tkutil import after_idle, bind

from six.moves import tkinter_tkfiledialog


def createToolbarMenu(menubar, menu):
    tearoff = menu.cget('tearoff')
    data_dir = os.path.join(menubar.app.dataloader.dir, 'images', 'toolbar')
    submenu = MfxMenu(menu, label=n_('Icon Style'), tearoff=tearoff)
    styledirs = os.listdir(data_dir)
    styledirs.sort()
    for f in styledirs:
        d = os.path.join(data_dir, f)
        if os.path.isdir(d) and os.path.exists(os.path.join(d, 'small')):
            name = f.replace('_', ' ').capitalize()
            submenu.add_radiobutton(
              label=name,
              variable=menubar.tkopt.toolbar_style,
              value=f, command=menubar.mOptToolbarStyle)
    submenu = MfxMenu(menu, label=n_('Icon Size'), tearoff=tearoff)
    submenu.add_radiobutton(label=n_("Small icons"),
                            variable=menubar.tkopt.toolbar_size, value=0,
                            command=menubar.mOptToolbarSize)
    submenu.add_radiobutton(label=n_("Large icons"),
                            variable=menubar.tkopt.toolbar_size, value=1,
                            command=menubar.mOptToolbarSize)
    submenu.add_radiobutton(label=n_("Extra large icons"),
                            variable=menubar.tkopt.toolbar_size, value=2,
                            command=menubar.mOptToolbarSize)
    submenu = MfxMenu(menu, label=n_('Compound'), tearoff=tearoff)
    for comp, label in COMPOUNDS:
        submenu.add_radiobutton(
            label=label, variable=menubar.tkopt.toolbar_compound,
            value=comp, command=menubar.mOptToolbarCompound)
    submenu = MfxMenu(menu, label=n_('Visible buttons'), tearoff=tearoff)
    for w in TOOLBAR_BUTTONS:
        submenu.add_checkbutton(
            label=_(w.capitalize()),
            variable=menubar.tkopt.toolbar_vars[w],
            command=lambda m=menubar, w=w: m.mOptToolbarConfig(w))
    menu.add_separator()
    menu.add_radiobutton(label=n_("Hide"),
                         variable=menubar.tkopt.toolbar, value=0,
                         command=menubar.mOptToolbar)
    menu.add_radiobutton(label=n_("Top"),
                         variable=menubar.tkopt.toolbar, value=1,
                         command=menubar.mOptToolbar)
    menu.add_radiobutton(label=n_("Bottom"),
                         variable=menubar.tkopt.toolbar, value=2,
                         command=menubar.mOptToolbar)
    menu.add_radiobutton(label=n_("Left"),
                         variable=menubar.tkopt.toolbar, value=3,
                         command=menubar.mOptToolbar)
    menu.add_radiobutton(label=n_("Right"),
                         variable=menubar.tkopt.toolbar, value=4,
                         command=menubar.mOptToolbar)


def createStatusbarMenu(menubar, menu):
    menu.add_checkbutton(
        label=n_("Show &statusbar"), variable=menubar.tkopt.statusbar,
        command=menubar.mOptStatusbar)
    menu.add_separator()
    for comp, label in STATUSBAR_ITEMS:
        menu.add_checkbutton(
            label=label,
            variable=menubar.tkopt.statusbar_vars[comp],
            command=lambda m=menubar, w=comp: m.mOptStatusbarConfig(w))


def createOtherGraphicsMenu(menubar, menu):
    tearoff = menu.cget('tearoff')
    data_dir = os.path.join(menubar.app.dataloader.dir, 'images', 'buttons')
    submenu = MfxMenu(menu, label=n_('&Button icons'), tearoff=tearoff)
    styledirs = os.listdir(data_dir)
    styledirs.append("none")
    styledirs.sort()
    for f in styledirs:
        d = os.path.join(data_dir, f)
        if (os.path.isdir(d) and os.path.exists(os.path.join(d))) \
                or f == "none":
            name = f.replace('_', ' ').capitalize()
            submenu.add_radiobutton(
                label=name,
                variable=menubar.tkopt.button_icon_style,
                value=f, command=menubar.mOptButtonIconStyle)
    data_dir = os.path.join(menubar.app.dataloader.dir, 'images', 'demo')
    submenu = MfxMenu(menu, label=n_('&Demo logo'), tearoff=tearoff)
    styledirs = os.listdir(data_dir)
    styledirs.append("none")
    styledirs.sort()
    for f in styledirs:
        d = os.path.join(data_dir, f)
        if (os.path.isdir(d) and os.path.exists(os.path.join(d))) \
                or f == "none":
            name = f.replace('_', ' ').capitalize()
            submenu.add_radiobutton(
                label=name,
                variable=menubar.tkopt.demo_logo_style,
                value=f, command=menubar.mOptDemoLogoStyle)
    data_dir = os.path.join(menubar.app.dataloader.dir, 'images', 'dialog')
    submenu = MfxMenu(menu, label=n_('D&ialog icons'), tearoff=tearoff)
    styledirs = os.listdir(data_dir)
    styledirs.sort()
    for f in styledirs:
        d = os.path.join(data_dir, f)
        if os.path.isdir(d) and os.path.exists(os.path.join(d)):
            name = f.replace('_', ' ').capitalize()
            submenu.add_radiobutton(
                label=name,
                variable=menubar.tkopt.dialog_icon_style,
                value=f, command=menubar.mOptDialogIconStyle)
    data_dir = os.path.join(menubar.app.dataloader.dir, 'images', 'pause')
    submenu = MfxMenu(menu, label=n_('&Pause text'), tearoff=tearoff)
    styledirs = os.listdir(data_dir)
    styledirs.sort()
    for f in styledirs:
        d = os.path.join(data_dir, f)
        if os.path.isdir(d) and os.path.exists(os.path.join(d)):
            name = f.replace('_', ' ').capitalize()
            submenu.add_radiobutton(
                label=name,
                variable=menubar.tkopt.pause_text_style,
                value=f, command=menubar.mOptPauseTextStyle)
    data_dir = os.path.join(menubar.app.dataloader.dir, 'images',
                            'redealicons')
    submenu = MfxMenu(menu, label=n_('&Redeal icons'), tearoff=tearoff)
    styledirs = os.listdir(data_dir)
    styledirs.sort()
    for f in styledirs:
        d = os.path.join(data_dir, f)
        if os.path.isdir(d) and os.path.exists(os.path.join(d)):
            name = f.replace('_', ' ').capitalize()
            submenu.add_radiobutton(
                label=name,
                variable=menubar.tkopt.redeal_icon_style,
                value=f, command=menubar.mOptRedealIconStyle)
    data_dir = os.path.join(menubar.app.dataloader.dir, 'images', 'tree')
    submenu = MfxMenu(menu, label=n_('&Tree icons'), tearoff=tearoff)
    styledirs = os.listdir(data_dir)
    styledirs.sort()
    for f in styledirs:
        d = os.path.join(data_dir, f)
        if os.path.isdir(d) and os.path.exists(os.path.join(d)):
            name = f.replace('_', ' ').capitalize()
            submenu.add_radiobutton(
                label=name,
                variable=menubar.tkopt.tree_icon_style,
                value=f, command=menubar.mOptTreeIconStyle)


def createResamplingMenu(menubar, menu):
    tearoff = menu.cget('tearoff')
    submenu = MfxMenu(menu, label=n_('R&esampling'), tearoff=tearoff)

    submenu.add_radiobutton(label=n_("&Nearest Neighbor"),
                            variable=menubar.tkopt.resampling,
                            value=int(Image.NEAREST),
                            command=menubar.mOptResampling)
    if hasattr(Image, "BILINEAR"):
        submenu.add_radiobutton(label=n_("&Bilinear"),
                                variable=menubar.tkopt.resampling,
                                value=int(Image.BILINEAR),
                                command=menubar.mOptResampling)
    if hasattr(Image, "BICUBIC"):
        submenu.add_radiobutton(label=n_("B&icubic"),
                                variable=menubar.tkopt.resampling,
                                value=int(Image.BICUBIC),
                                command=menubar.mOptResampling)
    if hasattr(Image, "LANCZOS"):
        submenu.add_radiobutton(label=n_("&Lanczos"),
                                variable=menubar.tkopt.resampling,
                                value=int(Image.LANCZOS),
                                command=menubar.mOptResampling)
    elif hasattr(Image, "ANTIALIAS"):
        submenu.add_radiobutton(label=n_("&Antialiasing"),
                                variable=menubar.tkopt.resampling,
                                value=int(Image.ANTIALIAS),
                                command=menubar.mOptResampling)
    if hasattr(Image, "BOX"):
        submenu.add_radiobutton(label=n_("B&ox"),
                                variable=menubar.tkopt.resampling,
                                value=int(Image.BOX),
                                command=menubar.mOptResampling)
    if hasattr(Image, "HAMMING"):
        submenu.add_radiobutton(label=n_("&Hamming"),
                                variable=menubar.tkopt.resampling,
                                value=int(Image.HAMMING),
                                command=menubar.mOptResampling)


# ************************************************************************
# *
# ************************************************************************

class MfxMenubar(tkinter.Menu):
    addPath = None

    def __init__(self, master, **kw):
        self.name = kw["name"]
        tearoff = 0
        self.n = kw["tearoff"] = int(kw.get("tearoff", tearoff))
        tkinter.Menu.__init__(self, master, **kw)

    def labeltoname(self, label):
        # print label, type(label)
        name = re.sub(r"[^0-9a-zA-Z]", "", label).lower()
        label = _(label)
        underline = label.find('&')
        if underline >= 0:
            label = label.replace('&', '')
        return name, label, underline

    def add(self, itemType, cnf={}):
        label = cnf.get("label")
        if label:
            name = cnf.get('name')
            if name:
                del cnf['name']  # TclError: unknown option "-name"
            else:
                name, label, underline = self.labeltoname(label)
                cnf["underline"] = cnf.get("underline", underline)
            cnf["label"] = label
            if name and self.addPath:
                path = str(self._w) + "." + name
                self.addPath(path, self, self.n, cnf.get("menu"))
        tkinter.Menu.add(self, itemType, cnf)
        self.n = self.n + 1


class MfxMenu(MfxMenubar):
    def __init__(self, master, label, underline=None, **kw):
        if 'name' in kw:
            name, label_underline = kw['name'], -1
        else:
            name, label, label_underline = self.labeltoname(label)
        kwdefault(kw, name=name)
        MfxMenubar.__init__(self, master, **kw)
        if underline is None:
            underline = label_underline
        if master:
            master.add_cascade(
                menu=self, name=name, label=label, underline=underline)


class PysolMenubarTkCommon:
    def __init__(self, app, top, progress=None):
        self._createTkOpt()
        self._setOptions()
        # init columnbreak
        self.cb_max = int(self.top.winfo_screenheight()//23)
        #  sh = self.top.winfo_screenheight()
        #  self.cb_max = 22
        #  if sh >= 600: self.cb_max = 27
        #  if sh >= 768: self.cb_max = 32
        #  if sh >= 1024: self.cb_max = 40
        self.progress = progress
        # create menus
        self.menubar = None
        self.menupath = {}
        self.keybindings = {}
        self._createMenubar()
        self.top = top

        if self.progress:
            self.progress.update(step=1)

        # set the menubar
        self.updateBackgroundImagesMenu()
        self.top.config(menu=self.menubar)

    def _createTkOpt(self):
        # structure to convert menu-options to Toolkit variables
        self.tkopt = Struct(
            gameid=tkinter.IntVar(),
            gameid_popular=tkinter.IntVar(),
            comment=tkinter.BooleanVar(),
            autofaceup=tkinter.BooleanVar(),
            autodrop=tkinter.BooleanVar(),
            autodeal=tkinter.BooleanVar(),
            quickplay=tkinter.BooleanVar(),
            undo=tkinter.BooleanVar(),
            bookmarks=tkinter.BooleanVar(),
            hint=tkinter.BooleanVar(),
            free_hint=tkinter.BooleanVar(),
            shuffle=tkinter.BooleanVar(),
            highlight_piles=tkinter.BooleanVar(),
            highlight_cards=tkinter.BooleanVar(),
            highlight_samerank=tkinter.BooleanVar(),
            highlight_not_matching=tkinter.BooleanVar(),
            peek_facedown=tkinter.BooleanVar(),
            stuck_notification=tkinter.BooleanVar(),
            mahjongg_show_removed=tkinter.BooleanVar(),
            shisen_show_hint=tkinter.BooleanVar(),
            accordion_deal_all=tkinter.BooleanVar(),
            pegged_auto_remove=tkinter.BooleanVar(),
            sound=tkinter.BooleanVar(),
            auto_scale=tkinter.BooleanVar(),
            preserve_aspect_ratio=tkinter.BooleanVar(),
            resampling=tkinter.IntVar(),
            spread_stacks=tkinter.BooleanVar(),
            center_layout=tkinter.BooleanVar(),
            save_games_geometry=tkinter.BooleanVar(),
            cardback=tkinter.IntVar(),
            tabletile=tkinter.IntVar(),
            animations=tkinter.IntVar(),
            redeal_animation=tkinter.BooleanVar(),
            win_animation=tkinter.BooleanVar(),
            flip_animation=tkinter.BooleanVar(),
            shadow=tkinter.BooleanVar(),
            shade=tkinter.BooleanVar(),
            shade_filled_stacks=tkinter.BooleanVar(),
            compact_stacks=tkinter.BooleanVar(),
            shrink_face_down=tkinter.BooleanVar(),
            randomize_place=tkinter.BooleanVar(),
            toolbar=tkinter.IntVar(),
            toolbar_style=tkinter.StringVar(),
            toolbar_relief=tkinter.StringVar(),
            toolbar_compound=tkinter.StringVar(),
            toolbar_size=tkinter.IntVar(),
            statusbar=tkinter.BooleanVar(),
            num_cards=tkinter.BooleanVar(),
            helpbar=tkinter.BooleanVar(),
            splashscreen=tkinter.BooleanVar(),
            button_icon_style=tkinter.StringVar(),
            demo_logo=tkinter.BooleanVar(),
            demo_logo_style=tkinter.StringVar(),
            pause_text_style=tkinter.StringVar(),
            redeal_icon_style=tkinter.StringVar(),
            dialog_icon_style=tkinter.StringVar(),
            tree_icon_style=tkinter.StringVar(),
            mouse_type=tkinter.StringVar(),
            mouse_undo=tkinter.BooleanVar(),
            negative_bottom=tkinter.BooleanVar(),
            pause=tkinter.BooleanVar(),
            theme=tkinter.StringVar(),
            toolbar_vars={},
            statusbar_vars={},
        )
        for w in TOOLBAR_BUTTONS:
            self.tkopt.toolbar_vars[w] = tkinter.BooleanVar()
        for w, x in STATUSBAR_ITEMS:
            self.tkopt.statusbar_vars[w] = tkinter.BooleanVar()

    def _setOptions(self):
        tkopt, opt = self.tkopt, self.app.opt
        # set state of the menu items
        tkopt.autofaceup.set(opt.autofaceup)
        tkopt.autodrop.set(opt.autodrop)
        tkopt.autodeal.set(opt.autodeal)
        tkopt.quickplay.set(opt.quickplay)
        tkopt.undo.set(opt.undo)
        tkopt.hint.set(opt.hint)
        tkopt.free_hint.set(opt.free_hint)
        tkopt.shuffle.set(opt.shuffle)
        tkopt.bookmarks.set(opt.bookmarks)
        tkopt.highlight_piles.set(opt.highlight_piles)
        tkopt.highlight_cards.set(opt.highlight_cards)
        tkopt.highlight_samerank.set(opt.highlight_samerank)
        tkopt.highlight_not_matching.set(opt.highlight_not_matching)
        tkopt.peek_facedown.set(opt.peek_facedown)
        tkopt.stuck_notification.set(opt.stuck_notification)
        tkopt.shrink_face_down.set(opt.shrink_face_down)
        tkopt.shade_filled_stacks.set(opt.shade_filled_stacks)
        tkopt.compact_stacks.set(opt.compact_stacks)
        tkopt.randomize_place.set(opt.randomize_place)
        tkopt.mahjongg_show_removed.set(opt.mahjongg_show_removed)
        tkopt.shisen_show_hint.set(opt.shisen_show_hint)
        tkopt.accordion_deal_all.set(opt.accordion_deal_all)
        tkopt.pegged_auto_remove.set(opt.pegged_auto_remove)
        tkopt.sound.set(opt.sound)
        tkopt.auto_scale.set(opt.auto_scale)
        tkopt.preserve_aspect_ratio.set(opt.preserve_aspect_ratio)
        tkopt.resampling.set(opt.resampling)
        tkopt.spread_stacks.set(opt.spread_stacks)
        tkopt.center_layout.set(opt.center_layout)
        tkopt.save_games_geometry.set(opt.save_games_geometry)
        tkopt.cardback.set(self.app.cardset.backindex)
        tkopt.tabletile.set(self.app.tabletile_index)
        tkopt.animations.set(opt.animations)
        tkopt.redeal_animation.set(opt.redeal_animation)
        tkopt.win_animation.set(opt.win_animation)
        tkopt.flip_animation.set(opt.flip_animation)
        tkopt.shadow.set(opt.shadow)
        tkopt.shade.set(opt.shade)
        tkopt.toolbar.set(opt.toolbar)
        tkopt.toolbar_style.set(opt.toolbar_style)
        tkopt.toolbar_relief.set(opt.toolbar_relief)
        tkopt.toolbar_compound.set(opt.toolbar_compound)
        tkopt.toolbar_size.set(opt.toolbar_size)
        tkopt.toolbar_relief.set(opt.toolbar_relief)
        tkopt.statusbar.set(opt.statusbar)
        # tkopt.num_cards.set(opt.num_cards)
        # tkopt.helpbar.set(opt.helpbar)
        tkopt.button_icon_style.set(opt.button_icon_style)
        tkopt.demo_logo.set(opt.demo_logo)
        if opt.demo_logo:
            tkopt.demo_logo_style.set(opt.demo_logo_style)
        else:
            tkopt.demo_logo_style.set("none")
        tkopt.pause_text_style.set(opt.pause_text_style)
        tkopt.redeal_icon_style.set(opt.redeal_icon_style)
        tkopt.dialog_icon_style.set(opt.dialog_icon_style)
        tkopt.tree_icon_style.set(opt.tree_icon_style)
        tkopt.splashscreen.set(opt.splashscreen)
        tkopt.mouse_type.set(opt.mouse_type)
        tkopt.mouse_undo.set(opt.mouse_undo)
        tkopt.negative_bottom.set(opt.negative_bottom)
        for w in TOOLBAR_BUTTONS:
            tkopt.toolbar_vars[w].set(opt.toolbar_vars.get(w, False))
        for w, x in STATUSBAR_ITEMS:
            tkopt.statusbar_vars[w].set(opt.statusbar_vars.get(w, False))

    def connectGame(self, game):
        self.game = game
        if game is None:
            return
        assert self.app is game.app
        tkopt = self.tkopt
        tkopt.gameid.set(game.id)
        tkopt.gameid_popular.set(game.id)
        tkopt.comment.set(bool(game.gsaveinfo.comment))
        tkopt.pause.set(self.game.pause)
        if game.canFindCard():
            self._connect_game_find_card_dialog(game)
        else:
            self._destroy_find_card_dialog()
        if game.canShowFullPicture():
            self._connect_game_full_picture_dialog(game)
        else:
            self._destroy_full_picture_dialog()
        self._connect_game_solver_dialog(game)

    # create a GTK-like path
    def _addPath(self, path, menu, index, submenu):
        if path not in self.menupath:
            # print path, menu, index, submenu
            self.menupath[path] = (menu, index, submenu)

    def _getEnabledState(self, enabled):
        if enabled:
            return "normal"
        return "disabled"

    def updateProgress(self):
        if self.progress:
            self.progress.update(step=1)

    def _createMenubar(self):
        MfxMenubar.addPath = self._addPath
        kw = {"name": "menubar"}
        self.menubar = MfxMenubar(self.top, **kw)

        # init keybindings
        bind(self.top, "<KeyPress>", self._keyPressHandler)

        m = "Ctrl-"
        if sys.platform == "darwin":
            m = "Cmd-"

        if WIN_SYSTEM == "aqua":
            applemenu = MfxMenu(self.menubar, "apple")
            applemenu.add_command(
                label=_("&About %s") % TITLE, command=self.mHelpAbout)

        menu = MfxMenu(self.menubar, n_("&File"))
        menu.add_command(
            label=n_("&New game"), command=self.mNewGame, accelerator="N")
        submenu = MfxMenu(menu, label=n_("R&ecent games"))
        # menu.add_command(label=n_("Select &random game"),
        #   command=self.mSelectRandomGame, accelerator=m+"R")
        submenu = MfxMenu(menu, label=n_("Select &random game"))
        submenu.add_command(
            label=n_("&All games"), command=lambda:
            self.mSelectRandomGame('all'), accelerator=m+"R")
        submenu.add_separator()
        submenu.add_command(
            label=n_("&Games played"),
            command=lambda: self.mSelectRandomGame('played'))
        submenu.add_command(
            label=n_("Games played and &won"),
            command=lambda: self.mSelectRandomGame('won'))
        submenu.add_command(
            label=n_("Games played and &not won"),
            command=lambda: self.mSelectRandomGame('not won'))
        submenu.add_command(
            label=n_("Games not &played"),
            command=lambda: self.mSelectRandomGame('not played'))
        menu.add_command(
            label=n_("Select game by nu&mber..."),
            command=self.mSelectGameById, accelerator=m+"M")
        menu.add_command(
            label=n_("Next game by num&ber"),
            command=self.mNewGameWithNextId, accelerator=m+"N")
        menu.add_separator()
        submenu = MfxMenu(menu, label=n_("Fa&vorite games"))
        menu.add_command(label=n_("A&dd to favorites"), command=self.mAddFavor)
        menu.add_command(
            label=n_("Remove &from favorites"),
            command=self.mDelFavor)
        menu.add_separator()
        menu.add_command(
            label=n_("&Open..."),
            command=self.mOpen, accelerator=m+"O")
        menu.add_command(
            label=n_("&Save"),
            command=self.mSave, accelerator=m+"S")
        menu.add_command(label=n_("Save &as..."), command=self.mSaveAs)
        menu.add_command(
            label=n_("E&xport current layout..."),
            command=self.mExportCurrentLayout)
        menu.add_command(
            label=n_("&Import starting layout..."),
            command=self.mImportStartingLayout)
        menu.add_separator()
        menu.add_command(
            label=n_("&Hold and quit"),
            command=self.mHoldAndQuit, accelerator=m+"X")
        if WIN_SYSTEM != "aqua":
            menu.add_command(
                label=n_("&Quit"),
                command=self.mQuit, accelerator=m+"Q")

        if self.progress:
            self.progress.update(step=1)

        menu = MfxMenu(self.menubar, label=n_("&Select"))
        self._addSelectGameMenu(menu)

        if self.progress:
            self.progress.update(step=1)

        menu = MfxMenu(self.menubar, label=n_("&Edit"))
        menu.add_command(
            label=n_("&Undo"),
            command=self.mUndo, accelerator="Z")
        menu.add_command(
            label=n_("&Redo"),
            command=self.mRedo, accelerator="R")
        menu.add_command(label=n_("Redo &all"), command=self.mRedoAll)

        menu.add_separator()
        menu.add_command(
            label=n_("Restart"),
            command=self.mRestart, accelerator=m+"G")

        menu.add_separator()
        submenu = MfxMenu(menu, label=n_("&Set bookmark"))
        for i in range(9):
            label = _("Bookmark %d") % (i + 1)
            submenu.add_command(
                label=label,
                command=lambda i=i: self.mSetBookmark(i))
        submenu = MfxMenu(menu, label=n_("Go&to bookmark"))
        for i in range(9):
            label = _("Bookmark %d") % (i + 1)
            acc = m + "%d" % (i + 1)
            submenu.add_command(
                label=label,
                command=lambda i=i: self.mGotoBookmark(i), accelerator=acc)
        menu.add_command(
            label=n_("&Clear bookmarks"),
            command=self.mClearBookmarks)

        menu.add_separator()
        menu.add_command(
            label=n_("Solitaire &Wizard..."),
            command=self.mWizard)
        menu.add_command(
            label=n_("&Edit current game..."),
            command=self.mWizardEdit)
        menu.add_command(
            label=n_("&Delete current game"),
            command=self.mWizardDelete)

        menu = MfxMenu(self.menubar, label=n_("&Game"))
        menu.add_command(
            label=n_("&Deal cards"),
            command=self.mDeal, accelerator="D")
        menu.add_command(
            label=n_("&Auto drop"),
            command=self.mDrop, accelerator="A")
        menu.add_command(
            label=n_("Shu&ffle tiles"),
            command=self.mShuffle, accelerator="F")
        menu.add_checkbutton(
            label=n_("&Pause"), variable=self.tkopt.pause,
            command=self.mPause, accelerator="P")
        # menu.add_command(
        #    label=n_("&Pause"), command=self.mPause, accelerator="P")
        menu.add_separator()
        menu.add_command(
            label=n_("S&tatus..."),
            command=lambda: self.mPlayerStats(mode=100), accelerator=m+"Y")
        menu.add_command(
            label=n_("&Statistics..."),
            command=self.mPlayerStats, accelerator=m+"T")
        menu.add_command(
            label=n_("D&emo statistics..."),
            command=lambda: self.mPlayerStats(mode=1101))
        menu.add_command(
            label=n_("Log..."),
            command=lambda: self.mPlayerStats(mode=103))
        menu.add_separator()
        menu.add_checkbutton(
            label=n_("&Comments..."), variable=self.tkopt.comment,
            command=self.mEditGameComment)

        menu = MfxMenu(self.menubar, label=n_("&Assist"))
        menu.add_command(
            label=n_("&Hint"),
            command=self.mHint, accelerator="H")
        menu.add_command(
            label=n_("Highlight p&iles"),
            command=self.mHighlightPiles, accelerator="I")
        menu.add_command(
            label=n_("&Find card..."),
            command=self.mFindCard, accelerator="F3")
        menu.add_command(
            label=n_("Sh&ow full picture..."),
            command=self.mFullPicture)
        menu.add_separator()
        menu.add_command(
            label=n_("&Demo"),
            command=self.mDemo, accelerator=m+"D")
        menu.add_command(
            label=n_("Demo (&all games)"),
            command=self.mMixedDemo)
        if USE_FREECELL_SOLVER:
            menu.add_command(label=n_("&Solver..."), command=self.mSolver)
        else:
            menu.add_command(label=n_("&Solver..."), state='disabled')
        menu.add_separator()
        menu.add_command(
            label=n_("&Piles description"),
            command=self.mStackDesk, accelerator="F2")

        if self.progress:
            self.progress.update(step=1)

        menu = MfxMenu(self.menubar, label=n_("&Options"))
        menu.add_command(
            label=n_("&Player options..."),
            command=self.mOptPlayerOptions, accelerator=m+'P')
        submenu = MfxMenu(menu, label=n_("&Automatic play"))
        submenu.add_checkbutton(
            label=n_("Auto &face up"), variable=self.tkopt.autofaceup,
            command=self.mOptAutoFaceUp)
        submenu.add_checkbutton(
            label=n_("A&uto drop"), variable=self.tkopt.autodrop,
            command=self.mOptAutoDrop)
        submenu.add_checkbutton(
            label=n_("Auto &deal"), variable=self.tkopt.autodeal,
            command=self.mOptAutoDeal)
        submenu.add_separator()
        submenu.add_checkbutton(
            label=n_("&Quick play"), variable=self.tkopt.quickplay,
            command=self.mOptQuickPlay)
        submenu = MfxMenu(menu, label=n_("Assist &level"))
        submenu.add_checkbutton(
            label=n_("Enable &undo"), variable=self.tkopt.undo,
            command=self.mOptEnableUndo)
        submenu.add_checkbutton(
            label=n_("Enable &bookmarks"), variable=self.tkopt.bookmarks,
            command=self.mOptEnableBookmarks)
        submenu.add_checkbutton(
            label=n_("Enable &hint"), variable=self.tkopt.hint,
            command=self.mOptEnableHint)
        submenu.add_checkbutton(
            label=n_("Enable shu&ffle"), variable=self.tkopt.shuffle,
            command=self.mOptEnableShuffle)
        submenu.add_checkbutton(
            label=n_("Free hin&ts"), variable=self.tkopt.free_hint,
            command=self.mOptFreeHints)
        submenu.add_checkbutton(
            label=n_("Enable highlight p&iles"),
            variable=self.tkopt.highlight_piles,
            command=self.mOptEnableHighlightPiles)
        submenu.add_checkbutton(
            label=n_("Enable highlight &cards"),
            variable=self.tkopt.highlight_cards,
            command=self.mOptEnableHighlightCards)
        submenu.add_checkbutton(
            label=n_("Enable highlight same &rank"),
            variable=self.tkopt.highlight_samerank,
            command=self.mOptEnableHighlightSameRank)
        submenu.add_checkbutton(
            label=n_("Enable face-down &peek"),
            variable=self.tkopt.peek_facedown,
            command=self.mOptEnablePeekFacedown)
        submenu.add_checkbutton(
            label=n_("Highlight &no matching"),
            variable=self.tkopt.highlight_not_matching,
            command=self.mOptEnableHighlightNotMatching)
        submenu.add_checkbutton(
            label=n_("Stuc&k notification"),
            variable=self.tkopt.stuck_notification,
            command=self.mOptEnableStuckNotification)
        submenu.add_separator()
        submenu.add_checkbutton(
            label=n_("&Show removed tiles (in Mahjongg games)"),
            variable=self.tkopt.mahjongg_show_removed,
            command=self.mOptMahjonggShowRemoved)
        submenu.add_checkbutton(
            label=n_("Show hint &arrow (in Shisen-Sho games)"),
            variable=self.tkopt.shisen_show_hint,
            command=self.mOptShisenShowHint)
        submenu.add_checkbutton(
            label=n_("&Deal all cards (in Accordion type games)"),
            variable=self.tkopt.accordion_deal_all,
            command=self.mOptAccordionDealAll)
        submenu.add_checkbutton(
            label=n_("A&uto-remove first card (in Pegged games)"),
            variable=self.tkopt.pegged_auto_remove,
            command=self.mOptPeggedAutoRemove)
        menu.add_separator()
        label = n_("&Sound...")
        menu.add_command(
            label=label, command=self.mOptSoundDialog)
        # cardsets
        if USE_PIL:
            submenu = MfxMenu(menu, label=n_("Card si&ze"))
            submenu.add_command(
                label=n_("&Increase the card size"),
                command=self.mIncreaseCardset, accelerator=m+"+")
            submenu.add_command(
                label=n_("&Decrease the card size"),
                command=self.mDecreaseCardset, accelerator=m+"-")
            submenu.add_command(
                label=n_("&Reset the card size"),
                command=self.mResetCardset)
            submenu.add_separator()
            submenu.add_checkbutton(
                label=n_("&Auto scaling"), variable=self.tkopt.auto_scale,
                command=self.mOptAutoScale, accelerator=m+'0')
            submenu.add_checkbutton(
                label=n_("&Preserve aspect ratio"),
                variable=self.tkopt.preserve_aspect_ratio,
                command=self.mOptPreserveAspectRatio)
            submenu.add_separator()
            createResamplingMenu(self, submenu)
            submenu = MfxMenu(menu, label=n_("Card la&yout"))
            submenu.add_checkbutton(
                label=n_("&Spread stacks"), variable=self.tkopt.spread_stacks,
                command=self.mOptSpreadStacks)
            submenu.add_checkbutton(
                label=n_("&Center layout"), variable=self.tkopt.center_layout,
                command=self.mOptCenterLayout)
            submenu.add_checkbutton(
                label=n_("Save games &geometry"),
                variable=self.tkopt.save_games_geometry,
                command=self.mOptSaveGamesGeometry)
        # manager = self.app.cardset_manager
        # n = manager.len()
        menu.add_command(
            label=n_("Cards&et..."),
            command=self.mSelectCardsetDialog, accelerator=m+"E")
        menu.add_command(
            label=n_("Table t&ile..."),
            command=self.mSelectTileDialog)
        # this submenu will get set by updateBackgroundImagesMenu()
        submenu = MfxMenu(menu, label=n_("Card &background"))
        submenu = MfxMenu(menu, label=n_("Card &view"))
        submenu.add_checkbutton(
            label=n_("Card shado&w"), variable=self.tkopt.shadow,
            command=self.mOptShadow)
        submenu.add_checkbutton(
            label=n_("Shade &legal moves"), variable=self.tkopt.shade,
            command=self.mOptShade)
        submenu.add_checkbutton(
            label=n_("&Negative cards bottom"),
            variable=self.tkopt.negative_bottom,
            command=self.mOptNegativeBottom)
        submenu.add_checkbutton(
            label=n_("Shrink face-down cards"),
            variable=self.tkopt.shrink_face_down,
            command=self.mOptShrinkFaceDown)
        submenu.add_checkbutton(
            label=n_("Shade &filled stacks"),
            variable=self.tkopt.shade_filled_stacks,
            command=self.mOptShadeFilledStacks)
        submenu.add_checkbutton(
            label=n_("&Compact long stacks"),
            variable=self.tkopt.compact_stacks,
            command=self.mOptCompactStacks)
        submenu.add_checkbutton(
            label=n_("&Randomize card placement"),
            variable=self.tkopt.randomize_place,
            command=self.mOptRandomizePlace)
        submenu = MfxMenu(menu, label=n_("A&nimations"))
        submenu.add_radiobutton(
            label=n_("&None"), variable=self.tkopt.animations, value=0,
            command=self.mOptAnimations)
        submenu.add_radiobutton(
            label=n_("&Very fast"), variable=self.tkopt.animations, value=1,
            command=self.mOptAnimations)
        submenu.add_radiobutton(
            label=n_("&Fast"), variable=self.tkopt.animations, value=2,
            command=self.mOptAnimations)
        submenu.add_radiobutton(
            label=n_("&Medium"), variable=self.tkopt.animations, value=3,
            command=self.mOptAnimations)
        submenu.add_radiobutton(
            label=n_("&Slow"), variable=self.tkopt.animations, value=4,
            command=self.mOptAnimations)
        submenu.add_radiobutton(
            label=n_("V&ery slow"), variable=self.tkopt.animations, value=5,
            command=self.mOptAnimations)
        submenu.add_separator()
        submenu.add_checkbutton(
            label=n_("&Redeal animation"),
            variable=self.tkopt.redeal_animation,
            command=self.mRedealAnimation)
        submenu.add_checkbutton(
            label=n_("F&lip animation"),
            variable=self.tkopt.flip_animation,
            command=self.mFlipAnimation)
        if Image:
            submenu.add_checkbutton(
                label=n_("&Winning animation"),
                variable=self.tkopt.win_animation,
                command=self.mWinAnimation)
        submenu = MfxMenu(menu, label=n_("&Mouse"))
        submenu.add_radiobutton(
            label=n_("&Drag-and-Drop"), variable=self.tkopt.mouse_type,
            value='drag-n-drop',
            command=self.mOptMouseType)
        submenu.add_radiobutton(
            label=n_("&Point-and-Click"), variable=self.tkopt.mouse_type,
            value='point-n-click',
            command=self.mOptMouseType)
        submenu.add_radiobutton(
            label=n_("&Sticky mouse"), variable=self.tkopt.mouse_type,
            value='sticky-mouse',
            command=self.mOptMouseType)
        submenu.add_separator()
        submenu.add_checkbutton(
            label=n_("Use mouse for undo/redo"),
            variable=self.tkopt.mouse_undo,
            command=self.mOptMouseUndo)
        menu.add_separator()
        menu.add_command(label=n_("&Fonts..."), command=self.mOptFonts)
        menu.add_command(label=n_("&Colors..."), command=self.mOptColors)
        menu.add_command(label=n_("Time&outs..."), command=self.mOptTimeouts)
        menu.add_separator()
        self.createThemesMenu(menu)
        submenu = MfxMenu(menu, label=n_("&Toolbar"))
        createToolbarMenu(self, submenu)
        submenu = MfxMenu(menu, label=n_("Stat&usbar"))
        createStatusbarMenu(self, submenu)
        submenu = MfxMenu(menu, label=n_("Othe&r graphics"))
        createOtherGraphicsMenu(self, submenu)
        if not USE_PIL:
            menu.add_separator()
            menu.add_checkbutton(
                label=n_("Save games &geometry"),
                variable=self.tkopt.save_games_geometry,
                command=self.mOptSaveGamesGeometry)

        # menu.add_checkbutton(
        #     label=n_("Startup splash sc&reen"),
        #     variable=self.tkopt.splashscreen,
        #     command=self.mOptSplashscreen)
        #  menu.add_separator()
        #  menu.add_command(label="Save options", command=self.mOptSave)

        if self.progress:
            self.progress.update(step=1)

        # macOS: tk creates the menu item "Help->PySolFC Help", therefore
        # we will not create a duplicate "Help->Contents" item.
        # The tk-provided menu item expects this callback.
        self.top.createcommand('tk::mac::ShowHelp', self.mHelp)

        menu = MfxMenu(self.menubar, label=n_("&Help"))
        if WIN_SYSTEM != "aqua":
            menu.add_command(
                label=n_("&Contents"),
                command=self.mHelp, accelerator=m+"F1")
        menu.add_command(
            label=n_("&How to use PySol"),
            command=self.mHelpHowToPlay)
        menu.add_command(
            label=n_("&Rules for this game"),
            command=self.mHelpRules, accelerator="F1")
        menu.add_separator()
        menu.add_command(
            label=n_("What's &new?"),
            command=self.mHelpNews)
        menu.add_command(
            label=n_("R&eport a Bug"),
            command=self.mHelpReportBug)
        menu.add_command(
            label=n_("&License terms"),
            command=self.mHelpLicense)
        if WIN_SYSTEM != "aqua":
            menu.add_separator()
            menu.add_command(
                label=_("&About %s...") % TITLE,
                command=self.mHelpAbout)

        MfxMenubar.addPath = None

        # FIXME: all key bindings should be *added* to keyPressHandler
        ctrl = "Control-"
        if sys.platform == "darwin":
            ctrl = "Command-"
        self._bindKey("",   "n", self.mNewGame)
        self._bindKey(ctrl, "w", self.mSelectGameDialog)
        self._bindKey(ctrl, "v", self.mSelectGameDialogWithPreview)
        self._bindKey(ctrl, "r", lambda e: self.mSelectRandomGame())
        self._bindKey(ctrl, "m", self.mSelectGameById)
        self._bindKey(ctrl, "n", self.mNewGameWithNextId)
        self._bindKey(ctrl, "o", self.mOpen)
        self._bindKey(ctrl, "s", self.mSave)
        self._bindKey(ctrl, "x", self.mHoldAndQuit)
        self._bindKey(ctrl, "q", self.mQuit)
        self._bindKey(ctrl, "z", self.mUndo)
        self._bindKey("",   "z", self.mUndo)
        self._bindKey("",   "BackSpace", self.mUndo)    # undocumented
        self._bindKey("",   "KP_Enter", self.mUndo)     # undocumented
        self._bindKey("",   "r", self.mRedo)
        self._bindKey(ctrl, "g", self.mRestart)
        self._bindKey("",   "space", self.mDeal)        # undocumented
        self._bindKey(ctrl, "y", lambda e: self.mPlayerStats(mode=100))
        self._bindKey(ctrl, "t", lambda e: self.mPlayerStats(mode=105))
        self._bindKey("",   "h", self.mHint)
        self._bindKey(ctrl, "h", self.mHint1)           # undocumented
        # self._bindKey("",   "Shift_L", self.mHighlightPiles)
        # self._bindKey("",   "Shift_R", self.mHighlightPiles)
        self._bindKey("",   "i", self.mHighlightPiles)
        self._bindKey("",   "F3", self.mFindCard)
        self._bindKey(ctrl, "d", self.mDemo)
        self._bindKey(ctrl, "e", self.mSelectCardsetDialog)
        if USE_PIL:
            self._bindKey(ctrl, "plus", self.mIncreaseCardset)
            self._bindKey(ctrl, "equal", self.mIncreaseCardset)
            self._bindKey(ctrl, "minus", self.mDecreaseCardset)
            self._bindKey(ctrl, "0", self.mOptAutoScale)
        self._bindKey(ctrl, "b", self.mOptChangeCardback)  # undocumented
        self._bindKey(ctrl, "i", self.mOptChangeTableTile)  # undocumented
        self._bindKey(ctrl, "p", self.mOptPlayerOptions)   # undocumented
        self._bindKey(ctrl, "F1", self.mHelp)
        self._bindKey("",   "F1", self.mHelpRules)
        self._bindKey("",   "Print", self.mScreenshot)
        self._bindKey(ctrl, "u", self.mPlayNextMusic)   # undocumented
        self._bindKey("",   "p", self.mPause)
        self._bindKey("",   "Pause", self.mPause)       # undocumented
        self._bindKey("",   "Escape", self.mIconify)    # undocumented
        # ASD and LKJ
        self._bindKey("",   "a", self.mDrop)
        self._bindKey(ctrl, "a", self.mDrop1)
        self._bindKey("",   "s", self.mUndo)
        self._bindKey("",   "d", self.mDeal)
        self._bindKey("",   "l", self.mDrop)
        self._bindKey(ctrl, "l", self.mDrop1)
        self._bindKey("",   "k", self.mUndo)
        self._bindKey("",   "j", self.mDeal)

        self._bindKey("",   "F2", self.mStackDesk)
        #
        # undocumented, devel
        self._bindKey("", "slash", lambda e: self.mPlayerStats(mode=106))
        #
        self._bindKey("",   "f", self.mShuffle)

        for i in range(9):
            self._bindKey(
                ctrl, str(i+1),
                lambda e, i=i: self.mGotoBookmark(i, confirm=0))

        # undocumented, devel
        self._bindKey(ctrl, "End", self.mPlayNextMusic)
        self._bindKey(ctrl, "Prior", self.mSelectPrevGameByName)
        self._bindKey(ctrl, "Next", self.mSelectNextGameByName)
        self._bindKey(ctrl, "Up", self.mSelectPrevGameById)
        self._bindKey(ctrl, "Down", self.mSelectNextGameById)

        self._bindKey("", "F5", self.refresh)

        if os.name == 'posix' and platform.system() != 'Darwin':
            self._bindKey('Alt-', 'F4', self.mQuit)

    #
    # key binding utility
    #

    def _bindKey(self, modifier, key, func):
        sequence = "<" + modifier + "KeyPress-" + key + ">"
        bind(self.top, sequence, func)
        if len(key) == 1 and key != key.upper():
            key = key.upper()
            sequence = "<" + modifier + "KeyPress-" + key + ">"
            bind(self.top, sequence, func)

    def _keyPressHandler(self, event):
        r = EVENT_PROPAGATE
        if event and self.game:
            # print event.__dict__
            if self.game.demo:
                # stop the demo by setting self.game.demo.keypress
                if event.char:    # ignore Ctrl/Shift/etc.
                    self.game.demo.keypress = event.char
                    r = EVENT_HANDLED
                # func = self.keybindings.get(event.char)
                # if func and (event.state & ~2) == 0:
                #    func(event)
                #    r = EVENT_HANDLED
        return r

    #
    # Select Game menu creation
    #

    def _addSelectGameMenu(self, menu):
        # games = map(self.app.gdb.get,
        #   self.app.gdb.getGamesIdSortedByShortName())
        games = list(map(
            self.app.gdb.get, self.app.gdb.getGamesIdSortedByName()))
        # games = tuple(games)
        # menu = MfxMenu(menu, label="Select &game")
        m = "Ctrl-"
        if sys.platform == "darwin":
            m = "Cmd-"
        menu.add_command(label=n_("All &games..."), accelerator=m+"V",
                         command=self.mSelectGameDialogWithPreview)
        if not SELECT_GAME_MENU:
            return
        menu.add_separator()
        self._addSelectPopularGameSubMenu(games, menu, self.mSelectGame,
                                          self.tkopt.gameid)
        self._addSelectFrenchGameSubMenu(games, menu, self.mSelectGame,
                                         self.tkopt.gameid)
        if self.progress:
            self.progress.update(step=1)
        self._addSelectMahjonggGameSubMenu(games, menu, self.mSelectGame,
                                           self.tkopt.gameid)
        self._addSelectOrientalGameSubMenu(games, menu, self.mSelectGame,
                                           self.tkopt.gameid)
        self._addSelectSpecialGameSubMenu(games, menu, self.mSelectGame,
                                          self.tkopt.gameid)
        self._addSelectCustomGameSubMenu(games, menu, self.mSelectGame,
                                         self.tkopt.gameid)
        menu.add_separator()
        if self.progress:
            self.progress.update(step=1)
        self._addSelectAllGameSubMenu(games, menu, self.mSelectGame,
                                      self.tkopt.gameid)

    def _addSelectGameSubMenu(self, games, menu, select_data,
                              command, variable, short_name=False):
        # print select_data
        need_sep = 0
        for label, select_func in select_data:
            if label is None:
                need_sep = 1
                continue
            g = list(filter(select_func, games))
            if not g:
                continue
            if need_sep:
                menu.add_separator()
                need_sep = 0
            submenu = MfxMenu(menu, label=label)
            self._addSelectGameSubSubMenu(g, submenu, command, variable,
                                          short_name=short_name)

    def _getNumGames(self, games, select_data):
        ngames = 0
        for label, select_func in select_data:
            ngames += len(list(filter(select_func, games)))
        return ngames

    def _addSelectMahjonggGameSubMenu(self, games, menu, command, variable):
        def select_func(gi):
            return gi.si.game_type == GI.GT_MAHJONGG

        def sort_func(gi):
            return gi.short_name

        mahjongg_games = list(filter(select_func, games))
        if len(mahjongg_games) == 0:
            return

        mahjongg_games.sort(key=sort_func)
        #
        menu = MfxMenu(menu, label=n_("&Mahjongg games"))
        n, d = 0, self.cb_max
        i = 0
        while True:
            if self.progress:
                self.progress.update(step=1)
            columnbreak = i > 0 and (i % d) == 0
            i += 1
            if not mahjongg_games[n:n + d]:
                break
            m = min(n + d - 1, len(mahjongg_games) - 1)
            label = mahjongg_games[n].short_name[:3] + ' - ' + \
                mahjongg_games[m].short_name[:3]
            submenu = MfxMenu(menu, label=label, name=None)
            self._addSelectGameSubSubMenu(mahjongg_games[n:n + d], submenu,
                                          command, variable, short_name=True)
            n += d
            if columnbreak:
                menu.entryconfigure(i, columnbreak=columnbreak)

    def _addSelectPopularGameSubMenu(self, games, menu, command, variable):
        def select_func(gi):
            return gi.si.game_flags & GI.GT_POPULAR
        if len(list(filter(select_func, games))) == 0:
            return
        data = (n_("&Popular games"), select_func)
        self._addSelectGameSubMenu(games, menu, (data, ),
                                   self.mSelectGamePopular,
                                   self.tkopt.gameid_popular)

    def _addSelectFrenchGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&French games"))
        self._addSelectGameSubMenu(games, submenu, GI.SELECT_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectOrientalGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_ORIENTAL_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&Oriental games"))
        self._addSelectGameSubMenu(games, submenu,
                                   GI.SELECT_ORIENTAL_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectSpecialGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_ORIENTAL_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&Special games"))
        self._addSelectGameSubMenu(games, submenu,
                                   GI.SELECT_SPECIAL_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectCustomGameSubMenu(self, games, menu, command, variable):
        submenu = MfxMenu(menu, label=n_("&Custom games"))

        def select_func(gi):
            return gi.si.game_type == GI.GT_CUSTOM
        games = list(filter(select_func, games))
        self.updateGamesMenu(submenu, games)

    def _addSelectAllGameSubMenu(self, games, menu, command, variable):
        if menu.name == "select":
            menu = MfxMenu(menu, label=n_("&All games by name"))
        n, d = 0, self.cb_max
        i = 0
        while True:
            if self.progress:
                self.progress.update(step=1)
            columnbreak = i > 0 and (i % d) == 0
            i += 1
            if not games[n:n+d]:
                break
            m = min(n+d-1, len(games)-1)
            label = games[n].name[:3] + ' - ' + games[m].name[:3]
            submenu = MfxMenu(menu, label=label, name=None)
            self._addSelectGameSubSubMenu(games[n:n+d], submenu,
                                          command, variable)
            n += d
            if columnbreak:
                menu.entryconfigure(i, columnbreak=columnbreak)

    def _addSelectGameSubSubMenu(self, games, menu, command, variable,
                                 short_name=False):
        # cb = (25, self.cb_max) [ len(g) > 4 * 25 ]
        # cb = min(cb, self.cb_max)
        cb = self.cb_max
        for i in range(len(games)):
            gi = games[i]
            columnbreak = i > 0 and (i % cb) == 0
            if short_name:
                label = gi.short_name
            else:
                label = gi.name
            # optimized by inlining
            menu.tk.call((menu._w, 'add', 'radiobutton') +
                         menu._options({'command': command,
                                        'variable': variable,
                                        'columnbreak': columnbreak,
                                        'value': gi.id,
                                        'label': label}))

    def updateGamesMenu(self, menu, games):
        menu.delete(0, 'last')
        if len(games) == 0:
            menu.add_radiobutton(label=_('<none>'), name=None,
                                 state='disabled')
        elif len(games) > self.cb_max*4:
            games.sort(key=lambda x: x.name)
            self._addSelectAllGameSubMenu(games, menu,
                                          command=self.mSelectGame,
                                          variable=self.tkopt.gameid)
        else:
            self._addSelectGameSubSubMenu(games, menu,
                                          command=self.mSelectGame,
                                          variable=self.tkopt.gameid)

    #
    # Select Game menu actions
    #

    def mSelectGame(self, *args):
        self._mSelectGame(self.tkopt.gameid.get())
        self.tkopt.gameid.set(self.game.id)

    def mSelectGamePopular(self, *args):
        self._mSelectGame(self.tkopt.gameid_popular.get())
        self.tkopt.gameid_popular.set(self.game.id)

    def _mSelectGameDialog(self, d):
        if d.status == 0 and d.button == 0 and d.gameid != self.game.id:
            self.tkopt.gameid.set(d.gameid)
            self.tkopt.gameid_popular.set(d.gameid)
            if 0:
                self._mSelectGame(d.gameid, random=d.random)
            else:
                # don't ask areYouSure()
                self._cancelDrag()
                self.game.endGame()
                self.game.quitGame(d.gameid, random=d.random)
        return EVENT_HANDLED

    def __restoreCursor(self, *event):
        self.game.setCursor(cursor=self.app.top_cursor)

    def mSelectGameDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        d = self._calcSelectGameDialog()(
            self.top, title=_("Select game"),
            app=self.app, gameid=self.game.id)
        return self._mSelectGameDialog(d)

    def mSelectGameDialogWithPreview(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.game.setCursor(cursor=CURSOR_WATCH)
        bookmark = None
        if 0:
            # use a bookmark for our preview game
            if self.game.setBookmark(-2, confirm=0):
                bookmark = self.game.gsaveinfo.bookmarks[-2][0]
                del self.game.gsaveinfo.bookmarks[-2]
        after_idle(self.top, self.__restoreCursor)
        d = self._calcSelectGameDialogWithPreview()(
            self.top, title=_("Select game"),
            app=self.app, gameid=self.game.id,
            bookmark=bookmark)
        return self._mSelectGameDialog(d)

    #
    # menubar overrides
    #

    def updateFavoriteGamesMenu(self):
        gameids = self.app.opt.favorite_gameid
        menu, index, submenu = self.menupath[".menubar.file.favoritegames"]
        games = []
        for id in gameids:
            gi = self.app.getGameInfo(id)
            if gi:
                games.append(gi)

        def sort_func(gi):
            return gi.name

        games.sort(key=sort_func)
        state = self._getEnabledState
        if len(games) > 0:
            self.updateGamesMenu(submenu, games)
            menu.entryconfig(index, state=state(True))
        else:
            menu.entryconfig(index, state=state(False))
        in_favor = self.app.game.id in gameids
        menu, index, submenu = self.menupath[".menubar.file.addtofavorites"]
        menu.entryconfig(index, state=state(not in_favor))
        menu, index, submenu = \
            self.menupath[".menubar.file.removefromfavorites"]
        menu.entryconfig(index, state=state(in_favor))

    def updateRecentGamesMenu(self, gameids):
        submenu = self.menupath[".menubar.file.recentgames"][2]
        games = []
        for id in gameids:
            gi = self.app.getGameInfo(id)
            if gi:
                games.append(gi)
        self.updateGamesMenu(submenu, games)
        submenu.add_separator()
        submenu.add_command(label=n_("&Clear recent games"),
                            command=self.mClearRecent)

    def updateCustomGamesMenu(self):
        menu = self.menupath[".menubar.select.customgames"][2]
        menu2 = self.menupath[".menubar.select.allgamesbyname"][2]

        def select_func_visible(gi):
            return gi.si.game_type != GI.GT_HIDDEN

        def select_func_custom(gi):
            return gi.si.game_type == GI.GT_CUSTOM

        games = list(map(self.app.gdb.get,
                         self.app.gdb.getGamesIdSortedByName()))
        games = list(filter(select_func_visible, games))
        self.progress = False
        self.updateGamesMenu(menu2, games)
        games = list(filter(select_func_custom, games))
        self.updateGamesMenu(menu, games)

    def updateBookmarkMenuState(self):
        state = self._getEnabledState
        mp1 = self.menupath.get(".menubar.edit.setbookmark")
        mp2 = self.menupath.get(".menubar.edit.gotobookmark")
        mp3 = self.menupath.get(".menubar.edit.clearbookmarks")
        if mp1 is None or mp2 is None or mp3 is None:
            return
        x = self.app.opt.bookmarks and self.game.canSetBookmark()
        #
        menu, index, submenu = mp1
        for i in range(9):
            submenu.entryconfig(i, state=state(x))
        menu.entryconfig(index, state=state(x))
        #
        menu, index, submenu = mp2
        ms = 0
        for i in range(9):
            s = self.game.gsaveinfo.bookmarks.get(i) is not None
            submenu.entryconfig(i, state=state(s and x))
            ms = ms or s
        menu.entryconfig(index, state=state(ms and x))
        #
        menu, index, submenu = mp3
        menu.entryconfig(index, state=state(ms and x))

    def updateBackgroundImagesMenu(self):
        mp = self.menupath.get(".menubar.options.cardbackground")
        # delete all entries
        submenu = mp[2]
        submenu.delete(0, "last")
        # insert new cardbacks
        mbacks = self.app.images.getCardbacks()
        cb = int(math.ceil(math.sqrt(len(mbacks))))
        for i in range(len(mbacks)):
            columnbreak = i > 0 and (i % cb) == 0
            submenu.add_radiobutton(
                label=mbacks[i].name, image=mbacks[i].menu_image,
                variable=self.tkopt.cardback, value=i,
                command=self.mOptCardback, columnbreak=columnbreak,
                indicatoron=0, hidemargin=0)

    #
    # menu updates
    #

    def setMenuState(self, state, path):
        # print state, path
        path = ".menubar." + path
        mp = self.menupath.get(path)
        menu, index, submenu = mp
        s = self._getEnabledState(state)
        menu.entryconfig(index, state=s)

    def setToolbarState(self, state, path):
        # print state, path
        s = self._getEnabledState(state)
        w = getattr(self.app.toolbar, path + "_button")
        w["state"] = s

    def _setCommentMenu(self, v):
        self.tkopt.comment.set(v)

    def _setPauseMenu(self, v):
        self.tkopt.pause.set(v)

    #
    # menu actions
    #

    DEFAULTEXTENSION = ".pso"
    FILETYPES = ((_("%s files") % TITLE, "*" + DEFAULTEXTENSION),
                 (_("All files"), "*"))

    def mAddFavor(self, *event):
        gameid = self.app.game.id
        if gameid not in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.append(gameid)
            self.updateFavoriteGamesMenu()

    def mDelFavor(self, *event):
        gameid = self.app.game.id
        if gameid in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.remove(gameid)
            self.updateFavoriteGamesMenu()

    def mClearRecent(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.game.areYouSure(_("Clear recent games"),
                                    _("Clear the recent games list?")):
            return
        gameid = self.app.game.id
        self.app.opt.recent_gameid = []
        self.app.opt.recent_gameid.append(gameid)
        self.updateRecentGamesMenu(self.app.opt.recent_gameid)

    def mOpen(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        filename = self.game.filename
        if filename:
            idir, ifile = os.path.split(os.path.normpath(filename))
        else:
            idir, ifile = "", ""
        if not idir:
            idir = self.app.dn.savegames
        d = tkinter_tkfiledialog.Open()
        filename = d.show(filetypes=self.FILETYPES,
                          defaultextension=self.DEFAULTEXTENSION,
                          initialdir=idir, initialfile=ifile)
        if filename:
            filename = os.path.normpath(filename)
            # filename = os.path.normcase(filename)
            if os.path.isfile(filename):
                self.game.loadGame(filename)

    def mExportCurrentLayout(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        game = self.game
        if not self.menustate.save_as:
            return
        if not game.Solver_Class:
            d = self._calc_MfxMessageDialog()(
                self.top, title=_('Export game error'),
                text=_('''
Unsupported game for export.
'''),
                bitmap='error')
            return

        filename = game.filename
        if not filename:
            filename = self.app.getGameSaveName(self.game.id)
            if os.name == "posix" or os.path.supports_unicode_filenames:
                filename += "-" + self.game.getGameNumber(format=0)
            else:
                filename += "-01"
            filename += ".board"
        idir, ifile = os.path.split(os.path.normpath(filename))
        if not idir:
            idir = self.app.dn.boards
        # print self.game.filename, ifile
        d = tkinter_tkfiledialog.SaveAs()
        filename = d.show(filetypes=self.FILETYPES,
                          defaultextension=self.DEFAULTEXTENSION,
                          initialdir=idir, initialfile=ifile)
        if filename:
            filename = os.path.normpath(filename)
            # filename = os.path.normcase(filename)
            with open(filename, 'w') as fh:
                game = self.game
                fh.write(game.Solver_Class(game, self).calcBoardString())
            self.updateMenus()

    def mImportStartingLayout(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        game = self.game
        if not game.Solver_Class:
            d = self._calc_MfxMessageDialog()(
                self.top, title=_('Import game error'),
                text=_('''
Unsupported game for import.
'''),
                bitmap='error')
            return

        filename = self.game.filename
        if filename:
            idir, ifile = os.path.split(os.path.normpath(filename))
        else:
            idir, ifile = "", ""
        if not idir:
            idir = self.app.dn.boards
        d = tkinter_tkfiledialog.Open()
        key = 'PYSOL_DEBUG_IMPORT'
        if key not in os.environ:
            filename = d.show(filetypes=self.FILETYPES,
                              defaultextension=self.DEFAULTEXTENSION,
                              initialdir=idir, initialfile=ifile)
        else:
            filename = os.environ[key]
        if filename:
            filename = os.path.normpath(filename)
            # filename = os.path.normcase(filename)
            if os.path.isfile(filename):
                with open(filename, 'r+b') as fh:
                    game = self.game
                    try:
                        game.Solver_Class(game, self).importFile(
                            fh, game, self)
                    except PySolHintLayoutImportError as err:
                        self._calc_MfxMessageDialog()(
                            self.top,
                            title=_('Import game error'),
                            text=err.format(),
                            bitmap='error'
                        )
                        game.busy = False
                        game.endGame()
                        game.newGame()

    def mSaveAs(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.menustate.save_as:
            return
        filename = self.game.filename
        if not filename:
            filename = self.app.getGameSaveName(self.game.id)
            if os.name == "posix":
                filename = filename + "-" + self.game.getGameNumber(format=0)
            elif os.path.supports_unicode_filenames:  # new in python 2.3
                filename = filename + "-" + self.game.getGameNumber(format=0)
            else:
                filename = filename + "-01"
            filename = filename + self.DEFAULTEXTENSION
        idir, ifile = os.path.split(os.path.normpath(filename))
        if not idir:
            idir = self.app.dn.savegames
        # print self.game.filename, ifile
        d = tkinter_tkfiledialog.SaveAs()
        filename = d.show(filetypes=self.FILETYPES,
                          defaultextension=self.DEFAULTEXTENSION,
                          initialdir=idir, initialfile=ifile)
        if filename:
            filename = os.path.normpath(filename)
            # filename = os.path.normcase(filename)
            self.game.saveGame(filename)
            self.updateMenus()

    def mPause(self, *args):
        if not self.game:
            return
        if not self.game.pause:
            if self._cancelDrag():
                return
        self.game.doPause()
        self.tkopt.pause.set(self.game.pause)

    def mOptSoundDialog(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self._calcSoundOptionsDialog()(
            self.top, _("Sound settings"), self.app)
        self.tkopt.sound.set(self.app.opt.sound)

    def mOptAutoFaceUp(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.autofaceup = self.tkopt.autofaceup.get()
        if self.app.opt.autofaceup:
            self.game.autoPlay()

    def mOptAutoDrop(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.autodrop = self.tkopt.autodrop.get()
        if self.app.opt.autodrop:
            self.game.autoPlay()

    def mOptAutoDeal(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.autodeal = self.tkopt.autodeal.get()
        if self.app.opt.autodeal:
            self.game.autoPlay()

    def mOptQuickPlay(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.quickplay = self.tkopt.quickplay.get()

    def mOptEnableUndo(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.undo = self.tkopt.undo.get()
        self.game.updateMenus()

    def mOptEnableBookmarks(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.bookmarks = self.tkopt.bookmarks.get()
        self.game.updateMenus()

    def mOptEnableHint(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.hint = self.tkopt.hint.get()
        self.game.updateMenus()

    def mOptFreeHints(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.free_hint = self.tkopt.free_hint.get()
        self.game.updateMenus()

    def mOptEnableShuffle(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shuffle = self.tkopt.shuffle.get()
        self.game.updateMenus()

    def mOptEnableHighlightPiles(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_piles = self.tkopt.highlight_piles.get()
        self.game.updateMenus()

    def mOptEnableHighlightCards(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_cards = self.tkopt.highlight_cards.get()
        self.game.updateMenus()

    def mOptEnableHighlightSameRank(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_samerank = self.tkopt.highlight_samerank.get()
        # self.game.updateMenus()

    def mOptEnablePeekFacedown(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.peek_facedown = self.tkopt.peek_facedown.get()
        # self.game.updateMenus()

    def mOptEnableHighlightNotMatching(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.highlight_not_matching = \
            self.tkopt.highlight_not_matching.get()
        # self.game.updateMenus()

    def mOptEnableStuckNotification(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.stuck_notification = self.tkopt.stuck_notification.get()
        # self.game.updateMenus()

    def mOptAnimations(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.animations = self.tkopt.animations.get()

    def mRedealAnimation(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.redeal_animation = self.tkopt.redeal_animation.get()

    def mFlipAnimation(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.flip_animation = self.tkopt.flip_animation.get()

    def mWinAnimation(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.win_animation = self.tkopt.win_animation.get()

    def mOptShadow(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shadow = self.tkopt.shadow.get()

    def mOptShade(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shade = self.tkopt.shade.get()

    def mOptShrinkFaceDown(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shrink_face_down = self.tkopt.shrink_face_down.get()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShadeFilledStacks(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shade_filled_stacks = self.tkopt.shade_filled_stacks.get()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptCompactStacks(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.compact_stacks = self.tkopt.compact_stacks.get()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptMahjonggShowRemoved(self, *args):
        if self._cancelDrag():
            return
        self.app.opt.mahjongg_show_removed = \
            self.tkopt.mahjongg_show_removed.get()
        # self.game.updateMenus()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShisenShowHint(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.shisen_show_hint = self.tkopt.shisen_show_hint.get()
        # self.game.updateMenus()

    def mOptAccordionDealAll(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.accordion_deal_all = self.tkopt.accordion_deal_all.get()
        # self.game.updateMenus()

    def mOptPeggedAutoRemove(self, *args):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.pegged_auto_remove = self.tkopt.pegged_auto_remove.get()
        # self.game.updateMenus()

    def _updateCardSize(self):
        geom = (self.app.canvas.winfo_width(),
                self.app.canvas.winfo_height())
        self.app.opt.game_geometry = geom
        self.app.game.resizeGame(card_size_manually=True)
        if self.app.opt.auto_scale or self.app.opt.spread_stacks:
            w, h = self.app.opt.game_geometry
            self.app.canvas.setInitialSize(w, h, scrollregion=False)
            # Resize a second time to auto scale
            self.app.game.resizeGame(card_size_manually=False)
        else:
            w = int(round(self.app.game.width * self.app.opt.scale_x))
            h = int(round(self.app.game.height * self.app.opt.scale_y))
            self.app.canvas.setInitialSize(w, h)
            self.app.top.wm_geometry("")    # cancel user-specified geometry
        # self.app.top.update_idletasks()
        self.app.setTile(self.app.tabletile_index)
        self.tkopt.tabletile.set(self.app.tabletile_index)

        self.updateMenus()

    def mIncreaseCardset(self, *event):
        if self._cancelDrag(break_pause=True):
            return
        if self.app.opt.scale_x < 4:
            self.app.opt.scale_x += 0.1
        else:
            return
        if self.app.opt.scale_y < 4:
            self.app.opt.scale_y += 0.1
        else:
            return
        self.app.opt.auto_scale = False
        self.tkopt.auto_scale.set(False)
        self._updateCardSize()

    def mDecreaseCardset(self, *event):
        if self._cancelDrag(break_pause=True):
            return
        if self.app.opt.scale_x > 0.5:
            self.app.opt.scale_x -= 0.1
        else:
            return
        if self.app.opt.scale_y > 0.5:
            self.app.opt.scale_y -= 0.1
        else:
            return
        self.app.opt.auto_scale = False
        self.tkopt.auto_scale.set(False)
        self._updateCardSize()

    def mResetCardset(self, *event):
        if self._cancelDrag(break_pause=True):
            return
        self.app.opt.scale_x = 1
        self.app.opt.scale_y = 1

        self.app.opt.auto_scale = False
        self.tkopt.auto_scale.set(False)
        self._updateCardSize()

    def mOptAutoScale(self, *event):
        if self._cancelDrag(break_pause=True):
            return
        auto_scale = not self.app.opt.auto_scale

        # In the future, it should be possible to use both options together,
        # but the current logic conflicts, so not allowed for now.
        self.app.opt.spread_stacks = False
        self.tkopt.spread_stacks.set(False)

        self.app.opt.auto_scale = auto_scale
        self.tkopt.auto_scale.set(auto_scale)
        self._updateCardSize()

    def mOptPreserveAspectRatio(self, *event):
        if self._cancelDrag(break_pause=True):
            return
        preserve_aspect_ratio = not self.app.opt.preserve_aspect_ratio

        self.app.opt.preserve_aspect_ratio = preserve_aspect_ratio
        self.tkopt.preserve_aspect_ratio.set(preserve_aspect_ratio)
        self._updateCardSize()

    def mOptResampling(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        resampling = self.tkopt.resampling.get()
        self.app.opt.resampling = resampling
        self.tkopt.resampling.set(resampling)  # update radiobutton
        self.app.opt.resampling = (self.tkopt.resampling.get())
        self._updateCardSize()

    def mOptSpreadStacks(self, *event):
        if self._cancelDrag(break_pause=True):
            return
        spread_stacks = not self.app.opt.spread_stacks

        # In the future, it should be possible to use both options together,
        # but the current logic conflicts, so not allowed for now.
        self.app.opt.auto_scale = False
        self.tkopt.auto_scale.set(False)

        self.app.opt.spread_stacks = spread_stacks
        self.tkopt.spread_stacks.set(spread_stacks)
        self._updateCardSize()

    def mOptCenterLayout(self, *event):
        if self._cancelDrag(break_pause=True):
            return
        self.app.opt.center_layout = not self.app.opt.center_layout
        self._updateCardSize()

    def mOptRandomizePlace(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.randomize_place = self.tkopt.randomize_place.get()
        self._updateCardSize()

    def mOptSaveGamesGeometry(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.save_games_geometry = self.tkopt.save_games_geometry.get()

    def _mOptCardback(self, index):
        if self._cancelDrag(break_pause=False):
            return
        cs = self.app.cardset
        old_index = cs.backindex
        cs.updateCardback(backindex=index)
        if cs.backindex == old_index:
            return
        self.app.updateCardset(self.game.id)
        image = self.app.images.getBack(update=True)
        for card in self.game.cards:
            card.updateCardBackground(image=image)
        self.app.canvas.update_idletasks()
        self.tkopt.cardback.set(cs.backindex)

    def mOptCardback(self, *event):
        self._mOptCardback(self.tkopt.cardback.get())

    def mOptChangeCardback(self, *event):
        self._mOptCardback(self.app.cardset.backindex + 1)

    def mOptChangeTableTile(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        n = self.app.tabletile_manager.len()
        if n >= 2:
            i = (self.tkopt.tabletile.get() + 1) % n
            if self.app.setTile(i):
                self.tkopt.tabletile.set(i)

    def mSelectTileDialog(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        key = self.app.tabletile_index
        if key <= 0:
            key = self.app.opt.colors['table']  # .lower()
        d = self._calcSelectTileDialogWithPreview()(
            self.top, app=self.app,
            title=_("Select table background"),
            manager=self.app.tabletile_manager,
            key=key)
        if d.status == 0 and d.button == 0:
            if isinstance(d.key, str):
                tile = self.app.tabletile_manager.get(0)
                tile.color = d.key
                if self.app.setTile(0):
                    self.tkopt.tabletile.set(0)
            elif d.key > 0 and (d.key != self.app.tabletile_index or
                                d.preview_scaling !=
                                self.app.opt.tabletile_scale_method):
                if self.app.setTile(d.key, d.preview_scaling):
                    self.tkopt.tabletile.set(d.key)
                self.app.opt.tabletile_scale_method = d.preview_scaling

    def mOptToolbar(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarSide(self.tkopt.toolbar.get())

    def mOptToolbarStyle(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarStyle(self.tkopt.toolbar_style.get())

    def mOptToolbarCompound(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarCompound(self.tkopt.toolbar_compound.get())

    def mOptToolbarSize(self, *event):
        # if self._cancelDrag(break_pause=False): return
        self.setToolbarSize(self.tkopt.toolbar_size.get())

    def mOptToolbarConfig(self, w):
        self.toolbarConfig(w, self.tkopt.toolbar_vars[w].get())

    def mOptStatusbar(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.app.statusbar:
            return
        side = self.tkopt.statusbar.get()
        self.app.opt.statusbar = side
        resize = not self.app.opt.save_games_geometry
        if self.app.statusbar.show(side, resize=resize):
            self.top.update_idletasks()

    def mOptStatusbarConfig(self, w):
        self.statusbarConfig(w, self.tkopt.statusbar_vars[w].get())

    def mOptButtonIconStyle(self, *event):
        self.setButtonIconStyle(self.tkopt.button_icon_style.get())

    def mOptDemoLogoStyle(self, *event):
        self.setDemoLogoStyle(self.tkopt.demo_logo_style.get())

    def mOptDialogIconStyle(self, *event):
        self.setDialogIconStyle(self.tkopt.dialog_icon_style.get())

    def mOptPauseTextStyle(self, *event):
        self.setPauseTextStyle(self.tkopt.pause_text_style.get())

    def mOptRedealIconStyle(self, *event):
        self.setRedealIconStyle(self.tkopt.redeal_icon_style.get())

    def mOptTreeIconStyle(self, *event):
        self.setTreeIconStyle(self.tkopt.tree_icon_style.get())

    def mOptNumCards(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.num_cards = self.tkopt.num_cards.get()

    def mOptHelpbar(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.app.helpbar:
            return
        show = self.tkopt.helpbar.get()
        self.app.opt.helpbar = show
        resize = not self.app.opt.save_games_geometry
        if self.app.helpbar.show(show, resize=resize):
            self.top.update_idletasks()

    def mOptDemoLogo(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.demo_logo = self.tkopt.demo_logo.get()

    def mOptSplashscreen(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.splashscreen = self.tkopt.splashscreen.get()

    def mOptMouseType(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.mouse_type = self.tkopt.mouse_type.get()

    def mOptMouseUndo(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.mouse_undo = self.tkopt.mouse_undo.get()

    def mOptNegativeBottom(self, *event):
        if self._cancelDrag():
            return
        self.app.opt.negative_bottom = self.tkopt.negative_bottom.get()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def refresh(self, *event):
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    #
    # toolbar support
    #

    def setToolbarSide(self, side):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar = side
        self.tkopt.toolbar.set(side)                    # update radiobutton
        resize = not self.app.opt.save_games_geometry
        if self.app.toolbar.show(side, resize=resize):
            self.top.update_idletasks()

    def setToolbarSize(self, size):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_size = size
        self.tkopt.toolbar_size.set(size)                # update radiobutton
        dir = self.app.getToolbarImagesDir()
        if self.app.toolbar.updateImages(dir, size):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_style = style
        self.tkopt.toolbar_style.set(style)                # update radiobutton
        dir = self.app.getToolbarImagesDir()
        size = self.app.opt.toolbar_size
        if self.app.toolbar.updateImages(dir, size):
            # self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarCompound(self, compound):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_compound = compound
        self.tkopt.toolbar_compound.set(compound)          # update radiobutton
        if self.app.toolbar.setCompound(compound):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setButtonIconStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.button_icon_style = style
        self.tkopt.button_icon_style.set(style)      # update radiobutton
        self.app.loadImages1()
        self.app.loadImages4()

    def setDemoLogoStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        if style == "none":
            self.app.opt.demo_logo = False
        else:
            self.app.opt.demo_logo = True
            self.app.opt.demo_logo_style = style
            self.tkopt.demo_logo_style.set(style)         # update radiobutton
            self.app.loadImages2()
            self.app.loadImages4()
            self.app.updateCardset()
            self.game.endGame(bookmark=1)
            self.game.quitGame(bookmark=1)

    def setDialogIconStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.dialog_icon_style = style
        self.tkopt.dialog_icon_style.set(style)           # update radiobutton
        self.app.loadImages1()
        self.app.loadImages4()

    def setPauseTextStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.pause_text_style = style
        self.tkopt.pause_text_style.set(style)            # update radiobutton
        self.app.loadImages2()
        self.app.loadImages4()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def setRedealIconStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.redeal_icon_style = style
        self.tkopt.redeal_icon_style.set(style)           # update radiobutton
        self.app.loadImages2()
        self.app.loadImages4()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def setTreeIconStyle(self, style):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.tree_icon_style = style
        self.tkopt.tree_icon_style.set(style)           # update radiobutton
        self.app.loadImages3()
        self.app.loadImages4()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def wizardDialog(self, edit=False):
        from pysollib.wizardutil import write_game, reset_wizard
        WizardDialog = self._calcWizardDialog()

        if edit:
            reset_wizard(self.game)
        else:
            reset_wizard(None)
        d = WizardDialog(self.top, _('Solitaire Wizard'), self.app)
        if d.status == 0 and d.button == 0:
            try:
                if edit:
                    gameid = write_game(self.app, game=self.game)
                else:
                    gameid = write_game(self.app)
            except Exception as err:
                # if False:
                #    traceback.print_exc()
                self._calc_MfxMessageDialog()(
                    self.top, title=_('Save game error'),
                    text=_('''
Error while saving game.

%s
''') % str(err),
                    bitmap='error')
                return

            if SELECT_GAME_MENU:
                self.updateCustomGamesMenu()

            self.tkopt.gameid.set(gameid)
            self._mSelectGame(gameid, force=True)

    def mWizard(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.wizardDialog()

    def mWizardEdit(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        self.wizardDialog(edit=True)

    def mWizardDelete(self, *event):
        if self._cancelDrag(break_pause=False):
            return
        if not self.game.areYouSure(_("Delete game"),
                                    _("Delete the game %s?")
                                    % self.game.gameinfo.name):
            return
        from pysollib.wizardutil import delete_game
        delete_game(self.app, self.game)
        self.game.endGame()
        self.game.quitGame(2)

        if SELECT_GAME_MENU:
            self.updateCustomGamesMenu()

    def toolbarConfig(self, w, v):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.toolbar_vars[w] = v
        self.app.toolbar.config(w, v)
        self.top.update_idletasks()

    def statusbarConfig(self, w, v):
        if self._cancelDrag(break_pause=False):
            return
        self.app.opt.statusbar_vars[w] = v
        self.app.statusbar.config(w, v)
        self.top.update_idletasks()

    #
    # stacks descriptions
    #

    def mStackDesk(self, *event):
        if self.game.stackdesc_list:
            self.game.deleteStackDesc()
        else:
            if self._cancelDrag(break_pause=True):
                return
            self.game.showStackDesc()
