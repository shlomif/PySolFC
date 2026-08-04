import logging

from kivy.utils import platform

try:
    import jnius
except ImportError:
    jnius = None


class AndroidSafeArea:

    def __init__(self):
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
        self._decor_view = None
        if platform != 'android' or jnius is None:
            return
        try:
            PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            self._decor_view = activity.getWindow().getDecorView()
        except Exception:
            logging.exception('AndroidSafeArea: failed to access decor view')

    def refresh(self):
        if self._decor_view is None:
            return False
        try:
            window_insets = self._decor_view.getRootWindowInsets()
            if window_insets is None:
                return False
            VERSION = jnius.autoclass('android.os.Build$VERSION')
            sdk_int = VERSION.SDK_INT
            if sdk_int >= 30:
                WindowInsetsType = jnius.autoclass(
                    'android.view.WindowInsets$Type')
                mask = (WindowInsetsType.systemBars()
                        | WindowInsetsType.displayCutout())
                insets = window_insets.getInsets(mask)
                left, top = insets.left, insets.top
                right, bottom = insets.right, insets.bottom
            else:
                left = window_insets.getSystemWindowInsetLeft()
                top = window_insets.getSystemWindowInsetTop()
                right = window_insets.getSystemWindowInsetRight()
                bottom = window_insets.getSystemWindowInsetBottom()
                if sdk_int >= 28:
                    cutout = window_insets.getDisplayCutout()
                    if cutout is not None:
                        left = max(left, cutout.getSafeInsetLeft())
                        top = max(top, cutout.getSafeInsetTop())
                        right = max(right, cutout.getSafeInsetRight())
                        bottom = max(bottom, cutout.getSafeInsetBottom())
            self.left, self.top = left, top
            self.right, self.bottom = right, bottom
            logging.info(
                'AndroidSafeArea: left=%s top=%s right=%s bottom=%s',
                self.left, self.top, self.right, self.bottom)
            return True
        except Exception:
            logging.exception('AndroidSafeArea: failed to read window insets')
            return False
