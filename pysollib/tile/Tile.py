
from pysollib.settings import WIN_SYSTEM

import Tkinter
from Tkconstants import *


BooleanVar = Tkinter.BooleanVar
IntVar = Tkinter.IntVar
DoubleVar = Tkinter.DoubleVar
StringVar = Tkinter.StringVar

Tk = Tkinter.Tk
Toplevel = Tkinter.Toplevel
Menu = Tkinter.Menu
Message = Tkinter.Message
Listbox = Tkinter.Listbox
Text = Tkinter.Text
Canvas = Tkinter.Canvas
Spinbox = Tkinter.Spinbox

PhotoImage = Tkinter.PhotoImage
Event = Tkinter.Event
TkVersion = Tkinter.TkVersion
TclError = Tkinter.TclError


class Style(Tkinter.Misc):
    def __init__(self, master=None):
        if master is None:
            master = Tkinter._default_root
        self.tk = master.tk

    def default(self, style, **kw):
        """Sets the default value of the specified option(s) in style"""
        pass

    def map_style(self, **kw):
        """Sets dynamic values of the specified option(s) in style. See 
        "STATE MAPS", below."""
        pass

    def layout(self, style, layoutSpec):
        """Define the widget layout for style style. See "LAYOUTS" below 
        for the format of layoutSpec. If layoutSpec is omitted, return the 
        layout specification for style style. """
        pass

    def element_create(self, name, type, *args):
        """Creates a new element in the current theme of type type. The 
        only built-in element type is image (see image(n)), although 
        themes may define other element types (see 
        Ttk_RegisterElementFactory). 
        """
        pass

    def element_names(self):
        """Returns a list of all elements defined in the current theme. """
        pass

    def theme_create(self, name, parent=None, basedon=None):
        """Creates a new theme. It is an error if themeName already exists. 
        If -parent is specified, the new theme will inherit styles, elements, 
        and layouts from the parent theme basedon. If -settings is present, 
        script is evaluated in the context of the new theme as per style theme 
        settings. 
        """
        pass

    def theme_settings(self, name, script):
        """Temporarily sets the current theme to themeName, evaluate script, 
        then restore the previous theme. Typically script simply defines styles 
        and elements, though arbitrary Tcl code may appear. 
        """
        pass

    def theme_names(self):
        """Returns a list of the available themes. """
        return self.tk.call("style", "theme", "names")

    def theme_use(self, theme):   
        """Sets the current theme to themeName, and refreshes all widgets."""
        return self.tk.call("style", "theme", "use", theme)

    def configure(self, style, cnf={}, **kw):
        """Sets  the  default value of the specified option(s)
        in style."""
        opts = self._options(cnf, kw)
        return self.tk.call("style", "configure", style, *opts)
    config = configure

    def lookup(self, style, option, state=None, default=None):
        """Returns  the  value  specified for -option in style
        style in state state,  using  the  standard  lookup
        rules  for  element  options.   state  is a list of
        state names; if omitted, it defaults  to  all  bits
        off  (the  ``normal'' state).  If the default argu-
        ment is present, it is used as a fallback value  in
        case no specification for -option is found."""
        opts = []
        if state:
            opts = [state]
        if default:
            opts.append(default)
        return self.tk.call("style", "lookup", style, "-"+option, *opts)



class Widget(Tkinter.Widget, Style):
    def __init__(self, master, widgetName=None, cnf={}, kw={}, extra=()):
        if not widgetName:
            ## why you would ever want to create a Tile Widget is behond me!
            widgetName="ttk::widget"
        Tkinter.Widget.__init__(self, master, widgetName, cnf, kw)

    def instate(self,  spec=None, script=None):
        """Test the widget's state. If script is not specified, returns 1
        if the widget state matches statespec and 0 otherwise. If script 
        is specified, equivalent to if {[pathName instate stateSpec]} 
        script. 
        """
        return self.tk.call(self._w, "instate", spec, script)

    def state(self, spec=None):
        """Modify or inquire widget state. If stateSpec is present, sets 
        the widget state: for each flag in stateSpec, sets the corresponding
        flag or clears it if prefixed by an exclamation point. Returns a new
        state spec indicating which flags were changed: ''set changes 
        [pathName state spec] ; pathName state $changes'' will restore 
        pathName to the original state. If stateSpec is not specified, 
        returns a list of the currently-enabled state flags. 
        """
        return self.tk.call(self._w, "state", spec)


class Button(Widget, Tkinter.Button):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::button", cnf, kw)


