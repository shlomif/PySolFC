## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = ['cardsFaceUp',
           'cardsFaceDown',
           'isRankSequence',
           'isAlternateColorSequence',
           'isSameColorSequence',
           'isSameSuitSequence',
           'isAnySuitButOwnSequence',
           'getNumberOfFreeStacks',
           'getPileFromStacks',
           'Stack',
           'DealRow_StackMethods',
           'DealBaseCard_StackMethods',
           'RedealCards_StackMethods',
           'TalonStack',
           'DealRowTalonStack',
           'InitialDealTalonStack',
           'RedealTalonStack',
           'OpenStack',
           'AbstractFoundationStack',
           'SS_FoundationStack',
           'RK_FoundationStack',
           'AC_FoundationStack',
           'SequenceStack_StackMethods',
           'BasicRowStack',
           'SequenceRowStack',
           'AC_RowStack',
           'SC_RowStack',
           'SS_RowStack',
           'RK_RowStack',
           'BO_RowStack',
           'UD_AC_RowStack',
           'UD_SC_RowStack',
           'UD_SS_RowStack',
           'UD_RK_RowStack',
           'FreeCell_AC_RowStack',
           'FreeCell_SS_RowStack',
           'Spider_AC_RowStack',
           'Spider_SS_RowStack',
           'Yukon_AC_RowStack',
           'Yukon_SS_RowStack',
           'KingAC_RowStack',
           'KingSS_RowStack',
           'KingRK_RowStack',
           'WasteStack',
           'WasteTalonStack',
           'FaceUpWasteTalonStack',
           'OpenTalonStack',
           'ReserveStack',
           'InvisibleStack',
           'StackWrapper',
           'WeakStackWrapper',
           'FullStackWrapper',
           'ArbitraryStack',
           ]

# imports
import time, types

# PySol imports
from mfxutil import Struct, kwdefault, SubclassResponsibility
from util import Timer
from util import ACE, KING, SUITS
from util import ANY_SUIT, ANY_COLOR, ANY_RANK, NO_RANK
from util import NO_REDEAL, UNLIMITED_REDEALS, VARIABLE_REDEALS
from pysoltk import tkname, EVENT_HANDLED, EVENT_PROPAGATE
from pysoltk import CURSOR_DRAG, ANCHOR_NW, ANCHOR_SE
from pysoltk import bind, unbind_destroy
from pysoltk import after, after_idle, after_cancel
from pysoltk import MfxCanvasGroup, MfxCanvasImage, MfxCanvasRectangle, MfxCanvasText
from pysoltk import Card
from pysoltk import getTextWidth


# /***********************************************************************
# // Let's start with some test methods for cards.
# // Empty card-lists return false.
# ************************************************************************/

# check that all cards are face-up
def cardsFaceUp(cards):
    if not cards: return 0
    for c in cards:
        if not c.face_up:
            return 0
    return 1

# check that all cards are face-down
def cardsFaceDown(cards):
    if not cards: return 0
    for c in cards:
        if c.face_up:
            return 0
    return 1

# check that cards are face-up and build down by rank
def isRankSequence(cards, mod=8192, dir=-1):
    if not cardsFaceUp(cards):
        return 0
    c1 = cards[0]
    for c2 in cards[1:]:
        if (c1.rank + dir) % mod != c2.rank:
            return 0
        c1 = c2
    return 1

# check that cards are face-up and build down by alternate color
def isAlternateColorSequence(cards, mod=8192, dir=-1):
    if not cardsFaceUp(cards):
        return 0
    c1 = cards[0]
    for c2 in cards[1:]:
        if (c1.rank + dir) % mod != c2.rank or c1.color == c2.color:
            return 0
        c1 = c2
    return 1

# check that cards are face-up and build down by same color
def isSameColorSequence(cards, mod=8192, dir=-1):
    if not cardsFaceUp(cards):
        return 0
    c1 = cards[0]
    for c2 in cards[1:]:
        if (c1.rank + dir) % mod != c2.rank or c1.color != c2.color:
            return 0
        c1 = c2
    return 1

# check that cards are face-up and build down by same suit
def isSameSuitSequence(cards, mod=8192, dir=-1):
    if not cardsFaceUp(cards):
        return 0
    c1 = cards[0]
    for c2 in cards[1:]:
        if (c1.rank + dir) % mod != c2.rank or c1.suit != c2.suit:
            return 0
        c1 = c2
    return 1

# check that cards are face-up and build down by any suit but own
def isAnySuitButOwnSequence(cards, mod=8192, dir=-1):
    if not cardsFaceUp(cards):
        return 0
    c1 = cards[0]
    for c2 in cards[1:]:
        if (c1.rank + dir) % mod != c2.rank or c1.suit == c2.suit:
            return 0
        c1 = c2
    return 1

def getNumberOfFreeStacks(stacks):
    return len(filter(lambda s: not s.cards, stacks))

# collect the top cards of several stacks into a pile
def getPileFromStacks(stacks, reverse=0):
    cards = []
    for s in stacks:
        if not s.cards or not s.cards[-1].face_up:
            return None
        cards.append(s.cards[-1])
    if reverse:
        cards.reverse()
    return cards


# /***********************************************************************
# //
# ************************************************************************/

