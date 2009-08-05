#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-
#

import sys, os
from glob import glob
from math import sqrt, sin, cos, pi
from Tkinter import *
try:
    import Image, ImageTk
except ImportError:
    Image = None

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
        self.dir, self.name, self.type, self.ext, self.x, self.y = dir, name, type, ext, x, y

def create_cs_list(ls):
    cardsets_list = {}
    for f in ls:
        dir = os.path.split(f)[0]
        lines = open(f).readlines()
        l0 = lines[0].split(';')
        try:
            ext = l0[2]
        except IndexError:
            ##print f
            ext = '.gif'
        if len(l0) > 3:
            type = cardset_type[l0[3]]
        else:
            #type = 'Unknown'
            type = 'French'
        l1 = lines[1].split(';')
        name = l1[1].strip()
        l2 = lines[2].split()
        x, y = int(l2[0]), int(l2[1])
        cs = Cardset(dir, name, type, ext, x, y)
        cardsets_list[name] = cs
    return cardsets_list

tk_images = []
zoom = 0
def show_cardset(*args):
    global tk_images
    tk_images = []
    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]
        ls = glob(os.path.join(cs.dir, '[0-9][0-9][a-z]'+cs.ext))
        ls += glob(os.path.join(cs.dir, 'back*'+cs.ext))
        if all_imgs:
            ls += glob(os.path.join(cs.dir, 'bottom*'+cs.ext))
            ls += glob(os.path.join(cs.dir, 'l*'+cs.ext))
        #ls = glob(os.path.join(cs.dir, '*.gif'))
        ##if not ls: return
        ls.sort()
        n = 0
        pf = None
        x, y = 10, 10
        width, height = 0, 0
        canvas.delete('all')
        for f in ls:
            if Image:
                filter = {
                    'NEAREST'  : Image.NEAREST,
                    'BILINEAR' : Image.BILINEAR,
                    'BICUBIC'  : Image.BICUBIC,
                    'ANTIALIAS': Image.ANTIALIAS,
                    } [filter_var.get()]
                ##filter = Image.BILINEAR
                ##filter = Image.BICUBIC
                ##filter = Image.ANTIALIAS
                ##print f
                im = Image.open(f)
                if zoom != 0:
                    w, h = im.size
                    im = im.convert('RGBA')        # for save transparency
                    if rotate_var.get():
                        # rotate
                        #if filter == Image.ANTIALIAS:
                        #    filter = Image.BICUBIC
                        z = zoom*5
                        a = abs(pi/2/90*z)
                        neww = int(w*cos(a)+h*sin(a))
                        newh = int(h*cos(a)+w*sin(a))
                        ##print w, h, neww, newh
                        d = int(sqrt(w*w+h*h))
                        dx, dy = (d-w)/2, (d-h)/2
                        newim = Image.new('RGBA', (d, d))
                        newim.paste(im, (dx, dy))
                        im = newim
                        im = im.rotate(z, resample=filter)
                        x0, y0 = (d-neww)/2, (d-newh)/2
                        x1, y1 = d-x0, d-y0
                        im = im.crop((x0, y0, x1, y1))
                        t = str(z)
                    else:
                        # zoom
                        z = 1.0 + zoom/10.0
                        z = max(0.2, z)
                        if 1:
                            tmp = Image.new('RGBA', (w+2, h+2))
                            tmp.paste(im, (1,1), im)
                            im = tmp.resize((int(w*z), int(h*z)), resample=filter)
                        else:
                            im = im.resize((int(w*z), int(h*z)), resample=filter)
                        t = '%d %%' % int(z*100)

                    zoom_label.config(text=t)

                else:
                    zoom_label.config(text='')
                image = ImageTk.PhotoImage(im)
            else:
                image = PhotoImage(file=f)
            tk_images.append(image)
            ff = os.path.split(f)[1]
            if pf is None:
                pf = ff[:2]
                x, y = 10, 10
            elif ff[:2] != pf:
                pf = ff[:2]
                x = 10
                y += image.height()+10
            else:
                x += image.width()+10
            canvas.create_image(x, y, image=image, anchor=NW)
            ##canvas.create_rectangle(x, y, x+image.width(), y+image.height())
            width = max(width, x)
            height = max(height, y)
        width, height = width+image.width()+10, height+image.height()+10
        canvas.config(scrollregion=(0, 0, width, height))
        ##print image.width(), image.height()
        label.config(text='''\
Name: %s
Type: %s
Directory: %s''' % (cs.name, cs.type, cs.dir))

