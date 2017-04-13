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
import re
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
        make_backup (bool): True if a backup of the old file should be kept.
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
      module_name (string): The module, e.g. 'glib-2.0'

    Returns:
      string: the doc directory
    """
    path = subprocess.check_output([config.pkg_config, '--variable=prefix', module_name], universal_newlines=True)
    return os.path.join(path.strip(), 'share/gtk-doc/html')


def LogWarning(file, line, message):
    """Log a warning in gcc style format

    Args:
      file (string): The file the error comes from
      line (int): line number in the file
      message (string): the error message to print
    """
    file = file or "unknown"

    # TODO: write to stderr
    print ("%s:%d: warning: %s" % (file, line, message))


def CreateValidSGMLID(id):
    """Creates a valid SGML 'id' from the given string.

    According to http://www.w3.org/TR/html4/types.html#type-id "ID and NAME
    tokens must begin with a letter ([A-Za-z]) and may be followed by any number
    of letters, digits ([0-9]), hyphens ("-"), underscores ("_"), colons (":"),
    and periods (".")."

    When creating SGML IDS, we append ":CAPS" to all all-caps identifiers to
    prevent name clashes (SGML ids are case-insensitive). (It basically never is
    the case that mixed-case identifiers would collide.)

    Args:
      id (string): The text to be converted into a valid SGML id.

    Returns:
      string: The converted id.
    """

    # Special case, '_' would end up as '' so we use 'gettext-macro' instead.
    if id is "_":
        return "gettext-macro"

    id = re.sub(r'[,;]', '', id)
    id = re.sub(r'[_ ]', '-', id)
    id = re.sub(r'^-+', '', id)
    id = id.replace('::', '-')
    id = id.replace(':', '--')

    # Append ":CAPS" to all all-caps identifiers
    # FIXME: there are some inconsistencies here, we have index files containing e.g. TRUE--CAPS
    if id.isupper() and not id.endswith('-CAPS'):
        id += ':CAPS'

    return id
