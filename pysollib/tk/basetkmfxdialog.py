import Tkinter

from tkwidget import MfxDialog

class BaseTkMfxDialog(MfxDialog):
    def _calcToolkit(self):
        return Tkinter

    def _calc_MfxDialog(self):
        return MfxDialog
