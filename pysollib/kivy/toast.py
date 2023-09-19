# ================================================================
# flake8: noqa
# Toast implementation
# LB230919

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import RoundedRectangle

# ================================================================

class Toast(Label):
    def __init__(self, **kw):
        super().__init__(opacity=0, **kw)

        self.duration = 4.0
        self.tsize = self.size
        self.rsize = 20
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 0.8)
            self.rect = RoundedRectangle()
        self.bind(size=self._update_rect)
        self.bind(texture_size=self.eval_size)

    def eval_size(self,instance,size):
        width, height = size
        if width > self.parent.width:
            instance.text_size = (self.parent.width, None)
            instance.texture_update()
            width, height = instance.texture_size
        ads = height * 1.7
        self.tsize = (width + ads, height + ads)
        self.rsize = [(ads+height)/2.0,]
        #print(self.tsize,self.rsize)

    def _update_rect(self, instance, value):
        self.rect.size = self.tsize
        self.rect.pos = (instance.center_x-self.tsize[0]/2.0,instance.center_y-self.tsize[1]/2.0)
        self.rect.radius = self.rsize

    def stop(self, *args):
        self.parent.remove_widget(self)

    def hide(self, *args):
        anim = Animation(opacity=0, duration=0.4)
        anim.bind(on_complete=self.stop)
        anim.start(self)

    # Timed display with fadein/-out
    def show(self, parent=None, duration=2.0):
        if parent is None:
            return
        self.duration = duration
        parent.add_widget(self)
        anim = Animation(opacity=1, duration=0.4)
        anim.start(self)
        Clock.schedule_once(self.hide,self.duration)

    # Popup display - use 'stop' to terminate.
    def start(self,parent=None):
        if parent is None:
            return
        self.opacity = 1
        parent.add_widget(self)

# ================================================================
