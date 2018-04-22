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

"""Generate html from docbook

The tool loads the main xml document (<module>-docs.xml) and chunks it
like the xsl-stylesheets would do. For that it resolves all the xml-includes.
Each chunk is converted to html using python functions.

In contrast to our previous approach of running gtkdoc-mkhtml + gtkdoc-fixxref,
this tools will replace both without relying on external tools such as xsltproc
and source-highlight.

Please note, that we're not aiming for complete docbook-xml support. All tags
used in the generated xml are of course handled. More tags used in handwritten
xml can be easilly supported, but for some combinations of tags we prefer
simplicity.

TODO:
- tag converters:
  - inside 'footnote' one can have many tags, we only handle 'para'/'simpara'
  - inside 'inlinemediaobject'/'mediaobject' a 'textobject' becomes the 'alt'
    attr on the <img> tag of the 'imageobject'
  - handle 'label' attributes on part/chapter/section-types
    - the titles will have a generated prefix, such as 'Part I:'
      (locale dependent)
    - in the toc it would only be the label: 'I.'
  - 'link' seems to add a 'title' attr to 'a' if the target has a title.
    - we're using fixxref.MakeXRef to generate the 'a' tag, we could pass the
      title with a default value of "" there to inject it
    - we might need to split this a bit to first run the 'id' transform logic
      and then do the linking.
    - initially we could generate this as needed (we need to run the xpath on
      each of the chunks though
  - handle the 'xref' tag, this also need the title + the type of the target
- check each docbook tag if it can contain #PCDATA, if not don't check for
  xml.text
- consider some perf-warnings flag
  - see 'No "id" attribute on'

OPTIONAL:
- minify html: https://pypi.python.org/pypi/htmlmin/

Requirements:
sudo pip3 install anytree lxml pygments

Example invocation:
cd tests/bugs/docs/
../../../gtkdoc-mkhtml2 tester tester-docs.xml
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
import shutil
import sys

from anytree import Node, PreOrderIter
from copy import deepcopy
from glob import glob
from lxml import etree
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import HtmlFormatter

from . import config, fixxref

# pygments setup
# lazily constructed lexer cache
LEXERS = {
    'c': CLexer()
}
HTML_FORMATTER = HtmlFormatter(nowrap=True)


class ChunkParams(object):
    def __init__(self, prefix, parent=None, min_idx=0):
        self.prefix = prefix
        self.parent = parent
        self.min_idx = min_idx
        self.idx = 1


DONT_CHUNK = float('inf')
# docbook-xsl defines the chunk tags here.
# http://www.sagehill.net/docbookxsl/Chunking.html#GeneratedFilenames
# https://github.com/oreillymedia/HTMLBook/blob/master/htmlbook-xsl/chunk.xsl#L33
# If not defined, we can just create an example without an 'id' attr and see
# docbook xsl does.
#
# For toc levels see http://www.sagehill.net/docbookxsl/TOCcontrol.html
# TODO: this list has also a flag that controls wheter we add the
# 'Table of Contents' heading in convert_chunk_with_toc()
CHUNK_PARAMS = {
    'appendix': ChunkParams('app', 'book'),
    'book': ChunkParams('bk'),
    'chapter': ChunkParams('ch', 'book'),
    'glossary': ChunkParams('go', 'book'),
    'index': ChunkParams('ix', 'book'),
    'part': ChunkParams('pt', 'book'),
    'preface': ChunkParams('pr', 'book'),
    'refentry': ChunkParams('re', 'book'),
    'reference': ChunkParams('rn', 'book'),
    'sect1': ChunkParams('s', 'chapter', 1),
    'section': ChunkParams('s', 'chapter', 1),
    'sect2': ChunkParams('s', 'sect1', DONT_CHUNK),
    'sect3': ChunkParams('s', 'sect2', DONT_CHUNK),
    'sect4': ChunkParams('s', 'sect3', DONT_CHUNK),
    'sect5': ChunkParams('s', 'sect4', DONT_CHUNK),
}
# TAGS we don't support:
# 'article', 'bibliography', 'colophon', 'set', 'setindex'

TITLE_XPATHS = {
    '_': (etree.XPath('./title'), None),
    'book': (etree.XPath('./bookinfo/title'), None),
    'refentry': (
        etree.XPath('./refmeta/refentrytitle'),
        etree.XPath('./refnamediv/refpurpose')
    ),
}

ID_XPATH = etree.XPath('//@id')

GLOSSENTRY_XPATH = etree.XPath('//glossentry')
glossary = {}

footnote_idx = 1


def gen_chunk_name(node, chunk_params):
    """Generate a chunk file name

    This is either based on the id or on the position in the doc. In the latter
    case it uses a prefix from CHUNK_PARAMS and a sequence number for each chunk
    type.
    """
    if 'id' in node.attrib:
        return node.attrib['id']

    name = ('%s%02d' % (chunk_params.prefix, chunk_params.idx))
    chunk_params.idx += 1

    # handle parents to make names of nested tags like in docbook
    # - we only need to prepend the parent if there are > 1 of them in the
    #   xml. None, the parents we have are not sufficient, e.g. 'index' can
    #   be in 'book' or 'part' or ... Maybe we can track the chunk_parents
    #   when we chunk explicitly and on each level maintain the 'idx'
    # while chunk_params.parent:
    #     parent = chunk_params.parent
    #     if parent not in CHUNK_PARAMS:
    #         break;
    #     chunk_params = CHUNK_PARAMS[parent]
    #     name = ('%s%02d' % (chunk_params.prefix, chunk_params.idx)) + name

    logging.info('Gen chunk name: "%s"', name)
    return name


def get_chunk_titles(module, node):
    tag = node.tag
    if tag not in TITLE_XPATHS:
        # Use defaults
        (title, subtitle) = TITLE_XPATHS['_']
    else:
        (title, subtitle) = TITLE_XPATHS[tag]

    ctx = {
        'module': module,
    }
    result = {
        'title': None,
        'title_tag': None,
        'subtitle': None,
        'subtitle_tag': None
    }
    res = title(node)
    if res:
        xml = res[0]
        result['title'] = ''.join(convert_title(ctx, xml))
        if xml.tag != 'title':
            result['title_tag'] = xml.tag
        else:
            result['title_tag'] = tag

    if subtitle:
        res = subtitle(node)
        if res:
            xml = res[0]
            result['subtitle'] = ''.join(convert_title(ctx, xml))
            result['subtitle_tag'] = xml.tag
    return result


def chunk(xml_node, module, depth=0, idx=0, parent=None):
    """Chunk the tree.

    The first time, we're called with parent=None and in that case we return
    the new_node as the root of the tree. For each tree-node we generate a
    filename and process the children.
    """
    tag = xml_node.tag
    chunk_params = CHUNK_PARAMS.get(tag)
    if chunk_params:
        title_args = get_chunk_titles(module, xml_node)
        chunk_name = gen_chunk_name(xml_node, chunk_params)

        # check idx to handle 'sect1'/'section' special casing and title-only
        # segments
        if idx >= chunk_params.min_idx:
            logging.info('chunk tag: "%s"[%d]', tag, idx)
            if parent:
                # remove the xml-node from the parent
                sub_tree = etree.ElementTree(deepcopy(xml_node)).getroot()
                xml_node.getparent().remove(xml_node)
                xml_node = sub_tree

            parent = Node(tag, parent=parent, xml=xml_node, depth=depth,
                          idx=idx,
                          filename=chunk_name + '.html', anchor=None,
                          **title_args)
        else:
            parent = Node(tag, parent=parent, xml=xml_node, depth=depth,
                          idx=idx,
                          filename=parent.filename, anchor='#' + chunk_name,
                          **title_args)

        depth += 1
        idx = 0
        for child in xml_node:
            chunk(child, module, depth, idx, parent)
            if child.tag in CHUNK_PARAMS:
                idx += 1

    return parent


def add_id_links(files, links):
    for node in files:
        chunk_name = node.filename[:-5]
        chunk_base = node.filename + '#'
        for attr in ID_XPATH(node.xml):
            if attr == chunk_name:
                links[attr] = node.filename
            else:
                links[attr] = chunk_base + attr


def build_glossary(files):
    for node in files:
        if node.xml.tag != 'glossary':
            continue
        for term in GLOSSENTRY_XPATH(node.xml):
            # TODO: there can be all kind of things in a glossary. This only supports
            # what we commonly use
            key = etree.tostring(term.find('glossterm'), method="text", encoding=str).strip()
            value = etree.tostring(term.find('glossdef'), method="text", encoding=str).strip()
            glossary[key] = value
            # logging.debug('glosentry: %s:%s', key, value)


# conversion helpers


def convert_inner(ctx, xml, result):
    for child in xml:
        result.extend(convert_tags.get(child.tag, convert__unknown)(ctx, child))


def convert_ignore(ctx, xml):
    result = []
    convert_inner(ctx, xml, result)
    return result


def convert_skip(ctx, xml):
    return ['']


def append_text(text, result):
    if text and text.strip():
        result.append(text.replace('<', '&lt;').replace('>', '&gt;'))


missing_tags = {}


def convert__unknown(ctx, xml):
    # don't recurse on subchunks
    if xml.tag in CHUNK_PARAMS:
        return []
    if isinstance(xml, etree._Comment):
        return ['<!-- ' + xml.text + '-->\n']
    else:
        # warn only once
        if xml.tag not in missing_tags:
            logging.warning('Add tag converter for "%s"', xml.tag)
            missing_tags[xml.tag] = True
        result = ['<!-- ' + xml.tag + '-->\n']
        convert_inner(ctx, xml, result)
        result.append('<!-- /' + xml.tag + '-->\n')
        return result


def convert_sect(ctx, xml, h_tag, inner_func=convert_inner):
    result = ['<div class="%s">\n' % xml.tag]
    title = xml.find('title')
    if title is not None:
        if 'id' in xml.attrib:
            result.append('<a name="%s"></a>' % xml.attrib['id'])
        result.append('<%s>%s</%s>' % (h_tag, title.text, h_tag))
        xml.remove(title)
    append_text(xml.text, result)
    inner_func(ctx, xml, result)
    result.append('</div>')
    append_text(xml.tail, result)
    return result


def xml_get_title(ctx, xml):
    title_tag = xml.find('title')
    if title_tag is not None:
        return ''.join(convert_title(ctx, title_tag))
    else:
        # TODO(ensonic): any way to get the file (inlcudes) too?
        logging.warning('%s: Expected title tag under "%s %s"', xml.sourceline, xml.tag, str(xml.attrib))
        return ''


# docbook tags


def convert_abstract(ctx, xml):
    result = ["""<div class="abstract">
    <p class="title"><b>Abstract</b></p>"""]
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</div>')
    append_text(xml.tail, result)
    return result


def convert_acronym(ctx, xml):
    key = xml.text
    title = glossary.get(key, '')
    # TODO: print a sensible warning if missing
    result = ['<acronym title="%s"><span class="acronym">%s</span></acronym>' % (title, key)]
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_anchor(ctx, xml):
    return ['<a name="%s"></a>' % xml.attrib['id']]


def convert_bookinfo(ctx, xml):
    result = ['<div class="titlepage">']
    convert_inner(ctx, xml, result)
    result.append("""<hr>
