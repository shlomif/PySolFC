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


# ************************************************************************
# * moves (undo / redo)
# ************************************************************************

## Currently we have the following atomic moves:
## - move the top cards from one stack on the top of another
## - flip the top card of a stack
## - turn a whole stack onto another stack
## - update the model or complete view a stack
## - increase the round (the number of redeals)
## - save the seed of game.random
## - shuffle a stack

class AtomicMove:

    def do(self, game):
        self.redo(game)

    def __repr__(self):
        return str(self.__dict__)
    def __str__(self):
        return str(self.__dict__)

    # Custom comparision for detecting redo moves. See Game.finishMove().
    def cmpForRedo(self, other):
        return -1


# ************************************************************************
# * Move the top N cards from a stack to another stack.
# ************************************************************************

class AMoveMove(AtomicMove):
    def __init__(self, ncards, from_stack, to_stack, frames, shadow=-1):
        assert from_stack is not to_stack
        self.ncards = ncards
        self.from_stack_id = from_stack.id
        self.to_stack_id = to_stack.id
        self.frames = frames
        self.shadow = shadow

    # do the actual move
    def _doMove(self, game, ncards, from_stack, to_stack):
        if game.moves.state == game.S_PLAY:
            assert to_stack.acceptsCards(from_stack, from_stack.cards[-ncards:])
        frames = self.frames
        if frames == -2 and game.moves.state not in (game.S_UNDO, game.S_REDO):
            # don't use animation for drag-move
            frames = 0
        cards = from_stack.cards[-ncards:]
        if frames != 0:
            from_stack.unshadeStack()
            x, y = to_stack.getPositionForNextCard()
            game.animatedMoveTo(from_stack, to_stack, cards, x, y,
                                frames=frames, shadow=self.shadow)
        for i in range(ncards):
            from_stack.removeCard()
        for c in cards:
            to_stack.addCard(c)
        from_stack.updatePositions()
        to_stack.updatePositions()

    def redo(self, game):
        self._doMove(game, self.ncards, game.allstacks[self.from_stack_id],
                     game.allstacks[self.to_stack_id])

    def undo(self, game):
        self._doMove(game, self.ncards, game.allstacks[self.to_stack_id],
                     game.allstacks[self.from_stack_id])

    def cmpForRedo(self, other):
        return (cmp(self.ncards, other.ncards) or
                cmp(self.from_stack_id, other.from_stack_id) or
                cmp(self.to_stack_id, other.to_stack_id))


# ************************************************************************
# * Flip the top card of a stack.
# ************************************************************************

class AFlipMove(AtomicMove):
    def __init__(self, stack):
        self.stack_id = stack.id

    # do the actual move
    def _doMove(self, game, stack):
        card = stack.cards[-1]
        ##game.animatedFlip(stack)
        if card.face_up:
            card.showBack()
        else:
            card.showFace()

    def redo(self, game):
        self._doMove(game, game.allstacks[self.stack_id])

    def undo(self, game):
        self._doMove(game, game.allstacks[self.stack_id])

    def cmpForRedo(self, other):
        return cmp(self.stack_id, other.stack_id)

# flip with animation
class ASingleFlipMove(AFlipMove):
    def _doMove(self, game, stack):
        card = stack.cards[-1]
        game.animatedFlip(stack)
        if card.face_up:
            card.showBack()
        else:
            card.showFace()

