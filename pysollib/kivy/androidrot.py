# flake8: noqa
# LB230914.

from pysollib.kivy.androidtoast import AndroidToaster
from pysollib.mygettext import _
try:
    import jnius
except ImportError:
    jnius = None

class AndroidRot(object):
    def __init__(self):
        self.locked = False
        if jnius is None:
            return
        self.PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
        self.ActivityInfo = jnius.autoclass('android.content.pm.ActivityInfo')
        self.currentActivity = jnius.cast('android.app.Activity', self.PythonActivity.mActivity)

    def isLocked(self):
        return self.locked

    def lock(self, toaster=True):
        if jnius is not None:
            if not self.locked:
                self.currentActivity.setRequestedOrientation(
                    self.ActivityInfo.SCREEN_ORIENTATION_LOCKED)
                if toaster:
                    AndroidToaster.toastShort(_("screen rotation disabled"))
        self.locked = True

    def unlock(self, toaster=True):
        if jnius is not None:
            if self.locked:
                self.currentActivity.setRequestedOrientation(
                    self.ActivityInfo.SCREEN_ORIENTATION_FULL_SENSOR)
                if toaster:
                    AndroidToaster.toastShort(_("screen rotation enabled"))
        self.locked = False

    def toggle(self):
        if self.locked:
            self.unlock()
        else:
            self.lock()
        return self.isLocked()

AndroidScreenRotation = AndroidRot()
