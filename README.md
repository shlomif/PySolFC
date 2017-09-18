# PySol Fan Club edition

This is an open source and portable (Windows, Linux and Mac OS X) collection
of Card Solitaire/Patience games written in Python. It is based on
http://pysolfc.sourceforge.net/ .

This is a maintenance branch of PySol FC by [Shlomi
Fish](http://www.shlomifish.org/) and by some other
people, aiming to clean up the code, add features, fix bugs, port to Python
3, and implement other enhancements.

[![Build Status](https://travis-ci.org/shlomif/PySolFC.svg)](https://travis-ci.org/shlomif/PySolFC)

# Screenshots

![Image](<http://i.imgur.com/jQkTGwf.jpg>)

## Requirements.

- Python (2.4 or later) (NB: CPython 2.6.0 has a bug, use 2.6.1 instead)
- Tkinter (Tcl/Tk 8.4 or later)

- For sound support (optional)
  - PySol-Sound-Server: http://www.pysol.org/ (mp3, wav, tracker music)
  or
  - PyGame: http://www.pygame.org/ (mp3, ogg, wav, midi, tracker music)

- Other packages (optional):
  - Tile (ttk): http://tktable.sourceforge.net/tile/ (0.8.0 or later)
  - PIL (Python Imaging Library): http://www.pythonware.com/products/pil
  - Freecell Solver: http://fc-solve.shlomifish.org/ .
  - [Black Hole Solitaire Solver](http://www.shlomifish.org/open-source/projects/black-hole-solitaire-solver/)

## Installation.

See: http://www.python.org/doc/current/inst/

### Running from source without installation.

You can run from the source directory:

$ python pysol.py

After following steps similar to these (on
[Mageia Linux](http://www.mageia.org/) ):

#### Step 1 - install the dependencies

On Mageia you can do:

```
$ sudo urpmi git make pygtk2 pygtk2.0-libglade gnome-python-canvas tkinter
```

On Debian / Ubuntu / etc. you can do:

```
$ sudo apt-get install -y ack-grep cpanminus libperl-dev make perl python-glade2 python-gnome2 python-gnome2-dev python-gtk2 python-setuptools python-tk

```

#### Step 2 - build PySol.

```
$ git clone https://github.com/shlomif/PySolFC.git
$ cd PySolFC
$ sudo urpmi tkinter
$ sudo urpmi pygtk2
$ sudo urpmi pygtk2.0-libglade
$ sudo urpmi gnome-python-canvas
$ gmake test
$ ln -s html-src html
$ ln -s data/images images
$ tar -xvf PySolFC-Cardsets-2.0.tar.bz2 # Need to be downloaded from sourceforge
$ mkdir -p ~/.PySolFC
$ rmdir ~/.PySolFC/cardsets
$ ln -s "`pwd`/PySolFC-Cardsets-2.0" ~/.PySolFC/cardsets
$ python pysol.py
```

<b>Note!</b> If you are using a Debian derivative (e.g: Debian, Ubuntu, or
Linu Mint) and you are getting an error of "No cardsets were found !!! Main
data directory is `[insert dir here]` Please check your PySol installation.",
then you likely installed the cardsets package which has removed some files
that are needed by pysol from source (without the debian modifications).

Please uninstall that package and use the cardsets archive from sourceforge.net
per the instructions above.

### Configuring Freecell Solver

If you want to use the solver, you should configure freecell-solver
( http://fc-solve.shlomifish.org/ ) by passing the following options
to its CMake-based build-system:
`-DMAX_NUM_FREECELLS=8 -DMAX_NUM_STACKS=20 -DMAX_NUM_INITIAL_CARDS_IN_A_STACK=60`.

## Install Extras.

- Music
 - Copy some music files (mp3 for example) to ~/.PySolFC/music/

 - Original PySol music can be downloaded from:
   ftp://ibiblio.org/pub/linux/games/solitaires/pysol-music-4.40.tar.gz

- Cardsets
 - Copy cardsets to ~/.PySolFC/cardsets

 - Additional cardsets can be downloaded from the PySolFC project page:
   http://sourceforge.net/project/showfiles.php?group_id=150718

## Chat

To facilitate coordination about contributing to PySol, please join us for a
real time Internet chat on
the <a href="irc://irc.freenode.net/##pysol">##pysol</a> chat room on
[Freenode](http://freenode.net/) (note the double
octhothorpe/hash-sign/pound-sign) .  We may set up
chat rooms on different services in the future.

In addition, we set up a
[Google Group for discussing open source card games](https://groups.google.com/forum/#!forum/foss-card-games)
which will also be used for discussing PySol. Feel free to subscribe or post!
