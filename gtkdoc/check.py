# -*- python; coding: utf-8 -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 2007  David Nečas
#               2007-2017  Stefan Sauer
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

#############################################################################
# Script      : gtkdoc-check
# Description : Runs various checks on built documentation and outputs test
#                results. Can be run druring make check, by adding this to the
#                documentations Makefile.am: TESTS = $(GTKDOC_CHECK)
#############################################################################

# Support both Python 2 and 3
from __future__ import print_function

import os, re, sys, argparse, subprocess
from glob import glob

from . import config


def grep(regexp, filename, what):
    pattern = re.compile(regexp)
    with open(filename) as f:
        for line in f:
            for match in re.finditer(pattern, line):
                return match.group(1)
    sys.exit("Cannot find %s in %s" % (what, filename));


def check_empty(filename, what):
    with open(filename) as f:
        count = sum(1 for line in f if line.strip())
        if count:
            print("%s:1:E: %d %st\n" % (filename, count, what))
            return count
    return 0


def check_includes(filename):
    # Check that each XML file in the xml directory is included in doc_main_file
    with open(filename) as f:
        lines = f.read().splitlines()
        num_missing = 0;
        for include in glob('xml/*.xml'):
            try:
                next(line for line in lines if include in line)
            except StopIteration:
                num_missing += 1;
                print('% doesn\'t appear to include "%s"' % (filename, xml_file))

    return num_missing


def run():
    checks = 4

    parser = argparse.ArgumentParser(description='gtkdoc-check version %s - run documentation unit tests' % config.version)
    parser.add_argument('--version', action='version', version=config.version)
    parser.parse_args()

    # Get parameters from test env, if not there try to grab them from the makefile
    # We like Makefile.am more but builddir does not necessarily contain one.
    makefile = 'Makefile.am'
    if not os.path.exists(makefile):
        makefile = 'Makefile'

    # For historic reasons tests are launched in srcdir
    srcdir = os.environ.get('SRCDIR', None)
    builddir = os.environ.get('BUILDDIR', None)
    workdir = '.'
    if builddir:
        workdir = builddir

    doc_module = os.environ.get('DOC_MODULE', None)
    if not doc_module:
        doc_module = grep(r'^\s*DOC_MODULE\s*=\s*(\S+)', makefile, 'DOC_MODULE')

    doc_main_file = os.environ.get('DOC_MAIN_SGML_FILE', None)
    if not doc_main_file:
        doc_main_file = grep(r'^\s*DOC_MAIN_SGML_FILE\s*=\s*(\S+)', makefile, 'DOC_MAIN_SGML_FILE')
        doc_main_file = doc_main_file.replace('$(DOC_MODULE)', doc_module)

    print('Running suite(s): gtk-doc-doc_module')

    undocumented = int(grep(r'^(\d+)\s+not\s+documented\.\s*$',
                            os.path.join(workdir, doc_module + '-undocumented.txt'),
                            'number of undocumented symbols'))
    incomplete = int(grep(r'^(\d+)\s+symbols?\s+incomplete\.\s*$',
                          os.path.join(workdir, doc_module + '-undocumented.txt'),
                          'number of incomplete symbols'))
    total = undocumented + incomplete
    if total:
        print('doc_module-undocumented.txt:1:E: %d undocumented or incomplete symbols' % total)

    undeclared = check_empty(os.path.join(workdir, doc_module + '-undeclared.txt'),
                             'undeclared symbols')
    unused = check_empty(os.path.join(workdir, doc_module + '-unused.txt'),
                         'unused documentation entries')

    missing_includes = check_includes(os.path.join(workdir, doc_main_file))

    failed = (total > 0) + (undeclared != 0) + (unused != 0) + (missing_includes != 0)
    rate = 100.0 * (checks - failed) / checks
    print("%.1f%%: Checks %d, Failures: %d" % (rate, checks, failed))
    return failed
