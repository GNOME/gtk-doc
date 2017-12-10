#!/usr/bin/env python3
# -*- python; coding: utf-8 -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 2017  Stefan Sauer
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

"""Prototype for builtin docbook processing

The tool loaded the main xml document (<module>-docs.xml) and chunks it
like the xsl-stylesheets would do. For that it resolves all the xml-includes.

TODO: convert the docbook-xml to html

Examples:
python3 tools/db2html.py tests/gobject/docs/tester-docs.xml
ll tests/gobject/docs/db2html
python3 tools/db2html.py tests/bugs/docs/tester-docs.xml
ll tests/bugs/docs/db2html
"""

import argparse
import errno
import logging
import os
import sys

from lxml import etree

# http://www.sagehill.net/docbookxsl/Chunking.html
CHUNK_TAGS = [
    'appendix',
    'article',
    'bibliography',  # in article or book
    'book',
    'chapter',
    'colophon',
    'glossary',      # in article or book
    'index',         # in article or book
    'part',
    'preface',
    'refentry',
    'reference',
    'sect1',         # except first
    'section',       # if equivalent to sect1
    'set',
    'setindex',
]

# TODO: look up the abbrevs and hierarchy for other tags
# http://www.sagehill.net/docbookxsl/Chunking.html#GeneratedFilenames
CHUNK_NAMING = {
    'book': {
        'prefix': 'bk',
        'count': 0,
        'parent': None,
    },
    'chapter': {
        'prefix': 'ch',
        'count': 0,
        'parent': 'book'
    },
    'index': {
        'prefix': 'ix',
        'count': 0,
        'parent': 'book'
    },
    'sect1': {
        'prefix': 's',
        'count': 0,
        'parent': 'chapter',
    },
    'section': {
        'prefix': 's',
        'count': 0,
        'parent': 'chapter',
    },
}


def gen_chunk_name(node):
    if 'id' in node.attrib:
        return node.attrib['id']

    tag = node.tag
    if tag not in CHUNK_NAMING:
        CHUNK_NAMING[tag] = {
            'prefix': node.tag[:2],
            'count': 0
        }
        logging.warning('Add CHUNK_NAMING for "%s"', tag)

    naming = CHUNK_NAMING[tag]
    naming['count'] += 1
    name = ('%s%02d' % (naming['prefix'], naming['count']))
    # handle parents to make names of nested tags unique
    # TODO: we only need to prepend the parent if there are > 1 of them in the
    #       xml
    # while naming['parent']:
    #     parent = naming['parent']
    #     if parent not in CHUNK_NAMING:
    #         break;
    #     naming = CHUNK_NAMING[parent]
    #     name = ('%s%02d' % (naming['prefix'], naming['count'])) + name
    return name


def convert(out_dir, node, out_file=None):
    # iterate and chunk
    # TODO: convert to HTML, need a templates for each CHUNK_TAG

    for child in node:
        print('<%s %s>' % (child.tag, child.attrib))
        if child.tag in CHUNK_TAGS:
            base = gen_chunk_name(child) + '.html'
            out_filename = os.path.join(out_dir, base)
            convert(out_dir, child, open(out_filename, 'wt'))
        else:
            convert(out_dir, child, out_file)
    if out_file:
        out_file.close()


def main(index_file):
    tree = etree.parse(index_file)
    tree.xinclude()

    dir_name = os.path.dirname(index_file)

    # for testing: dump to output file
    # out_file = os.path.join(dir_name, 'db2html.xml')
    # tree.write(out_file)

    # TODO: rename to 'html' later on
    out_dir = os.path.join(dir_name, 'db2html')
    try:
        os.mkdir(out_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    convert(out_dir, tree.getroot())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='db2html - chunk docbook')
    parser.add_argument('sources', nargs='*')
    options = parser.parse_args()
    if len(options.sources) != 1:
        sys.exit('Expect one source file argument.')

    log_level = os.environ.get('GTKDOC_TRACE')
    if log_level == '':
        log_level = 'INFO'
    if log_level:
        logging.basicConfig(stream=sys.stdout,
                            level=logging.getLevelName(log_level.upper()),
                            format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    sys.exit(main(options.sources[0]))
