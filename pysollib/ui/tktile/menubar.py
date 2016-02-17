import re
import Tkinter

from pysollib.mfxutil import Struct, kwdefault
from pysollib.mygettext import _, n_

from pysollib.ui.tktile.tkconst import EVENT_HANDLED, EVENT_PROPAGATE, CURSOR_WATCH, COMPOUNDS
from pysollib.ui.tktile.tkconst import TOOLBAR_BUTTONS

def createToolbarMenu(menubar, menu):
    tearoff = menu.cget('tearoff')
##     data_dir = os.path.join(menubar.app.dataloader.dir, 'images', 'toolbar')
##     submenu = MfxMenu(menu, label=n_('Style'), tearoff=tearoff)
##     for f in os.listdir(data_dir):
##         d = os.path.join(data_dir, f)
##         if os.path.isdir(d) and os.path.exists(os.path.join(d, 'small')):
##             name = f.replace('_', ' ').capitalize()
##             submenu.add_radiobutton(label=name,
##                                     variable=menubar.tkopt.toolbar_style,
##                                     value=f, command=menubar.mOptToolbarStyle)
    submenu = MfxMenu(menu, label=n_('Compound'), tearoff=tearoff)
    for comp, label in COMPOUNDS:
        submenu.add_radiobutton(
            label=label, variable=menubar.tkopt.toolbar_compound,
            value=comp, command=menubar.mOptToolbarCompound)
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
##     menu.add_separator()
##     menu.add_radiobutton(label=n_("Small icons"),
##                          variable=menubar.tkopt.toolbar_size, value=0,
##                          command=menubar.mOptToolbarSize)
##     menu.add_radiobutton(label=n_("Large icons"),
##                          variable=menubar.tkopt.toolbar_size, value=1,
##                          command=menubar.mOptToolbarSize)
    menu.add_separator()
    submenu = MfxMenu(menu, label=n_('Visible buttons'), tearoff=tearoff)
    for w in TOOLBAR_BUTTONS:
        submenu.add_checkbutton(label=_(w.capitalize()),
            variable=menubar.tkopt.toolbar_vars[w],
            command=lambda m=menubar, w=w: m.mOptToolbarConfig(w))


# ************************************************************************
# *
# ************************************************************************

class MfxMenubar(Tkinter.Menu):
    addPath = None

    def __init__(self, master, **kw):
        self.name = kw["name"]
        tearoff = 0
        self.n = kw["tearoff"] = int(kw.get("tearoff", tearoff))
        Tkinter.Menu.__init__(self, master, **kw)

    def labeltoname(self, label):
        #print label, type(label)
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
                del cnf['name'] # TclError: unknown option "-name"
            else:
                name, label, underline = self.labeltoname(label)
                cnf["underline"] = cnf.get("underline", underline)
            cnf["label"] = label
            if name and self.addPath:
                path = str(self._w) + "." + name
                self.addPath(path, self, self.n, cnf.get("menu"))
        Tkinter.Menu.add(self, itemType, cnf)
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
            master.add_cascade(menu=self, name=name, label=label, underline=underline)


class PysolMenubarTkCommon:
    def __init__(self, app, top, progress=None):
        print "PysolMenubarTkCommon init called"
        self._createTkOpt()
        self._setOptions()
        # init columnbreak
        self.cb_max = int(self.top.winfo_screenheight()/23)
