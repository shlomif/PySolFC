from six.moves import tkinter_ttk as ttk

from .tkwidget import MfxDialog


class BaseTileMfxDialog(MfxDialog):
    def _calcToolkit(self):
        return ttk

    def _calc_MfxDialog(self):
        return MfxDialog
