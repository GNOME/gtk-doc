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

import unittest

from gtkdoc import mkdb


class ScanSourceContent(unittest.TestCase):

    def setUp(self):
        mkdb.MODULE = 'test'

    def test_EmptyInput(self):
        mkdb.ScanSourceContent([])
        self.assertEqual({}, mkdb.SourceSymbolDocs)

    def test_FindsDocComment(self):
        mkdb.ScanSourceContent("""\
            /**
             * symbol:
             *
             * Description.
             */""".splitlines(keepends=True))
        self.assertEqual({'symbol': 'Description.\n'}, mkdb.SourceSymbolDocs)

    def test_FindsDocCommentWithParam(self):
        mkdb.ScanSourceContent("""\
            /**
             * symbol:
             * @par: value
             *
             * Description.
             */""".splitlines(keepends=True))
        self.assertEqual({'symbol': 'Description.\n'}, mkdb.SourceSymbolDocs)
        self.assertIn('symbol', mkdb.SourceSymbolParams)
        self.assertEqual({'par': 'value\n'}, mkdb.SourceSymbolParams['symbol'])

    def test_FindsDocCommentWithReturns(self):
        mkdb.ScanSourceContent("""\
            /**
             * symbol:
             *
             * Description.
             *
             * Returns: result
             */""".splitlines(keepends=True))
        # TODO: trim multiple newlines in code
        self.assertEqual({'symbol': 'Description.\n\n'}, mkdb.SourceSymbolDocs)
        self.assertIn('symbol', mkdb.SourceSymbolParams)
        # TODO: trim whitespace in code
        self.assertEqual({'Returns': ' result\n'}, mkdb.SourceSymbolParams['symbol'])

    def test_FindsDocCommentWithSince(self):
        mkdb.ScanSourceContent("""\
            /**
             * symbol:
             *
             * Since: 0.1
             */""".splitlines(keepends=True))
        self.assertIn('symbol', mkdb.Since)
        self.assertEqual('0.1', mkdb.Since['symbol'])

    def test_FindsDocCommentWithDeprecated(self):
        mkdb.ScanSourceContent("""\
            /**
             * symbol:
             *
             * Deprecated: use function() instead
             */""".splitlines(keepends=True))
        self.assertIn('symbol', mkdb.Deprecated)
        # TODO: trim whitespace in code
        self.assertEqual(' use function() instead\n', mkdb.Deprecated['symbol'])

    def test_FindsDocCommentWithStability(self):
        mkdb.ScanSourceContent("""\
            /**
             * symbol:
             *
             * Stability: stable
             */""".splitlines(keepends=True))
        self.assertIn('symbol', mkdb.StabilityLevel)
        self.assertEqual('Stable', mkdb.StabilityLevel['symbol'])

    def test_HandlesHTMLEntities(self):
        mkdb.ScanSourceContent("""\
            /**
             * symbol:
             *
             * < & >.
             */""".splitlines(keepends=True))
        self.assertEqual({'symbol': '&lt; &amp; &gt;.\n'}, mkdb.SourceSymbolDocs)


if __name__ == '__main__':
    unittest.main()
