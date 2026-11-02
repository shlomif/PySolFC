#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------
#
# Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
# Copyright (C) 2003 Mt. Hood Playing Card Co.
# Copyright (C) 2005-2009 Skomoroh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------

from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.hint import AbstractHint
from pysollib.layout import Layout
from pysollib.mygettext import _
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        AbstractFoundationStack, \
        InvisibleStack, \
        OpenStack, \
        Stack, \
        TalonStack
from pysollib.util import ACE, ANY_SUIT, CLUB, DIAMOND, HEART, JACK, KING, \
        QUEEN, SPADE


# ************************************************************************
# * Scoundrel
# ************************************************************************

def strengthValue(card):
    # Face value, but aces count as 14.
    if card.rank == ACE:
        return 14
    return card.rank + 1


class Scoundrel_Hint(AbstractHint):
    def computeHints(self):
        game = self.game
        if game.health <= 0:
            return
        discard = game.s.foundations[0]
        weapon = game.s.reserves[0]
        slain = game.s.reserves[1]
        potions, weapons, slay, fists, extra = [], [], [], [], []
        for r in game.s.rows:
            if not r.cards:
                continue
            cards = r.cards[-1:]
            if not r.canMoveCards(cards):
                continue
            card = cards[0]
            if card.suit == HEART:
                if self._shouldDrinkPotion():
                    potions.append(r)
                else:
                    extra.append(r)
            elif card.suit == DIAMOND:
                if weapon.acceptsCards(r, cards):
                    weapons.append(r)
            elif slain.acceptsCards(r, cards):
                slay.append(r)
            elif discard.acceptsCards(r, cards):
                fists.append(r)
        if potions:
            potions.sort(key=lambda s: strengthValue(s.cards[-1]),
                         reverse=True)
            self.addHint(30000, 1, potions[0], discard)
        for r in weapons:
            self.addHint(20000 + strengthValue(r.cards[-1]), 1, r, weapon)
        for r in slay:
            self.addHint(10000, 1, r, slain)
        for r in fists:
            self.addHint(5000, 1, r, discard)
        for r in extra:
            self.addHint(1000, 1, r, discard)

    def _shouldDrinkPotion(self):
        game = self.game
        if game.potion_used:
            return False
        # Full health: a potion heals nothing, so treat it as filler.
        if game.health >= game.MAX_HEALTH:
            return False
        # 15-19: wait until the third play of the room, so a hit can
        # still be taken first and the heal is not wasted early.
        if game.health >= 15:
            return game.room_plays >= 2
        # 14 or less: drink immediately - a bad monster can end the game.
        return True


class Scoundrel_Talon(TalonStack):
    def canDealCards(self):
        # Deal from the talon is to run from the room.  No running
        # from two rooms in a row.
        game = self.game
        if not self.cards or game.health <= 0:
            return False
        if game.ran_last or game.room_plays > 0:
            return False
        return len([r for r in game.s.rows if r.cards]) == len(game.s.rows)

    def dealCards(self, sound=True):
        if not self.canDealCards():
            return 0
        return self.game.runFromRoom(sound=sound)

    def dealRoom(self, sound=True):
        # Fill the empty places in the room.
        rows = [r for r in self.game.s.rows if not r.cards]
        return self.dealRowAvail(rows=rows, sound=sound)

    def getHelp(self):
        return _('Talon. Click to run from the room.')


