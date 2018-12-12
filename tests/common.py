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

from unittest import mock
import unittest

from gtkdoc import common


class TestUpdateFileIfChanged(unittest.TestCase):

    @mock.patch('os.path.exists')
    @mock.patch('os.rename')
    def test_NoOldFile(self, os_rename, os_path_exists):
        os_path_exists.return_value = False
        res = common.UpdateFileIfChanged('/old', '/new', False)
        os_rename.assert_called_with('/new', '/old')
        self.assertTrue(res)

    @mock.patch('os.path.exists')
    @mock.patch('builtins.open', mock.mock_open(read_data='bar'))
    @mock.patch('os.unlink')
    def test_FilesAreTheSame(self, os_unlink, os_path_exists):
        os_path_exists.return_value = True
        res = common.UpdateFileIfChanged('/old', '/new', False)
        os_unlink.assert_called_with('/new')
        self.assertFalse(res)


class TestGetModuleDocDir(unittest.TestCase):

    @mock.patch('subprocess.check_output')
    def test_ReturnsPath(self, subprocess_check_output):
        subprocess_check_output.return_value = '/usr'
        self.assertEqual(common.GetModuleDocDir('glib-2.0'), '/usr/share/gtk-doc/html')


class TestCreateValidSGMLID(unittest.TestCase):

    def test_AlreadyValid(self):
        self.assertEqual(common.CreateValidSGMLID('x'), 'x')

    def test_SpecialCharsBecomeDash(self):
        self.assertEqual(common.CreateValidSGMLID('x_ y'), 'x--y')

    def test_SpecialCharsGetRemoved(self):
        self.assertEqual(common.CreateValidSGMLID('x,;y'), 'xy')


if __name__ == '__main__':
    unittest.main()
