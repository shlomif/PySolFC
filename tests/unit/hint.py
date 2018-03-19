#!/usr/bin/env python3
# Written by Shlomi Fish, under the MIT Expat License.

# imports
import sys
from TAP.Simple import diag, plan, ok

from pysollib.acard import AbstractCard
from pysollib.hint import Base_Solver_Hint


def shlomif_main(args):

    plan(1)

    card = AbstractCard(1001, 0, 3, 7, 3001)
    h = Base_Solver_Hint(None, None, base_rank=0)

    got = h.card2str2(card)
    # TEST
    if not ok(got == 'D-8', 'card2str2 works'):
        diag('got == ' + got)


if __name__ == "__main__":
    sys.exit(shlomif_main(sys.argv))