##         sh = self.top.winfo_screenheight()
##         self.cb_max = 22
##         if sh >= 600: self.cb_max = 27
##         if sh >= 768: self.cb_max = 32
##         if sh >= 1024: self.cb_max = 40
        self.progress = progress
        # create menus
        self.menubar = None
        self.menupath = {}
        self.keybindings = {}
        self._createMenubar()
        self.top = top

        if self.progress: self.progress.update(step=1)

        # set the menubar
        self.updateBackgroundImagesMenu()
        self.top.config(menu=self.menubar)

    def _createTkOpt(self):
        # structure to convert menu-options to Toolkit variables
        self.tkopt = Struct(
            gameid = Tkinter.IntVar(),
            gameid_popular = Tkinter.IntVar(),
            comment = Tkinter.BooleanVar(),
            autofaceup = Tkinter.BooleanVar(),
            autodrop = Tkinter.BooleanVar(),
            autodeal = Tkinter.BooleanVar(),
            quickplay = Tkinter.BooleanVar(),
            undo = Tkinter.BooleanVar(),
            bookmarks = Tkinter.BooleanVar(),
            hint = Tkinter.BooleanVar(),
            shuffle = Tkinter.BooleanVar(),
            highlight_piles = Tkinter.BooleanVar(),
            highlight_cards = Tkinter.BooleanVar(),
            highlight_samerank = Tkinter.BooleanVar(),
            highlight_not_matching = Tkinter.BooleanVar(),
            mahjongg_show_removed = Tkinter.BooleanVar(),
            shisen_show_hint = Tkinter.BooleanVar(),
            sound = Tkinter.BooleanVar(),
            auto_scale = Tkinter.BooleanVar(),
            cardback = Tkinter.IntVar(),
            tabletile = Tkinter.IntVar(),
            animations = Tkinter.IntVar(),
            redeal_animation = Tkinter.BooleanVar(),
            win_animation = Tkinter.BooleanVar(),
            shadow = Tkinter.BooleanVar(),
            shade = Tkinter.BooleanVar(),
            shade_filled_stacks = Tkinter.BooleanVar(),
            shrink_face_down = Tkinter.BooleanVar(),
            toolbar = Tkinter.IntVar(),
            toolbar_style = Tkinter.StringVar(),
            toolbar_relief = Tkinter.StringVar(),
            toolbar_compound = Tkinter.StringVar(),
            toolbar_size = Tkinter.IntVar(),
            statusbar = Tkinter.BooleanVar(),
            num_cards = Tkinter.BooleanVar(),
            helpbar = Tkinter.BooleanVar(),
            save_games_geometry = Tkinter.BooleanVar(),
            splashscreen = Tkinter.BooleanVar(),
            demo_logo = Tkinter.BooleanVar(),
            mouse_type = Tkinter.StringVar(),
            mouse_undo = Tkinter.BooleanVar(),
            negative_bottom = Tkinter.BooleanVar(),
            pause = Tkinter.BooleanVar(),
            theme = Tkinter.StringVar(),
            toolbar_vars = {},
        )
        for w in TOOLBAR_BUTTONS:
            self.tkopt.toolbar_vars[w] = Tkinter.BooleanVar()

    def _setOptions(self):
        tkopt, opt = self.tkopt, self.app.opt
        # set state of the menu items
        tkopt.autofaceup.set(opt.autofaceup)
        tkopt.autodrop.set(opt.autodrop)
        tkopt.autodeal.set(opt.autodeal)
        tkopt.quickplay.set(opt.quickplay)
        tkopt.undo.set(opt.undo)
        tkopt.hint.set(opt.hint)
        tkopt.shuffle.set(opt.shuffle)
        tkopt.bookmarks.set(opt.bookmarks)
        tkopt.highlight_piles.set(opt.highlight_piles)
        tkopt.highlight_cards.set(opt.highlight_cards)
        tkopt.highlight_samerank.set(opt.highlight_samerank)
        tkopt.highlight_not_matching.set(opt.highlight_not_matching)
        tkopt.shrink_face_down.set(opt.shrink_face_down)
        tkopt.shade_filled_stacks.set(opt.shade_filled_stacks)
        tkopt.mahjongg_show_removed.set(opt.mahjongg_show_removed)
        tkopt.shisen_show_hint.set(opt.shisen_show_hint)
        tkopt.sound.set(opt.sound)
        tkopt.auto_scale.set(opt.auto_scale)
        tkopt.cardback.set(self.app.cardset.backindex)
        tkopt.tabletile.set(self.app.tabletile_index)
        tkopt.animations.set(opt.animations)
        tkopt.redeal_animation.set(opt.redeal_animation)
        tkopt.win_animation.set(opt.win_animation)
        tkopt.shadow.set(opt.shadow)
        tkopt.shade.set(opt.shade)
        tkopt.toolbar.set(opt.toolbar)
        tkopt.toolbar_style.set(opt.toolbar_style)
        tkopt.toolbar_relief.set(opt.toolbar_relief)
        tkopt.toolbar_compound.set(opt.toolbar_compound)
        tkopt.toolbar_size.set(opt.toolbar_size)
        tkopt.toolbar_relief.set(opt.toolbar_relief)
        tkopt.statusbar.set(opt.statusbar)
        tkopt.num_cards.set(opt.num_cards)
        tkopt.helpbar.set(opt.helpbar)
        tkopt.save_games_geometry.set(opt.save_games_geometry)
        tkopt.demo_logo.set(opt.demo_logo)
        tkopt.splashscreen.set(opt.splashscreen)
        tkopt.mouse_type.set(opt.mouse_type)
        tkopt.mouse_undo.set(opt.mouse_undo)
        tkopt.negative_bottom.set(opt.negative_bottom)
        for w in TOOLBAR_BUTTONS:
            tkopt.toolbar_vars[w].set(opt.toolbar_vars.get(w, False))

    def connectGame(self, game):
        self.game = game
        if game is None:
            return
        assert self.app is game.app
        tkopt, opt = self.tkopt, self.app.opt
        tkopt.gameid.set(game.id)
        tkopt.gameid_popular.set(game.id)
        tkopt.comment.set(bool(game.gsaveinfo.comment))
        tkopt.pause.set(self.game.pause)
        if game.canFindCard():
            self._connect_game_find_card_dialog(game)
        else:
            self._destroy_find_card_dialog()
        self._connect_game_solver_dialog(game)

    # create a GTK-like path
    def _addPath(self, path, menu, index, submenu):
        if path not in self.menupath:
            ##print path, menu, index, submenu
            self.menupath[path] = (menu, index, submenu)

    def _getEnabledState(self, enabled):
        if enabled:
            return "normal"
        return "disabled"

    def updateProgress(self):
        if self.progress: self.progress.update(step=1)