</div>""")
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_blockquote(ctx, xml):
    result = ['<div class="blockquote">\n<blockquote class="blockquote">']
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</blockquote>\n</div>')
    append_text(xml.tail, result)
    return result


def convert_code(ctx, xml):
    result = ['<code class="%s">' % xml.tag]
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</code>')
    append_text(xml.tail, result)
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


def convert_command(ctx, xml):
    result = ['<strong class="userinput"><code>']
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</code></strong>')
    append_text(xml.tail, result)
    return result


def convert_corpauthor(ctx, xml):
    result = ['<div><h3 class="corpauthor">\n']
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</h3></div>\n')
    append_text(xml.tail, result)
    return result


def convert_div(ctx, xml):
    result = ['<div class="%s">\n' % xml.tag]
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</div>')
    append_text(xml.tail, result)
    return result


def convert_emphasis(ctx, xml):
    result = ['<span class="emphasis"><em>']
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</em></span>')
    append_text(xml.tail, result)
    return result


def convert_em_class(ctx, xml):
    result = ['<em class="%s"><code>' % xml.tag]
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</code></em>')
    append_text(xml.tail, result)
    return result


def convert_entry(ctx, xml):
    entry_type = ctx['table.entry']
    result = ['<' + entry_type]
    if 'role' in xml.attrib:
        result.append(' class="%s"' % xml.attrib['role'])
    if 'morerows' in xml.attrib:
        result.append(' rowspan="%s"' % (1 + int(xml.attrib['morerows'])))
    result.append('>')
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</' + entry_type + '>')
    append_text(xml.tail, result)
    return result


def convert_footnote(ctx, xml):
    footnotes = ctx.get('footnotes', [])
    # footnotes idx is not per page, but per doc
    global footnote_idx
    idx = footnote_idx
    footnote_idx += 1

    # need a pair of ids for each footnote (docbook generates different ids)
    this_id = 'footnote-%d' % idx
    that_id = 'ftn.' + this_id

    inner = ['<div id="%s" class="footnote">' % that_id]
    inner.append('<p><a href="#%s" class="para"><sup class="para">[%d] </sup></a>' % (
        this_id, idx))
    # TODO(ensonic): this can contain all kind of tags, if we convert them we'll
    # get double nested paras :/.
    # convert_inner(ctx, xml, inner)
    para = xml.find('para')
    if para is None:
        para = xml.find('simpara')
    if para is not None:
        inner.append(para.text)
    else:
        logging.warning('%s: Unhandled footnote content: %s', xml.sourceline,
                        etree.tostring(xml, method="text", encoding=str).strip())
    inner.append('</p></div>')
    footnotes.append(inner)
    ctx['footnotes'] = footnotes
    return ['<a href="#%s" class="footnote" name="%s"><sup class="footnote">[%s]</sup></a>' % (
        that_id, this_id, idx)]


def convert_formalpara(ctx, xml):
    result = None
    title_tag = xml.find('title')
    result = ['<p><b>%s</b>' % title_tag.text]
    para_tag = xml.find('para')
    append_text(para_tag.text, result)
    convert_inner(ctx, para_tag, result)
    append_text(para_tag.tail, result)
    result.append('</p>')
    append_text(xml.tail, result)
    return result


def convert_glossdef(ctx, xml):
    result = ['<dd class="glossdef">']
    convert_inner(ctx, xml, result)
    result.append('</dd>\n')
    return result


def convert_glossdiv(ctx, xml):
    title_tag = xml.find('title')
    title = title_tag.text
    xml.remove(title_tag)
    result = [
        '<a name="gls%s"></a><h3 class="title">%s</h3>' % (title, title)
    ]
    convert_inner(ctx, xml, result)
    return result


def convert_glossentry(ctx, xml):
    result = []
    convert_inner(ctx, xml, result)
    return result


def convert_glossterm(ctx, xml):
    glossid = ''
    text = ''
    anchor = xml.find('anchor')
    if anchor is not None:
        glossid = anchor.attrib.get('id', '')
        text += anchor.tail or ''
    text += xml.text or ''
    if glossid == '':
        glossid = 'glossterm-' + text
    return [
        '<dt><span class="glossterm"><a name="%s"></a>%s</span></dt>' % (
            glossid, text)
    ]


def convert_imageobject(ctx, xml):
    imagedata = xml.find('imagedata')
    if imagedata is not None:
        # TODO(ensonic): warn on missing fileref attr?
        return ['<img src="%s">' % imagedata.attrib.get('fileref', '')]
    else:
        return []


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


def convert_inlinegraphic(ctx, xml):
    # TODO(ensonic): warn on missing fileref attr?
    return ['<img src="%s">' % xml.attrib.get('fileref', '')]


def convert_itemizedlist(ctx, xml):
    result = ['<div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; ">']
    convert_inner(ctx, xml, result)
    result.append('</ul></div>')
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_link(ctx, xml):
    linkend = xml.attrib['linkend']
    if linkend in fixxref.NoLinks:
        linkend = None
    result = []
    if linkend:
        link_text = []
        append_text(xml.text, link_text)
        convert_inner(ctx, xml, link_text)
        # TODO: fixxref does some weird checks in xml.text
        result = [fixxref.MakeXRef(ctx['module'], '', 0, linkend, ''.join(link_text))]
    else:
        append_text(xml.text, result)
        convert_inner(ctx, xml, result)
    append_text(xml.tail, result)
    return result


def convert_listitem(ctx, xml):
    result = ['<li class="listitem">']
    convert_inner(ctx, xml, result)
    result.append('</li>')
    # is in itemizedlist and there can be no 'text'
    return result


def convert_literallayout(ctx, xml):
    result = ['<div class="literallayout"><p><br>\n']
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</p></div>')
    append_text(xml.tail, result)
    return result


def convert_orderedlist(ctx, xml):
    result = ['<div class="orderedlist"><ol class="orderedlist" type="1">']
    convert_inner(ctx, xml, result)
    result.append('</ol></div>')
    append_text(xml.tail, result)
    return result


def convert_para(ctx, xml):
    result = []
    if 'id' in xml.attrib:
        result.append('<a name="%s"></a>' % xml.attrib['id'])
    if 'role' in xml.attrib:
        result.append('<p class="%s">' % xml.attrib['role'])
    else:
        result.append('<p>')
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</p>')
    append_text(xml.tail, result)
    return result


def convert_para_like(ctx, xml):
    result = []
    if 'id' in xml.attrib:
        result.append('<a name="%s"></a>' % xml.attrib['id'])
    result.append('<p class="%s">' % xml.tag)
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</p>')
    append_text(xml.tail, result)
    return result


def convert_phrase(ctx, xml):
    result = ['<span']
    if 'role' in xml.attrib:
        result.append(' class="%s">' % xml.attrib['role'])
    else:
        result.append('>')
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</span>')
    append_text(xml.tail, result)
    return result


def convert_primaryie(ctx, xml):
    result = ['<dt>\n']
    convert_inner(ctx, xml, result)
    result.append('\n</dt>\n<dd></dd>\n')
    return result


def convert_pre(ctx, xml):
    result = ['<pre class="%s">\n' % xml.tag]
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</pre>')
    append_text(xml.tail, result)
    return result


def convert_programlisting(ctx, xml):
    result = []
    if xml.attrib.get('role', '') == 'example':
        if xml.text:
            lang = xml.attrib.get('language', 'c').lower()
            if lang not in LEXERS:
                LEXERS[lang] = get_lexer_by_name(lang)
            lexer = LEXERS.get(lang, None)
            if lexer:
                highlighted = highlight(xml.text, lexer, HTML_FORMATTER)

                # we do own line-numbering
                line_count = highlighted.count('\n')
                source_lines = '\n'.join([str(i) for i in range(1, line_count + 1)])
                result.append("""<table class="listing_frame" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td class="listing_lines" align="right"><pre>%s</pre></td>
      <td class="listing_code"><pre class="programlisting">%s</pre></td>
    </tr>
  </tbody>
