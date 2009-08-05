#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##---------------------------------------------------------------------------##


# imports
import os
import traceback

# PySol imports
from resource import CSI
from settings import TOOLKIT
from mfxutil import Image, ImageTk

# Toolkit imports
from pysoltk import loadImage, copyImage, createImage, shadowImage, createBottom


# ************************************************************************
# * Images
# ************************************************************************


class ImagesCardback:
    def __init__(self, index, name, image, menu_image=None):
        if menu_image is None: menu_image = image
        self.index = index
        self.name = name
        self.image = image
        self.menu_image = menu_image


class Images:
    def __init__(self, dataloader, cs, r=1):
        self.d = dataloader
        self.cs = cs
        self.reduced = r
        if cs is None:
            return
        self.use_pil = False
        if TOOLKIT == 'tk' and Image and Image.VERSION >= '1.1.7':
            self.use_pil = True
        # copy from cardset
        self.CARDW, self.CARDH, self.CARDD = cs.CARDW/r, cs.CARDH/r, cs.CARDD/r
        self.CARD_XOFFSET = cs.CARD_XOFFSET
        self.CARD_YOFFSET = cs.CARD_YOFFSET
        if r > 1:
            self.CARD_XOFFSET = max(10, cs.CARD_XOFFSET)/r
            self.CARD_YOFFSET = max(10, cs.CARD_YOFFSET)/r
        self.SHADOW_XOFFSET, self.SHADOW_YOFFSET = cs.SHADOW_XOFFSET/r, cs.SHADOW_YOFFSET/r
        self.CARD_DX, self.CARD_DY = cs.CARD_DX/r, cs.CARD_DY/r
        # other
        self._shade_index = 0
        self._card = []
        self._back = []
        self._bottom = []
        self._bottom_negative = []
        self._bottom_positive = []
        self._blank_bottom = None
        self._letter = []
        self._letter_negative = []
        self._letter_positive = []
        self._shadow = []
        self._xshadow = []
        self._shade = []
        self._shadow_cards = {}         # key: (suit, rank)
        self._pil_shadow = {}           # key: (width, height)
        self._pil_shadow_image = None

    def destruct(self):
        pass

    def __loadCard(self, filename, check_w=1, check_h=1):
        ##print '__loadCard:', filename
        f = os.path.join(self.cs.dir, filename)
        if not os.path.exists(f):
            return None
        try:
            img = loadImage(file=f)
        except:
            return None
        w, h = img.width(), img.height()
        if self.CARDW < 0:
            self.CARDW, self.CARDH = w, h
        else:
            if ((check_w and w != self.CARDW) or
                (check_h and h != self.CARDH)):
                raise ValueError("Invalid size %dx%d of image %s" % (w, h, f))
        return img

    def __loadBottom(self, filename, check_w=1, check_h=1, color='white'):
        cs_type = CSI.TYPE_ID[self.cs.type]
        imagedir = None
        d = os.path.join('images', 'cards', 'bottoms')
        try:
            imagedir = self.d.findDir(cs_type, d)
        except:
            pass
        if not self.use_pil or imagedir is None:
            # load image
            return self.__loadCard(filename+self.cs.ext, check_w, check_h)
        # create image
        d = os.path.join('images', 'cards', 'bottoms', cs_type)
        try:
            fn = self.d.findImage(filename, d)
        except:
            fn = None
        img = createBottom(self._card[0], color, fn)
        return img

    def __addBack(self, im1, name):
        r = max(self.CARDW / 40.0, self.CARDH / 60.0)
        r = max(2, int(round(r)))
        im2 = im1.subsample(r)
        self._back.append(ImagesCardback(len(self._back), name, im1, im2))

    def _createMissingImages(self):
        # back
        if not self._back:
            im = createImage(self.CARDW, self.CARDH, fill="#a0a0a0", outline="#000000")
            name = ""
            self.__addBack(im, name)
            self.cs.backnames = tuple(self.cs.backnames) + (name,)
        # bottoms / letters
        bottom = None
        neg_bottom = None
        while len(self._bottom_positive) < 7:
            if bottom is None:
                bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#000000")
            self._bottom_positive.append(bottom)
        while len(self._bottom_negative) < 7:
            if neg_bottom is None:
                neg_bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#ffffff")
            self._bottom_negative.append(neg_bottom)
        while len(self._letter_positive) < 4:
            if bottom is None:
                bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#000000")
            self._letter_positive.append(bottom)
        while len(self._letter_negative) < 4:
            if neg_bottom is None:
                neg_bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#ffffff")
            self._letter_negative.append(neg_bottom)
        self._blank_bottom = createImage(self.CARDW, self.CARDH, fill=None, outline=None)

    def load(self, app, progress=None):
        ext = self.cs.ext[1:]
        pstep = 0
        if progress:
            pstep = self.cs.ncards + len(self.cs.backnames) + self.cs.nbottoms + self.cs.nletters
            pstep += self.cs.nshadows + 1 # shadows & shade
            pstep = max(0, (80.0 - progress.percent) / pstep)
        # load face cards
        for n in self.cs.getFaceCardNames():
            self._card.append(self.__loadCard(n + self.cs.ext))
            self._card[-1].filename = n
            if progress: progress.update(step=pstep)
        assert len(self._card) == self.cs.ncards
        # load backgrounds
        for name in self.cs.backnames:
            if name:
                im = self.__loadCard(name)
                self.__addBack(im, name)
        if progress: progress.update(step=1)
        # load bottoms
        for i in range(self.cs.nbottoms):
            name = "bottom%02d" % (i + 1)
            self._bottom_positive.append(self.__loadBottom(name, color='black'))
            if progress: progress.update(step=pstep)
            # load negative bottoms
            name = "bottom%02d-n" % (i + 1)
            self._bottom_negative.append(self.__loadBottom(name, color='white'))
            if progress: progress.update(step=pstep)
        # load letters
        for rank in range(self.cs.nletters):
            name = "l%02d" % (rank + 1)
            self._letter_positive.append(self.__loadBottom(name, color='black'))
            if progress: progress.update(step=pstep)
            # load negative letters
            name = "l%02d-n" % (rank + 1)
            self._letter_negative.append(self.__loadBottom(name, color='white'))
            if progress: progress.update(step=pstep)
        # shadow
        if not self.use_pil:
            for i in range(self.cs.nshadows):
                name = "shadow%02d.%s" % (i, ext)
                im = self.__loadCard(name, check_w=0, check_h=0)
                self._shadow.append(im)
                if i > 0: # skip 0
                    name = "xshadow%02d.%s" % (i, ext)
                    im = self.__loadCard(name, check_w=0, check_h=0)
                    self._xshadow.append(im)
                if progress: progress.update(step=pstep)
        # shade
        if self.use_pil:
            self._shade.append(self._getShadow(self._card[0], None, '#3896f8'))
        else:
            self._shade.append(self.__loadCard("shade." + ext))
        if progress: progress.update(step=pstep)
        # create missing
        self._createMissingImages()
        #
        self._bottom = self._bottom_positive
        self._letter = self._letter_positive
        #
        return 1

    def getFace(self, deck, suit, rank):
        index = suit * len(self.cs.ranks) + rank
        ##print "getFace:", suit, rank, index
        return self._card[index % self.cs.ncards]

    def getBack(self, update=False):
        if update:
            self._shadow_back = None
        index = self.cs.backindex % len(self._back)
        return self._back[index].image

    def getTalonBottom(self):
        return self._bottom[0]

    def getReserveBottom(self):
        return self._bottom[0]

    def getBlankBottom(self):
        return self._blank_bottom

    def getSuitBottom(self, suit=-1):
        assert isinstance(suit, int)
        if suit == -1: return self._bottom[1]   # any suit
        i = 3 + suit
        if i >= len(self._bottom):
            # Trump (for Tarock type games)
            return self._bottom[1]
        return self._bottom[i]

    def getBraidBottom(self):
        return self._bottom[2]

    def getLetter(self, rank):
        assert 0 <= rank <= 3
        if rank >= len(self._letter):
            return self._bottom[0]
        return self._letter[rank]

    def getShadow(self, ncards):
        if ncards >= 0:
            if ncards >= len(self._shadow):
                ##ncards = len(self._shadow) - 1
                return None
            return self._shadow[ncards]
        else:
            ncards = abs(ncards)-2
            if ncards >= len(self._xshadow):
                return None
            return self._xshadow[ncards]

    def getShadowPIL(self, stack, cards):
        x0, y0 = stack.getPositionFor(cards[0])
        x1, y1 = stack.getPositionFor(cards[-1])
        x0, x1 = min(x1, x0), max(x1, x0)
        y0, y1 = min(y1, y0), max(y1, y0)
        x1 += self.CARDW
        y1 += self.CARDH
        w, h = x1-x0, y1-y0
        if (w,h) in self._pil_shadow:
            return self._pil_shadow[(w,h)]
        # create mask
        mask = Image.new('RGBA', (w, h))
        for c in cards:
            x, y = stack.getPositionFor(c)
            x, y = x-x0, y-y0
            im = c._active_image._pil_image
            mask.paste(im, (x, y), im)
        # create shadow
        sh_color = (0x00,0x00,0x00,0x50)
        shadow = Image.new('RGBA', (w, h))
        shadow.paste(sh_color, (0, 0, w, h), mask)
        sx, sy = self.SHADOW_XOFFSET, self.SHADOW_YOFFSET
        mask = mask.crop((sx,sy,w,h))
        tmp = Image.new('RGBA', (w-sx,h-sy))
        shadow.paste(tmp, (0,0), mask)
        #
        shadow = ImageTk.PhotoImage(shadow)
        self._pil_shadow[(w,h)] = shadow
        return shadow

    def getShade(self):
        return self._shade[self._shade_index]

    def _getShadow(self, image, card, color='#3896f8', factor=0.3):
        if self.use_pil:
            # use alpha image; one for each color
            if color in self._shadow_cards:
                shade = self._shadow_cards[color]
            else:
                shade = shadowImage(image, color, factor)
                self._shadow_cards[color] = shade
        else:
            if card in self._shadow_cards:
                shade = self._shadow_cards[card]
            else:
                shade = shadowImage(image, color, factor)
                self._shadow_cards[card] = shade
        if not shade:
            return self.getShade()
        return shade

    def getShadowCard(self, deck, suit, rank):
        image = self.getFace(deck, suit, rank)
        return self._getShadow(image, (suit, rank))

    def getHighlightCard(self, deck, suit, rank):
        image = self.getFace(deck, suit, rank)
        return self._getShadow(image, (suit, rank, 'black'), 'black')

    def getShadowBack(self):
        image = self.getBack()
        return self._getShadow(image, 'back')

    def getCardbacks(self):
        return self._back

    def setNegative(self, flag=0):
        if flag:
            self._bottom = self._bottom_negative
            self._letter = self._letter_negative
        else:
            self._bottom = self._bottom_positive
            self._letter = self._letter_positive


# ************************************************************************
# *
# ************************************************************************

class SubsampledImages(Images):
    def __init__(self, images, r=2):
        Images.__init__(self, None, images.cs, r=r)
        self._card = self._subsample(images._card, r)
        self._bottom_positive = self._subsample(images._bottom_positive, r)
        self._letter_positive = self._subsample(images._letter_positive, r)
        self._bottom_negative = self._subsample(images._bottom_negative, r)
        self._letter_negative = self._subsample(images._letter_negative, r)
        self._bottom = self._bottom_positive
        self._letter = self._letter_positive
        #
        for _back in images._back:
            if _back is None:
                self._back.append(None)
            else:
                im = _back.image.subsample(r)
                self._back.append(ImagesCardback(len(self._back), _back.name, im, im))
        #
        CW, CH = self.CARDW, self.CARDH
        for im in images._shade:
            ##self._shade.append(None)
            self._shade.append(copyImage(im, 0, 0, CW, CH))

    def getShadow(self, ncards):
        return None

    def _subsample(self, l, r):
        s = []
        for im in l:
            if im is None or r == 1:
                s.append(im)
            else:
                s.append(im.subsample(r))
        return s