def zoom_in(*args):
    global zoom
    zoom += 1
    show_cardset()

def zoom_out(*args):
    global zoom
    zoom -= 1
    show_cardset()

def zoom_cancel(*args):
    global zoom
    zoom = 0
    show_cardset()

def show_info(*args):
    if list_box.curselection():
        cs_name = list_box.get(list_box.curselection())
        cs = cardsets_dict[cs_name]
        fn = os.path.join(cs.dir, 'COPYRIGHT')
        top = Toplevel()
        text = Text(top)
        text.insert('insert', open(fn).read())
        text.pack(expand=YES, fill=BOTH)
        b_frame = Frame(top)
        b_frame.pack(fill=X)
        button = Button(b_frame, text='Close', command=top.destroy)
        button.pack(side=RIGHT)

def create_widgets():
    global list_box, canvas, label, zoom_label
    #
    root = Tk()
    #
    list_box = Listbox(root, exportselection=False)
    list_box.grid(row=0, column=0, rowspan=2, sticky=NS)
    cardsets_list = list(cardsets_dict)
    cardsets_list.sort()
    for cs in cardsets_list:
        list_box.insert(END, cs)
    list_box.bind('<<ListboxSelect>>', show_cardset)
    #
    sb = Scrollbar(root)
    sb.grid(row=0, column=1, rowspan=2, sticky=NS)
    list_box.config(yscrollcommand=sb.set)
    sb.config(command=list_box.yview)
    #
    canvas = Canvas(root, bg='#5eab6b')
    canvas.grid(row=0, column=2, sticky=NSEW)
    canvas.bind('<4>', lambda e: canvas.yview_scroll(-5, 'unit'))
    canvas.bind('<5>', lambda e: canvas.yview_scroll(5, 'unit'))
    #
    sb = Scrollbar(root)
    sb.grid(row=0, column=3, sticky=NS)
    canvas.config(yscrollcommand=sb.set)
    sb.config(command=canvas.yview)
    #
    if True:
        sb = Scrollbar(root, orient=HORIZONTAL)
        sb.grid(row=1, column=2, sticky=EW)
        canvas.config(xscrollcommand=sb.set)
        sb.config(command=canvas.xview)
    #
    label = Label(root)
    label.grid(row=2, column=0, columnspan=4)
    #
    b_frame = Frame(root)
    b_frame.grid(row=3, column=0, columnspan=4, sticky=EW)
    button = Button(b_frame, text='Quit', command=root.quit, width=8)
    button.pack(side=RIGHT)
    button = Button(b_frame, text='Info', command=show_info, width=8)
    button.pack(side=RIGHT)
    if Image:
        global rotate_var, filter_var
        rotate_var = IntVar(root)
        filter_var = StringVar(root)
        button = Button(b_frame, text='  +  ', command=zoom_in)
        button.pack(side=LEFT)
        button = Button(b_frame, text='  -  ', command=zoom_out)
        button.pack(side=LEFT)
        button = Button(b_frame, text='  =  ', command=zoom_cancel)
        button.pack(side=LEFT)
        button = Checkbutton(b_frame, text='Rotate', indicatoron=0,
                             selectcolor=b_frame['bg'], width=8,
                             variable=rotate_var, command=show_cardset)
        button.pack(side=LEFT, fill='y')
        om = OptionMenu(b_frame, filter_var,
                        'NEAREST', 'BILINEAR', 'BICUBIC', 'ANTIALIAS',
                        command=show_cardset)
        filter_var.set('NEAREST')
        om.pack(side=LEFT, fill='y')

        zoom_label = Label(b_frame)
        zoom_label.pack(side=LEFT)
    #
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)

    root.title('Show Cardsets')

    return root

if __name__ == '__main__':
    if '-a' in sys.argv:
        sys.argv.remove('-a')
        all_imgs = True
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = os.path.normpath(os.path.join(sys.path[0], os.pardir, 'data'))
    ls = glob(os.path.join(data_dir, '*', 'config.txt'))
    cardsets_dict = create_cs_list(ls)
    root = create_widgets()
    root.mainloop()