</table>
""" % (source_lines, highlighted))
            else:
                logging.warn('No pygments lexer for language="%s"', lang)
                result.append('<pre class="programlisting">')
                result.append(xml.text)
                result.append('</pre>')
    else:
        result.append('<pre class="programlisting">')
        append_text(xml.text, result)
        convert_inner(ctx, xml, result)
        result.append('</pre>')
    append_text(xml.tail, result)
    return result


def convert_quote(ctx, xml):
    result = ['<span class="quote">"<span class="quote">']
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</span>"</span>')
    append_text(xml.tail, result)
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
    return convert_sect(ctx, xml, 'h2', convert_inner)


def convert_refsect2(ctx, xml):
    return convert_sect(ctx, xml, 'h3')


def convert_refsect3(ctx, xml):
    return convert_sect(ctx, xml, 'h4')


def convert_row(ctx, xml):
    result = ['<tr>\n']
    convert_inner(ctx, xml, result)
    result.append('</tr>\n')
    return result


def convert_sect1_tag(ctx, xml):
    return convert_sect(ctx, xml, 'h2')


def convert_sect2(ctx, xml):
    return convert_sect(ctx, xml, 'h3')


def convert_sect3(ctx, xml):
    return convert_sect(ctx, xml, 'h4')


def convert_simpara(ctx, xml):
    result = ['<p>']
    append_text(xml.text, result)
    result.append('</p>')
    append_text(xml.tail, result)
    return result


def convert_span(ctx, xml):
    result = ['<span class="%s">' % xml.tag]
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</span>')
    append_text(xml.tail, result)
    return result


def convert_table(ctx, xml):
    result = ['<div class="table">']
    if 'id' in xml.attrib:
        result.append('<a name="%s"></a>' % xml.attrib['id'])
    title_tag = xml.find('title')
    if title_tag is not None:
        result.append('<p class="title"><b>')
        # TODO(ensonic): Add a 'Table X. ' prefix, needs a table counter
        result.extend(convert_title(ctx, title_tag))
        result.append('</b></p>')
        xml.remove(title_tag)
    result.append('<div class="table-contents"><table class="table" summary="g_object_new" border="1">')

    convert_inner(ctx, xml, result)

    result.append('</table></div></div>')
    append_text(xml.tail, result)
    return result


def convert_tbody(ctx, xml):
    result = ['<tbody>']
    ctx['table.entry'] = 'td'
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


def convert_thead(ctx, xml):
    result = ['<thead>']
    ctx['table.entry'] = 'th'
    convert_inner(ctx, xml, result)
    result.append('</thead>')
    # is in tgroup and there can be no 'text'
    return result


def convert_title(ctx, xml):
    # This is always called from some context
    result = []
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    append_text(xml.tail, result)
    return result


def convert_ulink(ctx, xml):
    result = ['<a class="%s" href="%s">%s</a>' % (xml.tag, xml.attrib['url'], xml.text)]
    if xml.tail:
        result.append(xml.tail)
    return result


def convert_userinput(ctx, xml):
    result = ['<span class="command"><strong>']
    append_text(xml.text, result)
    convert_inner(ctx, xml, result)
    result.append('</strong></span>')
    append_text(xml.tail, result)
    return result


def convert_variablelist(ctx, xml):
    result = ["""<div class="variablelist"><table border="0" class="variablelist">
