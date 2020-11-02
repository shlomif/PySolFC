# -*- coding: utf-8 -*-
#
# Usage:
# Load Directory: Look for folders that has cardsets in
# Click onto listbox to show cardset
# Info: gives infos about the sets, if available
# Arrow up/down flip through the sets

import os
from glob import glob
from six.moves import tkinter
from tkinter import filedialog  # messagebox

from PIL import Image, ImageTk


cardset_type = {
    '1': 'French',
    '2': 'Hanafuda',
    '3': 'Tarock',
    '4': 'Mahjongg',
    '5': 'Hexadeck',
    '6': 'Mughal Ganjifa',
    '7': 'Navagraha Ganjifa',
    '8': 'Dashavatara Ganjifa',
    '9': 'Trump only',
}

all_imgs = False


class Cardset:
    def __init__(self, dir, name, type, ext, x, y):
        self.dir, self.name, self.type, self.ext, self.x, self.y = \
            dir, name, type, ext, x, y


def create_cs_list(ls):

    cardsets_list = {}
    for f in ls:
        dir = os.path.split(f)[0]
        lines = open(f).readlines()
        l0 = lines[0].split(';')
        try:
            ext = l0[2]
        except IndexError:
            ext = '.gif'
        if len(l0) > 3:
            type = cardset_type[l0[3]]
        else:
            # type = 'Unknown'
            type = 'French'

        try:
            l1 = lines[1].split(';')
            if len(l1) > 1:
                name = l1[1].strip()
            else:
                print("\n Error: invalid config in ", dir, "\n")
                name = l1[0]

            l2 = lines[2].split()
            x, y = int(l2[0]), int(l2[1])
            cs = Cardset(dir, name, type, ext, x, y)
            cardsets_list[name] = cs
        except Exception:
            fehlermeldung = "Error: invalid config in " + str(dir)
            tkinter.messagebox.showerror(title=None, message=fehlermeldung)
    return cardsets_list


def show_cardset(*args):
    global label, photoliste

    if list_box.curselection():

        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]

        ls = glob(os.path.join(cs.dir, '[0-9][0-9][a-z]' + cs.ext))
        ls += glob(os.path.join(cs.dir, 'back*' + cs.ext))

        if all_imgs:
            ls += glob(os.path.join(cs.dir, 'bottom*' + cs.ext))
            ls += glob(os.path.join(cs.dir, 'l*' + cs.ext))

        ls.sort()

        canvas.delete("all")

        w, h, x, y, n = 0, 0, 0, 0, 0

        photoliste = []

        for file in ls:

            im = Image.open(file)
            # bilderliste.append(im)
            photo = ImageTk.PhotoImage(im, master=root)
            photoliste.append(photo)

            canvas.photo = photo

            xdiff, ydiff = 10, 10

            width = canvas.photo.width()
            height = canvas.photo.height()

            x = (xdiff + width) * (n % 4) + 10
            y = (ydiff + height) * (int(n / 4)) + 10

            canvas.create_image(x, y, image=canvas.photo, anchor='nw')

            w = max(w, x)
            h = max(h, y)

            n = n + 1

        w = 4 * (width + xdiff) + 10
        h = (1 + int((n - 1) / 4)) * (height + ydiff) + 10

        canvas.config(scrollregion=(0, 0, w, h))
        root.geometry("%dx%d" % (w + 220, root.winfo_height()))


def show_info(*args):
    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]

        fn = os.path.join(cs.dir, 'COPYRIGHT')

        top = tkinter.Toplevel()
        text = tkinter.Text(top)
        text.insert('insert', open(fn).read())
        text.pack(expand=tkinter.YES, fill=tkinter.BOTH)

        b_frame = tkinter.Frame(top)
        b_frame.pack(fill=tkinter.X)
        button = tkinter.Button(b_frame, text='Close', command=top.destroy)
        button.pack(side=tkinter.RIGHT)