# flip and move one card
class AFlipAndMoveMove(AtomicMove):

    def __init__(self, from_stack, to_stack, frames):
        assert from_stack is not to_stack
        self.from_stack_id = from_stack.id
        self.to_stack_id = to_stack.id
        self.frames = frames

    def _doMove(self, game, from_stack, to_stack):
        if game.moves.state == game.S_PLAY:
            assert to_stack.acceptsCards(from_stack, from_stack.cards[-1])
        if self.frames == 0:
            moved = True
        else:
            moved = game.animatedFlipAndMove(from_stack, to_stack, self.frames)
        c = from_stack.cards[-1]
        if c.face_up:
            c.showBack()
        else:
            c.showFace()
        if not moved:
            cards = from_stack.cards[-1:]
            x, y = to_stack.getPositionForNextCard()
            game.animatedMoveTo(from_stack, to_stack, cards, x, y,
                                frames=self.frames, shadow=0)
        c = from_stack.removeCard(update=False)
        to_stack.addCard(c, update=False)
        from_stack.updateText()
        to_stack.updateText()

    def redo(self, game):
        self._doMove(game, game.allstacks[self.from_stack_id],
                     game.allstacks[self.to_stack_id])

    def undo(self, game):
        self._doMove(game, game.allstacks[self.to_stack_id],
                     game.allstacks[self.from_stack_id])

    def cmpForRedo(self, other):
        return (cmp(self.from_stack_id, other.from_stack_id) or
                cmp(self.to_stack_id, other.to_stack_id))


# ************************************************************************
# * Flip all cards
# ************************************************************************

class AFlipAllMove(AtomicMove):
    def __init__(self, stack):
        self.stack_id = stack.id

    def redo(self, game):
        stack = game.allstacks[self.stack_id]
        for card in stack.cards:
            if card.face_up:
                card.showBack()
            else:
                card.showFace()
        stack.refreshView()

    def undo(self, game):
        stack = game.allstacks[self.stack_id]
        for card in stack.cards:
            if card.face_up:
                card.showBack()
            else:
                card.showFace()
        stack.refreshView()

    def cmpForRedo(self, other):
        return cmp(self.stack_id, other.stack_id)


# ************************************************************************
# * Turn the Waste stack onto the empty Talon.
# ************************************************************************

class ATurnStackMove(AtomicMove):
    def __init__(self, from_stack, to_stack):
        assert from_stack is not to_stack
        self.from_stack_id = from_stack.id
        self.to_stack_id = to_stack.id

    def redo(self, game):
        from_stack = game.allstacks[self.from_stack_id]
        to_stack = game.allstacks[self.to_stack_id]
        assert len(from_stack.cards) > 0
        assert len(to_stack.cards) == 0
        l = len(from_stack.cards)
        for i in range(l):
            ##unhide = (i >= l - 2)
            unhide = 1
            ##print 1, unhide, from_stack.getCard().__dict__
            card = from_stack.removeCard(unhide=unhide, update=0)
            ##print 2, unhide, card.__dict__
            assert card.face_up
            to_stack.addCard(card, unhide=unhide, update=0)
            card.showBack(unhide=unhide)
            ##print 3, unhide, to_stack.getCard().__dict__
        from_stack.updateText()
        to_stack.updateText()

    def undo(self, game):
        from_stack = game.allstacks[self.to_stack_id]
        to_stack = game.allstacks[self.from_stack_id]
        assert len(from_stack.cards) > 0
        assert len(to_stack.cards) == 0
        l = len(from_stack.cards)
        for i in range(l):
            ##unhide = (i >= l - 2)
            unhide = 1
            card = from_stack.removeCard(unhide=unhide, update=0)
            assert not card.face_up
            card.showFace(unhide=unhide)
            to_stack.addCard(card, unhide=unhide, update=0)
        from_stack.updateText()
        to_stack.updateText()

    def cmpForRedo(self, other):
        return (cmp(self.from_stack_id, other.from_stack_id) or
                cmp(self.to_stack_id, other.to_stack_id))


# ************************************************************************
# * ATurnStackMove is somewhat optimized to avoid unnecessary
# * unhide and hide operations.
# * FIXME: doesn't work yet
# ************************************************************************

