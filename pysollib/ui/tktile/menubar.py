import re
import Tkinter

from pysollib.mfxutil import kwdefault
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
        self._createTkOpt()
        self._setOptions()
        # init columnbreak
        self.__cb_max = int(self.top.winfo_screenheight()/23)
##         sh = self.top.winfo_screenheight()
##         self.__cb_max = 22
##         if sh >= 600: self.__cb_max = 27
##         if sh >= 768: self.__cb_max = 32
##         if sh >= 1024: self.__cb_max = 40
        self.progress = progress
        # create menus
        self.__menubar = None
        self.__menupath = {}
        self.__keybindings = {}
        self._createMenubar()
        self.top = top

        if self.progress: self.progress.update(step=1)

        # set the menubar
        self.updateBackgroundImagesMenu()
        self.top.config(menu=self.__menubar)

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
