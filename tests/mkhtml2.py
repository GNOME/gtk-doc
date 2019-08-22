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

import logging
import textwrap
import unittest

from lxml import etree
from parameterized import parameterized

from gtkdoc import mkhtml2
from gtkdoc.mkhtml2 import PreOrderIter


class TestChunking(unittest.TestCase):

    # def setUp(self):
    #     logging.basicConfig(
    #         level=logging.INFO,
    #         format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    def test_chunk_only_root_gives_single_chunk(self):
        root = etree.XML('<book />')
        files = mkhtml2.chunk(root, 'test')
        self.assertEqual('book', files.name)
        self.assertEqual(0, len(files.descendants))

    def test_chunk_single_chapter_gives_two_chunks(self):
        root = etree.XML('<book><chapter /></book>')
        files = mkhtml2.chunk(root, 'test')
        descendants = [f for f in files.descendants if f.anchor is None]
        logging.info('descendants : %s', str(descendants))
        self.assertEqual(1, len(descendants))

    def test_chunk_first_sect1_is_inlined(self):
        root = etree.XML('<book><chapter><sect1 /></chapter></book>')
        files = mkhtml2.chunk(root, 'test')
        descendants = [f for f in files.descendants if f.anchor is None]
        logging.info('descendants : %s', str(descendants))
        self.assertEqual(1, len(descendants))

    def test_chunk_second_sect1_is_not_inlined(self):
        root = etree.XML('<book><chapter><sect1 /><sect1 /></chapter></book>')
        files = mkhtml2.chunk(root, 'test')
        descendants = [f for f in files.descendants if f.anchor is None]
        logging.info('descendants : %s', str(descendants))
        self.assertEqual(2, len(descendants))


class TestDataExtraction(unittest.TestCase):

    # def setUp(self):
    #     logging.basicConfig(
    #         level=logging.INFO,
    #         format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    def chunk_db(self, xml):
        root = etree.XML(xml)
        files = mkhtml2.chunk(root, 'test')
        return [f for f in PreOrderIter(files) if f.anchor is None]

    def test_extract_ids(self):
        files = self.chunk_db('<book><chapter id="chap1"></chapter></book>')
        links = {}
        mkhtml2.add_id_links_and_titles(files, links)
        self.assertIn('chap1', links)

    def test_extract_titles(self):
        files = self.chunk_db('<book><chapter id="chap1"><title>Intro</title></chapter></book>')
        links = {}
        mkhtml2.add_id_links_and_titles(files, links)
        self.assertIn('chap1', mkhtml2.titles)
        self.assertEqual('Intro', mkhtml2.titles['chap1']['title'])
        self.assertEqual('chapter', mkhtml2.titles['chap1']['tag'])

    def test_extract_glossaries(self):
        files = self.chunk_db(textwrap.dedent("""\
            <book>
              <glossary id="glossary">
                <glossentry>
                  <glossterm><anchor id="glossterm-API"/>API</glossterm>
                  <glossdef>
                    <para>Application Programming Interface</para>
                  </glossdef>
                </glossentry>
              </glossary>
            </book>"""))
        mkhtml2.build_glossary(files)
        self.assertIn('API', mkhtml2.glossary)
        self.assertEqual('Application Programming Interface', mkhtml2.glossary['API'])


