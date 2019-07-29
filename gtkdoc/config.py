# This file is used when running gtkdoc uninstalled.

import os
from gtkdoc_uninstalled import builddir

exec(open(os.path.join(builddir, 'gtkdoc', 'config.py')).read())
