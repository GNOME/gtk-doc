# -*- python -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 2001  Damon Chaplin
#               2007-2016  Stefan Sauer
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

import logging
import os
import subprocess

from . import config


def UpdateFileIfChanged(old_file, new_file, make_backup):
    """Compares the old version of the file with the new version and if the
    file has changed it moves the new version into the old versions place. This
    is used so we only change files if needed, so we can do proper dependency
    tracking.

    Args:
        old_file (string): The pathname of the old file.
        new_file (string): The pathname of the new version of the file.
        make_backup (bool) True if a backup of the old file should be kept.
                           It will have the .bak suffix added to the file name.

    Returns:
        bool: It returns False if the file hasn't changed, and True if it has.
    """

    logging.debug("Comparing %s with %s...", old_file, new_file)

    if os.path.exists(old_file):
        old_contents = open(old_file, 'rb').read()
        new_contents = open(new_file, 'rb').read()
        if old_contents == new_contents:
            return False

        if make_backup:
            backupname = old_file + '.bak'
            if os.path.exists(backupname):
                os.unlink(backupname)
            os.rename(old_file, backupname)
        else:
            os.unlink(old_file)

    os.rename(new_file, old_file)
    return True


def GetModuleDocDir(module_name):
    """Get the docdir for the given module via pkg-config

    Args:
      module_name: The module, e.g. 'glib-2.0'

    Returns:
      string: the doc directory
    """
    path = subprocess.check_output([config.pkg_config, '--variable=prefix', module_name], universal_newlines=True)
    return os.path.join(path.strip(), "/share/gtk-doc/html")
