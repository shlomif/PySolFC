# ================================================================
# Toast implementation
# LB230919-22

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from pysollib.kivy.LBase import LBase

# ================================================================


class Toast(Label, LBase):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.duration = 4.0
        self.tsize = self.size
        self.rsize = [2, ]
        self.hook = None
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 0.85)
            self.rect = RoundedRectangle()
        self.bind(texture_size=self.eval_size)
        self.bind(size=self._update_rect)

    def eval_size(self, instance, size):
        width, height = size
        if self.parent is not None:
            if width > self.parent.width:
                instance.text_size = (self.parent.width, None)
                instance.texture_update()
                width, height = instance.texture_size
        ads = height * 1.7
        self.rsize = [(ads+height)/2.0, ]
        self.tsize = (width + ads, height + ads)
        # print('eval_size:',self.tsize,self.rsize)

    def _update_rect(self, instance, value):
        self.rect.size = self.tsize
        self.rect.pos = (instance.center_x-self.tsize[0]/2.0,
                         instance.center_y-self.tsize[1]/2.0)
        self.rect.radius = self.rsize
        # print('update_rect:',self.tsize,self.rsize,self.size)

    def start(self, *args):
        Clock.schedule_once(self.extro, self.duration)

    def stop(self, *args):
        if self.parent is not None:
            self.parent.remove_widget(self)

    def intro(self, *args):
        anim = Animation(opacity=1, duration=0.55)
        anim.bind(on_complete=self.start)
        anim.start(self)

    def extro(self, *args):
        anim = Animation(opacity=0, duration=0.45)
        anim.bind(on_complete=self.stop)
        anim.start(self)

    # Timed display with fadein/-out, click also works
    def show(self, parent=None, duration=2.0, offset=(0.0, -0.25), hook=None):
        if parent is None:
            return
        self.hook = hook
        duration = duration - 1.0
        if duration > 0.0: self.duration = duration  # noqa
        else: self.duration = 0.0  # noqa
        self.opacity = 0
        self.pos = [parent.width*offset[0], parent.height*offset[1]]
        parent.add_widget(self)
        self.intro()

    # Popup (needs call to stop to terminate or click on it)
    def popup(self, parent=None, offset=(0.0, -0.25), hook=None):
        if parent is None:
            return
        self.hook = hook
        self.opacity = 1
        self.pos = [parent.width*offset[0], parent.height*offset[1]]
        parent.add_widget(self)

    # dismiss popup by clicking on it.
    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        pos = [self.pos[0]+(self.width-self.rect.size[0])/2.0,
               self.pos[1]+(self.height-self.rect.size[1])/2.0]
        w = Widget(size=self.rect.size, pos=pos)
        if w.collide_point(*touch.pos):
            self.stop()
            if self.hook is not None:
                self.hook()
            return True
        return False

# ================================================================
