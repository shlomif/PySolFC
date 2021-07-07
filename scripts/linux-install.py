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
from subprocess import check_call


def main():
    try:
        subprocess.check_call(["gmake", "test", "rules"])
    except subprocess.CalledProcessError:
        subprocess.check_call(["make", "test", "rules"])

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
        cardsets_dir = "PySolFC-Cardsets-2.0"
        if not os.path.exists(cardsets_dir):
            arc = cardsets_dir + ".tar.gz"
            if not os.path.exists(arc):
                check_call([
                    "wget",
                    "https://github.com/shlomif/" +
                    "PySolFC-Cardsets/archive/2.0/" + arc])
                subprocess.check_call(["tar", "-xvf", arc])
        os.symlink(dot_pysol_cardsets, os.getcwd() + "/" + cardsets_dir)


main()
