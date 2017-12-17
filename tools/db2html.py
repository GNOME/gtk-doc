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
- more templates
- refentry/index nav headers
- for refsect, we need a 'long-title' that also contains refpurpose
- figure how to deal with all the possible docbook
  - how can we report 'unhandled' data

Requirements:
sudo pip3 install anytree jinja2 lxml

Examples:
python3 tools/db2html.py tests/gobject/docs/tester-docs.xml
ll tests/gobject/docs/db2html

python3 tools/db2html.py tests/bugs/docs/tester-docs.xml
ll tests/bugs/docs/db2html
cp tests/bugs/docs/html/*.{css,png} tests/bugs/docs/db2html/
xdg-open tests/bugs/docs/db2html/index.html
meld tests/bugs/docs/{html,db2html}

Benchmarking:
(cd tests/bugs/docs/; rm html-build.stamp; time make html-build.stamp)
"""

import argparse
import errno
import logging
import os
import sys

from anytree import Node, PreOrderIter
from jinja2 import Environment, FileSystemLoader
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


class ChunkParams(object):
    def __init__(self, prefix, parent=None):
        self.prefix = prefix
        self.parent = None
        self.count = 0


# TODO: look up the abbrevs and hierarchy for other tags
# http://www.sagehill.net/docbookxsl/Chunking.html#GeneratedFilenames
CHUNK_PARAMS = {
    'book': ChunkParams('bk'),
    'chapter': ChunkParams('ch', 'book'),
    'index': ChunkParams('ix', 'book'),
    'sect1': ChunkParams('s', 'chapter'),
    'section': ChunkParams('s', 'chapter'),
}

TITLE_XPATH = {
    'book': etree.XPath('./bookinfo/title/text()'),
    'chapter': etree.XPath('./title/text()'),
    'index': etree.XPath('./title/text()'),
    'refentry': etree.XPath('./refmeta/refentrytitle/text()'),
}

# Jinja2 templates
TOOL_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENV = Environment(
    # loader=PackageLoader('gtkdoc', 'templates'),
    # autoescape=select_autoescape(['html', 'xml'])
    loader=FileSystemLoader(os.path.join(TOOL_PATH, 'templates')),
    autoescape=False,
    trim_blocks=True,
)

TEMPLATES = {
    'book': TEMPLATE_ENV.get_template('book.html'),
    'index': TEMPLATE_ENV.get_template('index.html'),
    'refentry': TEMPLATE_ENV.get_template('refentry.html'),
}


def gen_chunk_name(node):
    if 'id' in node.attrib:
        return node.attrib['id']

    tag = node.tag
    if tag not in CHUNK_PARAMS:
        CHUNK_PARAMS[tag] = ChunkParams(node.tag[:2])
        logging.warning('Add CHUNK_PARAMS for "%s"', tag)

    naming = CHUNK_PARAMS[tag]
    naming.count += 1
    name = ('%s%02d' % (naming.prefix, naming.count))
    # handle parents to make names of nested tags unique
    # TODO: we only need to prepend the parent if there are > 1 of them in the
    #       xml
    # while naming.parent:
    #     parent = naming.parent
    #     if parent not in CHUNK_PARAMS:
    #         break;
    #     naming = CHUNK_PARAMS[parent]
    #     name = ('%s%02d' % (naming.prefix, naming.count)) + name
    return name


def get_chunk_title(node):
    tag = node.tag
    if tag not in TITLE_XPATH:
        logging.warning('Add TITLE_XPATH for "%s"', tag)
        return ''

    xpath = TITLE_XPATH[tag]
    return xpath(node, smart_strings=False)[0]


def chunk(xml_node, parent=None):
    """Chunk the tree.

    The first time, we're called with parent=None and in that case we return
    the new_node as the root of the tree
    """
    # print('<%s %s>' % (xml_node.tag, xml_node.attrib))
    if xml_node.tag in CHUNK_TAGS:
        # TODO: do we need to remove the xml-node from the parent?
        #       we generate toc from the files tree
        # from copy import deepcopy
        # sub_tree = deepcopy(xml_node)
        # xml_node.getparent().remove(xml_node)
        # # or:
        # sub_tree = etree.ElementTree(xml_node).getroot()
        parent = Node(xml_node.tag, parent=parent, xml=xml_node,
                      filename=gen_chunk_name(xml_node) + '.html',
                      title=get_chunk_title(xml_node))
    for child in xml_node:
        chunk(child, parent)

    return parent


def convert(out_dir, files, node):
    """Convert the docbook chunks to a html file."""

    logging.info('Writing: %s', node.filename)
    with open(os.path.join(out_dir, node.filename), 'wt') as html:
        if node.name in TEMPLATES:
            # TODO: ideally precomiple common xpath exprs once:
            #   func = etree.XPath('//b')
            #   func(xml_node)[0]
            def lxml_xpath(expr):
                return node.xml.xpath(expr, smart_strings=False)[0]

            template = TEMPLATES[node.name]
            template.globals['xpath'] = lxml_xpath
            params = {
                'title': node.title,
                'nav_home': node.root,
            }
            if 'id' in node.xml.attrib:
                params['id'] = node.xml.attrib['id']
            else:
                # TODO: generate?
                logging.warning('No top-level "id" for "%s"', node.xml.tag)
            # nav params: up, prev, next
            if node.parent:
                params['nav_up'] = node.parent
            ix = files.index(node)
            if ix > 0:
                params['nav_prev'] = files[ix - 1]
            if ix < len(files) - 1:
                params['nav_next'] = files[ix + 1]

            # page specific vars
            # TODO: extract into functions?
            if node.name == 'book':
                params['toc'] = node.root

            html.write(template.render(**params))
        else:
            logging.warning('Add template for "%s"', node.name)


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
    files = chunk(tree.getroot())
    # 2) iterate the tree and output files
    # TODO: use multiprocessing
    files = list(PreOrderIter(files))
    for node in files:
        convert(out_dir, files, node)


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
