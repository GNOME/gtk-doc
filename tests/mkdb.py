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

import textwrap
import unittest

from gtkdoc import mkdb


class ScanSourceContent(unittest.TestCase):

    def setUp(self):
        mkdb.MODULE = 'test'

    def test_EmptyInput(self):
        blocks = mkdb.ScanSourceContent([])
        self.assertEqual(0, len(blocks))

    def test_SkipsSingleLineComment(self):
        blocks = mkdb.ScanSourceContent("/** foo */")
        self.assertEqual(0, len(blocks))

    def test_FindsSingleDocComment(self):
        blocks = mkdb.ScanSourceContent("""\
            /**
             * symbol:
             *
             * Description.
             */""".splitlines(keepends=True))
        self.assertEqual(1, len(blocks))


class ParseCommentBlock(unittest.TestCase):

    def setUp(self):
        mkdb.MODULE = 'test'

    def test_EmptyInput(self):
        mkdb.ParseCommentBlock([])
        self.assertEqual({}, mkdb.SourceSymbolDocs)

    def test_FindsDocComment(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'symbol': 'Description.\n'}, mkdb.SourceSymbolDocs)

    def test_FindsDocCommentWithParam(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:
             @par: value

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'symbol': 'Description.\n'}, mkdb.SourceSymbolDocs)
        self.assertIn('symbol', mkdb.SourceSymbolParams)
        self.assertEqual({'par': 'value\n'}, mkdb.SourceSymbolParams['symbol'])

    def test_FindsDocCommentWithReturns(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Description.

             Returns: result
             """).splitlines(keepends=True))
        # TODO: trim multiple newlines in code
        self.assertEqual({'symbol': 'Description.\n\n'}, mkdb.SourceSymbolDocs)
        self.assertIn('symbol', mkdb.SourceSymbolParams)
        # TODO: trim whitespace in code
        self.assertEqual({'Returns': ' result\n'}, mkdb.SourceSymbolParams['symbol'])

    def test_FindsDocCommentWithSince(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Since: 0.1
             """).splitlines(keepends=True))
        self.assertIn('symbol', mkdb.Since)
        self.assertEqual('0.1', mkdb.Since['symbol'])

    def test_FindsDocCommentWithDeprecated(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Deprecated: use function() instead
             """).splitlines(keepends=True))
        self.assertIn('symbol', mkdb.Deprecated)
        # TODO: trim whitespace in code
        self.assertEqual(' use function() instead\n', mkdb.Deprecated['symbol'])

    def test_FindsDocCommentWithStability(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Stability: stable
             """).splitlines(keepends=True))
        self.assertIn('symbol', mkdb.StabilityLevel)
        self.assertEqual('Stable', mkdb.StabilityLevel['symbol'])

    def test_HandlesHTMLEntities(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             < & >.
             """).splitlines(keepends=True))
        self.assertEqual({'symbol': '&lt; &amp; &gt;.\n'}, mkdb.SourceSymbolDocs)


class ScanSourceContentAnnotations(unittest.TestCase):

    def setUp(self):
        mkdb.MODULE = 'test'

    def test_ParamAnnotation(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:
             @par: (allow-none): value

             description.
             """).splitlines(keepends=True))
        # TODO: we only extract those when outputting docbook, thats silly
        # self.assertEqual({'par': 'value\n'}, mkdb.SourceSymbolParams['symbol'])
        self.assertEqual({}, mkdb.SymbolAnnotations)

    def test_RetunsAnnotation(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             description.

             Returns: (transfer full) result.
             """).splitlines(keepends=True))
        # TODO: we only extract those when outputting docbook, thats silly
        self.assertEqual({}, mkdb.SymbolAnnotations)

    # multiple annotations, multiline annotations, symbol-level ...


if __name__ == '__main__':
    unittest.main()
