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
- more templates or maybe don't use jinja2 at all
- refentry/index nav headers
- check each docbook tag if it can contain #PCDATA, if not don't check for
  xml.text

OPTIONAL:
- minify html: https://pypi.python.org/pypi/htmlmin/

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

# TODO(ensonic): requires gtk-doc to be installed, rewrite later
sys.path.append('/usr/share/gtk-doc/python')
from gtkdoc.fixxref import NoLinks


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
    # extensions=['jinja2.ext.do'],
    autoescape=False,
    lstrip_blocks=True,
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

# conversion helpers


def convert_inner(xml, result):
    for child in xml:
        result.extend(convert_tags.get(child.tag, convert__unknown)(child))


def convert_ignore(xml):
    return ['']


missing_tags = {}


def convert__unknown(xml):
    # warn only once
    if xml.tag not in missing_tags:
        logging.warning('Add tag converter for "%s"', xml.tag)
        missing_tags[xml.tag] = True
    result = ['<!-- ' + xml.tag + '-->\n']
    convert_inner(xml, result)
    result.append('<!-- /' + xml.tag + '-->\n')
    return result


def convert_refsect(xml, h_tag, inner_func=convert_inner):
    result = ['<div class="%s">\n' % xml.tag]
    title = xml.find('title')
    if title is not None:
        if 'id' in xml.attrib:
            result.append('<a name="%s"></a>' % xml.attrib['id'])
        result.append('<%s>%s</%s>' % (h_tag, title.text, h_tag))
        xml.remove(title)
    if xml.text:
        result.append(xml.text)
    inner_func(xml, result)
    result.append('</div>')
    if xml.tail:
        result.append(xml.tail)
    return result


# docbook tags


def convert_colspec(xml):
    result = ['<col']
    a = xml.attrib
    if 'colname' in a:
        result.append(' class="%s"' % a['colname'])
    if 'colwidth' in a:
        result.append(' width="%s"' % a['colwidth'])
    result.append('>\n')
    # is in tgroup and there can be no 'text'
    return result


def convert_div(xml):
    result = ['<div class="%s">\n' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</div>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_em_class(xml):
    result = ['<em class="%s"><code>' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</code></em>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_entry(xml):
    result = ['<td']
    if 'role' in xml.attrib:
        result.append(' class="%s">\n' % xml.attrib['role'])
    else:
        result.append('>\n')
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</td>\n')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_informaltable(xml):
    result = ['<div class="informaltable"><table class="informaltable"']
    a = xml.attrib
    if 'pgwide' in a and a['pgwide'] == '1':
        result.append(' width="100%"')
    if 'frame' in a and a['frame'] == 'none':
        result.append(' border="0"')
    result.append('>\n')
    convert_inner(xml, result)
    result.append('</table></div>\n')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_itemizedlist(xml):
    result = ['<div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; ">']
    convert_inner(xml, result)
    result.append('</ul></div>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_link(xml):
    # TODO: inline more fixxref functionality
    # TODO: need to build an 'id' map and resolve against internal links too
    linkend = xml.attrib['linkend']
    if linkend in NoLinks:
        linkend = None
    result = []
    if linkend:
        result = ['<!-- GTKDOCLINK HREF="%s" -->' % linkend]
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    if linkend:
        result.append('<!-- /GTKDOCLINK -->')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_listitem(xml):
    result = ['<li class="listitem">']
    convert_inner(xml, result)
    result.append('</li>')
    # is in itemizedlist and there can be no 'text'
    return result


def convert_literal(xml):
    result = ['<code class="%s">' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</code>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_para(xml):
    result = ['<p>']
    if xml.tag != 'para':
        result = ['<p class="%s">' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</p>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_phrase(xml):
    result = ['<span']
    if 'role' in xml.attrib:
        result.append(' class="%s">' % xml.attrib['role'])
    else:
        result.append('>')
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</span>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_programlisting(xml):
    # TODO: encode entities
    result = ['<pre class="programlisting">']
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</pre>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_refsect1(xml):
    # Add a divider between two consequitive refsect2
    def convert_inner(xml, result):
        prev = None
        for child in xml:
            if child.tag == 'refsect2' and prev is not None and prev.tag == child.tag:
                result.append('<hr>\n')
            result.extend(convert_tags.get(child.tag, convert__unknown)(child))
            prev = child
    return convert_refsect(xml, 'h2', convert_inner)


def convert_refsect2(xml):
    return convert_refsect(xml, 'h3')


def convert_refsect3(xml):
    return convert_refsect(xml, 'h4')


def convert_row(xml):
    result = ['<tr>\n']
    convert_inner(xml, result)
    result.append('</tr>\n')
    return result


def convert_span(xml):
    result = ['<span class="%s">' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(xml, result)
    result.append('</span>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_tbody(xml):
    result = ['<tbody>']
    convert_inner(xml, result)
    result.append('</tbody>')
    # is in tgroup and there can be no 'text'
    return result


def convert_tgroup(xml):
    # tgroup does not expand to anything, but the nested colspecs need to
    # be put into a colgroup
    cols = xml.findall('colspec')
    result = []
    if cols:
        result.append('<colgroup>\n')
        for col in cols:
            result.extend(convert_colspec(col))
            xml.remove(col)
        result.append('</colgroup>\n')
    convert_inner(xml, result)
    # is in informaltable and there can be no 'text'
    return result


def convert_ulink(xml):
    result = ['<a class="%s" href="%s">%s</a>' % (xml.tag, xml.attrib['url'], xml.text)]
    if xml.tail:
        result.append(xml.tail)
    return result


convert_tags = {
    'colspec': convert_colspec,
    'entry': convert_entry,
    'function': convert_span,
    'indexterm': convert_ignore,
    'informalexample': convert_div,
    'informaltable': convert_informaltable,
    'itemizedlist': convert_itemizedlist,
    'link': convert_link,
    'listitem': convert_listitem,
    'literal': convert_literal,
    'para': convert_para,
    'parameter': convert_em_class,
    'phrase': convert_phrase,
    'programlisting': convert_programlisting,
    'refsect1': convert_refsect1,
    'refsect2': convert_refsect2,
    'refsect3': convert_refsect3,
    'returnvalue': convert_span,
    'row': convert_row,
    'structfield': convert_em_class,
    'tbody': convert_tbody,
    'tgroup': convert_tgroup,
    'type': convert_span,
    'ulink': convert_ulink,
    'warning': convert_div,
}


def convert(out_dir, files, node):
    """Convert the docbook chunks to a html file."""

    def jinja_convert_refsect1(xml):
        return ''.join(convert_refsect1(xml))

    def jinja_convert_para(xml):
        return ''.join(convert_para(xml))

    logging.info('Writing: %s', node.filename)
    with open(os.path.join(out_dir, node.filename), 'wt') as html:
        if node.name in TEMPLATES:
            # TODO: ideally precompile common xpath exprs once:
            #   func = etree.XPath('//b')
            #   func(xml_node)[0]
            # unused, we can call api :)
            # def lxml_xpath_str0(xml, expr):
            #     return xml.xpath(expr, smart_strings=False)[0]
            #
            # def lxml_xpath(xml, expr):
            #     return xml.xpath(expr)

            template = TEMPLATES[node.name]
            template.globals['convert_refsect1'] = jinja_convert_refsect1
            template.globals['convert_para'] = jinja_convert_para
            params = {
                'xml': node.xml,
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
            elif node.name == 'refsect':
                # TODO: toc params from xml
                # all refsect1 + refsect1/title/text() from xml
                pass

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
