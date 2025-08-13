#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
# Load Directory: Look for folders that has cardsets in
# Click onto listbox to show cardset
# Info: gives infos about the sets, if available
# Arrow up/down flip through the sets

import os
import tkinter
import tkinter.filedialog
from glob import glob

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
    '10': 'Matching',
    '11': 'Puzzle',
    '12': 'Ishido'
}

ALL_IMGS = False


class Cardset:
    def __init__(self, cs_dir, cs_name, cs_type, ext, card_w, card_h):
        self.cs_dir = cs_dir
        self.cs_name = cs_name
        self.cs_type = cs_type
        self.ext = ext
        self.card_w = card_w
        self.card_h = card_h


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
                print("\n Error: invalid config.txt in ", cs_dir, "\n")
                name = line_1[0]

            line_2 = lines[2].split()
            card_w, card_h = int(line_2[0]), int(line_2[1])
            card_set = Cardset(cs_dir, name, cs_type, ext, card_w, card_h)
            cardsets_list[name] = card_set
        except RuntimeError:
            fehlermeldung = "Error: invalid config.txt in " + str(cs_dir)
            tkinter.messagebox.showerror(title=None, message=fehlermeldung)
    return cardsets_list


def show_cardset(*args):
    global photolist

    if list_box.curselection():

        cs_name = list_box.get(list_box.curselection())
        card_set = cardsets_dict[cs_name]

        ls = glob(os.path.join(card_set.cs_dir,
                               '[0-9][0-9][a-z]' + card_set.ext))
        ls += glob(os.path.join(card_set.cs_dir,
                                'back*' + card_set.ext))

        if ALL_IMGS:  # dnf because showing bottom cards ist OFF
            ls += glob(os.path.join(card_set.cs_dir, 'bottom*' + card_set.ext))
            ls += glob(os.path.join(card_set.cs_dir, 'l*' + card_set.ext))

        ls.sort()

        canvas.delete("all")

        x_pos, y_pos, number = 0, 0, 0

        photolist = []

        for file in ls:

            image = Image.open(file)
            photo = ImageTk.PhotoImage(image, master=root)
            photolist.append(photo)

            image_width = photo.width()
            image_height = photo.height()

            x_pos = (10 + image_width) * (number % 4) + 10
            y_pos = (10 + image_height) * (int(number / 4)) + 10

            canvas.create_image(x_pos, y_pos, image=photo, anchor='nw')

            number = number + 1

        width = 4 * (image_width + 10) + 10
        height = (1 + int((number - 1) / 4)) * (image_height + 10) + 10

        canvas.config(scrollregion=(0, 0, width, height))
        root.geometry("%dx%d" % (width + 220, root.winfo_height()))


def show_info():
    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        card_set = cardsets_dict[cs_name]

        file_name = os.path.join(card_set.cs_dir, 'COPYRIGHT')

        top = tkinter.Toplevel()
        text = tkinter.Text(top)
        text.insert('insert', open(file_name).read())
        text.pack(expand=tkinter.YES, fill=tkinter.BOTH)

        b_frame = tkinter.Frame(top)
        b_frame.pack(fill=tkinter.X)
        button = tkinter.Button(b_frame, text='Close', command=top.destroy)
        button.pack(side=tkinter.RIGHT)


def show_config():
    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        card_set = cardsets_dict[cs_name]

        file_name = os.path.join(card_set.cs_dir, 'config.txt')

        top = tkinter.Toplevel()
        text = tkinter.Text(top)
        text.insert('insert', open(file_name).read())
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

    dialog = tkinter.filedialog.Directory(root)
    directory = dialog.show()
    if directory:
        data_dir = os.path.normpath(directory)
        read_into_listbox()


def read_into_listbox():
    global cardsets_dict

    ls = glob(os.path.join(data_dir, '*', 'config.txt'))

    if ls:
        cardsets_dict = create_cs_list(ls)

        cardsets_list = sorted(cardsets_dict)

        list_box.delete(0, tkinter.END)

        for card_set in cardsets_list:
            list_box.insert(tkinter.END, card_set)


def create_widgets():
    global list_box, canvas

    list_box = tkinter.Listbox(root, exportselection=False)
    list_box.grid(row=0, column=0, rowspan=2, sticky=tkinter.NS)

    list_box.bind('<<ListboxSelect>>', show_cardset)

    scroll_bar = tkinter.Scrollbar(root)
    scroll_bar.grid(row=0, column=1, rowspan=2, sticky=tkinter.NS)
    list_box.config(yscrollcommand=scroll_bar.set)
    scroll_bar.config(command=list_box.yview)

    # create Canvas
    canvas = tkinter.Canvas(root, width=600, height=600, bg='#5eab6b')
    canvas.grid(row=0, column=2, sticky=tkinter.NSEW)
    canvas.bind('<4>', lambda e: canvas.yview_scroll(-5, 'unit'))
    canvas.bind('<5>', lambda e: canvas.yview_scroll(5, 'unit'))
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    scroll_bar = tkinter.Scrollbar(root)
    scroll_bar.grid(row=0, column=3, sticky=tkinter.NS)
    canvas.config(yscrollcommand=scroll_bar.set)
    scroll_bar.config(command=canvas.yview)

    scroll_bar = tkinter.Scrollbar(root, orient=tkinter.HORIZONTAL)
    scroll_bar.grid(row=1, column=2, sticky=tkinter.EW)
    canvas.config(xscrollcommand=scroll_bar.set)
    scroll_bar.config(command=canvas.xview)

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

    root = tkinter.Tk()
    root = create_widgets()
    read_into_listbox()

    root.mainloop()
