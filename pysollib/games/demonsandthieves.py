from pysollib.game import Game
from pysollib.gamedb import GI, GameInfo, registerGame
from pysollib.layout import Layout
from pysollib.pysoltk import MfxCanvasText
from pysollib.stack import \
        AC_RowStack, \
        OpenStack, \
        SS_FoundationStack, \
        SS_RowStack, \
        WasteStack, \
        WasteTalonStack
from pysollib.util import ANY_RANK, RANKS


# ************************************************************************
# * Demons and Thieves
# ************************************************************************

class DemonsAndThieves_StackMethods:
    def acceptsCards(self, from_stack, cards):
        if not self.basicAcceptsCards(from_stack, cards):
            return False
        # [topcard + bottomcard] must be an acceptable sequence
        if (self.cards and not
                self._isAcceptableSequence([self.cards[-1]] + [cards[0]])):
            return False
        return True


class DemonsAndThieves_AC_RowStack(DemonsAndThieves_StackMethods, AC_RowStack):
    pass


class DemonsAndThieves_SS_RowStack(DemonsAndThieves_StackMethods, SS_RowStack):
    pass


class DemonsAndThieves(Game):
    def createGame(self, max_rounds=3, num_deal=1,
                   text=True, round_text=True, dir=-1):
        # create layout
        lay, s = Layout(self), self.s
        decks = self.gameinfo.decks

        # (piles up to 20 cards are playable in default window size)
        h = max(3 * lay.YS, lay.YS + 13 * 10)
        if round_text:
            h += lay.TEXT_HEIGHT
        self.setSize(
            lay.XM + (2 + max(9.5, 4 * decks)) * lay.XS + lay.XM,
            lay.YM + lay.YS + lay.TEXT_HEIGHT + h)

        # extra settings
        self.base_card = None

        # create stacks
        x, y = lay.XM, lay.YM
        if round_text:
            y += lay.TEXT_HEIGHT
        s.talon = WasteTalonStack(x, y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        lay.createText(s.talon, "s")
        if round_text:
            lay.createRoundText(s.talon, 'n')
        x += lay.XS
        s.waste = WasteStack(x, y, self)
        lay.createText(s.waste, "s")
        x += lay.XM
        y = lay.YM
        if round_text:
            y += lay.TEXT_HEIGHT
        for i in range(4):
            for j in range(decks):
                x += lay.XS
                s.foundations.append(SS_FoundationStack(x, y, self, i,
                                                        mod=13, max_move=0))
        if text:
            if 10 > 4 * decks:
                tx, ty, ta, tf = lay.getTextAttr(None, "se")
                tx, ty = x + tx + lay.XM, y + ty
            else:
                tx, ty, ta, tf = lay.getTextAttr(None, "s")
                tx, ty = x + tx, y + ty
            font = self.app.getFont("canvas_default")
            self.texts.info = MfxCanvasText(self.canvas, tx, ty,
                                            anchor=ta, font=font)
        x, y = lay.XM, lay.YM + lay.YS + lay.TEXT_HEIGHT
        if round_text:
            y += lay.TEXT_HEIGHT
        s.reserves.append(OpenStack(x, y, self))
        s.reserves[0].CARD_YOFFSET = 10
        x, y = lay.XM + 2 * lay.XS + lay.XM, lay.YM + lay.YS
        if round_text:
            y += lay.TEXT_HEIGHT
        if text:
            y += lay.TEXT_HEIGHT
        for i in range(4):
            s.rows.append(DemonsAndThieves_AC_RowStack(x, y, self,
                                                       base_rank=ANY_RANK,
                                                       dir=dir))
            x += lay.XS
        x += (lay.XS * .5)
        for i in range(5):
            s.rows.append(DemonsAndThieves_SS_RowStack(x, y, self,
                                                       base_rank=ANY_RANK,
                                                       dir=dir))
            x += lay.XS

        # define stack-groups
        lay.defaultStackGroups()

    #
    # game extras
    #

    def updateText(self):
        if self.preview > 1:
            return
        if not self.texts.info:
            return
        if not self.base_card:
            t = ""
        else:
            t = RANKS[self.base_card.rank]
        self.texts.info.config(text=t)

    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.base_card = None
        self.updateText()
        for i in range(7):
            self.s.talon.dealRow(rows=self.s.rows[4:9], flip=1, frames=0)
        self.s.talon.dealRow()
        # deal base_card to Foundations, update foundations cap.base_rank
        self.base_card = self.s.talon.getCard()
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank
        n = self.base_card.suit * self.gameinfo.decks
        if self.s.foundations[n].cards:
            assert self.gameinfo.decks > 1
            n = n + 1
        self.flipMove(self.s.talon)
        self.moveMove(1, self.s.talon, self.s.foundations[n])
        self.updateText()
        # fill the Reserve
        for i in range(13):
            self.moveMove(
                1, self.s.talon, self.s.reserves[0], frames=4, shadow=0)
        if self.s.reserves[0].canFlipCard():
            self.flipMove(self.s.reserves[0])

        self.s.talon.dealCards()

    shallHighlightMatch = Game._shallHighlightMatch_ACW

    def _restoreGameHook(self, game):
        self.base_card = self.cards[game.loadinfo.base_card_id]
        for s in self.s.foundations:
            s.cap.base_rank = self.base_card.rank

    def _loadGameHook(self, p):
        self.loadinfo.addattr(base_card_id=None)    # register extra load var.
        self.loadinfo.base_card_id = p.load()

    def _saveGameHook(self, p):
        p.dump(self.base_card.id)


# register the game
registerGame(GameInfo(889, DemonsAndThieves, "Demons and Thieves",
                      GI.GT_FORTY_THIEVES, 2, 2, GI.SL_MOSTLY_SKILL))
