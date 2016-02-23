# PySol Fan Club edition



Requirements.
-------------

- Python (2.4 or later) (NB: python 2.6.0 has a bug, use 2.6.1 instead)
- Tkinter (Tcl/Tk 8.4 or later)

** for sound support (optional) **
  - PySol-Sound-Server: http://www.pysol.org/ (mp3, wav, tracker music)
  or
  - PyGame: http://www.pygame.org/ (mp3, ogg, wav, midi, tracker music)

** other packages (optional) **
  - Tile (ttk): http://tktable.sourceforge.net/tile/ (0.8.0 or later)
  - PIL (Python Imaging Library): http://www.pythonware.com/products/pil
  - Freecell Solver: http://fc-solve.berlios.de/


Installation.
-------------

See: http://www.python.org/doc/current/inst/

or just run from the source directory:

$ python pysol.py


** Freecell Solver **
If you want to use Solver, you should configure freecell-solver with following
options:
--enable-max-num-freecells=8
--enable-max-num-stacks=20
--enable-max-num-initial-cards-per-stack=60
(or edit config.h)


Install Extras.
---------------

** Music **
 - Copy some music files (mp3 for example) to ~/.PySolFC/music/ 
 
 - Original PySol music can be download from: 
   ftp://ibiblio.org/pub/linux/games/solitaires/pysol-music-4.40.tar.gz

** Cardsets **
 - Copy cardsets to ~/.PySolFC/cardsets

 - Additional cardsets can be downloaded from the PySolFC project page:
   http://sourceforge.net/project/showfiles.php?group_id=150718


