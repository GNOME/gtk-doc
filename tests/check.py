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

import unittest

from gtkdoc import check


class TestCheck(unittest.TestCase):

    def test_grep_finds_token_in_one_line(self):
        result = check.grep(r'^(foo)', ['foo'], 'foo')
        self.assertEqual('foo', result)

    def test_grep_does_not_find_token(self):
        with self.assertRaises(check.FileFormatError) as ctx:
            check.grep(r'^(foo)', ['bar'], 'foo')
        self.assertEqual(str(ctx.exception), 'foo')

    def test_get_variable_prefers_env(self):
        result = check.get_variable({'foo': 'bar'}, ['foo=baz'], 'foo')
        self.assertEqual('bar', result)

    def test_get_variable_finds_in_file(self):
        result = check.get_variable({}, ['foo=bar'], 'foo')
        self.assertEqual('bar', result)

    def test_get_variable_finds_in_file_with_whitespce(self):
        result = check.get_variable({}, ['foo = bar'], 'foo')
        self.assertEqual('bar', result)

    def test_get_variable_empty_file(self):
        with self.assertRaises(check.FileFormatError) as ctx:
            check.get_variable({}, [], 'foo')
        self.assertEqual(str(ctx.exception), 'foo')


if __name__ == '__main__':
    unittest.main()