class Stack:
    # A generic stack of cards.
    #
    # This is used as a base class for all other stacks (e.g. the talon,
    # the foundations and the row stacks).
    #
    # The default event handlers turn the top card of the stack with
    # its face up on a (single or double) click, and also support
    # moving a subpile around.

    def __init__(self, x, y, game, cap={}):
        # Arguments are the stack's nominal x and y position (the top
        # left corner of the first card placed in the stack), and the
        # game object (which is used to get the canvas; subclasses use
        # the game object to find other stacks).

        #
        # link back to game
        #
        id = len(game.allstacks)
        game.allstacks.append(self)
        x = int(round(x))
        y = int(round(y))
        mapkey = (x, y)
        ###assert not game.stackmap.has_key(mapkey) ## can happen in PyJonngg
        game.stackmap[mapkey] = id

        #
        # setup our pseudo MVC scheme
        #
        model, view, controller = self, self, self

        #
        # model
        #
        model.id = id
        model.game = game
        model.cards = []

        # capabilites - the game logic
        model.cap = Struct(
            suit = -1,          # required suit for this stack (-1 is ANY_SUIT)
            color = -1,         # required color for this stack (-1 is ANY_COLOR)
            rank = -1,          # required rank for this stack (-1 is ANY_RANK)
            base_suit = -1,     # base suit for this stack (-1 is ANY_SUIT)
            base_color = -1,    # base color for this stack (-1 is ANY_COLOR)
            base_rank = -1,     # base rank for this stack (-1 is ANY_RANK)
            dir = 0,            # direction - stack builds up/down
            mod = 8192,         # modulo for wrap around (typically 13 or 8192)
            max_move = 0,       # can move at most # cards at a time
            max_accept = 0,     # can accept at most # cards at a time
            max_cards = 999999, # total number of cards may not exceed this
            # not commonly used:
            min_move = 1,       # must move at least # cards at a time
            min_accept = 1,     # must accept at least # cards at a time
            min_cards = 0,      # total number of cards this stack at least requires
        )
        model.cap.update(cap)
        assert type(model.cap.suit) is types.IntType
        assert type(model.cap.color) is types.IntType
        assert type(model.cap.rank) is types.IntType
        assert type(model.cap.base_suit) is types.IntType
        assert type(model.cap.base_color) is types.IntType
        assert type(model.cap.base_rank) is types.IntType
        #
        # view
        #
        view.x = x
        view.y = y
        view.canvas = game.canvas
        view.CARD_XOFFSET = 0
        view.CARD_YOFFSET = 0
        view.group = MfxCanvasGroup(view.canvas)
        ##view.group.move(view.x, view.y)
        # image items
        view.images = Struct(
            bottom = None,              # canvas item
            redeal = None,              # canvas item
            redeal_img = None,          #   the corresponding PhotoImage
            shade_img = None,
        )
        # other canvas items
        view.items = Struct(
            bottom = None,              # dummy canvas item
            shade_item = None,
        )
        # text items
        view.texts = Struct(
            ncards = None,              # canvas item
            # by default only used by Talon:
            rounds = None,              # canvas item
            redeal = None,              # canvas item
            redeal_str = None,          #   the corresponding string
            # for use by derived stacks:
            misc = None,                # canvas item
        )
        view.top_bottom = None          # the highest of all bottom items
        view.is_visible = view.x >= -100 and view.y >= -100
        view.is_open = -1
        view.can_hide_cards = -1
        view.max_shadow_cards = -1
        #
        view.is_filled = False

    def destruct(self):
        # help breaking circular references
        unbind_destroy(self.group)

    def prepareStack(self):
        self.prepareView()
        if self.is_visible:
            self.initBindings()


    # bindings {view widgets bind to controller}
    def initBindings(self):
        group = self.group
        bind(group, "<1>", self.__clickEventHandler)
        ##bind(group, "<B1-Motion>", self.__motionEventHandler)
        bind(group, "<Motion>", self.__motionEventHandler)
        bind(group, "<ButtonRelease-1>", self.__releaseEventHandler)
        bind(group, "<Control-1>", self.__controlclickEventHandler)
        bind(group, "<Shift-1>", self.__shiftclickEventHandler)
        bind(group, "<Double-1>", self.__doubleclickEventHandler)
        bind(group, "<3>", self.__rightclickEventHandler)
        bind(group, "<2>", self.__middleclickEventHandler)
        bind(group, "<Control-3>", self.__middleclickEventHandler)
        ##bind(group, "<Shift-3>", self.__shiftrightclickEventHandler)
        ##bind(group, "<Double-2>", "")
        bind(group, "<Enter>", self.__enterEventHandler)
        bind(group, "<Leave>", self.__leaveEventHandler)

    def prepareView(self):
        ##assertView(self)
        if (self.CARD_XOFFSET == 0 and self.CARD_YOFFSET == 0):
            assert self.cap.max_move <= 1
        # prepare some variables
        ox, oy = self.CARD_XOFFSET, self.CARD_YOFFSET
        if type(ox) is types.IntType:
            self.CARD_XOFFSET = (ox,)
        else:
            self.CARD_XOFFSET = tuple(map(int, map(round, ox)))
        if type(oy) is types.IntType:
            self.CARD_YOFFSET = (oy,)
        else:
            self.CARD_YOFFSET = tuple(map(int, map(round, oy)))
        if self.can_hide_cards < 0:
            self.can_hide_cards = self.is_visible
            if self.cap.max_cards < 3:
                self.can_hide_cards = 0
            elif filter(None, self.CARD_XOFFSET):
                self.can_hide_cards = 0
            elif filter(None, self.CARD_YOFFSET):
                self.can_hide_cards = 0
            elif self.canvas.preview:
                self.can_hide_cards = 0
        if self.can_hide_cards:
            # compute hide-off direction (see class Card)
            CW, CH = self.game.app.images.CARDW, self.game.app.images.CARDH
            cx = self.x + CW / 2
            cy = self.y + CH / 2
            if cy < 3 * CH / 2:
                self.hide_x, self.hide_y = 0, -10000    # hide at top
            elif cx < 3 * CW / 2:
                self.hide_x, self.hide_y = -10000, 0    # hide at left
            elif cy > self.game.height - 3 * CH / 2:
                self.hide_x, self.hide_y = 0, 10000     # hide at bottom
            else:
                self.hide_x, self.hide_y = 10000, 0     # hide at right
        if self.is_open < 0:
            self.is_open = (self.is_visible and
                            (abs(self.CARD_XOFFSET[0]) >= 5 or
                             abs(self.CARD_YOFFSET[0]) >= 5))
        if self.max_shadow_cards < 0:
            self.max_shadow_cards = 999999
            if abs(self.CARD_YOFFSET[0]) != self.game.app.images.CARD_YOFFSET:
                # don't display a shadow if the YOFFSET of the stack
                # and the images don't match
                self.max_shadow_cards = 1
        # bottom image
        if self.is_visible:
            self.prepareBottom()

    # stack bottom image
    def prepareBottom(self):
        assert self.is_visible and self.images.bottom is None
        img = self.getBottomImage()
        if img is not None:
            self.images.bottom = MfxCanvasImage(self.canvas, self.x, self.y,
                                                image=img, anchor=ANCHOR_NW)
            self.images.bottom.addtag(self.group)
            self.top_bottom = self.images.bottom

    # invisible stack bottom
    # We need this if we want to get any events for an empty stack (which
    # is needed by the quickPlayHandler in some games like Montana)
    def prepareInvisibleBottom(self):
        assert self.is_visible and self.items.bottom is None
        images = self.game.app.images
        self.items.bottom = MfxCanvasRectangle(self.canvas, self.x, self.y,
                                               self.x + images.CARDW,
                                               self.y + images.CARDH,
                                               fill="", outline="", width=0)
        self.items.bottom.addtag(self.group)
        self.top_bottom = self.items.bottom

    # sanity checks
    def assertStack(self):
        assert self.cap.min_move > 0
        assert self.cap.min_accept > 0
        assert not hasattr(self, "suit")


    #
    # Core access methods {model -> view}
    #

    # Add a card add the top of a stack. Also update display. {model -> view}
    def addCard(self, card, unhide=1, update=1):
        model, view = self, self
        model.cards.append(card)
        card.tkraise(unhide=unhide)
        if view.can_hide_cards and len(model.cards) >= 3:
            # we only need to display the 2 top cards
            model.cards[-3].hide(self)
        card.item.addtag(view.group)
        view._position(card)
        if update:
            view.updateText()
        if not self.game.moves.state == self.game.S_REDO:
            self.closeStackMove()
        return card

    def insertCard(self, card, positon, unhide=1, update=1):
        model, view = self, self
        model.cards.insert(positon, card)
        for c in model.cards[positon:]:
            c.tkraise(unhide=unhide)
        if view.can_hide_cards and len(model.cards) >= 3 and len(model.cards)-positon <= 2:
            # we only need to display the 2 top cards
            model.cards[-3].hide(self)
        card.item.addtag(view.group)
        for c in model.cards[positon:]:
            view._position(c)
        if update:
            view.updateText()
        if not self.game.moves.state == self.game.S_REDO:
            self.closeStackMove()
        return card

    # Remove a card from the stack. Also update display. {model -> view}
    def removeCard(self, card=None, unhide=1, update=1, update_positions=0):
        model, view = self, self
        assert len(model.cards) > 0
        if card is None:
            card = model.cards[-1]
            # optimized a little bit (compare with the else below)
            card.item.dtag(view.group)
            if unhide and self.can_hide_cards:
                card.unhide()
                if len(self.cards) >= 3:
                    model.cards[-3].unhide()
            del model.cards[-1]
        else:
            card.item.dtag(view.group)
            if unhide and view.can_hide_cards:
                # Note: the 2 top cards ([-1] and [-2]) are already unhidden.
                card.unhide()
                if len(model.cards) >= 3:
                    if card is model.cards[-1] or model is self.cards[-2]:
                        # Make sure that 2 top cards will be un-hidden.
                        model.cards[-3].unhide()
            card_index = model.cards.index(card)
            model.cards.remove(card)
            if update_positions:
                for c in model.cards[card_index:]:
                    view._position(c)
        if update:
            view.updateText()
        if self.is_filled:
            self._unshadeStack()
            self.is_filled = False
        return card

    # Get the top card {model}
    def getCard(self):
        if self.cards:
            return self.cards[-1]
        return None

    # get the largest moveable pile {model} - uses canMoveCards()
    def getPile(self):
        if self.cap.max_move > 0:
            cards = self.cards[-self.cap.max_move:]
            while len(cards) >= self.cap.min_move:
                if self.canMoveCards(cards):
                    return cards
                del cards[0]
        return None

    # Position the card on the canvas {view}
    def _position(self, card):
        x, y = self.getPositionFor(card)
        card.moveTo(x, y)

    # find card
    def _findCard(self, event):
        model, view = self, self
        if event is not None and model.cards:
            # ask the canvas
            return view.canvas.findCard(self, event)
        return -1

    # find card
    def _findCardXY(self, x, y, cards=None):
        model, view = self, self
        if cards is None: cards = model.cards
        images = self.game.app.images
        index = -1
        for i in range(len(cards)):
            c = cards[i]
            r = (c.x, c.y, c.x + images.CARDW, c.y + images.CARDH)
            if x >= r[0] and x < r[2] and y >= r[1] and y < r[3]:
                index = i
        return index

    # generic model update (can be used for undo/redo - see move.py)
    def updateModel(self, undo, flags):
        pass

    # copy model data - see Hint.AClonedStack
    def copyModel(self, clone):
        clone.id = self.id
        clone.game = self.game
        clone.cap = self.cap

    def getRankDir(self, cards=None):
        if cards is None:
            cards = self.cards[-2:]
        if len(cards) < 2:
            return 0
        dir = (cards[-1].rank - cards[-2].rank) % self.cap.mod
        if dir > self.cap.mod / 2:
            return dir - self.cap.mod
        return dir


    #
    # Basic capabilities {model}
    # Used by various subclasses.
    #

    def basicIsBlocked(self):
        # Check if the stack is blocked (e.g. Pyramid or Mahjongg)
        return 0

    def basicAcceptsCards(self, from_stack, cards):
        # Check that the limits are ok and that the cards are face up
        if from_stack is self or self.basicIsBlocked():
            return 0
        cap = self.cap
        l = len(cards)
        if l < cap.min_accept or l > cap.max_accept:
            return 0
        l = l + len(self.cards)
        if l > cap.max_cards:       # note: we don't check cap.min_cards here
            return 0
        for c in cards:
            if not c.face_up:
                return 0
            if cap.suit >= 0 and c.suit != cap.suit:
                return 0
            if cap.color >= 0 and c.color != cap.color:
                return 0
            if cap.rank >= 0 and c.rank != cap.rank:
                return 0
        if self.cards:
            # top card of our stack must be face up
            return self.cards[-1].face_up
        else:
            # check required base
            c = cards[0]
            if cap.base_suit >= 0 and c.suit != cap.base_suit:
                return 0
            if cap.base_color >= 0 and c.color != cap.base_color:
                return 0
            if cap.base_rank >= 0 and c.rank != cap.base_rank:
                return 0
            return 1

    def basicCanMoveCards(self, cards):
        # Check that the limits are ok and the cards are face up
        if self.basicIsBlocked():
            return 0
        cap = self.cap
        l = len(cards)
        if l < cap.min_move or l > cap.max_move:
            return 0
        l = len(self.cards) - l
        if l < cap.min_cards:       # note: we don't check cap.max_cards here
            return 0
        return cardsFaceUp(cards)


    #
    # Capabilities - important for game logic {model}
    #

    def acceptsCards(self, from_stack, cards):
        # Do we accept receiving `cards' from `from_stack' ?
        return 0

    def canMoveCards(self, cards):
        # Can we move these cards when assuming they are our top-cards ?
        return 0

    def canFlipCard(self):
        # Can we flip our top card ?
        return 0

    def canDropCards(self, stacks):
        # Can we drop the top cards onto one of the foundation stacks ?
        return (None, 0)    # return the stack and the number of cards


    #
    # State {model}
    #

    def resetGame(self):
        # Called when starting a new game.
        pass

    def __repr__(self):
        # Return a string for debug print statements.
        return "%s(%d)" % (self.__class__.__name__, self.id)


    #
    # Atomic move actions {model -> view}
    #

    def flipMove(self):
        # Flip the top card.
        self.game.flipMove(self)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        # Move the top n cards.
        self.game.moveMove(ncards, self, to_stack, frames=frames, shadow=shadow)
        self.fillStack()

    def fillStack(self):
        self.game.fillStack(self)

    def closeStackMove(self):
        pass

    #
    # Playing move actions. Better not override.
    #

    def playFlipMove(self, sound=1):
        if sound:
            self.game.playSample("flip", 5)
        self.flipMove()
        if not self.game.checkForWin():
            self.game.autoPlay()
        self.game.finishMove()

    def playMoveMove(self, ncards, to_stack, frames=-1, shadow=-1, sound=1):
        if sound:
            if to_stack in self.game.s.foundations:
                self.game.playSample("drop", priority=30)
            else:
                self.game.playSample("move", priority=10)
        self.moveMove(ncards, to_stack, frames=frames, shadow=shadow)
        if not self.game.checkForWin():
            # let the player put cards back from the foundations
            if not self in self.game.s.foundations:
                self.game.autoPlay()
        self.game.finishMove()


    #
    # Appearance {view}
    #

    def getBottomImage(self):
        return None

    def getPositionFor(self, card):
        model, view = self, self
        if view.can_hide_cards:
            return view.x, view.y
        x, y = view.x, view.y
        ix, iy, lx, ly = 0, 0, len(view.CARD_XOFFSET), len(view.CARD_YOFFSET)
        for c in model.cards:
            if c is card:
                break
            x = x + view.CARD_XOFFSET[ix]
            y = y + view.CARD_YOFFSET[iy]
            ix = (ix + 1) % lx
            iy = (iy + 1) % ly
        return (x, y)

    def getOffsetFor(self, card):
        model, view = self, self
        if view.can_hide_cards:
            return 0, 0
        lx, ly = len(view.CARD_XOFFSET), len(view.CARD_YOFFSET)
        i = list(model.cards).index(card)
        return view.CARD_XOFFSET[i%lx], view.CARD_YOFFSET[i%ly]

    # Fully update the view of a stack - updates
    # hiding, card positions and stacking order.
    # Avoid calling this as it is rather slow.
    def refreshView(self):
        model, view = self, self
        cards = model.cards
        if not view.is_visible or len(cards) < 2:
            return
        if view.can_hide_cards:
            # hide all lower cards
            for c in cards[:-2]:
                ##print "refresh hide", c, c.hide_stack
                c.hide(self)
            # unhide the 2 top cards
            for c in cards[-2:]:
                ##print "refresh unhide 1", c, c.hide_stack
                c.unhide()
                ##print "refresh unhide 1", c, c.hide_stack, c.hide_x, c.hide_y
        # update the card postions and stacking order
        item = cards[0].item
        x, y = view.x, view.y
        ix, iy, lx, ly = 0, 0, len(view.CARD_XOFFSET), len(view.CARD_YOFFSET)
        for c in cards[1:]:
            c.item.tkraise(item)
            item = c.item
            if not view.can_hide_cards:
                x = x + view.CARD_XOFFSET[ix]
                y = y + view.CARD_YOFFSET[iy]
                ix = (ix + 1) % lx
                iy = (iy + 1) % ly
                c.moveTo(x, y)

    def updateText(self):
        if self.game.preview > 1 or self.texts.ncards is None:
            return
        t = ""
        format = "%d"
        if self.texts.ncards.text_format is not None:
            format = self.texts.ncards.text_format
            if format == "%D":
                format = ""
                if self.cards:
                    format = "%d"
        if format:
            t = format % len(self.cards)
        if 0 and self.game.app.debug:
            visible = 0
            for c in self.cards:
                if c.isHidden():
                    assert c.hide_stack is not None
                    assert c.hide_x != 0 or c.hide_y != 0
                else:
                    visible = visible + 1
                    assert c.hide_stack is None
                    assert c.hide_x == 0 and c.hide_y == 0
            t  = t + " %2d" % visible
        self.texts.ncards.config(text=t)

    def basicShallHighlightSameRank(self, card):
        # by default all open stacks are available for highlighting
        assert card in self.cards
        if not self.is_visible or not card.face_up:
            return False
        if card is self.cards[-1]:
            return True
        if not self.is_open:
            return False
        dx, dy = self.getOffsetFor(card)
        if dx == 0 and dy <= 4:
            return False
        if dx <= 4 and dy == 0:
            return False
        return True

    def basicShallHighlightMatch(self, card):
        # by default all open stacks are available for highlighting
        return self.basicShallHighlightSameRank(card)

    def highlightSameRank(self, event):
        i = self._findCard(event)
        if i < 0:
            return 0
        card = self.cards[i]
        if not self.basicShallHighlightSameRank(card):
            return 0
        col = self.game.app.opt.highlight_samerank_colors
        info = [ (self, card, card, col[1]) ]
        for s in self.game.allstacks:
            for c in s.cards:
                if c is card: continue
                # check the rank
                if c.rank != card.rank: continue
                # ask the target stack
                if s.basicShallHighlightSameRank(c):
                    info.append((s, c, c, col[3]))
        self.game.stats.highlight_samerank = self.game.stats.highlight_samerank + 1
        return self.game._highlightCards(info, self.game.app.opt.highlight_samerank_sleep)

    def highlightMatchingCards(self, event):
        i = self._findCard(event)
        if i < 0:
            return 0
        card = self.cards[i]
        if not self.basicShallHighlightMatch(card):
            return 0
        col = self.game.app.opt.highlight_cards_colors
        c1 = c2 = card
        info = []
        found = 0
        for s in self.game.allstacks:
            # continue if both stacks are foundations
            if self in self.game.s.foundations and s in self.game.s.foundations:
                continue
            # for all cards
            for c in s.cards:
                if c is card: continue
                # ask the target stack
                if not s.basicShallHighlightMatch(c):
                    continue
                # ask the game
                if self.game.shallHighlightMatch(self, card, s, c):
                    found = 1
                    if s is self:
                        # enlarge rectangle for neighbours
                        j = self.cards.index(c)
                        if i - 1 == j: c1 = c; continue
                        if i + 1 == j: c2 = c; continue
                    info.append((s, c, c, col[3]))
        if found:
            if info:
                self.game.stats.highlight_cards = self.game.stats.highlight_cards + 1
            info.append((self, c1, c2, col[1]))
            return self.game._highlightCards(info, self.game.app.opt.highlight_cards_sleep)
        if not self.basicIsBlocked():
            self.game.highlightNotMatching()
        return 0


    #
    # Subclass overridable handlers {contoller -> model -> view}
    #

    def clickHandler(self, event):
        return 0

    def middleclickHandler(self, event):
        # default action: show the card if it is overlapped by other cards
        if not self.is_open:
            return 0
        i = self._findCard(event)
        positions = len(self.cards) - i - 1
        if i < 0 or positions <= 0 or not self.cards[i].face_up:
            return 0
        ##print self.cards[i]
        self.cards[i].item.tkraise()
        self.game.canvas.update_idletasks()
        self.game.sleep(self.game.app.opt.raise_card_sleep)
        self.cards[i].item.lower(self.cards[i+1].item)
        self.game.canvas.update_idletasks()
        return 1

    def rightclickHandler(self, event):
        return 0

    def doubleclickHandler(self, event):
        return self.clickHandler(event)

    def controlclickHandler(self, event):
        return 0

    def shiftclickHandler(self, event):
        # default action: highlight all cards of the same rank
        if self.game.app.opt.highlight_samerank:
            return self.highlightSameRank(event)
        return 0

    def shiftrightclickHandler(self, event):
        return 0

    def releaseHandler(self, event, drag, sound=1):
        # default action: move cards back to their origin position
        if drag.cards:
            if sound:
                self.game.playSample("nomove")
            self.moveCardsBackHandler(event, drag)

    def moveCardsBackHandler(self, event, drag):
        for card in drag.cards:
            self._position(card)


    #
    # Event handlers {controller}
    #

    def __defaultClickEventHandler(self, event, handler, start_drag=0, cancel_drag=1):
        self.game.event_handled = True # for Game.undoHandler
        if self.game.demo:
            self.game.stopDemo(event)
        self.game.interruptSleep()
        if self.game.busy: return EVENT_HANDLED
        if self.game.drag.stack and cancel_drag:
            self.game.drag.stack.cancelDrag(event) # in case we lost an event
        if start_drag:
            # this handler may start a drag operation
            r = handler(event)
            if r <= 0:
                sound = r == 0
                self.startDrag(event, sound=sound)
        else:
            handler(event)
        return EVENT_HANDLED

    def __clickEventHandler(self, event):
        if self.game.app.opt.sticky_mouse:
            cancel_drag = 0
            start_drag = not self.game.drag.stack
            if start_drag:
                handler = self.clickHandler
            else:
                handler = self.finishDrag
        else:
            cancel_drag = 1
            start_drag = 1
            handler = self.clickHandler
        return self.__defaultClickEventHandler(event, handler, start_drag, cancel_drag)

    def __doubleclickEventHandler(self, event):
        return self.__defaultClickEventHandler(event, self.doubleclickHandler)

    def __middleclickEventHandler(self, event):
        return self.__defaultClickEventHandler(event, self.middleclickHandler)

    def __rightclickEventHandler(self, event):
        return self.__defaultClickEventHandler(event, self.rightclickHandler)

    def __controlclickEventHandler(self, event):
        return self.__defaultClickEventHandler(event, self.controlclickHandler)

    def __shiftclickEventHandler(self, event):
        return self.__defaultClickEventHandler(event, self.shiftclickHandler)

    def __shiftrightclickEventHandler(self, event):
        return self.__defaultClickEventHandler(event, self.shiftrightclickHandler)

    def __motionEventHandler(self, event):
        if not self.game.drag.stack or not self is self.game.drag.stack:
            return EVENT_PROPAGATE
        if self.game.demo:
            self.game.stopDemo(event)
        if self.game.busy: return EVENT_HANDLED
        if not self.game.app.opt.sticky_mouse: # 1:
            # use a timer to update the drag
            # this allows us to skip redraws on slow machines
            drag = self.game.drag
            if drag.timer is None:
                drag.timer = after_idle(self.canvas, self.keepDragTimer)
            drag.event = event
        else:
            # update now
            self.keepDrag(event)
        return EVENT_HANDLED

    def __releaseEventHandler(self, event):
        if self.game.demo:
            self.game.stopDemo(event)
        self.game.interruptSleep()
        if self.game.busy: return EVENT_HANDLED
        if not self.game.app.opt.sticky_mouse:
            self.keepDrag(event)
            self.finishDrag(event)
        return EVENT_HANDLED

    def __enterEventHandler(self, event):
        if not self.game.drag.stack:
            after_idle(self.canvas, self.game.showHelp,
                       'help', self.getHelp(), ##+' '+self.getBaseCard(),
                       'info', self.getNumCards())
        return EVENT_HANDLED

    def __leaveEventHandler(self, event):
        if not self.game.drag.stack:
            after_idle(self.canvas, self.game.showHelp)
        if not self.game.app.opt.sticky_mouse:
            return EVENT_HANDLED
        drag_stack = self.game.drag.stack
        if self is drag_stack:
            x, y = event.x, event.y
            w, h = self.game.canvas.winfo_width(), self.game.canvas.winfo_height()
            if x < 0 or y < 0 or x >= w or y >= h:
                # cancel drag if mouse leave canvas
                drag_stack.cancelDrag(event)
                after_idle(self.canvas, self.game.showHelp)
                return EVENT_HANDLED
            else:
                # continue drag
                return self.__motionEventHandler(event)
        else:
            return EVENT_PROPAGATE


    #
    # Drag internals {controller -> model -> view}
    #

    def getDragCards(self, index):
        return self.cards[index:]

    # begin a drag operation
    def startDrag(self, event, sound=1):
        #print event.x, event.y
        assert self.game.drag.stack is None
        i = self._findCard(event)
        if i < 0 or not self.canMoveCards(self.cards[i:]):
            return
        if self.is_filled:
            self.items.shade_item.config(state='hidden')
        x_offset, y_offset = self.cards[i].x, self.cards[i].y
        if sound:
            self.game.playSample("startdrag")
        self.lastx = event.x
        self.lasty = event.y
        game = self.game
        drag = game.drag
        drag.start_x = event.x
        drag.start_y = event.y
        drag.stack = self
        drag.noshade_stacks = [ self ]
        drag.cards = self.getDragCards(i)
        drag.index = i
        images = game.app.images
        drag.shadows = self.createShadows(drag.cards)
        ##sx, sy = 0, 0
        sx, sy = -images.SHADOW_XOFFSET, -images.SHADOW_YOFFSET
        dx, dy = 0, 0
        if game.app.opt.sticky_mouse:
            # return cards under mouse
            dx = event.x - (x_offset+images.CARDW+sx) - game.canvas.xmargin
            dy = event.y - (y_offset+images.CARDH+sy) - game.canvas.ymargin
            if dx < 0: dx = 0
            if dy < 0: dy = 0
        for s in drag.shadows:
            if dx > 0 or dy > 0:
                s.move(dx, dy)
            s.tkraise()
        for card in drag.cards:
            card.tkraise()
            card.moveBy(sx+dx, sy+dy)
        if game.app.opt.dragcursor:
            game.canvas.config(cursor=CURSOR_DRAG)

    # continue a drag operation
    def keepDrag(self, event):
        drag = self.game.drag
        if not drag.cards:
            return
        assert self is drag.stack
        dx = event.x - self.lastx
        dy = event.y - self.lasty
        if dx or dy:
            self.lastx = event.x
            self.lasty = event.y
            if self.game.app.opt.shade:
                self._updateShade()
            for s in drag.shadows:
                s.move(dx, dy)
            for card in drag.cards:
                card.moveBy(dx, dy)
        drag.event = None

    def keepDragTimer(self):
        drag = self.game.drag
        after_cancel(drag.timer)
        drag.timer = None
        if drag.event:
            self.keepDrag(drag.event)
            self.canvas.update_idletasks()

    # create shadows, return a tuple of MfxCanvasImages
    def createShadows(self, cards, dx=0, dy=0):
        if not self.game.app.opt.shadow or self.canvas.preview > 1:
            return ()
        l = len(cards)
        if l == 0 or l > self.max_shadow_cards:
            return ()
        images = self.game.app.images
        cx, cy = cards[0].x, cards[0].y
        for c in cards[1:]:
            if c.x != cx or abs(c.y - cy) != images.CARD_YOFFSET:
                return ()
            cy = c.y
        img0, img1 = images.getShadow(0), images.getShadow(l)
