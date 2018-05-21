# -*- python -*-

from __future__ import print_function

import argparse
import os
import shutil
import sys

from subprocess import call

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gtkdoc-mkhtml runner.')

    parser.add_argument("--binary-dir", type=str, required=True,
                        help='Path to be used as a working directory')
    parser.add_argument("--change-dir", type=str, default=None,
                        help='Path to be used as a working directory')
    parser.add_argument("--html-assets", type=str, default=None,
                        help='List of HTML assets, seprated by "@@"')

    options, arguments = parser.parse_known_args()

    arguments.insert(0, os.path.join(options.binary_dir, 'gtkdoc-mkhtml'))

    if options.change_dir is not None:
        if not os.path.exists(options.change_dir):
            os.makedirs(options.change_dir)

    if not options.html_assets is None:
        for html_asset in options.html_assets.split('@@'):
            if options.change_dir is not None:
                html_target = os.path.join(options.change_dir, os.path.basename(html_asset))
            else:
                html_target = os.path.join(os.getcwd(), os.path.basename(html_asset))
            shutil.copyfile(html_asset, html_target)

    sys.exit(call(arguments, cwd=options.change_dir))