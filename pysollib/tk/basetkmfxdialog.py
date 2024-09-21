import tkinter

from pysollib.tk.tkwidget import MfxDialog


class BaseTkMfxDialog(MfxDialog):
    def _calcToolkit(self):
        return tkinter

    def _calc_MfxDialog(self):
        return MfxDialog