##         if 0:
##             # Dynamically compute the shadow. Doesn't work because
##             # PhotoImage.copy() doesn't preserve transparency.
##             img1 = images.getShadow(13)
##             if img1:
##                 h = images.CARDH - img0.height()
##                 h = h + (l - 1) * self.CARD_YOFFSET[0]
##                 if h < img1.height():
##                     if hasattr(img1, '_pil_image'): # use PIL
##                         import ImageTk
##                         im = img1._pil_image.crop((0,0,img1.width(),h))
##                         img1 = ImageTk.PhotoImage(im)
##                     else:
##                         import Tkinter
##                         dest = Tkinter.PhotoImage(width=img1.width(), height=h)
##                         dest.blank()
##                         img1.tk.call(dest, "copy", img1.name, "-from", 0, 0, img1.width(), h)
##                         assert dest.height() == h and dest.width() == img1.width()
##                         #print h, img1.height(), dest.height()
##                         img1 = dest
##                     self._foo = img1 # keep a reference
##                 elif h > img1.height():
##                     img1 = None
        if img0 and img1:
            c = cards[-1]
            if self.CARD_YOFFSET[0] < 0: c = cards[0]
            cx, cy = c.x + images.CARDW + dx, c.y + images.CARDH + dy
            s1 = MfxCanvasImage(self.game.canvas, cx, cy - img0.height(),
                                image=img1, anchor=ANCHOR_SE)
            s2 = MfxCanvasImage(self.game.canvas, cx, cy,
                                image=img0, anchor=ANCHOR_SE)
            s1.lower(c.item)
            s2.lower(c.item)
            return (s1, s2)
        return ()

    # handle shade within a drag operation
    def _deleteShade(self):
        if self.game.drag.shade_img:
            self.game.drag.shade_img.delete()
        self.game.drag.shade_img = None
        self.game.drag.shade_stack = None

    def _updateShade(self):
        # optimized for speed - we use lots of local variables
        game = self.game
        images = game.app.images
        if not self.images.shade_img:
            img = images.getShade()
            self.images.shade_img = img
        else:
            img = self.images.shade_img
        if img is None:
            return
        CW, CH = images.CARDW, images.CARDH
        drag = game.drag
        ##stacks = game.allstacks
        c = drag.cards[0]
        stacks = ( game.getClosestStack(c, drag.stack), )
        r1_0, r1_1, r1_2, r1_3 = c.x, c.y, c.x + CW, c.y + CH
        sstack, sdiff, sx, sy = None, 999999999, 0, 0
        for s in stacks:
            if s is None or s in drag.noshade_stacks:
                continue
            if s.cards:
                c = s.cards[-1]
                r2 = (c.x, c.y, c.x + CW, c.y + CH)
            else:
                r2 = (s.x, s.y, s.x + CW, s.y + CH)
            if r1_2 <= r2[0] or r1_3 <= r2[1] or r2[2] <= r1_0 or r2[3] <= r1_1:
                # rectangles do not intersect
                continue
            if s in drag.canshade_stacks:
                pass
            elif s.acceptsCards(drag.stack, drag.cards):
                drag.canshade_stacks.append(s)
            else:
                drag.noshade_stacks.append(s)
                continue
            diff = (r1_0 - r2[0])**2 + (r1_1 - r2[1])**2
            if diff < sdiff:
                sstack, sdiff, sx, sy = s, diff, r2[0], r2[1]
        if sstack is drag.shade_stack:
            return
        if sstack is None:
            self._deleteShade()
            return
        # move or create the shade image
        drag.shade_stack = sstack
        if drag.shade_img:
            drag.shade_img.moveTo(sx, sy)
        else:
            img = MfxCanvasImage(game.canvas, sx, sy, image=img, anchor=ANCHOR_NW)
            drag.shade_img = img
            # raise/lower the shade image to the correct stacking order
            if drag.shadows:
                img.lower(drag.shadows[0])
            else:
                img.lower(drag.cards[0].item)

    # for closeStackMove
    def _shadeStack(self):
        if not self.game.app.opt.shade_filled_stacks:
            return
        if not self.images.shade_img:
            img = self.game.app.images.getShade()
            self.images.shade_img = img
        else:
            img = self.images.shade_img
        if img is None:
            return
        if not self.items.shade_item:
            self.game.canvas.update_idletasks()
            card = self.cards[-1]
            item = MfxCanvasImage(self.game.canvas, card.x, card.y,
                                  image=img, anchor=ANCHOR_NW)
            ##item.tkraise()
            item.addtag(self.group)
            self.items.shade_item = item

    def _unshadeStack(self):
        if self.items.shade_item:
            self.items.shade_item.delete()
            self.items.shade_item = None

    def _stopDrag(self):
        drag = self.game.drag
        after_cancel(drag.timer)
        drag.timer = None
        self._deleteShade()
        drag.canshade_stacks = []
        drag.noshade_stacks = []
        for s in drag.shadows:
            s.delete()
        drag.shadows = []
        drag.stack = None
        drag.cards = []
        if self.is_filled:
            self.items.shade_item.config(state='normal')
            self.items.shade_item.tkraise()

    # finish a drag operation
    def finishDrag(self, event=None):
        if self.game.app.opt.dragcursor:
            self.game.canvas.config(cursor=self.game.app.top_cursor)
        drag = self.game.drag.copy()
        self._stopDrag()
        if drag.cards:
            assert drag.stack is self
            self.releaseHandler(event, drag)

    # cancel a drag operation
    def cancelDrag(self, event=None):
        if self.game.app.opt.dragcursor:
            self.game.canvas.config(cursor=self.game.app.top_cursor)
        drag = self.game.drag.copy()
        self._stopDrag()
        if drag.cards:
            assert drag.stack is self
            self.moveCardsBackHandler(event, drag)

    def getHelp(self):
        return str(self) # debug

    def getBaseCard(self):
        return ''

    def _getBaseCard(self):
        if self.cap.max_accept == 0:
            return ''
        br = self.cap.base_rank
        s = _('Base card - %s.')
        if br == NO_RANK: s = _('Empty row cannot be filled.')
        elif br == -1: s = s % _('any card')
        elif br == 10: s = s % _('Jack')
        elif br == 11: s = s % _('Queen')
        elif br == 12: s = s % _('King')
        elif br == 0 : s = s % _('Ace')
        else         : s = s % str(br+1)
        return s

    def getNumCards(self):
        if self.game.app.debug >= 5:
            t = repr(self)+' '
        else:
            t = ''
        n = len(self.cards)
        if   n == 0 : return t+_('No cards')
        elif n == 1 : return t+_('1 card')
        else        : return t+str(n)+_(' cards')


