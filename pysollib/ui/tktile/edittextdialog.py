import tkinter

from pysollib.mfxutil import KwStruct
from pysollib.mygettext import _


class BaseEditTextDialog:
    def __init__(self, parent, title, text, **kw):
        kw = self.initKw(kw)
        self._calc_MfxDialog().__init__(
            self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        self.top.wm_minsize(300, 150)

        #
        self.text_w = tkinter.Text(top_frame, bd=1, relief="sunken",
                                   wrap="word", width=64, height=16)
        self.text_w.pack(side='left', fill="both", expand=True)
        # self.text_w.pack(side='top', padx=kw.padx, pady=kw.pady)
        vbar = self._calcToolkit().Scrollbar(top_frame)
        vbar.pack(side='right', fill='y')
        self.text_w["yscrollcommand"] = vbar.set
        vbar["command"] = self.text_w.yview
        #
        self.text = ""
        if text:
            self.text = text
            old_state = self.text_w["state"]
            self.text_w.config(state="normal")
            self.text_w.insert("insert", self.text)
            self.text_w.config(state=old_state)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.text_w
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
                      strings=(_("&OK"), _("&Cancel")),
                      default=-1,
                      resizable=self._calc_Resizable(),
                      separator=False,
                      )
        return self._calc_MfxDialog().initKw(self, kw)

    def destroy(self):
        self.text = self.text_w.get("1.0", "end")
        self._calc_MfxDialog().destroy(self)

    def wmDeleteWindow(self, *event):   # ignore
        pass

    def mCancel(self, *event):          # ignore <Escape>
        pass