class Checkbutton(Widget, Tkinter.Checkbutton):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::checkbutton", cnf, kw)


class Combobox(Widget, Tkinter.Entry):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::combobox", cnf, kw)

    def current(self, index=None):
        """If index is supplied, sets the combobox value to the element
        at position newIndex in the list of -values. Otherwise, returns 
        the index of the current value in the list of -values or -1 if 
        the current value does not appear in the list.
        """
        return self.tk.call(self._w, "current", index)


class Entry(Widget, Tkinter.Entry):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::entry", cnf, kw)

    def validate(self):
        """Force revalidation, independent of the conditions specified by 
        the -validate option. Returns 0 if the -validatecommand returns a
        false value, or 1 if it returns a true value or is not specified.
        """
        return self.tk.call(self._w, "validate")


class Label(Widget, Tkinter.Label):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::label", cnf, kw)


class Frame(Widget, Tkinter.Frame):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::frame", cnf, kw)


class Sizegrip(Widget):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::sizegrip", cnf, kw)


class LabelFrame(Widget, Tkinter.LabelFrame):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::labelframe", cnf, kw)


class Menubutton(Widget, Tkinter.Menubutton):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::menubutton", cnf, kw)


class Scale(Widget, Tkinter.Scale):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::scale", cnf, kw)


class Notebook(Widget):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::notebook", cnf, kw)

    def add(self, child, cnf=(), **kw):
        """Adds a new tab to the notebook. When the tab is selected, the 
        child window will be displayed. child must be a direct child of 
        the notebook window. See TAB OPTIONS for the list of available 
        options. 
        """
        return self.tk.call((self._w, "add", child) +  self._options(cnf, kw))

    def forget(self, index):
        """Removes the tab specified by index, unmaps and unmanages the 
        associated child window. 
        """
        return self.tk.call(self._w, "forget", index)

    def index(self, index):
        """Returns the numeric index of the tab specified by index, or 
        the total number of tabs if index is the string "end". 
        """
        return self.tk.call(self._w, "index")

    def select(self, index):
        """Selects the specified tab; the associated child pane will 
        be displayed, and the previously-selected pane (if different)
        is unmapped. 
        """
        return self.tk.call(self._w, "select", index)

    def tab(self, index, **kw):
        """Query or modify the options of the specific tab. If no
        -option is specified, returns a dictionary of the tab option 
        values. If one -option is specified, returns the value of tha
        t option. Otherwise, sets the -options to the corresponding 
        values. See TAB OPTIONS for the available options. 
        """
        return self.tk.call((self._w, "tab", index) + self._options(kw))

    def tabs(self):
        """Returns a list of all pane windows managed by the widget."""
        return self.tk.call(self._w, "tabs")


class Paned(Widget):
    """
    WIDGET OPTIONS
        Name	Database name	Database class
        -orient	orient	Orient
        Specifies the orientation of the window. If vertical, subpanes
        are stacked top-to-bottom; if horizontal, subpanes are stacked 
        left-to-right.

    PANE OPTIONS
        The following options may be specified for each pane:
        Name	Database name	Database class
        -weight	weight	Weight
        An integer specifying the relative stretchability of the pane.
        When the paned window is resized, the extra space is added or
        subracted to each pane proportionally to its -weight
        """
    def __init__(self, master=None, cnf={}, **kw):
        if 'orient' not in kw:
            kw['orient'] = 'horizontal'
        ##Widget.__init__(self, master, "ttk::paned", cnf, kw)
        Widget.__init__(self, master, "ttk::panedwindow", cnf, kw)

    def add(self, subwindow, **kw):
        """Adds a new pane to the window. subwindow must be a direct child of
        the paned window pathname. See PANE OPTIONS for the list of available 
        options. 
        """
        return self.tk.call((self._w, "add", subwindow) + self._options(kw))

    def forget(self,  pane):
        """Removes the specified subpane from the widget. pane is either an 
        integer index or the name of a managed subwindow. 
        """
        self.tk.call(self._w, "forget", pane)

    def insert(self, pos, subwindow, **kw):
        """Inserts a pane at the specified position. pos is either the string 
        end, an integer index, or the name of a managed subwindow. If subwindow 
        is already managed by the paned window, moves it to the specified 
        position. See PANE OPTIONS for the list of available options. 
        """
        return self.tk.call((self._w, "insert", pos, subwindow) + self._options(kw))

    def pane(self, pane, **kw):
        """Query or modify the options of the specified pane, where pane is 
        either an integer index or the name of a managed subwindow. If no 
        -option is specified, returns a dictionary of the pane option values. 
        If one -option is specified, returns the value of that option. 
        Otherwise, sets the -options to the corresponding values. 
        """
        return self.tk.call((self._w, "pane", pane) + self._options(kw))

