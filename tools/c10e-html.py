#!/usr/bin/python3
# canonicalize html dirs to ease comaring them
#
# run as:
# ./tools/c10e-html html

import argparse
import glob
import os
import sys

from bs4 import BeautifulSoup


def prettify(filename):
    with open(filename, 'r') as doc:
        soup = BeautifulSoup(doc.read(), 'lxml')
    with open(filename, 'w') as doc:
        doc.write(soup.prettify())


def main(htmldir):
    for filename in glob.glob(os.path.join(htmldir, '*.devhelp2')):
        prettify(filename)
    for filename in glob.glob(os.path.join(htmldir, '*.html')):
        prettify(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='c10e-html - canonicalize html files for diffing')
    parser.add_argument('args', nargs='*',  help='HTML_DIR')

    options = parser.parse_args()
    if len(options.args) < 1:
        sys.exit('Too few arguments')

    main(options.args[0])