class TestDevhelp(unittest.TestCase):

    xml_minimal = textwrap.dedent("""\
      <book>
        <chapter id="chap1"><title>Intro</title></chapter>
      </book>""")

    xml_basic = textwrap.dedent("""\
      <book>
        <bookinfo>
          <title>test Reference Manual</title>
          <releaseinfo>
            The latest version of this documentation can be found on-line at
            <ulink role="online-location" url="http://www.example.com/tester/index.html">online-site</ulink>.
          </releaseinfo>
        </bookinfo>
        <chapter id="chap1"><title>Intro</title></chapter>
      </book>""")

    # TODO: need one with multiple conditions
    xml_full = textwrap.dedent("""\
      <book>
        <bookinfo>
          <title>test Reference Manual</title>
        </bookinfo>
        <chapter id="chap1">
          <title>Reference</title>
          <refentry id="GtkdocObject">
            <refmeta>
              <refentrytitle role="top_of_page" id="GtkdocObject.top_of_page">GtkdocObject</refentrytitle>
              <refmiscinfo>TESTER Library</refmiscinfo>
            </refmeta>
            <refnamediv>
              <refname>GtkdocObject</refname>
              <refpurpose>class for gtk-doc unit test</refpurpose>
            </refnamediv>
            <refsect1 id="GtkdocObject.functions" role="functions_proto">
              <title role="functions_proto.title">Functions</title>
            </refsect1>
            <refsect1 id="GtkdocObject.functions_details" role="details">
              <title role="details.title">Functions</title>
              <refsect2 id="gtkdoc-object-new" role="function" condition="since:0.1">
                <title>gtkdoc_object_new&#160;()</title>
                <refsect3 id="GtkdocObjectClass.members" role="struct_members">
                  <title>Members</title>
                  <informaltable role="struct_members_table" pgwide="1" frame="none">
                    <tgroup cols="3">
                      <colspec colname="struct_members_name" colwidth="300px"/>
                      <colspec colname="struct_members_description"/>
                      <colspec colname="struct_members_annotations" colwidth="200px"/>
                      <tbody>
                        <row role="member">
                          <entry role="struct_member_name">
                            <para>
                              GtkdocObjectClass
                              <structfield id="GtkdocObjectClass.parent">parent</structfield>;
                            </para>
                          </entry>
                          <entry role="struct_member_description">
                            <para>parent/</para>
                          </entry>
                          <entry role="struct_member_annotations"></entry>
                        </row>
                      </tbody>
                    </tgroup>
                  </informaltable>
                </refsect3>
              </refsect2>
            </refsect1>
            <refsect1 id="tester-GtkdocTypes.other_details" role="details">
              <title role="details.title">Types and Values</title>
              <refsect2 id="GtkdocEnum" role="enum">
                <title>enum GtkdocEnum</title>
                <indexterm zone="GtkdocEnum">
                  <primary>GtkdocEnum</primary>
                </indexterm>
                <para>Enum values for the <link linkend="GtkdocEnum"><type>GtkdocEnum</type>
                  </link> type.</para>
                <refsect3 id="GtkdocEnum.members" role="enum_members">
                  <title>Members</title>
                  <informaltable role="enum_members_table" pgwide="1" frame="none">
                    <tgroup cols="3">
                      <colspec colname="enum_members_name" colwidth="300px"/>
                      <colspec colname="enum_members_description"/>
                      <colspec colname="enum_members_annotations" colwidth="200px"/>
                      <tbody>
                        <row role="constant">
                          <entry role="enum_member_name">
                            <para id="GTKDOC-ENUM-V1:CAPS">GTKDOC_ENUM_V1</para>
                          </entry>
                          <entry role="enum_member_description">
                            <para>first</para>
                          </entry>
                          <entry role="enum_member_annotations"></entry>
                        </row>
                        <row role="constant">
                          <entry role="enum_member_name">
                            <para id="GTKDOC-ENUM-V2:CAPS">GTKDOC_ENUM_V2</para>
                          </entry>
                          <entry role="enum_member_description">
                            <para>second Since: 0.5</para>
                          </entry>
                          <entry role="enum_member_annotations"></entry>
                        </row>
                      </tbody>
                    </tgroup>
                  </informaltable>
                </refsect3>
              </refsect2>
            </refsect1>
          </refentry>
        </chapter>
      </book>""")

    # def setUp(self):
    #     logging.basicConfig(
    #         level=logging.INFO,
    #         format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    def convert(self, xml):
        root = etree.XML(xml)
        files = mkhtml2.chunk(root, 'test')
        files = [f for f in PreOrderIter(files) if f.anchor is None]
        mkhtml2.add_id_links_and_titles(files, {})
        return '\n'.join(mkhtml2.create_devhelp2_content('test', root, files))

    def test_create_devhelp_has_minimal_structure(self):
        devhelp = self.convert(self.xml_minimal)
        self.assertIn('<book xmlns', devhelp)
        self.assertIn('<chapters', devhelp)
        self.assertIn('<functions', devhelp)

    def test_create_devhelp_without_bookinfo(self):
        devhelp = self.convert(self.xml_minimal)
        self.assertNotIn('online', devhelp)

    def test_create_devhelp_with_bookinfo(self):
        devhelp = self.convert(self.xml_basic)
        self.assertIn('online="http://www.example.com/tester/index.html"', devhelp)
        self.assertIn('title="test Reference Manual"', devhelp)

    def test_create_devhelp_with_refentry_has_chapters(self):
        devhelp = self.convert(self.xml_full)
        self.assertIn('<sub name="Reference" link="chap1.html">', devhelp)
        self.assertIn('<sub name="GtkdocObject" link="GtkdocObject.html"/>', devhelp)

    def test_create_devhelp_with_refentry_has_keywords(self):
        devhelp = self.convert(self.xml_full)
        self.assertIn(
            '<keyword type="function" name="gtkdoc_object_new ()" '
            'link="GtkdocObject.html#gtkdoc-object-new" since="0.1"/>',
            devhelp)

    def test_create_devhelp_with_refesect3_has_member_keywords(self):
        devhelp = self.convert(self.xml_full)
        self.assertIn(
            '<keyword type="member" name="GtkdocObjectClass.parent" '
            'link="GtkdocObject.html#GtkdocObjectClass.parent"/>',
            devhelp)

    def test_create_devhelp_with_refesect3_has_constant_keywords(self):
        devhelp = self.convert(self.xml_full)
        self.assertIn(
            '<keyword type="constant" name="GTKDOC_ENUM_V1" '
            'link="GtkdocObject.html#GTKDOC-ENUM-V1:CAPS"/>',
            devhelp)


