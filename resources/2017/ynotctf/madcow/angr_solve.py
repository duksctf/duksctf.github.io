#!/usr/bin/env python2

import angr, simuvex, logging

logging.basicConfig(level=logging.DEBUG)

p = angr.Project('./MadCow_3ad6db829e62619f19a299086c0f22cf94b36903', load_options={'auto_load_libs': False})

ex = p.surveyors.Explorer(find=(0x0401C4D, ),avoid=(0x0401C54,))
res = ex.run()

for i in res.found:
    print i.state.posix.dumps(0)
