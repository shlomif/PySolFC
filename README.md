# PySol Fan Club edition

This is a collection of Card Solitaire/Patience games written in Python.
See http://pysolfc.sourceforge.net/ .

This is a maintenace branch of PySol FC by Shlomi Fish and by some other
people, aiming to clean up the code, add features, fix bugs, port to Python
3, etc.

[![Build Status](https://travis-ci.org/shlomif/PySolFC.svg?branch=shlomif--main-branch--master)](https://travis-ci.org/shlomif/PySolFC)

## Requirements.

- Python (2.4 or later) (NB: python 2.6.0 has a bug, use 2.6.1 instead)
- Tkinter (Tcl/Tk 8.4 or later)

- For sound support (optional)
  - PySol-Sound-Server: http://www.pysol.org/ (mp3, wav, tracker music)
  or
  - PyGame: http://www.pygame.org/ (mp3, ogg, wav, midi, tracker music)

- Other packages (optional):
  - Tile (ttk): http://tktable.sourceforge.net/tile/ (0.8.0 or later)
  - PIL (Python Imaging Library): http://www.pythonware.com/products/pil
  - Freecell Solver: http://fc-solve.shlomifish.org/ .

## Installation.

See: http://www.python.org/doc/current/inst/

### Running from source without installation.

You can run from the source directory:

$ python pysol.py

After following steps similar to this one (on
[Mageia Linux](http://www.mageia.org/) ):

```
$ sudo urpmi git # urpmi is similar to apt-get
$ git clone https://github.com/shlomif/PySolFC.git
$ cd PySolFC
$ git checkout shlomif--main-branch--master
$ sudo urpmi tkinter
$ sudo urpmi pygtk2
$ sudo urpmi pygtk2.0-libglade
$ sudo urpmi gnome-python-canvas
$ gmake test
$ ln -s html-src html
$ tar -xvf PySolFC-Cardsets-2.0.tar.bz2 # Need to be downloaded from sourceforge
$ mkdir -p ~/.PySolFC
$ rmdir ~/.PySolFC/cardsets
$ ln -s ~/.PySolFC/cardsets PySolFC-Cardsets-2.0
$ python pysol.py
```

### Configuring Freecell Solver

If you want to use the Solver, you should configure freecell-solver
( http://fc-solve.shlomifish.org/ ) by passing the following options
to its CMake-based build-system:
-DMAX_NUM_FREECELLS=8
-DMAX_NUM_STACKS=20
-DMAX_NUM_INITIAL_CARDS_IN_A_STACK=60
(or edit config.h)

## Install Extras.

- Music
 - Copy some music files (mp3 for example) to ~/.PySolFC/music/

 - Original PySol music can be download from:
   ftp://ibiblio.org/pub/linux/games/solitaires/pysol-music-4.40.tar.gz

- Cardsets
 - Copy cardsets to ~/.PySolFC/cardsets

 - Additional cardsets can be downloaded from the PySolFC project page:
   http://sourceforge.net/project/showfiles.php?group_id=150718