# /***********************************************************************
# // Abstract interface that supports a concept of dealing.
# ************************************************************************/

class DealRow_StackMethods:
    # Deal a card to each of the RowStacks. Return number of cards dealt.
    def dealRow(self, rows=None, flip=1, reverse=0, frames=-1, sound=0):
        if rows is None: rows = self.game.s.rows
        if sound and frames and self.game.app.opt.animations:
            self.game.startDealSample()
        n = self.dealToStacks(rows, flip, reverse, frames)
        if sound:
            self.game.stopSamples()
        return n

    # Same, but no error if not enough cards are available.
    def dealRowAvail(self, rows=None, flip=1, reverse=0, frames=-1, sound=0):
        if rows is None: rows = self.game.s.rows
        if sound and frames and self.game.app.opt.animations:
            self.game.startDealSample()
        if len(self.cards) < len(rows):
            rows = rows[:len(self.cards)]
        n = self.dealToStacks(rows, flip, reverse, frames)
        if sound:
            self.game.stopSamples()
        return n

    def dealToStacks(self, stacks, flip=1, reverse=0, frames=-1):
        if not self.cards or not stacks:
            return 0
        assert len(self.cards) >= len(stacks)
        old_state = self.game.enterState(self.game.S_DEAL)
        if reverse:
            stacks = list(stacks)
            stacks.reverse()
        for r in stacks:
            assert not self.getCard().face_up
            assert r is not self
            if frames == 0 and self.game.moves.state == self.game.S_INIT:
                # optimized a little bit for initial dealing
                c = self.removeCard(update=0)
                r.addCard(c, update=0)
                # doing the flip after the move seems to be a little faster
                if flip:
                    c.showFace()
            else:
                if flip:
                    self.game.flipMove(self)
                self.game.moveMove(1, self, r, frames=frames)
        self.game.leaveState(old_state)
        return len(stacks)

    # all Aces go to the Foundations
    def dealToStacksOrFoundations(self, stacks, flip=1, reverse=0, frames=-1, rank=-1):
        if rank < 0:
            rank = self.game.s.foundations[0].cap.base_rank
        if not self.cards or not stacks:
            return 0
        old_state = self.game.enterState(self.game.S_DEAL)
        if reverse:
            stacks = list(stacks)
            stacks.reverse()
        n = 0
        for r in stacks:
            assert r is not self
            while self.cards:
                n = n + 1
                if flip:
                    self.game.flipMove(self)
                if flip and self.cards[-1].rank == rank:
                    for s in self.game.s.foundations:
                        assert s is not self
                        if s.acceptsCards(self, self.cards[-1:]):
                            self.game.moveMove(1, self, s, frames=frames)
                            break
                else:
                    self.game.moveMove(1, self, r, frames=frames)
                    break
        self.game.leaveState(old_state)
        return n


