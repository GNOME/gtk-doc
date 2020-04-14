# -*- python -*-

from __future__ import print_function

import argparse
import os
import sys

from subprocess import call

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gtkdoc-check runner.')

    parser.add_argument("--binary-dir", type=str, required=True,
                        help='Path to be used as a working directory')
    parser.add_argument("--input-dir", type=str, required=True,
                        help='Path to be used as a working directory')
    parser.add_argument("--output-dir", type=str, required=True,
                        help='Path to be used as a working directory')

    options, arguments = parser.parse_known_args()

    arg_pos = 0
    if os.name == 'nt':
        arguments.insert(arg_pos, sys.executable)
        arg_pos += 1

    arguments.insert(arg_pos, os.path.join(options.binary_dir, 'gtkdoc-check'))

    environ = os.environ.copy()

    environ['SRCDIR'] = options.input_dir
    environ['BUILDDIR'] = options.output_dir

    sys.exit(call(arguments, env=environ))