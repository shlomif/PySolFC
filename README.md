<p align="center"><img src="html-src/images/high_res/logo_horizontal.png" alt="PySol FC logo" height="180px"></p>

# PySol Fan Club edition

This is an open source and portable (Windows, Linux and Mac OS X) collection
of Card Solitaire/Patience games written in Python. Its homepage is
https://pysolfc.sourceforge.io/.

The maintenance branch of PySol FC on GitHub by [Shlomi
Fish](https://www.shlomifish.org/) and by some other
people, has gained official status, ported the code to Python 3,
and implemented some other enhancements.

- [![CI tests at GitHub](https://github.com/shlomif/PySolFC/actions/workflows/ci.yml/badge.svg)](https://github.com/shlomif/PySolFC/actions/workflows/ci.yml)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/04re7umgl3yuukmh?svg=true)](https://ci.appveyor.com/project/shlomif/pysolfc)

## Call for Contributors

[Shlomi Fish](https://github.com/shlomif), who adopted PySol FC, and maintained
it for several years, has stepped down as its primary maintainer
due to the fact he no longer plays PySol, or other computer card games too
much and that it has been a time sink for him. (Also see
[this Twitter discussion](https://twitter.com/bagder/status/1336793880709238786)
). We are looking for other contributors and there are still
[some large-scale features](https://github.com/shlomif/PySolFC/issues) that
can be implemented.

# Screenshots

![Screenshot of PySol FC](https://i.imgur.com/jQkTGwf.jpg)

## Requirements.

- Python (2.7 or 3.x)
- Tkinter (Tcl/Tk 8.4 or later)

- For sound support (optional)
  - PySol-Sound-Server fork: https://github.com/shlomif/pysol-sound-server (mp3, wav, tracker music)
  - (or: ) PyGame: https://www.pygame.org/ (mp3, ogg, wav, midi, tracker music)

- Other packages (optional):
  - Pillow (Python Imaging Library): https://pillow.readthedocs.io/
  - TTKThemes: https://ttkthemes.readthedocs.io/
  - Freecell Solver: https://fc-solve.shlomifish.org/
  - [Black Hole Solitaire Solver](https://www.shlomifish.org/open-source/projects/black-hole-solitaire-solver/)

## Installation.

We provide an [installer for Windows](https://sourceforge.net/projects/pysolfc/files/PySolFC/)
(requires Windows XP SP3 or higher) as well as an
[Android package on F-droid](https://f-droid.org/packages/org.lufebe16.pysolfc/).

### Running from source without installation.

You can run from the source directory:

```
python pysol.py
```

After following steps similar to these (on
[Mageia Linux](http://www.mageia.org/) ):


#### Step 1 - install the dependencies

On Fedora you can do:

```
sudo dnf builddep PySolFC
```

On Mageia you can do:

```
sudo urpmi git make pygtk2 pygtk2.0-libglade gnome-python-canvas tkinter
```

On Debian / Ubuntu / etc. you can do:

```
sudo apt-get install cpanminus make perl python3-setuptools python3-tk
```

#### Step 2 - build PySol.

You can try running:

```
python3 scripts/linux-install.py
```

```
git clone https://github.com/shlomif/PySolFC.git
cd PySolFC
# Now make sure you have installed the dependencies.
gmake test
gmake rules
ln -s data/images images
tar -xvf PySolFC-Cardsets-2.0.tar.bz2 # Needs to be downloaded from sourceforge
mkdir -p ~/.PySolFC
rmdir ~/.PySolFC/cardsets
ln -s "`pwd`/PySolFC-Cardsets-2.0" ~/.PySolFC/cardsets
python pysol.py
```

<b>Note!</b> If you are using a Debian derivative (e.g: Debian, Ubuntu, or
Linu Mint) and you are getting an error of "No cardsets were found !!! Main
data directory is `[insert dir here]` Please check your PySol installation.",
then you likely installed the cardsets package which has removed some files
that are needed by pysol from source (without the debian modifications).

Please uninstall that package and use the cardsets archive from sourceforge.net
per the instructions above.

### Installing from source and running in a python venv (virtual environment)

At the moment, this only works on POSIX (Linux, FreeBSD and similar) systems.
Windows and Mac users - you'll need to chip in with a script for your system.

#### 1 - Install build prerequisites: six, random2 and pysol-cards

This is kind of stupid and maybe it can be fixed in the future, but for now:

```
pip install six
pip install random2
pip install pysol-cards
```

You may want to use your OS distribution package system instead, for example:

```
sudo apt-get install python-six
sudo apt-get install python-random2
```

For Pillow compilation, libjpeg headers and libraries need to be available:

```
sudo apt-get install libjpeg-dev
```

#### 2 - Clone the source from version control

```
git clone git://github.com/shlomif/PySolFC.git
cd PySolFC
```

#### 3 - Create your virtual environment.

```
PKGTREE=/usr/local/packages/PySolFC # or whatever
export PKGTREE
mkdir -p "$PKGTREE"
( cd "$PKGTREE" && python -m venv ./env )
```

#### 4 - Run the install script

```
./contrib/install-pysolfc.sh
```

#### 5 - Put cardsets into place as above.

#### 6 - Enjoy playing

```
"$PKGTREE"/env/bin/pysol.py
```

## Alternate toolkit.

- Kivy (10.0 or later)

- Features:
  - Sound support integrated.
  - Android apk build support.

- Running from source without installation:

```
python pysol.py --kivy
```

### Configuring Freecell Solver

If you want to use the solver, you should configure freecell-solver
( https://fc-solve.shlomifish.org/ ) by passing the following options
to its CMake-based build-system:
`-DMAX_NUM_FREECELLS=8 -DMAX_NUM_STACKS=20 -DMAX_NUM_INITIAL_CARDS_IN_A_STACK=60`.

## Install Extras.

- Music
 - Copy some music files (in mp3 format for example) to ~/.PySolFC/music/

 - Original PySol music can be downloaded from:
     https://sourceforge.net/projects/pysolfc/files/PySol-Music/

- Cardsets
 - Copy cardsets to ~/.PySolFC/cardsets

 - Additional cardsets can be downloaded from the PySolFC project page:
     https://sourceforge.net/projects/pysolfc/files/

## Related repositories and links

- [PySol-Sound-Server fork](https://github.com/shlomif/pysol-sound-server)
- [Sources for the PySolFC web site](https://github.com/shlomif/pysolfc-website)
- [PySolFC Announcements Drafts](https://github.com/shlomif/pysolfc-announcements)
- [PySolFC-Cardsets tarballs sources repo](https://github.com/shlomif/PySolFC-Cardsets)
- [Extra mahjongg cardsets for PySolFC - originally for flowersol](https://github.com/shlomif/PySol-Extra-Mahjongg-Cardsets)
- [The old "pysol-music" distribution](https://github.com/shlomif/pysol-music)

Related:

- [Freecell Solver](https://github.com/shlomif/fc-solve)
- [Black Hole Solver](https://github.com/shlomif/black-hole-solitaire)

Other open source solitaires:

- [solitaire.gg](https://github.com/KyleU/solitaire.gg) - web-based and written in Scala
- [Solitairey](https://github.com/shlomif/Solitairey/branches) - web-based written in JavaScript
- [KPat](https://games.kde.org/game.php?game=kpat) - desktop-based for KDE.
- [Aisleriot](https://wiki.gnome.org/Apps/Aisleriot) - desktop-based by the GNOME project with relatively limited functionality.

Screencasts:

- [Black Hole solving](https://github.com/shlomif/pysolfc-black-hole-solver--screencast)
- [Freecell solving using the qualified-seed-improved preset](https://bitbucket.org/shlomif/pysolfc-qualified-seed-improved-screencast)

## Chat

To facilitate coordination about contributing to PySol, please join us for a
real time Internet chat on
the <a href="irc://irc.freenode.net/##pysol">##pysol</a> chat room on
[Freenode](http://freenode.net/) (note the double
octothorpe/hash-sign/pound-sign).  We may set up
chat rooms on different services in the future.

In addition, we set up a
[Google Group for discussing open source card games](https://groups.google.com/forum/#!forum/foss-card-games)
which will also be used for discussing PySol. Feel free to subscribe or post!