<colgroup>
<col align="left" valign="top">
<col>
</colgroup>
<tbody>"""]
    convert_inner(ctx, xml, result)
    result.append("""</tbody>
</table></div>""")
    return result


def convert_varlistentry(ctx, xml):
    result = ['<tr>']

    result.append('<td><p>')
    term = xml.find('term')
    result.extend(convert_span(ctx, term))
    result.append('</p></td>')

    result.append('<td>')
    listitem = xml.find('listitem')
    convert_inner(ctx, listitem, result)
    result.append('</td>')

    result.append('<tr>')
    return result


# TODO(ensonic): turn into class with converters as functions and ctx as self
convert_tags = {
    'abstract': convert_abstract,
    'acronym': convert_acronym,
    'anchor': convert_anchor,
    'application': convert_span,
    'bookinfo': convert_bookinfo,
    'blockquote': convert_blockquote,
    'caption': convert_div,
    'code': convert_code,
    'colspec': convert_colspec,
    'constant': convert_code,
    'command': convert_command,
    'corpauthor': convert_corpauthor,
    'emphasis': convert_emphasis,
    'entry': convert_entry,
    'envar': convert_code,
    'footnote': convert_footnote,
    'filename': convert_code,
    'formalpara': convert_formalpara,
    'function': convert_code,
    'glossdef': convert_glossdef,
    'glossdiv': convert_glossdiv,
    'glossentry': convert_glossentry,
    'glossterm': convert_glossterm,
    'imageobject': convert_imageobject,
    'indexdiv': convert_indexdiv,
    'indexentry': convert_ignore,
    'indexterm': convert_skip,
    'informalexample': convert_div,
    'informaltable': convert_informaltable,
    'inlinegraphic': convert_inlinegraphic,
    'inlinemediaobject': convert_span,
    'itemizedlist': convert_itemizedlist,
    'legalnotice': convert_div,
    'link': convert_link,
    'listitem': convert_listitem,
    'literal': convert_code,
    'literallayout': convert_literallayout,
    'mediaobject': convert_div,
    'note': convert_div,
    'option': convert_code,
    'orderedlist': convert_orderedlist,
    'para': convert_para,
    'partintro': convert_div,
    'parameter': convert_em_class,
    'phrase': convert_phrase,
    'primaryie': convert_primaryie,
    'programlisting': convert_programlisting,
    'quote': convert_quote,
    'releaseinfo': convert_para_like,
    'refsect1': convert_refsect1,
    'refsect2': convert_refsect2,
    'refsect3': convert_refsect3,
    'replaceable': convert_em_class,
    'returnvalue': convert_span,
    'row': convert_row,
    'screen': convert_pre,
    'sect1': convert_sect1_tag,
    'sect2': convert_sect2,
    'sect3': convert_sect3,
    'simpara': convert_simpara,
    'structfield': convert_em_class,
    'structname': convert_span,
    'synopsis': convert_pre,
    'symbol': convert_span,
    'table': convert_table,
    'tbody': convert_tbody,
    'term': convert_span,
    'tgroup': convert_tgroup,
    'thead': convert_thead,
    'type': convert_span,
    'ulink': convert_ulink,
    'userinput': convert_userinput,
    'varname': convert_code,
    'variablelist': convert_variablelist,
    'varlistentry': convert_varlistentry,
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
        link = c.filename
        if c.anchor:
            link += c.anchor
        result.append('<dt><span class="%s"><a href="%s">%s</a></span>\n' % (
            c.title_tag, link, c.title))
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


def generate_alpha_nav(ctx, divs, prefix, span_id):
    ix_nav = []
    for s in divs:
        title = xml_get_title(ctx, s)
        ix_nav.append('<a class="shortcut" href="#%s%s">%s</a>' % (prefix, title, title))

    return """<table class="navigation" id="top" width="100%%" cellpadding="2" cellspacing="5">
  <tr valign="middle">
    <td width="100%%" align="left" class="shortcuts">
      <span id="nav_%s">
        %s
      </span>
    </td>
    %s
  </tr>
