#!/usr/bin/env python

import mock
import unittest

from gtkdoc import common


class TestUpdateFileIfChanged(unittest.TestCase):

    @mock.patch('os.path.exists')
    @mock.patch('os.rename')
    def test_NoOldFile(self, os_rename, os_path_exists):
        os_path_exists.return_value = False
        res = common.UpdateFileIfChanged('/foo', '/bar', False)
        os_rename.assert_called_with('/bar', '/foo')
        self.assertTrue(res)


class TestCreateValidSGMLID(unittest.TestCase):

    def test_AlreadyValid(self):
        self.assertEquals(common.CreateValidSGMLID('x'), 'x')

    def test_SpecialCharsBecomeDash(self):
        self.assertEquals(common.CreateValidSGMLID('x_ y'), 'x--y')

    def test_SpecialCharsGetRemoved(self):
        self.assertEquals(common.CreateValidSGMLID('x,;y'), 'xy')


if __name__ == '__main__':
    unittest.main()
