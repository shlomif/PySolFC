#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-

#
# Usage:
# Load Directory: Look for folders that has cardsets in
# Click onto listbox to show cardset
# Info: gives infos about the sets, if available
# Arrow up/down flip through the sets

import os
from glob import glob

from tkinter import filedialog
from tkinter import messagebox
from six.moves import tkinter

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

# Never show bottom cards
ALL_IMGS = False


photoliste = []
cardsets_dict = None
list_box = None
canvas = None
data_dir = None


class Cardset:
    def __init__(self, cs_dir, name, cs_type, ext, card_x, card_y):
        self.cs_dir = cs_dir
        self.name = name
        self.cs_type = cs_type
        self.ext = ext
        self.card_x = card_x
        self.card_y = card_y


def create_cs_list(ls):

    cardsets_list = {}
    for files in ls:
        cs_dir = os.path.split(files)[0]
        lines = open(files).readlines()
        line_0 = lines[0].split(';')
        try:
            ext = line_0[2]
        except IndexError:
            ext = '.gif'
        if len(line_0) > 3:
            cs_type = cardset_type[line_0[3]]
        else:
            # type = 'Unknown'
            cs_type = 'French'

        try:
            line_1 = lines[1].split(';')
            if len(line_1) > 1:
                name = line_1[1].strip()
            else:
                print("\n Error: invalid config in ", cs_dir, "\n")
                name = line_1[0]

            line_2 = lines[2].split()
            card_x, card_y = int(line_2[0]), int(line_2[1])
            cs = Cardset(cs_dir, name, cs_type, ext, card_x, card_y)
            cardsets_list[name] = cs

        except RuntimeError:
            fehlermeldung = "Error: invalid config in " + str(cs_dir)
            messagebox.showerror(title=None, message=fehlermeldung)
    return cardsets_list


def show_cardset(*args):

    global photoliste
    photoliste = []

    if list_box.curselection():

        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]

        ls = glob(os.path.join(cs.cs_dir, '[0-9][0-9][a-z]' + cs.ext))
        ls += glob(os.path.join(cs.cs_dir, 'back*' + cs.ext))

        if ALL_IMGS:  # Bottom cards will not be shown
            ls += glob(os.path.join(cs.cs_dir, 'bottom*' + cs.ext))
            ls += glob(os.path.join(cs.cs_dir, 'l*' + cs.ext))

        ls.sort()

        canvas.delete("all")

        width, height, x_pos, y_pos, number = 0, 0, 0, 0, 0

        for cs_file in ls:

            image = Image.open(cs_file)
            # bilderliste.append(im)
            photo = ImageTk.PhotoImage(image, master=root)
            photoliste.append(photo)

            im_width = photo.width()
            im_height = photo.height()

            x_pos = (10 + im_width) * (number % 4) + 10
            y_pos = (10 + im_height) * (int(number / 4)) + 10

            canvas.create_image(x_pos, y_pos, image=photo, anchor='nw')

            width = max(width, x_pos)
            height = max(height, y_pos)

            number = number + 1

        width = 4 * (im_width + 10) + 10
        height = (1 + int((number - 1) / 4)) * (im_height + 10) + 10

        canvas.config(scrollregion=(0, 0, width, height))
        root.geometry("%dx%d" % (width + 220, root.winfo_height()))


def show_info():

    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]

        file = os.path.join(cs.cs_dir, 'COPYRIGHT')

        top = tkinter.Toplevel()
        text = tkinter.Text(top)
        text.insert('insert', open(file).read())
        text.pack(expand=tkinter.YES, fill=tkinter.BOTH)

        b_frame = tkinter.Frame(top)
        b_frame.pack(fill=tkinter.X)
        button = tkinter.Button(b_frame, text='Close', command=top.destroy)
        button.pack(side=tkinter.RIGHT)


def show_config():

    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]

        file = os.path.join(cs.cs_dir, 'Config.txt')

        top = tkinter.Toplevel()
        text = tkinter.Text(top)
        text.insert('insert', open(file).read())
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


def select_dir():

    global data_dir

    dialog = filedialog.Directory(root)
    directory = dialog.show()
    if directory:
        data_dir = os.path.normpath(directory)
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

    global list_box, canvas

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

    # if True:
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

    root = tkinter.Tk()
    root = create_widgets()
    read_into_listbox()

    root.mainloop()
