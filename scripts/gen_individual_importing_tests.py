#!/usr/bin/env python
# Written by Shlomi Fish, under the MIT Expat License.

import os
import os.path
import re
from sys import platform

IS_MAC = (platform == "darwin")
TEST_TAGS = os.getenv('TEST_TAGS', '')


def _has_tag(tag):
    return re.search("\\b{}\\b".format(tag), TEST_TAGS)


PY_VERS = ([2] if _has_tag('WITH_PY2') else [])+[3]
SKIP_GTK = _has_tag('SKIP_GTK')
module_names = []
for d, _, files in os.walk("pysollib"):
    for f in files:
        if re.search("\\.py$", f):
            module_names.append(
                (d + "/" + re.sub("\\.py$", "", f))
                .replace("/", ".").replace(os.sep, "."))

module_names.sort()
for module_name in module_names:
    if "kivy" in module_name:
        continue
    is_gtk = ("gtk" in module_name)
    for ver in PY_VERS:
        if ((not is_gtk) or (ver == 2 and (not IS_MAC) and (not SKIP_GTK))):
            def fmt(s):
                return s % {'module_name': module_name, 'ver': ver}
            open(os.path.join(".", "tests", "individually-importing",
                              fmt("import_v%(ver)d_%(module_name)s.py")),
                 'w').write(fmt('''#!/usr/bin/env python%(ver)d
import sys
print('1..1')
sys.path.insert(0, ".")
import %(module_name)s
print('ok 1 - imported')
'''))
