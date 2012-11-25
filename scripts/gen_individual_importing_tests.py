#!/usr/bin/env python
import os.path
for module_name in ['pysollib.app', 'pysollib.acard', 'pysollib.actions', 'pysollib.customgame', 'pysollib.help', 'pysollib.hint', 'pysollib.images', 'pysollib.init', 'pysollib.main', 'pysollib.layout', 'pysollib.mfxutil', 'pysollib.move', 'pysollib.options', 'pysollib.pysolrandom', 'pysollib.resource', 'pysollib.settings', 'pysollib.stack', 'pysollib.stats', 'pysollib.mygettext', 'pysollib.wizardpresets', 'pysollib.util', 'pysollib.gamedb', 'pysollib.configobj.configobj', 'pysollib.configobj.validate', 'pysollib.game', 'pysollib.pysoltk', 'pysollib.pysolaudio', 'pysollib.wizardutil', 'pysollib.winsystems.aqua', 'pysollib.winsystems.common', 'pysollib.winsystems.x11', 'pysollib.winsystems.win32', 'pysollib.macosx.appSupport', ]:
    open(os.path.join(".", "tests", "individually-importing", "import_" + module_name + ".py"), 'w').write('''#!/usr/bin/env python
import sys
sys.path.append("./tests/lib")
from TAP.Simple import plan, ok

plan(1)
sys.path.insert(0, ".")
import %(module_name)s
ok(1, "imported")
''' % { 'module_name': module_name })