class TestNavNodes(unittest.TestCase):

    # def setUp(self):
    #     logging.basicConfig(
    #         level=logging.INFO,
    #         format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    def chunk_db(self, xml):
        root = etree.XML(xml)
        files = mkhtml2.chunk(root, 'test')
        return [f for f in PreOrderIter(files) if f.anchor is None]

    def test_nav_nodes_contains_home(self):
        files = self.chunk_db(textwrap.dedent("""\
            <book>
            </book>"""))
        nav = mkhtml2.generate_nav_nodes(files, files[0])
        self.assertEqual(1, len(nav))
        self.assertIn('nav_home', nav)

    def test_nav_nodes_contains_up_and_prev(self):
        files = self.chunk_db(textwrap.dedent("""\
            <book>
              <chapter id="chap1"><title>Intro</title></chapter>
            </book>"""))
        nav = mkhtml2.generate_nav_nodes(files, files[1])
        self.assertEqual(3, len(nav))
        self.assertIn('nav_up', nav)
        self.assertIn('nav_prev', nav)
        self.assertNotIn('nav_next', nav)

    def test_nav_nodes_contains_next(self):
        files = self.chunk_db(textwrap.dedent("""\
            <book>
              <chapter id="chap1"><title>Intro</title></chapter>
              <chapter id="chap2"><title>Content</title></chapter>
            </book>"""))
        nav = mkhtml2.generate_nav_nodes(files, files[1])
        self.assertEqual(4, len(nav))
        self.assertIn('nav_next', nav)