class DealBaseCard_StackMethods:
    def dealSingleBaseCard(self, frames=-1, update_saveinfo=1):
        c = self.cards[-1]
        self.dealBaseCards(ncards=1, frames=frames, update_saveinfo=0)
        for s in self.game.s.foundations:
            s.cap.base_rank = c.rank
            if update_saveinfo:
                cap = Struct(base_rank=c.rank)
                self.game.saveinfo.stack_caps.append((s.id, cap))
        return c

    def dealBaseCards(self, ncards=1, frames=-1, update_saveinfo=1):
        assert self.game.moves.state == self.game.S_INIT
        assert not self.base_cards
        while ncards > 0:
            assert self.cards
            c = self.cards[-1]
            for s in self.game.s.foundations:
                if not s.cards and (s.cap.base_suit < 0 or s.cap.base_suit == c.suit):
                    break
            else:
                assert 0
                s = None
            s.cap.base_rank = c.rank
            if update_saveinfo:
                cap = Struct(base_rank=c.rank)
                self.game.saveinfo.stack_caps.append((s.id, cap))
            if not c.face_up:
                self.game.flipMove(self)
            self.game.moveMove(1, self, s, frames=frames)
            ncards = ncards - 1


class RedealCards_StackMethods:

    def redealCards(self, rows=None, sound=0,
                    shuffle=False, reverse=False, frames=0):
        if sound and self.game.app.opt.animations:
            self.game.startDealSample()
        lr = len(self.game.s.rows)
        # move all cards to the Talon
        num_cards = 0
        assert len(self.cards) == 0
        if rows is None:
            rows = self.game.s.rows
        rows = list(rows)
        if reverse:
            rows.reverse()
        for r in rows:
            for i in range(len(r.cards)):
                num_cards += 1
                self.game.moveMove(1, r, self, frames=frames)
                if self.cards[-1].face_up:
                    self.game.flipMove(self)
        assert len(self.cards) == num_cards
        if num_cards == 0:          # game already finished
            return 0
        if shuffle:
            # shuffle
            self.game.shuffleStackMove(self)
        # redeal
        self.game.nextRoundMove(self)
        self.game.redealCards()
        if sound:
            self.game.stopSamples()
        return num_cards


# /***********************************************************************
# // The Talon is a stack with support for dealing.
# ************************************************************************/

