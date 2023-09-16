# flake8: noqa
# LB230914.

try:
    import jnius
    from android.runnable import run_on_ui_thread
except ImportError:
    jnius = None
    def run_on_ui_thread(a):
        pass

class AndroidToast(object):
    def __init__(self):
        if jnius is None:
            return
        self.PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
        self.Toast = jnius.autoclass('android.widget.Toast')
        self.String = jnius.autoclass('java.lang.String')
        self.context = self.PythonActivity.mActivity

    @run_on_ui_thread
    def toastShort(self, message):
        if jnius is not None:
            jtext = jnius.cast('java.lang.CharSequence', self.String(message))
            toast = self.Toast.makeText(
                self.context, jtext, self.Toast.LENGTH_SHORT)
            toast.show()

    @run_on_ui_thread
    def toastLong(self, message):
        if jnius is not None:
            jtext = jnius.cast('java.lang.CharSequence', self.String(message))
            toast = self.Toast.makeText(
                self.context, jtext, self.Toast.LENGTH_LONG)
            toast.show()

AndroidToaster = AndroidToast()
