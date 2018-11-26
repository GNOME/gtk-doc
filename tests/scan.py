# -*- python -*-
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

import argparse
import textwrap
import unittest

from gtkdoc import scan


class ScanHeaderContentTestCase(unittest.TestCase):
    """Baseclass for the header scanner tests."""

    def setUp(self):
        self.decls = []
        self.types = []
        self.options = argparse.Namespace(
            deprecated_guards='GTKDOC_TESTER_DISABLE_DEPRECATED',
            ignore_decorators='')

    def scanHeaderContent(self, content):
        return scan.ScanHeaderContent(content, self.decls, self.types,
                                      self.options)

    def assertNoDeclFound(self, slist):
        self.assertEqual([], slist)
        self.assertEqual([], self.decls)
        self.assertEqual([], self.types)

    def assertNothingFound(self, slist, doc_comments):
        self.assertEqual({}, doc_comments)
        self.assertNoDeclFound(slist)


class ScanHeaderContent(ScanHeaderContentTestCase):
    """Test generic scanner behaviour."""

    def test_EmptyInput(self):
        slist, doc_comments = self.scanHeaderContent([])
        self.assertNothingFound(slist, doc_comments)

    def test_FindsDocComment(self):
        slist, doc_comments = self.scanHeaderContent("""\
            /**
             * Symbol:
             */""".splitlines(keepends=True))
        self.assertEqual(1, len(doc_comments))
        self.assertIn('symbol', doc_comments)

    def test_DocDoesNotChangeSlistDeclAndTypes(self):
        slist, doc_comments = self.scanHeaderContent("""\
            /**
             * Symbol:
             */""".splitlines(keepends=True))
        self.assertNoDeclFound(slist)

    # TODO: test /* < private_header > */ maker

    def test_SkipSymbolWithPreprocessor(self):
        slist, doc_comments = self.scanHeaderContent("""\
            #ifndef __GTK_DOC_IGNORE__
            extern int bug_512565(void);
            #endif""".splitlines(keepends=True))
        self.assertNoDeclFound(slist)


# ENUM


# FUNCTION


class ScanHeaderContentMacros(ScanHeaderContentTestCase):
    """Test parsing of macro declarations."""

    def assertDecl(self, name, decl):
        d = '<MACRO>\n<NAME>%s</NAME>\n%s</MACRO>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsMacroNumber(self):
        slist, doc_comments = self.scanHeaderContent([
            '#define FOO 1'
        ])
        self.assertEqual(['FOO'], slist)
        self.assertDecl('FOO', '#define FOO 1')

    def test_FindsMacroExpression(self):
        slist, doc_comments = self.scanHeaderContent([
            '#define FOO (1 << 1)'
        ])
        self.assertEqual(['FOO'], slist)
        self.assertDecl('FOO', '#define FOO (1 << 1)')

    # TODO: test for a few variants
    def test_IgnoresInternalMacro(self):
        slist, doc_comments = self.scanHeaderContent([
            '#define _BUG_000000b (a) (a*a)'
        ])
        self.assertNoDeclFound(slist)


class ScanHeaderContentStructs(ScanHeaderContentTestCase):
    """Test parsing of struct declarations."""

    def assertDecl(self, name, decl):
        d = '<STRUCT>\n<NAME>%s</NAME>\n%s</STRUCT>\n' % (name, decl)
        self.assertEqual([d], self.decls)
        self.assertEqual([], self.types)

    def test_FindsStruct(self):
        header = textwrap.dedent("""\
            struct data {
              int test;
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('data', header)

    def test_FindsTypedefStruct(self):
        header = textwrap.dedent("""\
            typedef struct {
              int test;
            } Data;""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('Data', header)

    def test_HandleStructWithDeprecatedMember(self):
        header = textwrap.dedent("""\
            struct data {
              int test_a;
            #ifndef GTKDOC_TESTER_DISABLE_DEPRECATED
              int deprecated;
            #endif
              int test_b;
            };""")
        slist, doc_comments = self.scanHeaderContent(
            header.splitlines(keepends=True))
        self.assertDecl('data', header)


# VARIABLE


if __name__ == '__main__':
    unittest.main()
