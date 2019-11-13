import logging
try:
    import jnius
except ImportError:
    jnius = None

# link address of related support library:
# https://maven.google.com/com/android/support/support-v4/24.1.1/support-v4-24.1.1.aar

# inspired by stackoverflow.com/questions/47510030/
# as functools (reduce,partial,map) do not seem to work in python3 on android,
# implemented in a classic functional way.
# LB190927.
# wait loop removed. (Implement it in external code if needed.)
# LB191011.


class AndroidPerms(object):
    def __init__(self):
        if jnius is None:
            return
        self.PythonActivity = jnius.autoclass(
            'org.kivy.android.PythonActivity')
        self.Compat = jnius.autoclass(
            'android.support.v4.content.ContextCompat')
        self.currentActivity = jnius.cast(
            'android.app.Activity', self.PythonActivity.mActivity)

    def getPerm(self, permission):
        if jnius is None:
            return True
        p = self.Compat.checkSelfPermission(self.currentActivity, permission)
        return p == 0

    # check actual permissions
    def getPerms(self, permissions):
        if jnius is None:
            return True
        haveperms = True
        for perm in permissions:
            haveperms = haveperms and self.getPerm(perm)
        return haveperms

    # invoke the permissions dialog
    def requestPerms(self, permissions):
        if jnius is None:
            return True
        logging.info("androidperms: invoke permission dialog")
        self.currentActivity.requestPermissions(permissions, 0)
        return


def getStoragePerm():
    ap = AndroidPerms()
    return ap.getPerms(
        ["android.permission.WRITE_EXTERNAL_STORAGE"])


def requestStoragePerm():
    ap = AndroidPerms()
    # ap.requestPerms(
    #    ["android.permission.READ_EXTERNAL_STORAGE","android.permission.WRITE_EXTERNAL_STORAGE"])
    ap.requestPerms(
        ["android.permission.WRITE_EXTERNAL_STORAGE"])
