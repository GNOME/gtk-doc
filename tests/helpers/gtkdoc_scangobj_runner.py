# -*- python -*-

from __future__ import print_function

import argparse
import os
import sys

from subprocess import call, PIPE, Popen

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gtkdoc-scangobj runner.')

    parser.add_argument("--binary-dir", type=str, required=True,
                        help='Path to be used as a working directory')
    parser.add_argument("--pkg-config", type=str, required=True,
                        help='Path to the pkg-config executable to be used')
    parser.add_argument("--extra-pkg", type=str, default=[], action='append',
                        help='Extra package to be use while scanning')
    parser.add_argument("--extra-cflags", type=str, default=[], action='append',
                        help='Extra Cflags to be use while scanning')
    parser.add_argument("--extra-lib", type=str, default=[], action='append',
                        help='Extra library to be use while scanning')

    options, arguments = parser.parse_known_args()

    arguments.insert(0, os.path.join(options.binary_dir, 'gtkdoc-scangobj'))

    process = Popen([options.pkg_config,
                    '--cflags'] + options.extra_pkg,
                    stdout=PIPE, stderr=PIPE)

    cflags = []
    output, error = process.communicate()
    if process.returncode == 0:
        cflags += output.rstrip().decode('utf-8').split(' ')

    cflags += options.extra_cflags
    arguments.append('--cflags={0}'.format(' '.join(cflags)))

    process = Popen([options.pkg_config,
                    '--libs'] + options.extra_pkg,
                    stdout=PIPE, stderr=PIPE)

    libs = []
    output, error = process.communicate()
    if process.returncode == 0:
        libs += output.rstrip().decode('utf-8').split(' ')

    for lib in options.extra_lib:
        libs.append('-l{0}'.format(os.path.basename(lib).split('.')[0].lstrip('lib')))
        libs.append('-L{0}'.format(os.path.dirname(lib)))
        libs.append('-Wl,-rpath,{0}'.format(os.path.dirname(lib)))

    arguments.append('--ldflags={0}'.format(' '.join(libs)))

    sys.exit(call(arguments))
