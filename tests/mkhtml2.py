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

from anytree import PreOrderIter
from lxml import etree

from gtkdoc import mkhtml2


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

    # def setUp(self):
    #     logging.basicConfig(
    #         level=logging.INFO,
    #         format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    def chunk_db(self, xml):
        root = etree.XML(xml)
        files = mkhtml2.chunk(root, 'test')
        return root, [f for f in PreOrderIter(files) if f.anchor is None]

    def test_create_devhelp_without_bookinfo(self):
        root, files = self.chunk_db(textwrap.dedent("""\
            <book>
              <chapter id="chap1"><title>Intro</title></chapter>
            </book>"""))
        devhelp = mkhtml2.create_devhelp2_content('test', root, files)
        self.assertNotIn('online', devhelp[0])

    def test_create_devhelp_with_bookinfo(self):
        root, files = self.chunk_db(textwrap.dedent("""\
            <book>
              <bookinfo>
                <title>test Reference Manual</title>
                <releaseinfo>
                  The latest version of this documentation can be found on-line at
                  <ulink role="online-location" url="http://www.example.com/tester/index.html">online-site</ulink>.
                </releaseinfo>
              </bookinfo>
              <chapter id="chap1"><title>Intro</title></chapter>
            </book>"""))
        devhelp = mkhtml2.create_devhelp2_content('test', root, files)
        self.assertIn('online="http://www.example.com/tester/index.html"', devhelp[0])
        self.assertIn('title="test Reference Manual"', devhelp[0])


class TestNavNodes(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

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


if __name__ == '__main__':
    unittest.main()