PanedWindow = Paned


class Progressbar(Widget):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::progressbar", cnf, kw)

    def step(self, amount=1.0):
        """Increments the -value by amount. amount defaults to 1.0 
        if omitted. """
        return self.tk.call(self._w, "step", amount)

    def start(self):
        self.tk.call("ttk::progressbar::start", self._w)

    def stop(self):
        self.tk.call("ttk::progressbar::stop", self._w)


class Radiobutton(Widget, Tkinter.Radiobutton):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::radiobutton", cnf, kw)


class Scrollbar(Widget, Tkinter.Scrollbar):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::scrollbar", cnf, kw)

# from http://tkinter.unpythonic.net/wiki/PyLocateTile :
# standard Tk scrollbars work on OS X, but Tile ones look weird
if WIN_SYSTEM == "aqua":
    Scrollbar = Tkinter.Scrollbar


class Separator(Widget):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::separator", cnf, kw)


class Treeview(Widget, Tkinter.Listbox):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, 'ttk::treeview', cnf, kw)

    def children(self, item, newchildren=None):
        """If newchildren is not specified, returns the list of 
        children belonging to item.

        If newchildren is specified, replaces item's child list 
        with newchildren. Items in the old child list not present 
        in the new child list are detached from the tree. None of 
        the items in newchildren may be an ancestor of item.
        """
        return self.tk.call(self._w, "children", item, newchildren)

    def column(self, column, **kw):
        """Query or modify the options for the specified column. 
        If no options are specified, returns a dictionary of 
        option/value pairs. If a single option is specified, 
        returns the value of that option. Otherwise, the options
        are updated with the specified values. The following 
        options may be set on each column:

        -id name
            The column name. This is a read-only option. For example, 
            [$pathname column #n -id] returns the data column 
            associated with data column #n. 
        -anchor
            Specifies how the text in this column should be aligned 
            with respect to the cell. One of n, ne, e, se, s, sw, w, 
            nw, or center. 
        -width w
            The width of the column in pixels. Default is something 
            reasonable, probably 200 or so. 
        """
        return self.tk.call((self._w, 'column', column) + self._options(kw))

    def delete(self, items):
        """Deletes each of the items and all of their descendants. 
        The root item may not be deleted. See also: detach. 
        """
        return self.tk.call(self._w, "delete", items)

    def detach(self, items):
        """Unlinks all of the specified items from the tree. The 
        items and all of their descendants are still present and 
        may be reinserted at another point in the tree but will 
        not be displayed. The root item may not be detached. See
        also: delete. 
        """
        return self.tk.call(self._w, "detach", items)

    def exists(self, item):
        """Returns 1 if the specified item is present in the 
        tree, 0 otherwise. 
        """
        return self.tk.call(self._w, "exists", item)

    def focus(self, item=None):
        """If item is specified, sets the focus item to item. 
        Otherwise, returns the current focus item, or {} if there
        is none. 
        """
        return self.tk.call(self._w, "focus", item)

    def heading(self, column, **kw):
        """Query or modify the heading options for the specified 
        column. Valid options are:

        -text text
            The text to display in the column heading. 
        -image imageName
            Specifies an image to display to the right of the column heading. 
        -command script
            A script to evaluate when the heading label is pressed. 
        """
        return self.tk.call((self._w, 'heading', column) + self._options(kw))

    def identify(self, x, y):
        """Returns a description of the widget component under the point given 
        by x and y. The return value is a list with one of the following forms:

        heading #n
            The column heading for display column #n. 
        separator #n
            The border to the right of display column #n. 
        cell itemid #n
            The data value for item itemid in display column #n. 
        item itemid element
            The tree label for item itemid; element is one of text, image, or 
            indicator, or another element name depending on the style. 
        row itemid
            The y position is over the item but x does not identify any element
            or displayed data value. 
        nothing
            The coordinates are not over any identifiable object. 

        See COLUMN IDENTIFIERS for a discussion of display columns and data 
        columns.
        """
        pass

    def index(self, item):
        """Returns the integer index of item within its parent's list of 
        children. 
        """
        pass

    def insert(self, parent, index, id=None, **kw):
        """Creates a new item. parent is the item ID of the parent item, or 
        the empty string {} to create a new top-level item. index is an 
        integer, or the value end, specifying where in the list of parent's 
        children to insert the new item. If index is less than or equal to 
        zero, the new node is inserted at the beginning; if index is greater 
        than or equal to the current number of children, it is inserted at the 
        end. If -id is specified, it is used as the item identifier; id must 
        not already exist in the tree. Otherwise, a new unique identifier is 
        generated.
        returns the item identifier of the newly created item. See ITEM 
        OPTIONS for the list of available options.
        """
        if not parent: parent = ''
        args = (self._w, 'insert', parent, index)
        if id: args = args + ('-id', id)
        return self.tk.call(args + self._options(kw))

    def item(item, **kw):
        """Query or modify the options for the specified item. If no -option 
        is specified, returns a dictionary of option/value pairs. If a single 
        -option is specified, returns the value of that option. Otherwise, the
        item's options are updated with the specified values. See ITEM OPTIONS 
        for the list of available options. 
        """
        pass

    def move(self, item, parent, index):
        """Moves item to position index in parent's list of children. It is 
        illegal to move an item under one of its descendants.

        If index is less than or equal to zero, item is moved to the 
        beginning; if greater than or equal to the number of children, it's 
        moved to the end.
        """
        pass

    def next(self, item):
        """Returns the identifier of item's next sibling, or {} if item is the 
        last child of its parent. 
        """
        pass

    def parent(self, item):
        """Returns the ID of the parent of item, or {} if item is at the top 
        level of the hierarchy. 
        """
        pass

    def prev(self, item):
        """Returns the identifier of item's previous sibling, or {} if item is 
        the first child of its parent. 
        """
        pass

    def selection(self):
        """Returns the list of selected items"""
        return self.tk.call(self._w, "selection")

    def selection_set(self, items):
        """items becomes the new selection. """
        pass

    def selection_add(self, items):
        """Add items to the selection """
        pass

    def selection_remove(self, items):
        """Remove items from the selection """
        pass

    def selection_toggle(self, items):
        """Toggle the selection state of each item in items. """
        pass

    def set(self, item, column, value=None):
        """If value is specified, sets the value of column column in item item, 
        otherwise returns the current value. See COLUMN IDENTIFIERS. 
        """
        pass



