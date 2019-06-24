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


class ScanSourceContentTestCase(unittest.TestCase):
    """Baseclass for the source scanner tests."""

    def setUp(self):
        mkdb.MODULE = 'test'
        mkdb.SymbolDocs = {}


class ScanSourceContent(ScanSourceContentTestCase):

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


class ParseCommentBlock(ScanSourceContentTestCase):

    def test_EmptyInput(self):
        mkdb.ParseCommentBlock([])
        self.assertEqual({}, mkdb.SourceSymbolDocs)

    def test_FindsDocComment(self):
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'symbol': 'Description.\n'}, mkdb.SourceSymbolDocs)

    def test_FindsDocCommentForSignal(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             Class::signal-with-dashes:

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'Class::signal-with-dashes': 'Description.\n'}, mkdb.SourceSymbolDocs)

    def test_FindsDocCommentForProperty(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             Class:property-with-dashes:

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'Class:property-with-dashes': 'Description.\n'}, mkdb.SourceSymbolDocs)

    def test_FindsDocCommentForActions(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             Class|action.with.dots-and-dashes:

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'Class|action.with.dots-and-dashes': 'Description.\n'}, mkdb.SourceSymbolDocs)

    def test_FindsDocCommentWithParam(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:
             @par: value

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'symbol': 'Description.\n'}, mkdb.SourceSymbolDocs)
        self.assertIn('symbol', mkdb.SourceSymbolParams)
        self.assertEqual({'par': 'value\n'}, mkdb.SourceSymbolParams['symbol'])

    def test_FindsDocCommentWithMultilineParam(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:
             @par: value docs with
               two lines

             Description.
             """).splitlines(keepends=True))
        self.assertEqual({'symbol': 'Description.\n'}, mkdb.SourceSymbolDocs)
        self.assertIn('symbol', mkdb.SourceSymbolParams)
        self.assertEqual({'par': 'value docs with\ntwo lines\n'}, mkdb.SourceSymbolParams['symbol'])

    def test_FindsDocCommentWithReturns(self):
        mkdb.SourceSymbolDocs = {}
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
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Since: 0.1
             """).splitlines(keepends=True))
        self.assertIn('symbol', mkdb.Since)
        self.assertEqual('0.1', mkdb.Since['symbol'])

    def test_FindsDocCommentWithDeprecated(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Deprecated: use function() instead
             """).splitlines(keepends=True))
        self.assertIn('symbol', mkdb.Deprecated)
        # TODO: trim whitespace in code
        self.assertEqual(' use function() instead\n', mkdb.Deprecated['symbol'])

    def test_FindsDocCommentWithStability(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             Stability: stable
             """).splitlines(keepends=True))
        self.assertIn('symbol', mkdb.StabilityLevel)
        self.assertEqual('Stable', mkdb.StabilityLevel['symbol'])

    def test_HandlesHTMLEntities(self):
        mkdb.SourceSymbolDocs = {}
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             symbol:

             < & >.
             """).splitlines(keepends=True))
        self.assertEqual({'symbol': '&lt; &amp; &gt;.\n'}, mkdb.SourceSymbolDocs)


class ParseSectionCommentBlock(ScanSourceContentTestCase):

    def test_FindsSectionBlock(self):
        # TODO: maybe override common.LogWarning() instead and capture the messages
        # Suppress: 'Section symbol is not defined in the test-sections.txt file'
        mkdb.KnownSymbols['symbol:long_description'] = 1
        mkdb.ParseCommentBlock(textwrap.dedent("""\
             SECTION:symbol
             @short_description: short module description

             Module description.
             """).splitlines(keepends=True))
        self.assertIn('symbol:short_description', mkdb.SourceSymbolDocs)
        self.assertEqual('short module description\n', mkdb.SourceSymbolDocs['symbol:short_description'])
        self.assertIn('symbol:long_description', mkdb.SourceSymbolDocs)
        self.assertEqual('Module description.\n', mkdb.SourceSymbolDocs['symbol:long_description'])

    # TODO(ensonic): we need to refactor the code first (see comment there)
    # def test_FindsProgramBlock(self):
    #     mkdb.ParseCommentBlock(textwrap.dedent("""\
    #         PROGRAM:symbol
    #         @short_description: short program description
    #         @synopsis: test-program [*OPTIONS*...] --arg1 *arg* *FILE*
    #         @see_also: test(1)
    #         @--arg1 *arg*: set arg1 to *arg*
    #         @-v, --version: Print the version number
    #         @-h, --help: Print the help message
    #
    #         Program description.
    #          """).splitlines(keepends=True))
    #     self.assertIn('symbol:short_description', mkdb.SourceSymbolDocs)
    #     self.assertEqual('short program description\n', mkdb.SourceSymbolDocs['symbol:short_description'])
    #     self.assertIn('symbol:long_description', mkdb.SourceSymbolDocs)
    #     self.assertEqual('Program description.\n', mkdb.SourceSymbolDocs['symbol:long_description'])


class ScanSourceContentAnnotations(ScanSourceContentTestCase):

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


class OutputStruct(unittest.TestCase):

    def test_SimpleStructGetNormalized(self):
        res = mkdb.extract_struct_body('data', textwrap.dedent("""\
            struct data
            {
                int i;
                char *c;
            };
            """), False, True)
        self.assertEqual(textwrap.dedent("""\
            struct data {
                int i;
                char *c;
            };
            """), res)

    def test_SimpleTypedefStructGetNormalized(self):
        res = mkdb.extract_struct_body('data', textwrap.dedent("""\
            typedef struct _data
            {
                int i;
                char *c;
            } data;
            """), True, True)
        self.assertEqual(textwrap.dedent("""\
            typedef struct {
                int i;
                char *c;
            } data;
            """), res)

    def test_InternalStructNameIsNormalized(self):
        res = mkdb.extract_struct_body('data', textwrap.dedent("""\
            struct _data {
                int i;
                char *c;
            };
            """), False, True)
        self.assertEqual(textwrap.dedent("""\
            struct data {
                int i;
                char *c;
            };
            """), res)


if __name__ == '__main__':
    unittest.main()