class TalonStack(Stack,
                 DealRow_StackMethods,
                 DealBaseCard_StackMethods,
                 ):
    def __init__(self, x, y, game, max_rounds=1, num_deal=1, **cap):
        Stack.__init__(self, x, y, game, cap=cap)
        self.max_rounds = max_rounds
        self.num_deal = num_deal
        self.resetGame()

    def resetGame(self):
        self.round = 1
        self.base_cards = []        # for DealBaseCard_StackMethods

    def assertStack(self):
        Stack.assertStack(self)
        n = self.game.gameinfo.redeals
        if n < 0: assert self.max_rounds == n
        else:     assert self.max_rounds == n + 1

    # Control of dealing is transferred to the game which usually
    # transfers it back to the Talon - see dealCards() below.
    def clickHandler(self, event):
        return self.game.dealCards(sound=1)

    def rightclickHandler(self, event):
        return self.clickHandler(event)

    # Usually called by Game.canDealCards()
    def canDealCards(self):
        return len(self.cards) > 0

    # Actual dealing, usually called by Game.dealCards().
    # Either deal all cards in Game.startGame(), or subclass responsibility.
    def dealCards(self, sound=0):
        pass

    # remove all cards from all stacks
    def removeAllCards(self):
        for stack in self.game.allstacks:
            while stack.cards:
                stack.removeCard(update=0)
                ##stack.removeCard(unhide=0, update=0)
        for stack in self.game.allstacks:
            stack.updateText()

    def updateText(self, update_rounds=1, update_redeal=1):
        ##assertView(self)
        Stack.updateText(self)
        if update_rounds and self.game.preview <= 1:
            if self.texts.rounds is not None:
                t = _("Round %d") % self.round
                self.texts.rounds.config(text=t)
        if update_redeal:
            deal = self.canDealCards() != 0
            if self.images.redeal is not None:
                img = (self.getRedealImages())[deal]
                if img is not None and img is not self.images.redeal_img:
                    self.images.redeal.config(image=img)
                    self.images.redeal_img = img
                t = ("", _("Redeal"))[deal]
            else:
                t = (_("Stop"), _("Redeal"))[deal]
            if self.texts.redeal is not None and self.game.preview <= 1:
                if t != self.texts.redeal_str:
                    self.texts.redeal.config(text=t)
                    self.texts.redeal_str = t

    def prepareView(self):
        Stack.prepareView(self)
        if not self.is_visible or self.images.bottom is None:
            return
        if self.images.redeal is not None or self.texts.redeal is not None:
            return
        if self.game.preview > 1:
            return
        images = self.game.app.images
        cx, cy, ca = self.x + images.CARDW/2, self.y + images.CARDH/2, "center"
        if images.CARDW >= 54 and images.CARDH >= 54:
            # add a redeal image above the bottom image
            img = (self.getRedealImages())[self.max_rounds != 1]
            if img is not None:
                self.images.redeal = MfxCanvasImage(self.game.canvas, cx, cy,
                                         image=img, anchor="center")
                self.images.redeal_img = img
                self.images.redeal.tkraise(self.top_bottom)
                self.images.redeal.addtag(self.group)
                self.top_bottom = self.images.redeal
                if images.CARDH >= 90:
                    cy, ca = self.y + images.CARDH - 4, "s"
                else:
                    ca = None
        font = self.game.app.getFont("canvas_default")
        text_width = getTextWidth(_('Redeal'), font=font, root=self.game.canvas)
        if images.CARDW >= text_width+4 and ca:
            # add a redeal text above the bottom image
            if self.max_rounds != 1:
                images = self.game.app.images
                self.texts.redeal = MfxCanvasText(self.game.canvas, cx, cy,
                                                  anchor=ca, font=font)
                self.texts.redeal_str = ""
                self.texts.redeal.tkraise(self.top_bottom)
                self.texts.redeal.addtag(self.group)
                self.top_bottom = self.texts.redeal

    def getBottomImage(self):
        return self.game.app.images.getTalonBottom()

    def getRedealImages(self):
        # returns a tuple of two PhotoImages
        return self.game.app.gimages.redeal

    def getHelp(self):
        if   self.max_rounds == -2: nredeals = _('Variable redeals.')
        elif self.max_rounds == -1: nredeals = _('Unlimited redeals.')
        elif self.max_rounds ==  1: nredeals = _('No redeals.')
        elif self.max_rounds ==  2: nredeals = _('One redeal.')
        else: nredeals = str(self.max_rounds-1)+_(' redeals.')
        ##round = _('Round #%d.') % self.round
        return _('Talon.')+' '+nredeals ##+' '+round

    #def getBaseCard(self):
    #    return self._getBaseCard()


# A single click deals one card to each of the RowStacks.
class DealRowTalonStack(TalonStack):
    def dealCards(self, sound=0):
        return self.dealRowAvail(sound=sound)


# For games where the Talon is only used for the initial dealing.
class InitialDealTalonStack(TalonStack):
    # no bindings
    def initBindings(self):
        pass
    # no bottom
    def getBottomImage(self):
        return None


class RedealTalonStack(TalonStack, RedealCards_StackMethods):
    def canDealCards(self):
        if self.round == self.max_rounds:
            return False
        return not self.game.isGameWon()
    def dealCards(self, sound=0):
        RedealCards_StackMethods.redealCards(self, sound=sound)


# /***********************************************************************
# // An OpenStack is a stack where cards can be placed and dragged
# // (i.e. FoundationStack, RowStack, ReserveStack, ...)
# //
# // Note that it defaults to max_move=1 and max_accept=0.
# ************************************************************************/

class OpenStack(Stack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=0, max_cards=999999)
        Stack.__init__(self, x, y, game, cap=cap)


    #
    # Capabilities {model}
    #

    def acceptsCards(self, from_stack, cards):
        # default for OpenStack: we cannot accept cards (max_accept defaults to 0)
        return self.basicAcceptsCards(from_stack, cards)

    def canMoveCards(self, cards):
        # default for OpenStack: we can move the top card (max_move defaults to 1)
        return self.basicCanMoveCards(cards)

    def canFlipCard(self):
        # default for OpenStack: we can flip the top card
        if self.basicIsBlocked() or not self.cards:
            return 0
        return not self.cards[-1].face_up

    def canDropCards(self, stacks):
        if self.basicIsBlocked() or not self.cards:
            return (None, 0)
        cards = self.cards[-1:]
        if self.canMoveCards(cards):
            for s in stacks:
                if s is not self and s.acceptsCards(self, cards):
                    return (s, 1)
        return (None, 0)


    #
    # Mouse handlers {controller}
    #

    def clickHandler(self, event):
        flipstacks, dropstacks, quickstacks = self.game.getAutoStacks(event)
        if self in flipstacks and self.canFlipCard():
            self.playFlipMove()
            return -1               # continue this event (start a drag)
        return 0

    def rightclickHandler(self, event):
        if self.doubleclickHandler(event):
            return 1
        if self.game.app.opt.quickplay:
            flipstacks, dropstacks, quickstacks = self.game.getAutoStacks(event)
            if self in quickstacks:
                n = self.quickPlayHandler(event)
                self.game.stats.quickplay_moves += n
                return n
        return 0

    def doubleclickHandler(self, event):
        # flip or drop a card
        flipstacks, dropstacks, quickstacks = self.game.getAutoStacks(event)
        if self in flipstacks and self.canFlipCard():
            self.playFlipMove()
            return -1               # continue this event (start a drag)
        if self in dropstacks:
            to_stack, ncards = self.canDropCards(self.game.s.foundations)
            if to_stack:
                self.game.playSample("autodrop", priority=30)
                self.playMoveMove(ncards, to_stack, sound=0)
                return 1
        return 0

    def controlclickHandler(self, event):
        # highlight matching cards
        if self.game.app.opt.highlight_cards:
            return self.highlightMatchingCards(event)
        return 0

    def dragMove(self, drag, stack, sound=1):
        self.playMoveMove(len(drag.cards), stack, frames=0, sound=sound)

    def releaseHandler(self, event, drag, sound=1):
        cards = drag.cards
        # check if we moved the card by at least 10 pixels
        if event is not None:
            dx, dy = event.x - drag.start_x, event.y - drag.start_y
            if abs(dx) < 10 and abs(dy) < 10:
                # move cards back to their origin stack
                Stack.releaseHandler(self, event, drag, sound=sound)
                return
            ##print dx, dy
        # get destination stack
        stack = self.game.getClosestStack(cards[0], self)
        # move cards
        if not stack or stack is self or not stack.acceptsCards(self, cards):
            # move cards back to their origin stack
            Stack.releaseHandler(self, event, drag, sound=sound)
        else:
            # this code actually moves the cards to the new stack
            ##self.playMoveMove(len(cards), stack, frames=0, sound=sound)
            self.dragMove(drag, stack, sound=sound)

    def quickPlayHandler(self, event, from_stacks=None, to_stacks=None):
        # from_stacks and to_stacks are meant for possible
        # use in a subclasses
        if from_stacks is None:
            from_stacks = self.game.sg.dropstacks
        if to_stacks is None:
            ##to_stacks = self.game.s.rows + self.game.s.reserves
            ##to_stacks = self.game.sg.dropstacks
            to_stacks = self.game.s.foundations + self.game.sg.dropstacks
            ##from pprint import pprint; pprint(to_stacks)
        moves = []
        #
        if not self.cards:
            for s in from_stacks:
                if s is not self and s.cards:
                    pile = s.getPile()
                    if pile and self.acceptsCards(s, pile):
                        score = self.game.getQuickPlayScore(len(pile), s, self)
                        moves.append((score, -len(moves), len(pile), s, self))
        else:
            pile1, pile2 = None, self.getPile()
            if pile2:
                i = self._findCard(event)
                if i >= 0:
                    pile = self.cards[i:]
                    if len(pile) != len(pile2) and self.canMoveCards(pile):
                        pile1 = pile
            for pile in (pile1, pile2):
                if not pile:
                    continue
                for s in to_stacks:
                    if s is not self and s.acceptsCards(self, pile):
                        score = self.game.getQuickPlayScore(len(pile), self, s)
                        moves.append((score, -len(moves), len(pile), self, s))
        #
        if moves:
            moves.sort()
            ##from pprint import pprint; pprint(moves)
            score, len_moves, ncards, from_stack, to_stack = moves[-1]
            if score >= 0:
                ##self.game.playSample("startdrag")
                from_stack.playMoveMove(ncards, to_stack)
                return 1
        return 0

    def getHelp(self):
        if self.cap.max_accept == 0:
            return _('Reserve. No building.')
        return ''


# /***********************************************************************
# // Foundations stacks
# ************************************************************************/

