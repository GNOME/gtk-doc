#!/usr/bin/env python3
# -*- python; coding: utf-8 -*-
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

"""Migrate from inline docbook markup to markdown.

The tool converts markup in comments for the given source file(s). If --dry-run
is given it would only report that docbook tags were found with exit code 1.
To convert interatively one would make a copy of the docs/xml dir, run the
migration tool for some sources, rebuild the docs and compare the new xml.
If it looks the same (or similar enough), submit the changes and repeat for more
files.

Examples:
python3 tools/db2md.py --dry-run tests/*/src/*.{c,h} | sed -e 's/^ *//' | sort | uniq -c | sort -g
"""

import argparse
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET


def print_xml(node, depth=0):
    # if node.text:
    #     print('  ' * depth, node.text)
    for child in node:
        print('  ' * depth, '<%s %s>' % (child.tag, child.attrib))
        print_xml(child, depth + 1)
    # if node.tail:
    #     print('  ' * depth, node.tail)


def convert_block(dry_run, filename, lines, beg, end):
    logging.debug("%s: scan block %d..%d", filename, beg, end)

    # get indentation
    line = lines[beg]
    indent = line.find('* ')
    if indent == -1:
        logging.warning("%s:%d: missing '*' in comment?", filename, beg)
        return 0

    indent += 2

    found_docbook = 0
    end_skip = None
    content = ''
    for ix in range(beg, end):
        # scan for docbook tags
        line = lines[ix]
        content += line[indent:]

        if not re.search(r'^\s*\*', line):
            logging.warning("%s:%d: missing '*' in comment?", filename, ix)
            continue

        line = line[indent:]

        # skip |[ ... ]| and <![CDATA[ ...  ]]> blocks
        if end_skip:
            if re.search(end_skip, line):
                logging.debug("%s:%d: skip code block end", filename, ix)
                end_skip = None
            continue
        else:
            if re.search(r'\|\[', line):
                logging.debug("%s:%d: skip code block start", filename, ix)
                end_skip = r'\]\|'
                continue
            # if re.search(r'<!\[CDATA\[', line):
            #     logging.debug("%s:%d: skip code block start", filename, ix)
            #     end_skip = r'\]\]>'
            #     continue

        # TODO: skip `...` blocks
        # check for historic non markdown compatible chars
        if re.search(r'\s\*\w+[\s.]', line):
            logging.warning("%s:%d: leading '*' needs escaping: '%s'", filename, ix, line)
        # if re.search(r'\s\w+\*[\s.]', line):
        #     logging.warning("%s:%d: trailing '*' needs escaping: '%s'", filename, ix, line)
        if re.search(r'\s_\w+[\s.]', line):
            logging.warning("%s:%d: leading '_' needs escaping: '%s'", filename, ix, line)
        # if re.search(r'\s\w+_[\s.]', line):
        #     logging.warning("%s:%d: trailing '_' needs escaping: '%s'", filename, ix, line)

        # look for docbook
        for m in re.finditer(r'<([^>]*)>', line):
            tag = m.group(1)
            tag_name = tag.split(' ')[0]
            # check if it is a valid xml element name
            if not re.search(r'^/?[a-z_:][a-z0-9_:.-]*/?$', tag_name, re.I):
                continue

            found_docbook = 1
            break
            # if dry_run:
            #     # python3 tools/db2md.py --dry-run tests/*/src/*.{c,h} | \
            #     #   cut -d':' -f3- | sort | uniq -c | sort -g
            #     print('%s:%d:<%s>' % (filename, ix, tag_name.replace('/', '')))

    if found_docbook:
        # add a fake root
        content = '<gtkdoc>' + content + '</gtkdoc>'
        # TODO: protect |[ ... ]| sections, use CDATA?s
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return 0

        if not root:
            return 0

        if dry_run:
            print('%s:%d:' % (filename, ix))
            print_xml(root)
        else:
            # TODO: convert_tags()
            pass

    return found_docbook


def convert_file(dry_run, filename):
    """Scan scan a single file.

    Returns: 0 if no doocbook was found
    """

    found_docbook = 0
    lines = None
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    logging.debug("%s: read file with %d lines", filename, len(lines))

    beg = end = -1
    for ix in range(len(lines)):
        line = lines[ix]
        # logging.debug("%s:%d: %d,%d: %s", filename, ix, beg, end, line)
        if beg == -1 and end == -1:
            if re.search(r'^\s*/\*.*\*/', line):
                pass
            elif re.search(r'^\s*/\*\*(\s|$)', line):
                logging.debug("%s:%d: comment start", filename, ix)
                beg = ix
        elif beg > -1 and end == -1:
            if re.search(r'^\s*\*+/', line):
                logging.debug("%s:%d: comment end", filename, ix)
                end = ix

        if beg > -1 and end > -1:
            beg += 1
            end -= 1
            if beg < end:
                found_docbook = found_docbook | convert_block(dry_run, filename, lines, beg, end)
            beg = end = -1

    return found_docbook


def main(dry_run, files):
    """Scan for docbook tags in comments. If not in dry_run mode rewrite them as
    markdown. Report the files that contain(ed) docbook tags.

    Returns: 0 if no doocbook was found
    """

    found_docbook = 0
    for f in files:
        found_docbook = found_docbook | convert_file(dry_run, f)
    return found_docbook


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='db2md - convert docbook in comment to markdown')
    parser.add_argument('--dry-run', default=False, action='store_true',
                        help='Only print files with docbook comments.')
    parser.add_argument('sources', nargs='*')
    options = parser.parse_args()
    if len(options.sources) == 0:
        sys.exit('Too few arguments')

    log_level = os.environ.get('GTKDOC_TRACE')
    if log_level == '':
        log_level = 'INFO'
    if log_level:
        logging.basicConfig(stream=sys.stdout,
                            level=logging.getLevelName(log_level.upper()),
                            format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(levelname)s:%(message)s')

    sys.exit(main(options.dry_run, options.sources))