</table>
    """ % (span_id, '\n<span class="dim">|</span>\n'.join(ix_nav), generate_nav_links(ctx))


def generate_refentry_nav(ctx, refsect1s, result):
    result.append("""<table class="navigation" id="top" width="100%" cellpadding="2" cellspacing="5">
  <tr valign="middle">
    <td width="100%" align="left" class="shortcuts">
      <a href="#" class="shortcut">Top</a>""")

    for s in refsect1s:
        # don't list TOC sections (role="xxx_proto")
        if s.attrib.get('role', '').endswith("_proto"):
            continue
        # skip section without 'id' attrs
        if 'id' not in s.attrib:
            continue

        ref_id = s.attrib['id']
        # skip foreign sections
        if '.' not in ref_id:
            continue

        title = xml_get_title(ctx, s)
        span_id = ref_id.split('.')[1].replace('-', '_')

        result.append("""
          <span id="nav_%s">
            <span class="dim">|</span> 
            <a href="#%s" class="shortcut">%s</a>
          </span>
          """ % (span_id, ref_id, title))
    result.append("""
    </td>
    %s
  </tr>
</table>
""" % generate_nav_links(ctx))


def generate_footer(ctx):
    result = []
    if 'footnotes' in ctx:
        result.append("""<div class="footnotes">\n
