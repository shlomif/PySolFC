from pysollib.tk.tkwidget import MfxDialog

from six.moves import tkinter


class BaseTkMfxDialog(MfxDialog):
    def _calcToolkit(self):
        return tkinter

    def _calc_MfxDialog(self):
        return MfxDialog
