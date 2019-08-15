import os
import sys

try:
    from gtkdoc_uninstalled import builddir
    exec(open(os.path.join(builddir, 'gtkdoc', 'config_data.py')).read())
except ModuleNotFoundError:
    from gtkdoc.config_data import *


def get_dirs(uninstalled):
    try:
        from gtkdoc_uninstalled import sourcedir
        gtkdocdir = sourcedir
        styledir = os.path.join(sourcedir, 'style')
    except ModuleNotFoundError:
        if uninstalled:
            # this does not work from buiddir!=srcdir
            gtkdocdir = os.path.split(sys.argv[0])[0]
            if not os.path.exists(gtkdocdir + '/gtk-doc.xsl'):
                # try 'srcdir' (set from makefiles) too
                if os.path.exists(os.environ.get("ABS_TOP_SRCDIR", '') + '/gtk-doc.xsl'):
                    gtkdocdir = os.environ['ABS_TOP_SRCDIR']
            styledir = gtkdocdir + '/style'
        else:
            gtkdocdir = os.path.join(datadir, 'gtk-doc/data')
            styledir = gtkdocdir
    return (gtkdocdir, styledir)
