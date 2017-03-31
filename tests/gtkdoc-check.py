#!/usr/bin/env python

import unittest

from gtkdoc import check

class TestCheck(unittest.TestCase):
    def test_grep_finds_token_in_one_line(self):
        result = check.grep(r'^(foo)', ['foo'], 'foo')
        self.assertEqual('foo', result)

    def test_grep_does_not_find_token(self):
        with self.assertRaises(check.FileFormatError) as ctx:
            check.grep(r'^(foo)', ['bar'], 'foo')
        self.assertEqual(ctx.exception.detail, 'foo')

    def test_get_variable_prefers_env(self):
        result = check.get_variable({'foo':'bar'}, ['foo=baz'], 'foo')
        self.assertEqual('bar', result)

    def test_get_variable_finds_in_file(self):
        result = check.get_variable({}, ['foo=bar'], 'foo')
        self.assertEqual('bar', result)

    def test_get_variable_finds_in_file_with_whitespce(self):
        result = check.get_variable({}, ['foo = bar'], 'foo')
        self.assertEqual('bar', result)


if __name__ == '__main__':
    unittest.main()