class TestConverter(unittest.TestCase):

    xml_book_beg = textwrap.dedent("""\
        <book>
          <bookinfo>
            <title>test Reference Manual</title>
          </bookinfo>""")
    xml_book_end = textwrap.dedent("""\
        </book>""")
    xml_book = '\n'.join([xml_book_beg, xml_book_end])

    xml_book_preface = '\n'.join([
        xml_book_beg,
        '  <preface id="intro"><title>Intro</title></preface>',
        xml_book_end])

    xml_book_chapter = '\n'.join([
        xml_book_beg,
        '  <chapter id="chap1"><title>Intro</title></chapter>',
        xml_book_end])

    xml_book_reference = '\n'.join([
        xml_book_beg,
        '  <reference id="part.i"><title>Reference</title></reference>',
        xml_book_end])

    xml_book_part_chapter = '\n'.join([
        xml_book_beg,
        textwrap.dedent("""\
          <part label="1" id="part.i">
            <title>Overview</title>
            <chapter id="chap1"><title>Intro</title></chapter>
          </part>"""),
        xml_book_end])

    # 2 sections since the first one is not chunked
    xml_book_chapter_secton = '\n'.join([
        xml_book_beg,
        textwrap.dedent("""\
          <chapter id="chap1">
            <title>Overview</title>
            <section id="s1"><title>Intro</title></section>
            <section id="s2"><title>getting started</title></section>
          </chapter>"""),
        xml_book_end])
    xml_book_chapter_sect1 = xml_book_chapter_secton.replace('section', 'sect1')

    xml_book_chapter_refentry_beg = '\n'.join([
        xml_book_beg,
        textwrap.dedent("""\
          <chapter id="chap1">
            <title>Reference</title>
            <refentry id="GtkdocObject">
              <refmeta>
                <refentrytitle role="top_of_page" id="GtkdocObject.top_of_page">GtkdocObject</refentrytitle>
              </refmeta>""")])

    xml_book_chapter_refentry_end = '\n'.join([
        textwrap.dedent("""\
            </refentry>
          </chapter>"""),
        xml_book_end])
    xml_book_chapter_refentry = '\n'.join([xml_book_chapter_refentry_beg, xml_book_chapter_refentry_end])

    xml_book_index_empty = '\n'.join([
        xml_book_beg,
        '  <index id="api-index-full"><title>API Index</title></index>',
        xml_book_end])

    xml_book_index = '\n'.join([
        xml_book_beg,
        textwrap.dedent("""\
          <index id="api-index-full">
            <title>API Index</title>
            <indexdiv id="api-index-full">
              <indexdiv><title>O</title>
                <!-- we get a link warning, since we we don't include the 'refentry' -->
                <!--indexentry>
                  <primaryie linkends="gtkdoc-object-new">
                    <link linkend="gtkdoc-object-new">gtkdoc_object_new</link>,
                    function in <link linkend="GtkdocObject">GtkdocObject</link>
                  </primaryie>
                </indexentry-->
              </indexdiv>
            </indexdiv>
          </index>"""),
        xml_book_end])

    xml_book_glossary_empty = '\n'.join([
        xml_book_beg,
        '  <glossary id="glossary"><title>Glossary</title></glossary>',
        xml_book_end])

    xml_book_glossary = '\n'.join([
        xml_book_beg,
        textwrap.dedent("""\
          <glossary id="glossary">
            <title>Glossary</title>
            <glossdiv><title>A</title>
              <glossentry>
                <glossterm><anchor id="glossterm-API"/>API</glossterm>
                <glossdef>
                  <para>Application Programming Interface</para>
                </glossdef>
              </glossentry>
            </glossdiv>
          </glossary>"""),
        xml_book_end])

    # def setUp(self):
    #     logging.basicConfig(
    #         level=logging.INFO,
    #         format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    def convert(self, xml, ix):
        root = etree.XML(xml)
        files = mkhtml2.chunk(root, 'test')
        nodes = [f for f in PreOrderIter(files) if f.anchor is None]
        return '\n'.join(mkhtml2.convert_content('test', nodes, nodes[ix], 'c'))

    @parameterized.expand([
        ('book', (xml_book, 0)),
        ('preface', (xml_book_preface, 1)),
        ('reference', (xml_book_reference, 1)),
        ('chapter', (xml_book_chapter, 1)),
        ('part', (xml_book_part_chapter, 1)),
        ('section', (xml_book_chapter_secton, 2)),
        ('sect1', (xml_book_chapter_sect1, 2)),
        ('refentry', (xml_book_chapter_refentry, 2)),
        ('index', (xml_book_index, 1)),
        ('index_empty', (xml_book_index_empty, 1)),
        ('glossary', (xml_book_glossary, 1)),
        ('glossary_empty', (xml_book_glossary_empty, 1)),
    ])
    def test_convert_produces_html(self, _, params):
        html = self.convert(params[0], params[1])
        self.assertIn('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">', html)
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

    def test_convert_book_has_title(self):
        html = self.convert(self.xml_book, 0)
        self.assertIn('<title>test Reference Manual</title>', html)

    def test_refnav_includes_normal_refsect1(self):
        xml = '\n'.join([
            self.xml_book_chapter_refentry_beg,
            textwrap.dedent("""\
                  <refsect1 id="GtkdocObject.description" role="desc">
                     <title role="desc.title">Description</title>
                  </refsect1>
                """),
            self.xml_book_chapter_refentry_end])
        html = self.convert(xml, 2)
        self.assertIn('class="shortcut">Description</a>', html)

    def test_refnav_skips_protos_refsect1(self):
        xml = '\n'.join([
            self.xml_book_chapter_refentry_beg,
            textwrap.dedent("""\
                  <refsect1 id="GtkdocObject.functions" role="functions_proto">
                    <title role="functions_proto.title">Functions</title>
                  </refsect1>
                """),
            self.xml_book_chapter_refentry_end])
        html = self.convert(xml, 2)
        self.assertNotIn('class="shortcut">Functions</a>', html)


if __name__ == '__main__':
    unittest.main()
