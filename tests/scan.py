# -*- python -*-
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

import argparse
import unittest

from gtkdoc import scan


class ScanHeaderContent(unittest.TestCase):

    def setUp(self):
        self.decls = []
        self.types = []
        self.options = argparse.Namespace(deprecated_guards='')

    def scanHeaderContent(self, content):
        return scan.ScanHeaderContent(content, self.decls, self.types,
                                      self.options)

    def test_EmptyInput(self):
        slist, doc_comments = self.scanHeaderContent([])
        self.assertEqual([], slist)
        self.assertEqual({}, doc_comments)
        self.assertEqual([], self.decls)
        self.assertEqual([], self.types)

    def test_FindsDocComment(self):
        slist, doc_comments = self.scanHeaderContent([
            '/** FooBar:',
            ' */'
        ])
        self.assertEqual(1, len(doc_comments))
        self.assertIn('foobar', doc_comments)

    def test_DocDoesNotChangeSlistDeclAndTypes(self):
        slist, doc_comments = self.scanHeaderContent([
            '/** FooBar:',
            ' */'
        ])
        self.assertEqual([], slist)
        self.assertEqual([], self.decls)
        self.assertEqual([], self.types)

    # test /* < private_header > */ maker

    def test_SkipSymbolWithPreprocessor(self):
        slist, doc_comments = self.scanHeaderContent([
            '#ifndef __GTK_DOC_IGNORE__',
            'extern int bug_512565(void);'
            '#endif'
        ])
        self.assertEqual([], slist)
        self.assertEqual([], self.decls)
        self.assertEqual([], self.types)


if __name__ == '__main__':
    unittest.main()