def show_config(*args):
    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]

        fn = os.path.join(cs.dir, 'Config.txt')

        top = tkinter.Toplevel()
        text = tkinter.Text(top)
        text.insert('insert', open(fn).read())
        text.pack(expand=tkinter.YES, fill=tkinter.BOTH)

        b_frame = tkinter.Frame(top)
        b_frame.pack(fill=tkinter.X)
        button = tkinter.Button(b_frame, text='Close', command=top.destroy)
        button.pack(side=tkinter.RIGHT)


def on_mousewheel(event):
    shift = (event.state & 0x1) != 0
    scroll = -1 if event.delta > 0 else 1
    if shift:
        canvas.xview_scroll(scroll, "units")
    else:
        canvas.yview_scroll(scroll, "units")


def select_dir(*args):
    global data_dir

    dialog = filedialog.Directory(root)
    d = dialog.show()
    if d:
        data_dir = os.path.normpath(d)
        read_into_listbox()


def read_into_listbox():
    global cardsets_dict

    ls = glob(os.path.join(data_dir, '*', 'config.txt'))

    if ls:
        cardsets_dict = create_cs_list(ls)

        cardsets_list = list(cardsets_dict)
        cardsets_list.sort()

        list_box.delete(0, tkinter.END)

        for cs in cardsets_list:
            list_box.insert(tkinter.END, cs)


def create_widgets():
    global list_box, canvas  # label  # , label, zoom_label

    root = tkinter.Tk()

    list_box = tkinter.Listbox(root, exportselection=False)
    list_box.grid(row=0, column=0, rowspan=2, sticky=tkinter.NS)

    list_box.bind('<<ListboxSelect>>', show_cardset)

    sb = tkinter.Scrollbar(root)
    sb.grid(row=0, column=1, rowspan=2, sticky=tkinter.NS)
    list_box.config(yscrollcommand=sb.set)
    sb.config(command=list_box.yview)

    # create Canvas
    canvas = tkinter.Canvas(root, width=600, height=600, bg='#5eab6b')
    canvas.grid(row=0, column=2, sticky=tkinter.NSEW)
    canvas.bind('<4>', lambda e: canvas.yview_scroll(-5, 'unit'))
    canvas.bind('<5>', lambda e: canvas.yview_scroll(5, 'unit'))
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    sb = tkinter.Scrollbar(root)
    sb.grid(row=0, column=3, sticky=tkinter.NS)
    canvas.config(yscrollcommand=sb.set)
    sb.config(command=canvas.yview)

    if True:
        sb = tkinter.Scrollbar(root, orient=tkinter.HORIZONTAL)
        sb.grid(row=1, column=2, sticky=tkinter.EW)
        canvas.config(xscrollcommand=sb.set)
        sb.config(command=canvas.xview)

    # create buttons
    b_frame = tkinter.Frame(root)
    b_frame.grid(row=3, column=0, columnspan=4, sticky=tkinter.EW)

    button = tkinter.Button(b_frame, text='Quit',
                            command=root.destroy, width=8)
    button.pack(side=tkinter.RIGHT)

    button = tkinter.Button(b_frame, text='Info', command=show_info, width=8)
    button.pack(side=tkinter.RIGHT)

    button = tkinter.Button(b_frame, text='Config',
                            command=show_config, width=8)
    button.pack(side=tkinter.RIGHT)

    button = tkinter.Button(b_frame, text='Select Directory',
                            command=select_dir, width=14)
    button.place(x=200, y=0)

    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)

    root.title('Show Cardsets')
    root.wm_geometry("%dx%d+%d+%d" % (800, 600, 40, 40))
    return root


if __name__ == '__main__':

    current_working_directory = os.getcwd()
    data_dir = current_working_directory

    # print("\n current_working_directory")
    # print(data_dir)  # TEST

    root = create_widgets()
    read_into_listbox()

    root.mainloop()