class NEW_ATurnStackMove(AtomicMove):
    def __init__(self, from_stack, to_stack, update_flags=1):
        assert from_stack is not to_stack
        self.from_stack_id = from_stack.id
        self.to_stack_id = to_stack.id
        self.update_flags = update_flags

    # do the actual turning move
    def _doMove(self, from_stack, to_stack, show_face):
        assert len(from_stack.cards) > 0
        assert len(to_stack.cards) == 0
        for card in from_stack.cards:
            card.item.dtag(from_stack.group)
            card.item.addtag(to_stack.group)
            if show_face:
                assert not card.face_up
                card.showFace(unhide=0)
            else:
                assert card.face_up
                card.showBack(unhide=0)
        to_stack.cards = from_stack.cards
        from_stack.cards = []
        from_stack.refreshView()
        from_stack.updateText()
        to_stack.refreshView()
        to_stack.updateText()

    def redo(self, game):
        from_stack = game.allstacks[self.from_stack_id]
        to_stack = game.allstacks[self.to_stack_id]
        if self.update_flags & 1:
            assert to_stack is game.s.talon
            assert to_stack.round < to_stack.max_rounds or to_stack.max_rounds < 0
            to_stack.round = to_stack.round + 1
        self._doMove(from_stack, to_stack, 0)

    def undo(self, game):
        from_stack = game.allstacks[self.from_stack_id]
        to_stack = game.allstacks[self.to_stack_id]
        if self.update_flags & 1:
            assert to_stack is game.s.talon
            assert to_stack.round > 1
            to_stack.round = to_stack.round - 1
        self._doMove(to_stack, from_stack, 1)

    def cmpForRedo(self, other):
        return (cmp(self.from_stack_id, other.from_stack_id) or
                cmp(self.to_stack_id, other.to_stack_id) or
                cmp(self.update_flags, other.update_flags))


# ************************************************************************
# * Update the view or model of a stack. Only needed for complex
# * games in combination with undo.
# ************************************************************************

class AUpdateStackMove(AtomicMove):
    def __init__(self, stack, flags):
        self.stack_id = stack.id
        self.flags = flags

    # do the actual move
    def _doMove(self, game, stack, undo):
        if self.flags & 64:
            # model
            stack.updateModel(undo, self.flags)
        else:
            # view
            if self.flags & 16:
                stack.updateText()
            if self.flags & 32:
                stack.refreshView()

    def redo(self, game):
        if (self.flags & 3) in (1, 3):
            self._doMove(game, game.allstacks[self.stack_id], 0)

    def undo(self, game):
        if (self.flags & 3) in (2, 3):
            self._doMove(game, game.allstacks[self.stack_id], 1)

    def cmpForRedo(self, other):
        return cmp(self.stack_id, other.stack_id) or cmp(self.flags, other.flags)


AUpdateStackModelMove = AUpdateStackMove
AUpdateStackViewMove = AUpdateStackMove


# ************************************************************************
# * Increase the `round' member variable of a Talon stack.
# ************************************************************************

class ANextRoundMove(AtomicMove):
    def __init__(self, stack):
        self.stack_id = stack.id

    def redo(self, game):
        stack = game.allstacks[self.stack_id]
        assert stack is game.s.talon
        assert stack.round < stack.max_rounds or stack.max_rounds < 0
        stack.round = stack.round + 1
        stack.updateText()

    def undo(self, game):
        stack = game.allstacks[self.stack_id]
        assert stack is game.s.talon
        assert stack.round > 1
        stack.round = stack.round - 1
        stack.updateText()

    def cmpForRedo(self, other):
        return cmp(self.stack_id, other.stack_id)


# ************************************************************************
# * Save the current state (needed for undo in some games).
# ************************************************************************

class ASaveSeedMove(AtomicMove):
    def __init__(self, game):
        self.state = game.random.getstate()

    def redo(self, game):
        game.random.setstate(self.state)

    def undo(self, game):
        game.random.setstate(self.state)

    def cmpForRedo(self, other):
        return cmp(self.state, other.state)


# ************************************************************************
# * Save game variables
# ************************************************************************

