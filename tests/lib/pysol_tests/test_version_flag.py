# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 Shlomi Fish <shlomif@cpan.org>
#
# Written by Shlomi Fish, under the MIT Expat License.

import os
import re
import subprocess
import unittest


class CliFlagsTests(unittest.TestCase):
    def test_main(self):
        if os.name == 'nt':
            self.assertTrue(True)
            return
        o = subprocess.check_output(["./pysol.py", "--version", ])
        assert o
        string = o.decode('utf-8')
        self.assertTrue(re.match("\\APySol FC version [0-9]+\\.", string))
