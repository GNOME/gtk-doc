#!@PYTHON@
# -*- python; coding: utf-8 -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 1998 Owen Taylor
#               2001-2005 Damon Chaplin
#               2009-2017  Stefan Sauer
#               2017  Jussi Pakkanen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

# Support both Python 2 and 3
from __future__ import print_function

import os, sys, argparse, subprocess
from glob import glob

from . import config


def run(options):
    module = options.args[0]
    document = options.args[1]
    if options.verbose:
        quiet = '0'
    else:
        quiet = '1'

    if options.uninstalled:
        # TODO: this does not work from buiddir!=srcdir
        gtkdocdir = os.path.split(sys.argv[0])[0]
    else:
        gtkdocdir = os.path.join(config.datadir, 'gtk-doc/data')

    # we could do "$path_option $PWD " to avoid needing rewriting entities that
    # are copied from the header into docs under xml
    if options.path == '':
        path_arg = []
    else:
        path_arg = [path_option, options.path]

    # would it make sense to create man pages only for certain refentries
    # e.g. for tools
    # see http://bugzilla.gnome.org/show_bug.cgi?id=467488
    return subprocess.call([config.xsltproc] + path_arg + [
        '--nonet',
        '--xinclude',
        '--stringparam',
        'gtkdoc.bookname',
        module,
        '--stringparam',
        'gtkdoc.version',
        config.version,
        '--stringparam',
        'chunk.quietly ',
        quiet,
        '--stringparam',
        'chunker.output.quiet',
        quiet,
        'http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl',
        document])
