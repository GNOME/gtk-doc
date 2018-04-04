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

import unittest

from lxml import etree

from gtkdoc import mkhtml2


class TestChunking(unittest.TestCase):

    def test_chunk_only_root_gives_single_chunk(self):
        root = etree.XML('<book />')
        files = mkhtml2.chunk(root)
        self.assertEqual('book', files.name)
        self.assertEqual(0, len(files.descendants))

    def test_chunk_single_chapter_gives_two_chunks(self):
        root = etree.XML('<book><chapter /></book>')
        files = mkhtml2.chunk(root)
        self.assertEqual(1, len(files.descendants))

    def test_chunk_first_sect1_is_inlined(self):
        root = etree.XML('<book><chapter><sect1 /></chapter></book>')
        files = mkhtml2.chunk(root)
        self.assertEqual(1, len(files.descendants))

    def test_chunk_second_sect1_is_nt_inlined(self):
        root = etree.XML('<book><chapter><sect1 /><sect1 /></chapter></book>')
        files = mkhtml2.chunk(root)
        self.assertEqual(2, len(files.descendants))


if __name__ == '__main__':
    unittest.main()