class AbstractFoundationStack(OpenStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, suit=suit, base_suit=suit, base_rank=ACE,
                  dir=1, max_accept=1, max_cards=13)
        apply(OpenStack.__init__, (self, x, y, game), cap)

    def canDropCards(self, stacks):
        return (None, 0)

    def clickHandler(self, event):
        return 0

    def rightclickHandler(self, event):
        return 0

    def quickPlayHandler(self, event, from_stacks=None, to_stacks=None):
        return 0

    def getBottomImage(self):
        return self.game.app.images.getSuitBottom(self.cap.base_suit)

    def getBaseCard(self):
        return self._getBaseCard()

    def closeStackMove(self):
        if len(self.cards) == self.cap.max_cards:
            self.game.closeStackMove(self)

    def getHelp(self):
        return _('Foundation.')


# A SameSuit_FoundationStack is the typical Foundation stack.
# It builds up in rank and suit.
class SS_FoundationStack(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if self.cards:
            # check the rank
            if (self.cards[-1].rank + self.cap.dir) % self.cap.mod != cards[0].rank:
                return 0
        return 1

    def getHelp(self):
        if self.cap.dir > 0:   return _('Foundation. Build up by suit.')
        elif self.cap.dir < 0: return _('Foundation. Build down by suit.')
        else:                  return _('Foundation. Build by same rank.')


# A Rank_FoundationStack builds up in rank and ignores color and suit.
class RK_FoundationStack(SS_FoundationStack):
    def __init__(self, x, y, game, suit=ANY_SUIT, **cap):
        apply(SS_FoundationStack.__init__, (self, x, y, game, ANY_SUIT), cap)

    def assertStack(self):
        SS_FoundationStack.assertStack(self)
        ##assert self.cap.suit == ANY_SUIT
        assert self.cap.color == ANY_COLOR

    def getHelp(self):
        if self.cap.dir > 0:   return _('Foundation. Build up regardless of suit.')
        elif self.cap.dir < 0: return _('Foundation. Build down regardless of suit.')
        else:                  return _('Foundation. Build by same rank.')


# A AlternateColor_FoundationStack builds up in rank and alternate color.
# It is used in only a few games.
class AC_FoundationStack(SS_FoundationStack):
    def __init__(self, x, y, game, suit, **cap):
        kwdefault(cap, base_suit=suit)
        apply(SS_FoundationStack.__init__, (self, x, y, game, ANY_SUIT), cap)

    def acceptsCards(self, from_stack, cards):
        if not SS_FoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        if self.cards:
            # check the color
            if cards[0].color == self.cards[-1].color:
                return 0
        return 1

    def getHelp(self):
        if self.cap.dir > 0:   return _('Foundation. Build up by alternate color.')
        elif self.cap.dir < 0: return _('Foundation. Build down by alternate color.')
        else:                  return _('Foundation. Build by same rank.')


# /***********************************************************************
# // Abstract classes for row stacks.
# ************************************************************************/

# Abstract class.
class SequenceStack_StackMethods:
    def _isSequence(self, cards):
        # Are the cards in a basic sequence for our stack ?
        raise SubclassResponsibility

    def _isAcceptableSequence(self, cards):
        return self._isSequence(cards)

    def _isMoveableSequence(self, cards):
        return self._isSequence(cards)

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        # cards must be an acceptable sequence
        if not self._isAcceptableSequence(cards):
            return 0
        # [topcard + cards] must be an acceptable sequence
        if self.cards and not self._isAcceptableSequence([self.cards[-1]] + cards):
            return 0
        return 1

    def canMoveCards(self, cards):
        return self.basicCanMoveCards(cards) and self._isMoveableSequence(cards)


# Abstract class.
class BasicRowStack(OpenStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, dir=-1, base_rank=ANY_RANK)
        apply(OpenStack.__init__, (self, x, y, game), cap)
        self.CARD_YOFFSET = game.app.images.CARD_YOFFSET

    def getHelp(self):
        if self.cap.max_accept == 0:
            return _('Tableau. No building.')
        return ''

    #def getBaseCard(self):
    #    return self._getBaseCard()


# Abstract class.
class SequenceRowStack(SequenceStack_StackMethods, BasicRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=999999, max_accept=999999)
        apply(BasicRowStack.__init__, (self, x, y, game), cap)
    def getBaseCard(self):
        return self._getBaseCard()


# /***********************************************************************
# // Row stacks (the main playing stacks on the Tableau).
# ************************************************************************/

#
# Implementation of common row stacks follows here.
#

# An AlternateColor_RowStack builds down by rank and alternate color.
# e.g. Klondike
class AC_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isAlternateColorSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up by alternate color.')
        elif self.cap.dir < 0: return _('Tableau. Build down by alternate color.')
        else:                  return _('Tableau. Build by same rank.')

# A SameColor_RowStack builds down by rank and same color.
# e.g. Klondike
class SC_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isSameColorSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up by color.')
        elif self.cap.dir < 0: return _('Tableau. Build down by color.')
        else:                  return _('Tableau. Build by same rank.')

# A SameSuit_RowStack builds down by rank and suit.
class SS_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isSameSuitSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up by suit.')
        elif self.cap.dir < 0: return _('Tableau. Build down by suit.')
        else:                  return _('Tableau. Build by same rank.')

# A Rank_RowStack builds down by rank ignoring suit.
class RK_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isRankSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up regardless of suit.')
        elif self.cap.dir < 0: return _('Tableau. Build down regardless of suit.')
        else:                  return _('Tableau. Build by same rank.')


# ButOwn_RowStack
class BO_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isAnySuitButOwnSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up in any suit but the same.')
        elif self.cap.dir < 0: return _('Tableau. Build down in any suit but the same.')
        else:                  return _('Tableau. Build by same rank.')


# A Freecell_AlternateColor_RowStack
class FreeCell_AC_RowStack(AC_RowStack):
    def canMoveCards(self, cards):
        max_move = getNumberOfFreeStacks(self.game.s.reserves) + 1
        return len(cards) <= max_move and AC_RowStack.canMoveCards(self, cards)

# A Freecell_SameSuit_RowStack (i.e. Baker's Game)
class FreeCell_SS_RowStack(SS_RowStack):
    def canMoveCards(self, cards):
        max_move = getNumberOfFreeStacks(self.game.s.reserves) + 1
        return len(cards) <= max_move and SS_RowStack.canMoveCards(self, cards)

# A Spider_AlternateColor_RowStack builds down by rank and alternate color,
# but accepts sequences that match by rank only.
class Spider_AC_RowStack(AC_RowStack):
    def _isAcceptableSequence(self, cards):
        return isRankSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up regardless of suit. Sequences of cards in alternate color can be moved as a unit.')
        elif self.cap.dir < 0: return _('Tableau. Build down regardless of suit. Sequences of cards in alternate color can be moved as a unit.')
        else:                  return _('Tableau. Build by same rank.')

# A Spider_SameSuit_RowStack builds down by rank and suit,
# but accepts sequences that match by rank only.
class Spider_SS_RowStack(SS_RowStack):
    def _isAcceptableSequence(self, cards):
        return isRankSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up regardless of suit. Sequences of cards in the same suit can be moved as a unit.')
        elif self.cap.dir < 0: return _('Tableau. Build down regardless of suit. Sequences of cards in the same suit can be moved as a unit.')
        else:                  return _('Tableau. Build by same rank.')

# A Yukon_AlternateColor_RowStack builds down by rank and alternate color,
# but can move any face-up cards regardless of sequence.
class Yukon_AC_RowStack(BasicRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=999999, max_accept=999999)
        apply(BasicRowStack.__init__, (self, x, y, game), cap)

    def _isSequence(self, c1, c2):
        return (c1.rank + self.cap.dir) % self.cap.mod == c2.rank and c1.color != c2.color

    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return 0
        # [topcard + card[0]] must be acceptable
        if self.cards and not self._isSequence(self.cards[-1], cards[0]):
            return 0
        return 1

    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up by alternate color, can move any face-up cards regardless of sequence.')
        elif self.cap.dir < 0: return _('Tableau. Build down by alternate color, can move any face-up cards regardless of sequence.')
        else:                  return _('Tableau. Build by same rank, can move any face-up cards regardless of sequence.')

    def getBaseCard(self):
        return self._getBaseCard()

# A Yukon_SameSuit_RowStack builds down by rank and suit,
# but can move any face-up cards regardless of sequence.
class Yukon_SS_RowStack(Yukon_AC_RowStack):
    def _isSequence(self, c1, c2):
        return (c1.rank + self.cap.dir) % self.cap.mod == c2.rank and c1.suit == c2.suit
    def getHelp(self):
        if self.cap.dir > 0:   return _('Tableau. Build up by suit, can move any face-up cards regardless of sequence.')
        elif self.cap.dir < 0: return _('Tableau. Build down by suit, can move any face-up cards regardless of sequence.')
        else:                  return _('Tableau. Build by same rank, can move any face-up cards regardless of sequence.')

#
# King-versions of some of the above stacks: they accepts only Kings or
# sequences starting with a King as base_rank cards (i.e. when empty).
#

class KingAC_RowStack(AC_RowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, base_rank=KING)
        apply(AC_RowStack.__init__, (self, x, y, game), cap)

class KingSS_RowStack(SS_RowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, base_rank=KING)
        apply(SS_RowStack.__init__, (self, x, y, game), cap)

class KingRK_RowStack(RK_RowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, base_rank=KING)
        apply(RK_RowStack.__init__, (self, x, y, game), cap)


# up or down by color
class UD_SC_RowStack(SequenceRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1)
        apply(SequenceRowStack.__init__, (self, x, y, game), cap)
    def _isSequence(self, cards):
        return (isSameColorSequence(cards, self.cap.mod, 1) or
                isSameColorSequence(cards, self.cap.mod, -1))
    def getHelp(self):
        return _('Tableau. Build up or down by color.')

# up or down by alternate color
class UD_AC_RowStack(SequenceRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1)
        apply(SequenceRowStack.__init__, (self, x, y, game), cap)
    def _isSequence(self, cards):
        return (isAlternateColorSequence(cards, self.cap.mod, 1) or
                isAlternateColorSequence(cards, self.cap.mod, -1))
    def getHelp(self):
        return _('Tableau. Build up or down by alternate color.')

# up or down by suit
class UD_SS_RowStack(SequenceRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1)
        apply(SequenceRowStack.__init__, (self, x, y, game), cap)
    def _isSequence(self, cards):
        return (isSameSuitSequence(cards, self.cap.mod, 1) or
                isSameSuitSequence(cards, self.cap.mod, -1))
    def getHelp(self):
        return _('Tableau. Build up or down by suit.')

# up or down by rank ignoring suit
class UD_RK_RowStack(SequenceRowStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1, max_accept=1)
        apply(SequenceRowStack.__init__, (self, x, y, game), cap)
    def _isSequence(self, cards):
        return (isRankSequence(cards, self.cap.mod, 1) or
                isRankSequence(cards, self.cap.mod, -1))
    def getHelp(self):
        return _('Tableau. Build up or down regardless of suit.')




# /***********************************************************************
# // WasteStack (a helper stack for the Talon, e.g. in Klondike)
# ************************************************************************/

class WasteStack(OpenStack):
    def getHelp(self):
        return _('Waste.')


class WasteTalonStack(TalonStack):
    # A single click moves the top cards to the game's waste and
    # moves it face up; if we're out of cards, it moves the waste
    # back to the talon and increases the number of rounds (redeals).
    def __init__(self, x, y, game, max_rounds, num_deal=1, waste=None, **cap):
        apply(TalonStack.__init__, (self, x, y, game, max_rounds, num_deal), cap)
        self.waste = waste

    def prepareStack(self):
        TalonStack.prepareStack(self)
        if self.waste is None:
            self.waste = self.game.s.waste

    def canDealCards(self):
        waste = self.waste
        if self.cards:
            num_cards = min(len(self.cards), self.num_deal)
            return len(waste.cards) + num_cards <= waste.cap.max_cards
        elif waste.cards and self.round != self.max_rounds:
            return 1
        return 0

    def dealCards(self, sound=0):
        old_state = self.game.enterState(self.game.S_DEAL)
        num_cards = 0
        waste = self.waste
        if self.cards:
            if sound and not self.game.demo:
                self.game.playSample("dealwaste")
            num_cards = min(len(self.cards), self.num_deal)
            assert len(waste.cards) + num_cards <= waste.cap.max_cards
            for i in range(num_cards):
                if not self.cards[-1].face_up:
                    self.game.flipMove(self)
                self.game.moveMove(1, self, waste, frames=4, shadow=0)
                self.fillStack()
        elif waste.cards and self.round != self.max_rounds:
            if sound:
                self.game.playSample("turnwaste", priority=20)
            num_cards = len(waste.cards)
            self.game.turnStackMove(waste, self, update_flags=1)
        self.game.leaveState(old_state)
        return num_cards


class FaceUpWasteTalonStack(WasteTalonStack):
    def canFlipCard(self):
        return len(self.cards) > 0 and not self.cards[-1].face_up

    def fillStack(self):
        if self.canFlipCard():
            self.game.flipMove(self)
        self.game.fillStack(self)


class OpenTalonStack(TalonStack, OpenStack):
    canMoveCards = OpenStack.canMoveCards
    canDropCards = OpenStack.canDropCards
    releaseHandler = OpenStack.releaseHandler

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_move=1)
        apply(TalonStack.__init__, (self, x, y, game), cap)

    def canDealCards(self):
        return 0

    def canFlipCard(self):
        return len(self.cards) > 0 and not self.cards[-1].face_up

    def fillStack(self):
        if self.canFlipCard():
            self.game.flipMove(self)
        self.game.fillStack(self)

    def clickHandler(self, event):
        if self.canDealCards():
            return TalonStack.clickHandler(self, event)
        else:
            return OpenStack.clickHandler(self, event)


