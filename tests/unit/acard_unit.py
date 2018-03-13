#!/usr/bin/env python3
# Written by Shlomi Fish, under the MIT Expat License.

# imports
import sys
from TAP.Simple import plan, ok

from pysollib.acard import AbstractCard


def shlomif_main(args):

    plan(4)

    card1 = AbstractCard(1001, 0, 1, 2, 3001)
    # TEST
    ok(card1.color == 0, 'card1.color is sane.')

    # TEST
    ok(card1.rank == 2, 'card1.rank')

    card2 = AbstractCard(1001, 0, 3, 7, 3001)
    # TEST
    ok(card2.color == 1, 'card2.color is sane.')

    # TEST
    ok(card2.rank == 7, 'card2.rank')


if __name__ == "__main__":
    sys.exit(shlomif_main(sys.argv))
