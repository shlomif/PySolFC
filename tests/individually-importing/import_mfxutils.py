#!/usr/bin/env python
import sys
sys.path.append("./tests/lib")
from TAP.Simple import plan, ok

plan(1)
sys.path.append(".")
import pysollib.mfxutil
ok(1, "imported")
