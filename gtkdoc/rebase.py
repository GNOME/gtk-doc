#!@PYTHON@
# -*- python -*-
#
# gtk-doc - GTK DocBook documentation generator.
# Copyright (C) 1998  Damon Chaplin
#               2007  David Necas (Yeti)
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

#############################################################################
# Script      : gtkdoc-rebase
# Description : Rebases URI references in installed HTML documentation.
#############################################################################

from __future__ import print_function

import os, sys, argparse, subprocess, re

from . import config

# Maps.
# These two point to the last seen URI of given type for a package:
# OnlineMap: package => on-line URI
# LocalMap: package => local URI
# This maps all seen URIs of a package to fix broken links in the process:
# RevMap: URI => package
OnLineMap = {}
LocalMap = {}
RevMap = {}
# Remember what mangling we did.
Mapped = {}


def log(options, *msg):
    if options.verbose:
        print(*msg)


def Run(options):
    other_dirs = []

    if (options.html_dir == ''):
        sys.exit("No HTML directory (--html-dir) given.")

    # We scan the directory containing GLib and any directories in GNOME2_PATH
    # first, but these will be overriden by any later scans.
    if "GNOME2_PATH" in os.environ:
        for dir in os.environ["GNOME2_PATH"].split(':'):
            dir = os.path.join(dir, "/share/gtk-doc/html")
            if os.path.isdir(dir):
                log(options, "Prepending GNOME2_PATH directory:", dir)
                other_dirs = [dir] + other_dirs

    dir = subprocess.check_output([config.pkg_config, '--variable=prefix', 'glib-2.0'], universal_newlines=True)
    dir = dir.strip()
    dir = os.path.join(dir, "/share/gtk-doc/html")
    log(options, "Prepending GLib directory", dir)
    other_dirs = [dir] + other_dirs

    # Check all other dirs, but skip already scanned dirs ord subdirs of those

    for dir in other_dirs:
        ScanDirectory(dir, options);

    if options.relative:
        RelativizeLocalMap(options.html_dir, options);

    RebaseReferences(options.html_dir, options)
    PrintWhatWeHaveDone()


def ScanDirectory(dir, options):
    # This array holds any subdirectories found.
    subdirs = []
    onlinedir = None

    log(options, "Scanning documentation directory " + dir)

    if dir == options.html_dir:
        log(options, "Excluding self")
        return

    if not os.path.isdir(dir):
        print('Cannot open dir "%s"' % dir)
        return

    have_index = False
    for entry in os.listdir(dir):
        if os.path.isdir(entry):
            subdirs.push_back(entry)
            continue

        if entry.endswith('.devhelp2'):
            log(options, "Reading index from " + entry)
            o = ReadDevhelp(dir, entry);
            # Prefer this location over possibly stale index.sgml
            if o is not None:
                onlinedir = o
            have_index = True

        if onlinedir and entry == "index.sgml":
            log(options, "Reading index from index.sgml")
            onlinedir = ReadIndex(dir, entry);
            have_index = True
        elif entry == "index.sgml.gz" and not os.path.exists(os.path.join(dir, 'index.sgml')):
            # debian/ubuntu started to compress this as index.sgml.gz :/
            print(''' Please fix https://bugs.launchpad.net/ubuntu/+source/gtk-doc/+bug/77138 . For now run:
gunzip %s/%s
''' % (dir, entry))
        elif entry.endswith('.devhelp2.gz') and not os.path.exists(os.path.join(dir, entry, 'devhelp2')):
            # debian/ubuntu started to compress this as *devhelp2.gz :/
            print('''Please fix https://bugs.launchpad.net/ubuntu/+source/gtk-doc/+bug/1466210 . For now run:
gunzip %d/%s
''' % (dir, entry))
        # we could consider supporting: gzip module

    if have_index:
        AddMap(dir, onlinedir);

    # Now recursively scan the subdirectories.
    for subdir in subdirs:
        ScanDirectory(os.path.join(dir, subdir), options);


def ReadDevhelp(dir, file):
    onlinedir = None

    for line in open(os.path.join(dir, file)):
        # online must come before chapter/functions
        if '<chapters' in line or '<functions' in line:
            break
        match = re.search(r'  online="([^"]*)"/')
        if match:
            # Remove trailing non-directory component.
            onlinedir = re.sub(r'(.*/).*', r'\1', match.groups(1))
    return onlinedir


def ReadIndex(dir, file):
    onlinedir = None

    for line in open(os.path.join(dir, file)):
        # ONLINE must come before any ANCHORs
        if '<ANCHOR' in line:
            break
        match = re.match(r'''^<ONLINE\s+href\s*=\s*"([^"]+)"\s*>''', line)
        if match:
            # Remove trailing non-directory component.
            onlinedir = re.sub(r'''(.*/).*''', r'\1', match.groups(1))
    return onlinedir


def AddMap(dir, onlinerdir, options):
    package = None

    package = os.path.split(dir)[1]
    if options.dest_dir != '' and dir.startswith(options.dest_dir):
        dir = dir[len(options.dest_dir)-1:]

    if onlinedir:
        log(options, "On-line location of %s." % onlinedir)
        OnlineMap[package] = onlinedir;
        RevMap[onlinedir] = package;
    else:
        log(options, "No On-line location for %s found" % package)

    log(options,  "Local location of $package: " + dir)
    LocalMap[package] = dir;
    RevMap[dir] = package;


def RelativizeLocalMap(dirname, options):
    prefix = None
    dir = None

    dirname = os.path.realpath(dirname)
    prefix = os.path.split(dirname)
    for package, dir in LocalMap.items():
        if dir.startswith(prefix):
            dir = os.path.join("..", dir[len(prefix):])
            LocalMap[package] = dir
            log(options, "Relativizing local location of $package to " + dir)

def RebaseReferences(dirname, options):
    for ifile in os.listdir(dirname):
        if ifile.endswith('.html'):
            RebaseFile(os.path.join(dirname, ifile), options)


def RebaseFile(filename, options):
    log(options, "Fixing file: " + filename)
    regex = re.compile(r'''(<a(?:\s+\w+=(?:"[^"]*"|'[^']*'))*\s+href=")([^"]*)(")''',
                       flags=re.MULTILINE)

    def repl_func(match):
        return match.group(1) + RebaseLink(match.group(2), options) + match.group(3)

    contents = open(filename).read()
    processed = re.sub(regex, repl_func, contents)
    newfilename = filename + '.new'
    open(newfilename, 'w').write(processed)
    os.unlink(filename)
    os.rename(newfilename, filename)


def RebaseLink(href, options):
    match = re.match(r'^(.*/)([^/]*)$', href)
    package = None
    origdir = 'INVALID'

    if match:
        dir = origdir = match.group(1)
        file = match.group(2)
        if dir in RevMap:
            package = RevMap[dir]
        else:
            match = re.match(r'\.\./([^/]+)', href)
            if match is not None:
                package = match.groups(1)
            elif options.aggressive:
                match = re.search(r'''([^/]+)/$''', href)
                package = match.groups(1);

        if package:
            if options.online and package in OnlineMap:
              dir = OnlineMap[package]
            elif package in LocalMap:
              dir = LocalMap[package]
            href = os.path.join(dir, file)
        else:
          log(options, "Can't determine package for '%s'" % href);

        if dir != origdir:
            if origdir in Mapped:
                Mapped[origdir][1] += 1
            else:
                Mapped[origdir] = [dir, 1]
    return href


def PrintWhatWeHaveDone():
    for origdir in sorted(Mapped.keys()):
        info = Mapped[origdir]
        print(origdir, "->", info[0], "(%s)" % info[1])