# /***********************************************************************
# // ReserveStack (free cell)
# ************************************************************************/

class ReserveStack(OpenStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_accept=1, max_cards=1)
        apply(OpenStack.__init__, (self, x, y, game), cap)

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()

    def getHelp(self):
        if self.cap.max_accept == 0:
            return _('Reserve. No building.')
        return _('Free cell.')


# /***********************************************************************
# // InvisibleStack (an internal off-screen stack to hold cards)
# ************************************************************************/

class InvisibleStack(Stack):
    def __init__(self, game, **cap):
        x, y = -500, -500 - len(game.allstacks)
        kwdefault(cap, max_move=0, max_accept=0)
        Stack.__init__(self, x, y, game, cap=cap)

    def assertStack(self):
        Stack.assertStack(self)
        assert not self.is_visible

    # no bindings
    def initBindings(self):
        pass

    # no bottom
    def getBottomImage(self):
        return None


# /***********************************************************************
# // ArbitraryStack (stack with arbitrary access)
# ************************************************************************/

class ArbitraryStack(OpenStack):

    def __init__(self, x, y, game, **cap):
        kwdefault(cap, max_accept=0)
        apply(OpenStack.__init__, (self, x, y, game), cap)
        self.CARD_YOFFSET = game.app.images.CARD_YOFFSET

    def canMoveCards(self, cards):
        return True

    def getDragCards(self, index):
        return [ self.cards[index] ]

    def startDrag(self, event, sound=1):
        OpenStack.startDrag(self, event, sound=sound)
        for c in self.cards[self.game.drag.index+1:]:
            c.moveBy(0, -self.CARD_YOFFSET[0])

    def doubleclickHandler(self, event):
        # flip or drop a card
        flipstacks, dropstacks, quickstacks = self.game.getAutoStacks(event)
        if self in flipstacks and self.canFlipCard():
            self.playFlipMove()
            return -1               # continue this event (start a drag)
        if self in dropstacks:
            i = self._findCard(event)
            if i < 0:
                return 0
            cards = [ self.cards[i] ]
            for s in self.game.s.foundations:
                if s is not self and s.acceptsCards(self, cards):
                    self.game.playSample("autodrop", priority=30)
                    self.playSingleCardMove(i, s, sound=0)
                    return 1
        return 0

    def moveCardsBackHandler(self, event, drag):
        i = self.cards.index(drag.cards[0])
        for card in self.cards[i:]:
            self._position(card)
            card.tkraise()

    def singleCardMove(self, index, to_stack, frames=-1, shadow=-1):
        self.game.singleCardMove(self, to_stack, index, frames=frames, shadow=shadow)
        self.fillStack()

    def dragMove(self, drag, to_stack, sound=1):
        self.playSingleCardMove(drag.index, to_stack, frames=0, sound=sound)

    def playSingleCardMove(self, index, to_stack, frames=-1, shadow=-1, sound=1):
        if sound:
            if to_stack in self.game.s.foundations:
                self.game.playSample("drop", priority=30)
            else:
                self.game.playSample("move", priority=10)
        self.singleCardMove(index, to_stack, frames=frames, shadow=shadow)
        if not self.game.checkForWin():
            # let the player put cards back from the foundations
            if not self in self.game.s.foundations:
                self.game.autoPlay()
        self.game.finishMove()

    def quickPlayHandler(self, event, from_stacks=None, to_stacks=None):
        if to_stacks is None:
            to_stacks = self.game.s.foundations + self.game.sg.dropstacks
        if not self.cards:
            return 0
        #
        moves = []
        i = self._findCard(event)
        if i < 0:
            return 0
        pile = [ self.cards[i] ]
        for s in to_stacks:
            if s is not self and s.acceptsCards(self, pile):
                score = self.game.getQuickPlayScore(1, self, s)
                moves.append((score, -len(moves), i, s))
        #
        if moves:
            moves.sort()
            ##from pprint import pprint; pprint(moves)
            score, len_moves, index, to_stack = moves[-1]
            if score >= 0:
                ##self.game.playSample("startdrag")
                self.playSingleCardMove(index, to_stack)
                return 1
        return 0


# /***********************************************************************
# // A StackWrapper is a functor (function object) that creates a
# // new stack when called, i.e. it wraps the constructor.
# //
# // "cap" are the capabilites, see class Stack above.
# ************************************************************************/

# self.cap override any call-time cap
class StackWrapper:
    def __init__(self, stack_class, **cap):
        assert type(stack_class) is types.ClassType
        assert issubclass(stack_class, Stack)
        self.stack_class = stack_class
        self.cap = cap

    # return a new stack (an instance of the stack class)
    def __call__(self, x, y, game, **cap):
        # must preserve self.cap, so create a shallow copy
        c = self.cap.copy()
        apply(kwdefault, (c,), cap)
        return apply(self.stack_class, (x, y, game), c)


# call-time cap override self.cap
class WeakStackWrapper(StackWrapper):
    def __call__(self, x, y, game, **cap):
        apply(kwdefault, (cap,), self.cap)
        return apply(self.stack_class, (x, y, game), cap)


# self.cap only, call-time cap is completely ignored
class FullStackWrapper(StackWrapper):
    def __call__(self, x, y, game, **cap):
        return apply(self.stack_class, (x, y, game), self.cap)



