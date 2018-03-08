#!/usr/bin/env python3
# -*- python; coding: utf-8 -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 2018  Stefan Sauer
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

The tool loads the main xml document (<module>-docs.xml) and chunks it
like the xsl-stylesheets would do. For that it resolves all the xml-includes.
Each chunk is converted to htnml using python functions.

In contrast to our previous approach of running gtkdoc-mkhtml + gtkdoc-fixxref,
this tools will replace both without relying on external tools such as xsltproc
and source-highlight.

TODO:
- more chunk converters
- check each docbook tag if it can contain #PCDATA, if not don't check for
  xml.text
- integrate fixxref:
  - as a step, we could run FixHTMLFile() on each output file
  - integrate syntax-highlighing from fixxref
    - maybe handle the combination <informalexample><programlisting> directly
    - switch to http://pygments.org/docs/quickstart/?
  - integrate MakeXRef from fixxref

OPTIONAL:
- minify html: https://pypi.python.org/pypi/htmlmin/

Requirements:
sudo pip3 install anytree lxml

Example invocation:
cd tests/bugs/docs/
../../../gtkdoc-mkhtml2 tester tester-docs.xml
ll db2html
cp html/*.{css,png} db2html/
xdg-open db2html/index.html
meld html db2html

Benchmarking:
cd tests/bugs/docs/;
rm html-build.stamp; time make html-build.stamp
"""

import argparse
import errno
import logging
import os
import sys

from anytree import Node, PreOrderIter
from copy import deepcopy
from lxml import etree

from .fixxref import NoLinks

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
# https://github.com/oreillymedia/HTMLBook/blob/master/htmlbook-xsl/chunk.xsl#L33
CHUNK_PARAMS = {
    'appendix': ChunkParams('app', 'book'),
    'book': ChunkParams('bk'),
    'chapter': ChunkParams('ch', 'book'),
    'index': ChunkParams('ix', 'book'),
    'part': ChunkParams('pt', 'book'),
    'sect1': ChunkParams('s', 'chapter'),
    'section': ChunkParams('s', 'chapter'),
}

TITLE_XPATHS = {
    '_': (etree.XPath('./title'), None),
    'book': (etree.XPath('./bookinfo/title'), None),
    'refentry': (
        etree.XPath('./refmeta/refentrytitle'),
        etree.XPath('./refnamediv/refpurpose')
    ),
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


def get_chunk_titles(node):
    tag = node.tag
    if tag not in TITLE_XPATHS:
        # Use defaults
        (title, subtitle) = TITLE_XPATHS['_']
    else:
        (title, subtitle) = TITLE_XPATHS[tag]

    xml = title(node)[0]
    result = {
        'title': xml.text
    }
    if xml.tag != 'title':
        result['title_tag'] = xml.tag
    else:
        result['title_tag'] = tag

    if subtitle:
        xml = subtitle(node)[0]
        result['subtitle'] = xml.text
        result['subtitle_tag'] = xml.tag
    else:
        result['subtitle'] = None
        result['subtitle_tag'] = None
    return result


def chunk(xml_node, parent=None):
    """Chunk the tree.

    The first time, we're called with parent=None and in that case we return
    the new_node as the root of the tree
    """
    # print('<%s %s>' % (xml_node.tag, xml_node.attrib))
    if xml_node.tag in CHUNK_TAGS:
        if parent:
            # remove the xml-node from the parent
            sub_tree = etree.ElementTree(deepcopy(xml_node)).getroot()
            xml_node.getparent().remove(xml_node)
            xml_node = sub_tree

        title_args = get_chunk_titles(xml_node)
        parent = Node(xml_node.tag, parent=parent, xml=xml_node,
                      filename=gen_chunk_name(xml_node) + '.html',
                      **title_args)
    for child in xml_node:
        chunk(child, parent)

    return parent

# conversion helpers


def escape_entities(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def convert_inner(ctx, xml, result):
    for child in xml:
        result.extend(convert_tags.get(child.tag, convert__unknown)(ctx, child))


def convert_ignore(ctx, xml):
    result = []
    convert_inner(ctx, xml, result)
    return result


def convert_skip(ctx, xml):
    return ['']


missing_tags = {}


def convert__unknown(ctx, xml):
    # don't recurse on subchunks
    if xml.tag in CHUNK_TAGS:
        return []
    # warn only once
    if xml.tag not in missing_tags:
        logging.warning('Add tag converter for "%s"', xml.tag)
        missing_tags[xml.tag] = True
    result = ['<!-- ' + xml.tag + '-->\n']
    convert_inner(ctx, xml, result)
    result.append('<!-- /' + xml.tag + '-->\n')
    return result


def convert_refsect(ctx, xml, h_tag, inner_func=convert_inner):
    result = ['<div class="%s">\n' % xml.tag]
    title = xml.find('title')
    if title is not None:
        if 'id' in xml.attrib:
            result.append('<a name="%s"></a>' % xml.attrib['id'])
        result.append('<%s>%s</%s>' % (h_tag, title.text, h_tag))
        xml.remove(title)
    if xml.text:
        result.append(xml.text)
    inner_func(ctx, xml, result)
    result.append('</div>')
    if xml.tail:
        result.append(xml.tail)
    return result


def xml_get_title(xml):
    title = xml.find('title')
    if title is not None:
        return title.text
    else:
        # TODO(ensonic): any way to get the file (inlcudes) too?
        logging.warning('%s: Expected title tag under "%s %s"', xml.sourceline, xml.tag, str(xml.attrib))
        return ''


# docbook tags

def convert_bookinfo(ctx, xml):
    result = ['<div class="titlepage">']
    for releaseinfo in xml.findall('releaseinfo'):
        result.extend(convert_para(ctx, releaseinfo))
    result.append("""<hr>
</div>""")
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_colspec(ctx, xml):
    result = ['<col']
    a = xml.attrib
    if 'colname' in a:
        result.append(' class="%s"' % a['colname'])
    if 'colwidth' in a:
        result.append(' width="%s"' % a['colwidth'])
    result.append('>\n')
    # is in tgroup and there can be no 'text'
    return result


def convert_div(ctx, xml):
    result = ['<div class="%s">\n' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(ctx, xml, result)
    result.append('</div>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_em_class(ctx, xml):
    result = ['<em class="%s"><code>' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(ctx, xml, result)
    result.append('</code></em>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_entry(ctx, xml):
    result = ['<td']
    if 'role' in xml.attrib:
        result.append(' class="%s">' % xml.attrib['role'])
    else:
        result.append('>')
    if xml.text:
        result.append(xml.text)
    convert_inner(ctx, xml, result)
    result.append('</td>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_indexdiv(ctx, xml):
    title_tag = xml.find('title')
    title = title_tag.text
    xml.remove(title_tag)
    result = [
        '<a name="idx%s"></a><h3 class="title">%s</h3>' % (title, title)
    ]
    convert_inner(ctx, xml, result)
    return result


def convert_informaltable(ctx, xml):
    result = ['<div class="informaltable"><table class="informaltable"']
    a = xml.attrib
    if 'pgwide' in a and a['pgwide'] == '1':
        result.append(' width="100%"')
    if 'frame' in a and a['frame'] == 'none':
        result.append(' border="0"')
    result.append('>\n')
    convert_inner(ctx, xml, result)
    result.append('</table></div>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_itemizedlist(ctx, xml):
    result = ['<div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; ">']
    convert_inner(ctx, xml, result)
    result.append('</ul></div>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_link(ctx, xml):
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
    convert_inner(ctx, xml, result)
    if linkend:
        result.append('<!-- /GTKDOCLINK -->')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_listitem(ctx, xml):
    result = ['<li class="listitem">']
    convert_inner(ctx, xml, result)
    result.append('</li>')
    # is in itemizedlist and there can be no 'text'
    return result


def convert_literal(ctx, xml):
    result = ['<code class="%s">' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(ctx, xml, result)
    result.append('</code>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_para(ctx, xml):
    result = ['<p>']
    if xml.tag != 'para':
        result = ['<p class="%s">' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(ctx, xml, result)
    result.append('</p>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_phrase(ctx, xml):
    result = ['<span']
    if 'role' in xml.attrib:
        result.append(' class="%s">' % xml.attrib['role'])
    else:
        result.append('>')
    if xml.text:
        result.append(xml.text)
    convert_inner(ctx, xml, result)
    result.append('</span>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_primaryie(ctx, xml):
    result = ['<dt>']
    convert_inner(ctx, xml, result)
    result.append('</dt>\n<dd></dd>\n')
    return result


def convert_programlisting(ctx, xml):
    result = ['<pre class="programlisting">']
    if xml.text:
        result.append(escape_entities(xml.text))
    convert_inner(ctx, xml, result)
    result.append('</pre>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_refsect1(ctx, xml):
    # Add a divider between two consequitive refsect2
    def convert_inner(ctx, xml, result):
        prev = None
        for child in xml:
            if child.tag == 'refsect2' and prev is not None and prev.tag == child.tag:
                result.append('<hr>\n')
            result.extend(convert_tags.get(child.tag, convert__unknown)(ctx, child))
            prev = child
    return convert_refsect(ctx, xml, 'h2', convert_inner)


def convert_refsect2(ctx, xml):
    return convert_refsect(ctx, xml, 'h3')


def convert_refsect3(ctx, xml):
    return convert_refsect(ctx, xml, 'h4')


def convert_row(ctx, xml):
    result = ['<tr>\n']
    convert_inner(ctx, xml, result)
    result.append('</tr>\n')
    return result


def convert_span(ctx, xml):
    result = ['<span class="%s">' % xml.tag]
    if xml.text:
        result.append(xml.text)
    convert_inner(ctx, xml, result)
    result.append('</span>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_tbody(ctx, xml):
    result = ['<tbody>']
    convert_inner(ctx, xml, result)
    result.append('</tbody>')
    # is in tgroup and there can be no 'text'
    return result


def convert_tgroup(ctx, xml):
    # tgroup does not expand to anything, but the nested colspecs need to
    # be put into a colgroup
    cols = xml.findall('colspec')
    result = []
    if cols:
        result.append('<colgroup>\n')
        for col in cols:
            result.extend(convert_colspec(ctx, col))
            xml.remove(col)
        result.append('</colgroup>\n')
    convert_inner(ctx, xml, result)
    # is in informaltable and there can be no 'text'
    return result


def convert_ulink(ctx, xml):
    result = ['<a class="%s" href="%s">%s</a>' % (xml.tag, xml.attrib['url'], xml.text)]
    if xml.tail:
        result.append(xml.tail)
    return result


# TODO(ensonic): turn into class with converters as functions and ctx as self
convert_tags = {
    'bookinfo': convert_bookinfo,
    'colspec': convert_colspec,
    'entry': convert_entry,
    'function': convert_span,
    'indexdiv': convert_indexdiv,
    'indexentry': convert_ignore,
    'indexterm': convert_skip,
    'informalexample': convert_div,
    'informaltable': convert_informaltable,
    'itemizedlist': convert_itemizedlist,
    'link': convert_link,
    'listitem': convert_listitem,
    'literal': convert_literal,
    'para': convert_para,
    'parameter': convert_em_class,
    'phrase': convert_phrase,
    'primaryie': convert_primaryie,
    'programlisting': convert_programlisting,
    'releaseinfo': convert_para,
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

# conversion helpers

HTML_HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>%s</title>
%s<link rel="stylesheet" href="style.css" type="text/css">
</head>
<body bgcolor="white" text="black" link="#0000FF" vlink="#840084" alink="#0000FF">
"""


def generate_head_links(ctx):
    n = ctx['nav_home']
    result = [
        '<link rel="home" href="%s" title="%s">\n' % (n.filename, n.title)
    ]
    if 'nav_up' in ctx:
        n = ctx['nav_up']
        result.append('<link rel="up" href="%s" title="%s">\n' % (n.filename, n.title))
    if 'nav_prev' in ctx:
        n = ctx['nav_prev']
        result.append('<link rel="prev" href="%s" title="%s">\n' % (n.filename, n.title))
    if 'nav_next' in ctx:
        n = ctx['nav_next']
        result.append('<link rel="next" href="%s" title="%s">\n' % (n.filename, n.title))
    return ''.join(result)


def generate_nav_links(ctx):
    n = ctx['nav_home']
    result = [
        '<td><a accesskey="h" href="%s"><img src="home.png" width="16" height="16" border="0" alt="Home"></a></td>' % n.filename
    ]
    if 'nav_up' in ctx:
        n = ctx['nav_up']
        result.append(
            '<td><a accesskey="u" href="%s"><img src="up.png" width="16" height="16" border="0" alt="Up"></a></td>' % n.filename)
    else:
        result.append('<td><img src="up-insensitive.png" width="16" height="16" border="0"></td>')
    if 'nav_prev' in ctx:
        n = ctx['nav_prev']
        result.append(
            '<td><a accesskey="p" href="%s"><img src="left.png" width="16" height="16" border="0" alt="Prev"></a></td>' % n.filename)
    else:
        result.append('<td><img src="left-insensitive.png" width="16" height="16" border="0"></td>')
    if 'nav_next' in ctx:
        n = ctx['nav_next']
        result.append(
            '<td><a accesskey="n" href="%s"><img src="right.png" width="16" height="16" border="0" alt="Next"></a></td>' % n.filename)
    else:
        result.append('<td><img src="right-insensitive.png" width="16" height="16" border="0"></td>')

    return ''.join(result)


def generate_toc(ctx, node):
    result = []
    for c in node.children:
        # TODO: urlencode the filename: urllib.parse.quote_plus()
        result.append('<dt><span class="%s"><a href="%s">%s</a></span>\n' % (
            c.title_tag, c.filename, c.title))
        if c.subtitle:
            result.append('<span class="%s"> — %s</span>' % (c.subtitle_tag, c.subtitle))
        result.append('</dt>\n')
        if c.children:
            result.append('<dd><dl>')
            result.extend(generate_toc(ctx, c))
            result.append('</dl></dd>')
    return result


def generate_basic_nav(ctx):
    return """<table class="navigation" id="top" width="100%%" cellpadding="2" cellspacing="5">
  <tr valign="middle">
    <td width="100%%" align="left" class="shortcuts"></td>
    %s
  </tr>
</table>
    """ % generate_nav_links(ctx)


def generate_index_nav(ctx, indexdivs):
    ix_nav = []
    for s in indexdivs:
        title = xml_get_title(s)
        ix_nav.append('<a class="shortcut" href="#idx%s">%s</a>' % (title, title))

    return """<table class="navigation" id="top" width="100%%" cellpadding="2" cellspacing="5">
  <tr valign="middle">
    <td width="100%%" align="left" class="shortcuts">
      <span id="nav_index">
        %s
      </span>
    </td>
    %s
  </tr>
</table>
    """ % ('\n<span class="dim">|</span>\n'.join(ix_nav), generate_nav_links(ctx))


def generate_refentry_nav(ctx, refsect1s, result):
    result.append("""<table class="navigation" id="top" width="100%%" cellpadding="2" cellspacing="5">
  <tr valign="middle">
    <td width="100%%" align="left" class="shortcuts">
      <a href="#" class="shortcut">Top</a>""")

    for s in refsect1s:
        # don't list TOC sections (role="xxx_proto")
        if s.attrib.get('role', '').endswith("_proto"):
            continue

        title = xml_get_title(s)
        result.append("""
          <span id="nav_description">
            <span class="dim">|</span> 
            <a href="#%s" class="shortcut">%s</a>
          </span>""" % (s.attrib['id'], title))
    result.append("""
    </td>
    %s
  </tr>
</table>
""" % generate_nav_links(ctx))


def get_id(node):
    xml = node.xml
    node_id = xml.attrib.get('id', None)
    if node_id:
        return node_id

    logging.warning('%d: No "id" attribute on "%s"', xml.sourceline, xml.tag)
    ix = []
    # Generate the 'id'. We need to walk up the xml-tree and check the positions
    # for each sibling.
    parent = xml.getparent()
    while parent is not None:
        children = parent.getchildren()
        ix.insert(0, str(children.index(xml) + 1))
        xml = parent
        parent = xml.getparent()
    # logging.warning('%s: id indexes: %s', node.filename, str(ix))
    return 'id-1.' + '.'.join(ix)


# docbook chunks


def convert_book(ctx):
    node = ctx['node']
    result = [
        HTML_HEADER % (node.title, generate_head_links(ctx)),
        """<table class="navigation" id="top" width="100%%" cellpadding="2" cellspacing="0">
    <tr><th valign="middle"><p class="title">%s</p></th></tr>
</table>
<div class="book">
""" % node.title
    ]
    bookinfo = node.xml.findall('bookinfo')[0]
    result.extend(convert_bookinfo(ctx, bookinfo))
    result.append("""<div class="toc">
  <dl class="toc">
""")
    result.extend(generate_toc(ctx, node.root))
    result.append("""</dl>
</div>
</div>
</body>
</html>""")
    return result


def convert_chapter(ctx):
    node = ctx['node']
    result = [
        HTML_HEADER % (node.title + ": " + node.root.title, generate_head_links(ctx)),
        generate_basic_nav(ctx),
        '<div class="chapter">',
    ]
    title = node.xml.find('title')
    if title is not None:
        result.append('<div class="titlepage"><h1 class="title"><a name="%s"></a>%s</h1></div>' % (
            get_id(node), title.text))
        node.xml.remove(title)
    convert_inner(ctx, node.xml, result)
    result.append("""<div class="toc">
  <dl class="toc">
""")
    result.extend(generate_toc(ctx, node))
    result.append("""</dl>
</div>
</div>
</body>
</html>""")
    return result


def convert_index(ctx):
    node = ctx['node']
    node_id = get_id(node)
    # Get all indexdivs under indexdiv
    indexdivs = node.xml.find('indexdiv').findall('indexdiv')

    result = [
        HTML_HEADER % (node.title + ": " + node.root.title, generate_head_links(ctx)),
        generate_index_nav(ctx, indexdivs),
        """<div class="index">
<div class="titlepage"><h1 class="title">
<a name="%s"></a>%s</h1>
</div>""" % (node_id, node.title)
    ]
    for i in indexdivs:
        result.extend(convert_indexdiv(ctx, i))
    result.append("""</div>
</body>
</html>""")
    return result


def convert_refentry(ctx):
    node = ctx['node']
    node_id = get_id(node)
    refsect1s = node.xml.findall('refsect1')

    result = [
        HTML_HEADER % (node.title + ": " + node.root.title, generate_head_links(ctx))
    ]
    generate_refentry_nav(ctx, refsect1s, result)
    result.append("""
<div class="refentry">
<a name="%s"></a>
<div class="refnamediv">
  <table width="100%%"><tr>
    <td valign="top">
      <h2><span class="refentrytitle"><a name="%s.top_of_page"></a>%s</span></h2>
      <p>%s — module for gtk-doc unit test</p>
    </td>
    <td class="gallery_image" valign="top" align="right"></td>
  </tr></table>
</div>
""" % (node_id, node_id, node.title, node.title))

    for s in refsect1s:
        result.extend(convert_refsect1(ctx, s))
    result.append("""</div>
</body>
</html>""")
    return result


# TODO(ensonic): turn into class with converters as functions and ctx as self
convert_chunks = {
    'book': convert_book,
    'chapter': convert_chapter,
    'index': convert_index,
    'refentry': convert_refentry,
}


def generate_nav_nodes(files, node):
    nav = {
        'nav_home': node.root,
    }
    # nav params: up, prev, next
    if node.parent:
        nav['nav_up'] = node.parent
    ix = files.index(node)
    if ix > 0:
        nav['nav_prev'] = files[ix - 1]
    if ix < len(files) - 1:
        nav['nav_next'] = files[ix + 1]
    return nav


def convert(out_dir, files, node):
    """Convert the docbook chunks to a html file.

    Args:
      out_dir: already created output dir
      files: list of nodes in the tree in pre-order
      node: current tree node
    """

    logging.info('Writing: %s', node.filename)
    with open(os.path.join(out_dir, node.filename), 'wt') as html:
        ctx = {
            'files': files,
            'node': node,
        }
        ctx.update(generate_nav_nodes(files, node))

        if node.name in convert_chunks:
            for line in convert_chunks[node.name](ctx):
                html.write(line)
        else:
            logging.warning('Add converter/template for "%s"', node.name)


def create_devhelp2_toc(node):
    result = []
    for c in node.children:
        if c.children:
            result.append('<sub name="%s" link="%s">\n' % (c.title, c.filename))
            result.extend(create_devhelp2_toc(c))
            result.append('</sub>\n')
        else:
            result.append('<sub name="%s" link="%s"/>\n' % (c.title, c.filename))
    return result


def create_devhelp2_condition_attribs(node):
    if 'condition' in node.attrib:
        # condition -> since, deprecated, ... (separated with '|')
        cond = node.attrib['condition'].replace('"', '&quot;').split('|')
        return' ' + ' '.join(['%s="%s"' % tuple(c.split(':', 1)) for c in cond])
    else:
        return ''


def create_devhelp2_refsect2_keyword(node, base_link):
    return'    <keyword type="%s" name="%s" link="%s"%s/>\n' % (
        node.attrib['role'], xml_get_title(node), base_link + node.attrib['id'],
        create_devhelp2_condition_attribs(node))


def create_devhelp2_refsect3_keyword(node, base_link, title, name):
    return'    <keyword type="%s" name="%s" link="%s"%s/>\n' % (
        node.attrib['role'], title, base_link + name,
        create_devhelp2_condition_attribs(node))


def create_devhelp2(out_dir, module, xml, files):
    with open(os.path.join(out_dir, module + '.devhelp2'), 'wt') as idx:
        bookinfo_nodes = xml.xpath('/book/bookinfo')
        title = ''
        if bookinfo_nodes is not None:
            bookinfo = bookinfo_nodes[0]
            title = bookinfo.xpath('./title/text()')[0]
            online_url = bookinfo.xpath('./releaseinfo/ulink[@role="online-location"]/@url')[0]
            # TODO: support author too (see devhelp2.xsl)
        # TODO: fixxref uses '--src-lang' to set the language
        result = [
            """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<book xmlns="http://www.devhelp.net/book" title="%s" link="index.html" author="" name="%s" version="2" language="c" online="%s">
  <chapters>
""" % (title, module, online_url)
        ]
        # toc
        result.extend(create_devhelp2_toc(files[0].root))
        result.append("""  </chapters>
  <functions>
""")
        # keywords from all refsect2 and refsect3
        refsect2 = etree.XPath('//refsect2[@role]')
        refsect3_enum = etree.XPath('refsect3[@role="enum_members"]/informaltable/tgroup/tbody/row[@role="constant"]')
        refsect3_enum_details = etree.XPath('entry[@role="enum_member_name"]/para')
        refsect3_struct = etree.XPath('refsect3[@role="struct_members"]/informaltable/tgroup/tbody/row[@role="member"]')
        refsect3_struct_details = etree.XPath('entry[@role="struct_member_name"]/para/structfield')
        for node in files:
            base_link = node.filename + '#'
            refsect2_nodes = refsect2(node.xml)
            for refsect2_node in refsect2_nodes:
                result.append(create_devhelp2_refsect2_keyword(refsect2_node, base_link))
                refsect3_nodes = refsect3_enum(refsect2_node)
                for refsect3_node in refsect3_nodes:
                    details_node = refsect3_enum_details(refsect3_node)[0]
                    name = details_node.attrib['id']
                    result.append(create_devhelp2_refsect3_keyword(refsect3_node, base_link, details_node.text, name))
                refsect3_nodes = refsect3_struct(refsect2_node)
                for refsect3_node in refsect3_nodes:
                    details_node = refsect3_struct_details(refsect3_node)[0]
                    name = details_node.attrib['id']
                    result.append(create_devhelp2_refsect3_keyword(refsect3_node, base_link, name, name))

        result.append("""  </functions>
</book>
""")
        for line in result:
            idx.write(line)


def main(module, index_file):
    tree = etree.parse(index_file)
    tree.xinclude()

    dir_name = os.path.dirname(index_file)

    # for testing: dump to output file
    # out_file = os.path.join(dir_name, 'db2html.xml')
    # tree.write(out_file)

    # TODO: rename to 'html' later on
    # - right now in mkhtml, the dir is created by the Makefile and mkhtml
    #   outputs into the working directory
    out_dir = os.path.join(dir_name, 'db2html')
    try:
        os.mkdir(out_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # We do multiple passes:
    # 1) recursively walk the tree and chunk it into a python tree so that we
    #   can generate navigation and link tags.
    # TODO: also collect all 'id' attributes on the way and build map of
    #   id:rel-link (in fixxref it is called Links[])
    files = chunk(tree.getroot())
    files = list(PreOrderIter(files))
    # 2) create a xxx.devhelp2 file, do this before 3), since we modify the tree
    create_devhelp2(out_dir, module, tree.getroot(), files)
    # 3) iterate the tree and output files
    # TODO: use multiprocessing
    for node in files:
        convert(out_dir, files, node)


def run(options):
    logging.info('options: %s', str(options.__dict__))
    module = options.args[0]
    document = options.args[1]
    sys.exit(main(module, document))
