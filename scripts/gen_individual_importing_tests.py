#!/usr/bin/env python
# Written by Shlomi Fish, under the MIT Expat License.

import os
import os.path
import re


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
    if "gtk" in module_name:
        continue

    def fmt(s):
        return s % {'module_name': module_name}

    open(os.path.join(".", "tests", "individually-importing",
                      fmt("import_v3_%(module_name)s.py")),
         'w').write(fmt('''#!/usr/bin/env python3
import sys
print('1..1')
sys.path.insert(0, ".")
import %(module_name)s
print('ok 1 - imported')
'''))