class ASaveStateMove(AtomicMove):
    def __init__(self, game, flags):
        self.state = game.getState()
        self.flags = flags

    def redo(self, game):
        if (self.flags & 3) in (1, 3):
            game.setState(self.state)

    def undo(self, game):
        if (self.flags & 3) in (2, 3):
            game.setState(self.state)

    def cmpForRedo(self, other):
        return cmp(self.state, other.state)


# ************************************************************************
# * Shuffle all cards of a stack. Saves the seed. Does not flip any cards.
# ************************************************************************

class AShuffleStackMove(AtomicMove):
    def __init__(self, stack, game):
        self.stack_id = stack.id
        # save cards and state
        self.card_ids = tuple([c.id for c in stack.cards])
        self.state = game.random.getstate()

    def redo(self, game):
        stack = game.allstacks[self.stack_id]
        # paranoia
        assert stack is game.s.talon
        # shuffle (see random)
        game.random.setstate(self.state)
        seq = stack.cards
        n = len(seq) - 1
        while n > 0:
            j = game.random.randint(0, n)
            seq[n], seq[j] = seq[j], seq[n]
            n = n - 1
        stack.refreshView()

    def undo(self, game):
        stack = game.allstacks[self.stack_id]
        # restore cards
        cards = []
        for id in self.card_ids:
            c = game.cards[id]
            assert c.id == id
            cards.append(c)
        stack.cards = cards
        # restore the state
        game.random.setstate(self.state)
        stack.refreshView()

    def cmpForRedo(self, other):
        return (cmp(self.stack_id, other.stack_id) or
                cmp(self.card_ids, other.card_ids) or
                cmp(self.state, other.state))


# ************************************************************************
# * ASingleCardMove - move single card from *anyone* position
# * (for ArbitraryStack)
# ************************************************************************

class ASingleCardMove(AtomicMove):

    def __init__(self, from_stack, to_stack, from_pos, frames, shadow=-1):
        self.from_stack_id = from_stack.id
        self.to_stack_id = to_stack.id
        self.from_pos = from_pos
        self.frames = frames
        self.shadow = shadow

    def redo(self, game):
        from_stack = game.allstacks[self.from_stack_id]
        to_stack = game.allstacks[self.to_stack_id]
        from_pos = self.from_pos
        if game.moves.state == game.S_PLAY:
            assert to_stack.acceptsCards(from_stack, [from_stack.cards[from_pos]])
        card = from_stack.cards[from_pos]
        card = from_stack.removeCard(card, update_positions=1)
        if self.frames != 0:
            x, y = to_stack.getPositionFor(card)
            game.animatedMoveTo(from_stack, to_stack, [card], x, y,
                                frames=self.frames, shadow=self.shadow)
        to_stack.addCard(card)
        ##to_stack.refreshView()

    def undo(self, game):
        from_stack = game.allstacks[self.from_stack_id]
        to_stack = game.allstacks[self.to_stack_id]
        from_pos = self.from_pos
        card = to_stack.removeCard()
##         if self.frames != 0:
##             x, y = to_stack.getPositionFor(card)
##             game.animatedMoveTo(from_stack, to_stack, [card], x, y,
##                                 frames=self.frames, shadow=self.shadow)
        from_stack.insertCard(card, from_pos)
        ##to_stack.refreshView()

    def cmpForRedo(self, other):
        return cmp((self.from_stack_id, self.to_stack_id, self.from_pos),
                   (other.from_stack_id, other.to_stack_id, other.from_pos))


# ************************************************************************
# * AInnerMove - change position of single card in stack (TODO)
# ************************************************************************

class AInnerMove(AtomicMove):

    def __init__(self, stack, from_pos, to_pos):
        self.stack_id = stack.id
        self.from_pos, self.to_pos = from_pos, to_pos

    def redo(self, game):
        stack = game.allstacks[self.stack_id]

    def undo(self, game):
        stack = game.allstacks[self.stack_id]

    def cmpForRedo(self, other):
        return cmp((self.stack_id, self.from_pos, self.to_pos),
                   (other.stack_id, other.from_pos, other.to_pos))

