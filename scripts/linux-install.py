#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Shlomi Fish < https://www.shlomifish.org/ >
#
# Licensed under the terms of the MIT license.

"""

"""

import os
import os.path
import subprocess


def main():
    def _make_test(make_exe):
        subprocess.check_call([make_exe, "test", "rules"])

    os.chdir('../')

    try:
        _make_test("gmake")
    except (subprocess.CalledProcessError, FileNotFoundError):
        _make_test("make")

    if not os.path.exists("./images"):
        os.symlink("./data/images/", "./images")
    home = os.environ['HOME']
    dot_pysol = home + "/.PySolFC"
    dot_pysol_cardsets = dot_pysol + "/cardsets"
    if not os.path.exists("./images"):
        os.symlink("./data/images/", "./images")
    if not os.path.exists(dot_pysol):
        os.mkdir(dot_pysol)
    if not os.path.exists(dot_pysol_cardsets):
        cardsets_dir = "PySolFC-Cardsets-2.1"
        if not os.path.exists(cardsets_dir):
            arc = cardsets_dir + ".tar.gz"
            if not os.path.exists(arc):
                subprocess.check_call([
                    "wget",
                    "https://github.com/joeraz/" +
                    "PySolFC-Cardsets/archive/2.1/" + arc
                ])
                subprocess.check_call(["tar", "-xvf", arc])
        os.symlink(os.getcwd() + "/" + cardsets_dir, dot_pysol_cardsets, )


main()
