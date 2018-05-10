# -*- python -*-

from __future__ import print_function

import argparse
import os
import sys

from subprocess import call

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gtkdoc-mkdb runner.')

    parser.add_argument("--binary-dir", type=str, required=True,
                        help='Path to the gtkdoc executables directory to be used')
    parser.add_argument("--change-dir", type=str, default=None,
                        help='Path to the gtkdoc executables directory to be used')

    options, arguments = parser.parse_known_args()

    arguments.insert(0, os.path.join(options.binary_dir, 'gtkdoc-mkdb'))

    if not options.change_dir is None:
        if not os.path.exists(options.change_dir):
            os.makedirs(options.change_dir)

    sys.exit(call(arguments, cwd=options.change_dir))