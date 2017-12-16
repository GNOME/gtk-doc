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
- try macros for the navigation

Requirements:
sudo pip3 install anytree jinja2 lxml

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

from anytree import Node
from jinja2 import Template
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

DOCTYPE = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'

BOOK_TEMPLATE = DOCTYPE + """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>{{ xpath('./bookinfo/title/text()') }}</title>
</head>
<body>
</body>
</html>
"""

TEMPLATES = {
    'book': Template(BOOK_TEMPLATE),
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


def chunk(out_dir, xml_node, parent=None):
    """Chunk the tree.

    The first time, we're called with parent=None and in that case we return
    the new_node as the root of the tree
    """
    # print('<%s %s>' % (xml_node.tag, xml_node.attrib))
    if xml_node.tag in CHUNK_TAGS:
        base = gen_chunk_name(xml_node) + '.html'
        out_filename = os.path.join(out_dir, base)
        # print('*** %s ***' % (out_filename))
        # TODO: do we need to remove the xml-node from the parent?
        #       we generate toc from the files tree
        # from copy import deepcopy
        # ..., xml=deepcopy(xml_node), ...
        # xml_node.getparent().remove(xml_node)
        parent = Node(xml_node.tag, parent=parent, xml=xml_node, filename=out_filename)
    for child in xml_node:
        chunk(out_dir, child, parent)

    return parent


def convert(node):
    """Convert the docbook chunks to html files."""

    logging.info('Writing: %s', node.filename)
    with open(node.filename, 'wt') as html:
        if node.name in TEMPLATES:
            # TODO: ideally precomiple common xpath exprs once:
            #   func = etree.XPath("//b")
            #   func(xml_node)[0]
            def lxml_xpath(expr):
                return node.xml.xpath(expr, smart_strings=False)[0]

            template = TEMPLATES[node.name]
            template.globals['xpath'] = lxml_xpath
            # TODO: extract from xml
            params = {
            }
            html.write(template.render(**params))
        else:
            logging.warning('Add template for "%s"', node.name)

    for child in node.children:
        convert(child)


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

    # We need two passes:
    # 1) recursively walk the tree and chunk it into a python tree so that we
    #   can generate navigation and link tags
    files = chunk(out_dir, tree.getroot())
    # 2) walk the tree and output files
    # TODO: iterate with the anytree iterator and use multiprocessing
    convert(files)


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
