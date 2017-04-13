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


class TestGetModuleDocDir(unittest.TestCase):

    @mock.patch('subprocess.check_output')
    def test_ReturnsPath(self, subprocess_check_output):
        subprocess_check_output.return_value = '/usr'
        self.assertEquals(common.GetModuleDocDir('glib-2.0'), '/usr/share/gtk-doc/html')


class TestCreateValidSGMLID(unittest.TestCase):

    def test_AlreadyValid(self):
        self.assertEquals(common.CreateValidSGMLID('x'), 'x')

    def test_SpecialCharsBecomeDash(self):
        self.assertEquals(common.CreateValidSGMLID('x_ y'), 'x--y')

    def test_SpecialCharsGetRemoved(self):
        self.assertEquals(common.CreateValidSGMLID('x,;y'), 'xy')


if __name__ == '__main__':
    unittest.main()