if __name__=="__main__":
    def callback():
        print "Hello"

    root = Tkinter.Tk()
    root.tk.call("package", "require", "tile")

    b = Button(root, text="Tile Button", command=callback)
    b.pack()

    #~ c = Checkbutton(root)
    #~ c.pack()
    #~ print b.theme_names()

    #~ cb = Combobox(root)
    #~ cb.pack()

    #~ e = Entry(root)
    #~ e.validate()
    #~ e.pack()

    #~ l = Label(root, text="Tile Label")
    #~ l.pack()


    #~ mb = Menubutton(root)
    #~ mb.pack()


    #~ nb = Notebook(root)

    #~ f1 = Label(nb, text="page1")
    #~ nb.add(f1, text="Page1")
    #~ f1.pack()

    #~ f2 =  Label(nb, text="page2")
    #~ nb.add(f2, text="Page 2")
    #~ f2.pack()

    #~ nb.pack()


    pb = Progressbar(root, mode="indeterminate")
    pb.pack()


    pb.start()
    b = Button(root, text="Start", command=pb.start)
    b.pack()
    b = Button(root, text="Stop", command=pb.stop)
    b.pack()

    #~ rb = Radiobutton(root)
    #~ rb.pack()

    #~ text = Tkinter.Text(root)
    #~ scrol = Scrollbar(root)
    #~ text.pack(side="left", fill="both", expand="yes")
    #~ scrol.pack(side="left", fill="y")
    #~ text['yscrollcommand'] = scrol.set
    #~ scrol['command'] = text.yview


    #~ l = Label(root, text="Label1")
    #~ l.pack()
    #~ s = Separator(root)
    #~ s.pack(fill="x")
    #~ l = Label(root, text="Label2")
    #~ l.pack()


    b.theme_use("default")

    #~ b1 = Tkinter.Button(root, text="Tk Button", command=callback)
    #~ b1.pack()


    panes = Paned(root)
    panes.pack(fill="both", expand="yes")

    label1 = Label(panes, text="pane1")
    label2 = Label(panes, text="Pane2")


    panes.add(label1)
    panes.add(label2)




    #~ tree = Treeview(root, columns=("One", "Two", "Three"))

    #~ tree.insert(None, "end", text="Hello")

    #~ tree.pack()

    root.mainloop()