class Scoundrel_Discard(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if cards[0].suit == HEART:
            return True
        elif cards[0].suit == DIAMOND:
            return from_stack == self.game.s.reserves[0]
        else:
            return True

    def getHelp(self):
        return _('Discard.')


class Scoundrel_RoomStack(OpenStack):
    def canMoveCards(self, cards):
        return self.game.health > 0 and OpenStack.canMoveCards(self, cards)

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        game = self.game
        card = self.cards[-1]
        old_state = game.enterState(game.S_FILL)
        game.saveStateMove(2 | 16)  # for undo
        game.applyHealthForMove(card, to_stack)
        cleared = game.countRoomPlay()
        game.saveStateMove(1 | 16)  # for redo
        game.leaveState(old_state)
        if to_stack is game.s.reserves[0] and to_stack.cards:
            to_stack.moveMove(
                len(to_stack.cards), game.s.foundations[0], frames=0)
        OpenStack.moveMove(self, ncards, to_stack, frames, shadow)

        if cleared and game.health > 0:
            game.s.talon.dealRoom()

    def doubleclickHandler(self, event):
        # Using the weapon is preferable to using fists
        for stacks in (self.game.s.reserves, self.game.s.foundations):
            to_stack, ncards = self.canDropCards(stacks)
            if to_stack:
                self.game.playSample("autodrop", priority=30)
                self.playMoveMove(ncards, to_stack, sound=False)
                return 1
        return 0


class Scoundrel_WeaponStack(OpenStack):
    def canMoveCards(self, cards):
        return False

    def acceptsCards(self, from_stack, cards):
        return from_stack in self.game.s.rows and cards[0].suit == DIAMOND

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        # Discard every monster slain with the weapon.
        game = self.game
        monsters = game.s.reserves[1]
        discard = game.s.foundations[0]
        if to_stack is discard and monsters.cards:
            game.moveMove(len(monsters.cards), monsters, discard, frames=0)
        OpenStack.moveMove(
            self, ncards, to_stack, frames=frames, shadow=shadow)

    def getHelp(self):
        return _('Equipped weapon.')

    getBottomImage = Stack._getReserveBottomImage


class Scoundrel_MonsterStack(OpenStack):
    def canMoveCards(self, cards):
        return False

    def acceptsCards(self, from_stack, cards):
        if len(self.game.s.reserves[0].cards) == 0:
            return False
        if from_stack not in self.game.s.rows:
            return False
        if cards[0].suit in (HEART, DIAMOND):
            return False
        if not self.cards:
            return True
        return strengthValue(cards[0]) <= strengthValue(self.cards[-1])

    def getHelp(self):
        return _('Monsters slain with weapon.')

    getBottomImage = Stack._getReserveBottomImage


class Scoundrel(Game):
    Hint_Class = Scoundrel_Hint
    MAX_HEALTH = 20
    ROOM_PLAYS = 3

    def _createCard(self, id, deck, suit, rank, x, y):
        # Remove red aces and face cards.
        if suit in (HEART, DIAMOND) and rank in (ACE, JACK, QUEEN, KING):
            return None
        return Game._createCard(self, id, deck, suit, rank, x, y)

    def createGame(self):
        self.health = self.MAX_HEALTH
        self.potion_used = False
        self.ran_last = False
        self.room_plays = 0
        l, s = Layout(self), self.s
        self.setSize(l.XM+6*l.XS, l.YM+2*l.YS)

        x, y = l.XM, l.YM
        s.talon = Scoundrel_Talon(x, y, self, max_rounds=1)
        l.createText(s.talon, 'ne')
        y += l.YS
        s.foundations.append(Scoundrel_Discard(x, y, self, suit=ANY_SUIT,
                                               max_cards=52))

        x = l.XM + 2 * l.XS
        y = l.YM
        for i in range(4):
            s.rows.append(Scoundrel_RoomStack(x, y, self))
            x += l.XS

        y += l.YS
        x = l.XM + 2 * l.XS
        s.reserves.append(Scoundrel_WeaponStack(
            x, y, self, max_accept=1, max_cards=1))
        x += l.XS
        s.reserves.append(Scoundrel_MonsterStack(x, y, self, max_accept=1))
        x += l.XS
        # To hold the deck while a room is put underneath it
        s.internals.append(InvisibleStack(self))
        y = l.YM + 1.4 * l.YS
        if self.preview <= 1:
            self.texts.info = \
                MfxCanvasText(self.canvas, x, y, anchor="nw",
                              font=self.app.getFont("canvas_large"))

        l.defaultStackGroups()

        self.setRegion(s.foundations,
                       (0, 0, l.XM + l.XS * 3 // 2, self.height))

    def startGame(self, flip=0, reverse=1):
        self.health = self.MAX_HEALTH
        self.potion_used = False
        self.ran_last = False
        self.room_plays = 0
        self._startAndDealRow()

    def applyHealthForMove(self, card, to_stack):
        # Black cards: fists (discard) take full damage; weapon reduces it
        if card.suit in (CLUB, SPADE):
            if to_stack is self.s.foundations[0]:
                self.health -= strengthValue(card)
            elif to_stack is self.s.reserves[1]:
                weapon = self.s.reserves[0].cards[-1]
                damage = max(0, strengthValue(card) - strengthValue(weapon))
                self.health -= damage
        elif card.suit == HEART and to_stack is self.s.foundations[0]:
            # Only the first potion in a room heals
            if not self.potion_used:
                self.health += strengthValue(card)
                self.potion_used = True
        if self.health < 0:
            self.health = 0
        elif self.health > self.MAX_HEALTH:
            self.health = self.MAX_HEALTH

    def countRoomPlay(self):
        # Playing three cards clears the room - return True
        # when that happened, so the next room can be dealt.
        self.room_plays += 1
        if self.room_plays < self.ROOM_PLAYS:
            return False
        # Reset the room.
        self.potion_used = False
        self.room_plays = 0
        self.ran_last = False
        return True

    def runFromRoom(self, sound=True):
        # The room is placed at the bottom of the deck.  Since cards are
        # dealt off the top, the deck is parked on an invisible stack, the
        # room is moved onto the empty talon and the deck is replaced.
        talon, parked = self.s.talon, self.s.internals[0]
        old_state = self.enterState(self.S_FILL)
        self.saveStateMove(2 | 16)  # for undo
        self.ran_last = True
        self.saveStateMove(1 | 16)  # for redo
        self.leaveState(old_state)
        ncards = len(talon.cards)
        if ncards:
            self.moveMove(ncards, talon, parked, frames=0)
        for r in self.s.rows:
            if r.cards:
                self.flipAndMoveMove(r, talon)
        if ncards:
            self.moveMove(ncards, parked, talon, frames=0)
        return talon.dealRoom(sound=sound)

    def getAutoStacks(self, event=None):
        # Disable auto-drop outside events.
        if event is None:
            return ((), (), self.sg.dropstacks)
        return ((), self.sg.dropstacks, self.sg.dropstacks)

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        # Using the weapon is preferable to using fists
        if to_stack in self.s.foundations:
            return 0
        return 1

    def isGameWon(self):
        if self.health <= 0:
            return False
        if len(self.s.talon.cards) > 0:
            return False
        for r in self.s.rows:
            if len(r.cards) > 0:
                return False
        return True

    def updateText(self):
        if self.preview > 1 or not self.texts.info:
            return
        self.texts.info.config(text=_("Health: %d") % self.health)

    def parseGameInfo(self):
        return _("Health: %d") % self.health

    def getState(self):
        return [self.health, self.potion_used, self.room_plays, self.ran_last]

    def setState(self, state):
        self.health = state[0]
        self.potion_used = state[1]
        self.room_plays = state[2]
        self.ran_last = state[3]

    def _restoreGameHook(self, game):
        dval = game.loadinfo.dval
        self.health = dval.get('Health', self.MAX_HEALTH)
        self.potion_used = dval.get('PotionUsed', False)
        self.room_plays = dval.get('RoomPlays', 0)
        self.ran_last = dval.get('RanLast', False)

    def _loadGameHook(self, p):
        self.loadinfo.addattr(dval=p.load())

    def _saveGameHook(self, p):
        p.dump({'Health': self.health,
                'PotionUsed': self.potion_used,
                'RoomPlays': self.room_plays,
                'RanLast': self.ran_last})


# register the game
registerGame(GameInfo(992, Scoundrel, "Scoundrel",
                      GI.GT_1DECK_TYPE | GI.GT_STRIPPED, 1, 0,
                      GI.SL_BALANCED, ncards=44, si={"ncards": 44}))
