#! /bin/sh
set -e

#
# y.sh
# Copyright (C) 2018 shlomif <shlomif@cpan.org>
#
# Distributed under terms of the MIT license.
#

rm -fr PySolFC-2.2.0
make dist
rm -fr PySolFC-2.2.0
tar -xvf dist/PySolFC-2.2.0.tar.xz
(cd PySolFC-2.2.0 && make test)