<br><hr style="width:100; text-align:left;margin-left: 0">
""")
        for f in ctx['footnotes']:
            result.extend(f)
        result.append('</div>\n')
    return result


def get_id_path(node):
    """ Generate the 'id'.
    We need to walk up the xml-tree and check the positions for each sibling.
    When reaching the top of the tree we collect remaining index entries from
    the chunked-tree.
    """
    ix = []
    xml = node.xml
    parent = xml.getparent()
    while parent is not None:
        children = parent.getchildren()
        ix.insert(0, str(children.index(xml) + 1))
        xml = parent
        parent = xml.getparent()
    while node is not None:
        ix.insert(0, str(node.idx + 1))
        node = node.parent

    return ix


def get_id(node):
    xml = node.xml
    node_id = xml.attrib.get('id', None)
    if node_id:
        return node_id

    # TODO: this is moot if nothing links to it, we could also consider to omit
    # the <a name="$id"></a> tag.
    logging.info('%d: No "id" attribute on "%s", generating one',
                 xml.sourceline, xml.tag)
    ix = get_id_path(node)
    # logging.warning('%s: id indexes: %s', node.filename, str(ix))
    return 'id-' + '.'.join(ix)


def convert_chunk_with_toc(ctx, div_class, title_tag):
    node = ctx['node']
    result = [
        HTML_HEADER % (node.title + ": " + node.root.title, generate_head_links(ctx)),
        generate_basic_nav(ctx),
        '<div class="%s">' % div_class,
    ]
    title = node.xml.find('title')
    if title is not None:
        result.append("""
