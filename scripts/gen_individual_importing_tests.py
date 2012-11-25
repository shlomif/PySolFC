#!/usr/bin/env python
import os.path
for module_name in ['pysollib.mfxutil', 'pysollib.move', 'pysollib.resource', 'pysollib.settings', 'pysollib.mygettext', 'pysollib.wizardpresets',]:
    open(os.path.join(".", "tests", "individually-importing", "import_" + module_name + ".py"), 'w').write('''#!/usr/bin/env python
import sys
sys.path.append("./tests/lib")
from TAP.Simple import plan, ok

plan(1)
sys.path.insert(0, ".")
import %(module_name)s
ok(1, "imported")
''' % { 'module_name': module_name })
