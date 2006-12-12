"""
A number of function that enhance PySol on MacOSX when it used as a normal
GUI application (as opposed to an X11 application).
"""
import sys
from Tkinter import Menu, Text, TclError

def runningAsOSXApp():
    """ Returns True iff running from the PySol.app bundle on OSX """
    return (sys.platform == 'darwin' and 'PySol.app' in sys.argv[0])

def hideTkConsole(root):
    try:
        root.tk.call('console', 'hide')
    except TclError:
        pass
    
def setupApp(app):
    """
    Perform setup for the OSX application bundle.
    """
    if not runningAsOSXApp(): return

    hideTkConsole(app.top)
    #overrideRootMenu(root, flist)