<div class="titlepage">
<%s class="title"><a name="%s"></a>%s</%s>
</div>""" % (
            title_tag, get_id(node), title.text, title_tag))
        node.xml.remove(title)

    toc = generate_toc(ctx, node)
    if toc:
        # TODO: not all docbook page types use this extra heading
        result.append("""<p><b>Table of Contents</b></p>
    <div class="toc">
      <dl class="toc">
    """)
        result.extend(toc)
        result.append("""</dl>
    </div>
    """)
    convert_inner(ctx, node.xml, result)
    result.extend(generate_footer(ctx))
    result.append("""</div>
</body>
</html>""")
    return result


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
    # we already used the title
    title = bookinfo.find('title')
    if title is not None:
        bookinfo.remove(title)
    result.extend(convert_bookinfo(ctx, bookinfo))
    result.append("""<div class="toc">
  <dl class="toc">
""")
    result.extend(generate_toc(ctx, node.root))
    result.append("""</dl>
</div>
""")
    result.extend(generate_footer(ctx))
    result.append("""</div>
</body>
</html>""")
    return result


def convert_chapter(ctx):
    return convert_chunk_with_toc(ctx, 'chapter', 'h2')


def convert_glossary(ctx):
    node = ctx['node']
    glossdivs = node.xml.findall('glossdiv')

    result = [
        HTML_HEADER % (node.title + ": " + node.root.title, generate_head_links(ctx)),
        generate_alpha_nav(ctx, glossdivs, 'gls', 'glossary'),
        """<div class="glossary">
<div class="titlepage"><h%1d class="title">
<a name="%s"></a>%s</h%1d>
</div>""" % (node.depth, get_id(node), node.title, node.depth)
    ]
    for i in glossdivs:
        result.extend(convert_glossdiv(ctx, i))
    result.extend(generate_footer(ctx))
    result.append("""</div>
</body>
</html>""")
    return result


def convert_index(ctx):
    node = ctx['node']
    # Get all indexdivs under indexdiv
    indexdivs = node.xml.find('indexdiv').findall('indexdiv')

    result = [
        HTML_HEADER % (node.title + ": " + node.root.title, generate_head_links(ctx)),
        generate_alpha_nav(ctx, indexdivs, 'idx', 'index'),
        """<div class="index">
<div class="titlepage"><h%1d class="title">
<a name="%s"></a>%s</h%1d>
</div>""" % (node.depth, get_id(node), node.title, node.depth)
    ]
    for i in indexdivs:
        result.extend(convert_indexdiv(ctx, i))
    result.extend(generate_footer(ctx))
    result.append("""</div>
</body>
</html>""")
    return result


def convert_part(ctx):
    return convert_chunk_with_toc(ctx, 'part', 'h1')


def convert_preface(ctx):
    node = ctx['node']
    result = [
        HTML_HEADER % (node.title + ": " + node.root.title, generate_head_links(ctx)),
        generate_basic_nav(ctx),
        '<div class="preface">'
    ]
    title = node.xml.find('title')
    if title is not None:
        result.append("""
<div class="titlepage">
<h2 class="title"><a name="%s"></a>%s</h2>
</div>""" % (get_id(node), title.text))
        node.xml.remove(title)
    convert_inner(ctx, node.xml, result)
    result.extend(generate_footer(ctx))
    result.append("""</div>
</body>
</html>""")
    return result


def convert_reference(ctx):
    return convert_chunk_with_toc(ctx, 'reference', 'h1')


def convert_refentry(ctx):
    node = ctx['node']
    node_id = get_id(node)
    refsect1s = node.xml.findall('refsect1')

    gallery = ''
    refmeta = node.xml.find('refmeta')
    if refmeta is not None:
        refmiscinfo = refmeta.find('refmiscinfo')
        if refmiscinfo is not None:
            inlinegraphic = refmiscinfo.find('inlinegraphic')
            if inlinegraphic is not None:
                gallery = ''.join(convert_inlinegraphic(ctx, inlinegraphic))

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
      <p>%s — %s</p>
    </td>
    <td class="gallery_image" valign="top" align="right">%s</td>
  </tr></table>
</div>
""" % (node_id, node_id, node.title, node.title, node.subtitle, gallery))

    for s in refsect1s:
        result.extend(convert_refsect1(ctx, s))
    result.extend(generate_footer(ctx))
    result.append("""</div>
</body>
</html>""")
    return result


def convert_sect1(ctx):
    return convert_chunk_with_toc(ctx, 'sect1', 'h2')


