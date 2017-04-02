#!/usr/bin/env python

import mock, os, unittest

from gtkdoc import common

class TestCommon(unittest.TestCase):

    @mock.patch('os.path.exists')
    @mock.patch('os.rename')
    def test_UpdateFileIfChanged_NoOldFile(self, os_rename, os_path_exists):
        os_path_exists.return_value = False
        res = common.UpdateFileIfChanged('/foo', '/bar', False)
        os_rename.assert_called_with('/bar', '/foo')
        self.assertTrue(res)

if __name__ == '__main__':
    unittest.main()