# TODO(ensonic): turn into class with converters as functions and ctx as self
convert_chunks = {
    'book': convert_book,
    'chapter': convert_chapter,
    'glossary': convert_glossary,
    'index': convert_index,
    'part': convert_part,
    'preface': convert_preface,
    'reference': convert_reference,
    'refentry': convert_refentry,
    'sect1': convert_sect1,
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


def convert(out_dir, module, files, node):
    """Convert the docbook chunks to a html file.

    Args:
      out_dir: already created output dir
      files: list of nodes in the tree in pre-order
      node: current tree node
    """

    logging.info('Writing: %s', node.filename)
    with open(os.path.join(out_dir, node.filename), 'wt',
              newline='\n', encoding='utf-8') as html:
        ctx = {
            'module': module,
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
        keywords = []
        for c in cond:
            if ':' in c:
                keywords.append('{}="{}"'.format(*c.split(':', 1)))
            else:
                # deprecated can have no description
                keywords.append('{}="{}"'.format(c, ''))
        return ' ' + ' '.join(keywords)
    else:
        return ''


def create_devhelp2_refsect2_keyword(node, base_link):
    return'    <keyword type="%s" name="%s" link="%s"%s/>\n' % (
        node.attrib['role'], xml_get_title({}, node), base_link + node.attrib['id'],
        create_devhelp2_condition_attribs(node))


def create_devhelp2_refsect3_keyword(node, base_link, title, name):
    return'    <keyword type="%s" name="%s" link="%s"%s/>\n' % (
        node.attrib['role'], title, base_link + name,
        create_devhelp2_condition_attribs(node))


def create_devhelp2(out_dir, module, xml, files):
    with open(os.path.join(out_dir, module + '.devhelp2'), 'wt',
              newline='\n', encoding='utf-8') as idx:
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


def get_dirs(uninstalled):
    if uninstalled:
        # this does not work from buiddir!=srcdir
        gtkdocdir = os.path.split(sys.argv[0])[0]
        if not os.path.exists(gtkdocdir + '/gtk-doc.xsl'):
            # try 'srcdir' (set from makefiles) too
            if os.path.exists(os.environ.get("ABS_TOP_SRCDIR", '') + '/gtk-doc.xsl'):
                gtkdocdir = os.environ['ABS_TOP_SRCDIR']
        styledir = gtkdocdir + '/style'
    else:
        gtkdocdir = os.path.join(config.datadir, 'gtk-doc/data')
        styledir = gtkdocdir
    return (gtkdocdir, styledir)


def main(module, index_file, out_dir, uninstalled):
    tree = etree.parse(index_file)
    tree.xinclude()

    (gtkdocdir, styledir) = get_dirs(uninstalled)
    # copy navigation images and stylesheets to html directory ...
    css_file = os.path.join(styledir, 'style.css')
    for f in glob(os.path.join(styledir, '*.png')) + [css_file]:
        shutil.copy(f, out_dir)
    css_file = os.path.join(out_dir, 'style.css')
    with open(css_file, 'at', newline='\n', encoding='utf-8') as css:
        css.write(HTML_FORMATTER.get_style_defs())

    # TODO: migrate options from fixxref
    # TODO: do in parallel with loading the xml above.
    # TODO: ideally explicity specify the files we need, this will save us the
    # globbing and we'll load less files.
    fixxref.LoadIndicies(out_dir, '/usr/share/gtk-doc/html', [])

    # We do multiple passes:
    # 1) recursively walk the tree and chunk it into a python tree so that we
    #   can generate navigation and link tags.
    files = chunk(tree.getroot(), module)
    files = [f for f in PreOrderIter(files) if f.anchor is None]

    # 2) extract tables:
    # TODO: can be done in parallel
    # - find all 'id' attribs and add them to the link map
    add_id_links(files, fixxref.Links)
    # - build glossary dict
    build_glossary(files)

    # 3) create a xxx.devhelp2 file, do this before 4), since we modify the tree
    create_devhelp2(out_dir, module, tree.getroot(), files)

    # 4) iterate the tree and output files
    # TODO: can be done in parallel, figure out why this is not faster
    # from multiprocessing.pool import Pool
    # with Pool(4) as p:
    #     p.apply_async(convert, args=(out_dir, module, files))
    # from multiprocessing.pool import ThreadPool
    # with ThreadPool(4) as p:
    #     p.apply_async(convert, args=(out_dir, module, files))
    for node in files:
        convert(out_dir, module, files, node)


def run(options):
    logging.info('options: %s', str(options.__dict__))
    module = options.args[0]
    document = options.args[1]

    # TODO: rename to 'html' later on
    # - right now in mkhtml, the dir is created by the Makefile and mkhtml
    #   outputs into the working directory
    out_dir = os.path.join(os.path.dirname(document), 'db2html')
    try:
        os.mkdir(out_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    sys.exit(main(module, document, out_dir, options.uninstalled))
